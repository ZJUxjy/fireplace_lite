"""Tests for the dev-only /api/cards/keyword-candidates endpoint.

The endpoint surfaces every boolean GameTag observed on a collectible
implemented card that is NOT one of the 13 canonical keywords and NOT on
the cosmetic deny-list. Disabled in production (404), enabled when the
app runs with FLASK_DEBUG or the DEBUG_KEYWORDS config flag.
"""
import pytest


@pytest.fixture
def debug_client():
    from webui.server import create_app
    app = create_app()
    app.config['DEBUG_KEYWORDS'] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def prod_client():
    from webui.server import create_app
    app = create_app()
    app.debug = False
    app.config['DEBUG_KEYWORDS'] = False
    with app.test_client() as c:
        yield c


def test_endpoint_404_in_production(prod_client):
    resp = prod_client.get('/api/cards/keyword-candidates')
    assert resp.status_code == 404


def test_endpoint_200_in_debug(debug_client):
    resp = debug_client.get('/api/cards/keyword-candidates')
    assert resp.status_code == 200
    body = resp.get_json()
    assert isinstance(body, dict)
    assert 'candidates' in body
    assert isinstance(body['candidates'], list)


def test_candidates_have_expected_shape(debug_client):
    from webui.server.card_catalog import KEYWORD_TAGS, KEYWORD_DENY_LIST

    resp = debug_client.get('/api/cards/keyword-candidates')
    body = resp.get_json()

    canonical = set(KEYWORD_TAGS.keys())
    deny = set(KEYWORD_DENY_LIST)

    for entry in body['candidates']:
        assert set(entry.keys()) == {'tag', 'count', 'examples'}
        assert isinstance(entry['tag'], str)
        assert isinstance(entry['count'], int) and entry['count'] >= 1
        assert isinstance(entry['examples'], list)
        assert 1 <= len(entry['examples']) <= 3
        assert all(isinstance(x, str) for x in entry['examples'])
        # No canonical keyword leaks into the candidate list.
        assert entry['tag'] not in canonical, \
            f"canonical keyword {entry['tag']} leaked into candidates"
        # No deny-listed cosmetic tag leaks either.
        assert entry['tag'] not in deny, \
            f"deny-listed tag {entry['tag']} leaked into candidates"


def test_candidates_sorted_by_descending_count(debug_client):
    resp = debug_client.get('/api/cards/keyword-candidates')
    body = resp.get_json()
    counts = [e['count'] for e in body['candidates']]
    assert counts == sorted(counts, reverse=True), \
        "candidate list should be sorted by descending count"
