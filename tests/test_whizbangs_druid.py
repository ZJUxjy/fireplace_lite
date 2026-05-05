from utils import *
from hearthstone.enums import CardClass, CardType, GameTag, Rarity, Zone


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


def test_sparkling_phial_discounts_next_card_by_damage_dealt():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    next_card = player.give("CS2_182")

    player.give("TOY_800").play(target=player.opponent.hero)

    assert player.opponent.hero.health == 28
    assert next_card.cost == max(0, next_card.data.cost - 2)

    next_card.play()

    assert not any(buff.id == "TOY_800e1" for buff in player.buffs)


def test_wind_up_sapling_refreshes_one_mana_crystal():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 5

    player.give("TOY_802").play()

    assert player.used_mana == 6


def test_jade_display_deathrattle_buffs_future_displays_and_shuffles_two():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    display = player.give("TOY_803").play()

    display.destroy()

    shuffled = [card for card in player.deck if card.id == "TOY_803"]
    assert len(shuffled) == 2
    assert all(card.atk == card.data.atk + 1 for card in shuffled)
    assert all(card.max_health == card.data.health + 1 for card in shuffled)


def test_sky_mother_aviana_shuffles_ten_one_cost_legendary_minions():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_806").play()

    assert len(player.deck) == 10
    assert all(card.type == CardType.MINION for card in player.deck)
    assert all(card.data.rarity == Rarity.LEGENDARY for card in player.deck)
    assert all(card.cost == 1 for card in player.deck)


def test_owlonius_doubles_spell_damage_bonus():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.summon("CS2_142")
    player.summon("TOY_807")
    game.refresh_auras()

    assert player.spellpower == 2
    assert player.get_spell_damage(2) == 8


def test_bottomless_toy_chest_discovers_from_deck_and_copies_with_spellpower():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.summon("CS2_142")
    wisp = player.card(WISP)
    wisp.zone = Zone.DECK

    player.give("TOY_851").play()

    assert player.choice is not None
    assert player.choice.cards == [wisp]
    player.choice.choose(wisp)

    wisps = [card for card in player.hand if card.id == WISP]
    assert len(wisps) == 2
    assert wisp in wisps
