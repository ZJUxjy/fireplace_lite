# Druid cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_060:
    """Ward of Earth"""

    class Hand:
        events = Death(FRIENDLY_MINIONS).on(
            Buff(SELF, "EDR_060e")
        )


class EDR_209:
    """Forest Lord Cenarius"""

    play = Choice(CONTROLLER, ["EDR_209a", "EDR_209b"]).then(
        Battlecry(Choice.CARD, None)
    )


class EDR_209a:
    """Growth of Dreams"""

    play = Buff(FRIENDLY_MINIONS, "EDR_209e2") * 2


class EDR_209b:
    """Ancients of the Dream"""

    play = Give(CONTROLLER, "EDR_209t5") * 2


class EDR_209e2:
    """Guidance of the Forest"""
    atk = 2
    health = 2


class EDR_209t5:
    """Ancient"""

    taunt = True


class EDR_270:
    """Horn of Plenty"""

    play = Draw(CONTROLLER).then(Buff(Draw.TARGET, "EDR_270e"))


class EDR_270e:
    """Horn of Plenty"""
    atk = 2
    health = 2


class EDR_271:
    """Grove Shaper"""

    play = Choice(CONTROLLER, ["EDR_271t", "EDR_271t"]).then(
        Battlecry(Choice.CARD, None)
    )


class EDR_271t:
    """Treant of Life"""

    deathrattle = Heal(FRIENDLY_HERO, 3)


class EDR_272:
    """Evergreen Stag"""

    taunt = True
    divine_shield = True


class EDR_273:
    """Symbiosis"""

    play = Summon(CONTROLLER, Copy(RANDOM(FRIENDLY_DECK + MINION))).then(
        Buff(Summon.CARD, "CS2_101e")
    )


class EDR_843:
    """Reforestation"""

    play = Choice(CONTROLLER, ["EDR_843a", "EDR_843b"]).then(
        Battlecry(Choice.CARD, None)
    )


class EDR_843a:
    """Aid of the Forest"""

    play = Summon(CONTROLLER, "EDR_843t1") * 3


class EDR_843b:
    """Fertilize"""

    play = Buff(FRIENDLY_MINIONS, "EDR_270e")


class EDR_843t1:
    """Reforestation"""

    pass


class EDR_845:
    """Hamuul Runetotem"""

    events = OWN_SPELL_PLAY.on(Buff(SELF, "EDR_845e1"))


class EDR_845e1:
    """Runetotem's Favor"""
    atk = 2
    health = 2


class EDR_847:
    """Dreambound Disciple"""

    play = Choice(CONTROLLER, ["EDR_847p"]).then(Buff(SELF, "EDR_847e"))


class EDR_847e:
    """Dreambound"""

    events = OWN_TURN_END.on(
        Summon(CONTROLLER, RandomMinion(cost=1))
    )


class EDR_847p:
    """Blessing of the Golem"""

    play = Summon(CONTROLLER, "EDR_847pt2")


class EDR_847pt2:
    """Plant Golem"""

    pass


class EDR_847pt3:
    """Plant Golem"""

    pass


class EDR_847pt4:
    """Plant Golem"""

    pass


class EDR_848:
    """Photosynthesis"""

    play = Draw(CONTROLLER) * 2


##
# Spells


class FIR_906:
    """Overheat"""

    play = Damage(ALL_MINIONS, 1)


class FIR_907:
    """Amirdrassil"""

    play = Summon(CONTROLLER, "CS2_101t")


class FIR_908:
    """Charred Chameleon"""

    play = Adapt(SELF)
