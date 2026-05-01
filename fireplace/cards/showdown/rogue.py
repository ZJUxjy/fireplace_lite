from ..utils import *


##
# Spells

class WW_403:
    """Pocket Sand"""

    # Deal 3 damage. Quickdraw: Your opponent's next card costs (1) more.
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3)
    # Quickdraw effect: increment a flag on opponent that adds +1 cost to next card.
    # Simplified: just buff opponent's hand cards' cost by 1 once (next card played
    # consumes the buff). For scope, we apply a buff that wears off at turn end.
    quickdraw = Buff(ENEMY_HAND, "WW_403e")


class WW_403e:
    # +1 cost; wears off at end of opponent's next turn (simplified).
    tags = {GameTag.COST: +1}
    events = TURN_END.on(Destroy(SELF))
