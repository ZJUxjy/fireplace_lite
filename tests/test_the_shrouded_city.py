from utils import *
from hearthstone.enums import CardClass


def test_dino_400_gain_armor_buff():
    """测试 DINO_400 怒袭甲龙 - 每当你获得护甲值，获得+2/+2并随机攻击一个敌方随从"""
    game = prepare_game(CardClass.WARRIOR, CardClass.WARRIOR)
    dino = game.player1.give("DINO_400")
    dino.play()
    assert dino.atk == 4
    assert dino.health == 3

    # 召唤一个敌方随从用于测试随机攻击
    enemy_wisp = game.player2.summon(WISP)
    enemy_wisp2 = game.player2.summon(WISP)
    game.end_turn()
    game.end_turn()

    # 使用英雄技能获得护甲
    game.player1.hero.power.use()
    assert game.player1.hero.armor == 2
    # 获得护甲后，DINO_400 获得 +2/+2
    assert dino.atk == 4 + 2
    # DINO_400 攻击 Wisp 时会受到 1 点伤害，所以当前生命值是 5-1=4
    assert dino.max_health == 3 + 2  # 最大生命值应该是 5
    assert dino.health == 3 + 2 - 1  # 当前生命值减去受到的 1 点伤害
    # 应该随机攻击了一个敌方随从
    # 检查是否有敌方随从死亡或受伤
    damaged_or_dead = (
        enemy_wisp.dead or enemy_wisp.damage > 0 or
        enemy_wisp2.dead or enemy_wisp2.damage > 0
    )
    assert damaged_or_dead

    # 再次获得护甲
    game.player1.give("EX1_606").play()  # Shield Block: 获得5护甲
    assert dino.atk == 4 + 2 + 2
    # 再次获得护甲时，DINO_400 又会随机攻击一个敌方随从，可能再受到伤害
    # 最大生命值应该是 3 + 2 + 2 = 7
    assert dino.max_health == 3 + 2 + 2


def test_dino_401_attack_splash_damage():
    """测试 DINO_401 伟岸的德拉克雷斯 - 突袭，攻击敌方随从后对所有其他敌方随从造成伤害"""
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)

    # 确定 DINO_401 的拥有者和敌人
    dino_controller = game.current_player  # 当前玩家（先手）
    enemy_player = dino_controller.opponent

    # 召唤多个敌方随从到敌人场上（不使用嘲讽，避免必须先攻击嘲讽的问题）
    enemy1 = enemy_player.summon(WISP)  # 1/1
    enemy2 = enemy_player.summon(WISP)  # 1/1
    enemy3 = enemy_player.summon("CS2_182")  # 2/2 的普通随从

    # 回合交换后回到 dino_controller
    game.end_turn()
    game.end_turn()

    dino = dino_controller.give("DINO_401")
    dino.play()
    assert dino.atk == 5
    assert dino.health == 12
    assert dino.rush  # 应该有突袭

    # 用 DINO_401 攻击 enemy1
    dino.attack(enemy1)

    # enemy1 应该死亡（5攻击力 vs 1生命值）
    assert enemy1.dead

    # 其他敌方随从应该受到等同于 DINO_401 攻击力的伤害（5点）
    # 溅射伤害导致所有其他敌方随从死亡
    assert enemy2.dead  # 1/1 承受5点伤害，死亡
    assert enemy3.dead  # 2/2 承受5点伤害，死亡
