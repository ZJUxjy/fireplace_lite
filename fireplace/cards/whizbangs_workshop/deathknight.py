from hearthstone.enums import SpellSchool

from ..utils import *


##
# Minions


class TOY_827_SpendCorpses(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if getattr(player, "corpses", 0) < 5:
            return
        player.corpses -= 5
        return source.game.queue_actions(source, [
            Summon(player, ExactCopy(SELF))
        ])


class TOY_827:
    """Shambling Zombietank"""

    tags = {GameTag.TAUNT: True}
    play = TOY_827_SpendCorpses(CONTROLLER)


class TOY_821_GainReborn(TargetedAction):
    TARGET = ActionArg()
    SPELL = ActionArg()

    def do(self, source, target, spell):
        if getattr(getattr(spell, "data", None), "spell_school", None) != SpellSchool.FROST:
            return
        return source.game.queue_actions(source, [
            GiveReborn(target)
        ])


class TOY_821:
    """Rambunctious Stuffy"""

    tags = {GameTag.RUSH: True}
    events = Play(CONTROLLER, SPELL).after(TOY_821_GainReborn(SELF, Play.CARD))


class TOY_824:
    """Darkthorn Quilter"""

    events = OWN_TURN_END.on(Hit(RANDOM(ENEMY_CHARACTERS), 1) * ATK(SELF))


# TOY_828: Amateur Puppeteer (5费 3/4)
# 微缩。嘲讽。亡语：给你手牌中的不死随从+2/+2
class TOY_828:
    """Amateur Puppeteer"""

    tags = {GameTag.TAUNT: True}

    deathrattle = Buff(FRIENDLY_HAND + UNDEAD, "TOY_828e")


@custom_card
class TOY_828e:
    tags = {
        GameTag.CARDNAME: "Amateur Puppeteer Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 2,
        GameTag.HEALTH: 2,
    }


##
# Spells


class TOY_825:
    """Lesser Spinel Spellstone"""

    play = Buff(FRIENDLY_HAND + UNDEAD, "TOY_825e")
    progress_total = 5
    reward = Morph(SELF, "TOY_825t")

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))


class TOY_825t:
    """Spinel Spellstone"""

    play = Buff(FRIENDLY_HAND + UNDEAD, "TOY_825e2")
    progress_total = 5
    reward = Morph(SELF, "TOY_825t2")

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))


class TOY_825t2:
    """Greater Spinel Spellstone"""

    play = Buff(FRIENDLY_HAND + UNDEAD, "TOY_825e3")


TOY_825e = buff(+1, +1)
TOY_825e2 = buff(+2, +2)
TOY_825e3 = buff(+3, +3)


class TOY_826:
    """Threads of Despair"""

    play = Buff(ALL_MINIONS, "TOY_826e")


@custom_card
class TOY_826e:
    tags = {
        GameTag.CARDNAME: "Threads of Despair",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.DEATHRATTLE: True,
    }

    deathrattle = Hit(ALL_MINIONS, 1)


class MIS_100:
    """Helm of Humiliation"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Buff(TARGET, "MIS_100e", atk=-5, max_health=-5), Buff(
        RANDOM(FRIENDLY_HAND + MINION), "MIS_100e2", atk=5, max_health=5
    )


@custom_card
class MIS_100e:
    tags = {
        GameTag.CARDNAME: "Humiliated",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


@custom_card
class MIS_100e2:
    tags = {
        GameTag.CARDNAME: "Inspired",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


##
# Weapons


class MIS_101_GainDurability(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        player = weapon.controller
        if getattr(player, "corpses", 0) < 3:
            return
        player.corpses -= 3
        return source.game.queue_actions(source, [
            Buff(weapon, "MIS_101e")
        ])


class MIS_101:
    """Foamrender"""

    events = Attack(FRIENDLY_HERO).on(MIS_101_GainDurability(SELF))


MIS_101e = buff(health=1)
