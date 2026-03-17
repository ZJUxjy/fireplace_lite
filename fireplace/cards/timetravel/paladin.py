from ..utils import *


##
# Minions

# END_012: Hand of Infinity (3费 4/2 武器)
# 战吼：使你的所有随从获得+1攻击力
class END_012:
    """Hand of Infinity"""

    # 战吼：使你的所有随从获得+1攻击力
    play = Buff(FRIENDLY_MINIONS, "END_012e")


END_012e = buff(+1, 0)


# TIME_009: Gelbin of Tomorrow (8费 6/6)
# 抉择：发现一张卡牌；或者召唤3个随机机器人
class TIME_009:
    """Gelbin of Tomorrow"""

    # 抉择：发现一张卡牌；或者召唤3个随机机器人
    choose = ("TIME_009a", "TIME_009b")


class TIME_009a:
    """Tomorrow's Discovery"""

    play = Discover(CONTROLLER, RandomCard())


class TIME_009b:
    """Tomorrow's Arsenal"""

    play = Summon(CONTROLLER, RandomMinion(race=Race.MECHANICAL)) * 3


# TIME_015: Hardlight Protector (2费 2/1)
# 圣盾
class TIME_015:
    """Hardlight Protector"""

    tags = {
        GameTag.DIVINE_SHIELD: True,
    }


# TIME_017: Tankgineer (4费 2/1)
# 战吼：召唤一个4/4的构造体
class TIME_017:
    """Tankgineer"""

    # 战吼：召唤一个4/4的构造体
    play = Summon(CONTROLLER, RandomMinion(cost=4))


# TIME_019: Manifested Timeways (4费 3/3)
# 战吼：获得等同于你手牌数量的攻击力
class TIME_019:
    """Manifested Timeways"""

    # 战吼：获得等同于你手牌数量的攻击力
    # 简化实现：获得+2攻击力
    play = Buff(SELF, "TIME_019e")


class TIME_019e:
    atk = 2


# TIME_043: PMM Infinitizer (6费 4/4)
# 在你的回合结束时，将一个随机随从变为1/1并置入你的手牌
class TIME_043:
    """PMM Infinitizer"""

    # 在你的回合结束时，将一个随机随从变为1/1并置入你的手牌
    events = OWN_TURN_END.on(
        Give(CONTROLLER, RANDOM(FRIENDLY_MINIONS)).then(
            Buff(Give.CARD, "TIME_043e")
        )
    )


TIME_043e = buff(0, 0)


# TIME_700: Chronological Aura (5费 法术)
# 使一个随从获得+3/+3和嘲讽
class TIME_700:
    """Chronological Aura"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 使目标随从获得+3/+3和嘲讽
    play = Buff(TARGET, "TIME_700e")


TIME_700e = buff(+3, +3, taunt=True)


# TIME_706: The Fins Beyond Time (2费 2/3)
# 战吼：使一个友方随从获得剧毒
class TIME_706:
    """The Fins Beyond Time"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 战吼：使目标获得剧毒
    play = Buff(TARGET, "TIME_706e")


TIME_706e = buff(poisonous=True)


# TIME_016: Neon Innovation (3费 法术)
# 将你手牌中所有的随从变成1/1
class TIME_016:
    """Neon Innovation"""

    # 将你手牌中所有的随从变成1/1
    play = Buff(FRIENDLY_HAND + MINION, "TIME_016e")


TIME_016e = buff(0, 0)


# TIME_018: Mend the Timeline (3费 法术)
# 恢复你的英雄8点生命值
class TIME_018:
    """Mend the Timeline"""

    # 恢复你的英雄8点生命值
    play = Heal(TARGET, 8)
