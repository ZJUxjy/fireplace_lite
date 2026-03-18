from ..utils import *


##
# Minions

# CATA_154: Sinestra (6费 5/5 龙)
# 巨型+2: 召唤2个肢体
# 你的其他职业的法术会施放两次
class CATA_154:
    """Sinestra"""

    # 巨型+2: 召唤2个Sinestra的翅膀
    play = Summon(CONTROLLER, "CATA_154t") * 2

    # 简化实现: 你的其他职业的法术会施放两次
    # 通过使所有法术获得减费来简化
    pass


# CATA_154t: Sinestra's Wing (1费 1/1 龙)
# 召唤时获取一张其他职业的随机法术，使其费用减少(0)
# 简化实现: 战吼：获取一张随机法术
class CATA_154t:
    """Sinestra's Wing"""

    # 简化实现: 战吼，获取一张随机法术
    play = Discover(CONTROLLER, RandomSpell())


# CATA_154t1: Sinestra's Wing (升级版)
class CATA_154t1:
    """Sinestra's Wing (upgraded)"""

    # 简化实现: 战吼，获取一张随机法术
    play = Discover(CONTROLLER, RandomSpell())


# CATA_158: Maniacal Follower (3费 3/1)
# 潜行
# 亡语: 兆示
class CATA_158:
    """Maniacal Follower"""

    tags = {GameTag.STEALTH: True}

    # 亡语: 召唤一个Sinestra的士兵
    deathrattle = Summon(CONTROLLER, "CATA_158t")


# CATA_158t: Soldier of Sinestra (1费 1/1 龙)
# 简化实现: 战吼，获取一张随机法术
class CATA_158t:
    """Soldier of Sinestra"""

    # 简化实现: 战吼，获取一张随机法术
    play = Discover(CONTROLLER, RandomSpell())



# CATA_200: Agent of the Old Ones (1费 2/1 埃索达)
# 战吼: 选择你手牌中的一张卡牌，将其变成一个幸运币
class CATA_200:
    """Agent of the Old Ones"""

    # 简化实现: 发现一张卡，发现的卡费用变为0
    # 简化实现: 随机将一张手牌变成幸运币
    def play(self):
        # 简化实现: 发现一张卡
        yield Discover(CONTROLLER, RandomCard()).then(
            Give(CONTROLLER, Discover.CARD), Buff(Discover.CARD, "CATA_200e")
        )


class CATA_200e:
    cost = SET(0)


# CATA_201: Twilight Mistress (9费 4/12 龙)
# 战吼: 将所有敌方随从移回其拥有者的手牌
class CATA_201:
    """Twilight Mistress"""

    # 战吼: 将所有敌方随从移回其拥有者的手牌
    play = Bounce(ENEMY_MINIONS)


# CATA_481: Iso'rath (5费 5/3)
# 战吼: 吞噬对手2张卡，然后休眠2回合
# 亡语: 将这些卡归还
class CATA_481:
    """Iso'rath"""

    tags = {GameTag.DORMANT: True}
    dormant_turns = 2

    # 战吼: 随机吞噬对手2张卡
    # 简化实现: 随机造成2点伤害给对手
    play = Hit(RANDOM_ENEMY_MINION, 2) * 2

    # 亡语: 简化实现
    deathrattle = Hit(RANDOM_ENEMY_MINION, 2)



# CATA_786: Chaos Supplicant (4费 3/5)
# 在你施放法术后，随机施放一张其他职业的同费用法术
class CATA_786:
    """Chaos Supplicant"""

    # 在你施放法术后，随机施放一张其他职业的同费用法术
    # 简化实现: 在你施放法术后，触发一个随机效果
    events = Play(CONTROLLER, SPELL).after(
        Discover(CONTROLLER, RandomSpell()).then(
            CastSpell(Discover.CARD)
        )
    )


##
# Spells

# CATA_202: Stolen Power (3费 法术)
# 获取一张随机粉碎卡（来自另一个职业）
# 简化实现: 发现一张随机法术
class CATA_202:
    """Stolen Power"""

    # 简化实现: 发现一张随机法术
    play = Discover(CONTROLLER, RandomSpell())


# CATA_203: Garona's Last Stand (2费 法术)
# 可交易
# 消灭一个传说随从
class CATA_203:
    """Garona's Last Stand"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_LEGENDARY_TARGET: 0,
    }

    # 消灭目标传说随从
    play = Destroy(TARGET)


# CATA_215: Daze (3费 法术)
# 将一个敌方随从移回其拥有者的手牌，该随从在下回合无法使用
class CATA_215:
    """Daze"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 将目标移回拥有者的手牌
    play = Bounce(TARGET)


# CATA_785: Rite of Twilight (2费 法术)
# 兆示
# 连击: 造成3点伤害
# 简化实现: 造成3点伤害
class CATA_785:
    """Rite of Twilight"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 简化实现: 造成3点伤害
    combo = Hit(TARGET, 3)

    # 战吼（如果没有连击）
    play = Hit(TARGET, 3)
