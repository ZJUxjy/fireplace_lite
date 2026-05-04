"""WONDERS — Paladin."""
from ..utils import *


class WON_311:
    """Keeper of Uldaman — Battlecry: Set a minion's Attack and Health to 3."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = SetTags(TARGET, {GameTag.ATK: 3, GameTag.HEALTH: 3})


class WON_309:
    """Silvermoon Portal — Give a minion +2/+2. Summon a random 2-Cost minion."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "WON_309e"), Summon(CONTROLLER, RandomMinion(cost=2))


class WON_309e:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class WON_310:
    """Steward of Darkshire — Whenever you summon a 1-Health minion, give it Divine Shield."""
    events = Summon(CONTROLLER, MINION + (CURRENT_HEALTH == 1)).on(
        SetTags(Summon.CARD, {GameTag.DIVINE_SHIELD: True})
    )


class WON_046:
    """Grimestreet Enforcer — At the end of your turn, give all minions in your hand +1/+1."""
    events = OWN_TURN_END.on(Buff(FRIENDLY_HAND + MINION, "WON_046e"))


class WON_046e:
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


class WON_048:
    """Lay on Hands — Restore 8 Health. Draw 3 cards."""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Heal(TARGET, 8), Draw(CONTROLLER) * 3


class WON_051:
    """Timeless Blessing — Give four random minions in your hand +4/+4, +3/+3, +2/+2, and +1/+1."""

    @staticmethod
    def play(self):
        # Pick up to 4 random hand minions; apply diminishing buffs.
        hand_minions = [c for c in self.controller.hand if c.type == CardType.MINION]
        if not hand_minions:
            return []
        rng = self.game.random
        picks = rng.sample(hand_minions, min(4, len(hand_minions)))
        actions = []
        for i, m in enumerate(picks):
            buff_id = "WON_051e_%d" % (4 - i)
            actions.append(Buff(m, buff_id))
        return actions


# Diminishing buff enchantments. Registered via @custom_card in custom/__init__.py
# so the engine can look them up by id.


class WON_311e:
    """Stat-set buff for Keeper of Uldaman (placeholder — SetTags handles it)."""
    pass


class WON_333:
    """A Light in the Darkness — Discover a Paladin minion. Give it +2/+2."""
    play = Discover(CONTROLLER, RandomMinion(card_class=CardClass.PALADIN)).then(
        Give(CONTROLLER, Discover.CARD), Buff(Discover.CARD, "WON_333e")
    )


class WON_333e:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class WON_049:
    """Enter the Coliseum — Destroy all minions except each player's highest-Attack."""
    play = Destroy(
        ALL_MINIONS - HIGHEST_ATK(FRIENDLY_MINIONS) - HIGHEST_ATK(ENEMY_MINIONS)
    )
