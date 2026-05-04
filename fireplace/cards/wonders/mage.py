"""WONDERS — Mage."""
from ..utils import *


class WON_031:
    """Mana Wyrm — Whenever you cast a spell, gain +1 Attack."""
    events = OWN_SPELL_PLAY.on(Buff(SELF, "WON_031e"))


class WON_031e:
    tags = {GameTag.ATK: 1}


class WON_037:
    """Cabalist's Tome — Get 3 random Mage spells."""
    play = Give(CONTROLLER, RandomSpell(card_class=CardClass.MAGE)) * 3


class WON_341:
    """Flame Lance — Deal 25 damage to a minion."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 25)


class WON_344:
    """Spellslinger — Battlecry: Both players get a random spell. Yours costs (2) less.

    Cost-modifying part skipped; both players just get a random spell.
    """
    play = Give(CONTROLLER, RandomSpell()), Give(OPPONENT, RandomSpell())


class WON_035:
    """Goblin Blastmage — Battlecry: If you control a Mech, deal 6 damage
    randomly split among enemies.
    """
    play = Find(FRIENDLY_MINIONS + MECH) & (
        Hit(RANDOM_ENEMY_CHARACTER, 1) * 6
    )


class WON_033:
    """Soot Spewer — Spell Damage +1. Battlecry: If you control another Mech,
    get a Spare Part. (Spare Parts not modeled — battlecry is a no-op.)
    """
    pass


class WON_036:
    """Servant of Yogg-Saron — Battlecry: Cast a random spell that costs (5)
    or more (targets chosen randomly).
    """
    play = CastSpell(RandomSpell(cost=[5, 6, 7, 8, 9, 10]))
