from utils import *
from hearthstone.enums import CardClass, CardType, Race, SpellSchool, Zone


def _set_mana(player):
    player.max_mana = 10
    player.used_mana = 0


def _kill_friendly_minions(player, amount):
    for _ in range(amount):
        minion = player.summon(WISP)
        minion.destroy()


def test_aessina_deals_twenty_split_after_twenty_friendly_minions_died():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)
    _kill_friendly_minions(player, 20)

    player.give("EDR_430").play()

    assert player.opponent.hero.damage == 20


def test_qonzu_discovers_spell_then_keeps_or_puts_on_enemy_deck():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_517").play()
    assert player.choice
    assert all(card.type == CardType.SPELL for card in player.choice.cards)
    discovered = player.choice.cards[0]
    player.choice.choose(discovered)

    assert player.choice
    player.choice.choose(player.choice.cards[0])
    assert discovered in player.hand

    player.used_mana = 0
    player.give("EDR_517").play()
    second = player.choice.cards[0]
    player.choice.choose(second)
    player.choice.choose(player.choice.cards[1])

    assert player.opponent.deck[-1].id == second.id


def test_wisprider_imbues_and_triggers_wisp_hero_power():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_519").play()

    assert player.hero.power.id == "EDR_851p"
    assert len(player.field.filter(id="EDR_851t")) == 1
    assert player.opponent.hero.damage == 1


def test_forbidden_shrine_spends_all_available_mana():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)
    location = player.give("EDR_520").play()
    player.used_mana = 7

    location.use()

    assert player.used_mana == player.max_mana


def test_divination_destroys_friendly_wisp_to_draw_three():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)
    wisp = player.summon("EDR_851t")
    for _ in range(3):
        player.card(WISP).zone = Zone.DECK

    player.give("EDR_804").play()

    assert wisp.zone == Zone.GRAVEYARD
    assert len(player.hand) == 3


def test_spirit_gatherer_gets_wisp_and_imbues_hero_power():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_871").play()

    assert player.hand[0].id == "EDR_851t"
    assert player.hero.power.id == "EDR_851p"


def test_spark_of_life_discovers_mage_or_druid_spell():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_872").play()
    mage_choice = player.choice.cards[0]
    player.choice.choose(mage_choice)

    assert all(card.type == CardType.SPELL and card.data.card_class == CardClass.MAGE for card in player.choice.cards)
    player.choice.choose(player.choice.cards[0])

    player.used_mana = 0
    player.give("EDR_872").play()
    druid_choice = player.choice.cards[1]
    player.choice.choose(druid_choice)

    assert all(card.type == CardType.SPELL and card.data.card_class == CardClass.DRUID for card in player.choice.cards)


def test_stellar_balance_adds_moonfire_and_starfire_with_spell_damage_buff():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_874").play()

    generated = [card for card in player.hand if card.id in ("CS2_008", "EX1_173")]
    assert {card.id for card in generated} == {"CS2_008", "EX1_173"}
    assert all(any(buff.id == "EDR_874e" for buff in card.buffs) for card in generated)


def test_merry_moonkin_gains_armor_improved_by_wisps():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)
    player.summon("EDR_940")
    player.summon("EDR_851t")
    player.summon("EDR_851t")

    game.end_turn()

    assert player.hero.armor == 3


def test_starsurge_damage_improves_by_friendly_minions_that_died():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon("EX1_399")
    _kill_friendly_minions(player, 3)

    player.give("EDR_941").play(target=target)

    assert target.damage == 4


def test_scorching_winds_discards_fire_spell_for_extra_damage():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon("EX1_399")
    fire_spell = player.give("FIR_911")

    player.give("FIR_910").play(target=target)

    assert fire_spell.zone == Zone.REMOVEDFROMGAME
    assert target.damage == 6


def test_smoldering_grove_upgrades_each_turn_then_discards():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)
    grove = player.give("FIR_911")
    for _ in range(3):
        player.card(WISP).zone = Zone.DECK

    game.end_turn()
    game.end_turn()
    before = len(player.hand)
    grove.play()

    assert len(player.hand) == before + 1

    later = player.give("FIR_911")
    for _ in range(3):
        game.end_turn()
        game.end_turn()

    assert later.zone == Zone.REMOVEDFROMGAME


def test_inferno_herald_gets_discounted_elemental_after_fire_spell():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player)
    player.summon("FIR_913")

    player.give("FIR_911").play()

    elementals = [card for card in player.hand if card.race == Race.ELEMENTAL]
    assert len(elementals) == 1
    assert any(buff.id == "EDR_519e" for buff in elementals[0].buffs)
