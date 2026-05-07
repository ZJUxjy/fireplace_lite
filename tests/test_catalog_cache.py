"""Tests for the persistent on-disk catalog cache.

The cache is keyed by CATALOG_SCHEMA_VERSION (filename suffix). Hits skip
the 25-second XML parse; corrupted cache files fall through to a clean
rebuild that overwrites the bad file.
"""
import json
import pytest


@pytest.fixture
def isolated_cache(tmp_path, monkeypatch):
    """Redirect the catalog cache dir to a tmp path and clear in-memory state."""
    from webui.server import card_catalog

    cache_dir = tmp_path / "catalog_cache"
    monkeypatch.setattr(card_catalog, "CACHE_DIR", cache_dir)

    # Reset both module-level caches so each test starts fresh.
    card_catalog.reset_catalog_cache()

    yield card_catalog, cache_dir

    card_catalog.reset_catalog_cache()


def test_cold_build_writes_cache_file(isolated_cache):
    """First build_catalog() with no cache file present writes one."""
    cc, cache_dir = isolated_cache
    expected_path = cache_dir / f"catalog-v{cc.CATALOG_SCHEMA_VERSION}.json"
    assert not expected_path.exists()

    cat = cc.build_catalog()

    assert expected_path.exists()
    on_disk = json.loads(expected_path.read_text(encoding="utf-8"))
    # Identity check: persisted snapshot reflects the in-memory result.
    assert on_disk["total"] == cat["total"]
    assert on_disk["etag"] == cat["etag"]
    assert len(on_disk["cards"]) == len(cat["cards"])


def test_warm_start_reads_cache_without_initializing_db(isolated_cache, monkeypatch):
    """A subsequent build_catalog() call reads the cache file and never
    re-invokes _ensure_db_initialized() — proving the slow XML parse is skipped."""
    cc, _ = isolated_cache

    # First build populates the on-disk cache.
    first = cc.build_catalog()

    # Reset only the in-memory cache (simulating a process restart).
    cc.reset_catalog_cache()

    # Now spy on the slow path.
    calls = {"n": 0}
    real_ensure = cc._ensure_db_initialized

    def spy():
        calls["n"] += 1
        real_ensure()

    monkeypatch.setattr(cc, "_ensure_db_initialized", spy)

    second = cc.build_catalog()

    assert calls["n"] == 0, "warm start must not re-init the card DB"
    assert second["etag"] == first["etag"]
    assert second["total"] == first["total"]


def test_corrupted_cache_falls_through_to_rebuild(isolated_cache):
    """A truncated/garbled cache file is logged and replaced, never raised."""
    cc, cache_dir = isolated_cache

    # Build once so the path exists.
    cat1 = cc.build_catalog()
    path = cache_dir / f"catalog-v{cc.CATALOG_SCHEMA_VERSION}.json"
    assert path.exists()

    # Corrupt: replace with garbage.
    path.write_text("{not json, definitely not", encoding="utf-8")

    # Reset in-memory and rebuild.
    cc.reset_catalog_cache()
    cat2 = cc.build_catalog()

    # Same data ETag (deterministic build) and the file is repaired.
    assert cat2["etag"] == cat1["etag"]
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["etag"] == cat1["etag"]


def test_schema_version_mismatch_uses_versioned_filename(isolated_cache, monkeypatch):
    """Bumping CATALOG_SCHEMA_VERSION leaves the old file in place and
    writes a new file under the new versioned name."""
    cc, cache_dir = isolated_cache

    # Build under v1.
    monkeypatch.setattr(cc, "CATALOG_SCHEMA_VERSION", 1)
    monkeypatch.setattr(cc, "_cache_path", lambda: cache_dir / "catalog-v1.json")
    cc.build_catalog()
    v1 = cache_dir / "catalog-v1.json"
    assert v1.exists()

    # Bump to v2 and reset.
    cc.reset_catalog_cache()
    monkeypatch.setattr(cc, "CATALOG_SCHEMA_VERSION", 2)
    monkeypatch.setattr(cc, "_cache_path", lambda: cache_dir / "catalog-v2.json")
    cc.build_catalog()

    v2 = cache_dir / "catalog-v2.json"
    assert v2.exists(), "new schema must produce a new versioned file"
    assert v1.exists(), "old versioned file must be left alone, not deleted"
