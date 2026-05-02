from ..utils import *


##
# SPELLBURST (originally Scholomance Academy, returns in The Great Dark Beyond).
# A passive ability that triggers exactly once when the controller casts a
# spell, then is consumed. Engine support: see actions.Play.do — when a
# CONTROLLER plays a spell, each friendly minion with an unconsumed
# `spellburst` script fires it and is marked consumed.


# GDB_106 — Guiding Figure (2-cost 3/2 minion).
# Spellburst: Trigger a random friendly minion's Deathrattle.
class GDB_106:
    """Guiding Figure"""
    spellburst = Deathrattle(RANDOM(FRIENDLY_MINIONS + DEATHRATTLE))


# GDB_310 — Ethereal Oracle (3-cost 2/3 minion).
# Spell Damage +1. Spellburst: Draw 2 spells.
class GDB_310:
    """Ethereal Oracle"""
    tags = {GameTag.SPELLPOWER: 1}
    spellburst = ForceDraw(RANDOM(FRIENDLY_DECK + SPELL)), ForceDraw(RANDOM(FRIENDLY_DECK + SPELL))


# GDB_134 — Arkwing Pilot (6-cost 4/3 minion).
# At the end of your turn, deal 3 damage to a random enemy.
# Spellburst: Summon an Arkwing Pilot.
class GDB_134:
    """Arkwing Pilot"""
    events = OWN_TURN_END.on(Hit(RANDOM_ENEMY_CHARACTER, 3))
    spellburst = Summon(CONTROLLER, "GDB_134")


# GDB_104 — Felfire Thrusters (3-cost 2/4 minion, Starship Piece).
# Spellburst: Deal this minion's Attack damage to 2 random enemy minions.
class GDB_104:
    """Felfire Thrusters"""
    spellburst = Hit(RANDOM_ENEMY_MINION, ATK(SELF)), Hit(RANDOM_ENEMY_MINION, ATK(SELF))


# GDB_127 — K'ara, the Dark Star (3-cost 3/3 minion).
# Spellburst: Steal 2 Health from a random enemy.
# (Shadow spells don't remove this Spellburst — simplified to default behavior.)
class GDB_127:
    """K'ara, the Dark Star"""
    spellburst = Hit(RANDOM_ENEMY_CHARACTER, 2), Heal(FRIENDLY_HERO, 2)
