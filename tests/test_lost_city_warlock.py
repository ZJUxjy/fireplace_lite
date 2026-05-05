from utils import *
from hearthstone.enums import CardClass, CardType, GameTag, Race, SpellSchool, Zone


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def _add_to_deck(player, *card_ids):
    return [player.card(card_id, zone=Zone.DECK) for card_id in card_ids]


def _temporary(card):
    card._tlc_temporary = True
    return card


def _all_races(card):
    races = set(card.races)
    races.update(getattr(card.data, "races", []))
    return races


def _spell_school(card):
    return card.tags.get(GameTag.SPELL_SCHOOL) or getattr(card.data, "spell_school", None)


def test_possessed_animancer_summons_beast_from_deck_with_lifesteal():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _add_to_deck(player, "TLC_469")
    animancer = player.summon("DINO_131")

    animancer.destroy()

    summoned = next(minion for minion in player.field if minion.id == "TLC_469")
    assert summoned.lifesteal
    assert not any(card.id == "TLC_469" for card in player.deck)


def test_asphyxiodon_hits_enemy_minion_at_turn_end():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    player.summon("DINO_132")
    target = player.opponent.summon("CS2_232")

    game.end_turn()

    assert target.damage == 5
    assert player.opponent.hero.damage == 0


def test_bat_mask_sets_friendly_minion_to_one_one_and_fills_board():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    target = player.summon("TLC_469")
    target.taunt = True

    player.give("DINO_402").play(target=target)

    assert len(player.field) == 7
    assert all(minion.id == "TLC_469" for minion in player.field)
    assert all((minion.atk, minion.max_health) == (1, 1) for minion in player.field)
    assert all(minion.taunt for minion in player.field)


def test_escape_the_underfel_rewards_after_six_temporary_cards():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)

    quest = player.give("TLC_446").play()
    for _ in range(6):
        _set_mana(player)
        _temporary(player.give(WISP)).play()

    assert quest.zone == Zone.GRAVEYARD
    assert any(card.id == "TLC_446t" for card in player.hand)


def test_underfel_rift_opens_object_that_discards_and_summons_felbeasts():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    discarded = player.give(WISP)

    player.give("TLC_446t").play()
    rift = next(minion for minion in player.field if minion.id == "TLC_446t1")
    attacker = player.opponent.summon(WISP)
    enemy_spell = player.opponent.give("TLC_447")

    assert not rift.attackable
    assert rift not in attacker.attack_targets
    assert rift not in enemy_spell.play_targets

    rift.use()
    player.choice.choose(discarded)

    assert discarded.zone == Zone.REMOVEDFROMGAME
    felbeasts = [minion for minion in player.field if Race.BEAST in minion.races]
    assert len(felbeasts) == 2
    assert all(Race.DEMON in _all_races(minion) for minion in felbeasts)


def test_caustic_fumes_destroy_enemy_and_kindred_hits_all_minions():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    target = player.opponent.summon("CS2_232")
    friendly = player.summon(WISP)
    enemy = player.opponent.summon("TLC_469")

    player.give("TLC_447").play(target=target)
    game.end_turn()
    game.end_turn()
    player.give("TLC_447").play(target=enemy)

    assert target.zone == Zone.GRAVEYARD
    assert enemy.zone == Zone.GRAVEYARD
    assert friendly.zone == Zone.GRAVEYARD


def test_bloodpetal_biome_discovers_temporary_one_cost_minion_and_discards_it_at_turn_end():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    biome = player.give("TLC_449").play()

    biome.use()
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert chosen in player.hand
    assert chosen.cost == 1
    assert getattr(chosen, "_tlc_temporary", False)
    game.end_turn()
    assert chosen.zone == Zone.REMOVEDFROMGAME


def test_spelunker_discounts_next_temporary_card_only():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    temp = _temporary(player.give("TLC_469"))
    normal = player.give("TLC_469")

    player.give("TLC_450").play()

    assert temp.cost == 1
    assert normal.cost == 3
    temp.play()
    assert not any(buff.id == "TLC_450e" for buff in player.buffs)


def test_cursed_catacombs_discovers_card_from_deck_as_temporary():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    _add_to_deck(player, "TLC_469", "TLC_467")

    player.give("TLC_451").play()
    chosen = player.choice.cards[0]
    player.choice.choose(chosen)

    assert chosen in player.hand
    assert getattr(chosen, "_tlc_temporary", False)
    assert chosen not in player.deck


def test_razidir_discards_own_hand_or_opponents_with_kindred():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    own = player.give(WISP)
    player.opponent.hand.clear()
    enemy = player.opponent.give("CS2_232")

    player.give("TLC_463").play()

    assert own.zone == Zone.REMOVEDFROMGAME
    assert enemy.zone == Zone.HAND

    game.end_turn()
    game.end_turn()
    player.give("TLC_463").play()

    assert enemy.zone == Zone.REMOVEDFROMGAME


def test_story_of_lakkari_runs_for_three_turns():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    player.give(WISP)
    player.give(WISP)
    player.give(WISP)

    story = player.give("TLC_466").play()
    for expected in (1, 2, 3):
        game.end_turn()
        imps = [minion for minion in player.field if minion.id == "TLC_466t"]
        assert len(imps) == min(7, expected * 7)
        assert all((imp.atk, imp.max_health) == (3, 2) for imp in imps)
        game.end_turn()

    assert story.zone == Zone.GRAVEYARD


def test_whispering_stone_gives_fel_spells_that_cost_health():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    _set_mana(player)
    stone = player.summon("TLC_467")

    stone.destroy()

    spells = [card for card in player.hand if card.type == CardType.SPELL]
    assert len(spells) == 2
    assert all(_spell_school(card) == SpellSchool.FEL for card in spells)
    assert all(getattr(card, "_costs_health", False) for card in spells)


def test_tunnel_terror_gives_two_temporary_two_cost_minions():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    terror = player.summon("TLC_469")

    terror.destroy()

    cards = [card for card in player.hand if getattr(card, "_tlc_temporary", False)]
    assert len(cards) == 2
    assert all(card.type == CardType.MINION and card.cost == 2 for card in cards)


def test_deathrot_maw_summons_random_felbeast():
    game = prepare_empty_game(CardClass.WARLOCK, CardClass.WARLOCK)
    player = game.current_player
    maw = player.summon("TLC_479")

    maw.destroy()

    felbeast = next(minion for minion in player.field if minion.id.startswith("TLC_446t"))
    assert Race.DEMON in _all_races(felbeast)
    assert Race.BEAST in _all_races(felbeast)
