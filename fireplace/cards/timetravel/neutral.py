from ..utils import *
from fireplace.cards import db


class _DoubleHandAction(TargetedAction):
    """Give a copy of each card currently in the target player's hand."""
    TARGET = ActionArg()

    def do(self, source, target):
        for card in list(target.hand):
            Give(CONTROLLER, card.id).trigger(source)


DOUBLE_HAND = _DoubleHandAction(CONTROLLER)


class TIME_EVENT_997_ReopenLocation(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, location):
        location.location_exhausted = False
        location.tags[GameTag.DEATHRATTLE] = True
        location.additional_deathrattles.append(
            (Summon(CONTROLLER, RandomMinion(cost=3)),)
        )
        source.game.manager.targeted_action(self, source, location)


class TIME_EVENT_301_DestroyOtherMinions(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        dragon_count = sum(
            1
            for card in source.controller.hand
            if Race.DRAGON in getattr(card, "races", [])
        )
        candidates = [
            card
            for card in source.game.board
            if card.type == CardType.MINION and card is not source and not card.dead
        ]
        count = min(1 + dragon_count, len(candidates))
        if count:
            targets = source.game.random.sample(candidates, count)
            return source.game.queue_actions(source, [Destroy(target) for target in targets])


##
# Minions

# END_033: Prescient Slitherdrake (7费 6/8)
# 战吼：发现一张龙牌
class END_033:
    """Prescient Slitherdrake"""

    # 战吼：发现一张龙牌
    play = Discover(CONTROLLER, RandomDragon())


# END_034: Crumblecrusher (8费 8/6)
# 战吼：对所有敌人造成2点伤害
class END_034:
    """Crumblecrusher"""

    # 战吼：对所有敌人造成2点伤害
    play = Hit(ENEMY_CHARACTERS, 2)


# END_035: Omen of the End (5费 5/5)
# 战吼：随机将一张卡牌的费用变为0
class END_035:
    """Omen of the End"""

    # 战吼：随机将一张卡牌的费用变为0
    play = Buff(RANDOM(FRIENDLY_HAND), "END_035e")


class END_035e:
    cost = SET(0)


# END_036: Morchie (4费 3/6)
# 在你的回合结束时，对所有敌人造成1点伤害
class END_036:
    """Morchie"""

    # 在你的回合结束时，对所有敌人造成1点伤害
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 1))


# END_037: Endtime Murozond (9费 4/6)
# 战吼：获得你手牌中所有卡牌的费用
class END_037:
    """Endtime Murozond"""

    # 战吼：获得你手牌中所有卡牌的费用
    def play(self):
        total = sum(c.cost for c in self.controller.hand)
        yield GainMana(CONTROLLER, total)


# TIME_002: Aeon Wizard (5费 3/5)
# 在你的回合结束时，对所有敌人造成2点伤害
class TIME_002:
    """Aeon Wizard"""

    # 在你的回合结束时，对所有敌人造成2点伤害
    # No battlecry

    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 2))


# TIME_003: Portal Vanguard (3费 2/2)
# 战吼：对所有敌人造成1点伤害
class TIME_003:
    """Portal Vanguard"""

    # 战吼：对所有敌人造成1点伤害
    play = Hit(ENEMY_CHARACTERS, 1)


# TIME_004: Conflux Crasher (7费 7/7)
# 战吼：造成3点伤害
class TIME_004:
    """Conflux Crasher"""

    # 战吼：造成3点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 3)


# TIME_024: Murozond, Unbounded (9费 8/8)
# 战吼：获得你手牌中所有卡牌的费用
class TIME_024:
    """Murozond, Unbounded"""

    # 战吼：获得你手牌中所有卡牌的费用
    def play(self):
        total = sum(c.cost for c in self.controller.hand)
        yield GainMana(CONTROLLER, total)


# TIME_035: Time Machine (6费 6/6)
# 嘲讽。亡语：获取一张随机回溯牌
class TIME_035_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        pool = [
            card_id
            for card_id, data in db.items()
            if data.collectible
            and data.tags.get(GameTag.REWIND)
            and (not source.game.is_standard or data.is_standard)
        ]
        if not pool and source.game.is_standard:
            pool = [
                card_id
                for card_id, data in db.items()
                if data.collectible and data.tags.get(GameTag.REWIND)
            ]
        if pool:
            return source.game.queue_actions(
                source, [Give(player, source.game.random.choice(pool))]
            )


class TIME_035:
    """Time Machine"""

    deathrattle = TIME_035_Deathrattle(CONTROLLER)


# TIME_038: Mister Clocksworth (8费 3/3)
# 战吼：发现一个时间点
class TIME_038:
    """Mister Clocksworth"""

    # 战吼：发现一个时间点
    play = Discover(CONTROLLER, RandomCard())


# TIME_040: Fading Memory (4费 6/3)
# 亡语：获取一张随机来自过去的5费随从牌
class TIME_040:
    """Fading Memory"""

    deathrattle = Give(CONTROLLER, RandomMinion(cost=5, is_standard=False))


# TIME_041: Futuristic Forefather (4费 4/4)
# 在你的回合开始时，获得一个空的法力水晶
class TIME_041:
    """Futuristic Forefather"""

    # 在你的回合开始时，获得一个空的法力水晶
    events = OWN_TURN_BEGIN.on(GainEmptyMana(CONTROLLER, 1))


# TIME_045: Whelp of the Infinite (3费 1/4)
# 战吼：获得一个空的法力水晶
class TIME_045:
    """Whelp of the Infinite"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_046: Cyborg Patriarch (3费 3/12)
# 在你的回合开始时，获得一个空的法力水晶
class TIME_046:
    """Cyborg Patriarch"""

    # 在你的回合开始时，获得一个空的法力水晶
    # No battlecry

    events = OWN_TURN_BEGIN.on(GainEmptyMana(CONTROLLER, 1))


# TIME_047: Devious Coyote (5费 5/3)
# 战吼：获得一个空的法力水晶
class TIME_047:
    """Devious Coyote"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_048: Clockwork Rager (5费 5/1)
# 在你的回合结束时，获得+2攻击力
class TIME_048:
    """Clockwork Rager"""

    # 在你的回合结束时，获得+2攻击力
    events = OWN_TURN_END.on(Buff(SELF, "TIME_048e"))


TIME_048e = buff(+2, 0)


# TIME_049: Dangerous Variant (2费 1/1)
# 战吼：造成2点伤害
class TIME_049:
    """Dangerous Variant"""

    # 战吼：造成2点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# TIME_050: Sentient Hourglass (6费 4/9)
# 在你的回合结束时，对所有敌人造成2点伤害
class TIME_050:
    """Sentient Hourglass"""

    # 在你的回合结束时，对所有敌人造成2点伤害
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 2))


# TIME_051: Soldier of the Infinite (5费 3/5)
# 战吼：获得+2/+2
class TIME_051:
    """Soldier of the Infinite"""

    # 战吼：获得+2/+2
    play = Buff(SELF, "TIME_051e")


TIME_051e = buff(+2, +2)


# TIME_052: Amber Warden (8费 4/12)
# 嘲讽。亡语：召唤一个随机来自过去的随从
class TIME_052:
    """Amber Warden"""

    deathrattle = Summon(CONTROLLER, RandomMinion(is_standard=False))


# TIME_053: Sandmaw (3费 7/2)
# 战吼：对一个随机敌人造成4点伤害
class TIME_053:
    """Sandmaw"""

    # 战吼：对一个随机敌人造成4点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 4)


# TIME_054: Time Skipper (4费 3/4)
# 战吼：将你的手牌翻倍
class TIME_054:
    """Time Skipper"""

    # 战吼：将你的手牌翻倍
    def play(self):
        for card in list(self.controller.hand):
            yield Give(CONTROLLER, card.id)


# TIME_055: Unknown Voyager (5费 4/5)
# 战吼：发现一张卡牌
class TIME_055:
    """Unknown Voyager"""

    # 战吼：发现一张卡牌
    play = Discover(CONTROLLER, RandomCard())


# TIME_056: Whelp of the Bronze (3费 4/1)
# 战吼：获得一个空的法力水晶
class TIME_056:
    """Whelp of the Bronze"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_057: Wizened Truthseeker (4费 4/5)
# 在你的回合开始时，发现一张卡牌
class TIME_057:
    """Wizened Truthseeker"""

    # 在你的回合开始时，发现一张卡牌
    events = OWN_TURN_BEGIN.on(Discover(CONTROLLER, RandomCard()))


# TIME_058: Paltry Flutterwing (1费 1/1)
# 亡语：获得一个空的法力水晶
class TIME_058:
    """Paltry Flutterwing"""

    # 亡语：获得一个空的法力水晶
    deathrattle = GainEmptyMana(CONTROLLER, 1)


# TIME_059: Living Paradox (3费 2/1)
# 战吼：获得一个空的法力水晶
class TIME_059:
    """Living Paradox"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_060: Quantum Destabilizer (3费 4/9)
# 战吼：对所有敌人造成2点伤害
class TIME_060:
    """Quantum Destabilizer"""

    # 战吼：对所有敌人造成2点伤害
    play = Hit(ENEMY_CHARACTERS, 2)


# TIME_061: Timeless Causality (2费 3/2)
# 战吼：获得一个空的法力水晶
class TIME_061:
    """Timeless Causality"""

    # 战吼：获得一个空的法力水晶
    play = GainEmptyMana(CONTROLLER, 1)


# TIME_062: Chronicle Keeper (4费 3/6)
# 在你的回合结束时，抽一张牌
class TIME_062:
    """Chronicle Keeper"""

    # 在你的回合结束时，抽一张牌
    events = OWN_TURN_END.on(Draw(CONTROLLER))


# TIME_063: Timelord Nozdormu (3费 8/8)
# 在你的回合开始时，对所有敌人造成2点伤害
class TIME_063:
    """Timelord Nozdormu"""

    # 在你的回合开始时，对所有敌人造成2点伤害
    events = OWN_TURN_BEGIN.on(Hit(ENEMY_CHARACTERS, 2))


# TIME_064: Chrono-Lord Deios (7费 4/8)
# 在你的回合结束时，对所有敌人造成3点伤害
class TIME_064:
    """Chrono-Lord Deios"""

    # 在你的回合结束时，对所有敌人造成3点伤害
    events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 3))


# TIME_100: Hourglass Attendant (4费 2/4)
# 圣盾。在你的回合结束时，使你手牌中的所有随从获得+1/+1
class TIME_100:
    """Hourglass Attendant"""

    tags = {
        GameTag.DIVINE_SHIELD: True,
    }

    # 在你的回合结束时，使你手牌中的所有随从获得+1/+1
    events = OWN_TURN_END.on(Buff(FRIENDLY_HAND + MINION, "TIME_100e"))


TIME_100e = buff(+1, +1)


# TIME_101: Misplaced Pyromancer (3费 4/3)
# 战吼：对所有敌人造成1点伤害
class TIME_101:
    """Misplaced Pyromancer"""

    # 战吼：对所有敌人造成1点伤害
    play = Hit(ENEMY_CHARACTERS, 1)


# TIME_102: Circadiamancer (3费 2/2)
# 在你的回合开始时，获得一个空的法力水晶
class TIME_102:
    """Circadiamancer"""

    # 在你的回合开始时，获得一个空的法力水晶
    # No battlecry

    events = OWN_TURN_BEGIN.on(GainEmptyMana(CONTROLLER, 1))


class TIME_103_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        played_ids = {card.id for card in player.cards_played_this_game}
        targets = [card for card in list(player.deck) if card.id in played_ids]
        return source.game.queue_actions(source, [ForceDraw(card) for card in targets])


# TIME_103: Chromie (6费 4/6)
# 亡语：抽取你在本局对战中使用过的牌的另一张复制
class TIME_103:
    """Chromie"""

    deathrattle = TIME_103_Deathrattle(CONTROLLER)


# TIME_428: Yesterloc (2费 3/1)
# 战吼：将一张随机随从的费用变为0
class TIME_428:
    """Yesterloc"""

    # 战吼：将一张随机随从的费用变为0
    play = Buff(RANDOM(FRIENDLY_HAND + MINION), "TIME_428e")


class TIME_428e:
    cost = SET(0)


# TIME_434: Temporal Traveler (3费 4/1)
# 战吼：造成2点伤害
class TIME_434:
    """Temporal Traveler"""

    # 战吼：造成2点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# TIME_720: Soldier of the Bronze (5费 5/3)
# 战吼：获得+2/+2
class TIME_720:
    """Soldier of the Bronze"""

    # 战吼：获得+2/+2
    play = Buff(SELF, "TIME_720e")


TIME_720e = buff(+2, +2)


# TIME_EVENT_300: Dark Iron Harbinger (4费 7/4)
# 亡语：召唤一个0/7的末日预言者，在你的回合开始时消灭所有随从
class TIME_EVENT_300:
    """Dark Iron Harbinger"""

    # 亡语：召唤一个末日预言者
    deathrattle = Summon(CONTROLLER, "TIME_EVENT_300t")


# TIME_EVENT_300t: Doomsayer
class TIME_EVENT_300t:
    """Doomsayer"""

    # 在你的回合开始时，消灭所有随从
    events = OWN_TURN_BEGIN.on(Destroy(ALL_MINIONS))


# TIME_EVENT_301: Disciole of Demise (8费 8/8)
# 战吼：随机消灭另一个随从。每持有一张龙牌，重复一次
class TIME_EVENT_301:
    """Disciple of Demise"""

    # 战吼：随机消灭另一个随从；每持有一张龙牌，重复一次
    play = TIME_EVENT_301_DestroyOtherMinions(SELF)


# TIME_EVENT_997: Welcome Home! (3费 法术)
# 重新打开一个位置。使其获得“亡语：召唤一个随机3费随从”
class TIME_EVENT_997:
    """Welcome Home!"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_LOCATION_TARGET: 0,
    }

    # 重新打开一个位置。使其获得“亡语：随机召唤一个法力值消耗为（3）的随从”
    play = TIME_EVENT_997_ReopenLocation(TARGET)


# TIME_EVENT_999: Sands of Time (1费 法术)
# 回响。发现一张任意职业的法术
class TIME_EVENT_999:
    """Sands of Time"""

    # 回响，发现一张任意职业的法术
    play = Discover(CONTROLLER, RandomCard())
