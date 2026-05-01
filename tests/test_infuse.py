#!/usr/bin/env python
"""Tests for the INFUSE keyword (Murder at Castle Nathria)."""
from utils import *
from hearthstone.enums import Zone


def _summon_and_kill_friendly_minion(game, n=1):
    """Helper: summon n friendly minions and kill them via Moonfire."""
    for _ in range(n):
        wisp = game.player1.summon(WISP)  # 1/1
        # Kill with Moonfire (1 damage)
        game.player1.give(MOONFIRE).play(target=wisp)


def test_infuse_progresses_on_friendly_death():
    """A card with INFUSE in hand increments progress when a friendly minion dies."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    imp = game.player1.give("REV_244")  # Infuse threshold = 3
    assert imp.progress == 0
    _summon_and_kill_friendly_minion(game, 1)
    assert imp.progress == 1


def test_infuse_morphs_when_threshold_reached():
    """When threshold is reached, the card morphs to its infused form."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    imp = game.player1.give("REV_244")  # threshold 3
    _summon_and_kill_friendly_minion(game, 3)
    morphed = next((c for c in game.player1.hand if c.id == "REV_244t"), None)
    assert morphed is not None
    assert imp.morphed is morphed


def test_infuse_does_not_morph_below_threshold():
    """The card stays in original form below threshold."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    imp = game.player1.give("REV_244")  # threshold 3
    _summon_and_kill_friendly_minion(game, 2)
    # Still in original form
    assert imp in game.player1.hand
    assert imp.id == "REV_244"


def test_infused_form_has_stronger_battlecry():
    """REV_244t: summons 2 copies (vs original which summons 1)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    imp = game.player1.give("REV_244")
    _summon_and_kill_friendly_minion(game, 3)
    morphed = next(c for c in game.player1.hand if c.id == "REV_244t")
    morphed.play()
    copies = [m for m in game.player1.field if m.id == "REV_244t"]
    # Original on field + 2 summoned copies = 3
    assert len(copies) == 3


def test_infuse_only_friendly_deaths_count():
    """Enemy minion deaths should NOT count toward Infuse progress."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    imp = game.player1.give("REV_244")
    # Summon and kill 3 enemy minions
    for _ in range(3):
        wisp = game.player2.summon(WISP)
        game.player1.give(MOONFIRE).play(target=wisp)
    # Progress should be 0, not 3
    assert imp.progress == 0
    assert imp.id == "REV_244"


def test_infuse_threshold_4_card():
    """REV_019 has threshold 4."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    fool = game.player1.give("REV_019")
    _summon_and_kill_friendly_minion(game, 3)
    assert fool.id == "REV_019"  # not yet
    _summon_and_kill_friendly_minion(game, 1)
    morphed = next((c for c in game.player1.hand if c.id == "REV_019t"), None)
    assert morphed is not None
