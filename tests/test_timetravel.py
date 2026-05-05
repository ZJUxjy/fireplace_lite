from utils import *
from hearthstone.enums import CardType, Zone


##
# neutral.py

def test_end_037_murozond_gains_mana_from_hand():
    """Endtime Murozond gains mana equal to total hand card costs."""
    game = prepare_empty_game()
    game.player1.max_mana = 3  # start with 3 max crystals
    game.player1.give("CS2_024")  # Frostbolt cost=2
    murozond = game.player1.give("END_037")
    murozond.cost = 0  # play for free so we can verify mana gain
    murozond.play()
    # Gained 2 mana (only Frostbolt in hand when battlecry fires)
    assert game.player1.max_mana == 5  # 3 + 2


def test_time_054_time_skipper_doubles_hand():
    """Time Skipper doubles your hand on battlecry."""
    game = prepare_empty_game()
    game.player1.give("CS2_029")  # Fireball
    game.player1.give("EX1_308")  # Soulfire
    hand_before = len(game.player1.hand)  # 2 cards
    skipper = game.player1.give("TIME_054")
    skipper.play()
    # TIME_054 moves to field, battlecry doubles the remaining 2 hand cards
    assert len(game.player1.hand) == hand_before * 2


def test_time_103_chromie_doubles_hand_on_turn_end():
    """Chromie doubles your hand at the end of your turn."""
    game = prepare_empty_game()
    game.player1.summon("TIME_103")
    game.player1.give("CS2_029")  # Fireball
    game.player1.give("EX1_308")  # Soulfire
    hand_before = len(game.player1.hand)
    game.end_turn()  # triggers OWN_TURN_END
    assert len(game.player1.hand) == hand_before * 2


def test_time_event_301_destroys_one_without_dragons():
    """Disciple of Demise destroys 1 minion when holding no dragons."""
    game = prepare_empty_game()
    m1 = game.player2.summon("CS2_189")  # Elven Archer
    m2 = game.player2.summon("CS2_189")
    disc = game.player1.give("TIME_EVENT_301")
    disc.play()
    dead = sum(1 for m in [m1, m2] if m.zone == Zone.GRAVEYARD)
    assert dead == 1


def test_time_event_301_destroys_extra_per_dragon():
    """Disciple of Demise destroys 1 + dragon_count minions."""
    game = prepare_empty_game()
    # Give player1 a dragon card in hand (Faerie Dragon = minion with DRAGON race)
    game.player1.give("NEW1_023")  # Faerie Dragon 3/2 Dragon
    # Summon 3 enemy minions
    m1 = game.player2.summon("CS2_189")
    m2 = game.player2.summon("CS2_189")
    m3 = game.player2.summon("CS2_189")
    disc = game.player1.give("TIME_EVENT_301")
    disc.play()
    # Should destroy 1 (base) + 1 (dragon in hand) = 2 minions
    dead = sum(1 for m in [m1, m2, m3] if m.zone == Zone.GRAVEYARD)
    assert dead == 2


def test_time_event_301_can_destroy_friendly_other_minion():
    """Disciple of Demise can destroy any other minion, including friendly minions."""
    game = prepare_empty_game()
    friendly = game.player1.summon("CS2_189")
    disc = game.player1.give("TIME_EVENT_301")
    disc.play()
    assert friendly.zone == Zone.GRAVEYARD


def test_time_event_997_reopens_location_and_adds_deathrattle():
    """Welcome Home reopens a friendly location and adds the 3-cost summon deathrattle."""
    game = prepare_empty_game()
    location = game.player1.give("TOY_512").play()
    location.use()
    assert location.location_exhausted
    spell = game.player1.give("TIME_EVENT_997")
    spell.play(target=location)
    assert not location.location_exhausted
    assert location.has_deathrattle
    field_before = len(game.player1.field)
    location.destroy()
    assert len(game.player1.field) == field_before
    assert any(card.cost == 3 for card in game.player1.field)


def test_time_442_imprisons_and_awakes_original_minion():
    """Timeway Warden makes the target dormant until Warden dies."""
    game = prepare_empty_game()
    target = game.player2.summon("CS2_222")
    warden = game.player1.give("TIME_442")
    warden.play(target=target)
    assert target.zone == Zone.PLAY
    assert target.dormant
    assert target.dormant_turns == 10000
    warden.destroy()
    assert target.zone == Zone.PLAY
    assert not target.dormant
    assert target.dormant_turns == 0


def test_time_event_998_sends_hand_minions_two_turns_then_buffs():
    """Runi sends hand minions away for two own turns, then returns them with +5/+5."""
    game = prepare_empty_game()
    minion = game.player1.give("CS2_231")
    spell = game.player1.give("CS2_029")
    runi = game.player1.give("TIME_EVENT_998")
    runi.play()
    assert minion.zone == Zone.SETASIDE
    assert minion not in game.player1.hand
    assert spell in game.player1.hand
    game.end_turn()
    game.end_turn()
    assert minion.zone == Zone.SETASIDE
    game.end_turn()
    game.end_turn()
    assert minion in game.player1.hand
    assert minion.atk == minion.data.atk + 5
    assert minion.max_health == minion.data.health + 5


##
# deathknight.py

def test_time_610_shadows_draws_all_deck_minions():
    """Shadows of Yesterday draws all minions from the deck."""
    game = prepare_empty_game()
    game.player1.deck.append(game.player1.card("CS2_189"))  # minion
    game.player1.deck.append(game.player1.card("CS2_189"))  # minion
    game.player1.deck.append(game.player1.card("CS2_029"))  # spell
    hand_before = len(game.player1.hand)
    shadows = game.player1.give("TIME_610")
    shadows.play()
    # Both minions drawn (spell stays in deck)
    assert len(game.player1.hand) == hand_before + 2


##
# rogue.py

def test_time_039_deja_vu_gives_copy_of_last_played():
    """Deja Vu puts a copy of the last card played this turn in hand."""
    game = prepare_empty_game()
    fireball = game.player1.give("CS2_029")  # Fireball
    fireball.play(target=game.player2.hero)
    hand_before = len(game.player1.hand)
    deja_vu = game.player1.give("TIME_039")
    deja_vu.play()
    # Should gain a copy of Fireball (last played before Deja Vu)
    assert len(game.player1.hand) == hand_before + 1
    assert game.player1.hand[-1].id == "CS2_029"


def test_time_712_dethrone_draws_bottom_card():
    """Dethrone draws the bottom card from the deck."""
    game = prepare_empty_game()
    bottom = game.player1.card("CS2_189")  # Elven Archer (bottom = deck[0])
    top = game.player1.card("CS2_029")     # Fireball (top = deck[-1])
    game.player1.deck.append(bottom)
    game.player1.deck.append(top)
    hand_before = len(game.player1.hand)
    dethrone = game.player1.give("TIME_712")
    dethrone.play()
    assert len(game.player1.hand) == hand_before + 1
    # The drawn card should be the bottom (Elven Archer), not the top (Fireball)
    assert game.player1.hand[-1].id == "CS2_189"


def test_time_770_fast_forward_swaps_hand_for_draws():
    """Fast Forward puts hand into deck and draws the same number of cards."""
    game = prepare_empty_game()
    game.player1.give("CS2_029")  # Fireball
    game.player1.give("EX1_308")  # Soulfire
    # Add cards with proper Zone.DECK so Draw can find them
    c1 = game.player1.card("CS2_189")
    c1.zone = Zone.DECK
    c2 = game.player1.card("CS2_189")
    c2.zone = Zone.DECK
    hand_before = len(game.player1.hand)  # 2 cards
    fast_forward = game.player1.give("TIME_770")
    fast_forward.play()
    # hand_before cards were shuffled into deck, same amount drawn back
    assert len(game.player1.hand) == hand_before


##
# druid.py

def test_time_023_contingency_draws_bottom_two():
    """Contingency draws the two bottom cards from the deck."""
    game = prepare_empty_game()
    bottom1 = game.player1.card("CS2_189")  # deck[0] = bottom
    bottom2 = game.player1.card("CS2_142")  # deck[1]
    top = game.player1.card("CS2_029")      # deck[2] = top
    game.player1.deck.append(bottom1)
    game.player1.deck.append(bottom2)
    game.player1.deck.append(top)
    hand_before = len(game.player1.hand)
    contingency = game.player1.give("TIME_023")
    contingency.play()
    # Both bottom cards drawn; top card stays undrawn
    assert len(game.player1.hand) == hand_before + 2


def test_time_702_ebb_and_flow_single_buff_without_treant():
    """Ebb and Flow gives +1/+1 without a treant on board."""
    game = prepare_empty_game()
    minion = game.player1.summon("CS2_189")  # Elven Archer 1/1
    atk_before = minion.atk
    hp_before = minion.health
    spell = game.player1.give("TIME_702")
    spell.play(target=minion)
    assert minion.atk == atk_before + 1
    assert minion.health == hp_before + 1


def test_time_702_ebb_and_flow_double_buff_with_treant():
    """Ebb and Flow gives +2/+2 when you control a treant."""
    game = prepare_empty_game()
    # LETL_858H3 is a Treant minion with Race.TREANT
    treant = game.player1.summon("LETL_858H3")
    minion = game.player1.summon("CS2_189")  # Elven Archer 1/1
    atk_before = minion.atk
    hp_before = minion.health
    spell = game.player1.give("TIME_702")
    spell.play(target=minion)
    assert minion.atk == atk_before + 2
    assert minion.health == hp_before + 2


def test_time_703_endangered_dodo_no_summon_without_damaged():
    """Endangered Dodo does NOT summon if no damaged friendly minion."""
    game = prepare_empty_game()
    dodo = game.player1.summon("TIME_703")
    field_before = len(game.player1.field)
    game.end_turn()
    # No damaged minions during player2's turn, then player1 ends turn
    game.end_turn()
    game.end_turn()  # trigger OWN_TURN_END for player1 again
    # No damaged minions, no token
    assert len(game.player1.field) == field_before


def test_time_703_endangered_dodo_summons_with_damaged_minion():
    """Endangered Dodo summons a 2/2 when a friendly minion is damaged."""
    game = prepare_empty_game()
    dodo = game.player1.summon("TIME_703")
    # Damage the dodo itself (give it 1 damage)
    dodo.damage = 1
    field_before = len(game.player1.field)
    game.end_turn()  # triggers OWN_TURN_END for player1
    # Find damaged: dodo is damaged → summon token
    assert len(game.player1.field) == field_before + 1


def test_time_705_krona_reduces_bottom_5_cost():
    """Krona reduces the cost of bottom 5 deck cards to 1."""
    game = prepare_empty_game()
    # Put 6 cards in deck: deck[0..4] are bottom 5, deck[5] is top
    for _ in range(5):
        game.player1.deck.append(game.player1.card("CS2_029"))  # Fireball cost=4
    game.player1.deck.append(game.player1.card("CS2_029"))  # top card cost=4
    top_card = game.player1.deck[-1]
    krona = game.player1.give("TIME_705")
    krona.play()
    # Bottom 5 should now cost 1
    for card in game.player1.deck[:5]:
        assert card.cost == 1
    # Top card should still cost 4
    assert game.player1.deck[-1].cost == 4


##
# warrior.py

def test_time_750_precursory_strike_no_weapon_in_hand():
    """Precursory Strike deals 3 damage; no copy if no weapon in hand."""
    game = prepare_empty_game()
    target = game.player2.summon("CS2_222")  # Stormwind Champion 6/6
    hp_before = target.health
    hand_before = len(game.player1.hand)  # 0 spells/weapons
    spell = game.player1.give("TIME_750")
    spell.play(target=target)
    assert target.health == hp_before - 3
    # No weapon in hand, so no copy of the spell; hand is empty
    assert len(game.player1.hand) == 0


def test_time_750_precursory_strike_with_weapon_in_hand():
    """Precursory Strike gives a copy if a weapon is in hand."""
    game = prepare_empty_game()
    target = game.player2.summon("CS2_222")
    game.player1.give("CS2_091")  # Light's Justice weapon in hand
    hand_before = len(game.player1.hand)  # 1 weapon
    spell = game.player1.give("TIME_750")
    spell.play(target=target)
    # Played spell (-1), got copy (+1), weapon still there
    # Net: hand_before (weapon) stays, plus copy gained
    assert len(game.player1.hand) == hand_before + 1


##
# hunter.py

def test_end_015_triennium_rex_buffs_beasts():
    """Triennium Rex gives +2/+2 to friendly beasts (aura)."""
    game = prepare_empty_game()
    # Stonetusk Boar (CS2_181) is 1/1 but may not be a beast in this db
    # Use King of Beasts (AT_063) or a known beast
    # Triennium Rex itself is a beast; its aura should apply to itself too
    rex = game.player1.summon("END_015")
    # Check that a beast summoned after gets the buff
    # CS2_181 = Stonetusk Boar (check if beast)
    # Use "FP1_011" = Webspinner 1/1 Beast
    beast = game.player1.summon("FP1_011")  # Webspinner 1/1 Beast
    # With rex's aura active, beast should have +2 ATK/+2 HP
    assert beast.atk >= 1 + 2  # at least base + 2 aura bonus


def test_time_042ta_banana_buffs_plus_1_1():
    """Banana (+1/+1) choice buffs target by +1/+1."""
    game = prepare_empty_game()
    target = game.player1.summon("CS2_189")
    atk_before = target.atk
    hp_before = target.health
    spell = game.player1.give("TIME_042ta")
    spell.play(target=target)
    assert target.atk == atk_before + 1
    assert target.health == hp_before + 1


##
# warlock.py

def test_end_018_acolyte_doubles_hand_on_death():
    """Acolyte of Infinity doubles the hand on deathrattle."""
    game = prepare_empty_game()
    acolyte = game.player1.summon("END_018")
    game.player1.give("CS2_029")
    game.player1.give("EX1_308")
    hand_before = len(game.player1.hand)  # 2
    acolyte.destroy()
    game.process_deaths()
    assert len(game.player1.hand) == hand_before * 2


##
# paladin.py

def test_time_019_manifested_timeways_gains_hand_size_atk():
    """Manifested Timeways gains ATK equal to hand size."""
    game = prepare_empty_game()
    game.player1.give("CS2_029")
    game.player1.give("CS2_029")
    game.player1.give("CS2_029")
    hand_count = len(game.player1.hand)  # 3 Fireballs
    minion = game.player1.give("TIME_019")
    minion.play()
    # Base ATK is 3; gained hand_count ATK (3 cards in hand when battlecry fires)
    assert minion.atk == 3 + hand_count


##
# mage.py

def test_time_858_temporal_construct_gains_spell_cost_atk():
    """Temporal Construct gains ATK equal to total spell cost in hand."""
    game = prepare_empty_game()
    game.player1.give("CS2_029")  # Fireball cost=4
    game.player1.give("CS2_029")  # Fireball cost=4
    minion = game.player1.give("TIME_858")
    minion.play()
    # Base ATK is 5; battlecry fires when 2 Fireballs (total 8) are in hand
    assert minion.atk == 5 + 8
