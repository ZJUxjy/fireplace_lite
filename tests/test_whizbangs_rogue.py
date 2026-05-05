from utils import *
from hearthstone.enums import CardClass, CardType, Race, Zone


JUNK_IDS = {"GAME_005", "WW_001t", "EX1_014t", "CS2_082"}


def test_dust_bunny_adds_junk_on_battlecry_and_deathrattle():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    bunny = player.give("MIS_706").play()

    assert player.hand[-1].id in JUNK_IDS

    bunny.destroy()

    assert player.hand[-1].id in JUNK_IDS
    assert len([card for card in player.hand if card.id in JUNK_IDS]) == 2


def test_twisted_pack_adds_five_temporary_other_class_cards():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("MIS_708").play()

    generated = list(player.hand)
    assert len(generated) == 5
    assert all(CardClass.ROGUE not in card.data.classes for card in generated)
    assert all(CardClass.NEUTRAL not in card.data.classes for card in generated)

    game.end_turn()

    assert all(card.zone == Zone.REMOVEDFROMGAME for card in generated)


def test_dubious_purchase_draws_three_and_combo_destroys_enemy():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    for card_id in (WISP, "CS2_182", "CS2_231"):
        player.card(card_id).zone = Zone.DECK
    target = player.opponent.summon("CS2_182")

    player.give("GAME_005").play()
    player.give("MIS_903").play()

    assert len(player.hand) == 3
    assert target.zone == Zone.GRAVEYARD


def test_toy_boat_draws_after_friendly_pirate_is_summoned():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    drawn = player.card(WISP)
    drawn.zone = Zone.DECK

    player.summon("TOY_505")
    player.summon("TOY_516")

    assert drawn in player.hand


def test_dig_for_treasure_draws_pirate_and_gets_coin():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    pirate = player.card("TOY_516")
    pirate.zone = Zone.DECK

    player.give("TOY_510").play()

    assert pirate in player.hand
    assert any(card.id == "GAME_005" for card in player.hand)


def test_shoplifter_goldbeard_summons_attacking_pirate_copy_that_dies():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    enemy = player.opponent.summon("CS2_182")

    player.summon("TOY_511")
    original = player.summon("TOY_516")

    assert original in player.field
    assert enemy.damage >= original.atk or player.opponent.hero.damage >= original.atk
    assert any(card.id == "TOY_516" for card in player.graveyard)


def test_crystal_cove_sets_next_summoned_minion_to_four_four():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    cove = player.give("TOY_512").play()
    cove.use()
    first = player.summon(WISP)
    second = player.summon(WISP)

    assert first.atk == 4
    assert first.max_health == 4
    assert second.atk == second.data.atk
    assert second.max_health == second.data.health
    assert cove.durability == cove.max_durability - 1


def test_thistle_tea_set_discovers_other_class_spell_and_gets_copy():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_514").play()

    assert player.choice is not None
    assert all(card.type == CardType.SPELL for card in player.choice.cards)
    assert all(CardClass.ROGUE not in card.data.classes for card in player.choice.cards)
    choice = player.choice.cards[0]
    player.choice.choose(choice)

    assert len(player.hand.filter(id=choice.id)) == 2


def test_sonya_copies_played_one_cost_minion_at_zero_cost():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.summon("TOY_515")
    player.give("CS2_171").play()

    copies = [card for card in player.hand if card.id == "CS2_171"]
    assert len(copies) == 1
    assert copies[0].cost == 0


def test_bargain_bin_buccaneer_has_rush_and_combo_summons_copy():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("GAME_005").play()
    buccaneer = player.give("TOY_516").play()

    assert buccaneer.rush
    assert len([minion for minion in player.field if minion.id == "TOY_516"]) == 2


def test_everything_must_go_discounts_for_draws_and_summons_two_four_costs():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    for card_id in (WISP, "CS2_182"):
        player.card(card_id).zone = Zone.DECK
    player.deck[-1].draw()
    player.deck[-1].draw()
    spell = player.give("TOY_519")

    assert spell.cost == spell.data.cost - 2

    spell.play()

    assert len(player.field) == 2
    assert all(minion.cost == 4 for minion in player.field)


def test_sandbox_scoundrel_miniaturizes_and_discounts_only_next_card():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    first = player.give("CS2_182")
    second = player.give("CS2_189")

    scoundrel = player.give("TOY_521").play()

    assert scoundrel.id == "TOY_521"
    assert any(card.id == "TOY_521t1" for card in player.hand)
    assert first.cost == max(0, first.data.cost - 2)
    assert second.cost == max(0, second.data.cost - 2)

    first.play()

    assert second.cost == second.data.cost


def test_watercannon_summons_waterslider_that_attacks_random_enemy():
    game = prepare_empty_game(CardClass.ROGUE, CardClass.ROGUE)
    player = game.current_player
    opponent = player.opponent
    player.max_mana = 10
    player.used_mana = 0
    enemy = opponent.summon("CS2_182")

    player.give("TOY_522").play()
    player.hero.attack(opponent.hero)

    sliders = [
        card
        for card in list(player.field) + list(player.graveyard)
        if card.id == "TOY_522t"
    ]
    assert len(sliders) == 1
    assert enemy.damage == 1 or opponent.hero.damage >= player.weapon.atk + 1
