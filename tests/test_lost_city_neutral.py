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
