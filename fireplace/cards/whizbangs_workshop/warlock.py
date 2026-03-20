from ..utils import *


##
# Minions

# TOY_915: Tabletop Roleplayer (4费 2/5)
# 微缩。战吼：给一个友方恶魔+2攻击力，本回合免疫
class TOY_915:
    """Tabletop Roleplayer"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Buff(TARGET, "TOY_915e")


@custom_card
class TOY_915e:
    tags = {
        GameTag.CARDNAME: "Tabletop Roleplayer Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.TAG_ONE_TURN_EFFECT: True,
        GameTag.ATK: 2,
        GameTag.CANT_BE_DAMAGED: True,
        GameTag.CANT_BE_TARGETED_BY_OPPONENTS: True,
    }
