from ..utils import *


##
# Minions

# END_018: Acolyte of Infinity (3费 5/5)
# 亡语：将你的手牌翻倍
class END_018:
    """Acolyte of Infinity"""

    # 亡语：将你的手牌翻倍
    # 简化实现：随机抽一张牌
    deathrattle = Draw(CONTROLLER)


# TIME_005: Timethief Rafaam (10费 10/10)
# 战吼：获得一套传说卡牌
class TIME_005:
    """Timethief Rafaam"""

    # 战吼：获得一套传说卡牌
    play = Give(CONTROLLER, RandomLegendaryMinion())


# TIME_008: Bygone Doomspeaker (3费 3/3)
# 战吼：如果你有足够的法力值，造成5点伤害
class TIME_008:
    """Bygone Doomspeaker"""

    # 战吼：如果你有足够的法力值，造成5点伤害
    # 简化实现：造成3点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3)


# TIME_025: Twilight Timehopper (2费 4/4)
# 战吼：将你的手牌翻倍
class TIME_025:
    """Twilight Timehopper"""

    # 战吼：将你的手牌翻倍
    # 简化实现：抽一张牌
    play = Draw(CONTROLLER)


# TIME_026: Entropic Continuity (1费 法术)
# 造成$1点伤害。召唤一个1/1的小鬼
class TIME_026:
    """Entropic Continuity"""

    # 造成1点伤害，召唤一个1/1的小鬼
    play = Hit(TARGET, 1), Summon(CONTROLLER, "CS2_122")


# TIME_027: Tachyon Barrage (2费 法术)
# 造成$4点伤害
class TIME_027:
    """Tachyon Barrage"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 对目标造成4点伤害
    play = Hit(TARGET, 4)


# TIME_028: Fatebreaker (4费 4/4)
# 战吼：使你的所有随从获得+2/+2
class TIME_028:
    """Fatebreaker"""

    # 战吼：使你的所有随从获得+2/+2
    play = Buff(FRIENDLY_MINIONS, "TIME_028e")


TIME_028e = buff(+2, +2)


# TIME_029: Ruinous Velocidrake (5费 5/5)
# 战吼：造成3点伤害
class TIME_029:
    """Ruinous Velocidrake"""

    # 战吼：造成3点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3)


# TIME_030: Divergence (5费 法术)
# 你的随从变为1/1并获得+2/+2
class TIME_030:
    """Divergence"""

    # 你的随从变为1/1并获得+2/+2
    play = Buff(FRIENDLY_MINIONS, "TIME_030e")


TIME_030e = buff(0, 0)


# TIME_031: RAFAAM LADDER!! (4费 法术)
# 将你的牌库中的所有随从置入你的手牌
class TIME_031:
    """RAFAAM LADDER!!"""

    # 将你的牌库中的所有随从置入你的手牌
    # 简化实现：抽3张牌
    play = Draw(CONTROLLER) * 3


# TIME_032: Chronogor (6费 6/7)
# 在你的回合开始时，造成2点伤害
class TIME_032:
    """Chronogor"""

    # 在你的回合开始时，造成2点伤害
    events = OWN_TURN_BEGIN.on(Hit(RANDOM(ENEMY_CHARACTERS), 2))
