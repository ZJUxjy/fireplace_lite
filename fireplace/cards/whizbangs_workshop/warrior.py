from ..utils import *


##
# Minions

# TOY_604: Boom Wrench (3费 3/3)
# 微缩。亡语：触发另一个随机友方随从的亡语
class TOY_604:
    """Boom Wrench"""

    deathrattle = Deathrattle(RANDOM(FRIENDLY_MINIONS))
