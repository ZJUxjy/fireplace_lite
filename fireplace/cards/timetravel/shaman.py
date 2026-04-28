from ..utils import *


##
# Minions

# END_030: Haywire Hornswog (6费 4/6)
# 战吼：对所有敌人造成2点伤害
class END_030:
    """Haywire Hornswog"""

    # 战吼：对所有敌人造成2点伤害
    play = Hit(ENEMY_CHARACTERS, 2)


# TIME_013: Farseer Wo (4费 2/6)
# 战吼：治疗所有友方角色3点
class TIME_013:
    """Farseer Wo"""

    # 战吼：治疗所有友方角色3点
    play = Heal(FRIENDLY_CHARACTERS, 3)


# TIME_014: Instant Multiverse (6费 法术)
# 发现一个随从并召唤它
class TIME_014:
    """Instant Multiverse"""

    # 发现一个随从并召唤它
    play = Discover(CONTROLLER, RandomMinion()).then(
        Summon(CONTROLLER, Discover.CARD)
    )


# TIME_209: Muradin, High King (5费 3/2)
# 战吼：装备一把高王的锤子
class TIME_209:
    """Muradin, High King"""

    # 战吼：装备一把高王的锤子
    play = Summon(CONTROLLER, "TIME_209t")


# TIME_209t: High King's Hammer (6费 3/4 武器)
class TIME_209t:
    """High King's Hammer"""

    # 战吼：使你的所有随从获得+2攻击力
    play = Buff(FRIENDLY_MINIONS, "TIME_209e")


TIME_209e = buff(+2, 0)


# TIME_212: Lightning Rod (1费 法术)
# 对一个友方随从造成2点伤害以对一个随机敌人随从造成4点伤害
class TIME_212:
    """Lightning Rod"""

    # 对一个友方随从造成2点伤害以对一个随机敌人随从造成4点伤害
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
    }

    play = Hit(TARGET, 2), Hit(RANDOM(ENEMY_MINIONS), 4)


# TIME_213: Primordial Overseer (2费 2/3)
# 在你的回合结束时，召唤一个2/2的元素
class TIME_213:
    """Primordial Overseer"""

    # 在你的回合结束时，召唤一个2/2的元素
    # No battlecry

    events = OWN_TURN_END.on(Summon(CONTROLLER, RandomMinion(race=Race.ELEMENTAL)))


# TIME_214: Flux Revenant (2费 1/4)
# 在你的回合结束时，获得一个空的法力水晶
class TIME_214:
    """Flux Revenant"""

    # 在你的回合结束时，获得一个空的法力水晶
    # No battlecry

    events = OWN_TURN_END.on(GainEmptyMana(CONTROLLER, 1))


# TIME_215: Thunderquake (2费 法术)
# 对所有敌人造成$1点伤害，获得一个空的法力水晶
class TIME_215:
    """Thunderquake"""

    # 对所有敌人造成1点伤害，获得一个空的法力水晶
    play = Hit(ENEMY_CHARACTERS, 1), GainEmptyMana(CONTROLLER, 1)


# TIME_216: Nascent Bolt (3费 法术)
# 造成$2点伤害。发现一张卡牌
class TIME_216:
    """Nascent Bolt"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 对目标造成2点伤害，发现一张卡牌
    play = Hit(TARGET, 2), Discover(CONTROLLER, RandomCard())


# TIME_217: Stormrook (5费 5/5)
# 战吼：造成3点伤害
class TIME_217:
    """Stormrook"""

    # 战吼：造成3点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3)


# TIME_218: Static Shock (0费 法术)
# 造成$1点伤害
class TIME_218:
    """Static Shock"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 对目标造成1点伤害
    play = Hit(TARGET, 1)
