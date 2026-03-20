from ..utils import *


##
# TTN_092: Aggramar, the Avenger (6费 3/7)
# 泰坦。战吼：装备一把3/3的泰沙拉克

class TTN_092:
    """Aggramar, the Avenger"""

    tags = {GameTag.ELITE: True}

    play = Summon(CONTROLLER, "TTN_092t")

    titan_abilities = ["TTN_092t1", "TTN_092t2", "TTN_092t3"]


# TTN_092t: Taeshalach (3费 3/3 武器)
class TTN_092t:
    """Taeshalach"""

    pass


# TTN_092t1: Maintain Order - Give weapon "After hero attacks, draw a card"
class TTN_092t1:
    """Maintain Order"""

    # 简化：立即抽一张牌
    play = Draw(CONTROLLER)


# TTN_092t2: Commanding Presence - Give weapon "After hero attacks, summon 3/3 Enforcer"
class TTN_092t2:
    """Commanding Presence"""

    # 简化：立即召唤一个3/3强制执行者
    play = Summon(CONTROLLER, "TTN_092e2t")


# TTN_092e2t: Vry'kul Enforcer (3/3 随从)
class TTN_092e2t:
    """Vry'kul Enforcer"""

    pass


# TTN_092t3: Swift Slash - Give weapon +2 attack and immune while attacking
class TTN_092t3:
    """Swift Slash"""

    # 简化：给武器+2攻击力
    play = Buff(FRIENDLY_WEAPON, "TTN_092t3e")


TTN_092t3e = buff(+2, 0)
