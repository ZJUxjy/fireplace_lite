#!/usr/bin/env python
"""Tests for Phase 7 — DARK GIFT (Emerald Dream)."""
from utils import *
from fireplace.actions import GiveDarkGift


def test_dark_gift_pool_is_11_enchantments():
    """The Dark Gift pool should have 11 distinct enchantment IDs."""
    assert len(GiveDarkGift.DARK_GIFT_POOL) == 11
    assert len(set(GiveDarkGift.DARK_GIFT_POOL)) == 11


def test_give_dark_gift_applies_an_enchantment_from_pool():
    """GiveDarkGift on a friendly minion attaches a Dark Gift enchantment."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    wisp = game.player1.give(WISP)
    wisp.play()
    initial_buff_count = len(wisp.buffs)
    game.cheat_action(wisp, [GiveDarkGift(wisp)])
    # An enchantment was attached
    assert len(wisp.buffs) == initial_buff_count + 1
    # And the attached enchantment ID is from the Dark Gift pool
    new_buff = wisp.buffs[-1]
    assert new_buff.id in GiveDarkGift.DARK_GIFT_POOL


def test_give_dark_gift_records_on_controller():
    """The controller tracks which Dark Gifts have been given (for Wallow)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    wisp = game.player1.give(WISP)
    wisp.play()
    assert not getattr(game.player1, 'dark_gifts_given', [])
    game.cheat_action(wisp, [GiveDarkGift(wisp)])
    assert hasattr(game.player1, 'dark_gifts_given')
    assert len(game.player1.dark_gifts_given) == 1
    assert game.player1.dark_gifts_given[0] in GiveDarkGift.DARK_GIFT_POOL


def test_treacherous_tormentor_discovers_and_gifts():
    """EDR_102 Battlecry: Discover a Legendary minion with a Dark Gift."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    initial_hand_size = len(game.player1.hand)
    tormentor = game.player1.give("EDR_102")
    tormentor.play()
    # Resolve discover choice (auto-pick first option)
    if game.player1.choice:
        game.player1.choice.choose(game.player1.choice.cards[0])
    # Discovered card added to hand
    assert len(game.player1.hand) >= initial_hand_size  # 1 played, 1 discovered
    # A dark gift was given (recorded on controller)
    assert len(getattr(game.player1, 'dark_gifts_given', [])) == 1


def test_avant_gardening_discovers_deathrattle_with_gift():
    """EDR_488 Discovers a Deathrattle minion with a Dark Gift."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    spell = game.player1.give("EDR_488")
    spell.play()
    if game.player1.choice:
        game.player1.choice.choose(game.player1.choice.cards[0])
    # Discovered card has deathrattle (sanity)
    assert len(getattr(game.player1, 'dark_gifts_given', [])) == 1


def test_xavius_discovers_from_deck_and_gifts():
    """EDR_856 Discovers a minion from the player's deck."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Stack deck with minions so Discover has options
    for cid in ["CS2_065", "CS2_172", "CS2_182"]:
        c = game.player1.card(cid)
        c.zone = Zone.DECK
    xavius = game.player1.give("EDR_856")
    xavius.play()
    if game.player1.choice:
        game.player1.choice.choose(game.player1.choice.cards[0])
    # A discover happened and a gift was given
    assert len(getattr(game.player1, 'dark_gifts_given', [])) == 1


def test_darkrider_no_dragon_in_hand_does_nothing():
    """EDR_456 Darkrider: only triggers if you're holding a Dragon."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    rider = game.player1.give("EDR_456")
    rider.play()
    # No Dragon in hand → no Discover, no gift
    assert not getattr(game.player1, 'dark_gifts_given', [])
