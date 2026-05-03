#!/usr/bin/env python
"""Tests for Phase 6 modern mechanics: HERALD, SHATTER (CATACLYSM-specific)."""
from utils import *


# === HERALD ===

def test_herald_increments_count_and_summons_soldier():
    """CATA_580 Cataclysmic War Axe: Battlecry: Herald (Soldier of Ragnaros)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    assert game.player1.herald_count == 0
    axe = game.player1.give("CATA_580")
    axe.play()
    assert game.player1.herald_count == 1
    soldiers = [m for m in game.player1.field if m.id == "CATA_580t"]
    assert len(soldiers) == 1


def test_herald_stacks_across_multiple_plays():
    """3 herald plays => count=3."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    for _ in range(3):
        game.player1.used_mana = 0
        c = game.player1.give("CATA_722")  # Envoy of the End — Battlecry: Herald
        c.play()
    assert game.player1.herald_count == 3


def test_herald_via_deathrattle():
    """CATA_158 Maniacal Follower: Stealth + Deathrattle: Herald."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    follower = game.player1.give("CATA_158")
    follower.play()
    assert game.player1.herald_count == 0
    # Kill it (5/5 Stealth)
    while follower.health > 0 and follower in game.player1.field:
        game.player1.give(MOONFIRE).play(target=follower)
    assert game.player1.herald_count == 1
    # Soldier of Sinestra summoned
    soldiers = [m for m in game.player1.field if m.id == "CATA_158t"]
    assert len(soldiers) == 1


def test_herald_twice_morphs_deathwing_in_deck():
    """Herald twice should morph CATA_190h Deathwing in deck to CATA_190t14."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Put Deathwing in deck
    deathwing = game.player1.card("CATA_190h")
    deathwing.zone = Zone.DECK
    game.player1.deck.append(deathwing)
    # Herald twice
    for _ in range(2):
        game.player1.used_mana = 0
        c = game.player1.give("CATA_722")
        c.play()
    # Deathwing should now be morphed to Progeny
    progeny = next(
        (c for c in game.player1.deck if c.id == "CATA_190t14"), None
    )
    assert progeny is not None


def test_herald_does_not_morph_deathwing_after_one_herald():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    deathwing = game.player1.card("CATA_190h")
    deathwing.zone = Zone.DECK
    game.player1.deck.append(deathwing)
    c = game.player1.give("CATA_722")
    c.play()
    # Deathwing still in deck as CATA_190h
    still_dw = next((d for d in game.player1.deck if d.id == "CATA_190h"), None)
    assert still_dw is not None


def test_herald_via_location_action():
    """CATA_492 Twilight Altar: Use: Herald, draw a card."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Stack deck with one card so draw succeeds
    drawn_card = game.player1.card("CS2_065")
    drawn_card.zone = Zone.DECK
    game.player1.deck.append(drawn_card)
    altar = game.player1.give("CATA_492")
    altar.play()
    altar.cooldown = False  # bypass placement cooldown for the test
    initial_hand = len(game.player1.hand)
    altar.use()
    # Heralded once + drew a card
    assert game.player1.herald_count == 1
    soldiers = [m for m in game.player1.field if m.id == "CATA_725t"]
    assert len(soldiers) == 1
    assert len(game.player1.hand) == initial_hand + 1


# === SHATTER ===

def test_shatter_adds_halves_to_hand():
    """CATA_134 Wildwood Circle: full effect + adds two halves to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    spell = game.player1.give("CATA_134")
    spell.play()
    # Two Treants on field
    treants = [m for m in game.player1.field if m.id == "CATA_134t3"]
    assert len(treants) == 2
    # Two halves in hand
    hand_ids = {c.id for c in game.player1.hand}
    assert "CATA_134t" in hand_ids
    assert "CATA_134t2" in hand_ids


def test_shatter_half_1_does_partial_effect():
    """CATA_134t (half 1) summons two 2/2 Treants, no buff."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    half = game.player1.give("CATA_134t")
    half.play()
    treants = [m for m in game.player1.field if m.id == "CATA_134t3"]
    assert len(treants) == 2


def test_shatter_half_2_does_partial_effect():
    """CATA_134t2 (half 2) only buffs minions with the deathrattle, no Treants."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    wisp = game.player1.give(WISP)
    wisp.play()
    half = game.player1.give("CATA_134t2")
    half.play()
    # No new Treants summoned
    treants = [m for m in game.player1.field if m.id == "CATA_134t3"]
    assert len(treants) == 0


def test_shatter_arcane_flow_full_effect():
    """CATA_489 Arcane Flow full version: 4 dmg + 2 dmg AoE + halves added."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Add a target enemy minion
    target = game.player2.summon("CS2_182")  # Chillwind Yeti 4/5
    target_initial_health = target.health
    spell = game.player1.give("CATA_489")
    spell.play(target=target)
    # 4 + 2 = 6 damage to target
    assert target.zone == Zone.GRAVEYARD or target.health == target_initial_health - 6
    # Two halves added to hand
    hand_ids = {c.id for c in game.player1.hand}
    assert "CATA_489t" in hand_ids
    assert "CATA_489t2" in hand_ids
