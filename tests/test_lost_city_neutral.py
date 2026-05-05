from utils import *
from hearthstone.enums import CardClass, Zone


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def _add_to_deck(player, *card_ids):
    return [player.card(card_id, zone=Zone.DECK) for card_id in card_ids]


def test_khelos_egg_deathrattle_chain_hatches_taunt_beast():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    current = player.summon("DINO_410")

    for expected in ("DINO_410t2", "DINO_410t3", "DINO_410t4", "DINO_410t5", "DINO_410t"):
        current.destroy()
        current = player.field[-1]
        assert current.id == expected

    assert (current.atk, current.max_health) == (20, 20)
    assert current.taunt


def test_sacred_eggbearer_draws_zero_attack_minion():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    _add_to_deck(player, "DINO_410", "TLC_469")

    player.give("DINO_411").play()

    assert any(card.id == "DINO_410" for card in player.hand)
    assert any(card.id == "TLC_469" for card in player.deck)


def test_fodder_helper_buffs_friendly_beast_and_grants_rush():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    beast = player.summon("TLC_469")

    player.give("DINO_419").play(target=beast)

    assert (beast.atk, beast.max_health) == (6, 5)
    assert beast.rush


def test_undercover_cultist_has_bonus_attack_while_damaged():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    cultist = player.summon("TLC_101")

    assert cultist.atk == 2
    cultist.hit(1)
    assert cultist.atk == 5


def test_curious_explorer_discounts_opponent_hand_minion():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    target = player.opponent.give("TLC_469")
    explorer = player.summon("TLC_244")

    explorer.destroy()

    assert target.cost == 1


def test_blazing_accretion_deathrattle_splits_damage_among_enemies():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    samples = []

    def sample(options, count):
        samples.append((list(options), count))
        return list(options)[:count]

    game.random.sample = sample
    accretion = player.summon("TLC_249")

    accretion.destroy()

    assert len(samples) == 2
    assert all(count == 1 for _, count in samples)
    assert player.opponent.hero.damage == 2


def test_blob_of_tar_splits_into_poisonous_and_taunt_blobs():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    tar = player.summon("TLC_468")

    tar.destroy()

    thin = next(minion for minion in player.field if minion.id == "TLC_468t1")
    thick = next(minion for minion in player.field if minion.id == "TLC_468t2")
    assert thin.poisonous
    assert thick.taunt


def test_stubborn_guardian_mills_top_three_cards():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    cards = _add_to_deck(player, "TLC_469", "TLC_468", "TLC_467", "TLC_466")
    milled = cards[1:]
    guardian = player.summon("TLC_621")

    guardian.destroy()

    assert [card.id for card in player.deck] == ["TLC_469"]
    assert all(card.zone == Zone.REMOVEDFROMGAME for card in milled)


def test_crater_experiment_kindred_summons_copy():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)

    player.give("DINO_435").play()
    assert len([minion for minion in player.field if minion.id == "DINO_435"]) == 1

    game.end_turn()
    game.end_turn()
    player.give("DINO_435").play()

    assert len([minion for minion in player.field if minion.id == "DINO_435"]) == 3


def test_ancient_stegodon_choice_options():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)

    stegodon = player.give("TLC_242").play()
    player.choice.choose("poisonous")

    assert stegodon.poisonous


def test_ancient_raptor_can_gain_deathrattle_plants():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)

    raptor = player.give("TLC_245").play()
    player.choice.choose("plants")
    raptor.destroy()

    plants = [minion for minion in player.field if minion.id == "TLC_245t"]
    assert len(plants) == 2
    assert all((plant.atk, plant.max_health) == (1, 1) for plant in plants)


def test_ancient_pterrordax_stealth_expires_next_turn():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)

    pterror = player.give("TLC_246").play()
    player.choice.choose("stealth")

    assert pterror.stealthed
    game.end_turn()
    game.end_turn()
    assert not pterror.stealthed


def test_misty_mountain_hopster_doubles_next_kindred_effect():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_251").play()
    game.end_turn()
    game.end_turn()
    player.give("TLC_429").play()

    assert len([minion for minion in player.field if minion.id == "TLC_429t"]) == 4


def test_storyteller_buffs_one_friendly_minion_per_type():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.summon("TLC_254")
    beast1 = player.summon("TLC_469")
    beast2 = player.summon("TLC_250")
    murloc = player.summon("TLC_429")
    elemental = player.summon("TLC_468")

    game.end_turn()

    buffed_beasts = [minion for minion in (beast1, beast2) if minion.atk > minion.data.atk]
    assert len(buffed_beasts) == 1
    assert (murloc.atk, murloc.max_health) == (
        murloc.data.atk + 1,
        murloc.data.health + 1,
    )
    assert (elemental.atk, elemental.max_health) == (
        elemental.data.atk + 1,
        elemental.data.health + 1,
    )


def test_marshland_thresher_gains_divine_shield_after_spell():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    thresher = player.summon("TLC_256")

    player.give("TLC_446").play()

    assert thresher.divine_shield


def test_steamfin_thief_kindred_summons_rushing_murlocs():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_251").play()
    game.end_turn()
    game.end_turn()
    player.give("TLC_429").play()

    tokens = [minion for minion in player.field if minion.id == "TLC_429t"]
    assert len(tokens) == 4
    assert all(token.rush for token in tokens)


def test_scalhide_kodo_destroys_lowest_or_highest_attack_with_kindred():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    low = player.opponent.summon(WISP)
    high = player.opponent.summon("TLC_469")

    player.give("TLC_454").play()
    assert low.zone == Zone.GRAVEYARD
    assert high.zone == Zone.PLAY

    game.end_turn()
    game.end_turn()
    player.give("TLC_454").play()
    assert high.zone == Zone.GRAVEYARD


def test_tar_tyrant_has_bonus_attack_on_opponents_turn():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    tyrant = player.summon("TLC_605")

    assert tyrant.atk == 1
    game.end_turn()
    assert tyrant.atk == 7


def test_primal_sabretooth_copies_minion_it_kills_by_attacking():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    sabretooth = player.summon("TLC_247")
    target = player.opponent.summon(WISP)
    game.end_turn()
    game.end_turn()

    sabretooth.attack(target)

    copied = [card for card in player.hand if card.id == WISP]
    assert len(copied) == 1


def test_crater_gator_prevents_enemy_hero_healing_until_next_turn():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    enemy_hero = player.opponent.hero
    enemy_hero.hit(5)

    player.give("TLC_250").play()
    Heal(enemy_hero, 3).trigger(player)
    assert enemy_hero.damage == 5

    game.end_turn()
    game.end_turn()
    Heal(enemy_hero, 3).trigger(player)
    assert enemy_hero.damage == 2


def test_crystal_tender_catches_up_empty_mana_crystals():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player.opponent, 7)
    player.max_mana = 3
    player.used_mana = 0

    player.give("TLC_255").play()

    assert player.max_mana == 7
    assert player.mana == 1


def test_rockskipper_gives_one_cost_rock_that_deals_three():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon("TLC_454")

    player.give("TLC_427").play()
    rock = next(card for card in player.hand if card.id == "TLC_427t")
    assert rock.cost == 1

    rock.play(target=target)

    assert target.damage == 3


def test_krog_sets_enemy_minions_to_one_one_at_end_of_turn():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    target = player.opponent.summon("TLC_454")
    player.summon("TLC_480")

    game.end_turn()

    assert (target.atk, target.max_health, target.health) == (1, 1, 1)


def test_platysaur_discards_drawn_card_on_death():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    drawn = _add_to_deck(player, "TLC_469")[0]

    platysaur = player.give("TLC_603").play()
    assert drawn in player.hand

    platysaur.destroy()

    assert drawn.zone == Zone.REMOVEDFROMGAME


def test_cloud_serpent_copies_another_elemental_or_dragon_in_hand():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    player.give("TLC_468")

    player.give("TLC_888").play()

    assert len([card for card in player.hand if card.id == "TLC_468"]) == 2


def test_questing_assistant_hits_enemy_minion_after_quest_played():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon("TLC_454")

    player.give("TLC_830").play()
    player.give("TLC_987").play(target=target)

    assert target.damage == 3
