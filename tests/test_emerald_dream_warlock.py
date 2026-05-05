from utils import *
from hearthstone.enums import CardClass, Race, Zone

from fireplace.actions import Hit


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def test_rotten_apple_heals_now_then_damages_on_next_two_own_turns():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    player.hero.damage = 15

    player.give("EDR_482").play()
    assert player.hero.damage == 3

    game.end_turn()
    assert player.hero.damage == 6
    game.end_turn()
    game.end_turn()
    assert player.hero.damage == 9
    game.end_turn()
    game.end_turn()
    assert player.hero.damage == 9


def test_fractured_power_destroys_crystal_then_restores_two_after_two_turns():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player, amount=5)

    player.give("EDR_483").play()
    assert player.max_mana == 4

    for _ in range(4):
        game.end_turn()
    assert player.max_mana == 8


def test_rotheart_dryad_deathrattle_draws_large_minion():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.card(WISP, zone=Zone.DECK)
    large = player.card("EDR_489", zone=Zone.DECK)

    player.summon("EDR_485").destroy()

    assert large in player.hand
    assert all(card.id != WISP for card in player.hand)


def test_wallow_copies_dark_gifts_given_to_minions_while_in_hand():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    wallow = player.give("EDR_487")

    player.give("EDR_488").play()
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert chosen in player.hand
    assert chosen.has_deathrattle
    assert getattr(chosen, "_dark_gift", False)
    assert getattr(wallow, "_dark_gift", False)
    assert wallow._edr_487_gifts == 1


def test_avant_gardening_discovers_deathrattle_minion_with_dark_gift():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_488").play()
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert chosen in player.hand
    assert chosen.type == CardType.MINION
    assert chosen.has_deathrattle
    assert chosen._dark_gift


def test_agamaggan_makes_next_card_cost_opponents_health_instead_of_mana():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_489").play()
    player.used_mana = player.max_mana

    player.give(GOLDSHIRE_FOOTMAN).play()

    assert player.used_mana == player.max_mana
    assert player.opponent.hero.damage == 1


def test_sleep_paralysis_summons_taunt_demons_or_destroys_enemy_minion():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_490").play(choose="EDR_490a")
    terrors = player.field.filter(id="EDR_490t")
    assert len(terrors) == 2
    assert all(terror.taunt and terror.cant_attack for terror in terrors)

    enemy = player.opponent.summon(WISP)
    player.used_mana = 0
    player.give("EDR_490").play(target=enemy, choose="EDR_490b")
    assert enemy.zone == Zone.GRAVEYARD


def test_archdruid_of_thorns_gains_deathrattles_from_minions_that_died_this_turn():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    large = player.card("EDR_489", zone=Zone.DECK)
    player.summon("EDR_485").destroy()

    archdruid = player.give("EDR_491").play()
    archdruid.destroy()

    assert large in player.hand


def test_hungering_ancient_eats_deck_minion_and_deathrattle_adds_it_to_hand():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    eaten = player.card("EDR_489", zone=Zone.DECK)

    ancient = player.give("EDR_494").play()
    game.end_turn()

    assert eaten.zone == Zone.GRAVEYARD
    assert (ancient.atk, ancient.max_health) == (
        ancient.data.atk + eaten.data.atk,
        ancient.data.health + eaten.data.health,
    )

    ancient.destroy()
    assert player.hand[-1].id == "EDR_489"


def test_overgrown_horror_reduces_dark_gift_minions_in_hand():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    gifted = player.give("EDR_489")
    gifted._dark_gift = True
    normal = player.give(GOLDSHIRE_FOOTMAN)

    horror = player.give("EDR_654").play()

    assert horror.taunt
    assert gifted.cost == gifted.data.cost - 2
    assert normal.cost == normal.data.cost


def test_shadowflame_stalker_discovers_demon_with_dark_gift():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)

    player.give("FIR_924").play()
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert chosen in player.hand
    assert Race.DEMON in chosen.races
    assert chosen._dark_gift


def test_conflagrate_damages_minion_and_its_owner_draws():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon("EDR_471")
    drawn = player.opponent.card(WISP, zone=Zone.DECK)

    player.give("FIR_954").play(target=enemy)

    assert enemy.damage == 5
    assert drawn in player.opponent.hand


def test_emberroot_destroyer_hits_enemy_minion_when_hero_takes_damage_on_own_turn():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    destroyer = player.summon("FIR_955")
    enemy = player.opponent.summon("EDR_654")

    game.cheat_action(destroyer, [Hit(player.hero, 2)])

    assert enemy.damage == 3
