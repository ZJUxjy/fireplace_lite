#!/usr/bin/env python
"""Tests for newly-implemented OUTCAST cards across multiple expansions."""
from utils import *


def _put_in_hand(player, card_ids):
    """Helper: clear hand and place cards in given order so leftmost = first."""
    for c in player.hand[::-1]:
        c.discard()
    for cid in card_ids:
        player.give(cid)


def test_vengeful_spirit_outcast_draws_2():
    """BAR_328 Vengeful Spirit: Outcast draws 2 cards."""
    from hearthstone.enums import Zone
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Add some cards properly into the deck
    for _ in range(5):
        c = game.player1.card("CS2_171")
        c.zone = Zone.DECK
    deck_before = len(game.player1.deck)
    _put_in_hand(game.player1, ["BAR_328", WISP, WISP])
    spirit = game.player1.hand[0]
    assert spirit.id == "BAR_328"
    spirit.play()
    # 2 cards drawn from deck
    assert len(game.player1.deck) == deck_before - 2


def test_glaivesmith_outcast_buffs_hero():
    """CS3_017 Gan'arg Glaivesmith: Outcast gives hero +3 atk."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    _put_in_hand(game.player1, ["CS3_017", WISP, WISP])
    smith = game.player1.hand[0]
    smith.play()
    assert game.player1.hero.atk == 3


def test_glaivesmith_no_outcast_when_middle():
    """When played from middle of hand, outcast does NOT trigger."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    _put_in_hand(game.player1, [WISP, "CS3_017", WISP])
    smith = game.player1.hand[1]
    assert smith.id == "CS3_017"
    smith.play()
    assert game.player1.hero.atk == 0  # no outcast → no buff


def test_dreadlords_bite_outcast_aoe():
    """DMF_227 Dreadlord's Bite: Outcast deals 1 to all enemies."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    enemy = game.player2.summon(WISP)  # 1/1 wisp
    enemy_hero_hp = game.player2.hero.health
    _put_in_hand(game.player1, ["DMF_227", WISP])
    bite = game.player1.hand[0]
    bite.play()
    # All enemies took 1 damage
    assert enemy.dead  # 1/1 wisp dies
    assert game.player2.hero.health == enemy_hero_hp - 1


def test_security_outcast_summons_three():
    """ETC_411 SECURITY!!: Plays 2 Illidari, Outcast plays 3 instead."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    _put_in_hand(game.player1, ["ETC_411", WISP])
    sec = game.player1.hand[0]
    sec.play()
    # Outcast variant summons 3 Illidari (not 2)
    illidari = [m for m in game.player1.field if m.id == "BT_036t"]
    assert len(illidari) == 3


def test_security_no_outcast_summons_two():
    """ETC_411 from middle: only 2 Illidari summoned."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    _put_in_hand(game.player1, [WISP, "ETC_411", WISP])
    sec = game.player1.hand[1]
    sec.play()
    illidari = [m for m in game.player1.field if m.id == "BT_036t"]
    assert len(illidari) == 2
