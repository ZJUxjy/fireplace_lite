from ..utils import *
from .patch_wog import *
from .patch_karazhan import *
from .patch_icc import *
from .patch_dalaran import *
from .patch_outlands import *
from .bonus_effects import *
from .core_extras import *


# Pre-nerf Warsong Commander for tests
@custom_card
class FIREPLACE_EX1_084:
    tags = {
        GameTag.CARDNAME: "Warsong Commander (Old)",
        GameTag.CARDTYPE: CardType.MINION,
        GameTag.CLASS: CardClass.WARRIOR,
        GameTag.COST: 3,
        GameTag.ATK: 2,
        GameTag.HEALTH: 3,
    }
    events = Summon(CONTROLLER, MINION + (ATK <= 3)).after(
        Buff(Summon.CARD, "FIREPLACE_EX1_084e")
    )


@custom_card
class FIREPLACE_EX1_084e:
    tags = {
        GameTag.CARDNAME: "Charge (Old)",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.CHARGE: True,
    }


# Python-only enchantments referenced by core_extras.py fill-ins.
@custom_card
class RLK_707e_big:
    tags = {
        GameTag.CARDNAME: "Mass Grave",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 3,
    }


@custom_card
class CORE_WON_350e:
    tags = {
        GameTag.CARDNAME: "Knew a Guy",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 1,
        GameTag.HEALTH: 2,
    }
