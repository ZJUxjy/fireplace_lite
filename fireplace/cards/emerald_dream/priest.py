# Priest cards from EMERALD_DREAM expansion
from ..utils import *


def _priest_spells_cast(player):
    return len([card for card in player.cards_played_this_game if card.type == CardType.SPELL])


def _moon_full(player):
    return _priest_spells_cast(player) >= 3


class EDR_449_Imbue(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if player.hero.power.id != "EDR_449p":
            player.hero.power.zone = Zone.SETASIDE
            power = player.card("EDR_449p", source=source)
            power._edr_449_discount = 0
            source.game.queue_actions(source, [Summon(player, power)])
        player.hero.power._edr_449_discount = getattr(
            player.hero.power, "_edr_449_discount", 0
        ) + 1
        source.game.manager.targeted_action(self, source, player)


class EDR_449p_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source,
            [Buff(card, "EDR_449e", amount=self.discount), Give(self.player, card)],
        )
        self.trigger_choice_callback()


class EDR_449p_Activate(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        discount = getattr(source, "_edr_449_discount", 1)
        available_mana = player.max_mana - player.used_mana
        ids = db.filter(
            collectible=True,
            card_class=CardClass.PRIEST,
            type=[CardType.MINION, CardType.SPELL],
            is_standard=True,
        )
        cards = [
            player.card(card_id, source=source)
            for card_id in ids
            if max(0, db[card_id].cost - discount) <= available_mana
        ]
        if not cards:
            return
        source.game.random.shuffle(cards)
        choice = EDR_449p_Choice(player, cards[:3])
        choice.discount = discount
        return source.game.queue_actions(source, [choice])


class EDR_460_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        source.lifesteal = _moon_full(source.controller)
        return source.game.queue_actions(source, [Hit(target, 6)])


class EDR_461_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cost = 6 if _moon_full(player) else 3
        return source.game.queue_actions(source, [Summon(player, RandomMinion(cost=cost)) * 2])


class EDR_463_StartChoice(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        choice = EDR_463_Choice(player, ["EDR_463a", "EDR_463b"])
        choice.target = source.target
        return source.game.queue_actions(source, [choice])


class EDR_463_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        if card.id == "EDR_463a":
            actions = (
                [Destroy(self.target), Deaths()]
                if self.target and self.target.atk <= 3
                else []
            )
        else:
            actions = [Summon(self.player, RandomMinion(cost=2))]
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class EDR_464_DoubleNextSpell(TargetedAction):
    TARGET = ActionArg()
    CARD = ActionArg()
    SPELL_TARGET = ActionArg()

    def do(self, source, player, played, target):
        if getattr(source, "_edr_464_remaining", 3) <= 0:
            return
        source._edr_464_remaining = getattr(source, "_edr_464_remaining", 3) - 1
        copy = player.card(played.id, source=source)
        actions = [CastSpell(copy, target)]
        if source._edr_464_remaining <= 0:
            actions.append(Destroy(source))
        return source.game.queue_actions(source, actions)


class EDR_472_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        if any(hand_card.type == CardType.SPELL and hand_card.cost >= 5 for hand_card in source.controller.hand):
            return source.game.queue_actions(source, [Hit(source.controller.opponent.hero, 3)])


class EDR_895_StartCycle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(source, [Buff(player, "EDR_895t")])


class EDR_895t_Tick(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, cycle):
        remaining = getattr(cycle, "_edr_895_turns_remaining", 3) - 1
        cycle._edr_895_turns_remaining = remaining
        if remaining <= 0:
            player = cycle.controller
            actions = [Buff(card, "EDR_895e") for card in list(player.hand) + list(player.deck)]
            actions.append(Buff(player, "EDR_895e"))
            cycle.remove()
            source.game.manager.targeted_action(self, source, cycle)
            return source.game.queue_actions(source, actions)


class EDR_970_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [Buff(ENEMY_MINIONS, "EDR_970e"), EDR_449_Imbue(player)]
        )


class FIR_777_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        if source.controller.hero.power.activations_this_turn > 0:
            return source.game.queue_actions(source, [Buff(card, "FIR_777e2")])


class FIR_916_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = getattr(source, "_fir_916_amount", 1)
        return source.game.queue_actions(source, [Hit(ENEMY_MINIONS, amount)])


class FIR_916_Upgrade(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        amount = getattr(card, "_fir_916_amount", 1) + 1
        card._fir_916_amount = amount
        if amount >= 3:
            return source.game.queue_actions(source, [Discard(card)])


class FIR_918_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = [Buff(target, "FIR_918e1")]
        if _moon_full(source.controller):
            actions.append(Give(source.controller, "FIR_918"))
        return source.game.queue_actions(source, actions)


##
# Minions


class EDR_449:
    """Lunarwing Messenger"""

    lifesteal = True
    play = EDR_449_Imbue(CONTROLLER)


class EDR_449e:
    """Fleeting Magic"""

    cost = lambda self, cost: max(0, cost - self.amount)

    class Hand:
        events = OWN_TURN_END.on(Discard(OWNER))

    events = REMOVED_IN_PLAY


class EDR_449p:
    """Blessing of the Moon"""

    activate = EDR_449p_Activate(CONTROLLER)


class EDR_460:
    """Wish of the New Moon"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = EDR_460_Play(TARGET)


class EDR_460t:
    """Wish of the Full Moon"""

    lifesteal = True
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 6)


class EDR_461:
    """Ritual of the New Moon"""

    play = EDR_461_Play(CONTROLLER)


class EDR_461t:
    """Ritual of the Full Moon"""

    play = Summon(CONTROLLER, RandomMinion(cost=6)) * 2


class EDR_462:
    """Selenic Drake"""

    elusive = True
    events = OWN_TURN_END.on(Give(CONTROLLER, RandomDragon()))


class EDR_463:
    """Twilight Influence"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = EDR_463_StartChoice(CONTROLLER)


class EDR_463a:
    """Constricting Thorns"""

    pass


class EDR_463b:
    """Controlling Vines"""

    pass


class EDR_464:
    """Tyrande"""

    play = Buff(CONTROLLER, "EDR_464e2")


class EDR_464e2:
    """Pull of the Moon"""

    tags = {
        GameTag.CARDNAME: "Pull of the Moon",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = Play(CONTROLLER, SPELL).after(
        EDR_464_DoubleNextSpell(CONTROLLER, Play.CARD, Play.TARGET)
    )


class EDR_472:
    """Weaver of the Cycle"""

    play = EDR_472_Play(SELF)


class EDR_970:
    """Kaldorei Priestess"""

    play = EDR_970_Play(CONTROLLER)


class EDR_970e:
    """Pacified"""

    tags = {GameTag.ATK: -2}
    events = OWN_TURN_BEGIN.on(Destroy(SELF))


class EDR_895:
    """Aviana, Elune's Chosen"""

    play = EDR_895_StartCycle(CONTROLLER)


class EDR_895e:
    """Full Moon"""

    tags = {
        GameTag.CARDNAME: "Full Moon",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    cost = SET(1)


class EDR_895t:
    """Moon Cycle"""

    tags = {
        GameTag.CARDNAME: "Moon Cycle",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = OWN_TURN_BEGIN.on(EDR_895t_Tick(SELF))


class FIR_777:
    """Spirit of the Kaldorei"""

    taunt = True
    lifesteal = True
    play = FIR_777_Play(SELF)


class FIR_916:
    """Smoldering Ascent"""

    play = FIR_916_Play(CONTROLLER)

    class Hand:
        events = OWN_TURN_BEGIN.on(FIR_916_Upgrade(SELF))


class FIR_918:
    """Light of the New Moon"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = FIR_918_Play(TARGET)


class EDR_476:
    """Moonwell"""

    play = Hit(ENEMY_CHARACTERS, 4), Heal(FRIENDLY_CHARACTERS, 4)


class FIR_918t:
    """Light of the Full Moon"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "FIR_918e1"), Give(CONTROLLER, "FIR_918")
