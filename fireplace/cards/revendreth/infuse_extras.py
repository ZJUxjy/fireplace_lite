from ..utils import *


##
# Additional INFUSE cards (Murder at Castle Nathria + Maw and Disorder
# mini-set + Onyxia's Lair / NX2). All cards follow the same template:
#   progress_total = <threshold>
#   class Hand: events = Death(<filter>).on(AddProgress(SELF, Death.ENTITY))
#   reward = Morph(SELF, "<infused_id>")
#
# The infused form is a separate card class declared in CardDefs.xml; the
# "play" effect on the infused form models the upgraded behavior.


# REV_017 — Insatiable Devourer (9-cost minion).
# Battlecry: Devour an enemy minion. Infuse(5): also neighbors.
class REV_017:
    """Insatiable Devourer"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    # "Devour" is approximated as: gain that minion's stats then destroy it.
    play = (
        Buff(SELF, "REV_017e").then(
            SetCurrentHealth(SELF, CURRENT_HEALTH(SELF) + CURRENT_HEALTH(TARGET))
        ),
        Destroy(TARGET),
    )
    progress_total = 5

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_017t")


REV_017e = buff(atk=1)


class REV_017t:
    """Insatiable Devourer (Infused)"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    play = (
        Buff(SELF, "REV_017e"),
        Destroy(TARGET + TARGET_ADJACENT),
    )


# REV_601 — Frozen Touch (3-cost spell).
# Deal 3 damage. Infuse(3): Add a copy of Frozen Touch to your hand.
class REV_601:
    """Frozen Touch"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3)
    progress_total = 3

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_601t")


class REV_601t:
    """Frozen Touch (Infused)"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 3), Give(CONTROLLER, "REV_601")


# REV_835 — Imp King Rafaam (6-cost minion).
# Battlecry: Resurrect 4 friendly Imps. Infuse(5): give Imps +2/+2.
# (Resurrection from graveyard not modeled — summon random demons instead.)
class REV_835:
    """Imp King Rafaam"""

    play = Summon(CONTROLLER, RandomDemon()) * 4
    progress_total = 5

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_835t")


class REV_835t:
    """Imp King Rafaam (Infused)"""

    play = (
        Summon(CONTROLLER, RandomDemon()) * 4,
        Buff(FRIENDLY_MINIONS + DEMON, "REV_835te"),
    )


REV_835te = buff(atk=2, health=2)


# REV_843 — Sinfueled Golem (7-cost minion).
# Infuse(3): Gain stats equal to the Attack of the minions that Infused this.
# (Simplified: gain +2/+2 per infusing minion via stacking buff.)
class REV_843:
    """Sinfueled Golem"""

    progress_total = 3

    class Hand:
        events = Death(FRIENDLY + MINION).on(
            AddProgress(SELF, Death.ENTITY),
            Buff(SELF, "REV_843e"),
        )

    reward = Morph(SELF, "REV_843t")


REV_843e = buff(atk=2, health=2)


class REV_843t:
    """Sinfueled Golem (Infused)"""
    pass


# REV_956 — Priest of the Deceased (2-cost minion).
# Taunt. Infuse(3): Gain +2/+2.
class REV_956:
    """Priest of the Deceased"""

    progress_total = 3

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_956t")


class REV_956t:
    """Priest of the Deceased (Infused)"""
    pass


# REV_957 — Murlocula (4-cost minion).
# Lifesteal. Infuse(4): This costs (0). (Cost reduction not modeled — morph
# to the infused form which simply has cost 0 in CardDefs.xml.)
class REV_957:
    """Murlocula"""

    progress_total = 4

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_957t")


class REV_957t:
    """Murlocula (Infused)"""
    pass


# REV_352 — Stonebound Gargon (4-cost minion).
# Rush. Infuse(3): also damages neighbors when attacking. (Cleave passive
# isn't easily modeled — morph to the infused form which has its own data.)
class REV_352:
    """Stonebound Gargon"""

    progress_total = 3

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_352t")


class REV_352t:
    """Stonebound Gargon (Infused)"""
    pass


# REV_920 — Convincing Disguise (1-cost spell).
# Transform a friendly minion into one that costs (2) more. Infuse(4): Transform all.
class REV_920:
    """Convincing Disguise"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Morph(TARGET, RandomMinion(cost=COST(TARGET) + 2))
    progress_total = 4

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_920t")


class REV_920t:
    """Convincing Disguise (Infused)"""

    play = Morph(FRIENDLY_MINIONS, RandomMinion(cost=COST(FRIENDLY_MINIONS) + 2))


# REV_933 — Imbued Axe (3-cost weapon).
# After your hero attacks, give your damaged minions +1/+2. Infuse(2): +2/+2.
class REV_933:
    """Imbued Axe"""

    events = Attack(FRIENDLY_HERO).after(Buff(FRIENDLY_MINIONS + DAMAGED, "REV_933e"))
    progress_total = 2

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_933t")


REV_933e = buff(atk=1, health=2)


class REV_933t:
    """Imbued Axe (Infused)"""

    events = Attack(FRIENDLY_HERO).after(Buff(FRIENDLY_MINIONS + DAMAGED, "REV_933te"))


REV_933te = buff(atk=2, health=2)


# REV_938 — Door of Shadows (2-cost spell).
# Draw a spell. Infuse(2): also add a temporary copy to hand.
# (Temporary not implemented — add a normal copy to hand.)
class REV_938:
    """Door of Shadows"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + SPELL))
    progress_total = 2

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_938t")


class REV_938t:
    """Door of Shadows (Infused)"""

    # Draw a random spell, and add another copy to hand.
    play = ForceDraw(RANDOM(FRIENDLY_DECK + SPELL)), Give(CONTROLLER, RANDOM(FRIENDLY_DECK + SPELL))


# MAW_033 — Sylvanas, the Accused (6-cost minion).
# Battlecry: Destroy an enemy minion. Infuse(7): Take control instead.
class MAW_033:
    """Sylvanas, the Accused"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    play = Destroy(TARGET)
    progress_total = 7

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "MAW_033t")


class MAW_033t:
    """Sylvanas, the Accused (Infused)"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    play = Steal(TARGET)


# MAW_009 — Shadehound (5-cost Beast minion).
# Whenever this attacks, give your other Beasts +2/+2.
# Infuse(3 Beasts): Gain Rush. (Race-conditional Hand event.)
class MAW_009:
    """Shadehound"""

    events = Attack(SELF).on(Buff(FRIENDLY_MINIONS + BEAST - SELF, "MAW_009e"))
    progress_total = 3

    class Hand:
        events = Death(FRIENDLY + MINION + BEAST).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "MAW_009t")


MAW_009e = buff(atk=2, health=2)


class MAW_009t:
    """Shadehound (Infused)"""

    events = Attack(SELF).on(Buff(FRIENDLY_MINIONS + BEAST - SELF, "MAW_009e"))


# NX2_011 — Life from Death (6-cost spell).
# Draw 3 cards. Infuse(6): This costs (1).
class NX2_011:
    """Life from Death"""

    play = Draw(CONTROLLER), Draw(CONTROLLER), Draw(CONTROLLER)
    progress_total = 6

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "NX2_011t")


class NX2_011t:
    """Life from Death (Infused)"""

    play = Draw(CONTROLLER), Draw(CONTROLLER), Draw(CONTROLLER)


# NX2_005 — Stitched Creation (3-cost minion).
# Combo: Gain +2/+2. Infuse(2): Gain +3/+3. Manathirst: +4/+4.
class NX2_005:
    """Stitched Creation"""

    combo = Buff(SELF, "NX2_005ce")
    progress_total = 2

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "NX2_005t")


NX2_005ce = buff(atk=2, health=2)


class NX2_005t:
    """Stitched Creation (Infused)"""

    play = Buff(SELF, "NX2_005te")


NX2_005te = buff(atk=3, health=3)


##
# === Final batch of INFUSE cards ===
# Faithful per real Hearthstone effect (with simplifications noted where the
# underlying mechanic — Discover Relics, Endlessly Infuse counter, in-deck
# infuse aura — is engine-deep).


# MAW_003 — Totemic Evidence (Shaman 1-cost spell).
# Choose a basic Totem and summon it. Infuse(2 Totems): Summon all 4 instead.
# Real card uses Choose-One; we approximate with a random pick (engine
# choose-one for spells with 4 sub-choices is non-trivial to wire here).
class MAW_003:
    """Totemic Evidence"""

    play = Summon(CONTROLLER, RandomBasicTotem())
    progress_total = 2

    class Hand:
        events = Death(FRIENDLY + MINION + TOTEM).on(
            AddProgress(SELF, Death.ENTITY)
        )

    reward = Morph(SELF, "MAW_003t")


class MAW_003t:
    """Totemic Evidence (Infused)"""

    # Summon all 4 basic totems.
    play = (
        Summon(CONTROLLER, "CS2_050"),
        Summon(CONTROLLER, "CS2_051"),
        Summon(CONTROLLER, "CS2_052"),
        Summon(CONTROLLER, "NEW1_009"),
    )


# MAW_031 — Afterlife Attendant (Neutral 3-cost 3/4 minion).
# "Your Infuse cards also Infuse while in your deck."
# This is an aura that expands the existing per-card Hand.events listener to
# also fire while the card is in deck — a structural engine extension that
# would require wiring per-INFUSE-card Deck.events listeners. Modeled here
# as a custom in-play event: on friendly minion death, iterate the friendly
# deck and add progress to every INFUSE-tagged card found there.
INFUSE_TAG = EnumSelector(GameTag.INFUSE)


class MAW_031:
    """Afterlife Attendant"""

    events = Death(FRIENDLY + MINION).on(
        AddProgress(FRIENDLY_DECK + INFUSE_TAG, Death.ENTITY)
    )


# REV_336 — Plot of Sin (Druid 3-cost spell).
# Summon two 2/2 Treants. Infuse(2): Two 5/5 Ancients instead.
class REV_336:
    """Plot of Sin"""

    play = Summon(CONTROLLER, "REV_336t2") * 2
    progress_total = 2

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_336t4")


class REV_336t4:
    """Plot of Sin (Infused)"""

    play = Summon(CONTROLLER, "REV_336t3") * 2


# REV_350 — Frenzied Fangs (Hunter 2-cost spell).
# Summon two 2/1 Bats. Infuse(2): Give them +1/+2.
class REV_350:
    """Frenzied Fangs"""

    play = Summon(CONTROLLER, "REV_350t") * 2
    progress_total = 2

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_350t2")


class REV_350t2:
    """Frenzied Fangs (Infused)"""

    # Summon two 2/1 Bats and buff them with +1/+2.
    play = (
        Summon(CONTROLLER, "REV_350t").then(Buff(Summon.CARD, "REV_350e")),
        Summon(CONTROLLER, "REV_350t").then(Buff(Summon.CARD, "REV_350e")),
    )


REV_350e = buff(atk=1, health=2)


# REV_353 — Huntsman Altimor (Hunter 7-cost legendary 5/4).
# Battlecry: Summon a Gargon Companion (Hecutis/Barghast/Margore — random).
# Infuse(3): Summon 2 instead. Infuse(3) AGAIN (chained): Summon all 3!
# This is a multi-stage infuse — implemented via Morph chain
# REV_353 -> REV_353t -> REV_353t2 (the final form summons all 3).
GARGON_COMPANIONS = ("REV_353t3", "REV_353t4", "REV_353t5")


class REV_353:
    """Huntsman Altimor"""

    play = Summon(CONTROLLER, RandomID(*GARGON_COMPANIONS))
    progress_total = 3

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_353t")


class REV_353t:
    """Huntsman Altimor (Infused once — summons 2)"""

    play = Summon(CONTROLLER, RandomID(*GARGON_COMPANIONS)) * 2
    progress_total = 3

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_353t2")


class REV_353t2:
    """Huntsman Altimor (Fully Infused — summons all 3)"""

    play = (
        Summon(CONTROLLER, "REV_353t3"),
        Summon(CONTROLLER, "REV_353t4"),
        Summon(CONTROLLER, "REV_353t5"),
    )


class REV_353t3:
    """Hecutis (3-cost 4/4 Taunt)"""
    tags = {GameTag.TAUNT: True}


class REV_353t4:
    """Barghast (3-cost 2/4) — Your other minions have +1 Attack"""
    update = Refresh(FRIENDLY_MINIONS - SELF, {GameTag.ATK: 1})


class REV_353t5:
    """Margore (3-cost 4/2 Charge)"""
    tags = {GameTag.CHARGE: True}


# REV_906 — Sire Denathrius (Neutral 10-cost legendary 10/10).
# Lifesteal. Battlecry: Deal 5 damage amongst enemies.
# "Endlessly Infuse" — every 5 friendly minion deaths grants +1 damage.
# Modeled as Morph chain through escalating forms (REV_906 -> REV_906t).
# After REV_906t fires, it morphs to itself (resetting progress) and stacks
# a self-buff that records cumulative cycles. We expose the cumulative
# damage via a ladder of damage hits scaled by Count.
class REV_906:
    """Sire Denathrius"""

    play = Hit(RANDOM_ENEMY_CHARACTER, 1) * 5
    progress_total = 5

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_906t")


class REV_906t:
    """Sire Denathrius (Infused, +1 damage per Endless cycle)"""

    # Deal 6 damage amongst enemies (one extra per cycle, but engine cap:
    # we only model the first cycle — further cycles re-morph to self and
    # stack REV_906te which is referenced for visual flag only).
    play = Hit(RANDOM_ENEMY_CHARACTER, 1) * 6
    progress_total = 5

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    # Endlessly Infuse: re-morph to self and apply a stacking marker buff.
    # Each cycle increments REV_906te so the eventual Battlecry reflects
    # accumulated cycles via the marker count (note: marker is purely
    # informational — the play action still fires fixed 6 hits since LazyNum
    # support for "6 + buff_count" inside Hit count multiplier requires
    # Count selectors that aren't trivially composed here).
    reward = Buff(SELF, "REV_906te"), ClearProgress(SELF)


REV_906te = buff(atk=0, health=0)


# REV_935 — Party Favor Totem (Shaman 3-cost 0/3 minion).
# At the end of your turn, summon a random basic Totem.
# Infuse(2): Summon two instead.
class REV_935:
    """Party Favor Totem"""

    events = OWN_TURN_END.on(Summon(CONTROLLER, RandomBasicTotem()))
    progress_total = 2

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_935t")


class REV_935t:
    """Party Favor Totem (Infused)"""

    events = OWN_TURN_END.on(Summon(CONTROLLER, RandomBasicTotem()) * 2)


# REV_937 — Artificer Xy'mox (Demon Hunter 8-cost legendary 8/8).
# Battlecry: Discover and cast a Relic. Infuse(3): Cast all three Relics.
# "Relic" is a cycling DH spell mechanic not implemented in fireplace.
# Simplification: discover a random Demon Hunter spell from your deck.
# Infused: cast 3 random DH spells.
class REV_937:
    """Artificer Xy'mox"""

    play = DISCOVER(RandomSpell(card_class=CardClass.DEMONHUNTER))
    progress_total = 3

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_937t")


class REV_937t:
    """Artificer Xy'mox (Infused)"""

    # Cast 3 random DH spells (simplified: just summon 3 random DH minions
    # since "cast spell from nothing" engine plumbing is involved).
    play = Give(CONTROLLER, RandomSpell(card_class=CardClass.DEMONHUNTER)) * 3


# REV_958 — Buffet Biggun (Paladin 4-cost 2/4 minion).
# Battlecry: Summon two Silver Hand Recruits.
# Infuse(2): Give them +2 Attack and Divine Shield.
class REV_958:
    """Buffet Biggun"""

    play = Summon(CONTROLLER, "CS2_101t") * 2
    progress_total = 2

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))

    reward = Morph(SELF, "REV_958t")


class REV_958t:
    """Buffet Biggun (Infused)"""

    # Summon two Recruits then buff them with REV_958e (+2 atk + Divine Shield).
    play = (
        Summon(CONTROLLER, "CS2_101t").then(
            Buff(Summon.CARD, "REV_958e"),
            SetTags(Summon.CARD, {GameTag.DIVINE_SHIELD: True}),
        ),
        Summon(CONTROLLER, "CS2_101t").then(
            Buff(Summon.CARD, "REV_958e"),
            SetTags(Summon.CARD, {GameTag.DIVINE_SHIELD: True}),
        ),
    )


REV_958e = buff(atk=2)
