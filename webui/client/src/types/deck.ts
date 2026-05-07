export type CardType = 'MINION' | 'SPELL' | 'WEAPON';
export type Format = 'STANDARD' | 'WILD' | 'CLASSIC';
export type Rarity = 'FREE' | 'COMMON' | 'RARE' | 'EPIC' | 'LEGENDARY';

/** Canonical mechanic-keyword identifiers. Order is the rendering order:
 * a card with multiple keywords picks the earliest one for its row badge.
 * Mirrors KEYWORD_TAGS in webui/server/card_catalog.py — keep the two in
 * sync. See openspec/changes/card-keyword-detection/design.md §D3. */
export const KEYWORDS = [
  'TAUNT', 'BATTLECRY', 'DEATHRATTLE', 'CHARGE', 'RUSH',
  'DIVINE_SHIELD', 'WINDFURY', 'STEALTH', 'POISONOUS',
  'LIFESTEAL', 'SECRET', 'SPELLPOWER', 'COMBO', 'COLOSSAL',
] as const;
export type Keyword = typeof KEYWORDS[number];

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
  keywords: Keyword[];
};

export type DeckCard = {
  card_id: string;
  count: number;
  /** True 表示后端在导入 deckstring 时把此卡标为未实现(spec §7:UI 灰显,开局拒绝) */
  unimplemented?: boolean;
};

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
