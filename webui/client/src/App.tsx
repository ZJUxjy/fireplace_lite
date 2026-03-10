import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './i18n';
import './App.css';
import { GameBoard } from './components/GameBoard';

function App() {
  const { t, i18n } = useTranslation();
  const [gameMode, setGameMode] = useState<string | null>(null);

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  if (gameMode) {
    return <GameBoard mode={gameMode} onBack={() => setGameMode(null)} />;
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
