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

export default function CardPreview({ card, anchor }: Props) {
  if (!card || !anchor) return null;
  const rect = anchor.getBoundingClientRect();
  const style: React.CSSProperties = {
    left: rect.right + 12,
    top: Math.max(8, Math.min(window.innerHeight - 320, rect.top - 40)),
  };

  return (
    <div className="card-preview" style={style}>
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
      {card.text_zh && <div className="card-preview__text">{card.text_zh}</div>}
      <div className="card-preview__footer">
        {RARITY_LABEL[card.rarity] ?? card.rarity} · {card.card_set} · {card.name_en}
      </div>
    </div>
  );
}
