from utils import *
from hearthstone.enums import CardClass, CardType, GameTag, Race, Zone


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def _add_to_deck(player, *card_ids):
    return [player.card(card_id, zone=Zone.DECK) for card_id in card_ids]


def test_flamemurgill_kindred_gives_other_minions_rush():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    other = player.summon(WISP)

    player.give("TLC_428").play()
    game.end_turn()
    game.end_turn()
    player.give("DINO_404").play()

    assert other.rush


def test_hatch_the_egg_buffs_minions_at_next_own_turn_end():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)

    player.give("DINO_405").play()
    minion = player.summon(WISP)
    game.end_turn()
    assert minion.atk == 1
    game.end_turn()
    game.end_turn()

    assert (minion.atk, minion.max_health) == (3, 3)


def test_heroes_welcome_discovers_summons_legendary_as_ten_ten():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)

    player.give("DINO_424").play()
    picked = player.choice.cards[0]
    player.choice.choose(picked)

    assert picked in player.field
    assert picked.data.rarity.name == "LEGENDARY"
    assert (picked.atk, picked.max_health) == (10, 10)


def test_gillassic_jaws_deathrattle_summons_three_bonus_murlocs():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    jaws = player.summon("TLC_240")

    jaws.destroy()

    murlocs = [minion for minion in player.field if Race.MURLOC in minion.races]
    assert len(murlocs) == 3
    assert all((murloc.atk, murloc.max_health) == (2, 1) for murloc in murlocs)
    assert all(
        murloc.rush or murloc.taunt or murloc.divine_shield or murloc.windfury
        for murloc in murlocs
    )


def test_lynessa_gives_repeatable_spellcraft_while_alive():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    lynessa = player.give("TLC_241").play()
    target = player.summon(WISP)

    assert any(card.id == "TLC_241t" for card in player.hand)
    spell = next(card for card in player.hand if card.id == "TLC_241t")
    spell.play(target=target)

    assert any(card.id == "TLC_241t" for card in player.hand)
    assert (target.atk, target.max_health) == (3, 3)
    assert target.divine_shield

    lynessa.destroy()
    spell = next(card for card in player.hand if card.id == "TLC_241t")
    spell.play(target=target)
    assert spell.zone == Zone.GRAVEYARD


def test_questing_sir_finley_rewards_murloc_summon_aura():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)

    quest = player.give("TLC_426").play()
    for _ in range(6):
        player.summon("TLC_240t")

    assert quest.progress == 0
    buffed = player.summon("TLC_240t")
    assert (buffed.atk, buffed.max_health) == (3, 2)


def test_murk_strider_discounts_next_murloc_and_kindred_gives_divine_shield():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)

    player.give("DINO_404").play()
    game.end_turn()
    game.end_turn()
    next_murloc = player.give("TLC_240t")
    player.give("TLC_428").play()

    assert next_murloc.cost == 1
    next_murloc.play()
    assert next_murloc.divine_shield


def test_holy_grotto_recasts_random_holy_spell_on_itself_at_turn_end():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    grotto = player.summon("TLC_430")

    player.give("TLC_241t").play(target=grotto)
    game.end_turn()

    assert (grotto.atk, grotto.max_health) == (6, 9)


def test_purplefin_callow_casts_small_deck_spell_on_itself():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    _add_to_deck(player, "TLC_241t")

    callow = player.give("TLC_438").play()

    assert (callow.atk, callow.max_health) == (3, 4)
    assert callow.divine_shield


def test_muster_to_formation_buffs_same_race_friendly_minions():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    target = player.summon("TLC_240t")
    same = player.summon("DINO_404")
    different = player.summon(WISP)

    player.give("TLC_441").play(target=target)

    assert (target.atk, target.max_health) == (3, 3)
    assert (same.atk, same.max_health) == (4, 4)
    assert (different.atk, different.max_health) == (1, 1)


def test_submerged_map_followup_choice_if_discovered_murloc_is_played():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_442").play()
    first = player.choice.cards[0]
    remaining = [card for card in player.choice.cards if card is not first]
    expected = {card.id for card in remaining}
    player.choice.choose(first)
    _set_mana(player)
    if first.requires_target():
        first.play(target=first.play_targets[0])
    else:
        first.play()
    for _ in range(3):
        if player.choice and {card.id for card in player.choice.cards} != expected:
            player.choice.choose(player.choice.cards[0])

    assert player.choice
    assert {card.id for card in player.choice.cards} == expected
    player.choice.choose(player.choice.cards[0])
    assert not player.choice


def test_story_of_galvadon_grants_three_adapt_bonuses():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)

    player.give("TLC_444").play(target=target)

    bonuses = [
        target.atk > 1,
        target.max_health > 1,
        target.taunt,
        target.divine_shield,
        target.windfury,
        target.stealthed,
    ]
    assert sum(bool(bonus) for bonus in bonuses) >= 3


def test_spikeridged_steed_buffs_and_deathrattle_summons_four_cost_minion():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)

    player.give("TLC_477").play(target=target)

    assert (target.atk, target.max_health) == (5, 5)
    assert target.has_deathrattle

    target.destroy()
    assert any(minion.cost == 4 for minion in player.field)
