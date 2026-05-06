from flask import Blueprint, jsonify, make_response, request

bp = Blueprint('views', __name__)

# 语言名称映射
LANGUAGE_NAMES = {
    'zhCN': '简体中文',
    'enUS': 'English',
    'enGB': 'English (UK)',
    'deDE': 'Deutsch',
    'esES': 'Español',
    'frFR': 'Français',
    'itIT': 'Italiano',
    'jaJP': '日本語',
    'koKR': '한국어',
    'plPL': 'Polski',
    'ptBR': 'Português (BR)',
    'ruRU': 'Русский',
    'thTH': 'ไทย',
    'zhTW': '繁體中文'
}

# 支持的语言（简化版）
SUPPORTED_LANGUAGES = ['zhCN', 'enUS']

def _load_card_multilang(card_id):
    """Get multilang name from card_text_loader (zhCN + enUS fallback; other languages not supported in v1)"""
    from .card_text import card_text_loader
    info = card_text_loader.card_data.get(card_id, {})
    name = info.get('name')
    if not name:
        return {}
    # card_text_loader currently only caches zhCN+fallback, so zhCN and enUS (via fallback) return the same value
    return {'zhCN': name, 'enUS': name}


@bp.route('/api/languages')
def languages():
    """获取支持的语言列表"""
    return jsonify([
        {'code': code, 'name': LANGUAGE_NAMES.get(code, code)}
        for code in SUPPORTED_LANGUAGES
    ])


@bp.route('/api/all_languages')
def all_languages():
    """获取所有可用语言列表"""
    return jsonify([
        {'code': code, 'name': LANGUAGE_NAMES.get(code, code)}
        for code in LANGUAGE_NAMES.keys()
    ])


@bp.route('/api/cards/all')
def cards_all():
    """Return full metadata for all implemented collectible cards (with ETag caching)"""
    from .card_catalog import build_catalog
    catalog = build_catalog()
    etag = f'"{catalog["etag"]}"'

    if request.headers.get('If-None-Match') == etag:
        resp = make_response('', 304)
        resp.headers['ETag'] = etag
        resp.headers['Cache-Control'] = 'private, max-age=300'
        return resp

    response = jsonify({
        'cards': catalog['cards'],
        'total': catalog['total'],
        'generated_at': catalog['generated_at'],
    })
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'private, max-age=300'
    return response


@bp.route('/api/cards/<card_id>')
def get_card(card_id):
    """获取卡牌信息（含多语言）"""
    lang = request.args.get('lang', 'zhCN')

    # 优先从 fireplace 获取卡牌对象
    from fireplace import cards
    if not cards.db.initialized:
        cards.db.initialize()

    card = cards.db.get(card_id)
    if card:
        # 从 XML 获取多语言名称
        names = _load_card_multilang(card.id)
        name = names.get(lang, str(card))

        return jsonify({
            'id': card.id,
            'name': name,
            'cost': card.cost,
            'type': str(type(card).__name__)
        })

    return jsonify({'error': 'Card not found'}), 404


@bp.route('/api/decks/validate', methods=['POST'])
def validate_deck():
    """Validate a deckstring and mark unimplemented cards"""
    from .deck_manager import import_deck_from_string, InvalidDeck

    body = request.get_json(silent=True) or {}
    deckstring = body.get('deckstring')
    if not deckstring:
        return jsonify({'valid': False, 'error': 'missing deckstring'}), 200

    try:
        result = import_deck_from_string(deckstring)
    except (InvalidDeck, ValueError, TypeError, Exception) as e:
        return jsonify({'valid': False, 'error': str(e)}), 200

    return jsonify({
        'valid': True,
        'hero_class': result['hero_class'],
        'format': result['format'],
        'cards': result['cards'],
        'unimplemented_count': result['unimplemented_count'],
        'total_cards': result['total_cards'],
        'error': None,
    })
