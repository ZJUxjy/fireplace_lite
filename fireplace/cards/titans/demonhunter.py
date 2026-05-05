from ..utils import *


class TTN_862_LeftOf(Selector):
    def eval(self, entities, source):
        if source.owner.zone != Zone.PLAY:
            return []
        field = source.owner.controller.field
        index = field.index(source.owner)
        return list(field[:index])


class TTN_862_RightOf(Selector):
    def eval(self, entities, source):
        if source.owner.zone != Zone.PLAY:
            return []
        field = source.owner.controller.field
        index = field.index(source.owner)
        return list(field[index + 1:])


##
# TTN_862: Argus, the Emerald Star (7费 5/9)
# 泰坦。本随从左边的随从均拥有突袭，右边的随从均拥有吸血

class TTN_862:
    """Argus, the Emerald Star"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_862t2", "TTN_862t3", "TTN_862t2"]
    update = (
        Refresh(SELF, buff="TTN_862e1"),
        Refresh(SELF, buff="TTN_862e2"),
    )


@custom_card
class TTN_862e1:
    tags = {
        GameTag.CARDNAME: "Argus, the Emerald Star",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    update = Refresh(TTN_862_LeftOf(), {GameTag.RUSH: True})


@custom_card
class TTN_862e2:
    tags = {
        GameTag.CARDNAME: "Argus, the Emerald Star",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    update = Refresh(TTN_862_RightOf(), {GameTag.LIFESTEAL: True})


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
