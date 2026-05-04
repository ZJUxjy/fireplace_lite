from ..utils import *


##
# Minions

# CATA_153: 奥拉基尔，风暴之主 (8费 2/8)
# 巨型+2, 突袭, 风怒
# 战吼：获取2个费用等于此随从攻击力的随从，费用变为(1)
class CATA_153:
    """Al'Akir, Lord of Storms"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 8,
        GameTag.ATK: 2,
        GameTag.HEALTH: 8,
        GameTag.RUSH: True,
        GameTag.WINDFURY: True,
    }

    # 战吼：获取2个费用等于此随从攻击力的随机随从，费用变为(1)
    def play(self):
        cost = self.atk
        return [
            Give(CONTROLLER, RandomMinion(cost=cost)).then(Buff(Give.CARD, "CATA_153_cost1e")),
            Give(CONTROLLER, RandomMinion(cost=cost)).then(Buff(Give.CARD, "CATA_153_cost1e")),
        ]


@custom_card
class CATA_153_cost1e:
    """Al'Akir Wind Cost"""

    tags = {
        GameTag.CARDNAME: "Al'Akir Wind Cost",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    cost = SET(1)


# CATA_153e: 火花之怒 (buff)
class CATA_153e:
    """Spark of Fury"""

    tags = {
        GameTag.ATK: +2,
    }


# CATA_153t: 奥拉基尔的充能之手 (附属物)
class CATA_153t:
    """Charged Hand of Al'Akir"""

    # 相邻随从获得+2攻击力
    play = Buff(ADJACENT, "CATA_153e")


# CATA_153t1: 奥拉基尔的充能之手 (升级版)
class CATA_153t1:
    """Charged Hand of Al'Akir (upgraded)"""

    # 相邻随从获得+3攻击力
    play = Buff(ADJACENT, "CATA_153e1")


@custom_card
class CATA_153e1:
    tags = {
        GameTag.CARDNAME: "Charged Hand Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 3,
    }



# CATA_561: 能量仪式 (2费 法术)
# 兆示，获取2个1/1具有突袭的元素
class CATA_561:
    """Ritual of Power"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 2,
        GameTag.CLASS: CardClass.SHAMAN,
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.RARITY: 3,
    }

    play = Give(CONTROLLER, "CATA_561t") * 2


# CATA_561t: 微风精灵 (1费 1/1 元素)
class CATA_561t:
    """Breezling"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 1,
        GameTag.ATK: 1,
        GameTag.HEALTH: 1,
        GameTag.RUSH: True,
    }


# CATA_563: 雷鸣流云 (3费 4/3)
# 战吼：选择手牌中一张费用(4)或更低的法术来吸收
# 亡语：释放它
class CATA_563_Absorb(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        source._absorbed_spell = target
        target.zone = Zone.SETASIDE
        source.game.manager.targeted_action(self, source, target)


class CATA_563_CastAbsorbed(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        spell = getattr(target, "_absorbed_spell", None)
        if spell:
            source.game.queue_actions(spell, [CastSpell(spell)])


class CATA_563:
    """Crackling Cloudstrider"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 3,
        GameTag.ATK: 4,
        GameTag.HEALTH: 3,
        GameTag.RARITY: 4,
    }

    play = Choice(CONTROLLER, FRIENDLY_HAND + SPELL + (COST <= 4)).then(
        CATA_563_Absorb(Choice.CARD)
    )
    deathrattle = CATA_563_CastAbsorbed(SELF)


# CATA_563e2: 阴云 (buff)
class CATA_563e2:
    """Overcast"""

    tags = {
        GameTag.DEATHRATTLE: True,
    }


class CATA_AlakirHerald(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        heralds = getattr(target, "_cataclysm_heralds", {}).copy()
        heralds["alakir"] = heralds.get("alakir", 0) + 1
        target._cataclysm_heralds = heralds


# CATA_564: 飞行助翼 (5费 5/5)
# 战吼：使一个友方随从获得Mega-Windfury，无法攻击英雄
class CATA_564:
    """Air Support"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 5,
        GameTag.ATK: 5,
        GameTag.HEALTH: 5,
        GameTag.RARITY: 1,
    }

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 战吼：给目标随从超级风怒，且无法攻击英雄。
    play = SetTags(TARGET, {
        GameTag.MEGA_WINDFURY: True,
        GameTag.CANNOT_ATTACK_HEROES: True,
    })


# CATA_565: 天空之墙哨兵 (2费 0/3)
# 嘲讽，战吼：兆示
class CATA_565:
    """Skywall Sentinel"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 2,
        GameTag.ATK: 0,
        GameTag.HEALTH: 3,
        GameTag.TAUNT: True,
        GameTag.RARITY: 3,
    }

    # 战吼：兆示
    play = CATA_AlakirHerald(CONTROLLER)


# CATA_565t: 奥拉基尔的士兵 (1费 1/2)
class CATA_565t:
    """Soldier of Al'Akir"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 1,
        GameTag.ATK: 1,
        GameTag.HEALTH: 2,
    }
    update = Refresh(SELF_ADJACENT, {GameTag.ATK: +1})


# CATA_567: 升腾 (4费 法术)
# 将所有友方随从变形成费用增加(1)的随从，它们死亡时召唤原始随从
class CATA_567_Ascend(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        cards = RandomMinion(cost=target.cost + 1).evaluate(source)
        if not cards:
            return []
        return source.game.queue_actions(
            source,
            [
                Morph(target, cards[0]).then(
                    StoringBuff(Morph.CARD, "CATA_567e", ExactCopy(Morph.TARGET))
                )
            ],
        )


class CATA_567:
    """Ascendance"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 4,
        GameTag.CLASS: CardClass.SHAMAN,
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.RARITY: 4,
    }

    play = CATA_567_Ascend(FRIENDLY_MINIONS)


class CATA_567e:
    """Ascendance enchantment"""

    tags = {GameTag.DEATHRATTLE: True}
    deathrattle = Summon(CONTROLLER, STORE_CARD)


# CATA_568: 穆拉丁的奋战 (9费 法术)
# 抽2张牌，每有一个友方角色攻击过，费用就减少(1)
def _muradins_last_stand_cost(entity, amount):
    return amount - entity.controller.friendly_attacks_this_game


class CATA_568:
    """Muradin's Last Stand"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 9,
        GameTag.CLASS: CardClass.SHAMAN,
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.RARITY: 3,
    }

    play = Draw(CONTROLLER) * 2

    class Hand:
        update = Refresh(SELF, {GameTag.COST: _muradins_last_stand_cost})


# CATA_569: 演武仪式 (4费 法术)
# 随机召唤一个3费、2费和1费的随从，过载(1)
class CATA_569:
    """Ceremonial Clash"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 4,
        GameTag.CLASS: CardClass.SHAMAN,
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.OVERLOAD: 1,
        GameTag.RARITY: 1,
    }

    # 随机召唤3费、2费、1费随从
    play = Summon(CONTROLLER, RandomMinion(cost=3)), Summon(CONTROLLER, RandomMinion(cost=2)), Summon(CONTROLLER, RandomMinion(cost=1))


class CATA_570_DrawOverflow(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        remaining = 10
        results = []
        while remaining > 0 and target.deck:
            card = target.deck[-1]
            spent = max(0, card.cost)
            drawn = source.game.queue_actions(source, [Draw(target)])
            results.extend(drawn)
            if card.zone == Zone.HAND:
                source.game.queue_actions(source, [
                    Buff(card, "CATA_570e", cost=-remaining)
                ])
            remaining -= spent
        return results


# CATA_570: 莫卓克 (10费 10/10)
# 战吼：抽1张牌并减少其费用(10)
class CATA_570:
    """Morchok"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 10,
        GameTag.ATK: 10,
        GameTag.HEALTH: 10,
        GameTag.RARITY: 5,
    }

    play = CATA_570_DrawOverflow(CONTROLLER)


CATA_570e = buff(cost=-10)



# CATA_724: 缚风者 (4费 7/7)
# 亡语：解锁你被过载的水晶，过载(3)
class CATA_724:
    """Stormbinder"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 4,
        GameTag.ATK: 7,
        GameTag.HEALTH: 7,
        GameTag.OVERLOAD: 3,
        GameTag.RARITY: 1,
    }

    # 亡语：解锁你被过载的水晶
    deathrattle = UnlockOverload(CONTROLLER)
