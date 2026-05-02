#!/usr/bin/env python
"""Tests for Phase 3 modern mechanics: FORGE, DREDGE."""
from utils import *
from hearthstone.enums import Zone


# === FORGE ===

def test_card_with_forge_tag_is_forgeable():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    crusher = game.player1.give("TTN_042")  # Cyclopian Crusher (Rush, Forge: +3/+2)
    assert crusher.is_forgeable


def test_forge_pays_two_mana_and_morphs():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    starting_mana = game.player1.mana
    crusher = game.player1.give("TTN_042")
    crusher.forge()
    # Paid 2 mana
    assert game.player1.mana == starting_mana - 2
    # Morphed to forged form (TTN_042t)
    forged = next((c for c in game.player1.hand if c.id == "TTN_042t"), None)
    assert forged is not None


def test_card_without_forge_is_not_forgeable():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    wisp = game.player1.give(WISP)
    assert not wisp.is_forgeable


def test_forge_requires_enough_mana():
    game = prepare_empty_game()
    game.player1.used_mana = game.player1.max_mana  # 0 available
    crusher = game.player1.give("TTN_042")
    assert not crusher.is_forgeable


def test_forge_only_in_hand():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    crusher = game.player1.give("TTN_042")
    crusher.play()  # now on board
    assert not crusher.is_forgeable


# === DREDGE ===

def test_dredge_moves_card_from_bottom_to_top():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Stack the deck with known cards (deck[0] is bottom; deck[-1] is top)
    game.player1.deck.clear()
    bottom = game.player1.card("CS2_065")  # Voidwalker (1/3 Taunt)
    middle = game.player1.card("CS2_172")  # Bloodfen Raptor (3/2)
    top = game.player1.card("CS2_182")     # Chillwind Yeti (4/5)
    for c in (bottom, middle, top):
        c.zone = Zone.DECK
    game.player1.deck[:] = [bottom, middle, top]  # bottom -> top
    # Play Rotting Necromancer (just dredges, ignores conditional)
    necro = game.player1.give("NX2_018")
    necro.play()
    # After dredge: chosen (bottom of deck = CS2_065 Voidwalker) should be on top
    assert game.player1.deck[-1].id == "CS2_065"


def test_dredge_does_nothing_with_empty_deck():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.deck.clear()
    necro = game.player1.give("NX2_018")
    # Should not crash even with empty deck
    necro.play()
    assert len(game.player1.deck) == 0


def test_dredge_with_small_deck_handles_all_cards():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.deck.clear()
    only = game.player1.card("CS2_065")
    only.zone = Zone.DECK
    game.player1.deck[:] = [only]
    necro = game.player1.give("NX2_018")
    necro.play()
    # Card stays in deck (it was already the only card, now it's the "top")
    assert len(game.player1.deck) == 1
    assert game.player1.deck[-1].id == "CS2_065"
