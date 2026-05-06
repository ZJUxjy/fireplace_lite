export type CardType = 'MINION' | 'SPELL' | 'WEAPON';
export type Format = 'STANDARD' | 'WILD' | 'CLASSIC';
export type Rarity = 'FREE' | 'COMMON' | 'RARE' | 'EPIC' | 'LEGENDARY';

export type Card = {
  id: string;
  dbf_id: number;
  name_zh: string;
  name_en: string;
  text_zh: string;
  text_en: string;
  cost: number;
  attack?: number;
  health?: number;
  durability?: number;
  type: CardType;
  card_class: string;
  rarity: Rarity;
  card_set: string;
  race?: string;
  collectible: true;
  max_count: number;
};

export type DeckCard = { card_id: string; count: number };

export type Deck = {
  id: string;
  name: string;
  hero_class: string;
  format: Format;
  cards: DeckCard[];
  created_at: string;
  updated_at: string;
};

export type DeckSpec =
  | { type: 'deckstring'; value: string }
  | { type: 'random'; card_class: string };

export const HERO_CLASSES = [
  'MAGE', 'HUNTER', 'PRIEST', 'SHAMAN', 'PALADIN',
  'WARLOCK', 'WARRIOR', 'ROGUE', 'DRUID', 'DEMONHUNTER',
] as const;
