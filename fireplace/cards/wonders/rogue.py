"""WONDERS — Rogue."""
from ..utils import *


class WON_071:
    """Burgle — Get 3 random cards (from your opponent's class)."""
    play = Give(CONTROLLER, RandomCard(card_class=ENEMY_CLASS)) * 3


class WON_073:
    """Dark Iron Skulker — Battlecry: Deal 2 damage to all undamaged enemy minions."""
    play = Hit(ENEMY_MINIONS + (DAMAGE == 0), 2)


class WON_316:
    """Shado-Pan Rider — Combo: Gain +4 Attack."""
    combo = Buff(SELF, "WON_316e")


class WON_316e:
    tags = {GameTag.ATK: 4}


class WON_340:
    """Tomb Pillager — Deathrattle: Get a Coin."""
    deathrattle = Give(CONTROLLER, "GAME_005")


class WON_317:
    """Undercity Huckster — Deathrattle: Get a random card (from opponent's class)."""
    deathrattle = Give(CONTROLLER, RandomCard(card_class=ENEMY_CLASS))


class WON_067:
    """Jade Swarmer — Stealth. Deathrattle: Summon a Jade Golem."""
    tags = {GameTag.STEALTH: True}
    deathrattle = SummonJadeGolem(CONTROLLER)


class WON_070:
    """Jade Shuriken — Deal 3 damage. Combo: Summon a Jade Golem."""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3)
    combo = Hit(TARGET, 3), SummonJadeGolem(CONTROLLER)


class WON_335:
    """Reincarnate — Destroy a minion, then return it to life with full Health.

    NOTE: This card is class=Shaman in modern HS. WONDERS may have it under
    a different class internally; the script works regardless.
    """
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Destroy(TARGET).then(Summon(CONTROLLER, ExactCopy(Destroy.TARGET)))
