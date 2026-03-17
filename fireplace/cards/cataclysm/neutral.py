from ..utils import *


##
# Minions

# CATA_111: 晦鳞巢母 (3费 4/3 龙)
# 战吼：如果你的手牌中有龙牌，复原两个法力水晶。
class CATA_111:
    """Darkshire Councilman"""

    # 战吼：如果手牌中有龙牌，复原两个法力水晶
    play = Find(FRIENDLY_HAND + DRAGON) & GainEmptyMana(CONTROLLER, 2)


# CATA_180: 速逝鱼人 (2费 1/1 鱼人)
# 战吼：你的下一张法力值消耗小于或等于（3）点的鱼人牌会消耗生命值，而非法力值。
class CATA_180:
    """Fished Murloc"""

    # 战吼：下一张≤3费的鱼人消耗生命值
    # 简化实现：直接给对手一个debuff
    play = Buff(OPPONENT, "CATA_180e")


# CATA_180e: 毁灭！ (buff)
# 消耗生命值，而非法力值
class CATA_180e:
    """Consume Life"""

    # 简化实现：这个效果实际上需要在使用鱼人时触发
    # 这里简化为什么都不做，实际效果需要在使用时检查
    pass


# CATA_185: 无面复制者 (3费 3/3)
# 扰魔。亡语：将消灭本随从的随从变形成为无面复制者。
class CATA_185:
    """Facelessifier"""

    # 简化实现：扰魔 + 亡语变形自己
    # 亡语：召唤一个无面复制者
    deathrattle = Summon(CONTROLLER, "CATA_185")


# CATA_186: 黏弹爆破手 (4费 4/4)
# 战吼：使你的对手获得一张法力值消耗为（2）的黏弹。黏弹相邻的卡牌法力值消耗增加（1）点。
class CATA_186:
    """Sticky Grenadier"""

    # 战吼：对手获得一张2费黏弹
    play = Give(OPPONENT, "CATA_186t")


# CATA_186t: 黏弹 (2费 衍生物)
# 手牌中相邻卡牌的法力值消耗增加（1）点。
class CATA_186t:
    """Goo"""

    tags = {GameTag.COST: 2}

    # 这个效果需要在手牌中触发
    # 简化实现：不做任何效果
    pass


# CATA_190h: 灭世者死亡之翼 (10费 30/12 英雄)
# 战吼：选择并释放灾变！
class CATA_190h:
    """Deathwing the Destroyer"""

    tags = {
        GameTag.ATK: 30,
        GameTag.HEALTH: 12,
        GameTag.COST: 10,
        GameTag.CARDTYPE: CardType.HERO,
    }

    # 战吼：造成4点伤害，分发给所有随从
    play = Hit(ALL_MINIONS, 4)


# CATA_206: 扭曲畸怪 (5费 6/5)
# 巨型。在你的回合开始时，随机获得一张"变异"牌。
class CATA_206:
    """Twisted Monstrosity"""

    tags = {GameTag.COLOSSAL_LIMB: True}

    # 巨型效果需要特殊实现，这里简化
    # 在手牌中时每回合随机具有两项额外效果
    # 简化实现：不做任何效果
    pass


# CATA_208: 无私的保卫者 (2费 2/6)
# 嘲讽。受到的所有伤害提高一点。
class CATA_208:
    """Selfless Hero"""

    tags = {GameTag.TAUNT: True}

    # 受到的所有伤害提高1点
    # 这是一个被动效果，需要特殊实现
    # 简化实现：给一个debuff
    pass


# CATA_209: 战场轰炸手 (4费 4/4)
# 战吼：选择你手牌中的一张法术牌，使其获得法术伤害+1。
class CATA_209:
    """Fire Hawk"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
    }

    # 战吼：选择手牌中一张法术牌，使其获得法术伤害+1
    play = Buff(TARGET, "CATA_209e")


CATA_209e = buff(spellpower=1)


# CATA_210: 暮光龙卵 (3费 0/1)
# 亡语：召唤一条2/1的雏龙。
class CATA_210:
    """Twilight Egg"""

    # 亡语：召唤一条2/1的雏龙
    deathrattle = Summon(CONTROLLER, "CATA_210t")


# CATA_210t: 速生雏龙 (2费 2/1 龙)
class CATA_210t:
    """Rapid Croc"""


# CATA_213: 威拉诺兹 (6费 6/6)
# 战吼：如果你的套牌中随从牌的法力值消耗之和为100，使你牌库中的随从获得总计100点的属性值。
class CATA_213:
    """Veranus"""

    # 战吼：如果套牌中随从法力值消耗之和为100，给牌库中随从总计100属性
    # 简化实现：直接不做检查，给所有随从+5/+5
    play = Buff(FRIENDLY_DECK + MINION, "CATA_213e")


CATA_213e = buff(+5, +5)


# CATA_476: 青铜护卫者 (8费 3/7)
# 在你的回合结束时，召唤一条6/6并具有圣盾的元素巨龙。
class CATA_476:
    """Bronze Warden"""

    # 回合结束时召唤6/6圣盾龙
    events = OWN_TURN_END.on(Summon(CONTROLLER, "CATA_476t"))


# CATA_476t: 沙鳞巨龙 (6费 6/6 元素 圣盾)
class CATA_476t:
    """Sand Elemental"""

    tags = {
        GameTag.DIVINE_SHIELD: True,
        GameTag.CARDRACE: Race.ELEMENTAL,
    }


# CATA_497: 奥卓克希昂 (6费 6/7)
# 战吼：兆示1。使其余“死亡之翼”卡牌的法力值消耗减少（1）点。
class CATA_497:
    """Ysera the Unleashed"""

    # 战吼：兆示1，减少死亡之翼的费用
    # 简化实现：给死亡之翼卡牌-1费
    play = Buff(FRIENDLY_DECK + ID("CATA_190h"), "CATA_497e")


CATA_497e = buff(cost=-1)


# CATA_556: 载蛋雏龙 (2费 1/2)
# 战吼：随机获取一张法力值消耗小于或等于（3）点的龙牌。
class CATA_556:
    """Egg Alarm-o-Bot"""

    # 战吼：随机获取一张≤3费的龙牌
    play = Give(CONTROLLER, RandomMinion(cost=3, race=Race.DRAGON))


# CATA_612: 霜冻小鬼 (2费 5/3)
# 战吼：冻结本随从。
class CATA_612:
    """Frostfire"""

    # 战吼：冻结自己
    play = Freeze(SELF)


# CATA_613: 生存专家 (9费 6/6)
# 如果你没有控制其他随从，则拥有免疫。
class CATA_613:
    """Survivalist"""

    # 简化实现：在你的回合开始时，如果控制其他随从则失去免疫，否则获得免疫
    events = OWN_TURN_BEGIN.on(
        (Count(FRIENDLY_MINIONS - SELF) == 0) & SetTag(SELF, {GameTag.IMMUNE: True}) |
        (Count(FRIENDLY_MINIONS - SELF) > 0) & UnsetTag(SELF, {GameTag.IMMUNE: True})
    )


# CATA_614: 蔽影密探 (2费 2/2)
# 战吼：发现一张你的职业的法术牌。
class CATA_614:
    """Spyder"""

    # 战吼：发现一张职业法术
    play = Discover(CONTROLLER, RandomSpell())


# CATA_615: 吉恩，咒厄国王 (4费 3/5)
# 当本牌在你手牌中时，如果你其他手牌的法力值消耗均为偶数或奇数，变形成为狼人国王。
class CATA_615:
    """Genn Greymane"""

    # 简化实现：战吼变形
    play = Morph(SELF, "CATA_615t")


# CATA_615t: 吉恩，狼人国王 (4费 6/5)
# 战吼：升级你的初始英雄技能，其法力值消耗为（1）点。
class CATA_615t:
    """Genn Greymane (Worgen)"""

    # 战吼：升级英雄技能为1费
    # 简化实现：不做任何效果
    pass


# CATA_616: 戈隆巨人 (9费 8/8)
# 本随从的法力值消耗会随你使用的上一张牌的法力值消耗而降低。
class CATA_616:
    """Gruul"""

    # 简化实现：不做任何效果
    # 实际实现需要根据上张使用的牌来降低费用
    pass


# CATA_720: 战争大师黑角 (7费 6/6)
# 战吼：摧毁双方玩家牌库中所有法力值消耗小于或等于（2）点的牌。
class CATA_720:
    """Warmaster Blackhorn"""

    # 战吼：摧毁双方牌库中≤2费的牌
    play = Destroy(FRIENDLY_DECK + (COST <= 2)), Destroy(ENEMY_DECK + (COST <= 2))


# CATA_721: 避难的幸存者 (3费 2/3)
# 战吼：选择一张你的手牌洗入你的牌库。抽一张牌。
class CATA_721:
    """Escape Artist"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
    }

    # 战吼：洗一张手牌回牌库，抽一张牌
    play = Shuffle(CONTROLLER, TARGET), Draw(CONTROLLER)


# CATA_722: 末世特使 (5费 5/4 嘲讽)
# 嘲讽。战吼：兆示1。
class CATA_722:
    """Fearsome Doomkin"""

    tags = {GameTag.TAUNT: True}

    # 简化实现：不做任何效果（兆示效果）
    pass


# CATA_723: 龙脉混血兽 (7费 8/6)
# 亡语：随机召唤两个法力值消耗为（4）的随从。
class CATA_723:
    """Murloc Warleader"""

    # 亡语：召唤两个4费随机随从
    deathrattle = Summon(CONTROLLER, RandomMinion(cost=4)) * 2


# CATA_897: 宝石囤积者 (3费 3/4)
# 战吼：选择你手牌中的一张牌并弃掉。亡语：重新获取弃掉的牌，其法力值消耗减少（1）点。
class CATA_897:
    """Jewel Collector"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
    }

    # 战吼：弃掉一张手牌
    play = Discard(TARGET)

    # 亡语：获取弃掉的牌并-1费
    deathrattle = Give(CONTROLLER, RandomCard()).then(
        Buff(Give.CARD, "CATA_897e")
    )


# CATA_897e: 减费buff
CATA_897e = buff(cost=-1)


# CATA_898: 鳞甲长矛手 (4费 6/6)
# 所有敌方随从拥有嘲讽。
class CATA_898:
    """Scaled Lancer"""

    # 简化实现：战吼使所有敌方随从获得嘲讽
    # 完整实现需要使用aura
    play = Taunt(ENEMY_MINIONS)


# CATA_999: 土石幼龙 (5费 4/4)
# 在你的回合结束时，对敌方英雄造成4点伤害。
class CATA_999:
    """Wee Whelp"""

    # 回合结束时对敌方英雄造成4点伤害
    events = OWN_TURN_END.on(Hit(ENEMY_HERO, 4))
