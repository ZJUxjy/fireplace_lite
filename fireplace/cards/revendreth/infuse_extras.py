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
