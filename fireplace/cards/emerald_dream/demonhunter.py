# Demonhunter cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_421:
    """Omen"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +4})


class EDR_493:
    """Alara'shi"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +3})


class EDR_493e2:
    """Demon Form"""

    atk = 3
    health = 3


class EDR_521e1:
    """Tricky"""

    pass


class EDR_521e2:
    """Tricked"""

    pass


class EDR_841:
    """Dreadsoul Corrupter"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_842:
    """Defiled Spear"""

    lifesteal = True


class EDR_890:
    """Nightmare Dragonkin"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_891:
    """Ravenous Felhunter"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class EDR_892:
    """Ferocious Felbat"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +2})


class FIR_904:
    """Felfire Blaze"""

    lifesteal = True


class FIR_952:
    """Scorchreaver"""

    deathrattle = Damage(ENEMY_HERO, 2)


##
# Spells


class EDR_820:
    """Wyvern's Slumber"""

    play = Choice(CONTROLLER, ["EDR_820a", "EDR_820b"]).then(Battlecry(Choice.CARD, None))


class EDR_820a:
    """Encroaching Fear"""

    play = Damage(ALL_MINIONS, 1)


class EDR_820b:
    """Awoken Darkness"""

    play = Buff(ENEMY_MINIONS, "EDR_570e")


class EDR_840:
    """Grim Harvest"""

    play = Choice(CONTROLLER, ["EDR_840t", "EDR_840t1", "EDR_840t2"]).then(Summon(CONTROLLER, Choice.CARD))


class EDR_840t:
    """Hound Dreadseed"""

    taunt = True


class EDR_840t1:
    """Crow Dreadseed"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_840t1e:
    """Dreaming Hound"""

    pass


class EDR_840t1e1:
    """Dreaming Crow"""

    pass


class EDR_840t2:
    """Serpent Dreadseed"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_840t2e1:
    """Dreaming Serpent"""

    pass


class EDR_840te:
    """Hound's Fangs"""

    pass


class EDR_840te2:
    """Eternal Nightmare"""

    pass


class EDR_882:
    """Jumpscare!"""

    play = Damage(ENEMY_MINIONS, 2)


class FIR_902:
    """Sigil of Cinder"""

    play = Damage(ALL_MINIONS, 1)
