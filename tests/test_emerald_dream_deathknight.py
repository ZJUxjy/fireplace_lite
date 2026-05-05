from utils import *
from hearthstone.enums import CardClass, CardType, Race, Zone


def test_hideous_husk_summons_two_leeches_and_improves_their_steal():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.hero.damage = 6

    player.give("EDR_810").play()

    leeches = player.field.filter(id="EDR_810t")
    assert len(leeches) == 2

    game.end_turn()

    assert player.opponent.hero.damage == 4
    assert player.hero.damage == 2


def test_rite_of_atrocity_discovers_undead_and_spends_corpses_for_dark_gift():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.corpses = 2

    player.give("EDR_811").play()

    assert player.choice
    assert all(Race.UNDEAD in card.races for card in player.choice.cards)
    choice = player.choice.cards[0]
    player.choice.choose(choice)

    assert choice in player.hand
    assert getattr(choice, "_dark_gift", False)
    assert player.corpses == 0


def test_grotesque_runeblade_uses_last_played_runes_for_attack_and_durability():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("EDR_811").play()
    player.choice.choose(player.choice.cards[0])
    player.used_mana = 0
    weapon = player.give("EDR_812").play()

    assert weapon.atk == 3
    assert weapon.max_durability == 2

    player.give("EDR_814").play(target=player.opponent.hero)
    player.used_mana = 0
    weapon = player.give("EDR_812").play()

    assert weapon.atk == 2
    assert weapon.max_durability == 3


def test_morbid_swarm_summons_ants_or_spends_corpses_to_damage_minion():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("EDR_813").play(choose="EDR_813a")

    assert len(player.field.filter(id="EDR_813at")) == 2

    target = player.opponent.summon("CS2_200")
    player.corpses = 2
    player.used_mana = 0
    player.give("EDR_813").play(target=target, choose="EDR_813b")

    assert target.damage == 4
    assert player.corpses == 0


def test_corpse_flower_spends_corpses_to_damage_enemy_summons():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.corpses = 2
    player.summon("EDR_815")

    enemy = player.opponent.summon("CS2_200")

    assert enemy.damage == 3
    assert player.corpses == 0


def test_montrous_mosquito_buffs_other_minions_attack_only():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    mosquito = player.summon("EDR_816")
    other = player.summon(WISP)

    game.end_turn()

    assert mosquito.atk == mosquito.data.atk
    assert other.atk == other.data.atk + 1
    assert other.health == other.data.health


def test_sanguine_infestation_draws_two_and_summons_two_leeches():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    for card_id in (WISP, "CS2_231"):
        player.card(card_id).zone = Zone.DECK

    player.give("EDR_817").play()

    assert len(player.hand) == 2
    assert len(player.field.filter(id="EDR_810t")) == 2


def test_nythendra_splits_into_beetles_and_reforms_next_turn():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    nythendra = player.summon("EDR_818")

    nythendra.destroy()

    assert len(player.field.filter(id="EDR_818t")) == 7
    player.field[0].destroy()
    player.field[0].destroy()

    game.end_turn()
    game.end_turn()

    assert len(player.field.filter(id="EDR_818t")) == 0
    assert len(player.field.filter(id="EDR_818")) == 1


def test_ursoc_attacks_all_other_minions_and_resurrects_kills():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    friendly = player.summon(WISP)
    enemy = player.opponent.summon("CS2_189")

    ursoc = player.give("EDR_819").play()

    assert friendly.zone == Zone.GRAVEYARD
    assert enemy.zone == Zone.GRAVEYARD

    ursoc.destroy()

    assert len(player.field.filter(id=WISP)) == 1
    assert len(player.field.filter(id="CS2_189")) == 1


def test_cremate_discovers_discounted_minion_with_dark_gift():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("FIR_900").play()

    assert player.choice
    assert all(card.type == CardType.MINION for card in player.choice.cards)
    choice = player.choice.cards[0]
    original_cost = choice.data.cost
    player.choice.choose(choice)

    assert choice in player.hand
    assert getattr(choice, "_dark_gift", False)
    assert choice.cost == max(0, original_cost - 2)


def test_frostburn_matriarch_summons_dragons_if_holding_dark_gift_minion():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    gifted = player.give(WISP)
    gifted._dark_gift = True

    player.give("FIR_901").play()

    dragons = player.field.filter(id="FIR_901t")
    assert len(dragons) == 2
    assert all(dragon.taunt for dragon in dragons)


def test_volcoross_spends_largest_affordable_corpses_for_stats():
    game = prepare_empty_game(CardClass.DEATHKNIGHT, CardClass.DEATHKNIGHT)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.corpses = 20

    volcoross = player.give("FIR_951").play()

    assert volcoross.atk == 25
    assert volcoross.health == 25
    assert player.corpses == 0
