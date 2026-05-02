from ..utils import *


##
# STARSHIP / STARSHIP_PIECE (The Great Dark Beyond, Space). STARSHIP_PIECE
# minions attach to the player's starship when played; "starship" cards
# (e.g. The Exodar) launch the assembled pieces. Engine support:
# - Player.starship_pieces tracks attached pieces
# - Player.is_building_starship is the predicate "if you're building a Starship"
# - actions.Play.do appends STARSHIP_PIECE plays to starship_pieces
# - actions.LaunchStarship re-fires each piece's battlecry as a launch effect


# GDB_100 — Arkonite Defense Crystal (4-cost 0/4 minion).
# Taunt. Deathrattle: Gain 4 Armor. Starship Piece.
class GDB_100:
    """Arkonite Defense Crystal"""
    tags = {GameTag.TAUNT: True}
    deathrattle = GainArmor(FRIENDLY_HERO, 4)


# GDB_101 — Dimensional Core (2-cost 1/3 minion).
# Divine Shield. Starship Piece.
class GDB_101:
    """Dimensional Core"""
    tags = {GameTag.DIVINE_SHIELD: True}


# GDB_105 — Shattershard Turret (3-cost 4/3 minion).
# Rush, Windfury. Starship Piece.
class GDB_105:
    """Shattershard Turret"""
    tags = {GameTag.RUSH: True, GameTag.WINDFURY: True}


# GDB_120 — The Exodar (7-cost spell, Paladin).
# Battlecry: If you're building a Starship, launch it.
# (Choose-a-Protocol simplified — just launches.)
class GDB_120:
    """The Exodar"""

    @staticmethod
    def play(self):
        if self.controller.is_building_starship:
            return [LaunchStarship(CONTROLLER)]
        return []


# GDB_130 — Crystal Welder (2-cost 2/2 minion).
# Taunt. Battlecry: If you're building a Starship, gain +2/+2.
class GDB_130:
    """Crystal Welder"""
    tags = {GameTag.TAUNT: True}

    @staticmethod
    def play(self):
        if self.controller.is_building_starship:
            return [Buff(SELF, "GDB_130e")]
        return []


GDB_130e = buff(atk=2, health=2)
