from ..utils import *


##
# FRENZY (introduced in Forged in the Barrens). Triggers once when the minion
# takes damage for the first time, before death checks. The engine wires this
# automatically through the `frenzy` script slot in actions.Damage.do.


# BAR_020 — Razormane Raider (5-cost 5/6 minion).
# Frenzy: Attack a random enemy.
class BAR_020:
    """Razormane Raider"""
    frenzy = Attack(SELF, RANDOM_ENEMY_CHARACTER)


# BAR_022 — Peon (2-cost 2/3 minion).
# Frenzy: Add a random spell from your class to your hand.
class BAR_022:
    """Peon"""
    frenzy = Give(CONTROLLER, RandomSpell(card_class=Attr(FRIENDLY_HERO, GameTag.CLASS)))


# BAR_024 — Oasis Thrasher (2-cost 2/3 minion).
# Frenzy: Deal 3 damage to the enemy hero.
class BAR_024:
    """Oasis Thrasher"""
    frenzy = Hit(ENEMY_HERO, 3)


# BAR_025 — Sunwell Initiate (3-cost 3/4 minion).
# Frenzy: Gain Divine Shield.
class BAR_025:
    """Sunwell Initiate"""
    frenzy = SetTags(SELF, {GameTag.DIVINE_SHIELD: True})


# BAR_073 — Barrens Blacksmith (5-cost 3/5 minion).
# Frenzy: Give your other minions +2/+2.
class BAR_073:
    """Barrens Blacksmith"""
    frenzy = Buff(FRIENDLY_MINIONS - SELF, "BAR_073e")


BAR_073e = buff(atk=2, health=2)
