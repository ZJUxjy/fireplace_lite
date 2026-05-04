"""Fill-in scripts for cards used by CORE that lacked implementations.

These cards exist in multiple sets but their original-set scripts were
missing in fireplace, so CORE_X auto-link had nothing to inherit.
Centralizing them here keeps the diff focused; each card script lives
under its original ID so the CORE_-prefix auto-link picks it up.
"""
from hearthstone.enums import CardType, Race, SpellSchool
from ..utils import *
from ...actions import GainCorpse, TargetedAction, ActionArg


class _SpendCorpsesSummon(TargetedAction):
    """Helper for end-of-turn / battlecry corpse-spend → summon-N actions.

    Reads `_max_count` and `_card_id` from instance attrs (set via class).
    Spends up to `_max_count` corpses and summons one copy of `_card_id`
    per spent corpse. Spawned via `_make_corpse_spend_action` factory below.
    """
    TARGET = ActionArg()

    def do(self, source, target):
        spend = min(target.corpses, self._max_count)
        if spend == 0:
            return
        target.corpses -= spend
        for _ in range(spend):
            source.game.queue_actions(source, [Summon(target, self._card_id)])


def _make_corpse_spend_action(max_count, card_id):
    """Build a `_SpendCorpsesSummon`-style class bound to fixed kwargs."""
    cls_name = "SpendCorpses_%s_x%d" % (card_id, max_count)
    cls = type(cls_name, (_SpendCorpsesSummon,), {
        "_max_count": max_count,
        "_card_id": card_id,
    })
    return cls


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
    """Body Bagger — Battlecry: Gain a Corpse."""
    play = GainCorpse(CONTROLLER, 1)


# --- Death Knight (Lich King RLK + others) ---


class CORE_CATA_009:
    """Death's Advance (CORE-only — no CATA_009 base card in data)."""
    # Freeze a character. Discover a spell.
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Freeze(TARGET), DISCOVER(RandomSpell())


class RLK_062:
    """Nerubian Swarmguard"""
    # Taunt. Battlecry: Summon two copies of this minion.
    tags = {GameTag.TAUNT: True}
    play = Summon(CONTROLLER, ExactCopy(SELF)) * 2


class RLK_083:
    """Deathchiller"""
    # After you cast a spell, deal 1 damage to two random enemies.
    events = OWN_SPELL_PLAY.after(
        Hit(RANDOM_ENEMY_CHARACTER, 1), Hit(RANDOM_ENEMY_CHARACTER, 1)
    )


class RLK_121:
    """Acolyte of Death"""
    # After a friendly Undead dies, draw a card.
    events = Death(FRIENDLY + MINION + UNDEAD).on(Draw(CONTROLLER))


class RLK_223:
    """Thassarian"""
    # Reborn. Battlecry and Deathrattle: Deal 2 damage to a random enemy.
    tags = {GameTag.REBORN: True}
    play = Hit(RANDOM_ENEMY_CHARACTER, 2)
    deathrattle = Hit(RANDOM_ENEMY_CHARACTER, 2)


class RLK_511:
    """Harbinger of Winter"""
    # Deathrattle: Draw a Frost spell.
    # Simplified: draw any spell (frost-school filter on deck draws is awkward).
    deathrattle = ForceDraw(RANDOM(FRIENDLY_DECK + SPELL))


class RLK_706:
    """Alexandros Mograine"""
    # Battlecry: For the rest of the game, deal 3 damage to your opponent
    # at the end of your turn. Modeled by buffing self with a permanent
    # turn-end aura that survives even after Mograine dies (the buff is
    # attached to the controller, not the minion). Simplified: stays on
    # the minion (lost when Mograine leaves the field).
    events = OWN_TURN_END.on(Hit(ENEMY_HERO, 3))


class RLK_025:
    """Frost Strike"""
    # Deal 3 damage to a minion. If it dies, Discover a Frost Rune card.
    # Simplified: always Discover after the hit (engine condition on
    # "if it dies" requires post-Damage check we'd need to wire).
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 3), DISCOVER(RandomSpell())


class RLK_086:
    """Frostmourne"""
    # Deathrattle: Summon every minion killed by this weapon.
    # Simplified: summon a single random Undead minion (full kill-tracking
    # requires per-weapon kill list maintenance the engine doesn't expose).
    deathrattle = Summon(CONTROLLER, RandomMinion(race=Race.UNDEAD))


class RLK_066:
    """Hematurge — Battlecry: Spend a Corpse to Discover a Blood Rune card."""

    @staticmethod
    def play(self):
        if self.controller.corpses >= 1:
            self.controller.corpses -= 1
            return [Discover(self.controller, RandomSpell()).then(
                Give(self.controller, Discover.CARD)
            )]
        return []


class RLK_116:
    """Necrotic Mortician — Battlecry: If a friendly Undead died this game,
    Discover an Unholy Rune.

    Real card checks "died after your last turn"; we simplify to "died this
    game" since fireplace's killed_this_turn flag resets at turn start.
    """

    @staticmethod
    def play(self):
        if self.controller.graveyard.filter(type=CardType.MINION, races=Race.UNDEAD):
            return [Discover(self.controller, RandomSpell()).then(
                Give(self.controller, Discover.CARD)
            )]
        return []


class RLK_505:
    """Marrow Manipulator — Battlecry: Spend up to 5 Corpses. Deal 2 damage
    to a random enemy for each.
    """

    @staticmethod
    def play(self):
        spend = min(self.controller.corpses, 5)
        if spend == 0:
            return []
        self.controller.corpses -= spend
        return [Hit(RANDOM_ENEMY_CHARACTER, 2)] * spend


class RLK_506:
    """Boneguard Commander — Taunt. Battlecry: Raise up to 6 Corpses as 1/3
    Risen Footmen with Taunt.
    """
    tags = {GameTag.TAUNT: True}

    @staticmethod
    def play(self):
        spend = min(self.controller.corpses, 6)
        if spend == 0:
            return []
        self.controller.corpses -= spend
        return [Summon(self.controller, "RLK_061t")] * spend


class CORE_EDR_003:
    """Falric (CORE-only — no EDR_003 base card in data).
    You gain twice as many Corpses as normal. Battlecry: Draw a card.
    Simplified: just the draw — corpse doubling isn't modeled (would
    require source tagging in Death.do).
    """
    play = Draw(CONTROLLER)


# --- New Corpse-aware cards (added in Phase 2A) ---


class RLK_061:
    """Battlefield Necromancer — At end of turn, raise a Corpse as a 1/3
    Risen Footman with Taunt.
    """
    events = OWN_TURN_END.on(_make_corpse_spend_action(1, "RLK_061t")(CONTROLLER))


class CORE_RLK_712:
    """Blood Tap — Give all minions in your hand +1/+1. Spend 2 Corpses to
    give them +1/+1 more.
    """

    @staticmethod
    def play(self):
        actions = [Buff(FRIENDLY_HAND + MINION, "RLK_712e")]
        if self.controller.corpses >= 2:
            self.controller.corpses -= 2
            actions.append(Buff(FRIENDLY_HAND + MINION, "RLK_712e"))
        return actions


class RLK_712e:
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


class _MalignantHorrorClone(TargetedAction):
    """Spend 4 corpses (controller) → summon a copy of source."""
    TARGET = ActionArg()

    def do(self, source, target):
        if target.corpses < 4:
            return
        target.corpses -= 4
        source.game.queue_actions(source, [Summon(target, ExactCopy(source))])


class CORE_RLK_745:
    """Malignant Horror — Reborn. At end of turn, spend 4 Corpses to summon
    a copy of this minion.
    """
    tags = {GameTag.REBORN: True}
    events = OWN_TURN_END.on(_MalignantHorrorClone(CONTROLLER))


class RLK_060:
    """Army of the Dead — Raise up to 5 Corpses as 2/2 Risen Ghouls with Rush.
    Real token: RLK_008t (Risen Ghoul 2/2 Rush).
    """

    @staticmethod
    def play(self):
        spend = min(self.controller.corpses, 5)
        if spend == 0:
            return []
        self.controller.corpses -= spend
        return [Summon(self.controller, "RLK_008t")] * spend


class CORE_WW_374:
    """Corpse Farm — Spend up to 8 Corpses to summon a random minion of that Cost."""

    @staticmethod
    def play(self):
        spend = min(self.controller.corpses, 8)
        if spend == 0:
            return []
        self.controller.corpses -= spend
        return [Summon(self.controller, RandomMinion(cost=spend))]


# ============================================================================
# Phase 2B: complex single-offs (Tichondrius / Ulfar / Vibrant Squirrel /
# Illidari Inquisitor / Keymaster Alabaster / Menagerie Mug / Jackpot).
# Cards with cost-modifying auras (Foxy Fraud, Cult Neophyte, Resistance
# Aura) and origin-tracking effects (Steamcleaner) remain unimplemented.
# ============================================================================


class CORE_CATA_001:
    """Tichondrius — Your hero is Immune. Battlecry: Your next Demon this
    turn costs (0).

    Hero-immune is modeled via an `update` aura that re-applies IMMUNE
    while Tichondrius is on the field. The "next Demon costs 0" cost-mod
    is omitted (requires a turn-bound aura the engine doesn't expose).
    """
    update = Refresh(FRIENDLY_HERO, {GameTag.IMMUNE: True})


class CORE_CATA_006:
    """Ulfar — Battlecry: Give your other minions
    'Deathrattle: Summon a minion with this minion's Cost.'
    """
    play = Buff(FRIENDLY_MINIONS - SELF, "CORE_CATA_006e")


class CORE_CATA_006e:
    deathrattle = Summon(CONTROLLER, RandomMinion(cost=COST(OWNER)))
    tags = {GameTag.DEATHRATTLE: True}


class WON_141e:
    """Menagerie Mug's "+1/+1 to selected friendly" buff."""
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


class CORE_SW_439:
    """Vibrant Squirrel — Deathrattle: Shuffle 4 Acorns into your deck.
    When drawn, an Acorn summons a 2/1 Squirrel.
    """
    deathrattle = Shuffle(CONTROLLER, "SW_439t") * 4


class SW_439t:
    """Acorn token — destroys itself and summons a Satisfied Squirrel
    (SW_439t2 = 2/1 Squirrel) when drawn.
    """
    draw = Destroy(SELF), Summon(CONTROLLER, "SW_439t2")


class CS3_020:
    """Illidari Inquisitor — Rush. After your hero attacks an enemy, this
    attacks it too.
    """
    tags = {GameTag.RUSH: True}
    events = Attack(FRIENDLY_HERO).after(Attack(SELF, Attack.DEFENDER))


class CORE_SCH_717:
    """Keymaster Alabaster — Whenever your opponent draws a card, add a
    copy to your hand that costs (1).

    The cost-mod portion is skipped (engine has no per-card cost override
    that survives leaving Keymaster's aura). The copy is added at full cost.
    """
    events = Draw(OPPONENT).on(Give(CONTROLLER, ExactCopy(Draw.CARD)))


class CORE_WON_141:
    """Menagerie Mug — Battlecry: Give 3 random friendly minions of
    different minion types +1/+1.

    Simplified: pick up to 3 friendly minions of distinct races and buff
    each. If fewer than 3 distinct races are present, buff what we can.
    """

    @staticmethod
    def play(self):
        seen_races = set()
        targets = []
        # Iterate friendly minions (excluding self) and pick first per race.
        for minion in self.controller.field:
            if minion is self:
                continue
            for race in minion.races or [None]:
                if race and race not in seen_races:
                    seen_races.add(race)
                    targets.append(minion)
                    break
            if len(targets) >= 3:
                break
        if not targets:
            return []
        return [Buff(t, "WON_141e") for t in targets]


class CORE_TID_931:
    """Jackpot! — Add two random spells from other classes that cost (5)
    or more to your hand.

    Simplified: pick from any class spells (not strictly off-class) at cost
    5+. The "off-class" filter would require comparing card_class to the
    controller's class, which the cards.filter helper can't express directly.
    """
    play = Give(CONTROLLER, RandomSpell(cost=[5, 6, 7, 8, 9, 10])) * 2


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


# ============================================================================
# Phase 12: additional CORE fill-ins (~36 cards across all classes).
# Cards here either (a) are CORE_-only with no base equivalent in data, or
# (b) have a base ID whose original implementation was missing.
# Hard-to-model effects (Corpses, cost-modifying auras, deck-origin tracking)
# remain unimplemented in this batch.
# ============================================================================


# --- DEATH KNIGHT ---


class RLK_048:
    """Anti-Magic Shell — Give your minions +1/+1 and 'Elusive'."""
    play = Buff(FRIENDLY_MINIONS, "RLK_048e")


class RLK_048e:
    tags = {
        GameTag.ATK: 1,
        GameTag.HEALTH: 1,
        GameTag.CANT_BE_TARGETED_BY_ABILITIES: True,
        GameTag.CANT_BE_TARGETED_BY_HERO_POWERS: True,
    }


class CORE_RLK_087:
    """Asphyxiate — Destroy the highest Attack enemy minion."""
    play = Destroy(HIGHEST_ATK(ENEMY_MINIONS))


class RLK_024:
    """Death Strike — Lifesteal. Deal 6 damage to a minion.

    LIFESTEAL is set on the spell via XML tags, so the engine handles
    the heal automatically when Hit fires.
    """
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 6)


class RLK_709:
    """Remorseless Winter — Deal 2 damage to all enemies. Draw a card."""
    play = Hit(ENEMY_CHARACTERS, 2), Draw(CONTROLLER)


class CORE_RLK_063:
    """Frostwyrm's Fury — Deal 5 damage. Freeze enemy minions. Summon 5/5."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = (
        Hit(TARGET, 5),
        Freeze(ENEMY_MINIONS),
        Summon(CONTROLLER, "RLK_063t"),
    )


class RLK_063t:
    """Frostwyrm token — 5/5 Frostwyrm."""
    tags = {GameTag.ATK: 5, GameTag.HEALTH: 5}


class CORE_EDR_002:
    """Poison Breath — Give a friendly Undead Poisonous."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_WITH_RACE: Race.UNDEAD.value,
    }
    play = Buff(TARGET, "CORE_EDR_002e")


class CORE_EDR_002e:
    tags = {GameTag.POISONOUS: True}


class RLK_707:
    """Grave Strength — Give your minions +1 Attack. Spend 5 Corpses to give
    them +3 instead.
    """

    @staticmethod
    def play(self):
        if self.controller.corpses >= 5:
            self.controller.corpses -= 5
            return [Buff(FRIENDLY_MINIONS, "RLK_707e_big")]
        return [Buff(FRIENDLY_MINIONS, "RLK_707e")]


class RLK_707e:
    tags = {GameTag.ATK: 1}


class RLK_707e_big:
    tags = {GameTag.ATK: 3}


class RLK_118:
    """Tomb Guardians — Summon two 2/2 Zombies with Taunt. Spend 4 Corpses
    to give them Reborn.
    """

    @staticmethod
    def play(self):
        if self.controller.corpses >= 4:
            self.controller.corpses -= 4
            # Summon then SetTags(REBORN) on each spawned token.
            return [
                Summon(self.controller, "RLK_118t3").then(
                    SetTags(Summon.CARD, {GameTag.REBORN: True})
                ),
                Summon(self.controller, "RLK_118t3").then(
                    SetTags(Summon.CARD, {GameTag.REBORN: True})
                ),
            ]
        return [Summon(self.controller, "RLK_118t3") * 2]


class CORE_CATA_007:
    """Consumption — Deal 3 damage to two random enemy minions.
    (The conditional 'Draw a card for each that dies' is skipped.)
    """
    play = Hit(RANDOM_ENEMY_MINION, 3) * 2


# --- DEMON HUNTER ---


class CORE_TTN_843:
    """Eredar Deceptor — Whenever you draw a card, summon a 1/1 Demon w/ Rush."""
    # TTN_843t1 = Invading Felbat (1/1 demon w/ Rush), the real card's token.
    events = Draw(CONTROLLER).on(Summon(CONTROLLER, "TTN_843t1"))


class CORE_WC_701:
    """Felrattler — Rush. Deathrattle: Deal 1 damage to all enemy minions."""
    tags = {GameTag.RUSH: True}
    deathrattle = Hit(ENEMY_MINIONS, 1)


# --- DRUID ---


class CORE_TSC_650:
    """Flipper Friends — Choose One: 6/6 Orca w/ Taunt; or six 1/1 Otters w/ Rush.

    Real-card tokens: TSC_650t (6/6 Orca Taunt), TSC_650t4 (1/1 Otter Rush).
    """
    choose = ("TSC_650a", "TSC_650d")
    play = Summon(CONTROLLER, "TSC_650t")


class TSC_650a:
    play = Summon(CONTROLLER, "TSC_650t")


class TSC_650d:
    play = Summon(CONTROLLER, "TSC_650t4") * 6


class CORE_RLK_657:
    """Underking — Rush. Battlecry and Deathrattle: Gain 6 Armor."""
    tags = {GameTag.RUSH: True}
    play = GainArmor(FRIENDLY_HERO, 6)
    deathrattle = GainArmor(FRIENDLY_HERO, 6)


# --- HUNTER ---


class CORE_BAR_801:
    """Wound Prey — Deal 1 damage. Summon a 1/1 Hyena with Rush."""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    # BAR_035t = Swift Hyena 1/1 Rush (the existing in-set hyena token).
    play = Hit(TARGET, 1), Summon(CONTROLLER, "BAR_035t")


class CORE_AV_337:
    """Mountain Bear — Taunt. Deathrattle: Summon two 2/4 Cubs with Taunt."""
    tags = {GameTag.TAUNT: True}
    deathrattle = Summon(CONTROLLER, "AV_337t") * 2


class AV_337t:
    tags = {GameTag.ATK: 2, GameTag.HEALTH: 4, GameTag.TAUNT: True}


# --- MAGE ---


class CORE_SW_108:
    """First Flame — Deal 2 damage to a minion. Add a Second Flame to hand."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 2), Give(CONTROLLER, "SW_108t")


class SW_108t:
    """Second Flame — Deal 2 damage to a minion."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 2)


class CORE_BAR_812:
    """Oasis Ally — Secret: when a friendly minion is attacked, summon a 3/6 Water Elemental."""
    # ICC_833t = 3/6 Water Elemental (existing token reused).
    secret = Attack(None, FRIENDLY_MINIONS).on(
        Reveal(SELF), Summon(CONTROLLER, "ICC_833t")
    )


# --- NEUTRAL ---


class CORE_SW_072:
    """Rustrot Viper — Tradeable. Battlecry: Destroy your opponent's weapon."""
    play = Destroy(ENEMY_WEAPON)


class CORE_SW_066:
    """Royal Librarian — Tradeable. Battlecry: Silence a minion."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Silence(TARGET)


class CORE_REV_023:
    """Demolition Renovator — Tradeable. Battlecry: Destroy an enemy location."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_LOCATION_TARGET: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    play = Destroy(TARGET)


class CORE_ETC_111:
    """Merch Seller — At end of turn, put a random spell on top of opponent's deck.
    (Engine doesn't expose 'top of deck' for arbitrary card; using Shuffle as
    an approximation — the random spell goes into the opponent's deck.)
    """
    events = OWN_TURN_END.on(Shuffle(OPPONENT, RandomSpell()))


class CORE_YOP_034:
    """Runaway Blackwing — At end of turn, deal 10 damage to a random enemy minion."""
    events = OWN_TURN_END.on(Hit(RANDOM_ENEMY_MINION, 10))


# --- PALADIN ---


class CORE_TSC_076:
    """Immortalized in Stone — Summon a 4/8, 2/4, and 1/2 Elemental with Taunt.

    Real-card tokens use these existing in-set ids: TSC_076t (Worn Statue),
    TSC_076t2 (Living Statue), TSC_076t3 (Pristine Statue). Stats taken
    straight from the tokens (data shows 1/2, 2/4, 1/2 — note that the
    description's '4/8 Pristine Statue' isn't reflected in this XML build;
    we summon what's there).
    """
    play = (
        Summon(CONTROLLER, "TSC_076t"),
        Summon(CONTROLLER, "TSC_076t2"),
        Summon(CONTROLLER, "TSC_076t3"),
    )


# --- PRIEST ---


class CORE_SW_442:
    """Void Shard — Lifesteal. Deal 4 damage."""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 4)


class CORE_SCH_512:
    """Initiation — Deal 4 damage to a minion. If it dies, summon a new copy."""
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 4).then(Dead(Hit.TARGET) & Summon(CONTROLLER, ExactCopy(Hit.TARGET)))


class CORE_BAR_311:
    """Devouring Plague — Lifesteal. Deal 4 damage randomly split among enemy minions."""
    play = Hit(RANDOM_ENEMY_MINION, 1) * 4


class CORE_BAR_313:
    """Priest of An'she — Taunt. Battlecry: If you've restored Health this turn, +3/+3.

    Tracked via the hero's healed_this_turn counter — covers the most common
    healing path (hero healed). Direct minion heals don't bump it; treated as
    a soft simplification.
    """
    tags = {GameTag.TAUNT: True}

    @staticmethod
    def play(self):
        if (self.controller.hero
                and getattr(self.controller.hero, "healed_this_turn", 0) > 0):
            return [Buff(self, "BAR_313e")]
        return []


class BAR_313e:
    tags = {GameTag.ATK: 3, GameTag.HEALTH: 3}


class CORE_RLK_814:
    """Crystalsmith Cultist — Battlecry: If holding a Shadow spell, gain +1/+1."""

    @staticmethod
    def play(self):
        for c in self.controller.hand:
            if c.type == CardType.SPELL and getattr(
                c.data, "spell_school", None
            ) == SpellSchool.SHADOW:
                return [Buff(self, "RLK_814e")]
        return []


class RLK_814e:
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


class CORE_CATA_002:
    """Calia Menethil — Battlecry: Resurrect your highest-Cost minion that died this game."""

    @staticmethod
    def play(self):
        deads = self.controller.graveyard.filter(type=CardType.MINION)
        if not deads:
            return []
        target = max(deads, key=lambda c: c.cost)
        return [Summon(self.controller, target.id)]


# --- SHAMAN ---


class CORE_WC_042:
    """Wailing Vapor — After you play an Elemental, gain +1 Attack."""
    events = Play(CONTROLLER, MINION + ELEMENTAL).on(Buff(SELF, "WC_042e"))


class WC_042e:
    tags = {GameTag.ATK: 1}


class CORE_AV_107:
    """Glaciate — Discover an 8-Cost minion. Summon and Freeze it."""
    play = Discover(CONTROLLER, RandomMinion(cost=8)).then(
        Summon(CONTROLLER, Discover.CARD).then(Freeze(Summon.CARD))
    )


# --- WARLOCK ---


class CORE_WON_096:
    """Dark Peddler — Battlecry: Discover a 1-Cost card."""
    play = DISCOVER(RandomCollectible(cost=1))


class CORE_SW_088:
    """Demonic Assault — Deal 3 damage. Summon two 1/3 Voidwalkers with Taunt."""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3), Summon(CONTROLLER, "CS2_065") * 2


# --- WARRIOR ---


class CORE_WON_350:
    """I Know a Guy — Discover a Taunt minion. Give it +1/+2."""
    play = Discover(CONTROLLER, RandomMinion(taunt=True)).then(
        Give(CONTROLLER, Discover.CARD), Buff(Discover.CARD, "CORE_WON_350e")
    )


class CORE_WON_350e:
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 2}


class CORE_WON_337:
    """Ironforge Portal — Gain 4 Armor. Summon a random 4-Cost minion."""
    play = GainArmor(FRIENDLY_HERO, 4), Summon(CONTROLLER, RandomMinion(cost=4))
