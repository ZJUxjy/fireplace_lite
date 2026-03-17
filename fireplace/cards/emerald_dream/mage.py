# Mage cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_430:
    """Aessina"""

    taunt = True
    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +4})


class EDR_517:
    """Q'onzu"""

    play = Choice(CONTROLLER, ["EDR_517A", "EDR_517B"]).then(Battlecry(Choice.CARD, None))


class EDR_517A:
    """Tranquil Breeze"""

    play = Heal(ALL_CHARACTERS, 2)


class EDR_517B:
    """Winds of Change"""

    play = Buff(RANDOM(FRIENDLY_MINIONS), "CS2_101e")


class EDR_519:
    """Wisprider"""

    play = Buff(ALL_MINIONS, "EDR_519e")


class EDR_519e:
    """Wisprider Magic"""

    events = OWN_TURN_END.on(Summon(CONTROLLER, "CS2_101t"))


class EDR_520:
    """Forbidden Shrine"""

    play = Summon(CONTROLLER, "CS2_101t")


class EDR_872:
    """Spark of Life"""

    play = Choice(CONTROLLER, ["EDR_872A", "EDR_872B"]).then(Battlecry(Choice.CARD, None))


class EDR_872A:
    """Gift of Fire"""

    play = Buff(RANDOM_MINION, "+3/+3")


class EDR_872B:
    """Gift of Nature"""

    play = Draw(CONTROLLER)


class EDR_940:
    """Merry Moonkin"""

    spell_power = 1
    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_941:
    """Starsurge"""

    play = Damage(ENEMY_MINIONS, 2)


##
# Spells


class EDR_804:
    """Divination"""

    play = Draw(CONTROLLER) * 2


class EDR_851p:
    """Blessing of the Wisp"""

    play = Summon(CONTROLLER, "EDR_851t")


class EDR_851t:
    """Wisp"""

    pass


class EDR_874:
    """Stellar Balance"""

    play = Buff(ALL_MINIONS, "EDR_874e")


class EDR_874e:
    """Stellar Balance"""

    events = Death(FRIENDLY_MINIONS).on(Draw(CONTROLLER))


class FIR_910:
    """Scorching Winds"""

    play = Damage(RANDOM_ENEMY_MINION, 3)


class FIR_911:
    """Smoldering Grove"""

    play = Draw(CONTROLLER)


class FIR_913:
    """Inferno Herald"""

    deathrattle = Damage(RANDOM_ENEMY_CHARACTER, 3)
