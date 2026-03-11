import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { gameService, type GameState, type CardData } from '../services/gameService';
import './GameBoard.css';

interface CardData {
  name: string;
  cost: number;
  atk?: number;
  health?: number;
  text?: string;
  race?: string;
  mechanics?: string[];
}

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

// 攻击箭头 SVG 组件
function AttackArrow({ start, end }: { start: { x: number; y: number }; end: { x: number; y: number } }) {
  // 计算贝塞尔曲线控制点（向上弯曲的弧线）
  const midX = (start.x + end.x) / 2;
  const midY = Math.min(start.y, end.y) - 60;

  const pathD = `M ${start.x} ${start.y} Q ${midX} ${midY} ${end.x} ${end.y}`;

  return (
    <svg
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 1000,
      }}
    >
      <defs>
        <linearGradient id="attackGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="rgba(255,255,255,1)" />
          <stop offset="100%" stopColor="rgba(255,0,0,1)" />
        </linearGradient>
        <marker
          id="arrowhead"
          markerWidth="12"
          markerHeight="8"
          refX="10"
          refY="4"
          orient="auto"
        >
          <polygon points="0 0, 12 4, 0 8" fill="#ff0000" />
        </marker>
      </defs>
      <path
        d={pathD}
        stroke="url(#attackGradient)"
        strokeWidth="4"
        fill="none"
        strokeLinecap="round"
        markerEnd="url(#arrowhead)"
      />
    </svg>
  );
}

export function GameBoard({ mode, onBack }: GameBoardProps) {
  const { t, i18n } = useTranslation();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [connecting, setConnecting] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [actionLog, setActionLog] = useState<string[]>([]);
  const [showTurnBanner, setShowTurnBanner] = useState(false);
  const [selectedCard, setSelectedCard] = useState<{ card: CardData; index: number } | null>(null);
  const [hoveredCard, setHoveredCard] = useState<{ card: CardData; x: number; y: number } | null>(null);
  const [hoveredMinion, setHoveredMinion] = useState<{ minion: MinionData; x: number; y: number } | null>(null);
  const [draggedCard, setDraggedCard] = useState<number | null>(null);
  const [attackingMinion, setAttackingMinion] = useState<number | null>(null);
  const [arrowStart, setArrowStart] = useState<{ x: number; y: number } | null>(null);
  const [arrowEnd, setArrowEnd] = useState<{ x: number; y: number } | null>(null);
  const prevTurnRef = useRef<number>(0);
  const prevPlayerRef = useRef<string>('');

  useEffect(() => {
    gameService.createGame(mode);

    const handleGameState = (data: { game_id: string; state: GameState }) => {
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
    };

    const handleError = (data: { message: string }) => {
      console.error('Game error:', data.message);
      setConnecting(false);
    };

    gameService.onGameState(handleGameState);
    gameService.onError(handleError);

    return () => {
      // 清理时直接断开连接
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
  const handleCardClick = (card: CardData, index: number) => {
    setSelectedCard({ card, index });
  };

  // 计算有效攻击目标
  const getValidAttackTargets = () => {
    if (!gameState || attackingMinion === null) return { minions: [] as number[], canAttackHero: false };

    const opponent = gameState.opponent;

    // 如果对手有嘲讽随从，只能攻击嘲讽随从
    if (opponent.has_taunt) {
      return {
        minions: opponent.field
          .map((m, i) => m.taunt ? i : -1)
          .filter(i => i >= 0),
        canAttackHero: false
      };
    }

    // 没有嘲讽，可以攻击所有随从和英雄
    return {
      minions: opponent.field.map((_, i) => i),
      canAttackHero: true
    };
  };

  const validTargets = getValidAttackTargets();

  // 随从攻击开始（鼠标按下）
  const handleAttackMouseDown = (e: React.MouseEvent, index: number) => {
    const minion = gameState!.player.field[index];
    if (!minion.can_attack) return;

    e.preventDefault();
    setAttackingMinion(index);
    const rect = e.currentTarget.getBoundingClientRect();
    const startX = rect.left + rect.width / 2;
    const startY = rect.top + rect.height / 2;
    setArrowStart({ x: startX, y: startY });
    setArrowEnd({ x: e.clientX, y: e.clientY });
  };

  if (connecting || !gameState) {
    return (
      <div className="game-container">
        <header className="game-header">
          <h1>Fireplace</h1>
        </header>
        <div className="game-loading">
          <div className="loading-spinner">
            <div className="spinner">
              <div className="spinner-ring"></div>
              <div className="spinner-ring"></div>
              <div className="spinner-ring"></div>
            </div>
            <div className="loading-text">正在初始化卡牌...</div>
          </div>
          <button className="back-btn" onClick={onBack}>← Back</button>
        </div>
      </div>
    );
  }

  const isMyTurn = gameState.current_player === 'player1';

  // 全局鼠标移动（更新箭头和攻击）
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (attackingMinion !== null) {
        setArrowEnd({ x: e.clientX, y: e.clientY });
      }
    };

    const handleMouseUp = (e: MouseEvent) => {
      if (attackingMinion !== null) {
        // 检查鼠标释放位置是否在有效目标上
        const target = document.elementFromPoint(e.clientX, e.clientY);
        if (target) {
          // 检查是否点击了敌方英雄
          const heroArea = target.closest('.opponent-hero-area');
          if (heroArea && validTargets.canAttackHero) {
            gameService.attack(attackingMinion, 'hero');
          }
          // 检查是否点击了敌方随从
          const minionEl = target.closest('.opponent-field .minion');
          if (minionEl) {
            const index = parseInt(minionEl.getAttribute('data-index') || '-1');
            if (validTargets.minions.includes(index)) {
              gameService.attack(attackingMinion, `minion-${index}`);
            }
          }
        }
        setAttackingMinion(null);
        setArrowStart(null);
        setArrowEnd(null);
      }
    };

    if (attackingMinion !== null) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [attackingMinion, validTargets]);

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
            <div className={`hero-portrait opponent hero-${getHeroClass(gameState.opponent.hero)} ${validTargets.canAttackHero ? 'valid-target' : ''}`}>
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
              <div
                key={i}
                data-index={i}
                className={`minion ${minion.taunt ? 'taunt' : ''} ${validTargets.minions.includes(i) ? 'valid-target' : ''}`}
                onMouseEnter={(e) => setHoveredMinion({ minion, x: e.clientX, y: e.clientY })}
                onMouseLeave={() => setHoveredMinion(null)}
                onMouseMove={(e) => hoveredMinion && setHoveredMinion({ minion, x: e.clientX, y: e.clientY })}
              >
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
              <div
                key={i}
                className={`minion ${minion.can_attack && isMyTurn ? 'can-attack' : ''} ${minion.taunt ? 'taunt' : ''}`}
                onMouseDown={(e) => handleAttackMouseDown(e, i)}
                onMouseEnter={(e) => setHoveredMinion({ minion, x: e.clientX, y: e.clientY })}
                onMouseLeave={() => setHoveredMinion(null)}
                onMouseMove={(e) => hoveredMinion && setHoveredMinion({ minion, x: e.clientX, y: e.clientY })}
              >
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
            {gameState.player.hand.map((card, i) => {
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
                  onClick={() => handleCardClick(card, i)}
                  onMouseEnter={(e) => setHoveredCard({ card, x: e.clientX, y: e.clientY })}
                  onMouseLeave={() => setHoveredCard(null)}
                  onMouseMove={(e) => hoveredCard && setHoveredCard({ card, x: e.clientX, y: e.clientY })}
                >
                  <div className="card-cost">{card.cost}</div>
                  <div className="card-name">{card.name}</div>
                  {card.atk !== undefined && card.health !== undefined && (
                    <div className="card-footer">
                      <span className="card-atk">{card.atk}</span>
                      <span className="card-health">{card.health}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* 悬浮提示 - 使用 fixed position 避免遮挡和布局抖动 */}
          {hoveredCard && (
            <div
              className="tooltip-fixed"
              style={{
                left: hoveredCard.x + 15,
                top: hoveredCard.y
              }}
            >
              <div className="tooltip-name">{hoveredCard.card.name}</div>
              {hoveredCard.card.race && <div className="tooltip-race">{hoveredCard.card.race}</div>}
              {hoveredCard.card.text && <div className="tooltip-text" dangerouslySetInnerHTML={{ __html: hoveredCard.card.text }} />}
              {hoveredCard.card.mechanics && hoveredCard.card.mechanics.length > 0 && (
                <div className="tooltip-mechanics">
                  {hoveredCard.card.mechanics.map((m, idx) => (
                    <span key={idx} className="mechanic-tag">{m}</span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* 随从悬浮提示 */}
          {hoveredMinion && (
            <div
              className="tooltip-fixed"
              style={{
                left: hoveredMinion.x + 15,
                top: hoveredMinion.y
              }}
            >
              <div className="tooltip-name">{hoveredMinion.minion.name}</div>
              {hoveredMinion.minion.race && <div className="tooltip-race">{hoveredMinion.minion.race}</div>}
              <div className="tooltip-stats">
                <span className="tooltip-atk">⚔️ {hoveredMinion.minion.atk}</span>
                <span className="tooltip-health">❤️ {hoveredMinion.minion.health}</span>
              </div>
              {hoveredMinion.minion.text && <div className="tooltip-text" dangerouslySetInnerHTML={{ __html: hoveredMinion.minion.text }} />}
              {hoveredMinion.minion.mechanics && hoveredMinion.minion.mechanics.length > 0 && (
                <div className="tooltip-mechanics">
                  {hoveredMinion.minion.mechanics.map((m, idx) => (
                    <span key={idx} className="mechanic-tag">{m}</span>
                  ))}
                </div>
              )}
            </div>
          )}

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
                  <div className="card-tooltip-cost">{selectedCard.card.cost}</div>
                  <div className="card-tooltip-name">{selectedCard.card.name}</div>
                </div>
                <div className="card-tooltip-body">
                  {selectedCard.card.race && <p className="tooltip-race">{selectedCard.card.race}</p>}
                  {selectedCard.card.atk !== undefined && selectedCard.card.health !== undefined && (
                    <div className="tooltip-stats">
                      <span className="tooltip-atk">⚔️ {selectedCard.card.atk}</span>
                      <span className="tooltip-health">❤️ {selectedCard.card.health}</span>
                    </div>
                  )}
                  {selectedCard.card.text && <p className="tooltip-text" dangerouslySetInnerHTML={{ __html: selectedCard.card.text }} />}
                  {selectedCard.card.mechanics && selectedCard.card.mechanics.length > 0 && (
                    <div className="tooltip-mechanics">
                      {selectedCard.card.mechanics.map((m, idx) => (
                        <span key={idx} className="mechanic-tag">{m}</span>
                      ))}
                    </div>
                  )}
                </div>
                <button className="card-tooltip-close" onClick={() => setSelectedCard(null)}>×</button>
              </div>
            </div>
          )}

          {/* 攻击箭头 */}
          {arrowStart && arrowEnd && (
            <AttackArrow start={arrowStart} end={arrowEnd} />
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
