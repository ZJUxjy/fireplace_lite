from ..utils import *
from hearthstone.enums import SpellSchool


##
# Minions

# CATA_151: 艾萨拉，海洋之主 (8费 8/8)
# 巨型+2：召唤2个触手。你的英雄拥有风怒
class CATA_151:
    """Azshara, Lady of the Sea"""

    # 巨型+2：召唤2个触手
    play = Summon(CONTROLLER, "CATA_151t") * 2

    # 你的英雄拥有风怒
    # 简化实现：给英雄风怒buff
    events = [
        OWN_TURN_BEGIN.on(Buff(FRIENDLY_HERO, "CATA_151e"))
    ]


# CATA_151e: 艾萨拉的风怒
class CATA_151e:
    tags = {GameTag.WINDFURY: True}


# CATA_151t: 艾萨拉的触手 (1费 2/1)
# 被召唤时，使你的英雄在当回合获得+1攻击力
class CATA_151t:
    """Azshara's Tentacle"""

    tags = {GameTag.COLOSSAL_LIMB: True}

    # 被召唤时，使你的英雄获得+1攻击力
    play = Buff(FRIENDLY_HERO, "CATA_151te")


class CATA_151te:
    tags = {GameTag.WINDFURY: True}
    atk = 1


# CATA_525: 装甲放血纳迦 (3费 3/1)
# 突袭。战吼：兆示
class CATA_525:
    """Armored Bloodsail Naga"""

    tags = {GameTag.RUSH: True}

    # 兆示效果（简化实现：直接触发效果）
    # 兆示2次，所以效果触发两次
    # 简化实现：直接造成2点伤害
    play = Hit(RANDOM(ENEMY_MINIONS), 2)


# CATA_525t: 艾萨拉的士兵 (1费 2/1)
# 被召唤时，使你的英雄在当回合获得+1攻击力
class CATA_525t:
    """Azshara's Mariner"""

    play = Buff(FRIENDLY_HERO, "CATA_525te")


class CATA_525te:
    atk = 1


# CATA_527: 奈瑟匹拉，蒙难古灵 (3费 5/5)
# 造成1点伤害。在你施放一个邪能法术后，重新开启。亡语：召唤奈瑟匹拉，脱困古灵
class CATA_527:
    """Naga, the Dissenter"""

    # 造成1点伤害
    def play(self):
        return Hit(RANDOM(ENEMY_MINIONS | ENEMY_HERO), 1)

    # 在你施放一个邪能法术后，重新开启
    # 简化实现：邪能法术后再次造成1点伤害
    # 由于 SPELL_FEL 选择器不可用，简化为任何法术都触发
    events = Play(CONTROLLER, SPELL).after(
        Hit(RANDOM(ENEMY_MINIONS | ENEMY_HERO), 1)
    )

    # 亡语：召唤奈瑟匹拉，脱困古灵
    deathrattle = Summon(CONTROLLER, "CATA_527t2")


# CATA_527t2: 奈瑟匹拉，脱困古灵 (6费 6/6)
# 在你施放一个邪能法术后，随机获取一张纳迦牌，其法力值为(1)
class CATA_527t2:
    """Naga, the Liberated"""

    # 在你施放一个邪能法术后，随机获取一张纳迦牌，费用为1
    # 简化实现：任何法术都触发
    events = Play(CONTROLLER, SPELL).after(
        Give(CONTROLLER, RandomMinion(race=Race.NAGA)).then(
            Buff(Give.CARD, "CATA_527t2e")
        )
    )


class CATA_527t2e:
    cost = SET(1)


# CATA_529: 贪婪的邪能钓鱼者 (6费 5/5)
# 在本局对战中，你每施放一个邪能法术，本牌的法力值消耗便减少(1)点
class CATA_529:
    """Greedy Fel钓鱼者"""

    # 邪能法术后减少费用
    # 简化实现：任何法术后减少费用
    events = Play(CONTROLLER, SPELL).after(
        Buff(SELF, "CATA_529e")
    )


class CATA_529e:
    cost = -1


# CATA_697: 恶念变异体 (3费 3/4)
# 战吼：选择你手牌中的一张邪能法术牌，获取一张它的复制
class CATA_697:
    """Fel Void Mutant"""

    # 战吼：选择手牌中的一张邪能法术牌，获取复制
    # 简化实现：从手牌中随机获取一张邪能法术的复制
    def play(self):
        # 寻找手牌中的邪能法术
        # 简化实现：随机给一张邪能法术
        return Give(CONTROLLER, RandomSpell(spellschool=SpellSchool.FEL))


# CATA_699: 恐怖海兽 (9费 9/6)
# 嘲讽。战吼：选择一个敌方随从，偷取其3点生命值，触发三次
class CATA_699:
    """Terrace Dredger"""

    tags = {GameTag.TAUNT: True}

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 战吼：偷取目标3点生命值，触发3次
    # 简化实现：造成9点伤害，给自己加9点生命
    def play(self):
        target = self.target
        # 偷取3次，每次3点
        actions = []
        for _ in range(3):
            actions.append(Hit(target, 3))
            actions.append(Heal(FRIENDLY_HERO, 3))
        return actions


##
# Spells


# CATA_526: 布洛克斯加的奋战 (2费 法术)
# 对所有随从造成$1点伤害。每有一个随从死亡，抽一张牌
class CATA_526:
    """Blink Fox's Struggle"""

    # 对所有随从造成1点伤害
    # 简化实现：先造成伤害，然后抽牌
    def play(self):
        # 对所有随从造成1点伤害
        Hit(ALL_MINIONS, 1).trigger(self)
        # 简化实现：抽一张牌
        # 完整实现需要跟踪死亡随从数量
        return Draw(CONTROLLER)


# CATA_528: 海洋咒符 (1费 法术)
# 在你的下个回合开始时，召唤一个3/3并具有嘲讽的纳迦
class CATA_528:
    """Oceanic Sigil"""

    # 在下个回合开始时召唤3/3嘲讽纳迦
    events = OWN_TURN_BEGIN.on(
        Summon(CONTROLLER, "CATA_528t")
    )


# CATA_528t: 纳迦畸体 (3费 3/3 纳迦 嘲讽)
class CATA_528t:
    """Naga Spawn"""

    tags = {
        GameTag.TAUNT: True,
        GameTag.CARDRACE: Race.NAGA,
    }


# CATA_530: 邪能灌魔 (2费 法术)
# 兆示。在本回合中，你的英雄拥有吸血
class CATA_530:
    """Fel Infusion"""

    # 兆示效果（简化实现：直接触发效果）
    # 简化实现：直接给英雄吸血
    play = Buff(FRIENDLY_HERO, "CATA_530e")


# CATA_530e: 邪能灌魔 buff
class CATA_530e:
    tags = {GameTag.LIFESTEAL: True}


# CATA_533: 涣漫洪流 (5费 法术)
# 对你的对手最左边和最右边的随从造成5点伤害。流放：重复一次
class CATA_533:
    """Surging Tide"""

    # 对最左边和最右边的随从造成5点伤害
    # 简化实现：直接对最左和最右敌人造成5点伤害
    def play(self):
        # 获取敌方随从
        enemy_minions = self.controller.opponent.field
        if not enemy_minions:
            return Hit(ENEMY_HERO, 5)
        # 最左边
        left_target = enemy_minions[0]
        # 最右边
        right_target = enemy_minions[-1]
        actions = [Hit(left_target, 5)]
        if left_target != right_target:
            actions.append(Hit(right_target, 5))
        return actions

    # 流放：重复一次
    events = Play(CONTROLLER, PLAY_OUTCAST).after(
        Hit(RANDOM(ENEMY_MINIONS), 5)
    )
