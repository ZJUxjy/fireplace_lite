from ..utils import *
from hearthstone.enums import SpellSchool


##
# Minions

# CATA_150: 拉格纳罗斯，绝世烈火 (8费 8/8)
# 巨型+2，在你的回合结束时，触发你的随从的亡语
class CATA_150:
    """Ragnaros, the Great Fire"""

    # 巨型+2：召唤2个手臂
    play = Summon(CONTROLLER, "CATA_150t") * 2

    # 在你的回合结束时，触发你的随从的亡语（随从不死亡）
    events = OWN_TURN_END.on(Deathrattle(FRIENDLY_MINIONS))


class CATA_150t:
    """Hand of Ragnaros"""

    # 亡语：对一个随机敌人造成2点伤害
    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


class CATA_150t1:
    """Hand of Ragnaros (upgraded)"""

    # 亡语：对一个随机敌人造成2点伤害
    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# CATA_160: 灼烧掠夺者 (4费 4/3)
# 战吼：兆示，使拉格纳罗斯的士兵获得冲锋
class CATA_160:
    """Scorching Ravager"""

    # 战吼：召唤一个拉格纳罗斯的士兵并使其获得冲锋
    play = Summon(CONTROLLER, "CATA_580t").then(
        GiveRush(Summon.CARD)
    )


# 亡语：对一个随机敌人造成2点伤害
class CATA_580t:
    """Soldier of Ragnaros"""

    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


# CATA_584: 喷发火山 (3费 3/3)
# 随机对敌人造成3点伤害(可分裂)，如果在本回合使用过火焰法术，再造成3点伤害
class CATA_584:
    """Erupting Volcano"""

    def play(self):
        yield Hit(RANDOM(ENEMY_CHARACTERS), 3)
        # 如果本回合使用过火焰法术，再造成3点伤害
        fire_spells_this_turn = [
            c for c in self.controller.cards_played_this_game
            if c.type == CardType.SPELL
            and c.turn_played == self.game.turn
            and getattr(getattr(c, "data", None), "spell_school", None) == SpellSchool.FIRE
        ]
        if fire_spells_this_turn:
            yield Hit(RANDOM(ENEMY_CHARACTERS), 3)


# CATA_586: 毁灭之焰 (5费 3/3)
# 在这次伤害后仍然存活，召唤一个毁灭之焰，亡语：对一个随机敌人造成2点伤害
class CATA_586:
    """Destructive Blaze"""

    # 在本随从受到伤害并存活下来后，召唤一个毁灭之焰。
    events = SELF_DAMAGE.on(Dead(SELF) | Summon(CONTROLLER, ExactCopy(SELF)))
    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


class CATA_591_DeckChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        actions = [Buff(card, "CATA_591e2"), ForceDraw(card)]
        actions.extend(Destroy(other) for other in self.cards if other is not card)
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class CATA_591_StartTurnDeckDiscover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        target.skip_next_turn_draw = True
        if not target.deck:
            return source.game.queue_actions(source, [Fatigue(target)])
        cards = list(target.deck)
        if len(cards) > 3:
            cards = source.game.random.sample(cards, 3)
        return source.game.queue_actions(source, [
            CATA_591_DeckChoice(target, cards)
        ])


# CATA_591: 指挥官迦顿 (7费 7/7)
# 战吼：你在每回合开始时的抽牌改为从你的牌库中发现一张牌，其法力值消耗减少（3）点，并摧毁未选的牌。
class CATA_591:
    """Commander Geddon"""

    play = Buff(CONTROLLER, "CATA_591e")


class CATA_591e:
    events = OWN_TURN_BEGIN.on(CATA_591_StartTurnDeckDiscover(CONTROLLER))


class CATA_591e2:
    tags = {GameTag.COST: -3}


# Spells


# CATA_581: 屠灭 (6费 法术)
# 对所有随从造成$@点伤害
class CATA_581:
    """Decimation"""

    # 对所有随从造成4点伤害
    play = Hit(ALL_MINIONS, 4)


# CATA_582: 灼热裂隙 (2费 法术)
# 对所有随从造成$1点伤害，使你的英雄获得+3攻击
class CATA_582:
    """Searing Fissure"""

    # 对所有随从造成1点伤害，使你的英雄获得+3攻击
    play = Hit(ALL_MINIONS, 1), Buff(FRIENDLY_HERO, "CATA_582e")


CATA_582e = buff(+3, 0)


# CATA_585: 烈火炙烤 (1费 法术)
# 对一个受伤的随从造成$@点伤害，将这张牌置入你的手牌，伤害超出目标生命值的部分会返还
class CATA_585:
    """Torch"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_DAMAGED_TARGET: 0,
    }

    # 对目标造成6点伤害，将这张牌置入你的手牌；溢出伤害给英雄+X攻击力
    def play(self):
        target = self.target
        leftover = max(0, 6 - target.health)
        yield Hit(target, 6)
        yield Give(CONTROLLER, "CATA_585")
        if leftover > 0:
            yield Buff(FRIENDLY_HERO, "CATA_585te", atk=leftover)


@custom_card
class CATA_585te:
    tags = {
        GameTag.CARDNAME: "Torch Return",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 0,
    }


# CATA_610: 洛戈什的奋战 (5费 法术)
# 使一个随从获得"亡语：随机从你的手牌中召唤一个随从"
class CATA_610:
    """Lo'Gosh's Last Stand"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    # 使目标获得亡语：随机从你的手牌中召唤一个随从
    play = Buff(TARGET, "CATA_610e")


class CATA_610e:
    """Lo'Gosh's Last Stand buff"""

    # 亡语：随机从你的手牌中召唤一个随从
    deathrattle = Summon(CONTROLLER, RANDOM(FRIENDLY_HAND + MINION))


# CATA_580: 灾变战斧 (3费 3/2 武器)
# 战吼：兆示
class CATA_580:
    """Cataclysmic War Axe"""

    # 战吼：造成2点伤害
    # 简化实现：战吼，对一个随机敌人造成2点伤害
    play = Hit(RANDOM(ENEMY_CHARACTERS), 2)
