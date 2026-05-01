from ..utils import *


##
# Outcast cards


class JAM_020:
    """Tough Crowd"""

    # 3-cost minion. Outcast: Return a minion to its owner's hand.
    outcast_requirements = {PlayReq.REQ_MINION_TARGET: 0}
    outcast = Bounce(TARGET)


class ETC_411:
    """SECURITY!!"""

    # 2-cost spell. Summon two 1/1 Illidari with Rush. Outcast: Summon one more.
    play = Summon(CONTROLLER, "BT_036t") * 2
    outcast = Summon(CONTROLLER, "BT_036t") * 3
