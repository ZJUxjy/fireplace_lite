from ..utils import *


##
# TTN_960: Sargeras, the Destroyer (9费 6/12 恶魔)
# 泰坦。战吼：打开一道传送门，每回合召唤两个3/2的小鬼

class TTN_960:
    """Sargeras, the Destroyer"""

    tags = {GameTag.ELITE: True, GameTag.CARDRACE: Race.DEMON}

    play = Summon(CONTROLLER, "TTN_960t")

    titan_abilities = ["TTN_960t2", "TTN_960t3", "TTN_960t4"]


class TTN_960_SummonPortalDemons(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, portal):
        enhanced = any(buff.id == "TTN_960t4e2" for buff in portal.buffs)
        actions = []
        for _ in range(2):
            summon = Summon(portal.controller, "TTN_960t6")
            if enhanced:
                summon = summon.then(Buff(Summon.CARD, "TTN_960t4e"))
            actions.append(summon)
        return source.game.queue_actions(source, actions)


# TTN_960t: The Twisting Nether (portal location)
class TTN_960t:
    """The Twisting Nether"""

    events = OWN_TURN_END.on(TTN_960_SummonPortalDemons(SELF))


# TTN_960t6: Felblaze Imp (3/2 Demon)
class TTN_960t6:
    """Nether Demon"""

    tags = {GameTag.CARDRACE: Race.DEMON}


# TTN_960t2: To the Void! - Send all other minions into the Twisting Nether
class TTN_960t2:
    """To the Void!"""

    play = Destroy(ALL_MINIONS - SELF)


# TTN_960t3: Inferno! - Summon two 6/6 Infernals
class TTN_960t3:
    """Inferno!"""

    play = Summon(CONTROLLER, "TTN_960t5") * 2


# TTN_960t4: Legion Invasion! - Your future Demons get +2 Health and Taunt
@custom_card
class TTN_960t4e:
    tags = {
        GameTag.CARDNAME: "Fel Fueled",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.HEALTH: 2,
        GameTag.TAUNT: True,
    }


@custom_card
class TTN_960t4e2:
    tags = {
        GameTag.CARDNAME: "Fel Fueled",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


class TTN_960t4:
    """Legion Invasion!"""

    play = Buff(FRIENDLY + ID("TTN_960t"), "TTN_960t4e2")


# TTN_960t5: Felblaze Infernal (6/6 Demon)
class TTN_960t5:
    """Felblaze Infernal"""

    tags = {GameTag.CARDRACE: Race.DEMON}
