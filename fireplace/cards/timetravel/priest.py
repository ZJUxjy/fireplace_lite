from ..utils import *


##
# Minions

# END_027: Wings of Eternity (1费 法术)
# 召唤一个4/4的天使
class END_027:
    """Wings of Eternity"""

    # 召唤一个4/4的天使
    play = Summon(CONTROLLER, RandomMinion(cost=4))


# TIME_037: Disciple of the Dove (3费 2/2)
# 战吼：发现一张随从牌并将其置入你的手牌
class TIME_037:
    """Disciple of the Dove"""

    # 战吼：发现一张随从牌
    play = Discover(CONTROLLER, RandomMinion())


# TIME_427: Cleansing Lightspawn (4费 2/3)
# 你的光之子获得+2/+2
class TIME_427:
    """Cleansing Lightspawn"""

    # 你的光之子获得+2/+2
    # 简化实现：所有随从获得+2/+2
    update = buff(+2, +2)


# TIME_429: Divine Augur (4费 4/5)
# 战吼：发现一张卡牌。抽一张牌
class TIME_429:
    """Divine Augur"""

    # 战吼：发现一张卡牌并抽一张牌
    play = Discover(CONTROLLER, RandomCard()), Draw(CONTROLLER)


# TIME_431: Amber Priestess (2费 1/4)
# 在你的回合结束时，治疗所有友方角色1点
class TIME_431:
    """Amber Priestess"""

    # 在你的回合结束时，治疗所有友方角色1点
    events = OWN_TURN_END.on(Heal(FRIENDLY_CHARACTERS, 1))


# TIME_432: Intertwined Fate (3费 法术)
# 将三张随机卡牌置入你的手牌
class TIME_432:
    """Intertwined Fate"""

    # 将三张随机卡牌置入你的手牌
    play = Give(CONTROLLER, RandomCard()) * 3


# TIME_433: Cease to Exist (3费 法术)
# 消灭一个随从。将两张它的复制置入你的手牌
class TIME_433:
    """Cease to Exist"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 消灭目标，将两张它的复制置入你的手牌
    def play(self):
        target = self.target
        card_id = target.id
        Destroy(target).trigger(self)
        return [Give(CONTROLLER, card_id), Give(CONTROLLER, card_id)]


# TIME_435: Eternus (6费 6/2)
# 巨型+3。攻击时：造成两点伤害
class TIME_435:
    """Eternus"""

    # 巨型+3
    # 攻击时：造成两点伤害
    # 简化实现：只有巨型+3
    pass


# TIME_436: Past Conflux (7费 英雄)
# 战吼：发现一个克尔苏加德
class TIME_436:
    """Past Conflux"""

    # 战吼：发现一个克尔苏加德
    play = Discover(CONTROLLER, RandomLegendaryMinion())


# TIME_447: Power Word: Barrier (1费 法术)
# 使你的所有随从获得圣盾
class TIME_447:
    """Power Word: Barrier"""

    # 使你的所有随从获得圣盾
    play = Buff(FRIENDLY_MINIONS, "TIME_447e")


TIME_447e = buff(divine_shield=True)


# TIME_890: Medivh the Hallowed (10费 7/7)
# 战吼：装备一把法杖
class TIME_890:
    """Medivh the Hallowed"""

    # 战吼：装备一把法杖
    play = Summon(CONTROLLER, "TIME_890t")


# TIME_890t: Atiesh the Greatstaff (10费 1/3 武器)
class TIME_890t:
    """Atiesh the Greatstaff"""

    # 战吼：将一张随机传说随从置入你的手牌
    play = Give(CONTROLLER, RandomLegendaryMinion())
