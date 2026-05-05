from ..utils import *


##
# TTN_737: The Primus (8费 7/9)
# 泰坦。使用技能后，发现对应符文的牌

class TTN_737:
    """The Primus"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_737t", "TTN_737t1", "TTN_737t3"]
    ability_used = Discover(CONTROLLER, RandomCard(card_class=CardClass.DEATHKNIGHT))


class TTN_737_RunesOfBlood(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        primus = getattr(source, "creator", source)
        amount = target.health
        return source.game.queue_actions(
            source,
            [
                Buff(primus.controller.hero, "TTN_737te", max_health=amount),
                Buff(primus, "TTN_737te", max_health=amount),
                Destroy(target),
            ],
        )


# TTN_737t: Runes of Blood - Destroy an enemy minion; restore health equal to its Health to your hero
class TTN_737t:
    """Runes of Blood"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = TTN_737_RunesOfBlood(TARGET)


@custom_card
class TTN_737te:
    tags = {
        GameTag.CARDNAME: "Blood of the Primus",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


# TTN_737t1: Runes of the Unholy - Summon two Reborn Taunt Undead
class TTN_737t1:
    """Runes of the Unholy"""

    play = Summon(CONTROLLER, "TTN_737t2") * 2


class TTN_737t2:
    """Servant of the Primus"""

    tags = {
        GameTag.TAUNT: True,
        GameTag.REBORN: True,
        GameTag.CARDRACE: Race.UNDEAD,
    }


# TTN_737t3: Runes of Frost - Next spell costs 3 less and has Spell Damage +3
class TTN_737t3:
    """Runes of Frost"""

    play = Buff(CONTROLLER, "TTN_737e")


@custom_card
class TTN_737e:
    tags = {
        GameTag.CARDNAME: "Chill of Death",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    update = (
        Refresh(FRIENDLY_HAND + SPELL, {GameTag.COST: -3}),
        Refresh(CONTROLLER, {GameTag.SPELLPOWER: 3}),
    )
    events = Play(CONTROLLER, SPELL).after(Destroy(SELF))
