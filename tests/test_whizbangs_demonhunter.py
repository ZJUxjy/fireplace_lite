from utils import *
from hearthstone.enums import CardClass, Zone


def test_sock_puppet_slitherspear_attack_includes_hero_attack():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    puppet = player.summon("MIS_710")

    player.hero.atk = 3
    game.refresh_auras()

    assert puppet.atk == puppet.data.atk + 3


def test_gibbering_reject_summons_another_after_hero_attacks():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.summon("MIS_911")
    player.give(LIGHTS_JUSTICE).play()

    player.hero.attack(player.opponent.hero)

    assert [minion.id for minion in player.field].count("MIS_911") == 2


def test_spirit_of_the_team_buffs_hero_attack_on_own_turn_then_unstealths():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    spirit = player.summon("TOY_028")

    game.refresh_auras()
    assert spirit.stealthed
    assert player.hero.atk == 2

    game.end_turn()
    game.end_turn()

    assert not spirit.stealthed
    assert player.hero.atk == 2


def test_umpires_grasp_deathrattle_draws_demon_and_discounts_it():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    demon = player.card("EX1_301")
    non_demon = player.card("CS2_182")
    non_demon.zone = Zone.DECK
    demon.zone = Zone.DECK
    weapon = player.give("TOY_641").play()

    weapon.destroy()

    assert demon.zone == Zone.HAND
    assert non_demon.zone == Zone.DECK
    assert demon.cost == max(0, demon.data.cost - 2)


def test_ball_hog_battlecry_and_deathrattle_hit_lowest_health_enemy():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    low = player.opponent.summon("CS2_182")
    high = player.opponent.summon("EX1_572")

    ball_hog = player.give("TOY_642").play()

    assert low.health == low.data.health - 3
    assert high.health == high.data.health

    ball_hog.destroy()

    assert low.zone == Zone.GRAVEYARD
    assert high.health == high.data.health


def test_red_card_makes_minion_dormant_for_two_turns():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.opponent.summon("EX1_572")

    player.give("TOY_644").play(target=target)

    assert target.dormant
    assert target.dormant_turns == 2


def test_opal_spellstone_upgrades_after_hero_attacks_four_times():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.give("TOY_645")
    weapon = player.give(LIGHTS_JUSTICE).play()

    for _ in range(4):
        player.hero.attack(player.opponent.hero)
        player.hero.num_attacks = 0

    assert "TOY_645t" in [card.id for card in player.hand]
    assert weapon.durability == 0


def test_magtheridon_dormant_deals_damage_at_own_turn_end():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    magtheridon = player.summon("TOY_647")
    enemy = player.opponent.summon("EX1_572")

    game.end_turn()

    assert magtheridon.dormant
    assert player.opponent.hero.health == 27
    assert enemy.health == enemy.data.health - 3
