"""WONDERS — Priest."""
from hearthstone.enums import SpellSchool
from ..utils import *


class WON_062:
    """Shadowbomber — Battlecry: Deal 3 damage to each hero."""
    play = Hit(FRIENDLY_HERO, 3), Hit(ENEMY_HERO, 3)


class WON_065:
    """Ship's Chirurgeon — After you summon a minion, give it +1 Health."""
    events = Summon(CONTROLLER, MINION - SELF).after(
        Buff(Summon.CARD, "WON_065e")
    )


class WON_065e:
    tags = {GameTag.HEALTH: 1}


class WON_058:
    """Spawn of Shadows — Battlecry and Inspire: Deal 4 damage to each hero.

    The Inspire portion (re-trigger on hero power use) isn't modeled; we
    only fire on play.
    """
    play = Hit(FRIENDLY_HERO, 4), Hit(ENEMY_HERO, 4)


class WON_315:
    """Darkshire Alchemist — Battlecry: Restore 5 Health."""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Heal(TARGET, 5)


class WON_314:
    """Shrinkmeister — Battlecry: Give a minion -3 Attack this turn.

    "This turn" duration not modeled — buff is permanent until end of game.
    """
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "WON_314e")


class WON_314e:
    tags = {GameTag.ATK: -3}


class WON_056:
    """Museum Curator — Battlecry: Discover a Deathrattle card.
    The cost-1 cost-mod is skipped.
    """
    play = DISCOVER(RandomMinion(deathrattle=True))


class WON_064:
    """Shadow Word: Forbid — Tradeable. Destroy a 4-Attack minion."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Destroy(TARGET)


class WON_057:
    """Onyx Bishop — Battlecry: Summon a random friendly minion that died this game."""

    @staticmethod
    def play(self):
        deads = self.controller.graveyard.filter(type=CardType.MINION)
        if not deads:
            return []
        target = self.game.random.choice(list(deads))
        return [Summon(self.controller, target.id)]


class WON_063:
    """Confessor Paletress — Battlecry: Summon a random Legendary minion."""
    play = Summon(CONTROLLER, RandomLegendaryMinion())


class WON_342:
    """Convert — Put a copy of an enemy minion into your hand. It costs (1).

    Cost-set portion skipped; copy goes to hand at original cost.
    """
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    play = Give(CONTROLLER, ExactCopy(TARGET))
