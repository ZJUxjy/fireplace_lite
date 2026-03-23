from ..utils import *


##
# Minions

# END_009: Splintered Reality (4费 随从)
# 战吼：选择一个方向，发现一个树人
class END_009:
    """Splintered Reality"""

    # 战吼：发现一个树人
    play = Discover(CONTROLLER, RandomMinion(race=Race.TREANT)).then(
        Summon(CONTROLLER, Discover.CARD)
    )


# END_009t: Treant (1费 2/2)
class END_009t:
    """Treant"""

    # 亡语：获得一个空的法力水晶
    deathrattle = GainEmptyMana(CONTROLLER, 1)


# TIME_023: Contingency (3费 法术)
# 抽你牌库底部的两张牌
class TIME_023:
    """Contingency"""

    # 抽你牌库底部的两张牌
    def play(self):
        cards_to_draw = list(self.controller.deck[:2])  # snapshot bottom 2 before drawing
        for card in cards_to_draw:
            sel = FuncSelector(lambda e, s, c=card: [c])
            yield Draw(CONTROLLER, sel)


# TIME_033: Druid of Regrowth (6费 3/5)
# 抉择：使一个随从获得+2/+2或+2/+2并获得嘲讽
class TIME_033:
    """Druid of Regrowth"""

    # 抉择：使一个随从获得+2/+2或+2/+2并获得嘲讽
    choose = ("TIME_033a", "TIME_033b")

    play = Buff(TARGET, "TIME_033e")


class TIME_033a:
    """Regrowth"""

    play = Buff(TARGET, "TIME_033e")


@custom_card
class TIME_033e:
    tags = {
        GameTag.CARDNAME: "Regrowth Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 2,
        GameTag.HEALTH: 2,
    }


class TIME_033b:
    """Renewed Growth"""

    play = Buff(TARGET, "TIME_033e2")


@custom_card
class TIME_033e2:
    tags = {
        GameTag.CARDNAME: "Renewed Growth Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 2,
        GameTag.HEALTH: 2,
        GameTag.TAUNT: True,
    }


# TIME_211: Lady Azshara (5费 5/5)
# 战吼：发现一张卡牌。选择一种时间之力！
class TIME_211:
    """Lady Azshara"""

    # 战吼：发现一张卡牌
    play = Discover(CONTROLLER, RandomCard())


# TIME_701: Waveshaping (1费 法术)
# 使一个随从获得+1/+2。将一个树人置入你的手牌
class TIME_701:
    """Waveshaping"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 使目标随从获得+1/+2，将一个树人置入你的手牌
    play = Buff(TARGET, "TIME_701e"), Give(CONTROLLER, RandomMinion(race=Race.TREANT))


TIME_701e = buff(+1, +2)


# TIME_702: Ebb and Flow (2费 法术)
# 使一个随从获得+1/+1。如果你操控一个树人，再获得+1/+1
class TIME_702:
    """Ebb and Flow"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 使目标随从获得+1/+1；如果你操控一个树人，再获得+1/+1
    def play(self):
        yield Buff(self.target, "TIME_702e")
        has_treant = any(Race.TREANT in getattr(m, "races", []) for m in self.controller.field)
        if has_treant:
            yield Buff(self.target, "TIME_702e")


@custom_card
class TIME_702e:
    tags = {
        GameTag.CARDNAME: "Ebb and Flow Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 1,
        GameTag.HEALTH: 1,
    }


# TIME_703: Endangered Dodo (5费 5/5)
# 在你的回合结束时，如果你控制一个受伤的随从，召唤一个2/2的猫
class TIME_703:
    """Endangered Dodo"""

    # 在你的回合结束时，如果你控制一个受伤的随从，召唤一个2/2的猫
    events = OWN_TURN_END.on(Find(FRIENDLY_MINIONS + DAMAGED) & Summon(CONTROLLER, "TIME_703t"))


# TIME_703t: Endangered Dodo (2费 2/2)
@custom_card
class TIME_703t:
    tags = {
        GameTag.CARDNAME: "Dodo",
        GameTag.CARDTYPE: CardType.MINION,
        GameTag.ATK: 2,
        GameTag.HEALTH: 2,
    }


# TIME_704: Highborne Mentor (7费 6/6)
# 在你的回合结束时，召唤一个2/2的学生
class TIME_704:
    """Highborne Mentor"""

    # 在你的回合结束时，召唤一个2/2的学生
    # No battlecry

    events = OWN_TURN_END.on(Summon(CONTROLLER, "TIME_704t"))


# TIME_704t: Highborne Pupil (2费 2/2)
class TIME_704t:
    """Highborne Pupil"""

    pass


# TIME_705: Krona, Keeper of Eons (6费 4/7)
# 嘲讽。战吼：将你牌库底部的5张卡牌的费用变为1
class TIME_705:
    """Krona, Keeper of Eons"""

    # 嘲讽
    tags = {
        GameTag.TAUNT: True,
    }

    # 战吼：将你牌库底部的5张卡牌的费用变为1
    def play(self):
        for card in list(self.controller.deck[:5]):
            Buff(FuncSelector(lambda e, s, c=card: [c]), "TIME_705e").trigger(self)


@custom_card
class TIME_705e:
    tags = {
        GameTag.CARDNAME: "Krona's Discount",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    cost = SET(1)


# TIME_707: Alternate Reality (2费 法术)
# 抉择：抽一张牌；或者还两张牌
class TIME_707:
    """Alternate Reality"""

    # 抉择：抽一张牌；或者还两张牌
    choose = ("TIME_707a", "TIME_707b")


class TIME_707a:
    """Past"""

    play = Draw(CONTROLLER)


class TIME_707b:
    """Future"""

    play = Draw(CONTROLLER) * 2


# TIME_730: Kaldorei Cultivator (2费 2/3)
# 战吼：如果你控制一个树人，获得+1/+1
class TIME_730:
    """Kaldorei Cultivator"""

    # 战吼：如果你控制一个树人，获得+1/+1
    play = Find(FRIENDLY_MINIONS + TREANT) & Buff(SELF, "TIME_730e")


TIME_730e = buff(+1, +1)
