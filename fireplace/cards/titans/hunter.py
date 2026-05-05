from ..utils import *


##
# TTN_721: V-07-TR-0N Prime (6费 3/5 机械)
# 泰坦。本随从的技能会在另一个随机友方随从身上重复

def _ttn_721_prime(source):
    return getattr(source, "creator", source)


def _ttn_721_repeat_target(prime):
    targets = [minion for minion in prime.controller.field if minion is not prime]
    if targets:
        return prime.game.random.choice(targets)


class TTN_721_AttachCannons(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        prime = _ttn_721_prime(source)
        repeat = _ttn_721_repeat_target(prime)
        actions = [
            Buff(prime, "TTN_721te"),
            Hit(RANDOM(ENEMY_MINIONS | ENEMY_HERO), 4),
        ]
        if repeat:
            actions.extend([
                Buff(repeat, "TTN_721te"),
                Hit(RANDOM(ENEMY_MINIONS | ENEMY_HERO), 4),
            ])
        return source.game.queue_actions(source, actions)


class TTN_721_MaximizeDefenses(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        prime = _ttn_721_prime(source)
        repeat = _ttn_721_repeat_target(prime)
        actions = [
            Buff(prime, "TTN_721t2e2"),
            SetTags(prime, {GameTag.ELUSIVE: True}),
        ]
        if repeat:
            actions.extend([
                Buff(repeat, "TTN_721t2e2"),
                SetTags(repeat, {GameTag.ELUSIVE: True}),
            ])
        return source.game.queue_actions(source, actions)


class TTN_721_FullPower(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        prime = _ttn_721_prime(source)
        repeat = _ttn_721_repeat_target(prime)
        actions = [
            Buff(prime, "TTN_721t1e"),
            Draw(prime.controller),
        ]
        if repeat:
            actions.extend([
                Buff(repeat, "TTN_721t1e"),
                Draw(prime.controller),
            ])
        return source.game.queue_actions(source, actions)

class TTN_721:
    """V-07-TR-0N Prime"""

    tags = {GameTag.ELITE: True, GameTag.CARDRACE: Race.MECHANICAL}

    titan_abilities = ["TTN_721t", "TTN_721t1", "TTN_721t2"]


# TTN_721t: Attach the Cannons! - Gain +2/+1. Deal 4 damage to a random enemy.
class TTN_721t:
    """Attach the Cannons!"""

    play = TTN_721_AttachCannons(CONTROLLER)


TTN_721te = buff(+2, +1)


# TTN_721t1: Maximize Defenses! - Gain +3 health and Elusive
class TTN_721t1:
    """Full Power!"""

    play = TTN_721_FullPower(CONTROLLER)


TTN_721t1e = buff(+1, +2)


class TTN_721t2:
    """Maximize Defenses!"""

    play = TTN_721_MaximizeDefenses(CONTROLLER)


TTN_721t2e2 = buff(0, +3)
