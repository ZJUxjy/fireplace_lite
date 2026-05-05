from utils import *
from hearthstone.enums import CardClass, CardType, GameTag, Race, Zone


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def _add_to_deck(player, *card_ids):
    return [player.card(card_id, zone=Zone.DECK) for card_id in card_ids]


def test_milreles_in_hand_becomes_opponents_last_minion_as_three_four():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    opponent = player.opponent
    _set_mana(player)
    _set_mana(opponent)
    milreles = player.give("DINO_407")

    game.end_turn()
    opponent.give(WISP).play()

    copied = player.hand[0]
    assert copied.id == WISP
    assert (copied.atk, copied.max_health) == (3, 4)


def test_prismatic_fang_shuffles_leftmost_hand_and_deathrattle_draws_two():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    left = player.give(WISP)
    player.give("CS2_231")
    _add_to_deck(player, "CS2_171", "CS2_172")

    weapon = player.give("DINO_408").play()

    assert left in player.deck
    weapon.destroy()
    assert len(player.hand) >= 2


def test_costume_merchant_gives_other_class_mask_and_combo_discounts_it():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)

    player.give(WISP).play()
    player.give("DINO_427").play()
    gained = player.hand[-1]

    assert gained.id.startswith("DINO_")
    assert gained.card_class != CardClass.ROGUE
    assert gained.cost <= gained.data.cost - 2


def test_the_gravitational_displacer_rewards_five_shuffles():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_513").play()
    for _ in range(5):
        game.queue_actions(player.hero, [Shuffle(player, WISP)])

    assert any(card.id == "TLC_513t" for card in player.hand)


def test_relic_vendor_discovers_legendary_and_shuffles_other_options():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_514").play()
    picked = player.choice.cards[0]
    others = [card.id for card in player.choice.cards if card is not picked]
    player.choice.choose(picked)

    assert picked in player.hand
    assert all(any(card.id == card_id for card in player.deck) for card_id in others)


def test_cultist_map_discovers_from_deck_and_followup_if_played_this_turn():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    _add_to_deck(player, WISP, "CS2_171", "CS2_172")

    player.give("TLC_515").play()
    first = player.choice.cards[0]
    remaining = [card.id for card in player.choice.cards if card is not first]
    player.choice.choose(first)
    _set_mana(player)
    first.play()

    assert player.choice
    assert {card.id for card in player.choice.cards} == set(remaining)


def test_neferset_weaponsmith_gives_other_class_weapon_and_combo_buffs_attack():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)

    player.give(WISP).play()
    player.give("TLC_516").play()
    weapon = player.hand[-1]

    assert weapon.type == CardType.WEAPON
    assert weapon.card_class != CardClass.ROGUE
    assert weapon.atk >= weapon.data.atk + 2


def test_trapdoor_kicker_damage_scales_with_shuffle_count():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon("CS2_232")

    for _ in range(3):
        game.queue_actions(player.hero, [Shuffle(player, WISP)])
    player.give("TLC_517").play(target=target)

    assert target.damage == 3


def test_interrogation_shuffles_three_ambush_ninjas_that_summon_when_drawn():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_518").play()
    ninjas = [card for card in player.deck if card.id == "TLC_513t2"]
    assert len(ninjas) == 3

    ForceDraw(ninjas[0]).trigger(player)
    assert any(minion.id == "TLC_513t2" for minion in player.field)


def test_stalk_the_prey_kindred_summons_two_stealthed_poisonous_spitters():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)

    _add_to_deck(player, WISP)
    player.give("TLC_515").play()
    player.choice.choose(player.choice.cards[0])
    game.end_turn()
    game.end_turn()
    player.give("TLC_519").play()

    spitters = [minion for minion in player.field if minion.id == "TLC_519t"]
    assert len(spitters) == 2
    assert all(minion.stealthed and minion.poisonous for minion in spitters)


def test_canopy_stalker_cost_reduces_for_each_shuffle():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    stalker = player.give("TLC_520")

    for _ in range(4):
        game.queue_actions(player.hero, [Shuffle(player, WISP)])

    assert stalker.cost == 2


def test_lookout_chooses_enemy_deck_card_to_put_on_top():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    enemy_cards = _add_to_deck(player.opponent, WISP, "CS2_171", "CS2_172")

    player.give("TLC_521").play()
    picked = player.choice.cards[-1]
    player.choice.choose(picked)

    assert player.opponent.deck[-1].id == picked.id


def test_opex_stealth_and_casts_fan_on_battlecry_combo_deathrattle():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    enemy1 = player.opponent.summon("CS2_232")
    enemy2 = player.opponent.summon("CS2_120")
    _add_to_deck(player, "CS2_171")

    player.give(WISP).play()
    opex = player.give("TLC_522").play()

    assert opex.stealthed
    assert enemy1.damage >= 2
    assert enemy2.damage >= 2

    opex.destroy()
    assert len(player.hand) >= 1
