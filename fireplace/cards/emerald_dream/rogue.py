# Rogue cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_521:
    """Tricky Satyr"""

    deathrattle = Draw(CONTROLLER)


class EDR_522:
    """Mimicry"""

    play = Give(CONTROLLER, Copy(RANDOM(ENEMY_HAND)))


class EDR_523:
    """Web of Deception"""

    play = Summon(CONTROLLER, "EDR_523t")


class EDR_523t:
    """Skittering Spiderling"""

    stealth = True


class EDR_524:
    """Shadowcloaked Assailant"""

    stealth = True


class EDR_525:
    """Barbed Thorn"""

    play = Choice(CONTROLLER, ["EDR_525A", "EDR_525B"]).then(Battlecry(Choice.CARD, None))


class EDR_525A:
    """Extra Eyes"""

    play = Buff(FRIENDLY_MINIONS, "EDR_525e")


class EDR_525B:
    """Extra Thorns"""

    play = Buff(FRIENDLY_WEAPON, "EDR_525e")


class EDR_525e:
    """Barbed Upgrade"""
    atk = 1


class EDR_526:
    """Renferal, the Malignant"""

    battlecry = Damage(ALL_MINIONS, 1)


class EDR_527:
    """Ashamane"""

    battlecry = GainArmor(FRIENDLY_HERO, 7)


class EDR_540:
    """Twisted Webweaver"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_780e:
    """Illusion?"""

    pass


class EDR_781:
    """Harbinger of the Blighted"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


##
# Spells


class EDR_528:
    """Nightmare Fuel"""

    play = Buff(ALL_MINIONS, "CS2_101e")


class FIR_919:
    """Everburning Phoenix"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")
    events = OWN_TURN_BEGIN.on(Buff(SELF, "-1"))


class FIR_920:
    """Smoke Bomb"""

    play = Stealth(FRIENDLY_MINIONS)


class FIR_922:
    """Cindersword"""

    play = Buff(SELF, "FIR_922e")


class FIR_922e:
    """Fiery"""

    events = Death(FRIENDLY_MINIONS).on(Summon(CONTROLLER, RandomMinion(cost=1)))
