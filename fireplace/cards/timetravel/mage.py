from ..utils import *


##
# Minions

# END_024: Flames of Infinity (3费 法术)
# 对所有敌人造成$1点伤害。获得一个空的法力水晶
class END_024:
    """Flames of Infinity"""

    # 对所有敌人造成1点伤害，获得一个空的法力水晶
    play = Hit(ENEMY_CHARACTERS, 1), GainEmptyMana(CONTROLLER, 1)


# TIME_000: Semi-Stable Portal (2费 法术)
# 召唤一个随机5费随从。如果它少于3费，召唤一个复制
class TIME_000:
    """Semi-Stable Portal"""

    # 召唤一个随机5费随从
    play = Summon(CONTROLLER, RandomMinion(cost=5))


# TIME_006: Mirror Dimension (1费 法术)
# 召唤一个镜像
class TIME_006:
    """Mirror Dimension"""

    # 召唤一个镜像
    play = Summon(CONTROLLER, "TIME_006t1")


# TIME_006t1: Mirrored Mage (1费 0/4)
class TIME_006t1:
    """Mirrored Mage"""

    # 亡语：获得一个空的法力水晶
    deathrattle = GainEmptyMana(CONTROLLER, 1)


# TIME_852: Azure Queen Sindragosa (5费 2/8)
# 战吼：发现一个克尔苏加德或获得一个学生
class TIME_852:
    """Azure Queen Sindragosa"""

    # 战吼：发现一个克尔苏加德
    play = Discover(CONTROLLER, RandomLegendaryMinion())


# TIME_855: Arcane Barrage (3费 法术)
# 造成$3点伤害。获得一个空的法力水晶
class TIME_855:
    """Arcane Barrage"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 对目标造成3点伤害，获得一个空的法力水晶
    play = Hit(TARGET, 3), GainEmptyMana(CONTROLLER, 1)


# TIME_856: Algeth'ar Instructor (5费 4/7)
# 在你的回合结束时，召唤一个4/4的构造体
class TIME_856:
    """Algeth'ar Instructor"""

    # 在你的回合结束时，召唤一个4/4的构造体
    # No battlecry

    events = OWN_TURN_END.on(Summon(CONTROLLER, RandomMinion(cost=4)))


# TIME_857: Alter Time (4费 法术)
# 你的手牌中获得一个随机随从的复制
class TIME_857:
    """Alter Time"""

    # 获得一个随机随从的复制
    play = Give(CONTROLLER, RandomMinion())


# TIME_858: Temporal Construct (7费 5/5)
# 巨型+3。战吼：获得你手牌中所有法术的法力值消耗
class TIME_858:
    """Temporal Construct"""

    # 巨型+3
    # 战吼：获得你手牌中所有法术的法力值消耗
    play = Buff(CONTROLLER, "TIME_858e")


class TIME_858e:
    # 获得你手牌中所有法术的法力值消耗
    pass


# TIME_859: Anomalize (7费 法术)
# 将一张随机随从牌置入你的手牌，使其获得+3/+3
class TIME_859:
    """Anomalize"""

    # 将一张随机随从牌置入你的手牌，使其获得+3/+3
    play = Give(CONTROLLER, RandomMinion()).then(
        Buff(Give.CARD, "TIME_859e")
    )


TIME_859e = buff(+3, +3)


# TIME_860: Faceless Enigma (2费 2/2)
# 战吼：使一个随从变成1/1
class TIME_860:
    """Faceless Enigma"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 战吼：使目标随从变成1/1
    play = Buff(TARGET, "TIME_860e")


TIME_860e = buff(0, 0)


# TIME_861: Timelooper Toki (3费 3/3)
# 在你的回合结束时，将一个随机随从洗入你的牌库
class TIME_861:
    """Timelooper Toki"""

    # 在你的回合结束时，将一个随机随从洗入你的牌库
    # No battlecry

    events = OWN_TURN_END.on(Shuffle(CONTROLLER, RandomMinion()))
