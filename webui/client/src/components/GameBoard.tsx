import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { gameService, type GameState } from '../services/gameService';
import './GameBoard.css';

interface GameBoardProps {
  mode: string;
  onBack: () => void;
}

// 英雄职业映射
const HERO_CLASSES: Record<string, string> = {
  'Rexxar': 'hunter',
  'Jaina Proudmoore': 'mage',
  'Anduin Wrynn': 'priest',
  'Thrall': 'shaman',
  'Uther Lightbringer': 'paladin',
  'Garrosh Hellscream': 'warrior',
  'Valeera Sanguinar': 'rogue',
  'Gul\'dan': 'warlock',
  'Malfurion Stormrage': 'druid',
  'Illidan Stormrage': 'demonhunter',
};

function getHeroClass(heroName: string): string {
  return HERO_CLASSES[heroName] || 'neutral';
}

export function GameBoard({ mode, onBack }: GameBoardProps) {
  const { t, i18n } = useTranslation();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [connecting, setConnecting] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [actionLog, setActionLog] = useState<string[]>([]);
  const [showTurnBanner, setShowTurnBanner] = useState(false);
  const [selectedCard, setSelectedCard] = useState<{ name: string; index: number } | null>(null);
  const [draggedCard, setDraggedCard] = useState<number | null>(null);
  const prevTurnRef = useRef<number>(0);
  const prevPlayerRef = useRef<string>('');

  useEffect(() => {
    gameService.createGame(mode);

    gameService.onGameState((data) => {
      setGameState(data.state);

      // 检测回合切换，显示提示
      const isMyTurn = data.state.current_player === 'player1';
      if (data.state.turn !== prevTurnRef.current || isMyTurn !== (prevPlayerRef.current === 'player1')) {
        if (isMyTurn) {
          setShowTurnBanner(true);
          setTimeout(() => setShowTurnBanner(false), 2000);
        }
      }
      prevTurnRef.current = data.state.turn;
      prevPlayerRef.current = data.state.current_player;

      setConnecting(false);
      setActionLog(prev => [`Turn ${data.state.turn}`, ...prev].slice(0, 20));
    });

    gameService.onError((data) => {
      console.error('Game error:', data.message);
      setConnecting(false);
    });

    return () => {
      gameService.cleanup();
    };
  }, [mode]);

  const handleEndTurn = () => {
    gameService.endTurn();
  };

  const handleNewGame = () => {
    setGameState(null);
    setConnecting(true);
    setActionLog([]);
    setSelectedCard(null);
    prevTurnRef.current = 0;
    prevPlayerRef.current = '';
    gameService.createGame(mode);
  };

  // 处理卡牌拖拽
  const handleDragStart = (e: React.DragEvent, index: number) => {
    setDraggedCard(index);
    e.dataTransfer.setData('text/plain', index.toString());
  };

  const handleDragEnd = () => {
    setDraggedCard(null);
  };

  // 处理拖拽到战场区域
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const cardIndex = parseInt(e.dataTransfer.getData('text/plain'));
    if (!isNaN(cardIndex) && isMyTurn) {
      gameService.playCard(cardIndex);
    }
    setDraggedCard(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  // 点击卡牌查看详情
  const handleCardClick = (name: string, index: number) => {
    setSelectedCard({ name, index });
  };

  if (connecting || !gameState) {
    return (
      <div className="game-container">
        <header className="game-header">
          <h1>Fireplace</h1>
        </header>
        <div className="game-loading">
          <div className="loading-spinner">Loading...</div>
          <button className="back-btn" onClick={onBack}>← Back</button>
        </div>
      </div>
    );
  }

  const isMyTurn = gameState.current_player === 'player1';

  return (
    <div className="game-container">
      {/* 顶部标题栏 */}
      <header className="game-header">
        <button className="header-back-btn" onClick={onBack}>←</button>
        <h1>Fireplace</h1>
        <button className="header-settings-btn" onClick={() => setShowSettings(!showSettings)}>
          ⚙️
        </button>
        {showSettings && (
          <div className="header-settings-menu">
            <h4>{t('ui.language')}</h4>
            <button
              className={i18n.language === 'zhCN' ? 'active' : ''}
              onClick={() => i18n.changeLanguage('zhCN')}
            >
              简体中文
            </button>
            <button
              className={i18n.language === 'enUS' ? 'active' : ''}
              onClick={() => i18n.changeLanguage('enUS')}
            >
              English
            </button>
          </div>
        )}
      </header>

      <div className="game-main">
        {/* 左侧游戏棋盘 */}
        <div
          className="game-board"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {/* 对手手牌 */}
          <div className="opponent-hand-area">
            {Array(gameState.opponent.hand_count).fill(0).map((_, i) => (
              <div key={i} className="card-back-small" />
            ))}
          </div>

          {/* 对手英雄区 */}
          <div className="hero-area opponent-hero-area">
            <div className="weapon-slot">
              <div className="weapon-slot-empty" />
            </div>
            <div className={`hero-portrait opponent hero-${getHeroClass(gameState.opponent.hero)}`}>
              <span className="hero-initial">{gameState.opponent.hero.charAt(0)}</span>
            </div>
            <div className="hero-stats">
              <div className="hero-health">❤️ {gameState.opponent.health}</div>
            </div>
            <div className="hero-power">
              <div className="hero-power-empty" />
            </div>
          </div>

          {/* 对手随从区域 */}
          <div className="field opponent-field">
            {gameState.opponent.field.map((minion, i) => (
              <div key={i} className="minion">
                <div className="minion-body">
                  <div className="minion-stats">
                    <span className="minion-atk">{minion.atk}</span>
                    <span className="minion-health">{minion.health}</span>
                  </div>
                  <div className="minion-name">{minion.name}</div>
                </div>
              </div>
            ))}
            {gameState.opponent.field.length === 0 && <div className="field-placeholder" />}
          </div>

          {/* 中央分隔线 */}
          <div className="field-divider">
            <div className="turn-indicator">
              {t('game.turn')} {gameState.turn}
            </div>
          </div>

          {/* 玩家随从区域 */}
          <div className="field player-field">
            {gameState.player.field.map((minion, i) => (
              <div key={i} className="minion playable">
                <div className="minion-body">
                  <div className="minion-stats">
                    <span className="minion-atk">{minion.atk}</span>
                    <span className="minion-health">{minion.health}</span>
                  </div>
                  <div className="minion-name">{minion.name}</div>
                </div>
              </div>
            ))}
            {gameState.player.field.length === 0 && <div className="field-placeholder" />}
          </div>

          {/* 玩家英雄区 */}
          <div className="hero-area player-hero-area">
            <div className="weapon-slot">
              <div className="weapon-slot-empty" />
            </div>
            <div className={`hero-portrait player hero-${getHeroClass(gameState.player.hero)}`}>
              <span className="hero-initial">{gameState.player.hero.charAt(0)}</span>
            </div>
            <div className="hero-stats">
              <div className="mana-crystal">💎 {gameState.player.mana}/{gameState.player.max_mana}</div>
              <div className="hero-health">❤️ {gameState.player.health}</div>
            </div>
            <div className="hero-power">
              <div className="hero-power-empty" />
            </div>
          </div>

          {/* 玩家手牌 - 拖拽打出 */}
          <div className="player-hand-area">
            {gameState.player.hand.map((cardName, i) => {
              const totalCards = gameState.player.hand.length;
              const angle = totalCards > 1 ? ((i / (totalCards - 1)) - 0.5) * 30 : 0;
              return (
                <div
                  key={i}
                  className={`card ${isMyTurn ? 'playable' : ''} ${draggedCard === i ? 'dragging' : ''}`}
                  style={{ transform: `rotate(${angle}deg)` }}
                  draggable={isMyTurn}
                  onDragStart={(e) => handleDragStart(e, i)}
                  onDragEnd={handleDragEnd}
                  onClick={() => handleCardClick(cardName, i)}
                >
                  <div className="card-cost">{i + 1}</div>
                  <div className="card-name">{cardName}</div>
                </div>
              );
            })}
          </div>

          {/* 回合提示 - 只在玩家回合开始时显示 */}
          {showTurnBanner && (
            <div className="turn-banner">
              {t('game.yourTurn')}
            </div>
          )}

          {/* 卡牌详情弹窗 */}
          {selectedCard && (
            <div className="card-tooltip" onClick={() => setSelectedCard(null)}>
              <div className="card-tooltip-content" onClick={(e) => e.stopPropagation()}>
                <div className="card-tooltip-header">
                  <div className="card-tooltip-cost">{selectedCard.index + 1}</div>
                  <div className="card-tooltip-name">{selectedCard.name}</div>
                </div>
                <div className="card-tooltip-body">
                  <p>卡牌详情</p>
                </div>
                <button className="card-tooltip-close" onClick={() => setSelectedCard(null)}>×</button>
              </div>
            </div>
          )}
        </div>

        {/* 中间控制按钮 */}
        <div className="game-controls">
          <button
            className="end-turn-btn"
            onClick={handleEndTurn}
            disabled={!isMyTurn || !gameState.player.can_end_turn}
          >
            {t('game.endTurn')}
          </button>
          <button className="concede-btn">{t('game.concede')}</button>
          <button className="new-game-btn" onClick={handleNewGame}>🔄 {t('ui.newGame')}</button>
        </div>

        {/* 右侧操作日志 */}
        <aside className="action-log">
          <h3>📜 {t('ui.actionLog')}</h3>
          <div className="log-content">
            {actionLog.map((log, i) => (
              <div key={i} className="log-entry">{log}</div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
