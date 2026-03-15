# 随从攻击功能设计文档

## 概述

实现随从攻击功能，包括：
1. 可攻击随从显示绿色边框
2. 拖拽随从攻击目标
3. 弧线攻击箭头动画
4. 随从椭圆形显示
5. 嘲讽盾牌边框
6. 智能高亮有效攻击目标

## 设计决策

| 决策项 | 选择 |
|--------|------|
| 随从形状 | 竖椭圆形（高度大于宽度） |
| 嘲讽盾牌颜色 | 金色 |
| 攻击触发方式 | 拖拽触发 |
| 攻击箭头样式 | 弧线箭头，从不透明渐变到红色 |
| 目标高亮逻辑 | 智能高亮（有嘲讽时只高亮嘲讽目标） |

## 技术方案

采用 **纯 CSS + SVG** 方案：
- 随从和盾牌：CSS 样式
- 攻击箭头：SVG 贝塞尔曲线 + 渐变
- 拖拽逻辑：原生 HTML5 Drag & Drop API

## 详细设计

### 1. 后端数据修改

**文件**: `webui/server/game.py`

修改 `get_game_state` 方法，为随从添加 `can_attack` 和 `taunt` 属性：

```python
# 玩家随从
"field": [{
    "name": str(m),
    "atk": m.atk,
    "health": m.health,
    "can_attack": m.can_attack(),   # 是否可攻击
    "taunt": m.taunt,                # 是否有嘲讽
} for m in player.field]

# 对手随从
"field": [{
    "name": str(m),
    "atk": m.atk,
    "health": m.health,
    "taunt": m.taunt,
} for m in opponent.field]

# 对手信息新增
"has_taunt": any(m.taunt for m in opponent.field)
```

### 2. 前端类型定义

**文件**: `webui/client/src/services/gameService.ts`

```typescript
export type MinionData = {
  name: string;
  atk: number;
  health: number;
  can_attack?: boolean;
  taunt?: boolean;
};
```

### 3. 随从椭圆形 + 可攻击边框

**文件**: `webui/client/src/components/GameBoard.css`

```css
.minion {
  border-radius: 50%;  /* 椭圆形 */
}

.minion.can-attack {
  border: 3px solid #4CAF50;
  box-shadow: 0 0 10px rgba(76, 175, 80, 0.6);
  cursor: grab;
}
```

### 4. 嘲讽盾牌边框

**文件**: `webui/client/src/components/GameBoard.css`

```css
.minion.taunt::before {
  content: '';
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  border: 4px solid #FFD700;
  border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
  box-shadow: 0 0 15px rgba(255, 215, 0, 0.5);
  pointer-events: none;
  z-index: -1;
}
```

### 5. 拖拽攻击逻辑

**文件**: `webui/client/src/components/GameBoard.tsx`

- 新增 `attackingMinion` 和 `attackTarget` 状态
- 实现 `handleMinionDragStart`、`handleMinionDrag`、`handleMinionDragEnd`
- 实现 `handleAttackDrop` 处理攻击目标放置

### 6. SVG 弧线箭头

**文件**: `webui/client/src/components/GameBoard.tsx`

- 使用 SVG `<path>` 绘制贝塞尔曲线
- 使用 `linearGradient` 实现从不透明到红色的渐变
- 使用 `<marker>` 绘制箭头头部

### 7. 智能高亮逻辑

**文件**: `webui/client/src/components/GameBoard.tsx`

```typescript
const getValidAttackTargets = () => {
  if (opponent.has_taunt) {
    // 只能攻击嘲讽随从
    return {
      minions: opponent.field.filter(m => m.taunt).map((_, i) => i),
      canAttackHero: false
    };
  }
  // 可以攻击所有
  return {
    minions: opponent.field.map((_, i) => i),
    canAttackHero: true
  };
};
```

## 实现顺序

1. 后端：修改 game.py 添加数据字段
2. 前端：更新类型定义
3. 前端：修改随从椭圆形样式
4. 前端：添加嘲讽盾牌样式
5. 前端：实现拖拽攻击逻辑
6. 前端：实现 SVG 弧线箭头
7. 前端：实现智能高亮逻辑
8. 后端：确认 attack 事件处理正确
