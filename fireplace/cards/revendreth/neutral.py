from ..utils import *


##
# INFUSE cards from Murder at Castle Nathria (Revendreth set)
#
# INFUSE keyword: After N friendly minions die, this card morphs in hand into
# its "infused" form (an upgraded version with stronger effect).
# Implementation reuses the existing AddProgress/reward infrastructure:
#   progress_total = N
#   Hand.events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))
#   reward = Morph(SELF, "<infused_id>")


class REV_244:
    """Mischievous Imp"""

    # 4-cost. Battlecry: Summon a copy of this. Infuse (3): Summon two copies instead.
    play = Summon(CONTROLLER, ExactCopy(SELF))
    progress_total = 3

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_244t")


class REV_244t:
    """Mischievous Imp (Infused)"""

    # Battlecry: Summon two copies of this.
    play = Summon(CONTROLLER, ExactCopy(SELF)) * 2


class REV_019:
    """Famished Fool"""

    # 5-cost. Battlecry: Draw a card. Infuse (4): Draw 3 instead.
    play = Draw(CONTROLLER)
    progress_total = 4

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_019t")


class REV_019t:
    """Famished Fool (Infused)"""

    # Battlecry: Draw 3 cards.
    play = Draw(CONTROLLER), Draw(CONTROLLER), Draw(CONTROLLER)


class REV_252:
    """Clean the Scene"""

    # 5-cost spell. Destroy minions with 3 or less Attack. Infuse (3): 6 or less.
    play = Destroy(ALL_MINIONS + (ATK <= 3))
    progress_total = 3

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_252t")


class REV_252t:
    """Clean the Scene (Infused)"""

    play = Destroy(ALL_MINIONS + (ATK <= 6))


class REV_013:
    """Stoneborn Accuser"""

    # 5-cost minion 5/5. Infuse (5): Gain "Battlecry: Deal 5 damage."
    progress_total = 5

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_013t")


class REV_013t:
    """Stoneborn Accuser (Infused)"""

    # Has gained "Battlecry: Deal 5 damage" — needs target.
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 5)
