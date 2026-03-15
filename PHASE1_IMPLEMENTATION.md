# Phase 1 实施计划: 核心缺失机制

## 状态盘点

### 已实现的引擎功能 (fireplace)
| 机制 | 状态 | 引擎支持 |
|------|------|----------|
| Charge (冲锋) | ✅ | `charge` 属性 + `asleep` 逻辑 |
| Rush (突袭) | ✅ | `rush` 属性 + `attack_targets` 过滤 |
| Silence (沉默) | ✅ | `silence()` 方法 + `silenced` 属性 |
| Immune (免疫) | ✅ | `immune` 属性 + `attackable` 影响 |
| 手牌上限 (10张) | ✅ | `max_hand_size = 10` |
| 疲劳伤害 | ✅ | `fatigue_counter` + `Fatigue` action |
| 随从上限 (7个) | ✅ | `MAX_MINIONS_ON_FIELD = 7` |
| 回合超时 | ✅ | `timeout = 75` 秒 |

### WebUI 需添加的内容
| 功能 | 优先级 | 工作内容 |
|------|--------|----------|
| Charge/Rush 视觉指示 | P0 | 卡牌/随从上的图标和绿光 |
| Silence 视觉指示 | P0 | 沉默图标、移除卡牌文本显示 |
| Immune 视觉指示 | P0 | 金色护盾效果 |
| 疲劳计数器显示 | P1 | 英雄区域的疲劳提示 |
| 手牌数量提示 | P1 | 手牌区域显示 X/10 |
| 烧绳动画 | P1 | 回合结束前的燃烧绳子效果 |
| 随从上限提示 | P2 | 场上满7个时的提示 |

---

## 实施步骤

### Step 1: Charge & Rush 视觉指示器
**目标**: 让玩家一眼看出哪些随从可以立即攻击

1. **后端** (`game.py`): 在 `get_minion_data` 中添加:
   - `charge: boolean`
   - `rush: boolean`
   - `turns_in_play: number`

2. **前端** (`GameBoard.tsx`):
   - 添加 Charge 图标 (⚡) 和 Rush 图标 (🌪️)
   - 新登场的 Charge/Rush 随从添加绿色高亮边框
   - 攻击目标选择时，Rush 随从只能指向敌方随从

3. **测试卡牌**: 添加经典 Charge/Rush 卡到测试卡组
   - Charge: 狼骑兵 (CS2_124), 地狱野猪
   - Rush: 猛禽 (BOT_502)

### Step 2: Silence (沉默)
**目标**: 实现完整的沉默机制

1. **后端** (`game.py`):
   - 在 `get_minion_data` 中添加 `silenced: boolean`
   - 沉默后的随从只显示基础属性，不显示卡牌文本

2. **前端** (`GameBoard.tsx`):
   - 添加沉默图标 (🔇 或自定义图标)
   - 被沉默的随从卡牌文本变灰/隐藏
   - 沉默特效动画 (可选)

3. **测试卡牌**: 添加沉默相关卡
   - 德鲁伊: 自然印记 (EX1_155)
   - 牧师: 沉默 (EX1_332)
   - 萨满: 妖术 (EX1_246)

### Step 3: Immune (免疫)
**目标**: 免疫单位无法被选中或受伤

1. **后端** (`game.py`):
   - 在 `get_minion_data` 中添加 `immune: boolean`
   - 确保免疫单位不在 `valid_targets` 列表中

2. **前端** (`GameBoard.tsx`):
   - 添加金色护盾边框效果
   - 免疫单位不能被选为目标 (已在 `attackable` 中处理)
   - 免疫图标 (🛡️金色)

3. **测试卡牌**:
   - 兽人之怒 (CS2_104) - 战士法术
   - 保护之手 (CS2_087) - 圣骑士

### Step 4: 游戏边界规则 UI
**目标**: 完善游戏规则提示

1. **疲劳计数器**:
   - 牌库为空时，在英雄区域显示疲劳层数
   - 疲劳伤害飘字动画

2. **手牌上限提示**:
   - 手牌区域显示 `X/10`
   - 达到10张时变红色警告

3. **随从上限提示**:
   - 场上7个随从时，召唤按钮禁用并提示

4. **烧绳动画**:
   - 回合剩余15秒时启动烧绳
   - 绳子燃烧动画 + 音效
   - 回合结束倒计时

---

## 文件修改清单

### 后端 (webui/server/)
```
game.py:
  - get_minion_data(): 添加 charge, rush, silenced, immune, turns_in_play
  - get_game_state(): 添加 fatigue_counter, deck_count 显示
  - 确保 valid_targets 排除 immune 单位
```

### 前端 (webui/client/src/)
```
components/GameBoard.tsx:
  - 添加视觉指示器组件
  - 修改随从渲染逻辑
  - 添加烧绳组件
  - 修改目标选择逻辑 (Rush限制)

components/GameBoard.css:
  - Charge/Rush 高亮样式
  - Silence 图标样式
  - Immune 金色护盾样式
  - 烧绳动画样式

services/gameService.ts:
  - 更新类型定义
```

---

## 验收标准

### Charge/Rush
- [ ] 新登场的 Charge 随从可以立即攻击英雄
- [ ] 新登场的 Rush 随从只能攻击敌方随从
- [ ] 有视觉指示器区分 Charge/Rush/普通随从
- [ ] 第二回合后 Rush 随从可以正常攻击英雄

### Silence
- [ ] 被沉默的随从显示沉默图标
- [ ] 被沉默随从不显示卡牌文本
- [ ] 沉默移除所有 buff/debuff
- [ ] API 正确返回 silenced 状态

### Immune
- [ ] 免疫单位显示金色护盾
- [ ] 免疫单位不能被选为目标
- [ ] 免疫单位不受伤害

### 游戏边界
- [ ] 手牌达到10张时，新抽的牌被烧毁
- [ ] 牌库抽空后每回合受到递增疲劳伤害
- [ ] 场上7个随从时无法再召唤
- [ ] 回合最后15秒显示烧绳动画
