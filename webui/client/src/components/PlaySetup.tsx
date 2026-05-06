import { useEffect, useState } from 'react';
import type { Deck, DeckSpec } from '../types/deck';
import { listDecks, exportDeckToDeckstring } from '../services/deckStore';
import { HERO_CLASSES } from '../types/deck';
import './PlaySetup.css';

type Props = {
  mode: 'pve' | 'pvp' | 'ai';
  onStart: (p1: DeckSpec, p2: DeckSpec) => void;
  onBack: () => void;
};

type SlotState = {
  type: 'saved' | 'deckstring' | 'random';
  deckId: string;
  deckstring: string;
  randomClass: string;
};

const HERO_LABEL: Record<string, string> = {
  MAGE: '🔮 法师', HUNTER: '🏹 猎人', PRIEST: '✨ 牧师', SHAMAN: '🌩️ 萨满',
  PALADIN: '⚔️ 圣骑', WARLOCK: '👹 术士', WARRIOR: '🛡️ 战士', ROGUE: '🗡️ 盗贼',
  DRUID: '🌿 德鲁伊', DEMONHUNTER: '👁️ 恶魔猎手',
};

function defaultSlot(filledRandom: boolean): SlotState {
  return {
    type: filledRandom ? 'random' : 'saved',
    deckId: '',
    deckstring: '',
    randomClass: filledRandom ? 'ANY' : 'MAGE',
  };
}

async function slotToSpec(slot: SlotState, decks: Deck[]): Promise<DeckSpec> {
  if (slot.type === 'random') {
    return { type: 'random', card_class: slot.randomClass };
  }
  if (slot.type === 'deckstring') {
    if (!slot.deckstring.trim()) throw new Error('请粘贴 deckstring');
    return { type: 'deckstring', value: slot.deckstring.trim() };
  }
  // saved
  const d = decks.find(d => d.id === slot.deckId);
  if (!d) throw new Error('请选择已存卡组');
  const ds = await exportDeckToDeckstring(d);
  return { type: 'deckstring', value: ds };
}

export default function PlaySetup(props: Props) {
  const isPvp = props.mode === 'pvp';
  const [decks, setDecks] = useState<Deck[]>(listDecks());
  const [p1, setP1] = useState<SlotState>(defaultSlot(false));
  const [p2, setP2] = useState<SlotState>(defaultSlot(!isPvp));
  const [error, setError] = useState('');

  useEffect(() => { setDecks(listDecks()); }, []);

  const start = async () => {
    try {
      const p1Spec = await slotToSpec(p1, decks);
      const p2Spec = await slotToSpec(p2, decks);
      props.onStart(p1Spec, p2Spec);
    } catch (e) { setError((e as Error).message); }
  };

  const renderSlot = (label: string, slot: SlotState, set: (s: SlotState) => void) => (
    <div className="play-setup__slot">
      <div className="play-setup__slot-label">{label}</div>
      <select value={slot.type} onChange={e => set({ ...slot, type: e.target.value as SlotState['type'] })}>
        <option value="saved">已存卡组</option>
        <option value="deckstring">粘贴 deckstring</option>
        <option value="random">随机职业</option>
      </select>
      {slot.type === 'saved' && (
        <select value={slot.deckId} onChange={e => set({ ...slot, deckId: e.target.value })}>
          <option value="">— 选择卡组 —</option>
          {decks.map(d => <option key={d.id} value={d.id}>{d.name} ({d.hero_class})</option>)}
        </select>
      )}
      {slot.type === 'deckstring' && (
        <textarea
          rows={3}
          placeholder="粘贴 deckstring..."
          value={slot.deckstring}
          onChange={e => set({ ...slot, deckstring: e.target.value })}
        />
      )}
      {slot.type === 'random' && (
        <select value={slot.randomClass} onChange={e => set({ ...slot, randomClass: e.target.value })}>
          <option value="ANY">随机职业</option>
          {HERO_CLASSES.map(c => <option key={c} value={c}>{HERO_LABEL[c]}</option>)}
        </select>
      )}
    </div>
  );

  return (
    <div className="play-setup">
      <h2>开始对局 · {props.mode.toUpperCase()}</h2>
      <div className="play-setup__slots">
        {renderSlot(isPvp ? '玩家 1' : '玩家', p1, setP1)}
        {renderSlot(isPvp ? '玩家 2' : '对手', p2, setP2)}
      </div>
      {error && <div className="play-setup__error">{error}</div>}
      <div className="play-setup__buttons">
        <button onClick={start}>开始游戏</button>
        <button onClick={props.onBack}>返回</button>
      </div>
    </div>
  );
}
