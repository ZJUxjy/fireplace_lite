from utils import *
from hearthstone.enums import CardClass, Race, Zone


def _set_mana(player):
    player.max_mana = 10
    player.used_mana = 0


def test_ohnahra_plays_top_three_cards_from_deck_at_end_of_turn():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    player.summon("EDR_031")
    top_cards = [player.card(WISP, zone=Zone.DECK), player.card("CS2_171", zone=Zone.DECK), player.card("CS2_172", zone=Zone.DECK)]

    game.end_turn()

    assert all(card.zone == Zone.PLAY for card in top_cards)


def test_beanstalk_brute_buffs_top_three_minions_in_deck():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    minions = [player.card(WISP, zone=Zone.DECK), player.card("CS2_171", zone=Zone.DECK), player.card("CS2_172", zone=Zone.DECK)]
    player.card(THE_COIN, zone=Zone.DECK)

    player.give("EDR_230").play()

    assert all((card.atk, card.max_health) == (card.data.atk + 4, card.data.health + 4) for card in minions)


def test_aspects_embrace_heals_draws_and_imbues_hero_power():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    player.hero.damage = 6
    drawn = player.card(WISP, zone=Zone.DECK)

    player.give("EDR_231").play()

    assert player.hero.damage == 2
    assert drawn in player.hand
    assert player.hero.power.id == "EDR_448p"


def test_typhoon_shuffles_every_minion_into_random_decks():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    minions = [player.summon(WISP), player.summon("CS2_171"), player.opponent.summon("CS2_172")]

    player.give("EDR_232").play()

    assert all(card.zone == Zone.DECK for card in minions)
    assert not player.field
    assert not player.opponent.field


def test_spirits_of_the_forest_summons_wolves_or_falcons():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_233").play(choose="EDR_233a")
    wolves = list(player.field)
    assert len(wolves) == 3
    assert all((wolf.atk, wolf.max_health, wolf.taunt) == (2, 3, True) for wolf in wolves)

    for minion in list(player.field):
        minion.zone = Zone.GRAVEYARD
    player.used_mana = 0
    player.give("EDR_233").play(choose="EDR_233b")

    assert len(player.field) == 2
    assert all((falcon.id, falcon.windfury) == ("EDR_233t2", True) for falcon in player.field)


def test_emerald_bounty_draws_two_cards_that_unlock_after_two_turns():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    drawn = [player.card(WISP, zone=Zone.DECK), player.card("CS2_171", zone=Zone.DECK)]

    player.give("EDR_234").play()

    assert all(card in player.hand for card in drawn)
    assert all(card.cant_play for card in drawn)

    game.end_turn()
    game.end_turn()
    assert all(card.cant_play for card in drawn)

    game.end_turn()
    game.end_turn()
    assert all(not card.cant_play for card in drawn)


def test_merithra_resurrects_different_friendly_minions_that_cost_eight_or_more():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    for card_id in ("EDR_031", "FIR_778", "EDR_031", WISP):
        card = player.card(card_id)
        card.zone = Zone.GRAVEYARD

    player.give("EDR_238").play()

    summoned_ids = [card.id for card in player.field]
    assert summoned_ids.count("EDR_031") == 1
    assert "FIR_778" in summoned_ids
    assert WISP not in summoned_ids


def test_glowroot_lure_costs_less_for_hero_power_uses():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.times_hero_power_used_this_game = 3

    lure = player.give("EDR_477")

    assert lure.cost == 3


def test_living_garden_imbues_and_discounts_a_minion_in_hand():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    minion = player.give("EDR_477")

    player.give("EDR_518").play()

    assert player.hero.power.id == "EDR_448p"
    assert minion.cost == 5


def test_blessing_of_the_wind_transforms_minion_and_plucky_podling_improves_it():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    player.give("EDR_518").play()
    podling = player.summon("EDR_529")

    player.hero.power.use(target=podling)

    assert podling.morphed is not None
    assert podling.morphed.cost == 4


def test_avatar_of_destruction_deathrattle_damages_enemy_minions():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    enemy = player.opponent.summon("EDR_477")

    player.summon("FIR_778").destroy()

    assert enemy.zone == Zone.GRAVEYARD


def test_flames_of_the_firelord_upgrades_when_holding_expensive_card():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon("EDR_031")

    player.give("FIR_923").play()
    assert enemy.damage == 4

    enemy.damage = 0
    player.used_mana = 0
    player.give("EDR_031")
    player.give("FIR_923").play()
    assert enemy.damage == 8


def test_emberscarred_whelp_discovers_five_cost_card_and_grants_next_turn_mana():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)

    player.give("FIR_927").play()
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert chosen in player.hand
    assert chosen.cost == 5

    player.max_mana = 1
    player.used_mana = 0
    game.end_turn()
    game.end_turn()
    assert player.max_mana == 2
    assert player.mana == 3
