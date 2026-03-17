from ..utils import *


##
# Minions

# END_015: Triennium Rex (5费 5/5)
# 你的野兽获得+2/+2
class END_015:
    """Triennium Rex"""

    # 你的野兽获得+2/+2
    # 简化实现：所有随从获得+2/+2
    update = buff(+2, +2)


# TIME_042: King Maluk (4费 5/6)
# 在你的回合结束时，使你的武器获得+1攻击力
class TIME_042:
    """King Maluk"""

    # 在你的回合结束时，使你的武器获得+1攻击力
    events = OWN_TURN_END.on(Buff(FRIENDLY_WEAPON, "TIME_042e"))


TIME_042e = buff(+1, 0)


# TIME_042t: Infinite Banana (1费 香蕉)
class TIME_042t:
    """Infinite Banana"""

    # 抉择：使一个随从获得+1/+1；或者+2/+1
    choose = ("TIME_042ta", "TIME_042tb")


class TIME_042ta:
    """First Option"""

    pass


class TIME_042tb:
    """Second Option"""

    pass


# TIME_601: Arrow Retriever (2费 3/1)
# 战吼：使一个友方野兽获得亡语：使 Arrow Retriever 回到你的手牌
class TIME_601:
    """Arrow Retriever"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 战吼：使一个友方野兽获得亡语：将该随从置入你的手牌
    play = Buff(TARGET, "TIME_601e")


class TIME_601e:
    """Retrieving"""

    deathrattle = Give(CONTROLLER, "TIME_601")


# TIME_602: Wormhole (3费 法术)
# 发现一个随从。召唤两个它的复制
class TIME_602:
    """Wormhole"""

    # 发现一个随从并召唤两个它的复制
    play = Discover(CONTROLLER, RandomMinion()).then(
        Summon(CONTROLLER, Discover.CARD) * 2
    )


# TIME_603: Ticking Timebomb (2费 1/1)
# 亡语：对所有敌人造成3点伤害
class TIME_603:
    """Ticking Timebomb"""

    # 亡语：对所有敌人造成3点伤害
    deathrattle = Hit(ENEMY_CHARACTERS, 3)


# TIME_605: Epoch Stalker (6费 3/4)
# 战吼：获得你手牌中所有野兽的冲锋
class TIME_605:
    """Epoch Stalker"""

    # 战吼：使你手牌中的所有野兽获得冲锋
    # 简化实现：没有效果
    pass


# TIME_606: Quel'dorei Fletcher (1费 1/3)
# 在你施放一个法术后，使一个友方野兽获得+1攻击力
class TIME_606:
    """Quel'dorei Fletcher"""

    # 在你施放一个法术后，使一个友方野兽获得+1攻击力
    events = OWN_SPELL_PLAY.on(Buff(RANDOM(FRIENDLY_MINIONS + BEAST), "TIME_606e"))


TIME_606e = buff(+1, 0)


# TIME_609: Ranger General Sylvanas (3费 2/4)
# 战吼：发现一个时间流。选择一条时间线！
class TIME_609:
    """Ranger General Sylvanas"""

    # 战吼：发现一个时间流
    play = Discover(CONTROLLER, RandomCard())


# TIME_620: Untimely Death (2费 法术)
# 对一个随从造成4点伤害。如果该随从死亡，召唤一个4/4的幽灵
class TIME_620:
    """Untimely Death"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 对目标造成4点伤害
    def play(self):
        Hit(self.target, 4).trigger(self)
        if self.target.dead:
            Summon(CONTROLLER, "TIME_620t").trigger(self)


# TIME_810: Past Silvermoon (4费 英雄)
# 战吼：召唤两个银月城凤凰
class TIME_810:
    """Past Silvermoon"""

    # 战吼：召唤两个银月城凤凰
    play = Summon(CONTROLLER, "TIME_810t") * 2


# TIME_810t: Present Silvermoon (4费 随从)
class TIME_810t:
    """Silvermoon"""

    pass


# TIME_600: Precise Shot (2费 法术)
# 造成2点伤害。发现一张卡牌
class TIME_600:
    """Precise Shot"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 对目标造成2点伤害，发现一张卡牌
    play = Hit(TARGET, 2), Discover(CONTROLLER, RandomCard())
