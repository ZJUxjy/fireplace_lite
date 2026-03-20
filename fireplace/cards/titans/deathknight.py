from ..utils import *


##
# TTN_737: The Primus (8费 7/9)
# 泰坦。使用技能后，发现对应符文的牌（简化实现）

class TTN_737:
    """The Primus"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_737t", "TTN_737t2", "TTN_737t3"]
    ability_used = Discover(RandomCard(card_class=CardClass.DEATHKNIGHT))


# TTN_737t: Runes of Blood - Destroy an enemy minion; gain its health
class TTN_737t:
    """Runes of Blood"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = (
        Buff(SELF, "TTN_737te"),
        Heal(FRIENDLY_HERO, Attr(TARGET, GameTag.HEALTH)),
        Destroy(TARGET),
    )


class TTN_737te:
    max_health = lambda self, at, current: current + Attr(self, GameTag.HEALTH).evaluate(self)


TTN_737te = buff(0, +3)  # 简化：固定+3生命


# TTN_737t2: Servant of the Primus - Summon a Reborn Taunt minion token
class TTN_737t2:
    """Servant of the Primus"""

    play = Summon(CONTROLLER, "TTN_737t2t")


# TTN_737t2t: 兵主的仆人 (4/4 嘲讽 复生)
class TTN_737t2t:
    """Servant of the Primus"""

    tags = {GameTag.TAUNT: True, GameTag.REBORN: True}


# TTN_737t3: Runes of Frost - Next spell costs 3 less and has Spell Damage +3
class TTN_737t3:
    """Runes of Frost"""

    # 简化：抽一张牌并给控制者+3法术伤害
    play = (
        Draw(CONTROLLER),
        Buff(CONTROLLER, "TTN_737t3e"),
    )


TTN_737t3e = buff(cost=-3)
