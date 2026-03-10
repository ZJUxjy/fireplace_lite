# Fireplace Web UI 设计方案

**日期**: 2026-03-10
**版本**: 1.0

## 1. 项目概述

为 Fireplace 炉石传说模拟器开发 Web UI 界面，提供完整的游戏对战功能。

## 2. 技术栈

- **前端**: React 18 + Vite + TypeScript
- **状态管理**: React Context + useReducer
- **国际化**: react-i18next
- **后端**: Flask + Flask-SocketIO
- **样式**: CSS Modules 实现经典炉石风格
- **通信**: WebSocket 实时对战

## 3. 核心功能

### 3.1 游戏模式
- 玩家 vs AI
- 玩家 vs 玩家（本地双人对战）
- AI vs AI（观战模式）

### 3.2 多语言支持
- 初始语言：简体中文、English
- 从 CardDefs.xml 读取卡牌多语言文本
- 运行时语言切换
- UI 文本国际化

### 3.3 游戏功能
- 卡牌打出（包含目标选择、抉择）
- 随从/英雄攻击
- 英雄技能使用
- 回合管理
- 胜负判定

## 4. 架构设计

```
┌─────────────────────────────────────────────────────┐
│                    React Frontend                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  Game   │  │  Card   │  │  i18n   │  │  Style  │ │
│  │  State  │  │ Display │  │   L10n  │  │  Theme  │ │
│  └────┬────┘  └─────────┘  └─────────┘  └─────────┘ │
│       ↓                                                  │
│  ┌──────────────────────────────────────────────┐    │
│  │           WebSocket Client                    │    │
│  └──────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────┘
                          │ WebSocket / JSON
                          ↓
┌─────────────────────────────────────────────────────┐
│                   Flask Backend                      │
│  ┌─────────┐  ┌─────────┐  ┌──────────────────┐   │
│  │  Game   │  │ Session │  │   CardDefs XML   │   │
│  │ Manager │  │  Manager │  │   Multi-lang     │   │
│  └────┬────┘  └────┬────┘  └────────┬─────────┘   │
│       ↓            ↓                 ↓              │
│  ┌──────────────────────────────────────────────┐   │
│  │              Fireplace Game Engine            │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 5. 前端模块设计

### 5.1 页面结构
- **主页**: 游戏模式选择、设置入口
- **对战**: 游戏主界面（战场、手牌、UI 控制）
- **结算**: 游戏结束画面

### 5.2 组件层级
```
App
├── GameModeSelect (主页)
├── GameBoard (对战)
│   ├── OpponentArea (对手)
│   │   ├── HeroPortrait
│   │   ├── HeroPower
│   │   ├── Deck
│   │   └── Hand (背面)
│   ├── BattleField (战场)
│   │   ├── MinionSlot (己方随从)
│   │   └── MinionSlot (对方随从)
│   ├── PlayerArea (玩家)
│   │   ├── HeroPortrait
│   │   ├── HeroPower
│   │   ├── Deck
│   │   └── Hand
│   │       └── Card (可打出)
│   ├── ActionPanel (操作面板)
│   ├── EndTurnButton
│   └── TurnIndicator
├── CardDetail (卡牌详情弹窗)
├── TargetSelect (目标选择)
├── ChoiceSelect (抉择选择)
└── GameResult (结算)
```

### 5.3 状态管理
- `gameState`: 游戏状态（等待中、进行中、结束）
- `player`: 当前玩家信息
- `opponent`: 对手信息
- `hand`: 手牌列表
- `field`: 场上随从
- `turn`: 当前回合
- `phase`: 当前阶段（己方回合、对手回合、选择中）
- `availableActions`: 可用操作
- `selectedCard`: 选中的卡牌
- `language`: 当前语言

## 6. 后端 API 设计

### 6.1 WebSocket 事件

**客户端 → 服务器**:
- `create_game`: 创建游戏
- `join_game`: 加入游戏
- `play_card`: 打出卡牌
- `attack`: 攻击
- `use_hero_power`: 使用英雄技能
- `end_turn`: 结束回合
- `choose`: 选择（抉择/发现等）
- `concede`: 认输

**服务器 → 客户端**:
- `game_state`: 游戏状态同步
- `action_result`: 操作结果
- `game_over`: 游戏结束
- `error`: 错误信息

### 6.2 REST API
- `GET /api/languages` - 获取支持的语言列表
- `GET /api/cards/:id` - 获取卡牌信息（含多语言）
- `GET /api/game/:id` - 获取游戏状态

## 7. 多语言设计

### 7.1 语言代码映射
| 代码 | 语言 |
|------|------|
| zhCN | 简体中文 |
| enUS | English |

### 7.2 国际化内容
- UI 按钮文本（结束回合、确认、取消等）
- 游戏提示（你的回合、对手回合等）
- 卡牌名称和描述（从 XML 读取）
- 英雄技能名称
- 职业名称

### 7.3 实现方案
- 使用 `react-i18next`
- 语言文件: `locales/{lang}/translation.json`
- 卡牌文本: 后端从 CardDefs.xml 提取，前端按需请求

## 8. UI 设计规范

### 8.1 视觉风格
- 经典炉石传说风格
- 深色木纹背景
- 黄金/古铜色边框
- 卡牌使用炉石原画风格

### 8.2 布局
- 竖屏布局，符合游戏习惯
- 战场在中央，手牌在底部
- 对手信息在顶部

### 8.3 交互
- 点击卡牌查看详情
- 拖拽或点击打牌
- 点击攻击/被攻击高亮目标

## 9. 后续扩展

- 卡牌收藏/构筑系统
- 历史对局记录
- 更多的 AI 难度
- 移动端适配
