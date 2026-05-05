from utils import *
from hearthstone.enums import CardClass, CardType, Race, Zone


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def _clear_hand(player):
    for card in list(player.hand):
        card.zone = Zone.GRAVEYARD


def _add_to_deck(player, *card_ids):
    return [player.card(card_id, zone=Zone.DECK) for card_id in card_ids]


def test_techysaurus_discounts_for_played_cards_outside_starting_deck():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)

    player.give(WISP).play()
    player.give(MOONFIRE).play(target=player.opponent.hero)
    techysaurus = player.give("DINO_409")

    assert techysaurus.cost == 5
    assert techysaurus.taunt


def test_tribute_dance_transforms_target_into_different_board_minion():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)
    target = player.summon(WISP)
    form = player.summon(GOLDSHIRE_FOOTMAN)

    player.give("DINO_414").play(target=target)
    assert form in player.choice.cards
    player.choice.choose(form)

    assert target.zone == Zone.SETASIDE
    assert player.field[0].id == GOLDSHIRE_FOOTMAN


def test_sheep_mask_sets_stats_and_deathrattle_hits_all_minions():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)
    target = player.summon(TARGET_DUMMY)
    friendly = player.summon("DINO_409")
    enemy = player.opponent.summon("DINO_409")

    player.give("DINO_429").play(target=target)

    assert (target.atk, target.max_health) == (1, 1)
    assert target.has_deathrattle

    target.destroy()

    assert friendly.damage == 2
    assert enemy.damage == 2


def test_windswept_pageturner_hits_random_enemy_after_elemental_summon():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.summon("TLC_220")

    player.summon("TLC_226")

    assert player.opponent.hero.damage == 3


def test_conjured_bookkeeper_draws_spell_and_kindred_summons_copy():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)
    _add_to_deck(player, MOONFIRE)

    player.give("TLC_220").play()
    game.end_turn()
    game.end_turn()
    bookkeeper = player.summon("TLC_226")

    bookkeeper.destroy()

    assert player.hand[0].id == MOONFIRE
    assert any(minion.id == "TLC_226" for minion in player.field)


def test_relic_of_kings_discovers_large_spell_and_sets_cost_to_one():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)

    player.give("TLC_334").play()
    choice = player.choice

    assert all(card.type == CardType.SPELL and card.cost >= 8 for card in choice.cards)
    picked = choice.cards[0]
    choice.choose(picked)

    assert picked in player.hand
    assert picked.cost == 1


def test_story_of_the_waygate_discounts_generated_hand_cards_only():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)
    generated = player.give(PYROBLAST)
    started = player.give(FIREBALL)
    player.starting_deck.append(started)

    player.give("TLC_364").play()

    assert generated.cost == generated.data.cost - 1
    assert started.cost == started.data.cost


def test_storage_scuffle_costs_zero_after_discover_and_damages_minion():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)
    target = player.opponent.summon("DINO_409")
    storage = player.give("TLC_365")

    assert storage.cost == 3

    player.give("TLC_334").play()
    player.choice.choose(player.choice.cards[0])

    assert storage.cost == 0
    storage.play(target=target)
    assert target.damage == 3


def test_titanographer_osk_rolls_hand_ability_and_uses_it_on_play():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)
    osk = player.give("TLC_452")
    target = player.opponent.summon("DINO_409")
    osk._tlc_452_ability = "TLC_452t13"

    osk.play(target=target)

    assert target.damage == 5


def test_forbidden_sequence_rewards_origin_stone_after_seven_discovers():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)
    _clear_hand(player)

    player.give("TLC_460").play()
    quest = player.secrets[0]
    for _ in range(7):
        player.used_mana = 0
        player.give("TLC_334").play()
        player.choice.choose(player.choice.cards[0])

    assert quest.zone == Zone.GRAVEYARD
    assert any(card.id == "TLC_460t" for card in player.hand)


def test_scrappy_scavenger_discovers_card_matching_remaining_mana():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 6)

    player.give("TLC_461").play()

    assert player.choice
    assert player.mana == 5
    assert all(card.cost == 5 for card in player.choice.cards)


def test_unearthed_artifacts_summons_four_cost_minion_after_discover():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)

    player.give("TLC_462").play()
    first = player.field[-1]
    assert first.cost == 2

    player.give("TLC_334").play()
    player.choice.choose(player.choice.cards[0])
    player.used_mana = 0
    player.give("TLC_462").play()
    second = player.field[-1]

    assert second.cost == 4


def test_vault_breaker_reduces_discovered_card_cost():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)
    player.summon("TLC_483")

    player.give("TLC_334").play()
    picked = player.choice.cards[0]
    player.choice.choose(picked)

    assert picked in player.hand
    assert picked.cost == 0


def test_origin_stone_uses_unpicked_discover_options_and_loses_durability():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    _set_mana(player, 20)
    _clear_hand(player)

    weapon = player.give("TLC_460t").play()
    player.give("TLC_334").play()
    cards = list(player.choice.cards)
    player.choice.choose(cards[0])

    assert all(card in player.hand for card in cards)
    assert weapon.durability == weapon.max_durability - 1
