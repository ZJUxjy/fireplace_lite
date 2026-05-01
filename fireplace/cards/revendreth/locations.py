from ..utils import *


##
# LOCATION cards (Murder at Castle Nathria)
#
# Locations are deployed for {N} mana, have HEALTH (durability), and can be
# Used once per turn for their `location_action` effect, then enter a 1-turn
# cooldown and lose 1 durability. At 0 durability they are destroyed.
#
# Card scripts use `location_requirements` (not `requirements`) for the use
# action, since `requirements` would be checked at placement.


class REV_290:
    """Cathedral of Atonement"""

    # 3-cost, 3-durability. Use: Give a minion +2/+1 and draw a card.
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    location_action = Buff(TARGET, "REV_290e"), Draw(CONTROLLER)


REV_290e = buff(atk=2, health=1)


class REV_602:
    """Nightcloak Sanctum"""

    # 3-cost, 3-durability. Use: Freeze a minion. Summon a 2/2 Volatile Skeleton.
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    location_action = (
        Freeze(TARGET),
        Summon(CONTROLLER, "REV_602t"),
    )


class REV_362:
    """Castle Kennels"""

    # 2-cost, 3-durability. Use: Give a friendly minion +2 Attack.
    # (Simplified: skip the Beast → Rush conditional bonus.)
    location_requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    location_action = Buff(TARGET, "REV_362e")


REV_362e = buff(atk=2)


class REV_371:
    """Vile Library"""

    # 2-cost, 2-durability. Use: Give a friendly minion +1/+1.
    # (Simplified: skip the "repeat per Imp" multiplier.)
    location_requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    location_action = Buff(TARGET, "REV_371e")


REV_371e = buff(atk=1, health=1)
