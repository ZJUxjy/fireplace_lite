## Why

Opening the deck-builder's "卡牌收藏" view today is *very* slow on a fresh server: ~25 seconds before the first card row paints. Measured locally:

| stage                                  | time     |
| -------------------------------------- | -------- |
| `fireplace.cards.db.initialize()` (XML parse, 35k entries) | **20 s** |
| `build_catalog()` (filter to 2628 collectible + keyword tags) | **4.3 s** |
| JSON serialize (1.48 MB)               | 10 ms    |
| **total cold path**                    | **~25 s** |

The pain is twofold:

1. **Cold-start blocks the user.** The very first `/api/cards/all` request after a server (re)start synchronously triggers `db.initialize()` and `build_catalog()`, so the user sits with a spinner for ~25 s. The Flask debug-mode autoreloader makes this worse — every code edit triggers another cold path.
2. **Subsequent loads still feel sluggish.** After the in-memory cache is warm, the request itself is fast (304 with ETag, or ~250 ms for the 1.48 MB body), but the client renders nothing until the entire JSON has downloaded and parsed. With 2628 rows the browse grid stalls visibly.

The user explicitly asked for chunked / async loading: render the filter rail and the first page of cards immediately, fill the rest progressively, and never let the user stare at a blank screen.

## What Changes

- **Eager warm-up at server startup.** `create_app()` kicks off a background thread that calls `_ensure_db_initialized()` then `build_catalog()` so the in-memory cache is ready before the first user request. The first request only waits if it races the warm-up — and even then, it waits behind a future, not a fresh init.
- **On-disk persistent cache.** After `build_catalog()` runs, the resulting `{cards,total,etag,generated_at}` blob is written to `webui/server/cache/catalog-<schema>.json`. On the next process start, `build_catalog()` checks the cache file's `schema` matches the current code's expected schema; if so it loads the JSON in ~50 ms instead of re-parsing XML. Cache busts automatically when the schema bumps (new fields, dropped fields).
- **Paged catalog endpoint.** Add `GET /api/cards/page?cursor=<n>&size=<m>` that returns one page (default 200 cards) plus a `next_cursor` token. The full `/api/cards/all` keeps working for callers that need everything in one shot.
- **Client progressive loader.** `loadCatalog()` becomes a streaming loader: it returns immediately with an empty array and a Promise that resolves after the first page; the UI subscribes via `onCatalogChunk(callback)` to receive each subsequent page. Filter rail mounts with a "正在加载…" footer; the first 200 cards (one full pagination page in the new UI) paint within ~300 ms; the rest stream in over the next second or two while the user is already interacting.
- **Persistent client cache.** Catalog is stored in IndexedDB keyed by ETag. On a return visit the client paints from IndexedDB **immediately** (no network), then revalidates with `If-None-Match`. If the server returns 304, no further work; if it returns a new ETag, the client streams the new pages and swaps the in-memory copy.

**BREAKING:** none. Existing `/api/cards/all` keeps its contract; new endpoints and behaviors are additive. Old clients continue to work.

## Capabilities

### New Capabilities

- `catalog-progressive-load`: defines the eager-warmup, on-disk catalog cache, paged endpoint, and client-side progressive loader contract that together remove cold-start latency from the user-perceived path.

### Modified Capabilities

(none — `card-keywords` is unchanged; this change only affects how the catalog is delivered, not its content.)

## Impact

- **Code:**
  - `webui/server/__init__.py` — kick off warm-up thread in `create_app()`.
  - `webui/server/card_catalog.py` — load/save persistent cache; expose `iter_catalog_pages()`.
  - `webui/server/views.py` — new `GET /api/cards/page` endpoint.
  - `webui/client/src/services/cardCatalog.ts` — streaming `loadCatalog()` with progress callback; IndexedDB persistence.
  - `webui/client/src/components/DeckEditor.tsx` — render skeleton immediately, subscribe to chunks, repaint as pages arrive.
  - `webui/client/src/components/CardPool.tsx` — show "loading more…" hint when not all pages have arrived yet.
- **API:**
  - `GET /api/cards/all` unchanged.
  - `GET /api/cards/page?cursor=<int>&size=<int>` new.
- **Storage:** one new file `webui/server/cache/catalog-v<N>.json` (~1.5 MB, gitignored). Browser stores ~1.5 MB in IndexedDB under origin storage.
- **Performance:**
  - First-ever load (cold disk cache): warm-up runs in background; user sees first 200 cards within ~5 s instead of 25 s; full grid populated within ~7 s.
  - Subsequent loads with disk cache: first paint <500 ms.
  - Returning client visit (IndexedDB hit): first paint **immediate**, revalidate in background.
- **Risk:** stale on-disk cache after a code change to row schema → mitigated by schema-version key in the file name.
