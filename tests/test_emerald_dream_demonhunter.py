from utils import *
from hearthstone.enums import CardClass, CardType, Race, SpellSchool, Zone

from fireplace.actions import Attack


DREADSEEDS = {"EDR_840t": 2, "EDR_840t1": 1, "EDR_840t2": 3}


def _set_mana(player):
    player.max_mana = 10
    player.used_mana = 0


def _assert_dreadseed(minion):
    assert minion.id in DREADSEEDS
    assert minion.dormant
    assert minion.dormant_turns == DREADSEEDS[minion.id]


def test_omen_has_rush_windfury_and_deathrattle_improves_after_attacks():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    omen = player.summon("EDR_421")
    enemy = player.opponent.summon("CS2_200")

    assert omen.rush
    assert omen.windfury

    game.cheat_action(
        omen,
        [
            Attack(omen, player.opponent.hero),
            Attack(omen, player.opponent.hero),
        ],
    )
    omen.destroy()

    assert enemy.damage == 3
    assert player.opponent.hero.damage == 15


def test_alarashi_transforms_hand_minions_into_demons_preserving_stats_and_cost():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    wisp = player.give(WISP)
    footman = player.give(GOLDSHIRE_FOOTMAN)
    spell = player.give(THE_COIN)
    originals = {
        wisp: (wisp.cost, wisp.atk, wisp.max_health),
        footman: (footman.cost, footman.atk, footman.max_health),
    }

    player.give("EDR_493").play()

    transformed = [card for card in player.hand if card is not spell]
    assert len(transformed) == 2
    assert spell in player.hand
    assert {card.id for card in transformed}.isdisjoint({WISP, GOLDSHIRE_FOOTMAN})
    for card, (cost, atk, health) in zip(transformed, originals.values()):
        assert Race.DEMON in card.races
        assert (card.cost, card.atk, card.max_health) == (cost, atk, health)


def test_wyverns_slumber_summons_two_dormant_dreadseeds_or_damages_minions():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_820").play(choose="EDR_820a")

    assert len(player.field) == 2
    for dreadseed in player.field:
        _assert_dreadseed(dreadseed)

    for minion in list(player.field):
        minion.destroy()
    friendly = player.summon(WISP)
    enemy = player.opponent.summon("CS2_200")
    player.used_mana = 0

    player.give("EDR_820").play(choose="EDR_820b")

    assert friendly.zone == Zone.GRAVEYARD
    assert enemy.damage == 2


def test_grim_harvest_draws_and_summons_a_dormant_dreadseed():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    player.card(WISP).zone = Zone.DECK

    player.give("EDR_840").play()

    assert len(player.hand) == 1
    assert player.hand[0].id == WISP
    assert len(player.field) == 1
    _assert_dreadseed(player.field[0])


def test_dreadsoul_corrupter_summons_dormant_dreadseed_on_play_and_death():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)

    corrupter = player.give("EDR_841").play()

    assert len(player.field) == 2
    _assert_dreadseed(player.field[1])

    corrupter.destroy()

    assert len([minion for minion in player.field if minion.id in DREADSEEDS]) == 2


def test_defiled_spear_splashes_hero_attack_to_another_random_enemy():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon("CS2_200")
    player.give("EDR_842").play()

    player.hero.attack(player.opponent.hero)

    assert player.opponent.hero.damage == 2
    assert enemy.damage == 2


def test_jumpscare_discovers_large_demon_with_dark_gift_and_shuffles_others():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_882").play()

    assert player.choice
    assert all(
        card.type == CardType.MINION and Race.DEMON in card.races and card.cost >= 5
        for card in player.choice.cards
    )
    cards = list(player.choice.cards)
    chosen = cards[0]
    player.choice.choose(chosen)

    assert chosen in player.hand
    assert getattr(chosen, "_dark_gift", False)
    assert all(card in player.deck for card in cards[1:])


def test_nightmare_dragonkin_discounts_rightmost_card_on_deathrattle():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    left = player.give(WISP)
    right = player.give("CS2_200")
    dragonkin = player.summon("EDR_890")

    dragonkin.destroy()

    assert left.cost == left.data.cost
    assert right.cost == max(0, right.data.cost - 2)


def test_ravenous_felhunter_resurrects_low_cost_deathrattle_minion_and_copy():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    leper = player.summon("EX1_029")
    leper.destroy()
    player.opponent.hero.damage = 0
    _set_mana(player)

    player.give("EDR_891").play().destroy()

    assert len(player.field.filter(id="EX1_029")) == 2


def test_ferocious_felbat_resurrects_different_high_cost_deathrattle_minion_and_copy():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    belcher = player.summon("FP1_012")
    belcher.destroy()
    for minion in list(player.field):
        minion.destroy()
    _set_mana(player)

    player.give("EDR_892").play().destroy()

    assert len(player.field.filter(id="FP1_012")) == 2
    assert not player.field.filter(id="EDR_892")


def test_sigil_of_cinder_deals_six_randomly_split_at_start_of_next_turn():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("FIR_902").play()
    game.end_turn()
    game.end_turn()

    assert player.opponent.hero.damage == 6


def test_felfire_blaze_destroys_itself_after_fel_spell_and_hits_all_enemies():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    blaze = player.summon("FIR_904")
    enemy = player.opponent.summon("CS2_200")

    player.give("BT_035").play()

    assert blaze.zone == Zone.GRAVEYARD
    assert enemy.damage == 2
    assert player.opponent.hero.damage == 2


def test_scorchreaver_discovers_fel_spell_and_discounts_fel_spells_in_hand():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    fel = player.give("BT_753")
    non_fel = player.give(THE_COIN)

    player.give("FIR_952").play()

    assert fel.cost == max(0, fel.data.cost - 1)
    assert non_fel.cost == non_fel.data.cost
    assert player.choice
    assert all(
        card.type == CardType.SPELL
        and getattr(card.data, "spell_school", None) == SpellSchool.FEL
        for card in player.choice.cards
    )
    choice = player.choice.cards[0]
    player.choice.choose(choice)

    assert choice in player.hand
