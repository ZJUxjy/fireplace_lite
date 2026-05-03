#!/usr/bin/env python
"""Tests for Phase 10 — FABLED, TEMPORARY, BONUS EFFECT."""
from utils import *
from fireplace.actions import GiveBonusEffect


# === FABLED ===

def test_fabled_card_is_marked():
    """TIME_020 Broxigar has FABLED."""
    game = prepare_empty_game()
    brox = game.player1.give("TIME_020")
    assert brox.is_fabled


def test_fabled_plus_card_is_marked():
    """TIME_005 Timethief Rafaam has FABLED+."""
    game = prepare_empty_game()
    rafaam = game.player1.give("TIME_005")
    assert rafaam.is_fabled


def test_non_fabled_card_returns_false():
    game = prepare_empty_game()
    wisp = game.player1.give(WISP)
    assert not wisp.is_fabled


# === TEMPORARY ===

def test_temporary_flag_can_be_set_at_runtime():
    """A card with _is_temporary=True should be flagged as temporary."""
    game = prepare_empty_game()
    wisp = game.player1.give(WISP)
    assert not wisp.is_temporary
    wisp._is_temporary = True
    assert wisp.is_temporary


def test_temporary_card_discarded_at_end_of_turn():
    """Temporary cards in the active player's hand are discarded at end of turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    wisp = game.player1.give(WISP)
    wisp._is_temporary = True
    initial_grave = len(game.player1.graveyard)
    assert wisp in game.player1.hand
    game.end_turn()
    # Wisp should now be discarded (in graveyard or removed from hand)
    assert wisp not in game.player1.hand


def test_non_temporary_card_persists_across_turns():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    wisp = game.player1.give(WISP)
    assert wisp in game.player1.hand
    game.end_turn()
    game.end_turn()
    assert wisp in game.player1.hand


# === BONUS EFFECT ===

def test_bonus_effect_pool_has_six_options():
    assert len(GiveBonusEffect.BONUS_EFFECT_POOL) == 6
    assert len(set(GiveBonusEffect.BONUS_EFFECT_POOL)) == 6


def test_give_bonus_effect_attaches_an_enchantment():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    wisp = game.player1.give(WISP)
    wisp.play()
    initial_buff_count = len(wisp.buffs)
    game.cheat_action(wisp, [GiveBonusEffect(wisp)])
    assert len(wisp.buffs) == initial_buff_count + 1
    new_buff = wisp.buffs[-1]
    assert new_buff.id in GiveBonusEffect.BONUS_EFFECT_POOL


def test_bonus_effect_grants_a_keyword():
    """Trial multiple times — at least once we should observe a granted keyword."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    keyword_observed = False
    for _ in range(15):
        wisp = game.player1.summon(WISP)
        game.cheat_action(wisp, [GiveBonusEffect(wisp)])
        if (wisp.taunt or wisp.lifesteal or wisp.windfury or
                wisp.rush or wisp.divine_shield or wisp.reborn):
            keyword_observed = True
            break
    assert keyword_observed
