from utils import *
from hearthstone.enums import CardClass, Race, Rarity, Zone


def test_mystery_egg_miniaturizes_and_copies_discounted_beast_from_deck():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    beast = player.card("CS2_201")
    beast.zone = Zone.DECK

    egg = player.give("TOY_351").play()

    assert any(card.id == "TOY_351t" for card in player.hand)

    egg.destroy()

    copied = [card for card in player.hand if card.id == "CS2_201"][0]
    assert copied is not beast
    assert copied.cost == max(0, copied.data.cost - 3)


def test_wilderness_pack_adds_five_temporary_beasts():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("MIS_104").play()

    generated = list(player.hand)
    assert len(generated) == 5
    assert all(Race.BEAST in card.data.races for card in generated)

    game.end_turn()

    assert all(card.zone == Zone.REMOVEDFROMGAME for card in generated)


def test_fetch_draws_minion_then_spell_if_minion_is_beast():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    beast = player.card("CS2_201")
    spell = player.card("CS2_029")
    beast.zone = Zone.DECK
    spell.zone = Zone.DECK

    player.give("TOY_352").play()

    assert beast in player.hand
    assert spell in player.hand


def test_patchwork_pals_adds_discounted_animal_companions():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_353").play()

    companions = {card.id: card for card in player.hand}
    assert {"NEW1_032", "NEW1_033", "NEW1_034"} <= set(companions)
    assert all(
        companions[card_id].cost == companions[card_id].data.cost - 1
        for card_id in ("NEW1_032", "NEW1_033", "NEW1_034")
    )


def test_rc_rampage_buffs_hounds_that_fit_for_each_overflow():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    for _ in range(5):
        player.summon(WISP)

    player.give("TOY_354").play()

    hounds = [minion for minion in player.field if minion.id == "TOY_358t"]
    assert len(hounds) == 2
    assert all(hound.atk == 5 for hound in hounds)
    assert all(hound.max_health == 5 for hound in hounds)


def test_toyrannosaurus_deathrattle_hits_random_enemy():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    dino = player.give("TOY_356").play()

    dino.destroy()

    assert player.opponent.hero.health == 23


def test_remote_control_summons_hound_after_hero_attacks():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_358").play()
    player.hero.attack(player.opponent.hero)

    assert any(minion.id == "TOY_358t" for minion in player.field)


def test_jungle_gym_repeats_for_each_friendly_beast():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.summon("CS2_201")
    player.summon("TOY_358t")
    gym = player.give("TOY_359").play()

    gym.use()

    assert player.opponent.hero.health == 27


def test_painted_canvasaur_gives_other_friendly_beast_bonus_effect():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    other = player.summon("CS2_201")

    canvasaur = player.give("TOY_350").play()

    assert other.buffs
    assert not canvasaur.buffs


def test_bargain_bin_draws_other_two_card_types_after_opponent_play():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    opponent = player.opponent
    player.max_mana = 10
    player.used_mana = 0
    spell = player.card("CS2_029")
    weapon = player.card("CS2_091")
    spell.zone = Zone.DECK
    weapon.zone = Zone.DECK

    player.give("MIS_105").play()
    game.end_turn()
    opponent.max_mana = 10
    opponent.used_mana = 0
    opponent.give(WISP).play()

    assert spell in player.hand
    assert weapon in player.hand
    assert not player.secrets


def test_product_9_recasts_friendly_secrets_triggered_this_game():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    opponent = player.opponent
    player.max_mana = 10
    player.used_mana = 0

    player.give("MIS_105").play()
    game.end_turn()
    opponent.max_mana = 10
    opponent.used_mana = 0
    opponent.give(WISP).play()

    assert not player.secrets

    game.end_turn()
    player.max_mana = 10
    player.used_mana = 0

    player.give("MIS_914").play()

    assert player.secrets
    assert player.secrets[0].id == "MIS_105"


def test_hemet_gets_discounted_legendary_beast_after_friendly_beast_dies():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.summon("TOY_355")
    beast = player.summon("TOY_358t")

    beast.destroy()

    assert len(player.hand) == 1
    reward = player.hand[0]
    assert Race.BEAST in reward.data.races
    assert reward.data.rarity == Rarity.LEGENDARY
    assert reward.cost == max(0, reward.data.cost - 2)


def test_king_plush_shuffles_all_lower_attack_minions_into_owners_decks():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.HUNTER)
    player = game.current_player
    opponent = player.opponent
    player.max_mana = 10
    player.used_mana = 0
    friendly_low = player.summon(WISP)
    friendly_high = player.summon("CS2_201")
    enemy_low = opponent.summon(WISP)

    plush = player.give("TOY_357").play()

    assert plush in player.field
    assert friendly_high in player.field
    assert friendly_low in player.deck
    assert enemy_low in opponent.deck
