from ..utils import *


def _woodland_wonders_cost(entity, cost):
    if entity.controller.spellpower:
        return cost - 3
    return cost


def _effective_health(entity):
    return entity.health + getattr(entity, "armor", 0)


def _jade_display_bonus(player):
    return getattr(player, "_toy_803_jade_display_bonus", 0)


def _set_jade_display_bonus(player, amount):
    player._toy_803_jade_display_bonus = amount


def _jade_display_buff(card, amount):
    return Buff(card, "TOY_803e2", atk=amount, max_health=amount)


class TOY_800_SparklingPhial(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        before = _effective_health(target)
        source.game.queue_actions(source, [Hit(target, 2)])
        dealt = max(0, before - _effective_health(target))
        if dealt:
            source.game.queue_actions(
                source, [Buff(source.controller, "TOY_800e1", _discount=dealt)]
            )


class TOY_803_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = _jade_display_bonus(player) + 1
        _set_jade_display_bonus(player, amount)
        actions = [
            _jade_display_buff(card, 1)
            for card in player.hand + player.field + player.deck
            if card.id == "TOY_803" and card is not source
        ]
        for _ in range(2):
            card = player.card("TOY_803", source=source)
            actions.extend([_jade_display_buff(card, amount), Shuffle(player, card)])
        return source.game.queue_actions(source, actions)


class TOY_851_DeckChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        actions = [ForceDraw(card)]
        if self.player.spellpower:
            copy = self.player.card(card.id, source=self.source)
            actions.append(Give(self.player, copy))
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class TOY_851_DeckDiscover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = list(player.deck)
        if len(cards) > 3:
            cards = source.game.random.sample(cards, 3)
        return source.game.queue_actions(source, [TOY_851_DeckChoice(player, cards)])


##
# Minions


class MIS_300:
    """Snuggle Teddy"""

    play = Give(CONTROLLER, "MIS_300t")


class MIS_300t:
    """Snuggle Teddy"""


class MIS_301t:
    """Treant"""


class MIS_712:
    """Toyrantus"""

    play = (MANA(CONTROLLER) >= 10) & Buff(SELF, "MIS_712e")


MIS_712e = buff(+7, +7)


class TOY_804t:
    """Grove Beetle"""

    tags = {GameTag.TAUNT: True}


class TOY_802:
    """Wind-Up Sapling"""

    play = SpendMana(CONTROLLER, -1)


class TOY_803:
    """Jade Display"""

    deathrattle = TOY_803_Deathrattle(CONTROLLER)


class TOY_806:
    """Sky Mother Aviana"""

    play = Shuffle(CONTROLLER, RandomLegendaryMinion()).then(
        Buff(Shuffle.CARD, "TOY_806e")
    ) * 10


class TOY_807:
    """Owlonius"""

    spellpower = lambda self, i: i + 1
    update = Refresh(CONTROLLER, {GameTag.SPELLPOWER_DOUBLE: 1})


# TOY_801: Chia Drake (4费 3/5 龙)
# 微缩。抉择 - 获得+1法术伤害；或抽一张法术牌
class TOY_801:
    """Chia Drake"""

    miniaturize_mini = "TOY_801t"

    choose = ("TOY_801a", "TOY_801b")
    play = ChooseBoth(CONTROLLER) & (Buff(SELF, "TOY_801e"), ForceDraw(RANDOM(FRIENDLY_DECK + SPELL)))


class TOY_801a:
    """Mana Growth"""

    play = Buff(SELF, "TOY_801e")


class TOY_801b:
    """Botanical Studies"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + SPELL))


TOY_801e = buff(spellpower=1)


##
# Spells


class TOY_800:
    """Sparkling Phial"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = TOY_800_SparklingPhial(TARGET)


class MIS_301:
    """Overgrown Beanstalk"""

    play = Summon(CONTROLLER, "MIS_301t").then(
        Draw(CONTROLLER) * Count(FRIENDLY_MINIONS + ID("MIS_301t"))
    )


class TOY_804:
    """Woodland Wonders"""

    play = Summon(CONTROLLER, "TOY_804t") * 2

    class Hand:
        update = Refresh(SELF, {GameTag.COST: _woodland_wonders_cost})


class TOY_805:
    """Ensmallen"""

    play = Buff(FRIENDLY_DECK + MINION, "TOY_805e"), Buff(
        FRIENDLY_DECK + MINION, "TOY_805e2"
    )


TOY_805e = buff(cost=-1)
TOY_805e2 = buff(atk=-1)


class TOY_851:
    """Bottomless Toy Chest"""

    play = TOY_851_DeckDiscover(CONTROLLER)


class TOY_800e1:
    update = Refresh(FRIENDLY_HAND, buff="TOY_800e2")
    events = Play(CONTROLLER).on(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))


@custom_card
class TOY_800e2:
    tags = {
        GameTag.CARDNAME: "Sparkling",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    cost = lambda self, cost: cost - self.source._discount


TOY_803e = buff(+1, +1)
TOY_803e2 = buff(+1, +1)


class TOY_806e:
    cost = SET(1)


##
# Locations


class TOY_850:
    """Magical Dollhouse"""

    spellpower = 0
    activate = Buff(CONTROLLER, "TOY_850e")


@custom_card
class TOY_850e:
    tags = {
        GameTag.CARDNAME: "Magical Harvest",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    spellpower = lambda self, i: i + 1
    events = OWN_TURN_END.on(Destroy(SELF))
