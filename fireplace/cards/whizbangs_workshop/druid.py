from ..utils import *


##
# Minions

# TOY_801: Chia Drake (4费 3/5 龙)
# 微缩。抉择 - 获得+1法术伤害；或抽一张法术牌
class TOY_801:
    """Chia Drake"""

    miniaturize_mini = "TOY_801t"

    choose = ("TOY_801a", "TOY_801b")
    play = ChooseBoth(CONTROLLER) & (Buff(SELF, "TOY_801e"), ForceDraw(RANDOM(FRIENDLY_DECK + SPELL)))


class TOY_801a:
    """Mana Growth"""

    play = Buff(SELF, "TOY_801e")


class TOY_801b:
    """Botanical Studies"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + SPELL))


TOY_801e = buff(spellpower=1)
