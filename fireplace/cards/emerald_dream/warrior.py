# Warrior cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_454:
    """Clutch of Corruption"""

    deathrattle = Summon(CONTROLLER, "EDR_454t")


class EDR_454t:
    """Horrible Egg"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_456:
    """Darkrider"""

    charge = True


class EDR_457:
    """Brood Keeper"""

    deathrattle = Summon(CONTROLLER, "EDR_457t")


class EDR_457t:
    """Nightmare Slicer"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_459:
    """Afflicted Devastator"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_465:
    """Ysondre"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_468:
    """Eggbasher"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_471:
    """Tortolla"""

    taunt = True
    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +4})


class EDR_471e:
    """Tortolla's Rage"""

    pass


class FIR_928:
    """Keeper of Flame"""

    events = Damage(SELF).on(Buff(SELF, "FIR_928e"))


class FIR_928e:
    """Blazing Strength"""
    atk = 2
    health = 2


class FIR_956:
    """Dragon Turtle"""

    deathrattle = GainArmor(FRIENDLY_HERO, 5)


class FIR_956e:
    """Turtle Maw"""

    pass


##
# Spells


class EDR_455:
    """Succumb to Madness"""

    play = Damage(FRIENDLY_HERO, 5)


class EDR_531:
    """Siphoning Growth"""

    play = Draw(CONTROLLER), GainArmor(FRIENDLY_HERO, 3)


class EDR_531e:
    """Siphoned Growth"""

    pass


class EDR_570:
    """Ominous Nightmares"""

    play = Choice(CONTROLLER, ["EDR_570A", "EDR_570B"]).then(Battlecry(Choice.CARD, None))


class EDR_570A:
    """Nightmarish Burst"""

    play = Damage(ENEMY_MINIONS, 1)


class EDR_570B:
    """Unstable Power"""

    play = Buff(FRIENDLY_MINIONS, "EDR_570e")


class EDR_570e:
    """Terror of the Night"""
    atk = 2
    health = 2


class EDR_468e1:
    """Scrambled Attack"""

    pass


class FIR_939:
    """Shadowflame Suffusion"""

    play = Buff(FRIENDLY_MINIONS, "CS2_101e")
