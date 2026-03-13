import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { gameService, type GameState, type CardData } from '../services/gameService';
import './GameBoard.css';

interface GameBoardProps {
  mode: string;
  playerClass?: string;
  onBack: () => void;
}

interface MinionData {
  name: string;
  atk: number;
  health: number;
  can_attack?: boolean;
  taunt?: boolean;
  text?: string;
  race?: string;
  mechanics?: string[];
}

const HERO_CLASSES: Record<string, string> = {
  'Malfurion Stormrage': 'druid',
  'Rexxar': 'hunter',
  'Jaina Proudmoore': 'mage',
  'Uther Lightbringer': 'paladin',
  'Anduin Wrynn': 'priest',
  'Valeera Sanguinar': 'rogue',
  'Thrall': 'shaman',
  'Garrosh Hellscream': 'warrior',
  'Gul\'dan': 'warlock',
  'Illidan Stormrage': 'demonhunter',
};

function getHeroClass(heroName: string): string {
  return HERO_CLASSES[heroName] || 'neutral';
}

// 职业图标映射
const HERO_ICONS: Record<string, string> = {
  'Malfurion Stormrage': '🌿',
  'Rexxar': '🏹',
  'Jaina Proudmoore': '🔮',
  'Uther Lightbringer': '⚔️',
  'Anduin Wrynn': '✨',
  'Valeera Sanguinar': '🗡️',
  'Thrall': '🌩️',
  'Garrosh Hellscream': '🛡️',
  "Gul'dan": '👹',
  'Illidan Stormrage': '👁️',
};

function getHeroClassIcon(heroName: string): string {
  return HERO_ICONS[heroName] || '❓';
}

// 攻击箭头 SVG 组件
function AttackArrow({ start, end }: { start: { x: number; y: number }; end: { x: number; y: number } }) {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  const midX = (start.x + end.x) / 2;
  const midY = (start.y + end.y) / 2;
  const arcHeight = Math.min(distance * 0.3, 100);
  const controlY = midY - arcHeight;
  const pathD = `M ${start.x} ${start.y} Q ${midX} ${controlY} ${end.x} ${end.y}`;

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
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="5"
          orient="auto"
          markerUnits="strokeWidth"
        >
          <path d="M0,0 L0,10 L10,5 Z" fill="#ff4444" />
        </marker>
      </defs>
      <path
        d={pathD}
        stroke="#ff4444"
        strokeWidth="4"
        fill="none"
        markerEnd="url(#arrowhead)"
      />
    </svg>
  );
}

export default function GameBoard({ mode, playerClass = 'random', onBack }: GameBoardProps) {
  const { t, i18n } = useTranslation();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [connecting, setConnecting] = useState(true);
  const [showTurnBanner, setShowTurnBanner] = useState(false);
  const [actionLog, setActionLog] = useState<string[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const [, setSelectedCard] = useState<{ card: CardData; index: number } | null>(null);
  const [hoveredCard, setHoveredCard] = useState<{ card: CardData; x: number; y: number } | null>(null);
  const [hoveredMinion, setHoveredMinion] = useState<{ minion: MinionData; x: number; y: number } | null>(null);
  const [hoveredHeroPower, setHoveredHeroPower] = useState<{ x: number; y: number } | null>(null);
  const [draggedCard, setDraggedCard] = useState<number | null>(null);
  const [attackingMinion, setAttackingMinion] = useState<number | null>(null);
  const [arrowStart, setArrowStart] = useState<{ x: number; y: number } | null>(null);
  const [arrowEnd, setArrowEnd] = useState<{ x: number; y: number } | null>(null);
  const prevTurnRef = useRef<number>(0);
  const prevPlayerRef = useRef<string>('');

  // 目标选择状态
  const [pendingAction, setPendingAction] = useState<{
    type: 'card' | 'hero_power';
    cardIndex?: number;
    targets: string[];
    requiredCount: number;
    validTargets: string[];
  } | null>(null);

  const isMyTurn = gameState?.current_player === 'player1';

  useEffect(() => {
    const handleGameState = (data: { game_id: string; state: GameState }) => {
      setGameState(data.state);

      const isMyTurnNow = data.state.current_player === 'player1';
      if (data.state.turn !== prevTurnRef.current || isMyTurnNow !== (prevPlayerRef.current === 'player1')) {
        if (isMyTurnNow) {
          setShowTurnBanner(true);
          setTimeout(() => setShowTurnBanner(false), 2000);
        }
      }
      prevTurnRef.current = data.state.turn;
      prevPlayerRef.current = data.state.current_player;
      setConnecting(false);
      setActionLog(prev => [`Turn ${data.state.turn}`, ...prev.slice(0, 20)]);
    };

    const handleError = (data: { message: string }) => {
      setActionLog(prev => [`Error: ${data.message}`, ...prev.slice(0, 20)]);
    };

    gameService.createGame(mode, playerClass);
    gameService.onGameState(handleGameState);
    gameService.onError(handleError);

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
    gameService.createGame(mode, playerClass);
  };

  // 处理卡牌拖拽
  const handleDragStart = (e: React.DragEvent, index: number, _card: CardData) => {
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
    if (isNaN(cardIndex) || !isMyTurn || !gameState) return;
    const card = gameState.player.hand[cardIndex];
    if (!card.is_playable) return;

    // 检查是否需要目标
    if (card.requires_target && card.valid_targets && card.valid_targets.length > 0) {
      setPendingAction({
        type: 'card',
        cardIndex,
        targets: [],
        requiredCount: 1,
        validTargets: card.valid_targets,
      });
    } else {
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
    if (opponent.has_taunt) {
      return {
        minions: opponent.field
          .map((m, i) => m.taunt ? i : -1)
          .filter(i => i >= 0),
        canAttackHero: false
      };
    }
    return {
      minions: opponent.field.map((_, i) => i),
      canAttackHero: true
    };
  };

  const validAttackTargets = getValidAttackTargets();

  // 随从攻击开始
  const handleAttackMouseDown = (e: React.MouseEvent, index: number) => {
    const minion = gameState?.player.field[index];
    if (!minion?.can_attack) return;
    e.preventDefault();
    setAttackingMinion(index);
    const rect = e.currentTarget.getBoundingClientRect();
    setArrowStart({ x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 });
    setArrowEnd({ x: e.clientX, y: e.clientY });
  };

  // 从目标元素获取目标ID
  const getTargetIdFromElement = (element: Element | null): string | null => {
    if (!element) return null;

    // 检查敌方英雄
    const heroArea = element.closest('.opponent-hero-area');
    if (heroArea) return 'opponent_hero';

    // 检查玩家英雄
    const playerHeroArea = element.closest('.player-hero-area');
    if (playerHeroArea) return 'hero';

    // 检查敌方随从
    const opponentMinion = element.closest('.opponent-field .minion');
    if (opponentMinion) {
      const index = parseInt(opponentMinion.getAttribute('data-index') || '-1');
      if (index >= 0) return `enemy_minion-${index}`;
    }

    // 检查玩家随从
    const playerMinion = element.closest('.player-field .minion');
    if (playerMinion) {
      const index = parseInt(playerMinion.getAttribute('data-index') || '-1');
      if (index >= 0) return `minion-${index}`;
    }

    return null;
  };

  // 检查目标是否在有效目标列表中
  const isValidTarget = (targetId: string | null): boolean => {
    if (!targetId || !pendingAction) return false;
    // 如果 validTargets 为空，允许选择任何目标（由后端验证）
    if (pendingAction.validTargets.length === 0) return true;
    return pendingAction.validTargets.includes(targetId);
  };

  // 英雄技能点击
  const handleHeroPowerClick = () => {
    if (!isMyTurn || !gameState?.player.hero_power?.is_usable) return;
    const heroPower = gameState.player.hero_power;
    console.log('[HeroPower] Click - requires_target:', heroPower.requires_target, 'valid_targets:', heroPower.valid_targets);

    // 法师技能需要目标，即使 valid_targets 为空也要进入选择模式
    if (heroPower.requires_target) {
      setPendingAction({
        type: 'hero_power',
        targets: [],
        requiredCount: 1,
        validTargets: heroPower.valid_targets || [],
      });
      // 设置箭头起点
      const heroPowerEl = document.querySelector('.player-hero-power');
      if (heroPowerEl) {
        const rect = heroPowerEl.getBoundingClientRect();
        setArrowStart({ x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 });
      }
    } else {
      gameService.useHeroPower();
    }
  };

  // 全局鼠标事件处理
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (attackingMinion !== null || pendingAction !== null) {
        setArrowEnd({ x: e.clientX, y: e.clientY });
      }
    };

    const handleMouseUp = (e: MouseEvent) => {
      if (attackingMinion !== null) {
        const target = document.elementFromPoint(e.clientX, e.clientY);
        if (target) {
          const heroArea = target.closest('.opponent-hero-area');
          if (heroArea && validAttackTargets.canAttackHero) {
            gameService.attack(attackingMinion, 'hero');
          }
          const minionEl = target.closest('.opponent-field .minion');
          if (minionEl) {
            const index = parseInt(minionEl.getAttribute('data-index') || '-1');
            if (validAttackTargets.minions.includes(index)) {
              gameService.attack(attackingMinion, `minion-${index}`);
            }
          }
        }
        setAttackingMinion(null);
        setArrowStart(null);
        setArrowEnd(null);
      } else if (pendingAction !== null) {
        const target = document.elementFromPoint(e.clientX, e.clientY);
        const targetId = getTargetIdFromElement(target);
        console.log('[TargetSelect] Target element:', target?.className, 'Target ID:', targetId);
        console.log('[TargetSelect] Valid targets:', pendingAction.validTargets);

        if (targetId && isValidTarget(targetId)) {
          const newTargets = [...pendingAction.targets, targetId];
          if (newTargets.length >= pendingAction.requiredCount) {
            if (pendingAction.type === 'card') {
              gameService.playCard(pendingAction.cardIndex!, newTargets[0]);
            } else if (pendingAction.type === 'hero_power') {
              gameService.useHeroPower(newTargets[0]);
            }
            setPendingAction(null);
            setArrowStart(null);
            setArrowEnd(null);
          } else {
            setPendingAction({ ...pendingAction, targets: newTargets });
          }
        }
      }
    };

    // 右键取消目标选择
    const handleContextMenu = (e: MouseEvent) => {
      if (pendingAction !== null || attackingMinion !== null) {
        e.preventDefault();
        setAttackingMinion(null);
        setPendingAction(null);
        setArrowStart(null);
        setArrowEnd(null);
      }
    };

    if (attackingMinion !== null || pendingAction !== null) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      window.addEventListener('contextmenu', handleContextMenu);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('contextmenu', handleContextMenu);
    };
  }, [attackingMinion, pendingAction]);

  // 渲染加载界面
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
            <div className="loading-text">{t('ui.loading')}</div>
          </div>
          <button className="back-btn" onClick={onBack}>← Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="game-container">
      {/* 攻击箭头 */}
      {arrowStart && arrowEnd && (
        <AttackArrow start={arrowStart} end={arrowEnd} />
      )}

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
            <div
              className={`hero-portrait opponent hero-${getHeroClass(gameState.opponent.hero)} ${validAttackTargets.canAttackHero ? 'valid-target' : ''}`}
              title={gameState.opponent.hero}
            >
              <div className="hero-class-icon">{getHeroClassIcon(gameState.opponent.hero)}</div>
              <div className="hero-name">{gameState.opponent.hero.split(' ')[0]}</div>
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
                className={`minion ${minion.taunt ? 'taunt' : ''} ${validAttackTargets.minions.includes(i) ? 'valid-target' : ''}`}
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
            <div
              className={`hero-portrait player hero-${getHeroClass(gameState.player.hero)}`}
              title={gameState.player.hero}
            >
              <div className="hero-class-icon">{getHeroClassIcon(gameState.player.hero)}</div>
              <div className="hero-name">{gameState.player.hero.split(' ')[0]}</div>
            </div>
            <div className="hero-stats">
              <div className="mana-crystal">💎 {gameState.player.mana}/{gameState.player.max_mana}</div>
              <div className="hero-health">❤️ {gameState.player.health}</div>
            </div>
            <div
              className={`hero-power player-hero-power ${isMyTurn && gameState.player.hero_power?.is_usable ? 'usable' : ''}`}
              onClick={handleHeroPowerClick}
              onMouseEnter={(e) => setHoveredHeroPower({ x: e.clientX, y: e.clientY })}
              onMouseLeave={() => setHoveredHeroPower(null)}
              onMouseMove={(e) => hoveredHeroPower && setHoveredHeroPower({ x: e.clientX, y: e.clientY })}
            >
              <span className="hero-power-cost">{gameState.player.hero_power.cost}</span>
              <div className="hero-power-icon">
                {gameState.player.hero_power.name}
              </div>
            </div>
          </div>

          {/* 玩家手牌 */}
          <div className="player-hand-area">
            {gameState.player.hand.map((card, i) => {
              const totalCards = gameState.player.hand.length;
              const angle = totalCards > 1 ? ((i / (totalCards - 1)) - 0.5) * 30 : 0;
              return (
                <div
                  key={i}
                  className={`card ${isMyTurn && card.is_playable ? 'playable' : ''} ${draggedCard === i ? 'dragging' : ''}`}
                  style={{ transform: `rotate(${angle}deg)` }}
                  draggable={isMyTurn && !!card.is_playable}
                  onDragStart={(e) => handleDragStart(e, i, card)}
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
        </div>

        {/* 右侧控制区和日志 */}
        <div className="game-sidebar">
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

      {/* 悬浮提示 - 卡牌 */}
      {hoveredCard && (
        <div
          className="tooltip-fixed"
          style={{
            left: hoveredCard.x + 15,
            top: hoveredCard.y,
          }}
        >
          <div className="tooltip-name">{hoveredCard.card.name}</div>
          {hoveredCard.card.race && <div className="tooltip-race">{hoveredCard.card.race}</div>}
          {hoveredCard.card.text && (
            <div className="tooltip-text" dangerouslySetInnerHTML={{ __html: hoveredCard.card.text }} />
          )}
          {hoveredCard.card.mechanics && hoveredCard.card.mechanics.length > 0 && (
            <div className="tooltip-mechanics">
              {hoveredCard.card.mechanics.map((m, idx) => (
                <span key={idx} className="mechanic-tag">{m}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 悬浮提示 - 随从 */}
      {hoveredMinion && (
        <div
          className="tooltip-fixed"
          style={{
            left: hoveredMinion.x + 15,
            top: hoveredMinion.y,
          }}
        >
          <div className="tooltip-name">{hoveredMinion.minion.name}</div>
          {hoveredMinion.minion.race && <div className="tooltip-race">{hoveredMinion.minion.race}</div>}
          <div className="tooltip-stats">
            <span className="tooltip-atk">⚔️ {hoveredMinion.minion.atk}</span>
            <span className="tooltip-health">❤️ {hoveredMinion.minion.health}</span>
          </div>
          {hoveredMinion.minion.text && (
            <div className="tooltip-text" dangerouslySetInnerHTML={{ __html: hoveredMinion.minion.text }} />
          )}
          {hoveredMinion.minion.mechanics && hoveredMinion.minion.mechanics.length > 0 && (
            <div className="tooltip-mechanics">
              {hoveredMinion.minion.mechanics.map((m, idx) => (
                <span key={idx} className="mechanic-tag">{m}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 悬浮提示 - 英雄技能 */}
      {hoveredHeroPower && gameState && (
        <div
          className="tooltip-fixed"
          style={{
            left: hoveredHeroPower.x + 15,
            top: hoveredHeroPower.y,
          }}
        >
          <div className="tooltip-name">{gameState.player.hero_power.name}</div>
          <div className="tooltip-stats">
            <span className="tooltip-cost">💎 {gameState.player.hero_power.cost}</span>
          </div>
          {gameState.player.hero_power.description && (
            <div className="tooltip-text" dangerouslySetInnerHTML={{ __html: gameState.player.hero_power.description }} />
          )}
        </div>
      )}

      {/* 回合提示 */}
      {showTurnBanner && (
        <div className="turn-banner">
          {t('game.yourTurn')}
        </div>
      )}

    </div>
  );
}
