from ..utils import *


##
# Minions

# CATA_216: "净化祭司" (4费 4/5)
# 战吼：在本局对战中，你的治疗效果恢复的生命值增加2点
class CATA_216:
    """Sanctified Priest"""

    # 战吼：在本局对战中，你的治疗效果恢复的生命值增加2点
    # 简化实现：给玩家一个 buff 作为标记
    # 实际的治疗增强在 card.py 的 get_heal 中处理
    play = Buff(CONTROLLER, "CATA_216e")


# CATA_216e: 治疗增强 buff - 作为一个标记
# 注意：这是一个标记 buff，实际的治疗增强需要在 card.py 中处理
CATA_216e = buff(health=0)  # 空 buff 作为标记


# CATA_300: "黑血" (7费 4/8 巨型+3)
# 在你为一个角色恢复生命值后，随机攻击一个敌方随从
class CATA_300:
    """Black Blood"""

    # 巨型+3：召唤3条腿
    play = Summon(CONTROLLER, "CATA_300t1"), Summon(CONTROLLER, "CATA_300t2"), Summon(CONTROLLER, "CATA_300t3")

    # 在你为一个角色恢复生命值后，随机攻击一个敌方随从
    events = Heal().after(Hit(RANDOM_ENEMY_MINION, ATK(SELF)))


# CATA_300t1, CATA_300t2, CATA_300t3: 黑血之腿 (1费 0/2)
class CATA_300t1:
    """Black Blood Limb"""


CATA_300t2 = CATA_300t1
CATA_300t3 = CATA_300t1


# CATA_301: "红玉圣殿" (1费 法术)
# 在本回合中，你的下一次治疗效果转而造成等量的伤害
class CATA_301:
    """Ruby Sanctum"""

    # 在本回合中，你的下一次治疗效果转而造成等量的伤害
    # 简化实现：使用自定义动作来处理
    def play(self):
        # 设置 healing_as_damage 标志
        self.controller.healing_as_damage = True


# CATA_302: "愈合" (1费 法术)
# 为一个随从恢复所有生命值。抽一张牌。
class CATA_302:
    """Mending"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}

    # 为一个随从恢复所有生命值。抽一张牌。
    play = FullHeal(TARGET), Draw(CONTROLLER)


# CATA_303: "净化吐息" (2费 法术)
# 对一个随从造成$5点伤害。如果该随从死亡，则为敌方英雄恢复#5点生命值。
class CATA_303:
    """Purifying Breath"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}

    # 对一个随从造成5点伤害。如果该随从死亡，则为敌方英雄恢复5点生命值
    def play(self):
        target = self.target
        yield Hit(target, 5)
        # 检查目标是否死亡
        yield Dead(target).after(Heal(ENEMY_HERO, 5))


# CATA_304: "受伤的侍者" (3费 3/8 野兽)
# 吸血。战吼：对本随从造成4点伤害。
class CATA_304:
    """Injured Khadgar"""

    # 战吼：对本随从造成4点伤害
    play = Hit(SELF, 4)

    # 吸血
    tags = {GameTag.LIFESTEAL: True}


# CATA_305: "盛怒主母" (4费 3/3 恶魔)
# 在你的回合结束时，如果本随从具有所有生命值，获得+3生命值。
class CATA_305:
    """Mother of Fury"""

    # 在回合结束时，如果本随从具有所有生命值，获得+3生命值
    events = OWN_TURN_END.on(
        (CURRENT_HEALTH(SELF) == MAX_HEALTH(SELF)) & Buff(SELF, "CATA_305e")
    )


CATA_305e = buff(+0, +3)


# CATA_306: "教派分歧" (4费 法术 裂变)
# 使一个友方随从获得+2/+3和扰魔。召唤一个它的复制。
class CATA_306:
    """Schism"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}

    # 使一个友方随从获得+2/+3和扰魔。召唤一个它的复制
    def play(self):
        target = self.target
        # 给目标+2/+3和扰魔
        yield Buff(target, "CATA_306e")
        # 召唤一个复制
        yield Summon(CONTROLLER, ExactCopy(target))


# CATA_306e: +2/+3 和 扰魔
CATA_306e = buff(+2, +3, elusive=True)


# CATA_307: "阿莱克丝塔萨，生命守护者" (7费 8/8 龙)
# 战吼：将你的英雄剩余生命值变为15。当你恢复所有生命值时，对敌方英雄造成15点伤害。
class CATA_307:
    """Alexstrasza, Guardian of Life"""

    # 战吼：将你的英雄剩余生命值变为15
    play = SetCurrentHealth(FRIENDLY_HERO, 15)

    # 当你恢复所有生命值时，对敌方英雄造成15点伤害
    # 简化实现：监听 Heal 事件，检查是否完全恢复
    events = Heal(FRIENDLY_HERO).after(
        (CURRENT_HEALTH(FRIENDLY_HERO) == MAX_HEALTH(FRIENDLY_HERO)) & Hit(ENEMY_HERO, 15)
    )


# CATA_308: "麦迪文的胜利" (5费 法术)
# 对所有随从造成$4点伤害。如果你控制着传说牌，本牌的法力值消耗为（1）点。
class CATA_308:
    """Medivh's Triumph"""

    # 对所有随从造成4点伤害
    play = Hit(ALL_MINIONS, 4)

    # 简化实现：手动设置费用
    # 实际实现需要在费用计算时检查是否有传说随从
    pass
