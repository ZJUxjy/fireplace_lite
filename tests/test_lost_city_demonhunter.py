from utils import *
from hearthstone.enums import CardClass, Zone


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def _clear_hand(player):
    for card in list(player.hand):
        card.zone = Zone.GRAVEYARD


def test_feast_of_horns_summons_three_rush_raptors_and_outcast_grants_attack_immunity():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    _clear_hand(player)

    player.give(WISP)
    player.give("DINO_136").play()

    assert [minion.id for minion in player.field] == ["DINO_136t"] * 3
    assert all(minion.rush for minion in player.field)
    assert all(minion.immune_while_attacking for minion in player.field)


def test_agile_cook_discounts_adjacent_hand_cards():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    _clear_hand(player)
    left = player.give(WISP)
    chef = player.give("DINO_137")
    right = player.give(GOLDSHIRE_FOOTMAN)
    far = player.give(TARGET_DUMMY)

    chef.play()

    assert left.cost == max(0, left.data.cost - 1)
    assert right.cost == right.data.cost - 1
    assert far.cost == far.data.cost


def test_felscale_saur_kindred_hits_opponents_outer_minions():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    left = player.opponent.summon(GOLDSHIRE_FOOTMAN)
    middle = player.opponent.summon(WISP)
    right = player.opponent.summon(TARGET_DUMMY)

    player.give("TLC_903").play()
    game.end_turn()
    game.end_turn()
    player.give("DINO_138").play()

    assert left.zone == Zone.GRAVEYARD
    assert middle.damage == 0
    assert right.zone == Zone.GRAVEYARD


def test_grish_xenomite_gives_stinger_when_damaged():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    xenomite = player.summon("TLC_630")

    xenomite.hit(1)

    assert any(card.id == "TLC_630t" for card in player.hand)


def test_unleash_the_colossus_tracks_exact_two_enemy_damage_and_rewards_grish():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    quest = player.give("TLC_631").play()

    for _ in range(12):
        _set_mana(player)
        player.give("TLC_630t").play(target=player.opponent.hero)

    assert quest.zone == Zone.GRAVEYARD
    assert any(card.id == "TLC_631t" for card in player.hand)


def test_grish_the_colossus_makes_future_exact_two_enemy_damage_deal_two_more():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_631t").play()
    player.give("TLC_630t").play(target=player.opponent.hero)

    assert player.opponent.hero.damage == 4


def test_exterminator_hits_typed_enemy_minion():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.summon(TARGET_DUMMY)

    player.give("TLC_633").play(target=enemy)

    assert enemy.zone == Zone.GRAVEYARD


def test_insect_claw_summons_xenomite_larva_after_hero_attacks():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_833").play()
    player.hero.attack(player.opponent.hero)

    assert any(minion.id == "TLC_903t" and minion.rush for minion in player.field)


def test_grish_burrower_hits_enemy_hero_after_attack():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    burrower = player.summon("TLC_840")
    burrower.turns_in_play = 1
    burrower.num_attacks = 0
    target = player.opponent.summon(TARGET_DUMMY)

    burrower.attack(target)

    assert player.opponent.hero.damage == 2


def test_entomologist_toru_jars_hand_minions_and_releases_them_on_deathrattle():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    _clear_hand(player)
    stored = player.give(TARGET_DUMMY)

    player.give("TLC_841").play()

    jar = player.hand[0]
    assert stored.zone == Zone.SETASIDE
    assert jar.id == "TLC_841t"
    assert jar.cost == 1

    player.summon(jar).destroy()

    assert any(minion.id == TARGET_DUMMY for minion in player.field)


def test_hive_map_offers_followup_if_discovered_fel_spell_is_played_this_turn():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_900").play()
    first = player.choice.cards[0]
    player.choice.choose(first)
    first.play()

    assert player.choice is not None
    assert first not in player.choice.cards


def test_fumigation_damages_target_and_same_race_minions():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    beast1 = player.opponent.summon("DINO_416")
    beast2 = player.opponent.summon("TLC_630")
    other = player.opponent.summon(GOLDSHIRE_FOOTMAN)

    player.give("TLC_901").play(target=beast1)

    assert beast1.damage == 3
    assert beast2.damage == 3
    assert other.damage == 0


def test_insect_infestation_gives_two_stingers_that_damage_and_summon_larvae():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)
    enemy = player.opponent.hero

    player.give("TLC_902").play()
    stingers = [card for card in player.hand if card.id == "TLC_630t"]
    stingers[0].play(target=enemy)

    assert len(stingers) == 2
    assert enemy.damage == 2
    assert any(minion.id == "TLC_903t" for minion in player.field)


def test_xenomite_queen_kindred_gives_hero_temporary_attack():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_630").play()
    game.end_turn()
    game.end_turn()
    player.give("TLC_903").play()

    assert player.hero.atk == 5
    game.end_turn()
    assert player.hero.atk == 0
