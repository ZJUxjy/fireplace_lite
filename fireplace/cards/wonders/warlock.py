"""WONDERS — Warlock."""
from ..utils import *


class WON_093:
    """Demonfuse — Give a Demon +3/+3."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_WITH_RACE: 15,  # DEMON
    }
    play = Buff(TARGET, "WON_093e")


class WON_093e:
    tags = {GameTag.ATK: 3, GameTag.HEALTH: 3}


class WON_095:
    """Darkbomb — Deal 3 damage to a character. (Conditional shadow draw skipped.)"""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3)


class WON_097:
    """Spreading Madness — Deal 13 damage randomly split among ALL characters."""
    play = Hit(RANDOM(ALL_CHARACTERS), 1) * 13


class WON_322:
    """Usher of Souls — Whenever a minion dies, give your C'Thun +1/+1."""
    events = Death(MINION).on(Buff(CTHUN, "OG_281e", atk=1, max_health=1))


class WON_323:
    """Bane of Doom — Deal 3 damage to a character. If it dies, summon a random Demon."""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3).then(
        Dead(Hit.TARGET) & Summon(CONTROLLER, RandomMinion(race=Race.DEMON))
    )


class WON_104:
    """Witch of the Arch-Thief — Battlecry: Summon a 1/3 Voidwalker with Taunt.
    (Conditional 'if opponent has fewer cards' skipped.)
    """
    play = Summon(CONTROLLER, "CS2_065")  # Voidwalker token


class WON_096:
    """Dark Peddler — Battlecry: Discover a 1-Cost card."""
    play = DISCOVER(RandomCollectible(cost=1))


class WON_100:
    """Dark Bargain — Destroy 2 random enemy minions. Discard 2 random cards."""
    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Destroy(RANDOM(ENEMY_MINIONS) * 2), Discard(RANDOM(FRIENDLY_HAND) * 2)


class WON_099:
    """Tiny Knight of Evil — Whenever you discard a card, gain +2/+1."""
    events = Discard(FRIENDLY_HAND).on(Buff(SELF, "WON_099e"))


class WON_099e:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 1}
