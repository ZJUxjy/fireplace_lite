from ..utils import *


# Luck of the Coin
GAME_001 = buff(health=3)


class GAME_003:
    """Coin's Vengeance"""

    events = Play(CONTROLLER, MINION).on(Buff(Play.CARD, "GAME_003e"), Destroy(SELF))


GAME_003e = buff(+1, +1)


class GAME_004:
    """AFK"""

    update = Refresh(CONTROLLER, {GameTag.TIMEOUT: 10})


class GAME_005:
    """The Coin"""

    play = ManaThisTurn(CONTROLLER, 1)


class BG31_BOB_Play(MultipleChoice):
    choose_times = 1
    action_ids = ("BG31_BOBt", "BG31_BOBt2", "BG31_BOBt3", "BG31_BOBt4")

    def do_step1(self):
        self.cards = [self.player.card(card_id, source=self.source) for card_id in self.action_ids]

    def done(self):
        chosen = self.choosed_cards[0].id
        if chosen == "BG31_BOBt":
            actions = [Freeze(ENEMY_MINIONS)]
        elif chosen == "BG31_BOBt2":
            actions = [
                Find(ENEMY_MINIONS)
                & Give(CONTROLLER, ExactCopy(RANDOM(ENEMY_MINIONS))),
                Give(OPPONENT, "GAME_005") * 3,
            ]
        elif chosen == "BG31_BOBt3":
            actions = [Discover(CONTROLLER, RandomMinion(cost=3)), FillMana(CONTROLLER, 3)]
        else:
            actions = [
                ForceDraw(RANDOM(FRIENDLY_DECK + MINION)).then(
                    Give(CONTROLLER, ExactCopy(ForceDraw.TARGET)) * 2
                )
            ]
        return self.source.game.queue_actions(self.source, actions)


class BG31_BOB:
    """Bob the Bartender"""

    play = BG31_BOB_Play(CONTROLLER)


class BG31_BOBt:
    """Freeze the Shop"""


class BG31_BOBt2:
    """Recruit a Minion"""


class BG31_BOBt3:
    """Refresh the Tavern"""


class BG31_BOBt4:
    """Find a Triple"""


class GBL_001e:
    cost = SET(1)
    events = REMOVED_IN_PLAY


class GBL_002e:
    tags = {GameTag.COST: -2}
    events = REMOVED_IN_PLAY


class GBL_003e:
    tags = {GameTag.COST: -1}
    events = REMOVED_IN_PLAY


class GBL_004e:
    tags = {GameTag.COST: -3}
    events = REMOVED_IN_PLAY


class GBL_005e:
    tags = {GameTag.COST: +2}
    events = REMOVED_IN_PLAY


class GBL_006e:
    cost = SET(2)
    events = REMOVED_IN_PLAY


class GBL_007e:
    cost = SET(10)
    events = REMOVED_IN_PLAY


class GBL_008e:
    tags = {GameTag.COST: -4}
    events = REMOVED_IN_PLAY


class GBL_009e:
    cost = SET(0)
    events = REMOVED_IN_PLAY
