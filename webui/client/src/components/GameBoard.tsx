import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { gameService, type GameState, type CardData, type LogEntry, type MinionData as ServiceMinionData } from '../services/gameService';
import './GameBoard.css';

interface GameBoardProps {
  mode: string;
  playerClass?: string;
  onBack: () => void;
}

interface MinionData extends ServiceMinionData {}

// 格式化日志条目
function formatLogEntry(log: LogEntry): string {
  const timestamp = new Date(log.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const prefix = `[${timestamp}]`;

  switch (log.type) {
    case 'game_start':
      return `${prefix} 🎮 游戏开始: ${log.message}`;
    case 'play_card':
      return `${prefix} 🃏 ${log.message}`;
    case 'battlecry':
      return `${prefix} ⚡ 战吼: ${log.message}`;
    case 'attack':
      return `${prefix} ⚔️ ${log.message}`;
    case 'damage':
      return `${prefix} 💥 ${log.message}`;
    case 'minion_died':
      return `${prefix} 💀 ${log.message}`;
    case 'weapon_attack':
      return `${prefix} ⚔️ ${log.message}`;
    case 'weapon_broken':
      return `${prefix} 💔 ${log.message}`;
    case 'hero_power':
      return `${prefix} 🔮 ${log.message}`;
    case 'hero_power_effect':
      return `${prefix} ✨ ${log.message}`;
    case 'end_turn':
      return `${prefix} ⏹️ ${log.message}`;
    default:
      return `${prefix} ${log.message}`;
  }
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
  const [useTestDeck, setUseTestDeck] = useState(false);
  const [, setSelectedCard] = useState<{ card: CardData; index: number } | null>(null);
  const [hoveredCard, setHoveredCard] = useState<{ card: CardData; x: number; y: number } | null>(null);
  const [hoveredMinion, setHoveredMinion] = useState<{ minion: MinionData; x: number; y: number } | null>(null);
  const [hoveredHeroPower, setHoveredHeroPower] = useState<{ x: number; y: number; isOpponent?: boolean } | null>(null);
  const [draggedCard, setDraggedCard] = useState<number | null>(null);
  const [attackingMinion, setAttackingMinion] = useState<number | null>(null);
  const [weaponAttacking, setWeaponAttacking] = useState<boolean>(false);
  const [arrowStart, setArrowStart] = useState<{ x: number; y: number } | null>(null);
  const [arrowEnd, setArrowEnd] = useState<{ x: number; y: number } | null>(null);
  const prevTurnRef = useRef<number>(0);
  const prevPlayerRef = useRef<string>('');

  // 目标选择状态
  const [pendingAction, setPendingAction] = useState<{
    type: 'card' | 'hero_power' | 'weapon';
    cardIndex?: number;
    targets: string[];
    requiredCount: number;
    validTargets: string[];
    committed: boolean; // true 表示不能再取消
  } | null>(null);

  // 预放置/预施法状态（用于随从战吼和法术目标选择）
  const [stagedCard, setStagedCard] = useState<{
    cardIndex: number;
    card: CardData;
    type: 'minion' | 'spell';
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

      // 更新详细日志
      if (data.state.logs && data.state.logs.length > 0) {
        const logMessages = data.state.logs.map(log => formatLogEntry(log));
        setActionLog(logMessages);
      } else {
        setActionLog([`Turn ${data.state.turn}`]);
      }

    };

    const handleError = (data: { message: string }) => {
      setActionLog(prev => [`Error: ${data.message}`, ...prev.slice(0, 20)]);
    };

    gameService.createGame(mode, playerClass, useTestDeck);
    gameService.onGameState(handleGameState);
    gameService.onError(handleError);

    return () => {
      gameService.cleanup();
    };
  }, [mode]);

  // 当随从被消灭时清除悬浮提示
  useEffect(() => {
    if (!gameState || !hoveredMinion) return;

    const allMinions = [
      ...gameState.player.field,
      ...gameState.opponent.field
    ];

    // 检查悬浮的随从是否还在场上（通过name, atk, health匹配）
    const minionStillExists = allMinions.some(m =>
      m.name === hoveredMinion.minion.name &&
      m.atk === hoveredMinion.minion.atk &&
      m.health === hoveredMinion.minion.health
    );

    if (!minionStillExists) {
      setHoveredMinion(null);
    }
  }, [gameState?.player.field, gameState?.opponent.field, hoveredMinion?.minion.name]);

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
    gameService.createGame(mode, playerClass, useTestDeck);
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
    if (!card?.is_playable) {
      setDraggedCard(null);
      return;
    }

    // 检查是否真的拖放到战场区域
    const dropTarget = document.elementFromPoint(e.clientX, e.clientY);
    const isOnBattlefield = dropTarget?.closest('.player-field') ||
                            dropTarget?.closest('.player-hero-area') ||
                            dropTarget?.closest('.field-divider');

    // 判断卡牌类型：有攻击力的是随从，没有的是法术
    const isMinion = card.atk !== undefined && card.health !== undefined;

    if (isMinion) {
      // ===== 随从牌逻辑 =====
      if (!isOnBattlefield) {
        // 拖回手牌区，取消操作
        setDraggedCard(null);
        return;
      }

      // 检查是否需要目标（战吼需要目标）
      if (card.requires_target && card.valid_targets && card.valid_targets.length > 0) {
        // 进入预放置状态：显示占位符，开始选择目标
        setStagedCard({
          cardIndex,
          card,
          type: 'minion',
          validTargets: card.valid_targets,
        });
        setPendingAction({
          type: 'card',
          cardIndex,
          targets: [],
          requiredCount: 1,
          validTargets: card.valid_targets,
          committed: false, // 可以取消
        });
        // 设置箭头起点为战场中心位置
        const fieldEl = document.querySelector('.player-field');
        if (fieldEl) {
          const rect = fieldEl.getBoundingClientRect();
          setArrowStart({ x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 });
        }
      } else {
        // 不需要目标，直接打出
        gameService.playCard(cardIndex);
      }
    } else {
      // ===== 法术牌逻辑 =====
      // 法术牌：拖拽离开手牌区并松开后开始选择
      const isLeavingHand = !dropTarget?.closest('.player-hand-area');

      if (!isLeavingHand) {
        // 拖回手牌区，取消操作
        setDraggedCard(null);
        return;
      }

      // 检查是否需要目标
      if (card.requires_target && card.valid_targets && card.valid_targets.length > 0) {
        // 进入预施法状态
        setStagedCard({
          cardIndex,
          card,
          type: 'spell',
          validTargets: card.valid_targets,
        });
        setPendingAction({
          type: 'card',
          cardIndex,
          targets: [],
          requiredCount: 1,
          validTargets: card.valid_targets,
          committed: false,
        });
        // 设置箭头起点为手牌位置
        const handEl = document.querySelector('.player-hand-area');
        if (handEl) {
          const rect = handEl.getBoundingClientRect();
          setArrowStart({ x: rect.left + rect.width / 2, y: rect.top });
        }
      } else {
        // 不需要目标的法术，直接打出
        gameService.playCard(cardIndex);
      }
    }

    setDraggedCard(null);
  };

  // 取消预放置/预施法状态（右键或拖回）
  const cancelStagedCard = () => {
    if (stagedCard) {
      setStagedCard(null);
      setPendingAction(null);
      setArrowStart(null);
      setArrowEnd(null);
      // 添加日志提示
      setActionLog(prev => ['[系统] 取消了卡牌打出', ...prev.slice(0, 29)]);
    }
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

  // 确认打出卡牌（目标选择完成后）
  const confirmPlayCard = (targetId?: string) => {
    if (!stagedCard) return;

    const { cardIndex } = stagedCard;

    // 发送打出请求
    gameService.playCard(cardIndex, targetId);

    // 清理状态
    setStagedCard(null);
    setPendingAction(null);
    setArrowStart(null);
    setArrowEnd(null);
  };


  // 英雄技能按下 - 像攻击一样拖动选择目标
  const handleHeroPowerMouseDown = (e: React.MouseEvent) => {
    if (!isMyTurn || !gameState?.player.hero_power?.is_usable) return;
    e.preventDefault();

    const heroPower = gameState.player.hero_power;
    console.log('[HeroPower] MouseDown - requires_target:', heroPower.requires_target, 'valid_targets:', heroPower.valid_targets);

    // 法师技能需要目标，按下就开始拖动选择
    if (heroPower.requires_target) {
      setPendingAction({
        type: 'hero_power',
        targets: [],
        requiredCount: 1,
        validTargets: heroPower.valid_targets || [],
        committed: false,
      });
      // 设置箭头起点为英雄技能位置
      const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
      setArrowStart({ x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 });
      setArrowEnd({ x: e.clientX, y: e.clientY });
    } else {
      // 不需要目标的技能直接触发
      gameService.useHeroPower();
    }
  };

  // 武器按下 - 像攻击一样拖动选择目标
  const handleWeaponMouseDown = (e: React.MouseEvent) => {
    if (!isMyTurn || !gameState?.player.weapon) return;
    e.preventDefault();

    const weapon = gameState.player.weapon;
    console.log('[Weapon] MouseDown - weapon:', weapon.name, 'atk:', weapon.atk, 'durability:', weapon.durability);

    // 设置武器攻击状态
    setPendingAction({
      type: 'weapon',
      targets: [],
      requiredCount: 1,
      validTargets: [], // 武器可以攻击任何目标，由后端验证
      committed: false,
    });
    setWeaponAttacking(true);

    // 设置箭头起点为武器槽位置
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    setArrowStart({ x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 });
    setArrowEnd({ x: e.clientX, y: e.clientY });
  };

  // 计算武器攻击的有效目标（与随从攻击逻辑相同）
  const getValidWeaponTargets = () => {
    if (!gameState || !weaponAttacking) return { minions: [] as number[], canAttackHero: false };

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

  const validWeaponTargets = getValidWeaponTargets();

  // 计算英雄技能的有效目标（用于视觉指示器）
  const getHeroPowerValidTargets = () => {
    if (!gameState || !pendingAction || pendingAction.type !== 'hero_power') {
      return { minions: [] as number[], canTargetHero: false };
    }

    const validTargets = pendingAction.validTargets;
    // 如果没有指定有效目标，允许所有目标（由后端验证）
    if (validTargets.length === 0) {
      return {
        minions: gameState.opponent.field.map((_, i) => i),
        canTargetHero: true
      };
    }

    // 从 validTargets 中提取目标
    const minionIndices: number[] = [];
    let canTargetHero = false;

    for (const targetId of validTargets) {
      if (targetId === 'opponent_hero' || targetId === 'hero') {
        canTargetHero = true;
      } else if (targetId.startsWith('enemy_minion-')) {
        const index = parseInt(targetId.split('-')[1]);
        if (!isNaN(index)) {
          minionIndices.push(index);
        }
      }
    }

    return { minions: minionIndices, canTargetHero };
  };

  const heroPowerValidTargets = getHeroPowerValidTargets();

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
      } else if (pendingAction !== null && stagedCard !== null) {
        // ===== 卡牌目标选择（随从战吼/法术）=====
        const target = document.elementFromPoint(e.clientX, e.clientY);
        const targetId = getTargetIdFromElement(target);

        console.log('[TargetSelect] Card type:', stagedCard.type, 'Target ID:', targetId);

        if (targetId && isValidTarget(targetId)) {
          // 目标有效，确认打出
          confirmPlayCard(targetId);
        } else {
          // 点击无效目标，不执行操作（保持选择状态）
          console.log('[TargetSelect] Invalid target, selection continues');
        }
      } else if (pendingAction !== null && stagedCard === null) {
        // ===== 英雄技能/武器攻击目标选择 =====
        const target = document.elementFromPoint(e.clientX, e.clientY);
        const targetId = getTargetIdFromElement(target);
        console.log('[TargetSelect] Target element:', target?.className, 'Target ID:', targetId);
        console.log('[TargetSelect] Valid targets:', pendingAction.validTargets);

        if (targetId && isValidTarget(targetId)) {
          if (pendingAction.type === 'hero_power') {
            gameService.useHeroPower(targetId);
          } else if (pendingAction.type === 'weapon') {
            gameService.weaponAttack(targetId);
          }
        }
        // 无论是否有效目标，都清理状态（拖动操作结束）
        setPendingAction(null);
        setWeaponAttacking(false);
        setArrowStart(null);
        setArrowEnd(null);
      }
    };

    // 右键取消目标选择
    const handleContextMenu = (e: MouseEvent) => {
      if (attackingMinion !== null) {
        e.preventDefault();
        setAttackingMinion(null);
        setArrowStart(null);
        setArrowEnd(null);
      } else if (stagedCard !== null && pendingAction !== null && !pendingAction.committed) {
        // ===== 可以取消的卡牌选择（随从战吼/法术）=====
        e.preventDefault();
        cancelStagedCard();
      } else if (pendingAction !== null && stagedCard === null) {
        // ===== 英雄技能/武器攻击（直接取消，不回退）=====
        e.preventDefault();
        setPendingAction(null);
        setWeaponAttacking(false);
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
  }, [attackingMinion, pendingAction, stagedCard]);

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

      {/* 目标选择提示 */}
      {stagedCard && (
        <div className="targeting-hint">
          <div className="hint-text">
            {stagedCard.type === 'minion' ? '随从战吼：选择目标' : '法术：选择目标'}
          </div>
          <div className="hint-subtext">右键取消，卡牌将退回手牌</div>
        </div>
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
            <hr style={{ margin: '0.5rem 0', borderColor: '#444' }} />
            <h4>测试卡组</h4>
            <button
              className={useTestDeck ? 'active' : ''}
              onClick={() => setUseTestDeck(!useTestDeck)}
            >
              {useTestDeck ? '✓ 启用测试卡组' : '使用测试卡组'}
            </button>
            <div style={{ fontSize: '0.7rem', color: '#888', marginTop: '0.3rem' }}>
              包含各种机制卡牌用于测试
            </div>
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
            <div className="weapon-slot opponent-weapon-slot">
              {gameState.opponent.weapon ? (
                <div className="weapon-equipped">
                  <div className="weapon-icon">⚔️</div>
                  <div className="weapon-stats">
                    <span className="weapon-atk">{gameState.opponent.weapon.atk}</span>
                    <span className="weapon-durability">{gameState.opponent.weapon.durability}</span>
                  </div>
                </div>
              ) : (
                <div className="weapon-slot-empty" />
              )}
            </div>
            <div
              className={`hero-portrait opponent hero-${getHeroClass(gameState.opponent.hero)} ${(validAttackTargets.canAttackHero || validWeaponTargets.canAttackHero || heroPowerValidTargets.canTargetHero) ? 'valid-target' : ''}`}
              title={gameState.opponent.hero}
            >
              <div className="hero-class-icon">{getHeroClassIcon(gameState.opponent.hero)}</div>
              <div className="hero-name">{gameState.opponent.hero.split(' ')[0]}</div>
            </div>
            <div className="hero-stats opponent-stats">
              <div className="mana-crystal">💎 {gameState.opponent.mana ?? 0}/{gameState.opponent.max_mana ?? 0}</div>
              <div className="hero-health">❤️ {gameState.opponent.health}</div>
              <div className="hero-armor">🛡️ {gameState.opponent.armor}</div>
              {gameState.opponent.spell_power > 0 && (
                <div className="spell-power opponent">🔮 +{gameState.opponent.spell_power}</div>
              )}
            </div>
            <div
              className="hero-power opponent-hero-power"
              onMouseEnter={(e) => setHoveredHeroPower({ x: e.clientX, y: e.clientY, isOpponent: true })}
              onMouseLeave={() => setHoveredHeroPower(null)}
              onMouseMove={(e) => hoveredHeroPower && setHoveredHeroPower({ x: e.clientX, y: e.clientY, isOpponent: true })}
            >
              <span className="hero-power-cost">{gameState.opponent.hero_power.cost}</span>
              <div className="hero-power-icon">
                {gameState.opponent.hero_power.name}
              </div>
            </div>
          </div>

          {/* 对手随从区域 */}
          <div className="field opponent-field">
            {gameState.opponent.field.map((minion, i) => (
              <div
                key={i}
                data-index={i}
                className={`minion ${minion.taunt ? 'taunt' : ''} ${minion.divine_shield ? 'divine-shield' : ''} ${minion.stealth ? 'stealth' : ''} ${minion.windfury ? 'windfury' : ''} ${minion.frozen ? 'frozen' : ''} ${(validAttackTargets.minions.includes(i) || validWeaponTargets.minions.includes(i) || heroPowerValidTargets.minions.includes(i)) ? 'valid-target' : ''}`}
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
                {minion.has_deathrattle && (
                  <div className="deathrattle-icon" title="亡语">💀</div>
                )}
                {minion.windfury && (
                  <div className="windfury-icon" title="风怒">🌪️</div>
                )}
                {minion.poisonous && (
                  <div className="poisonous-icon" title="剧毒">🐍</div>
                )}
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
                data-index={i}
                className={`minion ${minion.can_attack && isMyTurn ? 'can-attack' : ''} ${minion.taunt ? 'taunt' : ''} ${minion.divine_shield ? 'divine-shield' : ''} ${minion.stealth ? 'stealth' : ''} ${minion.windfury ? 'windfury' : ''} ${minion.frozen ? 'frozen' : ''}`}
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
                {minion.has_deathrattle && (
                  <div className="deathrattle-icon" title="亡语">💀</div>
                )}
                {minion.windfury && (
                  <div className="windfury-icon" title="风怒">🌪️</div>
                )}
                {minion.poisonous && (
                  <div className="poisonous-icon" title="剧毒">🐍</div>
                )}
              </div>
            ))}
            {/* 预放置随从占位符 */}
            {stagedCard?.type === 'minion' && (
              <div className="minion staged-minion-placeholder">
                <div className="minion-body">
                  <div className="minion-stats">
                    <span className="minion-atk">{stagedCard.card.atk}</span>
                    <span className="minion-health">{stagedCard.card.health}</span>
                  </div>
                  <div className="minion-name">{stagedCard.card.name}</div>
                </div>
                <div className="staged-indicator">选择目标...</div>
              </div>
            )}
            {gameState.player.field.length === 0 && !stagedCard && <div className="field-placeholder" />}
          </div>

          {/* 玩家英雄区 */}
          <div className="hero-area player-hero-area">
            <div
              className={`weapon-slot player-weapon-slot ${gameState.player.weapon ? 'has-weapon' : ''} ${weaponAttacking ? 'attacking' : ''}`}
              onMouseDown={handleWeaponMouseDown}
            >
              {gameState.player.weapon ? (
                <div className="weapon-equipped" title={gameState.player.weapon.name}>
                  <div className="weapon-icon">⚔️</div>
                  <div className="weapon-stats">
                    <span className="weapon-atk">{gameState.player.weapon.atk}</span>
                    <span className="weapon-durability">{gameState.player.weapon.durability}</span>
                  </div>
                </div>
              ) : (
                <div className="weapon-slot-empty" />
              )}
            </div>
            <div
              className={`hero-portrait player hero-${getHeroClass(gameState.player.hero)}`}
              title={gameState.player.hero}
            >
              <div className="hero-class-icon">{getHeroClassIcon(gameState.player.hero)}</div>
              <div className="hero-name">{gameState.player.hero.split(' ')[0]}</div>
            </div>
            <div className="hero-stats player-stats">
              <div className="mana-crystal">💎 {gameState.player.mana}/{gameState.player.max_mana}</div>
              <div className="hero-health">❤️ {gameState.player.health}</div>
              <div className="hero-armor">🛡️ {gameState.player.armor}</div>
              {gameState.player.spell_power > 0 && (
                <div className="spell-power">🔮 +{gameState.player.spell_power}</div>
              )}
            </div>
            <div
              className={`hero-power player-hero-power ${isMyTurn && gameState.player.hero_power?.is_usable ? 'usable' : ''}`}
              onMouseDown={handleHeroPowerMouseDown}
              onMouseEnter={(e) => setHoveredHeroPower({ x: e.clientX, y: e.clientY, isOpponent: false })}
              onMouseLeave={() => setHoveredHeroPower(null)}
              onMouseMove={(e) => hoveredHeroPower && setHoveredHeroPower({ x: e.clientX, y: e.clientY, isOpponent: false })}
            >
              <span className="hero-power-cost">{gameState.player.hero_power.cost}</span>
              <div className="hero-power-icon">
                {gameState.player.hero_power.name}
              </div>
            </div>
          </div>

          {/* 玩家手牌 */}
          <div className={`player-hand-area ${stagedCard ? 'has-staged-card' : ''}`}>
            {gameState.player.hand.map((card, i) => {
              const totalCards = gameState.player.hand.length;
              const angle = totalCards > 1 ? ((i / (totalCards - 1)) - 0.5) * 30 : 0;
              const isStaged = stagedCard?.cardIndex === i;
              return (
                <div
                  key={i}
                  className={`card ${isMyTurn && card.is_playable ? 'playable' : ''} ${draggedCard === i ? 'dragging' : ''} ${isStaged ? 'staged' : ''} ${card.has_combo ? 'has-combo' : ''}`}
                  style={{ transform: `rotate(${angle}deg)`, opacity: isStaged ? 0.4 : 1 }}
                  draggable={isMyTurn && !!card.is_playable && !stagedCard}
                  onDragStart={(e) => handleDragStart(e, i, card)}
                  onDragEnd={handleDragEnd}
                  onClick={() => handleCardClick(card, i)}
                  onMouseEnter={(e) => setHoveredCard({ card, x: e.clientX, y: e.clientY })}
                  onMouseLeave={() => setHoveredCard(null)}
                  onMouseMove={(e) => hoveredCard && setHoveredCard({ card, x: e.clientX, y: e.clientY })}
                >
                  <div className="card-cost">{card.cost}</div>
                  {card.lifesteal && (
                    <div className="card-lifesteal" title="吸血">🩸</div>
                  )}
                  {card.poisonous && (
                    <div className="card-poisonous" title="剧毒">🐍</div>
                  )}
                  {card.has_combo && (
                    <div className="card-combo" title="连击">连击</div>
                  )}
                  <div className="card-name">{card.name}</div>
                  {card.atk !== undefined && card.health !== undefined && (
                    <div className="card-footer">
                      <span className="card-atk">{card.atk}</span>
                      <span className="card-health">{card.health}</span>
                    </div>
                  )}
                  {isStaged && (
                    <div className="card-staged-indicator">
                      {stagedCard?.type === 'minion' ? '选择目标...' : '施法中...'}
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
              {[...actionLog].reverse().map((log, i) => (
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
          {(hoveredCard.card.lifesteal || hoveredCard.card.has_combo || hoveredCard.card.poisonous) && (
            <div className="tooltip-mechanics">
              {hoveredCard.card.lifesteal && <span className="mechanic-tag lifesteal">吸血</span>}
              {hoveredCard.card.poisonous && <span className="mechanic-tag poisonous">剧毒</span>}
              {hoveredCard.card.has_combo && <span className="mechanic-tag combo">连击</span>}
            </div>
          )}
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
          {(() => {
            const heroPower = hoveredHeroPower.isOpponent
              ? gameState.opponent.hero_power
              : gameState.player.hero_power;
            return (
              <>
                <div className="tooltip-name">{heroPower.name}</div>
                <div className="tooltip-stats">
                  <span className="tooltip-cost">💎 {heroPower.cost}</span>
                </div>
                {heroPower.description && (
                  <div className="tooltip-text" dangerouslySetInnerHTML={{ __html: heroPower.description }} />
                )}
              </>
            );
          })()}
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
