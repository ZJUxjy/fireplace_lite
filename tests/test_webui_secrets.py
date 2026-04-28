"""Audit + integration tests for the WebUI secret system.

This module starts with a sanity check that every ROADMAP-listed secret loads
from the CardDefs DB. Later tasks add parametrized tests that exercise
webui.server.game.GameManager.track_secrets() with simulated triggers.
"""
import pytest
from hearthstone.enums import CardClass

from utils import prepare_game

# All Phase 2 ROADMAP-listed secrets (card_id -> human name).
# These match webui/server/game.py TEST_DECK_CARDS entries.
ROADMAP_SECRETS = [
    # Mage
    ("EX1_295", "Ice Block"),
    ("EX1_287", "Counterspell"),
    ("EX1_289", "Ice Barrier"),
    ("EX1_294", "Mirror Entity"),
    ("EX1_594", "Vaporize"),
    ("ICC_082", "Frozen Clone"),
    # Hunter
    ("EX1_610", "Explosive Trap"),
    ("EX1_611", "Freezing Trap"),
    ("EX1_533", "Misdirection"),
    ("EX1_554", "Snake Trap"),
    ("EX1_609", "Snipe"),
    # Paladin
    ("EX1_130", "Noble Sacrifice"),
    ("EX1_136", "Redemption"),
    ("EX1_132", "Eye for an Eye"),
    ("EX1_379", "Repentance"),
]


def test_all_roadmap_secrets_load_from_carddb():
    """Sanity: every ROADMAP secret instantiates and is tagged as secret."""
    game = prepare_game()
    for card_id, _name in ROADMAP_SECRETS:
        card = game.player1.give(card_id)
        assert card is not None, f"{card_id} failed to instantiate"
        assert getattr(card.data, "secret", False), (
            f"{card_id} ({_name}) is not flagged as secret in CardDefs.xml"
        )
        # Drop from hand so the next give() doesn't hit the 10-card hand limit
        # (prepare_game starts the player with ~4 cards from mulligan; the loop
        # adds 15 more, which would otherwise burn 9 cards and break give()).
        card.destroy()


def _register_managed_game(game, game_id="test-game"):
    """Register an engine game into manager.games so track_secrets() can find it."""
    from webui.server.game import manager
    manager.games[game_id] = {
        "game": game,
        "players": [game.player1, game.player2],
        "logger": None,
        "mode": "pvp",
    }
    return game_id


def test_track_secrets_handles_two_same_name_secrets():
    """Bug regression: two Mirror Entities should both be tracked individually.

    Old impl keyed prev_secrets by str(secret) which collapses duplicates,
    so when one fires the diff sees zero deletions.

    We bypass the engine's "no duplicate secrets" uniqueness check by directly
    appending to player.secrets — the purpose here is purely to exercise the
    track_secrets() diff logic, not the engine trigger plumbing.
    """
    from webui.server.game import manager

    game = prepare_game(CardClass.MAGE, CardClass.MAGE)
    game_id = _register_managed_game(game, "dup-secret-test")
    try:
        s1 = game.player1.give("EX1_294")  # Mirror Entity (entity_id assigned at give())
        s2 = game.player1.give("EX1_294")  # Mirror Entity (second copy, distinct entity_id)
        # Directly inject both into the secrets zone, bypassing the engine's
        # "only one of each secret" uniqueness guard (is_summonable).  This lets
        # us test track_secrets() in isolation without wiring up full trigger logic.
        game.player1.secrets.append(s1)
        game.player1.secrets.append(s2)
        assert len(game.player1.secrets) == 2

        # Initialize tracker baseline
        manager.track_secrets(game_id)

        # Manually fire one secret by removing it from the secrets CardList.
        # (track_secrets diffs `player.secrets` directly, so this is the cleanest
        # way to isolate the tracker from engine-level trigger plumbing — the
        # engine-level trigger conditions are exhaustively covered in tests/test_secrets.py.)
        game.player1.secrets.remove(s1)
        assert s1 not in game.player1.secrets
        assert s2 in game.player1.secrets

        triggered = manager.track_secrets(game_id)
        assert len(triggered) == 1, (
            f"expected exactly one triggered secret, got {len(triggered)}: {triggered}"
        )
        assert triggered[0]["entity_id"] == s1.entity_id
    finally:
        manager.games.pop(game_id, None)


def _arm_and_simulate_trigger(game, card_id):
    """Play `card_id` as a secret on player1.

    We test the WebUI tracker, NOT every secret's trigger condition
    (which is covered exhaustively by tests/test_secrets.py at the engine level).
    """
    secret = game.player1.give(card_id)
    secret.play()
    assert secret in game.player1.secrets, f"{card_id} did not enter secrets zone"
    return secret


def _fire(secret):
    """Simulate the engine removing a fired secret from the secrets CardList."""
    secret.controller.secrets.remove(secret)


@pytest.mark.parametrize("card_id,name", ROADMAP_SECRETS)
def test_secret_fires_through_webui_tracker(card_id, name):
    """Every ROADMAP secret, when removed from the secrets zone, surfaces as a
    triggered event with the correct entity_id and card_id from track_secrets.
    """
    from webui.server.game import manager

    # Pick a class that can play this secret. EX1_* mage secrets need MAGE etc.
    # All hunter/paladin/mage/rogue secrets play fine via give() + play() regardless
    # of class because give() bypasses class restrictions; but Mulligan needs both
    # players to have a valid class. MAGE works for everything.
    game = prepare_game(CardClass.MAGE, CardClass.MAGE)
    game_id = _register_managed_game(game, f"sec-{card_id}")
    try:
        secret = _arm_and_simulate_trigger(game, card_id)
        manager.track_secrets(game_id)  # baseline

        _fire(secret)
        triggered = manager.track_secrets(game_id)

        assert len(triggered) == 1, f"{card_id}: expected 1 trigger, got {triggered}"
        t = triggered[0]
        assert t["player"] == "player"
        assert t["card_id"] == card_id
        assert t["entity_id"] == secret.entity_id
        assert t["secret_name"], f"{card_id}: secret_name should be non-empty"
    finally:
        manager.games.pop(game_id, None)


def test_track_secrets_returns_player_secrets_before_opponent():
    """ROADMAP §2.3: when secrets fire on both sides in the same tick,
    track_secrets must surface them in deterministic order (player first,
    then opponent), so the client renders reveal flashes left-to-right
    in a stable sequence.
    """
    from webui.server.game import manager

    game = prepare_game(CardClass.MAGE, CardClass.MAGE)
    game_id = _register_managed_game(game, "order-test")
    try:
        my_secret = game.player1.give("EX1_289")  # Ice Barrier
        opp_secret = game.player2.give("EX1_295")  # Ice Block
        my_secret.play()
        game.end_turn()
        opp_secret.play()
        game.end_turn()

        manager.track_secrets(game_id)  # baseline

        # Fire both in same tick
        _fire(my_secret)
        _fire(opp_secret)

        triggered = manager.track_secrets(game_id)
        assert len(triggered) == 2
        # Player's own secrets are reported first; opponent's after.
        assert triggered[0]["player"] == "player"
        assert triggered[1]["player"] == "opponent"

    finally:
        manager.games.pop(game_id, None)


def test_track_secrets_preserves_arming_order_within_one_side():
    """When two secrets on the same side fire on the same tick, the order
    should match the order they were armed (FIFO over the secrets list)."""
    from webui.server.game import manager

    game = prepare_game(CardClass.MAGE, CardClass.MAGE)
    game_id = _register_managed_game(game, "order-fifo-test")
    try:
        first = game.player1.give("EX1_287")  # Counterspell
        second = game.player1.give("EX1_289")  # Ice Barrier
        first.play()
        second.play()

        manager.track_secrets(game_id)  # baseline

        _fire(first)
        _fire(second)

        triggered = manager.track_secrets(game_id)
        names = [t["entity_id"] for t in triggered]
        assert names == [first.entity_id, second.entity_id], (
            f"expected FIFO order, got {names}"
        )
    finally:
        manager.games.pop(game_id, None)
