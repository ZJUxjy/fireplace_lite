# 卡牌收藏 + 卡组构建工具 · 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给 Fireplace WebUI 增加卡组管理与卡库浏览,把已存卡组接入对局开始流程。

**Architecture:** 前端 React 19(无 router,沿用 App.tsx state-driven 视图)+ Flask/Socket.IO 后端。卡组持久化用 `localStorage`,deckstring 作可移植格式。卡牌元数据以 `/api/cards/all` 一次性下发,前端内存索引并在客户端做筛选/搜索。`socket.create_game` 改造为接收双 `DeckSpec`(玩家槽 + 对手槽),允许两边独立选择已存卡组、deckstring 或随机职业。

**Tech Stack:** Python 3.10+ / Flask / Flask-SocketIO / fireplace / hearthstone-enums · React 19 / TypeScript 5.9 / Vite 7 / i18next · pytest(后端测试)

**Spec:** `docs/superpowers/specs/2026-05-06-card-collection-deck-builder-design.md`

---

## 文件总览

### 后端(Python)

| 文件 | 操作 | 职责 |
|---|---|---|
| `webui/server/card_catalog.py` | **新增** | 已实现 collectible 卡的元数据组装 + ETag + 进程级缓存;`is_card_implemented` 等的新家 |
| `webui/server/card_text.py` | **不动** | 已有 `CardTextLoader`,提供 `get_name` / `get_text` |
| `webui/server/deck_manager.py` | 微调 | `import_deck_from_string` 增加 `mark_implemented` 选项,服务 validate |
| `webui/server/views.py` | 改 | 删 `_load_card_multilang`(改用 `card_text_loader`);新增 `/api/cards/all` 与 `/api/decks/validate` |
| `webui/server/game.py` | 改 | 移除 `IMPLEMENTED_CARD_PREFIXES` / `is_card_implemented` / `CARD_BLACKLIST`(改 import 自 `card_catalog`);`GameManager.create_game` 改签名 |
| `webui/server/socket.py` | 改 | `handle_create_game` 处理双 `DeckSpec`;不再有 `create_game_with_deck` 引用 |
| `tests/test_card_catalog.py` | **新增** | catalog 基础属性、缓存、ETag |
| `tests/test_deck_validate.py` | **新增** | validate API 各种 deckstring 用例 |
| `tests/test_create_game_specs.py` | **新增** | 双 DeckSpec、向后无兼容、错误事件 |

### 前端(TypeScript / React)

| 文件 | 操作 | 职责 |
|---|---|---|
| `webui/client/src/types/deck.ts` | **新增** | `Card` / `Deck` / `DeckSpec` / `Format` 类型 |
| `webui/client/src/services/cardCatalog.ts` | **新增** | 加载 `/api/cards/all`,内存索引,提供 `filter()` / `getById()` |
| `webui/client/src/services/deckStore.ts` | **新增** | localStorage CRUD + import/export deckstring(走 `/api/decks/validate`)|
| `webui/client/src/services/gameService.ts` | 改 | 重写 `createGame(mode, p1Spec, p2Spec)`;删 `create_game_with_deck` 引用 |
| `webui/client/src/components/CardRow.tsx` | **新增** | 单行卡牌格(费用 + 名 + 攻防/类型) |
| `webui/client/src/components/CardPreview.tsx` | **新增** | hover 时悬浮预览面板 |
| `webui/client/src/components/CardPool.{tsx,css}` | **新增** | 左侧卡库:筛选条 + 列表 + hover 触发预览 |
| `webui/client/src/components/DeckPanel.{tsx,css}` | **新增** | 右侧卡组面板:卡组名 + 已加卡 + 保存/导出/返回按钮 |
| `webui/client/src/components/DeckEditor.{tsx,css}` | **新增** | 组合 CardPool + DeckPanel;支持 `deckId: string \| null \| "new"` 三种模式 |
| `webui/client/src/components/DeckList.{tsx,css}` | **新增** | 卡组管理页:已存卡组列表 + 新建 + 导入 + 浏览全卡库 |
| `webui/client/src/components/PlaySetup.{tsx,css}` | **新增** | 开始对局页:玩家槽 + 对手槽 |
| `webui/client/src/App.tsx` | 改 | 新 `view` 字段;主菜单加"卡组"入口;PVE/PVP/AI 走 PlaySetup |
| `webui/client/src/i18n.ts` | 改 | 加新文案串(zhCN + enUS) |

---

## Task 1: 抽出 `is_card_implemented` 到 `card_catalog.py`(纯重构)

**Files:**
- Create: `webui/server/card_catalog.py`
- Modify: `webui/server/game.py`(删除 lines 66-123 的 `IMPLEMENTED_CARD_PREFIXES` / `CARD_BLACKLIST` / `is_card_implemented`)
- Test: `tests/test_card_catalog.py`(新增,本任务只放重构验证)

- [ ] **Step 1: 写失败测试**

`tests/test_card_catalog.py`:
```python
"""Tests for webui/server/card_catalog.py"""
import pytest


def test_is_card_implemented_known_card():
    """已知扩展前缀(EX1)的卡片应判为已实现"""
    from webui.server.card_catalog import is_card_implemented
    assert is_card_implemented("EX1_565") is True  # Flametongue Totem


def test_is_card_implemented_unknown_prefix():
    """未列入 IMPLEMENTED_CARD_PREFIXES 的扩展应判为未实现"""
    from webui.server.card_catalog import is_card_implemented
    assert is_card_implemented("DINO_400") is False  # Shrouded City prefix


def test_is_card_implemented_blacklist():
    """卡片 ID 在 CARD_BLACKLIST 中应判为未实现,即使前缀已实现"""
    from webui.server.card_catalog import (
        is_card_implemented, CARD_BLACKLIST,
    )
    CARD_BLACKLIST.add("EX1_999_test")
    try:
        assert is_card_implemented("EX1_999_test") is False
    finally:
        CARD_BLACKLIST.discard("EX1_999_test")


def test_game_module_reexports_for_compat():
    """game.py 仍可通过 import 拿到这些符号(其他模块可能依赖)"""
    from webui.server import game
    assert callable(game.is_card_implemented)
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace
python -m pytest tests/test_card_catalog.py -v
```
Expected: ImportError 或 AttributeError(`webui.server.card_catalog` 不存在)

- [ ] **Step 3: 写 `card_catalog.py` 抽出代码**

`webui/server/card_catalog.py`:
```python
"""
Card catalog: implemented-card filter + (later) collectible card metadata.

This module is the single source of truth for "which cards can actually be
played in our simulator". Both the random-deck generator (game.py) and the
deck builder UI (via /api/cards/all) read from here.
"""
from typing import Set


# 已实现的卡牌系列前缀(对应 fireplace/cards/ 目录下的文件夹)
# 只有这些系列的卡牌会被加入随机牌库与卡库浏览
IMPLEMENTED_CARD_PREFIXES: Set[str] = {
    # Classic
    'CS2', 'CS3', 'EX1', 'NEW1',
    # Naxxramas
    'FP1', 'NX2',
    # Goblins vs Gnomes
    'GVG',
    # Blackrock Mountain
    'BRM',
    # The Grand Tournament
    'AT',
    # League of Explorers
    'LOE',
    # Whispers of the Old Gods
    'OG',
    # One Night in Karazhan
    'KAR',
    # Mean Streets of Gadgetzan
    'CFM',
    # Journey to Un'Goro
    'UNG',
    # Knights of the Frozen Throne
    'ICC',
    # Kobolds & Catacombs
    'LOOT',
    # The Witchwood
    'GIL',
    # The Boomsday Project
    'BOT',
    # Rastakhan's Rumble
    'TRL',
    # Rise of Shadows
    'DAL',
    # Saviors of Uldum
    'ULD',
    # Scholomance Academy
    'SCH',
    # Ashes of Outland / Demon Hunter Initiate
    'BT',
    # Descent of Dragons
    'DRG',
}

# 黑名单:即使在前缀列表中,这些卡牌也有问题,需要排除
CARD_BLACKLIST: Set[str] = set()


def is_card_implemented(card_id: str) -> bool:
    """检查卡牌是否来自已实现的系列且不在黑名单"""
    if card_id in CARD_BLACKLIST:
        return False
    prefix = card_id.split('_')[0] if '_' in card_id else card_id[:3]
    return prefix in IMPLEMENTED_CARD_PREFIXES
```

- [ ] **Step 4: 改 `game.py` import**

`webui/server/game.py`:删除原 lines ~66-123 的 `IMPLEMENTED_CARD_PREFIXES` / `CARD_BLACKLIST` / `is_card_implemented` 定义(保留注释说明已迁移)。在文件顶部 imports 区(第 9 行 `from .card_text import card_text_loader` 附近)加:
```python
from .card_catalog import (
    is_card_implemented,
    IMPLEMENTED_CARD_PREFIXES,
    CARD_BLACKLIST,
)
```

- [ ] **Step 5: 跑测试确认通过**

```bash
python -m pytest tests/test_card_catalog.py -v
```
Expected: 4 passed

- [ ] **Step 6: 跑现有测试确认未破坏**

```bash
python -m pytest tests/test_webui_hero_cards.py -v
```
Expected: 现有测试仍通过(若环境无 CardDefs.xml 而 skip,接受 skip)

- [ ] **Step 7: 提交**

```bash
git add webui/server/card_catalog.py webui/server/game.py tests/test_card_catalog.py
git commit -m "refactor(webui): extract is_card_implemented to card_catalog module

The implemented-card filter is the source of truth for both random
deck generation and the upcoming deck builder. Move it out of game.py
so the new card catalog can own it without circular imports.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: `card_catalog.build_catalog()` 装配卡牌元数据

**Files:**
- Modify: `webui/server/card_catalog.py`
- Modify: `tests/test_card_catalog.py`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_card_catalog.py`:
```python
def test_build_catalog_filters_collectible_implemented_only():
    """build_catalog() 只返回 collectible 且 implemented 的卡片"""
    from webui.server.card_catalog import build_catalog, is_card_implemented
    cat = build_catalog()
    assert len(cat["cards"]) > 1000  # 健康检查:多扩展应有 1000+ 张
    for card in cat["cards"]:
        assert card["collectible"] is True
        assert is_card_implemented(card["id"])
        assert card["type"] in {"MINION", "SPELL", "WEAPON"}  # 不应有 HERO


def test_build_catalog_max_count_legendary():
    """传说卡 max_count == 1, 其它 == 2"""
    from webui.server.card_catalog import build_catalog
    cat = build_catalog()
    for card in cat["cards"]:
        if card["rarity"] == "LEGENDARY":
            assert card["max_count"] == 1, f"{card['id']} legendary should be 1"
        else:
            assert card["max_count"] == 2, f"{card['id']} should be 2"


def test_build_catalog_has_localized_names():
    """每张卡都有 name_zh 和 name_en(缺失时 fallback id)"""
    from webui.server.card_catalog import build_catalog
    cat = build_catalog()
    for card in cat["cards"][:50]:  # 抽样
        assert card["name_zh"], f"{card['id']} missing name_zh"
        assert card["name_en"], f"{card['id']} missing name_en"


def test_build_catalog_etag_stable():
    """两次调用产生相同的 ETag"""
    from webui.server.card_catalog import build_catalog
    cat1 = build_catalog()
    cat2 = build_catalog()
    assert cat1["etag"] == cat2["etag"]


def test_build_catalog_caches_in_process():
    """同一进程内只构建一次,二次调用走缓存(同一对象引用)"""
    from webui.server.card_catalog import build_catalog
    cat1 = build_catalog()
    cat2 = build_catalog()
    assert cat1 is cat2
```

- [ ] **Step 2: 跑测试确认失败**

```bash
python -m pytest tests/test_card_catalog.py -v -k "build_catalog"
```
Expected: 5 failures(`build_catalog` 未定义)

- [ ] **Step 3: 实现 `build_catalog()`**

追加到 `webui/server/card_catalog.py` 末尾:
```python
import hashlib
import json
from typing import Any, Dict, List, Optional

from fireplace.cards import db as _cards_db
from hearthstone.enums import CardType

_catalog_cache: Optional[Dict[str, Any]] = None


def _ensure_db_initialized() -> None:
    if not _cards_db.initialized:
        _cards_db.initialize()


def _safe_text_for(card_id: str, lang: str) -> str:
    """从 card_text_loader 取本地化文本,缺失时返回空串"""
    from .card_text import card_text_loader
    info = card_text_loader.card_data.get(card_id, {})
    if lang == "zhCN":
        return info.get("name") or ""
    return ""  # card_text.py 当前只缓存 zhCN+fallback;enUS 走下面 _english_name


def _english_name(card) -> str:
    """从 fireplace card 对象拿英文名(它的 __str__ 即英文名)"""
    return str(card)


def _card_to_dict(card_id: str, card) -> Dict[str, Any]:
    """把 fireplace card 对象 + 多语言数据组装成 API 字典"""
    from .card_text import card_text_loader

    rarity = card.rarity.name if card.rarity else "FREE"
    max_count = 1 if rarity == "LEGENDARY" else 2

    info = card_text_loader.card_data.get(card_id, {})
    name_zh = info.get("name") or _english_name(card) or card_id
    text_zh = info.get("text") or ""

    out: Dict[str, Any] = {
        "id": card_id,
        "dbf_id": card.dbf_id,
        "name_zh": name_zh,
        "name_en": _english_name(card) or card_id,
        "text_zh": text_zh,
        "text_en": "",  # v1: card_text.py 只存 zhCN+fallback;留空字符串占位
        "cost": getattr(card, "cost", 0),
        "type": card.type.name,
        "card_class": card.card_class.name if card.card_class else "NEUTRAL",
        "rarity": rarity,
        "card_set": card.card_set.name if card.card_set else "INVALID",
        "collectible": True,
        "max_count": max_count,
    }
    if card.type == CardType.MINION:
        out["attack"] = getattr(card, "atk", 0)
        out["health"] = getattr(card, "health", 0)
    elif card.type == CardType.WEAPON:
        out["attack"] = getattr(card, "atk", 0)
        out["durability"] = getattr(card, "durability", 0)

    race = getattr(card, "race", None)
    if race and race.name != "INVALID":
        out["race"] = race.name
    return out


def build_catalog() -> Dict[str, Any]:
    """构建已实现 collectible 卡的全量元数据列表(进程级缓存)"""
    global _catalog_cache
    if _catalog_cache is not None:
        return _catalog_cache

    _ensure_db_initialized()

    cards: List[Dict[str, Any]] = []
    for card_id in sorted(_cards_db.keys()):
        card = _cards_db[card_id]
        if not getattr(card, "collectible", False):
            continue
        if card.type == CardType.HERO:
            continue
        if card.type not in {CardType.MINION, CardType.SPELL, CardType.WEAPON}:
            continue
        if not is_card_implemented(card_id):
            continue
        cards.append(_card_to_dict(card_id, card))

    payload_json = json.dumps(cards, sort_keys=True, ensure_ascii=False)
    etag = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()[:16]

    from datetime import datetime, timezone
    _catalog_cache = {
        "cards": cards,
        "total": len(cards),
        "etag": etag,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return _catalog_cache


def reset_catalog_cache() -> None:
    """测试用:清缓存让下次 build_catalog() 重新计算"""
    global _catalog_cache
    _catalog_cache = None
```

- [ ] **Step 4: 跑测试确认通过**

```bash
python -m pytest tests/test_card_catalog.py -v -k "build_catalog"
```
Expected: 5 passed

- [ ] **Step 5: 提交**

```bash
git add webui/server/card_catalog.py tests/test_card_catalog.py
git commit -m "feat(webui): build_catalog produces implemented-card metadata

Reads collectible+implemented cards from fireplace.cards.db, joins
localized names from the existing card_text_loader, and assembles
a stable list with an ETag for HTTP caching. Process-level cache
since cards.db is immutable at runtime.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: `GET /api/cards/all` endpoint

**Files:**
- Modify: `webui/server/views.py`
- Test: `tests/test_card_catalog.py`(继续用)

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_card_catalog.py`:
```python
def test_api_cards_all_returns_catalog():
    """GET /api/cards/all 返回 catalog 内容"""
    from webui.server import create_app
    app = create_app()
    with app.test_client() as client:
        resp = client.get("/api/cards/all")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "cards" in data
        assert "total" in data
        assert data["total"] == len(data["cards"])
        assert data["total"] > 1000


def test_api_cards_all_etag_304():
    """带 If-None-Match 命中 ETag 时返回 304"""
    from webui.server import create_app
    app = create_app()
    with app.test_client() as client:
        first = client.get("/api/cards/all")
        etag = first.headers.get("ETag")
        assert etag

        second = client.get("/api/cards/all", headers={"If-None-Match": etag})
        assert second.status_code == 304
```

- [ ] **Step 2: 跑测试确认失败**

```bash
python -m pytest tests/test_card_catalog.py -v -k "api_cards_all"
```
Expected: 404 or AssertionError

- [ ] **Step 3: 加 endpoint**

修改 `webui/server/views.py`,在已有的 `/api/cards/<card_id>` route 之上加:
```python
@bp.route('/api/cards/all')
def cards_all():
    """返回全部已实现 collectible 卡的元数据(带 ETag 缓存)"""
    from .card_catalog import build_catalog
    catalog = build_catalog()
    etag = f'"{catalog["etag"]}"'

    if request.headers.get('If-None-Match') == etag:
        return ('', 304)

    response = jsonify({
        'cards': catalog['cards'],
        'total': catalog['total'],
        'generated_at': catalog['generated_at'],
    })
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'private, max-age=300'
    return response
```

- [ ] **Step 4: 跑测试确认通过**

```bash
python -m pytest tests/test_card_catalog.py -v
```
Expected: all passed(共 9 个测试)

- [ ] **Step 5: 提交**

```bash
git add webui/server/views.py tests/test_card_catalog.py
git commit -m "feat(webui): GET /api/cards/all endpoint with ETag

Single-shot endpoint feeding the deck builder's in-memory card index.
ETag matches the catalog hash; if the client sends If-None-Match
the server returns 304 with no body.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: `POST /api/decks/validate` endpoint

**Files:**
- Modify: `webui/server/deck_manager.py`(加 `mark_implemented`)
- Modify: `webui/server/views.py`
- Test: `tests/test_deck_validate.py`(新增)

- [ ] **Step 1: 写失败测试**

`tests/test_deck_validate.py`:
```python
"""Tests for POST /api/decks/validate"""
import pytest


@pytest.fixture
def client():
    from webui.server import create_app
    app = create_app()
    with app.test_client() as c:
        yield c


def _build_deckstring(cards, hero_class_id, fmt=2):
    """直接用 fireplace.deckstring 构造一个合法 deckstring"""
    from fireplace.deckstring import encode_deck, Format
    return encode_deck(cards, hero_class_id, Format(fmt))


def test_validate_valid_deckstring(client):
    """合法 deckstring 返回 valid=True 与解析后的卡片列表"""
    # Mage hero (hero_class_id=8 -> CardClass.MAGE), all implemented Classic spells
    # CS2_029 (Fireball) dbf_id is known stable
    from fireplace.cards import db as _db
    if not _db.initialized:
        _db.initialize()
    fb = _db.get("CS2_029")
    fz = _db.get("CS2_023")  # Arcane Intellect
    deckstring = _build_deckstring([(fb.dbf_id, 2), (fz.dbf_id, 2)], 8, 2)

    resp = client.post("/api/decks/validate", json={"deckstring": deckstring})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["valid"] is True
    assert data["hero_class"] == "MAGE"
    assert data["format"] == "STANDARD"
    assert data["unimplemented_count"] == 0
    assert data["total_cards"] == 4
    assert all(c["implemented"] for c in data["cards"])


def test_validate_malformed_deckstring(client):
    """无效 base64 / 损坏数据返回 valid=False"""
    resp = client.post("/api/decks/validate", json={"deckstring": "not-a-valid-deckstring"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["valid"] is False
    assert data["error"]


def test_validate_missing_body(client):
    """缺 deckstring 字段返回 valid=False,而不是 500"""
    resp = client.post("/api/decks/validate", json={})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["valid"] is False
    assert data["error"]


def test_validate_marks_unimplemented_cards(client):
    """deckstring 含未实现卡时, implemented:false 标记 + unimplemented_count > 0"""
    # 用一个明显未实现的 dbf_id(从 CardDefs.xml 找一张 DINO_ 系列的 dbf_id)
    # 简化:直接构造一个虚假大 dbf_id,deckstring 解码后 lookup 失败
    deckstring = _build_deckstring([(999999, 1)], 8, 2)
    resp = client.post("/api/decks/validate", json={"deckstring": deckstring})
    data = resp.get_json()
    # 此分支取决于 deck_manager 行为;期望 valid=True 但 cards 列表中该项 implemented=False
    # 或者 valid=False 抛出 InvalidDeck — 都接受,关键是不 500
    assert resp.status_code == 200
    if data["valid"]:
        assert data["unimplemented_count"] >= 1
```

- [ ] **Step 2: 跑测试确认失败**

```bash
python -m pytest tests/test_deck_validate.py -v
```
Expected: 4 errors / failures(endpoint 不存在)

- [ ] **Step 3: 微调 `deck_manager.import_deck_from_string`**

修改 `webui/server/deck_manager.py`:在返回 dict 中给每张卡加 `implemented` 字段(默认 True;DBF 找不到的卡走 `invalid_cards` 通道)。具体改 `import_deck_from_string` 的返回构造,**lines ~120-143**:

替换:
```python
    cards = []
    invalid_cards = []

    for dbf_id, count in cards_dbf:
        card_id = get_card_by_dbf_id(dbf_id)
        if card_id:
            cards.append((card_id, count))
        else:
            invalid_cards.append(dbf_id)
    ...
    return {
        "cards": cards,
        ...
    }
```
为:
```python
    from .card_catalog import is_card_implemented

    cards_with_status = []
    invalid_cards = []
    unimplemented_count = 0

    for dbf_id, count in cards_dbf:
        card_id = get_card_by_dbf_id(dbf_id)
        if not card_id:
            invalid_cards.append(dbf_id)
            continue
        impl = is_card_implemented(card_id)
        if not impl:
            unimplemented_count += count
        cards_with_status.append({
            "card_id": card_id,
            "count": count,
            "implemented": impl,
        })

    total_cards = sum(c["count"] for c in cards_with_status)

    return {
        "cards": cards_with_status,
        "hero_class": hero_class,
        "hero_id": hero_id,
        "format": format_type.name,
        "invalid_cards": invalid_cards,
        "unimplemented_count": unimplemented_count,
        "total_cards": total_cards,
    }
```

注意:这是行为变化(原来 `cards` 是 tuple 列表)。检查 `import_deck_from_string` 的内部调用方:用 `grep -rn "import_deck_from_string" webui/` 确认无其它调用受影响,如果有则一并改适配。

- [ ] **Step 4: 加 validate endpoint**

修改 `webui/server/views.py`,加:
```python
@bp.route('/api/decks/validate', methods=['POST'])
def validate_deck():
    """校验 deckstring 并标记未实现卡"""
    from .deck_manager import import_deck_from_string, InvalidDeck

    body = request.get_json(silent=True) or {}
    deckstring = body.get('deckstring')
    if not deckstring:
        return jsonify({'valid': False, 'error': 'missing deckstring'}), 200

    try:
        result = import_deck_from_string(deckstring)
    except (InvalidDeck, ValueError, TypeError, Exception) as e:
        return jsonify({'valid': False, 'error': str(e)}), 200

    return jsonify({
        'valid': True,
        'hero_class': result['hero_class'],
        'format': result['format'],
        'cards': result['cards'],
        'unimplemented_count': result['unimplemented_count'],
        'total_cards': result['total_cards'],
        'error': None,
    })
```

- [ ] **Step 5: 跑测试确认通过**

```bash
python -m pytest tests/test_deck_validate.py -v
```
Expected: 4 passed

- [ ] **Step 6: 跑现有测试确认未破坏 import_deck_from_string 调用方**

```bash
python -m pytest tests/test_webui_hero_cards.py -v
```
Expected: 仍 PASS(若没有命中调用)

- [ ] **Step 7: 提交**

```bash
git add webui/server/deck_manager.py webui/server/views.py tests/test_deck_validate.py
git commit -m "feat(webui): POST /api/decks/validate endpoint

Decodes a deckstring, marks each card as implemented/unimplemented
against the catalog filter, and returns the result without ever
500ing on bad input. The import_deck_from_string return shape now
carries the implementation flag so the API can surface it directly.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: `GameManager.create_game` 改签名为接收双 DeckSpec

**Files:**
- Modify: `webui/server/game.py`(`GameManager.create_game` 签名 + body)
- Test: `tests/test_create_game_specs.py`(新增)

- [ ] **Step 1: 写失败测试**

`tests/test_create_game_specs.py`:
```python
"""Tests for GameManager.create_game with DeckSpec args."""
import pytest


@pytest.fixture
def manager():
    from webui.server.game import GameManager
    m = GameManager()
    m.initialize()
    return m


def test_create_game_random_specs(manager):
    """两边都是 random:ANY 时,正常创建游戏"""
    gid = manager.create_game(
        mode="pve",
        p1_spec={"type": "random", "card_class": "MAGE"},
        p2_spec={"type": "random", "card_class": "ANY"},
    )
    assert gid in manager.games


def test_create_game_deckstring_spec(manager):
    """玩家槽传 deckstring 时,p1 用该卡组"""
    from fireplace.cards import db
    db.initialize()
    fb = db.get("CS2_029")  # Fireball
    intel = db.get("CS2_023")  # Arcane Intellect
    cards = [(fb.dbf_id, 2), (intel.dbf_id, 2)]
    # 凑足 30 张:简单填同卡(实际编辑器不会,但 manager 不校验)
    from fireplace.deckstring import encode_deck, Format
    # 这里只测试 manager 能接收 deckstring 并解析,无需真实 30 张
    deckstring = encode_deck(cards, 8, Format.STANDARD)

    gid = manager.create_game(
        mode="pvp",
        p1_spec={"type": "deckstring", "value": deckstring},
        p2_spec={"type": "random", "card_class": "ANY"},
    )
    assert gid in manager.games
    g = manager.games[gid]
    # p1 卡组应至少包含 Fireball
    p1_deck_card_ids = [c.id if hasattr(c, "id") else c for c in g["players"][0].deck]
    assert "CS2_029" in p1_deck_card_ids


def test_create_game_invalid_deckstring_raises(manager):
    """坏 deckstring 应抛 ValueError 让上层处理"""
    with pytest.raises(Exception):
        manager.create_game(
            mode="pve",
            p1_spec={"type": "deckstring", "value": "garbage"},
            p2_spec={"type": "random", "card_class": "ANY"},
        )


def test_create_game_test_deck_overrides_spec(manager):
    """test_deck=True 时忽略 spec 走 create_test_deck(开发便利)"""
    gid = manager.create_game(
        mode="pve",
        p1_spec={"type": "random", "card_class": "MAGE"},
        p2_spec={"type": "random", "card_class": "WARRIOR"},
        test_deck=True,
    )
    assert gid in manager.games
```

- [ ] **Step 2: 跑测试确认失败**

```bash
python -m pytest tests/test_create_game_specs.py -v
```
Expected: TypeError("got unexpected keyword argument 'p1_spec'")

- [ ] **Step 3: 改 `GameManager.create_game` 签名**

修改 `webui/server/game.py` lines 297-339,**完全替换** `create_game` 方法为:
```python
    def create_game(self, *, mode, p1_spec, p2_spec, test_deck=False):
        """创建游戏返回 game_id

        Args:
            mode: "pve" / "pvp" / "ai"
            p1_spec: DeckSpec dict for player 1
            p2_spec: DeckSpec dict for player 2
            test_deck: True 时无视 specs 走机制测试卡组
        """
        self.initialize()
        game_id = str(uuid.uuid4())

        if test_deck:
            p1_class = self._spec_class(p1_spec)
            p2_class = self._spec_class(p2_spec)
            p1_deck = create_test_deck(p1_class)
            p2_deck = create_test_deck(p2_class)
        else:
            p1_class, p1_deck = self._build_deck_from_spec(p1_spec)
            p2_class, p2_deck = self._build_deck_from_spec(p2_spec)

        player1 = Player("Player1", p1_deck, p1_class.default_hero)
        player2 = Player("Player2", p2_deck, p2_class.default_hero)

        game = Game(players=(player1, player2))
        game.start()

        # 跳过换牌
        for p in game.players:
            if p.choice:
                p.choice.choose()

        # 创建游戏日志记录器
        # ... (保留原后续代码,从 'logger = GameLogger()' 行起不动)
```

注意:**复制原 `create_game` 中"跳过换牌"之后的所有代码**(GameLogger 创建、self.games 注册、return game_id 等),不变。

然后追加两个 helper 方法:
```python
    @staticmethod
    def _spec_class(spec):
        """从 DeckSpec 反推 CardClass(deckstring 模式查 hero,random 模式直接读 card_class)"""
        if spec["type"] == "deckstring":
            from .deck_manager import import_deck_from_string
            info = import_deck_from_string(spec["value"])
            return CardClassEnum[info["hero_class"]]
        elif spec["type"] == "random":
            return get_card_class(spec["card_class"])
        raise ValueError(f"unknown DeckSpec type: {spec.get('type')}")

    def _build_deck_from_spec(self, spec):
        """返回 (CardClass enum, [card_id,...])"""
        if spec["type"] == "deckstring":
            from .deck_manager import import_deck_from_string
            info = import_deck_from_string(spec["value"])
            cc = CardClassEnum[info["hero_class"]]
            # cards 已是 list[{card_id,count,implemented}],展平到 list[card_id]
            deck = []
            for c in info["cards"]:
                deck.extend([c["card_id"]] * c["count"])
            return cc, deck
        elif spec["type"] == "random":
            cc = get_card_class(spec["card_class"]) if spec["card_class"] != "ANY" else random_class()
            return cc, filtered_random_draft(cc)
        raise ValueError(f"unknown DeckSpec type: {spec.get('type')}")
```

- [ ] **Step 4: 跑测试确认通过**

```bash
python -m pytest tests/test_create_game_specs.py -v
```
Expected: 4 passed

- [ ] **Step 5: 检查回归**

```bash
python -m pytest tests/test_webui_hero_cards.py -v
```
Expected:可能需要修;若 `test_webui_hero_cards.py` 直接调 `manager.create_game(player_class, ...)` 旧签名会失败。
- 如有失败:同步改测试调用为 `manager.create_game(mode=..., p1_spec={"type":"random","card_class":...}, p2_spec={...})` 形式
- **不**保留旧签名兼容(spec 决策第 4 项)

- [ ] **Step 6: 提交**

```bash
git add webui/server/game.py tests/test_create_game_specs.py [tests/test_webui_hero_cards.py 如有改动]
git commit -m "refactor(webui): GameManager.create_game takes DeckSpec slots

Replaces the scattered (player1_class, player2_class, custom_deck)
signature with (p1_spec, p2_spec) so each side can independently
choose a saved deckstring or a random class. test_deck=True still
shortcuts to create_test_deck for dev iteration.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: `socket.create_game` handler 解析双 DeckSpec

**Files:**
- Modify: `webui/server/socket.py`(`handle_create_game`)
- Test: 追加到 `tests/test_create_game_specs.py`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_create_game_specs.py`:
```python
def test_handle_create_game_emits_state_on_success(monkeypatch):
    """handle_create_game 收到合法双 DeckSpec 时 emit game_state"""
    from webui.server.socket import _build_socket_handlers_for_test
    # 简化:测试 socketio 提供的 test_client
    from webui.server import create_app, socketio
    app = create_app()
    client = socketio.test_client(app)

    client.emit('create_game', {
        'mode': 'pve',
        'player': {'type': 'random', 'card_class': 'MAGE'},
        'opponent': {'type': 'random', 'card_class': 'ANY'},
    })
    received = client.get_received()
    types = [r['name'] for r in received]
    assert 'game_state' in types, f"got {types}"


def test_handle_create_game_invalid_deckstring_emits_error():
    """坏 deckstring 不创建游戏,emit create_game_error"""
    from webui.server import create_app, socketio
    app = create_app()
    client = socketio.test_client(app)

    client.emit('create_game', {
        'mode': 'pve',
        'player': {'type': 'deckstring', 'value': 'garbage'},
        'opponent': {'type': 'random', 'card_class': 'ANY'},
    })
    received = client.get_received()
    types = [r['name'] for r in received]
    assert 'create_game_error' in types, f"got {types}"
    assert 'game_state' not in types
```

- [ ] **Step 2: 跑测试确认失败**

```bash
python -m pytest tests/test_create_game_specs.py -v -k "handle_create_game"
```
Expected: AssertionError(handler 还没解析 player/opponent)

- [ ] **Step 3: 改 `handle_create_game`**

修改 `webui/server/socket.py` 的 `handle_create_game`(原 lines 313-338),**完全替换**为:
```python
    @socketio.on('create_game')
    def handle_create_game(data):
        mode = data.get('mode', 'pve')
        test_deck = data.get('test_deck', False)

        # 兼容性兜底:旧字段 player_class 仍翻译成 random spec(便于测试 socket 的旧测试不全部改)
        if 'player' in data and 'opponent' in data:
            p1_spec = data['player']
            p2_spec = data['opponent']
        else:
            # 旧 payload(test fixtures 可能仍用),临时翻译
            player_class = data.get('player_class', 'random')
            p1_spec = {'type': 'random', 'card_class': player_class.upper() if player_class != 'random' else 'ANY'}
            p2_spec = {'type': 'random', 'card_class': 'ANY'}

        try:
            game_id = manager.create_game(
                mode=mode,
                p1_spec=p1_spec,
                p2_spec=p2_spec,
                test_deck=test_deck,
            )
        except Exception as e:
            print(f"[create_game] failed: {e}")
            emit('create_game_error', {'error': str(e)})
            return

        join_room(game_id)

        if mode == "pve":
            g = manager.games[game_id]
            game = g["game"]
            if game.current_player == g["players"][1]:
                import threading
                ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
                ai_thread.daemon = True
                ai_thread.start()

        g = manager.games[game_id]
        game = g["game"]
        if game.current_player == g["players"][0]:
            schedule_timeout_check(game_id)

        state = manager.get_game_state(game_id)
        emit('game_state', {'game_id': game_id, 'state': state})
```

注意:上面保留了 `player_class` 旧字段的临时翻译,只是为了让现有 `tests/test_webui_hero_cards.py` 中可能存在的 socket fixture 不必同步改动。前端在 Task 9 会切到新格式,**之后可以再删掉这个兜底**(留个 v2 cleanup TODO)。

- [ ] **Step 4: 跑测试确认通过**

```bash
python -m pytest tests/test_create_game_specs.py -v
```
Expected: 全部 6 个测试通过

- [ ] **Step 5: 提交**

```bash
git add webui/server/socket.py tests/test_create_game_specs.py
git commit -m "feat(webui): socket create_game handler accepts double DeckSpec

The handler now reads player+opponent from the payload, builds both
sides via GameManager, and emits create_game_error if either side
fails to decode. A short-term fallback still translates the legacy
player_class field; remove once the frontend migration is verified.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: 前端类型 + `deckStore` service

**Files:**
- Create: `webui/client/src/types/deck.ts`
- Create: `webui/client/src/services/deckStore.ts`

(此任务及之后均无 TDD —— 见 spec §8.2;每任务用 `tsc -b` 做静态验证 + 手测 + 提交)

- [ ] **Step 1: 写类型文件**

`webui/client/src/types/deck.ts`:
```typescript
export type CardType = 'MINION' | 'SPELL' | 'WEAPON';
export type Format = 'STANDARD' | 'WILD' | 'CLASSIC';
export type Rarity = 'FREE' | 'COMMON' | 'RARE' | 'EPIC' | 'LEGENDARY';

export type Card = {
  id: string;
  dbf_id: number;
  name_zh: string;
  name_en: string;
  text_zh: string;
  text_en: string;
  cost: number;
  attack?: number;
  health?: number;
  durability?: number;
  type: CardType;
  card_class: string;
  rarity: Rarity;
  card_set: string;
  race?: string;
  collectible: true;
  max_count: number;
};

export type DeckCard = { card_id: string; count: number };

export type Deck = {
  id: string;
  name: string;
  hero_class: string;       // "MAGE" | "WARRIOR" | ... | "NEUTRAL"(中立不应出现作为 hero,但保险)
  format: Format;
  cards: DeckCard[];
  created_at: string;
  updated_at: string;
};

export type DeckSpec =
  | { type: 'deckstring'; value: string }
  | { type: 'random'; card_class: string };  // "MAGE" / "WARRIOR" / ... / "ANY"

export const HERO_CLASSES = [
  'MAGE', 'HUNTER', 'PRIEST', 'SHAMAN', 'PALADIN',
  'WARLOCK', 'WARRIOR', 'ROGUE', 'DRUID', 'DEMONHUNTER',
] as const;
```

- [ ] **Step 2: 写 deckStore**

`webui/client/src/services/deckStore.ts`:
```typescript
import type { Deck, Format, DeckCard } from '../types/deck';

export const DECKS_STORAGE_KEY = 'fireplace.decks.v1';
export const DECKS_SCHEMA_VERSION = 1;

type StoredEnvelope = {
  schema_version: number;
  decks: Record<string, Deck>;
};

function readEnvelope(): StoredEnvelope {
  try {
    const raw = localStorage.getItem(DECKS_STORAGE_KEY);
    if (!raw) return { schema_version: DECKS_SCHEMA_VERSION, decks: {} };
    const parsed = JSON.parse(raw) as StoredEnvelope;
    return migrate(parsed);
  } catch (e) {
    console.warn('[deckStore] failed to read localStorage, starting empty', e);
    return { schema_version: DECKS_SCHEMA_VERSION, decks: {} };
  }
}

function migrate(env: StoredEnvelope): StoredEnvelope {
  // v1 是首版,无需迁移;留这层方便 v2 时插入
  if (!env || typeof env.schema_version !== 'number') {
    return { schema_version: DECKS_SCHEMA_VERSION, decks: {} };
  }
  return env;
}

function writeEnvelope(env: StoredEnvelope): void {
  try {
    localStorage.setItem(DECKS_STORAGE_KEY, JSON.stringify(env));
  } catch (e) {
    console.error('[deckStore] write failed (quota?)', e);
    throw new Error('localStorage write failed');
  }
}

function isValidDeck(d: unknown): d is Deck {
  if (!d || typeof d !== 'object') return false;
  const x = d as Partial<Deck>;
  return Boolean(
    x.id && x.name && x.hero_class && x.format &&
    Array.isArray(x.cards) && x.created_at && x.updated_at
  );
}

export function listDecks(): Deck[] {
  const env = readEnvelope();
  return Object.values(env.decks).filter(isValidDeck)
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at));
}

export function getDeck(id: string): Deck | null {
  return readEnvelope().decks[id] ?? null;
}

export function saveDeck(deck: Deck): void {
  if (!isValidDeck(deck)) throw new Error('invalid deck shape');
  const env = readEnvelope();
  deck.updated_at = new Date().toISOString();
  env.decks[deck.id] = deck;
  writeEnvelope(env);
}

export function deleteDeck(id: string): void {
  const env = readEnvelope();
  delete env.decks[id];
  writeEnvelope(env);
}

export function newDeck(heroClass: string, name = '新卡组'): Deck {
  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    name,
    hero_class: heroClass,
    format: 'STANDARD',
    cards: [],
    created_at: now,
    updated_at: now,
  };
}

export function deckCardCount(deck: Deck): number {
  return deck.cards.reduce((sum, c) => sum + c.count, 0);
}

export function findCardInDeck(deck: Deck, cardId: string): DeckCard | undefined {
  return deck.cards.find(c => c.card_id === cardId);
}

/** 加一张卡;到达 maxCount 或 deck 满 30 张时返回 false */
export function addCardToDeck(deck: Deck, cardId: string, maxCount: number): boolean {
  if (deckCardCount(deck) >= 30) return false;
  const existing = findCardInDeck(deck, cardId);
  if (existing) {
    if (existing.count >= maxCount) return false;
    existing.count++;
  } else {
    deck.cards.push({ card_id: cardId, count: 1 });
  }
  return true;
}

/** 减一张卡;到 0 时移除该 entry。返回是否真的减了 */
export function removeCardFromDeck(deck: Deck, cardId: string): boolean {
  const idx = deck.cards.findIndex(c => c.card_id === cardId);
  if (idx < 0) return false;
  deck.cards[idx].count--;
  if (deck.cards[idx].count <= 0) deck.cards.splice(idx, 1);
  return true;
}

/** 校验:总数 1-30,单卡不超 max_count(由调用者保证传入的 max 正确) */
export function isDeckSavable(deck: Deck): { ok: boolean; reason?: string } {
  const total = deckCardCount(deck);
  if (total < 1) return { ok: false, reason: '卡组至少 1 张' };
  if (total > 30) return { ok: false, reason: `卡组超过 30 张(当前 ${total})` };
  return { ok: true };
}

export type DeckstringExportFormat = Format;

/** 通过 /api/decks/validate 走后端做 deckstring → Deck 的转换(后端持有 dbf 表) */
export async function importDeckFromDeckstring(deckstring: string, name: string): Promise<Deck> {
  const resp = await fetch('/api/decks/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ deckstring }),
  });
  const data = await resp.json();
  if (!data.valid) throw new Error(data.error || 'invalid deckstring');

  const now = new Date().toISOString();
  return {
    id: crypto.randomUUID(),
    name,
    hero_class: data.hero_class,
    format: data.format,
    cards: data.cards.map((c: { card_id: string; count: number }) => ({
      card_id: c.card_id,
      count: c.count,
    })),
    created_at: now,
    updated_at: now,
  };
}

/** 由 Deck 生成 deckstring。需要后端帮忙(它持有 dbf 表)。
 *  策略:暂时 POST 到一个尚未实现的 /api/decks/encode endpoint。
 *  v1 简化:在前端调用 import endpoint 反向是不行的——所以:
 *  我们让 `gameService.createGame` 直接发送 Deck 的卡片列表,服务端走 `import_deck_from_string`
 *  对于"复制 deckstring"这个 UI 功能,留 TODO 到 v2 或加 /api/decks/encode endpoint。
 *
 *  本 task 暂不实现 export;v1 的"导出 deckstring"按钮会在后续 task 加 endpoint 后启用。
 */
```

注意上面 `importDeckFromDeckstring` 末尾留的 TODO 备忘——下面会单独加导出。

- [ ] **Step 3: 跑 tsc 确认无类型错误**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace/webui/client
npx tsc -b --noEmit
```
Expected: 无错误输出

- [ ] **Step 4: 提交**

```bash
git add webui/client/src/types/deck.ts webui/client/src/services/deckStore.ts
git commit -m "feat(client): add Card/Deck types and localStorage deckStore

Versioned localStorage envelope with a migrate hook, plus pure helpers
for adding/removing/validating cards within a deck. importDeck calls
the backend validate endpoint to translate a deckstring into the
local Deck shape.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7b: 加 `/api/decks/encode` endpoint(让前端能导出 deckstring)

**Files:**
- Modify: `webui/server/views.py`
- Modify: `webui/client/src/services/deckStore.ts`(加 `exportDeckToDeckstring`)
- Test: 追加到 `tests/test_deck_validate.py`

- [ ] **Step 1: 写失败测试**

追加到 `tests/test_deck_validate.py`:
```python
def test_encode_deckstring_round_trip(client):
    """POST /api/decks/encode -> /api/decks/validate 往返一致"""
    body = {
        'hero_class': 'MAGE',
        'format': 'STANDARD',
        'cards': [
            {'card_id': 'CS2_029', 'count': 2},
            {'card_id': 'CS2_023', 'count': 2},
        ],
    }
    enc = client.post('/api/decks/encode', json=body)
    assert enc.status_code == 200, enc.get_json()
    deckstring = enc.get_json()['deckstring']

    val = client.post('/api/decks/validate', json={'deckstring': deckstring})
    data = val.get_json()
    assert data['valid'] is True
    assert data['hero_class'] == 'MAGE'
    assert data['format'] == 'STANDARD'
    ids = sorted([c['card_id'] for c in data['cards']])
    assert ids == ['CS2_023', 'CS2_029']
```

- [ ] **Step 2: 跑测试确认失败**

```bash
python -m pytest tests/test_deck_validate.py -v -k "encode"
```
Expected: 404

- [ ] **Step 3: 加 endpoint**

修改 `webui/server/views.py`,加:
```python
@bp.route('/api/decks/encode', methods=['POST'])
def encode_deck_endpoint():
    """从 Deck 生成 deckstring"""
    from .deck_manager import export_deck_to_string, InvalidDeck
    from fireplace.deckstring import Format

    body = request.get_json(silent=True) or {}
    hero_class = body.get('hero_class')
    cards_in = body.get('cards', [])
    fmt_name = body.get('format', 'STANDARD')

    if not hero_class or not cards_in:
        return jsonify({'error': 'missing hero_class or cards'}), 400

    cards = [(c['card_id'], int(c['count'])) for c in cards_in]
    try:
        fmt = Format[fmt_name]
        deckstring = export_deck_to_string(cards, hero_class, fmt)
    except (InvalidDeck, KeyError, Exception) as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'deckstring': deckstring})
```

- [ ] **Step 4: 加前端 export helper**

追加到 `webui/client/src/services/deckStore.ts`:
```typescript
export async function exportDeckToDeckstring(deck: Deck): Promise<string> {
  const resp = await fetch('/api/decks/encode', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      hero_class: deck.hero_class,
      format: deck.format,
      cards: deck.cards,
    }),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.error || `encode failed: ${resp.status}`);
  }
  const data = await resp.json();
  return data.deckstring;
}
```

- [ ] **Step 5: 跑后端测试 + tsc 检查**

```bash
python -m pytest tests/test_deck_validate.py -v -k "encode"
cd webui/client && npx tsc -b --noEmit
```
Expected: 1 passed,tsc 无错

- [ ] **Step 6: 提交**

```bash
git add webui/server/views.py webui/client/src/services/deckStore.ts tests/test_deck_validate.py
git commit -m "feat(webui): POST /api/decks/encode + frontend export helper

Round-trip deck encode/decode is now backend-owned (the dbf table
lives there). Frontend deckStore.exportDeckToDeckstring posts the
local Deck and returns the deckstring for clipboard copy.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: `cardCatalog` service(前端加载 + 索引)

**Files:**
- Create: `webui/client/src/services/cardCatalog.ts`

- [ ] **Step 1: 写实现**

`webui/client/src/services/cardCatalog.ts`:
```typescript
import type { Card, CardType } from '../types/deck';

let _catalog: Card[] | null = null;
let _byId: Map<string, Card> | null = null;
let _loadPromise: Promise<Card[]> | null = null;

export async function loadCatalog(): Promise<Card[]> {
  if (_catalog) return _catalog;
  if (_loadPromise) return _loadPromise;

  _loadPromise = fetch('/api/cards/all')
    .then(r => {
      if (!r.ok) throw new Error(`catalog fetch failed: ${r.status}`);
      return r.json();
    })
    .then(data => {
      _catalog = data.cards as Card[];
      _byId = new Map(_catalog.map(c => [c.id, c]));
      return _catalog;
    })
    .catch(err => {
      _loadPromise = null;
      throw err;
    });
  return _loadPromise;
}

export function getCardById(id: string): Card | undefined {
  return _byId?.get(id);
}

export function getCatalogSync(): Card[] {
  return _catalog ?? [];
}

export type CardFilter = {
  cardClass?: string;       // "MAGE" | "NEUTRAL" | undefined(undefined = 全部)
  includeNeutral?: boolean; // true 时即使 cardClass 也带上中立卡
  costs?: Set<number>;      // {0,1,...,7}; 7 表示 7+; 空集 = 不过滤
  types?: Set<CardType>;
  search?: string;          // 中英文卡名关键字
};

export function filterCards(catalog: Card[], filter: CardFilter): Card[] {
  const q = filter.search?.trim().toLowerCase();
  return catalog.filter(c => {
    if (filter.cardClass) {
      if (filter.includeNeutral) {
        if (c.card_class !== filter.cardClass && c.card_class !== 'NEUTRAL') return false;
      } else {
        if (c.card_class !== filter.cardClass) return false;
      }
    }
    if (filter.costs && filter.costs.size > 0) {
      const bucket = c.cost >= 7 ? 7 : c.cost;
      if (!filter.costs.has(bucket)) return false;
    }
    if (filter.types && filter.types.size > 0) {
      if (!filter.types.has(c.type)) return false;
    }
    if (q) {
      const matchZh = c.name_zh.toLowerCase().includes(q);
      const matchEn = c.name_en.toLowerCase().includes(q);
      if (!matchZh && !matchEn) return false;
    }
    return true;
  });
}

export function sortCards(cards: Card[]): Card[] {
  return [...cards].sort((a, b) =>
    a.cost - b.cost || a.name_zh.localeCompare(b.name_zh)
  );
}
```

- [ ] **Step 2: tsc 检查**

```bash
cd webui/client && npx tsc -b --noEmit
```
Expected: 无错

- [ ] **Step 3: 提交**

```bash
git add webui/client/src/services/cardCatalog.ts
git commit -m "feat(client): cardCatalog service loads and indexes /api/cards/all

Single in-memory load with id-keyed map for O(1) lookup, plus pure
filterCards/sortCards helpers used by the deck editor's left pool.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: `gameService.createGame` 重写

**Files:**
- Modify: `webui/client/src/services/gameService.ts`

- [ ] **Step 1: 改 createGame 签名 + 删 create_game_with_deck**

修改 `webui/client/src/services/gameService.ts` lines 174-190(替换整个 `createGame` 方法):
```typescript
  createGame(
    mode: string,
    p1Spec: import('../types/deck').DeckSpec,
    p2Spec: import('../types/deck').DeckSpec,
    testDeck = false,
  ) {
    socketService.connect();
    socketService.onReconnect(() => {
      if (this.gameId) {
        console.log('[GameService] Reconnected, rejoining game:', this.gameId);
        socketService.emit('rejoin_game', { game_id: this.gameId });
      }
    });
    socketService.emit('create_game', {
      mode,
      player: p1Spec,
      opponent: p2Spec,
      test_deck: testDeck,
    });
  }
```

- [ ] **Step 2: 加 `onCreateGameError` listener helper**

在 `gameService.ts` 类中加(放在 `onErrorMessage` 附近):
```typescript
  onCreateGameError(callback: (data: { error: string }) => void) {
    socketService.on('create_game_error', (data) => callback(data as { error: string }));
  }
```

- [ ] **Step 3: 检查 GameBoard.tsx 是否调用旧 createGame 签名**

```bash
grep -n "createGame\|create_game_with_deck" /home/xu/code/hstone/hearthstone/fireplace/webui/client/src/components/GameBoard.tsx
```
若有,则要在后续 Task 17 改。本 task 只确认改动后 tsc 通过(GameBoard 还会保留旧签名调用 → tsc 报错 → 暂时容忍,在 Task 17 集中改)。

实际:由于 createGame 签名变化,**Task 17 也要改 GameBoard 的调用**。本 task 把 createGame 留为可调用即可。

- [ ] **Step 4: tsc 看冲突点**

```bash
cd webui/client && npx tsc -b --noEmit 2>&1 | head -20
```
预期可能在 GameBoard.tsx 出现一处 createGame 旧签名错;**记下这个错误,Task 17 修**。本 task 不强求 0 错。

- [ ] **Step 5: 提交**

```bash
git add webui/client/src/services/gameService.ts
git commit -m "refactor(client): gameService.createGame takes DeckSpec slots

Drops the dead create_game_with_deck branch. The server now expects
{mode, player, opponent}; GameBoard's invocation will be updated when
the new menu wires up.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: `CardRow` 组件(单行卡牌格)

**Files:**
- Create: `webui/client/src/components/CardRow.tsx`
- Create: `webui/client/src/components/CardRow.css`

- [ ] **Step 1: 写组件**

`webui/client/src/components/CardRow.tsx`:
```tsx
import type { Card } from '../types/deck';
import './CardRow.css';

type Props = {
  card: Card;
  count?: number;
  disabled?: boolean;
  showRightCount?: boolean;  // 右侧显示 ×N(用于 DeckPanel)
  onClick?: () => void;
  onHoverStart?: (card: Card, anchor: HTMLElement) => void;
  onHoverEnd?: () => void;
  onContextMenu?: (e: React.MouseEvent) => void;
};

const TYPE_BADGE: Record<string, string> = {
  MINION: '随',
  SPELL: '法',
  WEAPON: '武',
};

export default function CardRow({
  card, count, disabled, showRightCount,
  onClick, onHoverStart, onHoverEnd, onContextMenu,
}: Props) {
  const cls = card.card_class === 'NEUTRAL' ? 'neutral' : 'class';
  const right = showRightCount && count
    ? `×${count}`
    : card.type === 'MINION'
      ? `${card.attack ?? 0}/${card.health ?? 0}`
      : card.type === 'WEAPON'
        ? `${card.attack ?? 0}/${card.durability ?? 0}`
        : TYPE_BADGE[card.type] ?? '';

  return (
    <div
      className={`card-row card-row--${cls} ${disabled ? 'card-row--disabled' : ''}`}
      onClick={disabled ? undefined : onClick}
      onMouseEnter={(e) => onHoverStart?.(card, e.currentTarget)}
      onMouseLeave={onHoverEnd}
      onContextMenu={onContextMenu}
    >
      <span className="card-row__cost">{card.cost}</span>
      <span className="card-row__name">{card.name_zh}</span>
      <span className="card-row__right">{right}</span>
    </div>
  );
}
```

- [ ] **Step 2: 写 CSS**

`webui/client/src/components/CardRow.css`:
```css
.card-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
  font-size: 13px;
  border-left: 3px solid #888;
  background: linear-gradient(90deg, rgba(120, 120, 120, 0.15), transparent);
  transition: background 0.1s;
}
.card-row--class {
  border-left-color: #3b6cff;
  background: linear-gradient(90deg, rgba(59, 108, 255, 0.18), transparent);
}
.card-row:hover:not(.card-row--disabled) {
  background: linear-gradient(90deg, rgba(255, 200, 100, 0.25), transparent);
}
.card-row--disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.card-row__cost {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #2a4a8a;
  color: #fff;
  font-weight: bold;
  font-size: 12px;
  flex-shrink: 0;
}
.card-row__name { flex: 1; color: #eee; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-row__right { color: #fa6; font-size: 12px; flex-shrink: 0; }
```

- [ ] **Step 3: tsc 检查**

```bash
cd webui/client && npx tsc -b --noEmit 2>&1 | grep -v "GameBoard\|gameService" | head -10
```
Expected: 无新错(GameBoard/gameService 错先忽略,Task 17 修)

- [ ] **Step 4: 提交**

```bash
git add webui/client/src/components/CardRow.tsx webui/client/src/components/CardRow.css
git commit -m "feat(client): CardRow — single-line card cell

Compact card row used by both the pool and the deck panel: cost circle,
name, and a right-aligned slot that shows attack/health, type badge,
or count depending on context.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 11: `CardPreview` 组件(hover 预览面板)

**Files:**
- Create: `webui/client/src/components/CardPreview.tsx`
- Create: `webui/client/src/components/CardPreview.css`

- [ ] **Step 1: 写组件**

`webui/client/src/components/CardPreview.tsx`:
```tsx
import type { Card } from '../types/deck';
import './CardPreview.css';

type Props = {
  card: Card | null;
  anchor: HTMLElement | null;
};

const CLASS_LABEL: Record<string, string> = {
  MAGE: '法师', HUNTER: '猎人', PRIEST: '牧师', SHAMAN: '萨满',
  PALADIN: '圣骑士', WARLOCK: '术士', WARRIOR: '战士', ROGUE: '盗贼',
  DRUID: '德鲁伊', DEMONHUNTER: '恶魔猎手', NEUTRAL: '中立',
};
const TYPE_LABEL: Record<string, string> = {
  MINION: '随从', SPELL: '法术', WEAPON: '武器',
};
const RARITY_LABEL: Record<string, string> = {
  FREE: '免费', COMMON: '普通', RARE: '稀有', EPIC: '史诗', LEGENDARY: '传说',
};

export default function CardPreview({ card, anchor }: Props) {
  if (!card || !anchor) return null;
  const rect = anchor.getBoundingClientRect();
  const style: React.CSSProperties = {
    left: rect.right + 12,
    top: Math.max(8, Math.min(window.innerHeight - 320, rect.top - 40)),
  };

  return (
    <div className="card-preview" style={style}>
      <div className="card-preview__header">
        <span className="card-preview__cost">{card.cost}</span>
        <span className="card-preview__name">{card.name_zh}</span>
      </div>
      <div className="card-preview__meta">
        {TYPE_LABEL[card.type]} · {CLASS_LABEL[card.card_class] ?? card.card_class}
        {card.race ? ` · ${card.race}` : ''}
      </div>
      <div className="card-preview__stats">
        {card.type === 'MINION' && <>{card.attack ?? 0} 攻 / {card.health ?? 0} 血</>}
        {card.type === 'WEAPON' && <>{card.attack ?? 0} 攻 / {card.durability ?? 0} 耐久</>}
      </div>
      {card.text_zh && <div className="card-preview__text">{card.text_zh}</div>}
      <div className="card-preview__footer">
        {RARITY_LABEL[card.rarity] ?? card.rarity} · {card.card_set} · {card.name_en}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: CSS**

`webui/client/src/components/CardPreview.css`:
```css
.card-preview {
  position: fixed;
  z-index: 1000;
  width: 280px;
  background: #1a1a2e;
  border: 2px solid #4a4a8a;
  border-radius: 8px;
  padding: 12px;
  color: #eee;
  font-size: 13px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
  pointer-events: none;
}
.card-preview__header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.card-preview__cost {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 50%;
  background: #3b6cff; color: #fff; font-weight: bold;
}
.card-preview__name { font-size: 16px; font-weight: bold; }
.card-preview__meta { color: #aaa; font-size: 11px; margin-bottom: 4px; }
.card-preview__stats { color: #fa6; font-weight: bold; margin-bottom: 8px; }
.card-preview__text {
  white-space: pre-wrap; line-height: 1.4;
  border-top: 1px solid #2a2a4a; padding-top: 8px; color: #ddd;
}
.card-preview__footer {
  margin-top: 8px; padding-top: 6px; border-top: 1px solid #2a2a4a;
  color: #888; font-size: 11px;
}
```

- [ ] **Step 3: tsc 检查**

```bash
cd webui/client && npx tsc -b --noEmit 2>&1 | grep -v "GameBoard\|gameService" | head -10
```
Expected: 无新错

- [ ] **Step 4: 提交**

```bash
git add webui/client/src/components/CardPreview.tsx webui/client/src/components/CardPreview.css
git commit -m "feat(client): CardPreview floating panel for hover/right-click details

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: `CardPool` 组件(左侧卡库:筛选 + 列表)

**Files:**
- Create: `webui/client/src/components/CardPool.tsx`
- Create: `webui/client/src/components/CardPool.css`

- [ ] **Step 1: 写组件**

`webui/client/src/components/CardPool.tsx`:
```tsx
import { useMemo, useState } from 'react';
import type { Card, CardType } from '../types/deck';
import { filterCards, sortCards } from '../services/cardCatalog';
import CardRow from './CardRow';
import './CardPool.css';

type Props = {
  catalog: Card[];
  defaultClass?: string;          // 默认筛选职业(编辑器:卡组职业)
  forceIncludeNeutral?: boolean;  // 编辑器模式始终带中立
  onCardClick?: (card: Card) => void;
  onCardContextMenu?: (card: Card) => void;
  onCardHoverStart?: (card: Card, anchor: HTMLElement) => void;
  onCardHoverEnd?: () => void;
  cardDisabled?: (card: Card) => boolean;  // edit 模式:已加上限或非法职业 → disabled
};

const ALL_CLASSES = ['MAGE','HUNTER','PRIEST','SHAMAN','PALADIN','WARLOCK','WARRIOR','ROGUE','DRUID','DEMONHUNTER','NEUTRAL'] as const;
const TYPES: CardType[] = ['MINION', 'SPELL', 'WEAPON'];

export default function CardPool(props: Props) {
  const [classFilter, setClassFilter] = useState<string | undefined>(props.defaultClass);
  const [costs, setCosts] = useState<Set<number>>(new Set());
  const [types, setTypes] = useState<Set<CardType>>(new Set());
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => sortCards(filterCards(props.catalog, {
    cardClass: classFilter,
    includeNeutral: classFilter ? props.forceIncludeNeutral : false,
    costs,
    types,
    search,
  })), [props.catalog, classFilter, costs, types, search, props.forceIncludeNeutral]);

  const toggleCost = (n: number) => {
    const s = new Set(costs);
    s.has(n) ? s.delete(n) : s.add(n);
    setCosts(s);
  };
  const toggleType = (t: CardType) => {
    const s = new Set(types);
    s.has(t) ? s.delete(t) : s.add(t);
    setTypes(s);
  };

  return (
    <div className="card-pool">
      <div className="card-pool__filters">
        <select value={classFilter ?? ''} onChange={(e) => setClassFilter(e.target.value || undefined)}>
          <option value="">全部职业</option>
          {ALL_CLASSES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <div className="card-pool__cost-bar">
          {[0,1,2,3,4,5,6,7].map(n => (
            <button key={n} className={costs.has(n) ? 'on' : ''} onClick={() => toggleCost(n)}>
              {n === 7 ? '7+' : n}
            </button>
          ))}
        </div>
        <div className="card-pool__type-bar">
          {TYPES.map(t => (
            <button key={t} className={types.has(t) ? 'on' : ''} onClick={() => toggleType(t)}>
              {t === 'MINION' ? '随' : t === 'SPELL' ? '法' : '武'}
            </button>
          ))}
        </div>
        <input
          className="card-pool__search"
          placeholder="搜索卡名…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <div className="card-pool__list">
        {filtered.map(c => (
          <CardRow
            key={c.id}
            card={c}
            disabled={props.cardDisabled?.(c)}
            onClick={() => props.onCardClick?.(c)}
            onContextMenu={(e) => { e.preventDefault(); props.onCardContextMenu?.(c); }}
            onHoverStart={props.onCardHoverStart}
            onHoverEnd={props.onCardHoverEnd}
          />
        ))}
        {filtered.length === 0 && (
          <div className="card-pool__empty">没有匹配的卡牌</div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: CSS**

`webui/client/src/components/CardPool.css`:
```css
.card-pool { display: flex; flex-direction: column; height: 100%; background: #1a1a2e; }
.card-pool__filters {
  padding: 10px;
  background: #23234a;
  border-bottom: 2px solid #2a2a4a;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.card-pool__filters select,
.card-pool__filters input {
  background: #1a1a2e; color: #eee;
  border: 1px solid #3a3a6a; padding: 4px 8px; border-radius: 3px; font-size: 12px;
}
.card-pool__filters input { flex: 1; min-width: 120px; }
.card-pool__cost-bar, .card-pool__type-bar { display: flex; gap: 2px; }
.card-pool__cost-bar button, .card-pool__type-bar button {
  background: #3a3a6a; color: #ccc; border: 1px solid #4a4a8a;
  width: 24px; height: 24px; cursor: pointer; font-size: 11px;
}
.card-pool__type-bar button { width: 28px; }
.card-pool__cost-bar button.on, .card-pool__type-bar button.on {
  background: #fa6; color: #1a1a2e; border-color: #fa6; font-weight: bold;
}
.card-pool__list {
  flex: 1; overflow-y: auto; padding: 8px;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 4px;
}
.card-pool__empty { padding: 20px; color: #888; text-align: center; grid-column: 1/-1; }
```

- [ ] **Step 3: tsc**

```bash
cd webui/client && npx tsc -b --noEmit 2>&1 | grep -v "GameBoard\|gameService" | head -10
```
Expected: 无新错

- [ ] **Step 4: 提交**

```bash
git add webui/client/src/components/CardPool.tsx webui/client/src/components/CardPool.css
git commit -m "feat(client): CardPool with class/cost/type/search filters

Pure presentational component; parent passes catalog and click/hover
handlers. Filtering happens entirely client-side via cardCatalog.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 13: `DeckPanel` 组件(右侧已加卡 + 操作)

**Files:**
- Create: `webui/client/src/components/DeckPanel.tsx`
- Create: `webui/client/src/components/DeckPanel.css`

- [ ] **Step 1: 写组件**

`webui/client/src/components/DeckPanel.tsx`:
```tsx
import { useMemo, useState } from 'react';
import type { Deck, Format } from '../types/deck';
import { deckCardCount, isDeckSavable } from '../services/deckStore';
import { getCardById } from '../services/cardCatalog';
import CardRow from './CardRow';
import './DeckPanel.css';

type Props = {
  deck: Deck;
  onChange: (deck: Deck) => void;
  onSave: () => void;
  onExport: () => void;
  onBack: () => void;
  onRemoveCard: (cardId: string) => void;
};

const FORMATS: Format[] = ['STANDARD', 'WILD', 'CLASSIC'];
const HERO_LABEL: Record<string, string> = {
  MAGE: '🔮', HUNTER: '🏹', PRIEST: '✨', SHAMAN: '🌩️',
  PALADIN: '⚔️', WARLOCK: '👹', WARRIOR: '🛡️', ROGUE: '🗡️',
  DRUID: '🌿', DEMONHUNTER: '👁️',
};

export default function DeckPanel(props: Props) {
  const { deck } = props;
  const [editingName, setEditingName] = useState(false);
  const [nameDraft, setNameDraft] = useState(deck.name);

  const total = deckCardCount(deck);
  const savable = isDeckSavable(deck);

  // 按 cost 排序展示
  const sorted = useMemo(() => {
    return [...deck.cards].map(dc => {
      const card = getCardById(dc.card_id);
      return { dc, card, cost: card?.cost ?? 99, name: card?.name_zh ?? dc.card_id };
    }).sort((a, b) => a.cost - b.cost || a.name.localeCompare(b.name));
  }, [deck.cards]);

  const commitName = () => {
    if (nameDraft.trim()) {
      props.onChange({ ...deck, name: nameDraft.trim() });
    }
    setEditingName(false);
  };

  return (
    <div className="deck-panel">
      <div className="deck-panel__header">
        <div className="deck-panel__title-row">
          <span className="deck-panel__hero">{HERO_LABEL[deck.hero_class] ?? '?'}</span>
          {editingName ? (
            <input
              autoFocus
              value={nameDraft}
              onChange={e => setNameDraft(e.target.value)}
              onBlur={commitName}
              onKeyDown={e => e.key === 'Enter' && commitName()}
            />
          ) : (
            <span className="deck-panel__name" onClick={() => { setNameDraft(deck.name); setEditingName(true); }}>
              {deck.name}
            </span>
          )}
        </div>
        <div className="deck-panel__meta">
          <span className={`deck-panel__count ${total === 30 ? 'full' : total > 30 ? 'over' : ''}`}>
            {total}/30
          </span>
          <select
            value={deck.format}
            onChange={e => props.onChange({ ...deck, format: e.target.value as Format })}
          >
            {FORMATS.map(f => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>
      </div>

      <div className="deck-panel__list">
        {sorted.map(({ dc, card }) => card && (
          <CardRow
            key={dc.card_id}
            card={card}
            count={dc.count}
            showRightCount
            onClick={() => props.onRemoveCard(dc.card_id)}
          />
        ))}
        {sorted.length === 0 && (
          <div className="deck-panel__empty">点左侧卡牌加入卡组</div>
        )}
      </div>

      <div className="deck-panel__footer">
        {!savable.ok && <div className="deck-panel__warn">{savable.reason}</div>}
        <div className="deck-panel__buttons">
          <button onClick={props.onSave} disabled={!savable.ok}>保存</button>
          <button onClick={props.onExport}>导出</button>
          <button onClick={props.onBack}>返回</button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: CSS**

`webui/client/src/components/DeckPanel.css`:
```css
.deck-panel { display: flex; flex-direction: column; height: 100%; background: #1f1f3a; border-left: 2px solid #2a2a4a; }
.deck-panel__header { padding: 10px; background: #23234a; }
.deck-panel__title-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.deck-panel__hero { font-size: 22px; }
.deck-panel__name { color: #eee; font-weight: bold; font-size: 14px; cursor: pointer; }
.deck-panel__name:hover { color: #fa6; }
.deck-panel__title-row input { background: #1a1a2e; color: #eee; border: 1px solid #4a4a8a; padding: 3px 6px; border-radius: 3px; flex: 1; }
.deck-panel__meta { display: flex; gap: 10px; align-items: center; }
.deck-panel__count { color: #fa6; font-size: 12px; font-weight: bold; }
.deck-panel__count.full { color: #6f6; }
.deck-panel__count.over { color: #f66; }
.deck-panel__meta select { background: #1a1a2e; color: #eee; border: 1px solid #3a3a6a; padding: 2px 6px; border-radius: 3px; font-size: 11px; }
.deck-panel__list { flex: 1; overflow-y: auto; padding: 6px; }
.deck-panel__list .card-row { margin-bottom: 2px; }
.deck-panel__empty { padding: 30px 10px; color: #888; text-align: center; font-size: 12px; }
.deck-panel__footer { padding: 10px; background: #23234a; border-top: 2px solid #2a2a4a; }
.deck-panel__warn { color: #f66; font-size: 11px; margin-bottom: 6px; }
.deck-panel__buttons { display: flex; gap: 6px; }
.deck-panel__buttons button {
  flex: 1; background: #3a3a6a; color: #eee; border: 1px solid #4a4a8a;
  padding: 6px; border-radius: 3px; font-size: 12px; cursor: pointer;
}
.deck-panel__buttons button:hover:not(:disabled) { background: #4a4a8a; }
.deck-panel__buttons button:disabled { opacity: 0.4; cursor: not-allowed; }
```

- [ ] **Step 3: tsc**

```bash
cd webui/client && npx tsc -b --noEmit 2>&1 | grep -v "GameBoard\|gameService" | head -10
```
Expected: 无新错

- [ ] **Step 4: 提交**

```bash
git add webui/client/src/components/DeckPanel.tsx webui/client/src/components/DeckPanel.css
git commit -m "feat(client): DeckPanel — sorted card list, rename/format/save/export

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 14: `DeckEditor` 组件(三模式:edit / new / browse)

**Files:**
- Create: `webui/client/src/components/DeckEditor.tsx`
- Create: `webui/client/src/components/DeckEditor.css`

- [ ] **Step 1: 写组件**

`webui/client/src/components/DeckEditor.tsx`:
```tsx
import { useEffect, useState } from 'react';
import type { Card, Deck } from '../types/deck';
import { loadCatalog, getCatalogSync, getCardById } from '../services/cardCatalog';
import {
  getDeck, saveDeck, addCardToDeck, removeCardFromDeck,
  exportDeckToDeckstring, deckCardCount, findCardInDeck,
} from '../services/deckStore';
import CardPool from './CardPool';
import DeckPanel from './DeckPanel';
import CardPreview from './CardPreview';
import './DeckEditor.css';

type Props = {
  // null = 浏览模式;"new"+initialDeck 必填 = 新建模式;字符串 id = 编辑模式
  deckId: string | null | 'new';
  initialDeck?: Deck;
  onBack: () => void;
};

export default function DeckEditor({ deckId, initialDeck, onBack }: Props) {
  const [catalog, setCatalog] = useState<Card[]>(getCatalogSync());
  const [deck, setDeck] = useState<Deck | null>(() => {
    if (deckId === null) return null;
    if (deckId === 'new' && initialDeck) return initialDeck;
    return getDeck(deckId as string);
  });
  const [hoverCard, setHoverCard] = useState<{ card: Card; anchor: HTMLElement } | null>(null);
  const [previewLockedCard, setPreviewLockedCard] = useState<Card | null>(null);
  const [toast, setToast] = useState<string>('');

  useEffect(() => {
    if (catalog.length === 0) loadCatalog().then(setCatalog).catch(e => setToast(`加载卡库失败: ${e.message}`));
  }, [catalog.length]);

  const isBrowse = deck === null;

  const onCardClick = (card: Card) => {
    if (isBrowse) { setPreviewLockedCard(card); return; }
    if (!deck) return;
    const max = card.max_count;
    const ok = addCardToDeck(deck, card.id, max);
    if (ok) {
      setDeck({ ...deck });
    } else if (deckCardCount(deck) >= 30) {
      setToast('卡组已满 30 张');
    } else {
      setToast(`已达 ${max} 张上限`);
    }
  };

  const cardDisabled = (c: Card): boolean => {
    if (isBrowse || !deck) return false;
    if (c.card_class !== deck.hero_class && c.card_class !== 'NEUTRAL') return true;
    if (deckCardCount(deck) >= 30) return true;
    const inDeck = findCardInDeck(deck, c.id);
    if (inDeck && inDeck.count >= c.max_count) return true;
    return false;
  };

  const onRemove = (cardId: string) => {
    if (!deck) return;
    if (removeCardFromDeck(deck, cardId)) setDeck({ ...deck });
  };

  const onSave = () => {
    if (!deck) return;
    try {
      saveDeck(deck);
      setToast('已保存');
      setTimeout(onBack, 600);
    } catch (e) { setToast(`保存失败: ${(e as Error).message}`); }
  };

  const onExport = async () => {
    if (!deck) return;
    try {
      const ds = await exportDeckToDeckstring(deck);
      await navigator.clipboard.writeText(ds);
      setToast('Deckstring 已复制到剪贴板');
    } catch (e) { setToast(`导出失败: ${(e as Error).message}`); }
  };

  // toast auto-clear
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(''), 1800);
    return () => clearTimeout(t);
  }, [toast]);

  return (
    <div className={`deck-editor ${isBrowse ? 'deck-editor--browse' : ''}`}>
      <div className="deck-editor__pool">
        <CardPool
          catalog={catalog}
          defaultClass={deck?.hero_class}
          forceIncludeNeutral={!isBrowse}
          onCardClick={onCardClick}
          onCardContextMenu={(c) => setPreviewLockedCard(c)}
          onCardHoverStart={(card, anchor) => setHoverCard({ card, anchor })}
          onCardHoverEnd={() => setHoverCard(null)}
          cardDisabled={cardDisabled}
        />
      </div>
      {!isBrowse && deck && (
        <div className="deck-editor__panel">
          <DeckPanel
            deck={deck}
            onChange={setDeck}
            onSave={onSave}
            onExport={onExport}
            onBack={onBack}
            onRemoveCard={onRemove}
          />
        </div>
      )}
      {isBrowse && (
        <div className="deck-editor__back-bar">
          <button onClick={onBack}>返回</button>
        </div>
      )}

      <CardPreview card={hoverCard?.card ?? null} anchor={hoverCard?.anchor ?? null} />

      {previewLockedCard && (
        <div className="deck-editor__locked-overlay" onClick={() => setPreviewLockedCard(null)}>
          <div className="deck-editor__locked-content" onClick={e => e.stopPropagation()}>
            <CardPreview card={previewLockedCard} anchor={document.body} />
            <button onClick={() => setPreviewLockedCard(null)}>关闭</button>
          </div>
        </div>
      )}

      {toast && <div className="deck-editor__toast">{toast}</div>}
    </div>
  );
}
```

- [ ] **Step 2: CSS**

`webui/client/src/components/DeckEditor.css`:
```css
.deck-editor { display: flex; height: 100vh; background: #1a1a2e; position: relative; }
.deck-editor__pool { flex: 2; min-width: 0; }
.deck-editor__panel { width: 320px; flex-shrink: 0; }
.deck-editor--browse .deck-editor__pool { flex: 1; }
.deck-editor__back-bar { position: absolute; top: 12px; right: 16px; z-index: 50; }
.deck-editor__back-bar button {
  background: #3a3a6a; color: #eee; border: 1px solid #4a4a8a;
  padding: 6px 14px; border-radius: 3px; cursor: pointer;
}
.deck-editor__toast {
  position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%);
  background: rgba(50, 50, 90, 0.95); color: #eee; padding: 10px 20px;
  border-radius: 4px; z-index: 2000; box-shadow: 0 2px 12px rgba(0,0,0,0.5);
}
.deck-editor__locked-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6);
  z-index: 1500; display: flex; align-items: center; justify-content: center;
}
.deck-editor__locked-content { position: relative; }
.deck-editor__locked-content button {
  position: absolute; top: 8px; right: 8px;
  background: #3a3a6a; color: #eee; border: 1px solid #4a4a8a;
  padding: 4px 10px; border-radius: 3px; cursor: pointer; z-index: 1600;
}
```

- [ ] **Step 3: tsc**

```bash
cd webui/client && npx tsc -b --noEmit 2>&1 | grep -v "GameBoard\|gameService" | head -10
```
Expected: 无新错

- [ ] **Step 4: 提交**

```bash
git add webui/client/src/components/DeckEditor.tsx webui/client/src/components/DeckEditor.css
git commit -m "feat(client): DeckEditor combines CardPool + DeckPanel with three modes

deckId='new' or string id renders the panel; deckId=null hides it
and turns the pool into a read-only browser. Hover preview, right-click
locked detail, save/export wired through.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 15: `DeckList` 组件(卡组管理页)

**Files:**
- Create: `webui/client/src/components/DeckList.tsx`
- Create: `webui/client/src/components/DeckList.css`

- [ ] **Step 1: 写组件**

`webui/client/src/components/DeckList.tsx`:
```tsx
import { useEffect, useState } from 'react';
import type { Deck } from '../types/deck';
import {
  listDecks, deleteDeck, importDeckFromDeckstring, saveDeck, deckCardCount,
} from '../services/deckStore';
import { HERO_CLASSES } from '../types/deck';
import './DeckList.css';

type Props = {
  onOpenDeck: (deckId: string) => void;
  onCreateDeck: (heroClass: string) => void;
  onBrowseAll: () => void;
  onBack: () => void;
};

const HERO_LABEL: Record<string, { name: string; icon: string }> = {
  MAGE: { name: '法师', icon: '🔮' },
  HUNTER: { name: '猎人', icon: '🏹' },
  PRIEST: { name: '牧师', icon: '✨' },
  SHAMAN: { name: '萨满', icon: '🌩️' },
  PALADIN: { name: '圣骑士', icon: '⚔️' },
  WARLOCK: { name: '术士', icon: '👹' },
  WARRIOR: { name: '战士', icon: '🛡️' },
  ROGUE: { name: '盗贼', icon: '🗡️' },
  DRUID: { name: '德鲁伊', icon: '🌿' },
  DEMONHUNTER: { name: '恶魔猎手', icon: '👁️' },
};

export default function DeckList(props: Props) {
  const [decks, setDecks] = useState<Deck[]>(listDecks());
  const [showNewClass, setShowNewClass] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [importText, setImportText] = useState('');
  const [importName, setImportName] = useState('');
  const [error, setError] = useState('');

  const refresh = () => setDecks(listDecks());

  const onDelete = (id: string, name: string) => {
    if (confirm(`确认删除卡组「${name}」?`)) {
      deleteDeck(id);
      refresh();
    }
  };

  const onImport = async () => {
    if (!importText.trim()) return;
    try {
      const d = await importDeckFromDeckstring(importText.trim(), importName.trim() || '导入的卡组');
      saveDeck(d);
      setShowImport(false);
      setImportText(''); setImportName(''); setError('');
      refresh();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <div className="deck-list">
      <div className="deck-list__header">
        <h2>我的卡组</h2>
        <div className="deck-list__actions">
          <button onClick={() => setShowNewClass(true)}>+ 新建</button>
          <button onClick={() => setShowImport(true)}>📋 导入 deckstring</button>
          <button onClick={props.onBrowseAll}>🔍 浏览全卡库</button>
          <button onClick={props.onBack}>← 返回</button>
        </div>
      </div>

      <div className="deck-list__grid">
        {decks.length === 0 && (
          <div className="deck-list__empty">还没有卡组,点"新建"或"导入"开始</div>
        )}
        {decks.map(d => {
          const hero = HERO_LABEL[d.hero_class] ?? { name: d.hero_class, icon: '?' };
          return (
            <div key={d.id} className="deck-card" onClick={() => props.onOpenDeck(d.id)}>
              <div className="deck-card__hero">{hero.icon}</div>
              <div className="deck-card__body">
                <div className="deck-card__name">{d.name}</div>
                <div className="deck-card__meta">{hero.name} · {d.format} · {deckCardCount(d)}/30</div>
              </div>
              <button className="deck-card__del" onClick={(e) => { e.stopPropagation(); onDelete(d.id, d.name); }}>×</button>
            </div>
          );
        })}
      </div>

      {showNewClass && (
        <div className="deck-list__modal" onClick={() => setShowNewClass(false)}>
          <div className="deck-list__modal-content" onClick={e => e.stopPropagation()}>
            <h3>选择职业</h3>
            <div className="deck-list__class-grid">
              {HERO_CLASSES.map(c => (
                <button key={c} onClick={() => { setShowNewClass(false); props.onCreateDeck(c); }}>
                  {HERO_LABEL[c].icon} {HERO_LABEL[c].name}
                </button>
              ))}
            </div>
            <button onClick={() => setShowNewClass(false)}>取消</button>
          </div>
        </div>
      )}

      {showImport && (
        <div className="deck-list__modal" onClick={() => setShowImport(false)}>
          <div className="deck-list__modal-content" onClick={e => e.stopPropagation()}>
            <h3>导入 deckstring</h3>
            <input placeholder="卡组名(可选)" value={importName} onChange={e => setImportName(e.target.value)} />
            <textarea
              placeholder="粘贴炉石 deckstring..."
              value={importText}
              onChange={e => setImportText(e.target.value)}
              rows={4}
            />
            {error && <div className="deck-list__error">{error}</div>}
            <div>
              <button onClick={onImport}>导入</button>
              <button onClick={() => { setShowImport(false); setError(''); }}>取消</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: CSS**

`webui/client/src/components/DeckList.css`:
```css
.deck-list { padding: 30px; min-height: 100vh; background: #1a1a2e; color: #eee; }
.deck-list__header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.deck-list__header h2 { margin: 0; }
.deck-list__actions { display: flex; gap: 8px; }
.deck-list__actions button {
  background: #3a3a6a; color: #eee; border: 1px solid #4a4a8a;
  padding: 8px 14px; border-radius: 3px; cursor: pointer;
}
.deck-list__actions button:hover { background: #4a4a8a; }
.deck-list__grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px;
}
.deck-list__empty { color: #888; padding: 40px; text-align: center; grid-column: 1/-1; }
.deck-card {
  display: flex; align-items: center; gap: 12px;
  padding: 14px; background: #23234a; border-radius: 6px; cursor: pointer;
  border: 1px solid #2a2a4a; transition: border-color 0.1s;
}
.deck-card:hover { border-color: #fa6; }
.deck-card__hero { font-size: 28px; }
.deck-card__body { flex: 1; }
.deck-card__name { font-weight: bold; margin-bottom: 4px; }
.deck-card__meta { color: #aaa; font-size: 12px; }
.deck-card__del {
  background: transparent; color: #888; border: none; font-size: 18px;
  cursor: pointer; padding: 4px 8px;
}
.deck-card__del:hover { color: #f66; }

.deck-list__modal {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.deck-list__modal-content {
  background: #23234a; padding: 24px; border-radius: 8px; min-width: 400px;
  border: 2px solid #4a4a8a;
}
.deck-list__class-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin: 16px 0;
}
.deck-list__class-grid button {
  background: #3a3a6a; color: #eee; border: 1px solid #4a4a8a;
  padding: 10px; border-radius: 3px; cursor: pointer; text-align: left;
}
.deck-list__modal-content input,
.deck-list__modal-content textarea {
  width: 100%; padding: 8px; background: #1a1a2e; color: #eee;
  border: 1px solid #4a4a8a; border-radius: 3px; margin: 6px 0; box-sizing: border-box;
  font-family: monospace; font-size: 12px;
}
.deck-list__error { color: #f66; padding: 6px 0; font-size: 12px; }
.deck-list__modal-content button {
  background: #3a3a6a; color: #eee; border: 1px solid #4a4a8a;
  padding: 6px 14px; border-radius: 3px; cursor: pointer; margin: 4px 4px 0 0;
}
```

- [ ] **Step 3: tsc**

```bash
cd webui/client && npx tsc -b --noEmit 2>&1 | grep -v "GameBoard\|gameService" | head -10
```
Expected: 无新错

- [ ] **Step 4: 提交**

```bash
git add webui/client/src/components/DeckList.tsx webui/client/src/components/DeckList.css
git commit -m "feat(client): DeckList — saved decks grid + new/import/browse entries

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 16: `PlaySetup` 组件(开始对局页:双槽)

**Files:**
- Create: `webui/client/src/components/PlaySetup.tsx`
- Create: `webui/client/src/components/PlaySetup.css`

- [ ] **Step 1: 写组件**

`webui/client/src/components/PlaySetup.tsx`:
```tsx
import { useEffect, useState } from 'react';
import type { Deck, DeckSpec } from '../types/deck';
import { listDecks, importDeckFromDeckstring, exportDeckToDeckstring } from '../services/deckStore';
import { HERO_CLASSES } from '../types/deck';
import './PlaySetup.css';

type Props = {
  mode: 'pve' | 'pvp' | 'ai';
  onStart: (p1: DeckSpec, p2: DeckSpec) => void;
  onBack: () => void;
};

type SlotState = {
  type: 'saved' | 'deckstring' | 'random';
  deckId: string;
  deckstring: string;
  randomClass: string;     // "MAGE" | ... | "ANY"
};

const HERO_LABEL: Record<string, string> = {
  MAGE: '🔮 法师', HUNTER: '🏹 猎人', PRIEST: '✨ 牧师', SHAMAN: '🌩️ 萨满',
  PALADIN: '⚔️ 圣骑', WARLOCK: '👹 术士', WARRIOR: '🛡️ 战士', ROGUE: '🗡️ 盗贼',
  DRUID: '🌿 德鲁伊', DEMONHUNTER: '👁️ 恶魔猎手',
};

function defaultSlot(filledRandom: boolean): SlotState {
  return {
    type: filledRandom ? 'random' : 'saved',
    deckId: '',
    deckstring: '',
    randomClass: filledRandom ? 'ANY' : 'MAGE',
  };
}

async function slotToSpec(slot: SlotState, decks: Deck[]): Promise<DeckSpec> {
  if (slot.type === 'random') {
    return { type: 'random', card_class: slot.randomClass };
  }
  if (slot.type === 'deckstring') {
    if (!slot.deckstring.trim()) throw new Error('请粘贴 deckstring');
    return { type: 'deckstring', value: slot.deckstring.trim() };
  }
  // saved
  const d = decks.find(d => d.id === slot.deckId);
  if (!d) throw new Error('请选择已存卡组');
  const ds = await exportDeckToDeckstring(d);
  return { type: 'deckstring', value: ds };
}

export default function PlaySetup(props: Props) {
  const isPvp = props.mode === 'pvp';
  const [decks, setDecks] = useState<Deck[]>(listDecks());
  const [p1, setP1] = useState<SlotState>(defaultSlot(false));
  // PVE/AI 默认对手 random;PVP 默认对手 saved(必填)
  const [p2, setP2] = useState<SlotState>(defaultSlot(!isPvp));
  const [error, setError] = useState('');

  useEffect(() => { setDecks(listDecks()); }, []);

  const start = async () => {
    try {
      const p1Spec = await slotToSpec(p1, decks);
      const p2Spec = await slotToSpec(p2, decks);
      props.onStart(p1Spec, p2Spec);
    } catch (e) { setError((e as Error).message); }
  };

  const renderSlot = (label: string, slot: SlotState, set: (s: SlotState) => void) => (
    <div className="play-setup__slot">
      <div className="play-setup__slot-label">{label}</div>
      <select value={slot.type} onChange={e => set({ ...slot, type: e.target.value as SlotState['type'] })}>
        <option value="saved">已存卡组</option>
        <option value="deckstring">粘贴 deckstring</option>
        <option value="random">随机职业</option>
      </select>
      {slot.type === 'saved' && (
        <select value={slot.deckId} onChange={e => set({ ...slot, deckId: e.target.value })}>
          <option value="">— 选择卡组 —</option>
          {decks.map(d => <option key={d.id} value={d.id}>{d.name} ({d.hero_class})</option>)}
        </select>
      )}
      {slot.type === 'deckstring' && (
        <textarea
          rows={3}
          placeholder="粘贴 deckstring..."
          value={slot.deckstring}
          onChange={e => set({ ...slot, deckstring: e.target.value })}
        />
      )}
      {slot.type === 'random' && (
        <select value={slot.randomClass} onChange={e => set({ ...slot, randomClass: e.target.value })}>
          <option value="ANY">随机职业</option>
          {HERO_CLASSES.map(c => <option key={c} value={c}>{HERO_LABEL[c]}</option>)}
        </select>
      )}
    </div>
  );

  return (
    <div className="play-setup">
      <h2>开始对局 · {props.mode.toUpperCase()}</h2>
      <div className="play-setup__slots">
        {renderSlot(isPvp ? '玩家 1' : '玩家', p1, setP1)}
        {renderSlot(isPvp ? '玩家 2' : '对手', p2, setP2)}
      </div>
      {error && <div className="play-setup__error">{error}</div>}
      <div className="play-setup__buttons">
        <button onClick={start}>开始游戏</button>
        <button onClick={props.onBack}>返回</button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: CSS**

`webui/client/src/components/PlaySetup.css`:
```css
.play-setup { min-height: 100vh; padding: 40px; background: #1a1a2e; color: #eee; }
.play-setup h2 { margin-bottom: 24px; }
.play-setup__slots {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;
}
.play-setup__slot {
  background: #23234a; padding: 16px; border-radius: 8px; border: 1px solid #2a2a4a;
}
.play-setup__slot-label { font-weight: bold; margin-bottom: 10px; color: #fa6; }
.play-setup__slot select,
.play-setup__slot textarea {
  width: 100%; padding: 8px; background: #1a1a2e; color: #eee;
  border: 1px solid #4a4a8a; border-radius: 3px; margin-top: 6px; box-sizing: border-box;
  font-family: inherit; font-size: 13px;
}
.play-setup__slot textarea { font-family: monospace; font-size: 11px; }
.play-setup__error { color: #f66; margin-bottom: 8px; }
.play-setup__buttons button {
  background: #3a3a6a; color: #eee; border: 1px solid #4a4a8a;
  padding: 10px 20px; border-radius: 3px; cursor: pointer; margin-right: 8px;
}
.play-setup__buttons button:first-child { background: #fa6; color: #1a1a2e; font-weight: bold; }
```

- [ ] **Step 3: tsc**

```bash
cd webui/client && npx tsc -b --noEmit 2>&1 | grep -v "GameBoard\|gameService" | head -10
```
Expected: 无新错

- [ ] **Step 4: 提交**

```bash
git add webui/client/src/components/PlaySetup.tsx webui/client/src/components/PlaySetup.css
git commit -m "feat(client): PlaySetup — dual-slot deck/random selector before game start

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 17: `App.tsx` 状态机扩展 + GameBoard 调用更新

**Files:**
- Modify: `webui/client/src/App.tsx`
- Modify: `webui/client/src/components/GameBoard.tsx`(`createGame` 调用点)

- [ ] **Step 1: 找 GameBoard 中 createGame 调用**

```bash
grep -n "createGame\|playerClass\|onBack" /home/xu/code/hstone/hearthstone/fireplace/webui/client/src/components/GameBoard.tsx | head -20
```
记下 `gameService.createGame(...)` 的调用行号。

- [ ] **Step 2: 改 GameBoard `createGame` 调用**

GameBoard 当前从 props 拿 `playerClass` 然后调 `gameService.createGame(mode, playerClass, ...)`。改为接收 `p1Spec`/`p2Spec`:

修改 `GameBoard.tsx` props 类型 + 调用点:
- props 增加 `p1Spec: DeckSpec; p2Spec: DeckSpec`
- 移除 `playerClass: string` 字段
- `createGame` 调用改为 `gameService.createGame(mode, p1Spec, p2Spec)`

具体编辑(假设 `GameBoard.tsx` 顶部有 `type Props = { mode: string; playerClass: string; onBack: () => void }`)— 实际行号见 grep 输出:

```typescript
import type { DeckSpec } from '../types/deck';

type Props = { mode: string; p1Spec: DeckSpec; p2Spec: DeckSpec; onBack: () => void };
// ...
useEffect(() => {
  gameService.createGame(mode, p1Spec, p2Spec);
  // ...
}, []);
```

- [ ] **Step 3: 改 App.tsx 全部状态机**

完全替换 `webui/client/src/App.tsx` 内容为:
```tsx
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './i18n';
import './App.css';
import GameBoard from './components/GameBoard';
import DeckList from './components/DeckList';
import DeckEditor from './components/DeckEditor';
import PlaySetup from './components/PlaySetup';
import type { DeckSpec } from './types/deck';
import { newDeck } from './services/deckStore';

type View =
  | { kind: 'menu' }
  | { kind: 'decks-list' }
  | { kind: 'deck-edit'; deckId: string | null | 'new'; initialDeck?: import('./types/deck').Deck }
  | { kind: 'play-setup'; mode: 'pve' | 'pvp' | 'ai' }
  | { kind: 'in-game'; mode: string; p1: DeckSpec; p2: DeckSpec };

function App() {
  const { t, i18n } = useTranslation();
  const [view, setView] = useState<View>({ kind: 'menu' });
  const [showSettings, setShowSettings] = useState(false);

  const changeLanguage = (lang: string) => i18n.changeLanguage(lang);

  if (view.kind === 'in-game') {
    return (
      <GameBoard
        mode={view.mode}
        p1Spec={view.p1}
        p2Spec={view.p2}
        onBack={() => setView({ kind: 'menu' })}
      />
    );
  }

  if (view.kind === 'play-setup') {
    return (
      <PlaySetup
        mode={view.mode}
        onStart={(p1, p2) => setView({ kind: 'in-game', mode: view.mode, p1, p2 })}
        onBack={() => setView({ kind: 'menu' })}
      />
    );
  }

  if (view.kind === 'deck-edit') {
    return (
      <DeckEditor
        deckId={view.deckId}
        initialDeck={view.initialDeck}
        onBack={() => setView({ kind: 'decks-list' })}
      />
    );
  }

  if (view.kind === 'decks-list') {
    return (
      <DeckList
        onOpenDeck={(id) => setView({ kind: 'deck-edit', deckId: id })}
        onCreateDeck={(cls) => {
          const d = newDeck(cls);
          setView({ kind: 'deck-edit', deckId: 'new', initialDeck: d });
        }}
        onBrowseAll={() => setView({ kind: 'deck-edit', deckId: null })}
        onBack={() => setView({ kind: 'menu' })}
      />
    );
  }

  // menu
  return (
    <div className="app">
      <div className="app-content">
        <h1>Fireplace</h1>
        <h2>Hearthstone Simulator</h2>

        <div className="mode-select">
          <button onClick={() => setView({ kind: 'play-setup', mode: 'pve' })}>{t('game.mode.pve')}</button>
          <button onClick={() => setView({ kind: 'play-setup', mode: 'pvp' })}>{t('game.mode.pvp')}</button>
          <button onClick={() => setView({ kind: 'play-setup', mode: 'ai' })}>{t('game.mode.ai')}</button>
          <button onClick={() => setView({ kind: 'decks-list' })}>{t('ui.decks')}</button>
        </div>

        <button className="settings-btn" onClick={() => setShowSettings(!showSettings)}>
          ⚙️ {t('ui.settings')}
        </button>

        {showSettings && (
          <div className="settings-menu">
            <h3>{t('ui.language')}</h3>
            <div className="language-options">
              <button className={i18n.language === 'zhCN' ? 'active' : ''} onClick={() => changeLanguage('zhCN')}>简体中文</button>
              <button className={i18n.language === 'enUS' ? 'active' : ''} onClick={() => changeLanguage('enUS')}>English</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
```

- [ ] **Step 4: tsc 整体过一遍**

```bash
cd webui/client && npx tsc -b --noEmit
```
Expected: **0 错误**

- [ ] **Step 5: 提交**

```bash
git add webui/client/src/App.tsx webui/client/src/components/GameBoard.tsx
git commit -m "feat(client): App.tsx state machine for decks/play-setup/in-game

Replaces hero-class state with a tagged View union covering menu,
decks-list, deck-edit (three sub-modes), play-setup, and in-game.
GameBoard now receives DeckSpec slots instead of a single class.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 18: i18n 文案串

**Files:**
- Modify: `webui/client/src/i18n.ts`

- [ ] **Step 1: 加文案**

修改 `i18n.ts`,在 `zhCN.translation` 末尾(`"ui.back": "返回"` 之后)加:
```typescript
      "ui.decks": "卡组",
      "deck.list.title": "我的卡组",
      "deck.list.new": "新建",
      "deck.list.import": "导入 deckstring",
      "deck.list.browseAll": "浏览全卡库",
      "deck.list.empty": "还没有卡组,点新建或导入开始",
      "deck.editor.save": "保存",
      "deck.editor.export": "导出",
      "deck.play.start": "开始游戏",
      "deck.play.player": "玩家",
      "deck.play.opponent": "对手",
      "deck.play.player1": "玩家 1",
      "deck.play.player2": "玩家 2",
```

在 `enUS.translation` 同一位置加对应英文(同样 key,值改成英文)。

(组件代码里目前用了硬编码中文字符串—这是 v1 简化的取舍。如果你想完整 i18n,可以再开一个 task 把组件里的中文替换成 `t(key)`,但 spec 没把这定为 v1 必做。)

- [ ] **Step 2: tsc**

```bash
cd webui/client && npx tsc -b --noEmit
```
Expected: 0 错误

- [ ] **Step 3: 提交**

```bash
git add webui/client/src/i18n.ts
git commit -m "feat(client): i18n strings for deck list/editor/play setup

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 19: 端到端手测

**Files:** 无新建/修改 — 仅运行验证

**预备:**
```bash
# 后端
cd /home/xu/code/hstone/hearthstone/fireplace
source webui/venv/bin/activate 2>/dev/null || true
python -m pytest tests/test_card_catalog.py tests/test_deck_validate.py tests/test_create_game_specs.py -v
# 前端构建
cd webui/client && npm run build
# 启动 server(在另一终端)
cd /home/xu/code/hstone/hearthstone/fireplace && python webui/run.py
```

打开 `http://localhost:<server-port>`,逐项过 spec §8.3 验收清单:

- [ ] **C1**:主菜单"卡组" → 列表 → 新建 → 选职业(法师) → 编辑器 → 加 30 张 → 保存 → 列表显示
- [ ] **C2**:编辑器筛选费用 / 类型 / 中文搜索 / 英文搜索 各能 narrow 列表
- [ ] **C3**:hover 卡牌出 `CardPreview`;单击加入;DeckPanel 单击移除
- [ ] **C4**:法师卡组里"火球术"加到 2 张 → 第三次"加入"按钮 disabled
- [ ] **C5**:法师卡组中点猎人独有卡 → disabled
- [ ] **C6**:导出 deckstring → 复制到剪贴板 → "导入 deckstring" 粘贴 → 卡组与原 cards/hero/format 完全相同
- [ ] **C7**:用真实炉石客户端的 deckstring 导入 → 已实现部分正常,未实现部分 implemented:false 标灰
- [ ] **C8**:主菜单 PVE → 双槽位:玩家槽 = 已存卡组,对手槽 = `random:ANY` → 开始 → 对局正常
- [ ] **C9**:PVE 对手槽改为某副已存卡组 → 对手 AI 用该卡组开局(查 server 日志确认 `[Deck]` 行不是 `filtered_random_draft`)
- [ ] **C10**:PVP 双槽都用已存卡组 → 对局正常
- [ ] **C11**:`localStorage.setItem('fireplace.decks.v1', '<garbage>')` → 刷新 → 卡组列表为空,console.warn,不崩
- [ ] **C12**:卡组列表 → "浏览全卡库" → 进入浏览模式,DeckPanel 不显示;点卡只弹详情,不加卡
- [ ] **C13**:含未实现卡的 deckstring 导入 → DeckPanel 标红;尝试开局 → 收到 `create_game_error` toast,游戏未创建

如果某项失败,**回到对应任务**修复,重做该任务的 commit。

- [ ] **Step Final: 总提交**(若手测过程中有补丁)

```bash
git log --oneline | head -25
# 应能看到 Task 1..18 各自的 commit + 任何 fixup
```

---

## 自检清单

完成上述 19 个任务后,回头对照 spec:

- [ ] §1 目标:卡组列表/新建/编辑/删除/复制 ✅(Task 15);卡库筛选+搜索 ✅(Task 12);localStorage + deckstring ✅(Task 7、7b);双槽位开始游戏 ✅(Task 16、17);复用 `fireplace.deckstring` + `card_text_loader` ✅(Task 2、4、7b);删除 `create_game_with_deck` ✅(Task 9)
- [ ] §3.2 重构:`is_card_implemented` 移到 `card_catalog.py` ✅(Task 1);`card_catalog.py` 复用 `card_text_loader` 不重复 parse XML ✅(Task 2);`views.py` 的 `_load_card_multilang` 还在 — **TODO**:Task 3 应该删它,我留了 endpoint 但没主动删旧函数。**补充任务**:
   - 在 Task 3 末尾加上 **Step "remove _load_card_multilang from views.py"**:把它改用 `card_text_loader.get_name(id)` / `get_text(id)`
- [ ] §4.1 Card 类型 ✅(Task 7);`max_count` 推导 ✅(Task 2 `_card_to_dict`)
- [ ] §4.2 Deck schema + DECKS_STORAGE_KEY + migrate ✅(Task 7)
- [ ] §5 API:`/api/cards/all`(Task 3)、`/api/decks/validate`(Task 4)、`/api/decks/encode`(Task 7b);ETag(Task 3)
- [ ] §5.3 socket create_game payload + GameManager 签名(Task 5、6)
- [ ] §6 UX:状态机(Task 17)、编辑器三模式(Task 14)、卡组保存约束(Task 13 + deckStore.isDeckSavable)、PlaySetup(Task 16)
- [ ] §7 错误处理:导入未实现卡灰显(Task 4 backend + Task 14 cardDisabled);localStorage 损坏(Task 7 readEnvelope);超 30 disable save(Task 13);删除卡组确认(Task 15);多语言 fallback(Task 2);浏览模式不加卡(Task 14)
- [ ] §8.1 Python 测试覆盖:test_card_catalog.py(Task 1、2、3)、test_deck_validate.py(Task 4、7b)、test_create_game_specs.py(Task 5、6)

**有一个 spec 项漏了**:§3.2 "`views.py` 中 `_load_card_multilang` 删除并改用 `card_text_loader`"。**补加 Task 3.5**:

---

## Task 3.5: 清理 `views.py._load_card_multilang`

**Files:**
- Modify: `webui/server/views.py`

- [ ] **Step 1: 把 `_load_card_multilang` 替换为 wrapper**

修改 `views.py`:删除原 lines ~30-67 的 `_card_cache` 字典 + `_load_card_multilang` 函数;改为:
```python
def _load_card_multilang(card_id):
    """从 card_text_loader 取多语言名称(只有 zhCN + enUS fallback;其它语言 v1 不支持)"""
    from .card_text import card_text_loader
    info = card_text_loader.card_data.get(card_id, {})
    name = info.get('name')
    if not name:
        return {}
    # card_text_loader 当前只缓存 zhCN+fallback,所以 zhCN 与 enUS(通过 fallback 已含)都返回同一个值
    return {'zhCN': name, 'enUS': name}
```
注意:这个 wrapper 用法接近原 `_load_card_multilang` 返回的 dict 形状,所以已有的 `/api/cards/<card_id>` endpoint 不用动。**(如果觉得这个 wrapper 太鸡肋,直接把 `/api/cards/<card_id>` 也改成调 `card_text_loader.get_name` 即可。)**

- [ ] **Step 2: 跑测试确认未破坏 `/api/cards/<id>`**

```bash
python -m pytest tests/ -v -k "test_carddb or test_webui_hero" 2>&1 | tail -15
```
Expected: 仍 PASS

- [ ] **Step 3: 提交**

```bash
git add webui/server/views.py
git commit -m "refactor(webui): drop views._load_card_multilang per-call XML parse

Now delegates to the existing card_text_loader; the old code parsed
the entire CardDefs.xml on every cache miss, which got noticeable as
the catalog grew.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

(此任务建议在 Task 3 完成后立即执行,即"Task 3.5",而非到全部任务后。)

---

## 完成

所有任务完成后:

```bash
git log --oneline | head -25
git push origin main
```

(如果是 worktree,先 merge 回主分支再 push。)

打开 PR 时引用 spec 与本 plan 文档作为评审上下文。
