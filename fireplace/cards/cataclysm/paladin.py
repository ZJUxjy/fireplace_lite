from ..utils import *
from ... import enums
from hearthstone.enums import SpellSchool


##
# Minions

# CATA_432: 克洛玛图斯 (Chromatus)
# 8费 8/8 巨型+4
# 嘲讽、吸血、扰魔、圣盾
class CATA_432:
    """Chromatus"""

    colossal_limb_count = 4  # 巨型+4：4个头颅（field slots needed beyond the body）
    # 绿、红、蓝、青铜头颅
    play = Summon(CONTROLLER, "CATA_432t1"), Summon(CONTROLLER, "CATA_432t2"), Summon(CONTROLLER, "CATA_432t3"), Summon(CONTROLLER, "CATA_432t4")


# CATA_432t1: 克洛玛图斯的绿色头颅
# 2费 2/3 龙
# 嘲讽。亡语：移除克洛玛图斯的嘲讽
class CATA_432t1:
    """Green Head of Chromatus"""

    tags = {
        GameTag.TAUNT: True,
        GameTag.COLOSSAL_LIMB: True,
        GameTag.COLOSSAL_LIMB_ON_LEFT: True,
    }

    deathrattle = SetTags(COLOSSAL_BODY, {GameTag.TAUNT: False})


# CATA_432t2: 克洛玛图斯的红色头颅
# 2费 2/3 龙
# 吸血。亡语：移除克洛玛图斯的吸血
class CATA_432t2:
    """Red Head of Chromatus"""

    tags = {
        GameTag.LIFESTEAL: True,
        GameTag.COLOSSAL_LIMB: True,
        GameTag.COLOSSAL_LIMB_ON_LEFT: True,
    }

    deathrattle = SetTags(COLOSSAL_BODY, {GameTag.LIFESTEAL: False})


# CATA_432t3: 克洛玛图斯的蓝色头颅
# 2费 2/3 龙
# 扰魔。亡语：移除克洛玛图斯的扰魔
class CATA_432t3:
    """Blue Head of Chromatus"""

    tags = {
        GameTag.ELUSIVE: True,
        GameTag.COLOSSAL_LIMB: True,
    }

    deathrattle = SetTags(COLOSSAL_BODY, {GameTag.ELUSIVE: False})


# CATA_432t4: 克洛玛图斯的青铜头颅
# 2费 2/3 龙
# 圣盾。亡语：移除克洛玛图斯的圣盾
class CATA_432t4:
    """Bronze Head of Chromatus"""

    tags = {
        GameTag.DIVINE_SHIELD: True,
        GameTag.COLOSSAL_LIMB: True,
    }

    deathrattle = SetTags(COLOSSAL_BODY, {GameTag.DIVINE_SHIELD: False})


# CATA_472: 灵感之槌
# 2费 2/2 武器
# 亡语：随机触发一个友方随从的回合结束效果
class CATA_472:
    """Inspiring Maul"""

    deathrattle = Activate(RANDOM(FRIENDLY_MINIONS))


# CATA_473: 诺兹多姆，青铜守护巨龙
# 5费 4/4 龙
# 在你的回合结束时，使你的随从获得圣盾，已有圣盾的随从改为获得+3/+3
class CATA_473_EndTurn(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        initially_shielded = [minion for minion in target.field if minion.divine_shield]
        initially_unshielded = [
            minion for minion in target.field if not minion.divine_shield
        ]
        actions = [GiveDivineShield(minion) for minion in initially_unshielded]
        actions.extend(Buff(minion, "CATA_473e") for minion in initially_shielded)
        source.game.queue_actions(source, actions)


class CATA_473:
    """Nozdormu, Bronze Aspect"""

    events = OWN_TURN_END.on(CATA_473_EndTurn(CONTROLLER))


CATA_473e = buff(+3, +3)


# CATA_474: 矛心哨卫
# 4费 3/4 龙
# 在你的回合结束时，随机获取一张神圣法术牌，其法力值消耗减少（3）点
class CATA_474:
    """Spearheart Sentry"""

    events = OWN_TURN_END.on(
        Give(CONTROLLER, RandomSpell(spell_school=SpellSchool.HOLY)).then(
            Buff(Give.CARD, "CATA_474e")
        )
    )


@custom_card
class CATA_474e:
    tags = {
        GameTag.CARDNAME: "Holy Spell Discount",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -3,
    }


# CATA_475: 破鳞盾卫
# 6费 3/6
# 在你的回合结束时，对所有敌人造成2点伤害
class CATA_475:
    """Scales of Justice"""

    events = OWN_TURN_END.on(Hit(ENEMY_MINIONS | ENEMY_HERO, 2))


class CATA_478_SummonCurrentStats(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        atk_delta = source.atk - 1
        health_delta = source.health - 1
        return source.game.queue_actions(source, [
            Summon(target, "CATA_478t").then(
                Buff(Summon.CARD, "CATA_478e", atk=atk_delta, max_health=health_delta)
            )
        ])


# CATA_478: 青铜救赎者
# 5费 3/3 龙
# 在你的回合结束时，召唤一条属性值等同于本随从的龙
class CATA_478:
    """Bronze Redemption"""

    events = OWN_TURN_END.on(CATA_478_SummonCurrentStats(CONTROLLER))


# CATA_478t: 青铜蛮兵
# 1费 1/1 龙
class CATA_478t:
    """Bronze Sellsword"""

    tags = {GameTag.CARDRACE: Race.DRAGON}


@custom_card
class CATA_478e:
    tags = {
        GameTag.CARDNAME: "Bronze Redeemer Stats",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


##
# Spells

# CATA_477: 守护巨龙之厅
# 2费 法术
# 选择你手牌中的一张随从牌，使其获得+2/+2
class CATA_477:
    """Hall of the Dragonflight"""

    activate = Choice(CONTROLLER, FRIENDLY_HAND + MINION).then(
        Buff(Choice.CARD, "CATA_477e")
    )


CATA_477e = buff(+2, +2)


# CATA_479: 飞龙机动
# 4费 法术
# 裂变：召唤两条4/2的幼龙。使你的随从获得+1/+1和圣盾
class CATA_479:
    """Dragonriding"""

    play = (
        Summon(CONTROLLER, "CATA_479t3") * 2,
        Buff(FRIENDLY_MINIONS, "CATA_479e"),
        GiveDivineShield(FRIENDLY_MINIONS),
    )


class CATA_479t:
    """Dragonriding"""

    play = Summon(CONTROLLER, "CATA_479t3") * 2


class CATA_479t2:
    """Dragonriding"""

    play = Buff(FRIENDLY_MINIONS, "CATA_479e"), GiveDivineShield(FRIENDLY_MINIONS)


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

    def play(self):
        turns = 3 + getattr(self, "_aura_duration_bonus", 0)
        return (Buff(CONTROLLER, "CATA_480e", _sandwind_turns_remaining=turns),)


# CATA_480e: 沙怒光环 buff
@custom_card
class CATA_480e:
    def _tick_duration(self, *args):
        if getattr(self, "_sandwind_last_tick_turn", None) == self.game.turn:
            return None
        self._sandwind_last_tick_turn = self.game.turn
        self._sandwind_turns_remaining = getattr(
            self, "_sandwind_turns_remaining", 3
        ) - 1
        if self._sandwind_turns_remaining <= 0:
            self._sandwind_expired = True
        return None

    def _destroy_if_expired(self, *args):
        if getattr(self, "_sandwind_expired", False):
            return Destroy(SELF)
        return None

    tags = {
        GameTag.CARDNAME: "Sandwind Aura",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    update = Refresh(CONTROLLER, {enums.MINION_EXTRA_END_TURN_EFFECT: True})
    events = [
        OWN_TURN_END.on(_tick_duration),
        OWN_TURN_BEGIN.on(_destroy_if_expired),
    ]


# CATA_621: 格尔宾的胜利
# 1费 法术
# 随机获取一张圣骑士光环牌，其持续时间增加一回合
class CATA_621_AddDuration(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        target._aura_duration_bonus = getattr(target, "_aura_duration_bonus", 0) + 1
        source.game.manager.targeted_action(self, source, target)


class CATA_621:
    """Galakrond's Triumph"""

    play = Give(CONTROLLER, RandomID("CATA_480")).then(
        CATA_621_AddDuration(Give.CARD)
    )
