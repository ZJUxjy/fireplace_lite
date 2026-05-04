from utils import *
from hearthstone.enums import CardClass, GameTag, Zone


def test_snuggle_teddy_gigantify_adds_gigantic_copy_with_keywords():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    teddy = player.give("MIS_300").play()

    assert teddy.taunt
    assert teddy.lifesteal
    assert teddy.data.tags[GameTag.ELUSIVE]
    gigantic = player.hand[0]
    assert gigantic.id == "MIS_300t"
    assert gigantic.data.atk == 8
    assert gigantic.data.health == 8
    assert gigantic.taunt
    assert gigantic.lifesteal
    assert gigantic.data.tags[GameTag.ELUSIVE]


def test_overgrown_beanstalk_summons_treant_and_draws_for_each_treant():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    existing = player.summon("MIS_301t")
    for card_id in (WISP, "CS2_182", "CS2_189"):
        player.card(card_id).zone = Zone.DECK

    player.give("MIS_301").play()

    treants = [minion for minion in player.field if minion.id == "MIS_301t"]
    assert existing in treants
    assert len(treants) == 2
    assert len(player.hand) == 2


def test_toyrantus_gains_stats_at_ten_mana_crystals():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    toyrantus = player.give("MIS_712").play()

    assert toyrantus.taunt
    assert toyrantus.data.tags[GameTag.ELUSIVE]
    assert toyrantus.atk == toyrantus.data.atk + 7
    assert toyrantus.max_health == toyrantus.data.health + 7


def test_woodland_wonders_summons_taunt_beetles_and_costs_less_with_spellpower():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    spellpower_minion = player.summon("CS2_142")
    spell = player.give("TOY_804")
    game.refresh_auras()

    assert spellpower_minion.spellpower == 1
    assert spell.cost == spell.data.cost - 3

    spell.play()

    beetles = [minion for minion in player.field if minion.id == "TOY_804t"]
    assert len(beetles) == 2
    assert all(beetle.taunt for beetle in beetles)


def test_ensmallen_reduces_cost_and_attack_of_minions_in_deck():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    minion = player.card("CS2_182")
    spell = player.card("CS2_029")
    minion.zone = Zone.DECK
    spell.zone = Zone.DECK

    player.give("TOY_805").play()

    assert minion.cost == max(0, minion.data.cost - 1)
    assert minion.atk == minion.data.atk - 1
    assert spell.cost == spell.data.cost


def test_magical_dollhouse_gives_temporary_spellpower():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    dollhouse = player.give("TOY_850").play()

    dollhouse.use()

    assert player.spellpower == 1

    game.end_turn()

    assert player.spellpower == 0
