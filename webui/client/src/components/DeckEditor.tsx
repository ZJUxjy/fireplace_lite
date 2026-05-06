import { useEffect, useState } from 'react';
import type { Card, Deck } from '../types/deck';
import { loadCatalog, getCatalogSync } from '../services/cardCatalog';
import {
  getDeck, saveDeck, addCardToDeck, removeCardFromDeck,
  exportDeckToDeckstring, deckCardCount, findCardInDeck,
} from '../services/deckStore';
import CardPool from './CardPool';
import DeckPanel from './DeckPanel';
import CardPreview from './CardPreview';
import './DeckEditor.css';

type Props = {
  // null = browse mode; "new"+initialDeck = create mode; string id = edit mode
  deckId: string | null | 'new';
  initialDeck?: Deck;
  onBack: () => void;
};

export default function DeckEditor({ deckId, initialDeck, onBack }: Props) {
  const [catalog, setCatalog] = useState<Card[]>(getCatalogSync());
  const [deck, setDeck] = useState<Deck | null>(() => {
    if (deckId === null) return null;
    if (deckId === 'new' && initialDeck) return initialDeck;
    return getDeck(deckId as string);
  });
  const [hoverCard, setHoverCard] = useState<{ card: Card; anchor: HTMLElement } | null>(null);
  const [previewLockedCard, setPreviewLockedCard] = useState<Card | null>(null);
  const [toast, setToast] = useState<string>('');

  useEffect(() => {
    if (catalog.length === 0) loadCatalog().then(setCatalog).catch(e => setToast(`加载卡库失败: ${e.message}`));
  }, [catalog.length]);

  const isBrowse = deck === null;

  const onCardClick = (card: Card) => {
    if (isBrowse) { setPreviewLockedCard(card); return; }
    if (!deck) return;
    const max = card.max_count;
    const ok = addCardToDeck(deck, card.id, max);
    if (ok) {
      setDeck({ ...deck });
    } else if (deckCardCount(deck) >= 30) {
      setToast('卡组已满 30 张');
    } else {
      setToast(`已达 ${max} 张上限`);
    }
  };

  const cardDisabled = (c: Card): boolean => {
    if (isBrowse || !deck) return false;
    if (c.card_class !== deck.hero_class && c.card_class !== 'NEUTRAL') return true;
    if (deckCardCount(deck) >= 30) return true;
    const inDeck = findCardInDeck(deck, c.id);
    if (inDeck && inDeck.count >= c.max_count) return true;
    return false;
  };

  const onRemove = (cardId: string) => {
    if (!deck) return;
    if (removeCardFromDeck(deck, cardId)) setDeck({ ...deck });
  };

  const onSave = () => {
    if (!deck) return;
    try {
      saveDeck(deck);
      setToast('已保存');
      setTimeout(onBack, 600);
    } catch (e) { setToast(`保存失败: ${(e as Error).message}`); }
  };

  const onExport = async () => {
    if (!deck) return;
    try {
      const ds = await exportDeckToDeckstring(deck);
      await navigator.clipboard.writeText(ds);
      setToast('Deckstring 已复制到剪贴板');
    } catch (e) { setToast(`导出失败: ${(e as Error).message}`); }
  };

  // toast auto-clear
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(''), 1800);
    return () => clearTimeout(t);
  }, [toast]);

  return (
    <div className={`deck-editor ${isBrowse ? 'deck-editor--browse' : ''}`}>
      <div className="deck-editor__pool">
        <CardPool
          catalog={catalog}
          defaultClass={deck?.hero_class}
          forceIncludeNeutral={!isBrowse}
          onCardClick={onCardClick}
          onCardContextMenu={(c) => setPreviewLockedCard(c)}
          onCardHoverStart={(card, anchor) => setHoverCard({ card, anchor })}
          onCardHoverEnd={() => setHoverCard(null)}
          cardDisabled={cardDisabled}
        />
      </div>
      {!isBrowse && deck && (
        <div className="deck-editor__panel">
          <DeckPanel
            deck={deck}
            onChange={setDeck}
            onSave={onSave}
            onExport={onExport}
            onBack={onBack}
            onRemoveCard={onRemove}
          />
        </div>
      )}
      {isBrowse && (
        <div className="deck-editor__back-bar">
          <button onClick={onBack}>返回</button>
        </div>
      )}

      <CardPreview card={hoverCard?.card ?? null} anchor={hoverCard?.anchor ?? null} />

      {previewLockedCard && (
        <div className="deck-editor__locked-overlay" onClick={() => setPreviewLockedCard(null)}>
          <div className="deck-editor__locked-content" onClick={e => e.stopPropagation()}>
            <CardPreview card={previewLockedCard} anchor={document.body} />
            <button onClick={() => setPreviewLockedCard(null)}>关闭</button>
          </div>
        </div>
      )}

      {toast && <div className="deck-editor__toast">{toast}</div>}
    </div>
  );
}
