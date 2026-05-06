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
    """Bad deckstring should raise InvalidDeck to let handler deal with it"""
    from webui.server.deck_manager import InvalidDeck
    with pytest.raises(InvalidDeck):
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


def test_handle_create_game_emits_state_on_success():
    """handle_create_game emits game_state when receiving valid dual DeckSpec"""
    from webui.server import create_app, socketio
    app = create_app()
    client = socketio.test_client(app)

    client.emit('create_game', {
        'mode': 'pve',
        'player': {'type': 'random', 'card_class': 'MAGE'},
        'opponent': {'type': 'random', 'card_class': 'ANY'},
    })
    received = client.get_received()
    types = [r['name'] for r in received]
    assert 'game_state' in types, f"got {types}"


def test_create_game_unknown_class_raises(manager):
    """unknown card_class string should raise ValueError, not silently random"""
    with pytest.raises(ValueError, match="unknown card_class"):
        manager.create_game(
            mode="pve",
            p1_spec={"type": "random", "card_class": "FOO_BAR_NOT_A_CLASS"},
            p2_spec={"type": "random", "card_class": "ANY"},
        )


def test_create_game_lowercase_any_works(manager):
    """case-insensitive ANY should be accepted (resolve_card_class_strict uses upper())"""
    gid = manager.create_game(
        mode="pve",
        p1_spec={"type": "random", "card_class": "any"},
        p2_spec={"type": "random", "card_class": "MAGE"},
    )
    assert gid in manager.games


def test_handle_create_game_rejects_legacy_player_class():
    """Legacy {mode, player_class} payload no longer accepted; must emit create_game_error"""
    from webui.server import create_app, socketio
    app = create_app()
    client = socketio.test_client(app)

    client.emit('create_game', {'mode': 'pve', 'player_class': 'mage'})
    received = client.get_received()
    types = [r['name'] for r in received]
    assert 'create_game_error' in types, f"got {types}"
    assert 'game_state' not in types


def test_handle_create_game_invalid_deckstring_emits_error():
    """Bad deckstring should not create game, emits create_game_error"""
    from webui.server import create_app, socketio
    app = create_app()
    client = socketio.test_client(app)

    client.emit('create_game', {
        'mode': 'pve',
        'player': {'type': 'deckstring', 'value': 'garbage'},
        'opponent': {'type': 'random', 'card_class': 'ANY'},
    })
    received = client.get_received()
    types = [r['name'] for r in received]
    assert 'create_game_error' in types, f"got {types}"
    assert 'game_state' not in types
