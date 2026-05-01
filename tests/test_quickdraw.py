#!/usr/bin/env python
"""Tests for the QUICKDRAW keyword."""
from utils import *


def test_quickdraw_first_card_triggers():
    """Quickdraw effect fires when this is the first card played this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    assert game.player1.cards_played_this_turn == 0
    serpent = game.player1.give("WW_808")  # Silver Serpent
    serpent.play()
    # Quickdraw triggered → Immune buff applied
    assert serpent.immune is True


def test_quickdraw_not_triggered_when_not_first():
    """Quickdraw does NOT fire when another card was already played this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Play a non-quickdraw card first
    game.player1.give(WISP).play()
    assert game.player1.cards_played_this_turn == 1
    serpent = game.player1.give("WW_808")
    serpent.play()
    # Quickdraw didn't trigger → no immune
    assert serpent.immune is False


def test_quickdraw_resets_each_turn():
    """A second turn allows Quickdraw on the first card played that turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.give(WISP).play()  # play first card
    game.end_turn(); game.end_turn()
    # New turn — counter is back to 0
    assert game.player1.cards_played_this_turn == 0
    serpent = game.player1.give("WW_808")
    serpent.play()
    assert serpent.immune is True


def test_quickdraw_battlecry_and_quickdraw_both_fire():
    """Cards with both Battlecry and Quickdraw should fire both effects."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    chain_gang = game.player1.give("WW_360")  # Battlecry+Quickdraw both summon copy
    chain_gang.play()
    # Battlecry summoned 1 copy + Quickdraw summoned 1 more copy + the original = 3
    azerite_count = sum(1 for m in game.player1.field if m.id == "WW_360")
    assert azerite_count == 3


def test_quickdraw_battlecry_only_when_not_first():
    """Battlecry-only fires when Quickdraw condition is not met."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.give(WISP).play()  # play first card
    chain_gang = game.player1.give("WW_360")
    chain_gang.play()
    # Only battlecry triggered: original + 1 summoned copy = 2
    azerite_count = sum(1 for m in game.player1.field if m.id == "WW_360")
    assert azerite_count == 2


def test_quickdraw_spell_refresh_mana():
    """WW_823 Rehydrate: heal + Quickdraw refreshes 2 mana."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Drain mana to set baseline
    game.player1.used_mana = 5
    mana_before = game.player1.mana  # 5
    rehydrate = game.player1.give("WW_823")
    rehydrate.play(target=game.player1.hero)
    # Quickdraw triggered → +2 temp mana (after paying 2-cost)
    # Net: 5 - 2 (cost) + 2 (refresh) = 5
    assert game.player1.mana == mana_before


def test_quickdraw_get_coin():
    """WW_363 Bounty Wrangler: Quickdraw OR Combo: Get a Coin."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    hand_size_before = len(game.player1.hand)
    wrangler = game.player1.give("WW_363")
    wrangler.play()
    # +1 (give) - 1 (play) + 1 (coin from quickdraw) = +1 net
    assert len(game.player1.hand) == hand_size_before + 1
    assert any(c.id == "GAME_005" for c in game.player1.hand)
