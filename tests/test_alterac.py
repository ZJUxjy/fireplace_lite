from utils import *
import pytest

from fireplace.cards.utils import LICH_KING_CARDS
from fireplace.actions import GainArmor, Hit, Reveal
from fireplace.exceptions import GameOver


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


def test_kazakus_golem_shaper_builds_custom_golem_without_four_cost_deck_cards():
    game = prepare_empty_game()
    player = game.player1

    player.give("BAR_079").play()
    choice = player.choice
    assert choice
    choice.choose(next(card for card in choice.cards if card.id == "BAR_079_m1"))
    choice.choose(next(card for card in choice.cards if card.id == "BAR_079t4"))
    choice.choose(next(card for card in choice.cards if card.id == "BAR_079t5"))

    golem = player.hand[0]
    assert golem.id == "BAR_079_m1"
    assert golem.custom_card
    assert golem.cost == 1
    assert golem.atk == 1
    assert golem.health == 1
    assert golem.rush
    assert golem.taunt


def test_kazakus_golem_shaper_requires_no_four_cost_deck_cards():
    game = prepare_empty_game()
    player = game.player1
    player.card("CS2_182", zone=Zone.DECK)

    player.give("BAR_079").play()

    assert player.choice is None


def test_core_tomb_pillager_deathrattle_adds_coin():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.player1

    pillager = player.give("CORE_LOE_012").play()
    pillager.destroy()

    assert len(player.hand) == 1
    assert player.hand[0].id == THE_COIN


def test_shadow_hunter_voljin_swaps_minion_with_owner_hand_minion():
    game = prepare_empty_game()
    player = game.player1
    target = player.summon(WISP)
    hand_minion = player.give("CS2_200")

    player.give("BAR_080").play(target=target)

    assert hand_minion in player.field
    assert target in player.hand
    assert hand_minion not in player.hand
    assert target not in player.field


def test_core_mounted_raptor_deathrattle_summons_one_cost_minion():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.player1

    raptor = player.give("CORE_LOE_050").play()
    raptor.destroy()

    assert len(player.field) == 1
    assert player.field[0].cost == 1


def test_southsea_scoundrel_discovers_opponent_deck_card_for_both_players():
    game = prepare_empty_game()
    player = game.player1
    opponent = game.player2
    first = opponent.card(WISP, zone=Zone.DECK)
    second = opponent.card("CS2_182", zone=Zone.DECK)

    player.give("BAR_081").play()

    assert player.choice is not None
    assert set(player.choice.cards) == {first, second}
    player.choice.choose(first)

    assert first in opponent.hand
    assert second in opponent.deck
    assert len(player.hand) == 1
    assert player.hand[0].id == first.id


def test_core_plated_beetle_deathrattle_gains_armor():
    game = prepare_empty_game()
    player = game.player1

    beetle = player.give("CORE_LOOT_413").play()
    beetle.destroy()

    assert player.hero.armor == 3


def test_void_flayer_hits_random_enemy_minions_for_each_spell_in_hand():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.player1
    opponent = game.player2
    first = opponent.summon("CS2_200")
    second = opponent.summon("CS2_200")
    player.give("CS2_008")
    player.give("CS2_029")
    player.give(WISP)

    player.give("BAR_307").play()

    assert first.damage + second.damage == 2


def test_core_incriminating_psychic_copies_two_random_opponent_hand_cards():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.player1
    opponent = game.player2
    opponent.hand.clear()
    first = opponent.give(WISP)
    second = opponent.give("CS2_182")

    psychic = player.give("CORE_MAW_022").play()
    psychic.destroy()

    assert sorted(card.id for card in player.hand) == sorted([first.id, second.id])
    assert first in opponent.hand
    assert second in opponent.hand
    assert all(card is not first and card is not second for card in player.hand)


def test_priest_of_anshe_gains_stats_after_restoring_health_this_turn():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.player1
    player.hero.damage = 3
    game.cheat_action(player.hero, [Heal(player.hero, 1)])

    priest = player.give("BAR_313").play()

    assert priest.atk == 8
    assert priest.health == 8


def test_core_darkshire_librarian_discards_random_card_and_draws_on_deathrattle():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1
    player.hand.clear()
    discarded = player.give(WISP)
    drawn = player.card("CS2_182", zone=Zone.DECK)

    librarian = player.give("CORE_OG_109").play()

    assert discarded.zone == Zone.REMOVEDFROMGAME
    assert discarded.discarded
    assert not player.hand

    librarian.destroy()

    assert drawn in player.hand


def test_serena_bloodfeather_steals_stats_until_higher_than_target():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.player1
    target = game.player2.summon("CS2_200")

    serena = player.give("BAR_315").play(target=target)

    assert serena.atk == 4
    assert serena.health == 5
    assert target.atk == 3
    assert target.health == 3


def test_core_possessed_villager_deathrattle_summons_shadowbeast():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1

    villager = player.give("CORE_OG_241").play()
    villager.destroy()

    assert len(player.field) == 1
    assert player.field[0].id == "OG_241a"
    assert player.field[0].atk == 1
    assert player.field[0].health == 1


def test_oil_rig_ambusher_deals_two_or_four_if_entered_hand_this_turn():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.player1
    target = game.player2.summon("CS2_200")

    ambusher = player.give("BAR_316")
    ambusher.turn_drawn = game.turn
    ambusher.play(target=target)
    assert target.damage == 4

    old_ambusher = player.give("BAR_316")
    old_ambusher.turn_drawn = game.turn - 1
    old_ambusher.play(target=target)
    assert target.damage == 6


def test_core_bog_beast_deathrattle_summons_muckmare():
    game = prepare_empty_game()
    player = game.player1

    bog_beast = player.give("CORE_REV_012").play()
    bog_beast.destroy()

    assert len(player.field) == 1
    assert player.field[0].id == "REV_012t"
    assert player.field[0].atk == 2
    assert player.field[0].health == 4
    assert player.field[0].taunt


def test_death_speaker_blackthorn_summons_three_cheap_deathrattle_minions_from_deck():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    first = player.card("CORE_LOOT_413", zone=Zone.DECK)
    second = player.card("CORE_FP1_011", zone=Zone.DECK)
    third = player.card("CORE_OG_241", zone=Zone.DECK)
    expensive = player.card("CORE_REV_015", zone=Zone.DECK)
    non_deathrattle = player.card(WISP, zone=Zone.DECK)

    blackthorn = player.give("BAR_329").play()

    assert set(player.field) == {blackthorn, first, second, third}
    assert expensive in player.deck
    assert non_deathrattle in player.deck


def test_core_masked_reveler_summons_two_two_copy_of_other_deck_minion():
    game = prepare_empty_game()
    player = game.player1
    deck_minion = player.card("CS2_200", zone=Zone.DECK)

    reveler = player.give("CORE_REV_015").play()
    reveler.destroy()

    assert deck_minion in player.deck
    assert len(player.field) == 1
    copy = player.field[0]
    assert copy.id == deck_minion.id
    assert copy is not deck_minion
    assert copy.atk == 2
    assert copy.health == 2


def test_kurtrus_ashfallen_attacks_left_and_right_enemy_minions():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    left = player.opponent.summon(TARGET_DUMMY)
    middle = player.opponent.summon("EX1_572")
    right = player.opponent.summon(TARGET_DUMMY)
    player.give(WISP)
    player.give("BAR_333").play()

    assert left.zone == Zone.GRAVEYARD
    assert middle.health == middle.max_health
    assert right.zone == Zone.GRAVEYARD


def test_kurtrus_outcast_is_immune_until_turn_end():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.player1
    left = player.opponent.summon("EX1_572")
    right = player.opponent.summon("EX1_572")

    kurtrus = player.give("BAR_333").play()

    assert kurtrus.cant_be_damaged
    assert kurtrus.health == kurtrus.max_health
    assert left.health == left.max_health - kurtrus.atk
    assert right.health == right.max_health - kurtrus.atk

    game.end_turn()

    assert not kurtrus.cant_be_damaged


def test_core_sinrunner_deathrattle_destroys_random_enemy_minion():
    game = prepare_empty_game()
    player = game.player1
    target = player.opponent.summon("CS2_182")
    other = player.summon(WISP)

    sinrunner = player.give("CORE_REV_251").play()
    sinrunner.destroy()

    assert target.zone == Zone.GRAVEYARD
    assert other.zone == Zone.PLAY


def test_overlord_saurfang_resurrects_two_friendly_frenzy_minions_and_damages_others():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.player1
    first = player.card("BAR_020", zone=Zone.GRAVEYARD)
    second = player.card("BAR_021", zone=Zone.GRAVEYARD)
    non_frenzy = player.card(WISP, zone=Zone.GRAVEYARD)
    friendly = player.summon("CS2_200")
    enemy = player.opponent.summon("CS2_200")

    saurfang = player.give("BAR_334").play()

    assert first.zone == Zone.PLAY
    assert second.zone == Zone.PLAY
    assert non_frenzy.zone == Zone.GRAVEYARD
    assert saurfang.health == saurfang.max_health
    assert first.health == first.max_health - 1
    assert second.health == second.max_health - 1
    assert friendly.health == friendly.max_health - 1
    assert enemy.health == enemy.max_health - 1


def test_core_batty_guest_deathrattle_summons_two_one_bat():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.player1

    guest = player.give("CORE_REV_356").play()
    guest.destroy()

    assert len(player.field) == 1
    bat = player.field[0]
    assert bat.id == "REV_350t"
    assert bat.atk == 2
    assert bat.health == 1


def test_reckless_apprentice_fires_hero_power_at_all_enemies():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.player1
    first = player.opponent.summon("CS2_182")
    second = player.opponent.summon("CS2_142")
    friendly = player.summon("CS2_182")

    player.give("BAR_544").play()

    assert player.opponent.hero.health == player.opponent.hero.max_health - 1
    assert first.health == first.max_health - 1
    assert second.health == second.max_health - 1
    assert friendly.health == friendly.max_health


def test_core_shadowborn_discounts_highest_cost_shadow_spell_in_hand():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.player1
    low_shadow = player.give("CS2_057")
    high_shadow = player.give("CORE_EX1_309")
    non_shadow = player.give("CS2_062")

    shadowborn = player.give("CORE_REV_374").play()
    shadowborn.destroy()

    assert high_shadow.cost == max(0, high_shadow.data.cost - 3)
    assert low_shadow.cost == low_shadow.data.cost
    assert non_shadow.cost == non_shadow.data.cost


def test_mordresh_fire_eye_deals_ten_to_all_enemies_when_ready():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    enemy = player.opponent.summon("EX1_572")
    friendly = player.summon("EX1_572")
    player.hero_power_damage_this_game = 10

    player.give("BAR_547").play()

    assert player.opponent.hero.health == player.opponent.hero.max_health - 10
    assert enemy.health == enemy.max_health - 10
    assert friendly.health == friendly.max_health


def test_mordresh_fire_eye_does_nothing_before_ten_hero_power_damage():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    enemy = player.opponent.summon("EX1_572")
    player.hero_power_damage_this_game = 9

    player.give("BAR_547").play()

    assert player.opponent.hero.health == player.opponent.hero.max_health
    assert enemy.health == enemy.max_health


def test_core_stoneborn_general_deathrattle_summons_gravewing():
    game = prepare_empty_game()
    player = game.current_player

    general = player.give("CORE_REV_375").play()
    general.destroy()

    assert len(player.field) == 1
    gravewing = player.field[0]
    assert gravewing.id == "REV_375t"
    assert gravewing.atk == 8
    assert gravewing.health == 8
    assert gravewing.rush


def test_barak_kodobane_draws_one_two_and_three_cost_spells():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    one = player.card("CS2_084", zone=Zone.DECK)
    two = player.card("EX1_533", zone=Zone.DECK)
    three = player.card("EX1_539", zone=Zone.DECK)
    minion = player.card(WISP, zone=Zone.DECK)

    player.give("BAR_551").play()

    assert one in player.hand
    assert two in player.hand
    assert three in player.hand
    assert minion in player.deck


def test_core_kryxis_discards_hand_and_draws_three_on_deathrattle():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    player.hand.clear()
    discarded = player.give(WISP)
    first = player.card("CS2_182", zone=Zone.DECK)
    second = player.card("CS2_200", zone=Zone.DECK)
    third = player.card("CS2_231", zone=Zone.DECK)

    kryxis = player.give("CORE_REV_510").play()

    assert discarded.zone == Zone.REMOVEDFROMGAME
    assert discarded.discarded
    assert not player.hand

    kryxis.destroy()

    assert set(player.hand) == {first, second, third}


def test_mankrik_shuffles_olgra_and_drawn_olgra_summons_attacking_mankrik():
    game = prepare_empty_game()
    player = game.current_player

    player.give("BAR_721").play()

    olgra = next(card for card in player.deck if card.id == "BAR_721t")
    assert olgra.controller == player

    player.deck.remove(olgra)
    player.deck.append(olgra)
    player.draw()

    assert olgra.zone == Zone.GRAVEYARD
    consumed = player.field[-1]
    assert consumed.id == "BAR_721t2"
    assert consumed.atk == 3
    assert consumed.health == 7
    assert player.opponent.hero.health == player.opponent.hero.max_health - consumed.atk


def test_core_halkias_stores_soul_in_friendly_secret_and_resummons_when_revealed():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    secret = player.give("BT_707").play()
    halkias = player.give("CORE_REV_829").play()

    halkias.destroy()

    assert halkias.zone == Zone.GRAVEYARD
    assert secret.zone == Zone.SECRET
    assert any(buff.id == "REV_829e" for buff in secret.buffs)

    game.trigger(secret, [Reveal(secret)], event_args=None)

    assert secret.zone == Zone.GRAVEYARD
    assert any(minion.id == "REV_829" for minion in player.field)


def test_xyrella_deals_damage_equal_to_health_restored_this_turn_to_enemy_minions():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    enemy = player.opponent.summon("EX1_572")
    other_enemy = player.opponent.summon("EX1_572")
    friendly = player.summon("EX1_572")
    player.hero.hit(3)
    player.hero.heal(player.hero, 2)

    player.give("BAR_735").play()

    assert enemy.health == enemy.max_health - 2
    assert other_enemy.health == other_enemy.max_health - 2
    assert friendly.health == friendly.max_health


def test_core_volatile_skeleton_deathrattle_hits_random_enemy():
    game = prepare_empty_game()
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")
    friendly = player.summon("CS2_182")

    skeleton = player.give("CORE_REV_845").play()
    skeleton.destroy()

    enemy_damage = enemy.max_health - enemy.health
    hero_damage = player.opponent.hero.max_health - player.opponent.hero.health
    assert sorted([enemy_damage, hero_damage]) == [0, 2]
    assert friendly.health == friendly.max_health


def test_toad_of_the_wilds_gains_health_when_holding_nature_spell():
    game = prepare_empty_game()
    player = game.current_player
    player.give("EX1_169")

    toad = player.give("BAR_743").play()

    assert toad.taunt
    assert toad.max_health == 4
    assert toad.health == 4


def test_toad_of_the_wilds_does_not_gain_health_without_nature_spell():
    game = prepare_empty_game()
    player = game.current_player
    player.give("CS2_008")

    toad = player.give("BAR_743").play()

    assert toad.taunt
    assert toad.max_health == 2
    assert toad.health == 2


def test_core_sinful_sous_chef_deathrattle_adds_two_recruits_to_hand():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player

    chef = player.give("CORE_REV_952").play()
    chef.destroy()

    recruits = [card for card in player.hand if card.id == "CS2_101t"]
    assert len(recruits) == 2


def test_hecklefang_hyena_battlecry_damages_your_hero():
    game = prepare_empty_game()
    player = game.current_player

    player.give("BAR_745").play()

    assert player.hero.health == player.hero.max_health - 3
    assert player.opponent.hero.health == player.opponent.hero.max_health


def test_core_stewart_the_steward_buffs_next_recruit_and_chains_deathrattle():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player

    stewart = player.give("CORE_REV_955").play()
    stewart.destroy()
    first_recruit = player.summon("CS2_101t")
    second_recruit = player.summon("CS2_101t")

    assert first_recruit.atk == 4
    assert first_recruit.max_health == 4
    assert first_recruit.health == 4
    assert first_recruit.has_deathrattle
    assert second_recruit.atk == 1
    assert second_recruit.max_health == 1

    first_recruit.destroy()
    chained_recruit = player.summon("CS2_101t")

    assert chained_recruit.atk == 4
    assert chained_recruit.max_health == 4
    assert chained_recruit.has_deathrattle


def test_varden_dawngrasp_freezes_unfrozen_enemy_minions():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")
    other_enemy = player.opponent.summon("CS2_182")
    friendly = player.summon("CS2_182")

    player.give("BAR_748").play()

    assert enemy.frozen
    assert other_enemy.frozen
    assert enemy.health == enemy.max_health
    assert friendly.frozen is False


def test_varden_dawngrasp_hits_already_frozen_enemy_minions():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    frozen_enemy = player.opponent.summon("CS2_182")
    fresh_enemy = player.opponent.summon("CS2_182")
    player.give("CS2_024").play(target=frozen_enemy)
    player.used_mana = 0

    player.give("BAR_748").play()

    assert frozen_enemy.dead
    assert fresh_enemy.frozen
    assert fresh_enemy.health == fresh_enemy.max_health


def test_core_frostmourne_summons_minions_killed_by_this_weapon():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.player1
    first = player.opponent.summon(WISP)
    second = player.opponent.summon("CS2_142")
    player.used_mana = 0
    weapon = player.give("CORE_RLK_086").play()

    weapon.destroy()
    assert not player.field

    player.used_mana = 0
    weapon = player.give("CORE_RLK_086").play()
    player.hero.attack(first)
    player.hero.num_attacks = 0
    player.hero.attack(second)
    weapon.destroy()

    summoned_ids = [minion.id for minion in player.field]
    assert summoned_ids == [WISP, "CS2_142"]


def test_earth_revenant_battlecry_damages_enemy_minions():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")
    other_enemy = player.opponent.summon("CS2_182")
    friendly = player.summon("CS2_182")

    revenant = player.give("BAR_750").play()

    assert revenant.taunt
    assert enemy.health == enemy.max_health - 1
    assert other_enemy.health == other_enemy.max_health - 1
    assert friendly.health == friendly.max_health


def test_core_underking_battlecry_and_deathrattle_gain_armor():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    underking = player.give("CORE_RLK_657").play()

    assert underking.rush
    assert player.hero.armor == 6

    underking.destroy()

    assert player.hero.armor == 12


def test_whirling_combatant_battlecry_damages_all_other_minions():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    friendly = player.summon("CS2_182")
    enemy = player.opponent.summon("CS2_182")

    combatant = player.give("BAR_840").play()

    assert combatant.health == combatant.max_health
    assert friendly.health == friendly.max_health - 1
    assert enemy.health == enemy.max_health - 1


def test_whirling_combatant_frenzy_damages_all_other_minions_once():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    friendly = player.summon("CS2_182")
    enemy = player.opponent.summon("CS2_182")
    combatant = player.give("BAR_840").play()

    combatant.hit(1)

    assert combatant.health == combatant.max_health - 1
    assert friendly.health == friendly.max_health - 2
    assert enemy.health == enemy.max_health - 2

    combatant.hit(1)

    assert friendly.health == friendly.max_health - 2
    assert enemy.health == enemy.max_health - 2


def test_core_moarg_forgefiend_deathrattle_gains_armor():
    game = prepare_empty_game()
    player = game.current_player

    forgefiend = player.give("CORE_SW_068").play()
    forgefiend.destroy()

    assert forgefiend.taunt
    assert player.hero.armor == 8


def test_morshan_elite_summons_copy_if_hero_attacked_this_turn():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.give("CS2_091").play()
    player.hero.attack(player.opponent.hero)
    player.used_mana = 0

    elite = player.give("BAR_846").play()

    elites = player.field.filter(id="BAR_846")
    assert elite.taunt
    assert len(elites) == 2
    assert all(minion.taunt for minion in elites)


def test_morshan_elite_does_not_summon_copy_without_hero_attack():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    player.give("BAR_846").play()

    assert len(player.field.filter(id="BAR_846")) == 1


def test_core_vibrant_squirrel_deathrattle_shuffles_acorns_that_summon_squirrels():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player

    squirrel = player.give("CORE_SW_439").play()
    squirrel.destroy()

    acorns = player.deck.filter(id="SW_439t")
    assert len(acorns) == 4

    acorns[0].draw()

    assert acorns[0].zone == Zone.GRAVEYARD
    assert player.field[0].id == "SW_439t2"


def test_lilypad_lurker_transforms_enemy_minion_after_elemental_last_turn():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    target = player.opponent.summon("CS2_182")
    player.elemental_played_last_turn = True

    player.give("BAR_848").play(target=target)

    assert target.zone == Zone.SETASIDE
    frog = player.opponent.field[0]
    assert frog.id == "hexfrog"
    assert frog.atk == 0
    assert frog.health == 1
    assert frog.taunt


def test_lilypad_lurker_requires_elemental_last_turn_to_transform():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    target = player.opponent.summon("CS2_182")

    player.give("BAR_848").play(target=target)

    assert target.zone == Zone.PLAY
    assert target.id == "CS2_182"


def test_core_gnomelia_deathrattle_damages_all_enemies():
    game = prepare_empty_game()
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")
    friendly = player.summon("CS2_182")

    gnomelia = player.give("CORE_TOY_100").play()
    gnomelia.destroy()

    assert gnomelia.rush
    assert enemy.health == enemy.max_health - 2
    assert player.opponent.hero.health == player.opponent.hero.max_health - 2
    assert friendly.health == friendly.max_health


def test_kindling_elemental_discounts_next_elemental_only():
    game = prepare_empty_game()
    player = game.current_player
    elemental = player.give("BAR_750")
    non_elemental = player.give(WISP)

    player.give("BAR_854").play()

    assert elemental.cost == elemental.data.cost - 1
    assert non_elemental.cost == non_elemental.data.cost

    player.used_mana = 0
    elemental.play()

    assert not any(buff.id == "BAR_854e" for buff in player.buffs)


def test_core_felrattler_deathrattle_damages_enemy_minions():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")
    friendly = player.summon("CS2_182")

    felrattler = player.give("CORE_WC_701").play()
    felrattler.destroy()

    assert felrattler.rush
    assert enemy.health == enemy.max_health - 1
    assert friendly.health == friendly.max_health


def test_knight_of_anointment_draws_holy_spell():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    holy = player.card("CS2_089", zone=Zone.DECK)
    non_holy = player.card(WISP, zone=Zone.DECK)

    player.give("BAR_873").play()

    assert holy.zone == Zone.HAND
    assert non_holy.zone == Zone.DECK


def test_aegwynn_next_drawn_minion_inherits_spell_damage_and_deathrattle():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    next_minion = player.card(WISP, zone=Zone.DECK)
    aegwynn = player.give("CS3_001").play()

    aegwynn.destroy()
    next_minion.draw()

    assert next_minion.spellpower == 2
    assert next_minion.has_deathrattle


def test_legacy_aegwynn_has_same_deathrattle_as_core_aegwynn():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    next_minion = player.card(WISP, zone=Zone.DECK)
    aegwynn = player.give("LEG_CS3_001").play()

    aegwynn.destroy()
    next_minion.draw()

    assert next_minion.spellpower == 2
    assert next_minion.has_deathrattle


def test_northwatch_commander_draws_minion_if_controlling_secret():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    minion = player.card(WISP, zone=Zone.DECK)
    spell = player.card("CS2_029", zone=Zone.DECK)
    player.give("EX1_610").play()
    player.used_mana = 0

    player.give("BAR_876").play()

    assert minion.zone == Zone.HAND
    assert spell.zone == Zone.DECK


def test_northwatch_commander_requires_secret_to_draw_minion():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    minion = player.card(WISP, zone=Zone.DECK)

    player.give("BAR_876").play()

    assert minion.zone == Zone.DECK


def test_felsoul_jailer_discards_enemy_minion_and_returns_it_on_deathrattle():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    enemy = player.opponent
    jailed = enemy.give(WISP)
    other = enemy.give("CS2_029")

    jailer = player.give("CS3_003").play()

    assert jailed.zone == Zone.REMOVEDFROMGAME
    assert other.zone == Zone.HAND

    jailer.destroy()

    assert jailed.zone == Zone.HAND
    assert jailed.controller is enemy


def test_cannonmaster_smythe_turns_friendly_secrets_into_soldiers_that_restore_secrets():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    secret = player.give("EX1_610").play()
    player.used_mana = 0

    player.give("BAR_879").play()

    assert secret.zone == Zone.REMOVEDFROMGAME
    assert not player.secrets
    soldier = player.field[-1]
    assert soldier.id == "BAR_879t"
    assert soldier.atk == 3
    assert soldier.health == 3

    soldier.destroy()

    assert secret.zone == Zone.SECRET
    assert secret in player.secrets


def test_shadowed_spirit_deathrattle_damages_enemy_hero():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player

    spirit = player.give("CS3_013").play()
    spirit.destroy()

    assert player.opponent.hero.health == player.opponent.hero.max_health - 3


def test_legacy_shadowed_spirit_deathrattle_damages_enemy_hero():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player

    spirit = player.give("LEG_CS3_013").play()
    spirit.destroy()

    assert player.opponent.hero.health == player.opponent.hero.max_health - 3


def test_legacy_deathbringer_saurfang_returns_to_hand_costing_health():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    saurfang = player.give("LEG_RLK_082").play()
    saurfang.destroy()

    returned = player.hand[-1]
    assert returned.id == "LEG_RLK_082"
    assert getattr(returned, "_costs_health", False)


def test_legacy_ymirjar_deathbringer_spends_corpses_to_summon_taunt():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.corpses = 3

    deathbringer = player.give("LEG_RLK_226").play()
    deathbringer.destroy()

    assert player.corpses == 0
    assert any(card.id == "RLK_226t" and card.taunt for card in player.field)


def test_taelan_fordring_deathrattle_draws_highest_cost_minion():
    game = prepare_empty_game()
    player = game.current_player
    low_cost = player.card(WISP, zone=Zone.DECK)
    high_cost = player.card("CS2_182", zone=Zone.DECK)
    spell = player.card("CS2_029", zone=Zone.DECK)

    taelan = player.give("CS3_024").play()
    taelan.destroy()

    assert high_cost.zone == Zone.HAND
    assert low_cost.zone == Zone.DECK
    assert spell.zone == Zone.DECK


def test_bob_the_bartender_offers_battlegrounds_actions():
    game = prepare_empty_game()
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")

    player.give("BG31_BOB").play()

    assert player.choice is not None
    assert len(player.choice.cards) == 4
    assert [card.id for card in player.choice.cards] == [
        "BG31_BOBt",
        "BG31_BOBt2",
        "BG31_BOBt3",
        "BG31_BOBt4",
    ]

    player.choice.choose(player.choice.cards[0])

    assert enemy.frozen


def test_ysiel_windsinger_makes_spells_cost_one_this_turn():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    spell = player.give("CS2_008")

    player.give("BT_131").play()

    assert spell.cost == 1

    game.end_turn()

    assert spell.cost == spell.data.cost


def test_hullbreaker_battlecry_and_deathrattle_draw_spell_and_damage_your_hero():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    spell = player.card("CS2_029", zone=Zone.DECK)
    other_spell = player.card("CS2_029", zone=Zone.DECK)
    minion = player.card(WISP, zone=Zone.DECK)

    hullbreaker = player.give("DED_505").play()

    assert spell.zone == Zone.HAND
    assert minion.zone == Zone.DECK
    assert player.hero.health == player.hero.max_health - spell.cost

    hullbreaker.destroy()

    assert other_spell.zone == Zone.HAND
    assert player.hero.health == player.hero.max_health - spell.cost - other_spell.cost


def test_darkglare_battlecry_refreshes_mana_if_hero_took_damage_this_turn():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.used_mana = 5
    player.hero.hit(2)

    player.give("BT_307").play()

    assert player.used_mana == 5


def test_darkglare_battlecry_requires_hero_damage_this_turn():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.used_mana = 5

    player.give("BT_307").play()

    assert player.used_mana == 8


def test_cookie_the_cook_deathrattle_equips_stirring_rod():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player

    cookie = player.give("DED_522").play()
    cookie.destroy()

    assert player.weapon.id == "DED_522t"
    assert player.weapon.atk == 2
    assert player.weapon.durability == 3
    assert player.weapon.lifesteal


def test_destructive_phoenix_discards_marked_hand_card_after_three_turns_and_summons_copy():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    target = player.give(WISP)

    player.give("CATA_EVENT_001").play(target=target)

    assert target.zone == Zone.HAND
    assert len(player.field.filter(id="CATA_EVENT_001")) == 1

    game.end_turn()
    game.end_turn()
    game.end_turn()
    game.end_turn()
    game.end_turn()
    game.end_turn()

    assert target.zone == Zone.REMOVEDFROMGAME
    assert len(player.field.filter(id="CATA_EVENT_001")) == 2


def test_obsidian_revenant_summons_two_random_cheap_deathrattle_minions():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    revenant = player.give("DEEP_005").play()
    revenant.destroy()

    summoned = [minion for minion in player.field if minion.id != "DEEP_005"]
    assert len(summoned) == 2
    assert all(minion.has_deathrattle and minion.cost <= 3 for minion in summoned)


def test_baleful_blazer_destroys_minion_after_fire_spell_this_turn():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    target = player.opponent.summon("CS2_182")
    player.give("CS2_029").play(target=player.opponent.hero)
    player.used_mana = 0

    player.give("CATA_EVENT_002").play(target=target)

    assert target.zone == Zone.GRAVEYARD


def test_baleful_blazer_requires_fire_spell_this_turn():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    target = player.opponent.summon("CS2_182")

    player.give("CATA_EVENT_002").play(target=target)

    assert target.zone == Zone.PLAY


def test_shadestone_skulker_takes_weapon_stats_and_returns_weapon_on_deathrattle():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.give("CS2_082").play()
    weapon = player.weapon
    player.used_mana = 0

    skulker = player.give("DEEP_012").play()

    assert player.weapon is None
    assert weapon.zone == Zone.REMOVEDFROMGAME
    assert skulker.atk == 2
    assert skulker.health == 3

    skulker.destroy()

    assert player.weapon is weapon
    assert weapon.zone == Zone.PLAY


def test_core_draenei_totemcarver_gains_stats_for_each_friendly_totem():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.summon("CS2_050")
    player.summon("CS2_051")
    player.summon(WISP)

    carver = player.give("CORE_AT_047").play()

    assert carver.atk == 6
    assert carver.health == 7


def test_elementium_geode_battlecry_and_deathrattle_draw_card_and_damage_your_hero():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    first = player.card(WISP, zone=Zone.DECK)
    second = player.card("CS2_142", zone=Zone.DECK)

    geode = player.give("DEEP_030").play()

    assert second.zone == Zone.HAND
    assert player.hero.health == player.hero.max_health - 2

    geode.destroy()

    assert first.zone == Zone.HAND
    assert player.hero.health == player.hero.max_health - 4


def test_core_justicar_trueheart_upgrades_starting_hero_power():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    player.give("CORE_AT_132").play()

    assert player.hero.power.id == "HERO_01bp2"


def test_iridescent_gyreworm_deathrattle_gives_each_friendly_minion_bonus_effect():
    game = prepare_empty_game()
    player = game.current_player
    friendly = player.summon(WISP)
    gyreworm = player.give("DEEP_035").play()

    gyreworm.destroy()

    assert friendly.buffs


def test_therazane_deathrattle_doubles_elementals_in_hand_and_deck():
    game = prepare_empty_game()
    player = game.current_player
    hand_elemental = player.give("CS2_042")
    deck_elemental = player.card("CS2_042", zone=Zone.DECK)
    non_elemental = player.give(WISP)

    therazane = player.give("DEEP_036").play()
    therazane.destroy()

    assert hand_elemental.atk == 12
    assert hand_elemental.health == 10
    assert deck_elemental.atk == 12
    assert deck_elemental.health == 10
    assert non_elemental.atk == non_elemental.data.atk
    assert non_elemental.health == non_elemental.data.health


def test_core_barak_kodobane_draws_one_two_and_three_cost_spells():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    one = player.card("CS2_084", zone=Zone.DECK)
    two = player.card("EX1_533", zone=Zone.DECK)
    three = player.card("EX1_539", zone=Zone.DECK)
    minion = player.card(WISP, zone=Zone.DECK)

    player.give("CORE_BAR_551").play()

    assert one in player.hand
    assert two in player.hand
    assert three in player.hand
    assert minion in player.deck


def test_claw_machine_deathrattle_draws_minion_and_buffs_it():
    game = prepare_empty_game()
    player = game.current_player
    minion = player.card(WISP, zone=Zone.DECK)
    spell = player.card("CS2_029", zone=Zone.DECK)

    claw_machine = player.give("DMF_069").play()
    claw_machine.destroy()

    assert minion.zone == Zone.HAND
    assert minion.atk == minion.data.atk + 3
    assert minion.health == minion.data.health + 3
    assert spell.zone == Zone.DECK


def test_core_toxicologist_buffs_friendly_weapon_attack():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.give("CS2_082").play()
    player.used_mana = 0

    player.give("CORE_BOT_083").play()

    assert player.weapon.atk == 2


def test_darkmoon_tonk_deathrattle_fires_four_missiles_at_enemies():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player

    tonk = player.give("DMF_085").play()
    tonk.destroy()

    assert player.opponent.hero.health == player.opponent.hero.max_health - 8


def test_core_dyn_o_matic_hits_non_mech_minions_only():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")

    player.give("CORE_BOT_104").play()

    assert enemy.dead


def test_showstopper_deathrattle_silences_all_minions():
    game = prepare_empty_game()
    player = game.current_player
    taunt_minion = player.opponent.summon("CS2_179")
    assert taunt_minion.taunt

    showstopper = player.give("DMF_191").play()
    showstopper.destroy()

    assert not taunt_minion.taunt


def test_core_menacing_nimbus_adds_random_elemental_to_hand():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player

    player.give("CORE_BOT_533").play()

    assert len(player.hand) == 1
    assert player.hand[0].race == Race.ELEMENTAL


def test_renowned_performer_deathrattle_summons_two_assistants():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player

    performer = player.give("DMF_223").play()
    performer.destroy()

    assistants = [minion for minion in player.field if minion.id == "DMF_223t"]
    assert len(assistants) == 2
    assert all(assistant.taunt for assistant in assistants)


def test_core_sightless_watcher_puts_chosen_card_on_top_of_deck():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    top_choice = player.card("CS2_120")
    bottom = player.card("CS2_182")
    middle = player.card("CS2_179")
    bottom.zone = Zone.DECK
    middle.zone = Zone.DECK
    top_choice.zone = Zone.DECK

    player.give("CORE_BT_323").play()
    choice = player.choice
    assert choice
    choice.choose(top_choice)

    assert player.deck[-1] is top_choice


def test_ticket_master_shuffles_tickets_that_summon_plush_bears_when_drawn():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player

    ticket_master = player.give("DMF_514").play()
    ticket_master.destroy()

    tickets = player.deck.filter(id="DMF_514t")
    assert len(tickets) == 3

    tickets[0].draw()
    assert tickets[0].zone == Zone.GRAVEYARD
    assert any(minion.id == "DMF_514t2" for minion in player.field)


def test_core_lady_liadrin_returns_spells_cast_on_friendly_characters():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    friendly = player.summon(WISP)
    player.give("CS2_087").play(target=friendly)
    player.hand.clear()

    player.give("CORE_BT_334").play()

    assert [card.id for card in player.hand] == ["CS2_087"]


def test_bumper_car_deathrattle_adds_two_riders_to_hand():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    bumper_car = player.give("DMF_523").play()
    bumper_car.destroy()

    riders = player.hand.filter(id="DMF_523t")
    assert len(riders) == 2
    assert all(rider.rush for rider in riders)


def test_core_raging_felscreamer_discounts_next_demon_played():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    demon = player.give("CS2_065")

    player.give("CORE_BT_416").play()

    assert demon.cost == max(0, demon.data.cost - 2)
    demon.play()
    assert demon.cost == demon.data.cost


def test_ring_matron_deathrattle_summons_two_fiery_imps():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player

    matron = player.give("DMF_533").play()
    matron.destroy()

    assert len(player.field.filter(id="DMF_533t")) == 2


def test_core_umberwing_battlecry_summons_two_felwings():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player

    player.give("CORE_BT_922").play()

    assert len(player.field.filter(id="BT_922t")) == 2


def test_sporegnasher_deathrattle_hits_random_enemy_minion():
    game = prepare_empty_game()
    player = game.current_player
    enemy = player.opponent.summon(WISP)

    sporegnasher = player.give("EDR_110").play()
    sporegnasher.destroy()

    assert enemy.dead


def test_core_tichondrius_makes_hero_immune_and_next_demon_cost_zero_this_turn():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    demon = player.give("CS2_065")

    tichondrius = player.give("CORE_CATA_001").play()

    assert player.hero.immune
    assert demon.cost == 0
    demon.play()
    assert tichondrius in player.field
    assert player.hero.immune


def test_illusory_greenwing_shuffles_illusions_that_summon_when_drawn():
    game = prepare_empty_game()
    player = game.current_player

    greenwing = player.give("EDR_260").play()
    greenwing.destroy()

    illusions = player.deck.filter(id="EDR_260t")
    assert len(illusions) == 2

    illusions[0].draw()
    assert illusions[0].zone == Zone.PLAY
    assert illusions[0] in player.field
    assert illusions[0].taunt


def test_core_calia_menethil_resurrects_highest_cost_friendly_minion():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    low_cost = player.give(WISP).play()
    high_cost = player.give("CS2_182").play()
    low_cost.destroy()
    high_cost.destroy()

    player.give("CORE_CATA_002").play()

    assert len(player.field.filter(id="CS2_182")) == 1
    assert not player.field.filter(id=WISP)


def test_twisted_treant_deathrattle_gives_random_minion_in_each_hand_minus_attack():
    game = prepare_empty_game()
    player = game.current_player
    friendly = player.give("CS2_182")
    enemy = player.opponent.give("CS2_182")

    treant = player.give("EDR_495").play()
    treant.destroy()

    assert friendly.atk == friendly.data.atk - 2
    assert enemy.atk == enemy.data.atk - 2


def test_core_ulfar_grants_other_minions_cost_based_deathrattle():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    other = player.summon("CS2_065")

    player.give("CORE_CATA_006").play()
    other.destroy()

    assert len(player.field) == 2
    assert any(minion.cost == other.cost for minion in player.field if minion.id != "CORE_CATA_006")


def test_meadowstrider_deathrattle_places_one_cost_copy_on_bottom_of_deck():
    game = prepare_empty_game()
    player = game.current_player

    meadowstrider = player.give("EDR_978").play()
    meadowstrider.destroy()

    assert player.deck[0].id == "EDR_978"
    assert player.deck[0].cost == 1


def test_core_drakonid_operative_discovers_copy_from_opponent_deck_while_holding_dragon():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.give("AT_008")
    player.opponent.card("CS2_182").zone = Zone.DECK

    player.give("CORE_CFM_605").play()
    choice = player.choice
    assert choice
    choice.choose(choice.cards[0])

    assert player.hand[-1].id == "CS2_182"
    assert player.opponent.deck.filter(id="CS2_182")


def test_wicked_blightspawn_deathrattle_equips_or_buffs_dagger():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    blightspawn = player.give("END_002").play()
    blightspawn.destroy()
    assert player.weapon.id == "CS2_082"
    assert (player.weapon.atk, player.weapon.durability) == (1, 2)

    blightspawn = player.give("END_002").play()
    blightspawn.destroy()
    assert player.weapon.id == "CS2_082"
    assert player.weapon.atk == 3


def test_core_abyssal_enforcer_hits_all_other_characters():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    friendly = player.summon(WISP)
    enemy = player.opponent.summon(WISP)

    enforcer = player.give("CORE_CFM_751").play()

    assert player.hero.damage == 3
    assert player.opponent.hero.damage == 3
    assert friendly.dead
    assert enemy.dead
    assert enforcer.damage == 0


def test_triennium_rex_kindred_and_deathrattle_get_discounted_deathrattle_minion():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player

    rex = player.give("END_015").play()
    assert len(player.hand) == 1
    assert player.hand[0].has_deathrattle
    assert player.hand[0].cost == max(0, player.hand[0].data.cost - 2)

    player.hand.clear()
    rex.destroy()
    assert len(player.hand) == 1
    assert player.hand[0].has_deathrattle
    assert player.hand[0].cost == max(0, player.hand[0].data.cost - 2)


def test_core_grimestreet_outfitter_buffs_minions_in_hand():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    minion = player.give("CS2_182")
    spell = player.give("CS2_029")

    player.give("CORE_CFM_753").play()

    assert minion.atk == minion.data.atk + 1
    assert minion.health == minion.data.health + 1
    assert spell.cost == spell.data.cost


def test_rin_orchestrator_deathrattle_draws_discards_and_mills_both_players():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    opponent = player.opponent
    for target in (player, opponent):
        target.hand.clear()
        for card_id in ("CS2_231", "CS2_182", "CS2_065", "CS2_142"):
            target.card(card_id).zone = Zone.DECK

    rin = player.give("ETC_071").play()
    rin.destroy()

    assert len(player.deck) == 0
    assert len(opponent.deck) == 0
    assert len(player.hand) == 0
    assert len(opponent.hand) == 0
    assert player.discarded_cards_this_game == 2
    assert opponent.discarded_cards_this_game == 2


def test_core_dirty_rat_summons_random_minion_from_opponent_hand():
    game = prepare_empty_game()
    player = game.current_player
    opponent = player.opponent
    minion = opponent.give("CS2_182")
    spell = opponent.give("CS2_029")

    player.give("CORE_CFM_790").play()

    assert minion.zone == Zone.PLAY
    assert minion in opponent.field
    assert spell.zone == Zone.HAND


def test_amplified_elekk_deathrattle_damages_enemy_minions():
    game = prepare_empty_game()
    player = game.current_player
    friendly = player.summon("CS2_182")
    enemy = player.opponent.summon("CS2_182")

    elekk = player.give("ETC_086").play()
    elekk.destroy()

    assert friendly.damage == 0
    assert enemy.damage == 3


def test_core_fire_elemental_battlecry_deals_four_damage():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    target = game.player2.summon("CS2_182")

    game.player1.give("CORE_CS2_042").play(target=target)

    assert target.damage == 4


def test_crowd_surfer_gives_other_minion_stats_and_deathrattle():
    game = prepare_empty_game()
    player = game.current_player
    recipient = player.summon("CS2_182")

    surfer = player.give("ETC_104").play()
    surfer.destroy()

    assert recipient.atk == recipient.data.atk + 1
    assert recipient.health == recipient.data.health + 1
    assert recipient.has_deathrattle


def test_core_dread_infernal_hits_all_other_characters():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    friendly = player.summon("CS2_231")
    enemy = player.opponent.summon("CS2_231")

    infernal = player.give("CORE_CS2_064").play()

    assert player.hero.damage == 1
    assert player.opponent.hero.damage == 1
    assert friendly.dead
    assert enemy.dead
    assert infernal.damage == 0


def test_disco_maul_improves_while_equipped_and_buffs_on_deathrattle():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    recipient = player.summon("CS2_182")

    maul = player.give("ETC_317").play()
    player.give("CS2_231").play()
    player.give("CS2_231").play()
    maul.destroy()

    buffed = [
        minion
        for minion in player.field
        if minion.atk == minion.data.atk + 2
        and minion.health == minion.data.health + 2
    ]
    assert len(buffed) == 1


def test_core_guardian_of_kings_restores_hero_health():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.hero.damage = 8

    player.give("CORE_CS2_088").play()

    assert player.hero.damage == 2


def test_annoy_o_troupe_deathrattle_summons_annoy_o_trons():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player

    troupe = player.give("ETC_321").play()
    troupe.destroy()

    tokens = player.field.filter(id="GVG_085")
    assert len(tokens) == 3
    assert all(token.taunt and token.divine_shield for token in tokens)


def test_core_earthen_ring_farseer_restores_target_health():
    game = prepare_empty_game()
    target = game.player1.summon("CS2_182")
    target.damage = 3

    game.player1.give("CORE_CS2_117").play(target=target)

    assert target.damage == 0


def test_lead_dancer_deathrattle_summons_lower_attack_minion_from_deck():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    lower_attack = player.card("CS2_065")
    equal_attack = player.card("CS2_182")
    lower_attack.zone = Zone.DECK
    equal_attack.zone = Zone.DECK

    dancer = player.give("ETC_328").play()
    dancer.destroy()

    assert lower_attack.zone == Zone.PLAY
    assert equal_attack.zone == Zone.DECK


def test_core_injured_blademaster_damages_itself_on_play():
    game = prepare_empty_game()

    blademaster = game.player1.give("CORE_CS2_181").play()

    assert blademaster.damage == 4


def test_kangor_dancing_king_swaps_with_hand_minion_and_grants_lifesteal():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    hand_minion = player.give("CS2_182")

    kangor = player.give("ETC_329").play()
    kangor.destroy()

    assert hand_minion.zone == Zone.PLAY
    assert hand_minion.lifesteal
    assert kangor.zone == Zone.HAND


def test_core_abusive_sergeant_gives_minion_attack_this_turn():
    game = prepare_empty_game()
    target = game.player1.summon("CS2_231")

    game.player1.give("CORE_CS2_188").play(target=target)

    assert target.atk == target.data.atk + 2


def test_unpopular_has_been_deathrattle_summons_random_five_cost_minion():
    game = prepare_empty_game()
    player = game.current_player

    has_been = player.give("ETC_349").play()
    has_been.destroy()

    assert len(player.field) == 1
    assert player.field[0].cost == 5


def test_core_elven_archer_battlecry_deals_one_damage():
    game = prepare_empty_game()
    target = game.player2.summon("CS2_231")

    game.player1.give("CORE_CS2_189").play(target=target)

    assert target.dead


def test_free_spirit_battlecry_and_deathrattle_increase_shapeshift_armor():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player

    spirit = player.give("ETC_382").play()
    spirit.destroy()
    player.hero_power.activate(None, None)

    assert player.hero.armor == 3


def test_core_ironbeak_owl_silences_minion():
    game = prepare_empty_game()
    target = game.player2.summon("CS2_231")
    game.cheat_action(target, [Buff(target, "CS2_188o")])
    assert target.atk == 3

    game.player1.give("CORE_CS2_203").play(target=target)

    assert target.atk == 1


def test_groovy_cat_battlecry_and_deathrattle_increase_shapeshift_attack():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player

    cat = player.give("ETC_385").play()
    cat.destroy()
    player.hero_power.activate(None, None)

    assert player.hero.atk == 3


def test_core_bloodsail_deckhand_discounts_next_weapon():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    weapon = player.give("CS2_091")

    player.give("CORE_CS3_008").play()

    assert weapon.cost == 0


def test_timber_tambourine_summons_ancients_for_expensive_cards_played():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    player.max_mana = 10

    tambourine = player.give("ETC_388").play()
    player.used_mana = 0
    player.give("CS2_200").play()
    player.used_mana = 0
    player.give("CS2_200").play()
    tambourine.destroy()

    ancients = player.field.filter(id="TTN_903t4")
    assert len(ancients) == 2
    assert all(ancient.atk == 5 and ancient.health == 5 for ancient in ancients)


def test_core_nordrassil_druid_discounts_next_spell_this_turn():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    spell = player.give("CS2_011")

    player.give("CORE_CS3_012").play()

    assert spell.cost == max(0, spell.data.cost - 3)


def test_glaivetar_draws_for_outcast_cards_played_while_equipped():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    deck_cards = [player.card("CS2_231"), player.card("CS2_231"), player.card("CS2_231")]
    for card in deck_cards:
        card.zone = Zone.DECK

    glaivetar = player.give("ETC_405").play()
    player.give("BT_035").play()
    player.give("BT_035").play()
    glaivetar.destroy()

    assert len(player.hand) == 3


def test_core_sunreaver_spy_gains_stats_if_you_control_secret():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.give("EX1_289").play()

    spy = player.give("CORE_DAL_086").play()

    assert spy.atk == 3
    assert spy.health == 4


def test_arcanite_ripper_improves_when_health_changes_on_your_turn():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    ripper = player.give("ETC_423").play()
    game.cheat_action(player.hero, [Hit(player.hero, 1)])
    ripper.destroy()

    blighthead = player.field[0]
    assert blighthead.id == "ETC_423t"
    assert blighthead.lifesteal
    assert blighthead.atk == 2
    assert blighthead.health == 2


def test_core_hench_clan_burglar_discovers_another_class_spell():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player

    player.give("CORE_DAL_416").play()
    player.choice.choose(player.choice.cards[0])

    assert len(player.hand) == 1
    assert player.hand[0].type == CardType.SPELL
    assert player.hand[0].card_class != CardClass.ROGUE


def test_pozzik_adds_audio_bots_to_opponent_and_deathrattle_summons_them():
    game = prepare_empty_game()
    player = game.current_player
    opponent = player.opponent

    pozzik = player.give("ETC_425").play()

    bots = opponent.hand.filter(id="ETC_425t")
    assert len(bots) == 2

    pozzik.destroy()

    assert len(player.field.filter(id="ETC_425t")) == 2


def test_core_arch_villain_rafaam_replaces_hand_and_deck_with_legendaries():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    hand_card = player.give("CS2_231")
    deck_card = player.card("CS2_231")
    deck_card.zone = Zone.DECK

    player.give("CORE_DAL_422").play()

    assert hand_card.morphed is not None
    assert deck_card.morphed is not None
    assert all(card.rarity == Rarity.LEGENDARY for card in list(player.hand) + list(player.deck))


def test_record_scratcher_refreshes_mana_for_combo_cards_played_while_equipped():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10

    scratcher = player.give("ETC_518").play()
    player.give("EX1_131").play()
    player.give("EX1_131").play()
    player.used_mana = 5
    scratcher.destroy()

    assert player.used_mana == 2


def test_core_kalecgos_makes_first_spell_free_and_discovers_spell():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    spell = player.give("CS2_024")

    player.give("CORE_DAL_609").play()
    player.choice.choose(player.choice.cards[0])

    assert spell.cost == 0
    assert len(player.hand) == 2
    assert player.hand[-1].type == CardType.SPELL


def test_kodohide_drumkit_damages_all_minions_for_armor_gained():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    friendly = player.summon("CS2_182")
    enemy = player.opponent.summon("CS2_182")

    drumkit = player.give("ETC_520").play()
    game.cheat_action(player.hero, [GainArmor(player.hero, 3)])
    drumkit.destroy()

    assert friendly.damage == 4
    assert enemy.damage == 4


def test_core_madame_lazul_discovers_copy_from_opponent_hand():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    opponent_card = player.opponent.give("CS2_231")

    player.give("CORE_DAL_729").play()
    player.choice.choose(player.choice.cards[0])

    assert len(player.hand) == 1
    assert player.hand[0].id == opponent_card.id
    assert player.hand[0] is not opponent_card


def test_cage_head_deathrattle_summons_charging_taunt_blight_boar():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    cage_head = player.give("ETC_526").play()
    cage_head.destroy()

    boar = player.field[0]
    assert boar.id == "ETC_526t"
    assert boar.atk == 9
    assert boar.health == 9
    assert boar.charge
    assert boar.taunt


def test_core_zai_copies_left_and_right_most_cards_in_hand():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    left = player.give("CS2_231")
    middle = player.give("CS2_182")
    right = player.give("CS2_200")

    player.give("CORE_DMF_231").play()

    assert left.zone == Zone.HAND
    assert middle.zone == Zone.HAND
    assert right.zone == Zone.HAND
    assert [card.id for card in player.hand].count(left.id) == 2
    assert [card.id for card in player.hand].count(middle.id) == 1
    assert [card.id for card in player.hand].count(right.id) == 2


def test_audio_splitter_deathrattle_copies_highest_cost_spell_in_hand():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.give("CS2_024")
    high_cost_spell = player.give("CS2_028")

    splitter = player.give("ETC_536").play()
    splitter.destroy()

    assert [card.id for card in player.hand].count(high_cost_spell.id) == 2


def test_core_hammer_of_the_naaru_summons_holy_elemental():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player

    player.give("CORE_DMF_238").play()

    elemental = player.field[0]
    assert elemental.id == "DMF_238t"
    assert elemental.atk == 6
    assert elemental.health == 6
    assert elemental.taunt


def test_jazz_bass_discounts_next_spell_for_overload_while_equipped():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    spell = player.give("CS2_045")

    bass = player.give("ETC_813").play()
    game.cheat_action(player, [Overload(player, 2)])
    bass.destroy()

    assert spell.cost == max(0, spell.data.cost - 3)


def test_core_lothraxion_gives_future_silver_hand_recruits_divine_shield():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player

    player.give("CORE_DMF_240").play()
    game.cheat_action(player, [Summon(player, "CS2_101t")])
    recruit = player.field[1]

    assert recruit.divine_shield


def test_jungle_jammer_summons_random_beast_improved_by_spells_cast():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player

    jammer = player.give("ETC_832").play()
    player.give("DS1_185").play(target=player.opponent.hero)
    player.give("DS1_185").play(target=player.opponent.hero)
    jammer.destroy()

    assert len(player.field) == 1
    assert player.field[0].cost == 10
    assert Race.BEAST in player.field[0].races


def test_core_foxy_fraud_discounts_next_combo_card_this_turn():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    combo_card = player.give("CS2_073")

    player.give("CORE_DMF_511").play()

    assert combo_card.cost == 0


def test_living_flame_deathrattle_draws_fire_spell_from_deck():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    fire_spell = player.card("CS2_029")
    frost_spell = player.card("CS2_024")
    fire_spell.zone = Zone.DECK
    frost_spell.zone = Zone.DECK

    flame = player.give("FIR_929").play()
    flame.destroy()

    assert fire_spell.zone == Zone.HAND
    assert frost_spell.zone == Zone.DECK


def test_core_sword_eater_equips_jawbreaker():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    sword_eater = player.give("CORE_DMF_521").play()

    assert sword_eater.taunt
    assert player.weapon.id == "DMF_521t"
    assert player.weapon.atk == 3
    assert player.weapon.durability == 2


def test_tindral_sageswift_deathrattle_damages_all_enemies_on_your_turn():
    game = prepare_empty_game()
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")
    friendly = player.summon("CS2_182")

    tindral = player.give("FIR_958").play()
    tindral.destroy()

    assert player.opponent.hero.damage == 1
    assert enemy.damage == 1
    assert friendly.damage == 0


def test_tindral_sageswift_deathrattle_damages_all_enemies_more_on_opponents_turn():
    game = prepare_empty_game()
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")
    friendly = player.summon("CS2_182")

    tindral = player.give("FIR_958").play()
    game.end_turn()
    tindral.destroy()

    assert player.opponent.hero.damage == 4
    assert enemy.damage == 4
    assert friendly.damage == 0


def test_core_kiri_adds_solar_and_lunar_eclipse():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player

    player.give("CORE_DMF_733").play()

    assert "DMF_058" in [card.id for card in player.hand]
    assert "DMF_057" in [card.id for card in player.hand]


def test_arkonite_defense_crystal_deathrattle_gains_armor():
    game = prepare_empty_game()
    player = game.current_player

    crystal = player.give("GDB_100").play()
    crystal.destroy()

    assert player.hero.armor == 4


def test_core_deathwing_mad_aspect_attacks_all_other_minions():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    friendly = player.summon("CS2_231")
    enemy = player.opponent.summon("CS2_231")

    deathwing = player.give("CORE_DRG_026").play()

    assert friendly.dead
    assert enemy.dead
    assert deathwing.damage == 2


def test_biopod_deathrattle_hits_random_enemy_for_its_attack():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player

    biopod = player.give("GDB_111").play()
    biopod.destroy()

    assert player.opponent.hero.damage == 2


def test_core_flik_skyshiv_destroys_target_and_all_copies():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    target = player.opponent.summon("CS2_231")
    copy_on_board = player.summon("CS2_231")
    different_minion = player.summon("CS2_182")

    player.give("CORE_DRG_037").play(target=target)

    assert target.dead
    assert copy_on_board.dead
    assert not different_minion.dead


def test_soulbound_spire_summons_minion_with_cost_equal_to_attack():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    spire = player.give("GDB_112").play()
    spire.destroy()

    assert len(player.field) == 1
    assert player.field[0].cost == 2


def test_soulbound_spire_caps_summoned_minion_cost_at_ten():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    spire = player.give("GDB_112").play()
    game.cheat_action(spire, [Buff(spire, "CS2_188o")])
    game.cheat_action(spire, [Buff(spire, "CS2_188o")])
    game.cheat_action(spire, [Buff(spire, "CS2_188o")])
    game.cheat_action(spire, [Buff(spire, "CS2_188o")])
    game.cheat_action(spire, [Buff(spire, "CS2_188o")])
    spire.destroy()

    assert len(player.field) == 1
    assert player.field[0].cost == 10


def test_core_murozond_replays_opponents_previous_turn_cards():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    game.end_turn()

    player.opponent.give("CS2_231").play()
    game.end_turn()
    player.give("CORE_DRG_090").play()

    assert len(player.field.filter(id="CS2_231")) == 1


def test_dirdra_shuffles_all_crewmates_and_deathrattle_draws_two():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    crewmates = {
        "GDB_471t",
        "GDB_471t2",
        "GDB_471t3",
        "GDB_471t4",
        "GDB_471t5",
        "GDB_471t6",
        "GDB_471t7",
        "GDB_471t8",
    }

    dirdra = player.give("GDB_117").play()

    assert {card.id for card in player.deck} == crewmates

    dirdra.destroy()

    assert len(player.hand) == 2
    assert {card.id for card in player.hand}.issubset(crewmates)
    assert len(player.deck) == 6


def test_core_amber_watcher_restores_health():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.hero.damage = 10

    player.give("CORE_DRG_226").play(target=player.hero)

    assert player.hero.damage == 2


def test_velen_retriggers_other_played_draenei_battlecries_and_deathrattles():
    game = prepare_empty_game()
    player = game.current_player
    hand_draenei = player.give("GDB_139t")

    player.give("GDB_722").play()
    velen = player.give("GDB_131").play()
    velen.destroy()

    assert hand_draenei.atk == 9
    assert hand_draenei.health == 6


def test_core_bronze_explorer_discovers_dragon():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player

    player.give("CORE_DRG_229").play()
    player.choice.choose(player.choice.cards[0])

    assert len(player.hand) == 1
    assert Race.DRAGON in player.hand[0].races


def test_yrel_deathrattle_gets_three_older_librams():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player

    yrel = player.give("GDB_141").play()
    yrel.destroy()

    assert {card.id for card in player.hand} == {"BT_011", "BT_024", "BT_025"}


def test_core_babbling_bookcase_adds_two_random_mage_spells():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player

    player.give("CORE_EDR_001").play()

    assert len(player.hand) == 2
    assert all(card.type == CardType.SPELL for card in player.hand)
    assert all(card.card_class == CardClass.MAGE for card in player.hand)


def test_hostile_invader_damages_other_minions_on_battlecry_spellburst_and_deathrattle():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    friendly = player.summon("CS2_200")
    enemy = player.opponent.summon("CS2_200")

    invader = player.give("GDB_226").play()

    assert friendly.damage == 2
    assert enemy.damage == 2
    assert invader.damage == 0

    player.give("CS2_105").play()
    assert friendly.damage == 4
    assert enemy.damage == 4
    assert invader.damage == 0

    invader.destroy()
    assert friendly.damage == 6
    assert enemy.damage == 6


def test_core_falric_draws_card_that_spends_corpses_and_doubles_corpse_gain():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    corpse_spender = player.card("CORE_RLK_051")
    other_spell = player.card("CS2_024")
    corpse_spender.zone = Zone.DECK
    other_spell.zone = Zone.DECK

    player.give("CORE_EDR_003").play()
    player.summon("CS2_231").destroy()

    assert corpse_spender.zone == Zone.HAND
    assert other_spell.zone == Zone.DECK
    assert player.corpses == 2


def test_splitting_spacerock_deathrattle_summons_two_boulders():
    game = prepare_empty_game()
    player = game.current_player

    spacerock = player.give("GDB_331").play()
    spacerock.destroy()

    assert [minion.id for minion in player.field] == ["GDB_331t1", "GDB_331t1"]
    assert all(minion.atk == 4 and minion.health == 4 for minion in player.field)


def test_core_raptor_herald_discovers_beast_with_dark_gift_and_kindred_discount():
    game = prepare_empty_game()
    player = game.current_player
    player.cards_played_last_turn.append(player.card("CS2_171"))

    player.give("CORE_EDR_004").play()
    choice = player.choice.cards[0]
    player.choice.choose(choice)

    assert len(player.hand) == 1
    beast = player.hand[0]
    assert Race.BEAST in set(beast.races).union(beast.data.races)
    assert getattr(beast, "_dark_gift", False)
    assert beast.cost == max(0, beast.data.cost - 1)


def test_space_pirate_deathrattle_discounts_next_weapon_this_turn():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    weapon = player.give("CS2_106")

    pirate = player.give("GDB_333").play()
    pirate.destroy()

    assert weapon.cost == max(0, weapon.data.cost - 1)

    player.give("CS2_106").play()
    second_weapon = player.give("CS2_106")
    assert second_weapon.cost == second_weapon.data.cost


def test_core_black_knight_destroys_enemy_taunt_minion():
    game = prepare_empty_game()
    player = game.current_player
    target = player.opponent.summon("CS2_179")

    player.give("CORE_EX1_002").play(target=target)

    assert target.dead


def test_farseer_nobundo_deathrattle_opens_galaxys_lens():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player

    nobundo = player.give("GDB_447").play()
    nobundo.destroy()

    assert len(player.field) == 1
    assert player.field[0].id == "GDB_136t"


def test_core_big_game_hunter_destroys_large_attack_minion():
    game = prepare_empty_game()
    player = game.current_player
    target = player.opponent.summon("CS2_201")

    player.give("CORE_EX1_005").play(target=target)

    assert target.dead


def test_core_voodoo_doctor_restores_two_health():
    game = prepare_empty_game()
    player = game.current_player
    player.hero.damage = 5

    player.give("CORE_EX1_011").play(target=player.hero)

    assert player.hero.damage == 3


def test_core_king_mukla_gives_opponent_two_bananas():
    game = prepare_empty_game()
    player = game.current_player

    player.give("CORE_EX1_014").play()

    assert [card.id for card in player.opponent.hand].count("EX1_014t") == 2


def test_core_twilight_drake_gains_health_for_cards_in_hand():
    game = prepare_empty_game()
    player = game.current_player
    player.give("CS2_231")
    player.give("CS2_231")

    drake = player.give("CORE_EX1_043").play()

    assert drake.health == drake.data.health + 2


def test_core_dark_iron_dwarf_gives_minion_two_attack():
    game = prepare_empty_game()
    player = game.current_player
    target = player.summon("CS2_231")
    original_atk = target.atk

    player.give("CORE_EX1_046").play(target=target)

    assert target.atk == original_atk + 2


def test_core_youthful_brewmaster_returns_friendly_minion_to_hand():
    game = prepare_empty_game()
    player = game.current_player
    target = player.summon("CS2_231")

    player.give("CORE_EX1_049").play(target=target)

    assert target in player.hand
    assert target not in player.field


def test_core_coldlight_oracle_draws_two_for_each_player():
    game = prepare_empty_game()
    player = game.current_player
    opponent = player.opponent
    for _ in range(2):
        card = player.card("CS2_231", zone=Zone.DECK)
        card.zone = Zone.DECK
        card = opponent.card("CS2_231", zone=Zone.DECK)
        card.zone = Zone.DECK

    player.give("CORE_EX1_050").play()

    assert len(player.hand) == 2
    assert len(opponent.hand) == 3


def test_core_crazed_alchemist_swaps_minion_attack_and_health():
    game = prepare_empty_game()
    player = game.current_player
    target = player.summon("CS2_200")

    player.give("CORE_EX1_059").play(target=target)

    assert (target.atk, target.health) == (7, 6)


def test_core_acidic_swamp_ooze_destroys_opponent_weapon():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    player.opponent.summon("CS2_106")

    player.give("CORE_EX1_066").play()

    assert player.opponent.weapon is None


def test_core_mad_bomber_deals_three_to_other_characters():
    game = prepare_empty_game()
    player = game.current_player
    target1 = player.summon("CS2_200")
    target2 = player.opponent.summon("CS2_200")

    bomber = player.give("CORE_EX1_082").play()

    assert bomber.damage == 0
    assert target1.damage + target2.damage + player.hero.damage + player.opponent.hero.damage == 3


def test_core_mind_control_tech_steals_enemy_minion_if_opponent_has_four():
    game = prepare_empty_game()
    player = game.current_player
    targets = [player.opponent.summon("CS2_231") for _ in range(4)]

    player.give("CORE_EX1_085").play()

    assert any(target.controller is player for target in targets)


def test_core_defender_of_argus_buffs_adjacent_minions():
    game = prepare_empty_game()
    player = game.current_player
    left = player.summon("CS2_231")
    right = player.summon("CS2_231")
    defender = player.give("CORE_EX1_093").play(index=1)

    assert (left.atk, left.health) == (2, 2)
    assert (right.atk, right.health) == (2, 2)
    assert left.taunt
    assert right.taunt
    assert not defender.taunt


def test_core_coldlight_seer_buffs_other_murlocs_health():
    game = prepare_empty_game()
    player = game.current_player
    murloc = player.summon("CS2_168")
    non_murloc = player.summon("CS2_231")

    seer = player.give("CORE_EX1_103").play()

    assert murloc.health == murloc.data.health + 2
    assert non_murloc.health == non_murloc.data.health
    assert seer.health == seer.data.health


def test_core_leeroy_jenkins_summons_two_whelps_for_opponent():
    game = prepare_empty_game()
    player = game.current_player

    player.give("CORE_EX1_116").play()

    assert [card.id for card in player.opponent.field].count("EX1_116t") == 2


def test_wakener_of_souls_resurrects_different_friendly_deathrattle_minion():
    game = prepare_empty_game()
    player = game.current_player
    crystal = player.summon("GDB_100")
    crystal.destroy()

    wakener = player.summon("GDB_468")
    wakener.destroy()

    assert any(card.id == "GDB_100" for card in player.field)


def test_interstellar_wayfarer_discounts_librams_on_battlecry_and_deathrattle():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    libram = player.give("BT_011")
    original_cost = libram.cost

    wayfarer = player.give("GDB_721").play()

    assert libram.cost == original_cost - 1

    wayfarer.destroy()

    assert libram.cost == original_cost - 2


def test_extraterrestrial_egg_summons_beast_that_attacks_lowest_health_enemy():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    low_health = player.opponent.summon("CS2_231")
    player.opponent.summon("CS2_200")

    egg = player.summon("GDB_840")
    egg.destroy()

    assert any(card.id == "GDB_840t" for card in player.field)
    assert low_health.dead


def test_galactic_crusader_deathrattle_adds_two_discounted_holy_spells():
    game = prepare_empty_game()
    player = game.current_player

    crusader = player.summon("GDB_862")
    crusader.destroy()

    holy_spells = [
        card for card in player.hand
        if card.type == CardType.SPELL and card.cost == card.data.cost - 3
    ]
    assert len(holy_spells) == 2


def test_escape_pod_deathrattle_buffs_adjacent_minions_and_gives_rush():
    game = prepare_empty_game()
    player = game.current_player
    left = player.summon("CS2_231")
    pod = player.summon("GDB_877")
    right = player.summon("CS2_231")
    original_left_stats = (left.atk, left.health)
    original_right_stats = (right.atk, right.health)

    pod.destroy()

    assert (left.atk, left.health) == (
        original_left_stats[0] + 1,
        original_left_stats[1] + 1,
    )
    assert (right.atk, right.health) == (
        original_right_stats[0] + 1,
        original_right_stats[1] + 1,
    )
    assert left.rush
    assert right.rush


def test_shambling_chow_deathrattle_damages_friendly_hero():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player

    chow = player.give("NX2_024").play()
    chow.destroy()

    assert player.hero.damage == 4


def test_calamitys_grasp_deathrattle_adds_outcast_card():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player

    weapon = player.give("NX2_025").play()
    weapon.destroy()

    assert len(player.hand) == 1
    assert player.hand[0].get_actions("outcast")


def test_core_si7_infiltrator_destroys_random_enemy_secret():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.MAGE)
    player = game.current_player
    opponent = player.opponent

    game.end_turn()
    secret = opponent.give("EX1_287").play()
    assert secret in opponent.secrets

    game.end_turn()
    player.give("CORE_EX1_186").play()

    assert secret not in opponent.secrets


def test_lost_exarch_spends_all_mana_to_summon_rushing_ghouls():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 3
    player.used_mana = 0

    exarch = player.summon("NX2_032")
    exarch.destroy()

    ghouls = player.field.filter(id="NX2_032t")
    assert player.mana == 0
    assert len(ghouls) == 3
    assert all(ghoul.rush for ghoul in ghouls)


def test_core_barrens_stablehand_summons_random_beast():
    game = prepare_empty_game()
    player = game.current_player

    player.give("CORE_EX1_188").play()

    beasts = [minion for minion in player.field if Race.BEAST in minion.races]
    assert len(player.field) == 2
    assert len(beasts) == 1


def test_rivendare_warrider_shuffles_other_horsemen():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    rivendare = player.summon("NX2_034")
    rivendare.destroy()

    assert sorted(card.id for card in player.deck) == [
        "NX2_034t",
        "NX2_034t1",
        "NX2_034t2",
    ]


def test_rivendare_horsemen_destroy_enemy_hero_after_all_four_die():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    horsemen = ["NX2_034", "NX2_034t", "NX2_034t1", "NX2_034t2"]

    with pytest.raises(GameOver):
        for card_id in horsemen:
            player.summon(card_id).destroy()

    assert player.opponent.playstate == PlayState.LOST


def test_core_brightwing_adds_random_legendary_minion():
    game = prepare_empty_game()
    player = game.current_player

    player.give("CORE_EX1_189").play()

    assert len(player.hand) == 1
    assert player.hand[0].type == CardType.MINION
    assert player.hand[0].rarity == Rarity.LEGENDARY


def test_mida_pure_light_shuffles_fragment_that_resummons_mida_when_drawn():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player

    mida = player.summon("ONY_028")
    mida.destroy()

    fragment = player.deck[0]
    assert fragment.id == "ONY_028t"

    player.draw()

    assert fragment.zone == Zone.GRAVEYARD
    assert len(player.field.filter(id="ONY_028")) == 1


def test_core_high_inquisitor_whitemane_summons_friendly_minions_dead_this_turn():
    game = prepare_empty_game()
    player = game.current_player

    wisp = player.summon(WISP)
    opponent_wisp = player.opponent.summon(WISP)
    wisp.destroy()
    opponent_wisp.destroy()

    player.give("CORE_EX1_190").play()

    assert len(player.field.filter(id=WISP)) == 1
    assert not player.opponent.field.filter(id=WISP)


def test_shatterskin_gargoyle_deathrattle_hits_random_enemy_for_four():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    gargoyle = player.summon("RLK_029")
    gargoyle.destroy()

    assert player.opponent.hero.damage == 4


def test_core_psychic_conjurer_copies_card_from_enemy_deck():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    card = player.opponent.card(WISP)
    card.zone = Zone.DECK

    player.give("CORE_EX1_193").play()

    assert len(player.hand) == 1
    assert player.hand[0].id == WISP
    assert card in player.opponent.deck


def test_infected_peasant_deathrattle_summons_undead_peasant():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    peasant = player.summon("RLK_070")
    peasant.destroy()

    token = player.field[0]
    assert token.id == "RLK_070t"
    assert (token.atk, token.health) == (2, 2)
    assert Race.UNDEAD in token.races


def test_core_kul_tiran_chaplain_gives_friendly_minion_health():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    target = player.summon(WISP)

    player.give("CORE_EX1_195").play(target=target)

    assert target.max_health == 3
    assert target.health == 3


def test_brittleskin_zombie_damages_opponent_on_opponent_turn_only():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    zombie = player.summon("RLK_113")
    zombie.destroy()
    assert player.opponent.hero.damage == 0

    zombie = player.summon("RLK_113")
    game.end_turn()
    zombie.destroy()

    assert player.opponent.hero.damage == 3


def test_core_natalie_seline_destroys_minion_and_gains_its_health():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    target = player.opponent.summon("CS2_200")

    natalie = player.give("CORE_EX1_198").play(target=target)

    assert target.zone == Zone.GRAVEYARD
    assert natalie.max_health == natalie.data.health + target.data.health
    assert natalie.health == natalie.max_health


def test_scourge_illusionist_adds_discounted_four_four_deathrattle_copy():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    minion = player.card("RLK_070")
    minion.zone = Zone.DECK

    illusionist = player.summon("RLK_217")
    illusionist.destroy()

    copied = player.hand[0]
    assert copied.id == "RLK_070"
    assert (copied.atk, copied.health) == (4, 4)
    assert copied.cost == max(0, copied.data.cost - 4)


def test_core_azure_drake_draws_a_card():
    game = prepare_empty_game()
    player = game.current_player
    card = player.card(WISP)
    card.zone = Zone.DECK

    player.give("CORE_EX1_284").play()

    assert card in player.hand


def test_thassarian_battlecry_and_deathrattle_damage_random_enemy():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    thassarian = player.give("RLK_223").play()
    assert player.opponent.hero.damage == 2

    thassarian.destroy()

    assert player.opponent.hero.damage == 4


def test_core_void_terror_destroys_adjacent_minions_and_gains_stats():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    left = player.summon(WISP)
    right = player.summon("CS2_231")

    terror = player.give("CORE_EX1_304").play(index=1)

    assert left.zone == Zone.GRAVEYARD
    assert right.zone == Zone.GRAVEYARD
    assert terror.atk == terror.data.atk + left.data.atk + right.data.atk
    assert terror.health == terror.data.health + left.data.health + right.data.health


def test_core_doomguard_discards_two_random_cards():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    first = player.give(WISP)
    second = player.give("CS2_231")

    player.give("CORE_EX1_310").play()

    assert first.zone == Zone.REMOVEDFROMGAME
    assert second.zone == Zone.REMOVEDFROMGAME
    assert not player.hand


def test_core_flame_imp_damages_own_hero():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player

    player.give("CORE_EX1_319").play()

    assert player.hero.damage == 3


def test_core_argent_protector_gives_friendly_minion_divine_shield():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    target = player.summon(WISP)

    player.give("CORE_EX1_362").play(target=target)

    assert target.divine_shield


def test_core_aldor_peacekeeper_sets_enemy_minion_attack_to_one():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    target = player.opponent.summon("CS2_200")

    player.give("CORE_EX1_382").play(target=target)

    assert target.atk == 1


def test_core_murloc_tidehunter_summons_murloc_scout():
    game = prepare_empty_game()
    player = game.current_player

    player.give("CORE_EX1_506").play()

    assert len(player.field.filter(id="CORE_EX1_506a")) == 1


def test_core_faceless_manipulator_becomes_copy_of_target_minion():
    game = prepare_empty_game()
    player = game.current_player
    target = player.opponent.summon("CS2_200")

    player.give("CORE_EX1_564").play(target=target)

    faceless = player.field[0]
    assert faceless.id == "CS2_200"
    assert (faceless.atk, faceless.health) == (6, 7)


def test_core_cruel_taskmaster_damages_minion_and_grants_attack():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    target = player.summon("CS2_200")

    player.give("CORE_EX1_603").play(target=target)

    assert target.damage == 1
    assert target.atk == 8


def test_core_temple_enforcer_gives_friendly_minion_health():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    target = player.summon(WISP)

    player.give("CORE_EX1_623").play(target=target)

    assert target.max_health == 4
    assert target.health == 4


def test_harth_stonebrew_replaces_hand_once_per_game():
    game = prepare_empty_game()
    player = game.current_player
    old_card = player.give(WISP)

    player.give("CORE_GIFT_01").play()

    assert old_card.zone == Zone.REMOVEDFROMGAME
    assert player.hand
    first_hand = [card.id for card in player.hand]

    player.used_mana = 0
    player.give(WISP)
    player.give("CORE_GIFT_01").play()

    assert [card.id for card in player.hand][: len(first_hand)] == first_hand


def test_core_mossy_horror_destroys_other_low_attack_minions():
    game = prepare_empty_game()
    player = game.current_player
    low = player.summon(WISP)
    enemy_low = player.opponent.summon("CS2_231")
    high = player.opponent.summon("CS2_200")

    horror = player.give("CORE_GIL_124").play()

    assert horror.zone == Zone.PLAY
    assert low.zone == Zone.GRAVEYARD
    assert enemy_low.zone == Zone.GRAVEYARD
    assert high.zone == Zone.PLAY


def test_harbinger_of_winter_deathrattle_draws_frost_spell():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    frost_spell = player.card("CS2_024")
    frost_spell.zone = Zone.DECK
    non_frost = player.card(WISP)
    non_frost.zone = Zone.DECK

    harbinger = player.summon("RLK_511")
    harbinger.destroy()

    assert frost_spell in player.hand
    assert non_frost in player.deck


def test_amorphous_slime_discards_undead_and_summons_copy_on_deathrattle():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    undead = player.give("FP1_001")
    non_undead = player.give(WISP)

    slime = player.give("RLK_540").play()

    assert undead.zone == Zone.REMOVEDFROMGAME
    assert non_undead in player.hand

    slime.destroy()

    assert len(player.field.filter(id="FP1_001")) == 1


def test_arcsplitter_deathrattle_adds_two_arcane_bolts():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player

    arcsplitter = player.summon("RLK_542")
    arcsplitter.destroy()

    assert [card.id for card in player.hand].count("RLK_843") == 2


def test_blightblood_berserker_deathrattle_damages_random_enemy():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    berserker = player.summon("RLK_551")
    berserker.destroy()

    assert player.opponent.hero.damage == 3


def test_harkener_of_dread_deathrattle_summons_drakkari_specter():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    harkener = player.summon("RLK_554")
    harkener.destroy()

    specter = player.field.filter(id="RLK_554t")[0]
    assert specter.id == "RLK_554t"
    assert (specter.atk, specter.health) == (4, 4)
    assert specter.taunt


def test_bonelord_frostwhisper_makes_first_card_free_and_kills_in_three_turns():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    first = player.give("CS2_200")
    second = player.give("CS2_231")

    bonelord = player.summon("RLK_591")
    bonelord.destroy()

    assert first.cost == 0
    assert second.cost == second.data.cost

    first.play()
    assert second.cost == second.data.cost

    game.end_turn()
    game.end_turn()
    game.end_turn()
    game.end_turn()
    game.end_turn()
    with pytest.raises(GameOver):
        game.end_turn()


def test_invincible_battlecry_and_deathrattle_buff_another_friendly_undead():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    target = player.summon("FP1_001")

    invincible = player.give("RLK_592").play()

    assert (target.atk, target.health) == (7, 8)
    assert target.taunt

    second = player.summon("ICC_900")
    attack_before = target.atk + second.atk
    health_before = target.health + second.health
    invincible.destroy()

    assert target.atk + second.atk == attack_before + 5
    assert target.health + second.health == health_before + 5
    assert target.taunt or second.taunt


def test_thoribelore_goes_dormant_then_revives_after_fire_spell():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    thoribelore = player.summon("RLK_604")
    thoribelore.destroy()

    assert thoribelore in player.field
    assert thoribelore.dormant
    assert not thoribelore.dead

    player.give("CS2_029").play(target=player.opponent.hero)

    assert thoribelore in player.field
    assert not thoribelore.dormant


def test_lingering_zombie_deathrattle_chain_summons_zombies():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player

    lingering = player.summon("RLK_650")
    lingering.destroy()

    disarmed = player.field[0]
    assert disarmed.id == "RLK_650t"

    disarmed.destroy()

    assert player.field[0].id == "RLK_650t2"


def test_infectious_ghoul_deathrattle_grants_ghoul_summoning_deathrattle():
    game = prepare_empty_game()
    player = game.current_player
    target = player.summon(WISP)

    ghoul = player.summon("RLK_653")
    ghoul.destroy()

    assert target.has_deathrattle

    target.destroy()

    assert len(player.field.filter(id="RLK_653")) == 1


def test_chillfallen_baron_battlecry_and_deathrattle_draw_cards():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    first = player.card(WISP)
    first.zone = Zone.DECK
    second = player.card("CS2_231")
    second.zone = Zone.DECK

    baron = player.give("RLK_708").play()

    assert [card.id for card in player.hand] == [first.id]

    baron.destroy()

    assert sorted(card.id for card in player.hand) == sorted([first.id, second.id])


def test_core_town_crier_draws_rush_minion():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    non_rush = player.card(WISP)
    non_rush.zone = Zone.DECK
    rush = player.card("AV_132")
    rush.zone = Zone.DECK

    player.give("CORE_GIL_580").play()

    assert [card.id for card in player.hand] == [rush.id]
    assert [card.id for card in player.deck] == [non_rush.id]


def test_lady_deathwhisper_deathrattle_copies_frost_spells_in_hand():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    frost_spell = player.give("AV_266")
    non_frost_spell = player.give("CS2_029")
    lady = player.summon("RLK_713")

    lady.destroy()

    hand_ids = [card.id for card in player.hand]
    assert hand_ids.count(frost_spell.id) == 2
    assert hand_ids.count(non_frost_spell.id) == 1


def test_core_tess_greymane_replays_other_class_minions():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player

    player.give("CS2_033").play()
    assert len(player.field.filter(id="CS2_033")) == 1

    player.used_mana = 0
    player.give("CORE_GIL_598").play()

    assert len(player.field.filter(id="CS2_033")) == 2


def test_bonecaller_deathrattle_summons_risen_skeleton():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player

    bonecaller = player.summon("RLK_813")
    bonecaller.destroy()

    skeleton = player.field[0]
    assert skeleton.id == "SCH_710t"
    assert skeleton.atk == 2
    assert skeleton.health == 2
    assert skeleton.taunt


def test_core_lifedrinker_damages_enemy_hero_and_heals_own_hero():
    game = prepare_empty_game()
    player = game.current_player
    player.hero.damage = 5

    player.give("CORE_GIL_622").play()

    assert player.opponent.hero.damage == 3
    assert player.hero.damage == 2


def test_flesh_behemoth_deathrattle_draws_undead_and_summons_copy():
    game = prepare_empty_game()
    player = game.current_player
    non_undead = player.card(WISP)
    non_undead.zone = Zone.DECK
    undead = player.card("FP1_001")
    undead.zone = Zone.DECK

    behemoth = player.summon("RLK_830")
    behemoth.destroy()

    assert [card.id for card in player.hand] == [undead.id]
    assert [card.id for card in player.deck] == [non_undead.id]
    assert len(player.field.filter(id=undead.id)) == 1


def test_core_shieldmaiden_gains_armor():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    player.give("CORE_GVG_053").play()

    assert player.hero.armor == 5


def test_plaguespreader_deathrattle_transforms_opponent_hand_minion():
    game = prepare_empty_game()
    player = game.current_player
    opponent = player.opponent
    opponent.hand.clear()
    minion = opponent.give(WISP)
    spell = opponent.give("CS2_029")

    plaguespreader = player.summon("RLK_831")
    plaguespreader.destroy()

    assert [card.id for card in opponent.hand] == ["RLK_831", spell.id]
    assert minion.zone == Zone.SETASIDE


def test_core_dr_boom_summons_two_boom_bots():
    game = prepare_empty_game()
    player = game.current_player

    player.give("CORE_GVG_110").play()

    assert len(player.field.filter(id="GVG_110t")) == 2


def test_foul_egg_deathrattle_summons_foul_fowl():
    game = prepare_empty_game()
    player = game.current_player

    egg = player.summon("RLK_833")
    egg.destroy()

    fowl = player.field[0]
    assert fowl.id == "RLK_833t"
    assert fowl.atk == 3
    assert fowl.health == 3


def test_core_phantom_freebooter_gains_friendly_weapon_stats():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    weapon = player.give("CS2_106").play()
    freebooter = player.give("CORE_ICC_018")
    original_atk = freebooter.atk
    original_health = freebooter.health

    freebooter.play()

    assert freebooter.atk == original_atk + weapon.atk
    assert freebooter.health == original_health + weapon.durability


def test_mind_eater_deathrattle_copies_card_from_opponent_deck():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    opponent_card = player.opponent.card(WISP)
    opponent_card.zone = Zone.DECK

    mind_eater = player.summon("RLK_845")
    mind_eater.destroy()

    assert [card.id for card in player.hand] == [opponent_card.id]
    assert [card.id for card in player.opponent.deck] == [opponent_card.id]


def test_core_grim_necromancer_summons_two_skeletons():
    game = prepare_empty_game()
    player = game.current_player

    player.give("CORE_ICC_026").play()

    assert len(player.field.filter(id="ICC_026t")) == 2


def test_umbral_geist_deathrattle_adds_shadow_spell():
    game = prepare_empty_game()
    player = game.current_player

    geist = player.summon("RLK_914")
    geist.destroy()

    assert len(player.hand) == 1
    assert player.hand[0].data.spell_school == SpellSchool.SHADOW


def test_core_sunborne_valkyr_buffs_adjacent_minion_health():
    game = prepare_empty_game()
    player = game.current_player
    left = player.summon(WISP)
    player.give("CORE_ICC_028").play()
    right = player.summon(WISP)

    assert left.max_health == 3
    assert left.health == 3
    assert right.max_health == 1
    assert right.health == 1


def test_wailing_banshee_deathrattle_buffs_friendly_undead():
    game = prepare_empty_game()
    player = game.current_player
    undead = player.summon("FP1_001")
    non_undead = player.summon(WISP)

    banshee = player.summon("RLK_957")
    banshee.destroy()

    assert undead.atk == undead.data.atk + 2
    assert undead.max_health == undead.data.health + 1
    assert non_undead.atk == non_undead.data.atk
    assert non_undead.max_health == non_undead.data.health


def test_core_brrrloc_freezes_enemy():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    enemy = player.opponent.summon(WISP)

    player.give("CORE_ICC_058").play(target=enemy)

    assert enemy.frozen


def test_spawning_pool_deathrattle_gives_friendly_zerg_rush_this_turn():
    game = prepare_empty_game()
    player = game.current_player
    zerg = player.summon("SC_010")
    non_zerg = player.summon(WISP)

    pool = player.summon("SC_000")
    pool.destroy()

    assert zerg.rush
    assert not non_zerg.rush


def test_core_ghastly_conjurer_adds_mirror_image():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player

    player.give("CORE_ICC_069").play()

    assert [card.id for card in player.hand] == ["CS2_027"]


def test_infestor_deathrattle_gives_zerg_attack_for_rest_of_game():
    game = prepare_empty_game()
    player = game.current_player
    zerg = player.summon("SC_010")
    non_zerg = player.summon(WISP)

    infestor = player.summon("SC_002")
    infestor.destroy()

    assert zerg.atk == zerg.data.atk + 1
    assert non_zerg.atk == non_zerg.data.atk

    new_zerg = player.summon("SC_010")
    assert new_zerg.atk == new_zerg.data.atk + 1


def test_core_acherus_veteran_buffs_friendly_minion_attack():
    game = prepare_empty_game()
    player = game.current_player
    target = player.summon(WISP)
    enemy = player.opponent.summon(WISP)

    player.give("CORE_ICC_092").play(target=target)

    assert target.atk == target.data.atk + 1
    assert enemy.atk == enemy.data.atk


def test_core_tuskarr_fisherman_gives_friendly_minion_spell_damage():
    game = prepare_empty_game()
    player = game.current_player
    target = player.summon(WISP)
    enemy = player.opponent.summon(WISP)

    player.give("CORE_ICC_093").play(target=target)

    assert target.spellpower == 1
    assert player.spellpower == 1
    assert enemy.spellpower == 0


def test_core_fallen_sun_cleric_buffs_friendly_minion_stats():
    game = prepare_empty_game()
    player = game.current_player
    target = player.summon(WISP)
    enemy = player.opponent.summon(WISP)

    player.give("CORE_ICC_094").play(target=target)

    assert target.atk == target.data.atk + 1
    assert target.max_health == target.data.health + 1
    assert enemy.atk == enemy.data.atk
    assert enemy.max_health == enemy.data.health


def test_core_furnacefire_colossus_discards_weapons_and_gains_stats():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    weapon = player.give("CS2_106")
    second_weapon = player.give("CS2_091")
    spell = player.give("CS2_108")
    colossus = player.give("CORE_ICC_096")
    original_atk = colossus.atk
    original_health = colossus.health

    colossus.play()

    assert colossus.atk == original_atk + weapon.atk + second_weapon.atk
    assert colossus.max_health == original_health + weapon.durability + second_weapon.durability
    assert weapon.zone == Zone.REMOVEDFROMGAME
    assert second_weapon.zone == Zone.REMOVEDFROMGAME
    assert spell.zone == Zone.HAND


def test_core_tomb_lurker_adds_died_deathrattle_minion_to_hand():
    game = prepare_empty_game()
    player = game.current_player

    egg = player.summon("SCH_147")
    egg.destroy()

    player.give("CORE_ICC_098").play()

    assert any(card.id == "SCH_147" for card in player.hand)


def test_core_archbishop_benedictus_shuffles_copy_of_opponent_deck():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    opponent = player.opponent
    first = opponent.card(WISP)
    first.zone = Zone.DECK
    second = opponent.card("SCH_340")
    second.zone = Zone.DECK

    player.give("CORE_ICC_215").play()

    assert [card.id for card in opponent.deck] == [first.id, second.id]
    assert [card.id for card in player.deck] == [first.id, second.id]
    assert all(card is not original for card, original in zip(player.deck, opponent.deck))


def test_core_coldwraith_draws_if_an_enemy_is_frozen():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    frozen_enemy = player.opponent.summon(WISP)
    frozen_enemy.frozen = True
    drawn = player.card("SCH_340")
    drawn.zone = Zone.DECK

    player.give("CORE_ICC_252").play()

    assert drawn.zone == Zone.HAND


def test_core_corpse_raiser_gives_deathrattle_to_resummon_minion():
    game = prepare_empty_game()
    player = game.current_player
    target = player.summon(WISP)

    player.give("CORE_ICC_257").play(target=target)
    target.destroy()

    resummoned = next(minion for minion in player.field if minion.id == WISP)
    assert resummoned.id == WISP
    assert resummoned is not target


def test_core_gnomeferatu_removes_top_card_of_opponent_deck():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    opponent = player.opponent
    bottom = opponent.card(WISP)
    bottom.zone = Zone.DECK
    top = opponent.card("SCH_340")
    top.zone = Zone.DECK

    player.give("CORE_ICC_407").play()

    assert top.zone == Zone.REMOVEDFROMGAME
    assert [card.id for card in opponent.deck] == [bottom.id]


def test_core_stitched_tracker_discovers_copy_of_deck_minion():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    deck_minion = player.card("SCH_340")
    deck_minion.zone = Zone.DECK
    deck_spell = player.card("CS2_029")
    deck_spell.zone = Zone.DECK

    player.give("CORE_ICC_415").play()

    assert player.choice
    assert all(card.id == deck_minion.id for card in player.choice.cards)
    picked = player.choice.cards[0]
    player.choice.choose(picked)

    assert picked.zone == Zone.HAND
    assert deck_minion.zone == Zone.DECK


def test_core_death_revenant_gains_stats_for_each_damaged_minion():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player
    damaged_friendly = player.summon("CS2_120")
    damaged_enemy = player.opponent.summon("CS2_120")
    undamaged = player.summon(WISP)
    damaged_friendly.damage = 1
    damaged_enemy.damage = 1

    revenant = player.give("CORE_ICC_450").play()

    assert revenant.atk == revenant.data.atk + 2
    assert revenant.max_health == revenant.data.health + 2
    assert undamaged.damage == 0


def test_core_saronite_chain_gang_summons_copy_of_itself():
    game = prepare_empty_game()
    player = game.current_player

    original = player.give("CORE_ICC_466").play()

    assert len(player.field.filter(id="CORE_ICC_466")) == 2
    copy = next(minion for minion in player.field if minion is not original)
    assert copy.taunt
    assert copy.atk == original.atk
    assert copy.health == original.health


def test_core_deathspeaker_gives_friendly_minion_immune_this_turn():
    game = prepare_empty_game()
    player = game.current_player
    target = player.summon(WISP)
    enemy = player.opponent.summon(WISP)

    player.give("CORE_ICC_467").play(target=target)

    assert target.immune
    assert not enemy.immune


def test_core_thrall_deathseer_evolves_friendly_minions_by_two():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    one_cost = player.summon(WISP)
    two_cost = player.summon("CS2_120")

    player.give("CORE_ICC_481").play()

    assert [minion.cost for minion in player.field] == [
        one_cost.data.cost + 2,
        two_cost.data.cost + 2,
    ]


def test_core_skulking_geist_destroys_one_cost_spells_in_hands_and_decks():
    game = prepare_empty_game()
    player = game.current_player
    own_spell = player.give("CS2_005")
    own_minion = player.give(WISP)
    enemy_spell = player.opponent.give("CS2_005")
    enemy_two_cost_spell = player.opponent.give("CS2_029")
    deck_spell = player.card("CS2_005")
    deck_spell.zone = Zone.DECK

    player.give("CORE_ICC_701").play()

    assert own_spell.zone == Zone.GRAVEYARD
    assert enemy_spell.zone == Zone.GRAVEYARD
    assert deck_spell.zone == Zone.GRAVEYARD
    assert own_minion.zone == Zone.HAND
    assert enemy_two_cost_spell.zone == Zone.HAND


def test_core_bonemare_buffs_friendly_minion_and_gives_taunt():
    game = prepare_empty_game()
    player = game.current_player
    target = player.summon(WISP)

    player.give("CORE_ICC_705").play(target=target)

    assert target.atk == 5
    assert target.health == 5
    assert target.taunt


def test_stubborn_suspect_deathrattle_summons_random_three_cost_minion():
    game = prepare_empty_game()
    player = game.current_player

    suspect = player.summon("SW_006")
    suspect.destroy()

    summoned = player.field[0]
    assert summoned.cost == 3
    assert summoned.type == CardType.MINION


def test_core_howling_commander_draws_divine_shield_minion():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    divine_shield_minion = player.card("CORE_ICC_038")
    divine_shield_minion.zone = Zone.DECK
    other_minion = player.card(WISP)
    other_minion.zone = Zone.DECK

    player.give("CORE_ICC_801").play()

    assert divine_shield_minion.zone == Zone.HAND
    assert other_minion.zone == Zone.DECK


def test_persistent_peddler_deathrattle_summons_copy_from_deck():
    game = prepare_empty_game(CardClass.DEMONHUNTER, CardClass.DEMONHUNTER)
    player = game.current_player
    peddler = player.summon("SW_042")
    deck_peddler = player.card("SW_042")
    deck_peddler.zone = Zone.DECK
    other_minion = player.card(WISP)
    other_minion.zone = Zone.DECK

    peddler.destroy()

    assert deck_peddler in player.field
    assert deck_peddler.zone == Zone.PLAY
    assert other_minion.zone == Zone.DECK


def test_core_strongshell_scavenger_buffs_friendly_taunt_minions():
    game = prepare_empty_game(CardClass.DRUID, CardClass.DRUID)
    player = game.current_player
    taunt = player.summon("CS2_121")
    non_taunt = player.summon(WISP)
    enemy_taunt = player.opponent.summon("CS2_121")

    player.give("CORE_ICC_807").play()

    assert taunt.atk == 4
    assert taunt.health == 4
    assert non_taunt.atk == 1
    assert non_taunt.health == 1
    assert enemy_taunt.atk == 2
    assert enemy_taunt.health == 2


def test_enthusiastic_banker_stores_deck_cards_and_returns_them_on_death():
    game = prepare_empty_game()
    player = game.current_player
    banker = player.summon("SW_069")
    stored = player.card(WISP)
    stored.zone = Zone.DECK

    game.end_turn()

    assert stored.zone == Zone.REMOVEDFROMGAME
    assert stored not in player.deck

    banker.destroy()

    assert stored.zone == Zone.HAND
    assert stored in player.hand


def test_core_deathaxe_punisher_buffs_lifesteal_minion_in_hand():
    game = prepare_empty_game()
    player = game.current_player
    lifesteal = player.give("CORE_GIL_558")
    other = player.give(WISP)

    player.give("CORE_ICC_810").play()

    assert lifesteal.atk == 4
    assert lifesteal.health == 3
    assert other.atk == 1
    assert other.health == 1


def test_mailbox_dancer_battlecry_gives_coin_and_deathrattle_gives_opponent_coin():
    game = prepare_empty_game()
    player = game.current_player
    opponent_coins = [card.id for card in player.opponent.hand].count(THE_COIN)

    dancer = player.give("SW_070").play()

    assert [card.id for card in player.hand] == [THE_COIN]

    dancer.destroy()

    assert [card.id for card in player.opponent.hand].count(THE_COIN) == opponent_coins + 1


def test_core_lilian_voss_replaces_friendly_spells_with_enemy_class_spells():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.MAGE)
    player = game.current_player
    spell = player.give("CS2_072")
    minion = player.give(WISP)

    player.give("CORE_ICC_811").play()

    spells = [card for card in player.hand if card.type == CardType.SPELL]
    assert spell.zone == Zone.SETASIDE
    assert len(spells) == 1
    assert spells[0].card_class == CardClass.MAGE
    assert minion.zone == Zone.HAND


def test_elwynn_boar_equips_sword_after_seven_friendly_boars_die():
    game = prepare_empty_game()
    player = game.current_player

    for _ in range(6):
        player.summon("SW_075").destroy()

    assert player.weapon is None

    player.summon("SW_075").destroy()

    assert player.weapon.id == "SW_075t"
    assert player.weapon.atk == 15
    assert player.weapon.durability == 3


def test_core_valeera_the_hollow_stealths_and_grants_shadow_reflection():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player

    player.give("CORE_ICC_827").play()

    assert player.hero.stealthed
    assert [card.id for card in player.hand] == ["ICC_827t"]

    game.end_turn()
    assert player.hero.stealthed
    game.end_turn()

    assert not player.hero.stealthed
    assert player.hero.power.id == "ICC_827p"


def test_rat_king_goes_dormant_and_revives_after_five_friendly_minions_die():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    rat_king = player.summon("SW_323")

    rat_king.destroy()

    dormant_rat = player.field[0]
    assert dormant_rat.id == "SW_323"
    assert dormant_rat.dormant

    for _ in range(4):
        player.summon(WISP).destroy()

    assert dormant_rat.dormant

    player.summon(WISP).destroy()

    assert dormant_rat in player.field
    assert not dormant_rat.dormant


def test_core_deathstalker_rexxar_damages_all_enemy_minions():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    enemy = player.opponent.summon("CS2_182")
    friendly = player.summon("CS2_182")

    player.give("CORE_ICC_828").play()

    assert enemy.damage == 2
    assert friendly.damage == 0


def test_loan_shark_battlecry_gives_opponent_coin_and_deathrattle_gives_two():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player_coins = [card.id for card in player.hand].count(THE_COIN)
    opponent_coins = [card.id for card in player.opponent.hand].count(THE_COIN)

    shark = player.give("SW_434").play()

    assert [card.id for card in player.opponent.hand].count(THE_COIN) == opponent_coins + 1

    shark.destroy()

    assert [card.id for card in player.hand].count(THE_COIN) == player_coins + 2


def test_core_uther_of_the_ebon_blade_equips_grave_vengeance():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player

    player.give("CORE_ICC_829").play()

    assert player.weapon.id == "ICC_829t"
    assert player.weapon.atk == 5
    assert player.weapon.durability == 3


def test_rodent_nest_deathrattle_summons_five_rats():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player

    nest = player.summon("SW_455")
    nest.destroy()

    assert [minion.id for minion in player.field] == ["SW_455t"] * 5
    assert [(minion.atk, minion.health) for minion in player.field] == [(1, 1)] * 5


def test_core_shadowreaper_anduin_destroys_high_attack_minions():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    friendly_high_attack = player.summon("CS2_200")
    enemy_high_attack = player.opponent.summon("CS2_200")
    enemy_low_attack = player.opponent.summon(WISP)

    player.give("CORE_ICC_830").play()

    assert friendly_high_attack.zone == Zone.GRAVEYARD
    assert enemy_high_attack.zone == Zone.GRAVEYARD
    assert enemy_low_attack.zone == Zone.PLAY


def test_imported_tarantula_deathrattle_summons_two_poisonous_rush_spiders():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player

    tarantula = player.summon("SW_463")
    tarantula.destroy()

    assert [minion.id for minion in player.field] == ["SW_463t", "SW_463t"]
    assert all(minion.poisonous and minion.rush for minion in player.field)


def test_core_bloodreaver_guldan_summons_friendly_demons_that_died():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    demon = player.summon("CORE_EX1_310")
    non_demon = player.summon(WISP)
    demon.destroy()
    non_demon.destroy()

    player.give("CORE_ICC_831").play()

    assert [minion.id for minion in player.field] == ["CORE_EX1_310"]


def test_submerged_spacerock_deathrattle_adds_two_temporary_arcane_mage_spells():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player

    spacerock = player.summon("TID_707")
    spacerock.destroy()

    assert len(player.hand) == 2
    assert all(card.card_class == CardClass.MAGE for card in player.hand)
    assert all(card.type == CardType.SPELL for card in player.hand)
    assert all(card.data.spell_school == SpellSchool.ARCANE for card in player.hand)

    game.end_turn()

    assert len(player.hand) == 0


def test_core_frost_lich_jaina_summons_water_elemental_and_grants_lifesteal():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    elemental = player.summon("UNG_809")
    assert not elemental.lifesteal

    player.give("CORE_ICC_833").play()

    assert [minion.id for minion in player.field] == ["UNG_809", "ICC_833t"]
    assert elemental.lifesteal
    assert player.hero.power.id == "ICC_833h"


def test_ozumat_deathrattle_destroys_one_enemy_minion_per_tentacle():
    game = prepare_empty_game()
    player = game.current_player
    ozumat = player.summon("TID_711")
    player.summon("TID_711t")
    player.summon("TID_711t2")
    for _ in range(4):
        player.opponent.summon(WISP)

    ozumat.destroy()

    assert len(player.opponent.field) == 2


def test_core_scourgelord_garrosh_equips_shadowmourne():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    player.give("CORE_ICC_834").play()

    assert player.weapon.id == "ICC_834w"
    assert player.hero.power.id == "ICC_834h"


def test_tankgineer_deathrattle_summons_force_tank_max():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    tankgineer = player.summon("TIME_017")

    tankgineer.destroy()

    tank = player.field[0]
    assert tank.id == "GVG_079"
    assert tank.atk == 7
    assert tank.health == 7
    assert tank.divine_shield


def test_core_sindragosa_summons_two_frozen_champions():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player

    player.give("CORE_ICC_838").play()

    assert [minion.id for minion in player.field] == ["ICC_838t", "CORE_ICC_838", "ICC_838t"]
    champions = [minion for minion in player.field if minion.id == "ICC_838t"]
    assert [(minion.atk, minion.health) for minion in champions] == [(0, 1), (0, 1)]


def test_time_machine_deathrattle_adds_random_rewind_card():
    game = prepare_empty_game()
    player = game.current_player
    time_machine = player.summon("TIME_035")

    time_machine.destroy()

    assert len(player.hand) == 1
    card = player.hand[0]
    assert card.data.collectible
    assert card.data.tags.get(GameTag.REWIND)


def test_core_shadowblade_makes_hero_immune_this_turn():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player

    player.give("CORE_ICC_850").play()

    assert player.weapon.id == "CORE_ICC_850"
    assert player.hero.immune

    game.end_turn()

    assert not player.hero.immune


def test_fading_memory_deathrattle_adds_random_five_cost_minion_from_past():
    game = prepare_empty_game()
    player = game.current_player
    fading_memory = player.summon("TIME_040")

    fading_memory.destroy()

    assert len(player.hand) == 1
    card = player.hand[0]
    assert card.type == CardType.MINION
    assert card.cost == 5
    assert not card.data.is_standard


def test_core_prince_keleseth_buffs_minions_in_deck_without_two_cost_cards():
    game = prepare_empty_game()
    player = game.current_player
    player.deck.clear()
    minion = player.give(WISP)
    spell = player.give("CS2_005")
    other_minion = player.give("CS2_182")
    minion.zone = Zone.DECK
    spell.zone = Zone.DECK
    other_minion.zone = Zone.DECK

    player.give("CORE_ICC_851").play()

    assert minion.atk == 2
    assert minion.health == 2
    assert spell.cost == 1
    assert other_minion.atk == 5
    assert other_minion.health == 6


def test_core_prince_keleseth_does_not_buff_deck_with_two_cost_card():
    game = prepare_empty_game()
    player = game.current_player
    player.deck.clear()
    minion = player.give(WISP)
    two_cost = player.give("CORE_EX1_096")
    minion.zone = Zone.DECK
    two_cost.zone = Zone.DECK

    player.give("CORE_ICC_851").play()

    assert minion.atk == 1
    assert minion.health == 1


def test_amber_warden_deathrattle_summons_random_minion_from_past():
    game = prepare_empty_game()
    player = game.current_player
    amber_warden = player.summon("TIME_052")

    amber_warden.destroy()

    assert len(player.field) == 1
    minion = player.field[0]
    assert minion.type == CardType.MINION
    assert not minion.data.is_standard


def test_core_prince_taldaram_becomes_three_three_copy_without_three_cost_cards():
    game = prepare_empty_game()
    player = game.current_player
    player.deck.clear()
    target = player.summon("CS2_182")

    player.give("CORE_ICC_852").play(target=target)

    taldaram = player.field[-1]
    assert taldaram.id == "CS2_182"
    assert taldaram.atk == 3
    assert taldaram.health == 3


def test_chromie_deathrattle_draws_copies_of_played_cards_from_deck():
    game = prepare_empty_game()
    player = game.current_player
    player.deck.clear()
    played = player.give(WISP)
    deck_copy = player.give(WISP)
    unplayed_copy = player.give("CS2_182")
    deck_copy.zone = Zone.DECK
    unplayed_copy.zone = Zone.DECK
    chromie = player.summon("TIME_103")

    played.play()
    chromie.destroy()

    assert [card.id for card in player.hand] == [WISP]
    assert [card.id for card in player.deck] == ["CS2_182"]


def test_ultralisk_cavern_deathrattle_summons_ultralisk():
    game = prepare_empty_game()
    player = game.current_player

    cavern = player.summon("SC_019")
    cavern.destroy()

    ultralisk = player.field[0]
    assert ultralisk.id == "SC_006"
    assert ultralisk.atk == 8
    assert ultralisk.health == 8
    assert ultralisk.rush


def test_mothership_battlecry_and_deathrattle_add_two_protoss_minions():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    mothership_card = player.give("SC_762")
    mothership_card.cost = 0

    mothership_card.play()

    assert len(player.hand) == 2
    assert all(card.type == CardType.MINION for card in player.hand)
    assert all(card.data.tags.get(GameTag.PROTOSS) for card in player.hand)

    mothership = player.summon("SC_762")
    mothership.destroy()

    assert len(player.hand) == 4
    assert all(card.type == CardType.MINION for card in player.hand)
    assert all(card.data.tags.get(GameTag.PROTOSS) for card in player.hand)


def test_sentry_deathrattle_discounts_protoss_minions_this_game():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    protoss_in_hand = player.give("SC_763")
    non_protoss = player.give(WISP)
    protoss_in_deck = player.card("SC_783")
    protoss_in_deck.zone = Zone.DECK
    hand_cost = protoss_in_hand.cost
    deck_cost = protoss_in_deck.cost

    sentry = player.summon("SC_764")
    sentry.destroy()

    assert protoss_in_hand.cost == hand_cost - 1
    assert non_protoss.cost == non_protoss.data.cost
    assert protoss_in_deck.cost == deck_cost - 1

    future_protoss = player.give("SC_765")
    assert future_protoss.cost == future_protoss.data.cost - 1


def test_boneweb_egg_deathrattle_and_discard_summon_two_spiders():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player

    egg = player.summon("SCH_147")
    egg.destroy()

    assert len(player.field.filter(id="SCH_147t")) == 2

    for minion in list(player.field):
        minion.destroy()

    egg_in_hand = player.give("SCH_147")
    egg_in_hand.discard()

    assert egg_in_hand.zone == Zone.REMOVEDFROMGAME
    assert len(player.field.filter(id="SCH_147t")) == 2


def test_teachers_pet_deathrattle_summons_random_three_cost_beast():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player

    pet = player.summon("SCH_244")
    pet.destroy()

    summoned = player.field[0]
    assert summoned.cost == 3
    assert Race.BEAST in summoned.races


def test_bloated_python_deathrattle_summons_hapless_handler():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player

    python = player.summon("SCH_340")
    python.destroy()

    handler = player.field[0]
    assert handler.id == "SCH_340t"
    assert handler.atk == 4
    assert handler.health == 4


def test_infiltrator_lilian_deathrattle_summons_attacking_forsaken_lilian():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    enemy = player.opponent.summon(WISP)

    lilian = player.summon("SCH_426")
    lilian.destroy()

    forsaken = player.field[0]
    assert forsaken.id == "SCH_426t"
    assert enemy.dead
    assert forsaken.damage == 1


def test_lord_barov_sets_other_minions_to_one_health_and_deals_one_on_death():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    friendly = player.summon("CS2_120")
    enemy = player.opponent.summon("CS2_120")

    barov = player.give("SCH_526").play()

    assert friendly.health == 1
    assert enemy.health == 1
    assert barov.health == barov.data.health

    barov.destroy()

    assert friendly.dead
    assert enemy.dead


def test_totem_goliath_deathrattle_summons_all_basic_totems():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player

    goliath = player.summon("SCH_615")
    goliath.destroy()

    assert sorted(card.id for card in player.field) == sorted(BASIC_TOTEMS)


def test_rattlegore_deathrattle_resummons_with_minus_one_minus_one():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    rattlegore = player.summon("SCH_621")
    rattlegore.destroy()

    smaller = player.field[0]
    assert smaller.id == "SCH_621"
    assert smaller.atk == 8
    assert smaller.health == 8
    assert smaller.max_health == 8


def test_fishy_flyer_deathrattle_adds_spectral_flyer_to_hand():
    game = prepare_empty_game()
    player = game.current_player

    flyer = player.summon("SCH_707")
    flyer.destroy()

    assert [card.id for card in player.hand] == ["SCH_707t"]
    assert player.hand[0].rush


def test_sneaky_delinquent_deathrattle_adds_spectral_delinquent_to_hand():
    game = prepare_empty_game()
    player = game.current_player

    delinquent = player.summon("SCH_708")
    delinquent.destroy()

    assert [card.id for card in player.hand] == ["SCH_708t"]
    assert player.hand[0].stealthed


def test_smug_senior_deathrattle_adds_spectral_senior_to_hand():
    game = prepare_empty_game()
    player = game.current_player

    senior = player.summon("SCH_709")
    senior.destroy()

    assert [card.id for card in player.hand] == ["SCH_709t"]
    assert player.hand[0].taunt


def test_plagued_protodrake_deathrattle_summons_random_seven_cost_minion():
    game = prepare_empty_game()
    player = game.current_player

    protodrake = player.summon("SCH_711")
    protodrake.destroy()

    summoned = player.field[0]
    assert summoned.cost == 7
    assert summoned.type == CardType.MINION


def test_educated_elekk_deathrattle_shuffles_remembered_spells():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    elekk = player.summon("SCH_714")

    player.give("CS2_008").play(target=player.opponent.hero)
    player.give("CS2_029").play(target=player.opponent.hero)
    elekk.destroy()

    assert sorted(card.id for card in player.deck) == ["CS2_008", "CS2_029"]


def test_iron_juggernaut_shuffles_mine_on_battlecry_and_deathrattle():
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.WARRIOR)
    player = game.current_player

    juggernaut = player.give("GVG_056").play()

    assert [card.id for card in player.opponent.deck].count("GVG_056t") == 1

    juggernaut.destroy()

    assert [card.id for card in player.opponent.deck].count("GVG_056t") == 2


def test_interstellar_starslicer_discounts_librams_on_battlecry_and_deathrattle():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    libram = player.give("BT_011")
    original_cost = libram.cost

    weapon = player.give("GDB_726").play()

    assert libram.cost == original_cost - 1

    weapon.destroy()

    assert libram.cost == original_cost - 2


def test_overzealous_healer_heals_enemy_hero_unless_silenced_by_spellburst():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.opponent.hero.damage = 10

    healer = player.give("GDB_454").play()
    healer.destroy()

    assert player.opponent.hero.damage == 4

    second = player.give("GDB_454").play()
    player.give("CS1_112").play(target=player.hero)
    second.destroy()

    assert player.opponent.hero.damage == 4
