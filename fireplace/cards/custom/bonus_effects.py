from hearthstone.enums import GameTag, CardType
from ..utils import custom_card


##
# BONUS EFFECT pool (Cataclysm/Emerald Dream). Random keyword grants used
# by GiveBonusEffect. fireplace's bundled CardDefs lacks dedicated Bonus
# Effect tokens, so we register simple keyword enchantments here. Each
# grants exactly one keyword (matching the simplest "Bonus Effect" form
# from real Hearthstone — Battlegrounds-style single-keyword buffs).


@custom_card
class BONUS_EFFECT_TAUNT:
    tags = {
        GameTag.CARDNAME: "Bonus Effect: Taunt",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.TAUNT: True,
    }


@custom_card
class BONUS_EFFECT_DS:
    tags = {
        GameTag.CARDNAME: "Bonus Effect: Divine Shield",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.DIVINE_SHIELD: True,
    }


@custom_card
class BONUS_EFFECT_REBORN:
    tags = {
        GameTag.CARDNAME: "Bonus Effect: Reborn",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.REBORN: True,
    }


@custom_card
class BONUS_EFFECT_WF:
    tags = {
        GameTag.CARDNAME: "Bonus Effect: Windfury",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.WINDFURY: True,
    }


@custom_card
class BONUS_EFFECT_LIFESTEAL:
    tags = {
        GameTag.CARDNAME: "Bonus Effect: Lifesteal",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.LIFESTEAL: True,
    }


@custom_card
class BONUS_EFFECT_RUSH:
    tags = {
        GameTag.CARDNAME: "Bonus Effect: Rush",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.RUSH: True,
    }
