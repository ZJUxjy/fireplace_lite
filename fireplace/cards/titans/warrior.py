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


class TTN_092_AddWeaponEvent(TargetedAction):
    TARGET = ActionArg()
    EVENT = ActionArg()

    def do(self, source, player, event):
        weapon = player.weapon
        if weapon:
            weapon._events.append(event)


# TTN_092t1: Maintain Order - Give weapon "After hero attacks, draw a card"
class TTN_092t1:
    """Maintain Order"""

    play = TTN_092_AddWeaponEvent(CONTROLLER, Attack(FRIENDLY_HERO).after(Draw(CONTROLLER)))


# TTN_092t2: Commanding Presence - Give weapon "After hero attacks, summon 3/3 Enforcer"
class TTN_092t2:
    """Commanding Presence"""

    play = TTN_092_AddWeaponEvent(
        CONTROLLER,
        Attack(FRIENDLY_HERO).after(Summon(CONTROLLER, "TTN_092e2t")),
    )


# TTN_092e2t: Vry'kul Enforcer (3/3 随从)
class TTN_092e2t:
    """Vry'kul Enforcer"""

    pass


# TTN_092t3: Swift Slash - Give weapon +2 attack and immune while attacking
class TTN_092t3:
    """Swift Slash"""

    play = Buff(FRIENDLY_WEAPON, "TTN_092t3e"), Buff(FRIENDLY_HERO, "TTN_092t3e2")


@custom_card
class TTN_092t3e:
    tags = {
        GameTag.CARDNAME: "Swift Slash",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 2,
    }


@custom_card
class TTN_092t3e2:
    tags = {
        GameTag.CARDNAME: "Swift Slash",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.IMMUNE_WHILE_ATTACKING: True,
    }
