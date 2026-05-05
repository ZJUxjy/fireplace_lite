from utils import *
from hearthstone.enums import CardClass, Race, Zone


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


def test_return_policy_discovers_played_deathrattle_and_triggers_it():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    leper = player.give("EX1_029").play()
    leper.destroy()
    health_after_deathrattle = player.opponent.hero.health

    player.give("MIS_102").play()

    assert player.choice is not None
    assert player.choice.cards == [leper]
    player.choice.choose(leper)
    assert player.opponent.hero.health == health_after_deathrattle - 2


def test_workshop_mishap_deals_excess_to_both_neighbors():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    left = player.opponent.summon("EX1_572")
    middle = player.opponent.summon("CS2_182")
    right = player.opponent.summon("EX1_572")
    middle.damage = 3

    player.give("TOY_640").play(target=middle)

    assert middle.zone == Zone.GRAVEYARD
    assert left.health == left.data.health - 3
    assert right.health == right.data.health - 3


def test_workshop_mishap_outcast_has_lifesteal():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.hero.damage = 10
    target = player.opponent.summon("EX1_572")

    player.give("TOY_640").play(target=target)

    assert target.health == target.data.health - 5
    assert player.hero.health == 25


def test_blind_box_gets_two_random_demons_without_outcast():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.give(WISP)
    blind_box = player.give("TOY_643")
    player.give(WISP)
    hand_before = list(player.hand)

    blind_box.play()

    new_cards = [card for card in player.hand if card not in hand_before]
    assert len(new_cards) == 2


def test_blind_box_outcast_discovers_two_demons():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_643").play()

    assert player.choice is not None
    first = player.choice.cards[0]
    assert Race.DEMON in first.data.races
    player.choice.choose(first)
    assert player.choice is not None
    second = player.choice.cards[0]
    assert Race.DEMON in second.data.races
    player.choice.choose(second)

    assert first in player.hand
    assert second in player.hand


def test_cicigi_battlecry_outcast_and_deathrattle_get_first_edition_dh_cards():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    first_edition = {"TOY_913t1", "TOY_913t2", "TOY_913t3"}

    player.give(WISP)
    cicigi = player.give("TOY_913")
    player.give(WISP)
    cicigi.play()

    battlecry_cards = [card for card in player.hand if card.id in first_edition]
    assert len(battlecry_cards) == 1

    outcast_cicigi = player.give("TOY_913").play()
    outcast_cards = [card for card in player.hand if card.id in first_edition]
    assert len(outcast_cards) == 2

    outcast_cicigi.destroy()

    deathrattle_cards = [card for card in player.hand if card.id in first_edition]
    assert len(deathrattle_cards) == 3
