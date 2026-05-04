"""WONDERS — neutral cards."""
from hearthstone.enums import Race
from ..utils import *


class WON_124:
    """Twilight Geomancer — Taunt. Battlecry: Give your C'Thun +1/+1 and Taunt."""
    tags = {GameTag.TAUNT: True}
    play = Buff(CTHUN, "OG_284e")


class WON_125:
    """C'Thun's Chosen — Divine Shield. Battlecry: Give your C'Thun +3/+3."""
    tags = {GameTag.DIVINE_SHIELD: True}
    play = Buff(CTHUN, "OG_281e", atk=3, max_health=3)


class WON_127:
    """Disciple of C'Thun — Battlecry: Deal 2 damage. Give C'Thun +2/+2."""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 2), Buff(CTHUN, "OG_281e", atk=2, max_health=2)


class WON_128:
    """Sludge Belcher — Taunt. Deathrattle: Summon a 1/2 Slime with Taunt."""
    tags = {GameTag.TAUNT: True}
    deathrattle = Summon(CONTROLLER, "FP1_012t")


class WON_131:
    """Crazed Worshipper — Taunt. Whenever this minion takes damage, give
    your C'Thun +1/+1 (wherever it is).
    """
    tags = {GameTag.TAUNT: True}
    events = SELF_DAMAGE.on(Buff(CTHUN, "OG_281e", atk=1, max_health=1))


class WON_135:
    """C'Thun — Battlecry: Deal damage equal to this minion's Attack
    randomly split among all enemies.
    """
    play = Hit(RANDOM(ENEMY_CHARACTERS), 1) * ATK(SELF)


class WON_138:
    """Shark Puncher — Deathrattle: Give a random friendly Pirate +2/+2."""
    deathrattle = Buff(RANDOM(FRIENDLY_MINIONS + PIRATE), "WON_138e")


class WON_138e:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class WON_330:
    """Cult Apothecary — Battlecry: For each enemy minion, restore 2 Health
    to your hero.
    """
    play = Heal(FRIENDLY_HERO, 2) * Count(ENEMY_MINIONS)


class WON_345:
    """Valstann Staghelm — Deathrattle: Summon a Taunt minion from your deck."""
    deathrattle = Summon(CONTROLLER, RANDOM(FRIENDLY_DECK + MINION + TAUNT))


class WON_357:
    """Acolyte of Pain — Whenever this minion takes damage, draw a card."""
    events = SELF_DAMAGE.on(Draw(CONTROLLER))


class WON_142:
    """Menagerie Jug — Battlecry: Give 3 random friendly minions of
    different minion types +2/+2.
    """

    @staticmethod
    def play(self):
        seen = set()
        targets = []
        for m in self.controller.field:
            if m is self:
                continue
            for race in m.races or []:
                if race and race not in seen:
                    seen.add(race)
                    targets.append(m)
                    break
            if len(targets) >= 3:
                break
        if not targets:
            return []
        return [Buff(t, "WON_142e") for t in targets]


class WON_142e:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class WON_329:
    """Blackwing Corruptor — Battlecry: If you're holding a Dragon, deal 5 damage."""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = HOLDING_DRAGON & Hit(TARGET, 5)
