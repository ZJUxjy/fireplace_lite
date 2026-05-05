from utils import *
from fireplace.cards.utils import LICH_KING_CARDS
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


def test_balinda_stonehearth_draws_two_spells_and_swaps_costs_with_stats():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.player1
    first_spell = player.give("CS2_024")
    second_spell = player.give("CS2_029")
    original_costs = sorted([first_spell.cost, second_spell.cost])
    first_spell.shuffle_into_deck()
    second_spell.shuffle_into_deck()

    balinda = player.give("AV_284").play()

    assert first_spell.zone == Zone.HAND
    assert second_spell.zone == Zone.HAND
    assert first_spell.cost == 5
    assert second_spell.cost == 5
    assert sorted([balinda.atk, balinda.health]) == original_costs


def test_core_cairne_bloodhoof_summons_baine_on_deathrattle():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.player1

    cairne = player.give("CORE_EX1_110").play()
    cairne.destroy()

    assert player.field.filter(id="EX1_110t")


def test_felwalker_casts_highest_cost_fel_spell_from_hand():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    cheap_fel = player.give("BT_035")
    expensive_fel = player.give("BT_235")

    player.give("AV_286").play()

    assert expensive_fel.zone == Zone.GRAVEYARD
    assert cheap_fel.zone == Zone.HAND


def test_core_tirion_fordring_equips_ashbringer_on_deathrattle():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.player1

    tirion = player.give("CORE_EX1_383").play()
    tirion.destroy()

    assert player.weapon.id == "EX1_383t"
    assert player.weapon.atk == 5
    assert player.weapon.durability == 3


def test_clawfury_adept_gives_other_friendly_characters_attack_this_turn():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.player1
    minion = player.summon(WISP)
    base_hero_atk = player.hero.atk

    adept = player.give("AV_294").play()

    assert player.hero.atk == base_hero_atk + 1
    assert minion.atk == 2
    assert adept.atk == 2

    game.end_turn()

    assert player.hero.atk == base_hero_atk
    assert minion.atk == 1


def test_core_savannah_highmane_summons_two_hyenas_on_deathrattle():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.player1

    highmane = player.give("CORE_EX1_534").play()
    highmane.destroy()

    hyenas = player.field.filter(id="EX1_534t")
    assert len(hyenas) == 2


def test_pride_seeker_discounts_next_choose_one_card():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.player1
    choose_one = player.give("EX1_164")
    other_card = player.give(WISP)

    player.give("AV_296").play()

    assert choose_one.cost == choose_one.data.cost - 2
    assert other_card.cost == other_card.data.cost

    choose_one.play(choose="EX1_164a")

    assert not any(buff.id == "AV_296e" for buff in player.buffs)


def test_core_nerubian_egg_summons_nerubian_on_deathrattle():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.player1

    egg = player.give("CORE_FP1_007").play()
    egg.destroy()

    nerubians = player.field.filter(id="FP1_007t")
    assert len(nerubians) == 1


def test_grave_defiler_copies_chosen_fel_spell_from_hand():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1
    fel_spell = player.give("EX1_596")

    player.give("AV_308").play()
    choice = player.choice
    choice.choose(fel_spell)

    copies = player.hand.filter(id="EX1_596")
    assert len(copies) == 2


def test_core_webspinner_adds_random_beast_on_deathrattle():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.player1

    webspinner = player.give("CORE_FP1_011").play()
    webspinner.destroy()

    assert player.hand
    assert Race.BEAST in player.hand[0].races


def test_sacrificial_summoner_destroys_friendly_minion_and_summons_plus_one_cost():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1
    sacrifice = player.summon("CS2_122")
    summoned = player.give("CS2_182")
    summoned.shuffle_into_deck()

    player.give("AV_312").play(target=sacrifice)

    assert sacrifice.zone == Zone.GRAVEYARD
    assert summoned.zone == Zone.PLAY


def test_core_voidcaller_summons_demon_from_hand_on_deathrattle():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1
    demon = player.give("CS2_064")

    voidcaller = player.give("CORE_FP1_022").play()
    voidcaller.destroy()

    assert demon.zone == Zone.PLAY
    assert demon in player.field


def test_hollow_abomination_honorable_kill_gains_minion_attack():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1
    enemy = game.player2
    dying_minion = enemy.summon(WISP)
    surviving_minion = enemy.summon("CS2_120")

    abomination = player.give("AV_313").play()

    assert dying_minion.dead
    assert surviving_minion.health == 2
    assert abomination.atk == 3


def test_core_woodcutters_axe_buffs_random_friendly_minion_on_deathrattle():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.player1
    minion = player.summon(WISP)

    weapon = player.give("CORE_GIL_653").play()
    weapon.destroy()

    assert minion.atk == 3
    assert minion.health == 2
    assert not minion.rush


def test_dreadlich_tamsin_damages_all_minions_and_draws_fel_rifts():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1
    opponent = game.player2
    friendly = player.summon(WISP)
    enemy = opponent.summon("CS2_120")

    player.give("AV_316").play()

    assert friendly.dead
    assert enemy.dead
    assert player.hero.id == "AV_316"
    assert player.hero.armor == 5
    assert player.hero_power.id == "AV_316hp"
    dread_imps = player.field.filter(id="AV_316t")
    assert len(dread_imps) == 3
    assert all(imp.atk == 3 and imp.health == 3 for imp in dread_imps)


def test_core_rotten_applebaum_restores_six_health_on_deathrattle():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.player1
    game.cheat_action(player.hero, [Hit(player.hero, 10)])

    applebaum = player.give("CORE_GIL_667").play()
    applebaum.destroy()

    assert player.hero.health == 26


def test_scrapsmith_adds_two_scrappy_grunts_to_hand():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.player1

    player.give("AV_323").play()

    grunts = player.hand.filter(id="AV_323t")
    assert len(grunts) == 2
    assert all(grunt.atk == 2 and grunt.health == 4 and grunt.taunt for grunt in grunts)


def test_core_explosive_sheep_deathrattle_damages_all_minions():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.player1
    opponent = game.player2
    friendly = player.summon("CS2_120")
    enemy = opponent.summon("CS2_120")

    sheep = player.give("CORE_GVG_076").play()
    sheep.destroy()

    assert friendly.health == 1
    assert enemy.health == 1


def test_ram_tamer_gains_stats_and_stealth_with_secret():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.player1
    player.give("EX1_554").play()

    ram_tamer = player.give("AV_335").play()

    assert ram_tamer.atk == 5
    assert ram_tamer.health == 4
    assert ram_tamer.stealthed


def test_core_skelemancer_summons_skeleton_on_opponent_turn_deathrattle():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.player1
    skelemancer = player.give("CORE_ICC_019").play()

    game.end_turn()
    skelemancer.destroy()

    skeletons = player.field.filter(id="ICC_019t")
    assert len(skeletons) == 1
    assert skeletons[0].atk == 8
    assert skeletons[0].health == 8


def test_wing_commander_ichman_summons_rushing_beast_and_repeats_on_kill():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.player1
    opponent = game.player2
    first_beast = player.give("CS2_120")
    first_beast.shuffle_into_deck()

    player.give("AV_336").play()

    beast = player.field.filter(id="CS2_120")[0]
    assert beast.rush
    assert first_beast.zone == Zone.PLAY

    second_beast = player.give("CS2_120")
    second_beast.shuffle_into_deck()
    target = opponent.summon(WISP)

    beast.attack(target)

    assert target.dead
    assert second_beast.zone == Zone.PLAY
    assert second_beast.rush


def test_core_exploding_bloatbat_deathrattle_damages_enemy_minions_only():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.player1
    opponent = game.player2
    friendly = player.summon("CS2_120")
    enemy = opponent.summon("CS2_120")

    bloatbat = player.give("CORE_ICC_021").play()
    bloatbat.destroy()

    assert friendly.health == 3
    assert enemy.health == 1


def test_stonehearth_vindicator_draws_cheap_spell_and_discounts_this_turn():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.player1
    cheap_spell = player.give("CS2_087")
    cheap_spell.shuffle_into_deck()
    expensive_spell = player.give("CS2_092")
    expensive_spell.shuffle_into_deck()

    player.give("AV_343").play()

    assert cheap_spell.zone == Zone.HAND
    assert cheap_spell.cost == 0
    assert expensive_spell.zone == Zone.DECK

    game.end_turn()

    assert cheap_spell.cost == cheap_spell.data.cost


def test_core_rattling_rascal_summons_skeleton_for_each_side():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.player1
    opponent = game.player2

    rascal = player.give("CORE_ICC_025").play()
    assert len(player.field.filter(id="ICC_025t")) == 1

    rascal.destroy()

    assert len(opponent.field.filter(id="ICC_025t")) == 1


def test_cerathine_replaces_hand_and_deck_minions_with_discounted_other_class_minions():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.player1
    hand_minion = player.give(WISP)
    deck_minion = player.give("CS2_120")
    deck_minion.shuffle_into_deck()
    spell = player.give("CS2_072")
    spell.shuffle_into_deck()

    player.give("AV_403").play()

    assert hand_minion.morphed.type == CardType.MINION
    assert CardClass.ROGUE not in hand_minion.morphed.data.classes
    assert CardClass.NEUTRAL not in hand_minion.morphed.data.classes
    assert hand_minion.morphed.cost == max(0, hand_minion.morphed.data.cost - 2)
    assert deck_minion.morphed.type == CardType.MINION
    assert CardClass.ROGUE not in deck_minion.morphed.data.classes
    assert CardClass.NEUTRAL not in deck_minion.morphed.data.classes
    assert spell.zone == Zone.DECK
    assert spell.morphed is None


def test_core_bone_drake_adds_random_dragon_on_deathrattle():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.player1

    bone_drake = player.give("CORE_ICC_027").play()
    bone_drake.destroy()

    assert player.hand
    assert Race.DRAGON in player.hand[0].races


def test_double_agent_summons_copy_when_holding_card_from_another_class():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.player1
    player.give(FIREBALL)

    double_agent = player.give("AV_711").play()

    agents = player.field.filter(id="AV_711")
    assert len(agents) == 2
    assert double_agent in agents
    assert all(agent.atk == 3 and agent.health == 3 for agent in agents)


def test_double_agent_ignores_neutral_cards_in_hand():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.player1
    player.give(WISP)

    player.give("AV_711").play()

    assert len(player.field.filter(id="AV_711")) == 1


def test_core_arrogant_crusader_summons_ghoul_on_opponent_turn_deathrattle():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.player1
    crusader = player.give("CORE_ICC_034").play()

    game.end_turn()
    crusader.destroy()

    ghouls = player.field.filter(id="ICC_900t")
    assert len(ghouls) == 1
    assert ghouls[0].atk == 2
    assert ghouls[0].health == 2


def test_core_arrogant_crusader_does_not_summon_ghoul_on_own_turn():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.player1
    crusader = player.give("CORE_ICC_034").play()

    crusader.destroy()

    assert not player.field.filter(id="ICC_900t")


def test_pack_kodo_discovers_beast_secret_or_weapon():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.player1

    player.give("BAR_030").play()

    assert player.choice is not None
    assert len(player.choice.cards) == 3
    assert all(
        (card.type == CardType.MINION and Race.BEAST in card.races)
        or card.tags.get(GameTag.SECRET)
        or card.type == CardType.WEAPON
        for card in player.choice.cards
    )

    picked = player.choice.cards[0]
    player.choice.choose(picked)

    assert picked.zone == Zone.HAND


def test_core_mountainfire_armor_gains_armor_on_opponent_turn_deathrattle():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.player1
    armor = player.give("CORE_ICC_062").play()

    game.end_turn()
    armor.destroy()

    assert player.hero.armor == 6


def test_core_mountainfire_armor_does_not_gain_armor_on_own_turn():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.player1
    armor = player.give("CORE_ICC_062").play()

    armor.destroy()

    assert player.hero.armor == 0


def test_warsong_wrangler_discovers_deck_beast_and_buffs_all_copies():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.player1
    deck_beast = player.give("CS2_120")
    deck_beast.shuffle_into_deck()
    hand_copy = player.give("CS2_120")
    board_copy = player.summon("CS2_120")
    non_beast = player.give(WISP)
    non_beast.shuffle_into_deck()

    player.give("BAR_037").play()

    assert player.choice is not None
    assert deck_beast in player.choice.cards
    player.choice.choose(deck_beast)

    assert deck_beast.zone == Zone.HAND
    assert deck_beast.atk == 4
    assert deck_beast.health == 4
    assert hand_copy.atk == 4
    assert hand_copy.health == 4
    assert board_copy.atk == 4
    assert board_copy.health == 4
    assert non_beast.zone == Zone.DECK


def test_core_blood_razor_battlecry_and_deathrattle_damage_all_minions():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.player1
    friendly = player.summon("CS2_120")
    enemy = game.player2.summon("CS2_120")

    razor = player.give("CORE_ICC_064").play()

    assert friendly.damage == 1
    assert enemy.damage == 1

    razor.destroy()

    assert friendly.damage == 2
    assert enemy.damage == 2


def test_primordial_protector_draws_highest_cost_spell_and_summons_same_cost_minion():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.player1
    low_spell = player.give("CS2_024")
    low_spell.shuffle_into_deck()
    high_spell = player.give(FIREBALL)
    high_spell.shuffle_into_deck()

    protector = player.give("BAR_042").play()

    assert high_spell.zone == Zone.HAND
    assert low_spell.zone == Zone.DECK
    summoned = [minion for minion in player.field if minion is not protector][0]
    assert summoned.type == CardType.MINION
    assert summoned.cost == high_spell.cost


def test_core_bone_baron_adds_two_skeletons_on_deathrattle():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.player1

    baron = player.give("CORE_ICC_065").play()
    baron.destroy()

    skeletons = player.hand.filter(id="ICC_026t")
    assert len(skeletons) == 2
    assert all(skeleton.atk == 1 and skeleton.health == 1 for skeleton in skeletons)


def test_arid_stormer_gains_rush_and_windfury_after_elemental_previous_turn():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.player1
    player.give("CS2_118").play()

    game.end_turn()
    game.end_turn()

    stormer = player.give("BAR_045").play()

    assert stormer.rush
    assert stormer.windfury


def test_arid_stormer_without_previous_turn_elemental_keeps_base_keywords():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.player1

    stormer = player.give("BAR_045").play()

    assert not stormer.rush
    assert not stormer.windfury


def test_core_vryghoul_summons_ghoul_on_opponent_turn_deathrattle():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.player1
    vryghoul = player.give("CORE_ICC_067").play()

    game.end_turn()
    vryghoul.destroy()

    ghouls = player.field.filter(id="ICC_900t")
    assert len(ghouls) == 1
    assert ghouls[0].atk == 2
    assert ghouls[0].health == 2


def test_core_vryghoul_does_not_summon_ghoul_on_own_turn():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.player1
    vryghoul = player.give("CORE_ICC_067").play()

    vryghoul.destroy()

    assert not player.field.filter(id="ICC_900t")


def test_hog_rancher_summons_rushing_hog():
    game = prepare_empty_game()
    player = game.player1

    player.give("BAR_060").play()

    hogs = player.field.filter(id="BAR_060t")
    assert len(hogs) == 1
    assert hogs[0].atk == 2
    assert hogs[0].health == 1
    assert hogs[0].rush


def test_core_ticking_abomination_deathrattle_damages_friendly_minions():
    game = prepare_empty_game()
    player = game.player1
    friendly = player.summon("CS2_200")
    enemy = game.player2.summon("CS2_200")

    abomination = player.give("CORE_ICC_099").play()
    abomination.destroy()

    assert friendly.damage == 5
    assert enemy.damage == 0


def test_ratchet_privateer_gives_weapon_attack():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.player1
    weapon = player.give("CS2_091").play()

    player.give("BAR_061").play()

    assert player.weapon is weapon
    assert weapon.atk == 2
    assert weapon.durability == 4


def test_core_obsidian_statue_deathrattle_destroys_random_enemy_minion():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.player1
    friendly = player.summon("CS2_200")
    enemy = game.player2.summon("CS2_200")

    statue = player.give("CORE_ICC_214").play()
    statue.destroy()

    assert enemy.dead
    assert not friendly.dead


def test_lushwater_murcenary_buffs_itself_as_controlled_murloc():
    game = prepare_empty_game()
    player = game.player1

    murcenary = player.give("BAR_062").play()

    assert murcenary.atk == 4
    assert murcenary.health == 3


def test_core_shallow_gravedigger_deathrattle_adds_deathrattle_minion():
    game = prepare_empty_game()
    player = game.player1
    gravedigger = player.give("CORE_ICC_702").play()

    gravedigger.destroy()

    assert len(player.hand) == 1
    card = player.hand[0]
    assert card.type == CardType.MINION
    assert card.data.tags.get(GameTag.DEATHRATTLE)


def test_talented_arcanist_gives_next_spell_spell_damage():
    game = prepare_empty_game()
    player = game.player1
    enemy = game.player2.summon("CS2_200")

    player.give("BAR_064").play()
    assert player.spellpower == 2

    player.give(MOONFIRE).play(target=enemy)

    assert enemy.damage == 3
    assert player.spellpower == 0


def test_core_meat_wagon_deathrattle_summons_lower_attack_minion_from_deck():
    game = prepare_empty_game()
    player = game.player1
    wisp = player.card(WISP, zone=Zone.DECK)
    ogre = player.card("CS2_200", zone=Zone.DECK)
    wagon = player.give("CORE_ICC_812").play()
    wagon.buff(wagon, "BAR_062e")

    wagon.destroy()

    assert wisp in player.field
    assert ogre in player.deck


def test_venomous_scorpid_discovers_spell():
    game = prepare_empty_game()
    player = game.player1

    scorpid = player.give("BAR_065").play()

    assert scorpid.poisonous
    assert player.choice
    assert len(player.choice.cards) == 3
    assert all(card.type == CardType.SPELL for card in player.choice.cards)


def test_core_abominable_bowman_summons_friendly_dead_beast_copy():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.player1
    beast = player.summon("CS2_171")
    beast.destroy()

    bowman = player.give("CORE_ICC_825").play()
    bowman.destroy()

    summoned = player.field.filter(id="CS2_171")
    assert len(summoned) == 1
    assert summoned[0] is not beast


def test_injured_marauder_damages_itself():
    game = prepare_empty_game()
    player = game.player1

    marauder = player.give("BAR_069").play()

    assert marauder.taunt
    assert marauder.damage == 6
    assert marauder.health == 4


def test_core_hadronox_summons_friendly_dead_taunt_minions():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.player1
    taunt = player.summon(GOLDSHIRE_FOOTMAN)
    non_taunt = player.summon(WISP)
    taunt.destroy()
    non_taunt.destroy()

    hadronox = player.give("CORE_ICC_835").play()
    hadronox.destroy()

    assert len(player.field.filter(id=GOLDSHIRE_FOOTMAN)) == 1
    assert not player.field.filter(id=WISP)


def test_kargal_battlescar_summons_lookouts_for_summoned_watch_posts():
    game = prepare_empty_game()
    player = game.player1
    player.summon("BAR_074")
    player.summon("BAR_076")

    player.give("BAR_077").play()

    lookouts = player.field.filter(id="BAR_077t")
    assert len(lookouts) == 2
    assert all(lookout.atk == 5 and lookout.health == 5 for lookout in lookouts)


def test_core_arfus_deathrattle_adds_lich_king_card():
    game = prepare_empty_game()
    player = game.player1

    arfus = player.give("CORE_ICC_854").play()
    arfus.destroy()

    assert len(player.hand) == 1
    assert player.hand[0].id in LICH_KING_CARDS
