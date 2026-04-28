from ..utils import *


##
# TTN_075: Norgannon (6费 3/8)
# 泰坦。使用技能后，其他技能效果翻倍（简化：不实现翻倍）

class TTN_075:
    """Norgannon"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_075t", "TTN_075t2", "TTN_075t3"]


# TTN_075t: Progenitor's Power - Deal 5 damage to a target
class TTN_075t:
    """Progenitor's Power"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    play = Hit(TARGET, 5)


# TTN_075t2: Ancient Knowledge - Enemy cards cost 1 more next turn
class TTN_075t2:
    """Ancient Knowledge"""

    # 简化：对所有敌方随从造成1点伤害（完整效果需要持续状态跟踪）
    play = Hit(ENEMY_MINIONS, 1)


# TTN_075t3: Unlimited Potential - Cast 1 random Mage secret
class TTN_075t3:
    """Unlimited Potential"""

    play = Summon(CONTROLLER, RandomSpell(secret=True, card_class=CardClass.MAGE))
