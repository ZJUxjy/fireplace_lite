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
