from ..utils import *


##
# TTN_960: Sargeras, the Destroyer (9费 6/12 恶魔)
# 泰坦。战吼：打开一道传送门，每回合召唤两个3/2的小鬼

class TTN_960:
    """Sargeras, the Destroyer"""

    tags = {GameTag.ELITE: True, GameTag.CARDRACE: Race.DEMON}

    play = Summon(CONTROLLER, "TTN_960t")

    titan_abilities = ["TTN_960t2", "TTN_960t3", "TTN_960t4"]


# TTN_960t: The Twisting Nether (portal location)
# 简化：在你的回合结束时召唤两个3/2小鬼
class TTN_960t:
    """The Twisting Nether"""

    events = OWN_TURN_END.on(Summon(CONTROLLER, "TTN_960t1") * 2)


# TTN_960t1: Demon from the Nether (3/2 恶魔)
class TTN_960t1:
    """Nether Demon"""

    tags = {GameTag.CARDRACE: Race.DEMON}


# TTN_960t2: To the Void! - Send all other minions into the Twisting Nether
class TTN_960t2:
    """To the Void!"""

    play = Destroy(ALL_MINIONS - SELF)


# TTN_960t3: Inferno! - Summon two 6/6 Infernals
class TTN_960t3:
    """Inferno!"""

    play = Summon(CONTROLLER, "EX1_301") * 2  # 狱火恶魔 Infernal token


# TTN_960t4: Legion Invasion! - Future demons get +2 health and Taunt (simplified)
class TTN_960t4:
    """Legion Invasion!"""

    # 简化：召唤两个3/4嘲讽恶魔
    play = Summon(CONTROLLER, "TTN_960t1") * 2, SetTags(FRIENDLY_MINIONS - TAUNT, {GameTag.TAUNT: True})
