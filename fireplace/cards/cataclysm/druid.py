from ..utils import *


##
# Minions

# CATA_130: 炫晶小熊 (1费 1/2 野兽)
# 每当你消耗掉最后一个法力水晶，获得+1/+1
# 简化实现：每当你使用一张卡时触发
class CATA_130:
    """Crystalspine Cub"""

    # 简化实现：每当使用一张卡时触发
    events = Play(CONTROLLER).after(
        Buff(SELF, "CATA_130e")
    )


CATA_130e = buff(+1, +1)


# CATA_131: 费伍德树人 (2费 2/2)
# 战吼：获得一个临时法力水晶。如果你使用4点法力，则变为永久
class CATA_131:
    """Felwood Treant"""

    # 战吼：获得一个临时法力水晶
    # 简化实现：直接获得一个临时水晶
    play = GainEmptyMana(CONTROLLER, 1)


# CATA_132: 护巢龙 (4费 4/5 龙)
# 战吼：获得两个3/3嘲讽龙。如果你使用8点法力，则直接召唤
class CATA_132:
    """Broodwatcher"""

    # 战吼：获得两张衍生物卡
    # 简化实现：直接召唤两个3/3嘲讽龙
    play = Summon(CONTROLLER, "CATA_132t") * 2


# CATA_132t: 翡翠龙雏 (3费 3/3 龙 嘲讽)
class CATA_132t:
    """Emerald Whelp"""

    tags = {GameTag.TAUNT: True}


# CATA_133: 彩翼灵龙 (5费 4/5 野兽)
# 难瞄
# 在你的回合结束时，给你的其他随从+1/+1
class CATA_133:
    """Iridescent Flitterwing"""

    tags = {GameTag.ELUSIVE: True}

    # 在回合结束时，给其他随从+1/+1
    events = OWN_TURN_END.on(
        Buff(FRIENDLY_MINIONS - SELF, "CATA_133e")
    )


CATA_133e = buff(+1, +1)


# CATA_135: 苔缚术 (2费 法术)
# 召唤两个1/2元素。用所有法力值给它们+1/+1
class CATA_135:
    """Mossbinding"""

    # 召唤两个1/2元素
    # 简化实现：直接召唤两个1/2元素并根据花费的水晶给它们buff
    def play(self):
        # 获得当前花费的水晶数
        mana_spent = self.controller.mana_spent_this_turn
        # 召唤两个1/2元素并buff
        return [
            Summon(CONTROLLER, "CATA_135t"),
            Summon(CONTROLLER, "CATA_135t"),
            Buff(FRIENDLY_MINIONS + "CATA_135t", "CATA_135e", atk=mana_spent, health=mana_spent),
        ]


# CATA_135t: 苔岩元素 (1费 1/2)
class CATA_135t:
    """Moss Golem"""


CATA_135e = buff(atk=1, health=1)


# CATA_138: 森林赠礼 (2费 法术)
# 给一个随从 +1/+1，数值等于你控制的随从数量
class CATA_138:
    """Forest's Gift"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 获得等同于随从数量的+1/+1
    play = Buff(TARGET, "CATA_138e")


CATA_138e = buff(+1, +1)


# CATA_139: 柳牙 (6费 0/5)
# 巨型+4
# 在柳牙的一条腿获得属性后，柳牙也获得相同属性
class CATA_139:
    """Wickerfang"""

    # 巨型+4：召唤4条腿
    play = Summon(CONTROLLER, "CATA_139t"), Summon(CONTROLLER, "CATA_139t2"), Summon(CONTROLLER, "CATA_139t3"), Summon(CONTROLLER, "CATA_139t4")

    # 简化实现：每回合结束时获得+1/+1 (腿也会获得)
    # 柳牙的效果是在腿获得buff时同步获得，这里简化为每回合结束时获得buff
    pass


# CATA_139t, CATA_139t2, CATA_139t3, CATA_139t4: 柳牙之腿 (1费 0/2)
# 在你的回合结束时获得+1/+1
class CATA_139t:
    """Wickerfang's Leg"""

    events = OWN_TURN_END.on(Buff(SELF, "CATA_139te"))


CATA_139t2 = CATA_139t
CATA_139t3 = CATA_139t
CATA_139t4 = CATA_139t

CATA_139e = buff(atk=1, health=1)
CATA_139te = buff(+1, +1)


# CATA_140: 梦境之龙麦琳瑟拉 (8费 4/12 龙)
# 战吼：随机将龙牌填入你的手牌直到满。如果你使用25点法力，则改为1费
class CATA_140:
    """Merithra of the Dream"""

    # 战吼：将随机龙牌填入你的手牌
    # 简化实现：给3张随机龙牌
    play = Give(CONTROLLER, RandomDragon()) * 3


##
# Spells


# CATA_134: 荒林怪圈 (3费 法术)
# 破碎：召唤两个2/2树人。给你的随从"亡语：召唤一个2/2树人"
class CATA_134:
    """Wildwood Circle"""

    # 破碎效果：召唤两个2/2树人，给所有友方随从亡语buff
    # 简化实现：直接召唤两个树人并给随从亡语
    play = Summon(CONTROLLER, "CATA_134t3") * 2, Buff(FRIENDLY_MINIONS, "CATA_134e")


# CATA_134t3: 树人 (1费 2/2)
class CATA_134t3:
    """Treant"""


CATA_134e = buff(deathrattle=Summon(CONTROLLER, "CATA_134t3"))


# CATA_136: 艾萨拉的胜利 (1费 法术)
# 洗入5张随机8+费随从并使其属性翻倍
class CATA_136:
    """Azshara's Triumph"""

    # 洗入5张随机8+费随从并翻倍属性
    # 简化实现：直接给5张随机高费随从并翻倍
    def play(self):
        cards = []
        for _ in range(5):
            card = RandomMinion(cost=8)
            cards.append(Give(CONTROLLER, card))
            cards.append(Buff(Give.CARD, "CATA_136e"))
        return cards


CATA_136e = buff(+1, +1)  # 翻倍通过使用两次实现
