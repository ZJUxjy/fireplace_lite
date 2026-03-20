from ..utils import *


##
# Minions

# TOY_351: Mystery Egg (2费 0/3)
# 微缩。亡语：随机获取一张野兽牌
class TOY_351:
    """Mystery Egg"""

    deathrattle = Give(CONTROLLER, RandomMinion(race=Race.BEAST))
