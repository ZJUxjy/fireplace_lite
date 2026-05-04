from ..utils import *


##
# Minions

# CATA_154: Sinestra (6费 5/5 龙)
# 巨型+2: 召唤2个肢体
# 你的其他职业的法术会施放两次
class CATA_154_DoubleOtherClassSpell(TargetedAction):
    CARD = ActionArg()
    TARGET = ActionArg()

    def do(self, source, card, target):
        if card.card_class == source.card_class:
            return
        copied = source.controller.card(card.id, source=source, zone=Zone.SETASIDE)
        return source.game.queue_actions(source, [CastSpell(copied, target)])


class CATA_154:
    """Sinestra"""

    # 巨型+2: 召唤2个Sinestra的翅膀
    play = Summon(CONTROLLER, "CATA_154t") * 2

    # 你的其他职业的法术会施放两次
    events = Play(CONTROLLER, SPELL).after(
        CATA_154_DoubleOtherClassSpell(Play.CARD, Play.TARGET)
    )


SINESTRA_TOKEN_SPELL = Give(CONTROLLER, RandomSpell(card_class=ANOTHER_CLASS)).then(
    Buff(Give.CARD, "CATA_154te")
)


@custom_card
class CATA_154te:
    tags = {
        GameTag.CARDNAME: "Sinestra Spell Discount",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


# CATA_154t: Sinestra's Wing (1费 1/1 龙)
# 召唤时获取一张其他职业的随机法术，使其费用减少(0)
class CATA_154t:
    """Sinestra's Wing"""

    play = SINESTRA_TOKEN_SPELL


# CATA_154t1: Sinestra's Wing (升级版)
class CATA_154t1:
    """Sinestra's Wing (upgraded)"""

    play = SINESTRA_TOKEN_SPELL


# CATA_158: Maniacal Follower (3费 3/1)
# 潜行
# 亡语: 兆示
class CATA_158:
    """Maniacal Follower"""

    tags = {GameTag.STEALTH: True}

    # 亡语: 召唤一个Sinestra的士兵
    deathrattle = Summon(CONTROLLER, "CATA_158t")


# CATA_158t: Soldier of Sinestra (1费 1/1 龙)
class CATA_158t:
    """Soldier of Sinestra"""

    play = SINESTRA_TOKEN_SPELL



# CATA_200: Agent of the Old Ones (1费 2/1 埃索达)
# 战吼: 将你手牌中的一张随机卡牌变成一个幸运币
class CATA_200_TransformHandCardToCoin(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if not target.hand:
            return []
        transformed = source.game.random.choice(list(target.hand))
        transformed.zone = Zone.REMOVEDFROMGAME
        source.game.manager.targeted_action(self, source, transformed)
        return source.game.queue_actions(source, [Give(target, THE_COIN)])


class CATA_200:
    """Agent of the Old Ones"""

    play = CATA_200_TransformHandCardToCoin(CONTROLLER)


# CATA_201: Twilight Mistress (9费 4/12 龙)
# 战吼: 将所有敌方随从移回其拥有者的手牌
class CATA_201:
    """Twilight Mistress"""

    # 战吼: 将所有敌方随从移回其拥有者的手牌
    play = Bounce(ENEMY_MINIONS)


# CATA_481: Iso'rath (5费 5/3)
# 战吼: 吞噬对手2张卡，然后休眠2回合
# 亡语: 将这些卡归还
class CATA_481_DevourOpponentHand(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        opponent_hand = list(source.controller.opponent.hand)
        devoured = source.game.random.sample(
            opponent_hand, min(2, len(opponent_hand))
        )
        source.devoured_cards = devoured
        for card in devoured:
            card.zone = Zone.REMOVEDFROMGAME
            source.game.manager.targeted_action(self, source, card)
        return devoured


class CATA_481_ReturnDevoured(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        devoured = getattr(target, "devoured_cards", [])
        for card in list(devoured):
            if len(card.controller.hand) < card.controller.max_hand_size:
                card.zone = Zone.HAND
                source.game.manager.targeted_action(self, source, card)
        devoured.clear()
        return devoured


class CATA_481:
    """Iso'rath"""

    tags = {GameTag.DORMANT: True}
    dormant_turns = 2

    # 战吼: 随机吞噬对手2张卡
    play = CATA_481_DevourOpponentHand(SELF)

    # 亡语: 将吞噬的牌吐回对手手牌
    deathrattle = CATA_481_ReturnDevoured(SELF)



# CATA_786: Chaos Supplicant (4费 3/5)
# 在你施放法术后，随机施放一张其他职业的同费用法术
class CATA_786_CastSameCostOtherClassSpell(TargetedAction):
    CARD = ActionArg()

    def do(self, source, card):
        spells = RandomSpell(
            cost=card.cost,
            card_class=ANOTHER_CLASS,
        ).evaluate(source)
        if not spells:
            return
        return source.game.queue_actions(source, [CastSpell(spells[0])])


class CATA_786:
    """Chaos Supplicant"""

    events = Play(CONTROLLER, SPELL).after(
        CATA_786_CastSameCostOtherClassSpell(Play.CARD)
    )


##
# Spells

# CATA_202: Stolen Power (3费 法术)
# 获取一张随机粉碎卡（来自另一个职业）
STOLEN_POWER_SHATTER_CARDS = ("CATA_134", "CATA_306", "CATA_479", "CATA_489", "CATA_820")


class CATA_202_GiveCompleteShatter(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        card_id = source.game.random.choice(STOLEN_POWER_SHATTER_CARDS)
        card = target.card(card_id, source=source, zone=Zone.SETASIDE)
        card._shatter_locked = True
        return source.game.queue_actions(source, [Give(target, card)])


class CATA_202:
    """Stolen Power"""

    play = CATA_202_GiveCompleteShatter(CONTROLLER)


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
class CATA_215_Daze(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        source.game.queue_actions(source, [Bounce(target)])
        target.unplayable_until_turn = source.game.turn + 1
        return target


class CATA_215:
    """Daze"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 将目标移回拥有者的手牌
    play = CATA_215_Daze(TARGET)


# CATA_785: Rite of Twilight (2费 法术)
# 兆示
# 连击: 造成3点伤害
class CATA_785:
    """Rite of Twilight"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 连击: 造成3点伤害（无连击时的兆示效果未实现）
    combo = Hit(TARGET, 3)
