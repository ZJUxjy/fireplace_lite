import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './i18n';
import './App.css';
import { GameBoard } from './components/GameBoard';

function App() {
  const { t, i18n } = useTranslation();
  const [gameMode, setGameMode] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  if (gameMode) {
    return <GameBoard mode={gameMode} onBack={() => setGameMode(null)} />;
  }

  return (
    <div className="app">
      <div className="app-content">
        <h1>Fireplace</h1>
        <h2>Hearthstone Simulator</h2>

        <div className="mode-select">
          <button onClick={() => setGameMode('pve')}>{t('game.mode.pve')}</button>
          <button onClick={() => setGameMode('pvp')}>{t('game.mode.pvp')}</button>
          <button onClick={() => setGameMode('ai')}>{t('game.mode.ai')}</button>
        </div>

        <button className="settings-btn" onClick={() => setShowSettings(!showSettings)}>
          ⚙️ {t('ui.settings')}
        </button>

        {showSettings && (
          <div className="settings-menu">
            <h3>{t('ui.language')}</h3>
            <div className="language-options">
              <button
                className={i18n.language === 'zhCN' ? 'active' : ''}
                onClick={() => changeLanguage('zhCN')}
              >
                简体中文
              </button>
              <button
                className={i18n.language === 'enUS' ? 'active' : ''}
                onClick={() => changeLanguage('enUS')}
              >
                English
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
