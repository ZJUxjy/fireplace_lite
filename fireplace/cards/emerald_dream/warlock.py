# Warlock cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_482:
    """Rotten Apple"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")
    events = OWN_TURN_END.on(Heal(FRIENDLY_HERO, 6))


class EDR_482e:
    """Fracture"""

    pass


class EDR_483:
    """Fractured Power"""

    play = Draw(CONTROLLER) * 2


class EDR_485:
    """Rotheart Dryad"""

    lifesteal = True


class EDR_487:
    """Wallow, the Wretched"""

    lifesteal = True


class EDR_488:
    """Avant-Gardening"""

    play = Summon(CONTROLLER, "CS2_101t")


class EDR_489:
    """Agamaggan"""

    battlecry = Buff(ALL_MINIONS, "EDR_489e1")


class EDR_489e1:
    """Corrupted Thorns"""

    atk = 2
    health = 2


class EDR_490:
    """Sleep Paralysis"""

    play = Choice(CONTROLLER, ["EDR_490a", "EDR_490b"]).then(Battlecry(Choice.CARD, None))


class EDR_490a:
    """Figure in the Dark"""

    play = Summon(CONTROLLER, "EDR_490t")


class EDR_490b:
    """Wit's End"""

    play = Destroy(ENEMY_MINIONS)


class EDR_490t:
    """Night Terror"""

    deathrattle = Damage(FRIENDLY_HERO, 3)


class EDR_491:
    """Archdruid of Thorns"""

    battlecry = Buff(FRIENDLY_MINIONS, "EDR_491e")


class EDR_491e:
    """Devoured Soul"""
    atk = 1
    health = 1


class EDR_494:
    """Hungering Ancient"""

    lifesteal = True


class EDR_654:
    """Overgrown Horror"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_654e:
    """Overgrown"""
    atk = 1
    health = 1


##
# Spells


class EDR_482e:
    """Fracture"""

    pass


class EDR_483e:
    """Delayed Mana"""

    pass


class EDR_489e2:
    """Corrupted Thorns"""

    atk = 3
    health = 3


class FIR_924:
    """Shadowflame Stalker"""

    deathrattle = Damage(RANDOM_ENEMY_CHARACTER, 2)


class FIR_954:
    """Conflagrate"""

    play = Damage(TARGET, 2)


class FIR_955:
    """Emberroot Destroyer"""

    deathrattle = Damage(ENEMY_HERO, 3)
