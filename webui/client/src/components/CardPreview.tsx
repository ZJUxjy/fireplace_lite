import type { Card } from '../types/deck';
import './CardPreview.css';

type Props = {
  card: Card | null;
  anchor: HTMLElement | null;
};

const CLASS_LABEL: Record<string, string> = {
  MAGE: '法师', HUNTER: '猎人', PRIEST: '牧师', SHAMAN: '萨满',
  PALADIN: '圣骑士', WARLOCK: '术士', WARRIOR: '战士', ROGUE: '盗贼',
  DRUID: '德鲁伊', DEMONHUNTER: '恶魔猎手', NEUTRAL: '中立',
};
const TYPE_LABEL: Record<string, string> = {
  MINION: '随从', SPELL: '法术', WEAPON: '武器',
};
const RARITY_LABEL: Record<string, string> = {
  FREE: '免费', COMMON: '普通', RARE: '稀有', EPIC: '史诗', LEGENDARY: '传说',
};

const PREVIEW_WIDTH = 280;
const PREVIEW_HEIGHT_EST = 320;

function calcPosition(anchor: HTMLElement): React.CSSProperties {
  const rect = anchor.getBoundingClientRect();
  const gap = 12;

  // Horizontal: prefer right of anchor, but flip left if it would overflow
  let left: number;
  if (rect.right + gap + PREVIEW_WIDTH <= window.innerWidth) {
    left = rect.right + gap;
  } else {
    left = Math.max(gap, rect.left - PREVIEW_WIDTH - gap);
  }

  // Vertical: align with anchor top, clamp within viewport
  const top = Math.max(8, Math.min(window.innerHeight - PREVIEW_HEIGHT_EST - 8, rect.top - 40));

  return { left, top };
}

export default function CardPreview({ card, anchor }: Props) {
  if (!card || !anchor) return null;

  return (
    <div className="card-preview" style={calcPosition(anchor)}>
      <div className="card-preview__header">
        <span className="card-preview__cost">{card.cost}</span>
        <span className="card-preview__name">{card.name_zh}</span>
      </div>
      <div className="card-preview__meta">
        {TYPE_LABEL[card.type]} · {CLASS_LABEL[card.card_class] ?? card.card_class}
        {card.race ? ` · ${card.race}` : ''}
      </div>
      <div className="card-preview__stats">
        {card.type === 'MINION' && <>{card.attack ?? 0} 攻 / {card.health ?? 0} 血</>}
        {card.type === 'WEAPON' && <>{card.attack ?? 0} 攻 / {card.durability ?? 0} 耐久</>}
      </div>
      {card.text_zh && (
        <div className="card-preview__text" dangerouslySetInnerHTML={{ __html: card.text_zh }} />
      )}
      <div className="card-preview__footer">
        {RARITY_LABEL[card.rarity] ?? card.rarity} · {card.card_set} · {card.name_en}
      </div>
    </div>
  );
}
