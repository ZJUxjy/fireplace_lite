from utils import *
from hearthstone.enums import CardClass, CardType, SpellSchool, Zone


def test_malfunction_splits_extra_damage_when_deck_has_no_minions():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.opponent.summon("CS2_186")

    player.give("MIS_107").play()

    assert target.damage == 6


def test_buy_one_get_one_freeze_summons_frozen_copy():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.opponent.summon("CS2_182")

    player.give("MIS_302").play(target=target)

    copies = [minion for minion in player.field if minion.id == target.id]
    assert target.frozen
    assert len(copies) == 1
    assert copies[0].frozen


def test_darkmoon_magician_casts_random_spell_one_cost_higher_after_spell():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    game.random.seed(0)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    magician = player.summon("MIS_303")
    player.summon("CS2_231")

    player.give("GAME_005").play()

    assert magician in player.field
    assert any(card.id != "GAME_005" and card.cost == 1 for card in player.graveyard)


def test_hidden_objects_discovers_secret_and_sets_cost_to_one():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_037").play()

    assert player.choice is not None
    assert all(card.data.secret for card in player.choice.cards)
    choice = player.choice.cards[0]
    player.choice.choose(choice)

    assert choice in player.hand
    assert choice.cost == 1


def test_triplewick_trickster_deals_two_damage_three_times():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_370").play()

    assert player.opponent.hero.health == 24


def test_manufacturing_error_draws_three_and_discounts_without_deck_minions():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    drawn = [player.card(card_id) for card_id in ("CS2_029", "CS2_023", "CS2_025")]
    for card in drawn:
        card.zone = Zone.DECK

    player.give("TOY_371").play()

    assert all(card in player.hand for card in drawn)
    assert all(card.cost == max(0, card.data.cost - 3) for card in drawn)


def test_yogg_in_the_box_casts_five_random_spells():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_372").play()

    assert player.cards_played_this_game.filter(id="TOY_372")


def test_puzzlemaster_khadgar_equips_wisdomball_that_ticks_at_turn_end():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_373").play()

    assert player.weapon.id == "TOY_373t"
    assert player.weapon.durability == 6

    game.end_turn()

    assert player.weapon.durability == 5


def test_spot_the_difference_discovers_minion_and_repeats_without_deck_minions():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_374").play()

    first_choice = player.choice
    assert first_choice is not None
    assert all(
        card.type == CardType.MINION and card.cost == 3
        for card in first_choice.cards
    )
    first = first_choice.cards[0]
    first_choice.choose(first)

    assert any(minion.id == first.id for minion in player.field)
    second_choice = player.choice
    assert second_choice is not None
    second = second_choice.cards[0]
    second_choice.choose(second)

    summoned = [
        minion for minion in player.field if minion.id in (first.id, second.id)
    ]
    assert len(summoned) == 2


def test_sleet_skater_miniaturizes_freezes_and_gains_armor():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.opponent.summon("CS2_182")

    player.give("TOY_375").play(target=target)

    assert target.frozen
    assert player.hero.armor == target.atk
    assert any(card.id == "TOY_375t" for card in player.hand)


def test_watercolor_artist_draws_frost_spell_and_reduces_each_turn():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    frostbolt = player.card("CS2_024")
    frostbolt.zone = Zone.DECK

    player.give("TOY_376").play()

    assert frostbolt in player.hand
    assert frostbolt.data.spell_school == SpellSchool.FROST
    assert frostbolt.cost == frostbolt.data.cost

    game.end_turn()
    game.end_turn()

    assert frostbolt.cost == max(0, frostbolt.data.cost - 1)


def test_frost_lich_cross_stitch_summons_water_elemental_if_target_dies():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.opponent.summon(WISP)

    player.give("TOY_377").play(target=target)

    assert target.zone == Zone.GRAVEYARD
    elemental = player.field[-1]
    assert elemental.id == "CS2_033"


def test_galactic_projection_orb_recasts_one_spell_of_each_cost():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("CS2_024").play(target=player.opponent.hero)
    player.used_mana = 0
    player.give("TOY_378").play()

    assert player.opponent.hero.health == 24
