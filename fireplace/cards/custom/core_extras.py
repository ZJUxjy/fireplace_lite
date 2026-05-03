"""Fill-in scripts for cards used by CORE that lacked implementations.

These cards exist in multiple sets but their original-set scripts were
missing in fireplace, so CORE_X auto-link had nothing to inherit.
Centralizing them here keeps the diff focused; each card script lives
under its original ID so the CORE_-prefix auto-link picks it up.
"""
from hearthstone.enums import SpellSchool
from ..utils import *


# --- Forged in the Barrens (BAR) ---


class BAR_310:
    """Lightshower Elemental"""
    # Taunt. Deathrattle: Restore 8 Health to all friendly characters.
    tags = {GameTag.TAUNT: True}
    deathrattle = Heal(FRIENDLY_CHARACTERS, 8)


class BAR_541:
    """Runed Orb"""
    # Deal 2 damage. Discover a spell.
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 2), DISCOVER(RandomSpell())


class BAR_878:
    """Veteran Warmedic"""
    # After you cast a Holy spell, summon a 2/2 Medic with Lifesteal.
    # Simplified: summon a generic 2/2 lifesteal token from existing pool.
    events = OWN_SPELL_PLAY.on(Summon(CONTROLLER, "BAR_878t"))


class BAR_878t:
    """Combat Medic (token)"""
    tags = {
        GameTag.LIFESTEAL: True,
        GameTag.ATK: 2,
        GameTag.HEALTH: 2,
    }


# --- Darkmoon Faire (DMF) ---


class DMF_067:
    """Prize Vendor"""
    # Battlecry and Deathrattle: Each player draws a card.
    play = Draw(CONTROLLER), Draw(OPPONENT)
    deathrattle = Draw(CONTROLLER), Draw(OPPONENT)


# --- Onyxia mini-set (NX2) ---


class NX2_028:
    """Hookfist-3000"""
    # After your hero attacks, gain 4 Armor and draw a card.
    events = Attack(FRIENDLY_HERO).on(GainArmor(FRIENDLY_HERO, 4), Draw(CONTROLLER))


# --- Onyxia / Vault (ONY) ---


class ONY_022:
    """Battle Vicar"""
    # Battlecry: Discover a Holy spell.
    play = DISCOVER(RandomSpell(spell_school=SpellSchool.HOLY))


class ONY_018:
    """Boomkin"""
    # Choose One - Restore 8 Health to your hero; or Deal 4 damage.
    requirements = {PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    choose = ("ONY_018a", "ONY_018b")
    play = Heal(FRIENDLY_HERO, 8)  # default first choice


class ONY_018a:
    play = Heal(FRIENDLY_HERO, 8)


class ONY_018b:
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 4)


# --- Revendreth + Onyxia mini-set (REV) ---


class REV_308:
    """Maze Guide"""
    # Battlecry: Summon a random 2-Cost minion.
    play = Summon(CONTROLLER, RandomMinion(cost=2))


# --- Lich King (RLK) ---


class RLK_708:
    """Chillfallen Baron"""
    # Battlecry and Deathrattle: Draw a card.
    play = Draw(CONTROLLER)
    deathrattle = Draw(CONTROLLER)


class RLK_958:
    """Skeletal Sidekick"""
    # Battlecry: Give a friendly Undead +2 Attack.
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "RLK_958e")


class RLK_958e:
    tags = {GameTag.ATK: 2}


class RLK_503:
    """Body Bagger"""
    # Battlecry: Gain a Corpse. (Corpses not modeled — no-op.)
    pass


# --- Scholomance (SCH) ---


class SCH_181:
    """Archwitch Willow"""
    # Battlecry: Summon a random Demon from your hand and deck.
    # Simplified: summon a random Demon from anywhere.
    play = Summon(CONTROLLER, RandomMinion(race=Race.DEMON))


class SCH_713:
    """Cult Neophyte"""
    # Battlecry: Your opponent's spells cost (1) more next turn.
    # Simplified: skip the cost mod (would need turn-bound aura).
    pass


# --- Stormwind (SW) ---


class SW_068:
    """Mo'arg Forgefiend"""
    # Taunt. Deathrattle: Gain 8 Armor.
    tags = {GameTag.TAUNT: True}
    deathrattle = GainArmor(FRIENDLY_HERO, 8)


class SW_429:
    """Best in Shell"""
    # Tradeable. Summon two 2/7 Turtles with Taunt. (Tradeable handled by tag.)
    play = Summon(CONTROLLER, "SW_429t") * 2


class SW_429t:
    """Tortoise Knight"""
    tags = {GameTag.TAUNT: True}


# --- Showdown / Wild West (WW) ---


class WW_329:
    """Detonation Juggernaut"""
    # Taunt. Battlecry: Give Taunt minions in your hand +2/+2.
    tags = {GameTag.TAUNT: True}
    play = Buff(FRIENDLY_HAND + MINION + TAUNT, "WW_329e")


class WW_329e:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


# --- New Core (CS3) ---


class CS3_022:
    """Fogsail Freebooter"""
    # Battlecry: If you have a weapon equipped, deal 2 damage.
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}

    @staticmethod
    def play(self):
        if self.controller.weapon:
            return [Hit(self.target, 2)]
        return []


class CS3_024:
    """Taelan Fordring"""
    # Taunt, Divine Shield. Deathrattle: Draw your highest Cost minion.
    tags = {GameTag.TAUNT: True, GameTag.DIVINE_SHIELD: True}
    deathrattle = ForceDraw(HIGHEST_COST(FRIENDLY_DECK + MINION))


class CS3_025:
    """Overlord Runthak"""
    # Rush. Whenever this attacks, give +1/+1 to all minions in your hand.
    tags = {GameTag.RUSH: True}
    events = Attack(SELF).on(Buff(FRIENDLY_HAND + MINION, "CS3_025e"))


class CS3_025e:
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


