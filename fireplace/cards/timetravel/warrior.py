from ..utils import *


##
# Minions

# END_021: Dimensional Weaponsmith (3费 2/5)
# 战吼：装备一把随机武器
class END_021:
    """Dimensional Weaponsmith"""

    # 战吼：装备一把随机武器
    play = Summon(CONTROLLER, RandomWeapon())


# TIME_034: Stadium Announcer (4费 3/3)
# 在你的回合结束时，造成2点伤害
class TIME_034:
    """Stadium Announcer"""

    # 在你的回合结束时，造成2点伤害
    # No battlecry

    events = OWN_TURN_END.on(Hit(RANDOM(ENEMY_CHARACTERS), 2))


# TIME_714: Chrono-Lord Epoch (6费 7/5)
# 战吼：将所有随从移回各自拥有者的手牌
class TIME_714:
    """Chrono-Lord Epoch"""

    # 战吼：将所有随从移回各自拥有者的手牌
    play = Bounce(ALL_MINIONS)


# TIME_850: Lo'Gosh, Blood Fighter (7费 7/7)
# 传说，突袭。亡语：从你的手牌中召唤一个血战士。它获得+5/+5并随机攻击一个敌人
class TIME_850:
    """Lo'Gosh, Blood Fighter"""

    # 突袭
    tags = {
        GameTag.RUSH: True,
    }

    # 亡语：从手牌召唤一个随从并使其获得+5/+5
    deathrattle = Summon(CONTROLLER, RANDOM(FRIENDLY_HAND + MINION)).then(
        Buff(Summon.CARD, "TIME_850e")
    )


TIME_850e = buff(+5, +5)


# TIME_870: Gladiatorial Combat (5费 法术)
# 召唤一个竞技场老虎
class TIME_870:
    """Gladiatorial Combat"""

    # 召唤一个竞技场老虎
    play = Summon(CONTROLLER, "TIME_870t")


# TIME_870t: Coliseum Tiger (5费 5/5)
class TIME_870t:
    """Coliseum Tiger"""

    pass


# TIME_871: Heir of Hereafter (5费 2/6)
# 战吼：使一个随机友方随从获得+3攻击力
class TIME_871:
    """Heir of Hereafter"""

    # 战吼：使一个随机友方随从获得+3攻击力
    play = Buff(RANDOM(FRIENDLY_MINIONS), "TIME_871e")


TIME_871e = buff(+3, 0)


# TIME_872: Undefeated Champion (8费 13/13)
# 突袭。战吼：用随机的1费随从占满对手的战场
class TIME_872:
    """Undefeated Champion"""

    # 突袭
    tags = {
        GameTag.RUSH: True,
    }

    # 战吼：用随机的1费随从占满对手的战场
    play = Summon(Opponent(), RandomMinion(cost=1)) * 7


# TIME_715: For Glory! (5费 法术)
# 你的所有随从获得+3/+3
class TIME_715:
    """For Glory!"""

    # 你的所有随从获得+3/+3
    play = Buff(FRIENDLY_MINIONS, "TIME_715e")


TIME_715e = buff(+3, +3)


# TIME_716: Slow Motion (2费 法术)
# 使一个随从变为1/1
class TIME_716:
    """Slow Motion"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 使目标随从变为1/1
    play = Buff(TARGET, "TIME_716e")


TIME_716e = buff(0, 0)


# TIME_750: Precursory Strike (2费 法术)
# 对一个随从造成3点伤害，如果你的手牌中有武器，召唤一个复制
class TIME_750:
    """Precursory Strike"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 对目标造成3点伤害
    # 简化实现：总是造成3点伤害
    play = Hit(TARGET, 3)


# TIME_873: Unleash the Crocolisks (2费 法术)
# 召唤两个鳄鱼
class TIME_873:
    """Unleash the Crocolisks"""

    # 召唤两个鳄鱼
    play = Summon(CONTROLLER, "TIME_873t") * 2


# TIME_873t: Coliseum Crocolisk (2费 2/3)
class TIME_873t:
    """Coliseum Crocolisk"""

    pass
