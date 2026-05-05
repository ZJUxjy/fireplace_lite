from ..utils import *


FROST_RUNE_CARDS = [
    "TOY_821",
    "TOY_825",
    "TOY_825t",
    "TOY_825t2",
]


def _spell_school(card):
    return card.tags.get(GameTag.SPELL_SCHOOL) or getattr(
        getattr(card, "data", None), "spell_school", None
    )


def _kindred(card):
    for played in getattr(card.controller, "cards_played_last_turn", []):
        if card.type == CardType.MINION and played.type == CardType.MINION:
            if set(card.races).intersection(played.races):
                return True
        spell_school = _spell_school(card)
        if spell_school and _spell_school(played) == spell_school:
            return True
    return False


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
    return cards[:3]


def _spend_corpses(source, player, amount):
    if getattr(player, "corpses", 0) < amount:
        return None
    player.corpses -= amount
    return [
        AddProgress(quest, source, amount)
        for quest in list(player.secrets.filter(id="TLC_433"))
    ]


class DINO_415_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source,
            [Summon(self.player, card).then(Deathrattle(Summon.CARD))],
        )
        self.trigger_choice_callback()


class DINO_415_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda data: data.type == CardType.MINION
            and data.cost >= 5
            and data.tags.get(GameTag.DEATHRATTLE),
        )
        return source.game.queue_actions(source, [DINO_415_Choice(player, cards)])


class DINO_416_Reborn(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, direhorn):
        if direhorn.zone != Zone.PLAY:
            return
        actions = _spend_corpses(source, direhorn.controller, 3)
        if actions is None:
            return
        actions.append(GiveReborn(direhorn))
        return source.game.queue_actions(source, actions)


class TLC_432_Draw(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        candidates = [
            card
            for card in player.deck
            if card.type == CardType.MINION
            and card.cost <= 3
            and card.tags.get(GameTag.DEATHRATTLE)
        ]
        if not candidates:
            return
        card = candidates[0]
        actions = [ForceDraw(card)]
        if _kindred(source):
            actions.append(Buff(card, "TLC_432e"))
        return source.game.queue_actions(source, actions)


class TLC_434_Discover(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class TLC_434_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(source, lambda data: Race.UNDEAD in data.races)
        corpse_progress = _spend_corpses(source, player, 5)
        if corpse_progress is not None:
            return source.game.queue_actions(
                source,
                corpse_progress + [Give(player, card) for card in cards],
            )
        return source.game.queue_actions(source, [TLC_434_Discover(player, cards)])


class TLC_435_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        remaining = [other.id for other in self.cards if other is not card]
        card._tlc_435_remaining = remaining
        actions = [Give(self.player, card)]
        if remaining:
            actions.append(Buff(self.player, "TLC_435e"))
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class TLC_435_FollowupChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class TLC_435_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = [player.card(card_id, source=source) for card_id in FROST_RUNE_CARDS]
        source.game.random.shuffle(cards)
        return source.game.queue_actions(source, [TLC_435_Choice(player, cards[:3])])


class TLC_435_Followup(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, player, card):
        remaining = getattr(card, "_tlc_435_remaining", None)
        if not remaining:
            return
        owner = source.controller
        cards = [owner.card(card_id, source=source) for card_id in remaining]
        source.game.queue_actions(
            source,
            [Destroy(SELF), TLC_435_FollowupChoice(owner, cards)],
        )


class TLC_436_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = _spend_corpses(source, player, source.data.cost)
        if actions:
            return source.game.queue_actions(source, actions)


class TLC_440_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = [Hit(target, 4), Draw(source.controller)]
        if _kindred(source):
            actions.append(Draw(source.controller))
        return source.game.queue_actions(source, actions)


class TLC_810_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [
            card
            for card in player.deck
            if card.type == CardType.MINION and card.tags.get(GameTag.DEATHRATTLE)
        ][:2]
        if len(minions) < 2:
            return
        first, second = minions
        return source.game.queue_actions(
            source,
            [
                Summon(player, first),
                Summon(player, second),
                Attack(first, second),
            ],
        )


class DINO_415:
    """Story of Umbra"""

    play = DINO_415_Discover(CONTROLLER)


class DINO_416:
    """Hollow Direhorn"""

    tags = {GameTag.RUSH: True}
    events = Death(FRIENDLY + MINION - SELF).on(DINO_416_Reborn(SELF))


class DINO_417:
    """Rite of Rest"""

    play = Buff(FRIENDLY_MINIONS, "DINO_417e")


class DINO_417e:
    events = OWN_TURN_END.on(Destroy(OWNER))
    tags = {
        GameTag.ATK: 1,
        GameTag.RUSH: True,
    }


class TLC_401:
    """Chillfallen Baronsaurus"""

    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 6) * 3


class TLC_432:
    """Dread Raptor"""

    play = TLC_432_Draw(CONTROLLER)


@custom_card
class TLC_432e:
    tags = {
        GameTag.CARDNAME: "Dread Raptor Discount",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -10,
    }


class TLC_433:
    """Reanimate the Terror"""

    reward = Give(CONTROLLER, "TLC_433t")


class TLC_433t:
    """Terrax, the Bone Terror"""

    deathrattle = Summon(CONTROLLER, "TLC_433t2")


class TLC_433t2:
    """Tomb of Terror"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    activate = Hit(TARGET, 4)
    deathrattle = Summon(CONTROLLER, "TLC_433t")


class TLC_434:
    """Necrotic Archaeology"""

    play = TLC_434_Play(CONTROLLER)


class TLC_435:
    """Burndown Map"""

    play = TLC_435_Play(CONTROLLER)


class TLC_435e:
    events = Play(CONTROLLER).after(TLC_435_Followup(SELF, Play.CARD))


class TLC_436:
    """Reanimated Pterrordax"""

    tags = {
        GameTag.RUSH: True,
        GameTag.LIFESTEAL: True,
    }
    play = TLC_436_Play(CONTROLLER)

    def cost(self, cost):
        if getattr(self.controller, "corpses", 0) >= self.data.cost:
            return -cost
        return 0


class TLC_439:
    """Tar Tide"""

    play = Hit(ENEMY_MINIONS, 2), Buff(ENEMY_HAND + MINION, "TLC_439e2")


TLC_439e2 = buff(cost=2)


class TLC_440:
    """Cryo Sleep"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    play = TLC_440_Play(TARGET)


class TLC_443:
    """Reluctant Wrangler"""

    tags = {GameTag.REBORN: True}
    deathrattle = Summon(CONTROLLER, "TLC_443t")


class TLC_443t:
    """Reanimated Skeletal Dino"""

    tags = {GameTag.TAUNT: True}
    extra_races = (Race.BEAST,)


class TLC_810:
    """High Cultist Herenn"""

    play = TLC_810_Play(CONTROLLER)
