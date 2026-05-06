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
        {sorted.map(({ dc, card }) => card && (
          <CardRow
            key={dc.card_id}
            card={card}
            count={dc.count}
            showRightCount
            onClick={() => props.onRemoveCard(dc.card_id)}
          />
        ))}
        {sorted.length === 0 && (
          <div className="deck-panel__empty">点左侧卡牌加入卡组</div>
        )}
      </div>

      <div className="deck-panel__footer">
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
