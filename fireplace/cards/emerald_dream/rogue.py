# Rogue cards from EMERALD_DREAM expansion
from ..utils import *


def _copy_card_for(player, source, card):
    return player.card(card.id, source=source)


class EDR_521_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if not player.opponent.hand:
            return
        lowest = min(card.cost for card in player.opponent.hand)
        candidates = [card for card in player.opponent.hand if card.cost == lowest]
        card = source.game.random.choice(candidates)
        return source.game.queue_actions(source, [Give(player, _copy_card_for(player, source, card))])


class EDR_522_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        cards = list(reversed(list(player.opponent.deck)[-2:]))
        for card in cards:
            actions.append(ForceDraw(card))
            actions.append(Give(player, _copy_card_for(player, source, card)))
        return source.game.queue_actions(source, actions)


class EDR_523_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        player = source.controller
        actions = [Bounce(target)]
        actions.append(Summon(player, "EDR_523t"))
        return source.game.queue_actions(source, actions)


class EDR_524_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        player = source.controller
        ids = {hand_card.id for hand_card in player.hand}
        matches = [card for card in player.opponent.hand if card.id in ids]
        if matches:
            return source.game.queue_actions(source, [Shuffle(player.opponent, source.game.random.choice(matches))])


class EDR_525_StartChoice(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(source, [EDR_525_Choice(player, ["EDR_525A", "EDR_525B"])])


class EDR_525_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        weapon = self.source
        if card.id == "EDR_525A":
            actions = [
                Buff(weapon, "EDR_525ae"),
                Buff(weapon.controller, "EDR_525ate", _edr_525_weapon=weapon),
            ]
        else:
            actions = [Buff(weapon, "EDR_525e")]
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class EDR_526_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        count = getattr(player, "_edr_526_played", 0) + 1
        player._edr_526_played = count
        candidates = [card for card in player.opponent.hand if not any(buff.id == "EDR_780e" for buff in card.buffs)]
        source.game.random.shuffle(candidates)
        cards = candidates[:count]
        return source.game.queue_actions(
            source,
            [Buff(card, "EDR_780e") for card in cards]
            + [Buff(player, "EDR_526te", _edr_526_trapped_cards=cards)],
        )


class EDR_527_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        while len(player.hand) + len(actions) < player.max_hand_size and player.opponent.deck:
            card = source.game.random.choice(player.opponent.deck)
            copy = _copy_card_for(player, source, card)
            actions.append(Give(player, copy).then(Buff(Give.CARD, "EDR_527e")))
        return source.game.queue_actions(source, actions)


class EDR_528_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        if self.dark_gift:
            self.source.game.queue_actions(self.source, [EDR_DarkGift(card)])
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class EDR_528_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = [_copy_card_for(player, source, card) for card in player.opponent.deck if card.type == CardType.MINION]
        if not cards:
            return
        source.game.random.shuffle(cards)
        choice = EDR_528_Choice(player, cards[:3])
        choice.dark_gift = player.combo
        return source.game.queue_actions(source, [choice])


class EDR_540_DrawReplay(TargetedAction):
    TARGET = ActionArg()
    CARD = ActionArg()

    def do(self, source, webweaver, card):
        if card is webweaver or card.type != CardType.MINION:
            return
        if any(played.id == card.id for played in source.controller.cards_played_this_game):
            return source.game.queue_actions(source, [Draw(source.controller)])


class EDR_526e_RemoveTraps(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, aura):
        for card in getattr(aura, "_edr_526_trapped_cards", []):
            for buff in list(card.buffs):
                if buff.id == "EDR_780e":
                    buff.remove()
        aura.remove()
        source.game.manager.targeted_action(self, source, aura)


class EDR_525a_RemovePoison(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, aura):
        weapon = getattr(aura, "_edr_525_weapon", None)
        if weapon:
            for buff in list(weapon.buffs):
                if buff.id == "EDR_525ae":
                    buff.remove()
        aura.remove()
        source.game.manager.targeted_action(self, source, aura)


class FIR_919e_EndTurn(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(source, [Give(player, "FIR_919"), Destroy(source)])


class FIR_920_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source, [EDR_DarkGift(card), Give(self.player, card)]
        )
        self.trigger_choice_callback()


class FIR_920_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        ids = ["EDR_521", "EDR_524", "EDR_540", "EDR_781", "FIR_919"]
        cards = [player.card(card_id, source=source) for card_id in ids]
        source.game.random.shuffle(cards)
        return source.game.queue_actions(source, [FIR_920_Choice(player, cards[:3])])


class FIR_922_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        if any(card.type == CardType.MINION and getattr(card, "_dark_gift", False) for card in source.controller.hand):
            return source.game.queue_actions(source, [Buff(weapon, "FIR_922e")])


##
# Minions


class EDR_521:
    """Tricky Satyr"""

    play = EDR_521_Play(CONTROLLER)


class EDR_522:
    """Mimicry"""

    play = EDR_522_Play(CONTROLLER)


class EDR_523:
    """Web of Deception"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = EDR_523_Play(TARGET)


class EDR_523t:
    """Skittering Spiderling"""

    stealth = True


class EDR_524:
    """Shadowcloaked Assailant"""

    stealth = True
    play = EDR_524_Play(SELF)


class EDR_525:
    """Barbed Thorn"""

    play = EDR_525_StartChoice(CONTROLLER)


class EDR_525A:
    """Extra Eyes"""

    pass


class EDR_525B:
    """Extra Thorns"""

    pass


@custom_card
class EDR_525ae:
    """Extra Eyes"""

    tags = {
        GameTag.CARDNAME: "Extra Eyes",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.POISONOUS: 1,
    }
    poisonous = True
    events = OWN_TURN_END.on(Destroy(SELF))


@custom_card
class EDR_525ate:
    """Extra Eyes Cleanup"""

    tags = {
        GameTag.CARDNAME: "Extra Eyes Cleanup",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = OWN_TURN_END.on(EDR_525a_RemovePoison(SELF))


class EDR_525e:
    """Barbed Upgrade"""

    tags = {GameTag.DEATHRATTLE: True}
    deathrattle = Hit(ENEMY_CHARACTERS, 2)


class EDR_526:
    """Renferal, the Malignant"""

    play = EDR_526_Play(CONTROLLER)


@custom_card
class EDR_526te:
    """Renferal's Traps"""

    tags = {
        GameTag.CARDNAME: "Renferal's Traps",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = OWN_TURN_BEGIN.on(EDR_526e_RemoveTraps(SELF))


class EDR_527:
    """Ashamane"""

    play = EDR_527_Play(CONTROLLER)


@custom_card
class EDR_527e:
    """Ashamane's Discount"""

    tags = {
        GameTag.CARDNAME: "Ashamane's Discount",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -3,
    }


class EDR_540:
    """Twisted Webweaver"""

    events = Play(CONTROLLER, MINION).after(EDR_540_DrawReplay(SELF, Play.CARD))


class EDR_780e:
    """Illusion?"""

    pass


class EDR_781:
    """Harbinger of the Blighted"""

    pass


##
# Spells


class EDR_528:
    """Nightmare Fuel"""

    play = EDR_528_Play(CONTROLLER)
    combo = EDR_528_Play(CONTROLLER)


class FIR_919:
    """Everburning Phoenix"""

    cost_mod = -Attr(CONTROLLER, GameTag.NUM_CARDS_PLAYED_THIS_TURN)
    deathrattle = Buff(CONTROLLER, "FIR_919e")


class FIR_920:
    """Smoke Bomb"""

    play = FIR_920_Play(CONTROLLER)


class FIR_922:
    """Cindersword"""

    play = FIR_922_Play(SELF)


class FIR_922e:
    """Fiery"""

    tags = {GameTag.ATK: 3}
