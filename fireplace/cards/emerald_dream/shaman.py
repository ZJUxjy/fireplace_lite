# Shaman cards from EMERALD_DREAM expansion
from ..utils import *


DREADSEED_WOLF = "EX1_tk11"


def _copy_card_for(player, source, card):
    return player.card(card.id, source=source)


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


def _random_minion(source, cost):
    ids = _collectible_ids(
        source,
        lambda data: data.type == CardType.MINION and data.cost == cost,
    )
    if ids:
        return source.controller.card(source.game.random.choice(ids), source=source)


class EDR_031_PlayTopThree(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for card in list(reversed(list(player.deck)[-3:])):
            card.zone = Zone.HAND
            actions.append(Play(card, None, None, None))
        return source.game.queue_actions(player, actions)


class EDR_230_BuffDeckMinions(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = []
        for card in reversed(player.deck):
            if card.type == CardType.MINION:
                minions.append(card)
                if len(minions) == 3:
                    break
        return source.game.queue_actions(source, [Buff(card, "EDR_230e") for card in minions])


class EDR_448_Imbue(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if player.hero.power.id != "EDR_448p":
            player.hero.power.zone = Zone.SETASIDE
            power = player.card("EDR_448p", source=source)
            power._edr_448_amount = 1
            source.game.queue_actions(source, [Summon(player, power)])
        else:
            player.hero.power._edr_448_amount = getattr(
                player.hero.power, "_edr_448_amount", 1
            ) + 1
        source.game.manager.targeted_action(self, source, player)


class EDR_232_ShuffleMinions(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for minion in list(player.game.board):
            target_player = source.game.random.choice([player, player.opponent])
            actions.append(Shuffle(target_player, minion))
        return source.game.queue_actions(source, actions)


class EDR_234_DrawAndLock(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = list(reversed(list(player.deck)[-2:]))
        return source.game.queue_actions(
            source,
            [
                action
                for card in cards
                for action in (ForceDraw(card).then(Buff(ForceDraw.TARGET, "EDR_234e2")),)
            ]
            + [Buff(player, "EDR_234te", _edr_234_cards=cards)],
        )


class EDR_234te_Tick(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, aura):
        remaining = getattr(aura, "_edr_234_turns_remaining", 2) - 1
        aura._edr_234_turns_remaining = remaining
        if remaining > 0:
            return
        for card in getattr(aura, "_edr_234_cards", []):
            card.cant_play = False
            for buff in list(card.buffs):
                if buff.id == "EDR_234e2":
                    buff.remove()
        aura.remove()
        source.game.manager.targeted_action(self, source, aura)


class EDR_238_ResurrectBigMinions(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        seen = set()
        actions = []
        for card in player.graveyard:
            if card.type == CardType.MINION and card.cost >= 8 and card.id not in seen:
                seen.add(card.id)
                actions.append(Summon(player, player.card(card.id, source=source)))
        return source.game.queue_actions(source, actions)


class EDR_518_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = [EDR_448_Imbue(player)]
        minions = [card for card in player.hand if card.type == CardType.MINION]
        if minions:
            actions.append(Buff(source.game.random.choice(minions), "EDR_518e"))
        return source.game.queue_actions(source, actions)


class EDR_448p_Transform(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        amount = getattr(source, "_edr_448_amount", 1)
        if target.id == "EDR_529":
            amount += 2
        card = _random_minion(source, target.cost + amount)
        if card:
            return source.game.queue_actions(source, [Morph(target, card)])


class FIR_923_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = 8 if any(card.cost >= 8 for card in player.hand) else 4
        enemies = list(player.opponent.field)
        if enemies:
            return source.game.queue_actions(
                source,
                [Hit(source.game.random.choice(enemies), amount)],
            )


class FIR_927_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source,
            [Give(self.player, card), Buff(self.player, "FIR_927e")],
        )
        self.trigger_choice_callback()


class FIR_927_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        ids = _collectible_ids(source, lambda data: data.cost == 5)
        cards = [player.card(card_id, source=source) for card_id in ids[:3]]
        if cards:
            return source.game.queue_actions(source, [FIR_927_Choice(player, cards)])


##
# Minions


class EDR_031:
    """Ohn'ahra"""

    events = OWN_TURN_END.on(EDR_031_PlayTopThree(CONTROLLER))


class EDR_230:
    """Beanstalk Brute"""

    play = EDR_230_BuffDeckMinions(CONTROLLER)


class EDR_230e:
    """Enchanted"""

    tags = {GameTag.ATK: 4, GameTag.HEALTH: 4}


class EDR_231:
    """Aspect's Embrace"""

    play = Heal(FRIENDLY_HERO, 4), Draw(CONTROLLER), EDR_448_Imbue(CONTROLLER)


class EDR_233:
    """Spirits of the Forest"""

    choose = ("EDR_233a", "EDR_233b")
    play = Choice(CONTROLLER, ["EDR_233a", "EDR_233b"]).then(Battlecry(Choice.CARD, None))


class EDR_233a:
    """Wolf's Strength"""

    play = Summon(CONTROLLER, DREADSEED_WOLF) * 3


class EDR_233b:
    """Falcon's Dexterity"""

    play = Summon(CONTROLLER, "EDR_233t2") * 2


class EDR_233t2:
    """Spirit Falcon"""

    windfury = True


class EDR_234:
    """Emerald Bounty"""

    play = EDR_234_DrawAndLock(CONTROLLER)


class EDR_234e2:
    """Still Growing"""

    def apply(self, target):
        target.cant_play = True


@custom_card
class EDR_234te:
    """Emerald Bounty Lock"""

    tags = {
        GameTag.CARDNAME: "Emerald Bounty Lock",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = OWN_TURN_BEGIN.on(EDR_234te_Tick(SELF))


class EDR_238:
    """Merithra"""

    play = EDR_238_ResurrectBigMinions(CONTROLLER)


class EDR_477:
    """Glowroot Lure"""

    taunt = True
    cost_mod = -Attr(CONTROLLER, GameTag.NUM_TIMES_HERO_POWER_USED_THIS_GAME)


class EDR_518:
    """Living Garden"""

    play = EDR_518_Play(CONTROLLER)


@custom_card
class EDR_518e:
    """Living Garden Discount"""

    tags = {
        GameTag.CARDNAME: "Living Garden Discount",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


class EDR_529:
    """Plucky Podling"""

    pass


class EDR_448p:
    """Blessing of the Wind"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    activate = EDR_448p_Transform(TARGET)


##
# Spells


class EDR_232:
    """Typhoon"""

    play = EDR_232_ShuffleMinions(CONTROLLER)


class FIR_778:
    """Avatar of Destruction"""

    taunt = True
    deathrattle = Hit(ENEMY_MINIONS, 9)


class FIR_923:
    """Flames of the Firelord"""

    play = FIR_923_Play(CONTROLLER)


class FIR_927:
    """Emberscarred Whelp"""

    play = FIR_927_Play(CONTROLLER)


@custom_card
class FIR_927e:
    """Emberscarred Mana"""

    tags = {
        GameTag.CARDNAME: "Emberscarred Mana",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = OWN_TURN_BEGIN.on(ManaThisTurn(CONTROLLER, 1), Destroy(SELF))


##
# Minion Tokens


class EDR_233t2:
    """Spirit Falcon"""

    windfury = True
