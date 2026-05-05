from ..utils import *


def _played_minion_last_turn(card):
    return any(
        played.type == CardType.MINION
        for played in getattr(card.controller, "cards_played_last_turn", [])
    )


class DINO_432_SetStats(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        return source.game.queue_actions(
            source,
            [
                Buff(
                    target,
                    "DINO_432e",
                    atk=5 - target.atk,
                    max_health=4 - target.max_health,
                )
            ],
        )


class TLC_231_Draw(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.deck if card.type == CardType.MINION]
        if not minions:
            return
        card = minions[-1]
        actions = [ForceDraw(card)]
        if card.atk >= 5:
            actions.append(Buff(card, "TLC_231e"))
            actions.append(GainArmor(player.hero, 5))
        return source.game.queue_actions(source, actions)


class TLC_235_Replace(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        controller = target.controller
        cost = target.cost
        return source.game.queue_actions(
            source,
            [
                Destroy(target),
                Summon(controller, RandomMinion(cost=cost)),
            ],
        )


class TLC_236_DrawCosts(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        drawn = []
        for cost in (1, 2, 3, 4):
            matches = [
                card
                for card in player.deck
                if card.type == CardType.MINION and card.data.cost == cost
            ]
            if not matches:
                continue
            card = matches[-1]
            drawn.append(card)
            actions.append(ForceDraw(card))
        if _played_minion_last_turn(source):
            actions.extend(Buff(card, "TLC_236e") for card in drawn)
        return source.game.queue_actions(source, actions)


class TLC_239_CheckFullBoard(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, quest):
        player = quest.controller
        if not player.current_player:
            return
        if len(player.field) < player.game.MAX_MINIONS_ON_FIELD:
            return
        if getattr(quest, "_tlc_239_last_turn", None) == player.game.turn:
            return
        quest._tlc_239_last_turn = player.game.turn
        return source.game.queue_actions(source, [AddProgress(quest, quest)])


class DINO_130:
    """Longneck Egg"""

    deathrattle = Summon(CONTROLLER, "DINO_130t"), Buff(
        FRIENDLY_MINIONS, "DINO_130e"
    )


DINO_130e = buff(atk=1, health=1)


class DINO_130t:
    """Tiny Longneck"""

    pass


class DINO_421:
    """Seismopod"""

    deathrattle = Buff(FRIENDLY + (IN_HAND | IN_DECK) + MINION, "DINO_421e")


DINO_421e = buff(atk=3, health=3)


class DINO_432:
    """Panther Mask"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = DINO_432_SetStats(TARGET), Draw(CONTROLLER) * 2


DINO_432e = buff(stealth=True)


class TLC_230:
    """TREEEES!!!"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Summon(CONTROLLER, "TLC_230t").then(Attack(Summon.CARD, TARGET)) * 4


class TLC_230t:
    """Treant"""

    pass


class TLC_231:
    """Story of Barnabus"""

    play = TLC_231_Draw(CONTROLLER)


TLC_231e = buff(health=5)


class TLC_232:
    """Ravenous Flock"""

    play = Buff(CONTROLLER, "TLC_232e")


class TLC_232e:
    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, "TLC_237t") * 3, Destroy(SELF))


class TLC_233:
    """Hatchery Helper"""

    play = Buff(FRIENDLY_MINIONS - SELF + (ATK <= 2), "TLC_233e")


TLC_233e = buff(atk=1, health=2, taunt=True)


class TLC_234:
    """Eternal Bloodpetal"""

    deathrattle = Summon(CONTROLLER, "TLC_234t")


class TLC_234t:
    """Eternal Seedling"""

    deathrattle = Summon(CONTROLLER, "TLC_234")


class TLC_235:
    """Life Cycle"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_235_Replace(TARGET)


class TLC_236:
    """Hybridization"""

    play = TLC_236_DrawCosts(CONTROLLER)


@custom_card
class TLC_236e:
    tags = {
        GameTag.CARDNAME: "Hybridized",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


class TLC_237:
    """Skyscreamer Eggs"""

    deathrattle = Summon(CONTROLLER, "TLC_237t") * 4


class TLC_237t:
    """Skyscreamer Hatchling"""

    pass


class TLC_239:
    """Restore the Wild"""

    quest = (
        Summon(CONTROLLER, MINION).after(TLC_239_CheckFullBoard(SELF)),
        OWN_TURN_END.on(TLC_239_CheckFullBoard(SELF)),
    )
    reward = Give(CONTROLLER, "TLC_239t")


TLC_239e = buff(atk=2, health=2)


class TLC_239t:
    """The Everbloom"""

    events = Attack(FRIENDLY_HERO).after(Buff(FRIENDLY_MINIONS, "TLC_239e"))


class TLC_257:
    """Loh, the Living Legend"""

    play = Buff(CONTROLLER, "TLC_257e1")


class TLC_257e1:
    update = Refresh(FRIENDLY + (IN_HAND | IN_DECK) + MINION, {GameTag.COST: SET(5)})
