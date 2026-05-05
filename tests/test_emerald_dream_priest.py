from utils import *
from hearthstone.enums import CardClass, CardType, Zone


def _set_mana(player):
    player.max_mana = 10
    player.used_mana = 0


def _cast_three_spells(player):
    for _ in range(3):
        _set_mana(player)
        player.give(THE_COIN).play()


def test_lunarwing_messenger_has_lifesteal_and_imbues_moon_hero_power():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)

    messenger = player.give("EDR_449").play()

    assert messenger.lifesteal
    assert player.hero.power.id == "EDR_449p"


def test_blessing_of_the_moon_discovers_discounted_temporary_priest_card():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    player.give("EDR_449").play()
    player.used_mana = 0

    player.hero.power.use()

    assert player.choice
    assert all(CardClass.PRIEST in card.data.classes for card in player.choice.cards)
    assert all(card.type in (CardType.MINION, CardType.SPELL) for card in player.choice.cards)
    chosen = player.choice.cards[0]
    printed_cost = chosen.data.cost
    player.choice.choose(chosen)

    assert chosen in player.hand
    assert chosen.cost == max(0, printed_cost - 1)

    game.end_turn()

    assert chosen.zone == Zone.REMOVEDFROMGAME


def test_wish_of_the_new_moon_damages_minion_and_gains_lifesteal_after_spells():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    player.hero.damage = 10
    target = player.opponent.summon("CS2_200")
    _cast_three_spells(player)

    player.give("EDR_460").play(target=target)

    assert target.damage == 6
    assert player.hero.damage == 4


def test_ritual_of_the_new_moon_summons_three_or_six_cost_minions():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_461").play()

    assert len(player.field) == 2
    assert all(minion.cost == 3 for minion in player.field)

    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _cast_three_spells(player)
    _set_mana(player)

    player.give("EDR_461").play()

    assert len(player.field) == 2
    assert all(minion.cost == 6 for minion in player.field)


def test_selenic_drake_gets_random_dragon_at_end_of_turn():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.summon("EDR_462")

    game.end_turn()

    assert len(player.hand) == 1
    assert Race.DRAGON in player.hand[0].races


def test_twilight_influence_choice_destroy_or_summon():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon(WISP)

    player.give("EDR_463").play(target=target)
    player.choice.choose(player.choice.cards[0])

    assert target.zone == Zone.GRAVEYARD

    player.used_mana = 0
    other = player.opponent.summon(WISP)
    player.give("EDR_463").play(target=other)
    player.choice.choose(player.choice.cards[1])

    assert len(player.field) == 1
    assert player.field[0].cost == 2


def test_tyrande_makes_next_three_spells_cast_twice():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_464").play()
    player.used_mana = 0
    player.give(MOONFIRE).play(target=player.opponent.hero)

    assert player.opponent.hero.damage == 2


def test_weaver_of_the_cycle_deals_three_if_holding_expensive_spell():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    player.give("EDR_461")

    player.give("EDR_472").play()

    assert player.opponent.hero.damage == 3


def test_kaldorei_priestess_reduces_enemy_attack_until_next_turn_and_imbues():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon("CS2_182")

    player.give("EDR_970").play()

    assert enemy.atk == enemy.data.atk - 2
    assert player.hero.power.id == "EDR_449p"

    game.end_turn()
    game.end_turn()

    assert enemy.atk == enemy.data.atk


def test_aviana_starts_lunar_cycle_that_makes_cards_cost_one():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    held = player.give("EDR_462")

    player.give("EDR_895").play()

    for _ in range(3):
        game.end_turn()
        game.end_turn()

    assert held.cost == 1


def test_spirit_of_the_kaldorei_gains_stats_after_hero_power():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    player.hero.power.use(target=player.hero)
    player.used_mana = 0

    spirit = player.give("FIR_777").play()

    assert (spirit.atk, spirit.max_health) == (4, 6)


def test_smoldering_ascent_upgrades_each_turn_then_discards():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")
    ascent = player.give("FIR_916")

    game.end_turn()
    game.end_turn()
    _set_mana(player)
    ascent.play()

    assert enemy.damage == 2

    later = player.give("FIR_916")
    for _ in range(3):
        game.end_turn()
        game.end_turn()

    assert later.zone == Zone.REMOVEDFROMGAME


def test_light_of_the_new_moon_buffs_and_returns_after_three_spells():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    target = player.summon(WISP)
    _cast_three_spells(player)
    _set_mana(player)

    player.give("FIR_918").play(target=target)

    assert (target.atk, target.max_health) == (4, 4)
    assert player.hand.filter(id="FIR_918")


def test_moonwell_damages_enemies_and_heals_friendlies():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    player.hero.damage = 6
    friendly = player.summon("CS2_182")
    friendly.damage = 3
    enemy = player.opponent.summon("CS2_182")

    player.give("EDR_476").play()

    assert player.opponent.hero.damage == 4
    assert enemy.damage == 4
    assert player.hero.damage == 2
    assert friendly.damage == 0
