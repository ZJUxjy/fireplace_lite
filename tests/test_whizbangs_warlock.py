from utils import *
from hearthstone.enums import CardClass, SpellSchool, Zone

from fireplace.exceptions import GameOver


def test_domino_effect_repeats_right_with_increasing_damage():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    first = player.opponent.summon("CS2_200")
    second = player.opponent.summon("CS2_200")
    third = player.opponent.summon("CS2_200")

    player.give("MIS_027").play(target=first)

    assert first.damage == 2
    assert second.damage == 3
    assert third.damage == 4


def test_infernal_sets_hero_remaining_health_to_fifteen():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.hero.damage = 20

    infernal = player.give("MIS_703").play()

    assert infernal.taunt
    assert player.hero.health == 15


def test_mass_production_draws_two_damages_hero_and_shuffles_copies():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    cards = [player.card(WISP), player.card("CS2_182")]
    for card in cards:
        card.zone = Zone.DECK

    player.give("MIS_707").play()

    assert all(card in player.hand for card in cards)
    assert player.hero.damage == 3
    assert len(player.deck.filter(id="MIS_707")) == 2


def test_game_master_nemsy_draws_demon_and_deathrattle_swaps_with_it():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    demon = player.card("TOY_526")
    demon.zone = Zone.DECK

    nemsy = player.give("TOY_524").play()

    assert demon in player.hand

    nemsy.destroy()

    assert demon in player.field
    assert nemsy in player.hand


def test_malefic_rook_attacks_own_hero_on_battlecry():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_526").play()

    assert player.hero.damage == 5


def test_cursed_campaign_gives_dormant_copy_deathrattle():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.summon(WISP)

    player.give("TOY_527").play(target=target)
    target.destroy()

    copies = player.field.filter(id=WISP)
    assert len(copies) == 2
    assert all(copy.dormant and copy.dormant_turns == 2 for copy in copies)


def test_wheel_of_death_destroys_deck_then_enemy_hero_after_five_enemy_turns():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    opponent = player.opponent
    player.max_mana = 10
    player.used_mana = 0
    for card_id in (WISP, "CS2_182", "CS2_231"):
        player.card(card_id).zone = Zone.DECK

    player.give("TOY_529").play()

    assert len(player.deck) == 0

    for _ in range(5):
        try:
            game.end_turn()
        except GameOver:
            break
        if opponent.hero.zone == Zone.GRAVEYARD:
            break
        try:
            game.end_turn()
        except GameOver:
            break

    assert opponent.hero.zone == Zone.GRAVEYARD


def test_table_flip_discounts_for_other_hand_cards_and_hits_enemy_minions():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    for card_id in (WISP, "CS2_182", "CS2_231"):
        player.give(card_id)
    spell = player.give("TOY_883")
    enemies = [player.opponent.summon("CS2_200"), player.opponent.summon("CS2_200")]
    game.refresh_auras()

    assert spell.cost == 7

    spell.play()

    assert all(enemy.damage == 3 for enemy in enemies)


def test_crane_game_summons_copies_of_two_demons_in_deck():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    demons = [player.card("TOY_526"), player.card("TOY_914")]
    for demon in demons:
        demon.zone = Zone.DECK

    player.give("TOY_884").play()

    assert {minion.id for minion in player.field} == {"TOY_526", "TOY_914"}
    assert all(demon in player.deck for demon in demons)


def test_endgame_resurrects_last_dead_demon():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    first = player.summon("TOY_914")
    second = player.summon("TOY_526")
    first.destroy()
    second.destroy()

    player.give("TOY_886").play()

    assert player.field[-1].id == "TOY_526"


def test_wretched_queen_deathrattle_summons_two_taunt_knights():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    queen = player.summon("TOY_914")

    queen.destroy()

    knights = player.field.filter(id="TOY_914t")
    assert len(knights) == 2
    assert all(knight.taunt and knight.atk == 4 and knight.max_health == 6 for knight in knights)


def test_tabletop_roleplayer_miniaturizes_and_temporarily_buffs_friendly_demon():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    demon = player.summon("TOY_526")

    player.give("TOY_915").play(target=demon)

    assert any(card.id == "TOY_915t" for card in player.hand)
    assert demon.atk == demon.data.atk + 2
    assert demon.immune

    game.end_turn()

    assert demon.atk == demon.data.atk
    assert not demon.immune


def test_sketch_artist_draws_shadow_spell_and_temporary_copy():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    shadow = player.card("TOY_527")
    other = player.card(FIREBALL)
    shadow.zone = Zone.DECK
    other.zone = Zone.DECK

    player.give("TOY_916").play()

    assert shadow in player.hand
    assert shadow.data.spell_school == SpellSchool.SHADOW
    copies = [card for card in player.hand if card.id == shadow.id]
    assert len(copies) == 2

    temporary = next(card for card in copies if card is not shadow)
    game.end_turn()

    assert shadow in player.hand
    assert temporary.zone == Zone.REMOVEDFROMGAME
