from utils import *
from hearthstone.enums import CardClass, CardType, GameTag, Race, Zone


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def _add_to_deck(player, *card_ids):
    return [player.card(card_id, zone=Zone.DECK) for card_id in card_ids]


def _all_races(card):
    races = set(card.races)
    races.update(getattr(card.data, "races", []))
    return races


def test_erupting_fire_damages_and_buffs_elementals():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    elemental = player.summon("TLC_225")
    target = player.opponent.summon("CS2_232")

    player.give("DINO_406").play(target=target)

    assert target.damage == 4
    assert (elemental.atk, elemental.max_health) == (2, 3)


def test_ancient_turtle_totem_gives_multitype_minion_at_turn_end():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    totem = player.summon("DINO_412")

    game.end_turn()

    gained = [card for card in player.hand if card.type == CardType.MINION]
    assert gained
    assert any(len(_all_races(card)) > 1 for card in gained)


def test_icespine_sivara_kindred_hits_two_enemy_minions_and_freezes():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)

    player.give("DINO_413").play()
    game.end_turn()
    game.end_turn()
    enemy1 = player.opponent.summon("CS2_120")
    enemy2 = player.opponent.summon("CS2_232")
    player.give("DINO_413").play()

    assert enemy1.damage == 2
    assert enemy2.damage == 2
    assert enemy1.frozen and enemy2.frozen


def test_blazing_inferno_deals_damage_and_summons_that_many_accumulations():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon("CS2_232")

    player.give("TLC_221").play(target=target)

    assert target.damage == 3
    assert len([minion for minion in player.field if minion.id == "TLC_249"]) == 3


def test_blazing_inferno_summons_actual_damage_amount():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    player.summon(KOBOLD_GEOMANCER)
    target = player.opponent.summon("CS2_232")

    player.give("TLC_221").play(target=target)

    assert target.damage == 4
    assert len([minion for minion in player.field if minion.id == "TLC_249"]) == 4


def test_firebird_flight_draws_two_different_races_and_buffs_them():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    _add_to_deck(player, "TLC_225", "GVG_085")

    player.give("TLC_222").play()

    drawn = [card for card in player.hand if card.id in ("TLC_225", "GVG_085")]
    assert len(drawn) == 2
    assert all((card.atk, card.max_health) == (3, 4) for card in drawn)


def test_volcanic_thrasher_draws_fire_spell_and_kindred_gives_spell_damage():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_225").play()
    game.end_turn()
    game.end_turn()
    _add_to_deck(player, "DINO_406")
    player.give("TLC_223").play()

    drawn = next(card for card in player.hand if card.id == "DINO_406")
    assert drawn.buffs and drawn.buffs[-1].spellpower == 2


def test_mechanical_molten_gains_stats_when_fire_spell_played():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    molten = player.summon("TLC_224")

    player.give("DINO_406").play(target=player.opponent.hero)

    assert (molten.atk, molten.max_health) == (6, 9)


def test_emberscarred_murloc_deathrattle_summons_blazing_accumulation():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    murloc = player.summon("TLC_225")

    murloc.destroy()

    assert any(minion.id == "TLC_249" for minion in player.field)


def test_lava_surge_hits_lowest_health_enemy_three_times():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    low = player.opponent.summon(WISP)
    high = player.opponent.summon("CS2_232")

    player.give("TLC_227").play()

    assert low.zone == Zone.GRAVEYARD
    assert high.damage == 4


def test_brrma_increases_blazing_accumulation_deathrattle_damage():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    bramma = player.summon("TLC_228")
    target = player.opponent.hero
    accretion = player.summon("TLC_249")

    accretion.destroy()

    assert target.damage == 3
    assert bramma in player.field


def test_blazing_accumulation_deathrattle_splits_damage_point_by_point():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    samples = []

    def sample(options, count):
        samples.append((list(options), count))
        return list(options)[:count]

    game.random.sample = sample
    accretion = player.summon("TLC_249")

    accretion.destroy()

    assert len(samples) == 2
    assert all(count == 1 for _, count in samples)
    assert player.opponent.hero.damage == 2


def test_brrma_increases_elemental_battlecry_damage():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    player.summon("TLC_228")
    target = player.opponent.summon("CS2_232")

    player.give("DINO_413").play()

    assert target.damage == 3


def test_spirits_of_the_mountain_rewards_six_different_minion_types():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_229").play()
    for card_id in ("TLC_225", "DINO_413", "GVG_085", "CS2_231", "DS1_055"):
        _set_mana(player)
        player.give(card_id).play()

    assert any(card.id == "TLC_229t14" for card in player.hand)


def test_ashamane_evolves_twice_and_evolves_future_minions():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)
    ashamane = player.give("TLC_229t14")

    ashamane.play()
    evolved_ashamane = player.field[0]

    assert ashamane.zone == Zone.SETASIDE
    assert evolved_ashamane.id != "TLC_229t14"
    assert evolved_ashamane.cost == 7

    _set_mana(player)
    wisp = player.give(WISP)
    wisp.play()

    assert wisp.zone == Zone.SETASIDE
    assert player.field[-1].id != WISP
    assert player.field[-1].cost == 2


def test_hiking_trail_discovers_unused_minion_type_and_followup():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_225").play()
    player.give("TLC_464").play()
    first = player.choice.cards[0]
    remaining = [card.id for card in player.choice.cards if card is not first]
    player.choice.choose(first)
    _set_mana(player)
    expected = set(remaining)
    first.play()
    for _ in range(3):
        if player.choice and {card.id for card in player.choice.cards} != expected:
            player.choice.choose(player.choice.cards[0])

    assert Race.ELEMENTAL not in _all_races(first)
    assert player.choice
    assert {card.id for card in player.choice.cards} == expected


def test_moltenclaw_summons_two_and_kindred_triggers_their_deathrattles():
    game = prepare_empty_game(CardClass.SHAMAN, CardClass.SHAMAN)
    player = game.current_player
    _set_mana(player)

    player.summon("TLC_249")
    player.give("TLC_225").play()
    game.end_turn()
    game.end_turn()
    player.give("TLC_482").play()

    assert len([minion for minion in player.field if minion.id == "TLC_249"]) == 3
    assert player.opponent.hero.damage == 6
