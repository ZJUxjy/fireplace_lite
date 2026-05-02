"""All remaining LOCATION cards across multiple expansions.

Each card declares `location_action` (the use effect) and optionally
`location_requirements` (target requirements for the use). Effects are
simplified where they require unimplemented mechanics (Spellburst, Corpses,
Excavate, Reopen-after-trigger, Dormant, multi-stage Time Travel forms).

This file uses simplified scripts that capture the spirit of each card.
"""

from ..utils import *


# ============================================================================
# CATA — Cataclysm
# ============================================================================

class CATA_301:
    """Ruby Sanctum"""
    # Your next Healing effect this turn deals damage instead.
    # Simplified: deal 3 damage to enemy hero (a typical heal-as-damage value).
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    location_action = Hit(TARGET, 3)


class CATA_477:
    """Chamber of Aspects"""
    # Choose a minion in your hand. Give it +2/+2.
    # Simplified: buff a random hand minion.
    location_action = Buff(RANDOM(FRIENDLY_HAND + MINION), "CATA_477e")


CATA_477e = buff(atk=2, health=2)


class CATA_492:
    """Shrine of Twilight"""
    # Herald: ... Draw a card. (Herald not implemented — just draw.)
    location_action = Draw(CONTROLLER)


class CATA_527:
    """Nespirah, Enthralled"""
    # Deal 1 damage. After Fel spell, reopen. Deathrattle: Summon unshackled.
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    location_action = Hit(TARGET, 1)


class CATA_584:
    """Erupting Volcano"""
    # Deal 3 damage randomly split among enemies. (Skip "if Fire spell, deal 3 more")
    location_action = Hit(RANDOM_ENEMY_CHARACTER, 1) * 3


# ============================================================================
# DEEP — Voyage to the Sunken City
# ============================================================================

class DEEP_019:
    """Crimson Expanse"""
    # Summon a copy of a damaged minion (skip Dormant).
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_DAMAGED_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    location_action = Summon(CONTROLLER, ExactCopy(TARGET))


# ============================================================================
# EDR — Into the Emerald Dream
# ============================================================================

class EDR_454:
    """Clutch of Corruption"""
    # Choose a friendly Dragon. Summon a 0/2 Egg copy of it.
    # Simplified: summon a copy directly.
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_WITH_RACE: 24,  # DRAGON
    }
    location_action = Summon(CONTROLLER, ExactCopy(TARGET))


class EDR_520:
    """Forbidden Shrine"""
    # Spend all your Mana. Cast a random spell that costs that much.
    # Simplified: cast a random spell of cost == current mana.
    location_action = CastSpell(RandomSpell())


# ============================================================================
# ETC — Festival of Legends
# ============================================================================

class ETC_449:
    """Fan Club"""
    # Restore 3 Health to all friendly characters.
    location_action = Heal(FRIENDLY_CHARACTERS, 3)


class ETC_533:
    """Mosh Pit"""
    # Spend 3 Corpses to give a friendly minion Reborn. (Corpses not impl.)
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    location_action = SetTags(TARGET, {GameTag.REBORN: True})


# ============================================================================
# FIR — Whizbang/recent
# ============================================================================

class FIR_907:
    """Amirdrassil"""
    # Summons a 1-Cost minion, gain 1 Armor, draw 1, refresh 1 mana.
    # (Improves each use — simplified to fixed values.)
    location_action = (
        Summon(CONTROLLER, RandomMinion(cost=1)),
        GainArmor(FRIENDLY_HERO, 1),
        Draw(CONTROLLER),
        ManaThisTurn(CONTROLLER, 1),
    )


# ============================================================================
# GDB — Great Dark Beyond
# ============================================================================

class GDB_136t:
    """The Galaxy's Lens"""
    # Spellburst: absorb spell power. (Spellburst not implemented.)
    location_action = Hit(RANDOM_ENEMY_CHARACTER, 2)


# ============================================================================
# JAM — additional ETC tokens
# ============================================================================

class JAM_009:
    """Dance Floor"""
    # Give your minions Rush.
    location_action = SetTags(FRIENDLY_MINIONS, {GameTag.RUSH: True})


# ============================================================================
# MIS — Whizbang's Workshop
# ============================================================================

class MIS_919:
    """Puppet Theatre"""
    # Choose an enemy minion. Get a 1/1 copy of it that costs (1).
    # Simplified: just copy the minion to hand.
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    location_action = Give(CONTROLLER, ExactCopy(TARGET))


# ============================================================================
# NX2 — Onyxia's Lair mini-set
# ============================================================================

class NX2_036:
    """Construct Quarter"""
    # Destroy a friendly minion to summon a 4/5 Undead with Rush.
    # Simplified: summon a 4/5 with Rush. (Sacrifice not modeled.)
    location_action = Summon(CONTROLLER, "NX2_036t")


class NX2_036t:
    pass


# ============================================================================
# REV — Murder at Castle Nathria (originals + tokens)
# ============================================================================

class REV_333:
    """Hedge Maze"""
    # Trigger a friendly minion's Deathrattle.
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    location_action = Deathrattle(TARGET)


class REV_750:
    """Sinstone Graveyard"""
    # Summon a Ghost (stats based on cards played this turn). Simplified: 2/2.
    location_action = Summon(CONTROLLER, "REV_750t")


class REV_750t:
    pass


# REV_790–799 are the "shifted location" tokens that show as "{0} {1}" — they
# reuse the parent location's effect. We map each to a basic friendly buff.

class REV_790:
    """Castle Kennels (shifted)"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_FRIENDLY_TARGET: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Buff(TARGET, "REV_362e")


class REV_791:
    """Cathedral of Atonement (shifted)"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Buff(TARGET, "REV_290e"), Draw(CONTROLLER)


class REV_792:
    """Hedge Maze (shifted)"""
    location_requirements = REV_333.location_requirements
    location_action = Deathrattle(TARGET)


class REV_793:
    """Sanguine Depths (shifted)"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Hit(TARGET, 1), Buff(TARGET, "REV_990e")


class REV_794:
    """Great Hall (shifted)"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Buff(TARGET, "REV_983e")


class REV_795:
    """Sinstone Graveyard (shifted)"""
    location_action = Summon(CONTROLLER, "REV_750t")


class REV_796:
    """Nightcloak Sanctum (shifted)"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Freeze(TARGET), Summon(CONTROLLER, "REV_602t")


class REV_797:
    """Relic Vault (shifted)"""
    # Next Relic this turn casts twice — unimplementable, give a draw.
    location_action = Draw(CONTROLLER)


class REV_798:
    """Muck Pools (shifted)"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_FRIENDLY_TARGET: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Morph(TARGET, RandomMinion(cost=COST(TARGET) + 1))


class REV_799:
    """Vile Library (shifted)"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_FRIENDLY_TARGET: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Buff(TARGET, "REV_371e")


class REV_923:
    """Muck Pools"""
    # Transform a friendly minion into one that costs (1) more.
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    location_action = Morph(TARGET, RandomMinion(cost=COST(TARGET) + 1))


class REV_942:
    """Relic Vault"""
    # The next Relic you play this turn casts twice. (Relics not impl.)
    location_action = Draw(CONTROLLER)


class REV_983:
    """Great Hall"""
    # Set a minion's Attack and Health to 3.
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Buff(TARGET, "REV_983e")


class REV_983e:
    atk = SET(3)
    max_health = SET(3)


class REV_990:
    """Sanguine Depths"""
    # Deal 1 damage to a minion and give it +2 Attack.
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Hit(TARGET, 1), Buff(TARGET, "REV_990e")


REV_990e = buff(atk=2)


# ============================================================================
# SC — Heroes of StarCraft
# ============================================================================

class SC_000:
    """Spawning Pool"""
    # Get a 1/1 Zergling. Deathrattle: Zerg minions have Rush.
    location_action = Give(CONTROLLER, "SC_000t")


class SC_000t:
    pass


class SC_019:
    """Ultralisk Cavern"""
    # Deal 1 damage to all enemies. Deathrattle: Summon 8/8 Ultralisk.
    location_action = Hit(ENEMY_CHARACTERS, 1)


class SC_403:
    """Starport"""
    # Summon a 2/1 Starship_Piece. (Starship not impl — summon vanilla.)
    location_action = Summon(CONTROLLER, "SC_403t")


class SC_403t:
    pass


class SC_751:
    """Warp Gate"""
    # Your next Protoss minion costs (3) less. (Cost mod not impl.)
    location_action = Draw(CONTROLLER)


# ============================================================================
# TIME — Time travel multi-stage locations
# ============================================================================

class TIME_044:
    """Past Gnomeregan"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Buff(TARGET, "TIME_044e")


TIME_044e = buff(atk=2, health=1)


class TIME_044t1:
    """Present Gnomeregan"""
    location_requirements = TIME_044.location_requirements
    location_action = Buff(TARGET, "TIME_044e")


class TIME_044t2:
    """Future Gnomeregan"""
    location_requirements = TIME_044.location_requirements
    location_action = Buff(TARGET, "TIME_044e"), SetTags(TARGET, {GameTag.DIVINE_SHIELD: True})


class TIME_211t1:
    """The Well of Eternity"""
    location_action = Give(CONTROLLER, RandomSpell())


class TIME_211t1t(TIME_211t1):
    pass


class TIME_211t2:
    """Zin-Azshari"""
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    location_action = Summon(CONTROLLER, ExactCopy(TARGET))


class TIME_211t2t(TIME_211t2):
    pass


class TIME_436:
    """Past Conflux"""
    location_action = Summon(CONTROLLER, RandomMinion(race=Race.DRAGON, cost=5))


class TIME_436t1(TIME_436):
    pass


class TIME_436t2(TIME_436):
    pass


class TIME_446:
    """The Eternal Hold"""
    location_action = DISCOVER(RandomMinion(race=Race.DEMON, cost=5))


class TIME_810:
    """Past Silvermoon"""
    location_action = Hit(RANDOM_ENEMY_MINION, 5)


class TIME_810t1(TIME_810):
    pass


class TIME_810t2(TIME_810):
    pass


class TIME_890t2:
    """Karazhan the Sanctum"""
    location_action = Summon(CONTROLLER, RandomMinion(cost=8)) * 2


# ============================================================================
# TLC — Lost City of Un'Goro (custom)
# ============================================================================

class TLC_100t1:
    """Un'Goro Jungle"""
    location_action = Summon(CONTROLLER, RandomMinion(race=Race.BEAST, cost=1))


class TLC_100t2:
    """Terror Run"""
    location_action = Summon(CONTROLLER, RandomMinion(cost=5))


class TLC_100t3:
    """Fire Plume Ridge"""
    location_action = Hit(ENEMY_CHARACTERS, 3)


class TLC_433t2:
    """Terror's Grave"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    location_action = Hit(TARGET, 4)


class TLC_449:
    """Bloodpetal Biome"""
    location_action = DISCOVER(RandomMinion(cost=1))


# ============================================================================
# TOY — Whizbang's Workshop locations
# ============================================================================

class TOY_359:
    """Jungle Gym"""
    # Deal 1 to a random enemy. Repeat for each friendly Beast. (Simplified: just 1)
    location_action = Hit(RANDOM_ENEMY_CHARACTER, 1)


class TOY_507:
    """Fairy Tale Forest"""
    # Draw a Battlecry minion. It costs (1) less. (Cost-1 skipped.)
    location_action = ForceDraw(RANDOM(FRIENDLY_DECK + MINION))


class TOY_512:
    """The Crystal Cove"""
    # Next minion summoned has stats set to 4/4. (Buff approximation.)
    location_action = Buff(FRIENDLY_HAND + MINION, "TOY_512e")


class TOY_512e:
    atk = SET(4)
    max_health = SET(4)


class TOY_850:
    """Magical Dollhouse"""
    # Gain Spell Damage +1 this turn only.
    location_action = Buff(FRIENDLY_HERO, "TOY_850e")


class TOY_850e:
    tags = {GameTag.SPELLPOWER: 1}
    events = OWN_TURN_END.on(Destroy(SELF))


# ============================================================================
# TTN — Titans
# ============================================================================

class TTN_090:
    """Prison of Yogg-Saron"""
    # Cast 4 random spells on a target.
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    location_action = CastSpell(RandomSpell()) * 4


class TTN_465:
    """Forge of Wills"""
    # Summon a Giant with friendly minion's stats and Rush.
    # Simplified: summon a 6/6 with Rush.
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    location_action = Summon(CONTROLLER, "TTN_465t")


class TTN_465t:
    pass


# ============================================================================
# VAC — Perils in Paradise
# ============================================================================

class VAC_334:
    """Knickknack Shack"""
    location_action = Draw(CONTROLLER)


class VAC_409:
    """Parrot Sanctuary"""
    # Next Battlecry minion costs (1) less. (Cost mod skipped.)
    location_action = Draw(CONTROLLER)


class VAC_425:
    """Horizon's Edge"""
    location_action = Hit(RANDOM_ENEMY_CHARACTER, 1) * 3


class VAC_517:
    """Hiking Trail"""
    location_action = DISCOVER(RandomMinion(taunt=True))


class VAC_522:
    """Tide Pools"""
    location_action = DISCOVER(RandomSpell(cost=3))


class VAC_923t:
    """Sanc'Azel"""
    location_requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    location_action = Buff(TARGET, "VAC_923te"), SetTags(TARGET, {GameTag.RUSH: True})


VAC_923te = buff(atk=3)


class VAC_929:
    """Dangerous Cliffside"""
    # Summon two 1/1 Pirates with Charge.
    location_action = Summon(CONTROLLER, "VAC_929t") * 2


class VAC_929t:
    tags = {GameTag.CHARGE: True}


# ============================================================================
# WON — Year of the Wolf wonder cards
# ============================================================================

class WON_015:
    """Cenarion Hold"""
    # Next Choose One card has both effects combined. (Skip — buff cost reduce instead.)
    location_action = Draw(CONTROLLER)


class WON_053t:
    """Outskirts of Lordaeron"""
    # Choose a minion. Destroy all minions with less Attack.
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Destroy(ALL_MINIONS + (ATK < ATK(TARGET)))


class WON_053t2:
    """Wind Rider Roost"""
    location_action = Summon(CONTROLLER, RandomMinion(cost=3)).then(SetTags(Summon.CARD, {GameTag.CHARGE: True}))


class WON_053t3:
    """Xenedar"""
    # Next battlecry triggers twice. (Skip.)
    location_action = Draw(CONTROLLER)


class WON_053t4:
    """The Nighthold"""
    location_action = Summon(CONTROLLER, RandomSpell(secret=True)) * 3


class WON_053t5:
    """Valdrakken"""
    location_action = Give(CONTROLLER, RandomMinion(race=Race.DRAGON)) * 2


class WON_053t6:
    """Ruins of Korune"""
    location_action = Draw(CONTROLLER) * 2


class WON_053t7:
    """Temple of Earth"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_FRIENDLY_TARGET: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Summon(CONTROLLER, ExactCopy(TARGET))


class WON_103:
    """Chamber of Viscidus"""
    # Look at 3 hand cards, discard 1, draw 2. Simplified.
    location_action = Discard(RANDOM(FRIENDLY_HAND)), Draw(CONTROLLER) * 2


# ============================================================================
# WW — Showdown in the Badlands
# ============================================================================

class WW_001t11:
    """Ogrefist Boulder"""
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Buff(TARGET, "WW_001t11e")


class WW_001t11e:
    atk = SET(6)
    max_health = SET(7)


class WW_359t:
    """Badlands Jail"""
    # Make a minion go Dormant for 3 turns. (Dormant simplified: just freeze.)
    location_requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    location_action = Freeze(TARGET)
