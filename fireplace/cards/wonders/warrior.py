"""WONDERS — Warrior."""
from ..utils import *


class WON_338:
    """Axe Flinger — Whenever this minion takes damage, deal 2 damage to enemy hero."""
    events = SELF_DAMAGE.on(Hit(ENEMY_HERO, 2))


class WON_339:
    """Alley Armorsmith — Taunt. Whenever this minion deals damage, gain that much Armor."""
    tags = {GameTag.TAUNT: True}
    events = Damage(source=SELF).on(GainArmor(FRIENDLY_HERO, Damage.AMOUNT))


class WON_350:
    """I Know a Guy — Discover a Taunt minion. Give it +1/+2."""
    play = Discover(CONTROLLER, RandomMinion(taunt=True)).then(
        Give(CONTROLLER, Discover.CARD), Buff(Discover.CARD, "CORE_WON_350e")
    )


class WON_337:
    """Ironforge Portal — Gain 4 Armor. Summon a random 4-Cost minion."""
    play = GainArmor(FRIENDLY_HERO, 4), Summon(CONTROLLER, RandomMinion(cost=4))


class WON_110:
    """Stolen Goods — Draw a Taunt minion. Give it +2/+2."""
    play = ForceDraw(RANDOM(FRIENDLY_DECK + MINION + TAUNT)).then(
        Buff(ForceDraw.TARGET, "WON_110e")
    )


class WON_110e:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class WON_108:
    """Grimy Gadgeteer — At the end of your turn, give a random minion in your hand +2/+2."""
    events = OWN_TURN_END.on(Buff(RANDOM(FRIENDLY_HAND + MINION), "WON_108e"))


class WON_108e:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class WON_111:
    """Ancient Shieldbearer — Battlecry: If your C'Thun has at least 10 Attack, gain 10 Armor."""

    @staticmethod
    def play(self):
        if self.controller.cthun and self.controller.cthun.atk >= 10:
            return [GainArmor(FRIENDLY_HERO, 10)]
        return []


class WON_116:
    """Ivory Rook — Battlecry: Discover a Taunt minion. Gain Armor equal to its Cost."""
    # Simplified: no armor gain; just discover.
    play = DISCOVER(RandomMinion(taunt=True))


class WON_117:
    """Hobart Grapplehammer — Battlecry: If you have a weapon equipped, give all
    minions in your hand +1/+1.
    """

    @staticmethod
    def play(self):
        if self.controller.weapon:
            return [Buff(FRIENDLY_HAND + MINION, "WON_117e")]
        return []


class WON_117e:
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}
