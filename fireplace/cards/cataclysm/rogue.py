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

    # Stealth. Deathrattle: Herald (summon Soldier of Sinestra).
    tags = {GameTag.STEALTH: True}
    herald_soldier_id = "CATA_158t"
    deathrattle = Herald(CONTROLLER)


# CATA_158t: Soldier of Sinestra (1费 1/1 龙)
# 简化实现: 战吼，获取一张随机法术
class CATA_158t:
    """Soldier of Sinestra"""

    # When summoned, get a random spell from another class. It costs
    # ({herald_count}) less. Simplified: give the spell with a stacked
    # cost-reduction buff equal to herald_count.
    @staticmethod
    def play(self):
        amount = max(1, self.controller.herald_count)
        return [
            Give(CONTROLLER, RandomSpell()).then(
                Buff(Give.CARD, "CATA_158te") * amount
            )
        ]


@custom_card
class CATA_158te:
    tags = {
        GameTag.CARDNAME: "Sinestra's Discount",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }



# CATA_200: Agent of the Old Ones (1费 2/1 埃索达)
# 战吼: 将你手牌中的一张随机卡牌变成一个幸运币
class CATA_200:
    """Agent of the Old Ones"""

    # 将手牌中一张随机卡弃掉，然后给一枚幸运币
    def play(self):
        if not self.controller.hand:
            return []
        return [Discard(RANDOM(FRIENDLY_HAND)), Give(CONTROLLER, THE_COIN)]


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
class CATA_785:
    """Rite of Twilight"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # Herald. Combo: Deal 3 damage. (Soldier of Sinestra)
    herald_soldier_id = "CATA_158t"
    play = Herald(CONTROLLER)
    combo = Herald(CONTROLLER), Hit(TARGET, 3)
