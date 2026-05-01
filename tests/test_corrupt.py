#!/usr/bin/env python
"""Tests for the CORRUPT keyword."""
from utils import *
from hearthstone.enums import Zone, GameTag


def test_corrupt_morphs_when_higher_cost_played():
    """A CORRUPT card in hand morphs to its corrupted form when controller plays a higher-cost card."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    cobra = game.player1.give("DMF_083")  # 2-cost CORRUPT
    # Play a 3-cost card
    game.player1.give("CS2_182")  # Chillwind Yeti (4-cost) — even higher
    yeti = game.player1.hand[-1]
    yeti.play()
    # Cobra should be morphed to DMF_083t
    morphed_cobra = next((c for c in game.player1.hand if c.id == "DMF_083t"), None)
    assert morphed_cobra is not None
    assert cobra.morphed is morphed_cobra


def test_no_corrupt_when_equal_cost():
    """Equal cost does NOT trigger corruption."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    cobra = game.player1.give("DMF_083")  # 2-cost
    same_cost = game.player1.give("CS2_171")  # Stonetusk Boar (1-cost) — actually lower
    # Need a 2-cost card. Let's use Bloodfen Raptor (CS2_172) which is 2-cost.
    raptor = game.player1.give("CS2_172")  # 2-cost
    raptor.play()
    # Cobra not morphed (cost 2 == 2)
    assert cobra.id == "DMF_083"
    assert cobra in game.player1.hand


def test_no_corrupt_when_lower_cost():
    """Lower cost does NOT trigger corruption."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    cobra = game.player1.give("DMF_083")  # 2-cost
    wisp = game.player1.give(WISP)  # 0-cost
    wisp.play()
    assert cobra.id == "DMF_083"


def test_corrupted_form_has_upgraded_stats():
    """The corrupted form (DMF_073t) has Rush + Divine Shield baked in."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    dirigible = game.player1.give("DMF_073")  # 3-cost
    yeti = game.player1.give("CS2_182")  # 4-cost
    yeti.play()
    morphed = next((c for c in game.player1.hand if c.id == "DMF_073t"), None)
    assert morphed is not None
    # Corrupted form has Rush (truthy, possibly int 1)
    assert morphed.rush


def test_corrupted_card_is_played_as_upgrade():
    """Playing the corrupted card yields the upgrade form on the field."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    pearltusk = game.player1.give("DMF_080")  # 5-cost minion 4/4
    ogre = game.player1.give("CS2_200")  # 6-cost
    ogre.play()
    # pearltusk now corrupted to DMF_080t
    morphed = next((c for c in game.player1.hand if c.id == "DMF_080t"), None)
    assert morphed is not None
    assert morphed.atk == 8
    # Refill mana so we can play the 5-cost morphed card
    game.player1.used_mana = 0
    morphed.play()
    on_field = [m for m in game.player1.field if m.id == "DMF_080t"]
    assert len(on_field) == 1
    assert on_field[0].rush


def test_corrupt_only_triggers_once():
    """A card already corrupted (morphed) does not get re-morphed when a 3rd higher-cost card is played."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    cobra = game.player1.give("DMF_083")  # 2-cost
    yeti = game.player1.give("CS2_182")
    yeti.play()
    # cobra morphed to DMF_083t
    morphed = next((c for c in game.player1.hand if c.id == "DMF_083t"), None)
    assert morphed is not None
    # Play another high-cost — should not re-trigger (DMF_083t doesn't have CORRUPT tag)
    ogre = game.player1.give("CS2_200")
    ogre.play()
    assert morphed in game.player1.hand
    # No further morph since DMF_083t lacks CORRUPT tag
    assert morphed.id == "DMF_083t"
