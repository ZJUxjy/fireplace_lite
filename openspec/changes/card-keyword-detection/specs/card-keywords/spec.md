## ADDED Requirements

### Requirement: Catalog payload exposes per-card keyword tags

The card catalog (`/api/cards/all`) SHALL include a `keywords` field on every card. The field MUST be an array of canonical keyword identifiers; cards with no recognized keywords MUST receive an empty array (`[]`), never `null` or a missing field.

The set of recognized keyword identifiers MUST be exactly:

```
TAUNT, BATTLECRY, DEATHRATTLE, CHARGE, RUSH,
DIVINE_SHIELD, WINDFURY, STEALTH, POISONOUS,
LIFESTEAL, SECRET, SPELLPOWER, COMBO
```

The order of identifiers in each card's array MUST be deterministic and consistent across catalog rebuilds.

#### Scenario: Card with a single keyword tag

- **WHEN** the catalog includes a card whose underlying `GameTag.TAUNT` is set (e.g. Sen'jin Shieldmasta, `EX1_finkle` or any taunt minion)
- **THEN** that card's payload contains `"keywords": ["TAUNT"]`

#### Scenario: Card with multiple keyword tags

- **WHEN** the catalog includes a card whose underlying `GameTag.BATTLECRY` and `GameTag.DEATHRATTLE` are both set
- **THEN** that card's payload contains both `"BATTLECRY"` and `"DEATHRATTLE"` in its `keywords` array
- **AND** the order matches the order in the canonical keyword list

#### Scenario: Card with no keyword tags

- **WHEN** the catalog includes a vanilla minion (e.g. Boulderfist Ogre, `CS2_200`) with no boolean keyword tags
- **THEN** that card's payload contains `"keywords": []`

#### Scenario: Card whose rules text mentions a keyword without granting it

- **WHEN** the catalog includes a card whose rules text contains the substring "战吼" or "Battlecry" but whose `GameTag.BATTLECRY` is not set (e.g. a card that *triggers* battlecries but does not have one)
- **THEN** the card's payload does NOT include `"BATTLECRY"` in its `keywords` array

#### Scenario: Spell-damage card uses the SPELLPOWER identifier

- **WHEN** the catalog includes a card with nonzero `GameTag.SPELLPOWER` (e.g. Kobold Geomancer)
- **THEN** that card's payload contains `"SPELLPOWER"` in its `keywords` array
- **AND** does NOT contain a numeric value or a different identifier (e.g. "SPELL_DAMAGE" or "+1 Spell Damage")

### Requirement: Card-name strings are not treated as keywords

No keyword identifier in the catalog SHALL correspond to a card name. Specifically, "法力浮龙" / "Mana Wyrm" MUST NOT appear as a keyword in any card's `keywords` array, in the canonical keyword list, or in any keyword-display label.

#### Scenario: Mana Wyrm card row

- **WHEN** the Mana Wyrm card (`NEW1_012`) is shown in the catalog
- **THEN** its `keywords` array does NOT contain any identifier whose label is "法力浮龙" or "Mana Wyrm"

#### Scenario: Filter rail keyword chip set

- **WHEN** the FilterRail renders its keyword chip group
- **THEN** none of the chips display the text "法力浮龙" or "Mana Wyrm"

### Requirement: Client localizes keywords through a single label map

The client SHALL provide one localization map keyed by canonical keyword identifier, with a label per supported locale (at minimum `zh` and `en`). All keyword UI affordances (filter chips, card-row badges, future tooltips) MUST resolve display text through this map; no other component may hardcode keyword display strings.

#### Scenario: Localization map covers every canonical identifier

- **WHEN** the client loads the keyword label map
- **THEN** the map contains an entry with non-empty `zh` and `en` strings for every identifier in the canonical keyword list
- **AND** the map contains no extra entries for identifiers outside the canonical list

#### Scenario: Card-row badge uses the label map

- **WHEN** a card with `keywords: ["DIVINE_SHIELD"]` is rendered in `CardRow` under a zh locale
- **THEN** the badge text is "圣盾" (resolved via the label map)
- **AND** the same card under en locale renders "Divine Shield"

### Requirement: Filter rail matches by canonical identifier

The FilterRail keyword chips SHALL store and emit canonical keyword identifiers (e.g. `"TAUNT"`), not display labels. Filtering MUST match a card iff `card.keywords` includes at least one of the selected identifiers (OR semantics across selected chips).

#### Scenario: Selecting a single chip filters to its keyword

- **WHEN** the user selects only the "嘲讽" / Taunt chip
- **THEN** the visible card grid contains only cards whose `keywords` array includes `"TAUNT"`

#### Scenario: Selecting two chips ORs the results

- **WHEN** the user selects the Taunt chip and the Divine Shield chip
- **THEN** the visible card grid includes every card whose `keywords` array includes either `"TAUNT"` or `"DIVINE_SHIELD"` (or both)

#### Scenario: Card text containing a keyword phrase does not match

- **WHEN** the user selects the Battlecry chip
- **AND** a card's rules text contains the phrase "战吼" but its `keywords` array does not include `"BATTLECRY"`
- **THEN** that card is NOT included in the filtered results

### Requirement: Card-row badge reflects the card's first canonical keyword

`CardRow` SHALL render a keyword badge derived from `card.keywords[0]` (the first entry in the canonical-list-ordered array) when the array is non-empty. When the array is empty, no keyword badge is rendered.

#### Scenario: First-keyword badge is deterministic

- **WHEN** a card has `keywords: ["BATTLECRY", "COMBO"]`
- **THEN** the row renders a single keyword badge labeled "战吼" / "Battlecry"
- **AND** does not render a "连击" / "Combo" badge

#### Scenario: No badge for vanilla minion

- **WHEN** Boulderfist Ogre is rendered
- **THEN** no keyword badge appears on its row

### Requirement: Server exposes a debug-only candidate-keyword report

When debug mode is enabled, the server SHALL expose a `GET /api/cards/keyword-candidates` endpoint that returns a histogram of boolean GameTags present on any collectible card that are NOT in the canonical keyword list AND NOT in a curated cosmetic/internal deny-list. Each entry MUST include the tag name, the count of cards carrying it, and up to three example card ids. The endpoint MUST NOT be reachable when debug mode is disabled.

The candidate report MUST NOT be surfaced anywhere in the user-facing UI.

#### Scenario: Endpoint returns 404 in production

- **WHEN** the server runs without `FLASK_DEBUG`/`DEBUG_KEYWORDS` enabled
- **AND** a client requests `/api/cards/keyword-candidates`
- **THEN** the response status is 404

#### Scenario: Endpoint returns histogram in debug mode

- **WHEN** the server runs with `FLASK_DEBUG=1`
- **AND** a client requests `/api/cards/keyword-candidates`
- **THEN** the response status is 200
- **AND** the body is a JSON object `{ "candidates": [...] }`
- **AND** each entry has shape `{ "tag": <enum_name>, "count": <int>, "examples": <up-to-3-card-ids> }`
- **AND** no entry's `tag` is one of the 13 canonical keyword identifiers
- **AND** no entry's `tag` is on the cosmetic-tag deny-list (`ELITE`, `COLLECTIBLE`, `PREMIUM`, `AURA`, `IMMUNE`, `IMMUNE_WHILE_ATTACKING`, `FROZEN`, `EXHAUSTED`, `CANT_ATTACK`, `CANT_BE_TARGETED_BY_SPELLS`, `OVERLOAD`, `SILENCE`, `RECRUIT`, `QUEST`, `INSPIRE`, `JADE_GOLEM`, `ADJACENT_BUFF`)
