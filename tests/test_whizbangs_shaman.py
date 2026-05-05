from utils import *
from hearthstone.enums import CardClass, CardType, Race, Rarity, Zone

from fireplace.cards.utils import Buff


def test_rocket_hopper_has_rush_and_overloads_four():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    hopper = player.give("MIS_306").play()

    assert hopper.rush
    assert player.overloaded == 4


def test_murloc_growfin_gigantifies_and_summons_matching_rush_tinyfin():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    growfin = player.give("MIS_307")
    game.cheat_action(growfin, [Buff(growfin, "TOY_877e")])

    growfin.play()

    tinyfin = player.field[-1]
    assert tinyfin.id == "MIS_307t"
    assert tinyfin.rush
    assert tinyfin.atk == growfin.atk
    assert tinyfin.max_health == growfin.max_health
    assert any(card.id == "MIS_307t1" for card in player.hand)


def test_wave_of_nostalgia_transforms_all_minions_into_legendary_minions():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    friendly = player.summon(WISP)
    enemy = player.opponent.summon("CS2_182")

    player.give("MIS_701").play()

    transformed = list(player.field) + list(player.opponent.field)
    assert {card.id for card in transformed}.isdisjoint({friendly.id, enemy.id})
    assert all(card.rarity == Rarity.LEGENDARY for card in transformed)


def test_incredible_value_discovers_four_cost_minion_and_sets_it_to_seven_seven():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_046").play()

    assert player.choice is not None
    assert all(card.type == CardType.MINION and card.cost == 4 for card in player.choice.cards)
    choice = player.choice.cards[0]
    player.choice.choose(choice)

    chosen = player.hand[-1]
    assert chosen.id == choice.id
    assert chosen.atk == 7
    assert chosen.max_health == 7


def test_baking_soda_volcano_has_lifesteal_splits_ten_damage_and_overloads():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.hero.damage = 10
    minions = [player.summon("CS2_200"), player.opponent.summon("CS2_200")]

    player.give("TOY_500").play()

    assert any(minion.damage or minion.zone == Zone.GRAVEYARD for minion in minions)
    assert player.hero.damage == 0
    assert player.overloaded == 1


def test_shudderblock_miniaturizes_and_next_battlecry_triggers_three_times():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_501").play()
    assert any(card.id == "TOY_501t" for card in player.hand)

    player.give("EX1_014").play()

    assert len(player.opponent.hand.filter(id="EX1_014t")) == 6

    player.used_mana = 0
    player.give("EX1_014").play()

    assert len(player.opponent.hand.filter(id="EX1_014t")) == 8


def test_shudderblock_prevents_its_battlecry_repeats_from_damaging_enemy_hero():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_501").play()
    player.give("CS2_189").play(target=player.opponent.hero)

    assert player.opponent.hero.damage == 0


def test_shining_sentinel_has_keywords_and_summons_a_copy():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    sentinel = player.give("TOY_503").play()

    sentinels = player.field.filter(id="TOY_503")
    assert sentinel.taunt
    assert sentinel.data.tags.get(GameTag.ELUSIVE)
    assert len(sentinels) == 2


def test_hagatha_draws_big_spells_as_slimes_that_cast_them():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    for card_id in ("CS2_032", "CS2_028"):
        player.card(card_id).zone = Zone.DECK

    player.give("TOY_504").play()

    slimes = player.hand.filter(id="TOY_504t")
    assert len(slimes) == 2
    assert {slime._hagatha_spell_id for slime in slimes} == {"CS2_032", "CS2_028"}

    enemy = player.opponent.summon("CS2_200")
    flamestrike_slime = next(slime for slime in slimes if slime._hagatha_spell_id == "CS2_032")
    flamestrike_slime.play()

    assert enemy.damage == 4


def test_once_upon_a_time_summons_four_three_cost_tribes():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_506").play()

    assert len(player.field) == 4
    assert all(minion.cost == 3 for minion in player.field)
    assert {Race.BEAST, Race.DRAGON, Race.ELEMENTAL, Race.MURLOC}.issubset(
        {race for minion in player.field for race in minion.data.races}
    )


def test_fairy_tale_forest_draws_battlecry_minion_and_discounts_it():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    battlecry = player.card("EX1_014")
    vanilla = player.card(WISP)
    battlecry.zone = Zone.DECK
    vanilla.zone = Zone.DECK

    forest = player.give("TOY_507").play()
    forest.use()

    assert battlecry in player.hand
    assert battlecry.cost == battlecry.data.cost - 1
    assert vanilla in player.deck
    assert forest.durability == forest.max_durability - 1


def test_pop_up_book_deals_two_and_summons_two_taunt_frogs():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.opponent.summon("CS2_182")

    player.give("TOY_508").play(target=target)

    frogs = player.field.filter(id="hexfrog")
    assert target.damage == 2
    assert len(frogs) == 2
    assert all(frog.taunt and frog.atk == 0 and frog.max_health == 1 for frog in frogs)


def test_sand_art_elemental_miniaturizes_and_temporarily_buffs_hero():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_513").play()

    assert any(card.id == "TOY_513t" for card in player.hand)
    assert player.hero.atk == 1
    assert player.hero.windfury

    game.end_turn()

    assert player.hero.atk == 0
    assert not player.hero.windfury


def test_wish_upon_a_star_buffs_minions_in_hand_deck_and_field():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    hand = player.give(WISP)
    deck = player.card("CS2_182")
    deck.zone = Zone.DECK
    field = player.summon("CS2_231")

    player.give("TOY_877").play()

    for minion in (hand, deck, field):
        assert minion.atk == minion.data.atk + 2
        assert minion.max_health == minion.data.health + 3
