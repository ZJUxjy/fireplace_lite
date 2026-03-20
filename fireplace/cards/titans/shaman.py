from ..utils import *


##
# TTN_415: Khaz'goroth (6费 4/5)
# 泰坦。使用技能后，获得免疫并攻击随机敌方随从（简化：buff自身）

class TTN_415:
    """Khaz'goroth"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_415t", "TTN_415t2", "TTN_415t3"]
    ability_used = Buff(SELF, "TTN_415ae")


TTN_415ae = buff(+1, 0)  # 简化：每次使用技能+1攻击


# TTN_415t: Titanforge - Gain +2/+2. Draw a weapon.
class TTN_415t:
    """Titanforge"""

    play = Buff(SELF, "TTN_415te"), Summon(CONTROLLER, RandomWeapon())


TTN_415te = buff(+2, +2)


# TTN_415t2: Tempering - Gain +5 attack. Give hero +5 attack this turn.
class TTN_415t2:
    """Tempering"""

    play = Buff(SELF, "TTN_415t2e"), Buff(FRIENDLY_HERO, "TTN_415t2he")


TTN_415t2e = buff(+5, 0)
TTN_415t2he = buff(+5, 0)


# TTN_415t3: Heart of Flame - Gain +5 health. Give hero 5 armor.
class TTN_415t3:
    """Heart of Flame"""

    play = Buff(SELF, "TTN_415t3e"), GainArmor(FRIENDLY_HERO, 5)


TTN_415t3e = buff(0, +5)


##
# TTN_800: Golganneth, the Thunderer (6费 5/7)
# 泰坦。被动：你每回合第一张法术费用减少3（简化实现）

class TTN_800:
    """Golganneth, the Thunderer"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_800t", "TTN_800t2", "TTN_800t3"]


# TTN_800t: Roaring Oceans - Deal 3 to all enemies, restore 6 to all friendlies
class TTN_800t:
    """Roaring Oceans"""

    play = Hit(ENEMY_MINIONS | ENEMY_HERO, 3), Heal(FRIENDLY_MINIONS | FRIENDLY_HERO, 6)


# TTN_800t2: Lord of Skies - Deal 20 damage to a minion
class TTN_800t2:
    """Lord of Skies"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Hit(TARGET, 20)


# TTN_800t3: Shargahn's Wrath - Draw 3 Overload cards (simplified: draw 3 cards)
class TTN_800t3:
    """Shargahn's Wrath"""

    play = Draw(CONTROLLER) * 3
