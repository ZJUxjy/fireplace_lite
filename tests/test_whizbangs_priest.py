from utils import *
from hearthstone.enums import CardClass, CardType, Rarity, Zone


def test_delayed_product_discovers_summons_and_dormants_big_minion():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("MIS_305").play()

    assert player.choice is not None
    assert all(
        card.type == CardType.MINION and card.cost >= 8
        for card in player.choice.cards
    )
    choice = player.choice.cards[0]
    player.choice.choose(choice)

    summoned = player.field[-1]
    assert summoned.id == choice.id
    assert summoned.dormant
    assert summoned.dormant_turns == 2


def test_funhouse_mirror_summons_copy_that_attacks_original():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.opponent.summon("CS2_182")

    player.give("MIS_714").play(target=target)

    copy = player.field[-1]
    assert copy.id == target.id
    assert target.damage == copy.atk
    assert copy.damage == target.atk


def test_puppet_theatre_location_gives_one_cost_one_one_enemy_copy():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.opponent.summon("CS2_182")

    theatre = player.give("MIS_919").play()
    theatre.use(target=target)

    copy = player.hand[-1]
    assert copy.id == target.id
    assert copy.atk == 1
    assert copy.max_health == 1
    assert copy.cost == 1
    assert theatre.durability == theatre.max_durability - 1


def test_clay_matriarch_miniaturizes_and_deathrattle_summons_elusive_whelp():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    matriarch = player.give("TOY_380").play()

    assert matriarch.taunt
    assert player.hand[0].id == "TOY_380t"

    matriarch.destroy()

    whelp = player.field[-1]
    assert whelp.id == "TOY_380t2"
    assert whelp.data.tags.get(GameTag.ELUSIVE)


def test_papercraft_angel_sets_hero_power_cost_to_zero_while_in_play():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    angel = player.give("TOY_381").play()
    game.refresh_auras()

    assert player.hero.power.cost == 0

    angel.destroy()
    game.refresh_auras()

    assert player.hero.power.cost == player.hero.power.data.cost


def test_careless_crafter_deathrattle_gives_two_zero_cost_bandages():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.hero.damage = 5

    crafter = player.summon("TOY_382")
    crafter.destroy()

    bandages = player.hand.filter(id="TOY_382t")
    assert len(bandages) == 2
    assert all(card.cost == 0 for card in bandages)

    bandages[0].play(target=player.hero)

    assert player.hero.damage == 2


def test_raza_shuffles_five_dead_friendly_minion_copies_that_cost_zero():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    dead_ids = ["CS2_231", "CS2_182", "CS2_189", "EX1_066", "EX1_015", "NEW1_023"]
    for card_id in dead_ids:
        minion = player.summon(card_id)
        minion.destroy()

    player.give("TOY_383").play()

    shuffled = [card for card in player.deck if card.id in dead_ids]
    assert len(shuffled) == 5
    assert all(card.cost == 0 for card in shuffled)


def test_purifying_power_silences_friendly_minions_then_buffs_them():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.summon("TOY_813")

    player.give("TOY_384").play()

    assert not target.taunt
    assert target.atk == target.data.atk + 1
    assert target.max_health == target.data.health + 2


def test_timewinder_zarimi_queues_extra_turn_after_eight_other_dragons():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    for _ in range(8):
        dragon = player.give("TOY_386")
        dragon.play()
        dragon.destroy()
        player.used_mana = 0

    player.give("TOY_385").play()

    assert game.next_players[0] is player
    assert player._timewinder_zarimi_used


def test_scale_replica_draws_lowest_and_highest_cost_dragons():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    low = player.card("TOY_386")
    high = player.card("TOY_380")
    other = player.card(WISP)
    for card in (low, high, other):
        card.zone = Zone.DECK

    player.give("TOY_387").play()

    assert low in player.hand
    assert high in player.hand
    assert other in player.deck


def test_chalk_artist_draws_minion_and_transforms_to_legendary_with_original_stats():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.card(WISP)
    target.zone = Zone.DECK

    player.give("TOY_388").play()

    transformed = player.hand[-1]
    assert transformed.id != WISP
    assert transformed.rarity == Rarity.LEGENDARY
    assert transformed.cost == target.data.cost
    assert transformed.atk == target.data.atk
    assert transformed.max_health == target.data.health


def test_fly_off_the_shelves_repeats_for_each_dragon_in_hand():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target1 = player.opponent.summon("CS2_231")
    target2 = player.opponent.summon("CS2_182")
    player.give("TOY_386")
    player.give("TOY_380")

    player.give("TOY_714").play()

    assert target1.zone == Zone.GRAVEYARD
    assert target2.damage == 3


def test_repackage_stuffs_all_minions_into_box_in_opponent_deck():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    opponent = player.opponent
    player.max_mana = 10
    player.used_mana = 0
    friendly = player.summon(WISP)
    enemy = opponent.summon("CS2_182")

    player.give("TOY_879").play()

    assert friendly.zone == Zone.SETASIDE
    assert enemy.zone == Zone.SETASIDE
    boxes = opponent.deck.filter(id="TOY_879t")
    assert len(boxes) == 1
    assert boxes[0].cost == 2

    box = boxes[0]
    box.draw()
    game.end_turn()
    opponent.max_mana = 10
    opponent.used_mana = 0
    box.play()

    assert any(card.id == WISP for card in opponent.hand)
    assert any(card.id == "CS2_182" for card in opponent.hand)
