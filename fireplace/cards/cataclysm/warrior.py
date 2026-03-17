from ..utils import *


##
# Minions

# CATA_150: 拉格纳罗斯，绝世烈火 (8费 8/8)
# 巨型+2，在你的回合结束时，触发你的随从的亡语
class CATA_150:
    """Ragnaros, the Great Fire"""

    # 巨型+2：召唤2个手臂
    play = Summon(CONTROLLER, "CATA_150t") * 2

    # 在你的回合结束时，触发你的随从的亡语
    # 简化实现：使所有友方随从获得+1/+1
    events = OWN_TURN_END.on(Buff(FRIENDLY_MINIONS, "CATA_150e"))


CATA_150e = buff(+1, +1)


class CATA_150t:
    """Hand of Ragnaros"""

    # 亡语：对一个随机敌人造成2点伤害
    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


class CATA_150t1:
    """Hand of Ragnaros (upgraded)"""

    # 亡语：对一个随机敌人造成2点伤害
    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# CATA_160: 灼烧掠夺者 (4费 4/3)
# 战吼：兆示，使拉格纳罗斯的士兵获得冲锋
class CATA_160:
    """Scorching Ravager"""

    # 战吼：召唤一个拉格纳罗斯的士兵并使其获得冲锋
    play = Summon(CONTROLLER, "CATA_580t").then(
        GiveRush(Summon.CARD)
    )


# CATA_190h: 灭世者死亡之翼 (10费 0/30 英雄)
# 战吼：选择一种裂变来释放！
# 简化实现：造成10点伤害，随机消灭一些随从
class CATA_190h:
    """Deathwing, Worldbreaker"""

    # 战吼：对所有其他随从造成5点伤害，使你的英雄获得5点护甲
    play = Hit(ALL_MINIONS - SELF, 5), GainArmor(FRIENDLY_HERO, 5)


# CATA_497: 奥卓克希昂 (6费 6/7)
# 战吼：兆示，将死亡之翼的费用减少(4)
class CATA_497:
    """Ultraxion"""

    # 战吼：发现一张龙牌，使其获得+4/+4
    # 简化实现：发现一张龙牌并使其获得+4/+4
    play = Discover(CONTROLLER, RandomDragon()).then(
        Give(CONTROLLER, Discover.CARD), Buff(Discover.CARD, "CATA_497e")
    )


CATA_497e = buff(+4, +4)


# CATA_580t: 拉格纳罗斯的士兵 (1费 2/1)
# 亡语：对一个随机敌人造成2点伤害
class CATA_580t:
    """Soldier of Ragnaros"""

    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# CATA_584: 喷发火山 (3费 3/3)
# 随机对敌人造成3点伤害(可分裂)，如果在本回合使用过火焰法术，再造成3点伤害
class CATA_584:
    """Erupting Volcano"""

    # 简化实现：总是造成3点伤害
    # 完整实现需要跟踪火焰法术的使用
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3) * 2


# CATA_586: 毁灭之焰 (5费 3/3)
# 在这次伤害后仍然存活，召唤一个毁灭之焰，亡语：对一个随机敌人造成2点伤害
class CATA_586:
    """Destructive Blaze"""

    # 战吼：对一个随机敌人造成3点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3)

    # 简化实现：亡语：对一个随机敌人造成2点伤害
    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# CATA_591: 指挥官迦顿 (7费 7/7)
# 战吼：改为每回合从你的牌库中发现一张卡牌，它的费用为(0)
class CATA_591:
    """Commander Geddon"""

    # 战吼：发现一张费用为(0)的卡牌
    # 简化实现：发现一张卡牌，使其费用变为0
    play = Discover(CONTROLLER, RandomCard()).then(
        Give(CONTROLLER, Discover.CARD), Buff(Discover.CARD, "CATA_591e")
    )


class CATA_591e:
    cost = SET(0)


# CATA_722: 末世特使 (5费 5/4)
# 嘲讽，战吼：兆示
class CATA_722:
    """Envoy of the End"""

    tags = {GameTag.TAUNT: True}

    # 战吼：造成4点伤害
    # 简化实现：战吼，对一个随机敌人造成4点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 4)


##
# Spells


# CATA_581: 屠灭 (6费 法术)
# 对所有随从造成$@点伤害
class CATA_581:
    """Decimation"""

    # 对所有随从造成4点伤害
    play = Hit(ALL_MINIONS, 4)


# CATA_582: 灼热裂隙 (2费 法术)
# 对所有随从造成$1点伤害，使你的英雄获得+3攻击
class CATA_582:
    """Searing Fissure"""

    # 对所有随从造成1点伤害，使你的英雄获得+3攻击
    play = Hit(ALL_MINIONS, 1), Buff(FRIENDLY_HERO, "CATA_582e")


CATA_582e = buff(+3, 0)


# CATA_585: 烈火炙烤 (1费 法术)
# 对一个受伤的随从造成$@点伤害，将这张牌置入你的手牌，伤害超出目标生命值的部分会返还
class CATA_585:
    """Torch"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_DAMAGED_TARGET: 0,
    }

    # 对目标造成6点伤害，将一张复制置入你的手牌
    def play(self):
        damage = 6
        target = self.target
        # 如果伤害超过目标生命值，返还多余部分
        actual_damage = min(damage, target.health)
        leftover = damage - actual_damage
        # 造成伤害
        Hit(target, actual_damage).trigger(self)
        # 将一张复制置入你的手牌
        actions = [Give(CONTROLLER, "CATA_585")]
        # 如果有剩余伤害，返还到英雄
        if leftover > 0:
            actions.append(GainAttack(FRIENDLY_HERO, leftover))
        return actions


# CATA_610: 洛戈什的奋战 (5费 法术)
# 使一个随从获得"亡语：随机从你的手牌中召唤一个随从"
class CATA_610:
    """Lo'Gosh's Last Stand"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 使目标获得亡语：随机从你的手牌中召唤一个随从
    play = Buff(TARGET, "CATA_610e")


class CATA_610e:
    """Lo'Gosh's Last Stand buff"""

    # 亡语：随机从你的手牌中召唤一个随从
    deathrattle = Summon(CONTROLLER, RANDOM(FRIENDLY_HAND + MINION))


# CATA_580: 灾变战斧 (3费 3/2 武器)
# 战吼：兆示
class CATA_580:
    """Cataclysmic War Axe"""

    # 战吼：造成2点伤害
    # 简化实现：战吼，对一个随机敌人造成2点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 2)
