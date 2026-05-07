## 1. Server: extract keyword tags into the catalog payload

- [x] 1.1 Add a `KEYWORD_TAGS` mapping (`enum-name → GameTag`) at module scope in `webui/server/card_catalog.py`, covering exactly the 13 canonical identifiers listed in `design.md` §D3 (TAUNT, BATTLECRY, DEATHRATTLE, CHARGE, RUSH, DIVINE_SHIELD, WINDFURY, STEALTH, POISONOUS, LIFESTEAL, SECRET, SPELLPOWER, COMBO).
- [x] 1.2 Add a private `_extract_keywords(card) -> list[str]` helper that iterates `KEYWORD_TAGS` in declaration order and returns the names whose corresponding tag is truthy on the card. Treat any nonzero `SPELLPOWER` value as present.
- [x] 1.3 In the row builder inside `build_catalog()`, set each card row's `keywords` field via `_extract_keywords(card)`. Field MUST always be a list (default `[]`).
- [x] 1.4 Confirm the per-row hash that feeds the catalog ETag includes the new `keywords` field so a build automatically produces a new ETag.
- [x] 1.5 Run `pytest tests/test_card_catalog.py` to confirm no existing test regresses.

## 2. Server: tests for keyword extraction

- [x] 2.1 Create `webui/server/tests/test_card_keyword_extraction.py`.
- [x] 2.2 Add a test that builds the catalog once, indexes by card id, and asserts the `keywords` list for one canonical card per identifier:
  - `EX1_finkle` (Finkle Einhorn) or any reliably implemented vanilla taunt → `TAUNT`
  - `EX1_277` (Arcane Missiles) → `[]` (vanilla spell, no tags)
  - `CS2_222` (Stormwind Champion) → `[]` (auras don't set boolean tags)
  - `EX1_008` (Argent Squire) → `["DIVINE_SHIELD"]`
  - `EX1_586` (Sea Giant) → `[]` (cost-mod is not a keyword)
  - `CS2_142` (Kobold Geomancer) → `["SPELLPOWER"]`
  - Pick at least one card per remaining identifier (BATTLECRY, DEATHRATTLE, CHARGE, RUSH, WINDFURY, STEALTH, POISONOUS, LIFESTEAL, SECRET, COMBO). Use `is_card_implemented` to skip ids the project doesn't ship.
- [x] 2.3 Add an assertion that no catalog row has `"法力浮龙"` or `"Mana Wyrm"` in its `keywords` list, and that Mana Wyrm itself (`NEW1_012`) has `keywords: []`.
- [x] 2.4 Add an assertion that every `keywords` value across the entire catalog is a subset of the 13 canonical identifiers.
- [x] 2.5 Run `pytest webui/server/tests/test_card_keyword_extraction.py -v` and confirm green.

## 3. Client: type and catalog service updates

- [x] 3.1 In `webui/client/src/types/deck.ts`, add a required `keywords: string[]` field to the `Card` type (typed via the `Keyword` union once defined in 3.2).
- [x] 3.2 In `webui/client/src/services/cardCatalog.ts`:
  - Replace `KEYWORD_TOKENS` with a `KEYWORDS` const tuple containing the 13 canonical identifiers, in canonical order.
  - Export `Keyword = typeof KEYWORDS[number]`.
  - Export `KEYWORD_LABELS: Record<Keyword, { zh: string; en: string }>` populated per `design.md` §D3.
  - Tighten `Card.keywords` type to `Keyword[]`.
- [x] 3.3 Rewrite `cardHasKeyword(card, kw)` to return `card.keywords.includes(kw)` (no text scan).
- [x] 3.4 Update the `keywords` branch of `filterCards` to test `card.keywords.includes(k)` instead of `card.text_zh.includes(k)`.

## 4. Client: FilterRail and CardRow rewires

- [x] 4.1 In `FilterRail.tsx`, render keyword chips using `KEYWORDS` and `KEYWORD_LABELS[k].zh` (until i18n is wired). Toggle behavior unchanged; the toggled value remains the canonical identifier.
- [x] 4.2 In `CardRow.tsx`, delete the local `KEYWORDS` array and `detectKeyword`. Compute `const kw = card.keywords[0]; const kwLabel = kw ? KEYWORD_LABELS[kw].zh : null;` and render the badge only when `kwLabel` is non-null.
- [x] 4.3 Verify the badge no longer appears on Mana Wyrm in the running app, and that selecting the Taunt chip filters to taunt minions only.

## 5. Server: dev-only candidate-keyword report

- [x] 5.1 In `webui/server/card_catalog.py`, add a module-level `KEYWORD_DENY_LIST` set of tag names that are boolean-on-cards but explicitly NOT keywords (cosmetic/internal/numeric — full list in `design.md` §D7).
- [x] 5.2 Add `_compute_keyword_candidates()` that walks every collectible card in the catalog, counts boolean GameTags whose value is truthy, drops anything in `KEYWORD_TAGS` or `KEYWORD_DENY_LIST`, and returns `[{ "tag": name, "count": n, "examples": [up to 3 card ids] }, ...]` sorted by descending count then tag name. Cache the result alongside the catalog (same lock).
- [x] 5.3 In `webui/server/views.py`, register `GET /api/cards/keyword-candidates`. Reject (404) when `app.debug` and `app.config.get("DEBUG_KEYWORDS")` are both falsy. Otherwise return `{"candidates": _compute_keyword_candidates()}`.
- [x] 5.4 Add `tests/test_keyword_candidates.py`:
  - 5.4.1 In a debug-mode test client, GET the endpoint and assert 200 + shape + that no entry's `tag` is in the canonical 13 or in `KEYWORD_DENY_LIST`.
  - 5.4.2 In a production-mode test client (`app.debug = False`, `DEBUG_KEYWORDS` unset), assert GET returns 404.
- [x] 5.5 Document the endpoint in a one-line comment near the route handler so future contributors know it's dev-only.

## 6. Cleanup and verification

- [x] 6.1 Search the client for any other references to `KEYWORD_TOKENS` or hardcoded keyword strings (`"嘲讽" |"战吼" | …`). Migrate any survivors to use `KEYWORD_LABELS`.
- [x] 6.2 Run `tsc --noEmit` in `webui/client` and confirm no type errors.
- [x] 6.3 Run `pytest webui/server/tests` end-to-end.
- [x] 6.4 Manually sanity-check in the browser:
  1. Open the deck builder.
  2. Confirm the FilterRail keyword chip group has 13 chips, none of which read "法力浮龙" or "沉默".
  3. Click Taunt — the grid filters to taunt minions; the count in the topbar updates.
  4. Click Mana Wyrm — its row shows no keyword badge; the card preview still shows full rules text.
  5. Click Battlecry + Divine Shield together — the grid shows the union.
- [x] 6.5 In dev mode, hit `http://localhost:5000/api/cards/keyword-candidates` and skim the histogram for any unexpectedly high-count tag — file a follow-up if a real keyword slipped through the deny-list.
- [x] 6.6 Run `openspec validate card-keyword-detection` and confirm valid.
- [x] 6.7 Stage and commit on the design branch with a single message describing the keyword-detection rebuild.
