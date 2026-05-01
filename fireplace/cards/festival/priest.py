from ..utils import *


##
# Minions


class ETC_334:
    """Heartbreaker Hedanis"""

    # Battlecry: Deal 4 damage to this minion. Overheal: Deal 5 damage to a random enemy.
    play = Hit(SELF, 4)
    events = Overheal(SELF).on(Hit(RANDOM_ENEMY_CHARACTER, 5))


class ETC_339:
    """Heartthrob"""

    # Overheal: Summon a random minion with Cost equal to the amount Overhealed.
    events = Overheal(SELF).on(
        Summon(CONTROLLER, RandomMinion(cost=Overheal.AMOUNT))
    )


class JAM_024:
    """Ambient Lightspawn"""

    # Finale and Overheal: Give another random friendly minion +2/+2.
    # NOTE: Finale (cost == max mana) is not yet engine-supported, so this
    # currently fires only the Overheal branch.
    events = Overheal(SELF).on(Buff(RANDOM_OTHER_FRIENDLY_MINION, "JAM_024e"))


JAM_024e = buff(+2, +2)
