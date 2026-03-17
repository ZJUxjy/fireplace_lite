from ..utils import *


##
# Minions

# CATA_550: Magmaw (熔喉) - 7费 2/12 野兽
# 巨型+2: 召唤2个肢体
# 战吼: 如果没有其他随从，召唤5个熔喉的肢体
class CATA_550:
    """Magmaw"""

    # 巨型+2: 召唤2个肢体
    play = Summon(CONTROLLER, "CATA_550t") * 2


# CATA_550t: Magmaw's Body (熔喉的肢体) - 1费 2/1
# 亡语: 对一个随机敌人造成2点伤害
class CATA_550t:
    """Magmaw's Body"""

    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# CATA_551: Stonetalon Striker (石爪打击者) - 3费 3/3
# 战吼: 如果控制一个野兽，获得+3/+3
class CATA_551:
    """Stonetalon Striker"""

    # 战吼: 如果控制一个野兽，获得+3/+3
    powered_up = Find(FRIENDLY_MINIONS + BEAST)
    play = powered_up & Buff(SELF, "CATA_551e")


CATA_551e = buff(+3, +3)


# CATA_552: Ebonscale Scout (黑鳞斥候) - 6费 4/4
# 战吼: 如果控制一个野兽，将一个友方野兽移回你的手牌
class CATA_552:
    """Ebonscale Scout"""

    # 战吼: 如果控制一个野兽，将一个友方野兽移回你的手牌
    powered_up = Find(FRIENDLY_MINIONS + BEAST)
    play = powered_up & Bounce(RANDOM(FRIENDLY_MINIONS + BEAST))


# CATA_553: Ebyssian (埃布西安) - 7费 6/6
# 战吼: 如果控制一个野兽，使其获得+6/+6
class CATA_553:
    """Ebyssian"""

    # 战吼: 如果控制一个野兽，使其获得+6/+6
    powered_up = Find(FRIENDLY_MINIONS + BEAST)
    play = powered_up & Buff(RANDOM(FRIENDLY_MINIONS + BEAST), "CATA_553e")


CATA_553e = buff(+6, +6)


##
# Spells

# CATA_554: Earthen Roar (大地之吼) - 1费 法术
# 使一个随从获得+4/+4
class CATA_554:
    """Earthen Roar"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Buff(TARGET, "CATA_554e")


CATA_554e = buff(+4, +4)


# CATA_557: Sylvanas's Triumph (希尔瓦娜斯的胜利) - 2费 法术
# 召唤一个2/2的骷髅
class CATA_557:
    """Sylvanas's Triumph"""

    # 召唤一个2/2的骷髅
    play = Summon(CONTROLLER, "CATA_557t")


# CATA_557t: Skeleton (骷髅) - 2费 2/2
class CATA_557t:
    """Skeleton"""


# CATA_558: Reinforcement Rallier (增援召集者) - 1费 2/2
# 战吼: 如果你的手牌中有另一张增援召集者，召唤一个2/2
class CATA_558:
    """Reinforcement Rallier"""

    # 战吼: 如果你的手牌中有另一张增援召集者，召唤一个2/2
    def play(self):
        if self.controller.hand.filter(id="CATA_558"):
            yield Summon(CONTROLLER, "CATA_558t")


# CATA_558t: Reinforcement (增援) - 1费 2/2
class CATA_558t:
    """Reinforcement"""


# CATA_560: Confront the Tol'vir (面对托维尔人) - 3费 法术
# 造成3点伤害
class CATA_560:
    """Confront the Tol'vir"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    play = Hit(TARGET, 3)


# CATA_566: Tol'vir Carver (托维尔雕刻师) - 3费 3/2
# 战吼: 随机使一个友方野兽获得+1/+1
class CATA_566:
    """Tol'vir Carver"""

    # 战吼: 随机使一个友方野兽获得+1/+1
    powered_up = Find(FRIENDLY_MINIONS + BEAST)
    play = powered_up & Buff(RANDOM(FRIENDLY_MINIONS + BEAST), "CATA_566e")


CATA_566e = buff(+1, +1)


# CATA_820: Supply Run (运输补给) - 4费 法术
# 使你的所有野兽获得+1/+1
class CATA_820:
    """Supply Run"""

    # 使你的所有野兽获得+1/+1
    play = Buff(FRIENDLY_MINIONS + BEAST, "CATA_820e")


CATA_820e = buff(+1, +1)
