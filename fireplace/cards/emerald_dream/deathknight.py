# Death Knight cards from EMERALD_DREAM expansion
from ..utils import *


##
# Minions


class EDR_810:
    """Hideous Husk"""

    events = Death(ENEMY_MINIONS).on(Buff(SELF, "EDR_810e"))


class EDR_810e:
    """Siphoned Strength"""

    atk = 1


class EDR_810t:
    """Bloated Leech"""

    deathrattle = Damage(ENEMY_HERO, 2)


class EDR_811:
    """Rite of Atrocity"""

    play = Buff(RANDOM(ALL_MINIONS), "EDR_811e")


class EDR_811e:
    """Empowered"""

    pass


class EDR_812:
    """Grotesque Runeblade"""

    lifesteal = True


class EDR_813:
    """Morbid Swarm"""

    play = Summon(CONTROLLER, "EDR_813at") * 2


class EDR_813a:
    """Contaminated Colony"""

    play = Summon(CONTROLLER, "EDR_813at") * 2


class EDR_813at:
    """Ant Husk"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_813b:
    """Bug Bites"""

    play = Damage(TARGET, 4)


class EDR_814:
    """Infested Breath"""

    play = Damage(TARGET, 2), Summon(CONTROLLER, "EDR_814t")


class EDR_814t:
    """Leech"""

    deathrattle = Heal(FRIENDLY_HERO, 1)


class EDR_815:
    """Corpse Flower"""

    events = Summon(ENEMY_MINIONS).on(Buff(SELF, "EDR_815e"))


class EDR_815e:
    """Pestilence"""

    atk = 1
    health = 1


class EDR_816:
    """Monstrous Mosquito"""

    events = OWN_TURN_END.on(Buff(FRIENDLY_MINIONS, "CS2_101e"))


class EDR_817:
    """Sanguine Infestation"""

    play = Summon(CONTROLLER, "EDR_817t") * 2


class EDR_817t:
    """Blood Matron"""

    deathrattle = Draw(CONTROLLER)


class EDR_818:
    """Nythendra"""

    deathrattle = Summon(CONTROLLER, "EDR_818t") * 5


class EDR_818t:
    """Nythendric Beetle"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_819:
    """Ursoc"""

    battlecry = Damage(ALL_MINIONS - SELF, 1)


class EDR_819e:
    """Grief"""

    pass


class FIR_900:
    """Cremate"""

    play = Discover(RandomMinion(rarity=Rarity.LEGENDARY))


class FIR_901:
    """Frostburn Matriarch"""

    play = Summon(CONTROLLER, "FIR_901t")


class FIR_901t:
    """Frostburn Broodling"""

    taunt = True


class FIR_951:
    """Volcoross"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class FIR_951t2:
    """Tail Smash"""

    deathrattle = Buff(SELF, "+10/+10")


class FIR_951t3:
    """Fiery Chomp"""

    deathrattle = Buff(SELF, "+20/+20")


class FIR_951t4:
    """Lava Wave"""

    deathrattle = Buff(SELF, "+30/+30")
