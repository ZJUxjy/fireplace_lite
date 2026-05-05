from ..utils import *


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


def _played_school_this_turn(player, school):
    return any(
        played.type == CardType.SPELL and _spell_school(played) == school
        for played in player.cards_played_this_turn_list
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


class TLC_PriestSetStats(TargetedAction):
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


class DINO_426_Choice(Choice):
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
                    TLC_PriestSetStats(Summon.CARD, 2, 3, "DINO_426e")
                )
            ],
        )
        self.trigger_choice_callback()


class DINO_426_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source, lambda card: card.type == CardType.MINION and card.cost == 3
        )
        return source.game.queue_actions(source, [DINO_426_Choice(player, cards[:3])])


class DINO_428_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = [
            TLC_PriestSetStats(target, 8, 10, "DINO_428e"),
            GiveLifesteal(target),
        ]
        enemies = list(target.controller.opponent.field)
        if enemies:
            actions.append(Attack(source.game.random.choice(enemies), target))
        return source.game.queue_actions(source, actions)


class DINO_431_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda card: card.type == CardType.MINION
            and card.cost >= 5
            and bool(getattr(card, "taunt", False)),
        )
        if not cards:
            return
        return source.game.queue_actions(source, [Summon(player, cards[0])])


class TLC_811_SetHealth(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, archaios, attacker):
        amount = archaios.health
        return source.game.queue_actions(
            source,
            [
                Buff(
                    attacker,
                    "DINO_426e",
                    max_health=amount - attacker.max_health,
                ),
                SetCurrentHealth(attacker, amount),
            ],
        )


class TLC_815_Summon(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        times = 2 if _kindred(source) else 1
        actions = [
            Summon(player, RandomMinion(cost=4)).then(Buff(Summon.CARD, "TLC_815e"))
            for _ in range(times)
        ]
        return source.game.queue_actions(source, actions)


class TLC_817_Progress(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, quest, card):
        if quest.zone != Zone.SECRET:
            return
        school = _spell_school(card)
        if school not in (5, 6):
            return
        attr = "_tlc_817_holy" if school == 5 else "_tlc_817_shadow"
        if getattr(quest, attr + "_done", False):
            return
        setattr(quest, attr, getattr(quest, attr, 0) + 1)
        if getattr(quest, attr) < 4:
            return
        setattr(quest, attr + "_done", True)
        reward = "TLC_817t3" if school == 5 else "TLC_817t4"
        other = "TLC_817t4" if reward == "TLC_817t3" else "TLC_817t3"
        other_piece = next((card for card in quest.controller.hand if card.id == other), None)
        if other_piece:
            other_piece.zone = Zone.REMOVEDFROMGAME
            return source.game.queue_actions(source, [Give(quest.controller, "TLC_817t5")])
        return source.game.queue_actions(source, [Give(quest.controller, reward)])


class TLC_818_Resurrect(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for cost in (1, 2, 3):
            dead = [
                card
                for card in player.graveyard
                if card.type == CardType.MINION and card.cost == cost
            ]
            if not dead:
                continue
            copy = player.card(source.game.random.choice(dead).id, source=source)
            actions.append(Summon(player, copy).then(GiveReborn(Summon.CARD)))
        return source.game.queue_actions(source, actions)


class TLC_813_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if target.controller is source.controller:
            return source.game.queue_actions(source, [Buff(target, "TLC_813e")])
        return source.game.queue_actions(source, [Buff(target, "TLC_813e2")])


class TLC_821_AttackHealedEnemy(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if target.controller is source.controller:
            return
        return source.game.queue_actions(source, [Attack(source, target)])


class TLC_835_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, hero):
        return source.game.queue_actions(
            source,
            [
                Buff(hero, "TLC_835e", max_health=40 - hero.max_health),
                SetCurrentHealth(hero, 40),
            ],
        )


class DINO_426:
    """Life Ritual"""

    play = DINO_426_Discover(CONTROLLER)


DINO_426e = buff()


class DINO_428:
    """Eel-Tusk Mask"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = DINO_428_Play(TARGET)


DINO_428e = buff()


class DINO_431:
    """Thundering Abomination"""

    deathrattle = DINO_431_Deathrattle(CONTROLLER)


class TLC_811:
    """Archaios"""

    events = Attack(FRIENDLY_MINIONS - SELF).after(
        TLC_811_SetHealth(SELF, Attack.ATTACKER)
    )


class TLC_814:
    """Twilight Mender"""

    deathrattle = (
        Give(CONTROLLER, RandomSpell(card_class=CardClass.PRIEST, spell_school=5)),
        Give(CONTROLLER, RandomSpell(card_class=CardClass.PRIEST, spell_school=6)),
    )


class TLC_815:
    """Gravedawn Voidbulb"""

    play = TLC_815_Summon(CONTROLLER)


TLC_815e = buff(taunt=True)


class TLC_816:
    """Gravedawn Sunbloom"""

    play = Draw(CONTROLLER) * 2
    cost = lambda self, cost: cost - 2 if _kindred(self) else cost


class TLC_817:
    """Seek Guidance"""

    events = Play(CONTROLLER, SPELL).after(TLC_817_Progress(SELF, Play.CARD))


class TLC_817t3:
    """Solitous, Lifebreath"""

    play = Summon(CONTROLLER, ExactCopy(SELF))


class TLC_817t4:
    """Solitous, Death's Touch"""

    deathrattle = Hit(RANDOM_ENEMY_CHARACTER, 5)


class TLC_817t5:
    """Solitous, Cycle Reborn"""

    play = Summon(CONTROLLER, ExactCopy(SELF))
    deathrattle = Hit(RANDOM_ENEMY_CHARACTER, 5)


class TLC_818:
    """Reincarnation"""

    play = TLC_818_Resurrect(CONTROLLER)


class TLC_819:
    """Gladesong Siren"""

    cost = (
        lambda self, cost: 1
        if _played_school_this_turn(self.controller, 5)
        and _played_school_this_turn(self.controller, 6)
        else cost
    )


class TLC_820:
    """Woodland Ecologist"""

    deathrattle = Give(CONTROLLER, "TLC_813")


class TLC_813:
    """Pure Vine"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_813_Play(TARGET)


TLC_813e = buff(health=2)
TLC_813e2 = buff(health=-2)


class TLC_821:
    """Wilted Shadow"""

    events = Heal(ENEMY_CHARACTERS).on(TLC_821_AttackHealedEnemy(Heal.TARGET))


class TLC_835:
    """Story of Amara"""

    play = TLC_835_Play(FRIENDLY_HERO)


TLC_835e = buff()
