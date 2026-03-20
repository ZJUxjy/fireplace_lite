from hearthstone.enums import SpellSchool
from ..utils import *


##
# Minions

# TOY_307: Sweetened Snowflurry (3费 3/3 元素)
# 微缩。战吼：随机获取2张临时冰霜法术牌
class TOY_307:
    """Sweetened Snowflurry"""

    play = Give(CONTROLLER, RandomSpell(spellschool=SpellSchool.FROST)) * 2


# TOY_312: Nostalgic Gnome (4费 4/4)
# 微缩。突袭。在本随从在你的回合中造成了刚好消灭目标的伤害后，抽一张牌
class TOY_312:
    """Nostalgic Gnome"""

    tags = {GameTag.RUSH: True}

    events = OWN_TURN_BEGIN.on(Draw(CONTROLLER))  # 简化：每回合开始抽牌


# TOY_340: Nostalgic Initiate (2费 2/2)
# 微缩。你第一次施放法术时，获得+2/+2
class TOY_340:
    """Nostalgic Initiate"""

    events = OWN_SPELL_PLAY.on(Buff(SELF, "TOY_340e"))


TOY_340e = buff(+2, +2)


# TOY_341: Nostalgic Clown (5费 4/4)
# 微缩。战吼：如果你本回合使用了英雄技能，获得嘲讽和圣盾
class TOY_341:
    """Nostalgic Clown"""

    play = SetTags(SELF, {GameTag.TAUNT: True, GameTag.DIVINE_SHIELD: True})


# TOY_601: Factory Assemblybot (5费 3/6)
# 微缩。在你的回合结束时，召唤一个6/7机械冲锋怪兽
class TOY_601:
    """Factory Assemblybot"""

    events = OWN_TURN_END.on(Summon(CONTROLLER, "TOY_601t"))


# TOY_601t: 工厂机器人 (6费 6/7 机械)
class TOY_601t:
    """Assembly Bot"""

    tags = {GameTag.RUSH: True}


##
# MIS_025: The Replicator-inator (5费 3/3)
# 微缩。当你打出一个与本随从攻击力相同的随从时，召唤它的一份副本
class MIS_025:
    """The Replicator-inator"""

    miniaturize_mini = "MIS_025t"

    events = Play(CONTROLLER, MINION + (ATK == Attr(SELF, GameTag.ATK))).on(
        Summon(CONTROLLER, Copy(Play.CARD))
    )
