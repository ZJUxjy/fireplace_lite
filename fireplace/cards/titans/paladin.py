from ..utils import *


##
# TTN_858: Amitus, the Peacekeeper (7费 1/8 嘲讽)
# 泰坦。嘲讽。你的随从每次受到伤害不会超过2点（简化：不实现伤害上限）

class TTN_858:
    """Amitus, the Peacekeeper"""

    tags = {GameTag.ELITE: True, GameTag.TAUNT: True}

    # TTN_858t不在数据库中，使用已知的t2和t3（用t2再补一个作为第三技能）
    titan_abilities = ["TTN_858t2", "TTN_858t3", "TTN_858t2"]


# TTN_858t2: Empowered - Give your other minions +2/+2
class TTN_858t2:
    """Empowered"""

    play = Buff(FRIENDLY_MINIONS - SELF, "TTN_858t2e")


TTN_858t2e = buff(+2, +2)


# TTN_858t3: Pacified - Set all enemy minions' ATK and Health to 2
class TTN_858t3:
    """Pacified"""

    play = Buff(ENEMY_MINIONS, "TTN_858t3e")


class TTN_858t3e:
    atk = SET(2)
    max_health = SET(2)
