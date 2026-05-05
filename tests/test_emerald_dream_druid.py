from utils import *
from hearthstone.enums import CardClass, CardType, Race, SpellSchool, Zone


def _set_mana(player):
    player.max_mana = 10
    player.used_mana = 0


def _empty_choices(game):
    for player in game.players:
        if player.choice:
            player.choice.choose()


def test_ward_of_earth_gains_armor_and_summons_taunt_five_cost_minion():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_060").play()

    assert player.hero.armor == 5
    assert len(player.field) == 1
    assert player.field[0].cost == 5
    assert player.field[0].taunt


def test_forest_lord_cenarius_chooses_three_times():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    other = player.summon(WISP)

    player.give("EDR_209").play()
    player.choice.choose(player.choice.cards[0])
    player.choice.choose(player.choice.cards[1])
    player.choice.choose(player.choice.cards[1])

    assert other.atk == other.data.atk + 1
    assert other.max_health == other.data.health + 3
    ancients = player.field.filter(id="EDR_209t5")
    assert len(ancients) == 2
    assert all(ancient.taunt for ancient in ancients)


def test_horn_of_plenty_discovers_discounted_nature_spell():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_270").play()

    assert player.choice
    assert all(
        card.type == CardType.SPELL
        and getattr(card.data, "spell_school", None) == SpellSchool.NATURE
        for card in player.choice.cards
    )
    choice = player.choice.cards[0]
    player.choice.choose(choice)

    assert choice in player.hand
    assert choice.cost == max(0, choice.data.cost - 2)


def test_grove_shaper_summons_treant_that_deathrattles_spell_copy():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    player.summon("EDR_271")

    spell = player.give("EDR_060")
    spell.play()

    treants = player.field.filter(id="EDR_271t")
    assert len(treants) == 1
    treant = treants[0]
    assert treant.atk == 2
    assert treant.max_health == 2

    treant.destroy()

    assert any(card.id == "EDR_060" for card in player.hand)


def test_evergreen_stag_has_elusive_lifesteal_and_taunt():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player

    stag = player.summon("EDR_272")

    assert stag.data.tags[GameTag.ELUSIVE]
    assert stag.lifesteal
    assert stag.taunt
    assert not stag.divine_shield


def test_symbiosis_discovers_choose_one_card_from_another_class():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_273").play()

    assert player.choice
    assert all(
        card.data.tags.get(GameTag.CHOOSE_ONE)
        and card.data.card_class not in (CardClass.DRUID, CardClass.NEUTRAL)
        for card in player.choice.cards
    )
    choice = player.choice.cards[0]
    player.choice.choose(choice)

    assert choice in player.hand


def test_reforestation_draws_choice_or_both_after_three_turns_in_hand():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    player.card("EDR_060").zone = Zone.DECK
    player.card(WISP).zone = Zone.DECK

    player.give("EDR_843").play()
    player.choice.choose(player.choice.cards[0])

    assert [card.id for card in player.hand] == ["EDR_060"]

    held = player.give("EDR_843")
    for _ in range(3):
        game.end_turn()
        game.end_turn()
    player.card("EDR_060").zone = Zone.DECK
    player.card(WISP).zone = Zone.DECK
    player.used_mana = 0

    held.play()

    assert {card.id for card in player.hand} >= {"EDR_060", WISP}


def test_hamuul_start_of_game_imbues_and_repeats_after_three_spells():
    player1 = Player("Player1", ["EDR_845", "EDR_060", "EDR_848"], CardClass.DRUID.default_hero)
    player1.cant_fatigue = True
    player2 = Player("Player2", [], CardClass.DRUID.default_hero)
    player2.cant_fatigue = True
    game = BaseTestGame(players=(player1, player2))
    game.start()
    _empty_choices(game)

    assert player1.hero.power.id == "EDR_847p"

    while game.current_player is not player1:
        game.end_turn()
    _set_mana(player1)
    for card_id in ("EDR_060", "EDR_848", "EDR_060"):
        card = player1.give(card_id)
        card.play()
        player1.used_mana = 0

    player1.hero.power.use()

    golem = player1.field[-1]
    assert golem.id == "EDR_847pt2"
    assert golem.atk == 2
    assert golem.max_health == 2


def test_dreambound_disciple_makes_next_hero_power_cost_zero_on_play_and_death():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)

    disciple = player.give("EDR_847").play()

    assert player.hero.power.cost == 0
    player.hero.power.use()
    assert player.hero.power.cost == player.hero.power.data.cost

    disciple.destroy()

    assert player.hero.power.cost == 0


def test_photosynthesis_heals_and_adds_three_random_druid_spells():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    player.hero.damage = 8

    player.give("EDR_848").play()

    assert player.hero.damage == 2
    added = [card for card in player.hand if card.type == CardType.SPELL]
    assert len(added) == 3
    assert all(card.data.card_class == CardClass.DRUID for card in added)


def test_overheat_buffs_minions_and_discards_nature_spell_for_second_buff():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    minion = player.summon(WISP)
    nature = player.give("EDR_060")

    player.give("FIR_906").play()

    assert nature.zone == Zone.REMOVEDFROMGAME
    assert minion.atk == minion.data.atk + 2
    assert minion.max_health == minion.data.health + 2


def test_amirdrassil_improves_each_use():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    player.card(WISP).zone = Zone.DECK
    player.card(WISP).zone = Zone.DECK
    location = player.give("FIR_907").play()
    player.used_mana = 5

    location.use()

    minions = [card for card in player.field if card.type == CardType.MINION]
    assert len(minions) == 1
    assert minions[0].cost == 1
    assert player.hero.armor == 1
    assert len(player.hand) == 1
    assert player.used_mana == 4

    location.location_exhausted = False
    location.use()

    minions = [card for card in player.field if card.type == CardType.MINION]
    assert len(minions) == 2
    assert minions[-1].cost == 2
    assert player.hero.armor == 3


def test_charred_chameleon_buffs_friendly_minion_after_hero_power_used():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)
    player.hero.power.use()
    player.used_mana = 0

    player.give("FIR_908").play()

    assert target.atk == target.data.atk + 1
    assert target.max_health == target.data.health + 2
    assert target.rush
