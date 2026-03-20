from ..utils import *


##
# TTN_862: Argus, the Emerald Star (7费 5/9)
# 泰坦。本随从左边的随从均拥有突袭，右边的随从均拥有吸血

class TTN_862:
    """Argus, the Emerald Star"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_862t2", "TTN_862t3", "TTN_862t2"]

    # 简化被动：进场时给左边突袭，右边吸血
    play = (
        SetTags(LEFT_OF(SELF), {GameTag.RUSH: True}),
        SetTags(RIGHT_OF(SELF), {GameTag.LIFESTEAL: True}),
    )

    # 持续光环（简化）：持续给左边突袭、右边吸血
    events = [
        OWN_TURN_BEGIN.on(SetTags(LEFT_OF(SELF), {GameTag.RUSH: True})),
        OWN_TURN_BEGIN.on(SetTags(RIGHT_OF(SELF), {GameTag.LIFESTEAL: True})),
    ]


# TTN_862t2: Show of Force - Reduce the cost of all minions in hand by 2
class TTN_862t2:
    """Show of Force"""

    play = Buff(FRIENDLY_HAND + MINION, "TTN_862t2e")


TTN_862t2e = buff(cost=-2)


# TTN_862t3: Argunite Army - Summon four 2/2 Elementals with Taunt
class TTN_862t3:
    """Argunite Army"""

    play = Summon(CONTROLLER, "TTN_862t3t") * 4


# TTN_862t3t: 阿古斯元素 (2费 2/2 嘲讽)
class TTN_862t3t:
    """Argunite"""

    tags = {GameTag.TAUNT: True, GameTag.CARDRACE: Race.ELEMENTAL}
