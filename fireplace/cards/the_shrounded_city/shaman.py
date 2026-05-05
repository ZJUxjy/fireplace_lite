from ..utils import *


def _spell_school(card):
    return card.tags.get(GameTag.SPELL_SCHOOL) or getattr(
        getattr(card, "data", None), "spell_school", None
    )


def _card_races(card):
    races = set(getattr(card, "races", []) or [])
    races.update(getattr(getattr(card, "data", None), "races", []) or [])
    return races


def _kindred(card):
    for played in getattr(card.controller, "cards_played_last_turn", []):
        if card.type == CardType.MINION and played.type == CardType.MINION:
            if _card_races(card).intersection(_card_races(played)):
                return True
        school = _spell_school(card)
        if school and _spell_school(played) == school:
            return True
    return False


def _played_minion_races(player):
    races = set()
    for played in getattr(player, "cards_played_this_game", []):
        if played.type == CardType.MINION:
            races.update(_card_races(played))
    return races


def _elemental_damage_bonus(source):
    if Race.ELEMENTAL not in _card_races(source):
        return 0
    return 1 if source.controller.field.contains("TLC_228") else 0


def _collectible_cards(source, predicate):
    cards = []
    for card_id, data in db.items():
        if not data.collectible or (source.game.is_standard and not data.is_standard):
            continue
        card = source.controller.card(card_id, source=source)
        if predicate(card):
            cards.append(card)
    if len(cards) < 3 and source.game.is_standard:
        for card_id, data in db.items():
            if not data.collectible or data.is_standard:
                continue
            card = source.controller.card(card_id, source=source)
            if predicate(card):
                cards.append(card)
    source.game.random.shuffle(cards)
    return cards


class DINO_406_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = [Hit(target, 4)]
        actions.extend(
            Buff(minion, "DINO_406e")
            for minion in source.controller.field
            if Race.ELEMENTAL in _card_races(minion)
        )
        return source.game.queue_actions(source, actions)


class DINO_412_End(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda card: card.type == CardType.MINION and len(_card_races(card)) > 1,
        )
        if not cards:
            return
        return source.game.queue_actions(source, [Give(player, cards[0])])


class DINO_413_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        targets = list(player.opponent.field)
        source.game.random.shuffle(targets)
        actions = []
        amount = 2 + _elemental_damage_bonus(source)
        for target in targets[:2]:
            actions.append(Hit(target, amount))
            if _kindred(source):
                actions.append(Freeze(target))
        return source.game.queue_actions(source, actions)


class TLC_221_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        amount = source.game.queue_actions(source, [Hit(target, 3)])[0][0]
        return source.game.queue_actions(
            source, [Summon(source.controller, "TLC_249") for _ in range(amount)]
        )


class TLC_222_Draw(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        seen = set()
        actions = []
        for card in list(player.deck):
            races = _card_races(card) or {None}
            if races.intersection(seen):
                continue
            seen.update(races)
            actions.append(ForceDraw(card).then(Buff(ForceDraw.TARGET, "TLC_222e")))
            if len(actions) == 2:
                break
        return source.game.queue_actions(source, actions)


class TLC_223_Draw(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = [
            card
            for card in player.deck
            if card.type == CardType.SPELL and _spell_school(card) == 2
        ]
        if not spells:
            return
        action = ForceDraw(spells[0])
        if _kindred(source):
            action = action.then(Buff(ForceDraw.TARGET, "TLC_223e"))
        return source.game.queue_actions(source, [action])


class TLC_224_GainStats(TargetedAction):
    CARD = CardArg()

    def do(self, source, card):
        if card.type != CardType.SPELL or _spell_school(card) != 2:
            return
        amount = card.cost
        return source.game.queue_actions(
            source, [Buff(source, "TLC_224e", atk=amount, max_health=amount)]
        )


class TLC_227_HitLowest(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        enemies = [entity for entity in player.opponent.characters if entity.health > 0]
        if not enemies:
            return
        target = min(enemies, key=lambda entity: entity.health)
        return source.game.queue_actions(source, [Hit(target, 2)])


class TLC_249_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = 2 + _elemental_damage_bonus(source)
        return source.game.queue_actions(
            source, [Hit(RANDOM_ENEMY_CHARACTER, 1) * amount]
        )


class TLC_229_Progress(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, quest, card):
        if quest.zone != Zone.SECRET or card.type != CardType.MINION:
            return
        races = getattr(quest, "_tlc_229_races", set())
        before = len(races)
        races.update(_card_races(card))
        quest._tlc_229_races = races
        added = len(races) - before
        if not added:
            return
        quest.add_progress(card, added)
        if quest.progress < 6:
            return
        return source.game.queue_actions(
            source, [Give(quest.controller, "TLC_229t14"), Destroy(quest)]
        )


class TLC_229t14_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [TLC_229t14_EvolveTwice(source), Buff(player, "TLC_229t14e")]
        )


class TLC_229t14_EvolveTwice(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = []
        current = target
        for _ in range(2):
            card_set = RandomMinion(cost=current.cost + 1).find_cards(source)
            if not card_set:
                break
            card_id = source.game.random.choice(card_set)
            card = current.controller.card(card_id, source=source)
            actions.append(Morph(current, card))
            current = card
        return source.game.queue_actions(source, actions)


class TLC_464_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        card._tlc_464_remaining = [
            other.id for other in self.cards if other is not card
        ]
        card._tlc_464_turn = self.source.game.turn
        self.source.game.queue_actions(
            self.source, [Give(self.player, card), Buff(self.player, "TLC_464e")]
        )
        self.trigger_choice_callback()


class TLC_464_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        used = _played_minion_races(player)
        cards = _collectible_cards(
            source,
            lambda card: card.type == CardType.MINION
            and _card_races(card)
            and not _card_races(card).intersection(used),
        )
        return source.game.queue_actions(source, [TLC_464_Choice(player, cards[:3])])


class TLC_464_FollowupChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class TLC_464_Followup(TargetedAction):
    CARD = CardArg()

    def do(self, source, card):
        remaining = getattr(card, "_tlc_464_remaining", None)
        if not remaining or getattr(card, "_tlc_464_turn", None) != source.game.turn:
            return
        cards = [card.controller.card(card_id, source=source) for card_id in remaining]
        return source.game.queue_actions(
            source, [Destroy(SELF), TLC_464_FollowupChoice(card.controller, cards)]
        )


class TLC_482_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for _ in range(2):
            actions.append(Summon(player, "TLC_249"))
        if _kindred(source):
            actions.append(TLC_482_TriggerAccretions(player))
        return source.game.queue_actions(source, actions)


class TLC_482_TriggerAccretions(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        accretions = [minion for minion in player.field if minion.id == "TLC_249"]
        return source.game.queue_actions(
            source, [Deathrattle(minion) for minion in accretions]
        )


class DINO_406:
    """Erupting Fire"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = DINO_406_Play(TARGET)


DINO_406e = buff(1, 1)


class DINO_412:
    """Ancient Turtle Totem"""

    events = OWN_TURN_END.on(DINO_412_End(CONTROLLER))


class DINO_413:
    """Icespine Sivara"""

    play = DINO_413_Play(CONTROLLER)


class TLC_221:
    """Blazing Inferno"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = TLC_221_Play(TARGET)


class TLC_222:
    """Firebird Flight"""

    play = TLC_222_Draw(CONTROLLER)


TLC_222e = buff(2, 2)


class TLC_223:
    """Volcanic Thrasher"""

    play = TLC_223_Draw(CONTROLLER)


TLC_223e = buff(spellpower=2)


class TLC_224:
    """Mechanical Molten"""

    events = Play(CONTROLLER, SPELL).after(TLC_224_GainStats(Play.CARD))


TLC_224e = buff()


class TLC_225:
    """Emberscarred Murloc"""

    deathrattle = Summon(CONTROLLER, "TLC_249")


class TLC_227:
    """Lava Surge"""

    play = TLC_227_HitLowest(CONTROLLER) * 3


class TLC_228:
    """Brrma Searstone"""

    pass


class TLC_229:
    """Spirit of the Mountain"""

    events = Play(CONTROLLER, MINION).after(TLC_229_Progress(SELF, Play.CARD))


class TLC_229t14:
    """Ashamane, Mountain Guardian"""

    play = TLC_229t14_Play(CONTROLLER)


class TLC_229t14e:
    events = Play(CONTROLLER, MINION).after(TLC_229t14_EvolveTwice(Play.CARD))


class TLC_249:
    """Blazing Accretion"""

    deathrattle = TLC_249_Deathrattle(CONTROLLER)


class TLC_464:
    """Hiking Trail"""

    play = TLC_464_Discover(CONTROLLER)


class TLC_464e:
    events = Play(CONTROLLER).after(TLC_464_Followup(Play.CARD))


class TLC_482:
    """Moltenclaw"""

    play = TLC_482_Play(CONTROLLER)
