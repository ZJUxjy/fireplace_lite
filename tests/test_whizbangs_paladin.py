from utils import *
from hearthstone.enums import CardClass, CardType, Race, SpellSchool, Zone


def test_whack_a_gnoll_discovers_buffed_paladin_weapon():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("MIS_700").play()

    assert player.choice is not None
    assert all(card.type == CardType.WEAPON for card in player.choice.cards)
    choice = player.choice.cards[0]
    player.choice.choose(choice)

    assert choice in player.hand
    assert choice.atk == choice.data.atk + 1
    assert choice.durability == choice.data.health + 1


def test_holy_glowsticks_costs_one_after_holy_spell_and_has_lifesteal():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.hero.damage = 5
    target = player.opponent.summon("CS2_182")

    player.give(HOLY_LIGHT).play(target=player.hero)
    glowsticks = player.give("MIS_709")

    assert glowsticks.cost == 1
    assert glowsticks.data.spell_school == SpellSchool.HOLY

    player.used_mana = 0
    player.hero.damage = 5
    glowsticks.play(target=target)

    assert target.damage == 4
    assert player.hero.damage == 1


def test_flickering_lightbot_gigantifies_and_discounts_for_holy_spells():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    player.give(HOLY_LIGHT).play(target=player.hero)
    player.used_mana = 0
    player.give(HOLY_LIGHT).play(target=player.hero)
    lightbot = player.give("MIS_918")

    assert lightbot.cost == lightbot.data.cost - 2

    lightbot.play()

    gigantic = player.hand[0]
    assert gigantic.id == "MIS_918t"
    assert gigantic.cost == gigantic.data.cost - 2


def test_flash_sale_summons_mech_and_buffs_friendly_minions():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    existing = player.summon(WISP)

    player.give("TOY_716").play()

    assert existing.atk == existing.data.atk + 1
    assert existing.max_health == existing.data.health + 2
    token = player.field[-1]
    assert token.atk == 2
    assert token.max_health == 4
    assert token.divine_shield
    assert token.taunt
    assert Race.MECHANICAL in token.races


def test_crafters_aura_summons_for_three_friendly_turn_ends():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("TOY_808").play()

    game.end_turn()
    assert len(player.field) == 1
    game.end_turn()

    game.end_turn()
    assert len(player.field) == 2
    game.end_turn()

    game.end_turn()
    assert len(player.field) == 3
    game.end_turn()

    game.end_turn()
    assert len(player.field) == 3


def test_cardboard_golem_increases_aura_duration_in_hand_and_battlefield():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    aura_in_hand = player.give("TOY_808")
    active_aura = player.give("TOY_808")
    active_aura.play()

    player.give("TOY_809").play()

    assert getattr(aura_in_hand, "_aura_duration_bonus", 0) == 1
    aura_buffs = [buff for buff in player.buffs if buff.id == "TOY_808e"]
    assert aura_buffs
    assert aura_buffs[0]._crafter_aura_turns_remaining == 4


def test_painters_virtue_buffs_minions_in_hand_after_hero_attack():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    minion = player.give(WISP)

    player.give("TOY_810").play()
    player.hero.attack(player.opponent.hero)

    assert minion.atk == minion.data.atk + 1
    assert minion.max_health == minion.data.health + 1


def test_tigress_plushy_miniaturizes_with_keywords():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    plushy = player.give("TOY_811").play()

    assert plushy.rush
    assert plushy.lifesteal
    assert plushy.divine_shield
    mini = player.hand[0]
    assert mini.id == "TOY_811t"
    assert mini.rush
    assert mini.lifesteal
    assert mini.divine_shield


def test_pipsi_summons_divine_shield_rush_and_taunt_minions_from_deck():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    shield = player.card("TOY_811")
    rush = player.card("AV_215")
    taunt = player.card("TOY_813")
    for card in (shield, rush, taunt):
        card.zone = Zone.DECK

    pipsi = player.summon("TOY_812")
    pipsi.destroy()

    assert shield in player.field
    assert rush in player.field
    assert taunt in player.field


def test_toy_captain_tarim_miniaturizes_and_sets_target_to_own_stats():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.opponent.summon("CS2_182")

    tarim = player.give("TOY_813").play(target=target)

    assert target.atk == tarim.atk
    assert target.max_health == tarim.max_health
    assert player.hand[0].id == "TOY_813t"


def test_wind_up_enforcer_summons_upgraded_number_of_copies():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    enforcer = player.give("TOY_880")
    enforcer._wind_up_copies = 3

    enforcer.play()

    assert len([minion for minion in player.field if minion.id == "TOY_880"]) == 4


def test_fancy_packaging_requires_divine_shield_and_buffs_target():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    target = player.summon("TOY_811")

    player.give("TOY_881").play(target=target)

    assert target.atk == target.data.atk + 2
    assert target.max_health == target.data.health + 3


def test_trinket_artist_draws_divine_shield_minion_and_aura():
    game = prepare_empty_game(CardClass.PALADIN, CardClass.PALADIN)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    shield = player.card("TOY_811")
    aura = player.card("TOY_808")
    other = player.card(WISP)
    for card in (shield, aura, other):
        card.zone = Zone.DECK

    player.give("TOY_882").play()

    assert shield in player.hand
    assert aura in player.hand
    assert other in player.deck
