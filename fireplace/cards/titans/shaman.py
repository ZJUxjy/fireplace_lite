from ..utils import *


##
# TTN_415: Khaz'goroth (6费 4/5)
# 泰坦。使用技能后，获得免疫并攻击随机敌方随从

class TTN_415:
    """Khaz'goroth"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_415t", "TTN_415t2", "TTN_415t3"]
    ability_used = Buff(SELF, "TTN_415ae")


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


def _golganneth_first_spell(entities, source):
    """Select friendly hand spells if no spell has been cast this turn yet."""
    if any(
        c.type == CardType.SPELL and c.turn_played == source.game.turn
        for c in source.controller.cards_played_this_game
    ):
        return []
    return [e for e in source.controller.hand if e.type == CardType.SPELL]


##
# TTN_800: Golganneth, the Thunderer (6费 5/7)
# 泰坦。被动：你每回合第一张法术费用减少3

class TTN_800:
    """Golganneth, the Thunderer"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_800t", "TTN_800t2", "TTN_800t3"]

    # 被动：每回合第一张法术费用减少3（持续光环）
    update = Refresh(FuncSelector(_golganneth_first_spell), {GameTag.COST: -3})


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


# TTN_800t3: Shargahn's Wrath - Draw 3 Overload cards from your deck
class TTN_800t3:
    """Shargahn's Wrath"""

    def play(self):
        import random as _random
        overload_cards = [c for c in self.controller.deck if getattr(c, "overload", 0) > 0]
        _random.shuffle(overload_cards)
        for card in overload_cards[:3]:
            yield Draw(CONTROLLER, CARD(card))
