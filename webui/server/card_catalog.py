"""
Card catalog: implemented-card filter + (later) collectible card metadata.

This module is the single source of truth for "which cards can actually be
played in our simulator". Both the random-deck generator (game.py) and the
deck builder UI (via /api/cards/all) read from here.
"""
import hashlib
import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from fireplace.cards import db as _cards_db
from hearthstone.enums import CardType, GameTag

logger = logging.getLogger(__name__)


# Catalog row schema version. BUMP THIS whenever the row dict shape changes
# — adds, removes, or changes the meaning of a key. Also bump when the set
# of implemented expansions changes (so users get fresh data on next load
# without having to clear browser/IDB cache manually). The on-disk cache is
# keyed by this number (see _cache_path), so a stale cache from an older
# schema is automatically ignored without explicit migration.
CATALOG_SCHEMA_VERSION = 2

CACHE_DIR = Path(__file__).parent / "cache"


def _cache_path() -> Path:
    return CACHE_DIR / f"catalog-v{CATALOG_SCHEMA_VERSION}.json"


_REQUIRED_CACHE_KEYS = {"cards", "total", "etag", "generated_at"}


def _load_persistent_cache() -> Optional[Dict[str, Any]]:
    """Read the versioned on-disk catalog if present and well-formed.
    Returns None on any failure (missing file, corrupted JSON, missing
    keys); the caller falls through to a fresh XML-parse build."""
    path = _cache_path()
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload, dict):
            raise ValueError("payload is not a dict")
        missing = _REQUIRED_CACHE_KEYS - set(payload.keys())
        if missing:
            raise ValueError(f"missing keys: {sorted(missing)}")
        if not isinstance(payload["cards"], list):
            raise ValueError("cards is not a list")
        return payload
    except (OSError, ValueError, json.JSONDecodeError) as e:
        logger.warning("persistent catalog cache at %s is unusable (%s); rebuilding", path, e)
        return None


def _write_persistent_cache(payload: Dict[str, Any]) -> None:
    """Atomically write the catalog payload to the versioned cache file.
    Failure is logged but never propagates — a missing on-disk cache
    only costs us a slow next start, not correctness."""
    path = _cache_path()
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        os.replace(tmp, path)
    except OSError as e:
        logger.warning("failed to write persistent catalog cache to %s: %s", path, e)


# Canonical mechanic keywords surfaced in the deck-builder filter rail and
# card-row badge. Order is the rendering order: a card with multiple
# keywords picks the earliest one for its badge slot. See
# openspec/changes/card-keyword-detection/design.md §D3 for rationale.
KEYWORD_TAGS = {
    "TAUNT":         GameTag.TAUNT,
    "BATTLECRY":     GameTag.BATTLECRY,
    "DEATHRATTLE":   GameTag.DEATHRATTLE,
    "CHARGE":        GameTag.CHARGE,
    "RUSH":          GameTag.RUSH,
    "DIVINE_SHIELD": GameTag.DIVINE_SHIELD,
    "WINDFURY":      GameTag.WINDFURY,
    "STEALTH":       GameTag.STEALTH,
    "POISONOUS":     GameTag.POISONOUS,
    "LIFESTEAL":     GameTag.LIFESTEAL,
    "SECRET":        GameTag.SECRET,
    "SPELLPOWER":    GameTag.SPELLPOWER,
    "COMBO":         GameTag.COMBO,
}

# Tags that show up on cards but are NOT mechanic keywords —
# either cosmetic (ELITE), runtime-only (FROZEN), numeric-with-its-own-column
# (OVERLOAD), effects rather than properties (SILENCE: Ironbeak Owl *casts*
# silence, the tag itself is on the target), or pure bookkeeping (CARDTYPE,
# CARD_SET, RARITY, COST, …). Used to filter the dev-only
# `/api/cards/keyword-candidates` report (design.md §D7).
KEYWORD_DENY_LIST = {
    # Static cosmetic / collectible flags
    "ELITE", "COLLECTIBLE", "PREMIUM", "FACTION", "MINI_SET",
    "MULTIPLE_CLASSES", "MULTI_CLASS_GROUP", "HAS_SIGNATURE_QUALITY",
    "DONT_PICK_FROM_SUBSETS", "DEV_STATE", "DevState",
    # Card-definition fields (every card has these by construction)
    "CARDTYPE", "CARD_SET", "CLASS", "RARITY", "COST",
    "ATK", "HEALTH", "DURABILITY", "ARMOR",
    "CARDRACE", "SPELL_SCHOOL", "TECH_LEVEL", "DBF_ID",
    "CARDNAME", "CARDTEXT_INHAND", "FLAVORTEXT", "ARTISTNAME",
    # Aura / runtime-state / control-flow tags
    "AURA", "IMMUNE", "IMMUNE_WHILE_ATTACKING", "FROZEN",
    "EXHAUSTED", "CANT_ATTACK", "CANT_BE_TARGETED_BY_SPELLS",
    "CANT_BE_DAMAGED", "CANNOT_ATTACK_HEROES", "HIDE_STATS",
    "FORGETFUL", "AFFECTED_BY_SPELL_POWER",
    "AFFECTED_BY_HEALING_DOES_DAMAGE",
    # Numeric mechanics with their own column / not chip-suitable
    "OVERLOAD", "SILENCE", "RECRUIT", "QUEST", "INSPIRE",
    "JADE_GOLEM", "ADJACENT_BUFF", "SIDE_QUEST",
    "QUEST_PROGRESS_TOTAL", "QUEST_REWARD_DATABASE_ID",
    "HEROPOWER_DAMAGE", "HERO_POWER",
    # Battlegrounds / multi-game-mode noise
    "BACON_SUBSET_BEAST", "BACON_SUBSET_MECH",
    "BACON_SUBSET_DEMON", "BACON_SUBSET_MURLOC", "BACON_SUBSET_DRAGON",
    "BACON_TRIPLE_UPGRADE_MINION_ID",
    # Visual / client-side / asset hints
    "TRIGGER_VISUAL", "AttackVisualType", "USE_DISCOVER_VISUALS",
    "DISPLAY_CARD_ON_MOUSEOVER", "DISCOVER_STUDIES_VISUAL",
    "TRANSFORMED_FROM_CARD_VISUAL_TYPE",
    "COLLECTION_RELATED_CARD_DATABASE_ID",
    "COLLECTIONMANAGER_FILTER_MANA_EVEN",
    "COLLECTIONMANAGER_FILTER_MANA_ODD",
    # Card-script / engine internals
    "TAG_SCRIPT_DATA_NUM_1", "TAG_SCRIPT_DATA_NUM_2",
    "PLAYER_TAG_THRESHOLD_TAG_ID", "PLAYER_TAG_THRESHOLD_VALUE",
    "ENTITY_TAG_THRESHOLD_TAG_ID", "ENTITY_TAG_THRESHOLD_VALUE",
    "CARDTEXT_ENTITY_0", "CARDTEXT_ENTITY_1",
    "MULTIPLY_BUFF_VALUE", "FAST_BATTLECRY", "NON_KEYWORD_ECHO",
    "FINISH_ATTACK_SPELL_ON_DAMAGE",
    "RECEIVES_DOUBLE_SPELLDAMAGE_BONUS",
    "DECK_RULE_MOD_DECK_SIZE", "DECK_ACTION_COST",
    # Class-flavor groupings (not keywords, just lore tags)
    "GRIMY_GOONS", "KABAL", "JADE_LOTUS", "SI_7", "LIBRAM",
    "RITUALIST_MINION", "VOODOO_LINK", "WHELP", "GEARS",
    "COST_FROST", "DEATH_KNIGHT",
    # Cosmetic / engine details masquerading as boolean tags
    "HAS_DIAMOND_QUALITY", "IMP",
    "ImmuneToSpellpower", "InvisibleDeathrattle",
    "ELUSIVE", "ENRAGED",
    "START_OF_GAME_KEYWORD",
}


def _extract_keywords(card) -> List[str]:
    """Return the canonical-keyword names whose corresponding GameTag is
    truthy on the given fireplace CardXML object. Order follows
    KEYWORD_TAGS declaration order so the result is deterministic.
    SPELLPOWER is numeric (+1, +2, …) — any nonzero value counts."""
    tags = getattr(card, "tags", None) or {}
    return [name for name, tag in KEYWORD_TAGS.items() if tags.get(tag)]


# Implemented card expansion prefixes (corresponding to fireplace/cards/ subdirectories)
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
    # ---------------------------------------------------------------
    # Modern sets (2024-2026). Only prefixes with ≥ 85% fireplace
    # script coverage are enabled here — partial sets like RLK / WW /
    # TTN need per-card whitelisting before they can be exposed.
    # ---------------------------------------------------------------
    # Whizbang's Workshop (2024) — MIS 36/37, TOY 139/144
    'MIS', 'TOY',
    # Cataclysm — CATA 131/132
    'CATA',
    # Whispers of the Emerald Dream — EDR 141/144, FIR 37/37
    'EDR', 'FIR',
    # The Lost City — TLC 141/146, DINO 38/38
    'TLC', 'DINO',
    # Time Travel set — TIME 146/146
    'TIME',
}

# Blacklist: cards with issues even if their prefix is implemented
CARD_BLACKLIST: Set[str] = set()


def is_card_implemented(card_id: str) -> bool:
    """Check if a card comes from an implemented expansion and is not blacklisted"""
    if card_id in CARD_BLACKLIST:
        return False
    prefix = card_id.split('_')[0] if '_' in card_id else card_id[:3]
    return prefix in IMPLEMENTED_CARD_PREFIXES


# ---------------------------------------------------------------------------
# build_catalog() -- full metadata for all implemented + collectible cards
# ---------------------------------------------------------------------------

_catalog_cache: Optional[Dict[str, Any]] = None
_catalog_lock = threading.Lock()  # 防止 Flask 多线程下首次构建竞态


def _ensure_db_initialized() -> None:
    if not _cards_db.initialized:
        _cards_db.initialize()


def _english_name(card) -> str:
    """Get English name from fireplace card object (__str__ is the English name)"""
    return str(card)


def _card_to_dict(card_id: str, card) -> Dict[str, Any]:
    """Convert fireplace card object + multilang data to API dict"""
    from .card_text import card_text_loader

    rarity = card.rarity.name if card.rarity else "FREE"
    max_count = 1 if rarity == "LEGENDARY" else 2

    info = card_text_loader.card_data.get(card_id, {})
    name_zh = info.get("name") or _english_name(card) or card_id
    text_zh = info.get("text") or ""
    # card_text_loader 当前只缓存 zhCN+enUS fallback,所以中英文效果文本相同。
    # 为了让英文用户至少能看到内容(spec §4.1 必填字段),fallback 到 text_zh。
    text_en = text_zh

    out: Dict[str, Any] = {
        "id": card_id,
        "dbf_id": card.dbf_id,
        "name_zh": name_zh,
        "name_en": _english_name(card) or card_id,
        "text_zh": text_zh,
        "text_en": text_en,
        "cost": getattr(card, "cost", 0),
        "type": card.type.name,
        "card_class": card.card_class.name if card.card_class else "NEUTRAL",
        "rarity": rarity,
        "card_set": card.card_set.name if card.card_set else "INVALID",
        "collectible": True,
        "max_count": max_count,
        "keywords": _extract_keywords(card),
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
    """Build full metadata list of implemented collectible cards (process-level cache)"""
    global _catalog_cache
    if _catalog_cache is not None:
        return _catalog_cache

    with _catalog_lock:
        # 双重检查:获得锁后另一线程可能已经构建好
        if _catalog_cache is not None:
            return _catalog_cache

        # Try the on-disk persistent cache before paying the 25s XML parse.
        persisted = _load_persistent_cache()
        if persisted is not None:
            _catalog_cache = persisted
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

        _catalog_cache = {
            "cards": cards,
            "total": len(cards),
            "etag": etag,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        _write_persistent_cache(_catalog_cache)
        return _catalog_cache


def reset_catalog_cache() -> None:
    """Test helper: clear cache so next build_catalog() recalculates"""
    global _catalog_cache, _candidates_cache
    with _catalog_lock:
        _catalog_cache = None
        _candidates_cache = None


# ---------------------------------------------------------------------------
# Paged catalog access — same in-memory list, sliced by cursor. Pages share
# the catalog's ETag so client revalidation is uniform across endpoints.
# ---------------------------------------------------------------------------

PAGE_MAX_SIZE = 500


def get_page(cursor: int, size: int) -> Dict[str, Any]:
    """Return one page of the catalog plus pagination metadata.
    `size` is silently capped at PAGE_MAX_SIZE; negative cursor is clamped to 0."""
    cat = build_catalog()
    cards = cat["cards"]
    total = cat["total"]

    cursor = max(0, int(cursor))
    size = max(0, min(int(size), PAGE_MAX_SIZE))

    end = cursor + size
    slice_ = cards[cursor:end] if cursor < total else []
    next_cursor: Optional[int] = end if end < total else None

    return {
        "cards": slice_,
        "cursor": cursor,
        "size": size,
        "next_cursor": next_cursor,
        "total": total,
        "etag": cat["etag"],
    }


# ---------------------------------------------------------------------------
# Dev-only: histogram of every boolean GameTag observed on at least one
# implemented collectible card that is NOT in the canonical keyword list and
# NOT in KEYWORD_DENY_LIST. Helps spot a real keyword that slipped past us
# when new card XML is dropped in. Surfaced via /api/cards/keyword-candidates
# behind FLASK_DEBUG/DEBUG_KEYWORDS — never shown in the UI.
# See openspec/changes/card-keyword-detection/design.md §D7.
# ---------------------------------------------------------------------------

_candidates_cache: Optional[List[Dict[str, Any]]] = None


def _compute_keyword_candidates() -> List[Dict[str, Any]]:
    """Walk every implemented collectible card, count boolean GameTags
    that fall outside KEYWORD_TAGS ∪ KEYWORD_DENY_LIST, return a list
    sorted by descending count (then tag name). Process-cached behind
    `_catalog_lock`."""
    global _candidates_cache
    if _candidates_cache is not None:
        return _candidates_cache

    with _catalog_lock:
        if _candidates_cache is not None:
            return _candidates_cache
        _ensure_db_initialized()

        recognized = set(KEYWORD_TAGS.keys())
        counts: Dict[str, int] = {}
        examples: Dict[str, List[str]] = {}

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

            tags = getattr(card, "tags", None) or {}
            for tag, value in tags.items():
                if not value:
                    continue
                # Only boolean-ish tags. Numeric tags (cost, atk, etc.) are
                # not GameTag-named keywords; skip anything that's not a
                # GameTag enum or whose value looks numeric beyond 1.
                name = getattr(tag, "name", None)
                if not name:
                    continue
                if name in recognized or name in KEYWORD_DENY_LIST:
                    continue
                # Filter out tags whose names look numeric/value-like or
                # are system bookkeeping (lots of GameTags are runtime
                # state, not card properties — they will never be set on
                # a card definition, but be defensive).
                if name.endswith("_VALUE") or name.endswith("_NUM") \
                        or name == "ZONE" or name == "CONTROLLER":
                    continue
                counts[name] = counts.get(name, 0) + 1
                ex = examples.setdefault(name, [])
                if len(ex) < 3:
                    ex.append(card_id)

        result = [
            {"tag": name, "count": counts[name], "examples": examples[name]}
            for name in sorted(counts, key=lambda n: (-counts[n], n))
        ]
        _candidates_cache = result
        return result
