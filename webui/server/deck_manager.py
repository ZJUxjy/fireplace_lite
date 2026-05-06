"""
Deck Manager for WebUI

Handles deck import/export using Hearthstone-compatible deckstrings.
"""

from typing import List, Tuple, Optional, Dict
from fireplace.cards import db
from hearthstone.enums import CardClass, CardType
from fireplace.deckstring import (
    encode_deck, decode_deck, Format,
    get_hero_class_name, get_hero_class_id,
    InvalidDeckstring
)


# Map hero class IDs to fireplace hero card IDs
HERO_ID_MAP = {
    1: "HERO_11",  # Death Knight - The Lich King (CardClass.DEATHKNIGHT = 1)
    7: "HERO_01",  # Warrior - Garrosh
    8: "HERO_03",  # Rogue - Valeera
    9: "HERO_04",  # Paladin - Uther
    10: "HERO_05",  # Hunter - Rexxar
    11: "HERO_06",  # Druid - Malfurion
    12: "HERO_02",  # Shaman - Thrall
    13: "HERO_07",  # Warlock - Gul'dan
    14: "HERO_08",  # Mage - Jaina
    15: "HERO_09",  # Priest - Anduin
    17: "HERO_10",  # Demon Hunter - Illidan
}

# Reverse mapping
HERO_ID_TO_CLASS = {v: k for k, v in HERO_ID_MAP.items()}


class DeckManagerError(Exception):
    """Base exception for deck manager"""
    pass


class CardNotFound(DeckManagerError):
    """Raised when a card cannot be found"""
    pass


class InvalidDeck(DeckManagerError):
    """Raised when deck is invalid"""
    pass


def get_card_by_dbf_id(dbf_id: int) -> Optional[str]:
    """
    Get card ID from DBF ID.

    Args:
        dbf_id: Hearthstone card DBF ID

    Returns:
        Card ID string or None if not found
    """
    if not db.initialized:
        db.initialize()

    return db.dbf.get(dbf_id)


def get_dbf_id_by_card_id(card_id: str) -> Optional[int]:
    """
    Get DBF ID from card ID.

    Args:
        card_id: Card ID string (e.g., "CS2_106")

    Returns:
        DBF ID or None if not found
    """
    if not db.initialized:
        db.initialize()

    card = db.get(card_id)
    if card:
        return card.dbf_id
    return None


def import_deck_from_string(deckstring: str) -> Dict:
    """
    Import a deck from a deckstring.

    Args:
        deckstring: Hearthstone deckstring

    Returns:
        Dict with:
        - cards: List of (card_id, count) tuples
        - hero_class: Hero class name (e.g., "WARRIOR")
        - hero_id: Hero card ID (e.g., "HERO_01")
        - format: Format name ("WILD", "STANDARD", "CLASSIC")
        - invalid_cards: List of DBF IDs that couldn't be found
    """
    if not db.initialized:
        db.initialize()

    try:
        cards_dbf, hero_class_id, format_type = decode_deck(deckstring)
    except InvalidDeckstring as e:
        raise InvalidDeck(f"Invalid deckstring: {e}")

    # Get hero class name
    hero_class = get_hero_class_name(hero_class_id)
    if not hero_class:
        raise InvalidDeck(f"Unknown hero class ID: {hero_class_id}")

    # Get hero card ID
    hero_id = HERO_ID_MAP.get(hero_class_id)
    if not hero_id:
        raise InvalidDeck(f"No hero found for class ID: {hero_class_id}")

    from .card_catalog import is_card_implemented

    # Convert card DBF IDs to card IDs with implementation status
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

    # Validate deck size
    if total_cards != 30:
        # Some modes allow different sizes, but standard is 30
        pass  # Don't enforce for now

    return {
        "cards": cards_with_status,
        "hero_class": hero_class,
        "hero_id": hero_id,
        "format": format_type.name,
        "invalid_cards": invalid_cards,
        "unimplemented_count": unimplemented_count,
        "total_cards": total_cards,
    }


def export_deck_to_string(
    cards: List[Tuple[str, int]],
    hero_class: str,
    format_type: Format = Format.STANDARD
) -> str:
    """
    Export a deck to a deckstring.

    Args:
        cards: List of (card_id, count) tuples
        hero_class: Hero class name (e.g., "WARRIOR")
        format_type: Game format

    Returns:
        Hearthstone deckstring
    """
    if not db.initialized:
        db.initialize()

    # Get hero class ID
    hero_class_id = get_hero_class_id(hero_class)
    if not hero_class_id:
        raise InvalidDeck(f"Unknown hero class: {hero_class}")

    # Convert card IDs to DBF IDs
    cards_dbf = []
    invalid_cards = []

    for card_id, count in cards:
        dbf_id = get_dbf_id_by_card_id(card_id)
        if dbf_id:
            cards_dbf.append((dbf_id, count))
        else:
            invalid_cards.append(card_id)

    if invalid_cards:
        raise InvalidDeck(f"Cards not found: {invalid_cards}")

    # Validate deck
    total_cards = sum(count for _, count in cards_dbf)
    if total_cards != 30:
        # Allow non-standard sizes for now
        pass

    # Check max 2 copies per card
    for dbf_id, count in cards_dbf:
        if count > 2:
            card_id = get_card_by_dbf_id(dbf_id)
            # Check if it's a legendary (can only have 1)
            card = db.get(card_id) if card_id else None
            if card and card.rarity.name == "LEGENDARY":
                if count > 1:
                    raise InvalidDeck(f"Too many copies of legendary card: {card_id}")
            else:
                raise InvalidDeck(f"Too many copies of card: {card_id}")

    return encode_deck(cards_dbf, hero_class_id, format_type)


def create_deck_from_class(hero_class: str, format_type: Format = Format.STANDARD) -> List[str]:
    """
    Create a default deck for a class using available cards.

    Args:
        hero_class: Hero class name
        format_type: Game format

    Returns:
        List of card IDs (30 cards)
    """
    if not db.initialized:
        db.initialize()

    # Get class enum
    class_enum = getattr(CardClass, hero_class, None)
    if not class_enum:
        raise InvalidDeck(f"Unknown hero class: {hero_class}")

    class_id = class_enum.value

    # Collect available cards for this class
    class_cards = []
    neutral_cards = []

    for card_id, card in db.items():
        # Skip heroes, tokens, etc.
        if card.type != CardType.MINION and card.type != CardType.SPELL and card.type != CardType.WEAPON:
            continue

        # Skip non-collectible cards
        if not getattr(card, 'collectible', False):
            continue

        # Check class
        card_class = getattr(card, 'card_class', None)
        if card_class == class_enum:
            class_cards.append(card_id)
        elif card_class == CardClass.NEUTRAL:
            neutral_cards.append(card_id)

    # Build a deck (simplified - just pick random cards)
    import random
    random.shuffle(class_cards)
    random.shuffle(neutral_cards)

    deck = []

    # Add class cards (up to 20)
    for card_id in class_cards[:20]:
        deck.extend([card_id] * 2)  # 2 copies

    # Fill with neutral cards
    for card_id in neutral_cards:
        if len(deck) >= 30:
            break
        deck.extend([card_id] * 2)

    # Trim to 30 cards
    deck = deck[:30]

    return deck


def get_deck_summary(cards: List[Tuple[str, int]]) -> Dict:
    """
    Get a summary of a deck.

    Args:
        cards: List of (card_id, count) tuples

    Returns:
        Dict with deck statistics
    """
    if not db.initialized:
        db.initialize()

    summary = {
        "total_cards": 0,
        "minions": 0,
        "spells": 0,
        "weapons": 0,
        "mana_curve": {i: 0 for i in range(8)},  # 0-7+
        "class_cards": 0,
        "neutral_cards": 0,
    }

    for card_id, count in cards:
        card = db.get(card_id)
        if not card:
            continue

        summary["total_cards"] += count

        # Card type
        if card.type == CardType.MINION:
            summary["minions"] += count
        elif card.type == CardType.SPELL:
            summary["spells"] += count
        elif card.type == CardType.WEAPON:
            summary["weapons"] += count

        # Mana cost
        cost = getattr(card, 'cost', 0)
        if cost >= 7:
            summary["mana_curve"][7] += count
        else:
            summary["mana_curve"][cost] += count

        # Class
        if card.card_class == CardClass.NEUTRAL:
            summary["neutral_cards"] += count
        else:
            summary["class_cards"] += count

    return summary
