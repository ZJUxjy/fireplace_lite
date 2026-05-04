from ..utils import *


def _woodland_wonders_cost(entity, cost):
    if entity.controller.spellpower:
        return cost - 3
    return cost


##
# Minions


class MIS_300:
    """Snuggle Teddy"""

    play = Give(CONTROLLER, "MIS_300t")


class MIS_300t:
    """Snuggle Teddy"""


class MIS_301t:
    """Treant"""


class MIS_712:
    """Toyrantus"""

    play = (MANA(CONTROLLER) >= 10) & Buff(SELF, "MIS_712e")


MIS_712e = buff(+7, +7)


class TOY_804t:
    """Grove Beetle"""

    tags = {GameTag.TAUNT: True}


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


##
# Spells


class MIS_301:
    """Overgrown Beanstalk"""

    play = Summon(CONTROLLER, "MIS_301t").then(
        Draw(CONTROLLER) * Count(FRIENDLY_MINIONS + ID("MIS_301t"))
    )


class TOY_804:
    """Woodland Wonders"""

    play = Summon(CONTROLLER, "TOY_804t") * 2

    class Hand:
        update = Refresh(SELF, {GameTag.COST: _woodland_wonders_cost})


class TOY_805:
    """Ensmallen"""

    play = Buff(FRIENDLY_DECK + MINION, "TOY_805e"), Buff(
        FRIENDLY_DECK + MINION, "TOY_805e2"
    )


TOY_805e = buff(cost=-1)
TOY_805e2 = buff(atk=-1)


##
# Locations


class TOY_850:
    """Magical Dollhouse"""

    spellpower = 0
    activate = Buff(CONTROLLER, "TOY_850e")


@custom_card
class TOY_850e:
    tags = {
        GameTag.CARDNAME: "Magical Harvest",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    spellpower = lambda self, i: i + 1
    events = OWN_TURN_END.on(Destroy(SELF))
