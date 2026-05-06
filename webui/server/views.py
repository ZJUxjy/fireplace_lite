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
        from .card_text import card_text_loader
        zh_name = card_text_loader.get_name(card.id)
        en_name = str(card)  # fireplace card __str__ returns enUS name
        if lang == 'zhCN':
            name = zh_name or en_name
        else:
            name = en_name or zh_name or card.id

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
    from .deck_manager import import_deck_from_string

    body = request.get_json(silent=True) or {}
    deckstring = body.get('deckstring')
    if not deckstring:
        return jsonify({'valid': False, 'error': 'missing deckstring'}), 200

    try:
        result = import_deck_from_string(deckstring)
    except Exception as e:
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


@bp.route('/api/decks/encode', methods=['POST'])
def encode_deck_endpoint():
    """Generate a deckstring from deck components"""
    from .deck_manager import export_deck_to_string, InvalidDeck
    from fireplace.deckstring import Format

    body = request.get_json(silent=True) or {}
    hero_class = body.get('hero_class')
    cards_in = body.get('cards', [])
    fmt_name = body.get('format', 'STANDARD')

    if not hero_class or not cards_in:
        return jsonify({'error': 'missing hero_class or cards'}), 400

    try:
        cards = []
        for c in cards_in:
            if not isinstance(c, dict) or 'card_id' not in c or 'count' not in c:
                return jsonify({'error': f'each card needs card_id and count: {c}'}), 400
            count = int(c['count'])
            if count < 1:
                return jsonify({'error': f'card count must be >= 1: {c}'}), 400
            cards.append((c['card_id'], count))
        fmt = Format[fmt_name]
        deckstring = export_deck_to_string(cards, hero_class, fmt)
    except InvalidDeck as e:
        return jsonify({'error': str(e)}), 400
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({'error': f'invalid encode payload: {e}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'deckstring': deckstring})
