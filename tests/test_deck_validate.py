"""Tests for POST /api/decks/validate"""
import pytest


@pytest.fixture
def client():
    from webui.server import create_app
    app = create_app()
    with app.test_client() as c:
        yield c


def _build_deckstring(cards, hero_class_id, fmt=2):
    """Construct a valid deckstring using fireplace.deckstring"""
    from fireplace.deckstring import encode_deck, Format
    return encode_deck(cards, hero_class_id, Format(fmt))


def test_validate_valid_deckstring(client):
    """Valid deckstring returns valid=True with parsed card list"""
    from fireplace.cards import db as _db
    if not _db.initialized:
        _db.initialize()
    fb = _db.get("CS2_029")  # Fireball (Mage card)
    fz = _db.get("CS2_023")  # Arcane Intellect (Mage card)
    deckstring = _build_deckstring([(fb.dbf_id, 2), (fz.dbf_id, 2)], 14, 2)

    resp = client.post("/api/decks/validate", json={"deckstring": deckstring})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["valid"] is True
    assert data["hero_class"] == "MAGE"
    assert data["format"] == "STANDARD"
    assert data["unimplemented_count"] == 0
    assert data["total_cards"] == 4
    assert all(c["implemented"] for c in data["cards"])


def test_validate_malformed_deckstring(client):
    """Invalid base64 / corrupted data returns valid=False"""
    resp = client.post("/api/decks/validate", json={"deckstring": "not-a-valid-deckstring"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["valid"] is False
    assert data["error"]


def test_validate_missing_body(client):
    """Missing deckstring field returns valid=False, not 500"""
    resp = client.post("/api/decks/validate", json={})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["valid"] is False
    assert data["error"]


def test_validate_marks_unimplemented_cards(client):
    """Deckstring with unimplemented cards: implemented=false + unimplemented_count > 0"""
    from fireplace.cards import db as _db
    if not _db.initialized:
        _db.initialize()
    # AV_100 (Drek'Thar) is in the DB but not from an implemented expansion
    non_impl = _db.get("AV_100")
    deckstring = _build_deckstring([(non_impl.dbf_id, 1)], 14, 2)
    resp = client.post("/api/decks/validate", json={"deckstring": deckstring})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["valid"] is True
    assert data["unimplemented_count"] >= 1
    assert not data["cards"][0]["implemented"]
