from ..utils import *


##
# Minions

# TOY_811: Tigress Plushy (5费 5/5)
# 微缩。突袭、吸血、圣盾
class TOY_811:
    """Tigress Plushy"""

    tags = {
        GameTag.RUSH: True,
        GameTag.LIFESTEAL: True,
        GameTag.DIVINE_SHIELD: True,
    }


# TOY_813: Toy Captain Tarim (6费 3/7 嘲讽)
# 微缩。嘲讽。战吼：将所有其他随从的攻击力和生命值设为3/3
class TOY_813:
    """Toy Captain Tarim"""

    tags = {GameTag.TAUNT: True}

    requirements = {
        PlayReq.REQ_MINIMUM_TOTAL_MINIONS: 1,
    }

    play = Buff(ALL_MINIONS - SELF, "TOY_813e")


class TOY_813e:
    atk = SET(3)
    max_health = SET(3)
