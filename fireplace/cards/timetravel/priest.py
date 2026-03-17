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
# 吸血。战吼：对一个敌人随从造成等同于本随从生命值的伤害
class TIME_427:
    """Cleansing Lightspawn"""

    # 吸血
    tags = {
        GameTag.LIFESTEAL: True,
    }

    # 战吼：对一个敌人随从造成等同于本随从生命值的伤害
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Hit(TARGET, ATK(SELF))


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
    # No battlecry

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
# 战吼：获得一个攻击力不超过本随从生命值的敌方随从的控制权
class TIME_435:
    """Eternus"""

    # 战吼：获得一个攻击力不超过本随从生命值的敌方随从的控制权
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_NUM_MINION_SLOTS: 1,
    }

    play = Steal(TARGET)


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
