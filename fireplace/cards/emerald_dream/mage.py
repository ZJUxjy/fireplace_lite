# Mage cards from EMERALD_DREAM expansion
from hearthstone.enums import SpellSchool

from ..utils import *


FIRE_SPELL = SPELL + FuncSelector(
    lambda entities, source: [
        e
        for e in entities
        if getattr(getattr(e, "data", None), "spell_school", None) == SpellSchool.FIRE
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


def _friendly_minions_died(player):
    return len(player.graveyard.filter(type=CardType.MINION))


def _wisp_count(player):
    return len(player.field.filter(id="EDR_851t"))


class EDR_430_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if _friendly_minions_died(player) < 20:
            return
        return source.game.queue_actions(
            source, [Hit(RANDOM_ENEMY_CHARACTER, 1) for _ in range(20)]
        )


class EDR_517_DiscoverChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source._edr_517_spell = card
        self.source.game.queue_actions(
            self.source, [EDR_517_ModeChoice(self.player, ["EDR_517A", "EDR_517B"])]
        )
        self.trigger_choice_callback()


class EDR_517_ModeChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        spell = getattr(self.source, "_edr_517_spell", None)
        if spell:
            if card.id == "EDR_517A":
                actions = [Give(self.player, spell)]
            else:
                actions = [PutOnTop(self.player.opponent, spell)]
            self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class EDR_517_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(source, lambda data: data.type == CardType.SPELL)
        return source.game.queue_actions(source, [EDR_517_DiscoverChoice(player, cards)])


class EDR_851_Imbue(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        player._edr_851p_amount = getattr(player, "_edr_851p_amount", 0) + 1
        if player.hero.power.id != "EDR_851p":
            return source.game.queue_actions(source, [Summon(player, "EDR_851p")])


class EDR_851p_Activate(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = getattr(player, "_edr_851p_amount", 1)
        return source.game.queue_actions(
            source,
            [Summon(player, "EDR_851t") for _ in range(amount)]
            + [Hit(RANDOM_ENEMY_CHARACTER, 1) for _ in range(amount)],
        )


class EDR_519_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [EDR_851_Imbue(player), EDR_851p_Activate(player)]
        )


class EDR_520_Activate(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, location):
        player = location.controller
        amount = player.max_mana - player.used_mana
        player.used_mana = player.max_mana
        cards = _collectible_cards(
            source,
            lambda data: data.type == CardType.SPELL and data.cost == amount,
        )
        if cards:
            return source.game.queue_actions(source, [CastSpell(cards[0])])


class EDR_804_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        wisps = player.field.filter(id="EDR_851t")
        if not wisps:
            return
        return source.game.queue_actions(
            source, [Destroy(source.game.random.choice(wisps)), Draw(player) * 3]
        )


class EDR_872_DiscoverChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        card_class = CardClass.MAGE if card.id == "EDR_872A" else CardClass.DRUID
        cards = _collectible_cards(
            self.source,
            lambda data: data.type == CardType.SPELL and data.card_class == card_class,
        )
        self.source.game.queue_actions(self.source, [Choice(self.player, cards).then(Give(CONTROLLER, Choice.CARD))])
        self.trigger_choice_callback()


class EDR_874_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        moonfire = player.card("CS2_008", source=source)
        starfire = player.card("EX1_173", source=source)
        return source.game.queue_actions(
            source,
            [
                Buff(moonfire, "EDR_874e"),
                Give(player, moonfire),
                Buff(starfire, "EDR_874e"),
                Give(player, starfire),
            ],
        )


class EDR_940_EndTurn(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [GainArmor(player.hero, 1 + _wisp_count(player))]
        )


class EDR_941_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        return source.game.queue_actions(
            source, [Hit(target, 1 + _friendly_minions_died(source.controller))]
        )


class FIR_910_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = [Hit(target, 3)]
        fire_spells = [
            card
            for card in source.controller.hand
            if card.type == CardType.SPELL
            and getattr(getattr(card, "data", None), "spell_school", None)
            == SpellSchool.FIRE
        ]
        if fire_spells:
            actions.append(Discard(source.game.random.choice(fire_spells)))
            actions.append(Hit(target, 3))
        return source.game.queue_actions(source, actions)


class FIR_911_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = getattr(source, "_fir_911_amount", 1)
        return source.game.queue_actions(source, [Draw(player) for _ in range(amount)])


class FIR_911_Upgrade(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        amount = getattr(card, "_fir_911_amount", 1) + 1
        card._fir_911_amount = amount
        if amount >= 3:
            return source.game.queue_actions(source, [Discard(card)])


class FIR_913_GiveElemental(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda data: data.type == CardType.MINION and data.race == Race.ELEMENTAL,
        )
        if cards:
            elemental = cards[0]
            return source.game.queue_actions(
                source,
                [Buff(elemental, "EDR_519e"), Give(player, elemental)],
            )


##
# Minions


class EDR_430:
    """Aessina"""

    play = EDR_430_Play(CONTROLLER)


class EDR_517:
    """Q'onzu"""

    play = EDR_517_Play(CONTROLLER)


class EDR_517A:
    """Tranquil Breeze"""

    pass


class EDR_517B:
    """Winds of Change"""

    pass


class EDR_519:
    """Wisprider"""

    play = EDR_519_Play(CONTROLLER)


class EDR_519e:
    """Wisprider Magic"""

    def cost(self, cost):
        return cost - 3


class EDR_520:
    """Forbidden Shrine"""

    activate = EDR_520_Activate(SELF)


class EDR_872:
    """Spark of Life"""

    play = EDR_872_DiscoverChoice(CONTROLLER, ["EDR_872A", "EDR_872B"])


class EDR_872A:
    """Gift of Fire"""

    pass


class EDR_872B:
    """Gift of Nature"""

    pass


class EDR_940:
    """Merry Moonkin"""

    events = OWN_TURN_END.on(EDR_940_EndTurn(CONTROLLER))


class EDR_941:
    """Starsurge"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = EDR_941_Play(TARGET)


##
# Spells


class EDR_804:
    """Divination"""

    play = EDR_804_Play(CONTROLLER)


class EDR_851p:
    """Blessing of the Wisp"""

    activate = EDR_851p_Activate(CONTROLLER)


class EDR_874:
    """Stellar Balance"""

    play = EDR_874_Play(CONTROLLER)


class EDR_874e:
    """Stellar Balance"""

    tags = {GameTag.SPELLPOWER: 1}


class FIR_910:
    """Scorching Winds"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = FIR_910_Play(TARGET)


class FIR_911:
    """Smoldering Grove"""

    play = FIR_911_Play(CONTROLLER)

    class Hand:
        events = OWN_TURN_BEGIN.on(FIR_911_Upgrade(SELF))


class FIR_913:
    """Inferno Herald"""

    events = Play(CONTROLLER, FIRE_SPELL).after(FIR_913_GiveElemental(CONTROLLER))


##
# Minion Tokens


class EDR_851t:
    """Wisp"""

    pass


class EDR_871:
    """Spirit Gatherer"""

    play = Give(CONTROLLER, "EDR_851t"), EDR_851_Imbue(CONTROLLER)
