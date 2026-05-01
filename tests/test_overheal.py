#!/usr/bin/env python
"""Tests for the OVERHEAL keyword and per-card behavior."""
import pytest
from utils import *


def _damage(target, amount):
    """Helper: deal exactly `amount` damage to target via Moonfire repeats."""
    for _ in range(amount):
        target.controller.give(MOONFIRE).play(target=target)


def test_overheal_full_health_target():
    """Healing a full-health minion fires Overheal for the entire amount."""
    game = prepare_game()
    holy = game.player1.give("AT_011").play()  # 1/4 priest
    assert holy.atk == 1
    assert holy.damage == 0

    # Voodoo Doctor heals 2 — all overheal on a full-health target
    game.player1.give("EX1_011").play(target=holy)
    # Overheal triggers → +2 atk
    assert holy.atk == 3


def test_overheal_partial_heal():
    """A heal exceeding the target's missing health fires Overheal."""
    game = prepare_game()
    holy = game.player1.give("AT_011").play()
    assert holy.atk == 1

    _damage(holy, 1)
    assert holy.damage == 1

    # Voodoo Doctor heals 2 → actual 1, overheal 1
    game.player1.give("EX1_011").play(target=holy)
    assert holy.damage == 0
    assert holy.atk == 3


def test_no_overheal_exact_heal():
    """Healing exactly the missing damage should NOT trigger Overheal."""
    game = prepare_game()
    holy = game.player1.give("AT_011").play()
    assert holy.atk == 1

    _damage(holy, 2)
    assert holy.damage == 2

    # Voodoo Doctor heals 2 → exactly fills, no overheal
    game.player1.give("EX1_011").play(target=holy)
    assert holy.damage == 0
    assert holy.atk == 1  # unchanged


def test_no_overheal_partial_under_heal():
    """Healing less than missing damage should NOT trigger Overheal."""
    game = prepare_game()
    holy = game.player1.give("AT_011").play()
    _damage(holy, 3)
    assert holy.damage == 3

    # Voodoo Doctor heals 2 → all 2 absorbed, no overheal
    game.player1.give("EX1_011").play(target=holy)
    assert holy.damage == 1
    assert holy.atk == 1  # unchanged


def test_holy_champion_multiple_overheals():
    """Each separate overheal fires the trigger again."""
    game = prepare_game()
    holy = game.player1.give("AT_011").play()
    assert holy.atk == 1

    game.player1.give("EX1_011").play(target=holy)
    assert holy.atk == 3

    game.player1.give("EX1_011").play(target=holy)
    assert holy.atk == 5


def test_crimson_clergy_draws_on_overheal():
    """CS3_014 Crimson Clergy: Overheal: Draw a card."""
    game = prepare_game()
    clergy = game.player1.give("CS3_014").play()  # 1/3
    game.player1.discard_hand()
    assert len(game.player1.hand) == 0

    game.player1.give("EX1_011").play(target=clergy)
    # Voodoo Doctor itself goes to hand? No — battlecry minions go to field. Heal happens on play.
    # But the Voodoo Doctor minion is now on field (1/1). Ensure draw happened.
    assert len(game.player1.hand) == 1


def test_mana_geode_summons_crystal_on_overheal():
    """CFM_606 Mana Geode: Overheal: Summon a 2/2 Crystal."""
    game = prepare_game()
    geode = game.player1.give("CFM_606").play()  # 2/3
    assert len(game.player1.field) == 1

    # Overheal full-health geode → summon 2/2 token
    game.player1.give("EX1_011").play(target=geode)
    # Now field: Geode + Voodoo Doctor + crystal token
    assert len(game.player1.field) == 3
    crystal = next(m for m in game.player1.field if "CFM_606t" in m.id)
    assert crystal.atk == 2
    assert crystal.max_health == 2


def test_old_holy_champion_does_not_trigger_on_normal_heal():
    """Regression: old Holy Champion would trigger on any heal; new Overheal must NOT."""
    game = prepare_game()
    holy = game.player1.give("AT_011").play()
    assert holy.atk == 1

    _damage(holy, 2)
    game.player1.give("EX1_011").play(target=holy)
    assert holy.damage == 0
    assert holy.atk == 1  # Would have been 3 with old behavior


def test_overheal_event_amount_passed_to_callback():
    """ETC_339 Heartthrob: Overheal: Summon a minion with cost == overheal amount.

    Verifies that Overheal.AMOUNT is correctly bound when a card script reads it.
    """
    game = prepare_game()
    heart = game.player1.give("ETC_339").play()  # 2/5
    assert len(game.player1.field) == 1

    # Heal full-health Heartthrob for 2 → overheal=2 → summon a 2-cost minion
    game.player1.give("EX1_011").play(target=heart)
    # Field: Heartthrob + Voodoo Doctor + summoned 2-cost minion
    assert len(game.player1.field) == 3
    summoned = game.player1.field[-1]
    # Voodoo Doctor itself has cost 1, the summoned minion should have cost 2
    if "EX1_011" in summoned.id:
        # Voodoo Doctor was inserted last; the random summon was second
        summoned = game.player1.field[1]
    assert summoned.cost == 2


def test_injured_hauler_overheal_aoe():
    """WW_381 Injured Hauler: Battlecry self-damage 4, Overheal: Deal 2 to enemy minions."""
    game = prepare_game()
    # Set up enemy minions
    game.end_turn()
    enemy1 = game.player2.give(WISP).play()  # 1/1
    enemy2 = game.player2.summon("CS2_182")  # Chillwind Yeti 4/5
    game.end_turn()

    # Heal-amplifier? No. Injured Hauler 3/7 → battlecry deals 4 to self → 3/3.
    # When healed, overheal triggers AOE 2.
    hauler = game.player1.give("WW_381").play()
    assert hauler.health == 3  # 7 - 4 self damage
    assert hauler.damage == 4

    # Heal hauler for 6 (Holy Light) → actual 4, overheal 2 → AOE 2
    game.player1.give(HOLY_LIGHT).play(target=hauler)
    # Wisp dies (1 - 2), Yeti damaged (5 → 3)
    assert enemy1.zone != enemy1.zone.PLAY or enemy1 not in game.player2.field
    assert enemy2.health == 3
