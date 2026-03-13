# Minion Attack Feature Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement minion attack functionality with drag-drop interaction, attack arrow animation, oval-shaped minions, and taunt shield borders.

**Architecture:** Backend provides can_attack and taunt data via game state API. Frontend renders oval minions with CSS, uses HTML5 Drag & Drop for attack interaction, and SVG for curved attack arrows with gradient coloring.

**Tech Stack:** Python/Flask (backend), React/TypeScript (frontend), CSS3, SVG

---

## Task 1: Backend - Add Minion Attack Data

**Files:**
- Modify: `webui/server/game.py:82-113`

**Step 1: Update player field data in get_game_state**

Modify the `get_game_state` method to include `can_attack` and `taunt` for player minions:

```python
"player": {
    "hero": str(player.hero),
    "health": player.hero.health,
    "max_health": player.hero.max_health,
    "mana": player.mana,
    "max_mana": player.max_mana,
    "deck": len(player.deck),
    "hand": [self.get_card_data(c) for c in player.hand],
    "field": [{
        "name": str(m),
        "atk": m.atk,
        "health": m.health,
        "can_attack": m.can_attack(),
        "taunt": m.taunt,
    } for m in player.field],
    "can_end_turn": game.current_player == player
},
```

**Step 2: Update opponent field data**

Add `taunt` to opponent minions and `has_taunt` to opponent object:

```python
"opponent": {
    "hero": str(opponent.hero),
    "health": opponent.hero.health,
    "deck": len(opponent.deck),
    "hand_count": len(opponent.hand),
    "field": [{
        "name": str(m),
        "atk": m.atk,
        "health": m.health,
        "taunt": m.taunt,
    } for m in opponent.field],
    "has_taunt": any(m.taunt for m in opponent.field)
}
```

**Step 3: Verify by checking server logs**

Start server and create a game, check that the response includes the new fields.

**Step 4: Commit**

```bash
git add webui/server/game.py
git commit -m "feat: add can_attack and taunt data to game state"
```

---

## Task 2: Frontend - Update TypeScript Types

**Files:**
- Modify: `webui/client/src/services/gameService.ts:13-34`

**Step 1: Add MinionData type**

Add new type after CardData definition:

```typescript
export type MinionData = {
  name: string;
  atk: number;
  health: number;
  can_attack?: boolean;
  taunt?: boolean;
};
```

**Step 2: Update GameState type**

Modify the GameState type to use MinionData and add has_taunt:

```typescript
export type GameState = {
  turn: number;
  current_player: string;
  player: {
    hero: string;
    health: number;
    max_health: number;
    mana: number;
    max_mana: number;
    deck: number;
    hand: CardData[];
    field: MinionData[];
    can_end_turn: boolean;
  };
  opponent: {
    hero: string;
    health: number;
    deck: number;
    hand_count: number;
    field: MinionData[];
    has_taunt?: boolean;
  };
};
```

**Step 3: Verify TypeScript compiles**

Run: `cd webui/client && npm run build`
Expected: No TypeScript errors

**Step 4: Commit**

```bash
git add webui/client/src/services/gameService.ts
git commit -m "feat: add MinionData type and update GameState"
```

---

## Task 3: Frontend - Oval Minion Shape with Attack Indicator

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:338-396`

**Step 1: Update minion base styles for oval shape**

Replace the `.minion` and `.minion-body` styles:

```css
/* 随从 - 竖椭圆形 */
.minion {
  width: var(--minion-width);
  height: var(--minion-height);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  position: relative;
}

.minion-body {
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #5a5a5a 0%, #3a3a3a 50%, #2a2a2a 100%);
  border: 2px solid #888;
  border-radius: 50%;  /* 椭圆形 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 8% 6%;
  position: relative;
}

/* 可攻击的随从 - 绿色边框 */
.minion.can-attack .minion-body {
  border: 3px solid #4CAF50;
  box-shadow: 0 0 12px rgba(76, 175, 80, 0.6);
}

.minion.can-attack {
  cursor: grab;
}

.minion.can-attack:hover {
  transform: scale(1.08);
}

.minion.can-attack:active {
  cursor: grabbing;
}

/* 拖拽中的随从 */
.minion.dragging {
  opacity: 0.4;
  transform: scale(0.95);
}
```

**Step 2: Verify styles apply correctly**

Start dev server and check that minions appear as ovals.

**Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "feat: oval minion shape with green attack indicator"
```

---

## Task 4: Frontend - Taunt Shield Border

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` (append)

**Step 1: Add taunt shield border styles**

Append to the CSS file:

```css
/* 嘲讽随从 - 金色盾牌边框 */
.minion.taunt .minion-body::before {
  content: '';
  position: absolute;
  top: -10px;
  left: -10px;
  right: -10px;
  bottom: -10px;
  border: 4px solid #FFD700;
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  box-shadow: 0 0 15px rgba(255, 215, 0, 0.5), inset 0 0 10px rgba(255, 215, 0, 0.2);
  pointer-events: none;
  z-index: -1;
  animation: taunt-glow 2s ease-in-out infinite;
}

@keyframes taunt-glow {
  0%, 100% {
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.5), inset 0 0 10px rgba(255, 215, 0, 0.2);
  }
  50% {
    box-shadow: 0 0 25px rgba(255, 215, 0, 0.8), inset 0 0 15px rgba(255, 215, 0, 0.3);
  }
}

/* 嘲讽 + 可攻击 - 同时显示绿色内框和金色外框 */
.minion.taunt.can-attack .minion-body {
  border-color: #4CAF50;
  box-shadow: 0 0 12px rgba(76, 175, 80, 0.6);
}
```

**Step 2: Verify shield appears**

Check that taunt minions show golden shield border.

**Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "feat: add golden taunt shield border"
```

---

## Task 5: Frontend - Valid Target Highlight Styles

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` (append)

**Step 1: Add valid target highlight styles**

Append to the CSS file:

```css
/* 有效攻击目标高亮 */
.minion.valid-target .minion-body {
  box-shadow: 0 0 20px rgba(255, 100, 100, 0.8);
  animation: pulse-target 0.8s ease-in-out infinite;
}

@keyframes pulse-target {
  0%, 100% {
    box-shadow: 0 0 20px rgba(255, 100, 100, 0.8);
  }
  50% {
    box-shadow: 0 0 35px rgba(255, 100, 100, 1);
  }
}

/* 英雄作为有效目标 */
.hero-portrait.valid-target {
  box-shadow: 0 0 25px rgba(255, 100, 100, 0.8);
  animation: pulse-target 0.8s ease-in-out infinite;
}
```

**Step 2: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "feat: add valid target highlight styles"
```

---

## Task 6: Frontend - Drag and Drop Attack Logic

**Files:**
- Modify: `webui/client/src/components/GameBoard.tsx`

**Step 1: Add new state variables**

Add after existing useState declarations (around line 48):

```typescript
const [attackingMinion, setAttackingMinion] = useState<number | null>(null);
const [arrowStart, setArrowStart] = useState<{ x: number; y: number } | null>(null);
const [arrowEnd, setArrowEnd] = useState<{ x: number; y: number } | null>(null);
```

**Step 2: Add helper function for valid targets**

Add before the return statement:

```typescript
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
```

**Step 3: Add minion drag handlers**

Add after getValidAttackTargets function:

```typescript
// 随从拖拽开始
const handleMinionDragStart = (e: React.DragEvent, index: number) => {
  const minion = gameState!.player.field[index];
  if (!minion.can_attack) {
    e.preventDefault();
    return;
  }
  setAttackingMinion(index);
  const rect = e.currentTarget.getBoundingClientRect();
  const startX = rect.left + rect.width / 2;
  const startY = rect.top + rect.height / 2;
  setArrowStart({ x: startX, y: startY });
  setArrowEnd({ x: startX, y: startY });
  e.dataTransfer.setData('text/plain', `attack-${index}`);
  e.dataTransfer.effectAllowed = 'move';
};

// 随从拖拽中
const handleMinionDrag = (e: React.DragEvent) => {
  if (arrowStart) {
    setArrowEnd({ x: e.clientX, y: e.clientY });
  }
};

// 随从拖拽结束
const handleMinionDragEnd = () => {
  setAttackingMinion(null);
  setArrowStart(null);
  setArrowEnd(null);
};

// 攻击目标放置
const handleAttackDrop = (e: React.DragEvent, targetType: 'hero' | 'minion', targetIndex?: number) => {
  e.preventDefault();
  const data = e.dataTransfer.getData('text/plain');
  if (!data.startsWith('attack-')) return;

  const attackerIndex = parseInt(data.split('-')[1]);
  const targetId = targetType === 'hero' ? 'hero' : `minion-${targetIndex}`;

  gameService.attack(attackerIndex, targetId);
  handleMinionDragEnd();
};

// 阻止默认行为
const handleAttackDragOver = (e: React.DragEvent) => {
  e.preventDefault();
};
```

**Step 4: Commit**

```bash
git add webui/client/src/components/GameBoard.tsx
git commit -m "feat: add minion drag-drop attack handlers"
```

---

## Task 7: Frontend - SVG Attack Arrow Component

**Files:**
- Modify: `webui/client/src/components/GameBoard.tsx`

**Step 1: Add AttackArrow component**

Add before the GameBoard function:

```typescript
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
```

**Step 2: Render arrow in GameBoard**

Add before the closing `</div>` of game-board, after the card-tooltip section:

```typescript
{/* 攻击箭头 */}
{arrowStart && arrowEnd && (
  <AttackArrow start={arrowStart} end={arrowEnd} />
)}
```

**Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.tsx
git commit -m "feat: add SVG curved attack arrow with gradient"
```

---

## Task 8: Frontend - Update Minion Rendering with Classes and Events

**Files:**
- Modify: `webui/client/src/components/GameBoard.tsx`

**Step 1: Update player minion rendering**

Replace the player field section (around line 235-248) with:

```typescript
{/* 玩家随从区域 */}
<div className="field player-field">
  {gameState.player.field.map((minion, i) => (
    <div
      key={i}
      className={`minion ${minion.can_attack ? 'can-attack' : ''} ${minion.taunt ? 'taunt' : ''} ${draggedCard === null ? '' : 'drag-disabled'}`}
      draggable={minion.can_attack && isMyTurn}
      onDragStart={(e) => handleMinionDragStart(e, i)}
      onDrag={handleMinionDrag}
      onDragEnd={handleMinionDragEnd}
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
```

**Step 2: Update opponent minion rendering**

Replace the opponent field section (around line 211-225) with:

```typescript
{/* 对手随从区域 */}
<div className="field opponent-field">
  {gameState.opponent.field.map((minion, i) => (
    <div
      key={i}
      className={`minion ${minion.taunt ? 'taunt' : ''} ${validTargets.minions.includes(i) ? 'valid-target' : ''}`}
      onDrop={(e) => handleAttackDrop(e, 'minion', i)}
      onDragOver={handleAttackDragOver}
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
```

**Step 3: Update opponent hero as attack target**

Modify the opponent-hero-area div (around line 196-209) to accept drops:

```typescript
{/* 对手英雄区 */}
<div
  className={`hero-area opponent-hero-area ${validTargets.canAttackHero ? 'valid-target-wrapper' : ''}`}
  onDrop={(e) => handleAttackDrop(e, 'hero')}
  onDragOver={handleAttackDragOver}
>
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
```

**Step 4: Commit**

```bash
git add webui/client/src/components/GameBoard.tsx
git commit -m "feat: integrate attack drag-drop with minion rendering"
```

---

## Task 9: Backend - Verify Attack Event Handler

**Files:**
- Read: `webui/server/socket.py:206-235`

**Step 1: Review attack handler**

Verify the existing attack handler in socket.py handles minion attacks correctly:

```python
@socketio.on('attack')
def handle_attack(data):
    game_id = data.get('game_id')
    attacker_index = data.get('attacker_index')  # 随从索引，0 是英雄
    target_id = data.get('target_id')            # 'hero' 或 'minion-N'

    g = manager.games[game_id]
    player = g["players"][0]
    opponent = g["players"][1]

    # 获取攻击者（英雄或随从）
    if attacker_index == 0:
        attacker = player.hero
    else:
        attacker = player.field[attacker_index - 1]

    # 获取目标
    if target_id == 'hero':
        target = opponent.hero
    else:
        target_index = int(target_id.split('-')[1])
        target = opponent.field[target_index]

    try:
        attacker.attack(target)
        state = manager.get_game_state(game_id)
        emit('game_state', {'game_id': game_id, 'state': state})

        # PVE 模式触发 AI
        if g["mode"] == "pve":
            game = g["game"]
            if game.current_player == g["players"][1]:
                import threading
                ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
                ai_thread.daemon = True
                ai_thread.start()

    except Exception as e:
        emit('error', {'message': str(e)})
```

**Step 2: No changes needed if already correct**

The existing handler should work. If modifications are needed, update accordingly.

**Step 3: Commit if changes made**

```bash
git add webui/server/socket.py
git commit -m "fix: ensure attack handler works with new target format"
```

---

## Task 10: Integration Testing

**Step 1: Start backend server**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace
python webui/run.py
```

**Step 2: Start frontend dev server**

```bash
cd webui/client
npm run dev
```

**Step 3: Test attack functionality**

1. Create a PVE game
2. Play a minion with attack capability
3. Verify minion has green border when can attack
4. Drag minion to opponent hero - verify arrow appears
5. Drop on target - verify attack executes
6. Test with taunt minion if available

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete minion attack functionality with drag-drop and arrow animation"
```

---

## Summary

| Task | Description | Files Modified |
|------|-------------|----------------|
| 1 | Backend attack data | game.py |
| 2 | Frontend types | gameService.ts |
| 3 | Oval minion shape | GameBoard.css |
| 4 | Taunt shield border | GameBoard.css |
| 5 | Valid target highlight | GameBoard.css |
| 6 | Drag-drop handlers | GameBoard.tsx |
| 7 | SVG attack arrow | GameBoard.tsx |
| 8 | Minion rendering | GameBoard.tsx |
| 9 | Verify backend | socket.py |
| 10 | Integration test | - |
