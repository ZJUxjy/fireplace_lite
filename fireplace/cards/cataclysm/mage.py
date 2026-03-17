from ..utils import *
from hearthstone.enums import Race, Rarity, SpellSchool


##
# Minions

# CATA_458: 大法师卡雷 - 4费 4/4 传说
# 战吼：使你手牌和牌库中所有法术牌获得法术伤害+1。
class CATA_458:
    """Archmage Kalec"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 4,
        GameTag.ATK: 4,
        GameTag.HEALTH: 4,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.RARITY: Rarity.LEGENDARY,
        GameTag.COLLECTIBLE: True,
        GameTag.ELITE: True,
    }

    # 战吼：使你手牌和牌库中所有法术牌获得法术伤害+1
    play = Buff(FRIENDLY_HAND + SPELL, "CATA_458e"), Buff(FRIENDLY_DECK + SPELL, "CATA_458e")


class CATA_458e:
    """Kalec's Insight"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.SPELLPOWER: 1,
    }


# CATA_483: 不稳定的施法者 - 4费 2/5 稀有
# 法术伤害+1。战吼：如果你在本回合中用法术造成过伤害，召唤一个本随从的复制。
class CATA_483:
    """Unstable Spellcaster"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 4,
        GameTag.ATK: 2,
        GameTag.HEALTH: 5,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.CARDRACE: Race.ELEMENTAL,
        GameTag.RARITY: Rarity.RARE,
        GameTag.COLLECTIBLE: True,
    }

    # 法术伤害+1
    update = Refresh(CONTROLLER, {GameTag.SPELLPOWER: 1})

    # 战吼：如果你在本回合中用法术造成过伤害，召唤一个本随从的复制
    play = Find(Count(CARDS_PLAYED_THIS_TURN + SPELL) > 0) & Summon(CONTROLLER, ExactCopy(SELF))


# CATA_484: 冬泉雏龙 - 1费 1/2 普通
# 战吼：发现一张任意职业的法力值消耗为（1）的法术牌。
class CATA_484:
    """Winterspring Whelp"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 1,
        GameTag.ATK: 1,
        GameTag.HEALTH: 2,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.CARDRACE: Race.DRAGON,
        GameTag.RARITY: Rarity.COMMON,
        GameTag.COLLECTIBLE: True,
    }

    # 战吼：发现一张任意职业的法力值消耗为（1）的法术牌
    play = DISCOVER(RandomSpell(cost=1))


# CATA_487: 祈雨元素 - 2费 1/4 稀有
# 每回合中，你第一次用法术造成伤害时，获得+2攻击力。
class CATA_487:
    """Raincaller"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 2,
        GameTag.ATK: 1,
        GameTag.HEALTH: 4,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.CARDRACE: Race.ELEMENTAL,
        GameTag.RARITY: Rarity.RARE,
        GameTag.COLLECTIBLE: True,
    }

    # 每回合中，你第一次用法术造成伤害时，获得+2攻击力
    events = Damage(ENEMY_CHARACTERS, None, SPELL).on(Buff(SELF, "CATA_487e"))


class CATA_487e:
    """Brewing Storm"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.ATK: 2,
    }


# CATA_488: 沃坎诺斯 - 7费 4/8 传说 巨型+2
# 巨型+2。在你的回合结束时，对所有其他随从造成2点伤害。
class CATA_488:
    """Vulcanos"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 7,
        GameTag.ATK: 4,
        GameTag.HEALTH: 8,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.CARDRACE: Race.ELEMENTAL,
        GameTag.RARITY: Rarity.LEGENDARY,
        GameTag.COLLECTIBLE: True,
        GameTag.ELITE: True,
        GameTag.COLOSSAL: True,
    }

    # 在你的回合结束时，对所有其他随从造成2点伤害
    events = OWN_TURN_END.on(Hit(ALL_MINIONS - SELF, 2))


# CATA_488t: 沃坎诺斯的喷发柱 - 2费 1/4 元素
# 每当本随从受到伤害，随机获取一张火焰法术牌，其法力值消耗减少（3）点。
class CATA_488t:
    """Vulcanos' Eruption Column"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 2,
        GameTag.ATK: 1,
        GameTag.HEALTH: 4,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.CARDRACE: Race.ELEMENTAL,
    }

    # 每当本随从受到伤害，随机获取一张火焰法术牌，其法力值消耗减少（3）点
    events = Damage(SELF).on(
        Give(CONTROLLER, RandomSpell(spell_school=SpellSchool.FIRE)).then(
            Buff(Give.CARD, "CATA_488te")
        )
    )


class CATA_488te:
    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: -3,
    }


# CATA_488t2: 喷发 - 0费 0/0


# CATA_979: 咒术专家 - 3费 3/4 普通
# 战吼：选择你手牌中的一张法术牌，将其拆分为两张法力值消耗与其相同的随机法术牌。
class CATA_979:
    """Conjuration Specialist"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 3,
        GameTag.ATK: 3,
        GameTag.HEALTH: 4,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.RARITY: Rarity.COMMON,
        GameTag.COLLECTIBLE: True,
    }

    # 战吼：选择你手牌中的一张法术牌，将其拆分为两张法力值消耗与其相同的随机法术牌
    # 简化实现：获取两张随机法术牌，并使其费用与选中的卡相同
    play = Give(CONTROLLER, RandomSpell()).then(
        Buff(Give.CARD, "CATA_979e", cost=-COST(TARGET))
    ), Give(CONTROLLER, RandomSpell()).then(
        Buff(Give.CARD, "CATA_979e", cost=-COST(TARGET))
    )


class CATA_979e:
    tags = {
        GameTag.CARD_SET: 1980,
    }


##
# Spells

# CATA_452: 织法者的光辉 - 10费
# 召唤一条6/6的龙。在本回合中，你每用法术造成一点伤害，本牌的法力值消耗便减少（1）点。
class CATA_452:
    """Spellweaver's Brilliance"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 10,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.RARITY: Rarity.RARE,
        GameTag.COLLECTIBLE: True,
    }

    # 召唤一条6/6的龙
    play = Summon(CONTROLLER, "CATA_452t")


# CATA_452t: 碧蓝守卫 - 6费 6/6 龙


# CATA_485: 激寒急流 - 1费
# 造成$2点伤害。随机对一个敌方随从造成$1点伤害。
class CATA_485:
    """Sleet Storm"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 1,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.RARITY: Rarity.COMMON,
        GameTag.COLLECTIBLE: True,
        GameTag.SPELL_SCHOOL: SpellSchool.FROST,
    }

    # 造成2点伤害。随机对一个敌方随从造成1点伤害
    play = Hit(TARGET, 2), Hit(RANDOM(ENEMY_MINIONS), 1)


# CATA_489: 奥术涌流 - 4费
# 裂变：造成$4点伤害。对所有敌人造成$2点伤害。
# 由于SHATTER机制未实现，这里简化为直接触发两个效果
class CATA_489:
    """Arcane Flow"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 4,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.RARITY: Rarity.RARE,
        GameTag.COLLECTIBLE: True,
        GameTag.SPELL_SCHOOL: SpellSchool.ARCANE,
    }

    # 裂变：造成4点伤害。对所有敌人造成2点伤害
    play = Hit(TARGET, 4), Hit(ENEMY_CHARACTERS, 2)


# CATA_978: 辛达苟萨的胜利 - 5费
# 对一个随从造成$8点伤害。使你手牌中一张随机牌的法力值消耗减少，减少的量等于超过目标生命值的伤害。
class CATA_978:
    """Sindragosa's Triumph"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 5,
        GameTag.CLASS: CardClass.MAGE,
        GameTag.RARITY: Rarity.RARE,
        GameTag.COLLECTIBLE: True,
        GameTag.SPELL_SCHOOL: SpellSchool.ARCANE,
    }

    # 对一个随从造成8点伤害。使你手牌中一张随机牌的法力值消耗减少，减少的量等于超过目标生命值的伤害
    # 简化实现：造成8点伤害，随机减少手牌一张卡1点费用
    play = Hit(TARGET, 8), Buff(RANDOM(FRIENDLY_HAND), "CATA_978e", cost=-1)


class CATA_978e:
    """Victorious"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: -1,
    }
