from ..utils import *


##
# Minions

# CATA_153: 奥拉基尔，风暴之主 (8费 2/8)
# 巨型+2, 突袭, 风怒
# 战吼：获取2个费用等于此随从攻击力的随从，费用变为(1)
class CATA_153:
    """Al'Akir, Lord of Storms"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 8,
        GameTag.ATK: 2,
        GameTag.HEALTH: 8,
        GameTag.RUSH: True,
        GameTag.WINDFURY: True,
    }

    # 战吼：获取2个费用等于此随从攻击力的随从，费用变为(1)
    # 简化实现：召唤2个费用为2的随机随从，费用变为1
    play = Summon(CONTROLLER, RandomMinion(cost=2)) * 2


# CATA_153e: 火花之怒 (buff)
class CATA_153e:
    """Spark of Fury"""

    tags = {
        GameTag.ATK: +2,
    }


# CATA_153t: 奥拉基尔的充能之手 (附属物)
class CATA_153t:
    """Charged Hand of Al'Akir"""

    # 相邻随从获得+2攻击力
    play = Buff(ADJACENT, "CATA_153e")


# CATA_153t1: 奥拉基尔的充能之手 (升级版)
class CATA_153t1:
    """Charged Hand of Al'Akir (upgraded)"""

    # 相邻随从获得+3攻击力
    play = Buff(ADJACENT, "CATA_153e1")


CATA_153e1 = buff(+3, 0)


# CATA_497: 奥卓克希昂 (6费 6/7)
# 战吼：兆示
class CATA_497:
    """Ultraxion"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 6,
        GameTag.ATK: 6,
        GameTag.HEALTH: 7,
        GameTag.RARITY: 5,
    }

    # 简化实现：战吼，造成3点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3)


# CATA_561: 能量仪式 (2费 法术)
# 兆示，召唤2个1/1具有突袭的元素
class CATA_561:
    """Ritual of Power"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 2,
        GameTag.CLASS: CardClass.SHAMAN,
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.RARITY: 3,
    }

    # 简化实现：召唤2个1/1突袭元素
    play = Summon(CONTROLLER, "CATA_561t") * 2


# CATA_561t: 微风精灵 (1费 1/1 元素)
class CATA_561t:
    """Breezling"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 1,
        GameTag.ATK: 1,
        GameTag.HEALTH: 1,
        GameTag.RUSH: True,
    }


# CATA_563: 雷鸣流云 (3费 4/3)
# 战吼：选择手牌中一张费用(4)或更低的法术来吸收
# 亡语：释放它
class CATA_563:
    """Crackling Cloudstrider"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 3,
        GameTag.ATK: 4,
        GameTag.HEALTH: 3,
        GameTag.RARITY: 4,
    }

    # 简化实现：战吼，随机获得一张手牌中的法术
    # 亡语：造成2点伤害
    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# CATA_563e2: 阴云 (buff)
class CATA_563e2:
    """Overcast"""

    tags = {
        GameTag.DEATHRATTLE: True,
    }


# CATA_564: 飞行助翼 (5费 5/5)
# 战吼：使一个友方随从获得Mega-Windfury，无法攻击英雄
class CATA_564:
    """Air Support"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 5,
        GameTag.ATK: 5,
        GameTag.HEALTH: 5,
        GameTag.RARITY: 1,
    }

    # 简化实现：战吼，使一个友方随从获得+2/+2
    play = Buff(TARGET, "CATA_564e")


CATA_564e = buff(+2, +2)


# CATA_565: 天空之墙哨兵 (2费 0/3)
# 嘲讽，战吼：兆示
class CATA_565:
    """Skywall Sentinel"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 2,
        GameTag.ATK: 0,
        GameTag.HEALTH: 3,
        GameTag.TAUNT: True,
        GameTag.RARITY: 3,
    }

    # 简化实现：战吼，召唤一个1/2的士兵
    play = Summon(CONTROLLER, "CATA_565t")


# CATA_565t: 奥拉基尔的士兵 (1费 1/2)
class CATA_565t:
    """Soldier of Al'Akir"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 1,
        GameTag.ATK: 1,
        GameTag.HEALTH: 2,
    }


# CATA_567: 升腾 (4费 法术)
# 将所有友方随从变形成费用增加(1)的随从，它们死亡时召唤原始随从
class CATA_567:
    """Ascendance"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 4,
        GameTag.CLASS: CardClass.SHAMAN,
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.RARITY: 4,
    }

    # 简化实现：使所有友方随从获得+1/+1
    play = Buff(FRIENDLY_MINIONS, "CATA_567e")


CATA_567e = buff(+1, +1)


# CATA_568: 穆拉丁的奋战 (9费 法术)
# 抽2张牌，每有一个友方角色攻击过，费用就减少(1)
class CATA_568:
    """Muradin's Last Stand"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 9,
        GameTag.CLASS: CardClass.SHAMAN,
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.RARITY: 3,
    }

    # 简化实现：抽2张牌
    play = Draw(CONTROLLER) * 2


# CATA_569: 演武仪式 (4费 法术)
# 随机召唤一个3费、2费和1费的随从，过载(1)
class CATA_569:
    """Ceremonial Clash"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 4,
        GameTag.CLASS: CardClass.SHAMAN,
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.OVERLOAD: 1,
        GameTag.RARITY: 1,
    }

    # 随机召唤3费、2费、1费随从
    play = Summon(CONTROLLER, RandomMinion(cost=3)), Summon(CONTROLLER, RandomMinion(cost=2)), Summon(CONTROLLER, RandomMinion(cost=1))


# CATA_570: 莫卓克 (10费 10/10)
# 战吼：抽1张牌并减少其费用(10)
class CATA_570:
    """Morchok"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 10,
        GameTag.ATK: 10,
        GameTag.HEALTH: 10,
        GameTag.RARITY: 5,
    }

    # 简化实现：战吼，抽1张牌
    play = Draw(CONTROLLER)


# CATA_722: 末世特使 (5费 5/4)
# 嘲讽，战吼：兆示
class CATA_722:
    """Envoy of the End"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 5,
        GameTag.ATK: 5,
        GameTag.HEALTH: 4,
        GameTag.TAUNT: True,
        GameTag.RARITY: 1,
    }

    # 简化实现：战吼，造成3点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3)


# CATA_724: 缚风者 (4费 7/7)
# 亡语：解锁你被过载的水晶，过载(3)
class CATA_724:
    """Stormbinder"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 4,
        GameTag.ATK: 7,
        GameTag.HEALTH: 7,
        GameTag.OVERLOAD: 3,
        GameTag.RARITY: 1,
    }

    # 简化实现：亡语，使你的英雄获得+3攻击力
    deathrattle = Buff(FRIENDLY_HERO, "CATA_724e")


CATA_724e = buff(+3, 0)


# CATA_190h: 灭世者死亡之翼 (10费 0/30 英雄)
# 战吼：选择一种裂变来释放
class CATA_190h:
    """Deathwing, Worldbreaker"""

    tags = {
        GameTag.CARD_SET: 1980,
        GameTag.COST: 10,
        GameTag.ATK: 0,
        GameTag.HEALTH: 30,
        GameTag.RARITY: 5,
    }

    # 简化实现：战吼，对所有其他随从造成5点伤害，使你的英雄获得5点护甲
    play = Hit(ALL_MINIONS - SELF, 5), GainArmor(FRIENDLY_HERO, 5)
