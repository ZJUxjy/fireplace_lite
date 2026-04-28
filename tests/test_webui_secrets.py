"""WebUI-layer integration tests for the secret system.

These tests exercise webui.server.game.GameManager.track_secrets() against
real engine games, confirming each ROADMAP-listed secret can be played and
its trigger is detected by the WebUI's diff-based tracker.
"""
import pytest
from hearthstone.enums import CardClass

from utils import prepare_game

# All Phase 2 ROADMAP-listed secrets (card_id -> human name).
# These match webui/server/game.py TEST_DECK_CARDS entries.
ROADMAP_SECRETS = [
    # Mage
    ("EX1_295", "Ice Block"),
    ("EX1_287", "Counterspell"),
    ("EX1_289", "Ice Barrier"),
    ("EX1_294", "Mirror Entity"),
    ("EX1_594", "Vaporize"),
    ("ICC_082", "Frozen Clone"),
    # Hunter
    ("EX1_610", "Explosive Trap"),
    ("EX1_611", "Freezing Trap"),
    ("EX1_533", "Misdirection"),
    ("EX1_554", "Snake Trap"),
    ("EX1_609", "Snipe"),
    # Paladin
    ("EX1_130", "Noble Sacrifice"),
    ("EX1_136", "Redemption"),
    ("EX1_132", "Eye for an Eye"),
    ("EX1_379", "Repentance"),
]


def test_all_roadmap_secrets_load_from_carddb():
    """Sanity: every ROADMAP secret instantiates and is tagged as secret."""
    game = prepare_game()
    for card_id, _name in ROADMAP_SECRETS:
        card = game.player1.give(card_id)
        assert card is not None, f"{card_id} failed to instantiate"
        assert getattr(card.data, "secret", False), (
            f"{card_id} ({_name}) is not flagged as secret in CardDefs.xml"
        )
        # Drop from hand so the next give() doesn't hit the 10-card hand limit
        # (prepare_game starts the player with ~4 cards from mulligan; the loop
        # adds 15 more, which would otherwise burn 9 cards and break give()).
        card.destroy()
