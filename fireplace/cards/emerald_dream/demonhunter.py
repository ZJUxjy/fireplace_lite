# Demonhunter cards from EMERALD_DREAM expansion
from hearthstone.enums import SpellSchool, Zone

from ..utils import *


DREADSEEDS = ("EDR_840t", "EDR_840t1", "EDR_840t2")
DREADSEED_TURNS = {"EDR_840t": 2, "EDR_840t1": 1, "EDR_840t2": 3}

FEL_SPELL = SPELL + FuncSelector(
    lambda entities, source: [
        e for e in entities
        if getattr(getattr(e, "data", None), "spell_school", None) == SpellSchool.FEL
    ]
)


def _collectible_cards(source, predicate):
    cards = []
    for card_id, data in db.items():
        if (
            data.collectible
            and (not source.game.is_standard or data.is_standard)
            and predicate(data)
        ):
            cards.append(source.controller.card(card_id, source=source))
    source.game.random.shuffle(cards)
    return cards[:3]


def _is_fel_spell(card):
    return (
        card.type == CardType.SPELL
        and getattr(getattr(card, "data", None), "spell_school", None) == SpellSchool.FEL
    )


def _move_to_hand(card, index=None):
    if index is not None:
        card._summon_index = index
    card.zone = Zone.HAND
    card._summon_index = None


class EDR_421_Attacked(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, omen):
        omen._edr_421_damage = getattr(
            omen, "_edr_421_damage", omen.data.tags.get(GameTag.TAG_SCRIPT_DATA_NUM_1, 1)
        ) + 1


class EDR_421_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, omen):
        amount = getattr(
            omen, "_edr_421_damage", omen.data.tags.get(GameTag.TAG_SCRIPT_DATA_NUM_1, 1)
        )
        return source.game.queue_actions(source, [Hit(ENEMY_CHARACTERS, amount)])


class EDR_493_TransformHand(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        hand_minions = [
            (player.hand.index(card), card, card.cost, card.atk, card.max_health)
            for card in list(player.hand)
            if card.type == CardType.MINION
        ]
        if not hand_minions:
            return
        demon_ids = [
            card_id for card_id, data in db.items()
            if (
                data.collectible
                and data.type == CardType.MINION
                and Race.DEMON in data.races
                and (not source.game.is_standard or data.is_standard)
            )
        ]
        if not demon_ids:
            return

        actions = []
        for _, card, _, _, _ in hand_minions:
            card.zone = Zone.SETASIDE
        for index, card, cost, atk, health in hand_minions:
            demon = player.card(source.game.random.choice(demon_ids), source=source)
            actions.append(
                Buff(
                    demon,
                    "EDR_493e2",
                    cost=cost - demon.cost,
                    atk=atk - demon.atk,
                    max_health=health - demon.max_health,
                )
            )
            actions.append(EDR_493_MoveToHand(demon, index))
        return source.game.queue_actions(source, actions)


class EDR_493_MoveToHand(TargetedAction):
    TARGET = ActionArg()
    INDEX = IntArg()

    def do(self, source, card, index):
        _move_to_hand(card, index)


class EDR_840_SummonDreadseed(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        card_id = source.game.random.choice(DREADSEEDS)
        return source.game.queue_actions(
            source,
            [
                Summon(player, card_id).then(
                    Dormant(Summon.CARD, DREADSEED_TURNS[card_id])
                )
            ],
        )


class EDR_842_Splash(TargetedAction):
    TARGET = ActionArg()
    DEFENDER = ActionArg()

    def do(self, source, weapon, defender):
        candidates = [
            character for character in weapon.controller.opponent.characters
            if character is not defender and not getattr(character, "dead", False)
        ]
        if not candidates:
            return
        target = source.game.random.choice(candidates)
        return source.game.queue_actions(source, [Hit(target, weapon.atk)])


class EDR_890_DiscountRightmost(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if player.hand:
            return source.game.queue_actions(source, [Buff(player.hand[-1], "EDR_890e")])


class EDR_891_Resurrect(TargetedAction):
    TARGET = ActionArg()
    MIN_COST = IntArg()
    MAX_COST = IntArg()
    EXCLUDE_ID = ActionArg()

    def do(self, source, player, min_cost, max_cost, exclude_id):
        candidates = [
            card for card in player.graveyard
            if (
                card.type == CardType.MINION
                and card.has_deathrattle
                and min_cost <= card.cost <= max_cost
                and card.id != exclude_id
            )
        ]
        if not candidates:
            return
        card = source.game.random.choice(candidates)
        return source.game.queue_actions(
            source,
            [
                Summon(player, ExactCopy(TARGET).copy(source, card)),
                Summon(player, ExactCopy(TARGET).copy(source, card)),
            ],
        )


class EDR_882_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        card._dark_gift = True
        actions = [Give(self.player, card)]
        actions.extend(Shuffle(self.player, other) for other in self.cards if other is not card)
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class EDR_882_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda data: (
                data.type == CardType.MINION
                and Race.DEMON in data.races
                and data.cost >= 5
            ),
        )
        return source.game.queue_actions(source, [EDR_882_Choice(player, cards)])


class FIR_902_Cinder(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for _ in range(6):
            if not player.opponent.characters:
                break
            actions.append(Hit(source.game.random.choice(list(player.opponent.characters)), 1))
        actions.append(Destroy(SELF))
        return source.game.queue_actions(source, actions)


class FIR_904_Explode(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, blaze):
        if blaze.zone != Zone.PLAY:
            return
        return source.game.queue_actions(
            source, [Destroy(blaze), Hit(ENEMY_CHARACTERS, 2)]
        )


class FIR_952_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class FIR_952_DiscoverAndDiscount(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda data: (
                data.type == CardType.SPELL
                and getattr(data, "spell_school", None) == SpellSchool.FEL
            ),
        )
        actions = [Buff(card, "FIR_952e") for card in player.hand if _is_fel_spell(card)]
        actions.append(FIR_952_Choice(player, cards))
        return source.game.queue_actions(source, actions)


##
# Minions


class EDR_421:
    """Omen"""

    tags = {GameTag.RUSH: True, GameTag.WINDFURY: True, GameTag.DEATHRATTLE: True}
    events = Attack(SELF).after(EDR_421_Attacked(SELF))
    deathrattle = EDR_421_Deathrattle(SELF)


class EDR_493:
    """Alara'shi"""

    play = EDR_493_TransformHand(CONTROLLER)


class EDR_493e2:
    """Demon Form"""

    tags = {GameTag.CARDRACE: Race.DEMON}


class EDR_521e1:
    """Tricky"""

    pass


class EDR_521e2:
    """Tricked"""

    pass


class EDR_841:
    """Dreadsoul Corrupter"""

    play = EDR_840_SummonDreadseed(CONTROLLER)
    deathrattle = EDR_840_SummonDreadseed(CONTROLLER)


class EDR_842:
    """Defiled Spear"""

    events = Attack(FRIENDLY_HERO, ENEMY_CHARACTERS).after(
        EDR_842_Splash(SELF, Attack.DEFENDER)
    )


class EDR_890:
    """Nightmare Dragonkin"""

    deathrattle = EDR_890_DiscountRightmost(CONTROLLER)


class EDR_891:
    """Ravenous Felhunter"""

    deathrattle = EDR_891_Resurrect(CONTROLLER, 0, 4, None)


class EDR_892:
    """Ferocious Felbat"""

    deathrattle = EDR_891_Resurrect(CONTROLLER, 5, 100, "EDR_892")


class FIR_904:
    """Felfire Blaze"""

    events = Play(CONTROLLER, FEL_SPELL).after(FIR_904_Explode(SELF))


class FIR_952:
    """Scorchreaver"""

    play = FIR_952_DiscoverAndDiscount(CONTROLLER)


##
# Spells


class EDR_820:
    """Wyvern's Slumber"""

    choose = ("EDR_820a", "EDR_820b")


class EDR_820a:
    """Summon two Dreadseeds"""

    play = EDR_840_SummonDreadseed(CONTROLLER) * 2


class EDR_820b:
    """Deal 2 damage to all minions"""

    play = Hit(ALL_MINIONS, 2)


class EDR_840:
    """Grim Harvest"""

    play = Draw(CONTROLLER), EDR_840_SummonDreadseed(CONTROLLER)


class EDR_840t:
    """Hound Dreadseed"""

    awaken = Buff(FRIENDLY_HERO, "EDR_840te")


class EDR_840t1:
    """Crow Dreadseed"""

    elusive = True


class EDR_840t1e:
    """Dreaming Hound"""

    pass


class EDR_840t1e1:
    """Dreaming Crow"""

    pass


class EDR_840t2:
    """Serpent Dreadseed"""

    taunt = True
    lifesteal = True


class EDR_840t2e1:
    """Dreaming Serpent"""

    pass


class EDR_840te:
    """Hound's Fangs"""

    events = OWN_TURN_END.on(Destroy(SELF))


class EDR_840te2:
    """Eternal Nightmare"""

    pass


class EDR_882:
    """Jumpscare!"""

    play = EDR_882_Discover(CONTROLLER)


class FIR_902:
    """Sigil of Cinder"""

    play = Buff(CONTROLLER, "FIR_902e")


@custom_card
class EDR_890e:
    """Nightmare's Discount"""

    tags = {
        GameTag.CARDNAME: "Nightmare's Discount",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -2,
    }


@custom_card
class FIR_902e:
    """Sigil of Cinder"""

    tags = {
        GameTag.CARDNAME: "Sigil of Cinder",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = OWN_TURN_BEGIN.on(FIR_902_Cinder(CONTROLLER))


@custom_card
class FIR_952e:
    """Scorchreaver Discount"""

    tags = {
        GameTag.CARDNAME: "Scorchreaver Discount",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }
