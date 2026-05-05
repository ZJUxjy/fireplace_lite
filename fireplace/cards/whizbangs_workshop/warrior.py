from ..utils import *


def _mech(card):
    return Race.MECHANICAL in getattr(card, "races", ())


def _taunt_data(data):
    return bool(data.tags.get(GameTag.TAUNT))


def _mini_data(data):
    return bool(data.tags.get(GameTag.MINI))


class MIS_705_StandardizedPack(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        pool = [
            card_id
            for card_id, data in db.items()
            if data.collectible
            and data.type == CardType.MINION
            and _taunt_data(data)
            and (not source.game.is_standard or data.is_standard)
        ]
        if not pool:
            return
        actions = []
        for _ in range(5):
            card = player.card(source.game.random.choice(pool), source=source)
            actions.append(Give(player, Buff(card, "MIS_705e")))
        return source.game.queue_actions(source, actions)


class MIS_902_PartScrapper(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = min(player.hero.armor, 5)
        player.hero.armor -= amount
        if amount:
            return source.game.queue_actions(
                source, [Buff(player, "MIS_902e", _discount=amount)]
            )


class TOY_602_ChemicalSpill(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.hand if card.type == CardType.MINION]
        if not minions:
            return
        highest = max(minions, key=lambda card: card.cost)
        return source.game.queue_actions(
            source,
            [Summon(player, highest).then(Hit(Summon.CARD, 5))],
        )


class TOY_603_WreckemAndDeckem(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        copy = ExactCopy(TARGET).copy(source, target)
        if source.controller.opponent.characters:
            actions = [
                Summon(source.controller, copy).then(
                    Attack(Summon.CARD, RANDOM_ENEMY_CHARACTER),
                    Destroy(Summon.CARD),
                )
            ]
        else:
            actions = [Summon(source.controller, copy).then(Destroy(Summon.CARD))]
        return source.game.queue_actions(source, actions)


class TOY_604_BoomWrench(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        mechs = [
            minion
            for minion in player.field
            if _mech(minion) and minion.has_deathrattle
        ]
        if not mechs:
            return
        return source.game.queue_actions(
            source, [Deathrattle(source.game.random.choice(mechs))]
        )


class TOY_605_QualityAssurance(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        taunts = [card for card in player.deck if card.data.tags.get(GameTag.TAUNT)]
        actions = []
        for card in taunts[:2]:
            actions.append(ForceDraw(card))
        return source.game.queue_actions(source, actions)


class TOY_606_TestingDummy(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for _ in range(8):
            enemies = [minion for minion in player.opponent.field if not minion.dead]
            if not enemies:
                break
            actions.append(Hit(source.game.random.choice(enemies), 1))
        return source.game.queue_actions(source, actions)


class TOY_607_InventorBoom(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        seen = set()
        mechs = []
        for card in reversed(player.graveyard):
            if card.id in seen:
                continue
            if (
                card.type == CardType.MINION
                and _mech(card)
                and card.data.cost >= 5
            ):
                seen.add(card.id)
                mechs.append(card)
            if len(mechs) == 2:
                break

        actions = []
        for card in mechs:
            copy = ExactCopy(TARGET).copy(source, card)
            action = Summon(player, copy)
            if player.opponent.characters:
                action = action.then(Attack(Summon.CARD, RANDOM_ENEMY_CHARACTER))
            actions.append(action)
        return source.game.queue_actions(source, actions)


class TOY_651_LabPatron(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, patron):
        player = patron.controller
        if getattr(player, "_lab_patron_turn", None) == source.game.turn:
            return
        player._lab_patron_turn = source.game.turn
        return source.game.queue_actions(source, [Summon(player, "TOY_651")])


class TOY_906_Botface(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        pool = [card_id for card_id, data in db.items() if _mini_data(data)]
        if not pool:
            return
        return source.game.queue_actions(
            source,
            [Give(player, source.game.random.choice(pool)) for _ in range(2)],
        )


def _safety_goggles_cost(card, cost):
    return 0 if card.controller.hero.armor == 0 else cost


##
# Minions


class MIS_711:
    """Safety Expert"""

    deathrattle = Shuffle(OPPONENT, "BOT_511t") * 3


class TOY_606:
    """Testing Dummy"""

    deathrattle = TOY_606_TestingDummy(CONTROLLER)


class TOY_607:
    """Inventor Boom"""

    play = TOY_607_InventorBoom(CONTROLLER)


class TOY_651:
    """Lab Patron"""

    events = GainArmor(FRIENDLY_HERO).on(TOY_651_LabPatron(SELF))


class TOY_906:
    """Botface"""

    events = Damage(SELF).on(TOY_906_Botface(CONTROLLER))


class TOY_908:
    """Fireworker"""

    deathrattle = Summon(CONTROLLER, "GVG_110t") * 2


##
# Spells


class MIS_705:
    """Standardized Pack"""

    play = MIS_705_StandardizedPack(CONTROLLER)


class MIS_902:
    """Part Scrapper"""

    play = MIS_902_PartScrapper(CONTROLLER)


class TOY_602:
    """Chemical Spill"""

    play = TOY_602_ChemicalSpill(CONTROLLER)


class TOY_603:
    """Wreck'em and Deck'em"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_TARGET_WITH_RACE: Race.MECHANICAL,
    }
    play = TOY_603_WreckemAndDeckem(TARGET)


class TOY_605:
    """Quality Assurance"""

    play = TOY_605_QualityAssurance(CONTROLLER)


class TOY_907:
    """Safety Goggles"""

    play = GainArmor(FRIENDLY_HERO, 6)

    class Hand:
        update = Refresh(SELF, {GameTag.COST: _safety_goggles_cost})


##
# Weapons


class TOY_604:
    """Boom Wrench"""

    miniaturize_mini = "TOY_604t"
    play = Give(CONTROLLER, "TOY_604t")
    deathrattle = TOY_604_BoomWrench(CONTROLLER)


class TOY_604t:
    """Boom Wrench"""

    deathrattle = TOY_604_BoomWrench(CONTROLLER)


##
# Buffs


@custom_card
class MIS_705e:
    tags = {
        GameTag.CARDNAME: "Temporary",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    class Hand:
        events = OWN_TURN_END.on(Discard(OWNER))

    events = REMOVED_IN_PLAY


class MIS_902e:
    update = Refresh(FRIENDLY_HAND + MECH, buff="MIS_902e2")
    events = Play(CONTROLLER, MECH).on(Destroy(SELF))


@custom_card
class MIS_902e2:
    tags = {
        GameTag.CARDNAME: "Scrapped",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    cost = lambda self, cost: max(0, cost - self.source._discount)
