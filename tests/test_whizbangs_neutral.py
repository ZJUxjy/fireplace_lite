from utils import *
from hearthstone.enums import CardClass, CardType, GameTag, Race, Zone


def test_puppetmaster_dorian_copies_drawn_minion_as_one_one_cost_one():
    game = prepare_empty_game()
    player = game.current_player
    dorian = player.summon("MIS_026")
    drawn = player.card(WISP)
    drawn.zone = Zone.DECK

    player.draw()

    copies = [card for card in player.hand if card is not drawn]
    assert dorian in player.field
    assert len(copies) == 1
    assert copies[0].id == WISP
    assert copies[0].atk == 1
    assert copies[0].health == 1
    assert copies[0].cost == 1


def test_explodineer_shuffles_bomb_at_end_of_turn():
    game = prepare_empty_game()
    player = game.current_player
    player.summon("MIS_308")

    game.end_turn()

    assert player.opponent.hero.damage == 5


def test_building_block_golem_summons_three_one_cost_minions():
    game = prepare_empty_game()
    player = game.current_player
    golem = player.summon("MIS_314")

    golem.destroy()

    assert len(player.field) == 3
    assert all(card.type == CardType.MINION and card.cost == 1 for card in player.field)


def test_pro_gamer_winner_draws_two_cards():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    for owner in (player, player.opponent):
        for card_id in (WISP, "CS2_231"):
            owner.card(card_id).zone = Zone.DECK

    before = len(player.hand) + len(player.opponent.hand)

    player.give("MIS_916").play()

    assert len(player.hand) + len(player.opponent.hand) == before + 2


def test_tar_slime_has_extra_attack_on_opponents_turn_only():
    game = prepare_empty_game()
    player = game.current_player
    slime = player.summon("TOY_000")
    game.refresh_auras()

    assert slime.atk == 0

    game.end_turn()
    game.refresh_auras()

    assert slime.atk == 2


def test_scarab_keychain_discovers_two_cost_card():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_006").play()

    assert player.choice
    assert all(card.cost == 2 for card in player.choice.cards)


def test_card_grader_discovers_from_deck_after_spell_cast_while_held():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    grader = player.give("TOY_054")
    deck_card = player.card(WISP)
    deck_card.zone = Zone.DECK

    player.give("GAME_005").play()
    grader.play()

    assert player.choice
    assert deck_card in player.choice.cards


def test_giftwrapped_whelp_buffs_held_dragon_and_itself():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    dragon = player.give("AT_017")
    whelp = player.give("TOY_386")

    whelp.play()

    assert whelp.atk == 3
    assert whelp.health == 2
    assert dragon.atk == dragon.data.atk + 1
    assert dragon.health == dragon.data.health + 1


def test_clearance_promoter_discounts_two_spells_in_hand():
    game = prepare_empty_game()
    player = game.current_player
    first = player.give("CS2_029")
    second = player.give("CS2_022")
    player.give(WISP)
    promoter = player.summon("TOY_390")

    promoter.destroy()

    assert first.cost == first.data.cost - 1
    assert second.cost == second.data.cost - 1


def test_caricature_artist_draws_large_minion():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    large = player.card("CS2_200")
    small = player.card(WISP)
    for card in (large, small):
        card.zone = Zone.DECK

    player.give("TOY_391").play()

    assert large in player.hand
    assert small in player.deck


def test_wind_up_musician_damages_all_enemy_minions():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    enemies = [player.opponent.summon("CS2_172"), player.opponent.summon("CS2_172")]

    player.give("TOY_509").play()

    assert all(enemy.damage == 1 for enemy in enemies)


def test_plucky_paintfin_is_poisonous_and_draws_rush_minion():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    rush = player.card("MIS_711")
    other = player.card(WISP)
    for card in (rush, other):
        card.zone = Zone.DECK

    paintfin = player.give("TOY_517").play()

    assert paintfin.poisonous
    assert rush in player.hand


def test_treasure_distributor_buffs_summoned_pirate_attack():
    game = prepare_empty_game()
    player = game.current_player
    player.summon("TOY_518")
    pirate = player.summon("CS2_146")

    assert pirate.atk == pirate.data.atk + 1


def test_observer_of_mysteries_casts_temporary_secrets():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_520").play()

    assert len(player.secrets) == 2

    game.end_turn()
    game.end_turn()

    assert len(player.secrets) == 0


def test_sing_along_buddy_doubles_hero_power():
    game = prepare_empty_game()
    player = game.current_player
    player.summon("TOY_528")
    game.refresh_auras()

    assert player.hero_power_double == 1


def test_playhouse_giant_costs_less_for_cards_drawn_this_game():
    game = prepare_empty_game()
    player = game.current_player
    for card_id in (WISP, "CS2_231"):
        player.card(card_id).zone = Zone.DECK
    giant = player.give("TOY_530")

    player.draw()
    player.draw()
    game.refresh_auras()

    assert giant.cost == giant.data.cost - 2


def test_lina_fills_board_with_minions_matching_spell_cost():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    lina = player.summon("TOY_531")

    player.give("GAME_005").play()

    assert lina in player.field
    assert len(player.field) == game.MAX_MINIONS_ON_FIELD
    assert all(card.cost == 0 or card is lina for card in player.field)


def test_messmaker_deathrattle_damages_all_enemies():
    game = prepare_empty_game()
    player = game.current_player
    messmaker = player.summon("TOY_646")
    enemy = player.opponent.summon(WISP)
    friendly = player.summon(WISP)

    messmaker.destroy()

    assert player.opponent.hero.damage == 1
    assert enemy.zone == Zone.GRAVEYARD
    assert friendly.damage == 0


def test_giggling_toymaker_summons_two_annoy_o_trons():
    game = prepare_empty_game()
    player = game.current_player
    toymaker = player.summon("TOY_670")

    toymaker.destroy()

    bots = player.field.filter(id="GVG_085")
    assert len(bots) == 2
    assert all(bot.taunt and bot.divine_shield for bot in bots)


def test_colifero_draws_minion_and_transforms_other_friendly_minions():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.summon(WISP)
    deck_minion = player.card("CS2_200")
    deck_minion.zone = Zone.DECK

    player.give("TOY_703").play()

    assert deck_minion in player.hand
    assert any(card.id == "CS2_200" for card in player.field)


def test_bucket_of_soldiers_summons_five_bonus_soldiers():
    game = prepare_empty_game()
    player = game.current_player
    bucket = player.summon("TOY_814")

    bucket.destroy()

    assert len(player.field) == 5
    assert all(card.id.startswith("TOY_814t") for card in player.field)


def test_forgotten_animatronic_destroys_lower_attack_minion_end_turn():
    game = prepare_empty_game()
    player = game.current_player
    player.summon("TOY_820")
    low = player.opponent.summon(WISP)

    game.end_turn()

    assert low.zone == Zone.GRAVEYARD


def test_corridor_sleeper_starts_dormant_and_awakens_after_seven_deaths():
    game = prepare_empty_game()
    player = game.current_player
    sleeper = player.summon("TOY_866")

    assert sleeper.dormant

    for _ in range(7):
        minion = player.summon(WISP)
        minion.destroy()

    assert not sleeper.dormant


def test_cosplay_contestant_transforms_after_opponent_plays_minion():
    game = prepare_empty_game()
    player = game.current_player
    player.summon("TOY_878")
    game.end_turn()
    opponent = game.current_player
    opponent.max_mana = 10
    opponent.used_mana = 0

    opponent.give("CS2_200").play()

    transformed = player.field[0]
    assert transformed.id == "CS2_200"
    assert transformed.atk == 3
    assert transformed.health == 4


def test_workshop_janitor_draws_two_if_you_control_location():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.give("CATA_301").play()
    for card_id in (WISP, "CS2_231"):
        player.card(card_id).zone = Zone.DECK

    player.give("TOY_891").play()

    assert len(player.hand) == 2


def test_nesting_golem_resummons_with_minus_one_minus_one():
    game = prepare_empty_game()
    player = game.current_player
    golem = player.summon("TOY_893")

    golem.destroy()

    nested = player.field[0]
    assert nested.id == "TOY_893"
    assert nested.atk == 3
    assert nested.health == 2


def test_origami_minions_swap_attack_health_and_stats():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    attack_target = player.summon("CS2_200")
    frog = player.give("TOY_894").play(target=attack_target)
    assert frog.atk == 6
    assert attack_target.atk == 1

    health_target = player.summon("CS2_200")
    crane = player.give("TOY_895").play(target=health_target)
    assert crane.health == 7
    assert health_target.health == 1

    player.used_mana = 0
    stats_target = player.summon(WISP)
    dragon = player.give("TOY_896").play(target=stats_target)
    assert (dragon.atk, dragon.health) == (1, 1)
    assert (stats_target.atk, stats_target.health) == (1, 1)


def test_floppy_hydra_shuffles_permanently_doubled_copy():
    game = prepare_empty_game()
    player = game.current_player
    hydra = player.summon("TOY_897")

    hydra.destroy()

    copy = player.deck.filter(id="TOY_897")[0]
    assert copy.atk == 4
    assert copy.health == 8


def test_rumble_enthusiast_hits_random_enemy_after_outermost_card_played():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.summon("TOY_943")
    left = player.give("GAME_005")
    player.give(WISP)

    left.play()

    assert player.opponent.hero.damage == 1


def test_joymancer_jepetto_gets_copies_of_played_one_attack_or_health_minions():
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.give(WISP).play()
    player.give("CS2_200").play()
    player.used_mana = 0

    player.give("TOY_960").play()

    assert any(card.id == WISP for card in player.hand)
    assert not any(card.id == "CS2_200" for card in player.hand)
