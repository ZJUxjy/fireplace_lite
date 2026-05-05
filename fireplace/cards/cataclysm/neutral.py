from ..utils import *

_SELF_IF_ALONE = FuncSelector(
    lambda entities, source: [source]
    if source.zone == Zone.PLAY
    and not any(m for m in source.controller.field if m is not source)
    else []
)


def _hand_adjacent(entities, source):
    if source.zone != Zone.HAND:
        return []
    hand = source.controller.hand
    index = hand.index(source)
    adjacent = []
    if index > 0:
        adjacent.append(hand[index - 1])
    if index + 1 < len(hand):
        adjacent.append(hand[index + 1])
    return adjacent


_HAND_ADJACENT = FuncSelector(_hand_adjacent)


def _genn_ready(entities, source):
    if source.zone != Zone.HAND:
        return []
    other_cards = [card for card in source.controller.hand if card is not source]
    if not other_cards:
        return [source]
    parity = other_cards[0].cost % 2
    if all(card.cost % 2 == parity for card in other_cards):
        return [source]
    return []


_GENN_READY = FuncSelector(_genn_ready)


def _remember_facelessifier_killer(entity, target, amount, damage_source):
    if (
        damage_source.type == CardType.MINION
        and damage_source.controller is not entity.controller
        and damage_source.zone == Zone.PLAY
        and (target.dead or damage_source.poisonous)
    ):
        entity._facelessifier_killer = damage_source


##
# Minions

# CATA_111: 晦鳞巢母 (3费 4/3 龙)
# 战吼：如果你的手牌中有龙牌，复原两个法力水晶。
class CATA_111:
    """Darkscale Broodmother"""

    # 战吼：如果手牌中有龙牌，复原两个法力水晶
    play = Find(FRIENDLY_HAND + DRAGON) & GainEmptyMana(CONTROLLER, 2)


# CATA_180: 速逝鱼人 (2费 1/1 鱼人)
# 战吼：你的下一张法力值消耗小于或等于（3）点的鱼人牌会消耗生命值，而非法力值。
class CATA_180:
    """War'loc"""

    play = Buff(CONTROLLER, "CATA_180e")


# CATA_180e: 毁灭！ (buff)
# 消耗生命值，而非法力值
class CATA_180e:
    """Doom!"""

    events = Play(CONTROLLER, MURLOC + (COST <= 3)).on(Destroy(SELF))
    update = Refresh(
        CONTROLLER,
        {
            enums.MURLOCS_COST_HEALTH: True,
            enums.MURLOCS_COST_HEALTH_MAX: 3,
        },
    )


# CATA_185: 无面复制者 (3费 3/3)
# 扰魔。亡语：将消灭本随从的随从变形成为无面复制者。
class CATA_185:
    """Faceless Replicator"""

    tags = {
        GameTag.ELUSIVE: True,
        GameTag.CANT_BE_TARGETED_BY_ABILITIES: True,
        GameTag.CANT_BE_TARGETED_BY_HERO_POWERS: True,
    }

    events = Damage(SELF).on(_remember_facelessifier_killer)

    def deathrattle(self):
        killer = getattr(self, "_facelessifier_killer", None)
        if killer and killer.zone == Zone.PLAY and not killer.dead:
            return (Morph(killer, "CATA_185"),)


# CATA_186: 黏弹爆破手 (4费 4/4)
# 战吼：使你的对手获得一张法力值消耗为（2）的黏弹。黏弹相邻的卡牌法力值消耗增加（1）点。
class CATA_186:
    """Stickybomb Saboteur"""

    # 战吼：对手获得一张2费黏弹
    play = Give(OPPONENT, "CATA_186t")


# CATA_186t: 黏弹 (2费 衍生物)
# 手牌中相邻卡牌的法力值消耗增加（1）点。
class CATA_186t:
    """Sabotage!"""

    tags = {GameTag.COST: 2}

    class Hand:
        update = Refresh(_HAND_ADJACENT, {GameTag.COST: +1})


# CATA_190h: 灭世者死亡之翼 (10费 30/12 英雄)
# 战吼：选择并释放灾变！
class CATA_190h:
    """Deathwing, Worldbreaker"""

    tags = {
        GameTag.ATK: 30,
        GameTag.HEALTH: 12,
        GameTag.COST: 10,
        GameTag.CARDTYPE: CardType.HERO,
    }

    # 战吼：造成4点伤害，分发给所有随从
    play = Hit(ALL_MINIONS, 4)


# CATA_206: 扭曲畸怪 (5费 6/5)
# 扰魔。嘲讽。本牌在你的手牌中时，每回合随机具有两项额外效果。
class CATA_206:
    """Twisted Monstrosity"""

    tags = {
        GameTag.TAUNT: True,
        GameTag.ELUSIVE: True,
        GameTag.CANT_BE_TARGETED_BY_ABILITIES: True,
        GameTag.CANT_BE_TARGETED_BY_HERO_POWERS: True,
    }


# CATA_208: 无私的保卫者 (2费 2/6)
# 嘲讽。受到的所有伤害提高一点。
class CATA_208:
    """Selfless Protector"""

    tags = {GameTag.TAUNT: True}

    events = Predamage(SELF).on(
        Predamage(SELF, 0), Damage(SELF, Predamage.AMOUNT + 1)
    )


# CATA_209: 战场轰炸手 (4费 4/4)
# 战吼：选择你手牌中的一张法术牌，使其获得法术伤害+1。
class CATA_209:
    """Battlefield Blaster"""

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
class CATA_213_BuffDeck(TargetedAction):
    def do(self, source, target):
        minions = [card for card in target.deck if card.type == CardType.MINION]
        if not minions or sum(card.cost for card in minions) != 100:
            return
        actions = [
            Buff(
                source.game.random.choice(minions),
                source.game.random.choice(("CATA_213e", "CATA_213e2")),
            )
            for _ in range(100)
        ]
        source.game.queue_actions(source, actions)


class CATA_213:
    """Vyranoth"""

    play = CATA_213_BuffDeck(CONTROLLER)


CATA_213e = buff(+1, 0)
CATA_213e2 = buff(0, +1)


class CATA_DeathwingHerald(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        heralds = getattr(target, "_cataclysm_heralds", {}).copy()
        heralds["deathwing"] = heralds.get("deathwing", 0) + 1
        target._cataclysm_heralds = heralds


# CATA_476: 青铜护卫者 (8费 3/7)
# 在你的回合结束时，召唤一条6/6并具有圣盾的元素巨龙。
class CATA_476:
    """Bronze Keeper"""

    # 回合结束时召唤6/6圣盾龙
    events = OWN_TURN_END.on(Summon(CONTROLLER, "CATA_476t"))


# CATA_476t: 沙鳞巨龙 (6费 6/6 元素 圣盾)
class CATA_476t:
    """Sandscale Dragon"""

    tags = {
        GameTag.DIVINE_SHIELD: True,
        GameTag.CARDRACE: Race.ELEMENTAL,
    }


# CATA_497: 奥卓克希昂 (6费 6/7)
# 战吼：兆示1。使其余“死亡之翼”卡牌的法力值消耗减少（1）点。
class CATA_497:
    """Ultraxion"""

    # 战吼：兆示。使死亡之翼的法力值消耗减少（1）点
    play = (
        CATA_DeathwingHerald(CONTROLLER),
        Buff((FRIENDLY_HAND | FRIENDLY_DECK) + ID("CATA_190h"), "CATA_497e"),
    )


CATA_497e = buff(cost=-1)


# CATA_556: 载蛋雏龙 (2费 1/2)
# 战吼：随机获取一张法力值消耗小于或等于（3）点的龙牌。
class CATA_556:
    """Carrier Whelp"""

    # 战吼：随机获取一张≤3费的龙牌
    play = Give(CONTROLLER, RandomMinion(cost=list(range(4)), race=Race.DRAGON))


# CATA_612: 霜冻小鬼 (2费 5/3)
# 战吼：冻结本随从。
class CATA_612:
    """Frostbitten Imp"""

    # 战吼：冻结自己
    play = Freeze(SELF)


# CATA_613: 生存专家 (9费 6/6)
# 如果你没有控制其他随从，则拥有免疫。
class CATA_613:
    """Survivalist"""

    # 如果没有控制其他随从，则拥有免疫（持续光环）
    update = Refresh(_SELF_IF_ALONE, {GameTag.IMMUNE: True})


# CATA_614: 蔽影密探 (2费 2/2)
# 战吼：发现一张你的职业的法术牌。
class CATA_614:
    """Shadowed Informant"""

    # 战吼：发现一张职业法术
    play = Discover(CONTROLLER, RandomSpell())


# CATA_615: 吉恩，咒厄国王 (4费 3/5)
# 当本牌在你手牌中时，如果你其他手牌的法力值消耗均为偶数或奇数，变形成为狼人国王。
class CATA_615:
    """Genn, Cursed King"""

    class Hand:
        update = Find(_GENN_READY) & Morph(SELF, "CATA_615t")


# CATA_615t: 吉恩，狼人国王 (4费 6/5)
# 战吼：升级你的初始英雄技能，其法力值消耗为（1）点。
class CATA_615e:
    """The Moooon"""

    cost = SET(1)


class CATA_615t:
    """Genn Greymane (Worgen)"""

    play = Buff(FRIENDLY_HERO_POWER, "CATA_615e")


def _gruul_cost(entity, i):
    """Gruul hand aura: cost decreases by the cost of the last card played."""
    played = entity.controller.cards_played_this_game
    if played:
        return i - played[-1].data.cost
    return i


# CATA_616: 戈隆巨人 (9费 8/8)
# 本随从的法力值消耗会随你使用的上一张牌的法力值消耗而降低。
class CATA_616:
    """Gronn Giant"""

    class Hand:
        update = Refresh(SELF, {GameTag.COST: _gruul_cost})


# CATA_720: 战争大师黑角 (7费 6/6)
# 战吼：摧毁双方玩家牌库中所有法力值消耗小于或等于（2）点的牌。
class CATA_720:
    """Warmaster Blackhorn"""

    # 战吼：摧毁双方牌库中≤2费的牌
    play = Destroy(FRIENDLY_DECK + (COST <= 2)), Destroy(ENEMY_DECK + (COST <= 2))


# CATA_721: 避难的幸存者 (3费 2/3)
# 战吼：选择一张你的手牌洗入你的牌库。抽一张牌。
class CATA_721:
    """Sheltered Survivor"""

    # 战吼：洗一张手牌回牌库，抽一张牌
    play = Choice(CONTROLLER, FRIENDLY_HAND - SELF).then(
        Shuffle(CONTROLLER, Choice.CARD), Draw(CONTROLLER)
    )


# CATA_722: 末世特使 (5费 5/4 嘲讽)
# 嘲讽。战吼：兆示1。
class CATA_722:
    """Envoy of the End"""

    tags = {GameTag.TAUNT: True}

    # 战吼：兆示
    play = CATA_DeathwingHerald(CONTROLLER)


# CATA_723: 龙脉混血兽 (7费 8/6)
# 亡语：随机召唤两个法力值消耗为（4）的随从。
class CATA_723:
    """Drakeadon Mongrel"""

    # 亡语：召唤两个4费随机随从
    deathrattle = Summon(CONTROLLER, RandomMinion(cost=4)) * 2


# CATA_897: 宝石囤积者 (3费 3/4)
# 战吼：选择你手牌中的一张牌并弃掉。亡语：重新获取弃掉的牌，其法力值消耗减少（1）点。
class CATA_897_RememberDiscard(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        source._jewel_collector_card_id = target.id
        source.game.queue_actions(source, [Discard(target)])


class CATA_897:
    """Gemstone Hoarder"""

    # 战吼：弃掉一张手牌
    play = Choice(CONTROLLER, FRIENDLY_HAND - SELF).then(
        CATA_897_RememberDiscard(Choice.CARD)
    )

    def deathrattle(self):
        card_id = getattr(self, "_jewel_collector_card_id", None)
        if card_id:
            return (Give(CONTROLLER, card_id).then(Buff(Give.CARD, "CATA_897e")),)


# CATA_897e: 减费buff
@custom_card
class CATA_897e:
    tags = {
        GameTag.CARDNAME: "Jewel Discount",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


# CATA_898: 鳞甲长矛手 (4费 6/6)
# 所有敌方随从拥有嘲讽。
class CATA_898:
    """Scaled Lancer"""

    # 所有敌方随从拥有嘲讽（持续光环）
    update = Refresh(ENEMY_MINIONS, {GameTag.TAUNT: True})


# CATA_999: 土石幼龙 (5费 4/4)
# 在你的回合结束时，对敌方英雄造成4点伤害。
class CATA_999:
    """Earthen Drake"""

    # 回合结束时对敌方英雄造成4点伤害
    events = OWN_TURN_END.on(Hit(ENEMY_HERO, 4))
