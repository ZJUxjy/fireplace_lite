from ..utils import *


##
# Minions

# END_000: Eventuality (2费 法术)
# 将一张随机卡牌置入你的手牌两次
class END_000:
    """Eventuality"""

    # 将一张随机卡牌置入你的手牌两次
    play = Give(CONTROLLER, RandomCard()), Give(CONTROLLER, RandomCard())


# TIME_036: Royal Informant (3费 2/4)
# 战吼：发现一张连击牌
class TIME_036:
    """Royal Informant"""

    # 战吼：发现一张连击牌
    play = Discover(CONTROLLER, RandomCard())


# TIME_710: Troubled Double (4费 3/3)
# 战吼：召唤一个自己的复制
class TIME_710:
    """Troubled Double"""

    # 战吼：召唤一个自己的复制
    play = Summon(CONTROLLER, "TIME_710")


# TIME_713: Time Adm'ral Hooktail (5费 4/6)
# 战吼：召唤一个时间宝箱
class TIME_713:
    """Time Adm'ral Hooktail"""

    # 战吼：召唤一个时间宝箱
    play = Summon(CONTROLLER, "TIME_713t")


# TIME_713t: Timeless Chest (3费 0/8)
class TIME_713t:
    """Timeless Chest"""

    # 亡语：获得两张时间卡
    deathrattle = Give(CONTROLLER, RandomCard()) * 2


# TIME_770: Fast Forward (4费 法术)
# 将你的手牌翻转为你的牌库
class TIME_770:
    """Fast Forward"""

    # 将你的手牌翻转为你的牌库
    def play(self):
        hand = list(self.controller.hand)
        hand_count = len(hand)
        for card in hand:
            card.zone = Zone.DECK
        self.controller.shuffle_deck()
        for _ in range(hand_count):
            yield Draw(CONTROLLER)


# TIME_875: Garona Halforcen (4费 5/4)
# 战吼：发现一个国王
class TIME_875:
    """Garona Halforcen"""

    # 战吼：发现一个国王
    play = Discover(CONTROLLER, RandomMinion())


# TIME_876: Shapeshifter (1费 1/1)
# 战吼：将一个随机随从置入你的手牌
class TIME_876:
    """Shapeshifter"""

    # 战吼：将一个随机随从置入你的手牌
    play = Give(CONTROLLER, RandomMinion())


# TIME_001: Chrono Daggers (3费 武器)
# 在你的回合结束时，你的武器获得+1攻击力
class TIME_001:
    """Chrono Daggers"""

    # 在你的回合结束时，你的武器获得+1攻击力
    events = OWN_TURN_END.on(Buff(FRIENDLY_WEAPON, "TIME_001e"))


TIME_001e = buff(+1, 0)


# TIME_039: Deja Vu (1费 法术)
# 将一张你本回合使用的卡牌置入你的手牌
class TIME_039:
    """Deja Vu"""

    # 将一张你本回合使用的卡牌置入你的手牌
    def play(self):
        played = [
            c for c in self.controller.cards_played_this_game
            if c.turn_played == self.game.turn and c.id != "TIME_039"
        ]
        if played:
            yield Give(CONTROLLER, played[-1].id)


# TIME_711: Flashback (2费 法术)
# 召唤两个随机的1费随从。连击：获得+1攻击力
class TIME_711:
    """Flashback"""

    # 召唤两个随机的1费随从
    play = Summon(CONTROLLER, RandomMinion(cost=1)) * 2

    # 连报：获得+1攻击力
    combo = Buff(SELF, "TIME_711e")


TIME_711e = buff(+1, 0)


# TIME_712: Dethrone (7费 法术)
# 将你的牌库的底牌置入你的手牌
class TIME_712:
    """Dethrone"""

    # 将你的牌库的底牌置入你的手牌
    def play(self):
        if self.controller.deck:
            card = self.controller.deck[0]  # deck[0] is the bottom card
            yield Draw(CONTROLLER, CARD(card))
