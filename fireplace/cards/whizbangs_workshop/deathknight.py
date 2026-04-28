from ..utils import *


##
# Minions

# TOY_828: Amateur Puppeteer (5费 3/4)
# 微缩。嘲讽。亡语：给你手牌中的不死随从+2/+2
class TOY_828:
    """Amateur Puppeteer"""

    tags = {GameTag.TAUNT: True}

    deathrattle = Buff(FRIENDLY_HAND + UNDEAD, "TOY_828e")


@custom_card
class TOY_828e:
    tags = {
        GameTag.CARDNAME: "Amateur Puppeteer Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 2,
        GameTag.HEALTH: 2,
    }
