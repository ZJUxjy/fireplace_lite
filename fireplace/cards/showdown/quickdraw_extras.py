from ..utils import *


##
# Additional QUICKDRAW cards (Showdown in the Badlands + Voyage to the
# Sunken City). Some effects are simplified where they require mechanics
# (Excavate, in-hand cost mods) not implemented elsewhere.


# DEEP_024 — Glowstone Gyreworm (4-cost minion).
# Lifesteal. Quickdraw: Deal 5 damage. (Forge effect skipped — not impl.)
class DEEP_024:
    """Glowstone Gyreworm"""

    play_quickdraw_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    quickdraw = Hit(TARGET, 5)


# WW_325 — Dehydrate (3-cost spell). Lifesteal. Deal 4 to a minion.
# Quickdraw: Costs (1). (Cost reduction skipped — same damage either way.)
class WW_325:
    """Dehydrate"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = Hit(TARGET, 4)


# WW_348 — Misfire (2-cost spell). Deal 3, 2, and 1 damage to random minions.
# Quickdraw: Choose the targets. (Quickdraw choose-targeting simplified to
# the same random distribution.)
class WW_348:
    """Misfire"""

    play = Hit(RANDOM_MINION, 3), Hit(RANDOM_MINION, 2), Hit(RANDOM_MINION, 1)


# WW_358 — Farm Hand (3-cost minion). Battlecry: Discover an Undead.
# Quickdraw: It costs (2) less. (Cost reduction skipped.)
class WW_358:
    """Farm Hand"""

    play = DISCOVER(RandomMinion(race=Race.UNDEAD))


# WW_365 — Lay Down the Law (2-cost spell, tradeable).
# Set a minion's Attack and Health to 1. Quickdraw: Then deal 1 damage to it.
class WW_365:
    """Lay Down the Law"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = Buff(TARGET, "WW_365e")
    quickdraw = Hit(TARGET, 1)


class WW_365e:
    atk = SET(1)
    max_health = SET(1)


# WW_377 — Heat Wave (2-cost spell).
# Deal 2 damage to an enemy minion and its neighbors. Quickdraw: To all enemies.
class WW_377:
    """Heat Wave"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    play = Hit(TARGET_ADJACENT + TARGET, 2)
    quickdraw = Hit(ENEMY_CHARACTERS, 2)


# WW_384 — Benevolent Banker (3-cost minion).
# Battlecry: Discover a spell from your deck. Quickdraw: Enemy deck instead.
# (Simplified: always discover from your deck — implementing enemy-deck
# discovery requires a custom selector.)
class WW_384:
    """Benevolent Banker"""

    play = DISCOVER(RANDOM(FRIENDLY_DECK + SPELL))


# WW_417 — Drilly the Kid (4-cost minion).
# Battlecry, Quickdraw, and Deathrattle: Excavate a treasure.
# (Excavate not implemented — leave as vanilla minion for now.)


# WW_434 — Sunspot Dragon (6-cost minion).
# Tradeable, Lifesteal. Quickdraw: Deal 6 damage.
class WW_434:
    """Sunspot Dragon"""

    play_quickdraw_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    quickdraw = Hit(TARGET, 6)


# WW_436 — Trolley Problem (3-cost spell).
# Discard your lowest Cost spell. Summon two 3/3 Tram Cars with Rush.
# Quickdraw: Don't discard.
class WW_436:
    """Trolley Problem"""

    # Default behavior: discard then summon. Quickdraw skips the discard.
    play = (
        Discard(LOWEST_COST(FRIENDLY_HAND + SPELL)),
        Summon(CONTROLLER, "WW_436t") * 2,
    )
    quickdraw = Summon(CONTROLLER, "WW_436t") * 2


class WW_436t:
    """Tram Car"""
    tags = {GameTag.RUSH: True}


# WW_900 — Horseshoe Slinger (2-cost minion).
# Battlecry: Deal 2 damage to a random enemy minion.
# Quickdraw: And one of its neighbors. (Simplified: deal 2 to a 2nd random.)
class WW_900:
    """Horseshoe Slinger"""

    play = Hit(RANDOM_ENEMY_MINION, 2)
    quickdraw = Hit(RANDOM_ENEMY_MINION, 2)
