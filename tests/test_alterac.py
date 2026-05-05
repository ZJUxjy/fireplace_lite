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


def test_rokkara_the_valorous_equips_unstoppable_force():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.player1

    player.give("AV_202").play()

    assert player.weapon.id == "AV_202t2"
    assert player.weapon.atk == 5
    assert player.weapon.durability == 2


def test_razorboar_summons_cheap_deathrattle_minion_from_hand():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    player.give("BAR_325")
    cheap_deathrattle = player.give("BAR_026")
    player.give("CS2_142")

    razorboar = player.hand[0].play()
    razorboar.destroy()

    assert cheap_deathrattle.zone == Zone.PLAY
    assert cheap_deathrattle in player.field
    assert all(card.id != "CS2_142" for card in player.field)


def test_shadowcrafter_scabbs_bounces_minions_and_summons_shadows():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.player1
    friendly = player.summon("CS2_142")
    enemy = game.player2.summon("CS2_231")

    player.give("AV_203").play()

    shadows = player.field.filter(id="AV_203t")
    assert friendly.zone == Zone.HAND
    assert enemy.zone == Zone.HAND
    assert len(shadows) == 2
    assert all(shadow.atk == 4 and shadow.health == 2 and shadow.stealthed for shadow in shadows)


def test_razorfen_beastmaster_summons_four_or_less_deathrattle_from_hand():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    player.give("BAR_326")
    four_cost_deathrattle = player.give("BAR_027")
    player.give("CS2_142")

    beastmaster = player.hand[0].play()
    beastmaster.destroy()

    assert four_cost_deathrattle.zone == Zone.PLAY
    assert four_cost_deathrattle in player.field
    assert all(card.id != "CS2_142" for card in player.field)


def test_kurtrus_demon_render_uses_hero_attacks_this_game():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    enemy_hero = game.player2.hero
    player.give("CS2_091").play()

    player.hero.attack(enemy_hero)
    player.hero.num_attacks = 0
    player.hero.attack(enemy_hero)
    assert player.hero_attacks_this_game == 2

    player.give("AV_204").play()

    shriekers = player.field.filter(id="AV_204t2")
    assert len(shriekers) == 2
    assert all(shrieker.atk == 3 and shrieker.health == 4 and shrieker.rush for shrieker in shriekers)


def test_tuskpiercer_deathrattle_draws_deathrattle_minion():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    deathrattle_minion = player.give("BAR_026")
    non_deathrattle_minion = player.give("CS2_142")
    deathrattle_minion.shuffle_into_deck()
    non_deathrattle_minion.shuffle_into_deck()

    weapon = player.give("BAR_330").play()
    weapon.destroy()

    assert deathrattle_minion.zone == Zone.HAND
    assert non_deathrattle_minion.zone == Zone.DECK


def test_wildheart_guff_sets_max_mana_to_twenty_gains_mana_and_draws():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.player1
    drawn = player.give("CS2_231")
    drawn.shuffle_into_deck()

    player.give("AV_205").play()

    assert player.max_resources == 20
    assert player.max_mana == 11
    assert drawn.zone == Zone.HAND


def test_thickhide_kodo_deathrattle_gains_armor():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.player1

    kodo = player.give("BAR_535").play()
    kodo.destroy()

    assert player.hero.armor == 5
    assert player.armor_gained_this_game == 5


def test_lightforged_cariel_damages_enemies_and_equips_weapon():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.player1
    opponent = player.opponent
    enemy_minion = opponent.summon("CS2_182")

    player.give("AV_206").play()

    assert opponent.hero.health == 28
    assert enemy_minion.damage == 2
    assert player.weapon.id == "AV_146"
    assert player.weapon.atk == 2
    assert player.weapon.durability == 5


def test_spawnpool_forager_deathrattle_summons_tinyfin():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.player1

    forager = player.give("BAR_751").play()
    forager.destroy()

    tinyfins = player.field.filter(id="BAR_751t")
    assert len(tinyfins) == 1
    assert tinyfins[0].atk == 1
    assert tinyfins[0].health == 1


def test_xyrella_the_devout_triggers_friendly_dead_minion_deathrattles():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.player1
    berserker = player.give("BAR_027").play()
    berserker.destroy()
    assert player.hero.health == 25
    assert berserker.zone == Zone.GRAVEYARD

    player.used_mana = 0
    player.give("AV_207").play()

    assert player.hero.health == 20


def test_kabal_outfitter_battlecry_and_deathrattle_buff_other_friendly_minion():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.player1
    target = player.summon("CS2_231")

    outfitter = player.give("BAR_915").play()

    assert target.atk == 2
    assert target.health == 2

    outfitter.destroy()

    assert target.atk == 3
    assert target.health == 3


def test_pathmaker_casts_other_choice_from_last_choose_one_spell():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.player1
    drawn = player.give("CS2_231")
    drawn.shuffle_into_deck()

    nourish = player.give("EX1_164")
    nourish.play(choose="EX1_164a")
    assert player.max_mana == 10
    assert drawn.zone == Zone.DECK

    player.used_mana = 0
    player.give("AV_210").play()

    assert drawn.zone == Zone.HAND


def test_core_thickhide_kodo_deathrattle_gains_armor():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.player1

    kodo = player.give("CORE_BAR_535").play()
    kodo.destroy()

    assert player.hero.armor == 5
    assert player.armor_gained_this_game == 5


def test_ram_commander_adds_two_rams_to_hand():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.player1

    player.give("AV_219").play()

    rams = player.hand.filter(id="AV_219t")
    assert len(rams) == 2
    assert all(ram.atk == 1 and ram.health == 1 and ram.rush for ram in rams)


def test_core_replicating_menace_summons_three_microbots():
    game = prepare_empty_game()
    player = game.player1

    menace = player.give("CORE_BOT_312").play()
    menace.destroy()

    microbots = player.field.filter(id="BOT_312t")
    assert len(microbots) == 3
    assert all(bot.atk == 1 and bot.health == 1 for bot in microbots)
