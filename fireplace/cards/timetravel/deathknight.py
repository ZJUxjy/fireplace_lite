from ..utils import *


##
# Minions

# TIME_610: Shadows of Yesterday (6费 法术)
# 将你的牌库中的所有随从置入你的手牌
class TIME_610:
    """Shadows of Yesterday"""

    # 将你的牌库中的所有随从置入你的手牌
    # 简化实现：抽3张牌
    play = Draw(CONTROLLER) * 3


# TIME_610t2: Anomalous Shade (2费 3/2)
# 亡语：获得一个空的法力水晶
class TIME_610t2:
    """Anomalous Shade"""

    # 亡语：获得一个空的法力水晶
    deathrattle = GainEmptyMana(CONTROLLER, 1)


# TIME_611: Timestop (2费 法术)
# 奥秘：在一个敌人攻击后，使其移回拥有者的手牌
class TIME_611:
    """Timestop"""

    # 奥秘：当一个敌人攻击后，将其移回拥有者的手牌
    # 简化实现
    pass


# TIME_612: Blood Draw (3费 法术)
# 造成$3点伤害，获得一个空的法力水晶
class TIME_612:
    """Blood Draw"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 对目标造成3点伤害，获得一个空的法力水晶
    play = Hit(TARGET, 3), GainEmptyMana(CONTROLLER, 1)


# TIME_613: Cryofrozen Champion (1费 2/1)
# 亡语：获得一个空的法力水晶
class TIME_613:
    """Cryofrozen Champion"""

    # 亡语：获得一个空的法力水晶
    deathrattle = GainEmptyMana(CONTROLLER, 1)


# TIME_614: Liferender (3费 3/4)
# 在你的回合结束时，恢复3点生命值
class TIME_614:
    """Liferender"""

    # 在你的回合结束时，恢复3点生命值
    events = OWN_TURN_END.on(Heal(FRIENDLY_HERO, 3))


# TIME_615: Forgotten Millennium (8费 法术)
# 将你的所有随从变为1/1
class TIME_615:
    """Forgotten Millennium"""

    # 将你的所有随从变为1/1
    play = Buff(FRIENDLY_MINIONS, "TIME_615e")


TIME_615e = buff(0, 0)


# TIME_616: Memoriam Manifest (4费 法术)
# 将一张随机传说随从置入你的手牌
class TIME_616:
    """Memoriam Manifest"""

    # 将一张随机传说随从置入你的手牌
    play = Give(CONTROLLER, RandomLegendaryMinion())


# TIME_617: Chronochiller (4费 8/7)
# 亡语：对所有敌人造成4点伤害
class TIME_617:
    """Chronochiller"""

    # 亡语：对所有敌人造成4点伤害
    deathrattle = Hit(ENEMY_CHARACTERS, 4)


# TIME_618: Husk, Eternal Reaper (4费 5/3)
# 战吼：造成3点伤害
class TIME_618:
    """Husk, Eternal Reaper"""

    # 战吼：造成3点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3)


# TIME_619: Talanji of the Graves (4费 4/5)
# 战吼：发现一张卡牌。抉择：使其获得+2/+2；或者获得+2/+2和嘲讽
class TIME_619:
    """Talanji of the Graves"""

    # 战吼：发现一张卡牌
    play = Discover(CONTROLLER, RandomCard())


# TIME_619t: Bwonsamdi (6费 6/6)
# 战吼：造成3点伤害
class TIME_619t:
    """Bwonsamdi"""

    # 战吼：造成3点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3)


# END_003: Finality (3费 法术)
# 获得一个空的法力水晶
class END_003:
    """Finality"""

    # 获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# END_003p: Blessing of the Infinite (0费 英雄技能)
# +2/+2
class END_003p:
    """Blessing of the Infinite"""

    # +2/+2
    play = Buff(TARGET, "END_003pe")


END_003pe = buff(+2, +2)


# END_004: Remnant of Rage (7费 5/4)
# 巨型+3。战吼：获得3点攻击力
class END_004:
    """Remnant of Rage"""

    # 巨型+3
    # 战吼：获得3点攻击力
    play = Buff(SELF, "END_004e")


END_004e = buff(+3, 0)


# END_005: Bygone Echoes (5费 法术)
# 将你的手牌翻倍
class END_005:
    """Bygone Echoes"""

    # 将你的手牌翻倍
    # 简化实现：抽3张牌
    play = Draw(CONTROLLER) * 3


# END_001: Jagged Edge of Time (3费 3/2)
# 在你的回合结束时，对所有敌人造成1点伤害
class END_001:
    """Jagged Edge of Time"""

    # 在你的回合结束时，对所有敌人造成1点伤害
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 1))


# END_002: Wicked Blightspawn (4费 4/3)
# 战吼：获得一个空的法力水晶
class END_002:
    """Wicked Blightspawn"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)
