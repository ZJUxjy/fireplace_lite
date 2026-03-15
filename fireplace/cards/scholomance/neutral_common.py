from ..utils import *


##
# Minions


class SCH_311:
    """Animated Broomstick"""

    # <b>Battlecry:</b> Give your other minions <b>Rush</b>.
    play = Buff(FRIENDLY_MINIONS - SELF, "SCH_311e")


SCH_311e = buff(rush=True)
