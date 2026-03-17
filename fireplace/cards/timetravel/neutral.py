from ..utils import *


##
# Minions

# END_033: Prescient Slitherdrake (7费 6/8)
# 战吼：发现一张龙牌
class END_033:
    """Prescient Slitherdrake"""

    # 战吼：发现一张龙牌
    play = Discover(CONTROLLER, RandomDragon())


# END_034: Crumblecrusher (8费 8/6)
# 战吼：对所有敌人造成2点伤害
class END_034:
    """Crumblecrusher"""

    # 战吼：对所有敌人造成2点伤害
    play = Hit(ENEMY_CHARACTERS, 2)


# END_035: Omen of the End (5费 5/5)
# 战吼：随机将一张卡牌的费用变为0
class END_035:
    """Omen of the End"""

    # 战吼：随机将一张卡牌的费用变为0
    play = Buff(RANDOM(FRIENDLY_HAND), "END_035e")


class END_035e:
    cost = SET(0)


# END_036: Morchie (4费 3/6)
# 在你的回合结束时，对所有敌人造成1点伤害
class END_036:
    """Morchie"""

    # 在你的回合结束时，对所有敌人造成1点伤害
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 1))


# END_037: Endtime Murozond (9费 4/6)
# 战吼：获得你手牌中所有卡牌的费用
class END_037:
    """Endtime Murozond"""

    # 战吼：获得你手牌中所有卡牌的费用
    # 简化实现：获得5点法力值
    play = GainMana(CONTROLLER, 5)


# TIME_002: Aeon Wizard (5费 3/5)
# 在你的回合结束时，对所有敌人造成2点伤害
class TIME_002:
    """Aeon Wizard"""

    # 在你的回合结束时，对所有敌人造成2点伤害
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 2))


# TIME_003: Portal Vanguard (3费 2/2)
# 战吼：对所有敌人造成1点伤害
class TIME_003:
    """Portal Vanguard"""

    # 战吼：对所有敌人造成1点伤害
    play = Hit(ENEMY_CHARACTERS, 1)


# TIME_004: Conflux Crasher (7费 7/7)
# 战吼：造成3点伤害
class TIME_004:
    """Conflux Crasher"""

    # 战吼：造成3点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3)


# TIME_024: Murozond, Unbounded (9费 8/8)
# 战吼：获得你手牌中所有卡牌的费用
class TIME_024:
    """Murozond, Unbounded"""

    # 战吼：获得你手牌中所有卡牌的费用
    # 简化实现：获得5点法力值
    play = GainMana(CONTROLLER, 5)


# TIME_035: Time Machine (6费 6/6)
# 在你的回合结束时，召唤一个4/4的构造体
class TIME_035:
    """Time Machine"""

    # 在你的回合结束时，召唤一个4/4的构造体
    events = OWN_TURN_END.on(Summon(CONTROLLER, RandomMinion(cost=4)))


# TIME_038: Mister Clocksworth (8费 3/3)
# 战吼：发现一个时间点
class TIME_038:
    """Mister Clocksworth"""

    # 战吼：发现一个时间点
    play = Discover(CONTROLLER, RandomCard())


# TIME_040: Fading Memory (4费 6/3)
# 战吼：将一个随机随从的费用变为0
class TIME_040:
    """Fading Memory"""

    # 战吼：将一个随机随从的费用变为0
    play = Buff(RANDOM(FRIENDLY_HAND + MINION), "TIME_040e")


class TIME_040e:
    cost = SET(0)


# TIME_041: Futuristic Forefather (4费 4/4)
# 在你的回合开始时，获得一个空的法力水晶
class TIME_041:
    """Futuristic Forefather"""

    # 在你的回合开始时，获得一个空的法力水晶
    events = OWN_TURN_BEGIN.on(GainEmptyMana(CONTROLLER, 1))


# TIME_045: Whelp of the Infinite (3费 1/4)
# 战吼：获得一个空的法力水晶
class TIME_045:
    """Whelp of the Infinite"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_046: Cyborg Patriarch (3费 3/12)
# 在你的回合开始时，获得一个空的法力水晶
class TIME_046:
    """Cyborg Patriarch"""

    # 在你的回合开始时，获得一个空的法力水晶
    events = OWN_TURN_BEGIN.on(GainEmptyMana(CONTROLLER, 1))


# TIME_047: Devious Coyote (5费 5/3)
# 战吼：获得一个空的法力水晶
class TIME_047:
    """Devious Coyote"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_048: Clockwork Rager (5费 5/1)
# 在你的回合结束时，获得+2攻击力
class TIME_048:
    """Clockwork Rager"""

    # 在你的回合结束时，获得+2攻击力
    events = OWN_TURN_END.on(Buff(SELF, "TIME_048e"))


TIME_048e = buff(+2, 0)


# TIME_049: Dangerous Variant (2费 1/1)
# 战吼：造成2点伤害
class TIME_049:
    """Dangerous Variant"""

    # 战吼：造成2点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# TIME_050: Sentient Hourglass (6费 4/9)
# 在你的回合结束时，对所有敌人造成2点伤害
class TIME_050:
    """Sentient Hourglass"""

    # 在你的回合结束时，对所有敌人造成2点伤害
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 2))


# TIME_051: Soldier of the Infinite (5费 3/5)
# 战吼：获得+2/+2
class TIME_051:
    """Soldier of the Infinite"""

    # 战吼：获得+2/+2
    play = Buff(SELF, "TIME_051e")


TIME_051e = buff(+2, +2)


# TIME_052: Amber Warden (8费 4/12)
# 战吼：获得一个空的法力水晶
class TIME_052:
    """Amber Warden"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_053: Sandmaw (3费 7/2)
# 战吼：对一个随机敌人造成4点伤害
class TIME_053:
    """Sandmaw"""

    # 战吼：对一个随机敌人造成4点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 4)


# TIME_054: Time Skipper (4费 3/4)
# 战吼：将你的手牌翻倍
class TIME_054:
    """Time Skipper"""

    # 战吼：将你的手牌翻倍
    # 简化实现：抽一张牌
    play = Draw(CONTROLLER)


# TIME_055: Unknown Voyager (5费 4/5)
# 战吼：发现一张卡牌
class TIME_055:
    """Unknown Voyager"""

    # 战吼：发现一张卡牌
    play = Discover(CONTROLLER, RandomCard())


# TIME_056: Whelp of the Bronze (3费 4/1)
# 战吼：获得一个空的法力水晶
class TIME_056:
    """Whelp of the Bronze"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_057: Wizened Truthseeker (4费 4/5)
# 在你的回合开始时，发现一张卡牌
class TIME_057:
    """Wizened Truthseeker"""

    # 在你的回合开始时，发现一张卡牌
    events = OWN_TURN_BEGIN.on(Discover(CONTROLLER, RandomCard()))


# TIME_058: Paltry Flutterwing (1费 1/1)
# 亡语：获得一个空的法力水晶
class TIME_058:
    """Paltry Flutterwing"""

    # 亡语：获得一个空的法力水晶
    deathrattle = GainEmptyMana(CONTROLLER, 1)


# TIME_059: Living Paradox (3费 2/1)
# 战吼：获得一个空的法力水晶
class TIME_059:
    """Living Paradox"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_060: Quantum Destabilizer (3费 4/9)
# 战吼：对所有敌人造成2点伤害
class TIME_060:
    """Quantum Destabilizer"""

    # 战吼：对所有敌人造成2点伤害
    play = Hit(ENEMY_CHARACTERS, 2)


# TIME_061: Timeless Causality (2费 3/2)
# 战吼：获得一个空的法力水晶
class TIME_061:
    """Timeless Causality"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_062: Chronicle Keeper (4费 3/6)
# 在你的回合结束时，抽一张牌
class TIME_062:
    """Chronicle Keeper"""

    # 在你的回合结束时，抽一张牌
    events = OWN_TURN_END.on(Draw(CONTROLLER))


# TIME_063: Timelord Nozdormu (3费 8/8)
# 在你的回合开始时，对所有敌人造成2点伤害
class TIME_063:
    """Timelord Nozdormu"""

    # 在你的回合开始时，对所有敌人造成2点伤害
    events = OWN_TURN_BEGIN.on(Hit(ENEMY_CHARACTERS, 2))


# TIME_064: Chrono-Lord Deios (7费 4/8)
# 在你的回合结束时，对所有敌人造成3点伤害
class TIME_064:
    """Chrono-Lord Deios"""

    # 在你的回合结束时，对所有敌人造成3点伤害
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 3))


# TIME_100: Hourglass Attendant (4费 2/4)
# 你的卡牌获得+1攻击力
class TIME_100:
    """Hourglass Attendant"""

    # 你的卡牌获得+1攻击力
    update = buff(+1, 0)


# TIME_101: Misplaced Pyromancer (3费 4/3)
# 战吼：对所有敌人造成1点伤害
class TIME_101:
    """Misplaced Pyromancer"""

    # 战吼：对所有敌人造成1点伤害
    play = Hit(ENEMY_CHARACTERS, 1)


# TIME_102: Circadiamancer (3费 2/2)
# 在你的回合开始时，获得一个空的法力水晶
class TIME_102:
    """Circadiamancer"""

    # 在你的回合开始时，获得一个空的法力水晶
    events = OWN_TURN_BEGIN.on(GainEmptyMana(CONTROLLER, 1))


# TIME_103: Chromie (6费 4/6)
# 在你的回合结束时，将你的手牌翻倍
class TIME_103:
    """Chromie"""

    # 在你的回合结束时，将你的手牌翻倍
    # 简化实现：抽一张牌
    events = OWN_TURN_END.on(Draw(CONTROLLER))


# TIME_428: Yesterloc (2费 3/1)
# 战吼：将一张随机随从的费用变为0
class TIME_428:
    """Yesterloc"""

    # 战吼：将一张随机随从的费用变为0
    play = Buff(RANDOM(FRIENDLY_HAND + MINION), "TIME_428e")


class TIME_428e:
    cost = SET(0)


# TIME_434: Temporal Traveler (3费 4/1)
# 战吼：造成2点伤害
class TIME_434:
    """Temporal Traveler"""

    # 战吼：造成2点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# TIME_720: Soldier of the Bronze (5费 5/3)
# 战吼：获得+2/+2
class TIME_720:
    """Soldier of the Bronze"""

    # 战吼：获得+2/+2
    play = Buff(SELF, "TIME_720e")


TIME_720e = buff(+2, +2)
