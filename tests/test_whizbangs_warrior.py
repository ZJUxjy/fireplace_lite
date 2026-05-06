from utils import *
from hearthstone.enums import CardClass, GameTag, Zone

from fireplace.cards.utils import GainArmor


def test_standardized_pack_adds_five_temporary_taunt_minions():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("MIS_705").play()

    generated = list(player.hand)
    assert len(generated) == 5
    assert all(card.data.tags.get(GameTag.TAUNT) for card in generated)

    game.end_turn()

    assert all(card.zone == Zone.REMOVEDFROMGAME for card in generated)


def test_safety_expert_has_rush_and_shuffles_three_bombs():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    expert = player.summon("MIS_711")

    assert expert.rush

    expert.destroy()

    assert len(player.opponent.deck.filter(id="BOT_511t")) == 3


def test_part_scrapper_spends_armor_to_discount_next_mech():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.hero.armor = 7
    first = player.give("TOY_908")
    second = player.give("TOY_606")

    player.give("MIS_902").play()
    game.refresh_auras()

    assert player.hero.armor == 2
    assert first.cost == first.data.cost - 5
    assert second.cost == second.data.cost - 5

    first.play()
    game.refresh_auras()

    assert second.cost == second.data.cost


def test_chemical_spill_summons_highest_cost_minion_and_damages_it():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    low = player.give(WISP)
    high = player.give("MIS_711")

    player.give("TOY_602").play()

    assert high in player.field
    assert low in player.hand
    assert high.damage == 5


def test_wreckem_and_deckem_copy_attacks_then_dies():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    mech = player.summon("TOY_908")
    enemy = player.opponent.summon("CS2_200")

    player.give("TOY_603").play(target=mech)

    assert mech in player.field
    assert enemy.damage >= mech.atk or player.opponent.hero.damage >= mech.atk
    assert any(card.id == "TOY_908" for card in player.graveyard)


def test_boom_wrench_miniaturizes_and_triggers_friendly_mech_deathrattle():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    dummy = player.summon("TOY_606")
    enemy = player.opponent.summon("CS2_200")

    wrench = player.give("TOY_604").play()

    assert any(card.id == "TOY_604t" for card in player.hand)

    wrench.destroy()

    assert dummy in player.field
    assert enemy.damage or enemy.zone == Zone.GRAVEYARD


def test_quality_assurance_draws_two_taunt_minions():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    taunts = [player.card("TOY_606"), player.card("MIS_703")]
    other = player.card(WISP)
    for card in taunts + [other]:
        card.zone = Zone.DECK

    player.give("TOY_605").play()

    assert all(card in player.hand for card in taunts)
    assert other in player.deck


def test_testing_dummy_deathrattle_splits_damage_among_enemy_minions():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    dummy = player.summon("TOY_606")
    enemies = [player.opponent.summon("CS2_200"), player.opponent.summon("CS2_200")]

    dummy.destroy()

    assert any(enemy.damage or enemy.zone == Zone.GRAVEYARD for enemy in enemies)
    assert not any(minion.damage for minion in player.field)


def test_inventor_boom_resurrects_two_big_mechs_that_attack():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    first = player.summon("TOY_606")
    second = player.summon("TOY_908")
    first.destroy()
    second.destroy()
    enemies = [player.opponent.summon("CS2_101t"), player.opponent.summon("CS2_101t")]

    player.give("TOY_607").play()

    assert {"TOY_606", "TOY_908"}.issubset({card.id for card in player.field})
    assert (
        any(enemy.damage or enemy.zone == Zone.GRAVEYARD for enemy in enemies)
        or player.opponent.hero.damage
    )


def test_lab_patron_copies_once_per_turn_when_you_gain_armor():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    patron = player.summon("TOY_651")

    game.cheat_action(patron, [GainArmor(player.hero, 2)])

    assert len(player.field.filter(id="TOY_651")) == 2

    game.cheat_action(patron, [GainArmor(player.hero, 2)])

    assert len(player.field.filter(id="TOY_651")) == 2


def test_botface_gets_two_random_minis_after_taking_damage():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    botface = player.summon("TOY_906")

    game.cheat_action(botface, [Hit(botface, 1)])

    assert len(player.hand) == 2
    assert all(card.data.tags.get(GameTag.MINI) for card in player.hand)


def test_safety_goggles_cost_zero_without_armor_and_gains_six():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    goggles = player.give("TOY_907")
    game.refresh_auras()

    assert goggles.cost == 0

    goggles.play()

    assert player.hero.armor == 6


def test_fireworker_deathrattle_summons_two_boom_bots():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    fireworker = player.summon("TOY_908")

    fireworker.destroy()

    assert len(player.field.filter(id="GVG_110t")) == 2
