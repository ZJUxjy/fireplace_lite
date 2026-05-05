from ..utils import *


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
