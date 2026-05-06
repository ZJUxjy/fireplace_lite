import { useEffect, useState } from 'react';
import type { Deck } from '../types/deck';
import {
  listDecks, deleteDeck, importDeckFromDeckstring, saveDeck, deckCardCount,
} from '../services/deckStore';
import { loadCatalog } from '../services/cardCatalog';
import { HERO_CLASSES } from '../types/deck';
import './DeckList.css';

type Props = {
  onOpenDeck: (deckId: string) => void;
  onCreateDeck: (heroClass: string) => void;
  onBrowseAll: () => void;
  onBack: () => void;
};

const HERO_LABEL: Record<string, { name: string; icon: string }> = {
  MAGE: { name: '法师', icon: '🔮' },
  HUNTER: { name: '猎人', icon: '🏹' },
  PRIEST: { name: '牧师', icon: '✨' },
  SHAMAN: { name: '萨满', icon: '🌩️' },
  PALADIN: { name: '圣骑士', icon: '⚔️' },
  WARLOCK: { name: '术士', icon: '👹' },
  WARRIOR: { name: '战士', icon: '🛡️' },
  ROGUE: { name: '盗贼', icon: '🗡️' },
  DRUID: { name: '德鲁伊', icon: '🌿' },
  DEMONHUNTER: { name: '恶魔猎手', icon: '👁️' },
};

export default function DeckList(props: Props) {
  const [decks, setDecks] = useState<Deck[]>(listDecks());
  /** Warm catalog in background so「浏览全卡库」opens with data sooner. */
  useEffect(() => {
    loadCatalog().catch(() => {});
  }, []);
  const [showNewClass, setShowNewClass] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [importText, setImportText] = useState('');
  const [importName, setImportName] = useState('');
  const [error, setError] = useState('');

  const refresh = () => setDecks(listDecks());

  const onDelete = (id: string, name: string) => {
    if (confirm(`确认删除卡组「${name}」?`)) {
      deleteDeck(id);
      refresh();
    }
  };

  const onImport = async () => {
    if (!importText.trim()) return;
    try {
      const d = await importDeckFromDeckstring(importText.trim(), importName.trim() || '导入的卡组');
      saveDeck(d);
      setShowImport(false);
      setImportText(''); setImportName(''); setError('');
      refresh();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <div className="deck-list">
      <div className="deck-list__header">
        <h2>我的卡组</h2>
        <div className="deck-list__actions">
          <button onClick={() => setShowNewClass(true)}>+ 新建</button>
          <button onClick={() => setShowImport(true)}>📋 导入 deckstring</button>
          <button onClick={props.onBrowseAll}>🔍 浏览全卡库</button>
          <button onClick={props.onBack}>← 返回</button>
        </div>
      </div>

      <div className="deck-list__grid">
        {decks.length === 0 && (
          <div className="deck-list__empty">还没有卡组,点"新建"或"导入"开始</div>
        )}
        {decks.map(d => {
          const hero = HERO_LABEL[d.hero_class] ?? { name: d.hero_class, icon: '?' };
          return (
            <div key={d.id} className="deck-card" onClick={() => props.onOpenDeck(d.id)}>
              <div className="deck-card__hero">{hero.icon}</div>
              <div className="deck-card__body">
                <div className="deck-card__name">{d.name}</div>
                <div className="deck-card__meta">{hero.name} · {d.format} · {deckCardCount(d)}/30</div>
              </div>
              <button className="deck-card__del" onClick={(e) => { e.stopPropagation(); onDelete(d.id, d.name); }}>×</button>
            </div>
          );
        })}
      </div>

      {showNewClass && (
        <div className="deck-list__modal" onClick={() => setShowNewClass(false)}>
          <div className="deck-list__modal-content" onClick={e => e.stopPropagation()}>
            <h3>选择职业</h3>
            <div className="deck-list__class-grid">
              {HERO_CLASSES.map(c => (
                <button key={c} onClick={() => { setShowNewClass(false); props.onCreateDeck(c); }}>
                  {HERO_LABEL[c].icon} {HERO_LABEL[c].name}
                </button>
              ))}
            </div>
            <button onClick={() => setShowNewClass(false)}>取消</button>
          </div>
        </div>
      )}

      {showImport && (
        <div className="deck-list__modal" onClick={() => setShowImport(false)}>
          <div className="deck-list__modal-content" onClick={e => e.stopPropagation()}>
            <h3>导入 deckstring</h3>
            <input placeholder="卡组名(可选)" value={importName} onChange={e => setImportName(e.target.value)} />
            <textarea
              placeholder="粘贴炉石 deckstring..."
              value={importText}
              onChange={e => setImportText(e.target.value)}
              rows={4}
            />
            {error && <div className="deck-list__error">{error}</div>}
            <div>
              <button onClick={onImport}>导入</button>
              <button onClick={() => { setShowImport(false); setError(''); }}>取消</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
