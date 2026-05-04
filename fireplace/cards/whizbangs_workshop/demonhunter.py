from ..utils import *


LOWEST_HEALTH = lambda sel: RANDOM(
    sel + (CURRENT_HEALTH == OpAttr(sel, "health", min))
)


##
# Minions


class MIS_710:
    """Sock Puppet Slitherspear"""

    update = Refresh(SELF, {GameTag.ATK: ATK(FRIENDLY_HERO)})


class MIS_911:
    """Gibbering Reject"""

    events = Attack(FRIENDLY_HERO).after(Summon(CONTROLLER, "MIS_911"))


class TOY_028:
    """Spirit of the Team"""

    tags = {GameTag.STEALTH: True}
    update = CurrentPlayer(CONTROLLER) & Refresh(FRIENDLY_HERO, {GameTag.ATK: +2})
    events = OWN_TURN_BEGIN.on(Unstealth(SELF))


class TOY_642:
    """Ball Hog"""

    tags = {GameTag.LIFESTEAL: True}
    play = deathrattle = Hit(LOWEST_HEALTH(ENEMY_CHARACTERS), 3)


class TOY_647:
    """Magtheridon, Unreleased"""

    tags = {GameTag.DORMANT: True}
    dormant_turns = 2
    dormant_events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 3))


# TOY_652: Window Shopper (5费 3/4)
# 微缩。战吼：发现一个恶魔（简化：不设置属性）
class TOY_652:
    """Window Shopper"""

    play = Discover(CONTROLLER, RandomMinion(race=Race.DEMON))


##
# Spells


class TOY_644:
    """Red Card"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = Dormant(TARGET, 2)


class TOY_645:
    """Lesser Opal Spellstone"""

    progress_total = 4
    play = Draw(CONTROLLER)
    reward = Morph(SELF, "TOY_645t")

    class Hand:
        events = Attack(FRIENDLY_HERO).after(AddProgress(SELF, Attack.ATTACKER))


class TOY_645t:
    """Opal Spellstone"""

    progress_total = 4
    play = Draw(CONTROLLER) * 2
    reward = Morph(SELF, "TOY_645t1")

    class Hand:
        events = Attack(FRIENDLY_HERO).after(AddProgress(SELF, Attack.ATTACKER))


class TOY_645t1:
    """Greater Opal Spellstone"""

    play = Draw(CONTROLLER) * 3


##
# Weapons


class TOY_641:
    """Umpire's Grasp"""

    deathrattle = ForceDraw(RANDOM(FRIENDLY_DECK + DEMON)).then(
        Buff(ForceDraw.TARGET, "TOY_641e")
    )


TOY_641e = buff(cost=-2)
