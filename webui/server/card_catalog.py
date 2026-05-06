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
