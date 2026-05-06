"""Tests for GameManager.create_game with DeckSpec args."""
import pytest


@pytest.fixture
def manager():
    from webui.server.game import GameManager
    m = GameManager()
    m.initialize()
    return m


def test_create_game_random_specs(manager):
    """Both sides random:ANY should create game normally"""
    gid = manager.create_game(
        mode="pve",
        p1_spec={"type": "random", "card_class": "MAGE"},
        p2_spec={"type": "random", "card_class": "ANY"},
    )
    assert gid in manager.games


def test_create_game_deckstring_spec(manager):
    """Player slot with deckstring: p1 gets those cards"""
    from fireplace.cards import db
    from fireplace.deckstring import encode_deck, Format
    db.initialize()
    fb = db.get("CS2_029")  # Fireball
    intel = db.get("CS2_023")  # Arcane Intellect
    cards = [(fb.dbf_id, 2), (intel.dbf_id, 2)]
    deckstring = encode_deck(cards, 14, Format.STANDARD)

    gid = manager.create_game(
        mode="pvp",
        p1_spec={"type": "deckstring", "value": deckstring},
        p2_spec={"type": "random", "card_class": "ANY"},
    )
    assert gid in manager.games
    g = manager.games[gid]
    p1 = g["players"][0]
    p1_all_cards = list(p1.hand) + list(p1.deck)
    p1_all_card_ids = [c.id if hasattr(c, "id") else c for c in p1_all_cards]
    assert "CS2_029" in p1_all_card_ids


def test_create_game_invalid_deckstring_raises(manager):
    """Bad deckstring should raise Exception to let handler deal with it"""
    with pytest.raises(Exception):
        manager.create_game(
            mode="pve",
            p1_spec={"type": "deckstring", "value": "garbage"},
            p2_spec={"type": "random", "card_class": "ANY"},
        )


def test_create_game_test_deck_overrides_spec(manager):
    """test_deck=True ignores specs and uses create_test_deck (dev convenience)"""
    gid = manager.create_game(
        mode="pve",
        p1_spec={"type": "random", "card_class": "MAGE"},
        p2_spec={"type": "random", "card_class": "WARRIOR"},
        test_deck=True,
    )
    assert gid in manager.games
