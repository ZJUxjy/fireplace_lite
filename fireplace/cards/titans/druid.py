from ..utils import *


##
# TTN_903: Eonar, the Life-Binder (10费 5/7)
# 泰坦。使用技能后，召唤一个5/5嘲讽古树

class TTN_903:
    """Eonar, the Life-Binder"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_903t", "TTN_903t2", "TTN_903t3"]
    ability_used = Summon(CONTROLLER, "TTN_903t4")


# TTN_903t: Spontaneous Growth - Draw cards until hand is full
class TTN_903t:
    """Spontaneous Growth"""

    play = Draw(CONTROLLER) * 10  # draws until hand full (game caps at max)


# TTN_903t2: Bountiful Harvest - Restore hero to full health
class TTN_903t2:
    """Bountiful Harvest"""

    play = Heal(FRIENDLY_HERO, 30)


# TTN_903t3: Flourish - Refresh all mana crystals
class TTN_903t3:
    """Flourish"""

    play = FillMana(CONTROLLER, 10)


# TTN_903t4: Timeless Ancient (5费 5/5 嘲讽)
class TTN_903t4:
    """Timeless Ancient"""

    tags = {GameTag.TAUNT: True}
