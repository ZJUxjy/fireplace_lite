import { useLayoutEffect, useRef, useState, type CSSProperties } from 'react';
import DOMPurify from 'dompurify';
import type { Card } from '../types/deck';
import './CardPreview.css';

type Props = {
  card: Card | null;
  anchor: HTMLElement | null;
};

const PREVIEW_GAP = 12;
const VIEWPORT_PAD = 8;

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

/** Maximal HTML Blizzard-style card text uses; strip everything else before render. */
function sanitizeCardHtml(raw: string): string {
  const withBreaks = raw.replace(/\r\n/g, '\n').replace(/\n/g, '<br />');
  return DOMPurify.sanitize(withBreaks, {
    ALLOWED_TAGS: ['b', 'i', 'br', 'strong', 'em'],
    ALLOWED_ATTR: [],
  });
}

function computeCardPreviewPosition(
  anchor: HTMLElement,
  popupW: number,
  popupH: number,
): { left: number; top: number } {
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  if (anchor === document.body) {
    return {
      left: Math.max(VIEWPORT_PAD, (vw - popupW) / 2),
      top: Math.max(VIEWPORT_PAD, (vh - popupH) / 2),
    };
  }

  const rect = anchor.getBoundingClientRect();
  let left = rect.right + PREVIEW_GAP;
  const fitsRight = left + popupW <= vw - VIEWPORT_PAD;

  if (!fitsRight) {
    left = rect.left - PREVIEW_GAP - popupW;
  }
  if (left < VIEWPORT_PAD) {
    left = VIEWPORT_PAD;
  }
  if (left + popupW > vw - VIEWPORT_PAD) {
    left = Math.max(VIEWPORT_PAD, vw - popupW - VIEWPORT_PAD);
  }

  let top = rect.top + rect.height / 2 - popupH / 2;
  top = Math.max(VIEWPORT_PAD, Math.min(top, vh - popupH - VIEWPORT_PAD));
  return { left, top };
}

export default function CardPreview({ card, anchor }: Props) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [placement, setPlacement] = useState<Pick<CSSProperties, 'left' | 'top' | 'visibility'>>({
    left: -9999,
    top: 0,
    visibility: 'hidden',
  });

  const syncPosition = (): void => {
    if (!card || !anchor) return;
    const node = rootRef.current;
    if (!node) return;
    const w = node.offsetWidth;
    const h = node.offsetHeight;
    const { left, top } = computeCardPreviewPosition(anchor, w, h);
    setPlacement({ left, top, visibility: 'visible' });
  };

  useLayoutEffect(() => {
    syncPosition();

    window.addEventListener('resize', syncPosition);
    window.addEventListener('scroll', syncPosition, true);

    let ro: ResizeObserver | undefined;
    if (typeof ResizeObserver !== 'undefined' && rootRef.current) {
      ro = new ResizeObserver(() => syncPosition());
      ro.observe(rootRef.current);
    }

    return () => {
      window.removeEventListener('resize', syncPosition);
      window.removeEventListener('scroll', syncPosition, true);
      ro?.disconnect();
    };
  }, [card, anchor]);

  if (!card || !anchor) return null;

  const style: CSSProperties = {
    left: placement.left,
    top: placement.top,
    visibility: placement.visibility,
  };

  return (
    <div ref={rootRef} className="card-preview" style={style}>
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
      {card.text_zh ? (
        <div
          className="card-preview__text"
          // eslint-disable-next-line react/no-danger -- sanitized via DOMPurify
          dangerouslySetInnerHTML={{ __html: sanitizeCardHtml(card.text_zh) }}
        />
      ) : null}
      <div className="card-preview__footer">
        {RARITY_LABEL[card.rarity] ?? card.rarity} · {card.card_set} · {card.name_en}
      </div>
    </div>
  );
}
