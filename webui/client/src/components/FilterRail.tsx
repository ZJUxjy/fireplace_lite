import { useMemo } from 'react';
import type { Card, CardType, Rarity } from '../types/deck';
import { KEYWORD_TOKENS, type Keyword } from '../services/cardCatalog';
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
  CORE: '核心', EXPERT1: '经典', NAXX: '纳克萨玛斯', GVG: '哥哥侏儒',
  BRM: '黑石山', TGT: '冠军赛', LOE: '探险者协会', OG: '上古之神',
  KARA: '卡拉赞', GANGS: '加基森', UNGORO: '安戈洛',
  ICECROWN: '冰封王座', LOOTAPALOOZA: '狗头人', GILNEAS: '女巫森林',
  BOOMSDAY: '砰砰计划', TROLL: '拉斯塔哈', DALARAN: '暗影崛起',
  ULDUM: '奥丹姆', SCHOLOMANCE: '通灵学院', BLACK_TEMPLE: '外域灰烬',
  DRAGONS: '巨龙降临',
};

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
    return Object.entries(counts.sets)
      .sort((a, b) => b[1] - a[1])
      .map(([id, n]) => ({ id, n }));
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
          {KEYWORD_TOKENS.map(k => (
            <span
              key={k}
              className={`tag tag--keyword kwtag ${state.keywords.has(k) ? 'kwtag--active' : ''}`}
              onClick={() => toggle<Keyword>('keywords', k)}
            >
              {k}
            </span>
          ))}
        </div>
      </div>

      {setsSorted.length > 0 && (
        <div className="panel rail__section">
          <h3 className="rail__title">扩展包</h3>
          {setsSorted.map(({ id, n }) => (
            <FilterRow
              key={id}
              active={state.sets.has(id)}
              onClick={() => toggle<string>('sets', id)}
              leading={<span className="swatch" style={{ background: 'linear-gradient(135deg,#3a230f,#b88828)' }} />}
              label={SET_LABEL[id] ?? id}
              count={n}
            />
          ))}
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
