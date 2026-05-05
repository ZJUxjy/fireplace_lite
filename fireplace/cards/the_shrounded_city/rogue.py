from ..utils import *


MASKS = ("DINO_403", "DINO_428")


def _spell_school(card):
    return card.tags.get(GameTag.SPELL_SCHOOL) or getattr(
        getattr(card, "data", None), "spell_school", None
    )


def _kindred(card):
    school = _spell_school(card)
    if not school:
        return False
    return any(
        _spell_school(played) == school
        for played in getattr(card.controller, "cards_played_last_turn", [])
    )


def _collectible_cards(source, predicate):
    cards = []
    for card_id, data in db.items():
        if not data.collectible or (source.game.is_standard and not data.is_standard):
            continue
        if predicate(data):
            card = source.controller.card(card_id, source=source)
            if predicate(card):
                cards.append(card)
    if len(cards) < 3 and source.game.is_standard:
        for card_id, data in db.items():
            if data.collectible and not data.is_standard and predicate(data):
                card = source.controller.card(card_id, source=source)
                if predicate(card):
                    cards.append(card)
    source.game.random.shuffle(cards)
    return cards


class TLC_RogueSetStats(TargetedAction):
    TARGET = ActionArg()
    ATK = IntArg()
    HEALTH = IntArg()
    BUFF = ActionArg()

    def do(self, source, target, atk, health, buff_id):
        return source.game.queue_actions(
            source,
            [
                Buff(
                    target,
                    buff_id,
                    atk=atk - target.atk,
                    max_health=health - target.max_health,
                )
            ],
        )


class DINO_407_Copy(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, target, played):
        return source.game.queue_actions(
            source,
            [
                Morph(target, played.id).then(
                    TLC_RogueSetStats(Morph.CARD, 3, 4, "DINO_407e2")
                )
            ],
        )


class DINO_408_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if not player.hand:
            return
        return source.game.queue_actions(source, [Shuffle(player, player.hand[0])])


class DINO_427_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        card_id = source.game.random.choice(MASKS)
        actions = [Give(player, card_id)]
        if source.controller.combo:
            actions[-1] = actions[-1].then(Buff(Give.CARD, "DINO_407e", cost=-2))
        return source.game.queue_actions(source, actions)


class TLC_513_Progress(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, quest):
        if quest.zone != Zone.SECRET:
            return
        quest.add_progress(quest, 1)
        if quest.progress < 5:
            return
        return source.game.queue_actions(source, [Give(quest.controller, "TLC_513t"), Destroy(quest)])


class TLC_514_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        actions = [Give(self.player, card)]
        actions.extend(Shuffle(self.player, other) for other in self.cards if other is not card)
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class TLC_514_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda card: card.type == CardType.MINION
            and getattr(card, "rarity", None) == Rarity.LEGENDARY,
        )
        return source.game.queue_actions(source, [TLC_514_Choice(player, cards[:3])])


class TLC_515_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        card._tlc_515_remaining = [other.id for other in self.cards if other is not card]
        card._tlc_515_turn = self.source.game.turn
        self.source.game.queue_actions(
            self.source, [Give(self.player, card), Buff(self.player, "TLC_515e")]
        )
        self.trigger_choice_callback()


class TLC_515_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = [player.card(card.id, source=source) for card in player.deck[:3]]
        return source.game.queue_actions(source, [TLC_515_Choice(player, cards)])


class TLC_515_FollowupChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class TLC_515_Followup(TargetedAction):
    CARD = CardArg()

    def do(self, source, card):
        remaining = getattr(card, "_tlc_515_remaining", None)
        if not remaining or getattr(card, "_tlc_515_turn", None) != source.game.turn:
            return
        cards = [card.controller.card(card_id, source=source) for card_id in remaining]
        return source.game.queue_actions(
            source, [Destroy(SELF), TLC_515_FollowupChoice(card.controller, cards)]
        )


class TLC_516_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        weapons = _collectible_cards(
            source,
            lambda card: card.type == CardType.WEAPON
            and getattr(card, "card_class", None) != CardClass.ROGUE,
        )
        if not weapons:
            return
        action = Give(player, weapons[0])
        if source.controller.combo:
            action = action.then(Buff(Give.CARD, "TLC_516e"))
        return source.game.queue_actions(source, [action])


class TLC_517_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        amount = getattr(source.controller, "_tlc_shuffle_count", 0)
        return source.game.queue_actions(source, [Hit(target, amount)])


class TLC_518_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(source, [Shuffle(player, "TLC_513t2") for _ in range(3)])


class TLC_519_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        times = 2 if _kindred(source) else 1
        return source.game.queue_actions(source, [Summon(player, "TLC_519t") for _ in range(times)])


class TLC_521_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        deck = card.controller.deck
        if card in deck:
            deck.remove(card)
            deck.append(card)
        self.trigger_choice_callback()


class TLC_521_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = list(player.opponent.deck[:3])
        return source.game.queue_actions(source, [TLC_521_Choice(player, cards)])


class TLC_522_Fan(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [Hit(player.opponent.field, 1), Draw(player)]
        )


class DINO_407:
    """Milreles"""

    class Hand:
        events = Play(OPPONENT, MINION).after(DINO_407_Copy(SELF, Play.CARD))


DINO_407e2 = buff()


class DINO_408:
    """Prismatic Fang"""

    play = DINO_408_Play(CONTROLLER)
    deathrattle = Draw(CONTROLLER) * 2


class DINO_427:
    """Costume Merchant"""

    play = DINO_427_Play(CONTROLLER)
    combo = DINO_427_Play(CONTROLLER)


DINO_407e = buff()


class TLC_513:
    """The Gravitational Displacer"""

    events = Shuffle(CONTROLLER).after(TLC_513_Progress(SELF))


class TLC_513t:
    """Dusk Overseer"""

    play = Summon(CONTROLLER, "TLC_513t2") * 2


class TLC_513t2:
    """Ancient Ninja Turtle"""

    draw = Summon(CONTROLLER, SELF)
    deathrattle = Shuffle(CONTROLLER, SELF)


class TLC_514:
    """Relic Vendor"""

    play = TLC_514_Discover(CONTROLLER)


class TLC_515:
    """Cultist Map"""

    play = TLC_515_Discover(CONTROLLER)


class TLC_515e:
    events = Play(CONTROLLER).after(TLC_515_Followup(Play.CARD))


class TLC_516:
    """Neferset Weaponsmith"""

    play = TLC_516_Play(CONTROLLER)
    combo = TLC_516_Play(CONTROLLER)


TLC_516e = buff(atk=2)


class TLC_517:
    """Trapdoor Kicker"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_517_Play(TARGET)


class TLC_518:
    """Interrogation"""

    play = TLC_518_Play(CONTROLLER)


class TLC_519:
    """Stalk the Prey"""

    play = TLC_519_Play(CONTROLLER)


class TLC_519t:
    pass


class TLC_520:
    """Canopy Stalker"""

    cost = lambda self, cost: max(0, cost - getattr(self.controller, "_tlc_shuffle_count", 0))


class TLC_521:
    """Lookout"""

    play = TLC_521_Play(CONTROLLER)


class TLC_522:
    """Opu the Unseen"""

    tags = {GameTag.COMBO: True}
    play = TLC_522_Fan(CONTROLLER), Stealth(SELF)
    combo = TLC_522_Fan(CONTROLLER) * 2, Stealth(SELF)
    deathrattle = TLC_522_Fan(CONTROLLER)
