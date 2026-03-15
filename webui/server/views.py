from flask import Blueprint, jsonify, request
import os

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

# CardDefs.xml 路径
CARD_DEFS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'fireplace', 'cards', 'CardDefs.xml')

# 缓存卡牌多语言数据
_card_cache = {}


def _load_card_multilang(card_id):
    """从 CardDefs.xml 加载卡牌多语言数据"""
    if card_id in _card_cache:
        return _card_cache[card_id]

    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(CARD_DEFS_PATH)
        root = tree.getroot()

        for entity in root.findall('Entity'):
            entity_id = entity.get('ID')
            if str(entity_id) == str(card_id):
                # 查找卡牌名称
                name_tag = None
                for tag in entity.findall('Tag'):
                    if tag.get('name') == 'CARDNAME':
                        name_tag = tag
                        break

                if name_tag is not None:
                    names = {}
                    for lang in ['zhCN', 'enUS', 'enGB', 'deDE', 'esES', 'frFR', 'itIT', 'jaJP', 'koKR', 'plPL', 'ptBR', 'ruRU', 'thTH', 'zhTW']:
                        lang_elem = name_tag.find(lang)
                        if lang_elem is not None and lang_elem.text:
                            names[lang] = lang_elem.text
                    _card_cache[card_id] = names
                    return names

        _card_cache[card_id] = {}
        return {}
    except Exception as e:
        print(f"Error loading card {card_id}: {e}")
        return {}


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
