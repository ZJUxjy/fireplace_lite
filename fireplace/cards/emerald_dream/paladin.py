# Paladin cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_251:
    """Dragonscale Armaments"""

    play = Buff(FRIENDLY_MINIONS, "CS2_101e")


class EDR_253:
    """Ursine Maul"""

    divine_shield = True


class EDR_256:
    """Dreamwarden"""

    deathrattle = Draw(CONTROLLER)


class EDR_257:
    """Lightmender"""

    play = Choice(CONTROLLER, ["EDR_257a", "EDR_257b"]).then(Battlecry(Choice.CARD, None))


class EDR_257a:
    """Holy Bond"""

    play = Heal(FRIENDLY_HERO, 5)


class EDR_257ae:
    """Holy Bonded"""

    pass


class EDR_257b:
    """Embrace of the Light"""

    play = GainArmor(FRIENDLY_HERO, 5)


class EDR_257be:
    """Light's Embrace"""

    pass


class EDR_258:
    """Toreth the Unbreaking"""

    divine_shield = True


class EDR_259:
    """Ursol"""

    taunt = True
    play = Buff(FRIENDLY_MINIONS, "EDR_259e1")


class EDR_259e1:
    """Ursol's Aura"""

    taunt = True


class EDR_451:
    """Goldpetal Drake"""

    divine_shield = True
    taunt = True


##
# Spells


class EDR_252:
    """Mark of Ursol"""

    play = Buff(FRIENDLY_MINIONS, "EDR_252e")


class EDR_252e:
    """Mark of Ursol"""

    events = Attack(SELF, ALL_MINIONS).after(Damage(ENEMY_MINIONS, 1))


class EDR_252e1:
    """Might of Ursol"""
    atk = 3
    health = 3


class EDR_255:
    """Renewing Flames"""

    play = Summon(CONTROLLER, "CS2_101t"), Summon(CONTROLLER, "CS2_102t"), Summon(CONTROLLER, "CS2_103t")


class EDR_264:
    """Aegis of Light"""

    play = GainArmor(FRIENDLY_HERO, 4), Draw(CONTROLLER)


class EDR_445p:
    """Blessing of the Dragon"""

    play = Summon(CONTROLLER, "EDR_445pt3")


class EDR_445pt3:
    """Emerald Portal"""

    pass


class FIR_914:
    """Smoldering Strength"""

    play = Buff(FRIENDLY_MINIONS, "FIR_914e")


class FIR_914e:
    """Smoldering Strength"""
    atk = 1
    health = 1


class FIR_941:
    """Searing Reflection"""

    play = Summon(CONTROLLER, Copy(RANDOM_FRIENDLY_MINION))


class FIR_941e1:
    """Searing Reflection"""

    pass


class FIR_961:
    """Ashleaf Pixie"""

    play = Buff(ALL_MINIONS, "CS2_101e")
