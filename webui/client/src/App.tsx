import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './i18n';
import './App.css';

function App() {
  const { t, i18n } = useTranslation();
  const [gameMode, setGameMode] = useState<string | null>(null);

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  if (gameMode) {
    return (
      <div className="app">
        <div className="game-placeholder">
          <h2>Game Board - {gameMode}</h2>
          <p>Game functionality coming soon...</p>
          <button onClick={() => setGameMode(null)}>Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <h1>{t('game.title')}</h1>
      <div className="mode-select">
        <button onClick={() => setGameMode('pve')}>{t('game.mode.pve')}</button>
        <button onClick={() => setGameMode('pvp')}>{t('game.mode.pvp')}</button>
        <button onClick={() => setGameMode('ai')}>{t('game.mode.ai')}</button>
      </div>
      <div className="language-select">
        <button onClick={() => changeLanguage('zhCN')}>简体中文</button>
        <button onClick={() => changeLanguage('enUS')}>English</button>
      </div>
    </div>
  );
}

export default App;
