from hearthstone.enums import SpellSchool

from ..utils import *


def _has_no_deck_minions(player):
    return not player.deck.filter(type=CardType.MINION)


def _frost_spells(entities, source):
    return [
        card for card in entities
        if getattr(getattr(card, "data", None), "spell_school", None)
        == SpellSchool.FROST
    ]


FROST_SPELL = FuncSelector(_frost_spells)


class MIS_107_Malfunction(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = 3 + (3 if _has_no_deck_minions(player) else 0)
        actions = []
        for _ in range(amount):
            enemies = list(player.opponent.field)
            if not enemies:
                break
            actions.append(Hit(source.game.random.choice(enemies), 1))
        return source.game.queue_actions(source, actions)


class MIS_303_CastNextCostSpell(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        return source.game.queue_actions(
            source, [CastSpell(RandomSpell(cost=card.cost + 1))]
        )


class TOY_371_ManufacturingError(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        discount = _has_no_deck_minions(player)
        cards = list(player.deck)[:3]
        actions = []
        for card in cards:
            actions.append(ForceDraw(card))
            if discount:
                actions.append(Buff(card, "TOY_371e"))
        return source.game.queue_actions(source, actions)


class TOY_372_YoggInTheBox(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        random_spell = (
            RandomSpell(cost=range(5, 100))
            if _has_no_deck_minions(player)
            else RandomSpell()
        )
        return source.game.queue_actions(
            source, [CastSpellTargetsEnemiesIfPossible(random_spell) * 5]
        )


class TOY_373_Wisdomball(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        actions = [
            CastSpellTargetsEnemiesIfPossible(RandomSpell(card_class=CardClass.MAGE))
        ]
        weapon.damage += 1
        if weapon.durability <= 0:
            actions.append(Destroy(weapon))
        return source.game.queue_actions(source, actions)


class TOY_374_SpotTheDifferenceChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Summon(self.player, card)])
        if getattr(self, "repeat", False):
            self.source.game.queue_actions(
                self.source, [TOY_374_SpotTheDifference(self.player, repeat=False)]
            )
        self.trigger_choice_callback()


class TOY_374_SpotTheDifference(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player, repeat=None):
        repeat = _has_no_deck_minions(player) if repeat is None else repeat
        card_ids = RandomMinion(cost=3).evaluate(source)
        if not isinstance(card_ids, list):
            card_ids = [card_ids]
        while len(card_ids) < 3:
            card_ids.extend(RandomMinion(cost=3).evaluate(source))
        cards = [player.card(card_id, source=source) for card_id in card_ids[:3]]
        choice = TOY_374_SpotTheDifferenceChoice(player, cards)
        choice.repeat = repeat
        return source.game.queue_actions(source, [choice])


class TOY_377_FrostLichCrossStitch(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        source.game.queue_actions(source, [Hit(target, 3)])
        if target.dead:
            return source.game.queue_actions(
                source, [Summon(source.controller, "CS2_033")]
            )


class TOY_378_GalacticProjectionOrb(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells_by_cost = {}
        for card in player.cards_played_this_game:
            if card.type != CardType.SPELL or card is source or card.id == source.id:
                continue
            spells_by_cost.setdefault(card.cost, []).append(card)
        actions = []
        for spells in spells_by_cost.values():
            chosen = source.game.random.choice(spells)
            actions.append(
                CastSpellTargetsEnemiesIfPossible(player.card(chosen.id, source=source))
            )
        return source.game.queue_actions(source, actions)


##
# Minions


class MIS_303:
    """Darkmoon Magician"""

    events = OWN_SPELL_PLAY.after(MIS_303_CastNextCostSpell(Play.CARD))


class TOY_370:
    """Triplewick Trickster"""

    play = Hit(RANDOM(ENEMY_CHARACTERS), 2) * 3


class TOY_373:
    """Puzzlemaster Khadgar"""

    play = Summon(CONTROLLER, "TOY_373t")


class TOY_373t:
    """Magic Wisdomball"""

    events = OWN_TURN_END.on(TOY_373_Wisdomball(SELF))


class TOY_375:
    """Sleet Skater"""

    miniaturize_mini = "TOY_375t"

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Freeze(TARGET), GainArmor(FRIENDLY_HERO, ATK(TARGET))


class TOY_375t:
    """Sleet Skater"""

    requirements = TOY_375.requirements
    play = TOY_375.play


class TOY_376:
    """Watercolor Artist"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + SPELL + FROST_SPELL)).then(
        Buff(ForceDraw.TARGET, "TOY_376e1")
    )


##
# Spells


class MIS_107:
    """Malfunction"""

    play = MIS_107_Malfunction(CONTROLLER)


class MIS_302:
    """Buy One, Get One Freeze"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Freeze(TARGET), Summon(CONTROLLER, ExactCopy(TARGET)).then(
        Freeze(Summon.CARD)
    )


class TOY_037:
    """Hidden Objects"""

    play = Discover(
        CONTROLLER, RandomSpell(secret=True, card_class=CardClass.MAGE)
    ).then(Give(CONTROLLER, Buff(Discover.CARD, "TOY_037e")))


class TOY_371:
    """Manufacturing Error"""

    play = TOY_371_ManufacturingError(CONTROLLER)


class TOY_372:
    """Yogg in the Box"""

    play = TOY_372_YoggInTheBox(CONTROLLER)


class TOY_374:
    """Spot the Difference"""

    play = TOY_374_SpotTheDifference(CONTROLLER)


class TOY_377:
    """Frost Lich Cross-Stitch"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = TOY_377_FrostLichCrossStitch(TARGET)


class TOY_378:
    """The Galactic Projection Orb"""

    play = TOY_378_GalacticProjectionOrb(CONTROLLER)


class TOY_037e:
    cost = SET(1)


TOY_371e = buff(cost=-3)


class TOY_376e:
    tags = {GameTag.COST: -1}
    events = REMOVED_IN_PLAY


class TOY_376e1:
    class Hand:
        events = OWN_TURN_BEGIN.on(Buff(OWNER, "TOY_376e"))

    events = REMOVED_IN_PLAY
