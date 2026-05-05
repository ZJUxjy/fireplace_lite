from ..utils import *


##
# YOG_516: Yogg-Saron, Unleashed (9费 7/5)
# 泰坦。使用技能后，随机施放两个法术

class YOG_516:
    """Yogg-Saron, Unleashed"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["YOG_516t", "YOG_516t2", "YOG_516t3"]
    ability_used = CastSpell(RandomSpell()), CastSpell(RandomSpell())


# YOG_516t: Reign of Chaos - Take control of an enemy minion
class YOG_516t:
    """Reign of Chaos"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Steal(TARGET)


# YOG_516t2: Induce Insanity - Force each enemy minion to attack a random enemy minion
class YOG_516_InduceInsanity(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        for attacker in list(player.opponent.field):
            if attacker.dead or attacker.zone != Zone.PLAY:
                continue
            defenders = [
                minion
                for minion in player.opponent.field
                if minion is not attacker and not minion.dead and minion.zone == Zone.PLAY
            ]
            if defenders:
                source.game.queue_actions(
                    source, [Attack(attacker, source.game.random.choice(defenders))]
                )


class YOG_516t2:
    """Induce Insanity"""

    play = YOG_516_InduceInsanity(CONTROLLER)


# YOG_516t3: Tentacle Swarm - Fill your hand with 1/1 Chaotic Tendrils
class YOG_516t3:
    """Tentacle Swarm"""

    play = Give(CONTROLLER, "YOG_516t3t") * 7


# YOG_516t3t: Chaotic Tendril (1/1 随从)
class YOG_516t3t:
    """Chaotic Tendril"""

    pass
