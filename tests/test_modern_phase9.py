#!/usr/bin/env python
"""Tests for Phase 9 — REWIND (Time Travel)."""
from utils import *
from hearthstone.enums import GameTag


def test_rewind_card_returns_a_copy_to_hand():
    """A Rewind card adds a fresh copy back to the controller's hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # TIME_002 Aeon Wizard: Rewind. Battlecry: Get 2 random spells.
    wizard = game.player1.give("TIME_002")
    initial_hand = len(game.player1.hand)
    wizard.play()
    # Original wizard is on board, but a fresh TIME_002 copy is in hand
    rewinds_in_hand = [c for c in game.player1.hand if c.id == "TIME_002"]
    assert len(rewinds_in_hand) == 1


def test_rewind_copy_has_used_rewind_flag():
    """The copy in hand is marked rewind_used so it doesn't loop."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    wizard = game.player1.give("TIME_002")
    wizard.play()
    rewind_copy = next(c for c in game.player1.hand if c.id == "TIME_002")
    assert getattr(rewind_copy, "rewind_used", False)


def test_rewind_copy_does_not_rewind_again():
    """When the rewind copy is played, it does NOT spawn another copy."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # First play
    game.player1.give("TIME_002").play()
    rewind_copy = next(c for c in game.player1.hand if c.id == "TIME_002")
    # Refill mana for second play (Aeon Wizard is 5c)
    game.player1.used_mana = 0
    rewind_copy.play()
    # No new TIME_002 should appear in hand (USED_REWIND prevented the loop)
    assert not any(c.id == "TIME_002" for c in game.player1.hand)


def test_non_rewind_card_does_not_spawn_copy():
    """A regular card without Rewind doesn't get duplicated."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    wisp = game.player1.give(WISP)
    wisp.play()
    assert not any(c.id == WISP for c in game.player1.hand)


def test_rewind_spell_returns_to_hand_too():
    """A Rewind SPELL also gets a copy back."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # TIME_001 Chrono Daggers: Rewind. Throw 3 knives at random enemies.
    spell = game.player1.give("TIME_001")
    spell.play()
    # A copy of TIME_001 should now be in hand
    rewinds = [c for c in game.player1.hand if c.id == "TIME_001"]
    assert len(rewinds) == 1
    assert getattr(rewinds[0], "rewind_used", False)
