from ..utils import *


##
# Minions

# CATA_550: Magmaw (熔喉) - 7费 2/12 野兽
# 巨型+99。当场上有空位时，召唤剩余的肢节。
class CATA_550_FillLimbs(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, body):
        if body.zone != Zone.PLAY:
            return
        if not hasattr(body, "_cata_550_remaining_limbs"):
            body._cata_550_remaining_limbs = 99
        space = body.game.MAX_MINIONS_ON_FIELD - len(body.controller.field)
        amount = min(space, body._cata_550_remaining_limbs)
        if amount <= 0:
            return
        body._cata_550_remaining_limbs -= amount
        body.game.queue_actions(body, [Summon(body.controller, "CATA_550t")] * amount)


class CATA_550:
    """Magmaw"""

    play = CATA_550_FillLimbs(SELF)
    events = Death(FRIENDLY + MINION).after(CATA_550_FillLimbs(SELF))


# CATA_550t: Magmaw's Body (熔喉的肢节) - 1费 2/1
# 亡语：随机使一个友方随从获得+2攻击力。
class CATA_550t:
    """Magmaw's Body"""

    tags = {GameTag.COLOSSAL_LIMB: True}

    deathrattle = Buff(RANDOM(FRIENDLY_MINIONS), "CATA_550e1"), CATA_550_FillLimbs(
        COLOSSAL_BODY
    )


CATA_550e1 = buff(atk=2)


# CATA_551: Stonetalon Striker (石爪打击者) - 3费 3/3
# 嘲讽。当本牌在你手中时，使用一张龙牌即可将本牌变为6/6的龙。
class CATA_551:
    """Stonetalon Striker"""

    tags = {GameTag.TAUNT: True}

    class Hand:
        events = Play(CONTROLLER, DRAGON).after(Morph(SELF, "CATA_551t"))


class CATA_551t:
    """Stonetalon Striker"""

    tags = {GameTag.TAUNT: True}


# CATA_552: Ebonscale Scout (乌鳞斥候) - 6费 4/4
# 战吼：造成等同于本随从攻击力的伤害。当本牌在你手中时，使用一张龙牌即可将本牌变为8/8的龙。
class CATA_552:
    """Ebonscale Scout"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    play = Hit(TARGET, ATK(SELF))

    class Hand:
        events = Play(CONTROLLER, DRAGON).after(Morph(SELF, "CATA_552t"))


class CATA_552t:
    """Ebonscale Scout"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    play = Hit(TARGET, ATK(SELF))


# CATA_553: Ebyssian (埃布西安) - 7费 6/6
# 战吼：在本局对战中，你的龙拥有突袭。当本牌在你手中时，使用一张龙牌即可将本牌变为12/12的龙。
class CATA_553:
    """Ebyssian"""

    play = Buff(CONTROLLER, "CATA_553e")

    class Hand:
        events = Play(CONTROLLER, DRAGON).after(Morph(SELF, "CATA_553t"))


class CATA_553t:
    """Ebyssian"""

    play = Buff(CONTROLLER, "CATA_553e")


class CATA_553e:
    events = Summon(CONTROLLER, DRAGON).on(GiveRush(Summon.CARD))


class CATA_553e2:
    tags = {GameTag.RUSH: True}


##
# Spells

# CATA_554: Earthen Roar (撼地巨吼) - 1费 法术
# 将一个敌方随从的生命值变为1。如果你的手牌中有龙牌，再选择一个。
class CATA_554:
    """Earthen Roar"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }

    def play(self):
        target = self.target
        yield SetCurrentHealth(target, 1)
        if any(Race.DRAGON in card.races for card in self.controller.hand):
            candidates = [minion for minion in self.controller.opponent.field if minion is not target]
            if candidates:
                yield Choice(CONTROLLER, candidates).then(SetCurrentHealth(Choice.CARD, 1))


# CATA_557: Sylvanas's Triumph (希尔瓦娜斯的胜利) - 2费 法术
# 造成3点伤害。如果你使用过本牌的其他复制，改为对所有敌人造成伤害。
class CATA_557:
    """Sylvanas's Triumph"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }

    def play(self):
        if self.controller.cards_played_this_game.filter(id="CATA_557"):
            yield Hit(ENEMY_CHARACTERS, 3)
        elif self.target:
            yield Hit(self.target, 3)


# CATA_558: Reinforcement Rallier (进击的募援官) - 1费 2/2
# 扰魔
class CATA_558:
    """Reinforcement Rallier"""

    tags = {
        GameTag.ELUSIVE: True,
        GameTag.CANT_BE_TARGETED_BY_ABILITIES: True,
        GameTag.CANT_BE_TARGETED_BY_HERO_POWERS: True,
    }


# CATA_560: Confront the Tol'vir (面对托维尔人) - 3费 法术
# 再次使用你在本局对战中使用过的每一张法力值消耗为（1）的牌（尽可能以敌人为目标）。
class CATA_560_ReplayOneCostCards(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        for card in list(player.cards_played_this_game):
            if card.cost != 1:
                continue
            replay_card = player.card(card.id)
            if replay_card.type == CardType.SPELL:
                source.game.queue_actions(
                    source, [CastSpellTargetsEnemiesIfPossible(replay_card)]
                )
            else:
                source.game.queue_actions(source, [Summon(player, replay_card)])


class CATA_560:
    """Confront the Tol'vir"""

    play = CATA_560_ReplayOneCostCards(CONTROLLER)


# CATA_566: Tol'vir Carver (托维尔雕刻师) - 3费 3/2
# 战吼：选择你手牌中的一张牌。在你的回合开始时，其法力值消耗减少（1）点。
class CATA_566:
    """Tol'vir Carver"""

    play = Choice(CONTROLLER, FRIENDLY_HAND - SELF).then(Buff(Choice.CARD, "CATA_566e"))


class CATA_566e:
    events = OWN_TURN_BEGIN.on(Buff(OWNER, "CATA_566e2"))


@custom_card
class CATA_566e2:
    tags = {
        GameTag.CARDNAME: "Carving",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


# CATA_820: Supply Run (运输补给) - 4费 法术
# 裂变：抽三张随从牌。使你手牌中的随从牌获得+2/+2。
class CATA_820:
    """Supply Run"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + MINION)) * 3, Buff(
        FRIENDLY_HAND + MINION, "CATA_820e"
    )


class CATA_820t:
    """Supply Run"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + MINION)) * 3


class CATA_820t2:
    """Supply Run"""

    play = Buff(FRIENDLY_HAND + MINION, "CATA_820e")


CATA_820e = buff(+2, +2)
