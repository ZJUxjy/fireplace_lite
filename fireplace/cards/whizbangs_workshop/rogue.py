from ..utils import *


_JUNK = ("GAME_005", "WW_001t", "EX1_014t", "CS2_082")


class _CostMod:
    def __init__(self, func):
        self.func = func

    def evaluate(self, source):
        return self.func(source)


def _other_class_cards(source, card_type=None):
    ret = []
    for card_id, data in db.items():
        if not data.collectible:
            continue
        if source.game.is_standard and not data.is_standard:
            continue
        if CardClass.ROGUE in data.classes or CardClass.NEUTRAL in data.classes:
            continue
        if card_type is not None and data.type != card_type:
            continue
        ret.append(card_id)
    return ret


class MIS_708_TwistedPack(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        pool = _other_class_cards(source)
        cards = [
            player.card(source.game.random.choice(pool), source=source)
            for _ in range(5)
        ]
        return source.game.queue_actions(
            source, [Give(player, Buff(card, "MIS_708e")) for card in cards]
        )


class TOY_510_DigForTreasure(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.deck if card.type == CardType.MINION]
        if not minions:
            return
        card = source.game.random.choice(minions)
        actions = [ForceDraw(card)]
        if Race.PIRATE in card.races:
            actions.append(Give(player, "GAME_005"))
        return source.game.queue_actions(source, actions)


class TOY_511_Goldbeard(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, pirate):
        if pirate is source or getattr(pirate, "_shoplifter_goldbeard_copy", False):
            return
        copy = ExactCopy(TARGET).copy(source, pirate)
        copy._shoplifter_goldbeard_copy = True
        return source.game.queue_actions(
            source,
            [
                Summon(source.controller, copy).then(
                    Attack(Summon.CARD, RANDOM_ENEMY_CHARACTER),
                    Destroy(Summon.CARD),
                )
            ],
        )


class TOY_514_ThistleTeaSetChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source,
            [Give(self.player, card), Give(self.player, card.id)],
        )
        self.trigger_choice_callback()


class TOY_514_ThistleTeaSet(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        pool = _other_class_cards(source, card_type=CardType.SPELL)
        card_ids = source.game.random.sample(pool, min(3, len(pool)))
        cards = [player.card(card_id, source=source) for card_id in card_ids]
        return source.game.queue_actions(
            source, [TOY_514_ThistleTeaSetChoice(player, cards)]
        )


class TOY_515_SonyaCopy(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        copy = ExactCopy(TARGET).copy(source, card)
        return source.game.queue_actions(
            source,
            [Give(source.controller, Buff(copy, "TOY_515e", cost=-copy.cost))],
        )


##
# Minions


class MIS_706:
    """Dust Bunny"""

    play = Give(CONTROLLER, RandomID(*_JUNK))
    deathrattle = Give(CONTROLLER, RandomID(*_JUNK))


class TOY_505:
    """Toy Boat"""

    events = Summon(CONTROLLER, PIRATE).after(Draw(CONTROLLER))


class TOY_511:
    """Shoplifter Goldbeard"""

    events = Summon(CONTROLLER, PIRATE).after(TOY_511_Goldbeard(Summon.CARD))


class TOY_515:
    """Sonya Waterdancer"""

    events = Play(CONTROLLER, MINION + (COST == 1)).after(
        TOY_515_SonyaCopy(Play.CARD)
    )


class TOY_516:
    """Bargain Bin Buccaneer"""

    tags = {GameTag.RUSH: True}
    combo = Summon(CONTROLLER, ExactCopy(SELF))


class TOY_521:
    """Sandbox Scoundrel"""

    miniaturize_mini = "TOY_521t1"
    play = Buff(CONTROLLER, "TOY_521e")


class TOY_521t1:
    """Sandbox Scoundrel"""

    play = TOY_521.play


class TOY_522t:
    """Waterslider"""


##
# Weapons


class TOY_522:
    """Watercannon"""

    events = Attack(FRIENDLY_HERO).after(
        Summon(CONTROLLER, "TOY_522t").then(
            Attack(Summon.CARD, RANDOM_ENEMY_CHARACTER)
        )
    )


##
# Locations


class TOY_512:
    """The Crystal Cove"""

    activate = Buff(CONTROLLER, "TOY_512e1")


##
# Spells


class MIS_708:
    """Twisted Pack"""

    play = MIS_708_TwistedPack(CONTROLLER)


class MIS_903:
    """Dubious Purchase"""

    play = Draw(CONTROLLER) * 3
    combo = Draw(CONTROLLER) * 3, Destroy(RANDOM_ENEMY_MINION)


class TOY_510:
    """Dig for Treasure"""

    play = TOY_510_DigForTreasure(CONTROLLER)


class TOY_514:
    """Thistle Tea Set"""

    play = TOY_514_ThistleTeaSet(CONTROLLER)


class TOY_519:
    """Everything Must Go!"""

    cost_mod = _CostMod(lambda card: -card.controller.cards_drawn_this_turn)
    play = Summon(CONTROLLER, RandomMinion(cost=4)) * 2


##
# Buffs


@custom_card
class MIS_708e:
    tags = {
        GameTag.CARDNAME: "Twisted",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    class Hand:
        events = OWN_TURN_END.on(Discard(OWNER))

    events = REMOVED_IN_PLAY


class TOY_512e1:
    events = (
        Summon(CONTROLLER, MINION).on(
            Buff(Summon.CARD, "TOY_512e2"), Destroy(SELF)
        ),
        OWN_TURN_END.on(Destroy(SELF)),
    )


@custom_card
class TOY_512e2:
    tags = {
        GameTag.CARDNAME: "Treasures Below",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    atk = SET(4)
    max_health = SET(4)


@custom_card
class TOY_515e:
    tags = {
        GameTag.CARDNAME: "Waterdance",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


class TOY_521e:
    update = Refresh(FRIENDLY_HAND, {GameTag.COST: -2})
    events = Play(CONTROLLER).on(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))
