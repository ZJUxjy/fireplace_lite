from hearthstone.enums import SpellSchool

from ..utils import *


FELBEASTS = ["TLC_446t2", "TLC_446t3", "TLC_446t4"]


def _spell_school(card):
    return card.tags.get(GameTag.SPELL_SCHOOL) or getattr(
        getattr(card, "data", None), "spell_school", None
    )


def _card_races(card):
    races = set(getattr(card, "races", []) or [])
    races.update(getattr(getattr(card, "data", None), "races", []) or [])
    return races


TEMPORARY_CARD = FuncSelector(
    lambda entities, source: [
        entity for entity in entities if getattr(entity, "_tlc_temporary", False)
    ]
)


def _kindred(card):
    school = _spell_school(card)
    for played in getattr(card.controller, "cards_played_last_turn", []):
        if card.type == CardType.MINION and played.type == CardType.MINION:
            if _card_races(card).intersection(_card_races(played)):
                return True
        if school and _spell_school(played) == school:
            return True
    return False


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


def _ensure_temporary_cleanup(player, source):
    if not any(buff.id == "TLC_WARLOCK_TEMPORARY" for buff in player.buffs):
        source.game.queue_actions(source, [Buff(player, "TLC_WARLOCK_TEMPORARY")])


class TLC_WarlockMakeTemporary(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        card._tlc_temporary = True
        _ensure_temporary_cleanup(card.controller, source)


class TLC_WarlockGiveTemporary(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, player, card):
        if isinstance(card, list):
            card = card[0]
        card._tlc_temporary = True
        actions = [Give(player, card)]
        if not any(buff.id == "TLC_WARLOCK_TEMPORARY" for buff in player.buffs):
            actions.append(Buff(player, "TLC_WARLOCK_TEMPORARY"))
        return source.game.queue_actions(source, actions)


class TLC_WarlockTemporaryCleanup(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        temporary = [
            card for card in list(player.hand) if getattr(card, "_tlc_temporary", False)
        ]
        return source.game.queue_actions(source, [Discard(card) for card in temporary])


class DINO_131_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        beasts = [card for card in player.deck if Race.BEAST in _card_races(card)]
        if not beasts:
            return
        beast = source.game.random.choice(beasts)
        return source.game.queue_actions(
            source, [Summon(player, beast).then(GiveLifesteal(Summon.CARD))]
        )


class DINO_402_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        slots = target.controller.minion_slots
        source.game.queue_actions(
            source,
            [
                Buff(
                    target,
                    "DINO_402e",
                    atk=1 - target.atk,
                    max_health=1 - target.max_health,
                )
            ],
        )
        actions = [
            Summon(target.controller, ExactCopy(SELF).copy(source, target)).then(
                TLC_WarlockSetStats(Summon.CARD, 1, 1)
            )
            for _ in range(slots)
        ]
        return source.game.queue_actions(source, actions)


class TLC_WarlockSetStats(TargetedAction):
    TARGET = ActionArg()
    ATK = IntArg()
    HEALTH = IntArg()

    def do(self, source, target, atk, health):
        return source.game.queue_actions(
            source,
            [
                Buff(
                    target,
                    "DINO_402e",
                    atk=atk - target.atk,
                    max_health=health - target.max_health,
                )
            ],
        )


class TLC_446_Progress(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, quest, card):
        if quest.zone != Zone.SECRET or not getattr(card, "_tlc_temporary", False):
            return
        quest.add_progress(card, 1)
        if quest.progress < quest.progress_total:
            return
        return source.game.queue_actions(
            source, [Give(quest.controller, "TLC_446t"), Destroy(quest)]
        )


class TLC_446t1_Activate(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        felbeasts = [
            self.source.game.random.choice(FELBEASTS),
            self.source.game.random.choice(FELBEASTS),
        ]
        self.source.game.queue_actions(
            self.source,
            [Discard(card)]
            + [Summon(self.player, felbeast) for felbeast in felbeasts],
        )
        self.trigger_choice_callback()


class TLC_447_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = [Destroy(target)]
        if _kindred(source):
            actions.append(Hit(ALL_MINIONS, 2))
        return source.game.queue_actions(source, actions)


class TLC_449_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source, lambda card: card.type == CardType.MINION and card.cost == 1
        )
        return source.game.queue_actions(
            source, [TLC_WarlockTemporaryChoice(player, cards[:3])]
        )


class TLC_WarlockTemporaryChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source, [TLC_WarlockGiveTemporary(self.player, card)]
        )
        self.trigger_choice_callback()


class TLC_451_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = list(player.deck)
        source.game.random.shuffle(cards)
        if cards:
            return source.game.queue_actions(
                source, [TLC_WarlockTemporaryChoice(player, cards[:3])]
            )


class TLC_463_Discard(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        target_player = player.opponent if _kindred(source) else player
        if not target_player.hand:
            return
        return source.game.queue_actions(
            source, [Discard(source.game.random.choice(target_player.hand))]
        )


class TLC_466_End(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, enchantment):
        player = enchantment.controller
        actions = []
        if player.hand:
            actions.append(Discard(player.hand[0]))
        while player.minion_slots > len([a for a in actions if isinstance(a, Summon)]):
            actions.append(Summon(player, "TLC_466t"))
        enchantment._tlc_466_turns = getattr(enchantment, "_tlc_466_turns", 0) + 1
        if enchantment._tlc_466_turns >= 3:
            actions.append(Destroy(SELF))
        return source.game.queue_actions(source, actions)


class TLC_467_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = _collectible_cards(
            source,
            lambda card: card.type == CardType.SPELL
            and _spell_school(card) == SpellSchool.FEL,
        )
        actions = []
        for spell in spells[:2]:
            spell._costs_health = True
            actions.append(Give(player, spell))
        return source.game.queue_actions(source, actions)


class TLC_469_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source, lambda card: card.type == CardType.MINION and card.cost == 2
        )
        return source.game.queue_actions(
            source, [TLC_WarlockGiveTemporary(player, card) for card in cards[:2]]
        )


class TLC_479_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [Summon(player, source.game.random.choice(FELBEASTS))]
        )


class DINO_131:
    """Possessed Animancer"""

    deathrattle = DINO_131_Deathrattle(CONTROLLER)


class DINO_132:
    """Asphyxiodon"""

    events = OWN_TURN_END.on(Hit(RANDOM_ENEMY_MINION, 5))


class DINO_402:
    """Bat Mask"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = DINO_402_Play(TARGET)


DINO_402e = buff()


class TLC_446:
    """Escape the Underfel"""

    events = Play(CONTROLLER).after(TLC_446_Progress(SELF, Play.CARD))


class TLC_446t:
    """Underfel Rift"""

    play = Summon(CONTROLLER, "TLC_446t1")


class TLC_446t1:
    """Underfel Rift"""

    activate = TLC_446t1_Activate(CONTROLLER, FRIENDLY_HAND)


class TLC_446t2:
    """Felscreamer"""

    pass


class TLC_446t3:
    """Felraptor"""

    pass


class TLC_446t4:
    """Felhorn"""

    pass


class TLC_447:
    """Caustic Fumes"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_447_Play(TARGET)


class TLC_449:
    """Bloodpetal Biome"""

    activate = TLC_449_Discover(CONTROLLER)


class TLC_450:
    """Spelunker"""

    play = Buff(CONTROLLER, "TLC_450e")


class TLC_450e:
    update = Refresh(FRIENDLY_HAND + TEMPORARY_CARD, {GameTag.COST: -2})
    events = Play(CONTROLLER, TEMPORARY_CARD).after(Destroy(SELF))


class TLC_451:
    """Cursed Catacombs"""

    play = TLC_451_Discover(CONTROLLER)


class TLC_463:
    """Razidir"""

    play = TLC_463_Discard(CONTROLLER)


class TLC_466:
    """Story of Lakkari"""

    play = Buff(CONTROLLER, "TLC_466e")


@custom_card
class TLC_466e:
    tags = {
        GameTag.CARDNAME: "Story of Lakkari",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    events = OWN_TURN_END.on(TLC_466_End(SELF))


@custom_card
class TLC_466t:
    tags = {
        GameTag.CARDNAME: "Lakkari Imp",
        GameTag.CARDTYPE: CardType.MINION,
        GameTag.COST: 1,
        GameTag.ATK: 3,
        GameTag.HEALTH: 2,
        GameTag.CARDRACE: Race.DEMON,
    }


class TLC_467:
    """Whispering Stone"""

    deathrattle = TLC_467_Deathrattle(CONTROLLER)


class TLC_469:
    """Tunnel Terror"""

    deathrattle = TLC_469_Deathrattle(CONTROLLER)


class TLC_479:
    """Deathrot Maw"""

    deathrattle = TLC_479_Deathrattle(CONTROLLER)


@custom_card
class TLC_WARLOCK_TEMPORARY:
    tags = {
        GameTag.CARDNAME: "Temporary",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    events = OWN_TURN_END.on(TLC_WarlockTemporaryCleanup(CONTROLLER))
