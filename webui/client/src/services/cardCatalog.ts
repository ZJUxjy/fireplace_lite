import type { Card, CardType, Rarity } from '../types/deck';
import { KEYWORDS, type Keyword } from '../types/deck';

export { KEYWORDS };
export type { Keyword };

let _catalog: Card[] | null = null;
let _byId: Map<string, Card> | null = null;
let _loadPromise: Promise<Card[]> | null = null;

/** True once the catalog has been fetched and cached in this tab. */
export function isCatalogLoaded(): boolean {
  return _catalog !== null;
}

export async function loadCatalog(): Promise<Card[]> {
  if (_catalog) return _catalog;
  if (_loadPromise) return _loadPromise;

  _loadPromise = fetch('/api/cards/all')
    .then(r => {
      if (!r.ok) throw new Error(`catalog fetch failed: ${r.status}`);
      return r.json();
    })
    .then(data => {
      _catalog = data.cards as Card[];
      _byId = new Map(_catalog.map(c => [c.id, c]));
      return _catalog;
    })
    .catch(err => {
      _loadPromise = null;
      throw err;
    });
  return _loadPromise;
}

export function getCardById(id: string): Card | undefined {
  return _byId?.get(id);
}

export function getCatalogSync(): Card[] {
  return _catalog ?? [];
}

/** Localization map for canonical keywords. Single source of truth for the
 * UI; the FilterRail chip group and CardRow badge both render via this map. */
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

export function cardHasKeyword(card: Card, kw: Keyword): boolean {
  return card.keywords.includes(kw);
}

export type CardFilter = {
  cardClass?: string;
  includeNeutral?: boolean;
  costs?: Set<number>;
  types?: Set<CardType>;
  rarities?: Set<Rarity>;
  races?: Set<string>;
  sets?: Set<string>;
  keywords?: Set<Keyword>;
  search?: string;
};

export function filterCards(catalog: Card[], filter: CardFilter): Card[] {
  const q = filter.search?.trim().toLowerCase();
  return catalog.filter(c => {
    if (filter.cardClass) {
      if (filter.includeNeutral) {
        if (c.card_class !== filter.cardClass && c.card_class !== 'NEUTRAL') return false;
      } else {
        if (c.card_class !== filter.cardClass) return false;
      }
    }
    if (filter.costs && filter.costs.size > 0) {
      const bucket = c.cost >= 7 ? 7 : c.cost;
      if (!filter.costs.has(bucket)) return false;
    }
    if (filter.types && filter.types.size > 0) {
      if (!filter.types.has(c.type)) return false;
    }
    if (filter.rarities && filter.rarities.size > 0) {
      if (!filter.rarities.has(c.rarity)) return false;
    }
    if (filter.races && filter.races.size > 0) {
      if (!c.race || !filter.races.has(c.race)) return false;
    }
    if (filter.sets && filter.sets.size > 0) {
      if (!filter.sets.has(c.card_set)) return false;
    }
    if (filter.keywords && filter.keywords.size > 0) {
      let any = false;
      for (const k of filter.keywords) {
        if (c.keywords.includes(k)) { any = true; break; }
      }
      if (!any) return false;
    }
    if (q) {
      const matchZh = c.name_zh.toLowerCase().includes(q);
      const matchEn = c.name_en.toLowerCase().includes(q);
      if (!matchZh && !matchEn) return false;
    }
    return true;
  });
}

export function sortCards(cards: Card[]): Card[] {
  return [...cards].sort((a, b) =>
    a.cost - b.cost || a.name_zh.localeCompare(b.name_zh)
  );
}
