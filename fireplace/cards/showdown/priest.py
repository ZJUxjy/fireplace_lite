from ..utils import *


##
# Spells

class WW_823:
    """Rehydrate"""

    # Restore 7 Health. Quickdraw: Refresh 2 Mana Crystals.
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Heal(TARGET, 7)
    quickdraw = ManaThisTurn(CONTROLLER, 2)
