from ..utils import *


KINDRED_CARD_IDS = {
    "DINO_138",
    "DINO_404",
    "DINO_413",
    "DINO_435",
    "TLC_107",
    "TLC_223",
    "TLC_226",
    "TLC_236",
    "TLC_243",
    "TLC_366",
    "TLC_428",
    "TLC_429",
    "TLC_432",
    "TLC_440",
    "TLC_447",
    "TLC_454",
    "TLC_463",
    "TLC_482",
    "TLC_519",
    "TLC_600",
    "TLC_815",
    "TLC_816",
    "TLC_825",
    "TLC_829",
    "TLC_903",
}


def _spell_school(card):
    return card.tags.get(GameTag.SPELL_SCHOOL) or getattr(
        getattr(card, "data", None), "spell_school", None
    )


def _card_races(card):
    races = set(getattr(card, "races", []) or [])
    races.update(getattr(getattr(card, "data", None), "races", []) or [])
    return races


def _kindred(card):
    school = _spell_school(card)
    for played in getattr(card.controller, "cards_played_last_turn", []):
        if card.type == CardType.MINION and played.type == CardType.MINION:
            if _card_races(card).intersection(_card_races(played)):
                return True
        if school and _spell_school(played) == school:
            return True
    return False


def _kindred_repeats(card):
    if not _kindred(card):
        return 0
    player = card.controller
    repeats = 1 + getattr(player, "_tlc_251_next_kindred_bonus", 0)
    if getattr(player, "_tlc_251_next_kindred_bonus", 0):
        player._tlc_251_next_kindred_bonus = 0
    return repeats


def _collectible_cards(source, predicate):
    cards = []
    for card_id, data in db.items():
        if not data.collectible or (source.game.is_standard and not data.is_standard):
            continue
        card = source.controller.card(card_id, source=source)
        if predicate(card):
            cards.append(card)
    if len(cards) < 3 and source.game.is_standard:
        for card_id, data in db.items():
            if not data.collectible or data.is_standard:
                continue
            card = source.controller.card(card_id, source=source)
            if predicate(card):
                cards.append(card)
    source.game.random.shuffle(cards)
    return cards


class TLC_NeutralSetStats(TargetedAction):
    TARGET = ActionArg()
    ATK = IntArg()
    HEALTH = IntArg()

    def do(self, source, target, atk, health):
        return source.game.queue_actions(
            source,
            [
                Buff(
                    target,
                    "TLC_NEUTRAL_SET_STATS",
                    atk=atk - target.atk,
                    max_health=health - target.max_health,
                )
            ],
        )


@custom_card
class TLC_NEUTRAL_SET_STATS:
    tags = {
        GameTag.CARDNAME: "Set Stats",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


class DINO_410:
    """Khelos' Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_410t2")


class DINO_410t2:
    """Khelos' Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_410t3")


class DINO_410t3:
    """Khelos' Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_410t4")


class DINO_410t4:
    """Khelos' Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_410t5")


class DINO_410t5:
    """Khelos' Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_410t")


class DINO_411:
    """Sacred Eggbearer"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + MINION + (ATK == 0)))


class DINO_419:
    """Fodder Helper"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_TARGET_WITH_RACE: Race.BEAST,
    }
    play = Buff(TARGET, "DINO_419e"), GiveRush(TARGET)


DINO_419e = buff(2, 2)


class TLC_101:
    """Undercover Cultist"""

    enrage = Refresh(SELF, buff="TLC_101e")


TLC_101e = buff(atk=3)


class TLC_244:
    """Curious Explorer"""

    deathrattle = Buff(RANDOM(ENEMY_HAND + MINION), "TLC_244e")


@custom_card
class TLC_244e:
    tags = {
        GameTag.CARDNAME: "Explored",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -2,
    }


class TLC_249:
    """Blazing Accretion"""

    deathrattle = Hit(RANDOM_ENEMY_CHARACTER, 1) * 2


class DINO_430_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source._dino_430_beast_id = card.id
        self.source.game.queue_actions(
            self.source,
            [
                Buff(
                    self.source,
                    "DINO_430e",
                    atk=card.atk - self.source.atk,
                    max_health=card.max_health - self.source.max_health,
                )
            ],
        )
        self.trigger_choice_callback()


class DINO_430_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_cards(
            source,
            lambda card: card.type == CardType.MINION
            and Race.BEAST in _card_races(card)
            and card.rarity == Rarity.LEGENDARY,
        )
        cards.sort(key=lambda card: (card.id != "TLC_480", card.id))
        return source.game.queue_actions(source, [DINO_430_Choice(player, cards[:3])])


class DINO_430_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        beast_id = getattr(source, "_dino_430_beast_id", None)
        if beast_id:
            return source.game.queue_actions(source, [Summon(player, beast_id)])


class DINO_430:
    """Beast Speaker Taka"""

    play = DINO_430_Play(CONTROLLER)
    deathrattle = DINO_430_Deathrattle(CONTROLLER)


class TLC_107_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if _kindred(source):
            return source.game.queue_actions(source, [GiveRush(source)])


class TLC_107:
    """Stormbrewer"""

    play = TLC_107_Play(CONTROLLER)
    events = Attack(SELF).on(Hit(Attack.DEFENDER, 3))


class TLC_109_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class TLC_109_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if not player.deck:
            return
        top = player.deck[-1]
        cards = _collectible_cards(
            source,
            lambda card: card.id != top.id and card.rarity == top.rarity,
        )
        return source.game.queue_actions(
            source, [Mill(player), TLC_109_Choice(player, cards[:3])]
        )


class TLC_109:
    """Relic Miner"""

    play = TLC_109_Play(CONTROLLER)


class TLC_110_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        deck_minions = [card for card in player.deck if card.type == CardType.MINION]
        if not deck_minions:
            return
        common = None
        for card in deck_minions:
            races = _card_races(card) - {Race.INVALID}
            if not races:
                return
            common = set(races) if common is None else common.intersection(races)
        if not common:
            return
        minions = [
            card
            for card in list(player.field) + list(player.hand) + list(player.deck)
            if card is not source and card.type == CardType.MINION
        ]
        return source.game.queue_actions(
            source, [Buff(card, "TLC_110e", atk=2, max_health=2) for card in minions]
        )


class TLC_110:
    """City Chief Esho"""

    play = TLC_110_Play(CONTROLLER)


class TLC_100_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        costs = {card.cost for card in player.deck}
        if len(costs) >= 10:
            return source.game.queue_actions(source, [Give(player, "TLC_100t1")])


class TLC_100:
    """Elise the Navigator"""

    play = TLC_100_Play(CONTROLLER)


class TLC_100t1:
    """Un'Goro Jungle"""

    pass


class TLC_102_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        kindred_cards = [card for card in player.deck if card.id in KINDRED_CARD_IDS]
        if kindred_cards:
            kindred = kindred_cards[-1]
            actions.append(ForceDraw(kindred))
            races = _card_races(kindred) - {Race.INVALID}
            school = _spell_school(kindred)
            enablers = [
                card
                for card in player.deck
                if card is not kindred
                and (
                    (card.type == CardType.MINION and races.intersection(_card_races(card)))
                    or (school and _spell_school(card) == school)
                )
            ]
            if enablers:
                actions.append(ForceDraw(enablers[-1]))
        return source.game.queue_actions(source, actions)


class TLC_102:
    """Torga"""

    play = TLC_102_Play(CONTROLLER)


class TLC_106_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        deathrattle_minions = [
            card
            for card in player.graveyard
            if card.type == CardType.MINION and card.has_deathrattle
        ][-5:]
        for minion in deathrattle_minions:
            for deathrattle in minion.deathrattles:
                if isinstance(deathrattle, tuple):
                    actions.extend(deathrattle)
                else:
                    actions.append(deathrattle)
        return source.game.queue_actions(source, actions)


class TLC_106:
    """Endbringer Umbra"""

    play = TLC_106_Play(CONTROLLER)


class DINO_435_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = [Summon(player, ExactCopy(SELF).copy(source, source))]
        return source.game.queue_actions(source, actions * _kindred_repeats(source))


class DINO_435:
    """Crater Experiment"""

    play = DINO_435_Play(CONTROLLER)


class TLC_NeutralTextChoice(Choice):
    def get_target_args(self, source, target):
        cards = self._args[1]
        return [cards]


class TLC_242_Choice(TLC_NeutralTextChoice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        actions = {
            "taunt": [Buff(self.source, "TLC_NEUTRAL_242e1")],
            "poisonous": [Buff(self.source, "TLC_NEUTRAL_242e2")],
            "stats": [Buff(self.source, "TLC_NEUTRAL_242e3")],
        }[card]
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class TLC_242_StartChoice(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [TLC_242_Choice(player, ["taunt", "poisonous", "stats"])]
        )


class TLC_242:
    """Ancient Stegodon"""

    play = TLC_242_StartChoice(CONTROLLER)


@custom_card
class TLC_NEUTRAL_242e1:
    tags = {
        GameTag.CARDNAME: "Ancient Hide",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.TAUNT: True,
    }


@custom_card
class TLC_NEUTRAL_242e2:
    tags = {
        GameTag.CARDNAME: "Ancient Venom",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.POISONOUS: True,
    }


@custom_card
class TLC_NEUTRAL_242e3:
    tags = {
        GameTag.CARDNAME: "Ancient Strength",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 1,
        GameTag.HEALTH: 1,
    }


class TLC_243_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if _kindred(source):
            return source.game.queue_actions(source, [Buff(source, "TLC_243e")])


class TLC_243:
    """Doommaiden"""

    play = TLC_243_Play(CONTROLLER)


@custom_card
class TLC_243e:
    tags = {
        GameTag.CARDNAME: "Doomed",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.IMMUNE: True,
    }
    events = OWN_TURN_END.on(Destroy(SELF))


class TLC_245_AddPlantDeathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        target.tags[GameTag.DEATHRATTLE] = True
        target.additional_deathrattles.append(
            (Summon(CONTROLLER, "TLC_245t"), Summon(CONTROLLER, "TLC_245t"))
        )


class TLC_245_Choice(TLC_NeutralTextChoice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        actions = {
            "attack": [Buff(self.source, "TLC_NEUTRAL_245e1")],
            "divine_shield": [GiveDivineShield(self.source)],
            "plants": [TLC_245_AddPlantDeathrattle(self.source)],
        }[card]
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class TLC_245_StartChoice(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [TLC_245_Choice(player, ["attack", "divine_shield", "plants"])]
        )


class TLC_245:
    """Ancient Raptor"""

    play = TLC_245_StartChoice(CONTROLLER)


@custom_card
class TLC_NEUTRAL_245e1:
    tags = {
        GameTag.CARDNAME: "Ancient Claws",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 3,
    }


@custom_card
class TLC_245t:
    tags = {
        GameTag.CARDNAME: "Plant",
        GameTag.CARDTYPE: CardType.MINION,
        GameTag.COST: 1,
        GameTag.ATK: 1,
        GameTag.HEALTH: 1,
    }


class TLC_246_Choice(TLC_NeutralTextChoice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        actions = {
            "elusive": [Buff(self.source, "TLC_NEUTRAL_246e1")],
            "windfury": [Buff(self.source, "TLC_NEUTRAL_246e2")],
            "stealth": [Stealth(self.source), Buff(self.source, "TLC_NEUTRAL_246e3")],
        }[card]
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class TLC_246_StartChoice(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [TLC_246_Choice(player, ["elusive", "windfury", "stealth"])]
        )


class TLC_246:
    """Ancient Pterrordax"""

    play = TLC_246_StartChoice(CONTROLLER)


@custom_card
class TLC_NEUTRAL_246e1:
    tags = {
        GameTag.CARDNAME: "Ancient Scales",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.CANT_BE_TARGETED_BY_SPELLS: True,
        GameTag.CANT_BE_TARGETED_BY_HERO_POWERS: True,
    }


@custom_card
class TLC_NEUTRAL_246e2:
    tags = {
        GameTag.CARDNAME: "Ancient Wings",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.WINDFURY: True,
    }


@custom_card
class TLC_NEUTRAL_246e3:
    tags = {
        GameTag.CARDNAME: "Ancient Camouflage",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = OWN_TURN_BEGIN.on(Unstealth(OWNER), Destroy(SELF))


class TLC_247:
    """Primal Sabretooth"""

    events = Attack(SELF, ALL_MINIONS).after(
        Dead(Attack.DEFENDER) & Give(CONTROLLER, Copy(Attack.DEFENDER))
    )


class TLC_250_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        player.opponent._tlc_250_no_hero_heal = True
        return source.game.queue_actions(source, [Buff(player, "TLC_250e")])


class TLC_250_Clear(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        player.opponent._tlc_250_no_hero_heal = False


class TLC_250:
    """Crater Gator"""

    play = TLC_250_Play(CONTROLLER)


class TLC_250e:
    events = OWN_TURN_BEGIN.on(TLC_250_Clear(OWNER), Destroy(SELF))


class TLC_252_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        bone = source.controller.card("TLC_829t", source=source)
        bone._tlc_bone_atk = target.atk
        bone._tlc_bone_health = target.max_health
        return source.game.queue_actions(
            source, [Destroy(target), Give(source.controller, bone)]
        )


class TLC_252:
    """Dissolving Ooze"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_252_Play(TARGET)


class TLC_253_Begin(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, ogre):
        if source.game.random.choice([True, False]):
            return source.game.queue_actions(source, [Awaken(ogre)])
        return source.game.queue_actions(source, [Buff(ogre, "TLC_253e2")])


class TLC_253:
    """Petrified Ogre"""

    tags = {GameTag.DORMANT: True}
    dormant_turns = 999
    dormant_events = OWN_TURN_BEGIN.on(TLC_253_Begin(SELF))


TLC_253e2 = buff(2, 2)


class TLC_251:
    """Misty Mountain Hopster"""

    play = Buff(CONTROLLER, "TLC_251e")


class TLC_251e:
    def apply(self, player):
        player._tlc_251_next_kindred_bonus = (
            getattr(player, "_tlc_251_next_kindred_bonus", 0) + 1
        )


class TLC_254_EndTurn(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        seen_races = set()
        actions = []
        for minion in player.field:
            if minion is source:
                continue
            race = next(
                (race for race in _card_races(minion) if race not in seen_races),
                None,
            )
            if not race:
                continue
            seen_races.add(race)
            actions.append(Buff(minion, "TLC_NEUTRAL_254e"))
        return source.game.queue_actions(source, actions)


class TLC_254:
    """Storyteller"""

    events = OWN_TURN_END.on(TLC_254_EndTurn(CONTROLLER))


@custom_card
class TLC_NEUTRAL_254e:
    tags = {
        GameTag.CARDNAME: "Typecast",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 1,
        GameTag.HEALTH: 1,
    }


class TLC_256:
    """Marshland Thresher"""

    events = Play(CONTROLLER, SPELL).after(GiveDivineShield(SELF))


class TLC_255_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = max(0, player.opponent.max_mana - player.max_mana)
        return source.game.queue_actions(source, [GainEmptyMana(player, amount)])


class TLC_255:
    """Crystal Tender"""

    play = TLC_255_Play(CONTROLLER)


class TLC_427:
    """Rockskipper"""

    play = Give(CONTROLLER, "TLC_427t")


@custom_card
class TLC_427t:
    tags = {
        GameTag.CARDNAME: "Rock",
        GameTag.CARDTYPE: CardType.SPELL,
        GameTag.COST: 1,
    }
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 3)


class TLC_480:
    """Krog, Crater King"""

    events = OWN_TURN_END.on(TLC_NeutralSetStats(ENEMY_MINIONS, 1, 1))


class TLC_603_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if player.deck:
            source._tlc_603_drawn_card = player.deck[-1]
        return source.game.queue_actions(source, [Draw(player)])


class TLC_603_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        card = getattr(source, "_tlc_603_drawn_card", None)
        if card and card.zone == Zone.HAND:
            return source.game.queue_actions(source, [Discard(card)])


class TLC_603:
    """Platysaur"""

    play = TLC_603_Play(CONTROLLER)
    deathrattle = TLC_603_Deathrattle(CONTROLLER)


class TLC_465_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    bonuses = ("rush", "taunt", "divine_shield", "windfury", "lifesteal", "poisonous")

    def do(self, source, player):
        candidates = [minion for minion in player.field if minion is not source]
        if not candidates:
            return
        target = source.game.random.choice(candidates)
        bonus = source.game.random.choice(self.bonuses)
        actions = []
        if bonus == "rush":
            actions.append(GiveRush(target))
        elif bonus == "taunt":
            actions.append(Taunt(target))
        elif bonus == "divine_shield":
            actions.append(GiveDivineShield(target))
        elif bonus == "windfury":
            actions.append(GiveWindfury(target))
        elif bonus == "lifesteal":
            actions.append(GiveLifesteal(target))
        elif bonus == "poisonous":
            actions.append(GivePoisonous(target))
        target.tags[GameTag.DEATHRATTLE] = True
        target.additional_deathrattles.append((TLC_465_Deathrattle(CONTROLLER),))
        return source.game.queue_actions(source, actions)


class TLC_465:
    """Stranglevine"""

    tags = {GameTag.DEATHRATTLE: True}
    deathrattle = TLC_465_Deathrattle(CONTROLLER)


class TLC_468:
    """Blob of Tar"""

    deathrattle = Summon(CONTROLLER, "TLC_468t1"), Summon(CONTROLLER, "TLC_468t2")


class TLC_468t1:
    """Thin Blob"""

    pass


class TLC_468t2:
    """Thick Blob"""

    pass


class TLC_429_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for _ in range(_kindred_repeats(source)):
            actions.extend(
                [
                    Summon(player, "TLC_429t").then(GiveRush(Summon.CARD)),
                    Summon(player, "TLC_429t").then(GiveRush(Summon.CARD)),
                ]
            )
        return source.game.queue_actions(source, actions)


class TLC_429:
    """Steamfin Thief"""

    play = TLC_429_Play(CONTROLLER)


class TLC_429t:
    """Tadpole"""

    pass


class TLC_454_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        enemies = list(player.opponent.field)
        if not enemies:
            return
        if _kindred_repeats(source):
            attack = max(minion.atk for minion in enemies)
        else:
            attack = min(minion.atk for minion in enemies)
        target = source.game.random.choice(
            [minion for minion in enemies if minion.atk == attack]
        )
        return source.game.queue_actions(source, [Destroy(target)])


class TLC_454:
    """Scalhide Kodo"""

    play = TLC_454_Play(CONTROLLER)


class TLC_829_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = [Destroy(target)]
        if _kindred(source):
            actions.append(
                Buff(source, "TLC_829te2", atk=target.atk, max_health=target.max_health)
            )
        return source.game.queue_actions(source, actions)


class TLC_829:
    """Ravenous Devilsaur"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_829_Play(TARGET)


class TLC_829t_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        return source.game.queue_actions(
            source,
            [
                Buff(
                    target,
                    "TLC_829te",
                    atk=getattr(source, "_tlc_bone_atk", 0),
                    max_health=getattr(source, "_tlc_bone_health", 0),
                )
            ],
        )


class TLC_829t:
    """Bone"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_829t_Play(TARGET)


class TLC_831_StealHealth(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, hatchling):
        others = [minion for minion in hatchling.game.board if minion is not hatchling]
        actions = []
        for minion in others:
            actions.append(Buff(minion, "TLC_831e", max_health=-1))
        if others:
            actions.append(Buff(hatchling, "TLC_831e2", max_health=len(others)))
        return source.game.queue_actions(source, actions)


class TLC_831:
    """Pterrordax Egg"""

    deathrattle = Summon(CONTROLLER, "TLC_831t").then(TLC_831_StealHealth(Summon.CARD))


class TLC_831t:
    """Pterrordax Hatchling"""

    pass


class TLC_605:
    """Tar Tyrant"""

    update = CurrentPlayer(OPPONENT) & Refresh(SELF, {GameTag.ATK: +6})


class TLC_621:
    """Stubborn Guardian"""

    deathrattle = Mill(CONTROLLER) * 3


class TLC_888_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        candidates = [
            card
            for card in player.hand
            if card is not source
            and (Race.ELEMENTAL in _card_races(card) or Race.DRAGON in _card_races(card))
        ]
        if candidates:
            card = source.game.random.choice(candidates)
            return source.game.queue_actions(
                source, [Give(player, ExactCopy(SELF).copy(source, card))]
            )


class TLC_888:
    """Cloud Serpent"""

    play = TLC_888_Play(CONTROLLER)


class TLC_987_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        played_quest = any(
            card.tags.get(GameTag.QUEST)
            for card in getattr(source.controller, "cards_played_this_game", [])
        )
        if played_quest:
            return source.game.queue_actions(source, [Hit(target, 3)])


class TLC_987:
    """Questing Assistant"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_987_Play(TARGET)
