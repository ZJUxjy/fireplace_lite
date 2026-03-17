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


class EDR_102:
    """Treacherous Tormentor"""

    deathrattle = Give(OPPONENT, RandomCard())


class EDR_102t:
    """Dark Gift"""

    pass


class EDR_105:
    """Creature of Madness"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


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

    pass


class EDR_453:
    """Briarspawn Drake"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +4})


class EDR_469:
    """Slumbering Sprite"""

    events = OWN_TURN_BEGIN.on(Buff(SELF, "EDR_469e"))


class EDR_469e:
    """Knighttime"""
    atk = 1
    health = 1


class EDR_470:
    """Barkshield Sentinel"""

    events = Attack(SELF).on(Buff(SELF, "EDR_470e"))


class EDR_470e:
    """Alert"""
    atk = 1


class EDR_484:
    """Scavenging Flytrap"""

    events = Death(FRIENDLY_MINIONS).on(Buff(SELF, "EDR_484e"))


class EDR_484e:
    """Scavenging"""
    atk = 1
    health = 1


class EDR_486:
    """Scorching Observer"""

    deathrattle = Damage(ENEMY_HERO, 3)


class EDR_492:
    """Mother Duck"""

    deathrattle = Summon(CONTROLLER, "EDR_492t")


class EDR_492t:
    """Duckling"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


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


class EDR_500e:
    """Run, Forest!"""

    pass


class EDR_530:
    """Daydreaming Pixie"""

    deathrattle = Draw(CONTROLLER)


class EDR_571:
    """Fae Trickster"""

    battlecry = Give(OPPONENT, RandomCard())


class EDR_572:
    """Tormented Dreadwing"""

    deathrattle = Damage(ALL_MINIONS, 1)


class EDR_598:
    """Dream Rager"""

    events = Death(FRIENDLY_MINIONS).on(Buff(SELF, "+3/+1"))


class EDR_780:
    """Bloodthistle Illusionist"""

    battlecry = Copy(RANDOM(ENEMY_HAND))


class EDR_780e1:
    """Illusion?"""

    pass


class EDR_800:
    """Flutterwing Guardian"""

    divine_shield = True
    taunt = True


class EDR_812e:
    """Unholy Corruption"""

    pass


class EDR_812e1:
    """Bloody Corruption"""

    pass


class EDR_844:
    """Naralex, Herald of the Flights"""

    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, RandomMinion(cost=3)))


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

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_852:
    """Bitterbloom Knight"""

    deathrattle = Buff(FRIENDLY_MINIONS, "CS2_101e")


class EDR_856:
    """Nightmare Lord Xavius"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_860:
    """Resplendent Dreamweaver"""

    events = OWN_TURN_END.on(Buff(RANDOM_FRIENDLY_MINION, "CS2_101e"))


class EDR_861:
    """Tranquil Treant"""

    taunt = True


class EDR_873:
    """Envoy of the Glade"""

    taunt = True


class EDR_888:
    """Malorne the Waywatcher"""

    deathrattle = Shuffle(CONTROLLER, "EDR_888")


class EDR_889:
    """Petal Peddler"""

    deathrattle = Draw(CONTROLLER)


class EDR_889e:
    """Flowery"""

    pass


class EDR_942:
    """Curious Cumulus"""

    deathrattle = Summon(CONTROLLER, RandomMinion(cost=4))


class EDR_971:
    """Critter Caretaker"""

    deathrattle = Summon(CONTROLLER, RandomMinion(cost=1))


class EDR_978:
    """Meadowstrider"""

    taunt = True


class EDR_979:
    """Ancient of Yore"""

    deathrattle = Draw(CONTROLLER) * 2


class EDR_979e:
    """Ancient Slumber"""

    pass


class EDR_979e2:
    """Ancient Draw"""

    pass


class EDR_999:
    """Gnawing Greenfin"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +1})


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
    pass


class EDR_100t1:
    """Well Rested"""
    pass


class EDR_100t13:
    """Harpy's Talons"""
    pass


class EDR_100t13e:
    """Harpy's Talons"""
    pass


class EDR_100t2:
    """Short Claws"""
    pass


class EDR_100t3:
    """Bundled Up"""
    pass


class EDR_100t4:
    """Inner Demons"""
    pass


class EDR_100t5:
    """Living Nightmare"""
    pass


class EDR_100t5e2:
    """Tiny Nightmare"""
    pass


class EDR_100t5e5:
    """Living Nightmare"""
    pass


class EDR_100t6:
    """Sleepwalker"""
    pass


class EDR_100t7:
    """Rude Awakening"""
    pass


class EDR_100t8:
    """Sweet Dreams"""
    pass


class EDR_100t9:
    """Persisting Horror"""
    pass


class EDR_100t1e:
    """Well Rested"""
    pass


class EDR_100t2e:
    """Short Claws"""
    pass


class EDR_100t3e:
    """Bundled Up"""
    pass


class EDR_100t4e:
    """Inner Demons"""
    pass


class EDR_100t5e:
    """Living Nightmare"""
    pass


class EDR_100t6e:
    """Sneaky Sleepwalking"""
    pass


class EDR_100t7e:
    """Rude Awakening"""
    pass


class EDR_100t8e:
    """Turtled Up"""
    pass


class EDR_100t8e1:
    """Sweet Dreams"""
    pass


class EDR_100t9e:
    """Persisting Horror"""
    pass


class EDR_100t10e:
    """Nightmare Scales"""
    pass


class EDR_100te:
    """Waking Terror"""
    pass
