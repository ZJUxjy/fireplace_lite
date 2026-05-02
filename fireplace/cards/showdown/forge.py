from hearthstone.enums import SpellSchool
from ..utils import *


##
# FORGE (Showdown in Badlands). A card in hand can be Forged for 2 mana to
# upgrade it into its forged form (linked via the FORGES_INTO data tag).
# Engine support: PlayableCard.is_forgeable + .forge() — see actions.Forge.
# Card scripts only need to define the forged form's behavior.


# DEEP_024 — Glowstone Gyreworm (4-cost minion).
# Lifesteal. Quickdraw: Deal 5 damage. Forge: Change Quickdraw to Battlecry.
# Forged form (DEEP_024t) deals 5 damage as Battlecry.
class DEEP_024t:
    """Glowstone Gyreworm (Forged)"""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 5)


# TTN_039 — Watcher of the Sun (2-cost 2/3 minion).
# Battlecry: Get a random Holy spell. Forge: Also restore 6 Health to your hero.
class TTN_039t:
    """Watcher of the Sun (Forged)"""
    play = (
        Give(CONTROLLER, RandomSpell(spell_school=SpellSchool.HOLY)),
        Heal(FRIENDLY_HERO, 6),
    )


# TTN_042 — Cyclopian Crusher (3-cost 3/2 minion).
# Rush. Forge: Gain +3/+2.
class TTN_042t:
    """Cyclopian Crusher (Forged)"""
    tags = {GameTag.RUSH: True}


# TTN_457 — Eulogizer (3-cost 3/4 minion, DK).
# Battlecry: Spend 3 Corpses to deal 3 damage. Forge: Gain them instead.
# Corpses aren't implemented; simplified to: Forge form does no damage and
# gains +3 stats representing "gaining the 3 corpses worth of value".
class TTN_457:
    """Eulogizer"""
    play = Hit(RANDOM_ENEMY_CHARACTER, 3)


class TTN_457t:
    """Eulogizer (Forged)"""
    play = Buff(SELF, "TTN_457te")


TTN_457te = buff(atk=3, health=3)


# TTN_477 — Molten Rune (3-cost spell, mage).
# Deal 3 damage. Get a random spell. Forge: This casts twice.
class TTN_477:
    """Molten Rune"""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3), Give(CONTROLLER, RandomSpell())


class TTN_477t:
    """Molten Rune (Forged)"""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = (
        Hit(TARGET, 3),
        Give(CONTROLLER, RandomSpell()),
        Hit(TARGET, 3),
        Give(CONTROLLER, RandomSpell()),
    )
