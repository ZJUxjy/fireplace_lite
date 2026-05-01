#!/usr/bin/env python
"""Tests for the MINIATURIZE keyword."""
from utils import *
from hearthstone.enums import GameTag, CardType


def test_miniaturize_adds_mini_to_hand():
    """Playing a Miniaturize minion adds a 1/1 mini-version to its controller's hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    hand_size_before = len(game.player1.hand)
    big = game.player1.give("TOY_312")  # Nostalgic Gnome 4-cost
    big.play()
    # +1 (give) - 1 (play) + 1 (mini) = +1 net
    assert len(game.player1.hand) == hand_size_before + 1
    mini_present = any(c.id == "TOY_312t" for c in game.player1.hand)
    assert mini_present


def test_mini_has_mini_stats():
    """The mini added is a 1/1 1-cost copy of the original."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    big = game.player1.give("TOY_312")  # Nostalgic Gnome
    big.play()
    mini = next(c for c in game.player1.hand if c.id == "TOY_312t")
    assert mini.cost == 1
    assert mini.atk == 1
    assert mini.health == 1


def test_miniaturize_multiple_independent_minis():
    """Each Miniaturize play adds a separate mini to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    big1 = game.player1.give("TOY_312")
    big1.play()
    game.end_turn(); game.end_turn()
    big2 = game.player1.give("TOY_312")
    big2.play()
    minis = [c for c in game.player1.hand if c.id == "TOY_312t"]
    assert len(minis) == 2


def test_miniaturize_via_script_override():
    """Cards with miniaturize_mini script override (no COLLECTION_RELATED tag) also work."""
    # TOY_380 Clay Matriarch uses script override
    game = prepare_empty_game()
    game.player1.max_mana = 10
    big = game.player1.give("TOY_380")
    big.play()
    assert any(c.id == "TOY_380t" for c in game.player1.hand)


def test_non_miniaturize_minion_does_not_add_mini():
    """A regular minion without MINIATURIZE does not produce a mini."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    hand_size_before = len(game.player1.hand)
    chillwind = game.player1.give("CS2_182")  # Chillwind Yeti
    chillwind.play()
    # +1 (give) - 1 (play) = 0 net
    assert len(game.player1.hand) == hand_size_before
