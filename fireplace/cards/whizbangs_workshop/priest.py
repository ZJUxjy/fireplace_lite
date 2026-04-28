from ..utils import *


##
# Minions

# TOY_380: Clay Matriarch (6费 3/7 龙)
# 微缩。嘲讽。亡语：召唤一个4/4有虚空的黏土幼龙
class TOY_380:
    """Clay Matriarch"""

    miniaturize_mini = "TOY_380t"

    tags = {GameTag.TAUNT: True}

    deathrattle = Summon(CONTROLLER, "TOY_380t2")


# TOY_380t2: Clay Whelp (4费 4/4 虚空)
class TOY_380t2:
    """Clay Whelp"""

    tags = {GameTag.ELUSIVE: True}
