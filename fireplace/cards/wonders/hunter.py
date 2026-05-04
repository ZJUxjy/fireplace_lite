"""WONDERS — Hunter."""
from ..utils import *


class WON_018:
    """Snipe — Secret: After your opponent plays a minion, deal 6 damage to it."""
    secret = Play(OPPONENT, MINION).after(Reveal(SELF), Hit(Play.CARD, 6))


class WON_021:
    """Ball of Spiders — Summon three 1/1 Webspinners."""
    play = Summon(CONTROLLER, "FP1_011") * 3


class WON_023:
    """Lock and Load — Each time you cast a spell this turn, get a random Hunter card."""
    # Simplified: skip "this turn" duration; treat as a one-shot give.
    play = Give(CONTROLLER, RandomCard(card_class=CardClass.HUNTER))


class WON_025:
    """Dreadscale — At the end of your turn, deal 1 damage to all enemies."""
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 1))


class WON_028:
    """Trial of the Jormungars — Summon copies of two Beasts in your deck that cost (3) or less."""
    play = Summon(CONTROLLER, ExactCopy(
        RANDOM(FRIENDLY_DECK + MINION + BEAST + (COST <= 3))
    )) * 2


class WON_307:
    """Shaky Zipgunner — Deathrattle: Give a random minion in your hand +2/+2."""
    deathrattle = Buff(RANDOM(FRIENDLY_HAND + MINION), "WON_307e")


class WON_307e:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class WON_306:
    """Cobra Shot — Deal 3 damage to a minion and the enemy hero."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 3), Hit(ENEMY_HERO, 3)


class WON_347:
    """Smuggler's Crate — Give a random Beast in your hand +2/+2."""
    play = Buff(RANDOM(FRIENDLY_HAND + MINION + BEAST), "WON_347e")


class WON_347e:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class WON_022:
    """Explorer's Hat — Give a minion +1/+1 and 'Deathrattle: Get an Explorer's Hat.'"""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "WON_022e")


class WON_022e:
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1, GameTag.DEATHRATTLE: True}
    deathrattle = Give(CONTROLLER, "WON_022")


class WON_024:
    """Acidmaw — Whenever an enemy minion takes damage, destroy it."""
    events = Damage(ENEMY_MINIONS).on(Destroy(Damage.TARGET))


class WON_027:
    """Time-Lost Raptor — Echo. Battlecry: Adapt your Time-Lost Raptors.

    Echo and Adapt aren't natively modeled here — the Echo tag from XML
    handles cost-on-cast, Adapt requires a discover-from-pool engine bit
    we don't ship. Treat as a no-op battlecry; the minion still functions
    as a 2/2 with whatever XML tags ship.
    """
    pass
