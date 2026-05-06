"""Tests for webui/server/card_catalog.py"""
import pytest


def test_is_card_implemented_known_card():
    """Known card prefixes (EX1) should be implemented"""
    from webui.server.card_catalog import is_card_implemented
    assert is_card_implemented("EX1_565") is True  # Flametongue Totem


def test_is_card_implemented_unknown_prefix():
    """Unlisted expansion prefixes should not be implemented"""
    from webui.server.card_catalog import is_card_implemented
    assert is_card_implemented("DINO_400") is False


def test_is_card_implemented_blacklist():
    """Blacklisted card IDs should be unimplemented even if prefix is implemented"""
    from webui.server.card_catalog import (
        is_card_implemented, CARD_BLACKLIST,
    )
    CARD_BLACKLIST.add("EX1_999_test")
    try:
        assert is_card_implemented("EX1_999_test") is False
    finally:
        CARD_BLACKLIST.discard("EX1_999_test")


def test_game_module_reexports_for_compat():
    """game.py should still export these symbols for other modules"""
    from webui.server import game
    assert callable(game.is_card_implemented)
