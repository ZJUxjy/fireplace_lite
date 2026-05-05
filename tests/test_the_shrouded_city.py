from utils import *
from hearthstone.enums import CardClass, Zone

from fireplace.actions import Hit


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


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


def test_dino_433_summons_taunt_minions_at_three_costs():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)

    player.give("DINO_433").play()

    assert sorted(minion.cost for minion in player.field) == [2, 4, 6]
    assert all(minion.taunt for minion in player.field)


def test_tlc_478_weapon_damages_all_minions_after_hero_attacks():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    friendly = player.summon(GOLDSHIRE_FOOTMAN)
    attack_target = player.opponent.summon(WISP)
    enemy = player.opponent.summon("EX1_399")

    player.give("TLC_478").play()
    player.hero.attack(attack_target)

    assert friendly.damage == 1
    assert enemy.damage == 1


def test_tlc_600_battlecry_and_dragon_kindred_discount():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon("EX1_399")

    player.give("TLC_600").play(target=enemy)

    assert enemy.damage == 5
    assert player.hero.armor == 5

    game.end_turn()
    game.end_turn()
    next_copy = player.give("TLC_600")

    assert next_copy.cost == next_copy.data.cost - 3


def test_tlc_601_spends_up_to_five_armor_to_damage_all_minions():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    player.hero.armor = 7
    friendly = player.summon("EX1_399")
    enemy = player.opponent.summon("EX1_399")

    player.give("TLC_601").play()

    assert player.hero.armor == 2
    assert friendly.damage == 5
    assert enemy.damage == 5


def test_tlc_602_quest_rewards_latorvius_after_surviving_ten_turns():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)

    quest = player.give("TLC_602").play()
    for _ in range(20):
        game.end_turn()

    assert quest.zone == Zone.GRAVEYARD
    assert any(card.id == "TLC_602t" for card in player.hand)


def test_tlc_602t_gives_two_ungoro_rewards_and_shuffles_the_rest():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    rewards = {
        "UNG_116t",
        "UNG_920t1",
        "UNG_028t",
        "UNG_954t1",
        "UNG_940t8",
        "UNG_067t1",
        "UNG_942t",
        "UNG_829t1",
        "UNG_934t1",
    }

    player.give("TLC_602t").play()

    assert len([card for card in player.hand if card.id in rewards]) == 2
    assert len([card for card in player.deck if card.id in rewards]) == 7


def test_tlc_606_gains_armor_if_battlecry_kills_enemy_minion():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon(WISP)

    player.give("TLC_606").play(target=enemy)

    assert enemy.dead
    assert player.hero.armor == 5


def test_tlc_620_gains_armor_before_damaging_enemy_minion():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    player.hero.armor = 4
    enemy = player.opponent.summon("EX1_399")

    player.give("TLC_620").play(target=enemy)

    assert player.hero.armor == 7
    assert enemy.damage == 7


def test_tlc_622_summons_guards_that_gain_attack_when_damaged():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_622").play()
    guards = player.field.filter(id="TLC_622t")

    assert len(guards) == 2
    assert all(guard.taunt and guard.atk == 0 and guard.max_health == 6 for guard in guards)

    game.cheat_action(guards[0], [Hit(guards[0], 2)])

    assert guards[0].atk == 1


def test_tlc_623_buffs_damaged_friendly_minion_at_end_of_turn():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    sculptor = player.summon("TLC_623")
    damaged = player.summon(GOLDSHIRE_FOOTMAN)
    game.cheat_action(damaged, [Hit(damaged, 1)])

    game.end_turn()

    assert (damaged.atk, damaged.max_health) == (
        damaged.data.atk + 2,
        damaged.data.health + 2,
    )
    assert sculptor.atk == sculptor.data.atk


def test_tlc_624_copies_each_damaged_friendly_minion_and_gives_rush():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    damaged_one = player.summon(GOLDSHIRE_FOOTMAN)
    damaged_two = player.summon(TARGET_DUMMY)
    healthy = player.summon(WISP)
    game.cheat_action(damaged_one, [Hit(damaged_one, 1)])
    game.cheat_action(damaged_two, [Hit(damaged_two, 1)])

    player.give("TLC_624").play()

    copies = [card for card in player.field if card not in (damaged_one, damaged_two, healthy) and card.id != "TLC_624"]
    assert sorted(card.id for card in copies) == sorted([damaged_one.id, damaged_two.id])
    assert all(card.rush for card in copies)


def test_tlc_632_replaces_hero_power_for_two_uses_then_restores_original():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    _set_mana(player)
    original_power = player.hero.power.id

    player.give("TLC_632").play()

    assert player.hero.power.id == "TLC_632t"

    player.hero.power.use()
    assert player.opponent.hero.damage == 8
    assert player.hero.power.id == "TLC_632t2"

    game.end_turn()
    game.end_turn()
    _set_mana(player)
    player.hero.power.use()

    assert player.opponent.hero.damage == 16
    assert player.hero.power.id == original_power
