from ..utils import *


##
# Minions

class END_015_GetDeathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        card_id = RandomMinion(deathrattle=True).evaluate(source)[0]
        card = player.card(card_id, source=source)
        card.cost = max(0, card.cost - 2)
        return source.game.queue_actions(source, [Give(player, card)])


class END_015:
    """Triennium Rex"""

    play = END_015_GetDeathrattle(CONTROLLER)
    deathrattle = END_015_GetDeathrattle(CONTROLLER)


# TIME_042: King Maluk (4费 5/6)
# 在你的回合结束时，使你的武器获得+1攻击力
class TIME_042:
    """King Maluk"""

    # 在你的回合结束时，使你的武器获得+1攻击力
    # No battlecry

    events = OWN_TURN_END.on(Buff(FRIENDLY_WEAPON, "TIME_042e"))


TIME_042e = buff(+1, 0)


# TIME_042t: Infinite Banana (1费 香蕉)
class TIME_042t:
    """Infinite Banana"""

    # 抉择：使一个随从获得+1/+1；或者+2/+1
    choose = ("TIME_042ta", "TIME_042tb")


@custom_card
class TIME_042ta:
    tags = {
        GameTag.CARDNAME: "Banana (+1/+1)",
        GameTag.CARDTYPE: CardType.SPELL,
    }
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Buff(TARGET, "TIME_042e1")


@custom_card
class TIME_042e1:
    tags = {
        GameTag.CARDNAME: "Banana Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 1,
        GameTag.HEALTH: 1,
    }


@custom_card
class TIME_042tb:
    tags = {
        GameTag.CARDNAME: "Bunch of Bananas (+2/+1)",
        GameTag.CARDTYPE: CardType.SPELL,
    }
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Buff(TARGET, "TIME_042e2")


@custom_card
class TIME_042e2:
    tags = {
        GameTag.CARDNAME: "Bunch of Bananas Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 2,
        GameTag.HEALTH: 1,
    }


# TIME_601: Arrow Retriever (2费 3/1)
# 战吼：使一个友方野兽获得亡语：使 Arrow Retriever 回到你的手牌
class TIME_601:
    """Arrow Retriever"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 战吼：使一个友方野兽获得亡语：将该随从置入你的手牌
    play = Buff(TARGET, "TIME_601e")


class TIME_601e:
    """Retrieving"""

    deathrattle = Give(CONTROLLER, "TIME_601")


# TIME_602: Wormhole (3费 法术)
# 发现一个随从。召唤两个它的复制
class TIME_602:
    """Wormhole"""

    # 发现一个随从并召唤两个它的复制
    play = Discover(CONTROLLER, RandomMinion()).then(
        Summon(CONTROLLER, Discover.CARD) * 2
    )


# TIME_603: Ticking Timebomb (2费 1/1)
# 亡语：对所有敌人造成3点伤害
class TIME_603:
    """Ticking Timebomb"""

    # 亡语：对所有敌人造成3点伤害
    # No battlecry

    deathrattle = Hit(ENEMY_CHARACTERS, 3)


# TIME_605: Epoch Stalker (6费 3/4)
# 突袭，嘲讽。战吼：召唤一个本随从的复制
class TIME_605:
    """Epoch Stalker"""

    # 突袭，嘲讽
    tags = {
        GameTag.RUSH: True,
        GameTag.ELUSIVE: True,
    }

    # 战吼：召唤一个本随从的复制
    play = Summon(CONTROLLER, "TIME_605")


# TIME_606: Quel'dorei Fletcher (1费 1/3)
# 在你施放一个法术后，使一个友方野兽获得+1攻击力
class TIME_606:
    """Quel'dorei Fletcher"""

    # 在你施放一个法术后，使一个友方野兽获得+1攻击力
    # No battlecry

    events = OWN_SPELL_PLAY.on(Buff(RANDOM(FRIENDLY_MINIONS + BEAST), "TIME_606e"))


TIME_606e = buff(+1, 0)


# TIME_609: Ranger General Sylvanas (3费 2/4)
# 战吼：发现一个时间流。选择一条时间线！
class TIME_609:
    """Ranger General Sylvanas"""

    # 战吼：发现一个时间流
    play = Discover(CONTROLLER, RandomCard())


# TIME_620: Untimely Death (2费 法术)
# 对一个随从造成4点伤害。如果该随从死亡，召唤一个4/4的幽灵
class TIME_620:
    """Untimely Death"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 对目标造成4点伤害
    def play(self):
        Hit(self.target, 4).trigger(self)
        if self.target.dead:
            Summon(CONTROLLER, "TIME_620t").trigger(self)


# TIME_810: Past Silvermoon (4费 英雄)
# 战吼：召唤两个银月城凤凰
class TIME_810:
    """Past Silvermoon"""

    # 战吼：召唤两个银月城凤凰
    play = Summon(CONTROLLER, "TIME_810t") * 2


# TIME_810t: Present Silvermoon (4费 随从)
class TIME_810t:
    """Silvermoon"""

    pass


# TIME_600: Precise Shot (2费 法术)
# 造成2点伤害。发现一张卡牌
class TIME_600:
    """Precise Shot"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 对目标造成2点伤害，发现一张卡牌
    play = Hit(TARGET, 2), Discover(CONTROLLER, RandomCard())
