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
    # Put Deathwing in deck — zone setter handles deck placement
    deathwing = game.player1.card("CATA_190h")
    deathwing.zone = Zone.DECK
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


# === SOLDIER EFFECT ASSERTIONS (catch the bug where Soldier.play didn't fire) ===


def test_soldier_of_azshara_actually_buffs_hero_attack():
    """CATA_530 Fel Infusion summons Soldier of Azshara — its 'When summoned'
    must give the hero +herald_count Attack this turn.
    """
    game = prepare_empty_game()
    game.player1.max_mana = 10
    assert game.player1.hero.atk == 0
    spell = game.player1.give("CATA_530")
    spell.play()
    # herald_count is 1 → hero gets +1 atk this turn
    assert game.player1.hero.atk == 1


def test_soldier_of_azshara_scales_with_herald_count():
    """Second Herald → soldier's effect triggers with herald_count=2."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # First Fel Infusion: herald_count=1, +1 atk
    game.player1.used_mana = 0
    game.player1.give("CATA_530").play()
    # Soldier from first cast disappears at end of turn? Actually the buff is
    # tag-one-turn-effect so it persists until turn end. Field has Soldier.
    base_atk = game.player1.hero.atk
    assert base_atk == 1
    # Second Fel Infusion within same turn: herald_count=2, soldier buffs +2
    game.player1.used_mana = 0
    game.player1.give("CATA_530").play()
    # Hero now has 1 (from first soldier) + 2 (from second soldier) = 3 atk
    assert game.player1.hero.atk == 3


def test_soldier_of_sinestra_gives_discounted_spell():
    """CATA_158 Maniacal Follower deathrattle: Herald (Soldier of Sinestra).
    The Soldier's 'When summoned' must give a random spell to hand at
    cost-reduced by herald_count.
    """
    game = prepare_empty_game()
    game.player1.max_mana = 10
    follower = game.player1.give("CATA_158")
    follower.play()
    initial_hand_size = len(game.player1.hand)
    # Kill follower → deathrattle → Herald → Sinestra Soldier → spell to hand
    while follower.health > 0 and follower in game.player1.field:
        game.player1.give(MOONFIRE).play(target=follower)
    # Hand should have grown by at least 1 (the spell from soldier's effect)
    assert len(game.player1.hand) > initial_hand_size


def test_scorching_ravager_actually_gives_soldier_rush():
    """CATA_160 Scorching Ravager: Battlecry: Herald. Give the Soldier Rush.
    Verifies the SetTags(Herald.CARD, ...) call site works.
    """
    game = prepare_empty_game()
    game.player1.max_mana = 10
    ravager = game.player1.give("CATA_160")
    ravager.play()
    soldiers = [m for m in game.player1.field if m.id == "CATA_580t"]
    assert len(soldiers) == 1
    assert soldiers[0].rush  # Rush granted via Herald.CARD


def test_ultraxion_reduces_deathwing_cost_by_herald_count():
    """CATA_497 Ultraxion: cost reduction = herald_count after Herald."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Put Deathwing in deck (assigning zone moves the card into the deck;
    # do NOT also call .append or you get a duplicate reference).
    deathwing = game.player1.card("CATA_190h")
    deathwing.zone = Zone.DECK
    base_cost = deathwing.cost
    assert sum(1 for c in game.player1.deck if c.id == "CATA_190h") == 1
    # First Ultraxion → herald_count becomes 1 → -1 cost
    game.player1.used_mana = 0
    game.player1.give("CATA_497").play()
    assert deathwing.cost == base_cost - 1


def test_herald_count_3_does_not_re_morph_progeny():
    """After Deathwing has morphed to Progeny, further Heralds don't re-fire."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    deathwing = game.player1.card("CATA_190h")
    deathwing.zone = Zone.DECK  # moves into deck — do NOT also append
    # Herald 3 times
    for _ in range(3):
        game.player1.used_mana = 0
        game.player1.give("CATA_722").play()
    # Exactly one Progeny in the deck (no duplicates from re-firing)
    progenies = [c for c in game.player1.deck if c.id == "CATA_190t14"]
    assert len(progenies) == 1
    # No CATA_190h left
    assert all(c.id != "CATA_190h" for c in game.player1.deck)


def test_deathwing_in_hand_also_morphs():
    """Deathwing in hand (not deck) should also morph after 2 Heralds."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    deathwing = game.player1.give("CATA_190h")  # in hand
    assert deathwing.id == "CATA_190h"
    # Herald twice
    for _ in range(2):
        game.player1.used_mana = 0
        game.player1.give("CATA_722").play()
    # Hand should now have Progeny instead of CATA_190h
    progeny = next((c for c in game.player1.hand if c.id == "CATA_190t14"), None)
    assert progeny is not None
    assert all(c.id != "CATA_190h" for c in game.player1.hand)


# === SUMMON-TRIGGER ON NON-HERALD PATHS ===
# Real Hearthstone "When summoned, ..." fires on any summon — not just
# the path that originally created the token. Verified via direct summon.


def test_soldier_effect_fires_on_direct_summon():
    """Direct player.summon('CATA_525t') should fire its 'When summoned'."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    assert game.player1.hero.atk == 0
    # No Herald yet — controller.herald_count == 0, but soldier's max(1, count)
    # gives at least +1 atk.
    game.player1.summon("CATA_525t")
    assert game.player1.hero.atk >= 1


def test_soldier_effect_fires_after_herald_then_direct_summon():
    """Herald once (count=1) → direct summon a 2nd Soldier → buff stacks."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.give("CATA_530").play()  # Herald → +1 atk
    assert game.player1.hero.atk == 1
    # Direct summon (e.g., as if a copy effect cloned the soldier)
    game.player1.summon("CATA_525t")
    # herald_count is still 1, so direct summon adds another +1 → total 2
    assert game.player1.hero.atk == 2


def test_sinestra_summon_trigger_via_direct_summon():
    """Soldier of Sinestra direct-summoned should still grant a discounted spell."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    initial_hand = len(game.player1.hand)
    game.player1.summon("CATA_158t")
    # Hand should have 1 more card (a discounted random spell).
    assert len(game.player1.hand) == initial_hand + 1
