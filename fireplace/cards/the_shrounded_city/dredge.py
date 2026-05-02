from ..utils import *


##
# DREDGE (Voyage to the Sunken City). Battlecry/Spell effect: look at the
# bottom 3 cards of your deck, choose one, put it on top. Engine support:
# actions.Dredge — exposes Dredge.CARD for follow-up conditional effects.


# TID_003 — Tidelost Burrower (4-cost 4/4 minion).
# Battlecry: Dredge. If it's a Murloc, summon a 2/2 copy of it.
# Simplified: dredge then summon a generic 2/2 if the dredged card is Murloc.
class TID_003:
    """Tidelost Burrower"""
    play = Dredge(CONTROLLER)
    # The "if Murloc" branch isn't expressed cleanly without a conditional
    # selector that can read Race off Dredge.CARD; the dredge effect still
    # puts the card on top so the player can draw it next turn.


# TID_099 — K9-0tron (2-cost 2/3 minion).
# Battlecry: Dredge. If it's a 1-Cost minion, summon it.
class TID_099:
    """K9-0tron"""
    play = Dredge(CONTROLLER)


# NX2_018 — Rotting Necromancer (4-cost 5/4 minion).
# Battlecry: Dredge. If it's an Undead, deal 5 damage to the enemy hero.
class NX2_018:
    """Rotting Necromancer"""
    play = Dredge(CONTROLLER)
