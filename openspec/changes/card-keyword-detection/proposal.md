## Why

Keyword detection in the deck builder is broken in two distinct ways and the FilterRail keyword chips and CardRow keyword badges currently produce wrong or empty results:

1. **`法力浮龙` is in the keyword list.** It is the *card name* of a minion (Mana Wyrm), not a Hearthstone keyword. Including it pollutes both the FilterRail chip grid and the badge shown on each card row.
2. **Substring matching against `text_zh` is fragile.** `cardCatalog.filterCards` and `CardRow.detectKeyword` both look for keyword tokens inside the card's localized rules text. This produces false positives ("获得+1/+1 后施放战吼…" is not the same as a card *having* Battlecry) and misses cards whose translation phrasing differs from the canonical token. CardRow keeps its own hardcoded keyword list separately from `cardCatalog.KEYWORD_TOKENS`, so the two will inevitably drift.

The authoritative source of truth — `CardDefs.xml` and `hearthstone.enums.GameTag` — already encodes each card's keywords as boolean tags (`TAUNT`, `BATTLECRY`, `DEATHRATTLE`, …). We should read those instead of guessing from translated rules text, and surface the result through the catalog so the filter and the badge use the same data.

## What Changes

- **Server (`webui/server/card_catalog.py`):** while building the catalog payload, read keyword GameTags off each `Card` and attach a `keywords: list[str]` field (canonical enum names like `"TAUNT"`).
- **Client (`webui/client/src/types/deck.ts`):** replace the existing untyped `keywords?: string[]` (if any) with a typed `keywords: Keyword[]` field on `Card`.
- **Client (`webui/client/src/services/cardCatalog.ts`):**
  - Replace the hardcoded `KEYWORD_TOKENS` array (which contains `法力浮龙`) with the canonical enum-keyed list of 13 keywords plus a localization map `KEYWORD_LABELS` (zh + en).
  - Rewrite `cardHasKeyword(card, kw)` to read from `card.keywords` instead of `card.text_zh.includes(kw)`.
  - Update `filterCards`'s `keywords` branch to match by enum membership, not substring.
- **Client (`webui/client/src/components/CardRow.tsx`):** delete the local `KEYWORDS` array and `detectKeyword`. Show the first canonical keyword from `card.keywords` (if any) localized via `KEYWORD_LABELS`.
- **Client (`webui/client/src/components/FilterRail.tsx`):** render keyword chips using the canonical enum list and the localization map (display label, internal value is the enum).
- **Tests (`webui/server/tests/`):** add `test_card_keyword_extraction.py` covering at least one card per supported keyword (e.g. Boulderfist Ogre has nothing; Stormwind Champion has nothing; Argent Squire has DIVINE_SHIELD; Knife Juggler has BATTLECRY but only via effect, not tag — confirms we use the tag, not the text).
- **Dev-only "candidate keyword" report:** the catalog builder additionally produces a histogram of every boolean GameTag found on at least one collectible card that is NOT in the recognized 13 nor on a curated cosmetic-tag deny-list. Exposed at `/api/cards/keyword-candidates`, gated behind `DEBUG_KEYWORDS`/`FLASK_DEBUG`. Helps catch new keywords introduced by future XML drops without ever surfacing internal tags to end users.

**BREAKING:** the catalog payload schema changes. `card.keywords` becomes a required array of enum strings rather than a substring-derived runtime computation. `KEYWORD_TOKENS` is renamed to `KEYWORDS` and its values are enum names (`TAUNT`) rather than display text (`嘲讽`). Consumers must use `KEYWORD_LABELS[kw]` to render.

## Capabilities

### New Capabilities

- `card-keywords`: canonical mechanic-keyword recognition for the catalog. Defines which keywords are recognized, where they are sourced from (GameTag, not text), how they appear in the catalog payload, and how clients localize and filter on them.

### Modified Capabilities

(none — `card-catalog` is not yet captured as a spec, so the keyword field is introduced as part of the new `card-keywords` capability rather than as a delta.)

## Impact

- **Code:**
  - `webui/server/card_catalog.py` — extend `build_catalog()` row builder.
  - `webui/server/tests/test_card_keyword_extraction.py` — new.
  - `webui/client/src/types/deck.ts` — `keywords` field on `Card`.
  - `webui/client/src/services/cardCatalog.ts` — `KEYWORDS`, `KEYWORD_LABELS`, `cardHasKeyword`, `filterCards`.
  - `webui/client/src/components/CardRow.tsx` — remove substring detector, use `card.keywords[0]`.
  - `webui/client/src/components/FilterRail.tsx` — render via `KEYWORD_LABELS`.
- **API:** `/api/cards/all` response gains a `keywords: string[]` field per card. ETag will change on the next build, invalidating cached client copies (intended).
- **Dependencies:** none added; uses the existing `hearthstone.enums.GameTag` already imported by `fireplace`.
- **Performance:** one extra pass over each card's tags during catalog build (one-time, server-side, cached). No client cost beyond an array lookup.
