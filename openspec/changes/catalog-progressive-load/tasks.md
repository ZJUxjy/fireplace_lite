## 1. Server: persistent on-disk catalog cache

- [x] 1.1 In `webui/server/card_catalog.py`, add a module-level `CATALOG_SCHEMA_VERSION` integer constant. Set it to `1` initially. Document next to the constant: "bump whenever the row dict shape changes — adds, removes, or changes the meaning of a key".
- [x] 1.2 Add `CACHE_DIR = Path(__file__).parent / "cache"` and a `_cache_path()` helper returning `CACHE_DIR / f"catalog-v{CATALOG_SCHEMA_VERSION}.json"`.
- [x] 1.3 Add `.gitignore` entry for `webui/server/cache/`.
- [x] 1.4 Add `_load_persistent_cache() -> Optional[Dict[str, Any]]` that reads the cache path, returns the parsed dict if it has the expected top-level keys (`cards`, `total`, `etag`, `generated_at`), else returns None and logs a warning.
- [x] 1.5 Add `_write_persistent_cache(payload: Dict[str, Any]) -> None` that writes the payload to `_cache_path()` atomically (write to `.tmp` then `os.replace`). Creates the cache dir on first write.
- [x] 1.6 Modify `build_catalog()`: after the existing in-memory cache check, attempt `_load_persistent_cache()` before invoking `_ensure_db_initialized()`. If hit, populate `_catalog_cache` and return. If the XML-parse path runs, call `_write_persistent_cache()` after the in-memory cache is set.
- [x] 1.7 Add a `tests/test_catalog_cache.py` with three tests:
  - 1.7.1 Cold build with no cache file present produces a file matching the in-memory result.
  - 1.7.2 Subsequent `reset_catalog_cache()` + `build_catalog()` reads the file (assert `db.initialize()` is not invoked — patch / mock `_ensure_db_initialized`).
  - 1.7.3 Manually corrupt the file (truncate) → next `build_catalog()` rebuilds and overwrites; assert no exception escapes.
- [x] 1.8 Run `pytest tests/test_catalog_cache.py tests/test_card_catalog.py` and confirm green.

## 2. Server: warm-up thread at app startup

- [x] 2.1 In `webui/server/__init__.py`, after `app.register_blueprint(views.bp)`, start a `threading.Thread(target=_warmup, daemon=True)` where `_warmup` calls `card_catalog.build_catalog()` inside a try/except (logging exceptions but not re-raising).
- [x] 2.2 Make the warm-up opt-out via `app.config.get('SKIP_CATALOG_WARMUP', False)` so unit tests can disable it (the existing test fixture sets this).
- [x] 2.3 Add `tests/test_app_warmup.py`:
  - 2.3.1 Default app warms up: after a short `time.sleep`, the in-memory `_catalog_cache` is set without any user request. (Use a fast path by pre-writing a minimal disk cache so the test doesn't pay the 25 s XML cost.)
  - 2.3.2 Race test: spin up the warm-up thread and immediately request `/api/cards/all` from a test client; assert the response is consistent and only one full build runs (use a counter inside `_extract_keywords` or wrap `build_catalog` with a counter).
- [x] 2.4 Document the opt-out flag in a one-line comment near the config read.

## 3. Server: paged endpoint

- [x] 3.1 In `webui/server/card_catalog.py`, add `get_page(cursor: int, size: int) -> Dict[str, Any]` that calls `build_catalog()` then returns `{cards: cards[cursor:cursor+size], cursor, size, next_cursor: cursor+size if cursor+size < total else None, total, etag}`. Cap `size` at 500 to prevent abuse.
- [x] 3.2 In `webui/server/views.py`, add `GET /api/cards/page` reading `cursor` and `size` from query params (default 0 and 200), coercing to int with 400 on bad input.
- [x] 3.3 Set `Cache-Control: private, max-age=300` and `ETag` headers on the page response (same etag as `/api/cards/all`); honor `If-None-Match` for 304s.
- [x] 3.4 Add `tests/test_cards_page.py` covering:
  - 3.4.1 Default page returns 200 cards and correct cursor metadata.
  - 3.4.2 Last partial page returns `next_cursor: null`.
  - 3.4.3 Out-of-range cursor returns empty `cards` and `next_cursor: null`.
  - 3.4.4 Bad query (`cursor=abc`) returns 400.
  - 3.4.5 ETag matches `/api/cards/all`.
  - 3.4.6 Concatenating all pages yields exactly the same array as `/api/cards/all`.
- [x] 3.5 Run all server tests; confirm green.

## 4. Client: streaming catalog loader

- [x] 4.1 In `webui/client/src/services/cardCatalog.ts`, add `streamCatalog(opts: { onChunk: (cards, progress) => void; signal?: AbortSignal }) => Promise<Card[]>`. Internally fetches `/api/cards/page` with `cursor=0, size=200`, then loops on `next_cursor` until null, calling `onChunk` after each page resolves.
- [x] 4.2 Refactor existing `loadCatalog()` to delegate to `streamCatalog()` for the network path, ignoring `onChunk` for legacy callers (still resolves with the full array). Keep the module-level `_catalog` cache.
- [x] 4.3 In `DeckEditor.tsx` and any other consumer that does the existing `loadCatalog().then(setCatalog)` pattern, switch to `streamCatalog({ onChunk: (cards, progress) => { setCatalog([...cards]); setProgress(progress); } })` so partial arrays paint as they arrive.
- [x] 4.4 In `CardPool.tsx`, when `progress.loaded < progress.total`, render a small "正在加载… {loaded}/{total}" badge in the topbar so the user sees streaming progress.
- [x] 4.5 Cancel in-flight pages on unmount via `AbortController`.

## 5. Client: IndexedDB persistence

- [x] 5.1 Create `webui/client/src/services/catalogStore.ts` exporting `get(): Promise<{etag,cards}|null>`, `put(record): Promise<void>`, `clear(): Promise<void>`. Wraps a single `'fireplace-catalog'` IDB database with a `'catalog'` object store. Catches `DOMException` and rejects to a console warning + null/no-op rather than throwing.
- [x] 5.2 In `cardCatalog.ts`, on `streamCatalog()` entry: read IDB; if a record exists, fire `onChunk(record.cards, {loaded: record.cards.length, total: record.cards.length})` synchronously, then issue a probe `GET /api/cards/page?cursor=0&size=1` with `If-None-Match: <stored-etag>`.
- [x] 5.3 If the probe returns 304, the streaming function resolves immediately with the stored array.
- [x] 5.4 If the probe returns 200 with a different ETag, throw away the stored record and stream from `cursor=0` as if no IDB record existed. Once the final page arrives, write the new record to IDB.
- [x] 5.5 Atomic swap: keep the IDB-restored array in a "pending" slot during streaming; only call `onChunk` for the new array once all pages have arrived. (Avoids visible flicker mid-load.)
- [x] 5.6 If `catalogStore.put()` fails (quota exceeded), log a one-time console warning and continue.

## 6. UI polish for the loading state

- [x] 6.1 In `DeckEditor.tsx`, render the FilterRail before any catalog data is available. The rail's filtered chip counts can show "—" while `progress.total === 0`.
- [x] 6.2 In `CardPool.tsx`, the empty-list state during loading shows the spinner + "正在加载卡库… {loaded}/{total}". Once `loaded === total` the spinner disappears.
- [x] 6.3 Pagination component: gray out when `loaded < total`. Buttons remain visible (so the layout doesn't shift) but onClick is no-op until the data is fully loaded.

## 7. Verification

- [x] 7.1 Build the client (`npm run build`) and the worktree's Flask backend; confirm both start without errors.
- [x] 7.2 With cold disk cache (`rm -f webui/server/cache/catalog-v*.json`), restart the server. Note the warm-up duration in the log.
- [x] 7.3 Issue `curl /api/cards/page?size=1` immediately after restart. The first request should still complete (it may briefly block on the warm-up thread); subsequent requests are instant.
- [x] 7.4 Restart the server again. Confirm `build_catalog()` now finishes within 200 ms (disk-cache hit).
- [x] 7.5 Open the catalog browser in a fresh incognito window. Verify the FilterRail paints before any cards. Verify the loading badge counts up. Verify final card count equals `/api/cards/all`'s `total`.
- [x] 7.6 Reload the same window (non-incognito). Verify the cards paint without a network spinner (IDB hit), then verify a 304 in the network panel.
- [x] 7.7 Bump `CATALOG_SCHEMA_VERSION` locally → restart → confirm a new cache file `catalog-v2.json` is created and the old `v1` is left in place.
- [x] 7.8 Run `openspec validate catalog-progressive-load` — confirm valid.
- [x] 7.9 Stage and commit on the worktree branch with a single message describing the progressive-load rebuild.
