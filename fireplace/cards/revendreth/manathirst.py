from ..utils import *


##
# MANATHIRST (Murder at Castle Nathria — Onyxia's Lair mini-set; returns in
# multiple expansions). A bonus play effect that fires only when the
# controller's max mana meets the threshold. Engine support: actions.Play.do
# checks `card.data.scripts.manathirst_threshold` and queues the
# `manathirst` script if `player.max_mana >= threshold`.


# NX2_010 — Death Beetle (6-cost 6/6 minion).
# Taunt. Manathirst (8): Gain +4/+4 and Charge.
class NX2_010:
    """Death Beetle"""
    tags = {GameTag.TAUNT: True}
    manathirst_threshold = 8
    manathirst = (
        Buff(SELF, "NX2_010e"),
        SetTags(SELF, {GameTag.CHARGE: True}),
    )


NX2_010e = buff(atk=4, health=4)


# NX2_021 — Knight of the Dead (3-cost 5/5 minion).
# Battlecry: Deal 5 damage to your hero. Manathirst (7): Restore 5 Health to
# your hero instead.
class NX2_021:
    """Knight of the Dead"""
    play = Hit(FRIENDLY_HERO, 5)
    manathirst_threshold = 7
    # Net effect at >= 7 mana: heal back the 5 damage = no-op damage, +5 heal.
    manathirst = Heal(FRIENDLY_HERO, 10)


# RLK_209 — Unleash Fel (1-cost spell, DH).
# Deal 1 damage to all enemies. Manathirst (6): With Lifesteal.
# (Lifesteal-on-spell: heal hero by total damage dealt — simplified to the
# count of enemies hit.)
class RLK_209:
    """Unleash Fel"""
    play = Hit(ENEMY_CHARACTERS, 1)
    manathirst_threshold = 6
    manathirst = Heal(FRIENDLY_HERO, Count(ENEMY_CHARACTERS))


# RLK_219 — Sunfury Clergy (3-cost 2/4 minion, Priest).
# Battlecry: Restore 3 Health to all friendly characters.
# Manathirst (6): Restore 6 instead.
class RLK_219:
    """Sunfury Clergy"""
    play = Heal(FRIENDLY_CHARACTERS, 3)
    manathirst_threshold = 6
    # When threshold met: extra +3 healing on top of the 3 already healed.
    manathirst = Heal(FRIENDLY_CHARACTERS, 3)


# RLK_221 — Crystal Broker (3-cost 3/2 minion, DK).
# Manathirst (5): Summon a random 3-Cost minion.
# Manathirst (10): Summon an 8-Cost minion instead.
# Two manathirst tiers — engine supports a single threshold; we model the
# 5-cost tier in the threshold and bake the higher tier into the script via
# a runtime mana check.
class RLK_221:
    """Crystal Broker"""
    manathirst_threshold = 5

    @staticmethod
    def manathirst(self):
        # If max mana also clears the higher tier, summon 8-cost; otherwise 3.
        if self.controller.max_mana >= 10:
            return [Summon(CONTROLLER, RandomMinion(cost=8))]
        return [Summon(CONTROLLER, RandomMinion(cost=3))]
