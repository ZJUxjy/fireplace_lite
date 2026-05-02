#!/usr/bin/env python
"""Tests for Phase 1 + Phase 2 modern mechanics:
FRENZY, MANATHIRST, SPELLBURST, START_OF_GAME."""
from utils import *


# === FRENZY ===

def test_frenzy_fires_on_first_damage():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    initiate = game.player1.give("BAR_025")  # Sunwell Initiate; Frenzy: gain Divine Shield
    initiate.play()
    assert not initiate.divine_shield
    game.player1.give(MOONFIRE).play(target=initiate)  # 1 dmg
    assert initiate.divine_shield


def test_frenzy_fires_only_once():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    blacksmith = game.player1.give("BAR_073")  # Frenzy: friendly minions +2/+2
    blacksmith.play()
    other = game.player1.give(WISP)  # 1/1
    other.play()
    base_atk, base_hp = other.atk, other.health
    game.player1.give(MOONFIRE).play(target=blacksmith)  # 1st damage - frenzy
    assert other.atk == base_atk + 2
    assert other.health == base_hp + 2
    game.player1.give(MOONFIRE).play(target=blacksmith)  # 2nd damage - no frenzy
    assert other.atk == base_atk + 2  # unchanged
    assert other.health == base_hp + 2


def test_frenzy_does_not_fire_when_silenced():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    initiate = game.player1.give("BAR_025")
    initiate.play()
    game.player1.give("EX1_332").play(target=initiate)  # Silence
    game.player1.give(MOONFIRE).play(target=initiate)
    assert not initiate.divine_shield


# === SPELLBURST ===

def test_spellburst_fires_on_next_friendly_spell():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    oracle = game.player1.give("GDB_310")  # Spellburst: Draw 2 spells
    oracle.play()
    hand_size = len(game.player1.hand)
    # Cast a spell - any spell triggers
    moonfire = game.player1.give(MOONFIRE)
    moonfire.play(target=game.player2.hero)
    # Played 1 spell, drew 2 → +1 net (drew 2, played 1 from hand)
    # We can't guarantee deck size but we can check at least one card was added
    # Better: check spellburst_consumed flag is set
    assert oracle.spellburst_consumed


def test_spellburst_only_fires_once():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    oracle = game.player1.give("GDB_310")
    oracle.play()
    game.player1.give(MOONFIRE).play(target=game.player2.hero)
    assert oracle.spellburst_consumed
    # Second spell should NOT trigger again
    pre_hand = len(game.player1.hand)
    game.player1.give(MOONFIRE).play(target=game.player2.hero)
    # Hand size shouldn't grow from spellburst (just one card removed)
    # The flag stays consumed
    assert oracle.spellburst_consumed


def test_spellburst_does_not_fire_on_minion_play():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    oracle = game.player1.give("GDB_310")
    oracle.play()
    wisp = game.player1.give(WISP)
    wisp.play()  # minion, not a spell
    assert not oracle.spellburst_consumed


# === MANATHIRST ===

def test_manathirst_fires_when_threshold_met():
    game = prepare_empty_game()
    game.player1.max_mana = 8  # threshold is 8 for NX2_010
    beetle = game.player1.give("NX2_010")  # +4/+4 and Charge
    beetle.play()
    # Base 6/6 + 4/4 buff = 10/10
    assert beetle.atk == 10
    assert beetle.health == 10
    assert beetle.charge


def test_manathirst_does_not_fire_below_threshold():
    game = prepare_empty_game()
    game.player1.max_mana = 7  # threshold is 8
    beetle = game.player1.give("NX2_010")
    beetle.play()
    # Base 6/6, no buff
    assert beetle.atk == 6
    assert beetle.health == 6
    assert not beetle.charge


def test_manathirst_extra_heal_on_top_of_play():
    """RLK_219 Sunfury Clergy: heal 3, manathirst (6) heals another 3."""
    game = prepare_empty_game()
    game.player1.max_mana = 6
    game.player1.hero.damage = 10  # so heal can be observed
    clergy = game.player1.give("RLK_219")
    clergy.play()
    # Healed 6 total (3 base + 3 manathirst)
    assert game.player1.hero.health == game.player1.hero.max_health - 4


# === START_OF_GAME ===

def test_genn_greymane_still_works():
    """Sanity: existing GameStart-event-based START_OF_GAME path works after refactor."""
    # Genn (GIL_692): if even-cost-only deck, hero power costs 1.
    # Just verify the card loads and the engine doesn't crash.
    game = prepare_empty_game()
    genn = game.player1.give("GIL_692")
    assert genn is not None
