# Priest cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_449:
    """Lunarwing Messenger"""

    deathrattle = CastSpell("EDR_449e")


class EDR_449e:
    """Fleeting Magic"""

    play = Bounce(ALL_MINIONS)


class EDR_449p:
    """Blessing of the Moon"""

    play = Buff(RANDOM_FRIENDLY_MINION, "EDR_449e")


class EDR_460:
    """Wish of the New Moon"""

    play = Summon(CONTROLLER, "EDR_460t")


class EDR_460t:
    """Wish of the Full Moon"""

    deathrattle = Draw(CONTROLLER)


class EDR_461:
    """Ritual of the New Moon"""

    play = Summon(CONTROLLER, "EDR_461t")


class EDR_461t:
    """Ritual of the Full Moon"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_462:
    """Selenic Drake"""

    deathrattle = CastSpell("CS2_101e")


class EDR_463:
    """Twilight Influence"""

    play = Choice(CONTROLLER, ["EDR_463a", "EDR_463b"]).then(Battlecry(Choice.CARD, None))


class EDR_463a:
    """Constricting Thorns"""

    play = Damage(ENEMY_MINIONS, 2)


class EDR_463b:
    """Controlling Vines"""

    play = Freeze(ENEMY_MINIONS)


class EDR_464:
    """Tyrande"""

    play = Buff(FRIENDLY_MINIONS, "EDR_464e2")


class EDR_464e2:
    """Pull of the Moon"""

    events = OWN_TURN_END.on(Heal(FRIENDLY_HERO, 2))


class EDR_472:
    """Weaver of the Cycle"""

    events = Draw(CONTROLLER).on(Buff(SELF, "CS2_101e"))


class EDR_970:
    """Kaldorei Priestess"""

    battlecry = Damage(TARGET, 1)


class EDR_970e:
    """Pacified"""

    pass


class EDR_895:
    """Aviana, Elune's Chosen"""

    play = Buff(FRIENDLY_MINIONS, "EDR_895e")


class EDR_895e:
    """Full Moon"""
    atk = 2
    health = 2


class EDR_895t:
    """Moon Cycle"""

    pass


class FIR_777:
    """Spirit of the Kaldorei"""

    # TODO: Should return to hand when friendly minion dies
    pass


class FIR_916:
    """Smoldering Ascent"""

    play = Damage(ENEMY_MINIONS, 1)


class FIR_918:
    """Light of the New Moon"""

    play = Summon(CONTROLLER, "FIR_918t")


class FIR_918t:
    """Light of the Full Moon"""

    deathrattle = Heal(FRIENDLY_HERO, 3)
