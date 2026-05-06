import { useMemo, useState } from 'react';
import type { Deck, Format } from '../types/deck';
import { deckCardCount, isDeckSavable } from '../services/deckStore';
import { getCardById } from '../services/cardCatalog';
import CardRow from './CardRow';
import './DeckPanel.css';

type Props = {
  deck: Deck;
  onChange: (deck: Deck) => void;
  onSave: () => void;
  onExport: () => void;
  onBack: () => void;
  onRemoveCard: (cardId: string) => void;
};

const FORMATS: Format[] = ['STANDARD', 'WILD', 'CLASSIC'];
const HERO_LABEL: Record<string, string> = {
  MAGE: '🔮', HUNTER: '🏹', PRIEST: '✨', SHAMAN: '🌩️',
  PALADIN: '⚔️', WARLOCK: '👹', WARRIOR: '🛡️', ROGUE: '🗡️',
  DRUID: '🌿', DEMONHUNTER: '👁️',
};

export default function DeckPanel(props: Props) {
  const { deck } = props;
  const [editingName, setEditingName] = useState(false);
  const [nameDraft, setNameDraft] = useState(deck.name);

  const total = deckCardCount(deck);
  const savable = isDeckSavable(deck);

  const sorted = useMemo(() => {
    return [...deck.cards].map(dc => {
      const card = getCardById(dc.card_id);
      return { dc, card, cost: card?.cost ?? 99, name: card?.name_zh ?? dc.card_id };
    }).sort((a, b) => a.cost - b.cost || a.name.localeCompare(b.name));
  }, [deck.cards]);

  const unimplementedCount = deck.cards
    .filter(c => c.unimplemented === true)
    .reduce((sum, c) => sum + c.count, 0);

  const commitName = () => {
    if (nameDraft.trim()) {
      props.onChange({ ...deck, name: nameDraft.trim() });
    }
    setEditingName(false);
  };

  return (
    <div className="deck-panel">
      <div className="deck-panel__header">
        <div className="deck-panel__title-row">
          <span className="deck-panel__hero">{HERO_LABEL[deck.hero_class] ?? '?'}</span>
          {editingName ? (
            <input
              autoFocus
              value={nameDraft}
              onChange={e => setNameDraft(e.target.value)}
              onBlur={commitName}
              onKeyDown={e => e.key === 'Enter' && commitName()}
            />
          ) : (
            <span className="deck-panel__name" onClick={() => { setNameDraft(deck.name); setEditingName(true); }}>
              {deck.name}
            </span>
          )}
        </div>
        <div className="deck-panel__meta">
          <span className={`deck-panel__count ${total === 30 ? 'full' : total > 30 ? 'over' : ''}`}>
            {total}/30
          </span>
          <select
            value={deck.format}
            onChange={e => props.onChange({ ...deck, format: e.target.value as Format })}
          >
            {FORMATS.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>
      </div>

      <div className="deck-panel__list">
        {sorted.map(({ dc, card }) => {
          if (!card) {
            // 卡片不在 catalog 中(未实现 / 未知 dbf_id),直接渲染占位灰条
            return (
              <div
                key={dc.card_id}
                className="deck-panel__row deck-panel__row--unimplemented"
                onClick={() => props.onRemoveCard(dc.card_id)}
                title="未实现的卡牌,本卡组无法开局"
              >
                <span className="deck-panel__row-name">⚠ {dc.card_id}</span>
                <span className="deck-panel__row-count">×{dc.count}</span>
              </div>
            );
          }
          const dim = dc.unimplemented === true;
          return (
            <div
              key={dc.card_id}
              className={dim ? 'deck-panel__row-wrap deck-panel__row-wrap--dim' : ''}
              title={dim ? '未实现的卡牌,本卡组无法开局' : undefined}
            >
              <CardRow
                card={card}
                count={dc.count}
                showRightCount
                onClick={() => props.onRemoveCard(dc.card_id)}
              />
            </div>
          );
        })}
        {sorted.length === 0 && (
          <div className="deck-panel__empty">点左侧卡牌加入卡组</div>
        )}
      </div>

      <div className="deck-panel__footer">
        {unimplementedCount > 0 && (
          <div className="deck-panel__warn">含 {unimplementedCount} 张未实现卡,开局会被拒绝</div>
        )}
        {!savable.ok && <div className="deck-panel__warn">{savable.reason}</div>}
        <div className="deck-panel__buttons">
          <button onClick={props.onSave} disabled={!savable.ok}>保存</button>
          <button onClick={props.onExport}>导出</button>
          <button onClick={props.onBack}>返回</button>
        </div>
      </div>
    </div>
  );
}
