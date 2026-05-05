from ..utils import *


class DINO_410:
    """Khelos' Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_410t2")


class DINO_410t2:
    """Khelos' Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_410t3")


class DINO_410t3:
    """Khelos' Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_410t4")


class DINO_410t4:
    """Khelos' Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_410t5")


class DINO_410t5:
    """Khelos' Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_410t")


class DINO_411:
    """Sacred Eggbearer"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + MINION + (ATK == 0)))


class DINO_419:
    """Fodder Helper"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_TARGET_WITH_RACE: Race.BEAST,
    }
    play = Buff(TARGET, "DINO_419e"), GiveRush(TARGET)


DINO_419e = buff(2, 2)


class TLC_101:
    """Undercover Cultist"""

    enrage = Refresh(SELF, buff="TLC_101e")


TLC_101e = buff(atk=3)


class TLC_244:
    """Curious Explorer"""

    deathrattle = Buff(RANDOM(ENEMY_HAND + MINION), "TLC_244e")


@custom_card
class TLC_244e:
    tags = {
        GameTag.CARDNAME: "Explored",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -2,
    }


class TLC_249:
    """Blazing Accretion"""

    deathrattle = Hit(RANDOM_ENEMY_CHARACTER, 1) * 2


class TLC_468:
    """Blob of Tar"""

    deathrattle = Summon(CONTROLLER, "TLC_468t1"), Summon(CONTROLLER, "TLC_468t2")


class TLC_468t1:
    """Thin Blob"""

    pass


class TLC_468t2:
    """Thick Blob"""

    pass


class TLC_621:
    """Stubborn Guardian"""

    deathrattle = Mill(CONTROLLER) * 3
