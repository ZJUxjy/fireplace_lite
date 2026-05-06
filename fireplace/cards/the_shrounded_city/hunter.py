from ..utils import *


def _kindred(card):
    for played in getattr(card.controller, "cards_played_last_turn", []):
        if played.type == CardType.MINION and set(card.races).intersection(played.races):
            return True
    return False


def _collectible_beasts(source, predicate):
    cards = []
    for card_id, data in db.items():
        if (
            data.collectible
            and data.type == CardType.MINION
            and data.race == Race.BEAST
            and (not source.game.is_standard or data.is_standard)
            and predicate(data)
        ):
            cards.append(source.controller.card(card_id, source=source))
    source.game.random.shuffle(cards)
    return cards


class DINO_403_SetStats(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        return source.game.queue_actions(
            source,
            [
                Buff(
                    target,
                    "DINO_403e",
                    atk=8 - target.atk,
                    max_health=8 - target.max_health,
                )
            ],
        )


class DINO_422_SummonBeastAttack(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        beasts = _collectible_beasts(source, lambda data: data.cost == 3)
        if not beasts:
            return
        beast = source.game.random.choice(beasts)
        return source.game.queue_actions(
            source,
            [Summon(player, beast).then(Attack(Summon.CARD, RANDOM_ENEMY_CHARACTER))],
        )


class TLC_822_Discount(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        beasts = [
            card
            for card in player.hand
            if card.type == CardType.MINION and Race.BEAST in card.races
        ]
        if beasts:
            return source.game.queue_actions(
                source, [Buff(source.game.random.choice(beasts), "TLC_822e")]
            )


class TLC_824_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        remaining = [other.id for other in self.cards if other is not card]
        card._tlc_824_remaining = remaining
        actions = [Give(self.player, card)]
        if remaining:
            actions.append(Buff(self.player, "TLC_824e"))
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class TLC_824_FollowupChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class TLC_824_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_beasts(source, lambda data: data.atk % 2 == 1)
        return source.game.queue_actions(source, [TLC_824_Choice(player, cards[:3])])


class TLC_824_Followup(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, player, card):
        remaining = getattr(card, "_tlc_824_remaining", None)
        if not remaining:
            return
        cards = [player.card(card_id, source=source) for card_id in remaining]
        return source.game.queue_actions(
            source, [Destroy(SELF), TLC_824_FollowupChoice(player, cards)]
        )


class TLC_825_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if target and _kindred(source):
            return source.game.queue_actions(source, [Hit(target, source.atk)])


class TLC_830_AddProgress(TargetedAction):
    CARD = CardArg()

    def do(self, source, card):
        if card.type != CardType.MINION or Race.BEAST not in card.races:
            return
        if card.atk not in (1, 3, 5, 7):
            return
        seen = getattr(source, "_tlc_830_seen", set())
        if card.atk in seen:
            return
        seen.add(card.atk)
        source._tlc_830_seen = seen
        return source.game.queue_actions(source, [AddProgress(source, card)])


class TLC_830t_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        actions = [Buff(card, "TLC_830e"), Give(self.player, card)]
        remaining = getattr(self, "remaining_attacks", [])
        if remaining:
            actions.append(TLC_830t_StartChoice(self.player, remaining))
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class TLC_830t_StartChoice(TargetedAction):
    TARGET = ActionArg()
    ATTACKS = ActionArg()

    def do(self, source, player, attacks):
        attack = attacks[0]
        cards = _collectible_beasts(source, lambda data: data.atk == attack)
        choice = TLC_830t_Choice(player, cards[:3])
        choice.remaining_attacks = attacks[1:]
        return source.game.queue_actions(source, [choice])


class TLC_836_DoubleMinion(TargetedAction):
    CARD = CardArg()

    def do(self, source, card):
        if card.type == CardType.MINION and card.cost == 1:
            return source.game.queue_actions(
                source,
                [Buff(card, "TLC_836e", atk=card.atk, max_health=card.max_health)],
            )


class TLC_836_CastAgain(TargetedAction):
    CARD = CardArg()

    def do(self, source, card):
        if card.type == CardType.SPELL and card.cost == 1:
            return source.game.queue_actions(source, [CastSpell(card, card.target)])


class DINO_403:
    """Devilsaur Mask"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = DINO_403_SetStats(TARGET)


DINO_403e = buff(charge=True)


class DINO_422:
    """Ankylodon"""

    deathrattle = DINO_422_SummonBeastAttack(CONTROLLER) * 2


class DINO_434:
    """Raptor-Nest Nurse"""

    play = Give(CONTROLLER, RandomMinion(cost=1))
    deathrattle = Give(CONTROLLER, RandomSpell(cost=1))


class TLC_366:
    """Pterrorwing Ravager"""

    tags = {GameTag.RUSH: True}

    def cost(self, cost):
        if _kindred(self):
            return cost - 2
        return cost


class TLC_822:
    """Dinositter"""

    events = OWN_TURN_END.on(TLC_822_Discount(CONTROLLER))


@custom_card
class TLC_822e:
    tags = {
        GameTag.CARDNAME: "Dino Care",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


class TLC_823:
    """Cower in Fear"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 3), Buff(CONTROLLER, "TLC_823e1")


class TLC_823e1:
    update = Refresh(FRIENDLY_HAND + BEAST, {GameTag.COST: -2})
    events = Play(CONTROLLER, BEAST).after(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))


class TLC_824:
    """Odd Map"""

    play = TLC_824_Play(CONTROLLER)


class TLC_824e:
    events = Play(CONTROLLER).after(TLC_824_Followup(CONTROLLER, Play.CARD))


class TLC_825:
    """Ravasaur Matriarch"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_825_Play(TARGET)


class TLC_826:
    """Story of Carnassa"""

    play = Shuffle(CONTROLLER, "UNG_920t2") * 10


class TLC_827:
    """Grazing Stegodon"""

    events = OWN_TURN_END.on(Buff(SELF, "TLC_827e"))

    class Hand:
        events = OWN_TURN_END.on(Buff(SELF, "TLC_827e"))

    class Deck:
        events = OWN_TURN_END.on(Buff(SELF, "TLC_827e"))


TLC_827e = buff(atk=1)


class TLC_828:
    """Supreme Dinomancy"""

    play = Buff(FRIENDLY + (IN_HAND | IN_DECK | IN_PLAY) + BEAST, "TLC_828e")


TLC_828e = buff(atk=2, health=2)


class TLC_830:
    """The Food Chain"""

    quest = Play(CONTROLLER).after(TLC_830_AddProgress(Play.CARD))
    reward = Give(CONTROLLER, "TLC_830t")


@custom_card
class TLC_830e:
    tags = {
        GameTag.CARDNAME: "Shokk's Call",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    def cost(self, cost):
        return 2


class TLC_830t:
    """Shokk, Jungle Tyrant"""

    tags = {GameTag.RUSH: True}
    play = TLC_830t_StartChoice(CONTROLLER, [8, 6, 4])


class TLC_836:
    """Niri of the Crater"""

    events = Play(CONTROLLER, MINION).after(
        TLC_836_DoubleMinion(Play.CARD)
    ), Play(CONTROLLER, SPELL).after(TLC_836_CastAgain(Play.CARD))


TLC_836e = buff()
