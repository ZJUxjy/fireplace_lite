from ..utils import *


##
# EXCAVATE (Showdown in Badlands). Each Excavate adds a random treasure from
# the current tier (1->4) to your hand and increments the player's
# excavate_count. Tier 1 = 1-cost trinket; tier 4 = Azerite legendary.
# Engine support: actions.Excavate (manages tier ladder + pool selection),
# Player.excavate_count tracks progress.


# WW_001 — Kobold Miner (2-cost 2/2 minion).
# Battlecry: Excavate a treasure.
class WW_001:
    """Kobold Miner"""
    play = Excavate(CONTROLLER)


# WW_002 — Burrow Buster (5-cost 4/3 minion).
# Rush. Battlecry: Excavate a treasure.
class WW_002:
    """Burrow Buster"""
    play = Excavate(CONTROLLER)


# DEEP_009 — Digging Straight Down (4-cost spell).
# Deal 8 damage to a minion. Excavate a treasure.
class DEEP_009:
    """Digging Straight Down"""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = Hit(TARGET, 8), Excavate(CONTROLLER)


# DEEP_018 — Shroomscavate (2-cost spell).
# Give a minion Divine Shield. Excavate a treasure.
class DEEP_018:
    """Shroomscavate"""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = SetTags(TARGET, {GameTag.DIVINE_SHIELD: True}), Excavate(CONTROLLER)


# DEEP_007 — Sir Finley, the Intrepid (3-cost 3/2 minion).
# Battlecry: If you've Excavated twice, transform all enemy minions into 1/1
# Murlocs. (Simplified: only fires when excavate_count >= 2 at play time.)
class DEEP_007:
    """Sir Finley, the Intrepid"""

    @staticmethod
    def play(self):
        if self.controller.excavate_count >= 2:
            return [Morph(ENEMY_MINIONS, RandomMinion(race=Race.MURLOC, cost=1))]
        return []
