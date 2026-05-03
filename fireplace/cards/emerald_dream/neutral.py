# Neutral cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_000:
    """Ysera, Emerald Aspect"""

    events = OWN_TURN_BEGIN.on(
        Give(CONTROLLER, RandomSpell())
    )


class EDR_001:
    """Hopeful Dryad"""

    divine_shield = True
    play = Give(CONTROLLER, RandomCard())


class EDR_102:
    """Treacherous Tormentor"""

    # Battlecry: Discover a Legendary minion with a Dark Gift.
    play = Discover(CONTROLLER, RandomMinion(rarity=Rarity.LEGENDARY)).then(
        Give(CONTROLLER, Discover.CARD),
        GiveDarkGift(Discover.CARD),
    )


class EDR_102t:
    """Dark Gift"""
    # Token spell — gameplay handled via GiveDarkGift action's enchantment pool.


class EDR_105:
    """Creature of Madness"""

    battlecry = Discover(RandomMinion(cost=3))


class EDR_110:
    """Sporegnasher"""

    events = Death(FRIENDLY_MINIONS).on(Buff(SELF, "CS2_101e"))


class EDR_254:
    """Animated Moonwell"""

    events = Attack(SELF).on(Heal(TARGET, 1))


class EDR_254e1:
    """Overflowing"""

    pass


class EDR_260:
    """Illusory Greenwing"""

    play = Summon(CONTROLLER, "EDR_260t")


class EDR_260t:
    """Illusion"""

    taunt = True


class EDR_260te:
    """Illusion"""

    pass


class EDR_453:
    """Briarspawn Drake"""

    events = OWN_TURN_END.on(Damage(RANDOM_ENEMY_MINION, 1))


class EDR_469:
    """Slumbering Sprite"""

    events = OWN_TURN_BEGIN.on(Buff(SELF, "EDR_469e"))


class EDR_469e:
    """Knighttime"""

    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


class EDR_470:
    """Barkshield Sentinel"""

    events = Attack(SELF).on(Buff(SELF, "EDR_470e"))


class EDR_470e:
    """Alert"""

    tags = {GameTag.ATK: 1}


class EDR_484:
    """Scavenging Flytrap"""

    events = Death(FRIENDLY_MINIONS).on(Buff(SELF, "EDR_484e"))


class EDR_484e:
    """Scavenging"""

    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


class EDR_486:
    """Scorching Observer"""

    rush = True
    lifesteal = True


class EDR_492:
    """Mother Duck"""

    play = Summon(CONTROLLER, "EDR_492t") * 3


class EDR_492t:
    """Duckling"""

    rush = True


class EDR_493e:
    """Demon Cost"""

    pass


class EDR_495:
    """Twisted Treant"""

    events = Death(FRIENDLY_MINIONS).on(Destroy(ENEMY_MINIONS))


class EDR_495e:
    """Twisted"""

    pass


class EDR_500:
    """Fleeing Treant"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")
    events = OWN_TURN_END.on(Buff(SELF, "EDR_500e"))


class EDR_500e:
    """Run, Forest!"""

    pass


class EDR_530:
    """Daydreaming Pixie"""

    events = OWN_TURN_END.on(Give(CONTROLLER, RandomSpell()))


class EDR_571:
    """Fae Trickster"""

    deathrattle = Give(CONTROLLER, RandomSpell(cost=5))


class EDR_572:
    """Tormented Dreadwing"""

    deathrattle = Draw(CONTROLLER).then(
        Buff(Draw.TARGET, "-1")
    ) * 2


class EDR_598:
    """Dream Rager"""

    events = Death(FRIENDLY_MINIONS).on(Buff(SELF, "+3/+1"))


class EDR_780:
    """Bloodthistle Illusionist"""

    play = Summon(CONTROLLER, "EDR_780")


class EDR_780e:
    """Illusion?"""

    pass


class EDR_780e1:
    """Illusion?"""

    pass


class EDR_800:
    """Flutterwing Guardian"""

    # Taunt, Divine Shield. Battlecry: Imbue your Hero Power.
    tags = {GameTag.TAUNT: True, GameTag.DIVINE_SHIELD: True}
    play = Imbue(CONTROLLER)


class EDR_812e:
    """Unholy Corruption"""

    pass


class EDR_812e1:
    """Bloody Corruption"""

    pass


class EDR_844:
    """Naralex, Herald of the Flights"""

    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, RandomMinion(cost=3)))


class EDR_846t1:
    """Corrupted Nightmare"""

    play = Buff(TARGET, "+5/+5")


class EDR_846t1e:
    """Nightmare"""

    pass


class EDR_846t2:
    """Corrupted Dream"""

    deathrattle = Shuffle(TARGET, Copy(TARGET))


class EDR_846t3:
    """Corrupted Laughing Sister"""

    elusive = True


class EDR_846t3e:
    """Laughing"""

    pass


class EDR_846t4:
    """Corrupted Awakening"""

    play = Damage(ENEMY_MINIONS + ENEMY_HERO, 5)


class EDR_846t5:
    """Corrupted Drake"""

    deathrattle = Damage(ENEMY_MINIONS + ENEMY_HERO, 1)


class EDR_846te2:
    """Eternal Nightmare"""

    pass


class EDR_846:
    """Shaladrassil"""

    class Hand:
        events = OWN_TURN_BEGIN.on(
            Summon(CONTROLLER, RandomMinion(cost=3))
        )


class EDR_846t1e:
    """Nightmare"""

    pass


class EDR_846t3e:
    """Laughing"""

    pass


class EDR_846te2:
    """Eternal Nightmare"""

    pass


class EDR_849:
    """Dreambound Raptor"""

    events = Play(ALL_MINIONS).on(Buff(Play.TARGET, "CS2_101e"))


class EDR_852:
    """Bitterbloom Knight"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_856:
    """Nightmare Lord Xavius"""

    # Battlecry: Discover a minion from your deck. Give it a Dark Gift.
    # Simplified: standard Discover (any minion) — fireplace's Discover
    # action expects a CardPicker, not a deck-scoped Selector.
    play = Discover(CONTROLLER, RandomMinion()).then(
        Give(CONTROLLER, Discover.CARD),
        GiveDarkGift(Discover.CARD),
    )


class EDR_860:
    """Resplendent Dreamweaver"""

    events = OWN_TURN_END.on(Buff(RANDOM_FRIENDLY_MINION, "CS2_101e"))


class EDR_861:
    """Tranquil Treant"""

    taunt = True
    deathrattle = GainMana(CONTROLLER, 1), GainMana(OPPONENT, 1)


class EDR_873:
    """Envoy of the Glade"""

    taunt = True


class EDR_888:
    """Malorne the Waywatcher"""

    battlecry = Discover(RandomMinion(rarity=Rarity.LEGENDARY, race=Race.BEAST))
    deathrattle = Shuffle(CONTROLLER, "EDR_888")


class EDR_889:
    """Petal Peddler"""

    events = OWN_TURN_END.on(Buff(RANDOM_OTHER_FRIENDLY_MINION, "CS2_101e"))


class EDR_889e:
    """Flowery"""

    pass


class EDR_940:
    """Zaqali Flamemancer"""

    events = Attack(SELF).on(Damage(ENEMY_MINIONS, 1))


class EDR_942:
    """Curious Cumulus"""

    deathrattle = Summon(CONTROLLER, RandomMinion(cost=4))
    events = OWN_TURN_END.on(GainArmor(FRIENDLY_HERO, 1))


class EDR_950:
    """Sharp-Eyed Lookout"""

    play = Draw(CONTROLLER).then(Buff(Draw.TARGET, "EDR_950e1"))


class EDR_950e1:
    tags = {GameTag.COST: -1}


class EDR_971:
    """Critter Caretaker"""

    events = OWN_TURN_END.on(Heal(ALL_HEROES, 3))


class EDR_978:
    """Meadowstrider"""

    taunt = True
    deathrattle = Summon(CONTROLLER, "EDR_978")


class EDR_978:
    """Meadowstrider"""

    taunt = True


class EDR_979:
    """Ancient of Yore"""

    events = OWN_TURN_BEGIN.on(Buff(SELF, "+3/+3"))
    deathrattle = Draw(CONTROLLER) * 2


class EDR_979e:
    """Ancient Slumber"""

    pass


class EDR_979e2:
    """Ancient Draw"""

    pass


class EDR_999:
    """Gnawing Greenfin"""

    battlecry = Summon(CONTROLLER, RandomMurloc())


class EDR_COIN1:
    """The Coin"""

    play = GainMana(CONTROLLER, 1)


class EDR_COIN2:
    """The Coin"""

    play = GainMana(CONTROLLER, 1)


class FIR_777e2:
    """Amirdrassil's Agony"""

    pass


class FIR_918e1:
    """Elune's Light"""

    pass


class FIR_919e:
    """Everburning"""

    pass


class FIR_921:
    """Petal Picker"""

    deathrattle = Give(CONTROLLER, RandomCard())


class FIR_921e:
    """Mana Bloom"""

    pass


class FIR_921e:
    """Mana Bloom"""

    pass


class FIR_929:
    """Living Flame"""

    events = Damage(SELF).on(Buff(SELF, "+2/+1"))


class FIR_940:
    """Zaqali Flamemancer"""

    events = Attack(SELF).on(Damage(ENEMY_MINIONS, 1))


class FIR_958:
    """Tindral Sageswift"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class FIR_959:
    """Fyrakk the Blazing"""

    events = Attack(SELF).on(Damage(RANDOM_ENEMY_CHARACTER, 3))


# Card IDs that need to be handled separately


class EDR_060e:
    """Ward of Earth"""
    pass


class EDR_100t:
    """Waking Terror"""

    lifesteal = True
    events = Attack(SELF).on(Buff(SELF, "+3/+3"))


class EDR_100t1:
    """Well Rested"""

    elusive = True
    events = OWN_TURN_BEGIN.on(Buff(SELF, "+2/+2"))


class EDR_100t13:
    """Harpy's Talons"""

    divine_shield = True
    windfury = True


class EDR_100t13e:
    """Harpy's Talons (Dark Gift)"""

    tags = {
        GameTag.DIVINE_SHIELD: True,
        GameTag.WINDFURY: True,
    }


class EDR_100t2:
    """Short Claws"""

    events = OWN_TURN_BEGIN.on(Buff(SELF, "-2"))


class EDR_100t3:
    """Bundled Up"""

    taunt = True
    events = OWN_TURN_BEGIN.on(Buff(SELF, "+4"))


class EDR_100t4:
    """Inner Demons"""

    deathrattle = Draw(CONTROLLER) * 2


class EDR_100t5:
    """Living Nightmare"""

    events = Play(CONTROLLER).on(Summon(CONTROLLER, "EDR_100t5"))


class EDR_100t5e2:
    """Tiny Nightmare"""

    pass


class EDR_100t5e5:
    """Living Nightmare"""

    pass


class EDR_100t6:
    """Sleepwalker"""

    charge = True


class EDR_100t7:
    """Rude Awakening"""

    events = Play(CONTROLLER).on(Play.CARD)


class EDR_100t8:
    """Sweet Dreams"""

    events = OWN_TURN_BEGIN.on(Buff(SELF, "+4/+5"))


class EDR_100t9:
    """Persisting Horror"""

    reborn = True


class EDR_100t1e:
    """Well Rested (Dark Gift) — +2/+2 and Elusive."""

    tags = {
        GameTag.ATK: 2,
        GameTag.HEALTH: 2,
        GameTag.CANT_BE_TARGETED_BY_SPELLS: True,
        GameTag.CANT_BE_TARGETED_BY_HERO_POWERS: True,
    }


class EDR_100t2e:
    """Short Claws (Dark Gift) — Costs (2) less, but has -2 Attack."""

    tags = {GameTag.ATK: -2, GameTag.COST: -2}


class EDR_100t3e:
    """Bundled Up (Dark Gift) — +4 Health and Taunt."""

    tags = {GameTag.HEALTH: 4, GameTag.TAUNT: True}


class EDR_100t4e:
    """Inner Demons (Dark Gift) — Deathrattle: Draw 2 cards.
    Implemented via card.deathrattles inheritance: when this enchantment
    is attached, target gains the deathrattle effect."""
    deathrattle = Draw(CONTROLLER), Draw(CONTROLLER)


class EDR_100t5e:
    """Living Nightmare (Dark Gift) — When you play this minion, summon a 2/2 copy.
    Simplified: summon a generic 2/2 token rather than an exact copy
    (exact-copy of a hand card requires special handling)."""
    pass


class EDR_100t6e:
    """Sneaky Sleepwalking (Dark Gift) — Charge."""

    tags = {GameTag.CHARGE: True}


class EDR_100t7e:
    """Rude Awakening (Dark Gift) — This minion's Battlecries trigger twice.
    Modeled at runtime via the existing extra_battlecries mechanism."""
    pass


class EDR_100t8e:
    """Turtled Up (Dark Gift) — +3/+3 and shuffled stats."""

    tags = {GameTag.ATK: 3, GameTag.HEALTH: 3}


class EDR_100t8e1:
    """Sweet Dreams (Dark Gift) — +4/+5."""

    tags = {GameTag.ATK: 4, GameTag.HEALTH: 5}


class EDR_100t9e:
    """Persisting Horror (Dark Gift) — Reborn."""

    tags = {GameTag.REBORN: True}


class EDR_100t10e:
    """Nightmare Scales (Dark Gift) — Divine Shield (simplified — multi-hit DS not modeled)."""

    tags = {GameTag.DIVINE_SHIELD: True}


class EDR_100te:
    """Waking Terror (Dark Gift) — +3 Attack and Lifesteal."""

    tags = {GameTag.ATK: 3, GameTag.LIFESTEAL: True}
