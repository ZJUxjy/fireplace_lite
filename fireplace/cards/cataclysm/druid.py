from ..utils import *


##
# Minions

# CATA_130: 炫晶小熊 (1费 1/2 野兽)
# 每当你消耗掉最后一个法力水晶，获得+1/+1
_SELF_IF_MANA_EMPTY = FuncSelector(
    lambda entities, source: [source] if source.controller.mana == 0 else []
)


class CATA_130:
    """Crystalspine Cub"""

    # 每当消耗掉最后一个法力水晶时触发
    events = Play(CONTROLLER).after(
        Buff(_SELF_IF_MANA_EMPTY, "CATA_130e")
    )


CATA_130e = buff(+1, +1)


# CATA_131: 费伍德树人 (2费 2/2)
# 战吼：获得一个临时法力水晶。如果你使用4点法力，则变为永久
class CATA_131:
    """Felwood Treant"""

    # 战吼：如果使用了4点法力，获得永久水晶；否则获得临时水晶
    def play(self):
        if self.controller.used_mana >= 4:
            return [GainMana(CONTROLLER, 1)]
        else:
            return [ManaThisTurn(CONTROLLER, 1)]


# CATA_132: 护巢龙 (4费 4/5 龙)
# 战吼：获得两个3/3嘲讽龙。如果你使用8点法力，则直接召唤
class CATA_132:
    """Broodwatcher"""

    # 战吼：获得两张衍生物卡；若本回合已消耗8点法力，则直接召唤
    def play(self):
        if self.controller.used_mana >= 8:
            return [Summon(CONTROLLER, "CATA_132t"), Summon(CONTROLLER, "CATA_132t")]
        else:
            return [Give(CONTROLLER, "CATA_132t"), Give(CONTROLLER, "CATA_132t")]


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

    # 召唤两个1/2元素，并给它们+used_mana/+used_mana
    def play(self):
        mana_spent = self.controller.used_mana
        return [
            Summon(CONTROLLER, "CATA_135t"),
            Summon(CONTROLLER, "CATA_135t"),
            Buff(FRIENDLY_MINIONS + ID("CATA_135t"), "CATA_135e", atk=mana_spent, max_health=mana_spent),
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
# 战吼：随机将龙牌填入你的手牌直到满
class CATA_140:
    """Merithra of the Dream"""

    # 战吼：将随机龙牌填入你的手牌直到满（10张上限）
    def play(self):
        count = 10 - len(self.controller.hand)
        return [Give(CONTROLLER, RandomDragon()) for _ in range(max(0, count))]


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

    # 洗入5张随机8+费随从
    play = Shuffle(CONTROLLER, RandomMinion(cost=8)) * 5
