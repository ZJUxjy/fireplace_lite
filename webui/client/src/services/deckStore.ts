import type { Deck, Format, DeckCard } from '../types/deck';

export const DECKS_STORAGE_KEY = 'fireplace.decks.v1';
export const DECKS_SCHEMA_VERSION = 1;

type StoredEnvelope = {
  schema_version: number;
  decks: Record<string, Deck>;
};

function readEnvelope(): StoredEnvelope {
  try {
    const raw = localStorage.getItem(DECKS_STORAGE_KEY);
    if (!raw) return { schema_version: DECKS_SCHEMA_VERSION, decks: {} };
    const parsed = JSON.parse(raw) as StoredEnvelope;
    return migrate(parsed);
  } catch (e) {
    console.warn('[deckStore] failed to read localStorage, starting empty', e);
    return { schema_version: DECKS_SCHEMA_VERSION, decks: {} };
  }
}

function migrate(env: StoredEnvelope): StoredEnvelope {
  if (!env || typeof env.schema_version !== 'number') {
    return { schema_version: DECKS_SCHEMA_VERSION, decks: {} };
  }
  return env;
}

function writeEnvelope(env: StoredEnvelope): void {
  try {
    localStorage.setItem(DECKS_STORAGE_KEY, JSON.stringify(env));
  } catch (e) {
    console.error('[deckStore] write failed (quota?)', e);
    throw new Error('localStorage write failed');
  }
}

function isValidDeck(d: unknown): d is Deck {
  if (!d || typeof d !== 'object') return false;
  const x = d as Partial<Deck>;
  return Boolean(
    x.id && x.name && x.hero_class && x.format &&
    Array.isArray(x.cards) && x.created_at && x.updated_at
  );
}

export function listDecks(): Deck[] {
  const env = readEnvelope();
  return Object.values(env.decks).filter(isValidDeck)
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at));
}

export function getDeck(id: string): Deck | null {
  return readEnvelope().decks[id] ?? null;
}

export function saveDeck(deck: Deck): void {
  if (!isValidDeck(deck)) throw new Error('invalid deck shape');
  const env = readEnvelope();
  deck.updated_at = new Date().toISOString();
  env.decks[deck.id] = deck;
  writeEnvelope(env);
}

export function deleteDeck(id: string): void {
  const env = readEnvelope();
  delete env.decks[id];
  writeEnvelope(env);
}

export function newDeck(heroClass: string, name = '新卡组'): Deck {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    name,
    hero_class: heroClass,
    format: 'STANDARD',
    cards: [],
    created_at: now,
    updated_at: now,
  };
}

export function deckCardCount(deck: Deck): number {
  return deck.cards.reduce((sum, c) => sum + c.count, 0);
}

export function findCardInDeck(deck: Deck, cardId: string): DeckCard | undefined {
  return deck.cards.find(c => c.card_id === cardId);
}

export function addCardToDeck(deck: Deck, cardId: string, maxCount: number): boolean {
  if (deckCardCount(deck) >= 30) return false;
  const existing = findCardInDeck(deck, cardId);
  if (existing) {
    if (existing.count >= maxCount) return false;
    existing.count++;
  } else {
    deck.cards.push({ card_id: cardId, count: 1 });
  }
  return true;
}

export function removeCardFromDeck(deck: Deck, cardId: string): boolean {
  const idx = deck.cards.findIndex(c => c.card_id === cardId);
  if (idx < 0) return false;
  deck.cards[idx].count--;
  if (deck.cards[idx].count <= 0) deck.cards.splice(idx, 1);
  return true;
}

export function isDeckSavable(deck: Deck): { ok: boolean; reason?: string } {
  const total = deckCardCount(deck);
  if (total < 1) return { ok: false, reason: '卡组至少 1 张' };
  if (total > 30) return { ok: false, reason: `卡组超过 30 张(当前 ${total})` };
  return { ok: true };
}

export type DeckstringExportFormat = Format;

export async function importDeckFromDeckstring(deckstring: string, name: string): Promise<Deck> {
  const resp = await fetch('/api/decks/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ deckstring }),
  });
  const data = await resp.json();
  if (!data.valid) throw new Error(data.error || 'invalid deckstring');

  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    name,
    hero_class: data.hero_class,
    format: data.format,
    cards: data.cards.map((c: { card_id: string; count: number }) => ({
      card_id: c.card_id,
      count: c.count,
    })),
    created_at: now,
    updated_at: now,
  };
}
