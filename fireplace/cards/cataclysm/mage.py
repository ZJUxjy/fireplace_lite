from ..utils import *


##
# Minions

# CATA_458: 大法师卡雷 (4费 4/4)
# 战吼：使你手牌和牌库中所有法术牌获得法术伤害+1
class CATA_458:
    """Archmage Kalec"""

    # 战吼：使你手牌和牌库中所有法术牌获得法术伤害+1
    # 简化实现：使你的英雄获得法术伤害+1
    play = Refresh(CONTROLLER, {GameTag.SPELLPOWER: 1})


# CATA_483: 不稳定的施法者 (4费 2/5)
# 法术伤害+1。战吼：如果你在本回合中用法术造成过伤害，召唤一个本随从的复制
class CATA_483:
    """Unstable Spellcaster"""

    # 法术伤害+1
    update = Refresh(CONTROLLER, {GameTag.SPELLPOWER: 1})

    # 战吼：如果你在本回合中用法术造成过伤害，召唤一个复制
    # 简化实现：总是触发战吼效果
    play = Summon(CONTROLLER, "CATA_483")


# CATA_484: 冬泉雏龙 (1费 1/2)
# 战吼：发现一张任意职业的法力值消耗为（1）的法术牌
class CATA_484:
    """Winterspring Whelp"""

    # 战吼：发现一张任意职业的费用为(1)的法术牌
    play = Discover(CONTROLLER, RandomSpell(cost=1))


# CATA_487: 祈雨元素 (2费 1/4)
# 每回合中，你第一次用法术造成伤害时，获得+2攻击力
class CATA_487:
    """Raincaller"""

    # 每回合第一次用法术造成伤害时，获得+2攻击力
    # 简化实现：在施放法术后获得+2攻击力
    events = Play(CONTROLLER, SPELL).after(Buff(SELF, "CATA_487e"))


CATA_487e = buff(+2, 0)


# CATA_488: 沃坎诺斯 (7费 4/8)
# 巨型+2，在你的回合结束时，对所有其他随从造成2点伤害
class CATA_488:
    """Vulcanos"""

    # 巨型+2：召唤2个手臂
    play = Summon(CONTROLLER, "CATA_488t") * 2

    # 在你的回合结束时，对所有其他随从造成2点伤害
    events = OWN_TURN_END.on(Hit(ALL_MINIONS - SELF, 2))


# CATA_488t: 沃坎诺斯的喷发柱 (2费 1/4)
# 每当本随从受到伤害，随机获取一张火焰法术牌，其法力值消耗减少（3）点
class CATA_488t:
    """Plume of Vulcanos"""

    # 每当本随从受到伤害，获取一张随机法术牌，费用减少3
    # 简化实现：获取随机法术
    events = SELF_DAMAGE.on(Give(CONTROLLER, RandomSpell()).then(
        Buff(Give.CARD, "CATA_488te")
    ))


CATA_488te = buff(cost=-3)


# CATA_979: 咒术专家 (3费 3/4)
# 战吼：选择你手牌中的一张法术牌，将其拆分为两张法力值消耗与其相同的随机法术牌
class CATA_979:
    """Conjuration Specialist"""

    # 简化实现：直接给两张随机法术牌
    # 完整实现需要选择目标和复制
    play = Give(CONTROLLER, RandomSpell()) * 2


##
# Spells


# CATA_452: 织法者的光辉 (10费 法术)
# 召唤一条6/6的龙。在本回合中，你每用法术造成一点伤害，本牌的法力值消耗便减少（1）点
class CATA_452:
    """Spellweaver's Brilliance"""

    # 召唤一条6/6的龙
    # 简化实现：直接召唤6/6龙，忽略费用减免
    play = Summon(CONTROLLER, "CATA_452t")


# CATA_452t: 碧蓝守卫 (6费 6/6 龙)
class CATA_452t:
    """Azure Warden"""

    # 简单的6/6龙
    pass


# CATA_485: 激寒急流 (1费 法术)
# 造成$2点伤害。随机对一个敌方随从造成$1点伤害
class CATA_485:
    """Sleet Storm"""

    # 造成2点伤害，随机对一个敌方随从造成1点伤害
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    def play(self):
        yield Hit(TARGET, 2)
        yield Hit(RANDOM(ENEMY_MINION), 1)


# CATA_489: 奥术涌流 (4费 法术)
# 裂变，造成$4点伤害。对所有敌人造成$2点伤害
class CATA_489:
    """Arcane Flow"""

    # 裂变：造成4点伤害，对所有敌人造成2点伤害
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    def play(self):
        yield Hit(TARGET, 4)
        yield Hit(ENEMY_CHARACTERS, 2)


# CATA_978: 辛达苟萨的胜利 (5费 法术)
# 对一个随从造成$8点伤害。使你手牌中一张随机牌的法力值消耗减少，减少的量等于超过目标生命值的伤害
class CATA_978:
    """Sindragosa's Triumph"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 对目标造成8点伤害，超出部分减少手牌费用
    def play(self):
        target = self.target
        damage = 8
        actual_damage = min(damage, target.health)
        overflow = damage - actual_damage
        yield Hit(target, damage)
        if overflow > 0:
            yield Buff(RANDOM(FRIENDLY_HAND), "CATA_978e")


CATA_978e = buff(cost=-3)  # 简化实现：固定减少3点费用
