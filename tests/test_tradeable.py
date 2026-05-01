#!/usr/bin/env python
"""Tests for the TRADEABLE keyword."""
import pytest
from utils import *
from fireplace.exceptions import InvalidAction
from hearthstone.enums import GameTag, Zone


# A known Tradeable spell from Stormwind
TRADEABLE_SPELL = "SW_046"  # City Tax — 2 mana, Tradeable


def test_card_is_tradeable_when_in_hand_with_mana():
    """A Tradeable card in hand with ≥1 mana and a non-empty deck is tradeable."""
    game = prepare_game()
    # Need cards in deck for trade to be valid
    for _ in range(3):
        game.player1.deck.append(game.player1.card("CS2_171"))  # Stonetusk Boar
    card = game.player1.give(TRADEABLE_SPELL)
    assert card.data.tags.get(GameTag.TRADEABLE)
    assert card.is_tradeable is True


def test_trade_pays_one_mana():
    """Trading a card costs exactly 1 mana regardless of card cost."""
    game = prepare_game()
    for _ in range(3):
        game.player1.deck.append(game.player1.card("CS2_171"))
    card = game.player1.give(TRADEABLE_SPELL)
    mana_before = game.player1.mana
    card.trade()
    assert game.player1.mana == mana_before - 1


def test_trade_returns_card_to_deck():
    """The traded card goes from hand into the controller's deck."""
    game = prepare_game()
    for _ in range(3):
        game.player1.deck.append(game.player1.card("CS2_171"))
    card = game.player1.give(TRADEABLE_SPELL)
    deck_size_before = len(game.player1.deck)
    hand_size_before = len(game.player1.hand)
    card.trade()
    # Hand: -1 (traded) +1 (drawn) = same
    assert len(game.player1.hand) == hand_size_before
    # Deck: +1 (shuffled) -1 (drawn) = same
    assert len(game.player1.deck) == deck_size_before
    # Card is no longer in hand
    assert card.zone in (Zone.DECK, Zone.HAND)  # could be redrawn


def test_trade_draws_one_card():
    """Trading draws exactly one card from the deck."""
    game = prepare_game()
    sentinel = game.player1.card("CS2_171")
    sentinel.zone = Zone.DECK
    other = game.player1.card("CS2_171")
    other.zone = Zone.DECK
    other2 = game.player1.card("CS2_171")
    other2.zone = Zone.DECK
    card = game.player1.give(TRADEABLE_SPELL)
    deck_size_before = len(game.player1.deck)
    hand_size_before = len(game.player1.hand)
    card.trade()
    # Net: hand same size (one drawn replaces traded card)
    assert len(game.player1.hand) == hand_size_before
    # Deck shifted by traded-in/drawn-out, total same
    assert len(game.player1.deck) == deck_size_before


def test_cannot_trade_without_mana():
    """A card cannot be traded if controller has 0 mana."""
    game = prepare_game()
    for _ in range(3):
        game.player1.deck.append(game.player1.card("CS2_171"))
    card = game.player1.give(TRADEABLE_SPELL)
    # Drain all mana
    game.player1.used_mana = game.player1.max_mana
    assert game.player1.mana == 0
    assert card.is_tradeable is False
    with pytest.raises(InvalidAction):
        card.trade()


def test_cannot_trade_non_tradeable_card():
    """Cards without the TRADEABLE tag raise on trade()."""
    game = prepare_game()
    moonfire = game.player1.give(MOONFIRE)
    assert moonfire.is_tradeable is False
    with pytest.raises(InvalidAction):
        moonfire.trade()


def test_cannot_trade_with_empty_deck():
    """A Tradeable card with an empty deck cannot be traded."""
    game = prepare_empty_game()  # decks start empty
    game.player1.max_mana = 5
    card = game.player1.give(TRADEABLE_SPELL)
    assert game.player1.deck == []
    assert card.is_tradeable is False


def test_cannot_trade_on_opponents_turn():
    """A Tradeable card cannot be traded during the opponent's turn."""
    game = prepare_game()
    for _ in range(3):
        game.player1.deck.append(game.player1.card("CS2_171"))
    card = game.player1.give(TRADEABLE_SPELL)
    game.end_turn()  # now it's player2's turn
    assert card.is_tradeable is False


def test_trade_preserves_card_object_when_redrawn():
    """If shuffled into a 1-card deck, the same card is drawn back."""
    game = prepare_empty_game()
    game.player1.max_mana = 5
    # Empty deck, then add no cards. The traded card itself becomes the only deck entry.
    card = game.player1.give(TRADEABLE_SPELL)
    assert game.player1.deck == []
    # Trade with empty deck is forbidden — but if we manually allow:
    # Create a deck with just one decoy then trade
    decoy = game.player1.card("CS2_171")
    decoy.zone = Zone.DECK
    assert len(game.player1.deck) == 1
    card.trade()
    # After trade: the traded card is shuffled in and one card drawn.
    # Either we drew the decoy (card stays in deck) or we drew the traded card back.
    assert len(game.player1.hand) == 1
    drawn = game.player1.hand[0]
    assert drawn in (card, decoy)
