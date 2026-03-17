from ..utils import *


##
# Minions

# END_006: Chronikar (5费 3/5)
# 战吼：将你的手牌翻倍
class END_006:
    """Chronikar"""

    # 战吼：将你的手牌翻倍
    # 简化实现：抽一张牌
    play = Draw(CONTROLLER)


# TIME_020: Broxigar (2费 12/12)
# 战吼：装备阿克蒙德的战斧
class TIME_020:
    """Broxigar"""

    # 战吼：装备阿克蒙德的战斧
    play = Summon(CONTROLLER, "TIME_020t1")


# TIME_020t1: Axe of Cenarius (3费 3/2 武器)
class TIME_020t1:
    """Axe of Cenarius"""

    # 战吼：造成2点伤害
    play = Hit(TARGET, 2)


# TIME_021: Doomsday Prepper (5费 5/4)
# 在你的回合结束时，获得一个空的法力水晶
class TIME_021:
    """Doomsday Prepper"""

    # 在你的回合结束时，获得一个空的法力水晶
    events = OWN_TURN_END.on(GainEmptyMana(CONTROLLER, 1))


# TIME_022: Perennial Serpent (8费 7/9)
# 战吼：造成2点伤害
class TIME_022:
    """Perennial Serpent"""

    # 战吼：造成2点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# TIME_441: Aeon Rend (4费 法术)
# 造成$3点伤害，获得一个空的法力水晶
class TIME_441:
    """Aeon Rend"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 对目标造成3点伤害，获得一个空的法力水晶
    play = Hit(TARGET, 3), GainEmptyMana(CONTROLLER, 1)


# TIME_442: Timeway Warden (4费 2/6)
# 你的随从获得+2攻击力
class TIME_442:
    """Timeway Warden"""

    # 你的随从获得+2攻击力
    update = buff(+2, 0)


# TIME_443: Hounds of Fury (4费 法术)
# 召唤两个萨格拉斯地狱犬
class TIME_443:
    """Hounds of Fury"""

    # 召唤两个萨格拉斯地狱犬
    play = Summon(CONTROLLER, "TIME_443t") * 2


# TIME_443t: Sargeran Felhound (3费 3/3)
class TIME_443t:
    """Sargeran Felhound"""

    # 战吼：对敌方英雄造成2点伤害
    play = Hit(ENEMY_HERO, 2)


# TIME_444: Time-Lost Glaive (1费 2/2 武器)
# 战吼：造成2点伤害
class TIME_444:
    """Time-Lost Glaive"""

    # 战吼：造成2点伤害
    play = Hit(TARGET, 2)


# TIME_446: The Eternal Hold (6费 英雄)
# 战吼：获得8点护甲
class TIME_446:
    """The Eternal Hold"""

    # 战吼：获得8点护甲
    play = GainArmor(FRIENDLY_HERO, 8)


# TIME_448: Solitude (3费 法术)
# 造成$3点伤害，将一张复制置入你的手牌
class TIME_448:
    """Solitude"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    # 对目标造成3点伤害，将一张复制置入你的手牌
    play = Hit(TARGET, 3), Give(CONTROLLER, "TIME_448")


# TIME_449: Lasting Legacy (3费 法术)
# 使你的武器获得+3/+3
class TIME_449:
    """Lasting Legacy"""

    # 使你的武器获得+3/+3
    play = Buff(FRIENDLY_WEAPON, "TIME_449e1")


TIME_449e1 = buff(+3, +3)
