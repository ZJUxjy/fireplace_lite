from ..utils import *


##
# Minions

# TOY_375: Sleet Skater (3费 3/4)
# 微缩。战吼：冻结一个敌方随从
class TOY_375:
    """Sleet Skater"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Freeze(TARGET)
