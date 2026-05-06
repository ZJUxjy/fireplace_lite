from utils import *
from hearthstone.enums import CardClass, CardType, Zone


def _set_mana(player):
    player.max_mana = 10
    player.used_mana = 0


def test_tricky_satyr_copies_lowest_cost_opponent_hand_card():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    for card in list(player.opponent.hand):
        card.zone = Zone.REMOVEDFROMGAME
    low = player.opponent.give(WISP)
    player.opponent.give("EDR_527")

    player.give("EDR_521").play()

    assert player.hand[-1].id == low.id


def test_mimicry_opponent_draws_two_and_rogue_gets_copies():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    drawn = [player.opponent.card(WISP, zone=Zone.DECK), player.opponent.card("EDR_521", zone=Zone.DECK)]

    player.give("EDR_522").play()

    assert all(card in player.opponent.hand for card in drawn)
    assert {card.id for card in player.hand} >= {card.id for card in drawn}


def test_web_of_deception_bounces_friendly_minion_and_summons_spider():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)

    player.give("EDR_523").play(target=target)

    spider = player.field[-1]
    assert target in player.hand
    assert spider.id == "EDR_523t"
    assert (spider.atk, spider.max_health) == (4, 4)
    assert spider.stealthed


def test_harbinger_triggers_when_bounced_by_other_effects():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    harbinger = player.summon("EDR_781")

    game.cheat_action(harbinger, [Bounce(harbinger)])

    assert harbinger in player.hand
    assert len(player.field) == 2
    assert all(minion.cost == 2 for minion in player.field)


def test_shadowcloaked_assailant_shuffles_matching_opponent_card():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    player.give(WISP)
    opponent_copy = player.opponent.give(WISP)

    player.give("EDR_524").play()

    assert opponent_copy.zone == Zone.DECK


def test_barbed_thorn_deathrattle_mode_deals_two_to_all_enemies():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon(WISP)
    thorn = player.give("EDR_525")

    thorn.play()
    player.choice.choose(player.choice.cards[1])
    player.weapon.destroy()

    assert player.opponent.hero.damage == 2
    assert enemy.zone == Zone.GRAVEYARD


def test_barbed_thorn_poisonous_mode_expires_at_end_of_turn():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)

    weapon = player.give("EDR_525").play()
    player.choice.choose(player.choice.cards[0])
    assert weapon.poisonous

    game.end_turn()

    assert not weapon.poisonous


def test_renferal_traps_more_cards_each_time_played():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    cards = [player.opponent.give(WISP) for _ in range(3)]

    player.give("EDR_526").play()
    player.used_mana = 0
    player.give("EDR_526").play()

    trapped = [card for card in player.opponent.hand if any(buff.id == "EDR_780e" for buff in card.buffs)]
    assert len(trapped) == 3

    game.end_turn()
    game.end_turn()

    assert all(not any(buff.id == "EDR_780e" for buff in card.buffs) for card in player.opponent.hand)


def test_ashamane_fills_hand_with_discounted_opponent_deck_copies():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    for card_id in (WISP, "EDR_521", "EDR_527"):
        player.opponent.card(card_id, zone=Zone.DECK)

    player.give("EDR_527").play()

    copied = [card for card in player.hand if card.id in (WISP, "EDR_521", "EDR_527")]
    assert copied
    assert all(card.cost == max(0, card.data.cost - 3) for card in copied)


def test_nightmare_fuel_discovers_opponent_deck_minion_with_combo_dark_gift():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    player.opponent.card(WISP, zone=Zone.DECK)
    player.give(THE_COIN).play()
    player.used_mana = 0

    player.give("EDR_528").play()
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert chosen in player.hand
    assert chosen._dark_gift


def test_twisted_webweaver_draws_when_replaying_minion():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    player.summon("EDR_540")
    player.give(WISP).play()
    player.card("EDR_521", zone=Zone.DECK)
    player.used_mana = 0

    player.give(WISP).play()

    assert player.hand.filter(id="EDR_521")


def test_harbinger_summons_two_minions_when_bounced_from_battlefield():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    harbinger = player.summon("EDR_781")

    player.give("EDR_523").play(target=harbinger)

    assert harbinger in player.hand
    assert len([minion for minion in player.field if minion.cost == 2]) == 2


def test_everburning_phoenix_costs_less_and_returns_at_end_of_turn_after_death():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    player.give(THE_COIN).play()
    phoenix = player.give("FIR_919")

    assert phoenix.cost == 3

    phoenix.play()
    phoenix.destroy()
    game.end_turn()

    assert player.hand.filter(id="FIR_919")


def test_smoke_bomb_discovers_minion_with_dark_gift():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)

    player.give("FIR_920").play()
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert chosen in player.hand
    assert chosen._dark_gift


def test_cindersword_gains_attack_if_holding_dark_gift_minion():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    _set_mana(player)
    gifted = player.give(WISP)
    gifted._dark_gift = True

    player.give("FIR_922").play()

    assert player.weapon.atk == 4
