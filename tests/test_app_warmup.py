"""Tests for the eager catalog warm-up thread that runs at create_app()."""
import json
import os
import time
import pytest


@pytest.fixture
def warmup_with_seeded_disk_cache(tmp_path, monkeypatch):
    """Pre-seed the on-disk cache so warm-up returns ~instantly without paying
    the 25-second XML parse, then create the app with warm-up enabled."""
    from webui.server import card_catalog

    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    monkeypatch.setattr(card_catalog, "CACHE_DIR", cache_dir)

    # Minimal valid cache payload — warm-up will load it instead of parsing XML.
    seeded = {
        "cards": [{"id": "FAKE_001", "keywords": []}],
        "total": 1,
        "etag": "deadbeefdeadbeef",
        "generated_at": "2026-05-08T00:00:00+00:00",
    }
    cache_file = cache_dir / f"catalog-v{card_catalog.CATALOG_SCHEMA_VERSION}.json"
    cache_file.write_text(json.dumps(seeded), encoding="utf-8")

    card_catalog.reset_catalog_cache()

    # Force warm-up on (the conftest default skips it).
    monkeypatch.setenv("SKIP_CATALOG_WARMUP", "")

    yield card_catalog, seeded

    card_catalog.reset_catalog_cache()


def test_warmup_populates_cache_before_first_request(warmup_with_seeded_disk_cache):
    cc, seeded = warmup_with_seeded_disk_cache
    # Sanity: in-memory cache is empty before app creation.
    assert cc._catalog_cache is None

    from webui.server import create_app
    create_app()

    # Give the daemon thread a moment to load the disk cache.
    deadline = time.monotonic() + 5.0
    while cc._catalog_cache is None and time.monotonic() < deadline:
        time.sleep(0.05)

    assert cc._catalog_cache is not None, "warm-up thread did not populate cache"
    assert cc._catalog_cache["etag"] == seeded["etag"]


def test_warmup_failure_does_not_break_app(monkeypatch, tmp_path):
    """If warm-up raises, the app still serves non-catalog endpoints."""
    from webui.server import card_catalog

    monkeypatch.setattr(card_catalog, "CACHE_DIR", tmp_path / "cache")
    card_catalog.reset_catalog_cache()
    monkeypatch.setenv("SKIP_CATALOG_WARMUP", "")

    # Inject a failing build_catalog so the warm-up thread blows up.
    def boom():
        raise RuntimeError("simulated warm-up failure")
    monkeypatch.setattr(card_catalog, "build_catalog", boom)

    from webui.server import create_app
    app = create_app()

    # Unrelated endpoint still works.
    with app.test_client() as c:
        resp = c.get("/api/languages")
        assert resp.status_code == 200


def test_warmup_disabled_via_env(monkeypatch):
    """SKIP_CATALOG_WARMUP=1 prevents the thread from starting."""
    from webui.server import card_catalog

    card_catalog.reset_catalog_cache()
    monkeypatch.setenv("SKIP_CATALOG_WARMUP", "1")

    # Spy: count calls.
    calls = {"n": 0}
    real_build = card_catalog.build_catalog

    def counting_build():
        calls["n"] += 1
        return real_build()
    monkeypatch.setattr(card_catalog, "build_catalog", counting_build)

    from webui.server import create_app
    create_app()

    # Wait briefly to confirm no background call happens.
    time.sleep(0.5)
    assert calls["n"] == 0
