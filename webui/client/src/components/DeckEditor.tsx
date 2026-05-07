import { useEffect, useMemo, useState } from 'react';
import type { Card, CardType, Deck, Rarity } from '../types/deck';
import {
  streamCatalog, getCatalogSync, isCatalogLoaded,
  filterCards, sortCards,
  type Keyword, type CatalogProgress,
} from '../services/cardCatalog';
import {
  getDeck, saveDeck, addCardToDeck, removeCardFromDeck,
  exportDeckToDeckstring, deckCardCount, findCardInDeck,
  newDeck,
} from '../services/deckStore';
import CardPool, { type PoolTopbarFilter } from './CardPool';
import DeckPanel from './DeckPanel';
import CardPreview from './CardPreview';
import FilterRail, { type FilterRailState } from './FilterRail';
import './DeckEditor.css';

type Props = {
  // null = browse mode; "new"+initialDeck = create mode; string id = edit mode
  deckId: string | null | 'new';
  initialDeck?: Deck;
  onBack: () => void;
};

const HERO_DEFS: { id: string; name: string; short: string; color: string }[] = [
  { id: 'MAGE',        name: '法师',     short: '法', color: '#69a7ff' },
  { id: 'WARRIOR',     name: '战士',     short: '战', color: '#c0392b' },
  { id: 'PRIEST',      name: '牧师',     short: '牧', color: '#d8d8d8' },
  { id: 'ROGUE',       name: '潜行者',   short: '潜', color: '#3a3a3a' },
  { id: 'HUNTER',      name: '猎人',     short: '猎', color: '#2a8b2a' },
  { id: 'DRUID',       name: '德鲁伊',   short: '德', color: '#b06a2a' },
  { id: 'WARLOCK',     name: '术士',     short: '术', color: '#7a4aa1' },
  { id: 'PALADIN',     name: '圣骑士',   short: '圣', color: '#e7b94a' },
  { id: 'SHAMAN',      name: '萨满',     short: '萨', color: '#1f4ea8' },
  { id: 'DEMONHUNTER', name: '恶魔猎手', short: '魔', color: '#8e3aa1' },
];

const initialRail = (defaultClass?: string): FilterRailState => ({
  cardClass: defaultClass ?? 'ALL',
  types: new Set<CardType>(),
  rarities: new Set<Rarity>(),
  races: new Set<string>(),
  sets: new Set<string>(),
  keywords: new Set<Keyword>(),
});
const initialTopbar = (): PoolTopbarFilter => ({
  costs: new Set<number>(),
  search: '',
});

export default function DeckEditor({ deckId, initialDeck, onBack }: Props) {
  const [catalog, setCatalog] = useState<Card[]>(getCatalogSync());
  const [catalogLoading, setCatalogLoading] = useState(() => !isCatalogLoaded());
  const [progress, setProgress] = useState<CatalogProgress>(() => {
    const sync = getCatalogSync();
    return { loaded: sync.length, total: sync.length };
  });
  const [deck, setDeck] = useState<Deck | null>(() => {
    if (deckId === null) return null;
    if (deckId === 'new' && initialDeck) return initialDeck;
    return getDeck(deckId as string);
  });
  const [rail, setRail] = useState<FilterRailState>(() => initialRail(deck?.hero_class));
  const [topbar, setTopbar] = useState<PoolTopbarFilter>(() => initialTopbar());
  const [hoverCard, setHoverCard] = useState<{ card: Card; anchor: HTMLElement } | null>(null);
  const [previewLockedCard, setPreviewLockedCard] = useState<Card | null>(null);
  const [toast, setToast] = useState<string>('');
  const [showClassPicker, setShowClassPicker] = useState(false);

  // Streaming catalog load. The FilterRail mounts immediately with whatever
  // we have in memory (possibly empty); each onChunk callback grows the
  // catalog state, repainting the grid as pages arrive.
  useEffect(() => {
    const ctrl = new AbortController();
    streamCatalog({
      signal: ctrl.signal,
      onChunk: (cards, prog) => {
        setCatalog(cards);
        setProgress(prog);
        if (prog.loaded > 0) setCatalogLoading(false);
      },
    }).catch((e) => {
      if ((e as Error).name === 'AbortError') return;
      setCatalogLoading(false);
      setToast(`加载卡库失败: ${(e as Error).message}`);
    });
    return () => ctrl.abort();
  }, []);

  const isBrowse = deck === null;
  const lockedHeroClass = isBrowse ? undefined : deck?.hero_class;

  const filtered = useMemo(() => {
    const effectiveClass = lockedHeroClass ?? (rail.cardClass === 'ALL' ? undefined : rail.cardClass);
    return sortCards(filterCards(catalog, {
      cardClass: effectiveClass,
      // Edit mode shows class + NEUTRAL; browse mode shows strict class.
      includeNeutral: !!lockedHeroClass,
      costs: topbar.costs,
      types: rail.types,
      rarities: rail.rarities,
      races: rail.races,
      sets: rail.sets,
      keywords: rail.keywords,
      search: topbar.search,
    }));
  }, [catalog, lockedHeroClass, rail, topbar]);

  const tryAddCard = (card: Card) => {
    if (!deck) return;
    if (cardDisabled(card)) {
      // Surface the same toast UX as a click on a maxed/illegal card.
      if (card.card_class !== deck.hero_class && card.card_class !== 'NEUTRAL') {
        setToast('该职业不能加入此卡组'); return;
      }
      if (deckCardCount(deck) >= 30) { setToast('卡组已满 30 张'); return; }
      setToast(`已达 ${card.max_count} 张上限`);
      return;
    }
    const ok = addCardToDeck(deck, card.id, card.max_count);
    if (ok) setDeck({ ...deck });
  };

  const onCardClick = (card: Card) => {
    if (isBrowse) { setPreviewLockedCard(card); return; }
    tryAddCard(card);
  };

  const onAddCardById = (cardId: string) => {
    if (isBrowse) return;
    const card = catalog.find(c => c.id === cardId);
    if (card) tryAddCard(card);
  };

  const cardDisabled = (c: Card): boolean => {
    if (isBrowse || !deck) return false;
    if (c.card_class !== deck.hero_class && c.card_class !== 'NEUTRAL') return true;
    if (deckCardCount(deck) >= 30) return true;
    const inDeck = findCardInDeck(deck, c.id);
    if (inDeck && inDeck.count >= c.max_count) return true;
    return false;
  };

  const cardCount = (c: Card): number => {
    if (!deck) return 0;
    return findCardInDeck(deck, c.id)?.count ?? 0;
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

  const onResetAll = () => {
    setRail(initialRail(deck?.hero_class));
    setTopbar(initialTopbar());
  };

  /** Inline create-deck flow (browse mode → scratch deck of chosen class). */
  const onPickHeroClass = (heroClass: string) => {
    const fresh = newDeck(heroClass);
    setDeck(fresh);
    setRail(initialRail(heroClass));
    setTopbar(initialTopbar());
    setShowClassPicker(false);
    setToast(`已新建 ${HERO_DEFS.find(h => h.id === heroClass)?.name ?? heroClass} 卡组`);
  };

  // toast auto-clear
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(''), 1800);
    return () => clearTimeout(t);
  }, [toast]);

  return (
    <div className="deck-editor">
      <FilterRail
        catalog={catalog}
        state={rail}
        onChange={setRail}
        lockedHeroClass={lockedHeroClass}
      />

      <main className="deck-editor__main">
        <CardPool
          cards={filtered}
          total={catalog.length}
          filtered={filtered.length}
          catalogLoading={catalogLoading}
          progress={progress}
          topbar={topbar}
          onTopbarChange={setTopbar}
          onResetAll={onResetAll}
          onCardClick={onCardClick}
          onCardContextMenu={(c) => setPreviewLockedCard(c)}
          onCardHoverStart={(card, anchor) => setHoverCard({ card, anchor })}
          onCardHoverEnd={() => setHoverCard(null)}
          cardDisabled={cardDisabled}
          cardCount={cardCount}
        />
      </main>

      <DeckPanel
        deck={deck}
        onChange={setDeck}
        onSave={onSave}
        onExport={onExport}
        onBack={onBack}
        onRemoveCard={onRemove}
        onAddCardById={onAddCardById}
        onCreateNewDeck={() => setShowClassPicker(true)}
        onCardHoverStart={(card, anchor) => setHoverCard({ card, anchor })}
        onCardHoverEnd={() => setHoverCard(null)}
      />

      <CardPreview card={hoverCard?.card ?? null} anchor={hoverCard?.anchor ?? null} />

      {previewLockedCard && (
        <div className="deck-editor__locked-overlay" onClick={() => setPreviewLockedCard(null)}>
          <div className="deck-editor__locked-content" onClick={e => e.stopPropagation()}>
            <CardPreview card={previewLockedCard} anchor={document.body} />
            <button className="btn deck-editor__locked-close" onClick={() => setPreviewLockedCard(null)}>关闭</button>
          </div>
        </div>
      )}

      {showClassPicker && (
        <div className="deck-editor__locked-overlay" onClick={() => setShowClassPicker(false)}>
          <div className="class-picker" onClick={e => e.stopPropagation()}>
            <h3 className="class-picker__title">选择职业</h3>
            <div className="class-picker__grid">
              {HERO_DEFS.map(h => (
                <button
                  key={h.id}
                  className="class-picker__btn"
                  onClick={() => onPickHeroClass(h.id)}
                >
                  <span
                    className="class-picker__crest"
                    style={{ background: `radial-gradient(circle at 35% 30%, ${h.color}, #2a1a0d 80%)` }}
                  >
                    {h.short}
                  </span>
                  <span>{h.name}</span>
                </button>
              ))}
            </div>
            <button className="btn btn--ghost class-picker__cancel" onClick={() => setShowClassPicker(false)}>取消</button>
          </div>
        </div>
      )}

      {toast && <div className="deck-editor__toast">{toast}</div>}
    </div>
  );
}
