"""WONDERS — Shaman."""
from ..utils import *


class WON_086:
    """Call in the Finishers — Summon four 1/1 Murlocs."""
    # Use an existing 1/1 Murloc token. CFM_065 (Finja's first finisher).
    play = Summon(CONTROLLER, "CFM_065t") * 4


class WON_320:
    """Healing Wave — Restore 8 Health. (Joust bonus simplified out.)"""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Heal(TARGET, 8)


class WON_081:
    """Tuskarr Totemic — Battlecry: Summon a random basic Totem."""
    play = Summon(CONTROLLER, RandomEntourage())
    entourage = BASIC_TOTEMS


class WON_082:
    """Jade Lightning — Deal 3 damage. Summon a Jade Golem."""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3), SummonJadeGolem(CONTROLLER)


class WON_083:
    """Wicked Witchdoctor — Whenever you cast a spell, summon a random basic Totem."""
    events = OWN_SPELL_PLAY.on(Summon(CONTROLLER, RandomEntourage()))
    entourage = BASIC_TOTEMS


class WON_084:
    """Jade Chieftain — Battlecry: Summon a Jade Golem. Give it Taunt."""
    play = SummonJadeGolem(CONTROLLER).then(
        SetTags(SummonJadeGolem.CARD, {GameTag.TAUNT: True})
    )


class WON_085:
    """Thunder Bluff Valiant — Battlecry and Inspire: Give your Totems +2 Attack.

    Inspire portion skipped; battlecry buffs once.
    """
    play = Buff(FRIENDLY_MINIONS + TOTEM, "WON_085e")


class WON_085e:
    tags = {GameTag.ATK: 2}


class WON_321:
    """Charged Hammer — Deathrattle: Your Hero Power becomes 'Deal 2 damage.'

    Hero-power morph not modeled — placeholder no-op.
    """
    pass


class WON_091:
    """Totally Totems — Summon all FIVE basic Totems. Overload: (1)."""
    play = [Summon(CONTROLLER, t) for t in BASIC_TOTEMS]
