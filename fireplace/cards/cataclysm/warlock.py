from ..utils import *


##
# Minions


class CATA_GuldanHerald(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        heralds = getattr(target, "_cataclysm_heralds", {}).copy()
        heralds["guldan"] = heralds.get("guldan", 0) + 1
        target._cataclysm_heralds = heralds


# CATA_490: 魔眼秘术师 (3费 3/6 嘲讽)
# 战吼：选择你手牌中的一张牌并弃掉
class CATA_490:
    """Ocular Occultist"""

    # 嘲讽属性
    tags = {GameTag.TAUNT: True}

    # 战吼：选择一张手牌并弃掉
    play = Choice(CONTROLLER, FRIENDLY_HAND - SELF).then(Discard(Choice.CARD))


# CATA_491: 怪异触手 (6费 法术)
# 对所有随从造成$3点伤害。重复此效果，每次伤害减少1点。
class CATA_491:
    """Eldritch Tentacles"""

    def play(self):
        yield Hit(ALL_MINIONS, 3)
        yield Deaths()
        yield Hit(ALL_MINIONS, 2)
        yield Deaths()
        yield Hit(ALL_MINIONS, 1)


# CATA_492: 暮光神坛 (3费 2/5)
# 兆示{0}。抽一张牌
class CATA_492:
    """Twilight Altar"""

    # 兆示。抽一张牌
    activate = CATA_GuldanHerald(CONTROLLER), Draw(CONTROLLER)


def _fiendish_servant_stats(entity, amount):
    return amount + (2 * entity.controller.discarded_cards_this_game)


# CATA_493: 地狱公爵 (4费 2/2 突袭)
# 在本局对战中，你每弃掉一张牌，便拥有+2/+2
class CATA_493:
    """Fiendish Servant"""

    tags = {GameTag.RUSH: True}

    update = Refresh(SELF, {
        GameTag.ATK: _fiendish_servant_stats,
        GameTag.HEALTH: _fiendish_servant_stats,
    })

    class Hand:
        update = Refresh(SELF, {
            GameTag.ATK: _fiendish_servant_stats,
            GameTag.HEALTH: _fiendish_servant_stats,
        })


# CATA_494: 马洛拉克 (5费 4/6)
# 在你弃掉一张随从牌后，召唤一个该随从的复制
class CATA_494:
    """Malorne"""

    # 在你弃掉一张随从牌后，召唤一个该随从的复制
    events = Discard(FRIENDLY_HAND + MINION).after(Summon(CONTROLLER, Copy(Discard.TARGET)))


# CATA_496: 诅咒之链 (5费 4/4)
# 直到敌方回合结束，夺取一个敌方随从的控制权。在本回合中，该随从无法攻击
class CATA_496_ReturnAtEnemyTurnEnd(TargetedAction):
    TARGET = ActionArg()
    PLAYER = ActionArg()

    def do(self, source, target, player):
        if player is not source.controller.opponent:
            return
        ret = source.game.queue_actions(source, [Steal(target, player)])
        source.remove()
        return ret


class CATA_496:
    """Cursed Chain"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 夺取控制权，并使其无法攻击
    play = Steal(TARGET), Buff(TARGET, "CATA_496e")


class CATA_496e:
    tags = {
        GameTag.CANT_ATTACK: True,
    }

    events = EndTurn().on(
        CATA_496_ReturnAtEnemyTurnEnd(OWNER, EndTurn.PLAYER)
    )


# CATA_498: 拉法姆的奋战 (3费 法术)
# 随机对两个敌方随从造成$@点伤害。（每回合都会升级！）
class CATA_498:
    """Rafaam's Strider"""

    def play(self):
        amount = 2 + sum(1 for buff in self.buffs if buff.id == "CATA_498e")
        yield Hit(RANDOM(ENEMY_MINIONS) * 2, amount)

    class Hand:
        events = OWN_TURN_BEGIN.on(Buff(SELF, "CATA_498e"))


@custom_card
class CATA_498e:
    tags = {
        GameTag.CARDNAME: "Rafaam's Strider Upgrade",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


# CATA_499: 助祭耗材 (3费 2/3)
# 当你使用或弃掉本牌时，随机召唤两个法力值消耗为（1）的随从
class CATA_499:
    """Sacrificial Summoner"""

    # 战吼（使用时）：召唤两个1费随从
    play = Summon(CONTROLLER, RandomMinion(cost=1)) * 2
    # 弃掉时：也召唤两个1费随从
    discard = Summon(CONTROLLER, RandomMinion(cost=1)) * 2


# CATA_725: 暗誓信徒 (2费 2/1)
# 战吼：兆示{0}。亡语：为你的英雄恢复#3点生命值
class CATA_725:
    """Dark Inquisitor"""

    # 战吼：兆示
    play = CATA_GuldanHerald(CONTROLLER)

    # 亡语：恢复3点生命值
    deathrattle = Heal(FRIENDLY_HERO, 3)


# CATA_726: 古加尔，暮光主谋 (9费 6/6)
# 巨型+2
# 你的手臂和士兵改为消灭敌方牌库中的随从
class CATA_726:
    """Gul'dan, Aspect of the Void"""

    tags = {GameTag.ELITE: True}

    colossal_limb_count = 2  # 巨型+2：手臂 + 士兵
    # 巨型+2：召唤手臂和士兵
    play = Summon(CONTROLLER, "CATA_726t"), Summon(CONTROLLER, "CATA_726t1")


# CATA_726t: 古加尔的手臂 (1费 1/1)
# 在你的回合结束时，消灭本随从右边的随从以获得+2/+2
class CATA_726t:
    """Gul'dan's Arm"""

    tags = {
        GameTag.COLOSSAL_LIMB: True,
        GameTag.COLOSSAL_LIMB_ON_LEFT: True,
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


@custom_card
class CATA_725te:
    tags = {
        GameTag.CARDNAME: "Gul'dan Soldier Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 2,
        GameTag.HEALTH: 2,
    }


##
# Spells


# CATA_791: 残影 (2费 法术)
# 造成4点伤害。重复
@custom_card
class CATA_791:
    """Shadowflame"""

    tags = {
        GameTag.CARDNAME: "Shadowflame",
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.CLASS: CardClass.WARLOCK,
        GameTag.COST: 2,
    }
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 对一个随从造成4点伤害，然后回到手牌（重复）
    play = Hit(TARGET, 4), Give(CONTROLLER, Copy(SELF))


# CATA_792: 暗影之怒 (6费 法术)
# 造成8点伤害。分裂：召唤两个3/3
@custom_card
class CATA_792:
    """Shadow Shock"""

    tags = {
        GameTag.CARDNAME: "Shadow Shock",
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.CLASS: CardClass.WARLOCK,
        GameTag.COST: 6,
    }
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 合成后的裂变牌执行两个半张效果。
    play = Hit(TARGET, 8), Summon(CONTROLLER, "CATA_792t3") * 2


@custom_card
class CATA_792t:
    """Shadow Shock"""

    tags = {
        GameTag.CARDNAME: "Shadow Shock",
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.CLASS: CardClass.WARLOCK,
        GameTag.COST: 6,
    }
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    play = Hit(TARGET, 8)


@custom_card
class CATA_792t2:
    """Shadow Shock"""

    tags = {
        GameTag.CARDNAME: "Shadow Shock",
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.CLASS: CardClass.WARLOCK,
        GameTag.COST: 6,
    }

    play = Summon(CONTROLLER, "CATA_792t3") * 2


@custom_card
class CATA_792t3:
    """Shadow Shock"""

    tags = {
        GameTag.CARDNAME: "Shadow Shock",
        GameTag.CARDTYPE: CardType.MINION,
        GameTag.CLASS: CardClass.WARLOCK,
        GameTag.COST: 3,
        GameTag.ATK: 3,
        GameTag.HEALTH: 3,
    }
