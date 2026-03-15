# Fireplace Web UI 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 Fireplace 炉石传说模拟器构建完整的 Web UI，支持玩家 vs AI/玩家/AI 三种模式，实现多语言切换

**Architecture:** React + Flask + WebSocket 实时通信，前端使用 CSS Modules 实现经典炉石风格，后端复用现有 fireplace 游戏引擎

**Tech Stack:** React 18, Vite, TypeScript, Flask, Flask-SocketIO, react-i18next

---

## Phase 1: 项目初始化

### Task 1: 创建项目目录结构

**Files:**
- Create: `webui/` (前端项目根目录)
- Create: `webui/server/` (后端目录)
- Create: `webui/server/__init__.py`
- Create: `webui/server/game.py` (游戏管理)
- Create: `webui/server/views.py` (API 视图)
- Create: `webui/server/socket.py` (WebSocket 处理)

**Step 1: 创建目录**

```bash
mkdir -p webui/server
touch webui/server/__init__.py
touch webui/server/game.py
touch webui/server/views.py
touch webui/server/socket.py
```

**Step 2: 验证目录创建**

```bash
ls -la webui/
ls -la webui/server/
```

**Step 3: Commit**

```bash
git add webui/
git commit -m "feat: create webui project structure"
```

---

### Task 2: 初始化 Flask 后端

**Files:**
- Modify: `webui/server/__init__.py`
- Create: `webui/requirements.txt`

**Step 1: 创建 Flask 应用**

```python
# webui/server/__init__.py
from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'fireplace-secret-key'

    socketio.init_app(app, cors_allowed_origins="*")

    from . import views, socket
    app.register_blueprint(views.bp)

    return app
```

**Step 2: 创建 requirements.txt**

```
flask>=2.3.0
flask-socketio>=5.3.0
eventlet>=0.33.0
```

**Step 3: 创建入口文件**

```python
# webui/run.py
from server import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
```

**Step 4: 测试 Flask 启动**

```bash
cd webui
pip install -r requirements.txt
python run.py &
sleep 2
curl http://localhost:5000/
# 预期返回 404（还没创建路由）
```

**Step 5: Commit**

```bash
git add webui/server/__init__.py webui/requirements.txt webui/run.py
git commit -m "feat: init Flask backend with SocketIO"
```

---

### Task 3: 初始化 React 前端

**Files:**
- Create: `webui/client/` (Vite 项目)

**Step 1: 创建 Vite React 项目**

```bash
cd webui
npm create vite@latest client -- --template react-ts
cd client
npm install
npm install react-i18next i18next socket.io-client
```

**Step 2: 验证前端运行**

```bash
cd webui/client
npm run dev -- --port 3000 &
sleep 3
curl http://localhost:3000/
# 预期返回 HTML
```

**Step 3: Commit**

```bash
git add webui/client/
git commit -m "feat: init React frontend with Vite"
```

---

## Phase 2: 后端核心功能

### Task 4: 后端 - 游戏管理模块

**Files:**
- Modify: `webui/server/game.py`
- Test: `webui/server/test_game.py`

**Step 1: 创建游戏管理类**

```python
# webui/server/game.py
import uuid
from fireplace import cards
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import random_class, random_draft

class GameManager:
    def __init__(self):
        self.games = {}
        self._initialized = False

    def initialize(self):
        if not self._initialized:
            cards.db.initialize()
            self._initialized = True

    def create_game(self, player1_class, player2_class=None, mode="pve"):
        """创建游戏返回 game_id"""
        self.initialize()
        game_id = str(uuid.uuid4())

        p1_class = random_class() if player1_class == "random" else cards.db[player1_class]
        if mode == "pve":
            p2_class = random_class() if player2_class is None else cards.db[player2_class]
        else:
            p2_class = random_class()

        p1_deck = random_draft(p1_class)
        p2_deck = random_draft(p2_class)

        player1 = Player("Player1", p1_deck, p1_class.default_hero)
        player2 = Player("Player2", p2_deck, p2_class.default_hero)

        game = Game(players=(player1, player2))
        game.start()

        # 跳过换牌
        for p in game.players:
            if p.choice:
                p.choice.choose()

        self.games[game_id] = {
            "game": game,
            "mode": mode,
            "players": [player1, player2],
            "current": player1
        }

        return game_id

    def get_game_state(self, game_id):
        """获取游戏状态"""
        if game_id not in self.games:
            return None

        g = self.games[game_id]
        game = g["game"]
        player = g["players"][0]
        opponent = g["players"][1]

        return {
            "turn": game.turn,
            "current_player": "player1" if game.current_player == player else "player2",
            "player": {
                "hero": str(player.hero),
                "health": player.hero.health,
                "max_health": player.hero.max_health,
                "mana": player.mana,
                "max_mana": player.max_mana,
                "deck": len(player.deck),
                "hand": [str(c) for c in player.hand],
                "field": [{"name": str(m), "atk": m.atk, "health": m.health} for m in player.field],
                "can_end_turn": game.current_player == player
            },
            "opponent": {
                "hero": str(opponent.hero),
                "health": opponent.hero.health,
                "deck": len(opponent.deck),
                "hand_count": len(opponent.hand),
                "field": [{"name": str(m), "atk": m.atk, "health": m.health} for m in opponent.field]
            }
        }

manager = GameManager()
```

**Step 2: 编写测试**

```python
# webui/server/test_game.py
def test_create_game():
    from server.game import manager
    game_id = manager.create_game("random", mode="pve")
    assert game_id is not None
    state = manager.get_game_state(game_id)
    assert state["turn"] == 1
    assert state["player"]["hero"] is not None
```

**Step 3: 运行测试**

```bash
cd webui
python -m pytest server/test_game.py -v
```

**Step 4: Commit**

```bash
git add webui/server/game.py
git commit -m "feat: add GameManager for game creation and state"
```

---

### Task 5: 后端 - WebSocket 事件处理

**Files:**
- Modify: `webui/server/socket.py`

**Step 1: 创建 SocketIO 事件处理**

```python
# webui/server/socket.py
from flask_socketio import emit, join_room
from .game import manager

def register_handlers(socketio):

    @socketio.on('create_game')
    def handle_create_game(data):
        mode = data.get('mode', 'pve')
        player_class = data.get('player_class', 'random')
        game_id = manager.create_game(player_class, mode=mode)
        join_room(game_id)
        state = manager.get_game_state(game_id)
        emit('game_state', {'game_id': game_id, 'state': state})

    @socketio.on('end_turn')
    def handle_end_turn(data):
        game_id = data.get('game_id')
        if game_id in manager.games:
            g = manager.games[game_id]
            g["game"].end_turn()
            state = manager.get_game_state(game_id)
            emit('game_state', {'state': state}, room=game_id)

    @socketio.on('play_card')
    def handle_play_card(data):
        game_id = data.get('game_id')
        card_index = data.get('card_index')
        target_id = data.get('target_id')

        g = manager.games[game_id]
        player = g["players"][0]

        if 0 <= card_index < len(player.hand):
            card = player.hand[card_index]
            target = None
            if target_id and card.requires_target():
                # 简化处理
                targets = list(card.targets)
                if targets:
                    target = targets[0] if target_id == "hero" else targets[int(target_id) - 1]

            try:
                card.play(target=target)
                state = manager.get_game_state(game_id)
                emit('game_state', {'state': state}, room=game_id)
            except Exception as e:
                emit('error', {'message': str(e)})

    @socketio.on('attack')
    def handle_attack(data):
        game_id = data.get('game_id')
        attacker_index = data.get('attacker_index')
        target_id = data.get('target_id')

        g = manager.games[game_id]
        player = g["players"][0]

        attacker = player.hero if attacker_index == 0 else player.field[attacker_index - 1]
        opponent = player.opponent

        target = opponent.hero if target_id == "hero" else opponent.field[int(target_id) - 1]

        try:
            attacker.attack(target)
            state = manager.get_game_state(game_id)
            emit('game_state', {'state': state}, room=game_id)
        except Exception as e:
            emit('error', {'message': str(e)})
```

**Step 2: 更新 __init__.py 加载 handlers**

```python
# webui/server/__init__.py (更新)
from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'fireplace-secret-key'
    socketio.init_app(app, cors_allowed_origins="*")

    from . import views, socket
    app.register_blueprint(views.bp)
    socket.register_handlers(socketio)

    return app
```

**Step 3: 测试后端启动**

```bash
cd webui
python run.py &
sleep 2
# 测试 WebSocket 连接（需要 socket.io 客户端测试）
```

**Step 4: Commit**

```bash
git add webui/server/socket.py
git commit -m "feat: add WebSocket event handlers"
```

---

### Task 6: 后端 - 多语言 API

**Files:**
- Modify: `webui/server/views.py`

**Step 1: 创建语言和卡牌 API**

```python
# webui/server/views.py
from flask import Blueprint, jsonify, request
import xml.etree.ElementTree as ET

bp = Blueprint('views', __name__)

# 语言映射
LANGUAGES = {
    'zhCN': 'zhCN',
    'enUS': 'enUS'
}

@bp.route('/api/languages', methods=['GET'])
def get_languages():
    """获取支持的语言列表"""
    return jsonify([
        {'code': 'zhCN', 'name': '简体中文'},
        {'code': 'enUS', 'name': 'English'}
    ])

@bp.route('/api/cards/<card_id>', methods=['GET'])
def get_card(card_id):
    """获取卡牌信息（含多语言）"""
    lang = request.args.get('lang', 'zhCN')

    try:
        tree = ET.parse('fireplace/cards/CardDefs.xml')
        root = tree.getroot()

        for entity in root.findall('Entity'):
            if entity.get('ID') == card_id:
                # 查找卡牌名称
                name_tag = None
                for tag in entity.findall('Tag'):
                    if tag.get('name') == 'CARDNAME':
                        name_tag = tag
                        break

                name = None
                if name_tag is not None:
                    lang_elem = name_tag.find(lang)
                    if lang_elem is not None:
                        name = lang_elem.text

                return jsonify({
                    'id': card_id,
                    'name': name or card_id
                })

        return jsonify({'error': 'Card not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Step 2: 测试 API**

```bash
curl http://localhost:5000/api/languages
# 预期返回语言列表
```

**Step 3: Commit**

```bash
git add webui/server/views.py
git commit -m "feat: add language and card API endpoints"
```

---

## Phase 3: 前端核心功能

### Task 7: 前端 - 项目基础配置

**Files:**
- Modify: `webui/client/src/App.tsx`
- Create: `webui/client/src/i18n.ts`

**Step 1: 配置 i18n**

```typescript
// webui/client/src/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  zhCN: {
    translation: {
      "game.title": "炉石传说",
      "game.mode.pve": "玩家 vs AI",
      "game.mode.pvp": "玩家 vs 玩家",
      "game.mode.ai": "AI vs AI",
      "game.yourTurn": "你的回合",
      "game.opponentTurn": "对手回合",
      "game.endTurn": "结束回合",
      "game.concede": "认输",
      "game.victory": "胜利",
      "game.defeat": "失败",
      "game.draw": "平局",
      "action.play": "打出",
      "action.attack": "攻击",
      "action.heroPower": "英雄技能",
      "card.cost": "费用",
      "card.attack": "攻击",
      "card.health": "生命",
      "ui.settings": "设置",
      "ui.language": "语言",
      "ui.startGame": "开始游戏"
    }
  },
  enUS: {
    translation: {
      "game.title": "Hearthstone",
      "game.mode.pve": "Player vs AI",
      "game.mode.pvp": "Player vs Player",
      "game.mode.ai": "AI vs AI",
      "game.yourTurn": "Your Turn",
      "game.opponentTurn": "Opponent's Turn",
      "game.endTurn": "End Turn",
      "game.concede": "Concede",
      "game.victory": "Victory",
      "game.defeat": "Defeat",
      "game.draw": "Draw",
      "action.play": "Play",
      "action.attack": "Attack",
      "action.heroPower": "Hero Power",
      "card.cost": "Cost",
      "card.attack": "Attack",
      "card.health": "Health",
      "ui.settings": "Settings",
      "ui.language": "Language",
      "ui.startGame": "Start Game"
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'zhCN',
    fallbackLng: 'enUS',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
```

**Step 2: 更新 App.tsx**

```tsx
// webui/client/src/App.tsx
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

  if (!gameMode) {
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

  return <div>Game Board - {gameMode}</div>;
}

export default App;
```

**Step 3: 验证运行**

```bash
cd webui/client
npm run dev
# 访问 http://localhost:5173 查看
```

**Step 4: Commit**

```bash
git add webui/client/src/i18n.ts webui/client/src/App.tsx
git commit -me "feat: add i18n configuration and basic UI"
```

---

### Task 8: 前端 - WebSocket 服务

**Files:**
- Create: `webui/client/src/services/socket.ts`
- Create: `webui/client/src/services/gameService.ts`

**Step 1: 创建 Socket 服务**

```typescript
// webui/client/src/services/socket.ts
import { io, Socket } from 'socket.io-client';

class SocketService {
  private socket: Socket | null = null;

  connect() {
    this.socket = io('http://localhost:5000');
    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  getSocket() {
    return this.socket;
  }

  emit(event: string, data: any) {
    this.socket?.emit(event, data);
  }

  on(event: string, callback: (data: any) => void) {
    this.socket?.on(event, callback);
  }

  off(event: string) {
    this.socket?.off(event);
  }
}

export const socketService = new SocketService();
```

**Step 2: 创建游戏服务**

```typescript
// webui/client/src/services/gameService.ts
import { socketService } from './socket';

export interface GameState {
  turn: number;
  current_player: string;
  player: {
    hero: string;
    health: number;
    max_health: number;
    mana: number;
    max_mana: number;
    deck: number;
    hand: string[];
    field: { name: string; atk: number; health: number }[];
    can_end_turn: boolean;
  };
  opponent: {
    hero: string;
    health: number;
    deck: number;
    hand_count: number;
    field: { name: string; atk: number; health: number }[];
  };
}

class GameService {
  private gameId: string | null = null;

  createGame(mode: string, playerClass: string = 'random') {
    socketService.connect();
    socketService.emit('create_game', { mode, player_class: playerClass });
  }

  endTurn() {
    if (this.gameId) {
      socketService.emit('end_turn', { game_id: this.gameId });
    }
  }

  playCard(cardIndex: number, targetId?: string) {
    if (this.gameId) {
      socketService.emit('play_card', {
        game_id: this.gameId,
        card_index: cardIndex,
        target_id: targetId
      });
    }
  }

  attack(attackerIndex: number, targetId: string) {
    if (this.gameId) {
      socketService.emit('attack', {
        game_id: this.gameId,
        attacker_index: attackerIndex,
        target_id: targetId
      });
    }
  }

  setGameId(id: string) {
    this.gameId = id;
  }

  onGameState(callback: (data: { game_id: string; state: GameState }) => void) {
    socketService.on('game_state', callback);
  }

  onError(callback: (data: { message: string }) => void) {
    socketService.on('error', callback);
  }
}

export const gameService = new GameService();
```

**Step 3: Commit**

```bash
git add webui/client/src/services/
git commit -m "feat: add WebSocket and game services"
```

---

### Task 9: 前端 - 游戏界面组件

**Files:**
- Create: `webui/client/src/components/GameBoard.tsx`
- Create: `webui/client/src/components/Card.tsx`
- Create: `webui/client/src/components/Hand.tsx`
- Create: `webui/client/src/components/Field.tsx`
- Create: `webui/client/src/components/Hero.tsx`

**Step 1: 创建 GameBoard 组件**

```tsx
// webui/client/src/components/GameBoard.tsx
import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { gameService, GameState } from '../services/gameService';
import './GameBoard.css';

interface GameBoardProps {
  mode: string;
  onBack: () => void;
}

export function GameBoard({ mode, onBack }: GameBoardProps) {
  const { t, i18n } = useTranslation();
  const [gameState, setGameState] = useState<GameState | null>(null);

  useEffect(() => {
    gameService.createGame(mode);

    gameService.onGameState((data) => {
      setGameState(data.state);
    });

    return () => {
      // cleanup
    };
  }, [mode]);

  const handleEndTurn = () => {
    gameService.endTurn();
  };

  if (!gameState) {
    return <div className="loading">Loading...</div>;
  }

  const isMyTurn = gameState.current_player === 'player1';

  return (
    <div className="game-board">
      {/* 对手区域 */}
      <div className="opponent-area">
        <div className="opponent-hero">
          <div className="hero-portrait opponent">{gameState.opponent.hero}</div>
          <div className="hero-health">{gameState.opponent.health}</div>
          <div className="deck-count">{gameState.opponent.deck} 🔴</div>
        </div>
        <div className="opponent-hand">
          {Array(gameState.opponent.hand_count).fill(0).map((_, i) => (
            <div key={i} className="card-back" />
          ))}
        </div>
      </div>

      {/* 对手战场 */}
      <div className="battle-field opponent-field">
        {gameState.opponent.field.map((minion, i) => (
          <div key={i} className="minion">
            <span className="minion-atk">{minion.atk}</span>
            <span className="minion-name">{minion.name}</span>
            <span className="minion-health">{minion.health}</span>
          </div>
        ))}
      </div>

      {/* 己方战场 */}
      <div className="battle-field player-field">
        {gameState.player.field.map((minion, i) => (
          <div key={i} className="minion player-minion">
            <span className="minion-atk">{minion.atk}</span>
            <span className="minion-name">{minion.name}</span>
            <span className="minion-health">{minion.health}</span>
          </div>
        ))}
      </div>

      {/* 玩家区域 */}
      <div className="player-area">
        <div className="player-hand">
          {gameState.player.hand.map((cardName, i) => (
            <div key={i} className="card playable">
              <div className="card-cost">{i + 1}</div>
              <div className="card-name">{cardName}</div>
            </div>
          ))}
        </div>
        <div className="player-hero">
          <div className="hero-portrait player">{gameState.player.hero}</div>
          <div className="hero-health">{gameState.player.health}</div>
          <div className="mana-crystal">
            {gameState.player.mana}/{gameState.player.max_mana}
          </div>
        </div>
      </div>

      {/* 控制面板 */}
      <div className="control-panel">
        <div className="turn-indicator">
          {isMyTurn ? t('game.yourTurn') : t('game.opponentTurn')}
        </div>
        <button
          className="end-turn-btn"
          onClick={handleEndTurn}
          disabled={!isMyTurn || !gameState.player.can_end_turn}
        >
          {t('game.endTurn')}
        </button>
        <button className="concede-btn">{t('game.concede')}</button>
        <button className="back-btn" onClick={onBack}>←</button>
      </div>
    </div>
  );
}
```

**Step 2: 创建 CSS 样式**

```css
/* webui/client/src/components/GameBoard.css */
.game-board {
  width: 100%;
  height: 100vh;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  display: flex;
  flex-direction: column;
  position: relative;
}

.opponent-area {
  height: 120px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.3);
}

.battle-field {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
}

.player-area {
  height: 180px;
  display: flex;
  align-items: center;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.3);
}

.control-panel {
  position: absolute;
  bottom: 200px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  align-items: center;
}

.card {
  width: 100px;
  height: 140px;
  background: linear-gradient(135deg, #2c3e50, #3498db);
  border: 3px solid #f1c40f;
  border-radius: 8px;
  color: white;
  padding: 5px;
  cursor: pointer;
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-10px);
}

.minion {
  width: 80px;
  height: 60px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid #c0c0c0;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
}

.hero-portrait {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 4px solid #f1c40f;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.end-turn-btn {
  padding: 15px 30px;
  background: linear-gradient(180deg, #e74c3c, #c0392b);
  border: 3px solid #f1c40f;
  border-radius: 8px;
  color: white;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
}

.end-turn-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

**Step 3: 更新 App.tsx 使用 GameBoard**

```tsx
// webui/client/src/App.tsx (更新)
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
```

**Step 4: 验证运行**

```bash
cd webui/client
npm run dev
# 访问查看游戏界面
```

**Step 5: Commit**

```bash
git add webui/client/src/components/
git commit -m "feat: add GameBoard and UI components"
```

---

## Phase 4: 完善与集成

### Task 10: 整合测试

**Step 1: 启动后端**

```bash
cd webui
python run.py &
```

**Step 2: 启动前端**

```bash
cd webui/client
npm run dev
```

**Step 3: 验证完整流程**

1. 打开 http://localhost:5173
2. 选择语言
3. 选择游戏模式
4. 验证游戏界面加载
5. 测试结束回合功能

**Step 4: Commit**

```bash
git add .
git commit -m "feat: complete basic game flow"
```

---

## 总结

此计划包含 10 个主要任务，涵盖：
- 项目初始化（3 个任务）
- 后端核心（4 个任务）
- 前端核心（3 个任务）

按照 TDD 原则，每个任务先写测试，再实现代码，最后验证提交。
