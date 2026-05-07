"""Tests for the paged catalog endpoint /api/cards/page."""
import pytest


@pytest.fixture
def client():
    from webui.server import create_app
    app = create_app()
    with app.test_client() as c:
        yield c


def test_default_page_returns_first_slice(client):
    resp = client.get('/api/cards/page')
    assert resp.status_code == 200
    body = resp.get_json()
    assert len(body['cards']) == 200
    assert body['cursor'] == 0
    assert body['size'] == 200
    assert body['next_cursor'] == 200
    assert body['total'] > 200


def test_explicit_size_clamps(client):
    resp = client.get('/api/cards/page?cursor=0&size=10')
    body = resp.get_json()
    assert len(body['cards']) == 10
    assert body['next_cursor'] == 10


def test_size_oversize_capped_at_500(client):
    resp = client.get('/api/cards/page?cursor=0&size=99999')
    body = resp.get_json()
    assert body['size'] == 500
    assert len(body['cards']) == 500


def test_last_partial_page_has_null_next_cursor(client):
    # First learn the total.
    resp = client.get('/api/cards/page?size=1')
    total = resp.get_json()['total']
    # Request a page positioned so it wraps the end.
    cursor = total - 50
    resp = client.get(f'/api/cards/page?cursor={cursor}&size=500')
    body = resp.get_json()
    assert len(body['cards']) == 50
    assert body['next_cursor'] is None


def test_out_of_range_cursor_returns_empty(client):
    resp = client.get('/api/cards/page?cursor=99999&size=200')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['cards'] == []
    assert body['next_cursor'] is None


def test_bad_query_returns_400(client):
    resp = client.get('/api/cards/page?cursor=abc')
    assert resp.status_code == 400


def test_etag_matches_cards_all(client):
    page_resp = client.get('/api/cards/page?size=1')
    all_resp = client.get('/api/cards/all')
    # /api/cards/all does not embed etag in the JSON body, only in the
    # header. /api/cards/page embeds it both places. The two header values
    # must match — that's the contract clients use to revalidate.
    assert page_resp.headers['ETag'] == all_resp.headers['ETag']
    assert page_resp.get_json()['etag'] == page_resp.headers['ETag'].strip('"')


def test_concatenating_pages_yields_full_catalog(client):
    # Walk the cursor until done.
    pages = []
    cursor = 0
    while True:
        resp = client.get(f'/api/cards/page?cursor={cursor}&size=500')
        body = resp.get_json()
        pages.extend(body['cards'])
        if body['next_cursor'] is None:
            break
        cursor = body['next_cursor']

    all_resp = client.get('/api/cards/all').get_json()
    paged_ids = [c['id'] for c in pages]
    all_ids = [c['id'] for c in all_resp['cards']]
    assert paged_ids == all_ids


def test_if_none_match_returns_304(client):
    first = client.get('/api/cards/page?size=1')
    etag = first.headers['ETag']
    second = client.get('/api/cards/page?size=1', headers={'If-None-Match': etag})
    assert second.status_code == 304
    assert second.headers['ETag'] == etag


def test_negative_cursor_clamps_to_zero(client):
    resp = client.get('/api/cards/page?cursor=-99&size=5')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['cursor'] == 0
    assert len(body['cards']) == 5
