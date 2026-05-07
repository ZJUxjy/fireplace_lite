import { useMemo } from 'react';
import type { Card, CardType, Rarity } from '../types/deck';
import { KEYWORDS, KEYWORD_LABELS, type Keyword } from '../services/cardCatalog';
import './FilterRail.css';

export type FilterRailState = {
  cardClass: string;        // 'ALL' | 'NEUTRAL' | one of HERO_CLASSES
  types: Set<CardType>;
  rarities: Set<Rarity>;
  races: Set<string>;
  sets: Set<string>;
  keywords: Set<Keyword>;
};

type Props = {
  catalog: Card[];
  state: FilterRailState;
  onChange: (next: FilterRailState) => void;
  /** When set, the class picker is locked to this hero class (edit mode). */
  lockedHeroClass?: string;
};

const CLASS_DEFS: { id: string; name: string; short: string; color: string }[] = [
  { id: 'ALL',         name: '全部职业', short: '全', color: '#8b7547' },
  { id: 'NEUTRAL',     name: '中立',     short: '中', color: '#8b7547' },
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

const TYPE_DEFS: { id: CardType; name: string; short: string }[] = [
  { id: 'MINION', name: '随从', short: '随' },
  { id: 'SPELL',  name: '法术', short: '法' },
  { id: 'WEAPON', name: '武器', short: '武' },
];

const RARITY_DEFS: { id: Rarity; name: string }[] = [
  { id: 'COMMON',    name: '普通' },
  { id: 'RARE',      name: '稀有' },
  { id: 'EPIC',      name: '史诗' },
  { id: 'LEGENDARY', name: '传说' },
];

const RACE_LABEL: Record<string, string> = {
  DRAGON: '龙', BEAST: '野兽', MURLOC: '鱼人', DEMON: '恶魔',
  ELEMENTAL: '元素', MECH: '机械', MECHANICAL: '机械',
  PIRATE: '海盗', TOTEM: '图腾',
  UNDEAD: '亡灵', NAGA: '娜迦', QUILBOAR: '野猪人',
  ALL: '全部种族',
};

const SET_LABEL: Record<string, string> = {
  // Always-available (in both Standard and Wild)
  CORE: '核心',
  // "Free / Legacy" sets — formerly Basic + Classic, always Wild now
  EXPERT1: '经典',
  LEGACY: '传统',
  // Wild — chronological by HS release
  NAXX: '纳克萨玛斯的诅咒',
  GVG: '地精大战侏儒',
  BRM: '黑石山的火焰',
  TGT: '冠军的试炼',
  LOE: '探险者协会',
  OG: '上古之神的低语',
  KARA: '卡拉赞之夜',
  GANGS: '龙争虎斗加基森',
  UNGORO: '勇闯安戈洛',
  ICECROWN: '冰封王座的骑士',
  LOOTAPALOOZA: '狗头人与地下世界',
  GILNEAS: '女巫森林',
  BOOMSDAY: '砰砰计划',
  TROLL: '拉斯塔哈的大乱斗',
  DALARAN: '暗影崛起',
  ULDUM: '奥丹姆奇兵',
  DRAGONS: '巨龙降临',
  BLACK_TEMPLE: '外域的灰烬',
  DEMON_HUNTER_INITIATE: '恶魔猎手新兵',
  SCHOLOMANCE: '通灵学园',
  // 2024 — Year of the Pegasus (now Wild as of 2026)
  WHIZBANGS_WORKSHOP: '威兹班的工坊',
  RETURN_OF_THE_LICH_KING: '巫妖王的进军',
  // Standard (2025 + 2026) — see STANDARD_SETS below
  EMERALD_DREAM: '漫游翡翠梦境',
  THE_LOST_CITY: '安戈洛龟途',
  TIME_TRAVEL: '穿越时间流',
  CATACLYSM: '大地的裂变',
  // Misc bookkeeping
  EVENT: '活动',
  PLACEHOLDER_202204: '占位',
};

/** Sets currently in Standard format (2025 + 2026 expansions per the
 * user's definition). Renders as a separate group above the Wild list. */
const STANDARD_SETS: Set<string> = new Set([
  'EMERALD_DREAM',     // Into the Emerald Dream — 漫游翡翠梦境 (2025-03)
  'THE_LOST_CITY',     // The Lost City of Un'Goro — 安戈洛龟途 (2025-07)
  'TIME_TRAVEL',       // Across the Timeways — 穿越时间流 (2025-11)
  'CATACLYSM',         // CATACLYSM — 大地的裂变 (2026-03)
]);

export default function FilterRail({ catalog, state, onChange, lockedHeroClass }: Props) {
  const counts = useMemo(() => {
    const out = {
      types: {} as Record<string, number>,
      rarities: {} as Record<string, number>,
      races: {} as Record<string, number>,
      sets: {} as Record<string, number>,
    };
    catalog.forEach(c => {
      out.types[c.type] = (out.types[c.type] ?? 0) + 1;
      out.rarities[c.rarity] = (out.rarities[c.rarity] ?? 0) + 1;
      if (c.race) out.races[c.race] = (out.races[c.race] ?? 0) + 1;
      out.sets[c.card_set] = (out.sets[c.card_set] ?? 0) + 1;
    });
    return out;
  }, [catalog]);

  const racesSorted = useMemo(() => {
    return Object.entries(counts.races)
      .sort((a, b) => b[1] - a[1])
      .map(([id, n]) => ({ id, n }));
  }, [counts.races]);

  const setsSorted = useMemo(() => {
    const all = Object.entries(counts.sets)
      .sort((a, b) => b[1] - a[1])
      .map(([id, n]) => ({ id, n }));
    const standard = all.filter(({ id }) => STANDARD_SETS.has(id));
    const wild = all.filter(({ id }) => !STANDARD_SETS.has(id));
    return { standard, wild };
  }, [counts.sets]);

  const toggle = <T,>(key: keyof FilterRailState, value: T) => {
    const cur = state[key] as Set<T>;
    const next = new Set(cur);
    if (next.has(value)) next.delete(value); else next.add(value);
    onChange({ ...state, [key]: next });
  };

  const setClass = (id: string) => {
    if (lockedHeroClass) return;
    onChange({ ...state, cardClass: id });
  };

  const effectiveClass = lockedHeroClass ?? state.cardClass;

  return (
    <aside className="rail">
      <div className="panel rail__section">
        <h3 className="rail__title">职业</h3>
        <div className={`classgrid ${lockedHeroClass ? 'classgrid--locked' : ''}`}>
          {CLASS_DEFS.map(c => {
            const active = effectiveClass === c.id || (lockedHeroClass === c.id);
            return (
              <div
                key={c.id}
                className={`classgrid__item ${active ? 'classgrid__item--active' : ''}`}
                onClick={() => setClass(c.id)}
                title={c.name}
              >
                <span
                  className="classgrid__crest"
                  style={{ background: `radial-gradient(circle at 35% 30%, ${c.color}, #2a1a0d 80%)` }}
                >
                  {c.short}
                </span>
                <span className="classgrid__name">{c.name}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="panel rail__section">
        <h3 className="rail__title">卡牌类型</h3>
        {TYPE_DEFS.map(t => (
          <FilterRow
            key={t.id}
            active={state.types.has(t.id)}
            onClick={() => toggle<CardType>('types', t.id)}
            leading={
              <span className={`row__type row__type--${t.id.toLowerCase()} row__type--mini`}>{t.short}</span>
            }
            label={t.name}
            count={counts.types[t.id] ?? 0}
          />
        ))}
      </div>

      <div className="panel rail__section">
        <h3 className="rail__title">稀有度</h3>
        {RARITY_DEFS.map(r => (
          <FilterRow
            key={r.id}
            active={state.rarities.has(r.id)}
            onClick={() => toggle<Rarity>('rarities', r.id)}
            leading={<span className={`rarity rarity--${r.id.toLowerCase()}`} />}
            label={r.name}
            count={counts.rarities[r.id] ?? 0}
          />
        ))}
      </div>

      {racesSorted.length > 0 && (
        <div className="panel rail__section">
          <h3 className="rail__title">种族</h3>
          {racesSorted.map(({ id, n }) => (
            <FilterRow
              key={id}
              active={state.races.has(id)}
              onClick={() => toggle<string>('races', id)}
              leading={<span className="swatch" style={{ background: 'linear-gradient(135deg,#b88828,#6b4715)' }} />}
              label={RACE_LABEL[id] ?? id}
              count={n}
            />
          ))}
        </div>
      )}

      <div className="panel rail__section">
        <h3 className="rail__title">关键词</h3>
        <div className="kwgrid">
          {KEYWORDS.map(k => (
            <span
              key={k}
              className={`tag tag--keyword kwtag ${state.keywords.has(k) ? 'kwtag--active' : ''}`}
              onClick={() => toggle<Keyword>('keywords', k)}
            >
              {KEYWORD_LABELS[k].zh}
            </span>
          ))}
        </div>
      </div>

      {(setsSorted.standard.length > 0 || setsSorted.wild.length > 0) && (
        <div className="panel rail__section">
          <h3 className="rail__title">扩展包</h3>

          {setsSorted.standard.length > 0 && (
            <>
              <div className="rail__subhead rail__subhead--standard">
                <span className="rail__subhead-dot rail__subhead-dot--standard" />
                标准
              </div>
              {setsSorted.standard.map(({ id, n }) => (
                <FilterRow
                  key={id}
                  active={state.sets.has(id)}
                  onClick={() => toggle<string>('sets', id)}
                  leading={<span className="swatch swatch--standard" />}
                  label={SET_LABEL[id] ?? id}
                  count={n}
                />
              ))}
            </>
          )}

          {setsSorted.wild.length > 0 && (
            <>
              <div className="rail__subhead rail__subhead--wild">
                <span className="rail__subhead-dot rail__subhead-dot--wild" />
                狂野
              </div>
              {setsSorted.wild.map(({ id, n }) => (
                <FilterRow
                  key={id}
                  active={state.sets.has(id)}
                  onClick={() => toggle<string>('sets', id)}
                  leading={<span className="swatch" style={{ background: 'linear-gradient(135deg,#3a230f,#b88828)' }} />}
                  label={SET_LABEL[id] ?? id}
                  count={n}
                />
              ))}
            </>
          )}
        </div>
      )}
    </aside>
  );
}

type RowProps = {
  active: boolean;
  onClick: () => void;
  leading: React.ReactNode;
  label: string;
  count?: number;
};
function FilterRow({ active, onClick, leading, label, count }: RowProps) {
  return (
    <div
      className={`rail__row ${active ? 'rail__row--active' : ''}`}
      onClick={onClick}
    >
      <div className="rail__row-lead">
        {leading}
        <span className="rail__row-label">{label}</span>
      </div>
      {count != null && <span className="rail__row-count">{count}</span>}
    </div>
  );
}
