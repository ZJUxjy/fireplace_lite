## Context

The deck builder ships a "keyword" filter (chips in `FilterRail`) and shows a small keyword tag on each `CardRow`. Both currently rely on substring matching against the localized rules text (`text_zh`):

```ts
// services/cardCatalog.ts
export const KEYWORD_TOKENS = [
  '嘲讽', '战吼', '亡语', '圣盾', '风怒', '突袭', '冲锋',
  '潜行', '剧毒', '吸血', '奥秘', '法力浮龙', '沉默',
];
export function cardHasKeyword(card, kw) { return card.text_zh.includes(kw); }
```

```ts
// CardRow.tsx — second hardcoded list, drift-prone
const KEYWORDS = ['嘲讽', '冲锋', '突袭', '亡语', '战吼', '圣盾', '风怒',
                  '潜行', '剧毒', '吸血', '奥秘', '法力浮龙'] as const;
function detectKeyword(text) { for (const k of KEYWORDS) if (text.includes(k)) return k; return null; }
```

This is wrong on two axes:

1. **`法力浮龙` is a card name** (Mana Wyrm). Including it in the keyword list shows a non-keyword chip in the filter UI and adds spurious badges to the Mana Wyrm row.
2. **Substring on rules text is unreliable.** "战吼" appears inside descriptive text like "下一张随从获得+战吼" without the card itself having Battlecry. Translation drift can also miss cards (some keyword cards say "战吼:" while older translations use "战嚎"). Two independent hardcoded lists guarantee divergence.

Hearthstone's data already encodes keywords as boolean `GameTag`s on each card. The fireplace simulator depends on `hearthstone.enums.GameTag` and exposes them via `card.tags[GameTag.X]` on every card instance. We have all 13 needed tags available locally:

```
present: ['BATTLECRY', 'CHARGE', 'COMBO', 'DEATHRATTLE', 'DIVINE_SHIELD',
         'LIFESTEAL', 'POISONOUS', 'RUSH', 'SECRET', 'SPELLPOWER',
         'STEALTH', 'TAUNT', 'WINDFURY']
```

The catalog is built once on the server (`webui/server/card_catalog.py`) and cached behind an ETag, so reading these tags adds no per-request cost.

## Goals / Non-Goals

**Goals:**

- Catalog payload contains an authoritative `keywords: string[]` field per card, sourced from GameTag, not text.
- Single source of truth for the canonical keyword list and its zh/en localization.
- Filter rail and card-row badge both consume that one source.
- Easy to extend: adding a new keyword is one edit (enum, label) — server picks it up automatically because tags are read by name.
- Existing tests pass; new test covers the extraction.

**Non-Goals:**

- Keyword **definitions** (what Taunt does). The simulator already enforces gameplay; we only surface display tags.
- Multi-keyword display on `CardRow`. Showing the *first* keyword is enough for the badge slot. The Filter Rail expansion can hover to reveal all.
- Detecting *keyword-granting effects* (e.g. "give your minions Taunt"). Out of scope — those cards do not themselves *have* Taunt.
- Backwards-compat shims for old `KEYWORD_TOKENS` consumers. The catalog is loaded fresh on each tab; clients that hold stale code will see chips with display-name labels but enum-keyed state — they should hard-refresh.

## Decisions

### D1 — Source: `GameTag` boolean flags, not card text

We extract keywords during `build_catalog()` by checking each `GameTag` enum value on the card. We use the enum *name* (e.g. `"TAUNT"`, `"SPELLPOWER"`) as the catalog field value.

**Why:** authoritative, locale-independent, free of false positives. The fireplace simulator already exposes these tags on every `Card`; we are simply forwarding what is already canonical.

**Alternatives rejected:**

- *Keep substring matching, just remove `法力浮龙`.* Doesn't fix the false-positive class of bugs and keeps two lists in drift.
- *Maintain a hand-curated card-id → keywords table.* Thousands of cards; will rot.
- *Use card.text regex per keyword.* Localization drift; "亡语:" vs "亡语：" punctuation differences; no canonical list of phrasings.

### D2 — Canonical key is the enum name, not the display label

Catalog ships `["TAUNT", "DIVINE_SHIELD"]`, not `["嘲讽", "圣盾"]`. The client localizes via a `KEYWORD_LABELS` map.

**Why:**

- The client already supports zh/en for card names; same separation applies here.
- Filter state stores stable identifiers, not display strings. State survives locale switches and is comparable across server/client.
- "Spell Damage" → `SPELLPOWER` makes the underlying enum name visible for anyone debugging a card payload.

### D3 — Keyword set is a fixed list of 13, defined once

```ts
export const KEYWORDS = [
  'TAUNT', 'BATTLECRY', 'DEATHRATTLE', 'CHARGE', 'RUSH',
  'DIVINE_SHIELD', 'WINDFURY', 'STEALTH', 'POISONOUS',
  'LIFESTEAL', 'SECRET', 'SPELLPOWER', 'COMBO',
] as const;
export type Keyword = typeof KEYWORDS[number];

export const KEYWORD_LABELS: Record<Keyword, { zh: string; en: string }> = {
  TAUNT:         { zh: '嘲讽',     en: 'Taunt' },
  BATTLECRY:     { zh: '战吼',     en: 'Battlecry' },
  DEATHRATTLE:   { zh: '亡语',     en: 'Deathrattle' },
  CHARGE:        { zh: '冲锋',     en: 'Charge' },
  RUSH:          { zh: '突袭',     en: 'Rush' },
  DIVINE_SHIELD: { zh: '圣盾',     en: 'Divine Shield' },
  WINDFURY:      { zh: '风怒',     en: 'Windfury' },
  STEALTH:       { zh: '潜行',     en: 'Stealth' },
  POISONOUS:     { zh: '剧毒',     en: 'Poisonous' },
  LIFESTEAL:     { zh: '吸血',     en: 'Lifesteal' },
  SECRET:        { zh: '奥秘',     en: 'Secret' },
  SPELLPOWER:    { zh: '法术伤害', en: 'Spell Damage' },
  COMBO:         { zh: '连击',     en: 'Combo' },
};
```

**Why this list:** matches the keywords most commonly used as deck-building filters and most visually relevant on a card row. Excludes cosmetic tags (`ELITE`), aura-only tags (`AURA`), and effect modifiers (`OVERLOAD`, which is shown numerically not as a chip).

We omit `SILENCE` (it is a *spell effect*, not something a card *has* — Ironbeak Owl doesn't have the SILENCE tag, it casts a silence). The current substring list incorrectly includes `沉默`; we drop it.

We omit `MANA_WYRM` 😉.

### D4 — Catalog field shape

```python
# server: card_catalog.py — inside build_catalog()
KEYWORD_TAGS = {
    "TAUNT": GameTag.TAUNT,
    "BATTLECRY": GameTag.BATTLECRY,
    "DEATHRATTLE": GameTag.DEATHRATTLE,
    "CHARGE": GameTag.CHARGE,
    "RUSH": GameTag.RUSH,
    "DIVINE_SHIELD": GameTag.DIVINE_SHIELD,
    "WINDFURY": GameTag.WINDFURY,
    "STEALTH": GameTag.STEALTH,
    "POISONOUS": GameTag.POISONOUS,
    "LIFESTEAL": GameTag.LIFESTEAL,
    "SECRET": GameTag.SECRET,
    "SPELLPOWER": GameTag.SPELLPOWER,
    "COMBO": GameTag.COMBO,
}

def _extract_keywords(card) -> list[str]:
    tags = card.tags  # dict-like {GameTag: int}
    return [name for name, tag in KEYWORD_TAGS.items() if tags.get(tag)]
```

`SPELLPOWER` is a numeric tag in the simulator (it stores +1, +2, etc.), but we treat any nonzero value as "this card has spell damage" — falsy 0 means absent.

The catalog row gets:

```json
{ "id": "EX1_277", "keywords": ["BATTLECRY"], ... }
```

Cards with no recognized keyword get `"keywords": []` (always present, never null) — simplifies client.

### D5 — Filter and badge implementations

**`filterCards`:**

```ts
if (filter.keywords && filter.keywords.size > 0) {
  let any = false;
  for (const k of filter.keywords) {
    if (card.keywords.includes(k)) { any = true; break; }
  }
  if (!any) return false;
}
```

OR semantics across selected chips (a card matching *any* selected keyword passes), consistent with how the existing rarity/race/set chips work.

**`CardRow` badge:** show `card.keywords[0]` if present, localized via `KEYWORD_LABELS`. Order in the catalog array matches the order in `KEYWORDS` const, so the badge is deterministic — Battlecry will always win over Combo on a card that has both.

### D6 — ETag invalidation

`build_catalog()` currently hashes the row payload to compute the ETag. Adding a new field changes every row's hash → fresh ETag → clients receive new payload on next load. No special migration needed.

## Risks / Trade-offs

- **Risk: cards we deem implemented but whose XML has incomplete tags.** → Mitigation: the test suite picks one canonical card per keyword (e.g. Argent Squire for Divine Shield, Sen'jin Shieldmasta for Taunt) and asserts the keyword appears. If we ship a card whose tags are missing, the test fails on import.
- **Risk: i18n drift (e.g. "法力之伤" vs "法术伤害").** → Mitigation: labels live in code and are reviewed in PR. The wire format (`SPELLPOWER`) never changes.
- **Trade-off: dropping `沉默` from the chip list** removes a filter people might miss. We accept this — silence is an effect, not a tag, and the current behavior was misleading. We can reintroduce a "Silence-effect cards" filter later via a curated card-id list if there's demand.
- **Trade-off: only first keyword in the badge slot.** Cards like Eaglehorn Bow (Secret + Battlecry-trigger combo) won't show all their keywords on the row. The hover `CardPreview` already shows full rules text, so this is acceptable.
- **Risk: server build error on `card.tags.get(...)` if `card` is a bare metadata object rather than an instance.** → Mitigation: verify in the test which API `build_catalog` already uses; if it iterates raw XML rather than instance objects we adapt the extractor accordingly.
- **Risk: the catalog ETag changes once and invalidates every cached client copy.** → Mitigation: this is a one-time, intentional cost for correctness; the catalog endpoint already supports 304 so subsequent loads remain cheap.

## Migration Plan

1. Land server change behind no flag — catalog payload always includes `keywords: []` (never null). Old clients that don't read the field are unaffected.
2. Land client change in the same commit (or PR). Once deployed, client uses the new field.
3. No data migration needed (no persisted state references the old `KEYWORD_TOKENS` strings — saved decks store card IDs only).

### D7 — Semi-dynamic discovery for ops, never for the UI

The runtime keyword list is the fixed 13 from D3. To make it easy to spot a *missing* keyword (e.g. a future expansion adds something we didn't enumerate), `build_catalog()` ALSO compiles an internal "candidate keyword" report: a histogram of every boolean `GameTag` that is set on at least one collectible card, *minus* the 13 we already recognize and minus a known-cosmetic deny-list (`ELITE`, `COLLECTIBLE`, `PREMIUM`, `AURA`, `IMMUNE`, `IMMUNE_WHILE_ATTACKING`, `FROZEN`, `EXHAUSTED`, `CANT_ATTACK`, `CANT_BE_TARGETED_BY_SPELLS`, `OVERLOAD`, `SILENCE`, `RECRUIT`, `QUEST`, `INSPIRE`, `JADE_GOLEM`, `ADJACENT_BUFF`, plus anything matching `_$` or `_VALUE$`).

The report is exposed at `/api/cards/keyword-candidates` (debug endpoint) and gated behind `DEBUG_KEYWORDS` — `app.config.get("DEBUG_KEYWORDS")` true (set when `FLASK_DEBUG=1`). Returns:

```json
{
  "candidates": [
    { "tag": "WINDFURY_RAGE", "count": 1, "examples": ["EX1_xyz"] },
    ...
  ]
}
```

This lets a developer check, after pulling new XML, whether anything interesting slipped past the deny-list. No UI surfaces it; users never see candidate tags.

**Why semi-dynamic instead of fully dynamic:**

- The chip grid stays a stable 13 — no surprise drift between locales or expansions.
- Localization remains explicit (no auto-generated label).
- Discovery cost is one-time per build and dev-only; production never executes the report.

## Open Questions

- **Should "RECRUIT", "OVERLOAD", "QUEST" be in scope?** Recommendation: no for now — Recruit and Quest are old/niche; Overload is mana-numeric and has its own column. They live on the deny-list (D7) so they don't pollute the candidate report either.
- **Do we want en localization actually wired up?** The current UI is zh-only. We define `KEYWORD_LABELS` with both zh and en for forward-compatibility, but the FilterRail and CardRow can render `.zh` until the i18n switch is built.
