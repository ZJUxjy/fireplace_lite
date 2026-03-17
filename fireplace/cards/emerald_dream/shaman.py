# Shaman cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_031:
    """Ohn'ahra"""

    windfury = True
    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +4})


class EDR_230:
    """Beanstalk Brute"""

    play = Buff(SELF, "EDR_230e")


class EDR_230e:
    """Enchanted"""
    atk = 2
    health = 2


class EDR_231:
    """Aspect's Embrace"""

    play = Adapt(SELF)


class EDR_233:
    """Spirits of the Forest"""

    play = Choice(CONTROLLER, ["EDR_233a", "EDR_233b"]).then(Battlecry(Choice.CARD, None))


class EDR_233a:
    """Wolf's Strength"""

    play = Buff(FRIENDLY_MINIONS, "+3/+3")


class EDR_233b:
    """Falcon's Dexterity"""

    play = Draw(CONTROLLER)


class EDR_233t2:
    """Spirit Falcon"""

    windfury = True


class EDR_234:
    """Emerald Bounty"""

    play = Buff(FRIENDLY_MINIONS, "EDR_234e2")


class EDR_234e2:
    """Still Growing"""

    events = OWN_TURN_END.on(Buff(SELF, "+1/+1"))


class EDR_238:
    """Merithra"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_477:
    """Glowroot Lure"""

    taunt = True


class EDR_518:
    """Living Garden"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_529:
    """Plucky Podling"""

    deathrattle = Draw(CONTROLLER)


class EDR_448p:
    """Blessing of the Wind"""

    play = Buff(RANDOM_FRIENDLY_MINION, "CS2_101e")


##
# Spells


class EDR_232:
    """Typhoon"""

    play = Damage(ENEMY_MINIONS, 3), Freeze(ENEMY_MINIONS)


class FIR_778:
    """Avatar of Destruction"""

    play = Damage(ENEMY_HERO, 6)


class FIR_923:
    """Flames of the Firelord"""

    play = Damage(RANDOM_ENEMY_MINION, 2), Damage(RANDOM_FRIENDLY_MINION, 1)


class FIR_927:
    """Emberscarred Whelp"""

    deathrattle = Damage(ALL_MINIONS, 1)
