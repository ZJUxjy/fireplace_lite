## Context

The `/api/cards/all` endpoint serves the deck-builder's entire collectible card catalog (2628 rows after filtering, ~1.48 MB JSON). Today the path is:

```
[user enters card browser]
    └─ fetch /api/cards/all
         └─ Flask handler calls build_catalog()
             ├─ _ensure_db_initialized()  ← 20s on cold start
             └─ iterate db, dict-encode 2628 cards  ← 4.3s
         └─ json.dumps  ← 10ms
    └─ browser parse + first paint
```

Three effects compound to make this feel slow:

1. **The user is the trigger.** The XML parse fires *because* of the first user request. The user pays the latency directly.
2. **Flask debug autoreload re-runs cold init.** Every code edit during local dev = another 25 s wait.
3. **No progressive rendering.** Even when the cache is warm, the client awaits the full 1.48 MB before painting any rows.

The card data is essentially static — it only changes when the underlying `CardDefs.xml` changes (rare) or when our extraction code changes (per commit). That makes it an obvious candidate for ahead-of-time caching and progressive delivery.

## Goals / Non-Goals

**Goals:**

- First card row visible in **under 500 ms** for the steady-state case (warm in-memory cache, no IndexedDB).
- First card row visible **immediately** (no network wait) for return visits with a populated IndexedDB.
- Cold server start no longer blocks the user: warm-up happens before the first request lands.
- Stale on-disk cache **never** ships incorrect data — schema mismatch invalidates instantly.
- No breaking changes to `/api/cards/all`.

**Non-Goals:**

- Splitting catalog *content* across endpoints (e.g. one for class cards, one for neutrals). The catalog is small enough that one paged endpoint suffices.
- Server-side rendering. We stay a SPA; the optimization is purely about *when* the bytes arrive.
- Retro-fitting the whole app to a streaming protocol. Other endpoints (`/api/decks/validate`, etc.) are fine as one-shot JSON.
- Hot-reloading the catalog when XML is replaced at runtime. A server restart is the canonical refresh mechanism.

## Decisions

### D1 — Warm-up runs in a daemon thread at app startup

`create_app()` spawns a daemon thread that calls `_ensure_db_initialized()` then `build_catalog()`. The thread is started **after** all blueprints register so the app is ready to serve other endpoints immediately.

**Why:** the cost is real, and we want to overlap it with the network round-trip the user makes when they hit any other route. By the time the user navigates to the deck-builder, the cache is usually already populated.

**Alternatives rejected:**

- *Flask's `before_first_request` hook* — fires synchronously on the first request. Doesn't help; user still waits.
- *Async/await* — Flask's request loop isn't async; would require a major refactor for a tiny gain.
- *External worker / cron* — overkill; this is a single-process app.

### D2 — Persistent cache is a JSON sidecar keyed by schema version

```
webui/server/cache/catalog-v3.json
```

The integer in the filename (`v3`) is `CATALOG_SCHEMA_VERSION`, a constant in `card_catalog.py`. Bump it whenever the row schema changes (new field, removed field, semantic change). On startup, `build_catalog()`:

1. If `_catalog_cache` is populated, return it.
2. Else, try to read `cache/catalog-v<CURRENT>.json`. If present and parses, set `_catalog_cache` from it and return.
3. Else, do the full XML parse + build, then write the result to `cache/catalog-v<CURRENT>.json`.

**Why JSON not pickle:**

- Human-inspectable when something's wrong.
- Cross-version safe (no Python-version coupling).
- Loads in ~50 ms; the size (1.5 MB) is fine.

**Why filename-as-version, not internal field:**

- Old cache files become unreachable instead of silently overwriting. No race with mid-deploy old workers.
- `git clean -dxf` removes all variants in one go.

**Cache directory:** added to `.gitignore`. Created lazily on first write.

### D3 — Paged endpoint accepts a cursor

```
GET /api/cards/page?cursor=0&size=200
```

Returns:

```json
{
  "cards": [ ... up to 200 rows ... ],
  "cursor": 0,
  "size": 200,
  "next_cursor": 200,
  "total": 2628,
  "etag": "987b8343248a1b11"
}
```

`next_cursor` is `null` when this is the last page. The cursor is just an integer offset into the same sorted array `build_catalog()` produces, so identical sequences across requests are guaranteed (no reshuffling). All pages share one ETag — the catalog's — so client-side cache validation is uniform.

**Why a cursor and not page numbers:**

- Server is free to switch to non-integer cursors later (e.g. last-id-seen) without API breakage.
- Avoids the off-by-one ambiguity of "page=1 means index 0–199".

### D4 — Client streams pages with a callback API

```ts
// services/cardCatalog.ts
export type CatalogProgress = { loaded: number; total: number };
export function loadCatalog(opts?: {
  onChunk?: (cards: Card[], progress: CatalogProgress) => void;
}): Promise<Card[]>;
```

`loadCatalog()` returns a Promise that resolves to the full array once all pages have arrived, but **the UI doesn't await it**. Instead:

```tsx
useEffect(() => {
  const cancel = streamCatalog((cards, progress) => {
    setCatalog(cards);                  // grow the array as pages arrive
    setProgress(progress);
  });
  return cancel;
}, []);
```

The first `onChunk` call fires after the first page response; subsequent calls fire as each page resolves. The fetcher pipelines pages so total latency is roughly `time-to-first-page + (n-1) × per-page-rtt / parallelism`.

**Parallelism:** start with serial (one page at a time) for simplicity. If perf demands it, switch to a 2- or 3-way parallel pump using `Promise.all` over a fixed window.

**Cancellation:** the returned cleanup aborts in-flight fetches via `AbortController`. Used when the user navigates away mid-load.

### D5 — IndexedDB persistence keyed by ETag

```
db: 'fireplace-catalog'
store: 'catalog'
record: { etag: string, cards: Card[], saved_at: number }
```

On startup, `loadCatalog()`:

1. Reads from IndexedDB. If a record exists, immediately fires `onChunk(record.cards, { loaded: total, total })` so the UI paints **before any network round-trip**.
2. Issues `GET /api/cards/page?cursor=0&size=1&if_etag=<stored>`. If the response is 304, nothing more to do — record is still valid.
3. If response is 200 with a new ETag, drops the IndexedDB record and starts a fresh paged stream, replacing the in-memory array atomically when it completes.

**Why ETag in the URL not header:** simpler proxy semantics, and the small first-page request also serves as a cheap revalidation probe without needing a separate `HEAD`.

**Storage budget:** one record per origin, ~1.5 MB. Browsers comfortably handle tens of MB of IndexedDB.

**Privacy/ephemeral browsers:** if IndexedDB is unavailable or quota-exceeded, fall back gracefully to network-only — no warning needed.

### D6 — UI shows the filter rail before any cards arrive

`DeckEditor` (and the future browse-only entry point) mount the FilterRail and topbar before the first card chunk. `CardPool`'s grid shows a "loading collection… 200 / 2628" footer until `progress.loaded === progress.total`. Pagination defaults to the first page; the user can scroll cost/keyword chips while data streams in.

This is the cheapest UX win: even if total wall-clock time is identical, the user has something to look at and can start interacting immediately.

## Risks / Trade-offs

- **Risk: warm-up thread races first request.** → Mitigation: `build_catalog()` is already protected by `_catalog_lock`. The first request acquires the lock, blocks until the thread releases it, then returns the populated cache. Worst case the user waits ~25 s on cold start, same as today, but only if they navigate to the catalog within the first second of process boot — uncommon.

- **Risk: corrupted disk cache.** → Mitigation: parse failure falls through to the full rebuild path and overwrites the bad file. We log a warning; we never serve partial / undefined data.

- **Risk: schema bump is forgotten.** → Mitigation: a unit test in `tests/test_catalog_cache.py` asserts the persisted cache file's row keys match a frozen reference set; a developer adding/removing a row field forgets to bump the version → the test fails before merge.

- **Risk: paged endpoint and `/all` drift.** → Mitigation: both call into the same in-memory list and slice it; there is no second path.

- **Risk: client gets pages out of order.** → Mitigation: the streaming loader keys received chunks by `cursor`. Out-of-order arrivals are sorted before assembly. With serial fetching this can't happen, but the safety net costs nothing.

- **Trade-off: IndexedDB adds complexity.** Mitigated by isolating it behind a single `catalogStore.ts` module with a tiny API (`get(): Promise<Record|null>` / `put(record): Promise<void>` / `clear()`). Only one consumer (`loadCatalog`) ever calls it.

- **Trade-off: total bytes transferred can rise slightly.** Each paged response carries small JSON envelope overhead. With 14 pages of 200 each, the overhead is ~5 KB versus a 1.5 MB body — negligible.

## Migration Plan

Single-PR rollout, no flag:

1. Land server changes (warm-up thread, disk cache, paged endpoint). `/api/cards/all` keeps working unchanged. Verify cold-start latency on next request drops to ~50 ms (disk cache hit).
2. Land client changes (streaming loader, IndexedDB). Feature is universal; no toggle.
3. After one week with no rollback, archive the openspec change.

Rollback strategy: revert the two commits. The disk cache file becomes orphaned but harmless; gitignore'd and small.

## Open Questions

- **Should we also gzip the persistent cache file?** 1.5 MB → ~250 KB, but read time is dominated by JSON parse, not disk I/O. Decision: skip for now; revisit if the file's footprint becomes a complaint.
- **Do we want the warm-up thread to publish progress over a websocket so an admin dashboard can see it?** Out of scope; can be layered on later.
- **Should `/api/cards/all` be deprecated long-term?** Probably yes, but keep both for at least a release cycle. No urgency.
