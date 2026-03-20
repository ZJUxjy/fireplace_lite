from utils import *


##
# Miniaturize tests

def test_miniaturize_gives_mini_copy():
    """Playing a Miniaturize minion should add a 1/1 mini copy to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    hand_before = len(game.player1.hand)
    # TOY_340: Nostalgic Initiate (2-cost, Miniaturize, no target requirement)
    initiate = game.player1.give("TOY_340")
    # hand_before + 1 card was added to hand; then: play(-1) + mini copy(+1) = hand_before + 1
    initiate.play()
    assert len(game.player1.hand) == hand_before + 1  # net: mini copy remains
    mini = game.player1.hand[-1]
    assert mini.id != "TOY_340"  # mini copy has a different card ID


def test_miniaturize_mini_copy_correct_card():
    """Mini copy should be a 1/1 version (different card) of the original."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    initiate = game.player1.give("TOY_340")  # Nostalgic Initiate (2/2 Miniaturize)
    initiate.play()
    assert len(game.player1.hand) == 1  # the mini copy
    mini = game.player1.hand[0]
    # The mini copy card ID should be TOY_340t1 (from COLLECTION_RELATED_CARD_DATABASE_ID)
    assert mini.id == "TOY_340t1"


##
# Titan engine tests

def _setup_titan_game():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    return game


def test_titan_has_three_abilities():
    """A Titan minion should have 3 ability cards initialized on play."""
    game = _setup_titan_game()
    eonar = game.player1.give("TTN_903")
    eonar.play()
    assert eonar in game.player1.field
    assert len(eonar.titan_abilities) == 3
    assert all(not used for used in eonar.titan_ability_used)


def test_titan_use_ability():
    """Using a Titan ability marks it as used and fires the play action."""
    game = _setup_titan_game()
    eonar = game.player1.give("TTN_903")
    eonar.play()
    hero = game.player1.hero
    hero.damage = 20  # set via damage (health = max_health - damage)
    assert hero.health == 10
    # Use ability index 1 (Bountiful Harvest: restore hero to full health)
    eonar.use_titan_ability(1)
    assert eonar.titan_ability_used[1] is True
    assert hero.health == 30  # fully healed


def test_titan_ability_once_ever():
    """A used Titan ability cannot be used again."""
    game = _setup_titan_game()
    eonar = game.player1.give("TTN_903")
    eonar.play()
    eonar.use_titan_ability(0)
    assert eonar.titan_ability_used[0] is True
    try:
        eonar.use_titan_ability(0)
        assert False, "Should have raised InvalidAction"
    except Exception:
        pass  # expected


def test_titan_one_ability_per_turn():
    """Only one ability can be used per turn."""
    game = _setup_titan_game()
    eonar = game.player1.give("TTN_903")
    eonar.play()
    eonar.use_titan_ability(0)
    assert eonar.titan_ability_cooldown is True
    try:
        eonar.use_titan_ability(1)
        assert False, "Should have raised InvalidAction"
    except Exception:
        pass  # expected


def test_titan_cooldown_resets_next_turn():
    """Titan ability cooldown resets at the start of each turn."""
    game = _setup_titan_game()
    eonar = game.player1.give("TTN_903")
    eonar.play()
    eonar.use_titan_ability(0)
    assert eonar.titan_ability_cooldown is True
    # End player 1's turn
    game.end_turn()
    game.end_turn()
    assert eonar.titan_ability_cooldown is False


def test_titan_ability_used_trigger():
    """Titan's ability_used script fires after each ability use."""
    game = _setup_titan_game()
    eonar = game.player1.give("TTN_903")
    eonar.play()
    field_before = len(game.player1.field)
    # Use any ability - Eonar's ability_used summons a 5/5 Ancient
    eonar.use_titan_ability(2)  # Flourish (refresh mana)
    # Should have summoned TTN_903t4 (Timeless Ancient)
    assert len(game.player1.field) > field_before


def test_titan_cleanup_on_death():
    """Titan ability state clears when the Titan dies."""
    game = _setup_titan_game()
    eonar = game.player1.give("TTN_903")
    eonar.play()
    assert len(eonar.titan_abilities) == 3
    eonar.destroy()
    assert len(eonar.titan_abilities) == 0
    assert len(eonar.titan_ability_used) == 0


def test_titan_ability_with_target():
    """Titan abilities that require a target work correctly."""
    game = _setup_titan_game()
    norgannon = game.player1.give("TTN_075")
    norgannon.play()
    # Target the enemy hero (any character target is valid for damage abilities)
    target = game.player2.hero
    health_before = target.health
    # Ability 0 (Progenitor's Power): Deal 5 damage to a target
    norgannon.use_titan_ability(0, target=target)
    assert target.health == health_before - 5


def test_titan_mana_refresh_ability():
    """Eonar's Flourish ability refreshes mana crystals."""
    game = _setup_titan_game()
    eonar = game.player1.give("TTN_903")
    eonar.play()
    game.player1.used_mana = 8  # set after playing Eonar
    # Flourish = ability index 2
    eonar.use_titan_ability(2)
    assert game.player1.used_mana == 0  # fully refreshed
