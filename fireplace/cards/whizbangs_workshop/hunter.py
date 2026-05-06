from ..utils import *


_ANIMAL_COMPANIONS = ("NEW1_032", "NEW1_033", "NEW1_034")
_BONUS_EFFECTS = (
    "UNG_999t10e",
    "UNG_999t2e",
    "UNG_999t3e",
    "UNG_999t4e",
    "UNG_999t5e",
    "UNG_999t6e",
    "UNG_999t7e",
    "UNG_999t8e",
    "UNG_999t13e",
    "UNG_999t14e",
)


class TOY_350_RandomBonusEffect(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        buff = source.game.random.choice(_BONUS_EFFECTS)
        return source.game.queue_actions(source, [Buff(target, buff)])


class TOY_354_RCRampage(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        open_slots = player.minion_slots
        summon_count = min(6, open_slots)
        overflow = 6 - summon_count
        hounds = [player.card("TOY_358t", source=source) for _ in range(summon_count)]
        actions = [Summon(player, hound) for hound in hounds]
        if overflow:
            actions.extend(
                Buff(hound, "TOY_354e", atk=overflow, max_health=overflow)
                for hound in hounds
            )
        return source.game.queue_actions(source, actions)


class TOY_357_ShuffleLowerAttack(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = [
            Shuffle(minion.controller, minion)
            for minion in list(source.game.board)
            if minion is not source and minion.atk < source.atk
        ]
        return source.game.queue_actions(source, actions)


class MIS_105_DrawOtherTypes(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        types = (CardType.MINION, CardType.SPELL, CardType.WEAPON)
        actions = []
        for card_type in types:
            if card.type == card_type:
                continue
            candidates = [
                deck_card
                for deck_card in source.controller.deck
                if deck_card.type == card_type
            ]
            if candidates:
                actions.append(ForceDraw(source.game.random.choice(candidates)))
        return source.game.queue_actions(source, actions)


class MIS_914_RecastTriggeredSecrets(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        secret_ids = dict.fromkeys(getattr(player, "triggered_secrets_this_game", []))
        actions = [Summon(player, secret_id) for secret_id in secret_ids]
        return source.game.queue_actions(source, actions)


##
# Minions

# TOY_351: Mystery Egg (2费 0/3)
# 微缩。亡语：随机获取一张野兽牌
class TOY_351:
    """Mystery Egg"""

    miniaturize_mini = "TOY_351t"
    deathrattle = Give(
        CONTROLLER, Buff(Copy(RANDOM(FRIENDLY_DECK + BEAST)), "TOY_351e1")
    )


class TOY_351t:
    """Mystery Egg"""

    deathrattle = TOY_351.deathrattle


class TOY_350:
    """Painted Canvasaur"""

    play = TOY_350_RandomBonusEffect(FRIENDLY_MINIONS + BEAST - SELF)


class TOY_355:
    """Hemet, Foam Marksman"""

    events = Death(FRIENDLY + MINION + BEAST).after(
        Give(
            CONTROLLER,
            Buff(
                RandomMinion(
                    race=Race.BEAST,
                    rarity=Rarity.LEGENDARY,
                    is_standard=False,
                ),
                "TOY_355e2",
            ),
        )
    )


class TOY_356:
    """Toyrannosaurus"""

    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 7)


class TOY_357:
    """King Plush"""

    tags = {GameTag.CHARGE: True}
    play = TOY_357_ShuffleLowerAttack(SELF)


class TOY_358t:
    """R.C. Hound"""


class MIS_914:
    """Product 9"""

    play = MIS_914_RecastTriggeredSecrets(CONTROLLER)


##
# Spells


class MIS_104:
    """Wilderness Pack"""

    play = Give(CONTROLLER, Buff(RandomBeast(), "MIS_104e")) * 5


class MIS_105:
    """Bargain Bin"""

    secret = Play(OPPONENT, MINION | SPELL | WEAPON).after(
        Reveal(SELF), MIS_105_DrawOtherTypes(Play.CARD)
    )


class TOY_352:
    """Fetch!"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + MINION)).then(
        Find(ForceDraw.TARGET + BEAST)
        & ForceDraw(RANDOM(FRIENDLY_DECK + SPELL))
    )


class TOY_353:
    """Patchwork Pals"""

    play = tuple(
        Give(CONTROLLER, Buff(card_id, "TOY_353e"))
        for card_id in _ANIMAL_COMPANIONS
    )


class TOY_354:
    """R.C. Rampage"""

    play = TOY_354_RCRampage(CONTROLLER)


##
# Weapons


class TOY_358:
    """Remote Control"""

    events = Attack(FRIENDLY_HERO).after(Summon(CONTROLLER, "TOY_358t"))


##
# Locations


class TOY_359:
    """Jungle Gym"""

    activate = Hit(RANDOM(ENEMY_CHARACTERS), 1) * (
        Count(FRIENDLY_MINIONS + BEAST) + 1
    )


class MIS_104e:
    class Hand:
        events = OWN_TURN_END.on(Discard(OWNER))

    events = REMOVED_IN_PLAY


TOY_351e1 = buff(cost=-3)
TOY_353e = buff(cost=-1)
TOY_354e = buff(+1, +1)


class TOY_355e2:
    tags = {GameTag.COST: -2}
    events = REMOVED_IN_PLAY
