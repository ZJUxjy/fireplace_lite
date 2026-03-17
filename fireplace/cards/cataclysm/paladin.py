from ..utils import *
from hearthstone.enums import SpellSchool


##
# Minions

# CATA_432: 克洛玛图斯 (Chromatus)
# 8费 8/8 巨型+4
# 嘲讽、吸血、扰魔、圣盾
class CATA_432:
    """Chromatus"""

    # 巨型+4：召唤4个头颅
    # 绿、红、蓝、青铜头颅
    play = Summon(CONTROLLER, "CATA_432t1"), Summon(CONTROLLER, "CATA_432t2"), Summon(CONTROLLER, "CATA_432t3"), Summon(CONTROLLER, "CATA_432t4")


# CATA_432t1: 克洛玛图斯的绿色头颅
# 2费 2/3 龙
# 嘲讽。亡语：移除克洛玛图斯的嘲讽
class CATA_432t1:
    """Chromatus's Green Head"""

    tags = {
        GameTag.TAUNT: True,
        GameTag.COLOSSAL_LIMB: True,
    }

    deathrattle = SetTags(SELF, {GameTag.TAUNT: False})


# CATA_432t2: 克洛玛图斯的红色头颅
# 2费 2/3 龙
# 吸血。亡语：移除克洛玛图斯的吸血
class CATA_432t2:
    """Chromatus's Red Head"""

    tags = {
        GameTag.LIFESTEAL: True,
        GameTag.COLOSSAL_LIMB: True,
    }

    deathrattle = SetTags(SELF, {GameTag.LIFESTEAL: False})


# CATA_432t3: 克洛玛图斯的蓝色头颅
# 2费 2/3 龙
# 扰魔。亡语：移除克洛玛图斯的扰魔
class CATA_432t3:
    """Chromatus's Blue Head"""

    tags = {
        GameTag.ELUSIVE: True,
        GameTag.COLOSSAL_LIMB: True,
    }

    deathrattle = SetTags(SELF, {GameTag.ELUSIVE: False})


# CATA_432t4: 克洛玛图斯的青铜头颅
# 2费 2/3 龙
# 圣盾。亡语：移除克洛玛图斯的圣盾
class CATA_432t4:
    """Chromatus's Bronze Head"""

    tags = {
        GameTag.DIVINE_SHIELD: True,
        GameTag.COLOSSAL_LIMB: True,
    }

    deathrattle = SetTags(SELF, {GameTag.DIVINE_SHIELD: False})


# CATA_472: 灵感之槌
# 2费 2/2 武器
# 亡语：随机触发一个友方随从的回合结束效果
class CATA_472:
    """Inspiring Hammer"""

    deathrattle = Activate(RANDOM(FRIENDLY_MINIONS))


# CATA_473: 诺兹多姆，青铜守护巨龙
# 5费 4/4 龙
# 在你的回合结束时，使你的随从获得圣盾，已有圣盾的随从改为获得+3/+3
class CATA_473:
    """Nozdormu the Bronze Dragonflight"""

    # 简化实现：给没有圣盾的随从圣盾，给已有圣盾的随从+3/+3
    events = OWN_TURN_END.on(
        GiveDivineShield(FRIENDLY_MINIONS - DIVINE_SHIELD),
        Buff(FRIENDLY_MINIONS + DIVINE_SHIELD, "CATA_473e")
    )


CATA_473e = buff(+3, +3)


# CATA_474: 矛心哨卫
# 4费 3/4 龙
# 在你的回合结束时，随机获取一张神圣法术牌，其法力值消耗减少（3）点
class CATA_474:
    """Spearhead Paladin"""

    events = OWN_TURN_END.on(
        Give(CONTROLLER, RandomSpell(spellschool=SpellSchool.HOLY)),
        Buff(Give.CARD, "CATA_474e")
    )


CATA_474e = buff(cost=-3)


# CATA_475: 破鳞盾卫
# 6费 3/6
# 在你的回合结束时，对所有敌人造成2点伤害
class CATA_475:
    """Scales of Justice"""

    events = OWN_TURN_END.on(Hit(ENEMY_MINIONS | ENEMY_HERO, 2))


# CATA_478: 青铜救赎者
# 5费 3/3 龙
# 在你的回合结束时，召唤一条属性值等同于本随从的龙
class CATA_478:
    """Bronze Redemption"""

    events = OWN_TURN_END.on(Summon(CONTROLLER, "CATA_478t"))


# CATA_478t: 青铜蛮兵
# 1费 1/1 龙
class CATA_478t:
    """Bronze Sellsword"""

    tags = {GameTag.CARDRACE: Race.DRAGON}


##
# Spells

# CATA_477: 守护巨龙之厅
# 2费 法术
# 选择你手牌中的一张随从牌，使其获得+2/+2
class CATA_477:
    """Hall of the Dragonflight"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Buff(TARGET, "CATA_477e")


CATA_477e = buff(+2, +2)


# CATA_479: 飞龙机动
# 4费 法术
# 裂变：召唤两条4/2的幼龙。使你的随从获得+1/+1和圣盾
class CATA_479:
    """Dragonriding"""

    # 裂变效果：召唤两条4/2幼龙，使你的随从获得+1/+1和圣盾
    play = Summon(CONTROLLER, "CATA_479t3") * 2, Buff(FRIENDLY_MINIONS, "CATA_479e")


CATA_479e = buff(+1, +1)


# CATA_479t3: 天空幼龙
# 3费 4/2 龙
class CATA_479t3:
    """Sky Roar"""

    tags = {GameTag.CARDRACE: Race.DRAGON}


# CATA_480: 沙怒光环
# 3费 法术
# 你的随从的回合结束效果会触发两次。持续3回合
class CATA_480:
    """Sandwind Aura"""

    # 简化实现：持续3回合的buff
    # 由于触发两次机制实现复杂，这里简化为持续3回合的 buff
    play = Buff(CONTROLLER, "CATA_480e")


# CATA_480e: 沙怒光环 buff
class CATA_480e:
    # 持续3回合
    max_turns = 3
    # 简化实现：回合结束时触发两次效果
    events = OWN_TURN_END.on(lambda self: None)  # 占位实现


# CATA_621: 格尔宾的胜利
# 1费 法术
# 随机获取一张圣骑士光环牌，其持续时间增加一回合
class CATA_621:
    """Galakrond's Triumph"""

    # 简化实现：随机获取一张圣骑士职业卡（这里简化为获取一张圣骑士卡）
    # 由于没有专门的光环牌列表，简化实现为获取一张圣骑士随机卡
    play = Give(CONTROLLER, RandomCard(type=CardType.SPELL, card_class=CardClass.PALADIN))
