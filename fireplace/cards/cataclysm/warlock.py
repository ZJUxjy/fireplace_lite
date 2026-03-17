from ..utils import *


##
# Minions

# CATA_490: 魔眼秘术师 (3费 3/6 嘲讽)
# 战吼：选择你手牌中的一张牌并弃掉
class CATA_490:
    """Ocular Occultist"""

    # 嘲讽属性
    tags = {GameTag.TAUNT: True}

    # 战吼：选择一张手牌并弃掉
    play = Discard(TARGET)

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }


# CATA_491: 怪异触手 (5费 5/4)
# 对所有随从造成$3点伤害。重复
class CATA_491:
    """Tentacle"""

    # 对所有随从造成3点伤害
    # 简化实现：一次性造成3点伤害
    play = Hit(ALL_MINIONS, 3)


# CATA_492: 暮光神坛 (3费 2/5)
# 兆示{0}。抽一张牌
class CATA_492:
    """Twilight Altar"""

    # 兆示：触发一次效果
    # 简化实现：直接抽一张牌
    # TODO: 实现完整的兆示机制
    play = Draw(CONTROLLER)


# CATA_493: 地狱公爵 (4费 4/4 突袭)
# 在本局对战中，你每弃掉一张牌，便拥有+2/+2
class CATA_493:
    """Fiendish Servant"""

    tags = {GameTag.RUSH: True}

    # 在本局对战中，你每弃掉一张牌，便拥有+2/+2
    # 简化实现：弃掉卡牌时触发
    events = Discard(FRIENDLY_HAND).on(Buff(SELF, "CATA_493e"))


CATA_493e = buff(+2, +2)


# CATA_494: 马洛拉克 (5费 4/6)
# 在你弃掉一张随从牌后，召唤一个该随从的复制
class CATA_494:
    """Malorne"""

    # 在你弃掉一张随从牌后，召唤一个该随从的复制
    events = Discard(FRIENDLY_HAND + MINION).after(Summon(CONTROLLER, Copy(Discard.TARGET)))


# CATA_496: 诅咒之链 (5费 4/4)
# 直到敌方回合结束，夺取一个敌方随从的控制权。在本回合中，该随从无法攻击
class CATA_496:
    """Cursed Chain"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 夺取控制权，并使其无法攻击
    play = Steal(TARGET), SetTags(TARGET, {GameTag.CANT_ATTACK: True})

    # 敌方回合结束时移除无法攻击的标记
    events = OWN_TURN_END.on(UnsetTags(TARGET, {GameTag.CANT_ATTACK: True}))


# CATA_498: 拉法姆的奋战 (1费 2/2)
# 随机对两个敌方随从造成$@点伤害。（每回合都会升级！）
class CATA_498:
    """Rafaam's Strider"""

    # 简化实现：每回合开始时升级伤害
    # 初始造成2点伤害，每回合+1
    events = OWN_TURN_BEGIN.on(Hit(RANDOM(ENEMY_MINIONS) * 2, 1))


# CATA_499: 助祭耗材 (3费 2/3)
# 当你使用或弃掉本牌时，随机召唤两个法力值消耗为（1）的随从
class CATA_499:
    """Sacrificial Summoner"""

    # 当使用或弃掉时，召唤两个1费随从
    events = Play(CONTROLLER, SELF).after(Summon(CONTROLLER, RandomMinion(cost=1)) * 2)


# CATA_725: 暗誓信徒 (2费 2/1)
# 战吼：兆示{0}。亡语：为你的英雄恢复#3点生命值
class CATA_725:
    """Dark Inquisitor"""

    # 兆示：触发一次效果
    # 简化实现：直接触发
    # TODO: 实现完整的兆示机制

    # 亡语：恢复3点生命值
    deathrattle = Heal(FRIENDLY_HERO, 3)


# CATA_726: 古加尔，暮光主谋 (9费 6/6)
# 巨型+2
# 你的手臂和士兵改为消灭敌方牌库中的随从
class CATA_726:
    """Gul'dan, Aspect of the Void"""

    tags = {GameTag.ELITE: True}

    # 巨型+2：召唤手臂和士兵
    play = Summon(CONTROLLER, "CATA_726t"), Summon(CONTROLLER, "CATA_726t1")


# CATA_726t: 古加尔的手臂 (1费 1/1)
# 在你的回合结束时，消灭本随从右边的随从以获得+2/+2
class CATA_726t:
    """Gul'dan's Arm"""

    tags = {
        GameTag.COLOSSAL_LIMB: True,
    }

    events = OWN_TURN_END.on(
        Destroy(RIGHT_OF(SELF)),
        Buff(SELF, "CATA_726te")
    )


CATA_726te = buff(+2, +2)


# CATA_726t1: 加尔的手臂 (1费 1/1)
class CATA_726t1:
    """Gahz'rilla's Arm"""

    tags = {
        GameTag.COLOSSAL_LIMB: True,
    }

    events = OWN_TURN_END.on(
        Destroy(RIGHT_OF(SELF)),
        Buff(SELF, "CATA_726te")
    )


# CATA_725t: 古加尔的士兵 (1费 1/1)
# 在你的回合结束时，消灭本随从右边的随从以获得+2/+2
class CATA_725t:
    """Gul'dan's Soldier"""

    events = OWN_TURN_END.on(
        Destroy(RIGHT_OF(SELF)),
        Buff(SELF, "CATA_725te")
    )


CATA_725e = buff(+2, +2)
CATA_725te = buff(+2, +2)


# CATA_780: 着魔的技师 (3费 3/4)
# 吸血。战吼：兆示{0}
class CATA_780:
    """Enslaved Felhound"""

    tags = {GameTag.LIFESTEAL: True}

    # 兆示：触发一次效果
    # 简化实现：直接触发
    # TODO: 实现完整的兆示机制


##
# Spells


# CATA_791: 残影 (2费 法术)
# 造成4点伤害。重复
class CATA_791:
    """Shadowflame"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 对一个随从造成4点伤害
    # 简化实现：一次性造成4点伤害
    play = Hit(TARGET, 4)


# CATA_792: 暗影之怒 (6费 法术)
# 造成8点伤害。分裂：召唤两个3/3
class CATA_792:
    """Shadow Shock"""

    # 造成8点伤害
    # 简化实现：直接造成8点伤害
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    play = Hit(TARGET, 8)
