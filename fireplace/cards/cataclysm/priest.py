from ..utils import *


##
# Minions

# CATA_216: "净化祭司" (4费 4/5)
# 战吼：在本局对战中，你的治疗效果恢复的生命值增加2点
class CATA_216:
    """Cleansing Cleric"""

    # 战吼：在本局对战中，你的治疗效果恢复的生命值增加2点
    # 玩家级增益由 Heal action 在治疗结算时读取。
    play = Buff(CONTROLLER, "CATA_216e")


# CATA_216e: 治疗增强 buff - 作为一个标记
class CATA_216e:
    healing_bonus = 2


# CATA_300: "黑血" (7费 4/8 巨型+3)
# 在你为一个角色恢复生命值后，随机攻击一个敌方随从
class CATA_300:
    """Black Blood"""

    colossal_limb_count = 3

    # 巨型+3：召唤3条腿
    play = Summon(CONTROLLER, "CATA_300t1"), Summon(CONTROLLER, "CATA_300t2"), Summon(CONTROLLER, "CATA_300t3")

    # 在你为一个角色恢复生命值后，随机攻击一个敌方随从
    events = Heal(source=FRIENDLY).on(Attack(SELF, RANDOM_ENEMY_MINION))


# CATA_300t1, CATA_300t2, CATA_300t3: 黑血之腿 (1费 0/2)
class CATA_300t1:
    """Black Blood Limb"""

    events = OWN_TURN_END.on(Heal(RANDOM(FRIENDLY + DAMAGED_CHARACTERS), 3))


CATA_300t2 = CATA_300t1
CATA_300t3 = CATA_300t1


# CATA_301: "红玉圣殿" (1费 法术)
# 在本回合中，你的下一次治疗效果转而造成等量的伤害
class CATA_301:
    """Ruby Sanctum"""

    # 在本回合中，你的下一次治疗效果转而造成等量的伤害
    activate = Buff(CONTROLLER, "CATA_301e")


class CATA_301e:
    healing_as_damage = True
    events = OWN_TURN_END.on(Destroy(SELF))


# CATA_302: "愈合" (1费 法术)
# 为一个随从恢复所有生命值。抽一张牌。
class CATA_302:
    """Mending"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}

    # 为一个随从恢复所有生命值。抽一张牌。
    play = FullHeal(TARGET), Draw(CONTROLLER)


# CATA_303: "净化吐息" (2费 法术)
# 对一个随从造成$5点伤害。如果该随从死亡，则为敌方英雄恢复#5点生命值。
class CATA_303_PurifyingBreath(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        source.game.queue_actions(source, [Hit(target, 5)])
        if target.dead:
            return source.game.queue_actions(
                source, [Heal(source.controller.opponent.hero, 5)]
            )


class CATA_303:
    """Purifying Breath"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}

    # 对一个随从造成5点伤害。如果该随从死亡，则为敌方英雄恢复5点生命值
    play = CATA_303_PurifyingBreath(TARGET)


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

    def play(self):
        target = self.target
        yield Buff(target, "CATA_306e")
        yield Summon(CONTROLLER, ExactCopy(target))


class CATA_306t1:
    """Schism"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = Buff(TARGET, "CATA_306e")


class CATA_306t2:
    """Schism"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = Summon(CONTROLLER, ExactCopy(TARGET))


# CATA_306e: +2/+3 和 扰魔
CATA_306e = buff(+2, +3, elusive=True)


# CATA_307: "阿莱克丝塔萨，生命守护者" (7费 8/8 龙)
# 战吼：将你的英雄剩余生命值变为15。当你恢复所有生命值时，对敌方英雄造成15点伤害。
class CATA_307_DamageAfterFullHeal(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if target is source.controller.hero and target.health == target.max_health:
            source.game.queue_actions(source, [Hit(source.controller.opponent.hero, 15)])


class CATA_307:
    """Alexstrasza, Guardian of Life"""

    # 战吼：将你的英雄剩余生命值变为15
    play = SetCurrentHealth(FRIENDLY_HERO, 15)

    # 当你恢复所有生命值时，对敌方英雄造成15点伤害
    events = Heal().on(CATA_307_DamageAfterFullHeal(Heal.TARGET))


# CATA_308: "麦迪文的胜利" (5费 法术)
# 对所有随从造成$4点伤害。如果你控制着传说牌，本牌的法力值消耗为（1）点。
class CATA_308:
    """Medivh's Triumph"""

    # 对所有随从造成4点伤害
    play = Hit(ALL_MINIONS, 4)

    # 如果你控制着传说随从，费用降至1（即-4）
    class Hand:
        update = Find(FRIENDLY_MINIONS + LEGENDARY) & Refresh(SELF, {GameTag.COST: -4})
