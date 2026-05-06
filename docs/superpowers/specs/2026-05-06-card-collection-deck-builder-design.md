# 卡牌收藏 + 卡组构建工具 · 设计文档

**日期**:2026-05-06
**作者**:与 Claude 头脑风暴产出
**目标产物**:为 Fireplace WebUI 增加卡牌浏览与卡组构建能力,并把建好的卡组接入对局开始流程。

---

## 1. 目标与非目标

### 目标
- 新增"卡组"主菜单入口,提供卡组列表 / 新建 / 编辑 / 删除 / 复制
- 编辑器:浏览全部已实现的可收藏卡(筛选 + 搜索),交互式加入卡组
- 卡组持久化:`localStorage` 为主,deckstring 为可移植格式(导入/导出)
- 对局开始流程改造:玩家槽 + 对手槽,各自可选已存卡组 / 粘贴 deckstring / 随机职业
- 100% 复用已有 `fireplace.deckstring` 编码 + `webui/server/deck_manager.py`
- 复用已有 `webui/server/card_text.py` 的 `CARDNAME` / `CARDTEXT` 缓存,**不重复 XML 解析**
- 清理现有断头代码:`gameService.ts` emit 的 `create_game_with_deck` 在 `socket.py` 没有 handler,本次合并到统一的 `create_game`

### 非目标(明确不做)
- 不模拟"已拥有卡牌 / 开包 / 合成"等账号收藏概念
- 不展示卡牌图片(没有图源,v1 文字+图标)
- 不做服务端卡组存储 / 多用户系统
- 不引入 react-router(沿用 App.tsx state 驱动)
- 不引入前端测试框架(YAGNI)
- v1 不做稀有度 / 扩展 / 种族 / 关键字筛选(v2 再加)
- 不强制 STANDARD 卡池过滤——format 仅作为元数据写入 deckstring

---

## 2. 用户场景

1. **造一副新卡组并立即测试**:主菜单 → 卡组 → 新建法师卡组 → 编辑器中按费用筛选凑齐 30 张 → 保存 → 主菜单 PVE → 玩家槽选这副卡组 / 对手槽选 `random:any` → 开始对局
2. **导入炉石客户端复制的 deckstring**:卡组列表 → "导入 deckstring" → 粘贴 → 工具识别已实现/未实现卡并展示 → 保存 → 进入对局测试
3. **两副卡组对线**:PVP 模式,玩家槽和对手槽都选已存卡组,直接开战
4. **纯浏览卡库**:卡组列表 → "浏览卡库"(临时模式)→ 看卡库筛选与详情但不修改任何卡组

---

## 3. 架构

### 3.1 模块拆分

```
webui/server/
├── card_catalog.py        新增:已实现 collectible 卡的元数据组装 + 进程级缓存(name/text 复用 card_text_loader)
├── card_text.py           已有:CARDNAME/CARDTEXT 启动时 parse + zhCN→enUS fallback;不动
├── deck_manager.py        已有:deckstring 编/解码,微调 export 接口
├── views.py               改:_load_card_multilang 删除,改用 card_text_loader;新增 cards/all + decks/validate endpoints
└── socket.py              改 create_game handler:接收双 DeckSpec;删除 create_game_with_deck 引用

webui/client/src/
├── App.tsx                状态机扩展:menu / decks-list / deck-edit / play-setup / in-game
├── components/
│   ├── DeckList.{tsx,css}     卡组列表页
│   ├── DeckEditor.{tsx,css}   编辑器(组合 CardPool + DeckPanel)
│   ├── CardPool.{tsx,css}     左侧卡库(筛选 + 列表 + hover 预览触发)
│   ├── DeckPanel.{tsx,css}    右侧卡组(已加卡 + 顶栏操作)
│   ├── CardRow.tsx            小尺寸"卡牌格"(费用 + 名 + 攻防/类型),复用
│   ├── CardPreview.tsx        hover/右键时的详情卡片
│   └── PlaySetup.{tsx,css}    开始游戏页(双槽位)
├── services/
│   ├── cardCatalog.ts         /api/cards/all 加载 + 内存索引 + 筛选/搜索
│   ├── deckStore.ts           localStorage 读写 + import/export deckstring
│   └── gameService.ts         已有,新增 startGameWithDecks
└── types/
    └── deck.ts                Card / Deck / DeckSpec / Format 类型定义
```

### 3.2 复用与重构

**`is_card_implemented` 单一出处**。`is_card_implemented` / `IMPLEMENTED_CARD_PREFIXES` / `CARD_BLACKLIST` 当前在 `webui/server/game.py`。**移到 `card_catalog.py`**,`game.py` 改为 import:`from .card_catalog import is_card_implemented`。导入方向:`card_catalog` → `fireplace.cards`(单向);`game` → `card_catalog`(单向);两者无循环。

**XML 解析复用 `card_text.py`**。`card_text_loader`(全局实例)启动时已经把 `CARDNAME` / `CARDTEXT` tag 的 `zhCN` + `enUS` fallback 摘进 `card_data` dict。`card_catalog.py` 直接调用 `card_text_loader.get_name(id)` / `get_text(id)`,**不重复 parse XML**。

**`views.py` 清理**。当前 `_load_card_multilang` 每次都重新 parse 整棵 XML(O(N×M))。删除该函数,`/api/cards/<card_id>` endpoint 改为调用 `card_text_loader`。

**断头代码清理**。`gameService.ts` 第 186 行 `socketService.emit('create_game_with_deck', ...)` 在 `socket.py` 没有 handler,目前永远走不通。本次重构将该分支合并到新版 `create_game` 统一处理。

**XML tag 命名**。`CardDefs.xml` 实际 tag 是 `CARDTEXT`(不是 `CARDTEXT_INHAND`);保持与 `card_text.py` 现有约定一致。

---

## 4. 数据模型

### 4.1 Card(后端 → 前端)

```ts
type Card = {
  id: string;             // "CS2_029"
  dbf_id: number;         // deckstring 用
  name_zh: string;        // CardDefs.xml CARDNAME zhCN(缺失 fallback enUS,再 fallback id)
  name_en: string;
  text_zh: string;        // CardDefs.xml CARDTEXT zhCN(由 card_text_loader 提供)
  text_en: string;
  cost: number;
  attack?: number;        // MINION / WEAPON
  health?: number;        // MINION
  durability?: number;    // WEAPON
  type: "MINION" | "SPELL" | "WEAPON";
  card_class: string;     // "MAGE" | "NEUTRAL" | ...
  rarity: string;         // "FREE" | "COMMON" | "RARE" | "EPIC" | "LEGENDARY"
  card_set: string;       // "EXPERT1" | "GVG" | ...(v1 不在 UI 暴露,只入 payload)
  race?: string;
  collectible: true;
  max_count: number;      // 推导规则:rarity == "LEGENDARY" → 1,否则 → 2。
                          // TODO(v2):若出现"非传说但限 1 张"的特殊卡(目前未知)再加例外列表
};
```

英雄卡(`CardType.HERO`)不进卡库——卡组的英雄由 `hero_class` 字段决定,后端 `import_deck_from_string` 已通过 `HERO_ID_MAP` 处理。

### 4.2 Deck(localStorage)

```ts
type Deck = {
  id: string;             // crypto.randomUUID()
  name: string;
  hero_class: string;     // "MAGE" | "WARRIOR" | ...
  format: "STANDARD" | "WILD" | "CLASSIC";  // 新建默认 STANDARD
  cards: Array<{ card_id: string; count: number }>;
  created_at: string;     // ISO
  updated_at: string;
};

// localStorage:
const DECKS_STORAGE_KEY = "fireplace.decks.v1";
const DECKS_SCHEMA_VERSION = 1;
//   key DECKS_STORAGE_KEY  →  { schema_version: 1, decks: { [deckId]: Deck } }

// 加载流程:
//   1. 读 raw,解 JSON
//   2. 看 schema_version → 选 migrate 函数;v1 的 migrate 是 identity
//   3. 逐个 deck 跑 schema 校验,坏的跳过 + console.warn
// 后续 v2 schema 变化时只需新增 migrate_v1_to_v2 + 升级 STORAGE_KEY 后缀
```

**deckstring 不直接存** —— `cards + hero_class + format` 是 source of truth,deckstring 在导出/导入时通过 `deck_manager.py` 现场转换,避免双副本不一致。

### 4.3 DeckSpec(socket payload)

```ts
type DeckSpec =
  | { type: "deckstring"; value: string }
  | { type: "random"; card_class: string };  // "MAGE" 或 "ANY"
```

---

## 5. 后端 API

### 5.1 `GET /api/cards/all`

- Query:`lang` 可选(默认返回 zhCN+enUS 两份)
- 返回:`{ cards: Card[], total: number, generated_at: string }`
- **缓存**:进程级 `_catalog_cache`(惰性初始化),内容基于 `fireplace.cards.db` + `card_text_loader`。`cards.db` 在运行时不变(无热更新机制),缓存永不过期
- **初始化保护**:第一次访问时若 `cards.db.initialized == False` 则先 `cards.db.initialize()`,避免和 game flow 第一次 init 抢
- **多进程注意**:若 server 用 gunicorn 多 worker 部署,每个进程各持一份 ≈ 600KB(可接受);未来若想跨进程共享需要 Redis 之类,v1 不做
- **ETag**:基于内容哈希,浏览器二次访问命中 304
- 大小估算:~2500 张 × ~250B ≈ 600KB JSON;gzip 后 ~150KB

### 5.2 `POST /api/decks/validate`

- Body:`{ deckstring: string }`
- 返回:
  ```json
  {
    "valid": true,
    "hero_class": "MAGE",
    "format": "STANDARD",
    "cards": [{"card_id": "CS2_029", "count": 2, "implemented": true}, ...],
    "unimplemented_count": 0,
    "total_cards": 30,
    "error": null
  }
  ```
- 失败时返回 `{ valid: false, error: "<具体原因>" }`(其它字段省略)
- **异常捕获**:必须 try/except 包裹所有解码逻辑(`InvalidDeckstring`、`InvalidDeck`、`KeyError` 等);任何异常 → `valid: false`,`error` 字段写人类可读说明;**绝不让异常 500**

### 5.3 `socket.create_game` 修改(注意:事件名是 `create_game`,**不是** `start_game`)

**当前 payload**(被替换):
```ts
{ mode, player_class, test_deck? }
```

**新 payload**:
```ts
{ mode, player: DeckSpec, opponent: DeckSpec, test_deck?: bool }
```

**不保留向后兼容**。`gameService.ts` 是该事件唯一的发起方(包括目前断头的 `create_game_with_deck` 也只在它一处),客户端在本次重构里同步改造,无需保留旧 payload 兼容路径。

**`GameManager.create_game()` 签名同步改为**:
```python
def create_game(self, *, mode: str, p1_spec: DeckSpec, p2_spec: DeckSpec, test_deck: bool = False) -> str
```
移除原 `player1_class` / `player2_class` / `custom_deck` 位置参数(它们的功能由 `DeckSpec.type=random` 和 `DeckSpec.type=deckstring` 表达)。`test_deck=True` 仍然走 `create_test_deck`(开发便利)且无视 spec(测试时不关心卡组)。

**Handler 逻辑**:
- 解析 `p1_spec` / `p2_spec`:
  - `type: "deckstring"` → `import_deck_from_string(value)` → 得到 `(cards, hero_class, format)` → 校验所有卡 `is_card_implemented`,任一失败 → `emit('create_game_error', {...})`,不开局
  - `type: "random"` → `filtered_random_draft(parse_card_class(card_class))`(支持 `"ANY"` = `random_class()`)
- 两边卡组都准备好后,调 `manager.create_game(mode=mode, p1_spec=..., p2_spec=...)`
- PVE 模式:p2 通常默认 `{type: "random", card_class: "ANY"}`,但允许玩家在 PlaySetup 改;handler 不区分 PVE/PVP,取信于前端送上的 spec
- PVP 模式:p1/p2 都由前端送 deckstring 或 random

---

## 6. UX 流程

### 6.1 状态机(App.tsx `view` 字段)

```
"menu"
  ├─ click "卡组" → "decks-list"
  │     ├─ click 已有卡组 → "deck-edit" (currentDeckId = id)
  │     ├─ click "新建" → "deck-edit" (currentDeckId = 新建占位)
  │     ├─ click "浏览全卡库" → "deck-edit" (currentDeckId = null) ← 浏览模式
  │     └─ "返回" → "menu"
  └─ click PVE/PVP/AI(mode 同步保存) → "play-setup"
        ├─ 双槽位选好 + "开始" → "in-game"
        │     └─ 退出对局 → "menu"
        └─ "返回" → "menu"
```

`deck-edit` 是**唯一**的卡组/卡库 view,通过 `currentDeckId: string | null | "new"` 区分三种子模式,组件复用最大化(见 §6.2)。

### 6.2 编辑器(DeckEditor)布局

`DeckEditor` 接受 `deckId: string | null` 与 `mode: "edit" | "new" | "browse"` 派生属性。三种模式共用同一组件,差异仅在右侧面板:

| 模式 | currentDeckId | DeckPanel | 卡库点击行为 |
|---|---|---|---|
| edit | 已有卡组 id | 显示 | 加卡 |
| new | "new"(临时) | 显示 | 加卡 |
| browse | null | **隐藏**(整个右栏不渲染) | **不加卡**;只触发 hover 预览 / 右键详情 |

炉石客户端式分栏:

- **左 2/3**:`CardPool`
  - 顶部筛选条:职业(下拉,默认= 当前卡组职业 + 中立;**browse 模式默认"全部"**)| 费用(0-7+ 多选格)| 类型(下拉)| 搜索框
  - 列表:每行一个 `CardRow`(费用 + 名 + 类型/攻防);hover → 右侧悬浮 `CardPreview`
  - 单击:edit/new 模式 = 加入卡组(达到 `max_count` 时按钮 disabled,非当前职业卡也 disabled);**browse 模式 = 打开详情面板**
  - 右键/长按 = 打开详情面板(显示 `text_zh`)
- **右 1/3**:`DeckPanel`(browse 模式时整个不渲染,左侧自动占满全宽)
  - 顶栏:卡组名(可点击重命名)| 职业图标 | "X/30" 计数 | Format 下拉
  - 主体:已加卡按费用排序;每行 `卡名 · ×N`,点击 = 移除一张
  - 底部按钮:**保存** | **导出 deckstring**(复制到剪贴板 + toast) | **返回**

### 6.3 卡组保存约束

- 卡组**总卡数**在 1-30 之间允许保存(模拟器场景下用户可能想测小卡组;UI 显示"X/30"提示但不阻止)。**总卡数 > 30 不允许保存**(理论上只可能由破坏性 deckstring 导入触发,通过 add 按钮无法达到)
- 单卡数量超过 `max_count`(传说=1,其他=2)UI 阻止"加入"
- 总卡数已达 30 时所有"加入"按钮 disabled

### 6.4 PlaySetup(开始对局页)

```
[玩家槽]                         [对手槽]
▼ 类型:已存卡组 / 粘贴deckstring / 随机    (同左)
  └─ 对应字段                     └─ 对应字段

                  [开始游戏]      (两槽都已选才亮)
```

**默认值**(进入页面时):
- PVE 模式:玩家槽 = 空(强制选择)、对手槽 = `{type: "random", card_class: "ANY"}`(开战不改也能立即玩)
- PVP 模式:两槽都为空,文案改为"玩家 1 / 玩家 2";要求两边都选满才能开始
- AI 模式:同 PVE

---

## 7. 错误处理与边界情况

| 情况 | 处理 |
|---|---|
| 导入 deckstring 含未实现卡 | `validate` 标记 `implemented:false`;编辑器灰显;**保存允许、开局拒绝** |
| `localStorage` 配额耗尽 | `deckStore` try/catch,降级到内存 + toast 警告 |
| `localStorage` 数据损坏 | 加载时按 schema 校验,坏卡组跳过 + console.warn,不阻塞其它 |
| 传说卡 > 1 / 普通卡 > 2(导入触发) | "加入"按钮在达到上限时 disabled;导入时 `validate` 标红;允许保存,开局拒绝 |
| 总卡数 > 30(导入触发) | `validate` 报错;允许进入编辑器查看,但**保存按钮 disabled**(必须先减到 ≤ 30) |
| 跨职业加卡 | 非当前职业且非中立的卡"加入"按钮 disabled |
| 删除卡组 | 二次确认 toast |
| 多语言 fallback | `name_zh` 缺失 → `name_en` → `card.id` |
| `CardDefs.xml` 解析慢 | `card_catalog.py` 启动时一次性 parse 进 dict |
| 后端 socket 收到无效 DeckSpec | emit `create_game_error` 给前端,显示 toast,不开局 |
| `validate` 任何解码异常 | try/except 全包裹 → `{valid:false, error:"..."}`,不返回 500 |
| 浏览模式下点击卡牌 | 打开详情面板,**不加卡**(DeckPanel 此时未挂载) |

---

## 8. 测试策略

### 8.1 Python 单元测试

新增 / 扩展:

- `tests/test_card_catalog.py`
  - 返回卡片均 `collectible == True`
  - 返回卡片均通过 `is_card_implemented`
  - 返回卡片均无 `CardType.HERO`
  - `max_count` 与 `rarity` 一致(LEGENDARY=1)
  - 多语言 fallback 行为(故意删一张卡的 zhCN 字段)
  - ETag 在卡库内容不变时稳定

- `tests/test_deck_manager.py`(扩展现有 `test_deckstring.py`)
  - round-trip:Deck → deckstring → Deck 完全一致
  - 未实现卡的 validate 输出正确

- `tests/test_socket_create_game.py`
  - 三种 DeckSpec(deckstring / random:CLASS / random:ANY)各走一次
  - 双槽位独立(PVE 玩家=deckstring + 对手=random;PVP 双方都 deckstring)
  - 无效 deckstring → `create_game_error` 事件,不创建 game
  - 含未实现卡的 deckstring → `create_game_error`,不创建 game

### 8.2 前端

v1 不引入测试框架。关键纯函数(`deckStore` 序列化、`cardCatalog` 筛选、deckstring import/export)写为可单测纯函数,以便后续接入 vitest。

### 8.3 验收清单(手测)

- [ ] 主菜单"卡组" → 列表 → 新建 → 选职业 → 编辑器加卡到 30 张 → 保存 → 列表显示
- [ ] 编辑器:筛选费用 / 类型 / 搜索中文名 / 搜索英文名 各能正确 narrow 列表
- [ ] hover 卡牌出现右侧 `CardPreview`;单击加入;面板里单击移除
- [ ] 法师卡组里把"火球术"加到 2 张,"加入"按钮变 disabled
- [ ] 法师卡组中,猎人独有卡的"加入"按钮 disabled
- [ ] 导出 deckstring → 复制到剪贴板 → 粘贴回导入框 → 卡组与原 cards/hero/format 完全相同
- [ ] 用真实炉石客户端的 deckstring(WILD)导入,正确解析已实现部分,未实现部分标灰
- [ ] 主菜单 PVE → 双槽位:玩家槽=已存卡组,对手槽=`random:ANY` → 开始,对局正常
- [ ] PVE 模式对手槽改为某副已存卡组 → 对手 AI 用该卡组开局(不再走 filtered_random_draft)
- [ ] PVP 双槽都用已存卡组 → 对局正常
- [ ] localStorage 手动改坏 JSON → 重新加载页面,提示+跳过,其它卡组照常
- [ ] 卡组列表 → "浏览全卡库" → 进入浏览模式,DeckPanel 不显示,左侧占满;点卡只弹详情,不加卡
- [ ] 含未实现卡的 deckstring 导入,validate 标红;尝试开局 → 收到 `create_game_error`,游戏未创建

---

## 9. 交付物 / 不在 v1 范围

### 在 v1 范围
- 上述全部模块、UI、API、测试
- 中英文 i18n 串(`webui/client/src/i18n.ts` 现有结构扩展)
- 文档:本设计文档落盘

### 留给 v2(明确不做)
- 稀有度 / 扩展 / 种族 / 关键字筛选
- 卡牌图片
- 服务端卡组存储 + 多用户
- "已拥有"概念 / 开包模拟
- 卡组对战胜率统计
- 卡组分享(URL 含 deckstring)
- 复制 deckstring 到剪贴板的 fallback(老浏览器无 `navigator.clipboard`)

---

## 10. 关键决策记录

| 决策 | 取舍 |
|---|---|
| 卡库范围 = 仅已实现 | 保证"造的卡组都能开战",代价是看不到正在开发的扩展 |
| 卡组存 localStorage | 无后端用户系统;靠 deckstring 跨设备 |
| 双卡组槽位(玩家+对手) | 模拟器核心场景是"对线测试";单槽位会丢失这个能力 |
| 不引入 react-router | 当前 5-6 个 view,state 驱动够用,装 router 是 over-engineer |
| 一次性返回全部卡库 | ~150KB gzip,体验远好于分页;且筛选可前端瞬时完成 |
| 保存允许 < 30 张 | 模拟器场景下需要测小/不完整卡组;UI 显示但不阻止 |
| `card_catalog.py` 抽出 `is_card_implemented` | 让"实现口径"只有一个出处,避免 game/card-pool 两边漂移 |
| Format 只作元数据,不过滤卡池 | 模拟器没有"轮换"概念,STANDARD/WILD 在我们这里没有真实区别 |
| `card_catalog.py` 复用 `card_text_loader`,不自建 XML 解析 | 102MB 的 `CardDefs.xml` parse 一次就好,避免双份缓存 |
| `create_game` 改签名,不保留旧 payload | 唯一调用方是自家 `gameService.ts`,本次同步改造;旧 `create_game_with_deck` 是断头死代码,顺便删 |
| 浏览模式 = `DeckEditor` with `deckId=null` | 状态机不增加分支;`CardPool` 组件保持单一,`DeckPanel` 条件渲染足够 |
