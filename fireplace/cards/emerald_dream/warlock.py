# Warlock cards from EMERALD_DREAM expansion
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


class EDR_482e_Tick(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, aura):
        player = aura.owner
        source.game.queue_actions(source, [Hit(player.hero, 3)])
        remaining = getattr(aura, "_edr_482_turns_remaining", 2) - 1
        aura._edr_482_turns_remaining = remaining
        if remaining <= 0:
            aura.remove()
            source.game.manager.targeted_action(self, source, aura)


class EDR_483_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        player.max_mana = max(player.max_mana - 1, 0)
        return source.game.queue_actions(source, [Buff(player, "EDR_483e")])


class EDR_483e_Tick(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, aura):
        remaining = getattr(aura, "_edr_483_turns_remaining", 2) - 1
        aura._edr_483_turns_remaining = remaining
        if remaining > 0:
            return
        player = aura.owner
        aura.remove()
        source.game.manager.targeted_action(self, source, aura)
        return source.game.queue_actions(source, [GainMana(player, 2)])


class EDR_485_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, dryad):
        candidates = [
            card for card in source.controller.deck
            if card.type == CardType.MINION and card.cost >= 7
        ]
        if candidates:
            return source.game.queue_actions(
                source, [ForceDraw(source.game.random.choice(candidates))]
            )


class EDR_488_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
        )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [EDR_DarkGift(card), Give(self.player, card)])
        self.trigger_choice_callback()


class EDR_488_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        ids = _collectible_ids(
            source,
            lambda data: data.type == CardType.MINION
            and data.tags.get(GameTag.DEATHRATTLE),
        )
        cards = [player.card(card_id, source=source) for card_id in ids[:3]]
        if cards:
            return source.game.queue_actions(source, [EDR_488_Choice(player, cards)])


class EDR_489_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        player._next_card_costs_opponent_health = True
        player._next_card_costs_opponent_health_max = 10
        source.game.manager.targeted_action(self, source, player)


class EDR_491_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, archdruid):
        copied = []
        for card in source.controller.graveyard:
            if (
                card.type == CardType.MINION
                and getattr(card, "killed_this_turn", False)
                and card.get_actions("deathrattle")
            ):
                copied.append(card.get_actions("deathrattle"))
        if copied:
            archdruid._edr_491_deathrattles = copied
            archdruid.tags[GameTag.DEATHRATTLE] = 1
        source.game.manager.targeted_action(self, source, archdruid)


class EDR_491_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, archdruid):
        for actions in getattr(archdruid, "_edr_491_deathrattles", []):
            source.game.queue_actions(source, actions)


class EDR_494_EndTurn(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, ancient):
        minions = [card for card in source.controller.deck if card.type == CardType.MINION]
        if not minions:
            return
        eaten = source.game.random.choice(minions)
        ancient._edr_494_eaten = getattr(ancient, "_edr_494_eaten", []) + [eaten.id]
        actions = [Buff(ancient, "EDR_494e", atk=eaten.atk, max_health=eaten.max_health)]
        eaten.zone = Zone.GRAVEYARD
        return source.game.queue_actions(source, actions)


class EDR_494_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, ancient):
        return source.game.queue_actions(
            source,
            [Give(source.controller, card_id) for card_id in getattr(ancient, "_edr_494_eaten", [])],
        )


class EDR_654_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        gifted = [
            card for card in player.hand
            if card.type == CardType.MINION and getattr(card, "_dark_gift", False)
        ]
        return source.game.queue_actions(
            source, [Buff(card, "EDR_654e") for card in gifted]
        )


class FIR_924_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
        )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [EDR_DarkGift(card), Give(self.player, card)])
        self.trigger_choice_callback()


class FIR_924_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        ids = _collectible_ids(
            source,
            lambda data: data.type == CardType.MINION and Race.DEMON in data.races,
        )
        cards = [player.card(card_id, source=source) for card_id in ids[:3]]
        if cards:
            return source.game.queue_actions(source, [FIR_924_Choice(player, cards)])


class FIR_954_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if not target:
            return
        return source.game.queue_actions(
            source, [Hit(target, 5), Draw(target.controller)]
        )


class FIR_955_Damage(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, destroyer):
        player = destroyer.controller
        if source.game.current_player != player or not player.opponent.field:
            return
        enemy = source.game.random.choice(player.opponent.field)
        return source.game.queue_actions(source, [Hit(enemy, 3)])


##
# Minions


class EDR_485:
    """Rotheart Dryad"""

    deathrattle = EDR_485_Deathrattle(SELF)


class EDR_487:
    """Wallow, the Wretched"""

    pass


class EDR_489:
    """Agamaggan"""

    play = EDR_489_Play(CONTROLLER)


class EDR_489e1:
    """Corrupted Thorns"""

    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class EDR_490t:
    """Night Terror"""

    taunt = True
    cant_attack = True


class EDR_491:
    """Archdruid of Thorns"""

    play = EDR_491_Play(SELF)
    deathrattle = EDR_491_Deathrattle(SELF)


class EDR_491e:
    """Devoured Soul"""

    pass


class EDR_494:
    """Hungering Ancient"""

    events = OWN_TURN_END.on(EDR_494_EndTurn(SELF))
    deathrattle = EDR_494_Deathrattle(SELF)


class EDR_494e:
    """Feed Me!"""

    pass


class EDR_654:
    """Overgrown Horror"""

    taunt = True
    play = EDR_654_Play(CONTROLLER)


class EDR_654e:
    """Overgrown"""

    tags = {GameTag.COST: -2}


class FIR_924:
    """Shadowflame Stalker"""

    play = FIR_924_Play(CONTROLLER)


class FIR_955:
    """Emberroot Destroyer"""

    events = Damage(FRIENDLY_HERO).on(FIR_955_Damage(SELF))


##
# Spells


class EDR_482:
    """Rotten Apple"""

    play = Heal(FRIENDLY_HERO, 12), Buff(CONTROLLER, "EDR_482e")


class EDR_482e:
    """Fracture"""

    events = OWN_TURN_END.on(EDR_482e_Tick(SELF))


class EDR_483:
    """Fractured Power"""

    play = EDR_483_Play(CONTROLLER)


class EDR_483e:
    """Delayed Mana"""

    events = OWN_TURN_BEGIN.on(EDR_483e_Tick(SELF))


class EDR_488:
    """Avant-Gardening"""

    play = EDR_488_Play(CONTROLLER)


class EDR_489e2:
    """Corrupted Thorns"""

    tags = {GameTag.ATK: 3, GameTag.HEALTH: 3}


class EDR_490:
    """Sleep Paralysis"""

    choose = ("EDR_490a", "EDR_490b")
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }


class EDR_490a:
    """Figure in the Dark"""

    play = Summon(CONTROLLER, "EDR_490t") * 2


class EDR_490b:
    """Wit's End"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Destroy(TARGET)


class FIR_954:
    """Conflagrate"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = FIR_954_Play(TARGET)
