#!/usr/bin/env python
"""Tests for the INFUSE keyword (Murder at Castle Nathria)."""
from utils import *
from hearthstone.enums import Zone


def _summon_and_kill_friendly_minion(game, n=1):
    """Helper: summon n friendly minions and kill them via Moonfire."""
    for _ in range(n):
        wisp = game.player1.summon(WISP)  # 1/1
        # Kill with Moonfire (1 damage)
        game.player1.give(MOONFIRE).play(target=wisp)


def test_infuse_progresses_on_friendly_death():
    """A card with INFUSE in hand increments progress when a friendly minion dies."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    imp = game.player1.give("REV_244")  # Infuse threshold = 3
    assert imp.progress == 0
    _summon_and_kill_friendly_minion(game, 1)
    assert imp.progress == 1


def test_infuse_morphs_when_threshold_reached():
    """When threshold is reached, the card morphs to its infused form."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    imp = game.player1.give("REV_244")  # threshold 3
    _summon_and_kill_friendly_minion(game, 3)
    morphed = next((c for c in game.player1.hand if c.id == "REV_244t"), None)
    assert morphed is not None
    assert imp.morphed is morphed


def test_infuse_does_not_morph_below_threshold():
    """The card stays in original form below threshold."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    imp = game.player1.give("REV_244")  # threshold 3
    _summon_and_kill_friendly_minion(game, 2)
    # Still in original form
    assert imp in game.player1.hand
    assert imp.id == "REV_244"


def test_infused_form_has_stronger_battlecry():
    """REV_244t: summons 2 copies (vs original which summons 1)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    imp = game.player1.give("REV_244")
    _summon_and_kill_friendly_minion(game, 3)
    morphed = next(c for c in game.player1.hand if c.id == "REV_244t")
    morphed.play()
    copies = [m for m in game.player1.field if m.id == "REV_244t"]
    # Original on field + 2 summoned copies = 3
    assert len(copies) == 3


def test_infuse_only_friendly_deaths_count():
    """Enemy minion deaths should NOT count toward Infuse progress."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    imp = game.player1.give("REV_244")
    # Summon and kill 3 enemy minions
    for _ in range(3):
        wisp = game.player2.summon(WISP)
        game.player1.give(MOONFIRE).play(target=wisp)
    # Progress should be 0, not 3
    assert imp.progress == 0
    assert imp.id == "REV_244"


def test_infuse_threshold_4_card():
    """REV_019 has threshold 4."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    fool = game.player1.give("REV_019")
    _summon_and_kill_friendly_minion(game, 3)
    assert fool.id == "REV_019"  # not yet
    _summon_and_kill_friendly_minion(game, 1)
    morphed = next((c for c in game.player1.hand if c.id == "REV_019t"), None)
    assert morphed is not None


# === Final batch of INFUSE cards ===


def test_rev_336_plot_of_sin_default():
    """REV_336 default form summons two 2/2 Treants."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    spell = game.player1.give("REV_336")
    spell.play()
    treants = [m for m in game.player1.field if m.id == "REV_336t2"]
    assert len(treants) == 2


def test_rev_336_plot_of_sin_infused():
    """REV_336 infused form summons two 5/5 Ancients."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    spell = game.player1.give("REV_336")
    _summon_and_kill_friendly_minion(game, 2)
    morphed = next((c for c in game.player1.hand if c.id == "REV_336t4"), None)
    assert morphed is not None
    morphed.play()
    ancients = [m for m in game.player1.field if m.id == "REV_336t3"]
    assert len(ancients) == 2


def test_rev_350_frenzied_fangs_infused_buffs_bats():
    """REV_350 infused form summons 2 Bats and gives them +1/+2."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    spell = game.player1.give("REV_350")
    _summon_and_kill_friendly_minion(game, 2)
    morphed = next((c for c in game.player1.hand if c.id == "REV_350t2"), None)
    assert morphed is not None
    morphed.play()
    bats = [m for m in game.player1.field if m.id == "REV_350t"]
    assert len(bats) == 2
    # Each bat is base 2/1 with +1/+2 buff -> 3/3
    for b in bats:
        assert b.atk == 3
        assert b.health == 3


def test_rev_353_altimor_chain_morphs_through_three_stages():
    """REV_353 -> REV_353t -> REV_353t2 (each tier needs 3 deaths)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    altimor = game.player1.give("REV_353")
    assert altimor.id == "REV_353"
    _summon_and_kill_friendly_minion(game, 3)
    altimor_mid = next((c for c in game.player1.hand if c.id == "REV_353t"), None)
    assert altimor_mid is not None
    _summon_and_kill_friendly_minion(game, 3)
    altimor_full = next((c for c in game.player1.hand if c.id == "REV_353t2"), None)
    assert altimor_full is not None


def test_rev_353t2_summons_all_three_companions():
    """Fully-infused Altimor summons Hecutis + Barghast + Margore."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    altimor = game.player1.give("REV_353t2")
    altimor.play()
    ids = {m.id for m in game.player1.field}
    assert "REV_353t3" in ids  # Hecutis
    assert "REV_353t4" in ids  # Barghast
    assert "REV_353t5" in ids  # Margore


def test_rev_958_buffet_biggun_infused_gives_divine_shield():
    """Infused Biggun summons 2 Recruits with +2 atk and Divine Shield."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    biggun = game.player1.give("REV_958t")
    biggun.play()
    recruits = [m for m in game.player1.field if m.id == "CS2_101t"]
    assert len(recruits) == 2
    for r in recruits:
        assert r.atk >= 3  # base 1 + 2 buff
        assert r.divine_shield


def test_rev_935_party_favor_summons_totem_at_turn_end():
    """REV_935 summons 1 random basic Totem at end of turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    totem = game.player1.give("REV_935")
    totem.play()
    initial_field = len(game.player1.field)
    game.end_turn()  # player1's turn ends
    # Should have summoned 1 totem
    assert len(game.player1.field) == initial_field + 1


def test_rev_906_sire_denathrius_default_battlecry():
    """REV_906 deals 5 damage spread among enemies."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    sire = game.player1.give("REV_906")
    initial_health = game.player2.hero.health
    sire.play()
    # 5 damage total among enemies; with no enemy minions, all to face
    assert game.player2.hero.health < initial_health


def test_maw_003_infused_summons_all_four_totems():
    """Infused Totemic Evidence summons all 4 basic totems."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    spell = game.player1.give("MAW_003t")
    spell.play()
    totem_ids = {m.id for m in game.player1.field}
    expected = {"CS2_050", "CS2_051", "CS2_052", "NEW1_009"}
    assert expected.issubset(totem_ids)
