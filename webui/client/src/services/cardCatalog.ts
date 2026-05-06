import type { Card, CardType } from '../types/deck';

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

export type CardFilter = {
  cardClass?: string;
  includeNeutral?: boolean;
  costs?: Set<number>;
  types?: Set<CardType>;
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
