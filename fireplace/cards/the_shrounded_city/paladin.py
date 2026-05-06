from ..utils import *


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


class SetStats(TargetedAction):
    TARGET = ActionArg()
    ATK = IntArg()
    HEALTH = IntArg()

    def do(self, source, target, atk, health):
        return source.game.queue_actions(
            source,
            [
                Buff(
                    target,
                    "DINO_424e",
                    atk=atk - target.atk,
                    max_health=health - target.max_health,
                )
            ],
        )


class DINO_405_End(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if not hasattr(source, "_dino_405_turn"):
            return
        if source.game.turn <= getattr(source, "_dino_405_turn", 0) + 1:
            return
        actions = [Buff(minion, "DINO_405e") for minion in player.field]
        actions.append(Destroy(SELF))
        return source.game.queue_actions(source, actions)


class DINO_424_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source,
            [
                Summon(self.player, card).then(
                    SetStats(Summon.CARD, 10, 10)
                )
            ],
        )
        self.trigger_choice_callback()


class DINO_424_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda card: card.type == CardType.MINION
            and getattr(card.data if hasattr(card, "data") else card, "rarity", None)
            == Rarity.LEGENDARY,
        )
        return source.game.queue_actions(source, [DINO_424_Choice(player, cards)])


class TLC_240_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    bonuses = ("rush", "taunt", "divine_shield", "windfury")

    def do(self, source, player):
        actions = []
        for token_id in ("TLC_240t", "TLC_240t2", "TLC_240t3"):
            token = player.card(token_id, source=source)
            actions.append(Summon(player, token))
            bonus = source.game.random.choice(self.bonuses)
            if bonus == "rush":
                actions.append(GiveRush(token))
            elif bonus == "taunt":
                actions.append(Taunt(token))
            elif bonus == "divine_shield":
                actions.append(GiveDivineShield(token))
            elif bonus == "windfury":
                actions.append(GiveWindfury(token))
        return source.game.queue_actions(source, actions)


class DINO_404_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, firegill):
        if not _kindred(firegill):
            return
        minions = [minion for minion in firegill.controller.field if minion is not firegill]
        return source.game.queue_actions(source, [GiveRush(minion) for minion in minions])


class TLC_241_Spellcraft(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = [Buff(target, "TLC_241e"), GiveDivineShield(target)]
        if source.controller.field.contains("TLC_241"):
            actions.append(Give(source.controller, "TLC_241t"))
        return source.game.queue_actions(source, actions)


class TLC_426_Progress(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, quest, card):
        if quest.zone != Zone.SECRET:
            return
        quest.add_progress(card, 1)
        if quest.progress < quest.progress_total:
            return
        quest.progress = 0
        return source.game.queue_actions(source, [Buff(quest.controller, "TLC_426e")])


class TLC_428_Discount(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        murlocs = [card for card in player.hand if Race.MURLOC in card.races]
        if not murlocs:
            return
        actions = [Buff(murlocs[0], "TLC_428e")]
        if _kindred(source):
            actions.append(GiveDivineShield(murlocs[0]))
        return source.game.queue_actions(source, actions)


class TLC_430_Recast(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, grotto):
        holy_spells = [
            card
            for card in grotto.controller.cards_played_this_turn_list
            if card.type == CardType.SPELL and _spell_school(card) == 5
        ]
        if not holy_spells:
            return
        original = grotto.game.random.choice(holy_spells)
        spell = grotto.controller.card(original.id, source=grotto)
        target = grotto if grotto in spell.targets else None
        return source.game.queue_actions(source, [CastSpell(spell, target)])


class TLC_438_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, callow):
        spells = [
            card
            for card in callow.controller.deck
            if card.type == CardType.SPELL and card.cost <= 2
        ]
        if not spells:
            return
        spell = callow.game.random.choice(spells)
        target = callow if callow in spell.targets else None
        return source.game.queue_actions(source, [CastSpell(spell, target)])


class TLC_441_Buff(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        races = set(target.races)
        minions = [
            minion
            for minion in target.controller.field
            if minion is target or races.intersection(minion.races)
        ]
        return source.game.queue_actions(
            source, [Buff(minion, "TLC_441e2") for minion in minions]
        )


class TLC_442_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        remaining = [other.id for other in self.cards if other is not card]
        card._tlc_442_remaining = remaining
        card._tlc_442_turn = self.source.game.turn
        actions = [Give(self.player, card)]
        if remaining:
            actions.append(Buff(self.player, "TLC_442e"))
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class TLC_442_FollowupChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class TLC_442_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(source, lambda card: Race.MURLOC in card.races)
        return source.game.queue_actions(source, [TLC_442_Choice(player, cards)])


class TLC_442_Followup(TargetedAction):
    CARD = CardArg()

    def do(self, source, card):
        remaining = getattr(card, "_tlc_442_remaining", None)
        if not remaining or getattr(card, "_tlc_442_turn", None) != source.game.turn:
            return
        cards = [card.controller.card(card_id, source=source) for card_id in remaining]
        return source.game.queue_actions(
            source, [Destroy(SELF), TLC_442_FollowupChoice(card.controller, cards)]
        )


class TLC_444_Adapt(TargetedAction):
    TARGET = ActionArg()

    bonuses = (
        "TLC_444e_atk",
        "TLC_444e_health",
        "TLC_444e_taunt",
        "TLC_444e_divine",
        "TLC_444e_windfury",
        "TLC_444e_stealth",
    )

    def do(self, source, target):
        buffs = source.game.random.sample(self.bonuses, 3)
        actions = []
        for buff in buffs:
            if buff == "TLC_444e_atk":
                actions.append(Buff(target, "DINO_424e", atk=3))
            elif buff == "TLC_444e_health":
                actions.append(Buff(target, "DINO_424e", max_health=3))
            elif buff == "TLC_444e_taunt":
                actions.append(Taunt(target))
            elif buff == "TLC_444e_divine":
                actions.append(GiveDivineShield(target))
            elif buff == "TLC_444e_windfury":
                actions.append(GiveWindfury(target))
            elif buff == "TLC_444e_stealth":
                actions.append(Stealth(target))
        return source.game.queue_actions(source, actions)


class DINO_404:
    """Firegill"""

    play = DINO_404_Play(SELF)


class DINO_405:
    """Hatching Ceremony"""

    play = Buff(CONTROLLER, "DINO_405e")


class DINO_405e:
    tags = {
        GameTag.ATK: 2,
        GameTag.HEALTH: 2,
    }
    events = OWN_TURN_END.on(DINO_405_End(CONTROLLER))

    def apply(self, target):
        if hasattr(target, "field"):
            self._dino_405_turn = target.game.turn


class DINO_424:
    """Hero's Welcome"""

    play = DINO_424_Discover(CONTROLLER)


DINO_424e = buff()


class TLC_240:
    """Tyrannogill"""

    deathrattle = TLC_240_Deathrattle(CONTROLLER)


class TLC_240t:
    pass


class TLC_240t2:
    pass


class TLC_240t3:
    pass


class TLC_241:
    """Ido of the Threshfleet"""

    play = Give(CONTROLLER, "TLC_241t")


class TLC_241t:
    """Call the Threshfleet!"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_241_Spellcraft(TARGET)


TLC_241e = buff(2, 2)


class TLC_426:
    """Dive the Golakka Depths"""

    progress_total = 6
    events = Summon(CONTROLLER, MURLOC).after(TLC_426_Progress(SELF, Summon.CARD))


class TLC_426e:
    events = Summon(CONTROLLER, MURLOC).after(Buff(Summon.CARD, "TLC_426e2"))


TLC_426e2 = buff(1, 1)


class TLC_428:
    """Hot Spring Glider"""

    play = TLC_428_Discount(CONTROLLER)


TLC_428e = buff(cost=-1)


class TLC_430:
    """Creature of the Sacred Cave"""

    events = OWN_TURN_END.on(TLC_430_Recast(SELF))


class TLC_438:
    """Violet Treasuregill"""

    play = TLC_438_Play(SELF)


class TLC_441:
    """Ready the Fleet"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
    }
    play = TLC_441_Buff(TARGET)


TLC_441e2 = buff(1, 2)


class TLC_442:
    """Submerged Map"""

    play = TLC_442_Discover(CONTROLLER)


class TLC_442e:
    events = Play(CONTROLLER).after(TLC_442_Followup(Play.CARD))


class TLC_444:
    """Story of Galvadon"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_444_Adapt(TARGET)


class TLC_477:
    """Threshrider's Blessing"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
    }
    play = Buff(TARGET, "TLC_477e")


class TLC_477e:
    tags = {
        GameTag.ATK: 4,
        GameTag.HEALTH: 4,
        GameTag.DEATHRATTLE: True,
    }
    deathrattle = Summon(CONTROLLER, RandomMinion(cost=4))
