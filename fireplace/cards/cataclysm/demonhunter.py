import random as _random

from ..utils import *
from hearthstone.enums import SpellSchool

# Selector: SPELL cards with fel school
FEL_SPELL = SPELL + FuncSelector(
    lambda entities, source: [
        e for e in entities
        if getattr(getattr(e, "data", None), "spell_school", None) == SpellSchool.FEL
    ]
)


##
# Minions

# CATA_151: 艾萨拉，海洋之主 (8费 8/8)
# 巨型+2：召唤2个触手。你的英雄拥有风怒
class CATA_151:
    """Azshara, Lady of the Sea"""

    # 巨型+2：召唤2个触手
    play = Summon(CONTROLLER, "CATA_151t") * 2

    # 你的英雄拥有风怒（持续光环）
    update = Refresh(FRIENDLY_HERO, {GameTag.WINDFURY: True})


# CATA_151t: 艾萨拉的触手 (1费 2/1)
# 被召唤时，使你的英雄在当回合获得+1攻击力
class CATA_151t:
    """Azshara's Tentacle"""

    tags = {GameTag.COLOSSAL_LIMB: True}

    # 被召唤时，使你的英雄获得+1攻击力
    play = Buff(FRIENDLY_HERO, "CATA_151te")


class CATA_151te:
    tags = {GameTag.WINDFURY: True, GameTag.ATK: 1}


# CATA_525: 装甲放血纳迦 (3费 3/1)
# 突袭。战吼：兆示
class CATA_525:
    """Armored Bloodsail Naga"""

    # Rush. Battlecry: Herald (Soldier of Azshara).
    tags = {GameTag.RUSH: True}
    herald_soldier_id = "CATA_525t"
    play = Herald(CONTROLLER)


class CATA_525t:
    """Azshara's Mariner"""

    # When summoned, give your hero +{herald_count} Attack this turn.
    @staticmethod
    def play(self):
        amount = max(1, self.controller.herald_count)
        return [Buff(FRIENDLY_HERO, "CATA_525te") * amount]


@custom_card
class CATA_525te:
    tags = {
        GameTag.CARDNAME: "Azshara Mariner Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 1,
        GameTag.TAG_ONE_TURN_EFFECT: True,
    }


# CATA_527: 奈瑟匹拉，蒙难古灵 (3费 5/5)
# 造成1点伤害。在你施放一个邪能法术后，重新开启。亡语：召唤奈瑟匹拉，脱困古灵
class CATA_527:
    """Naga, the Dissenter (Location)"""

    # Use: Deal 1 damage. After Fel spell, reopen (re-trigger).
    location_action = Hit(RANDOM(ENEMY_MINIONS | ENEMY_HERO), 1)
    events = Play(CONTROLLER, FEL_SPELL).after(
        Hit(RANDOM(ENEMY_MINIONS | ENEMY_HERO), 1)
    )
    # Deathrattle: Summon Nespirah, Unshackled
    deathrattle = Summon(CONTROLLER, "CATA_527t2")


# CATA_527t2: 奈瑟匹拉，脱困古灵 (6费 6/6)
# 在你施放一个邪能法术后，随机获取一张纳迦牌，其法力值为(1)
class CATA_527t2:
    """Naga, the Liberated"""

    # 在你施放一个邪能法术后，随机获取一张纳迦牌，费用为1
    events = Play(CONTROLLER, FEL_SPELL).after(
        Give(CONTROLLER, RandomMinion(race=Race.NAGA)).then(
            Buff(Give.CARD, "CATA_527t2e")
        )
    )


@custom_card
class CATA_527t2e:
    tags = {
        GameTag.CARDNAME: "Naga Liberation Cost",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    cost = SET(1)


# CATA_529: 贪婪的邪能钓鱼者 (6费 5/5)
# 在本局对战中，你每施放一个邪能法术，本牌的法力值消耗便减少(1)点
class CATA_529:
    """Greedy Fel钓鱼者"""

    # 邪能法术后减少费用
    events = Play(CONTROLLER, FEL_SPELL).after(
        Buff(SELF, "CATA_529e")
    )


@custom_card
class CATA_529e:
    tags = {
        GameTag.CARDNAME: "Fel Affinity",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


# CATA_697: 恶念变异体 (3费 3/4)
# 战吼：选择你手牌中的一张邪能法术牌，获取一张它的复制
class CATA_697:
    """Fel Void Mutant"""

    # 战吼：从手牌中的邪能法术中随机选一张，获取一张复制
    def play(self):
        fel_spells = [
            c for c in self.controller.hand
            if c.type == CardType.SPELL
            and getattr(getattr(c, "data", None), "spell_school", None) == SpellSchool.FEL
        ]
        if fel_spells:
            chosen = _random.choice(fel_spells)
            yield Give(CONTROLLER, chosen.id)


# CATA_699: 恐怖海兽 (9费 9/6)
# 嘲讽。战吼：选择一个敌方随从，偷取其3点生命值，触发三次
class CATA_699:
    """Terrace Dredger"""

    tags = {GameTag.TAUNT: True}

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 战吼：偷取目标3点生命值，触发3次（造成伤害并治疗英雄）
    def play(self):
        target = self.target
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

    def play(self):
        # Count minions that will die from 1 damage (health == 1, no divine shield)
        deaths = sum(
            1 for m in self.game.board
            if m.health <= 1 and not m.divine_shield
        )
        yield Hit(ALL_MINIONS, 1)
        for _ in range(deaths):
            yield Draw(CONTROLLER)


# CATA_528: 海洋咒符 (1费 法术)
# 在你的下个回合开始时，召唤一个3/3并具有嘲讽的纳迦
@custom_card
class CATA_528e:
    """Oceanic Sigil"""

    tags = {
        GameTag.CARDNAME: "Oceanic Sigil",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    # 在下个回合开始时召唤纳迦，然后销毁自身（一次性效果）
    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, "CATA_528t"), Destroy(SELF))


class CATA_528:
    """Oceanic Sigil"""

    # 施放时给英雄添加一个下回合触发效果
    play = Buff(FRIENDLY_HERO, "CATA_528e")


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

    # Herald (Soldier of Azshara). Your hero has Lifesteal this turn.
    herald_soldier_id = "CATA_525t"
    play = Herald(CONTROLLER), Buff(FRIENDLY_HERO, "CATA_530e")


# CATA_530e: 邪能灌魔 buff（仅本回合有效）
@custom_card
class CATA_530e:
    tags = {
        GameTag.CARDNAME: "Fel Infusion",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.LIFESTEAL: True,
    }
    events = OWN_TURN_END.on(Destroy(SELF))


# CATA_533: 涣漫洪流 (5费 法术)
# 对你的对手最左边和最右边的随从造成5点伤害。流放：重复一次
class CATA_533:
    """Surging Tide"""

    # 对最左边和最右边的随从造成5点伤害
    def play(self):
        enemy_minions = self.controller.opponent.field
        if not enemy_minions:
            yield Hit(ENEMY_HERO, 5)
            return
        left_target = enemy_minions[0]
        right_target = enemy_minions[-1]
        yield Hit(left_target, 5)
        if left_target != right_target:
            yield Hit(right_target, 5)

    # 流放：重复一次
    events = Play(CONTROLLER, PLAY_OUTCAST).after(
        Hit(RANDOM(ENEMY_MINIONS), 5)
    )
