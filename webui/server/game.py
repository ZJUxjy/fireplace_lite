import uuid
import random
from datetime import datetime
from fireplace import cards
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import random_class
from fireplace.deck import Deck
from hearthstone.enums import CardClass as CardClassEnum, CardType

# 游戏日志收集器
class GameLogger:
    def __init__(self):
        self.logs = []
        self.max_logs = 100

    def add_log(self, log_type: str, message: str, details: dict = None):
        """添加一条日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': log_type,
            'message': message,
            'details': details or {}
        }
        self.logs.append(log_entry)
        # 限制日志数量
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]

    def get_logs(self, count=20):
        """获取最近N条日志"""
        return self.logs[-count:]

    def clear(self):
        """清空日志"""
        self.logs = []

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


# 测试卡组：各职业的关键机制卡牌
TEST_DECK_CARDS = {
    # 中立卡牌（所有职业可用）
    'NEUTRAL': {
        # 基础机制
        'divine_shield': ['EX1_008', 'CS2_122'],  # 银色侍从、白银之手骑士
        'taunt': ['CS1_042', 'CS2_179', 'EX1_093'],  # 闪金镇步兵、森金持盾卫士、阿古斯之盾
        'windfury': ['CS2_231', 'NEW1_038'],  # 愤怒的小鸡、风领主奥拉基尔
        'stealth': ['EX1_593', 'NEW1_014'],  # 夜刃刺客、猢狲战士
        'deathrattle': ['EX1_534', 'FP1_002', 'LOOT_161'],  # 长鬃草原狮、鬼灵蜘蛛、龙骨卫士
        'poisonous': ['EX1_170', 'UNG_937'],  # 帝王眼镜蛇、翼手龙毒刺
        'lifesteal': ['ICC_855', 'BOT_423'],  # 鲜血掠夺者、鲁莽试验者
        'charge': ['CS2_103', 'EX1_084'],  # 冲锋、狼骑兵
        'rush': ['AV_132', 'AV_215', 'SCH_311'],  # Troll Centurion, Frantic Hippogryph, Animated Broomstick
        # 战吼
        'battlecry': ['CS2_141', 'CS2_189'],  # 侏儒发明家、精灵龙
    },
    # 法师
    'MAGE': {
        'freeze': ['CS2_026', 'CS2_033'],  # 冰霜新星、水元素
        'spell_damage': ['CS2_155', 'EX1_584'],  # 大法师、食人魔法师
        'secrets': ['EX1_294', 'EX1_295', 'EX1_287', 'EX1_289', 'EX1_594', 'ICC_082'],  # 寒冰屏障、寒冰护体、法术反制、寒冰护体(攻击)、蒸发、寒冰克隆
        'fire_spell': ['CS2_029', 'CS2_028'],  # 火球术、暴风雪
    },
    # 猎人
    'HUNTER': {
        'beast': ['CS2_172', 'EX1_534'],  # 血沼迅猛龙、长鬃草原狮
        'deathrattle': ['EX1_534', 'ICC_825'],  # 长鬃草原狮、熊鲨
        'secrets': ['EX1_533', 'EX1_609', 'EX1_610', 'EX1_611', 'EX1_554'],  # 误导、狙击、爆炸陷阱、冰冻陷阱、毒蛇陷阱
    },
    # 战士
    'WARRIOR': {
        'armor': ['EX1_402', 'EX1_606'],  # 炽炎战斧、盾牌格挡
        'enrage': ['EX1_393', 'EX1_412'],  # 阿曼尼狂战士、暴怒的狼人
        'charge': ['CS2_103', 'EX1_084'],  # 冲锋、狼骑兵
    },
    # 圣骑士
    'PALADIN': {
        'divine_shield': ['EX1_008', 'CS2_122'],  # 银色侍从
        'hand_buff': ['UNG_950', 'CFM_650'],  # 剑龙骑术、适者生存
        'secrets': ['EX1_130', 'EX1_136', 'EX1_132', 'EX1_379'],  # 崇高牺牲、救赎、以眼还眼、忏悔
        'immune': ['CS2_087'],  # 保护之手
    },
    # 潜行者
    'ROGUE': {
        'combo': ['EX1_131', 'CS2_073', 'CS2_072'],  # 军情七处特工、冷血、背刺
        'stealth': ['NEW1_014', 'EX1_522'],  # 猢狲战士、耐心的刺客
        'weapon': ['CS2_080', 'EX1_133'],  # 刺客之刃、毁灭之刃
        'damage_spell': ['EX1_124', 'EX1_145'],  # 剔骨、准备
    },
    # 牧师
    'PRIEST': {
        'heal': ['CS1_130', 'CS2_004'],  # 神圣惩击、真言术：盾
        'buff': ['CS2_236', 'EX1_339'],  # 神圣之灵、暗言术：痛
        'silence': ['EX1_332'],  # 沉默
    },
    # 德鲁伊
    'DRUID': {
        'choose_one': ['EX1_164', 'EX1_165'],  # 滋养、丛林守护者
        'ramp': ['CS2_013', 'EX1_169'],  # 野性成长、激活（可能为技能）
        'taunt': ['EX1_093', 'CS2_179'],  # 阿古斯之盾、森金持盾卫士
    },
    # 萨满
    'SHAMAN': {
        'overload': ['EX1_248', 'EX1_251'],  # 野性狼魂、闪电风暴
        'totem': ['CS2_050', 'UNG_201'],  # 石爪图腾、原始融合
        'windfury': ['EX1_259', 'UNG_938'],  # 风暴看守、雷霆万钧
    },
    # 术士
    'WARLOCK': {
        'demon': ['CS2_064', 'EX1_306'],  # 恐惧地狱火、魅魔
        'discard': ['EX1_308', 'EX1_310'],  # 灵魂之火、末日守卫
        'spell_damage': ['EX1_597', 'NEW1_021'],  # 古拉巴什狂暴者、狂野炎术师
    },
}


def create_test_deck(card_class):
    """
    创建测试卡组，包含各种已实现的机制卡牌
    优先选择职业特色机制，补足30张
    """
    deck = []
    class_name = card_class.name

    # 1. 添加本职业机制卡牌
    if class_name in TEST_DECK_CARDS:
        for mechanic, cards in TEST_DECK_CARDS[class_name].items():
            # 每种机制最多2张
            for card_id in cards[:2]:
                if len(deck) < 30:
                    deck.append(card_id)

    # 2. 添加中立机制卡牌补足
    neutral_cards = []
    for mechanic, cards in TEST_DECK_CARDS['NEUTRAL'].items():
        neutral_cards.extend(cards)

    # 随机打乱，确保不同测试卡组有变化
    import random
    random.shuffle(neutral_cards)

    # 补满30张
    for card_id in neutral_cards:
        if len(deck) >= 30:
            break
        # 检查是否已有2张
        if deck.count(card_id) < 2:
            deck.append(card_id)

    # 3. 如果还不够，随机填充
    while len(deck) < 30:
        deck.append(random.choice(neutral_cards))

    print(f"[TestDeck] Created {class_name} test deck with {len(deck)} cards")
    return deck


class GameManager:
    def __init__(self):
        self.games = {}
        self._initialized = False

    def initialize(self):
        if not self._initialized:
            cards.db.initialize()
            self._initialized = True

    def create_game(self, player1_class, player2_class=None, mode="pve", test_deck=False):
        """创建游戏返回 game_id

        Args:
            player1_class: 玩家1职业
            player2_class: 玩家2职业 (PVE模式下对手职业)
            mode: 游戏模式 (pve/pvp)
            test_deck: 是否使用测试卡组（包含各种机制卡牌）
        """
        self.initialize()
        game_id = str(uuid.uuid4())

        p1_class = get_card_class(player1_class)
        if mode == "pve":
            p2_class = random_class() if player2_class is None else get_card_class(player2_class)
        else:
            p2_class = random_class()

        # 选择卡组生成方式
        if test_deck:
            p1_deck = create_test_deck(p1_class)
            p2_deck = create_test_deck(p2_class)
        else:
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

        # 创建游戏日志记录器
        logger = GameLogger()
        logger.add_log('game_start', f'游戏开始 - {player1} vs {player2}', {
            'player1': str(player1),
            'player2': str(player2)
        })

        self.games[game_id] = {
            "game": game,
            "mode": mode,
            "players": [player1, player2],
            "current": player1,
            "logger": logger,
            "turn_start_time": datetime.now(),
            "turn_timeout": player1.timeout
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

        # 吸血(Lifesteal)
        if hasattr(card, 'lifesteal') and card.lifesteal:
            data["lifesteal"] = True

        # 连击(Combo)
        if hasattr(card, 'has_combo') and card.has_combo:
            data["has_combo"] = True

        # 剧毒(Poisonous)
        if hasattr(card, 'poisonous') and card.poisonous:
            data["poisonous"] = True

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
        # 获取游戏实例来查找玩家
        g = self.games.get(list(self.games.keys())[0]) if self.games else None
        if not g:
            return str(id(target))

        player = g["players"][0]
        opponent = g["players"][1]

        # 英雄 - 直接比较（最高优先级）
        if target == player.hero:
            return "hero"
        if target == opponent.hero:
            return "opponent_hero"

        # 随从 - 检查是否在玩家的战场上
        # 检查敌方随从（对手的战场）
        for i, m in enumerate(opponent.field):
            if m == target:
                return f"enemy_minion-{i}"

        # 检查己方随从（玩家的战场）
        for i, m in enumerate(player.field):
            if m == target:
                return f"minion-{i}"

        # 检查是否有控制器（可能是英雄或武器）
        if hasattr(target, 'controller'):
            if target.controller == player:
                # 检查是否是英雄类型
                if hasattr(target, 'type') and target.type == CardType.HERO:
                    return "hero"
                return "hero"  # Assume hero if controlled by player
            if target.controller == opponent:
                if hasattr(target, 'type') and target.type == CardType.HERO:
                    return "opponent_hero"
                return "opponent_hero"

        # 如果以上都不匹配，使用id作为fallback
        print(f"[TargetID] Could not identify target: {target}, type: {type(target)}")
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
            # 基础 can_attack 检查
            can_attack = minion.can_attack()
            # 对于 Charge/Rush 随从，在第一回合需要特殊处理
            has_charge = getattr(minion, 'charge', False)
            has_rush = getattr(minion, 'rush', False)
            turns_in_play = getattr(minion, 'turns_in_play', 0)
            num_attacks = getattr(minion, 'num_attacks', 0)
            max_attacks = getattr(minion, 'max_attacks', 1)
            # 如果随从有 Charge/Rush，是第一回合，且还可以攻击
            if (has_charge or has_rush) and turns_in_play == 0 and num_attacks < max_attacks:
                can_attack = True
            data["can_attack"] = can_attack
        # 嘲讽
        data["taunt"] = minion.taunt
        # 亡语
        data["has_deathrattle"] = getattr(minion, 'has_deathrattle', False)
        # 圣盾
        data["divine_shield"] = getattr(minion, 'divine_shield', False)
        # 潜行
        data["stealth"] = getattr(minion, 'stealthed', False)
        # 风怒
        data["windfury"] = getattr(minion, 'windfury', False)
        # 冻结
        data["frozen"] = getattr(minion, 'frozen', False)
        # 剧毒
        data["poisonous"] = getattr(minion, 'poisonous', False)
        # 冲锋
        data["charge"] = getattr(minion, 'charge', False)
        # 突袭
        data["rush"] = getattr(minion, 'rush', False)
        # 登场回合数 (用于Charge/Rush判断)
        data["turns_in_play"] = getattr(minion, 'turns_in_play', 0)
        # 免疫
        data["immune"] = getattr(minion, 'immune', False)
        # 沉默
        data["silenced"] = getattr(minion, 'silenced', False)
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

    def get_secret_data(self, secret):
        """获取奥秘信息（仅用于玩家自己的奥秘）"""
        card_id = getattr(secret, 'card_id', None)
        chinese_info = card_text_loader.get_card_info(card_id) if card_id else {}

        name = chinese_info.get('name') or str(secret)
        text = chinese_info.get('text')

        data = {
            "name": name,
            "id": card_id,
        }
        if text:
            data["text"] = text
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

        # 获取日志
        logger = g.get("logger")
        logs = logger.get_logs(30) if logger else []

        # 获取武器信息
        def get_weapon_data(hero):
            weapon = hero.weapon
            if weapon:
                return {
                    "name": str(weapon),
                    "atk": getattr(weapon, 'atk', 0),
                    "durability": getattr(weapon, 'durability', 0),
                    "max_durability": getattr(weapon, 'max_durability', getattr(weapon, 'durability', 0)),
                }
            return None

        # 计算回合剩余时间
        turn_start = g.get("turn_start_time")
        timeout = g.get("turn_timeout", 75)
        elapsed = (datetime.now() - turn_start).total_seconds() if turn_start else 0
        turn_remaining = max(0, timeout - elapsed)

        return {
            "turn": game.turn,
            "current_player": "player1" if game.current_player == player else "player2",
            "turn_remaining": int(turn_remaining),
            "turn_timeout": timeout,
            "player": {
                "hero": str(player.hero),
                "health": player.hero.health,
                "max_health": player.hero.max_health,
                "armor": getattr(player.hero, 'armor', 0),
                "mana": player.mana,
                "max_mana": player.max_mana,
                "spell_power": getattr(player, 'spellpower', 0),
                "deck": len(player.deck),
                "hand": [self.get_card_data(c) for c in player.hand],
                "field": [self.get_minion_data(m, include_can_attack=True) for m in player.field],
                "can_end_turn": game.current_player == player,
                "hero_power": hero_power_data,
                "weapon": get_weapon_data(player.hero),
                "fatigue_counter": getattr(player, 'fatigue_counter', 0),
                "hand_size": len(player.hand),
                "max_hand_size": getattr(player, 'max_hand_size', 10),
                "field_size": len(player.field),
                "max_field_size": getattr(game, 'MAX_MINIONS_ON_FIELD', 7),
                "secrets": [self.get_secret_data(s) for s in player.secrets],
                "secret_count": len(player.secrets),
            },
            "opponent": {
                "hero": str(opponent.hero),
                "health": opponent.hero.health,
                "max_health": opponent.hero.max_health,
                "armor": getattr(opponent.hero, 'armor', 0),
                "mana": opponent.mana,
                "max_mana": opponent.max_mana,
                "spell_power": getattr(opponent, 'spellpower', 0),
                "deck": len(opponent.deck),
                "hand_count": len(opponent.hand),
                "fatigue_counter": getattr(opponent, 'fatigue_counter', 0),
                "field": [self.get_minion_data(m) for m in opponent.field],
                "has_taunt": any(m.taunt for m in opponent.field),
                "hero_power": {
                    "name": str(opponent.hero.power),
                    "cost": opponent.hero.power.cost,
                    "is_usable": opponent.hero.power.is_usable() if hasattr(opponent.hero.power, 'is_usable') else False,
                    "requires_target": opponent.hero.power.requires_target() if hasattr(opponent.hero.power, 'requires_target') else False,
                    "description": str(opponent.hero.power.description) if hasattr(opponent.hero.power, 'description') else "",
                },
                "weapon": get_weapon_data(opponent.hero),
                "secret_count": len(opponent.secrets),
            },
            "logs": logs
        }


    def log_event(self, game_id, log_type, message, details=None):
        """记录游戏事件"""
        if game_id in self.games:
            logger = self.games[game_id].get("logger")
            if logger:
                logger.add_log(log_type, message, details)

    def on_turn_start(self, game_id):
        """回合开始时的回调，更新回合开始时间"""
        if game_id in self.games:
            g = self.games[game_id]
            g["turn_start_time"] = datetime.now()
            # 更新timeout为当前玩家的timeout
            current_player = g["game"].current_player
            g["turn_timeout"] = getattr(current_player, 'timeout', 75)

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
