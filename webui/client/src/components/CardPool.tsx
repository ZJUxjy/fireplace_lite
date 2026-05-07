import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import type { Card } from '../types/deck';
import CardRow from './CardRow';
import './CardPool.css';

export type PoolTopbarFilter = {
  costs: Set<number>;
  search: string;
};

type Props = {
  /** Already filtered + sorted by parent (DeckEditor). */
  cards: Card[];
  total: number;
  filtered: number;
  catalogLoading?: boolean;
  topbar: PoolTopbarFilter;
  onTopbarChange: (next: PoolTopbarFilter) => void;
  onResetAll: () => void;
  /** Slot rendered at the very right of the topbar (currently unused; reserved). */
  trailing?: ReactNode;
  onCardClick?: (card: Card) => void;
  onCardContextMenu?: (card: Card) => void;
  onCardHoverStart?: (card: Card, anchor: HTMLElement) => void;
  onCardHoverEnd?: () => void;
  cardDisabled?: (card: Card) => boolean;
  cardCount?: (card: Card) => number;
};

const PAGE_SIZE = 20;

export default function CardPool(props: Props) {
  const { topbar, onTopbarChange, total, filtered, catalogLoading } = props;

  const [page, setPage] = useState(1);
  const collectionRef = useRef<HTMLDivElement>(null);

  const totalPages = Math.max(1, Math.ceil(props.cards.length / PAGE_SIZE));

  // Reset to page 1 when the filtered card list reference changes (filter / search update).
  useEffect(() => {
    setPage(1);
  }, [props.cards]);

  // Snap to last available page if the current page falls out of range
  // (e.g. catalog reload).
  useEffect(() => {
    if (page > totalPages) setPage(totalPages);
  }, [page, totalPages]);

  // Scroll the grid to top whenever page changes.
  useEffect(() => {
    collectionRef.current?.scrollTo({ top: 0 });
  }, [page]);

  const pageCards = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return props.cards.slice(start, start + PAGE_SIZE);
  }, [props.cards, page]);

  const toggleCost = (n: number) => {
    const s = new Set(topbar.costs);
    s.has(n) ? s.delete(n) : s.add(n);
    onTopbarChange({ ...topbar, costs: s });
  };

  return (
    <div className="card-pool">
      <div className="topbar">
        <div className="topbar__title">卡牌收藏</div>
        <div className="topbar__sub">{filtered} / {total} 张</div>

        <span className="rivet" />

        <div className="chips">
          {[0,1,2,3,4,5,6,7].map(n => (
            <div
              key={n}
              className={`chip ${topbar.costs.has(n) ? 'chip--active' : ''}`}
              onClick={() => toggleCost(n)}
            >
              {n === 7 ? '7+' : n}
            </div>
          ))}
        </div>

        <div className="topbar__spacer" />

        <div className="search">
          <span className="search__icon" aria-hidden>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="7" />
              <path d="M20 20l-3.5-3.5" />
            </svg>
          </span>
          <input
            placeholder="搜索卡名…"
            value={topbar.search}
            onChange={(e) => onTopbarChange({ ...topbar, search: e.target.value })}
          />
        </div>

        <button className="btn" onClick={props.onResetAll}>重置</button>

        {props.trailing}
      </div>

      <div ref={collectionRef} className="collection">
        {catalogLoading && (
          <div className="card-pool__loading">正在加载卡库…</div>
        )}
        {!catalogLoading && pageCards.length === 0 && (
          <div className="card-pool__empty">
            <div className="card-pool__empty-icon">⚜</div>
            没有符合条件的卡牌
          </div>
        )}
        {!catalogLoading && pageCards.map(c => (
          <CardRow
            key={c.id}
            card={c}
            disabled={props.cardDisabled?.(c)}
            count={props.cardCount?.(c) ?? 0}
            onClick={() => props.onCardClick?.(c)}
            onContextMenu={(e) => { e.preventDefault(); props.onCardContextMenu?.(c); }}
            onHoverStart={props.onCardHoverStart}
            onHoverEnd={props.onCardHoverEnd}
          />
        ))}
      </div>

      {!catalogLoading && props.cards.length > 0 && (
        <Pagination
          page={page}
          totalPages={totalPages}
          onChange={setPage}
        />
      )}
    </div>
  );
}

type PaginationProps = {
  page: number;
  totalPages: number;
  onChange: (page: number) => void;
};

function Pagination({ page, totalPages, onChange }: PaginationProps) {
  const goPrev = () => onChange(Math.max(1, page - 1));
  const goNext = () => onChange(Math.min(totalPages, page + 1));
  const goFirst = () => onChange(1);
  const goLast = () => onChange(totalPages);

  return (
    <div className="pagination">
      <button
        className="pagination__btn"
        onClick={goFirst}
        disabled={page <= 1}
        title="第一页"
      >«</button>
      <button
        className="pagination__btn"
        onClick={goPrev}
        disabled={page <= 1}
        title="上一页"
      >‹</button>
      <span className="pagination__info">
        第 <span className="pagination__cur">{page}</span> / {totalPages} 页
      </span>
      <button
        className="pagination__btn"
        onClick={goNext}
        disabled={page >= totalPages}
        title="下一页"
      >›</button>
      <button
        className="pagination__btn"
        onClick={goLast}
        disabled={page >= totalPages}
        title="最后一页"
      >»</button>
    </div>
  );
}
