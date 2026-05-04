from utils import *
from hearthstone.enums import CardClass


def test_shambling_zombietank_spends_corpses_to_summon_copy():
    """Shambling Zombietank spends 5 Corpses to summon a copy."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.corpses = 5

    player.give("TOY_827").play()

    tanks = [minion for minion in player.field if minion.id == "TOY_827"]
    assert len(tanks) == 2
    assert player.corpses == 0


def test_shambling_zombietank_does_not_copy_without_corpses():
    """Shambling Zombietank does not copy itself without 5 Corpses."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.corpses = 4

    player.give("TOY_827").play()

    assert [minion.id for minion in player.field].count("TOY_827") == 1
    assert player.corpses == 4


def test_rambunctious_stuffy_gains_reborn_after_frost_spell():
    """Rambunctious Stuffy gains Reborn after its controller casts a Frost spell."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    stuffy = player.summon("TOY_821")

    player.give("CS2_024").play(target=player.opponent.hero)

    assert stuffy.reborn


def test_rambunctious_stuffy_ignores_non_frost_spell():
    """Rambunctious Stuffy does not gain Reborn from a non-Frost spell."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    stuffy = player.summon("TOY_821")

    player.give("CS2_029").play(target=player.opponent.hero)

    assert not stuffy.reborn


def test_helm_of_humiliation_debuffs_target_and_buffs_hand_minion():
    """Helm of Humiliation gives a minion -5/-5 and a random hand minion +5/+5."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.opponent.summon("EX1_572")
    hand_minion = player.give("CS2_231")
    base_hand_stats = (hand_minion.atk, hand_minion.health)

    player.give("MIS_100").play(target=target)

    assert (target.atk, target.health) == (
        max(0, target.data.atk - 5),
        target.data.health - 5,
    )
    assert (hand_minion.atk, hand_minion.health) == (
        base_hand_stats[0] + 5,
        base_hand_stats[1] + 5,
    )


def test_darkthorn_quilter_splits_attack_damage_among_enemies_at_turn_end():
    """Darkthorn Quilter splits its Attack as damage among enemies at end of turn."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    quilter = player.summon("TOY_824")
    player.opponent.summon("EX1_572")
    player.opponent.summon("EX1_572")
    total_health_before = player.opponent.hero.health + sum(
        minion.health for minion in player.opponent.field
    )

    game.end_turn()

    total_health_after = player.opponent.hero.health + sum(
        minion.health for minion in player.opponent.field
    )
    assert total_health_after == total_health_before - quilter.atk


def test_lesser_spinel_spellstone_buffs_undead_in_hand():
    """Lesser Spinel Spellstone gives Undead in hand +1/+1."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    undead = player.give("ICC_026")
    non_undead = player.give("CS2_182")

    player.give("TOY_825").play()

    assert (undead.atk, undead.health) == (undead.data.atk + 1, undead.data.health + 1)
    assert (non_undead.atk, non_undead.health) == (
        non_undead.data.atk,
        non_undead.data.health,
    )


def test_spinel_spellstone_buffs_undead_in_hand_by_2():
    """Spinel Spellstone gives Undead in hand +2/+2."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    undead = player.give("ICC_026")

    player.give("TOY_825t").play()

    assert (undead.atk, undead.health) == (undead.data.atk + 2, undead.data.health + 2)


def test_greater_spinel_spellstone_buffs_undead_in_hand_by_3():
    """Greater Spinel Spellstone gives Undead in hand +3/+3."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    undead = player.give("ICC_026")

    player.give("TOY_825t2").play()

    assert (undead.atk, undead.health) == (undead.data.atk + 3, undead.data.health + 3)


def test_lesser_spinel_spellstone_upgrades_after_five_friendly_minions_die():
    """Lesser Spinel Spellstone upgrades after its controller gains 5 Corpses."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.give("TOY_825")

    for _ in range(5):
        minion = player.summon(WISP)
        player.give(MOONFIRE).play(target=minion)

    assert "TOY_825" not in [card.id for card in player.hand]
    assert "TOY_825t" in [card.id for card in player.hand]


def test_spinel_spellstone_upgrades_to_greater_after_five_more_deaths():
    """Spinel Spellstone upgrades to Greater after 5 more Corpses."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.give("TOY_825t")

    for _ in range(5):
        minion = player.summon(WISP)
        player.give(MOONFIRE).play(target=minion)

    assert "TOY_825t" not in [card.id for card in player.hand]
    assert "TOY_825t2" in [card.id for card in player.hand]


def test_threads_of_despair_gives_all_current_minions_deathrattle():
    """Threads of Despair gives all current minions a board-damage Deathrattle."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    doomed = player.summon(WISP)
    friendly_survivor = player.summon("EX1_572")
    enemy_survivor = player.opponent.summon("EX1_572")
    late_minion = None

    player.give("TOY_826").play()
    late_minion = player.summon("EX1_572")

    player.give(MOONFIRE).play(target=doomed)

    assert doomed.dead
    assert friendly_survivor.health == friendly_survivor.data.health - 1
    assert enemy_survivor.health == enemy_survivor.data.health - 1
    assert late_minion.health == late_minion.data.health - 1


def test_foamrender_spends_corpses_to_gain_durability_on_hero_attack():
    """Foamrender spends 3 Corpses to gain Durability whenever the hero attacks."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.corpses = 3
    weapon = player.give("MIS_101").play()

    player.hero.attack(player.opponent.hero)

    assert player.corpses == 0
    assert player.weapon is weapon
    assert weapon.durability == 1


def test_foamrender_does_not_gain_durability_without_corpses():
    """Foamrender does not gain Durability unless 3 Corpses can be spent."""
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.corpses = 2

    player.give("MIS_101").play()
    player.hero.attack(player.opponent.hero)

    assert player.corpses == 2
    assert player.weapon is None
