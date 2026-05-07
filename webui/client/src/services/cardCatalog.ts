import type { Card, CardType, Rarity } from '../types/deck';
import { KEYWORDS, type Keyword } from '../types/deck';
import * as catalogStore from './catalogStore';

export { KEYWORDS };
export type { Keyword };

let _catalog: Card[] | null = null;
let _byId: Map<string, Card> | null = null;
let _loadPromise: Promise<Card[]> | null = null;

const PAGE_SIZE = 200;

/** True once the catalog has been fetched and cached in this tab. */
export function isCatalogLoaded(): boolean {
  return _catalog !== null;
}

export type CatalogProgress = { loaded: number; total: number };

type StreamOpts = {
  onChunk?: (cards: Card[], progress: CatalogProgress) => void;
  signal?: AbortSignal;
};

type PageResponse = {
  cards: Card[];
  cursor: number;
  size: number;
  next_cursor: number | null;
  total: number;
  etag: string;
};

function commitCatalog(cards: Card[], _etag: string) {
  _catalog = cards;
  _byId = new Map(cards.map(c => [c.id, c]));
}

/** Stream the catalog in pages, calling onChunk after each page. The
 * returned promise resolves with the complete array once the final page
 * arrives. On a return visit with IndexedDB-cached data, fires onChunk
 * synchronously with the cached array, then revalidates with If-None-Match
 * and replaces atomically if the server's etag has changed. */
export async function streamCatalog(opts: StreamOpts = {}): Promise<Card[]> {
  const { onChunk, signal } = opts;

  // Step 1 — IndexedDB hot start. Paint immediately if we have a cached copy.
  const cached = await catalogStore.get();
  if (cached && cached.cards.length > 0) {
    commitCatalog(cached.cards, cached.etag);
    onChunk?.(cached.cards, { loaded: cached.cards.length, total: cached.cards.length });

    // Revalidate with a cheap probe (1-card page).
    const headers: Record<string, string> = { 'If-None-Match': `"${cached.etag}"` };
    let probeStatus = 200;
    let probeBody: PageResponse | null = null;
    try {
      const r = await fetch(`/api/cards/page?cursor=0&size=1`, { headers, signal });
      probeStatus = r.status;
      if (r.status === 200) probeBody = await r.json();
    } catch (e) {
      if ((e as Error).name === 'AbortError') throw e;
      // Network failure during revalidation — keep the cached copy.
      return cached.cards;
    }
    if (probeStatus === 304) {
      return cached.cards;  // still valid
    }
    if (probeBody && probeBody.etag === cached.etag) {
      return cached.cards;  // server returned 200 but etag matches; rare
    }
    // Fall through: etag changed, stream a fresh copy. We deliberately
    // keep the in-memory _catalog populated with the old data during the
    // stream so UI lookups don't go undefined.
  }

  // Step 2 — Fresh paged stream.
  const pending: Card[] = [];
  let cursor = 0;
  let total = 0;
  let etag = '';

  while (true) {
    const r = await fetch(`/api/cards/page?cursor=${cursor}&size=${PAGE_SIZE}`, { signal });
    if (!r.ok) throw new Error(`catalog page fetch failed: ${r.status}`);
    const page = (await r.json()) as PageResponse;
    pending.push(...page.cards);
    total = page.total;
    etag = page.etag;
    onChunk?.(pending.slice(), { loaded: pending.length, total });
    if (page.next_cursor === null) break;
    cursor = page.next_cursor;
  }

  // Atomic swap into the in-memory cache.
  commitCatalog(pending, etag);

  // Persist to IDB; failures don't matter — we still have the in-memory copy.
  catalogStore.put({ etag, cards: pending, saved_at: Date.now() }).catch(() => {});

  return pending;
}

export async function loadCatalog(): Promise<Card[]> {
  if (_catalog) return _catalog;
  if (_loadPromise) return _loadPromise;
  _loadPromise = streamCatalog().catch(err => {
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
  COLOSSAL:      { zh: '巨型',     en: 'Colossal' },
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
