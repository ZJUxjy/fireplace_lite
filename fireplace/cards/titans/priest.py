from ..utils import *


##
# TTN_429: Aman'Thul (7费 3/10)
# 泰坦。使用技能后，发现任意职业的传说随从牌

class TTN_429:
    """Aman'Thul"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_429t", "TTN_429t2", "TTN_429t3"]
    ability_used = Discover(RandomMinion(rarity=Rarity.LEGENDARY))


# TTN_429t: Shape the Stars - Choose a non-Titan minion, summon a copy with +2/+2
class TTN_429t:
    """Shape the Stars"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Summon(CONTROLLER, Buff(Copy(TARGET), "TTN_429te"))


TTN_429te = buff(+2, +2)


# TTN_429t2: Strike from History - Remove two enemy minions from game
class TTN_429t2:
    """Strike from History"""

    requirements = {
        PlayReq.REQ_MINIMUM_ENEMY_MINIONS: 1,
    }

    # 简化：消灭一个随机敌方随从（完整效果需要双目标选择）
    play = Destroy(RANDOM(ENEMY_MINIONS) * 2)


# TTN_429t3: Vision of Heroes - Summon a random 6-cost minion with Taunt and Lifesteal
class TTN_429t3:
    """Vision of Heroes"""

    play = (
        Summon(CONTROLLER, RandomMinion(cost=6)),
        SetTags(FRIENDLY_MINIONS - TAUNT, {GameTag.TAUNT: True}),
    )
