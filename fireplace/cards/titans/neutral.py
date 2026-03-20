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
class YOG_516t2:
    """Induce Insanity"""

    # 简化：对所有敌方随从造成3点伤害
    play = Hit(ENEMY_MINIONS, 3)


# YOG_516t3: Tentacle Swarm - Fill your hand with 1/1 Chaotic Tendrils
class YOG_516t3:
    """Tentacle Swarm"""

    play = Give(CONTROLLER, "YOG_516t3t") * 7


# YOG_516t3t: Chaotic Tendril (1/1 随从)
class YOG_516t3t:
    """Chaotic Tendril"""

    pass
