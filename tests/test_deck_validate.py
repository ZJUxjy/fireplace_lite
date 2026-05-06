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


def test_encode_rejects_zero_count(client):
    """count<1 应返回 400 而不是默默通过"""
    body = {
        'hero_class': 'MAGE',
        'format': 'STANDARD',
        'cards': [{'card_id': 'CS2_029', 'count': 0}],
    }
    resp = client.post('/api/decks/encode', json=body)
    assert resp.status_code == 400
    assert 'count' in resp.get_json().get('error', '').lower()


def test_encode_rejects_legendary_two_copies(client):
    """传说卡 count==2 应被 export_deck_to_string 拒绝(此前外层守卫漏检)"""
    from fireplace.cards import db as _db
    if not _db.initialized:
        _db.initialize()
    # 找一张已实现 + LEGENDARY 卡(EX1 系列里有传说;EX1_558 = Harrison Jones)
    legendaries = [
        cid for cid in _db.keys()
        if (c := _db.get(cid)) is not None
        and getattr(c, 'collectible', False)
        and c.rarity.name == 'LEGENDARY'
        and cid.startswith(('EX1_', 'CS2_'))
    ]
    assert legendaries, "expected at least one legendary in classic set"
    leg_id = legendaries[0]

    body = {
        'hero_class': 'MAGE',  # 任意合法职业即可,卡是中立的
        'format': 'STANDARD',
        'cards': [{'card_id': leg_id, 'count': 2}],
    }
    resp = client.post('/api/decks/encode', json=body)
    assert resp.status_code == 400, resp.get_json()
    err = resp.get_json().get('error', '').lower()
    assert 'legendary' in err or 'too many' in err


def test_validate_unknown_lang_falls_back_to_english(client):
    """/api/cards/<id>?lang=enUS 必须返回真实英文名,而不是中文别名"""
    resp = client.get('/api/cards/CS2_029?lang=enUS')  # Fireball
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['name']
    # Fireball 中文名是"火球术",enUS 应该不同
    zh_resp = client.get('/api/cards/CS2_029?lang=zhCN')
    zh = zh_resp.get_json()['name']
    if zh and zh != data['name']:
        # 真正的双语回退;通过
        assert data['name'].lower() != zh.lower()
    # 即使数据库没区分两份(老 fixtures),enUS 也要返回英文(__str__),不是中文
    assert any(ord(ch) < 128 for ch in data['name']), f"enUS name should be ASCII-ish, got {data['name']!r}"


def test_encode_deckstring_round_trip(client):
    """POST /api/decks/encode -> /api/decks/validate round-trip consistency"""
    body = {
        'hero_class': 'MAGE',
        'format': 'STANDARD',
        'cards': [
            {'card_id': 'CS2_029', 'count': 2},
            {'card_id': 'CS2_023', 'count': 2},
        ],
    }
    enc = client.post('/api/decks/encode', json=body)
    assert enc.status_code == 200, enc.get_json()
    deckstring = enc.get_json()['deckstring']

    val = client.post('/api/decks/validate', json={'deckstring': deckstring})
    data = val.get_json()
    assert data['valid'] is True
    assert data['hero_class'] == 'MAGE'
    assert data['format'] == 'STANDARD'
    ids = sorted([c['card_id'] for c in data['cards']])
    assert ids == ['CS2_023', 'CS2_029']
