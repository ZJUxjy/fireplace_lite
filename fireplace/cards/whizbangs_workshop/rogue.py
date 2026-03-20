from ..utils import *


##
# Minions

# TOY_521: Sandbox Scoundrel (5费 4/5)
# 微缩。战吼：你本回合打出的下一张牌费用降低2（简化：手牌所有牌费用-2本回合）
class TOY_521:
    """Sandbox Scoundrel"""

    play = Buff(FRIENDLY_HAND, "TOY_521e")


@custom_card
class TOY_521e:
    tags = {
        GameTag.CARDNAME: "Sandbox Scoundrel Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -2,
        GameTag.TAG_ONE_TURN_EFFECT: True,
    }

    events = REMOVED_IN_PLAY
