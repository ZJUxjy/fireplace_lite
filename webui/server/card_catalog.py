"""
Card catalog: implemented-card filter + (later) collectible card metadata.

This module is the single source of truth for "which cards can actually be
played in our simulator". Both the random-deck generator (game.py) and the
deck builder UI (via /api/cards/all) read from here.
"""
from typing import Set


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

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fireplace.cards import db as _cards_db
from hearthstone.enums import CardType

_catalog_cache: Optional[Dict[str, Any]] = None


def _ensure_db_initialized() -> None:
    if not _cards_db.initialized:
        _cards_db.initialize()


def _safe_text_for(card_id: str, lang: str) -> str:
    """Get localized text from card_text_loader, return empty string if missing"""
    from .card_text import card_text_loader
    info = card_text_loader.card_data.get(card_id, {})
    if lang == "zhCN":
        return info.get("name") or ""
    return ""  # card_text.py currently only caches zhCN+fallback


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

    out: Dict[str, Any] = {
        "id": card_id,
        "dbf_id": card.dbf_id,
        "name_zh": name_zh,
        "name_en": _english_name(card) or card_id,
        "text_zh": text_zh,
        "text_en": "",  # v1: card_text.py only stores zhCN+fallback; leave as empty placeholder
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
    """Build full metadata list of implemented collectible cards (process-level cache)"""
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

    _catalog_cache = {
        "cards": cards,
        "total": len(cards),
        "etag": etag,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return _catalog_cache


def reset_catalog_cache() -> None:
    """Test helper: clear cache so next build_catalog() recalculates"""
    global _catalog_cache
    _catalog_cache = None
