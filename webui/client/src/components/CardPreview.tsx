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
const RACE_LABEL: Record<string, string> = {
  DRAGON: '龙', BEAST: '野兽', MURLOC: '鱼人', DEMON: '恶魔',
  ELEMENTAL: '元素', MECH: '机械', MECHANICAL: '机械',
  PIRATE: '海盗', TOTEM: '图腾',
  UNDEAD: '亡灵', NAGA: '娜迦', QUILBOAR: '野猪人',
  ALL: '全部',
};
const SET_LABEL: Record<string, string> = {
  CORE: '核心', EXPERT1: '经典', NAXX: '纳克萨玛斯', GVG: '哥哥侏儒',
  BRM: '黑石山', TGT: '冠军赛', LOE: '探险者协会', OG: '上古之神',
  KARA: '卡拉赞', GANGS: '加基森', UNGORO: '安戈洛',
  ICECROWN: '冰封王座', LOOTAPALOOZA: '狗头人', GILNEAS: '女巫森林',
  BOOMSDAY: '砰砰计划', TROLL: '拉斯塔哈', DALARAN: '暗影崛起',
  ULDUM: '奥丹姆', SCHOLOMANCE: '通灵学院', BLACK_TEMPLE: '外域灰烬',
  DRAGONS: '巨龙降临',
};
const RARITY_LABEL: Record<string, string> = {
  FREE: '免费', COMMON: '普通', RARE: '稀有', EPIC: '史诗', LEGENDARY: '传说',
};

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

  const isMinion = card.type === 'MINION';
  const isWeapon = card.type === 'WEAPON';
  const showStats = isMinion || isWeapon;
  const atk = card.attack ?? 0;
  const hp = isWeapon ? (card.durability ?? 0) : (card.health ?? 0);
  const rarity = (card.rarity ?? '').toLowerCase();

  const tribe = card.race && card.race !== 'INVALID' ? RACE_LABEL[card.race] ?? card.race : null;
  const setLabel = SET_LABEL[card.card_set] ?? card.card_set;
  const rarityLabel = RARITY_LABEL[card.rarity] ?? card.rarity;

  return (
    <div ref={rootRef} className={`card-preview card-preview--${rarity}`} style={style}>
      <div className="card-preview__header">
        <div className="card-preview__cost">{card.cost}</div>
        <div className="card-preview__title">
          <div className="card-preview__name">{card.name_zh}</div>
          <div className="card-preview__name-en">{card.name_en}</div>
        </div>
      </div>

      <div className="card-preview__meta">
        <span>{TYPE_LABEL[card.type] ?? card.type}</span>
        <span className="card-preview__sep">·</span>
        <span>{CLASS_LABEL[card.card_class] ?? card.card_class}</span>
        {tribe && <>
          <span className="card-preview__sep">·</span>
          <span>{tribe}</span>
        </>}
      </div>

      {showStats && (
        <div className="card-preview__stats">
          <div className="card-preview__atk">{atk}</div>
          <div className="card-preview__hp">{hp}</div>
          <div className="card-preview__stat-label">
            {isMinion ? '攻 / 血' : '攻 / 耐久'}
          </div>
        </div>
      )}

      {card.text_zh && (
        <div
          className="card-preview__text"
          // eslint-disable-next-line react/no-danger -- sanitized via DOMPurify
          dangerouslySetInnerHTML={{ __html: sanitizeCardHtml(card.text_zh) }}
        />
      )}

      <div className="card-preview__footer">
        <span className={`rarity rarity--${rarity} card-preview__rarity-gem`} />
        <span>{rarityLabel}</span>
        <span className="card-preview__sep">·</span>
        <span>{setLabel}</span>
      </div>
    </div>
  );
}
