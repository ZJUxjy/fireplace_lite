from ..utils import *
from fireplace import enums


##
# Minions

# TOY_501: Shudderblock (6费 6/6)
# 微缩。战吼：你下一个战吼触发3次（简化：战吼触发额外一次，类似布兰）
class TOY_501:
    """Shudderblock"""

    update = Refresh(CONTROLLER, {enums.EXTRA_BATTLECRIES: True})


# TOY_513: Sand Art Elemental (4费 3/5 元素)
# 微缩。战吼：给你的英雄+1攻击力和风怒（本回合）
class TOY_513:
    """Sand Art Elemental"""

    play = Buff(FRIENDLY_HERO, "TOY_513e")


@custom_card
class TOY_513e:
    tags = {
        GameTag.CARDNAME: "Sand Art Elemental Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.TAG_ONE_TURN_EFFECT: True,
        GameTag.ATK: 1,
        GameTag.WINDFURY: True,
    }
