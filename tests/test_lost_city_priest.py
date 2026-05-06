from utils import *
from hearthstone.enums import CardClass, CardType, GameTag, Race, Zone


def _set_mana(player, amount=10):
    player.max_mana = amount
    player.used_mana = 0


def _damage(character, amount):
    character.damage = amount


def test_life_ritual_discovers_three_cost_minion_and_summons_two_three_copy():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)

    player.give("DINO_426").play()
    picked = player.choice.cards[0]
    player.choice.choose(picked)

    assert picked in player.field
    assert picked.cost == 3
    assert (picked.atk, picked.max_health) == (2, 3)


def test_eel_mask_sets_stats_lifesteal_and_forces_enemy_attack():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)
    enemy = player.opponent.summon("CS2_231")

    player.give("DINO_428").play(target=target)

    assert (target.atk, target.max_health) == (8, 10)
    assert target.lifesteal
    assert target.damage == enemy.atk


def test_thunderbringer_deathrattle_summons_big_taunt():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    thunder = player.summon("DINO_431")

    thunder.destroy()

    summoned = [minion for minion in player.field if minion is not thunder]
    assert summoned
    assert all(minion.cost >= 5 and minion.taunt for minion in summoned)


def test_archaios_sets_attacker_health_to_own_health():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    archaios = player.summon("TLC_811")
    attacker = player.summon("CS2_171")
    enemy = player.opponent.summon(WISP)
    _damage(archaios, 2)

    attacker.attack(enemy)

    assert attacker.health == archaios.health


def test_twilight_mender_deathrattle_gives_holy_and_shadow_spells():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    mender = player.summon("TLC_814")

    mender.destroy()

    schools = {
        card.tags.get(GameTag.SPELL_SCHOOL)
        or getattr(getattr(card, "data", None), "spell_school", None)
        for card in player.hand
    }
    assert 5 in schools
    assert 6 in schools


def test_gravedawn_voidbulb_kindred_repeats_taunt_summon():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)

    player.give("TLC_818").play()
    game.end_turn()
    game.end_turn()
    player.give("TLC_815").play()

    summoned = [minion for minion in player.field if minion.cost == 4]
    assert len(summoned) == 2
    assert all(minion.taunt for minion in summoned)


def test_gravedawn_sunbloom_draws_two_and_kindred_costs_two_less():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    player.deck = [player.card(WISP, zone=Zone.DECK), player.card("CS2_231", zone=Zone.DECK)]

    player.give("TLC_813").play(target=player.summon(WISP))
    game.end_turn()
    game.end_turn()
    sunbloom = player.give("TLC_816")

    assert sunbloom.cost == 2
    sunbloom.play()
    assert len(player.hand) >= 2


def test_seek_guidance_rewards_holy_shadow_and_combines_pieces():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)

    player.give("TLC_817").play()
    for _ in range(4):
        _set_mana(player)
        player.give("TLC_813").play(target=target)
    assert any(card.id == "TLC_817t3" for card in player.hand)

    for _ in range(4):
        _set_mana(player)
        player.give("TLC_815").play()

    assert any(card.id == "TLC_817t5" for card in player.hand)
    assert not any(card.id in ("TLC_817t3", "TLC_817t4") for card in player.hand)


def test_reincarnation_resurrects_one_two_three_cost_minions_with_reborn():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    for card_id in ("CS2_171", "CS2_172", "TLC_811"):
        minion = player.summon(card_id)
        minion.destroy()

    player.give("TLC_818").play()

    costs = {minion.cost for minion in player.field}
    assert {1, 2, 3}.issubset(costs)
    assert all(minion.reborn for minion in player.field)


def test_cicadian_charmer_costs_one_after_holy_and_shadow_this_turn():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    target = player.summon(WISP)

    player.give("TLC_813").play(target=target)
    _set_mana(player)
    player.give("TLC_815").play()
    charmer = player.give("TLC_819")

    assert charmer.cost == 1


def test_woodland_ecologist_gives_pure_vine_that_buffs_friend_or_debuffs_enemy():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    ecologist = player.summon("TLC_820")
    friend = player.summon(WISP)
    enemy = player.opponent.summon("CS2_120")

    ecologist.destroy()
    vine = next(card for card in player.hand if card.id == "TLC_813")
    vine.play(target=friend)
    assert friend.max_health == 3

    vine = player.give("TLC_813")
    vine.play(target=enemy)
    assert enemy.max_health == 1


def test_wilted_shadow_attacks_enemy_when_you_heal_it():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    shadow = player.summon("TLC_821")
    enemy = player.opponent.hero
    _damage(enemy, 2)

    game.queue_actions(shadow, [Heal(enemy, 2)])

    assert enemy.damage == shadow.atk


def test_amara_story_sets_hero_health_to_forty():
    game = prepare_empty_game(CardClass.PRIEST, CardClass.PRIEST)
    player = game.current_player
    _set_mana(player)
    player.hero.damage = 10

    player.give("TLC_835").play()

    assert player.hero.max_health == 40
    assert player.hero.health == 40
