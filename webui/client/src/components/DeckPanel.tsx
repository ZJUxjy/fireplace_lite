import { useMemo, useState } from 'react';
import type { Card, Deck, Format } from '../types/deck';
import { deckCardCount, isDeckSavable } from '../services/deckStore';
import { getCardById } from '../services/cardCatalog';
import './DeckPanel.css';

type Props = {
  /** Null = browse mode (no deck being built). */
  deck: Deck | null;
  onChange?: (deck: Deck) => void;
  onSave?: () => void;
  onExport?: () => void;
  onBack: () => void;
  onRemoveCard?: (cardId: string) => void;
  /** Open the inline class picker to start a scratch deck (browse mode only). */
  onCreateNewDeck?: () => void;
  /** Show preview when hovering a deck row card. */
  onCardHoverStart?: (card: Card, anchor: HTMLElement) => void;
  onCardHoverEnd?: () => void;
  /** Drop target: add a card by id when dragged from the pool. */
  onAddCardById?: (cardId: string) => void;
};

const FORMATS: Format[] = ['STANDARD', 'WILD', 'CLASSIC'];
const HERO_LABEL: Record<string, { name: string; short: string; color: string }> = {
  MAGE:        { name: '法师',     short: '法', color: '#69a7ff' },
  HUNTER:      { name: '猎人',     short: '猎', color: '#2a8b2a' },
  PRIEST:      { name: '牧师',     short: '牧', color: '#d8d8d8' },
  SHAMAN:      { name: '萨满',     short: '萨', color: '#1f4ea8' },
  PALADIN:     { name: '圣骑士',   short: '圣', color: '#e7b94a' },
  WARLOCK:     { name: '术士',     short: '术', color: '#7a4aa1' },
  WARRIOR:     { name: '战士',     short: '战', color: '#c0392b' },
  ROGUE:       { name: '潜行者',   short: '潜', color: '#3a3a3a' },
  DRUID:       { name: '德鲁伊',   short: '德', color: '#b06a2a' },
  DEMONHUNTER: { name: '恶魔猎手', short: '魔', color: '#8e3aa1' },
};

export default function DeckPanel(props: Props) {
  const { deck } = props;
  const [editingName, setEditingName] = useState(false);
  const [nameDraft, setNameDraft] = useState(deck?.name ?? '');
  const [dragOver, setDragOver] = useState(false);

  const onDragOver = (e: React.DragEvent) => {
    if (!deck || !props.onAddCardById) return;
    if (!e.dataTransfer.types.includes('text/card-id')) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    if (!dragOver) setDragOver(true);
  };
  const onDragLeave = (e: React.DragEvent) => {
    // Only clear when leaving the aside itself, not its children.
    if (e.currentTarget === e.target) setDragOver(false);
  };
  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const cardId = e.dataTransfer.getData('text/card-id');
    if (cardId) props.onAddCardById?.(cardId);
  };

  const sorted = useMemo(() => {
    if (!deck) return [];
    return [...deck.cards].map(dc => {
      const card = getCardById(dc.card_id);
      return { dc, card, cost: card?.cost ?? 99, name: card?.name_zh ?? dc.card_id };
    }).sort((a, b) => a.cost - b.cost || a.name.localeCompare(b.name));
  }, [deck]);

  /** Mana curve buckets 0..7+ (counts include duplicates). */
  const buckets = useMemo(() => {
    const b = [0, 0, 0, 0, 0, 0, 0, 0];
    sorted.forEach(({ dc, card }) => {
      const cost = card?.cost ?? 0;
      const idx = Math.min(cost, 7);
      b[idx] += dc.count;
    });
    return b;
  }, [sorted]);

  if (!deck) {
    return (
      <aside className="deckrail" onDragOver={onDragOver} onDragLeave={onDragLeave} onDrop={onDrop}>
        <div className="panel panel--dark deck-header">
          <h2>卡牌收藏</h2>
          <div className="deck-header__sub">浏览全卡库</div>
        </div>
        <div className="panel panel--dark deck-rail-empty">
          <div className="deck-rail-empty__icon">⚜</div>
          <div className="deck-rail-empty__msg">
            浏览模式<br/>选择一个职业开始构建卡组
          </div>
          <div className="deck-rail-empty__actions">
            {props.onCreateNewDeck && (
              <button className="btn" onClick={props.onCreateNewDeck}>新建卡组</button>
            )}
            <button className="btn btn--ghost" onClick={props.onBack}>返回</button>
          </div>
        </div>
      </aside>
    );
  }

  const total = deckCardCount(deck);
  const savable = isDeckSavable(deck);
  const hero = HERO_LABEL[deck.hero_class] ?? { name: deck.hero_class, short: '?', color: '#8b7547' };
  const maxBucket = Math.max(1, ...buckets);

  const unimplementedCount = deck.cards
    .filter(c => c.unimplemented === true)
    .reduce((sum, c) => sum + c.count, 0);

  const commitName = () => {
    if (nameDraft.trim() && props.onChange) {
      props.onChange({ ...deck, name: nameDraft.trim() });
    }
    setEditingName(false);
  };

  return (
    <aside
      className={`deckrail ${dragOver ? 'deckrail--dragover' : ''}`}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      <div className="panel panel--dark deck-header">
        <div className="deck-header__hero">
          <span
            className="deck-header__crest"
            style={{ background: `radial-gradient(circle at 35% 30%, ${hero.color}, #2a1a0d 80%)` }}
          >
            {hero.short}
          </span>
          {editingName ? (
            <input
              className="deck-header__name-input"
              autoFocus
              value={nameDraft}
              onChange={e => setNameDraft(e.target.value)}
              onBlur={commitName}
              onKeyDown={e => e.key === 'Enter' && commitName()}
            />
          ) : (
            <h2
              className="deck-header__name"
              onClick={() => { setNameDraft(deck.name); setEditingName(true); }}
              title="点击修改名称"
            >
              {deck.name}
            </h2>
          )}
        </div>
        <div className="deck-header__count">
          {total}<span className="deck-header__count-tot">/30</span>
        </div>
        <div className="deck-header__sub">{hero.name} · {deck.format}</div>
        <div className="deck-mana-curve">
          {buckets.map((v, i) => (
            <div key={i} className="bar" style={{ height: `${(v / maxBucket) * 100}%` }} title={`${i === 7 ? '7+' : i} 费 · ${v} 张`}>
              <span>{i === 7 ? '7+' : i}</span>
            </div>
          ))}
        </div>
        <select
          className="deck-header__format"
          value={deck.format}
          onChange={e => props.onChange?.({ ...deck, format: e.target.value as Format })}
        >
          {FORMATS.map(f => <option key={f} value={f}>{f}</option>)}
        </select>
      </div>

      <div className="panel panel--dark deck-list">
        {sorted.length === 0 && (
          <div className="deck-list__empty">
            空空如也…<br/>从左侧卡库选择卡牌
          </div>
        )}
        {sorted.map(({ dc, card }) => {
          if (!card) {
            return (
              <div
                key={dc.card_id}
                className="deck-card deck-card--unimplemented"
                onClick={() => props.onRemoveCard?.(dc.card_id)}
                title="未实现的卡牌,本卡组无法开局"
              >
                <div className="mana-mini mana-mini--warn">!</div>
                <div className="deck-card__name">⚠ {dc.card_id}</div>
                <div className="deck-card__count">×{dc.count}</div>
              </div>
            );
          }
          const dim = dc.unimplemented === true;
          const isLeg = card.rarity === 'LEGENDARY';
          return (
            <div
              key={dc.card_id}
              className={`deck-card ${dim ? 'deck-card--dim' : ''} ${isLeg ? 'deck-card--legendary' : ''}`}
              onClick={() => props.onRemoveCard?.(dc.card_id)}
              onMouseEnter={(e) => props.onCardHoverStart?.(card, e.currentTarget)}
              onMouseLeave={props.onCardHoverEnd}
              title={dim ? '未实现的卡牌,本卡组无法开局' : '点击移除一张'}
            >
              <div className="mana-mini">{card.cost}</div>
              <div className={`deck-card__name ${isLeg ? 'deck-card__name--legendary' : ''}`}>
                {isLeg && <span className="deck-card__star">✦</span>}
                {card.name_zh}
              </div>
              <div className="deck-card__count">×{dc.count}</div>
            </div>
          );
        })}
      </div>

      <div className="deckrail__footer">
        {unimplementedCount > 0 && (
          <div className="deckrail__warn">含 {unimplementedCount} 张未实现卡,开局会被拒绝</div>
        )}
        {!savable.ok && <div className="deckrail__warn">{savable.reason}</div>}
        <div className="deckrail__buttons">
          <button className="btn" onClick={props.onSave} disabled={!savable.ok}>保存</button>
          <button className="btn" onClick={props.onExport}>导出</button>
          <button className="btn btn--ghost" onClick={props.onBack}>返回</button>
        </div>
      </div>
    </aside>
  );
}
