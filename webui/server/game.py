import uuid
from fireplace import cards
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import random_class, random_draft
from .card_text import card_text_loader

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

        p1_class = random_class() if player1_class == "random" else cards.db[player1_class]
        if mode == "pve":
            p2_class = random_class() if player2_class is None else cards.db[player2_class]
        else:
            p2_class = random_class()

        p1_deck = random_draft(p1_class)
        p2_deck = random_draft(p2_class)

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
        return data

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
                "can_end_turn": game.current_player == player
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

manager = GameManager()
