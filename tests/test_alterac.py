from utils import *
from fireplace.actions import GainArmor


def test_popsicooler_deathrattle_freezes_two_enemy_minions():
    game = prepare_empty_game()
    popsicooler = game.player1.give("AV_102").play()
    enemy1 = game.player2.summon(WISP)
    enemy2 = game.player2.summon(WISP)

    popsicooler.destroy()

    assert enemy1.frozen
    assert enemy2.frozen


def test_knight_captain_honorable_kill_gains_stats():
    game = prepare_empty_game()
    target = game.player2.summon("CS2_120")
    captain = game.player1.give("AV_131").play(target=target)

    assert target.dead
    assert captain.atk == 6
    assert captain.health == 6


def test_humongous_owl_deathrattle_hits_random_enemy():
    game = prepare_empty_game()
    owl = game.player1.give("AV_704").play()

    owl.destroy()

    assert game.player2.hero.health == 22


def test_captain_galvangar_checks_armor_gained_this_game():
    game = prepare_empty_game()
    player = game.player1
    game.cheat_action(player.hero, [GainArmor(player.hero, 15)])

    galvangar = player.give("AV_145").play()

    assert player.hero.armor == 15
    assert player.armor_gained_this_game == 15
    assert galvangar.atk == 9
    assert galvangar.health == 9
    assert galvangar.charge


def test_magister_dawngrasp_recasts_one_spell_from_each_school():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.player1
    enemy_hero = game.player2.hero

    player.give("CS2_029").play(target=enemy_hero)
    player.give("CS2_024").play(target=enemy_hero)
    assert enemy_hero.health == 21

    player.used_mana = 0
    player.give("AV_200").play()

    assert enemy_hero.health == 12


def test_apothecary_helbrim_adds_random_poison_twice():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.player1

    helbrim = player.give("BAR_324").play()

    assert len(player.hand) == 1
    assert "Poison" in player.hand[0].data.name

    helbrim.destroy()

    assert len(player.hand) == 2
    assert all("Poison" in card.data.name for card in player.hand)
