from utils import *
from fireplace.actions import GainArmor, Hit


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


def test_spammy_arcanist_repeats_while_minions_die():
    game = prepare_empty_game()
    player = game.player1
    friendly_wisp = player.summon(WISP)
    enemy_wisp = game.player2.summon(WISP)
    enemy_crocolisk = game.player2.summon("CS2_120")

    spammy = player.give("AV_222").play()

    assert friendly_wisp.dead
    assert enemy_wisp.dead
    assert enemy_crocolisk.health == 1
    assert spammy.health == 4


def test_core_enhanced_dreadlord_summons_lifesteal_dreadlord():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1

    dreadlord = player.give("CORE_BT_304").play()
    dreadlord.destroy()

    token = player.field.filter(id="BT_304t")[0]
    assert token.atk == 5
    assert token.health == 5
    assert token.lifesteal


def test_vanndar_stormpike_discounts_more_expensive_deck_minions():
    game = prepare_empty_game()
    player = game.player1
    ogre = player.give("CS2_200")
    ogre.shuffle_into_deck()
    spell = player.give(FIREBALL)
    spell.shuffle_into_deck()

    player.give("AV_223").play()

    assert ogre.cost == 3
    assert spell.cost == 4


def test_vanndar_stormpike_requires_every_deck_minion_to_cost_more():
    game = prepare_empty_game()
    player = game.player1
    ogre = player.give("CS2_200")
    ogre.shuffle_into_deck()
    wisp = player.give(WISP)
    wisp.shuffle_into_deck()

    player.give("AV_223").play()

    assert ogre.cost == 6
    assert wisp.cost == 0


def test_core_mistress_of_mixtures_heals_both_heroes():
    game = prepare_empty_game()
    player = game.player1
    opponent = game.player2
    player.hero.set_current_health(20)
    opponent.hero.set_current_health(18)

    mistress = player.give("CORE_CFM_120").play()
    mistress.destroy()

    assert player.hero.health == 24
    assert opponent.hero.health == 22


def test_snowfall_guardian_freezes_all_other_minions():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.player1
    friendly = player.summon(WISP)
    enemy = game.player2.summon("CS2_120")

    guardian = player.give("AV_255").play()

    assert friendly.frozen
    assert enemy.frozen
    assert not guardian.frozen
    assert guardian.atk == 5
    assert guardian.health == 5


def test_core_felsoul_jailer_discards_opponent_minion_then_returns_it():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1
    opponent = game.player2
    minion = opponent.give(WISP)
    spell = opponent.give(FIREBALL)

    jailer = player.give("CORE_CS3_003").play()

    assert minion.zone == Zone.REMOVEDFROMGAME
    assert spell.zone == Zone.HAND

    jailer.destroy()

    assert minion.zone == Zone.HAND
    assert minion in opponent.hand


def test_core_felsoul_jailer_ignores_opponent_hand_without_minions():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1
    opponent = game.player2
    spell = opponent.give(FIREBALL)

    jailer = player.give("CORE_CS3_003").play()
    jailer.destroy()

    assert spell.zone == Zone.HAND
    assert len(opponent.hand) == 2
    assert all(card.type != CardType.MINION for card in opponent.hand)


def test_reflecto_engineer_swaps_attack_and_health_of_hand_minions():
    game = prepare_empty_game()
    player = game.player1
    opponent = game.player2
    friendly_ogre = player.give("CS2_200")
    friendly_spell = player.give(FIREBALL)
    enemy_crocolisk = opponent.give("CS2_120")
    board_minion = player.summon(WISP)

    player.give("AV_256").play()

    assert (friendly_ogre.atk, friendly_ogre.health) == (7, 6)
    assert friendly_spell.cost == 4
    assert (enemy_crocolisk.atk, enemy_crocolisk.health) == (3, 2)
    assert (board_minion.atk, board_minion.health) == (1, 1)


def test_core_prize_vendor_draws_for_both_players_on_play_and_deathrattle():
    game = prepare_empty_game()
    player = game.player1
    opponent = game.player2
    player_card_1 = player.give(WISP)
    player_card_1.shuffle_into_deck()
    player_card_2 = player.give("CS2_120")
    player_card_2.shuffle_into_deck()
    opponent_card_1 = opponent.give(WISP)
    opponent_card_1.shuffle_into_deck()
    opponent_card_2 = opponent.give("CS2_120")
    opponent_card_2.shuffle_into_deck()

    vendor = player.give("CORE_DMF_067").play()

    assert len(player.hand) == 1
    assert len(opponent.hand) == 2

    vendor.destroy()

    assert len(player.hand) == 2
    assert len(opponent.hand) == 3


def test_bearon_glashear_summons_stagguards_for_frost_spells_cast():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.player1
    enemy_hero = game.player2.hero

    player.give("CS2_037").play(target=enemy_hero)
    player.give("CS2_037").play(target=enemy_hero)
    player.give(FIREBALL).play(target=enemy_hero)

    player.used_mana = 0
    player.give("AV_257").play()

    stagguards = player.field.filter(id="AV_257t")
    assert len(stagguards) == 2
    assert all(stag.atk == 3 and stag.health == 4 for stag in stagguards)


def test_frozen_stagguard_freezes_damaged_character():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.player1
    target = game.player2.summon(WISP)

    stagguard = player.summon("AV_257t")
    game.cheat_action(stagguard, [Hit(target, 1)])

    assert target.frozen


def test_core_redscale_dragontamer_draws_a_dragon():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.player1
    dragon = player.give("EX1_043")
    dragon.shuffle_into_deck()
    non_dragon = player.give(WISP)
    non_dragon.shuffle_into_deck()

    dragontamer = player.give("CORE_DMF_194").play()
    dragontamer.destroy()

    assert dragon.zone == Zone.HAND
    assert non_dragon.zone == Zone.DECK


def test_brukan_of_the_elements_chooses_two_battlecry_powers():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.player1
    opponent = game.player2

    player.give("AV_258").play()
    choice = player.choice
    choice.choose(choice.cards.filter(id="AV_258t")[0])
    choice = player.choice
    choice.choose(choice.cards.filter(id="AV_258t3")[0])

    guardians = player.field.filter(id="AV_258t6")
    assert len(guardians) == 2
    assert all(guardian.taunt and guardian.atk == 2 and guardian.health == 3 for guardian in guardians)
    assert opponent.hero.health == 24
    assert player.hero.id == "AV_258"
    assert player.hero.armor == 5
    assert player.hero_power.id == "AV_258pt7"


def test_brukan_command_the_elements_uses_current_invocation():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.player1

    player.give("AV_258").play()
    choice = player.choice
    choice.choose(choice.cards.filter(id="AV_258t2")[0])
    choice = player.choice
    choice.choose(choice.cards.filter(id="AV_258t3")[0])

    player.hero_power.use()

    guardians = player.field.filter(id="AV_258t6")
    assert len(guardians) == 2


def test_core_greybough_grants_summon_greybough_deathrattle():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.player1
    recipient = player.summon(WISP)

    greybough = player.give("CORE_DMF_734").play()
    greybough.destroy()

    assert recipient.has_deathrattle

    recipient.destroy()

    assert player.field.filter(id="DMF_734")


def test_sleetbreaker_adds_windchill_to_hand():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.player1

    player.give("AV_260").play()

    assert player.hand.filter(id="AV_266")


def test_core_bloodmage_thalnos_draws_on_deathrattle():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.player1
    drawn = player.give(WISP)
    drawn.shuffle_into_deck()

    thalnos = player.give("CORE_EX1_012").play()
    thalnos.destroy()

    assert drawn.zone == Zone.HAND


def test_warden_of_chains_buffs_when_holding_costly_demon():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    player.give("CS2_064")

    warden = player.give("AV_262").play()

    assert warden.taunt
    assert warden.atk == 3
    assert warden.health == 8


def test_warden_of_chains_does_not_buff_without_costly_demon():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    player.give(WISP)

    warden = player.give("AV_262").play()

    assert warden.taunt
    assert warden.atk == 2
    assert warden.health == 6


def test_core_sylvanas_steals_enemy_minion_on_deathrattle():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.player1
    enemy = game.player2.summon(WISP)

    sylvanas = player.give("CORE_EX1_016").play()
    sylvanas.destroy()

    assert enemy.controller is player
    assert enemy in player.field


def test_caria_felsoul_transforms_into_six_six_deck_demon_copy():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    demon = player.give("CS2_064")
    demon.shuffle_into_deck()

    caria = player.give("AV_267").play()

    assert caria.morphed.id == "CS2_064"
    assert caria.morphed.atk == 6
    assert caria.morphed.health == 6


def test_caria_felsoul_does_not_transform_without_deck_demon():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    player.give(WISP).shuffle_into_deck()

    caria = player.give("AV_267").play()

    assert caria.id == "AV_267"
    assert not caria.morphed


def test_core_loot_hoarder_draws_on_deathrattle():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.player1
    drawn = player.give(WISP)
    drawn.shuffle_into_deck()

    hoarder = player.give("CORE_EX1_096").play()
    hoarder.destroy()

    assert drawn.zone == Zone.HAND
