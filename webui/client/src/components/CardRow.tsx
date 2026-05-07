import type { Card } from '../types/deck';
import './CardRow.css';

type Props = {
  card: Card;
  /** Copies already in the active deck (browse mode passes 0; edit mode passes 0..max). */
  count?: number;
  disabled?: boolean;
  onClick?: () => void;
  onHoverStart?: (card: Card, anchor: HTMLElement) => void;
  onHoverEnd?: () => void;
  onContextMenu?: (e: React.MouseEvent) => void;
};

const TYPE_SHORT: Record<string, string> = {
  MINION: '随', SPELL: '法', WEAPON: '武',
};
const RACE_LABEL: Record<string, string> = {
  DRAGON: '龙', BEAST: '野兽', MURLOC: '鱼人', DEMON: '恶魔',
  ELEMENTAL: '元素', MECH: '机械', MECHANICAL: '机械',
  PIRATE: '海盗', TOTEM: '图腾',
  UNDEAD: '亡灵', NAGA: '娜迦', QUILBOAR: '野猪人',
  ALL: '全部',
};
const KEYWORDS = ['嘲讽', '冲锋', '突袭', '亡语', '战吼', '圣盾', '风怒', '潜行', '剧毒', '吸血', '奥秘', '法力浮龙'] as const;

function detectKeyword(text: string): string | null {
  for (const k of KEYWORDS) if (text.includes(k)) return k;
  return null;
}

export default function CardRow({
  card, count, disabled, onClick, onHoverStart, onHoverEnd, onContextMenu,
}: Props) {
  const rarity = (card.rarity ?? '').toLowerCase();
  const isLegendary = card.rarity === 'LEGENDARY';
  const rarityClass =
    rarity === 'legendary' ? 'row--legendary' :
    rarity === 'epic' ? 'row--epic' :
    rarity === 'rare' ? 'row--rare' : '';

  const isMinion = card.type === 'MINION';
  const isWeapon = card.type === 'WEAPON';
  const showStats = isMinion || isWeapon;
  const atk = card.attack ?? 0;
  const hp = isWeapon ? (card.durability ?? 0) : (card.health ?? 0);

  const tribe = card.race && card.race !== 'INVALID' ? RACE_LABEL[card.race] ?? card.race : null;
  const keyword = detectKeyword(card.text_zh);

  const max = card.max_count;
  const showCount = count !== undefined;
  const c = count ?? 0;
  const countClass =
    c === 0 ? 'owned--zero' :
    c >= max ? 'owned--max' : '';

  return (
    <div
      className={`row ${rarityClass} ${disabled ? 'row--disabled' : ''}`}
      onClick={disabled ? undefined : onClick}
      onMouseEnter={(e) => onHoverStart?.(card, e.currentTarget)}
      onMouseLeave={onHoverEnd}
      onContextMenu={onContextMenu}
    >
      <div className="mana">{card.cost}</div>

      <div className="row__main">
        <span className={`row__name ${isLegendary ? 'row__name--legendary' : ''}`}>
          {isLegendary && <span className="row__star">✦</span>}
          {card.name_zh}
        </span>
        {tribe && <span className="tag">{tribe}</span>}
        {keyword && <span className="tag tag--keyword">{keyword}</span>}
      </div>

      <div className="row__right">
        {showStats ? (
          <div className="stats">
            <span className="stats__atk">{atk}</span>
            <span className="stats__hp">{hp}</span>
          </div>
        ) : (
          <div className={`row__type row__type--${card.type.toLowerCase()}`} title={TYPE_SHORT[card.type]}>
            {TYPE_SHORT[card.type]}
          </div>
        )}

        {showCount && (
          <span className={`owned ${countClass}`}>{c}/{max}</span>
        )}
        <span className={`rarity rarity--${rarity}`} />
      </div>
    </div>
  );
}
