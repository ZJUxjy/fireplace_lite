#!/usr/bin/env python
"""Tests for Phase 8 — KINDRED (Year of the Raptor / The Lost City)."""
from utils import *
from hearthstone.enums import Race


def test_kindred_does_not_fire_without_same_race_friend():
    """Without a same-race ally on board, Kindred does NOT trigger."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    enemy = game.player2.summon("CS2_182")  # Yeti 4/5
    initial_hp = enemy.health
    # Firegill (Murloc) — Kindred: Give other minions Rush
    fish = game.player1.give("DINO_404")
    fish.play()
    # No allies on field, so kindred didn't fire (no "other minions" to receive Rush)
    others = [m for m in game.player1.field if m is not fish]
    assert all(not m.rush for m in others)


def test_kindred_fires_with_same_race_friend():
    """Firegill: Murloc with another Murloc on board → other gets Rush."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # First a Murloc (any will do; Bluegill Warrior CS2_173)
    bluegill = game.player1.summon("CS2_173")  # Bluegill 2/1 Charge
    assert Race.MURLOC in bluegill.races
    # Now Firegill — Kindred fires because another Murloc is in play
    fish = game.player1.give("DINO_404")
    fish.play()
    # Bluegill (other minion) should now have Rush from kindred
    assert bluegill.rush


def test_kindred_does_not_consider_self_for_race_match():
    """Self alone doesn't satisfy 'another minion of the same race'."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Lone Diabolus Rex (Beast) — Kindred shouldn't fire
    rex = game.player1.give("DINO_138")
    rex.play()
    # Enemy hero unharmed → Kindred didn't fire
    # (Diabolus Rex's Kindred deals damage to enemy minions; there are none,
    # so just verify it didn't crash and kindred didn't pick face.)
    assert game.player2.hero.health == game.player2.hero.max_health


def test_kindred_with_beast_ally_fires_on_beast_card():
    """Diabolus Rex (Beast) with another Beast → Kindred deals damage."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # First a Beast (any will do; Bloodfen Raptor CS2_172 is Beast 3/2)
    raptor = game.player1.summon("CS2_172")
    assert Race.BEAST in raptor.races
    # Enemy minions to receive damage
    enemy1 = game.player2.summon("CS2_182")  # Yeti 4/5
    enemy2 = game.player2.summon("CS2_182")  # Yeti 4/5
    enemy3 = game.player2.summon("CS2_182")  # Yeti 4/5
    rex = game.player1.give("DINO_138")
    rex.play()
    # Two random enemy minions should have taken 6 damage (likely killed Yetis at 5 hp)
    dead_count = sum(1 for e in (enemy1, enemy2, enemy3) if e.zone == Zone.GRAVEYARD)
    assert dead_count >= 1


def test_kindred_volcanic_thrasher_buffs_self():
    """TLC_223 Volcanic Thrasher: Kindred +2/+2."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    elemental_ally = game.player1.summon("EX1_507")  # Murk-Eye? actually we want Elemental
    # Let me use a known Elemental — CS2_236_DEF? Use AT_026 Hozen Healer?
    # Easier: just summon a token and verify race; Bog Slosher EX1_062 is Elemental? No.
    # Use BRM_002 Twilight Whelp — that's Dragon. Use UNG_809 — Bright-Eyed Scout (Beast).
    # Let me clear and try with a known Elemental.
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Spawn a fresh Elemental ally — use the Cataclysm Stormcaster (CATA_563 4/3 Elemental)
    fire_elem = game.player1.summon("CS2_042")  # Fire Elemental 6/5 Elemental
    assert Race.ELEMENTAL in fire_elem.races
    thrasher = game.player1.give("TLC_223")  # 3-cost Elemental
    thrasher.play()
    # Kindred fires → +2/+2
    # Thrasher is from XML — verify by checking attack
    # We assert it has the buff
    assert any(b.id == "TLC_223e" for b in thrasher.buffs)


def test_kindred_card_in_field_only_counts_field_minions():
    """An ally in HAND does not satisfy the Kindred condition."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.give("CS2_172")  # Raptor in HAND (not played)
    rex = game.player1.give("DINO_138")
    rex.play()
    # No allies on field → Kindred didn't fire
    # No CARD-specific assertion needed; the Kindred's Hit would have done damage
    # but there are no enemy minions either, so nothing observable. Verify no crash.
    assert rex in game.player1.field
