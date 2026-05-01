from ..utils import *


##
# Minions

class WW_360:
    """Azerite Chain Gang"""

    # Taunt. Battlecry AND Quickdraw: Summon a copy of this.
    play = Summon(CONTROLLER, ExactCopy(SELF))
    quickdraw = Summon(CONTROLLER, ExactCopy(SELF))


class WW_808:
    """Silver Serpent"""

    # Rush, Poisonous. Quickdraw: Gain Immune this turn.
    quickdraw = Buff(SELF, "WW_808e")


class WW_808e:
    tags = {GameTag.CANT_BE_DAMAGED: True}
    events = OWN_TURN_END.on(Destroy(SELF))


class WW_363:
    """Bounty Wrangler"""

    # 3-cost 3/3. Quickdraw or Combo: Get a Coin.
    quickdraw = Give(CONTROLLER, "GAME_005")
    combo = Give(CONTROLLER, "GAME_005")
