#!/usr/bin/env python
"""Tests for Phase 4 modern mechanics: EXCAVATE, STARSHIP."""
from utils import *


# === EXCAVATE ===

def test_excavate_increments_count_and_adds_treasure_to_hand():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    assert game.player1.excavate_count == 0
    miner = game.player1.give("WW_001")  # Kobold Miner
    miner.play()
    assert game.player1.excavate_count == 1
    # Treasure tier-1 ID should be in hand now
    treasure_ids = {c.id for c in game.player1.hand}
    tier1_pool = {"WW_001t", "WW_001t2", "WW_001t3", "WW_001t4", "WW_001t18"}
    assert treasure_ids & tier1_pool


def test_excavate_advances_through_tiers():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    for _ in range(4):
        m = game.player1.give("WW_001")
        m.play()
    assert game.player1.excavate_count == 4
    # 4th excavate should be tier 4 (Azerite legendary)
    azerite_pool = {"WW_001t23", "WW_001t24", "WW_001t25", "WW_001t26", "WW_001t27"}
    hand_ids = {c.id for c in game.player1.hand}
    assert hand_ids & azerite_pool


def test_excavate_caps_at_tier_4():
    """5th excavate stays at tier 4."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    for _ in range(5):
        m = game.player1.give("WW_001")
        m.play()
    assert game.player1.excavate_count == 5
    # All Azerite-tier treasures count tier-4 hits
    azerite_pool = {"WW_001t23", "WW_001t24", "WW_001t25", "WW_001t26", "WW_001t27"}
    azerite_in_hand = sum(1 for c in game.player1.hand if c.id in azerite_pool)
    assert azerite_in_hand >= 1  # at least the one from the 5th excavate


def test_excavate_via_spell():
    """DEEP_018 Shroomscavate: Give DS + Excavate."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    wisp = game.player1.give(WISP)
    wisp.play()
    spell = game.player1.give("DEEP_018")
    spell.play(target=wisp)
    assert wisp.divine_shield
    assert game.player1.excavate_count == 1


# === STARSHIP ===

def test_starship_piece_attaches_on_play():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    assert not game.player1.is_building_starship
    crystal = game.player1.give("GDB_101")  # Dimensional Core, Starship Piece
    crystal.play()
    assert game.player1.is_building_starship
    assert crystal in game.player1.starship_pieces


def test_starship_predicate_powers_bonus():
    """GDB_130 Crystal Welder: +2/+2 if building Starship."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Without a piece, no bonus
    welder1 = game.player1.give("GDB_130")
    welder1.play()
    assert welder1.atk == 2  # base 2/3
    assert welder1.health == 3
    # Now play a piece, then play another welder — should get bonus
    game.player1.give("GDB_101").play()  # Dimensional Core (Piece)
    welder2 = game.player1.give("GDB_130")
    welder2.play()
    assert welder2.atk == 4  # 2 + 2 = 4
    assert welder2.health == 5  # 3 + 2 = 5


def test_starship_launch_clears_pieces():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.give("GDB_101").play()  # piece (2c)
    game.player1.give("GDB_105").play()  # piece (3c, Rush, Windfury)
    assert len(game.player1.starship_pieces) == 2
    # Refill mana so Exodar (7c) is playable.
    game.player1.used_mana = 0
    exodar = game.player1.give("GDB_120")  # The Exodar
    exodar.play()
    assert len(game.player1.starship_pieces) == 0
    assert not game.player1.is_building_starship


def test_starship_launch_noop_when_not_building():
    """Exodar with no pieces launches nothing."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    assert not game.player1.is_building_starship
    exodar = game.player1.give("GDB_120")
    exodar.play()
    # No crash, no pieces remained
    assert len(game.player1.starship_pieces) == 0
