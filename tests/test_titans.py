from utils import *
from fireplace.actions import Hit
from hearthstone.enums import CardType


##
# TTN_737t: Runes of Blood
# Destroy an enemy minion; restore health equal to its Health to your hero

def test_runes_of_blood_heals_hero_by_minion_health():
    """Runes of Blood destroys a minion and heals hero by its health."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Summon a 3/5 minion for player2
    target = game.player2.summon("CS2_189")  # Elven Archer 1/1
    # Damage player1's hero a bit first
    game.player1.hero.damage = 5
    hero_hp_before = game.player1.hero.health  # 25

    primus = game.player1.summon("TTN_737")
    primus.use_titan_ability(0, target=target)  # TTN_737t: Runes of Blood

    # Target should be dead
    assert target.zone.name == "GRAVEYARD"
    # Hero should have gained 1 health (Elven Archer = 1/1, health = 1)
    assert game.player1.hero.health == hero_hp_before + 1


def test_runes_of_blood_heals_by_larger_minion_health():
    """Runes of Blood heals hero by the full health of a bigger minion."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Summon a minion with 4 health
    target = game.player2.summon("CS2_222")  # Stormwind Champion 6/6
    game.player1.hero.damage = 10
    hero_hp_before = game.player1.hero.health  # 20

    target_health = target.health  # capture before destroying
    primus = game.player1.summon("TTN_737")
    primus.use_titan_ability(0, target=target)  # TTN_737t: Runes of Blood

    assert target.zone.name == "GRAVEYARD"
    assert game.player1.hero.health == min(game.player1.hero.max_health, hero_hp_before + target_health)


##
# TTN_800: Golganneth, the Thunderer
# Passive: First spell each turn costs 3 less

def test_golganneth_passive_reduces_first_spell_cost():
    """Golganneth reduces the cost of the first spell by 3."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.summon("TTN_800")
    # Give player a spell — Frostbolt (CS2_024) costs 2
    spell = game.player1.give("CS2_024")  # Frostbolt 2-cost
    assert spell.cost == max(0, spell.data.cost - 3)


def test_golganneth_passive_only_first_spell():
    """Golganneth discount applies only before a spell is cast this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.summon("TTN_800")
    spell1 = game.player1.give("CS2_024")   # Frostbolt 2-cost
    spell2 = game.player1.give("CS2_024")   # second Frostbolt
    # Both start discounted (neither played yet)
    assert spell1.cost == max(0, spell1.data.cost - 3)
    assert spell2.cost == max(0, spell2.data.cost - 3)
    # Play one spell
    spell1.play(target=game.player2.hero)
    # Now the second spell should be at full cost
    assert spell2.cost == spell2.data.cost


##
# TTN_800t3: Shargahn's Wrath
# Draw 3 Overload cards from your deck

def test_sharghans_wrath_draws_overload_cards():
    """Shargahn's Wrath draws up to 3 Overload cards from deck."""
    from hearthstone.enums import GameTag as GTag
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Give player1 some overload cards in deck — AT_052 = Totem Golem (Overload 1)
    for _ in range(3):
        game.player1.deck.append(game.player1.card("AT_052"))
    # Add non-overload cards too
    for _ in range(5):
        game.player1.deck.append(game.player1.card("CS2_189"))

    golganneth = game.player1.summon("TTN_800")
    hand_before = len(game.player1.hand)
    golganneth.use_titan_ability(2)  # TTN_800t3: Shargahn's Wrath

    # Should draw 3 overload cards
    assert len(game.player1.hand) == hand_before + 3
    new_cards = game.player1.hand[-3:]
    assert all(getattr(c, "overload", 0) > 0 for c in new_cards)


##
# TTN_960t4: Legion Invasion!
# Future Demons summoned from the Twisting Nether have +2 Health and Taunt

def test_legion_invasion_buffs_future_portal_demons():
    game = prepare_empty_game()
    player = game.player1
    player.max_mana = 10
    player.summon("TTN_960t")
    sargeras = player.summon("TTN_960")
    sargeras.use_titan_ability(2)  # TTN_960t4: Legion Invasion!

    game.end_turn()

    demons = [minion for minion in player.field if minion.id == "TTN_960t6"]
    assert len(demons) == 2
    assert all(demon.max_health == demon.data.health + 2 for demon in demons)
    assert all(demon.taunt for demon in demons)


def test_legion_invasion_does_not_buff_demons_played_from_hand():
    game = prepare_empty_game()
    player = game.player1
    player.max_mana = 10
    sargeras = player.summon("TTN_960")
    sargeras.use_titan_ability(2)  # TTN_960t4: Legion Invasion!

    demon = player.give("AT_026")
    base_health = demon.data.health
    demon.play()

    played_demon = player.field[-1]
    assert played_demon.max_health == base_health
    assert played_demon.taunt is False


def test_amitus_caps_damage_to_friendly_minions_at_two():
    game = prepare_empty_game()
    player = game.player1
    target = player.summon("CS2_222")
    player.summon("TTN_858")

    game.queue_actions(game.player2.hero, [Hit(target, 6)])

    assert target.damage == 2


def test_argus_grants_positional_rush_and_lifesteal_as_aura():
    game = prepare_empty_game()
    player = game.player1
    left = player.summon("CS2_231")
    argus = player.summon("TTN_862")
    right = player.summon("CS2_231")
    game.refresh_auras()

    assert left.rush is True
    assert right.lifesteal is True

    player.field.remove(left)
    player.field.append(left)
    game.refresh_auras()

    assert right.rush is False
    assert left.rush is False
    assert left.lifesteal is True


def test_v07tr0n_prime_repeats_ability_on_another_friendly_minion():
    game = prepare_empty_game()
    player = game.player1
    ally = player.summon("CS2_231")
    target = player.opponent.hero
    prime = player.summon("TTN_721")

    prime.use_titan_ability(0)

    assert prime.atk == prime.data.atk + 2
    assert prime.max_health == prime.data.health + 1
    assert ally.atk == ally.data.atk + 2
    assert ally.max_health == ally.data.health + 1
    assert target.damage == 8


def test_aggramar_maintain_order_draws_after_hero_attacks():
    game = prepare_empty_game()
    player = game.player1
    player.max_mana = 10
    player.deck.append(player.card("CS2_189"))
    aggramar = player.give("TTN_092").play()
    hand_before = len(player.hand)

    aggramar.use_titan_ability(0)

    assert len(player.hand) == hand_before
    player.hero.attack(player.opponent.hero)
    assert len(player.hand) == hand_before + 1
    assert player.hand[-1].id == "CS2_189"


def test_aggramar_commanding_presence_summons_after_hero_attacks():
    game = prepare_empty_game()
    player = game.player1
    player.max_mana = 10
    aggramar = player.give("TTN_092").play()
    field_before = len(player.field)

    aggramar.use_titan_ability(1)

    assert len(player.field) == field_before
    player.hero.attack(player.opponent.hero)
    assert any(minion.id == "TTN_092e2t" for minion in player.field)


def test_aggramar_swift_slash_grants_attack_and_immune_while_attacking():
    game = prepare_empty_game()
    player = game.player1
    player.max_mana = 10
    target = player.opponent.summon("CS2_222")
    aggramar = player.give("TTN_092").play()
    hero_damage_before = player.hero.damage

    aggramar.use_titan_ability(2)

    assert player.hero.atk == 5
    player.hero.attack(target)
    assert player.hero.damage == hero_damage_before


def test_norgannon_progenitors_power_doubles_after_first_ability():
    game = prepare_empty_game()
    player = game.player1
    player.max_mana = 10
    norgannon = player.summon("TTN_075")
    target = player.opponent.hero

    norgannon.use_titan_ability(1)
    norgannon.titan_ability_cooldown = False
    norgannon.use_titan_ability(0, target=target)

    assert target.damage == 10


def test_norgannon_ancient_knowledge_raises_enemy_hand_cost_next_turn():
    game = prepare_empty_game()
    player = game.player1
    player.max_mana = 10
    enemy_card = player.opponent.give("CS2_189")
    base_cost = enemy_card.cost
    norgannon = player.summon("TTN_075")

    norgannon.use_titan_ability(1)

    assert enemy_card.cost == base_cost
    game.end_turn()
    assert enemy_card.cost == base_cost + 1
    game.end_turn()
    assert enemy_card.cost == base_cost


def test_yogg_saron_induce_insanity_forces_enemy_minions_to_attack_each_other():
    game = prepare_empty_game()
    player = game.player1
    enemy = player.opponent
    attacker = enemy.summon("CS2_182")
    defender = enemy.summon("CS2_182")
    ability = player.card("YOG_516t2")

    game.main_power(ability, ability.get_actions("play"), None)

    assert attacker.zone.name == "GRAVEYARD"
    assert defender.zone.name == "GRAVEYARD"
