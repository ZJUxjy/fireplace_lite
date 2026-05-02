#!/usr/bin/env python
"""Tests for Phase 5 modern mechanics: TOURIST, IMBUE."""
from utils import *


# === TOURIST ===

def test_tourist_card_is_marked_via_property():
    """Maestra (VAC_336) is a Warlock Tourist."""
    game = prepare_empty_game()
    maestra = game.player1.give("VAC_336")
    assert maestra.is_tourist


def test_non_tourist_card_returns_false():
    game = prepare_empty_game()
    wisp = game.player1.give(WISP)
    assert not wisp.is_tourist


# === IMBUE ===

def test_imbue_increments_count_on_play():
    """EDR_800 Flutterwing Guardian: Battlecry: Imbue."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    assert game.player1.imbue_count == 0
    flutter = game.player1.give("EDR_800")
    flutter.play()
    assert game.player1.imbue_count == 1


def test_imbue_stacks_across_multiple_plays():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    for _ in range(3):
        game.player1.used_mana = 0  # refresh between plays
        c = game.player1.give("EDR_800")
        c.play()
    assert game.player1.imbue_count == 3


def test_imbue_via_deathrattle():
    """EDR_227 Umbraclaw: Rush. Deathrattle: Imbue."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    umbra = game.player1.give("EDR_227")
    umbra.play()
    assert game.player1.imbue_count == 0
    # Umbraclaw is 5/2 → 2 damage kills it
    game.player1.give(MOONFIRE).play(target=umbra)
    game.player1.give(MOONFIRE).play(target=umbra)
    assert game.player1.imbue_count >= 1


def test_imbue_battlecry_and_deathrattle_both_trigger():
    """EDR_451 Goldpetal Drake: Battlecry AND Deathrattle: Imbue."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    drake = game.player1.give("EDR_451")
    drake.play()  # battlecry: +1
    assert game.player1.imbue_count == 1
    # Kill drake — find its actual stats and damage accordingly
    while drake.health > 0 and drake in game.player1.field:
        game.player1.give(MOONFIRE).play(target=drake)
    # Deathrattle: +1
    assert game.player1.imbue_count == 2
