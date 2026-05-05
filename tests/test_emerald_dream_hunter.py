from utils import *
from hearthstone.enums import CardClass, CardType, Race, Zone


def _set_mana(player):
    player.max_mana = 10
    player.used_mana = 0


def test_verdant_dreamsaber_attacks_twice_when_discounted_to_three_or_less():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    enemies = [player.opponent.summon(WISP), player.opponent.summon(WISP)]
    dreamsaber = player.give("EDR_014")
    dreamsaber._cost = -2

    dreamsaber.play()

    assert dreamsaber in player.field
    assert all(enemy.zone == Zone.GRAVEYARD for enemy in enemies)


def test_exotic_houndmaster_draws_beast_and_imbues_wolf_hero_power():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    player.card(WISP).zone = Zone.DECK
    player.card("EDR_227").zone = Zone.DECK

    player.give("EDR_226").play()

    beast = player.hand.filter(id="EDR_227")[0]
    assert player.hero.power.id == "EDR_850p"

    player.used_mana = 0
    player.hero.power.use()

    assert beast.atk == beast.data.atk + 1
    assert beast.cost == max(0, beast.data.cost - 3)


def test_umbraclaw_has_rush_and_deathrattle_imbues_hero_power():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    umbraclaw = player.summon("EDR_227")

    assert umbraclaw.rush

    umbraclaw.destroy()

    assert player.hero.power.id == "EDR_850p"


def test_amphibians_spirit_grants_recursive_deathrattle_buff():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)
    next_target = player.summon(WISP)

    player.give("EDR_261").play(target=target)

    assert target.atk == target.data.atk + 2
    assert target.max_health == target.data.health + 2
    assert target.has_deathrattle

    target.destroy()

    assert next_target.atk == next_target.data.atk + 2
    assert next_target.max_health == next_target.data.health + 2
    assert next_target.has_deathrattle


def test_spirit_bond_summons_rush_wolf_when_target_dies():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon(WISP)

    player.give("EDR_262").play(target=target)

    assert target.zone == Zone.GRAVEYARD
    wolf = player.field[-1]
    assert wolf.id == "EDR_850pe"
    assert wolf.atk == 3
    assert wolf.max_health == 2
    assert wolf.rush


def test_grace_of_the_greatwolf_choice_damage_or_two_wolves():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_263").play()
    damage_choice = player.choice.cards[0]
    player.choice.choose(damage_choice)

    assert player.opponent.hero.damage == 4

    player.used_mana = 0
    player.give("EDR_263").play()
    summon_choice = player.choice.cards[1]
    player.choice.choose(summon_choice)

    wolves = player.field.filter(id="EDR_850pe")
    assert len(wolves) == 2
    assert all(wolf.rush for wolf in wolves)


def test_shepherds_crook_summons_dormant_sheep_after_hero_attacks():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon("CS2_182")

    player.give("EDR_416").play()
    player.hero.attack(target)

    sheep = player.field[-1]
    assert sheep.id == "EDR_416t"
    assert sheep.atk == 3
    assert sheep.max_health == 3
    assert sheep.dormant
    assert sheep.dormant_turns == 2


def test_goldrinn_has_rush_and_friendly_beasts_deal_double_attack_damage():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    goldrinn = player.summon("EDR_480")
    beast = player.summon("EDR_850pe")
    target = player.opponent.summon("EX1_399")

    assert goldrinn.rush

    beast.attack(target)

    assert target.damage == beast.atk * 2


def test_mythical_runebear_summons_copy_if_attack_is_four_or_more():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    bear = player.give("EDR_481")
    bear.buff(bear, "EDR_853e")

    bear.play()

    bears = player.field.filter(id="EDR_481")
    assert len(bears) == 2
    assert all(bear.taunt for bear in bears)


def test_broll_summons_random_animal_companion_after_spell():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    player.summon("EDR_853")

    player.give("FIR_909").play()

    companions = [card for card in player.field if card.id in ("NEW1_032", "NEW1_033", "NEW1_034")]
    assert len(companions) == 1
    assert companions[0].race == Race.BEAST


def test_bursting_shot_deals_two_to_three_random_enemies():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)

    player.give("FIR_909").play()

    assert player.opponent.hero.damage == 6


def test_magma_hound_splits_attack_damage_after_attacking_and_surviving():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    hound = player.summon("FIR_953")
    target = player.opponent.summon(WISP)

    assert hound.rush

    hound.attack(target)

    assert target.zone == Zone.GRAVEYARD
    assert player.opponent.hero.damage == hound.atk


def test_tending_dragonkin_copies_lowest_cost_beast_in_hand():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    _set_mana(player)
    lower = player.give("EDR_227")
    player.give("EDR_480")

    player.give("FIR_960").play()

    copied = player.hand.filter(id=lower.id)
    assert len(copied) == 2
    assert all(card.race == Race.BEAST for card in copied)
