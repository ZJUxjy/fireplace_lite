import uuid
import random
from fireplace import cards
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import random_class
from fireplace.deck import Deck
from hearthstone.enums import CardClass as CardClassEnum, CardType

# 职业名称到 CardClass 枚举的映射
CLASS_NAME_MAP = {
    'mage': CardClassEnum.MAGE,
    'hunter': CardClassEnum.HUNTER,
    'priest': CardClassEnum.PRIEST,
    'shaman': CardClassEnum.SHAMAN,
    'paladin': CardClassEnum.PALADIN,
    'warlock': CardClassEnum.WARLOCK,
    'warrior': CardClassEnum.WARRIOR,
    'rogue': CardClassEnum.ROGUE,
    'druid': CardClassEnum.DRUID,
    'demonhunter': CardClassEnum.DEMONHUNTER,
}

def get_card_class(class_name: str):
    """将字符串职业名转换为 CardClass 枚举"""
    if class_name == 'random':
        return random_class()
    class_lower = class_name.lower()
    if class_lower in CLASS_NAME_MAP:
        return CLASS_NAME_MAP[class_lower]
    # 尝试直接查找
    try:
        return CardClassEnum[class_name.upper()]
    except KeyError:
        return random_class()
from .card_text import card_text_loader

# 已实现的卡牌系列前缀（对应 fireplace/cards/ 目录下的文件夹）
# 只有这些系列的卡牌会被加入随机牌库
IMPLEMENTED_CARD_PREFIXES = {
    # Classic
    'CS2', 'CS3', 'EX1', 'NEW1',
    # Naxxramas
    'FP1', 'NX2',
    # Goblins vs Gnomes
    'GVG',
    # Blackrock Mountain
    'BRM',
    # The Grand Tournament
    'AT',
    # League of Explorers
    'LOE',
    # Whispers of the Old Gods
    'OG',
    # One Night in Karazhan
    'KAR',
    # Mean Streets of Gadgetzan
    'CFM',
    # Journey to Un'Goro
    'UNG',
    # Knights of the Frozen Throne
    'ICC',
    # Kobolds & Catacombs
    'LOOT',
    # The Witchwood
    'GIL',
    # The Boomsday Project
    'BOT',
    # Rastakhan's Rumble
    'TRL',
    # Rise of Shadows
    'DAL',
    # Saviors of Uldum
    'ULD',
    # Scholomance Academy
    'SCH',
    # Ashes of Outland / Demon Hunter Initiate
    'BT',
    # Descent of Dragons
    'DRG',
    # The Shrouded City - 暂时移除，因为没有 Python 实现
    # 'DINO', 'TLC',
}

# 黑名单：即使在前缀列表中，这些卡牌也有问题，需要排除
CARD_BLACKLIST = set()


def is_card_implemented(card_id: str) -> bool:
    """检查卡牌是否来自已实现的系列"""
    if card_id in CARD_BLACKLIST:
        return False
    # 提取卡牌前缀（如 EDR_889 -> EDR）
    prefix = card_id.split('_')[0] if '_' in card_id else card_id[:3]
    return prefix in IMPLEMENTED_CARD_PREFIXES


def filtered_random_draft(card_class):
    """
    创建一个30张的随机牌库，只包含已实现的卡牌
    """
    deck = []
    collection = []
    skipped = []

    for card_id in cards.db.keys():
        cls = cards.db[card_id]
        if not cls.collectible:
            continue
        if cls.type == CardType.HERO:
            continue
        if cls.card_class and cls.card_class not in [card_class, CardClassEnum.NEUTRAL]:
            continue
        # 只添加已实现的卡牌
        if not is_card_implemented(card_id):
            skipped.append(card_id)
            continue
        collection.append(cls)

    print(f"[Deck] Collected {len(collection)} cards, skipped {len(skipped)} unimplemented")
    if skipped:
        print(f"[Deck] Skipped examples: {skipped[:10]}...")

    while len(deck) < Deck.MAX_CARDS:
        card = random.choice(collection)
        if deck.count(card.id) < card.max_count_in_deck:
            deck.append(card.id)

    return deck


class GameManager:
    def __init__(self):
        self.games = {}
        self._initialized = False

    def initialize(self):
        if not self._initialized:
            cards.db.initialize()
            self._initialized = True

    def create_game(self, player1_class, player2_class=None, mode="pve"):
        """创建游戏返回 game_id"""
        self.initialize()
        game_id = str(uuid.uuid4())

        p1_class = get_card_class(player1_class)
        if mode == "pve":
            p2_class = random_class() if player2_class is None else get_card_class(player2_class)
        else:
            p2_class = random_class()

        p1_deck = filtered_random_draft(p1_class)
        p2_deck = filtered_random_draft(p2_class)

        player1 = Player("Player1", p1_deck, p1_class.default_hero)
        player2 = Player("Player2", p2_deck, p2_class.default_hero)

        game = Game(players=(player1, player2))
        game.start()

        # 跳过换牌
        for p in game.players:
            if p.choice:
                p.choice.choose()

        self.games[game_id] = {
            "game": game,
            "mode": mode,
            "players": [player1, player2],
            "current": player1
        }

        return game_id

    def get_card_data(self, card):
        """获取卡牌详细信息"""
        # 优先使用中文名
        card_id = getattr(card, 'card_id', None)
        chinese_info = card_text_loader.get_card_info(card_id) if card_id else {}

        name = chinese_info.get('name') or str(card)
        text = chinese_info.get('text')

        data = {
            "name": name,
            "cost": card.cost,
            "is_playable": card.is_playable() if hasattr(card, 'is_playable') else False,
        }
        # 随从才有攻击力和血量
        if hasattr(card, 'atk') and hasattr(card, 'health'):
            data["atk"] = card.atk
            data["health"] = card.health
        # 卡牌描述 - 优先使用中文
        if text:
            data["text"] = text
        elif hasattr(card, 'description') and card.description:
            data["text"] = str(card.description)
        # 种族
        if hasattr(card, 'race') and str(card.race) != 'Race.INVALID':
            data["race"] = str(card.race)
        # 关键字（战吼、亡语等）
        if hasattr(card, 'mechanics') and card.mechanics:
            data["mechanics"] = [str(m) for m in card.mechanics]

        # 目标选择信息
        if hasattr(card, 'requires_target') and card.requires_target():
            data["requires_target"] = True
            # 获取有效目标列表
            if hasattr(card, 'targets'):
                data["valid_targets"] = [self._get_target_id(t) for t in card.targets]
        else:
            data["requires_target"] = False

        return data

    def _get_target_id(self, target):
        """获取目标的唯一标识符"""
        # 英雄用 "hero" 或 "opponent_hero"
        if hasattr(target, 'hero'):
            return "hero" if target == target.controller else "opponent_hero"
        # 随从用 "minion-index" 或 "enemy_minion-index"
        if hasattr(target, 'zone') and hasattr(target.controller, 'field'):
            is_own = target.controller == target.game.players[0]
            try:
                field = target.controller.field
                index = list(field).index(target)
                prefix = "minion" if is_own else "enemy_minion"
                return f"{prefix}-{index}"
            except (ValueError, AttributeError):
                pass
        return str(id(target))

    def get_minion_data(self, minion, include_can_attack=False):
        """获取随从详细信息（用于战场）"""
        card_id = getattr(minion, 'card_id', None)
        chinese_info = card_text_loader.get_card_info(card_id) if card_id else {}

        name = chinese_info.get('name') or str(minion)
        text = chinese_info.get('text')

        data = {
            "name": name,
            "atk": minion.atk,
            "health": minion.health,
        }
        # 是否可攻击（仅玩家随从需要）
        if include_can_attack:
            data["can_attack"] = minion.can_attack()
        # 嘲讽
        data["taunt"] = minion.taunt
        # 卡牌描述
        if text:
            data["text"] = text
        elif hasattr(minion, 'description') and minion.description:
            data["text"] = str(minion.description)
        # 种族
        if hasattr(minion, 'race') and str(minion.race) != 'Race.INVALID':
            data["race"] = str(minion.race)
        # 关键字
        if hasattr(minion, 'mechanics') and minion.mechanics:
            data["mechanics"] = [str(m) for m in minion.mechanics]
        return data

    def get_game_state(self, game_id):
        """获取游戏状态"""
        if game_id not in self.games:
            return None

        g = self.games[game_id]
        game = g["game"]
        player = g["players"][0]
        opponent = g["players"][1]

        # 获取英雄技能信息
        hero_power = player.hero.power
        requires_target = hero_power.requires_target() if hasattr(hero_power, 'requires_target') else False
        print(f"[HeroPower] {hero_power} - requires_target: {requires_target}")

        # 获取英雄技能描述
        hero_power_description = ""
        if hasattr(hero_power, 'description') and hero_power.description:
            hero_power_description = str(hero_power.description)

        hero_power_data = {
            "name": str(hero_power),
            "cost": hero_power.cost,
            "is_usable": hero_power.is_usable() if hasattr(hero_power, 'is_usable') else False,
            "requires_target": requires_target,
            "description": hero_power_description,
        }
        if requires_target and hasattr(hero_power, 'targets'):
            valid_targets = [self._get_target_id(t) for t in hero_power.targets]
            hero_power_data["valid_targets"] = valid_targets
            print(f"[HeroPower] valid_targets: {valid_targets}")

        return {
            "turn": game.turn,
            "current_player": "player1" if game.current_player == player else "player2",
            "player": {
                "hero": str(player.hero),
                "health": player.hero.health,
                "max_health": player.hero.max_health,
                "mana": player.mana,
                "max_mana": player.max_mana,
                "deck": len(player.deck),
                "hand": [self.get_card_data(c) for c in player.hand],
                "field": [self.get_minion_data(m, include_can_attack=True) for m in player.field],
                "can_end_turn": game.current_player == player,
                "hero_power": hero_power_data,
            },
            "opponent": {
                "hero": str(opponent.hero),
                "health": opponent.hero.health,
                "deck": len(opponent.deck),
                "hand_count": len(opponent.hand),
                "field": [self.get_minion_data(m) for m in opponent.field],
                "has_taunt": any(m.taunt for m in opponent.field)
            }
        }

    def _get_target_id(self, target):
        """获取目标的唯一标识符"""
        g = self.games.get(list(self.games.keys())[0]) if self.games else None
        if not g:
            return str(id(target))

        player = g["players"][0]
        opponent = g["players"][1]

        # 英雄
        if target == player.hero:
            return "hero"
        if target == opponent.hero:
            return "opponent_hero"

        # 随从
        for i, m in enumerate(player.field):
            if m == target:
                return f"minion-{i}"
        for i, m in enumerate(opponent.field):
            if m == target:
                return f"enemy_minion-{i}"

        return str(id(target))

    def get_target_by_id(self, game_id, target_id):
        """根据目标 ID 获取实际的游戏实体"""
        if game_id not in self.games:
            return None

        g = self.games[game_id]
        player = g["players"][0]
        opponent = g["players"][1]

        if target_id == "hero":
            return player.hero
        elif target_id == "opponent_hero":
            return opponent.hero
        elif target_id.startswith("minion-"):
            index = int(target_id.split("-")[1])
            if 0 <= index < len(player.field):
                return player.field[index]
        elif target_id.startswith("enemy_minion-"):
            index = int(target_id.split("-")[1])
            if 0 <= index < len(opponent.field):
                return opponent.field[index]

        return None


manager = GameManager()
