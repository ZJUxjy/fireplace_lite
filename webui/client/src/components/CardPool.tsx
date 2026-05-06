import { useMemo, useState } from 'react';
import type { Card, CardType } from '../types/deck';
import { filterCards, sortCards } from '../services/cardCatalog';
import CardRow from './CardRow';
import './CardPool.css';

type Props = {
  catalog: Card[];
  /** True until /api/cards/all has resolved (distinct from empty filter results). */
  catalogLoading?: boolean;
  defaultClass?: string;
  forceIncludeNeutral?: boolean;
  onCardClick?: (card: Card) => void;
  onCardContextMenu?: (card: Card) => void;
  onCardHoverStart?: (card: Card, anchor: HTMLElement) => void;
  onCardHoverEnd?: () => void;
  cardDisabled?: (card: Card) => boolean;
};

const ALL_CLASSES = ['MAGE','HUNTER','PRIEST','SHAMAN','PALADIN','WARLOCK','WARRIOR','ROGUE','DRUID','DEMONHUNTER','NEUTRAL'] as const;
const TYPES: CardType[] = ['MINION', 'SPELL', 'WEAPON'];

export default function CardPool(props: Props) {
  const catalogLoading = props.catalogLoading ?? false;
  const [classFilter, setClassFilter] = useState<string | undefined>(props.defaultClass);
  const [costs, setCosts] = useState<Set<number>>(new Set());
  const [types, setTypes] = useState<Set<CardType>>(new Set());
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => sortCards(filterCards(props.catalog, {
    cardClass: classFilter,
    includeNeutral: classFilter ? props.forceIncludeNeutral : false,
    costs,
    types,
    search,
  })), [props.catalog, classFilter, costs, types, search, props.forceIncludeNeutral]);

  const toggleCost = (n: number) => {
    const s = new Set(costs);
    s.has(n) ? s.delete(n) : s.add(n);
    setCosts(s);
  };
  const toggleType = (t: CardType) => {
    const s = new Set(types);
    s.has(t) ? s.delete(t) : s.add(t);
    setTypes(s);
  };

  return (
    <div className="card-pool">
      <div className="card-pool__filters">
        <select value={classFilter ?? ''} onChange={(e) => setClassFilter(e.target.value || undefined)}>
          <option value="">全部职业</option>
          {ALL_CLASSES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <div className="card-pool__cost-bar">
          {[0,1,2,3,4,5,6,7].map(n => (
            <button key={n} className={costs.has(n) ? 'on' : ''} onClick={() => toggleCost(n)}>
              {n === 7 ? '7+' : n}
            </button>
          ))}
        </div>
        <div className="card-pool__type-bar">
          {TYPES.map(t => (
            <button key={t} className={types.has(t) ? 'on' : ''} onClick={() => toggleType(t)}>
              {t === 'MINION' ? '随' : t === 'SPELL' ? '法' : '武'}
            </button>
          ))}
        </div>
        <input
          className="card-pool__search"
          placeholder="搜索卡名…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <div className="card-pool__list">
        {!catalogLoading && filtered.map(c => (
          <CardRow
            key={c.id}
            card={c}
            disabled={props.cardDisabled?.(c)}
            onClick={() => props.onCardClick?.(c)}
            onContextMenu={(e) => { e.preventDefault(); props.onCardContextMenu?.(c); }}
            onHoverStart={props.onCardHoverStart}
            onHoverEnd={props.onCardHoverEnd}
          />
        ))}
        {catalogLoading && (
          <div className="card-pool__loading">正在加载卡库…</div>
        )}
        {!catalogLoading && filtered.length === 0 && (
          <div className="card-pool__empty">没有匹配的卡牌</div>
        )}
      </div>
    </div>
  );
}
