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


def test_build_catalog_filters_collectible_implemented_only():
    """build_catalog() returns only collectible and implemented cards"""
    from webui.server.card_catalog import build_catalog, is_card_implemented
    cat = build_catalog()
    assert len(cat["cards"]) > 1000  # sanity check: multiple expansions should have 1000+ cards
    for card in cat["cards"]:
        assert card["collectible"] is True
        assert is_card_implemented(card["id"])
        assert card["type"] in {"MINION", "SPELL", "WEAPON"}  # no HERO cards


def test_build_catalog_max_count_legendary():
    """Legendary cards max_count == 1, others == 2"""
    from webui.server.card_catalog import build_catalog
    cat = build_catalog()
    for card in cat["cards"]:
        if card["rarity"] == "LEGENDARY":
            assert card["max_count"] == 1, f"{card['id']} legendary should be 1"
        else:
            assert card["max_count"] == 2, f"{card['id']} should be 2"


def test_build_catalog_has_localized_names():
    """Every card has name_zh and name_en (fallback to id if missing)"""
    from webui.server.card_catalog import build_catalog
    cat = build_catalog()
    for card in cat["cards"][:50]:  # sample
        assert card["name_zh"], f"{card['id']} missing name_zh"
        assert card["name_en"], f"{card['id']} missing name_en"


def test_build_catalog_etag_stable():
    """Two calls produce the same ETag"""
    from webui.server.card_catalog import build_catalog
    cat1 = build_catalog()
    cat2 = build_catalog()
    assert cat1["etag"] == cat2["etag"]


def test_build_catalog_caches_in_process():
    """Same process only builds once; second call returns cached (same object reference)"""
    from webui.server.card_catalog import build_catalog
    cat1 = build_catalog()
    cat2 = build_catalog()
    assert cat1 is cat2


def test_api_cards_all_returns_catalog():
    """GET /api/cards/all returns catalog content"""
    from webui.server import create_app
    app = create_app()
    with app.test_client() as client:
        resp = client.get("/api/cards/all")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "cards" in data
        assert "total" in data
        assert data["total"] == len(data["cards"])
        assert data["total"] > 1000


def test_api_cards_all_etag_304():
    """Sending If-None-Match matching ETag returns 304"""
    from webui.server import create_app
    app = create_app()
    with app.test_client() as client:
        first = client.get("/api/cards/all")
        etag = first.headers.get("ETag")
        assert etag

        second = client.get("/api/cards/all", headers={"If-None-Match": etag})
        assert second.status_code == 304
