#!/usr/bin/env python
"""Tests for the LOCATION card type."""
import pytest
from utils import *
from fireplace.exceptions import InvalidAction
from hearthstone.enums import CardType, Zone


def test_location_can_be_played():
    """A Location is played from hand and enters the location_zone."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    loc = game.player1.give("REV_290")
    assert loc.type == CardType.LOCATION
    loc.play()
    assert loc.zone == Zone.PLAY
    assert loc in game.player1.location_zone
    assert loc not in game.player1.field


def test_location_cannot_be_used_turn_played():
    """A Location is on cooldown the turn it is placed."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    loc = game.player1.give("REV_290")
    loc.play()
    assert loc.cooldown is True
    assert loc.is_usable() is False


def test_location_usable_next_turn():
    """Cooldown clears at the start of the controller's next turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    loc = game.player1.give("REV_290")
    loc.play()
    game.end_turn(); game.end_turn()
    assert loc.cooldown is False


def test_location_use_fires_action_and_loses_durability():
    """Using a Location fires its location_action and loses 1 durability."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    target = game.player1.summon(WISP)  # 1/1
    # Add multiple deck cards so a turn-start draw + the use draw both succeed.
    for _ in range(5):
        c = game.player1.card("CS2_171")
        c.zone = Zone.DECK
    sanctum = game.player1.give("REV_290")
    sanctum.play()
    game.end_turn(); game.end_turn()
    durability_before = sanctum.durability
    deck_before = len(game.player1.deck)
    sanctum.use(target=target)
    assert target.atk == 3  # 1 + 2
    assert target.max_health == 2  # 1 + 1
    assert sanctum.durability == durability_before - 1
    # Deck went down by 1 (drew 1)
    assert len(game.player1.deck) == deck_before - 1
    assert sanctum.cooldown is True


def test_location_destroyed_when_durability_reaches_zero():
    """When durability hits 0, the Location goes to graveyard."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    library = game.player1.give("REV_371")  # 2-durability
    minion1 = game.player1.summon(WISP)
    minion2 = game.player1.summon(WISP)
    library.play()
    game.end_turn(); game.end_turn()
    library.use(target=minion1)
    assert library.durability == 1
    assert library.zone == Zone.PLAY
    game.end_turn(); game.end_turn()
    library.use(target=minion2)
    assert library.zone == Zone.GRAVEYARD
    assert library not in game.player1.location_zone


def test_only_one_location_at_a_time():
    """Playing a new Location replaces the existing one."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    loc1 = game.player1.give("REV_290")
    loc1.play()
    assert loc1 in game.player1.location_zone
    game.end_turn(); game.end_turn()
    loc2 = game.player1.give("REV_602")
    loc2.play()
    # Old location replaced
    assert loc1 not in game.player1.location_zone
    assert loc2 in game.player1.location_zone
    assert loc1.zone == Zone.GRAVEYARD


def test_location_cannot_be_used_twice_same_turn():
    """A Location cannot be used twice in the same turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    target = game.player1.summon(WISP)
    deck_card = game.player1.card("CS2_171")
    deck_card.zone = Zone.DECK
    sanctum = game.player1.give("REV_290")
    sanctum.play()
    game.end_turn(); game.end_turn()
    sanctum.use(target=target)
    target2 = game.player1.summon(WISP)
    with pytest.raises(InvalidAction):
        sanctum.use(target=target2)


def test_location_cannot_attack_or_be_attacked():
    """Locations have attackable=False (cannot be attacked directly)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    loc = game.player1.give("REV_290")
    loc.play()
    assert loc.attackable is False
