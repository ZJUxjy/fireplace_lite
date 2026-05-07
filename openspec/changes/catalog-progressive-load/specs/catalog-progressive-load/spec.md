## ADDED Requirements

### Requirement: Server eagerly warms the catalog on startup

The server SHALL start a background daemon thread during `create_app()` that calls `_ensure_db_initialized()` followed by `build_catalog()`. The thread MUST be started after blueprint registration so other endpoints remain available immediately. Errors raised by the warm-up MUST be logged but MUST NOT prevent the app from serving non-catalog endpoints.

#### Scenario: Cache is populated before first user request

- **WHEN** `create_app()` returns and the warm-up thread has had time to complete
- **AND** a client requests `/api/cards/all`
- **THEN** the request completes without triggering a fresh `db.initialize()` or `build_catalog()`
- **AND** the response time is dominated by JSON serialization, not XML parsing

#### Scenario: First request races the warm-up thread

- **WHEN** `create_app()` has just returned and the warm-up thread is still running
- **AND** a client requests `/api/cards/all` before the thread completes
- **THEN** the handler blocks on the same `_catalog_lock` the thread uses
- **AND** the response is served exactly once, with no double-init and no partial data

#### Scenario: Warm-up failure does not break the app

- **WHEN** the warm-up thread raises (e.g. CardDefs.xml is missing)
- **THEN** the exception is logged with stack trace
- **AND** `/api/cards/all` returns a 500 with a structured error body when invoked
- **AND** unrelated endpoints (e.g. `/api/languages`) continue to work normally

### Requirement: Catalog is persisted to disk between server starts

The catalog payload SHALL be persisted to `webui/server/cache/catalog-v<N>.json` after the first successful `build_catalog()` call, where `N` is the current `CATALOG_SCHEMA_VERSION` constant. On subsequent process starts, `build_catalog()` MUST attempt to load this file before falling back to the XML-parse path. A schema-version mismatch MUST cause the file to be ignored (not deleted), and a fresh build to be written under the new versioned filename.

#### Scenario: Disk cache hit on warm start

- **WHEN** the server has previously built the catalog and written `cache/catalog-vN.json`
- **AND** the server starts again with the same `CATALOG_SCHEMA_VERSION = N`
- **THEN** `build_catalog()` reads the JSON file and returns within ~100 ms
- **AND** does not call `_cards_db.initialize()`

#### Scenario: Schema bump invalidates old cache

- **WHEN** `cache/catalog-v3.json` exists from a previous version
- **AND** the running code has `CATALOG_SCHEMA_VERSION = 4`
- **THEN** the v3 file is ignored
- **AND** the catalog is rebuilt from XML
- **AND** the result is written to `cache/catalog-v4.json` (v3 file remains untouched)

#### Scenario: Corrupted cache falls through to rebuild

- **WHEN** `cache/catalog-vN.json` exists but is malformed JSON or missing required keys
- **AND** `build_catalog()` is invoked
- **THEN** a warning is logged
- **AND** the catalog is rebuilt from XML
- **AND** the corrupted file is overwritten with the fresh build

### Requirement: Catalog is served paginated via cursor-based endpoint

The server SHALL expose `GET /api/cards/page` accepting query parameters `cursor` (integer, default 0) and `size` (integer, default 200, capped at 500). The response MUST include `cards`, `cursor`, `size`, `next_cursor` (integer or null), `total`, and `etag` fields. All pages within a single catalog snapshot MUST share the same `etag`. The page slice ordering MUST exactly match the order produced by `build_catalog()`'s in-memory list (no reshuffling between requests).

#### Scenario: First page returns first slice plus next cursor

- **WHEN** a client requests `GET /api/cards/page?cursor=0&size=200`
- **THEN** the response status is 200
- **AND** `cards` contains the first 200 catalog rows in canonical order
- **AND** `cursor === 0`, `size === 200`, `next_cursor === 200`, `total === 2628`
- **AND** `etag` matches the etag served by `/api/cards/all`

#### Scenario: Last page sets next_cursor to null

- **WHEN** a client requests `GET /api/cards/page?cursor=2400&size=500`
- **THEN** the response contains the remaining 228 cards
- **AND** `next_cursor === null`

#### Scenario: Out-of-range cursor returns empty page

- **WHEN** a client requests `GET /api/cards/page?cursor=99999&size=200`
- **THEN** the response status is 200
- **AND** `cards === []`
- **AND** `next_cursor === null`

#### Scenario: ETag is stable across paged requests

- **WHEN** a client fetches every page sequentially
- **THEN** every response carries the same `etag` value
- **AND** that `etag` equals the one returned by `/api/cards/all` for the same catalog snapshot

### Requirement: Client streams catalog pages and renders progressively

The client SHALL provide a `loadCatalog(opts?: { onChunk?: (cards, progress) => void })` API that fetches the catalog as a sequence of pages, invoking `onChunk` after each page resolves with the cumulative array and a `{ loaded, total }` progress object. The function MUST also return a Promise that resolves to the full array once the final page arrives. The DeckEditor and any catalog-consuming UI MUST mount their non-card affordances (filter rail, topbar, pagination shell) before the first chunk arrives.

#### Scenario: First chunk fires before the second page is requested

- **WHEN** the client calls `loadCatalog({ onChunk })` against a populated server
- **THEN** `onChunk` is invoked with the first 200 cards as soon as the first page response is parsed
- **AND** the returned promise has not yet resolved

#### Scenario: Final chunk corresponds to promise resolution

- **WHEN** the streaming loader receives the page whose `next_cursor` is null
- **THEN** `onChunk` fires one last time with the full catalog and `progress.loaded === progress.total`
- **AND** the returned Promise resolves with the same array

#### Scenario: UI mounts filter rail before any cards arrive

- **WHEN** the user opens the catalog browser
- **AND** the first page response has not yet arrived
- **THEN** the FilterRail and topbar are rendered and interactive
- **AND** the card grid area shows a "正在加载…" placeholder, not blank

### Requirement: Client persists catalog to IndexedDB and revalidates

The client SHALL persist the most recent fully-loaded catalog to IndexedDB keyed by ETag. On a return visit, the client MUST paint from IndexedDB before issuing any network request, then revalidate against the server using the stored ETag. A 304 response MUST require no further work; a fresh ETag MUST trigger a new streamed load that swaps the in-memory array atomically once complete. If IndexedDB is unavailable or rejects the write, the client MUST fall back to network-only behavior without surfacing a user-facing error.

#### Scenario: Return visit paints from IndexedDB instantly

- **WHEN** the user has previously fully loaded the catalog
- **AND** opens the catalog browser in a new tab
- **THEN** the FilterRail and the first 200 cards (or whatever the in-memory paginator shows) render before any network request completes
- **AND** a revalidation request is issued in the background

#### Scenario: Server returns 304 — no further loading

- **WHEN** the revalidation request is made with `If-None-Match: <stored-etag>`
- **AND** the server's catalog ETag matches
- **THEN** the server returns 304
- **AND** the client makes no further `/api/cards/page` requests
- **AND** the in-memory catalog remains the IndexedDB-restored copy

#### Scenario: Server returns new ETag — atomic swap

- **WHEN** the revalidation request returns a 200 with a different ETag
- **THEN** the client begins a fresh paged stream
- **AND** the existing in-memory catalog continues to serve UI lookups during the stream
- **AND** the new array replaces the old one only after the final chunk arrives
- **AND** IndexedDB is updated with the new ETag and rows

#### Scenario: IndexedDB unavailable

- **WHEN** the browser blocks IndexedDB (private mode, quota exceeded, or no support)
- **AND** the user opens the catalog browser
- **THEN** the client falls back to a network-only paged load
- **AND** no error toast or warning is shown to the user
- **AND** a console warning is logged once
