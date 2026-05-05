# Warrior cards from EMERALD_DREAM expansion
from ..utils import *


def _collectible_ids(source, predicate):
    ids = [
        card_id for card_id, data in db.items()
        if (
            data.collectible
            and (not source.game.is_standard or data.is_standard)
            and predicate(data)
        )
    ]
    source.game.random.shuffle(ids)
    return ids


def _dragon_in_hand(player):
    return any(card.type == CardType.MINION and Race.DRAGON in card.races for card in player.hand)


def _card_from_id(player, card_id, source):
    card = player.card(card_id, source=source)
    data_classes = set(db[card_id].classes)
    if len(data_classes) > 1 and set(card.classes) != data_classes:
        for group in MultiClassGroup:
            try:
                group_classes = set(group.card_classes)
            except ValueError:
                continue
            if group_classes == data_classes:
                card.multi_class_group = group
                break
    return card


class EDR_454_Activate(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if (
            not target
            or target.controller != source.controller
            or target.type != CardType.MINION
            or Race.DRAGON not in target.races
        ):
            raise InvalidAction("%r requires a friendly Dragon target." % (source))
        egg = source.controller.card("EDR_454t", source=source)
        egg._edr_454_copy_id = target.id
        return source.game.queue_actions(source, [Summon(source.controller, egg)])


class EDR_454t_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, egg):
        card_id = getattr(egg, "_edr_454_copy_id", None)
        if card_id:
            return source.game.queue_actions(source, [Summon(source.controller, card_id)])


class EDR_455_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source,
            [Summon(self.player, self.player.card(card.id, source=self.source))],
        )
        self.trigger_choice_callback()


class EDR_455_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        seen = set()
        cards = []
        for card in player.graveyard:
            if (
                card.type == CardType.MINION
                and Race.DRAGON in card.races
                and card.id not in seen
            ):
                seen.add(card.id)
                cards.append(player.card(card.id, source=source))
        if cards:
            return source.game.queue_actions(source, [EDR_455_Choice(player, cards[:3])])


class EDR_456_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
        )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [EDR_DarkGift(card), Give(self.player, card)])
        self.trigger_choice_callback()


class EDR_456_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if not _dragon_in_hand(player):
            return
        ids = _collectible_ids(source, lambda data: data.type == CardType.MINION and Race.DRAGON in data.races)
        cards = [_card_from_id(player, card_id, source) for card_id in ids[:3]]
        if cards:
            return source.game.queue_actions(source, [EDR_456_Choice(player, cards)])


class EDR_457_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if _dragon_in_hand(player):
            return source.game.queue_actions(source, [Summon(player, "EDR_457t")])


class EDR_465_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, ysondre):
        player = source.controller
        count = getattr(player, "_edr_465_deaths", 0) + 1
        player._edr_465_deaths = count
        ids = _collectible_ids(source, lambda data: data.type == CardType.MINION and Race.DRAGON in data.races)
        actions = []
        for _ in range(count):
            if ids:
                actions.append(Summon(player, source.game.random.choice(ids)))
        return source.game.queue_actions(source, actions)


class EDR_471_Damaged(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, tortolla):
        return source.game.queue_actions(
            source,
            [GainArmor(source.controller.hero, 1), Buff(tortolla, "EDR_471e")],
        )


class FIR_928_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.hand if card.type == CardType.MINION]
        return source.game.queue_actions(
            source,
            [Buff(card, "FIR_928e") for card in minions]
            + [Buff(player, "FIR_928te", _fir_928_cards=minions)],
        )


class FIR_928te_Tick(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, aura):
        remaining = getattr(aura, "_fir_928_turns_remaining", 3) - 1
        aura._fir_928_turns_remaining = remaining
        if remaining > 0:
            return
        for card in getattr(aura, "_fir_928_cards", []):
            if card.zone == Zone.HAND:
                card.zone = Zone.GRAVEYARD
        aura.remove()
        source.game.manager.targeted_action(self, source, aura)


class FIR_939_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
        )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [EDR_DarkGift(card), Give(self.player, card)])
        self.trigger_choice_callback()


class FIR_939_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        player = source.controller
        ids = _collectible_ids(
            source,
            lambda data: data.type == CardType.MINION and CardClass.WARRIOR in data.classes,
        )
        cards = [_card_from_id(player, card_id, source) for card_id in ids[:3]]
        actions = []
        if target:
            actions.append(Hit(target, 2))
        if cards:
            actions.append(FIR_939_Choice(player, cards))
        return source.game.queue_actions(source, actions)


class FIR_956_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if any(card.type == CardType.MINION and getattr(card, "_dark_gift", False) for card in player.hand):
            return source.game.queue_actions(
                source,
                [Buff(player.hero, "FIR_956e"), GainArmor(player.hero, 6)],
            )


##
# Minions


class EDR_454:
    """Clutch of Corruption"""

    activate = EDR_454_Activate(TARGET)


class EDR_454t:
    """Horrible Egg"""

    tags = {GameTag.DEATHRATTLE: 1}
    deathrattle = EDR_454t_Deathrattle(SELF)


class EDR_456:
    """Darkrider"""

    play = EDR_456_Play(CONTROLLER)


class EDR_457:
    """Brood Keeper"""

    play = EDR_457_Play(CONTROLLER)


class EDR_457t:
    """Nightmare Slicer"""

    pass


class EDR_459:
    """Afflicted Devastator"""

    play = Hit(FRIENDLY_MINIONS - SELF, 3)
    deathrattle = Hit(ENEMY_MINIONS, 3)


class EDR_465:
    """Ysondre"""

    taunt = True
    deathrattle = EDR_465_Deathrattle(SELF)


class EDR_468:
    """Eggbasher"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 1), Buff(TARGET, "EDR_468e1")


class EDR_468e1:
    """Scrambled Attack"""

    tags = {GameTag.ATK: 4}


class EDR_471:
    """Tortolla"""

    taunt = True
    elusive = True
    events = Damage(SELF).on(EDR_471_Damaged(SELF))


class EDR_471e:
    """Tortolla's Rage"""

    tags = {GameTag.ATK: 1}


class FIR_928:
    """Keeper of Flame"""

    play = FIR_928_Play(CONTROLLER)


class FIR_928e:
    """Blazing Strength"""

    tags = {GameTag.ATK: 3, GameTag.HEALTH: 3}


@custom_card
class FIR_928te:
    """Keeper of Flame Countdown"""

    tags = {
        GameTag.CARDNAME: "Keeper of Flame Countdown",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = OWN_TURN_BEGIN.on(FIR_928te_Tick(SELF))


class FIR_956:
    """Dragon Turtle"""

    play = FIR_956_Play(CONTROLLER)


class FIR_956e:
    """Turtle Maw"""

    tags = {GameTag.ATK: 3}
    events = OWN_TURN_END.on(Destroy(SELF))


##
# Spells


class EDR_455:
    """Succumb to Madness"""

    play = EDR_455_Play(CONTROLLER)


class EDR_531:
    """Siphoning Growth"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Destroy(TARGET), Deaths(), GainArmor(FRIENDLY_HERO, 8)


class EDR_531e:
    """Siphoned Growth"""

    pass


class EDR_570:
    """Ominous Nightmares"""

    choose = ("EDR_570A", "EDR_570B")
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_DAMAGED_TARGET: 0,
    }


class EDR_570A:
    """Nightmarish Burst"""

    play = Hit(ALL_MINIONS, 1)


class EDR_570B:
    """Unstable Power"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_DAMAGED_TARGET: 0,
    }
    play = Buff(TARGET, "EDR_570e")


class EDR_570e:
    """Terror of the Night"""

    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class FIR_939:
    """Shadowflame Suffusion"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = FIR_939_Play(TARGET)
