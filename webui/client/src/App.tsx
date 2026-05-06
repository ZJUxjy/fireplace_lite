import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './i18n';
import './App.css';
import GameBoard from './components/GameBoard';
import DeckList from './components/DeckList';
import DeckEditor from './components/DeckEditor';
import PlaySetup from './components/PlaySetup';
import type { DeckSpec } from './types/deck';
import { newDeck } from './services/deckStore';

type View =
  | { kind: 'menu' }
  | { kind: 'decks-list' }
  | { kind: 'deck-edit'; deckId: string | null | 'new'; initialDeck?: import('./types/deck').Deck }
  | { kind: 'play-setup'; mode: 'pve' | 'pvp' | 'ai' }
  | { kind: 'in-game'; mode: string; p1: DeckSpec; p2: DeckSpec };

function App() {
  const { t, i18n } = useTranslation();
  const [view, setView] = useState<View>({ kind: 'menu' });
  const [showSettings, setShowSettings] = useState(false);

  const changeLanguage = (lang: string) => i18n.changeLanguage(lang);

  if (view.kind === 'in-game') {
    return (
      <GameBoard
        mode={view.mode}
        p1Spec={view.p1}
        p2Spec={view.p2}
        onBack={() => setView({ kind: 'menu' })}
      />
    );
  }

  if (view.kind === 'play-setup') {
    return (
      <PlaySetup
        mode={view.mode}
        onStart={(p1, p2) => setView({ kind: 'in-game', mode: view.mode, p1, p2 })}
        onBack={() => setView({ kind: 'menu' })}
      />
    );
  }

  if (view.kind === 'deck-edit') {
    return (
      <DeckEditor
        deckId={view.deckId}
        initialDeck={view.initialDeck}
        onBack={() => setView({ kind: 'decks-list' })}
      />
    );
  }

  if (view.kind === 'decks-list') {
    return (
      <DeckList
        onOpenDeck={(id) => setView({ kind: 'deck-edit', deckId: id })}
        onCreateDeck={(cls) => {
          const d = newDeck(cls);
          setView({ kind: 'deck-edit', deckId: 'new', initialDeck: d });
        }}
        onBrowseAll={() => setView({ kind: 'deck-edit', deckId: null })}
        onBack={() => setView({ kind: 'menu' })}
      />
    );
  }

  // menu
  return (
    <div className="app">
      <div className="app-content">
        <h1>Fireplace</h1>
        <h2>Hearthstone Simulator</h2>

        <div className="mode-select">
          <button onClick={() => setView({ kind: 'play-setup', mode: 'pve' })}>{t('game.mode.pve')}</button>
          <button onClick={() => setView({ kind: 'play-setup', mode: 'pvp' })}>{t('game.mode.pvp')}</button>
          <button onClick={() => setView({ kind: 'play-setup', mode: 'ai' })}>{t('game.mode.ai')}</button>
          <button onClick={() => setView({ kind: 'decks-list' })}>{t('ui.decks')}</button>
        </div>

        <button className="settings-btn" onClick={() => setShowSettings(!showSettings)}>
          ⚙️ {t('ui.settings')}
        </button>

        {showSettings && (
          <div className="settings-menu">
            <h3>{t('ui.language')}</h3>
            <div className="language-options">
              <button className={i18n.language === 'zhCN' ? 'active' : ''} onClick={() => changeLanguage('zhCN')}>简体中文</button>
              <button className={i18n.language === 'enUS' ? 'active' : ''} onClick={() => changeLanguage('enUS')}>English</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
