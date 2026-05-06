from ..utils import *
from ...actions import _after_discover_choice


TLC_452_ABILITIES = [
    "TLC_452t1",
    "TLC_452t2",
    "TLC_452t3",
    "TLC_452t4",
    "TLC_452t5",
    "TLC_452t6",
    "TLC_452t7",
    "TLC_452t8",
    "TLC_452t9",
    "TLC_452t13",
    "TLC_452t14",
    "TLC_452t15",
    "TLC_452t16",
    "TLC_452t17",
    "TLC_452t18",
    "TLC_452t19",
    "TLC_452t20",
    "TLC_452t21",
    "TLC_452t22",
    "TLC_452t23",
    "TLC_452t24",
    "TLC_452t26",
    "TLC_452t27",
    "TLC_452t28",
    "TLC_452t29",
    "TLC_452t30",
    "TLC_452t31",
    "TLC_452t32",
    "TLC_452t33",
    "TLC_452t34",
    "TLC_452t35",
]


def _spell_school(card):
    return card.tags.get(GameTag.SPELL_SCHOOL) or getattr(
        getattr(card, "data", None), "spell_school", None
    )


def _kindred(card):
    for played in getattr(card.controller, "cards_played_last_turn", []):
        if card.type == CardType.MINION and played.type == CardType.MINION:
            if set(card.races).intersection(played.races):
                return True
        spell_school = _spell_school(card)
        if spell_school and _spell_school(played) == spell_school:
            return True
    return False


def _discovered_this_turn(player):
    return getattr(player, "_tlc_discovered_turn", None) == player.game.turn


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
    return cards[:3]


def _set_stats_action(target, buff_id, atk, health):
    return Buff(
        target, buff_id, atk=atk - target.atk, max_health=health - target.max_health
    )


def _random_or_target(source, target, candidates):
    if target in candidates:
        return target
    if candidates:
        return source.game.random.choice(candidates)
    return None


def _roll_osk(card):
    card._tlc_452_ability = card.game.random.choice(TLC_452_ABILITIES)
    return card._tlc_452_ability


class TLC_MageDiscoverChoice(Choice):
    def actions_for(self, card):
        return [Give(self.player, card)]

    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, self.actions_for(card))
        _after_discover_choice(self, card, self.actions_for)
        self.trigger_choice_callback()


class DINO_414_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        copy = ExactCopy(TARGET).copy(self.source, card)
        self.source.game.queue_actions(self.source, [Morph(self.transform_target, copy)])
        self.trigger_choice_callback()


class DINO_414_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        candidates = [minion for minion in source.game.board if minion is not target]
        choice = DINO_414_Choice(source.controller, candidates)
        choice.transform_target = target
        return source.game.queue_actions(source, [choice])


class DINO_429_SetStats(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        return source.game.queue_actions(
            source,
            [
                Buff(
                    target,
                    "DINO_429e",
                    atk=1 - target.atk,
                    max_health=1 - target.max_health,
                )
            ],
        )


class TLC_226_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = [ForceDraw(RANDOM(FRIENDLY_DECK + SPELL))]
        if _kindred(source):
            actions.append(Summon(player, ExactCopy(SELF)))
        return source.game.queue_actions(source, actions)


class TLC_334_Choice(TLC_MageDiscoverChoice):
    def actions_for(self, card):
        return [Buff(card, "TLC_334e"), Give(self.player, card)]


class TLC_334_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda card: card.type == CardType.SPELL and card.cost >= 8,
        )
        return source.game.queue_actions(source, [TLC_334_Choice(player, cards)])


class TLC_461_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(source, lambda card: card.cost == player.mana)
        return source.game.queue_actions(source, [TLC_MageDiscoverChoice(player, cards)])


class TLC_462_Summon(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cost = 4 if _discovered_this_turn(player) else 2
        return source.game.queue_actions(source, [Summon(player, RandomMinion(cost=cost))])


class TLC_452_Roll(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if target.zone == Zone.HAND and target.id == "TLC_452":
            _roll_osk(target)


class TLC_452_DrawMinions(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for card in [card for card in player.deck if card.type == CardType.MINION][:2]:
            actions.append(ForceDraw(card))
            actions.append(_set_stats_action(card, "TLC_452t18e", 2, 2))
            actions.append(Buff(card, "TLC_452t18e2"))
        return source.game.queue_actions(source, actions)


class TLC_452_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        ability = getattr(source, "_tlc_452_ability", None) or _roll_osk(source)
        player = source.controller
        enemy_minions = list(player.opponent.field)
        all_minions = list(source.game.board)
        enemy_target = _random_or_target(source, target, enemy_minions)
        any_minion = _random_or_target(
            source, target, [m for m in all_minions if m is not source]
        )

        if ability == "TLC_452t1" and enemy_target:
            health = enemy_target.health
            return source.game.queue_actions(
                source,
                [
                    Destroy(enemy_target),
                    Buff(source, "TLC_452t1e", health=health),
                    Heal(player.hero, health),
                ],
            )
        if ability in ("TLC_452t13", "TLC_452t26") and any_minion:
            return source.game.queue_actions(
                source, [Hit(any_minion, 5 if ability == "TLC_452t13" else 20)]
            )
        if ability == "TLC_452t14":
            return source.game.queue_actions(
                source, [CastSpell(RandomSpell(secret=True, card_class=CardClass.MAGE))]
            )
        if ability == "TLC_452t15":
            return source.game.queue_actions(source, [Buff(ENEMY_HAND, "TLC_452t15e")])
        if ability == "TLC_452t16":
            return source.game.queue_actions(
                source,
                [_set_stats_action(minion, "TLC_452t16e", 2, 2) for minion in enemy_minions],
            )
        if ability == "TLC_452t17":
            return source.game.queue_actions(source, [Buff(FRIENDLY_MINIONS - SELF, "TLC_452t17e")])
        if ability == "TLC_452t18":
            return source.game.queue_actions(source, [TLC_452_DrawMinions(player)])
        if ability == "TLC_452t19" and any_minion:
            return source.game.queue_actions(
                source,
                [Summon(player, Buff(ExactCopy(TARGET).copy(source, any_minion), "TLC_452t19e"))],
            )
        if ability == "TLC_452t20":
            return source.game.queue_actions(
                source,
                [Summon(player, RandomMinion(cost=6)).then(Buff(Summon.CARD, "TLC_452t20e"))],
            )
        if ability == "TLC_452t21" and enemy_target:
            others = [minion for minion in enemy_minions if minion is not enemy_target]
            actions = [Remove(enemy_target)]
            if others:
                actions.append(Remove(source.game.random.choice(others)))
            return source.game.queue_actions(source, actions)
        if ability == "TLC_452t22":
            return source.game.queue_actions(source, [Buff(source, "TLC_452t22e"), Hit(RANDOM_ENEMY_CHARACTER, 4)])
        if ability == "TLC_452t23":
            return source.game.queue_actions(source, [Buff(source, "TLC_452t23e"), Draw(player)])
        if ability == "TLC_452t24":
            return source.game.queue_actions(source, [Buff(source, "TLC_452t24e")])
        if ability == "TLC_452t27":
            return source.game.queue_actions(source, [Hit(ENEMY_CHARACTERS, 3), Heal(FRIENDLY_CHARACTERS, 6)])
        if ability == "TLC_452t28":
            return source.game.queue_actions(source, [Summon(player, "EX1_301") * 2])
        if ability == "TLC_452t29":
            return source.game.queue_actions(source, [Remove(ALL_MINIONS - SELF)])
        if ability == "TLC_452t3":
            return source.game.queue_actions(source, [Summon(player, "TLC_452t3t") * 2])
        if ability == "TLC_452t30":
            return source.game.queue_actions(source, [Buff(source, "TLC_452t30e"), GainArmor(player.hero, 5)])
        if ability == "TLC_452t31":
            return source.game.queue_actions(source, [Buff(source, "TLC_452t31e"), Buff(player.hero, "TLC_452t31e")])
        if ability == "TLC_452t32":
            return source.game.queue_actions(source, [Buff(source, "TLC_452t32e"), ForceDraw(RANDOM(FRIENDLY_DECK + WEAPON))])
        if ability == "TLC_452t33":
            return source.game.queue_actions(
                source,
                [Give(player, "TLC_452t33t") * (player.max_hand_size - len(player.hand))],
            )
        if ability == "TLC_452t35" and enemy_target:
            return source.game.queue_actions(source, [Steal(enemy_target)])
        if ability == "TLC_452t4":
            cards = _collectible_cards(
                source,
                lambda card: card.type == CardType.MINION
                and card.tags.get(GameTag.DEATHRATTLE),
            )
            choice = TLC_MageDiscoverChoice(player, cards)
            choice.actions_for = lambda card: [Buff(card, "TLC_452t4e"), Give(player, card)]
            return source.game.queue_actions(source, [choice])
        if ability == "TLC_452t5":
            return source.game.queue_actions(source, [Buff(FRIENDLY_HAND + MINION, "TLC_452t5e")])
        if ability == "TLC_452t6":
            return source.game.queue_actions(source, [Summon(player, "TTN_862t3t") * 4])
        if ability == "TLC_452t7":
            return source.game.queue_actions(source, [Draw(player) * (player.max_hand_size - len(player.hand))])
        if ability == "TLC_452t8":
            return source.game.queue_actions(source, [FullHeal(player.hero)])
        if ability == "TLC_452t9":
            player.used_mana = 0


class DINO_409:
    """Techysaurus"""

    cost_mod = -Count(CARDS_PLAYED_THIS_GAME - STARTING_DECK)


class DINO_414:
    """Tribute Dance"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = DINO_414_Play(TARGET)


class DINO_429:
    """Sheep Mask"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = DINO_429_SetStats(TARGET)


class DINO_429e:
    tags = {GameTag.DEATHRATTLE: True}
    deathrattle = Hit(ALL_MINIONS, 2)


class TLC_220:
    """Windswept Pageturner"""

    events = Summon(CONTROLLER, ELEMENTAL).after(Hit(RANDOM_ENEMY_CHARACTER, 3))


class TLC_226:
    """Conjured Bookkeeper"""

    deathrattle = TLC_226_Deathrattle(CONTROLLER)


class TLC_334:
    """Relic of Kings"""

    play = TLC_334_Discover(CONTROLLER)


@custom_card
class TLC_334e:
    tags = {
        GameTag.CARDNAME: "Relic of Kings",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    cost = SET(1)


class TLC_364:
    """Story of the Waygate"""

    play = Buff(FRIENDLY_HAND - STARTING_DECK, "TLC_364e")


@custom_card
class TLC_364e:
    tags = {
        GameTag.CARDNAME: "Story of the Waygate",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


class TLC_365:
    """Storage Scuffle"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    cost = lambda self, cost: 0 if _discovered_this_turn(self.controller) else cost
    play = Hit(TARGET, 3)


class TLC_452:
    """Titanographer Osk"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    events = OWN_TURN_BEGIN.on(TLC_452_Roll(FRIENDLY_HAND + ID("TLC_452")))
    play = TLC_452_Play(TARGET)


class TLC_460:
    """The Forbidden Sequence"""

    progress_total = 7
    reward = Give(CONTROLLER, "TLC_460t")


class TLC_460t:
    """The Origin Stone"""

    pass


class TLC_461:
    """Scrappy Scavenger"""

    play = TLC_461_Discover(CONTROLLER)


class TLC_462:
    """Unearthed Artifacts"""

    play = TLC_462_Summon(CONTROLLER)


class TLC_483:
    """Vault Breaker"""

    pass


@custom_card
class TLC_483e:
    tags = {
        GameTag.CARDNAME: "Vault Broken",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


TLC_452t1e = buff(health=0)
TLC_452t2e = buff(cost=-3, spellpower=3)
TLC_452t4e = buff(cost=-3)
TLC_452t5e = buff(cost=-2)
TLC_452t15e = buff(cost=1)
TLC_452t16e = buff()
TLC_452t17e = buff(2, 2)
TLC_452t18e = buff()
TLC_452t19e = buff(2, 2)
TLC_452t20e = buff(taunt=True, lifesteal=True)
TLC_452t22e = buff(2, 1)
TLC_452t23e = buff(1, 2)
TLC_452t24e = buff(health=3, elusive=True)
TLC_452t30e = buff(health=5)
TLC_452t31e = buff(atk=5)
TLC_452t32e = buff(2, 2)


@custom_card
class TLC_452t18e2:
    tags = {
        GameTag.CARDNAME: "Titanographer Osk Cost",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    cost = SET(2)


@custom_card
class TLC_452t3t:
    tags = {
        GameTag.CARDNAME: "Titanographer's Undead",
        GameTag.CARDTYPE: CardType.MINION,
        GameTag.COST: 3,
        GameTag.ATK: 3,
        GameTag.HEALTH: 3,
        GameTag.CARDRACE: Race.UNDEAD,
        GameTag.TAUNT: True,
        GameTag.REBORN: True,
    }


@custom_card
class TLC_452t33t:
    tags = {
        GameTag.CARDNAME: "Chaotic Tendril",
        GameTag.CARDTYPE: CardType.MINION,
        GameTag.COST: 1,
        GameTag.ATK: 1,
        GameTag.HEALTH: 1,
    }
