import type { Card } from '../types/deck';
import './CardRow.css';

type Props = {
  card: Card;
  count?: number;
  disabled?: boolean;
  showRightCount?: boolean;
  onClick?: () => void;
  onHoverStart?: (card: Card, anchor: HTMLElement) => void;
  onHoverEnd?: () => void;
  onContextMenu?: (e: React.MouseEvent) => void;
};

const TYPE_BADGE: Record<string, string> = {
  MINION: '随',
  SPELL: '法',
  WEAPON: '武',
};

export default function CardRow({
  card, count, disabled, showRightCount,
  onClick, onHoverStart, onHoverEnd, onContextMenu,
}: Props) {
  const cls = card.card_class === 'NEUTRAL' ? 'neutral' : 'class';
  const right = showRightCount && count
    ? `×${count}`
    : card.type === 'MINION'
      ? `${card.attack ?? 0}/${card.health ?? 0}`
      : card.type === 'WEAPON'
        ? `${card.attack ?? 0}/${card.durability ?? 0}`
        : TYPE_BADGE[card.type] ?? '';

  return (
    <div
      className={`card-row card-row--${cls} ${disabled ? 'card-row--disabled' : ''}`}
      onClick={disabled ? undefined : onClick}
      onMouseEnter={(e) => onHoverStart?.(card, e.currentTarget)}
      onMouseLeave={onHoverEnd}
      onContextMenu={onContextMenu}
    >
      <span className="card-row__cost">{card.cost}</span>
      <span className="card-row__name">{card.name_zh}</span>
      <span className="card-row__right">{right}</span>
    </div>
  );
}
