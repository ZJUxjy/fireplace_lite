from utils import *
from hearthstone.enums import CardClass, Zone


def _set_mana(player):
    player.max_mana = 10
    player.used_mana = 0


def test_dragonscale_armaments_draws_started_and_generated_spells():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    started = player.card("EDR_252", zone=Zone.DECK)
    generated = player.card("FIR_914", zone=Zone.DECK)
    player.starting_deck.append(started)

    player.give("EDR_251").play()

    assert started in player.hand
    assert generated in player.hand


def test_mark_of_ursol_sets_friendly_to_three_three_and_enemy_to_one_one():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    friendly = player.summon("CS2_182")
    enemy = player.opponent.summon("CS2_182")

    player.give("EDR_252").play(target=friendly)
    player.used_mana = 0
    player.give("EDR_252").play(target=enemy)

    assert (friendly.atk, friendly.max_health, friendly.damage) == (3, 3, 0)
    assert (enemy.atk, enemy.max_health, enemy.damage) == (1, 1, 0)


def test_ursine_maul_draws_after_hero_attacks():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    player.card(WISP, zone=Zone.DECK)
    target = player.opponent.summon("CS2_182")

    player.give("EDR_253").play()
    player.hero.attack(target)

    assert player.hand.filter(id=WISP)


def test_renewing_flames_lifesteal_hits_lowest_health_enemy_twice():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    player.hero.damage = 12
    low = player.opponent.summon(WISP)
    high = player.opponent.summon("CS2_182")

    player.give("EDR_255").play()

    assert low.zone == Zone.GRAVEYARD
    assert high.zone == Zone.GRAVEYARD
    assert player.hero.damage == 2


def test_dreamwarden_draws_generated_deck_card_and_gains_stats():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    generated = player.card(WISP, zone=Zone.DECK)

    dreamwarden = player.give("EDR_256").play()

    assert generated in player.hand
    assert (dreamwarden.atk, dreamwarden.max_health) == (5, 6)


def test_lightmender_choose_one_buffs_itself():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)

    attack_mode = player.give("EDR_257")
    attack_mode.play()
    player.choice.choose(player.choice.cards[0])

    assert attack_mode.atk == attack_mode.data.atk + 3
    assert attack_mode.divine_shield

    player.used_mana = 0
    health_mode = player.give("EDR_257")
    health_mode.play()
    player.choice.choose(player.choice.cards[1])

    assert health_mode.max_health == health_mode.data.health + 3
    assert health_mode.lifesteal


def test_toreth_makes_divine_shields_take_three_hits_to_break():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.summon("EDR_258")
    squire = player.summon("EX1_008")

    for _ in range(2):
        squire.damage = 0
        squire._hit(1)
        assert squire.divine_shield
        assert squire.damage == 0

    squire._hit(1)

    assert not squire.divine_shield
    assert squire.damage == 0


def test_ursol_casts_highest_cost_spell_as_three_turn_aura():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    aegis = player.give("EDR_264")
    player.give("FIR_914")

    player.give("EDR_259").play()

    assert aegis.zone == Zone.SETASIDE
    assert len(player.field) == 1

    for expected in range(2, 5):
        game.end_turn()
        assert len(player.field) == expected
        game.end_turn()

    game.end_turn()

    assert len(player.field) == 4


def test_aegis_of_light_summons_taunt_two_cost_minion_and_imbues():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)

    player.give("EDR_264").play()

    summoned = player.field[0]
    assert summoned.cost == 2
    assert summoned.taunt
    assert player.hero.power.id == "EDR_445p"


def test_goldpetal_drake_battlecry_and_deathrattle_imbue_hero_power():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)

    drake = player.give("EDR_451").play()

    assert player.hero.power.id == "EDR_445p"
    assert player.hero.power._edr_445_amount == 1

    drake.destroy()

    assert player.hero.power._edr_445_amount == 2


def test_paladin_hero_power_shuffles_portals_that_summon_improved_dragons():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    player.give("EDR_264").play()
    player.give("EDR_451").play()
    player.used_mana = 0

    player.hero.power.use()

    portals = player.deck.filter(id="EDR_445pt3")
    assert len(portals) == 2
    assert all(portal._edr_445_amount == 2 for portal in portals)

    portals[0].draw()

    assert portals[0].zone == Zone.GRAVEYARD
    assert any(minion.race == Race.DRAGON and minion.cost == 2 for minion in player.field)


def test_smoldering_strength_upgrades_each_turn_then_discards():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    target = player.summon(WISP)
    strength = player.give("FIR_914")

    game.end_turn()
    game.end_turn()
    _set_mana(player)
    strength.play(target=target)

    assert (target.atk, target.max_health) == (3, 3)

    later = player.give("FIR_914")
    for _ in range(3):
        game.end_turn()
        game.end_turn()

    assert later.zone == Zone.REMOVEDFROMGAME


def test_searing_reflection_draws_minion_and_summons_eight_eight_copy():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    deck_minion = player.card(WISP, zone=Zone.DECK)

    player.give("FIR_941").play()

    assert deck_minion in player.hand
    copy = player.field[-1]
    assert copy.id == WISP
    assert (copy.atk, copy.max_health) == (8, 8)
    assert copy.divine_shield


def test_ashleaf_pixie_gains_keywords_when_holding_expensive_spell():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    _set_mana(player)
    player.give("FIR_941")

    pixie = player.give("FIR_961").play()

    assert pixie.divine_shield
    assert pixie.lifesteal
