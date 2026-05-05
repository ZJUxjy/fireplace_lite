from utils import *
from hearthstone.enums import CardClass, CardType, Race, Zone


def _set_mana(player, amount=20):
    player.max_mana = amount
    player.used_mana = 0


def _clear_hand(player):
    for card in list(player.hand):
        card.zone = Zone.GRAVEYARD


def _add_to_deck(player, *card_ids):
    return [player.card(card_id, zone=Zone.DECK) for card_id in card_ids]


def test_devilsaur_mask_sets_stats_and_grants_charge():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)

    player.give("DINO_403").play(target=target)

    assert (target.atk, target.max_health) == (8, 8)
    assert target.charge


def test_ankylodon_summons_two_three_cost_beasts_that_attack():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    enemy = player.opponent.summon(TARGET_DUMMY)
    ankylodon = player.summon("DINO_422")

    ankylodon.destroy()

    assert len(player.field) == 2
    assert all(Race.BEAST in minion.races and minion.cost == 3 for minion in player.field)
    assert enemy.damage + player.opponent.hero.damage > 0


def test_raptor_nest_nurse_gets_random_one_cost_minion_and_spell():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    _clear_hand(player)

    nurse = player.give("DINO_434").play()
    assert len(player.hand) == 1
    assert player.hand[0].type == CardType.MINION
    assert player.hand[0].cost == 1

    nurse.destroy()
    assert any(card.type == CardType.SPELL and card.cost == 1 for card in player.hand)


def test_pterrorwing_ravager_kindred_costs_two_less():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("DINO_422").play()
    game.end_turn()
    game.end_turn()
    ravager = player.give("TLC_366")

    assert ravager.cost == 4


def test_dinositter_discounts_random_beast_in_hand_at_turn_end():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    beast = player.give("TLC_366")
    spell = player.give(MOONFIRE)

    player.summon("TLC_822")
    game.end_turn()

    assert beast.cost == beast.data.cost - 1
    assert spell.cost == spell.data.cost


def test_cower_in_fear_damages_minion_and_discounts_next_beast_this_turn_only():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon(TARGET_DUMMY)
    beast = player.give("TLC_366")

    player.give("TLC_823").play(target=target)
    assert target.zone == Zone.GRAVEYARD
    assert beast.cost == 4

    beast.play()
    other = player.give("DINO_422")
    assert other.cost == other.data.cost


def test_odd_map_offers_followup_when_discovered_beast_is_played_this_turn():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_824").play()
    first = player.choice.cards[0]
    player.choice.choose(first)
    _set_mana(player)
    first.play()

    assert player.choice is not None
    assert first not in player.choice.cards


def test_ravasaur_matriarch_kindred_hits_enemy_minion_for_its_attack():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon("DINO_421")

    player.give("TLC_366").play()
    game.end_turn()
    game.end_turn()
    player.give("TLC_825").play(target=enemy)

    assert enemy.damage == 5


def test_story_of_carnassa_shuffles_ten_raptors_that_draw_on_battlecry():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    _add_to_deck(player, WISP)

    player.give("TLC_826").play()

    raptors = [card for card in player.deck if card.id == "UNG_920t2"]
    assert len(raptors) == 10
    raptor = raptors[0]
    raptor.zone = Zone.HAND
    raptor.play()
    assert len(player.hand) == 1


def test_grazing_stegodon_gains_attack_in_play_hand_and_deck():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    field = player.summon("TLC_827")
    hand = player.give("TLC_827")
    deck = _add_to_deck(player, "TLC_827")[0]

    game.end_turn()

    assert field.atk == 1
    assert hand.atk == 1
    assert deck.atk == 1


def test_supreme_dinomancy_buffs_beasts_in_hand_deck_and_battlefield():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    field = player.summon("TLC_827")
    hand = player.give("TLC_366")
    deck = _add_to_deck(player, "DINO_422")[0]
    non_beast = player.give(WISP)

    player.give("TLC_828").play()

    assert (field.atk, field.max_health) == (2, 7)
    assert (hand.atk, hand.max_health) == (9, 7)
    assert (deck.atk, deck.max_health) == (9, 7)
    assert non_beast.atk == non_beast.data.atk


def test_food_chain_rewards_shokk_after_playing_one_three_five_seven_attack_beasts():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    quest = player.give("TLC_830").play()

    for card_id in ("UNG_076t1", "TRL_254t", "TLC_825", "TLC_366"):
        _set_mana(player)
        player.give(card_id).play()

    assert quest.zone == Zone.GRAVEYARD
    assert any(card.id == "TLC_830t" for card in player.hand)


def test_shokk_discovers_eight_six_and_four_attack_beasts_that_cost_two():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_830t").play()
    for expected_attack in (8, 6, 4):
        assert player.choice is not None
        choice = player.choice.cards[0]
        assert choice.atk == expected_attack
        player.choice.choose(choice)
        assert choice.cost == 2


def test_niri_doubles_one_cost_minion_stats_and_recasts_one_cost_spell():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    _clear_hand(player)

    player.summon("TLC_836")
    minion = player.give(GOLDSHIRE_FOOTMAN).play()
    spell = player.give("DS1_185")
    spell.play(target=player.opponent.hero)

    assert (minion.atk, minion.max_health) == (2, 4)
    assert player.opponent.hero.damage == 4
