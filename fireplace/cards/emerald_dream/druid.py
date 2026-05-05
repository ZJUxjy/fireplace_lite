# Druid cards from EMERALD_DREAM expansion
from hearthstone.enums import SpellSchool

from ..utils import *


NATURE_SPELL = SPELL + FuncSelector(
    lambda entities, source: [
        e for e in entities
        if getattr(getattr(e, "data", None), "spell_school", None) == SpellSchool.NATURE
    ]
)


def _is_nature_spell(card):
    return (
        card.type == CardType.SPELL
        and getattr(getattr(card, "data", None), "spell_school", None)
        == SpellSchool.NATURE
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


def _edr_847_cost(buff, cost):
    return 0 if buff.owner.controller.times_hero_power_used_this_game == buff._used_at else cost


class EDR_209_StartChoice(TargetedAction):
    TARGET = ActionArg()
    REMAINING = IntArg()

    def do(self, source, player, remaining):
        choice = EDR_209_Choice(player, ["EDR_209a", "EDR_209b"])
        choice.remaining = remaining
        return source.game.queue_actions(source, [choice])


class EDR_209_Choice(Choice):
    remaining = 3

    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        if card.id == "EDR_209a":
            actions = [Buff(FRIENDLY_MINIONS - SELF, "EDR_209e2")]
        else:
            actions = [Summon(self.player, "EDR_209t5")]
        if self.remaining > 1:
            actions.append(EDR_209_StartChoice(self.player, self.remaining - 1))
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class EDR_270_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source, [Buff(card, "EDR_270e"), Give(self.player, card)]
        )
        self.trigger_choice_callback()


class EDR_270_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda data: (
                data.type == CardType.SPELL
                and getattr(data, "spell_school", None) == SpellSchool.NATURE
            ),
        )
        return source.game.queue_actions(source, [EDR_270_Choice(player, cards)])


class EDR_271_SummonTreant(TargetedAction):
    TARGET = ActionArg()
    SPELL = CardArg()

    def do(self, source, player, spell):
        treant = player.card("EDR_271t", source=source)
        treant._edr_271_spell_id = spell.id
        treant.has_deathrattle = True
        return source.game.queue_actions(source, [Summon(player, treant)])


class EDR_271_GiveSpell(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, treant):
        spell_id = getattr(treant, "_edr_271_spell_id", None)
        if spell_id:
            return source.game.queue_actions(source, [Give(treant.controller, spell_id)])


class EDR_273_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class EDR_273_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda data: (
                data.tags.get(GameTag.CHOOSE_ONE)
                and data.card_class not in (CardClass.DRUID, CardClass.NEUTRAL)
            ),
        )
        return source.game.queue_actions(source, [EDR_273_Choice(player, cards)])


class EDR_843_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if source.progress >= source.progress_total:
            return source.game.queue_actions(
                source,
                [
                    ForceDraw(RANDOM(FRIENDLY_DECK + SPELL)),
                    ForceDraw(RANDOM(FRIENDLY_DECK + MINION)),
                ],
            )
        return source.game.queue_actions(
            source, [Choice(player, ["EDR_843a", "EDR_843b"]).then(Battlecry(Choice.CARD, None))]
        )


class EDR_845_Imbue(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = getattr(player, "_edr_847p_amount", 0) + 1
        player._edr_847p_amount = amount
        if player.hero.power.id != "EDR_847p":
            return source.game.queue_actions(source, [Summon(player, "EDR_847p")])


class EDR_845_Start(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if getattr(player, "_edr_845_active", False):
            return
        for card in player.starting_deck:
            data = db[card]
            if (
                data.type == CardType.SPELL
                and getattr(data, "spell_school", None) != SpellSchool.NATURE
            ):
                return
        player._edr_845_active = True
        player._edr_845_spell_count = 0
        return source.game.queue_actions(source, [EDR_845_Imbue(player)])


class EDR_845_CountSpell(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if not getattr(player, "_edr_845_active", False):
            return
        player._edr_845_spell_count = getattr(player, "_edr_845_spell_count", 0) + 1
        if player._edr_845_spell_count >= 3:
            player._edr_845_spell_count = 0
            return source.game.queue_actions(source, [EDR_845_Imbue(player)])


class EDR_847p_SummonGolem(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = getattr(player, "_edr_847p_amount", 1)
        golem = player.card("EDR_847pt2", source=source)
        return source.game.queue_actions(
            source,
            [
                Buff(
                    golem,
                    "EDR_847pe",
                    atk=amount - golem.atk,
                    max_health=amount - golem.max_health,
                ),
                Summon(player, golem),
            ],
        )


class FIR_906_Overheat(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = [Buff(FRIENDLY_MINIONS, "FIR_906e")]
        nature_spells = [card for card in player.hand if _is_nature_spell(card)]
        if nature_spells:
            actions.append(Discard(source.game.random.choice(nature_spells)))
            actions.append(Buff(FRIENDLY_MINIONS, "FIR_906e"))
        return source.game.queue_actions(source, actions)


class FIR_907_Activate(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, location):
        player = location.controller
        amount = getattr(location, "_fir_907_amount", 1)
        location._fir_907_amount = amount + 1
        return source.game.queue_actions(
            source,
            [
                Summon(player, RandomMinion(cost=amount)),
                GainArmor(player.hero, amount),
                Draw(player) * amount,
                FillMana(player, amount),
            ],
        )


class FIR_908_Battlecry(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if player.hero.power.activations_this_turn <= 0:
            return
        minions = [minion for minion in player.field if minion is not source]
        if not minions:
            return
        target = source.game.random.choice(minions)
        return source.game.queue_actions(source, [Buff(target, "FIR_908e")])


##
# Minions


class EDR_060:
    """Ward of Earth"""

    play = GainArmor(FRIENDLY_HERO, 5), Summon(CONTROLLER, RandomMinion(cost=5)).then(
        Taunt(Summon.CARD)
    )


class EDR_060e:
    """Ward of Earth"""

    taunt = True


class EDR_209:
    """Forest Lord Cenarius"""

    play = EDR_209_StartChoice(CONTROLLER, 3)


class EDR_209a:
    """Growth of Dreams"""

    play = Buff(FRIENDLY_MINIONS, "EDR_209e2") * 2


class EDR_209b:
    """Ancients of the Dream"""

    play = Give(CONTROLLER, "EDR_209t5") * 2


class EDR_209e2:
    """Guidance of the Forest"""

    tags = {GameTag.ATK: 1, GameTag.HEALTH: 3}


class EDR_209t5:
    """Ancient"""

    taunt = True


class EDR_270:
    """Horn of Plenty"""

    play = EDR_270_Discover(CONTROLLER)


class EDR_270e:
    """Horn of Plenty"""

    tags = {GameTag.COST: -2}


class EDR_271:
    """Grove Shaper"""

    events = Play(CONTROLLER, NATURE_SPELL).after(
        EDR_271_SummonTreant(CONTROLLER, Play.CARD)
    )


class EDR_271t:
    """Treant of Life"""

    tags = {GameTag.DEATHRATTLE: True}
    deathrattle = EDR_271_GiveSpell(SELF)


class EDR_272:
    """Evergreen Stag"""

    tags = {
        GameTag.ELUSIVE: True,
        GameTag.LIFESTEAL: True,
        GameTag.TAUNT: True,
    }


class EDR_273:
    """Symbiosis"""

    play = EDR_273_Discover(CONTROLLER)


class EDR_843:
    """Reforestation"""

    progress_total = 3
    play = EDR_843_Play(CONTROLLER)

    class Hand:
        events = OWN_TURN_BEGIN.on(AddProgress(SELF, SELF))


class EDR_843a:
    """Aid of the Forest"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + SPELL))


class EDR_843b:
    """Fertilize"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + MINION))


class EDR_843t1:
    """Reforestation"""

    pass


class EDR_845:
    """Hamuul Runetotem"""

    class Deck:
        events = GameStart().on(EDR_845_Start(CONTROLLER)), Play(CONTROLLER, SPELL).after(
            EDR_845_CountSpell(CONTROLLER)
        )

    class Hand:
        events = GameStart().on(EDR_845_Start(CONTROLLER)), Play(CONTROLLER, SPELL).after(
            EDR_845_CountSpell(CONTROLLER)
        )


class EDR_845e1:
    """Runetotem's Favor"""

    pass


class EDR_847:
    """Dreambound Disciple"""

    play = Buff(FRIENDLY_HERO_POWER, "EDR_847e")
    deathrattle = Buff(FRIENDLY_HERO_POWER, "EDR_847e")


class EDR_847e:
    """Dreambound"""

    def apply(self, target):
        self._used_at = target.controller.times_hero_power_used_this_game

    cost = _edr_847_cost
    events = OWN_TURN_END.on(Destroy(SELF))


class EDR_847p:
    """Blessing of the Golem"""

    activate = EDR_847p_SummonGolem(CONTROLLER)


class EDR_847pt2:
    """Plant Golem"""

    pass


class EDR_847pt3:
    """Plant Golem"""

    pass


class EDR_847pt4:
    """Plant Golem"""

    pass


class EDR_848:
    """Photosynthesis"""

    play = Heal(FRIENDLY_HERO, 6), Give(CONTROLLER, RandomSpell(card_class=CardClass.DRUID)) * 3


##
# Spells


class FIR_906:
    """Overheat"""

    play = FIR_906_Overheat(CONTROLLER)


class FIR_907:
    """Amirdrassil"""

    activate = FIR_907_Activate(SELF)


class FIR_908:
    """Charred Chameleon"""

    play = FIR_908_Battlecry(CONTROLLER)


@custom_card
class EDR_847pe:
    tags = {
        GameTag.CARDNAME: "Blessing of the Golem",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


class FIR_906e:
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


@custom_card
class FIR_908e:
    tags = {
        GameTag.CARDNAME: "Charred Chameleon",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 1,
        GameTag.HEALTH: 2,
        GameTag.RUSH: True,
    }
