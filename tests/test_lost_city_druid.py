from utils import *
from hearthstone.enums import CardClass, Race, Zone


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def _clear_hand(player):
    for card in list(player.hand):
        card.zone = Zone.GRAVEYARD


def _add_to_deck(player, *card_ids):
    return [player.card(card_id, zone=Zone.DECK) for card_id in card_ids]


def test_longneck_egg_summons_beast_and_buffs_friendly_minions():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    wisp = player.summon(WISP)
    egg = player.summon("DINO_130")

    egg.destroy()

    hatchling = player.field[-1]
    assert hatchling.id == "DINO_130t"
    assert Race.BEAST in hatchling.races
    assert (wisp.atk, wisp.max_health) == (2, 2)
    assert (hatchling.atk, hatchling.max_health) == (4, 4)


def test_seismopod_buffs_minions_in_hand_and_deck():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    hand_minion = player.give(WISP)
    player.give(MOONFIRE)
    deck_spell, deck_minion = _add_to_deck(player, MOONFIRE, GOLDSHIRE_FOOTMAN)
    seismopod = player.summon("DINO_421")

    seismopod.destroy()

    assert (hand_minion.atk, hand_minion.max_health) == (4, 4)
    assert (deck_minion.atk, deck_minion.max_health) == (4, 5)
    assert deck_spell.cost == deck_spell.data.cost


def test_panther_mask_sets_stats_grants_stealth_and_draws_two():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)
    _add_to_deck(player, GOLDSHIRE_FOOTMAN, TARGET_DUMMY)

    player.give("DINO_432").play(target=target)

    assert (target.atk, target.max_health) == (5, 4)
    assert target.stealthed
    assert len(player.hand) == 2


def test_treeees_summons_four_treants_that_attack_target():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon("DINO_421")

    player.give("TLC_230").play(target=target)

    assert target.damage == 8
    assert [card.id for card in player.graveyard].count("TLC_230t") == 4


def test_story_of_barnabus_draws_big_minion_buffs_health_and_gains_armor():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    _add_to_deck(player, WISP, "DINO_421")

    player.give("TLC_231").play()

    drawn = player.hand[-1]
    assert drawn.id == "DINO_421"
    assert drawn.max_health == 14
    assert player.hero.armor == 5


def test_ravenous_flock_summons_hatchlings_at_start_of_next_turn():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_232").play()
    game.end_turn()
    assert not player.field
    game.end_turn()

    assert [minion.id for minion in player.field] == ["TLC_237t"] * 3


def test_hatchery_helper_buffs_other_low_attack_minions_with_taunt():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    low = player.summon(WISP)
    high = player.summon("TLC_234")

    helper = player.give("TLC_233").play()

    assert (low.atk, low.max_health, low.taunt) == (2, 3, True)
    assert (high.atk, high.max_health, high.taunt) == (5, 1, False)
    assert helper.taunt is False


def test_eternal_bloodpetal_and_seedling_resummon_each_other():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    bloodpetal = player.summon("TLC_234")

    bloodpetal.destroy()
    seedling = player.field[0]
    assert seedling.id == "TLC_234t"

    seedling.destroy()
    assert player.field[0].id == "TLC_234"


def test_life_cycle_replaces_destroyed_minion_with_same_cost_minion():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon(GOLDSHIRE_FOOTMAN)

    player.give("TLC_235").play(target=target)

    assert target.zone == Zone.GRAVEYARD
    assert len(player.opponent.field) == 1
    assert player.opponent.field[0].cost == target.data.cost


def test_hybridization_draws_one_to_four_cost_minions_and_kindred_discounts_them():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    _clear_hand(player)

    player.give(WISP).play()
    game.end_turn()
    game.end_turn()
    _set_mana(player)
    _add_to_deck(player, GOLDSHIRE_FOOTMAN, "DINO_130", "TLC_233", "TLC_234")
    player.give("TLC_236").play()

    drawn = {card.id: card for card in player.hand}
    assert {"CS1_042", "DINO_130", "TLC_233", "TLC_234"} <= set(drawn)
    assert drawn["CS1_042"].cost == 0
    assert drawn["DINO_130"].cost == 1
    assert drawn["TLC_233"].cost == 2
    assert drawn["TLC_234"].cost == 3


def test_skyscreamer_eggs_deathrattle_summons_four_hatchlings():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    eggs = player.summon("TLC_237")

    eggs.destroy()

    assert [minion.id for minion in player.field] == ["TLC_237t"] * 4


def test_restore_the_wild_tracks_full_board_once_per_turn_and_rewards_everbloom():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    quest = player.give("TLC_239").play()

    for expected_progress in (1, 2, 3):
        for _ in range(game.MAX_MINIONS_ON_FIELD):
            player.summon(WISP)
        assert quest.progress == min(expected_progress, quest.progress_total)
        for minion in list(player.field):
            minion.destroy()
        if expected_progress < 3:
            game.end_turn()
            game.end_turn()

    assert quest.zone == Zone.GRAVEYARD
    assert any(card.id == "TLC_239t" for card in player.hand)


def test_everbloom_buffs_friendly_minions_after_hero_attacks():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    minion = player.summon(WISP)

    player.give("TLC_239t").play()
    player.give("CS2_005").play()
    player.hero.attack(player.opponent.hero)

    assert (minion.atk, minion.max_health) == (3, 3)


def test_loh_makes_friendly_minion_cards_cost_five_this_game():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    _set_mana(player)
    _clear_hand(player)
    cheap = player.give(WISP)
    expensive = player.give("DINO_421")
    spell = player.give(MOONFIRE)
    deck_minion = _add_to_deck(player, GOLDSHIRE_FOOTMAN)[0]

    player.give("TLC_257").play()

    assert cheap.cost == 5
    assert expensive.cost == 5
    assert spell.cost == spell.data.cost
    assert deck_minion.cost == 5
