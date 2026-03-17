# Hunter cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_014:
    """Verdant Dreamsaber"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_226:
    """Exotic Houndmaster"""

    play = Buff(RANDOM(FRIENDLY_MINIONS + BEAST), "EX1_538t")


class EDR_227:
    """Umbraclaw"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_416:
    """Shepherd's Crook"""

    play = Summon(CONTROLLER, "EDR_416t")


class EDR_416t:
    """Sleepy Sheep"""

    taunt = True


class EDR_480:
    """Goldrinn"""

    deathrattle = CastSpell("EDR_480e")


class EDR_480e:
    """Greatwolf's Ferocity"""

    play = Buff(FRIENDLY_MINIONS, "+4/+4")


class EDR_481:
    """Mythical Runebear"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_853:
    """Broll Bearmantle"""

    play = Buff(FRIENDLY_HAND, "EDR_853e")


class EDR_853e:
    """Verdant Dreamsaber"""
    atk = 1
    health = 1


##
# Spells


class EDR_261:
    """Amphibian's Spirit"""

    play = Buff(ALL_MINIONS, "EDR_261e")


class EDR_261e:
    """Amphibian's Spirit"""

    events = Death(FRIENDLY_MINIONS).on(Destroy(ENEMY_MINIONS))


class EDR_262:
    """Spirit Bond"""

    play = Buff(FRIENDLY_MINIONS, "EDR_261e")


class EDR_263:
    """Grace of the Greatwolf"""

    play = Choice(CONTROLLER, ["EDR_263a", "EDR_263b"]).then(
        Battlecry(Choice.CARD, None)
    )


class EDR_263a:
    """Greatwolf's Ferocity"""

    play = Buff(FRIENDLY_MINIONS, "+4/+4")


class EDR_263b:
    """Greatwolf's Guidance"""

    play = Summon(CONTROLLER, RandomMinion(cost=4))


class EDR_850p:
    """Blessing of the Wolf"""

    play = Summon(CONTROLLER, "EDR_850pe")


class EDR_850pe:
    """Playful Pup"""

    rush = True


class FIR_909:
    """Bursting Shot"""

    play = Destroy(ALL_MINIONS + TAUNT)


class FIR_953:
    """Magma Hound"""

    deathrattle = Damage(RANDOM_ENEMY_CHARACTER, 2)


class FIR_960:
    """Tending Dragonkin"""

    events = OWN_SPELL_PLAY.on(Buff(SELF, "CS2_101e"))


##
# Dream Cards (from EDR_100 and EDR_101)


class EDR_100t10:
    """Nightmare Scales"""

    divine_shield = True


class EDR_100t10e:
    """Nightmare Scales"""

    pass


class EDR_101t:
    """Blinding Carapace"""

    divine_shield = True
    rush = True


class EDR_101t1:
    """Blinding Carapace"""

    divine_shield = True
    lifesteal = True


class EDR_101t2:
    """Blinding Carapace"""

    divine_shield = True
    reborn = True


class EDR_101t3:
    """Blinding Carapace"""

    divine_shield = True
    taunt = True


class EDR_101t4:
    """Blinding Carapace"""

    divine_shield = True
    poisonous = True


class EDR_101t5:
    """Blinding Carapace"""

    rush = True
    lifesteal = True


class EDR_101t6:
    """Blinding Carapace"""

    rush = True
    reborn = True


class EDR_101t7:
    """Blinding Carapace"""

    rush = True
    taunt = True


class EDR_101t8:
    """Blinding Carapace"""

    rush = True
    poisonous = True


class EDR_101t9:
    """Blinding Carapace"""

    lifesteal = True
    reborn = True


class EDR_101t10:
    """Blinding Carapace"""

    lifesteal = True
    taunt = True


class EDR_101t11:
    """Blinding Carapace"""

    lifesteal = True
    poisonous = True


class EDR_101t12:
    """Blinding Carapace"""

    reborn = True
    taunt = True


class EDR_101t13:
    """Blinding Carapace"""

    reborn = True
    poisonous = True


class EDR_101t14:
    """Blinding Carapace"""

    taunt = True
    poisonous = True
