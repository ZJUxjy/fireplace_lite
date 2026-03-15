import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './i18n';
import './App.css';
import GameBoard from './components/GameBoard';

// 英雄职业列表
const HERO_CLASSES = [
  { id: 'random', name: '随机', nameEn: 'Random', icon: '🎲' },
  { id: 'mage', name: '法师', nameEn: 'Mage', icon: '🔮' },
  { id: 'hunter', name: '猎人', nameEn: 'Hunter', icon: '🏹' },
  { id: 'priest', name: '牧师', nameEn: 'Priest', icon: '✨' },
  { id: 'shaman', name: '萨满', nameEn: 'Shaman', icon: '🌩️' },
  { id: 'paladin', name: '圣骑士', nameEn: 'Paladin', icon: '⚔️' },
  { id: 'warlock', name: '术士', nameEn: 'Warlock', icon: '👹' },
  { id: 'warrior', name: '战士', nameEn: 'Warrior', icon: '🛡️' },
  { id: 'rogue', name: '盗贼', nameEn: 'Rogue', icon: '🗡️' },
  { id: 'druid', name: '德鲁伊', nameEn: 'Druid', icon: '🌿' },
  { id: 'demonhunter', name: '恶魔猎手', nameEn: 'Demon Hunter', icon: '👁️' },
];

function App() {
  const { t, i18n } = useTranslation();
  const [gameMode, setGameMode] = useState<string | null>(null);
  const [selectedClass, setSelectedClass] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  const handleStartGame = (mode: string) => {
    setGameMode(mode);
    setSelectedClass(null);
  };

  const handleSelectClass = (classId: string) => {
    setSelectedClass(classId);
  };

  const handleBack = () => {
    if (selectedClass !== null) {
      setSelectedClass(null);
    } else if (gameMode !== null) {
      setGameMode(null);
    }
  };

  // 游戏进行中
  if (gameMode && selectedClass !== null) {
    return <GameBoard mode={gameMode} playerClass={selectedClass} onBack={handleBack} />;
  }

  // 选择英雄
  if (gameMode) {
    return (
      <div className="app">
        <div className="app-content">
          <h1>Fireplace</h1>
          <h2>{t('game.selectHero')}</h2>

          <div className="hero-select">
            {HERO_CLASSES.map((hero) => (
              <button
                key={hero.id}
                className="hero-btn"
                onClick={() => handleSelectClass(hero.id)}
              >
                <span className="hero-icon">{hero.icon}</span>
                <span className="hero-name">
                  {i18n.language === 'zhCN' ? hero.name : hero.nameEn}
                </span>
              </button>
            ))}
          </div>

          <button className="back-btn" onClick={handleBack}>← {t('ui.back')}</button>
        </div>
      </div>
    );
  }

  // 主菜单
  return (
    <div className="app">
      <div className="app-content">
        <h1>Fireplace</h1>
        <h2>Hearthstone Simulator</h2>

        <div className="mode-select">
          <button onClick={() => handleStartGame('pve')}>{t('game.mode.pve')}</button>
          <button onClick={() => handleStartGame('pvp')}>{t('game.mode.pvp')}</button>
          <button onClick={() => handleStartGame('ai')}>{t('game.mode.ai')}</button>
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
