import uuid
from fireplace import cards
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import random_class, random_draft

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
                "hand": [str(c) for c in player.hand],
                "field": [{"name": str(m), "atk": m.atk, "health": m.health} for m in player.field],
                "can_end_turn": game.current_player == player
            },
            "opponent": {
                "hero": str(opponent.hero),
                "health": opponent.hero.health,
                "deck": len(opponent.deck),
                "hand_count": len(opponent.hand),
                "field": [{"name": str(m), "atk": m.atk, "health": m.health} for m in opponent.field]
            }
        }

manager = GameManager()
