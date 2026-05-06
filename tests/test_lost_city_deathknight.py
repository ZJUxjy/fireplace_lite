from utils import *
from hearthstone.enums import CardClass, Zone

from fireplace.actions import Hit


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def test_umbras_story_discovers_summons_and_triggers_large_deathrattle_minion():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    _set_mana(player)

    player.give("DINO_415").play()
    choice = player.choice.cards[0]
    assert choice.has_deathrattle
    assert choice.cost >= 5
    player.choice.choose(choice)

    assert player.field
    assert choice.zone in (Zone.PLAY, Zone.SETASIDE, Zone.GRAVEYARD)


def test_hollowhorn_reborns_after_friendly_death_by_spending_corpses():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.corpses = 3
    hollowhorn = player.summon("DINO_416")
    friendly = player.summon(WISP)

    friendly.destroy()

    assert hollowhorn.reborn
    assert player.corpses == 0


def test_rite_of_rest_gives_attack_rush_and_end_turn_death():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    _set_mana(player)
    minion = player.summon(GOLDSHIRE_FOOTMAN)

    player.give("DINO_417").play()

    assert minion.atk == minion.data.atk + 1
    assert minion.rush

    game.end_turn()

    assert minion.zone == Zone.GRAVEYARD


def test_chillfallen_baronsaurus_deathrattle_hits_three_random_enemies():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    baronsaurus = player.summon("TLC_401")

    baronsaurus.destroy()

    assert player.opponent.hero.damage == 18


def test_dread_raptor_draws_small_deathrattle_and_kindred_sets_cost_zero():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    _set_mana(player)
    drawn = player.card("TLC_443", zone=Zone.DECK)
    player.card(WISP, zone=Zone.DECK)

    player.give("TLC_401").play()
    game.end_turn()
    game.end_turn()
    player.give("TLC_432").play()

    assert drawn in player.hand
    assert drawn.cost == 0


def test_reanimate_the_terror_tracks_corpses_spent_and_rewards_terrax():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    _set_mana(player)
    player.corpses = 15

    quest = player.give("TLC_433").play()
    for _ in range(3):
        player.give("TLC_436").play()

    assert quest.zone == Zone.GRAVEYARD
    assert any(card.id == "TLC_433t" for card in player.hand)
    assert player.corpses == 0


def test_terrax_deathrattle_opens_tomb_that_resummons_terrax():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    terrax = player.summon("TLC_433t")

    terrax.destroy()
    tomb = player.field[0]

    assert tomb.id == "TLC_433t2"

    tomb.destroy()

    assert any(minion.id == "TLC_433t" for minion in player.field)


def test_necrotic_archaeology_spends_corpses_to_keep_all_three_undead():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    _set_mana(player)
    player.corpses = 5

    before = len(player.hand)
    player.give("TLC_434").play()

    undead = [card for card in player.hand[before:] if Race.UNDEAD in card.races]
    assert len(undead) == 3
    assert player.corpses == 0


def test_burndown_map_offers_followup_if_discovered_card_is_played_this_turn():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_435").play()
    first = player.choice.cards[0]
    player.choice.choose(first)
    first.play()

    assert player.choice is not None
    assert first not in player.choice.cards


def test_reanimated_pterrordax_costs_corpses_instead_of_mana():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    _set_mana(player)
    player.corpses = 5
    player.used_mana = player.max_mana

    player.give("TLC_436").play()

    assert player.corpses == 0
    assert player.used_mana == player.max_mana


def test_tar_tide_damages_enemy_minions_and_taxes_enemy_minions_in_hand():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon("EX1_399")
    taxed = player.opponent.give(GOLDSHIRE_FOOTMAN)

    player.give("TLC_439").play()

    assert enemy.damage == 2
    assert taxed.cost == taxed.data.cost + 2


def test_cryo_sleep_draws_twice_with_frost_kindred():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon("EX1_399")
    player.card(WISP, zone=Zone.DECK)
    player.card(GOLDSHIRE_FOOTMAN, zone=Zone.DECK)
    player.card(WISP, zone=Zone.DECK)
    player.card(GOLDSHIRE_FOOTMAN, zone=Zone.DECK)

    player.give("TLC_440").play(target=enemy)
    game.end_turn()
    game.end_turn()
    before = len(player.hand)
    player.give("TLC_440").play(target=enemy)

    assert len(player.hand) == before + 2


def test_reluctant_handler_reborn_and_deathrattle_summons_taunt_undead_beast():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    handler = player.summon("TLC_443")

    assert handler.reborn
    handler.destroy()

    token = player.field[-1]
    assert token.id == "TLC_443t"
    assert token.taunt
    assert Race.UNDEAD in token.races
    assert Race.BEAST in token.races


def test_high_cultist_summons_two_deathrattles_from_deck_and_they_fight():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    _set_mana(player)
    first = player.card("TLC_443", zone=Zone.DECK)
    second = player.card("TLC_401", zone=Zone.DECK)

    player.give("TLC_810").play()

    assert first.zone != Zone.DECK
    assert second.zone != Zone.DECK
    assert first.damage > 0 or first.zone == Zone.GRAVEYARD
    assert second.damage > 0 or second.zone == Zone.GRAVEYARD
