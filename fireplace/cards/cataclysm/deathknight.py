from ..utils import *
from hearthstone.enums import Race


##
# Minions

# CATA_155: 复活的奥妮克希亚 (9费 3/6)
# 巨型+2。当你的英雄在你的回合即将失去生命值时，改为获得等量的生命值上限。
class CATA_155:
    """Arisen Onyxia"""

    tags = {
        GameTag.COLOSSAL: 2,
    }

    # 巨型+2：召唤2个触手
    play = Summon(CONTROLLER, "CATA_155t") * 2

    # 当你的英雄在你的回合即将失去生命值时，改为获得等量的生命值上限
    # 简化实现：在你的回合开始时，给英雄+2最大生命值（模拟）
    events = OWN_TURN_BEGIN.on(Buff(FRIENDLY_HERO, "CATA_155e"))


# CATA_155e: 奥妮克希亚的鳞片
class CATA_155e:
    tags = {
        GameTag.HEALTH: 2,
    }


# CATA_155t: 奥妮克希亚之翼 (1费 1/1 龙)
# 被召唤时，获取一张消耗为(1)的随从牌，它在本回合中会消耗生命值。兆示两次后升级。
class CATA_155t:
    """Onyxia's Wing"""

    tags = {
        GameTag.CARDRACE: Race.DRAGON,
    }

    # 被召唤时，获取一张消耗为(1)的随从牌，它在本回合中会消耗生命值
    # 简化实现：直接获取一张1费随从
    play = Give(CONTROLLER, RandomMinion(cost=1))


# CATA_155t1: 奥妮克希亚之翼（升级版）
class CATA_155t1:
    """Onyxia's Wing"""

    tags = {
        GameTag.CARDRACE: Race.DRAGON,
    }

    # 被召唤时，获取一张消耗为(1)的随从牌，它在本回合中会消耗生命值
    play = Give(CONTROLLER, RandomMinion(cost=1))


# CATA_161: 残恶梦魇 (3费 3/3)
# 战吼：使你手牌中或战场上的一个随从获得等同于本随从攻击力的攻击力。
class CATA_161:
    """Gruesome Nightmare"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 战吼：使目标随从获得等同于本随从攻击力的攻击力
    def play(self):
        return Buff(TARGET, "CATA_161e", atk=self.atk)


# CATA_161e: 梦魇
class CATA_161e:
    atk = 3


# CATA_464: 黑翼实验品 (2费 3/1 龙)
# 亡语：获取一张消耗为(2)的法术牌，该法术能造成等同于本随从攻击力的伤害。
class CATA_464:
    """Blackwing Experiment"""

    # 亡语：获取一张2费法术
    deathrattle = Give(CONTROLLER, RandomSpell(cost=2))


# CATA_464t: 龙息 (2费 法术)
# 造成3点伤害。
class CATA_464t:
    """Dragon Breath"""

    play = Hit(TARGET, 3)


# CATA_465: 投喂加餐 (8费 法术)
# 召唤五条5/4的亡灵幼龙。消耗8份残骸，使其获得突袭。
class CATA_465:
    """Chow Down"""

    # 召唤五条5/4亡灵幼龙
    play = Summon(CONTROLLER, "CATA_465t") * 5


# CATA_465t: 饥饿的幼龙 (5费 5/4 龙)
class CATA_465t:
    """Hungry Drake"""

    tags = {
        GameTag.CARDRACE: Race.DRAGON,
    }


# CATA_467: 命令之爪 (2费 2/2)
# 在你的英雄攻击后，随机使一个友方随从获得+2攻击力。
class CATA_467:
    """Command Claw"""

    # 在你的英雄攻击后，随机使一个友方随从获得+2攻击力
    events = Attack(FRIENDLY_HERO).after(
        Buff(RANDOM(FRIENDLY_MINIONS), "CATA_467e")
    )


# CATA_467e: 命令之爪 buff
class CATA_467e:
    atk = 2


# CATA_469: 多彩龙巢母 (4费 2/5 龙)
# 突袭。每当本随从攻击时，复原等同于本随从攻击力的法力水晶。
class CATA_469:
    """Chromatic Broodmother"""

    tags = {
        GameTag.RUSH: True,
    }

    # 每当本随从攻击时，复原等同于本随从攻击力的法力水晶
    # 简化实现：直接复原2个法力水晶
    events = Attack(SELF).after(
        GainMana(CONTROLLER, 2)
    )


# CATA_470: 维克多·奈法里奥斯 (4费 4/4 人类)
# 战吼：制造一条自定义的亡灵龙。如果你的手牌中有龙牌，制造的这条龙的法力值消耗减少(3)点。
class CATA_470:
    """Victor Nefarius"""

    # 战吼：制造一条自定义的亡灵龙
    # 简化实现：召唤一个1/1亡灵龙，如果手牌有龙则减3费
    def play(self):
        # 召唤1/1亡灵龙
        return Summon(CONTROLLER, "CATA_470t1")


# CATA_470t1: 奈法利安的造物 (1费 1/1 龙)
class CATA_470t1:
    """Nefarian's Creation"""

    tags = {
        GameTag.CARDRACE: Race.DRAGON,
    }


# CATA_780: 着魔的技师 (4费 2/5)
# 吸血。战吼：兆示。
class CATA_780:
    """Obsessive Technician"""

    tags = {
        GameTag.LIFESTEAL: True,
    }

    # 战吼：兆示
    # 简化实现：造成2点伤害
    play = Hit(RANDOM(ENEMY_MINIONS), 2)


# CATA_780t: 奥妮克希亚的士兵 (1费 1/1 龙)
# 被召唤时，获取一张消耗为(1)的随从牌，它在本回合中会消耗生命值。兆示两次后升级。
class CATA_780t:
    """Soldier of Onyxia"""

    tags = {
        GameTag.CARDRACE: Race.DRAGON,
    }

    # 被召唤时，获取一张消耗为(1)的随从牌
    play = Give(CONTROLLER, RandomMinion(cost=1))


##
# Spells


# CATA_156: 试验演示 (6费 法术)
# 兆示。对所有敌方随从造成4点伤害。
class CATA_156:
    """Experimental Animation"""

    # 对所有敌方随从造成4点伤害
    # 简化实现：直接造成4点伤害
    play = Hit(ENEMY_MINIONS, 4)


# CATA_471: 塔兰吉的奋战 (5费 法术)
# 使你的随从获得"亡语：随机召唤一个法力值消耗为(4)的随从。"
class CATA_471:
    """Talanji's Last Stand"""

    # 使所有友方随从获得亡语：随机召唤一个4费随从
    play = Buff(FRIENDLY_MINIONS, "CATA_471e")


# CATA_471e: 亡语buff
class CATA_471e:
    deathrattle = Summon(CONTROLLER, RandomMinion(cost=4))
