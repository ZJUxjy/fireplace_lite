from ..utils import *


##
# TTN_721: V-07-TR-0N Prime (6费 3/5 机械)
# 泰坦。本随从的技能会在另一个随机友方随从身上重复（简化：不实现复制效果）

class TTN_721:
    """V-07-TR-0N Prime"""

    tags = {GameTag.ELITE: True, GameTag.CARDRACE: Race.MECHANICAL}

    titan_abilities = ["TTN_721t", "TTN_721t1", "TTN_721t2"]


# TTN_721t: Attach the Cannons! - Gain +2/+1. Deal 4 damage to a random enemy.
class TTN_721t:
    """Attach the Cannons!"""

    play = (
        Buff(SELF, "TTN_721te"),
        Hit(RANDOM(ENEMY_MINIONS | ENEMY_HERO), 4),
    )


TTN_721te = buff(+2, +1)


# TTN_721t1: Maximize Defenses! - Gain +3 health and Elusive
class TTN_721t1:
    """Maximize Defenses!"""

    play = (
        Buff(SELF, "TTN_721t1e"),
        SetTags(SELF, {GameTag.ELUSIVE: True}),
    )


TTN_721t1e = buff(0, +3)


# TTN_721t2: (third ability - deal damage to all enemies)
class TTN_721t2:
    """Maximize Defenses! Mk II"""

    # 简化：对所有敌方随从造成2点伤害
    play = Hit(ENEMY_MINIONS, 2)
