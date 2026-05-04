# WebUI 完整接入新卡牌 / 新机制 — 实施计划

**日期**: 2026-05-04
**背景**: 引擎已实现的 ~130+ 张新卡（CORE / RLK / EDR / CATA / WONDERS / TTN / TSC / BAR / REV / DMF / WW / SW / WC / YOP / ETC / TID）和 ~10 个新机制（Corpse / Herald / Imbue / Forge / Dredge / Excavate / Starship / Tourist / Kindred / Dark Gift / Bonus Effect / FABLED + Temporary）目前 WebUI 完全看不见。本计划把它们接入。

---

## 现状摘要

| 路径 | 当前 | 阻塞点 |
|------|------|--------|
| 牌组导入（deckstring） | ✅ 已能用 | 无（`deck_manager` 不做 prefix 过滤）|
| 随机抽牌组 | ❌ | `IMPLEMENTED_CARD_PREFIXES` 硬编码 24 旧前缀 |
| 测试牌组 | ❌ | `TEST_DECK_CARDS` 硬编码旧卡 ID；DK 类完全缺失 |
| 玩家资源序列化 | ❌ | `get_game_state()` 不输出 corpses / herald_count / imbue_count / excavate_count / starship_pieces / dark_gifts_given |
| 客户端资源 UI | ❌ | `GameBoard.tsx` 无对应 counter 显示 |
| 卡牌中文文本 | ⚠️ | `card_text.py` 自动读 XML，新卡如有 zhCN 节点会自动出现，否则回退英文（需抽查）|
| 卡牌图片 | ⚠️ | 项目里没看到 per-card art —— 应该走默认渲染（cost / atk / health 文本卡），新卡同理 |

---

## 实施分 4 阶段

### Phase 4A — Server-side 数据接入（低风险，~30min）

**4A.1 扩展 `IMPLEMENTED_CARD_PREFIXES`** （`webui/server/game.py`）
追加 16 个新前缀：
```python
'CORE',       # Core 重印
'RLK',        # Lich King DK 套包
'EDR',        # Emerald Dream
'CATA',       # Cataclysm
'WON',        # Wonders 迷你包
'BAR',        # Forged in the Barrens
'TTN',        # Titans
'TSC',        # Sunken City
'REV',        # Castle Nathria
'DMF',        # Darkmoon Faire
'WW',         # Showdown
'SW',         # Stormwind
'WC',         # Whatever
'YOP',        # Year of the Pegasus
'ETC',        # Festival of Legends
'TID',        # TID-prefixed mini-set
```
+ 删除 `'DINO', 'TLC'` 的 commented-out 句（如果想接 TLC，单独议）

**4A.2 在玩家状态序列化里加资源 counter**（`get_game_state()` 函数 ~line 728-758）

为 `player` 和 `opponent` 各加：
```python
"corpses": getattr(player, 'corpses', 0),
"herald_count": getattr(player, 'herald_count', 0),
"imbue_count": getattr(player, 'imbue_count', 0),
"excavate_count": getattr(player, 'excavate_count', 0),
"starship_pieces": len(getattr(player, 'starship_pieces', [])),
"is_building_starship": getattr(player, 'is_building_starship', False),
"dark_gifts_given": len(getattr(player, 'dark_gifts_given', [])),
"jade_golem": getattr(player, 'jade_golem', 0),
```

**4A.3 扩展 `TEST_DECK_CARDS`**

- 给 DK 加测试牌组（目前完全缺失 DEATHKNIGHT 键）
- 为现有职业追加新机制条目，例如：
  - DRUID: `kindred`, `imbue`
  - HUNTER: `dredge`, `imbue`, `excavate`
  - MAGE: `excavate`, `starship`, `forge`
  - PALADIN: `imbue`, `tourist`
  - PRIEST: `forge`, `dredge`
  - ROGUE: `tourist`, `excavate`
  - SHAMAN: `starship`, `forge`
  - WARLOCK: `tourist`, `dark_gift`
  - WARRIOR: `forge`, `excavate`, `starship`
  - NEUTRAL: `kindred`, `bonus_effect`, `temporary`
- 每条 2 张代表卡，挑实际工作良好的 ID（具体 ID 在执行时依赖 `tests/test_modern_phase*.py` 已验证的卡）

**4A.4 修剪 `CARD_BLACKLIST`**

加入个别已知边角问题卡。先空，发现问题再补。

---

### Phase 4B — Client-side UI（中风险，~1.5h）

**4B.1 TypeScript 类型扩展**（`client/src/services/gameService.ts`）

`PlayerState` / `OpponentState` 接口加新字段：
```typescript
corpses?: number;
herald_count?: number;
imbue_count?: number;
excavate_count?: number;
starship_pieces?: number;
is_building_starship?: boolean;
dark_gifts_given?: number;
jade_golem?: number;
```

**4B.2 GameBoard.tsx 资源 counter UI**

参考现有 `armor` / `secret_count` / `overload_locked` 渲染样式，在玩家与对手 hero portrait 周围加 badge 群：

| 资源 | 图标 | 显示条件 |
|------|------|----------|
| 尸体 corpses | 💀 | DK 职业且 `corpses > 0` |
| 祝福 imbue | ✨ | `imbue_count > 0` |
| 挖掘 excavate | ⛏️ | `excavate_count > 0`（显示等级 1-4）|
| 先驱 herald | ⚔️ | Cataclysm 卡组且 `herald_count > 0` |
| 飞船 starship | 🚀 | `is_building_starship` 真时显示部件数 |
| 暗礼 dark gifts | 🎁 | `dark_gifts_given > 0` |
| 翡翠 jade | 💚 | `jade_golem > 1` |

CSS 复用 `.overload-locked` 样式作为模板。

**4B.3 视觉打磨（可选）**

- counter 数值变化时短暂高亮（150ms transform: scale）
- hover tooltip 解释机制

---

### Phase 4C — 卡牌文本验证（低风险，~15min）

**4C.1 抽查中文文本可见性**

写一个小脚本，对 `IMPLEMENTED_CARD_PREFIXES` 的全部新前缀，抽 5 张卡看 `card_text_loader.get_card_info(id)` 是否返回 zhCN 内容。

如有缺失：
- 接受英文回退（card_text.py 已实现）
- 或硬编码补丁（不推荐，量太大）

**4C.2 简化机制说明**

我有一些卡是简化实现（例：`Marrow Manipulator` 全花完 corpses 而不让玩家选数量；`Necrotic Mortician` 用"任意 Undead 死过"代替"上回合后死过"）。考虑给这类卡的 description 加 `(simplified: ...)` 后缀，让用户知道实际行为。

可选——如果做，加在 `card_text_loader` 的 patch 字典里。

---

### Phase 4D — 验证 + Stab smoke test（~30min）

**4D.1 端到端 smoke**

1. 启动 `flask run`
2. **随机抽牌组路径**：建一局 PVE 战；P1 选 Druid → 检查 hand 里有没有 EDR_/CATA_/WON_ 卡
3. **测试牌组路径**：建一局 test_deck=True，DK 类 → hand 里应有 RLK_/CORE_RLK_ Corpse 卡
4. **deckstring 导入路径**：用一个含 Corpse 卡的 deckstring 导入 → 看玩家面板 corpse counter 是否正确累加
5. **机制 UI**：召一个 Body Bagger，验证 💀 icon 出现
6. **Resurrect / Discover / Imbue 等**：选一张代表卡逐个抽查不崩

**4D.2 回归**

`python -m pytest tests/ -p no:randomly` 应仍是 47 fail / 1082 pass（baseline 不变）。

**4D.3 已知缺口**

写一段已知不接入说明（cost-mod aura / Tourist 全套 / Adapt / Joust）。

---

## 风险评估

| 风险 | 概率 | 缓解 |
|------|------|------|
| 新卡随机抽出时崩溃（未充分测试的边角） | 中 | 4D.1 跑两三局观察日志；崩则加 `CARD_BLACKLIST` |
| 客户端字段缺失被读 → undefined render | 低 | TS 类型用 `?: number`，渲染前 `?? 0` |
| DK 职业 hero 没在 `HERO_ID_MAP` 里 | 中 | 检查 `deck_manager.HERO_ID_MAP`：缺则补 |
| 测试牌组 ID 引用了已重命名的卡 | 低 | 写完后 `python -c "from fireplace.cards import db; db.initialize(); db['<id>']"` 抽检 |
| Counter UI 占位太多挤压界面 | 低 | 只在 `> 0` 时渲染 |

---

## 工程顺序

```
Phase 4A.1  →  Phase 4A.2  →  Phase 4A.3
                                  ↓
                              Phase 4B.1  →  Phase 4B.2
                                                ↓
                                          Phase 4C  →  Phase 4D
```

预估 ~3h 完整闭环。每阶段独立 commit。

---

## 估算价值

| 接入后 | 数 |
|------|------|
| 随机抽牌组可见的额外卡数 | **~600+**（16 套包，多数 collectible 卡）|
| 测试牌组新增可演示机制 | **8-10 个机制**（Corpse / Imbue / Excavate / Forge / Dredge / Starship / Kindred / Dark Gift / Tourist / Bonus Effect）|
| 玩家可见资源 counter | **6-8 个** |
| 真正端到端可玩牌组 | **DK 整个职业**（之前 0 卡，现在 ~30 张）|
