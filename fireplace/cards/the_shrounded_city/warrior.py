from ..utils import *


class DINO_400:
    # 每当你获得护甲值，获得+2/+2并随机攻击一个敌方随从。
    events = GainArmor(FRIENDLY_HERO).on(Buff(SELF, "DINO_400e"), Attack(SELF, RANDOM_ENEMY_MINION))

DINO_400e = buff(+2,+2)



class DINO_401:
    # 突袭。在本随从攻击一个敌方随从后，还会对所有其他敌方随从造成伤害。
    events = Attack(SELF).after(
        Hit(ENEMY_MINIONS - Attack.DEFENDER, ATK(SELF))
    )


class DINO_433:
    # 随机召唤法力值消耗为（6），（4）和（2）的嘲讽随从各一个。
    pass


class TLC_478:
    # 在你的英雄攻击后，对所有随从造成1点伤害。
    pass


class TLC_600:
    # 战吼：造成5点伤害，获得5点护甲值。延系：法力值消耗减少（3）点。
    pass


class TLC_601:
    # 消耗最多5点护甲值。每消耗一点，对所有随从造成$1点伤害。
    pass


class TLC_602:
    # 任务：存活10个回合。奖励：拉特维厄斯，城市之眼。
    pass


class TLC_602t:
    # 战吼：随机获取2张勇闯安戈洛的任务奖励。将其余奖励洗入你的牌库。
    pass


class TLC_606:
    # 战吼：对一个敌方随从造成2点伤害。如果该随从死亡，获得5点护甲值。
    pass


class TLC_620:
    # 获得3点护甲值。对一个敌方随从造成等同于你护甲值的伤害。
    pass


class TLC_622:
    # 召唤两个0/6并具有嘲讽的守卫。守卫在受到伤害时会获得+1攻击力。
    pass


class TLC_622e:
    # 攻击力提高。
    pass


class TLC_622t:
    # 嘲讽在本随从受到伤害后，获得+1攻击力。
    pass


class TLC_623:
    # 在你的回合结束时，随机使一个受伤的友方随从获得+2/+2。
    pass


class TLC_623e:
    # +2/+2。
    pass


class TLC_624:
    # 战吼：召唤你受伤的随从的复制，使复制获得突袭。
    pass


class TLC_632:
    # 将你的英雄技能替换为"随机对一个敌人造成8点伤害。"使用两次后，换回原技能。
    pass


class TLC_632t:
    # 随机对一个敌人造成$8点伤害。<i>（还可使用两次！）</i>
    pass


class TLC_632t2:
    # 随机对一个敌人造成$8点伤害。<i>（还可使用一次！）</i>
    pass
