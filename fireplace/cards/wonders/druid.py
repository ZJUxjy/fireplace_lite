"""WONDERS — Druid."""
from ..utils import *


class WON_009:
    """Addled Grizzly — After you summon a Beast, give it +1/+1."""
    events = Summon(CONTROLLER, MINION + BEAST - SELF).after(
        Buff(Summon.CARD, "WON_009e")
    )


class WON_009e:
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


class WON_300:
    """Virmen Sensei — Battlecry: Give a friendly Beast +3/+3."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_WITH_RACE: 20,  # BEAST
    }
    play = Buff(TARGET, "WON_300e")


class WON_300e:
    tags = {GameTag.ATK: 3, GameTag.HEALTH: 3}


class WON_305:
    """Menagerie Warden — Battlecry: Choose a friendly Beast. Summon a copy of it."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_WITH_RACE: 20,
    }
    play = Summon(CONTROLLER, ExactCopy(TARGET))


class WON_302:
    """Mire Keeper — Choose One: Summon a 2/2 Slime; or Gain an empty Mana Crystal."""
    choose = ("WON_302a", "WON_302b")
    play = Summon(CONTROLLER, "OG_202b")  # 2/2 Slime token (existing)


class WON_302a:
    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, "OG_202b")


class WON_302b:
    play = AT_MAX_MANA(CONTROLLER) | GainEmptyMana(CONTROLLER, 1)


class WON_303:
    """Jade Behemoth — Taunt. Battlecry: Summon a Jade Golem."""
    tags = {GameTag.TAUNT: True}
    play = SummonJadeGolem(CONTROLLER)


class WON_304:
    """Dark Arakkoa — Taunt. Battlecry: Give your C'Thun +4/+4."""
    tags = {GameTag.TAUNT: True}
    play = Buff(CTHUN, "OG_281e", atk=4, max_health=4)
