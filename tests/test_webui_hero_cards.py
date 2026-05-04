"""WebUI-layer tests for v0.3.0 Phase 4 hero cards."""

from hearthstone.enums import CardClass, CardType, Zone

from utils import prepare_empty_game


PHASE4_HERO_CARDS = [
    ("ICC_828", "Deathstalker Rexxar", CardClass.HUNTER, "ICC_828p"),
    ("ICC_833", "Frost Lich Jaina", CardClass.MAGE, "ICC_833h"),
    ("ICC_827", "Valeera the Hollow", CardClass.ROGUE, "ICC_827p"),
    ("ICC_834", "Scourgelord Garrosh", CardClass.WARRIOR, "ICC_834h"),
    ("ICC_830", "Shadowreaper Anduin", CardClass.PRIEST, "ICC_830p"),
    ("ICC_829", "Uther of the Ebon Blade", CardClass.PALADIN, "ICC_829p"),
    ("ICC_832", "Malfurion the Pestilent", CardClass.DRUID, "ICC_832p"),
    ("ICC_831", "Bloodreaver Gul'dan", CardClass.WARLOCK, "ICC_831p"),
    ("GIL_504", "Hagatha the Witch", CardClass.SHAMAN, "GIL_504h"),
]


def test_test_decks_include_phase4_hero_cards_for_manual_smoke():
    from webui.server.game import create_test_deck

    expected = {
        CardClass.HUNTER: "ICC_828",
        CardClass.MAGE: "ICC_833",
        CardClass.ROGUE: "ICC_827",
        CardClass.WARRIOR: "ICC_834",
        CardClass.PRIEST: "ICC_830",
        CardClass.PALADIN: "ICC_829",
        CardClass.DRUID: "ICC_832",
        CardClass.WARLOCK: "ICC_831",
        CardClass.SHAMAN: "GIL_504",
    }

    for card_class, hero_card_id in expected.items():
        deck = create_test_deck(card_class)
        assert hero_card_id in deck
        assert len(deck) == 30


def _play_hero_card(player, card_id, choose_index=0):
    """Play a hero card, choosing `choose_index` for Choose One hero cards."""
    card = player.give(card_id)
    _play_given_hero_card(card, choose_index)
    return card


def _play_given_hero_card(card, choose_index=0):
    """Play a hero card already in hand."""
    choose = None
    if getattr(card, "must_choose_one", False) and getattr(card, "choose_cards", None):
        choose = card.choose_cards[choose_index]
    card.play(choose=choose)
    return card


def test_phase4_hero_cards_load_as_hero_cards():
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)

    for card_id, name, card_class, hero_power_id in PHASE4_HERO_CARDS:
        card = game.player1.card(card_id)
        assert card.type == CardType.HERO
        assert str(card) == name
        assert card.data.card_class == card_class
        assert card.data.hero_power == hero_power_id
        assert card.data.armor == 5


def _register_managed_game(game, game_id="hero-card-test"):
    from webui.server.game import manager

    previous = manager.games.get(game_id, _MISSING_GAME)
    manager.games[game_id] = {
        "game": game,
        "players": [game.player1, game.player2],
        "logger": None,
        "mode": "pvp",
    }
    return game_id, previous


def _restore_managed_game(game_id, previous):
    from webui.server.game import manager

    if previous is _MISSING_GAME:
        manager.games.pop(game_id, None)
    else:
        manager.games[game_id] = previous


_MISSING_GAME = object()


class _FakeSocketIO:
    def __init__(self):
        self.handlers = {}

    def on(self, event_name):
        def decorator(handler):
            self.handlers[event_name] = handler
            return handler

        return decorator


class _ListLogger:
    def __init__(self):
        self.logs = []

    def add_log(self, log_type, message, details=None):
        self.logs.append({"type": log_type, "message": message, "details": details or {}})

    def get_logs(self, count=20):
        return self.logs[-count:]


def _register_socket_handlers(monkeypatch):
    from webui.server import socket as socket_module

    emitted = []
    monkeypatch.setattr(
        socket_module,
        "emit",
        lambda event_name, payload: emitted.append((event_name, payload)),
    )
    fake_socketio = _FakeSocketIO()
    socket_module.register_socket_events(fake_socketio)
    return fake_socketio.handlers, emitted


def _ensure_current_player(game, player):
    for _ in range(len(game.players)):
        if game.current_player == player:
            return
        game.end_turn()
    assert game.current_player == player


def test_play_card_socket_emits_and_logs_hero_transformed(monkeypatch):
    from webui.server.game import manager

    handlers, emitted = _register_socket_handlers(monkeypatch)
    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    _ensure_current_player(game, game.player1)
    logger = _ListLogger()
    game_id, previous = _register_managed_game(game, "hero-transform-socket-test")
    manager.games[game_id]["logger"] = logger
    try:
        card = game.player1.give("ICC_833")
        old_hero_name = str(game.player1.hero)
        old_hero_id = game.player1.hero.id

        handlers["play_card"]({"game_id": game_id, "card_index": game.player1.hand.index(card)})

        event_names = [event_name for event_name, _payload in emitted]
        assert event_names.index("game_state") < event_names.index("hero_transformed")

        transform_events = [
            payload for event_name, payload in emitted if event_name == "hero_transformed"
        ]
        assert len(transform_events) == 1
        payload = transform_events[0]
        hero = payload["hero"]
        assert payload["game_id"] == game_id
        assert hero["player"] == str(game.player1)
        assert hero["old_hero"] == old_hero_name
        assert hero["old_hero_id"] == old_hero_id
        assert hero["new_hero"] == "Frost Lich Jaina"
        assert hero["new_hero_id"] == "ICC_833"
        assert hero["card_id"] == "ICC_833"
        assert hero["hero_power"] == str(game.player1.hero.power)
        assert hero["hero_power_id"] == "ICC_833h"
        assert hero["armor"] == game.player1.hero.armor

        transform_logs = [log for log in logger.logs if log["type"] == "hero_transformed"]
        assert len(transform_logs) == 1
        assert transform_logs[0]["details"] == hero
    finally:
        _restore_managed_game(game_id, previous)


def test_play_card_socket_does_not_emit_hero_transformed_for_hero_skin(monkeypatch):
    from webui.server.game import manager

    handlers, emitted = _register_socket_handlers(monkeypatch)
    game = prepare_empty_game(CardClass.WARRIOR, CardClass.MAGE)
    _ensure_current_player(game, game.player1)
    logger = _ListLogger()
    game_id, previous = _register_managed_game(game, "hero-skin-socket-test")
    manager.games[game_id]["logger"] = logger
    try:
        card = game.player1.give("HERO_01a")
        assert card.type == CardType.HERO
        assert card.data.armor == 0

        handlers["play_card"]({"game_id": game_id, "card_index": game.player1.hand.index(card)})

        assert [event_name for event_name, _payload in emitted].count("hero_transformed") == 0
        assert not any(log["type"] == "hero_transformed" for log in logger.logs)
    finally:
        _restore_managed_game(game_id, previous)


def test_each_phase4_hero_card_replaces_hero_and_hero_power():
    for card_id, _name, card_class, hero_power_id in PHASE4_HERO_CARDS:
        game = prepare_empty_game(card_class, CardClass.MAGE)
        old_hero = game.player1.hero
        old_hero_id = old_hero.id
        old_armor = old_hero.armor
        card = game.player1.give(card_id)
        expected_armor = card.data.armor

        _play_given_hero_card(card)

        assert game.player1.hero.id == card_id
        assert game.player1.hero is not old_hero
        assert old_hero.zone == Zone.GRAVEYARD
        assert game.player1.hero.power.id == hero_power_id
        assert game.player1.hero.armor == old_armor + expected_armor
        assert game.player1.hero.id != old_hero_id


def test_webui_state_after_hero_transform_keeps_health_armor_and_power():
    from webui.server.game import manager

    game = prepare_empty_game(CardClass.HUNTER, CardClass.MAGE)
    game_id, previous = _register_managed_game(game, "rexxar-state-test")
    try:
        # Hand serialization is not under test here; keep setup artifacts isolated.
        game.player1.hand.clear()
        game.player2.hand.clear()
        game.player1.hero.set_current_health(23)
        game.player1.hero.armor = 2
        old_health = game.player1.hero.health
        old_armor = game.player1.hero.armor

        card = game.player1.give("ICC_828")
        expected_armor = card.data.armor
        _play_given_hero_card(card)

        state = manager.get_game_state(game_id)

        assert state["player"]["hero"] == "Deathstalker Rexxar"
        assert state["player"]["health"] == game.player1.hero.health
        assert state["player"]["armor"] == game.player1.hero.armor
        assert state["player"]["hero_power"]["name"] == "Build-A-Beast"
        assert game.player1.hero.health == old_health
        assert game.player1.hero.armor == old_armor + expected_armor
    finally:
        _restore_managed_game(game_id, previous)


def test_webui_state_exposes_base_hero_metadata_before_transform():
    from webui.server.game import manager

    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    game_id, previous = _register_managed_game(game, "base-hero-metadata-test")
    try:
        state = manager.get_game_state(game_id)

        assert state["player"]["hero_id"] == game.player1.hero.id
        assert state["player"]["hero_class"] == "MAGE"
        assert state["player"]["is_hero_card"] is False
    finally:
        _restore_managed_game(game_id, previous)


def test_webui_hero_skin_metadata_is_not_played_hero_card():
    from webui.server.game import manager

    game = prepare_empty_game(CardClass.WARRIOR, CardClass.MAGE)
    hero_skin = game.player1.card("HERO_01a")

    data = manager.get_hero_data(hero_skin)

    assert data["id"] == "HERO_01a"
    assert data["hero_class"] == "WARRIOR"
    assert data["is_hero_card"] is False


def test_webui_state_exposes_hero_card_metadata_after_transform():
    from webui.server.game import manager

    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    game_id, previous = _register_managed_game(game, "jaina-metadata-test")
    try:
        _play_hero_card(game.player1, "ICC_833")

        state = manager.get_game_state(game_id)

        assert state["player"]["hero_id"] == "ICC_833"
        assert state["player"]["hero_class"] == "MAGE"
        assert state["player"]["is_hero_card"] is True
        assert state["player"]["hero_power"]["id"] == "ICC_833h"
        assert state["player"]["hero_power"]["is_passive"] is False
        assert state["player"]["hero_power"]["requires_target"] is True
        assert "valid_targets" in state["player"]["hero_power"]
    finally:
        _restore_managed_game(game_id, previous)


def test_webui_hero_power_valid_targets_are_scoped_to_current_game():
    from webui.server.game import manager

    first_game = prepare_empty_game(CardClass.HUNTER, CardClass.MAGE)
    second_game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    second_game.player2.summon("CS2_231")
    first_id, first_previous = _register_managed_game(first_game, "target-scope-first")
    second_id, second_previous = _register_managed_game(second_game, "target-scope-second")
    try:
        state = manager.get_game_state(second_id)

        valid_targets = state["player"]["hero_power"]["valid_targets"]
        assert "hero" in valid_targets
        assert "opponent_hero" in valid_targets
        assert "enemy_minion-0" in valid_targets
    finally:
        _restore_managed_game(second_id, second_previous)
        _restore_managed_game(first_id, first_previous)


def test_opponent_hero_power_valid_targets_use_player_view_ids():
    from webui.server.game import manager

    game = prepare_empty_game(CardClass.MAGE, CardClass.MAGE)
    game.player1.summon("CS2_231")
    game_id, previous = _register_managed_game(game, "opponent-target-view-test")
    try:
        state = manager.get_game_state(game_id)

        valid_targets = state["opponent"]["hero_power"]["valid_targets"]
        assert "hero" in valid_targets
        assert "opponent_hero" in valid_targets
        assert "minion-0" in valid_targets
    finally:
        _restore_managed_game(game_id, previous)


def test_webui_state_exposes_passive_hero_power_metadata():
    from webui.server.game import manager

    game = prepare_empty_game(CardClass.SHAMAN, CardClass.MAGE)
    game_id, previous = _register_managed_game(game, "hagatha-metadata-test")
    try:
        _play_hero_card(game.player1, "GIL_504")

        state = manager.get_game_state(game_id)

        assert state["player"]["hero_id"] == "GIL_504"
        assert state["player"]["hero_power"]["id"] == "GIL_504h"
        assert state["player"]["hero_power"]["is_passive"] is True
        assert state["player"]["hero_power"]["is_usable"] is False
    finally:
        _restore_managed_game(game_id, previous)


def test_deathstalker_rexxar_build_a_beast_uses_two_choice_steps():
    game = prepare_empty_game(CardClass.HUNTER, CardClass.MAGE)
    _play_hero_card(game.player1, "ICC_828")

    game.end_turn()
    game.end_turn()
    game.player1.hero.power.use()

    assert game.player1.choice is not None
    assert len(game.player1.choice.cards) == 3

    first_choice = game.player1.choice.cards[0]
    game.player1.choice.choose(first_choice)
    assert game.player1.choice is not None
    assert len(game.player1.choice.cards) == 3

    second_choice = game.player1.choice.cards[0]
    game.player1.choice.choose(second_choice)
    assert game.player1.choice is None
    assert any(card.id == "ICC_828t" for card in game.player1.hand)


def test_make_choice_socket_handler_resolves_current_player_choice(monkeypatch):
    from webui.server import socket as socket_module

    class FakeSocketIO:
        def __init__(self):
            self.handlers = {}

        def on(self, event_name):
            def decorator(handler):
                self.handlers[event_name] = handler
                return handler

            return decorator

    emitted = []
    monkeypatch.setattr(
        socket_module,
        "emit",
        lambda event_name, payload: emitted.append((event_name, payload)),
    )

    fake_socketio = FakeSocketIO()
    socket_module.register_socket_events(fake_socketio)
    assert "make_choice" in fake_socketio.handlers

    game = prepare_empty_game(CardClass.HUNTER, CardClass.MAGE)
    game_id, previous = _register_managed_game(game, "make-choice-socket-test")
    try:
        _play_hero_card(game.player1, "ICC_828")
        game.end_turn()
        game.end_turn()
        game.player1.hero.power.use()

        fake_socketio.handlers["make_choice"]({"game_id": game_id, "card_index": 0})

        assert emitted[-1][0] == "game_state"
        assert emitted[-1][1]["game_id"] == game_id
        assert game.player1.choice is not None

        fake_socketio.handlers["make_choice"]({"game_id": game_id, "card_index": 0})

        assert emitted[-1][0] == "game_state"
        assert game.player1.choice is None
        assert any(card.id == "ICC_828t" for card in game.player1.hand)
    finally:
        _restore_managed_game(game_id, previous)


def test_make_choice_socket_handler_rejects_malformed_card_index(monkeypatch):
    from webui.server import socket as socket_module

    class FakeSocketIO:
        def __init__(self):
            self.handlers = {}

        def on(self, event_name):
            def decorator(handler):
                self.handlers[event_name] = handler
                return handler

            return decorator

    emitted = []
    monkeypatch.setattr(
        socket_module,
        "emit",
        lambda event_name, payload: emitted.append((event_name, payload)),
    )

    fake_socketio = FakeSocketIO()
    socket_module.register_socket_events(fake_socketio)

    game = prepare_empty_game(CardClass.HUNTER, CardClass.MAGE)
    game_id, previous = _register_managed_game(game, "make-choice-malformed-test")
    try:
        _play_hero_card(game.player1, "ICC_828")
        game.end_turn()
        game.end_turn()
        game.player1.hero.power.use()

        fake_socketio.handlers["make_choice"]({"game_id": game_id, "card_index": "0"})

        assert emitted[-1] == ("error", {"message": "Invalid choice index"})
        assert game.player1.choice is not None
    finally:
        _restore_managed_game(game_id, previous)


def test_malfurion_hero_power_choice_options_are_serialized():
    from webui.server.game import manager

    game = prepare_empty_game(CardClass.DRUID, CardClass.MAGE)
    game_id, previous = _register_managed_game(game, "malfurion-power-test")
    try:
        _play_hero_card(game.player1, "ICC_832")

        state = manager.get_game_state(game_id)

        hero_power = state["player"]["hero_power"]
        assert hero_power["id"] == "ICC_832p"
        assert hero_power["must_choose_one"] is True
        assert [card["name"] for card in hero_power["choose_cards"]] == ["Plague Lord", "Plague Lord"]
        assert {card["id"] for card in hero_power["choose_cards"]} == {"ICC_832pa", "ICC_832pb"}
    finally:
        _restore_managed_game(game_id, previous)


def test_malfurion_hero_power_socket_uses_selected_choice(monkeypatch):
    from webui.server.game import manager

    handlers, emitted = _register_socket_handlers(monkeypatch)
    game = prepare_empty_game(CardClass.DRUID, CardClass.MAGE)
    _ensure_current_player(game, game.player1)
    logger = _ListLogger()
    game_id, previous = _register_managed_game(game, "malfurion-power-socket-choice-test")
    manager.games[game_id]["logger"] = logger
    try:
        _play_hero_card(game.player1, "ICC_832")
        armor_before = game.player1.hero.armor

        handlers["use_hero_power"]({"game_id": game_id, "choose_card_id": "ICC_832pa"})

        assert emitted[-1][0] == "game_state"
        assert game.player1.hero.armor == armor_before + 3
        assert any(log["type"] == "hero_power" for log in logger.logs)
    finally:
        _restore_managed_game(game_id, previous)


def test_malfurion_hero_power_socket_rejects_missing_and_invalid_choice(monkeypatch):
    from webui.server.game import manager

    handlers, emitted = _register_socket_handlers(monkeypatch)
    cases = [
        ("missing", {}),
        ("invalid", {"choose_card_id": "not-a-choice"}),
    ]

    for suffix, payload in cases:
        game = prepare_empty_game(CardClass.DRUID, CardClass.MAGE)
        _ensure_current_player(game, game.player1)
        logger = _ListLogger()
        game_id, previous = _register_managed_game(game, f"malfurion-power-{suffix}-choice-test")
        manager.games[game_id]["logger"] = logger
        try:
            _play_hero_card(game.player1, "ICC_832")
            armor_before = game.player1.hero.armor
            mana_before = game.player1.mana

            emitted.clear()
            handlers["use_hero_power"]({"game_id": game_id, **payload})

            assert emitted == [("error", {"message": "Invalid hero power choice"})]
            assert game.player1.hero.armor == armor_before
            assert game.player1.mana == mana_before
            assert not any(log["type"] == "hero_power" for log in logger.logs)
        finally:
            _restore_managed_game(game_id, previous)


def test_hero_power_socket_uses_choice_option_target_requirements(monkeypatch):
    from webui.server import socket as socket_module
    from webui.server.game import manager

    class FakeHero:
        def __init__(self, name):
            self.name = name
            self.power = None

        def __str__(self):
            return self.name

    class FakeChoiceOption:
        id = "choice-target"
        targets = []

        def requires_target(self):
            return True

        def __str__(self):
            return "Targeted Choice"

    class FakeHeroPower:
        cost = 2
        must_choose_one = True

        def __init__(self, choose):
            self.choose_cards = [choose]
            self.used = None

        def is_usable(self):
            return True

        def requires_target(self):
            return False

        def use(self, target=None, choose=None):
            self.used = (target, choose)

        def __str__(self):
            return "Choose Target Power"

    class FakePlayer:
        def __init__(self, name):
            self.name = name
            self.hero = FakeHero(f"{name} Hero")

        def __str__(self):
            return self.name

    class FakeGame:
        def __init__(self):
            self.player1 = FakePlayer("Player1")
            self.player2 = FakePlayer("Player2")
            self.player1.opponent = self.player2
            self.player2.opponent = self.player1
            self.current_player = self.player1

    handlers, emitted = _register_socket_handlers(monkeypatch)
    monkeypatch.setattr(manager, "get_game_state", lambda game_id: {"ok": True})
    monkeypatch.setattr(socket_module, "emit_triggered_secrets", lambda game_id: [])
    monkeypatch.setattr(socket_module, "emit_fatigue_events", lambda game_id: [])

    game = FakeGame()
    choice = FakeChoiceOption()
    choice.targets = [game.player2.hero]
    hero_power = FakeHeroPower(choice)
    game.player1.hero.power = hero_power
    logger = _ListLogger()
    game_id, previous = _register_managed_game(game, "choice-option-target-test")
    manager.games[game_id]["logger"] = logger
    try:
        handlers["use_hero_power"]({"game_id": game_id, "choose_card_id": "choice-target"})

        assert emitted == [("error", {"message": "Valid target required"})]
        assert hero_power.used is None
        assert not any(log["type"] == "hero_power" for log in logger.logs)

        emitted.clear()
        handlers["use_hero_power"]({
            "game_id": game_id,
            "choose_card_id": "choice-target",
            "target_id": "opponent_hero",
        })

        assert emitted[-1] == ("game_state", {"game_id": game_id, "state": {"ok": True}})
        assert hero_power.used == (game.player2.hero, choice)
        assert any(log["type"] == "hero_power" for log in logger.logs)
    finally:
        _restore_managed_game(game_id, previous)


def test_hero_power_choice_option_valid_targets_are_scoped_to_current_game():
    from webui.server.game import manager

    class FakeMinion:
        pass

    class FakeHero:
        pass

    class FakeChoiceOption:
        id = "targeted-choice"
        cost = 0

        def __init__(self, targets):
            self.targets = targets

        def requires_target(self):
            return True

        def __str__(self):
            return "Targeted Choice"

    class FakeHeroPower:
        id = "fake-power"
        cost = 2
        must_choose_one = True

        def __init__(self, choose_cards):
            self.choose_cards = choose_cards

        def is_usable(self):
            return True

        def requires_target(self):
            return False

        def __str__(self):
            return "Fake Power"

    class FakePlayer:
        def __init__(self):
            self.hero = FakeHero()
            self.field = []

    class FakeGame:
        def __init__(self):
            self.player1 = FakePlayer()
            self.player2 = FakePlayer()

    first_game = FakeGame()
    second_game = FakeGame()
    second_target = FakeMinion()
    second_game.player2.field.append(second_target)
    second_power = FakeHeroPower([FakeChoiceOption([second_target])])

    first_id, first_previous = _register_managed_game(first_game, "choice-target-first-game")
    second_id, second_previous = _register_managed_game(second_game, "choice-target-second-game")
    try:
        data = manager.get_hero_power_data(second_power, second_game.player1, second_game.player2)

        assert data["choose_cards"][0]["valid_targets"] == ["enemy_minion-0"]
    finally:
        _restore_managed_game(second_id, second_previous)
        _restore_managed_game(first_id, first_previous)
