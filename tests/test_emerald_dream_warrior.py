from utils import *
from hearthstone.enums import CardClass, Race, Zone


def _set_mana(player):
    player.max_mana = 10
    player.used_mana = 0


def test_clutch_of_corruption_hatches_copy_of_chosen_friendly_dragon():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    dragon = player.summon("EDR_465")

    location = player.give("EDR_454").play()
    location.use(target=dragon)
    egg = player.field[-1]
    egg.destroy()

    assert egg.id == "EDR_454t"
    assert player.field[-1].id == "EDR_465"


def test_succumb_to_madness_resummons_discovered_dead_friendly_dragon():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    dragon = player.card("EDR_465")
    dragon.zone = Zone.GRAVEYARD

    player.give("EDR_455").play()
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert chosen.id == "EDR_465"
    assert player.field[-1].id == "EDR_465"


def test_darkrider_discovers_dragon_with_dark_gift_when_holding_dragon():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    player.give("EDR_465")

    player.give("EDR_456").play()
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert Race.DRAGON in chosen.races
    assert chosen in player.hand
    assert chosen._dark_gift


def test_brood_keeper_equips_sword_when_holding_dragon():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    player.give("EDR_465")

    player.give("EDR_457").play()

    assert player.weapon.id == "EDR_457t"
    assert (player.weapon.atk, player.weapon.durability) == (2, 2)


def test_afflicted_devastator_damages_friendly_minions_and_enemy_minions():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    friendly = player.summon("EDR_477")
    enemy = player.opponent.summon("EDR_477")

    devastator = player.give("EDR_459").play()
    assert friendly.damage == 3
    assert devastator.damage == 0

    devastator.destroy()
    assert enemy.damage == 3


def test_ysondre_summons_dragons_equal_to_times_died_this_game():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    player.summon("EDR_465").destroy()
    first_count = len(player.field)
    for minion in list(player.field):
        minion.zone = Zone.GRAVEYARD

    player.summon("EDR_465").destroy()

    assert first_count == 1
    assert len(player.field) == 2
    assert all(Race.DRAGON in minion.races for minion in player.field)


def test_eggbasher_damages_minion_and_gives_attack():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    target = player.summon("EDR_477")

    player.give("EDR_468").play(target=target)

    assert target.damage == 1
    assert target.atk == target.data.atk + 4


def test_tortolla_gains_armor_and_attack_after_taking_damage():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    tortolla = player.summon("EDR_471")

    game.cheat_action(tortolla, [Hit(tortolla, 1)])

    assert player.hero.armor == 1
    assert tortolla.atk == 2


def test_siphoning_growth_destroys_friendly_minion_to_gain_armor():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)

    player.give("EDR_531").play(target=target)

    assert target.zone == Zone.GRAVEYARD
    assert player.hero.armor == 8


def test_ominous_nightmares_damages_all_or_buffs_damaged_minion():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    friendly = player.summon("EDR_477")
    enemy = player.opponent.summon("EDR_477")

    player.give("EDR_570").play(choose="EDR_570A")
    assert friendly.damage == 1
    assert enemy.damage == 1

    player.used_mana = 0
    player.give("EDR_570").play(target=friendly, choose="EDR_570B")
    assert (friendly.atk, friendly.max_health) == (friendly.data.atk + 2, friendly.data.health + 2)


def test_keeper_of_flame_buffs_hand_minions_then_destroys_them_after_three_turns():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    minion = player.give(WISP)

    player.give("FIR_928").play()
    assert (minion.atk, minion.max_health) == (4, 4)

    for _ in range(6):
        game.end_turn()
    assert minion.zone == Zone.GRAVEYARD


def test_shadowflame_suffusion_deals_damage_and_discovers_dark_gift_warrior_minion():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon("EDR_477")

    player.give("FIR_939").play(target=enemy)
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert enemy.damage == 2
    assert CardClass.WARRIOR in chosen.classes
    assert chosen.type == CardType.MINION
    assert chosen._dark_gift


def test_dragon_turtle_rewards_holding_dark_gift_minion():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    gifted = player.give(WISP)
    gifted._dark_gift = True

    player.give("FIR_956").play()

    assert player.hero.atk == 3
    assert player.hero.armor == 6

    game.end_turn()
    assert player.hero.atk == 0
