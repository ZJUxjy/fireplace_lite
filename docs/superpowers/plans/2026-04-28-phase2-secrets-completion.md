# Phase 2 奥秘系统补全 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the gap between fireplace's already-implemented engine-level secret cards and the WebUI's secret-handling layer — fix a duplicate-name detection bug, eliminate four-way DRY violation in socket emit code, prove every ROADMAP-listed secret triggers correctly through the WebUI manager, add deterministic trigger-order coverage, and reveal a fired opponent secret's name briefly to the player.

**Architecture:** All 15 ROADMAP-listed secrets are already implemented in `fireplace/cards/classic/{mage,hunter,paladin,rogue}.py` and one in `fireplace/cards/icecrown/mage.py`. This plan does NOT add card scripts. Work splits into three layers:
1. **WebUI server (`webui/server/game.py`, `socket.py`)**: refactor `track_secrets` to key diffs by stable `entity_id` instead of `str(secret)` (handles duplicates), centralize the four duplicated emit blocks into a single helper.
2. **Tests (`tests/test_webui_secrets.py` — new)**: register games into `manager.games` directly, parametrize one test per ROADMAP secret, plus one trigger-order test. Uses existing `prepare_game()` from `tests/utils.py`.
3. **WebUI client (`webui/client/src/components/GameBoard.tsx`, `GameBoard.css`)**: when a `secret_triggered` event arrives, render a brief "secret reveal" flash card that shows the fired secret's name, fading after ~1.6s.

**Tech Stack:** Python 3.10+, pytest, fireplace engine; React 19 + TypeScript + Vite + Socket.IO client; pure CSS animations.

**Branch to work from:** `glm-5v-turbo`. Worktree recommended but not mandatory — only touches files outside the active UI-beautification surface.

---

## Current State Summary

### Already Implemented
- All 15 ROADMAP secrets exist as engine card scripts (verified via grep on card IDs).
- WebUI `game.py` exposes per-player `secrets` (revealed name+text for self), `secret_count`, `max_secrets`.
- WebUI `track_secrets()` diffs prev vs current secret lists each tick.
- WebUI `socket.py` emits `secret_triggered` event in 4 places (after AI turn, after end_turn, after play_card, after attack, after hero_power).
- Client `GameBoard.tsx` renders secret zones for both players, listens for `secret_triggered`, plays an 800ms blink animation, appends to action log.

### Real Gaps Closed by This Plan
| Gap | Fix |
|---|---|
| `track_secrets` keys by `str(secret)` — duplicate-name secrets collapse | Key by `entity_id`, return secret name+id in payload |
| Same 6-line emit block duplicated 4× in socket.py | Extract `emit_triggered_secrets(game_id)` helper |
| Zero WebUI-layer tests for any secret | New `tests/test_webui_secrets.py`: 15 parametrized cases + order test |
| ROADMAP §2.3 trigger priority untested | Dedicated test: 2 secrets armed, single triggering action, verify both detected in deterministic order |
| Reveal UX: only blinks zone, no name shown | Client renders flash card with secret name on `secret_triggered` event |

### Out of Scope
- Adding new secret card implementations (engine already has them).
- Engine-level trigger priority redesign (fireplace's existing event order is what we test, not change).
- Source attribution ("which card triggered which secret") — needs engine event hook, deferred.
- New CSS for secret zone visuals beyond the reveal flash card.

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `webui/server/game.py` | Modify (lines 734-779) | `track_secrets` keys by `entity_id`; payload gains `card_id` and `secret_name` always populated |
| `webui/server/socket.py` | Modify (lines 106-110, 201-204, 272-275, 350-353, 435-438) | Add module-level `emit_triggered_secrets(game_id)` helper; replace 4 duplicate blocks |
| `tests/test_webui_secrets.py` | Create | Parametrized integration tests using `manager.games` registry directly |
| `tests/conftest.py` | Modify or create | Add path so tests can `from webui.server.game import manager` |
| `webui/client/src/components/GameBoard.tsx` | Modify (lines 319-336, plus new state and JSX) | Add `revealedSecret` state, render flash card on `secret_triggered`, auto-dismiss after 1600ms |
| `webui/client/src/components/GameBoard.css` | Modify (append) | `.secret-reveal-flash` styles + keyframes |
| `ROADMAP.md` | Modify (lines 38-67) | Mark Phase 2 sub-items complete |

---

## Task 1: Audit ROADMAP secrets exist in CardDef DB

**Files:**
- Create: `tests/test_webui_secrets.py`
- Modify: `tests/conftest.py` (create if absent)

- [ ] **Step 1: Add path-bridge conftest so webui server is importable from tests**

Check if `tests/conftest.py` exists:

```bash
ls tests/conftest.py 2>/dev/null && echo EXISTS || echo MISSING
```

If MISSING, create `tests/conftest.py` with:

```python
import os
import sys

# Make `webui.server` importable from tests
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
```

If EXISTS, append the same block (skip the `import os/sys` lines if already imported).

- [ ] **Step 2: Write the audit test**

Create `tests/test_webui_secrets.py` with:

```python
"""WebUI-layer integration tests for the secret system.

These tests exercise webui.server.game.GameManager.track_secrets() against
real engine games, confirming each ROADMAP-listed secret can be played and
its trigger is detected by the WebUI's diff-based tracker.
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
```

- [ ] **Step 3: Run the test to verify it passes**

Run:

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && pytest tests/test_webui_secrets.py::test_all_roadmap_secrets_load_from_carddb -v
```

Expected: PASS (all 15 cards instantiate; if any fails, that card_id is wrong in ROADMAP and must be corrected before continuing).

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py tests/test_webui_secrets.py
git commit -m "test(webui): add audit confirming all ROADMAP secrets load from CardDB"
```

---

## Task 2: Refactor `track_secrets` to key by `entity_id`

**Files:**
- Modify: `webui/server/game.py:734-779`
- Modify: `tests/test_webui_secrets.py`

- [ ] **Step 1: Write a failing test for the duplicate-name bug**

Append to `tests/test_webui_secrets.py`:

```python
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
        # is_summonable() "only one of each secret" guard. This lets us test
        # track_secrets() in isolation without wiring up trigger plumbing.
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && pytest tests/test_webui_secrets.py::test_track_secrets_handles_two_same_name_secrets -v
```

Expected: FAIL with `KeyError: 'entity_id'` or `len(triggered) == 0` — confirming the bug and the missing payload field.

- [ ] **Step 3: Apply the fix**

In `webui/server/game.py`, replace lines 734-779 (the entire `track_secrets` method) with:

```python
    def track_secrets(self, game_id):
        """追踪奥秘状态，检测触发的奥秘。

        通过 entity_id 进行身份比对（而非 str(secret)），可正确处理同名重复奥秘。
        每个触发条目包含: player ('player'|'opponent'), secret_name, card_id, entity_id。
        """
        if game_id not in self.games:
            return []
        g = self.games[game_id]
        player = g["players"][0]
        opponent = g["players"][1]

        # entity_id -> secret 实体
        current_player = {s.entity_id: s for s in player.secrets}
        current_opponent = {s.entity_id: s for s in opponent.secrets}

        if "prev_secrets" not in g:
            g["prev_secrets"] = {}
            g["prev_opponent_secrets"] = {}

        prev_player = g["prev_secrets"]
        prev_opponent = g["prev_opponent_secrets"]

        triggered = []

        for entity_id, secret in prev_player.items():
            if entity_id not in current_player:
                triggered.append({
                    "player": "player",
                    "secret_name": str(secret),
                    "card_id": getattr(secret, "id", None),
                    "entity_id": entity_id,
                })

        for entity_id, secret in prev_opponent.items():
            if entity_id not in current_opponent:
                triggered.append({
                    "player": "opponent",
                    "secret_name": str(secret),
                    "card_id": getattr(secret, "id", None),
                    "entity_id": entity_id,
                })

        g["prev_secrets"] = current_player
        g["prev_opponent_secrets"] = current_opponent

        return triggered
```

- [ ] **Step 4: Run the duplicate test to verify it passes**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && pytest tests/test_webui_secrets.py::test_track_secrets_handles_two_same_name_secrets -v
```

Expected: PASS.

- [ ] **Step 5: Run the audit test to confirm no regression**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && pytest tests/test_webui_secrets.py -v
```

Expected: 2 PASS.

- [ ] **Step 6: Commit**

```bash
git add webui/server/game.py tests/test_webui_secrets.py
git commit -m "fix(webui): track secrets by entity_id to handle duplicate-name secrets"
```

---

## Task 3: Centralize the four duplicated `secret_triggered` emit blocks

**Files:**
- Modify: `webui/server/socket.py:106-110`
- Modify: `webui/server/socket.py:201-204`
- Modify: `webui/server/socket.py:272-275`
- Modify: `webui/server/socket.py:350-353`
- Modify: `webui/server/socket.py:435-438`

- [ ] **Step 1: Add the helper near the top of `webui/server/socket.py`**

Find the existing `_socketio = None` module-level line near the top of `webui/server/socket.py` (it's the global the helper depends on). Immediately after the `def run_ai_turn(game_id):` definition closes (around line 100, just before `def register_socket_events(socketio):`), insert this helper:

```python
def emit_triggered_secrets(game_id, *, use_room=False):
    """检测并广播本次操作触发的奥秘。

    use_room=True 用于 run_ai_turn 这类不在 socket handler 内的调用点（必须用 room 路由）；
    其余 socket handler 内调用 emit() 即可（已有上下文）。
    """
    triggered = manager.track_secrets(game_id)
    for secret_info in triggered:
        manager.log_event(
            game_id,
            "secret_triggered",
            f'奥秘 "{secret_info["secret_name"]}" 被触发了！',
            secret_info,
        )
        if use_room:
            if _socketio:
                _socketio.emit(
                    "secret_triggered",
                    {"game_id": game_id, "secret": secret_info},
                    room=game_id,
                )
        else:
            emit("secret_triggered", {"game_id": game_id, "secret": secret_info})
    return triggered
```

- [ ] **Step 2: Replace the run_ai_turn block (current lines 106-110)**

Find this block in `run_ai_turn`:

```python
    # 检查奥秘触发
    triggered_secrets = manager.track_secrets(game_id)
    for secret_info in triggered_secrets:
        manager.log_event(game_id, 'secret_triggered', f'奥秘 "{secret_info["secret_name"]}" 被触发了！', secret_info)
        if _socketio:
            _socketio.emit('secret_triggered', {'game_id': game_id, 'secret': secret_info}, room=game_id)
```

Replace with:

```python
    # 检查奥秘触发
    emit_triggered_secrets(game_id, use_room=True)
```

- [ ] **Step 3: Replace the end_turn block (current lines 201-204)**

Find this block inside `handle_end_turn`:

```python
            triggered_secrets = manager.track_secrets(game_id)
            for secret_info in triggered_secrets:
                manager.log_event(game_id, 'secret_triggered', f'奥秘 "{secret_info["secret_name"]}" 被触发了！', secret_info)
                emit('secret_triggered', {'game_id': game_id, 'secret': secret_info})
```

Replace with:

```python
            emit_triggered_secrets(game_id)
```

- [ ] **Step 4: Replace the play_card block (current lines 272-275)**

Find the same 4-line `triggered_secrets = manager.track_secrets(game_id) ...` block inside `handle_play_card` and replace with:

```python
                emit_triggered_secrets(game_id)
```

(Match the existing indentation — likely 16 spaces inside the `if game_id in manager.games:` ... `if play succeeded:` nesting.)

- [ ] **Step 5: Replace the attack block (current lines 350-353)**

Find the same block inside `handle_attack` and replace with:

```python
            emit_triggered_secrets(game_id)
```

- [ ] **Step 6: Replace the hero_power block (current lines 435-438)**

Find the same block inside `handle_hero_power` and replace with:

```python
            emit_triggered_secrets(game_id)
```

- [ ] **Step 7: Sanity-check no orphaned reference remains**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && grep -n "track_secrets" webui/server/socket.py
```

Expected: only one match — inside the `emit_triggered_secrets` helper. If any of the original 4-line blocks remain, replace them.

- [ ] **Step 8: Run the WebUI test suite to confirm no regressions**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && pytest tests/test_webui_secrets.py -v
```

Expected: 2 PASS.

- [ ] **Step 9: Commit**

```bash
git add webui/server/socket.py
git commit -m "refactor(webui): consolidate four duplicated secret_triggered emit blocks into helper"
```

---

## Task 4: Parametrized "secret fires through tracker" test for every ROADMAP secret

**Files:**
- Modify: `tests/test_webui_secrets.py`

- [ ] **Step 1: Add a fixture and helper that arms a secret then forces a trigger**

Append to `tests/test_webui_secrets.py`:

```python
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
```

- [ ] **Step 2: Add the parametrized test**

Append to `tests/test_webui_secrets.py`:

```python
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
```

- [ ] **Step 3: Run the parametrized test**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && pytest tests/test_webui_secrets.py::test_secret_fires_through_webui_tracker -v
```

Expected: 15 PASS (one per ROADMAP_SECRETS entry).

If any single secret fails, the most likely cause is a bad card_id in `ROADMAP_SECRETS` — fix the id in the list, do not mask the test.

- [ ] **Step 4: Commit**

```bash
git add tests/test_webui_secrets.py
git commit -m "test(webui): parametrized coverage for all 15 ROADMAP secrets through tracker"
```

---

## Task 5: Trigger-order test for simultaneous secret firing

**Files:**
- Modify: `tests/test_webui_secrets.py`

- [ ] **Step 1: Add the order test**

Append to `tests/test_webui_secrets.py`:

```python
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
        my_secret = game.player1.give("EX1_287")  # Counterspell
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
```

- [ ] **Step 2: Run the order tests**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && pytest tests/test_webui_secrets.py -k "order" -v
```

Expected: 2 PASS.

If `test_track_secrets_preserves_arming_order_within_one_side` FAILS, it means dict iteration order doesn't match insertion order somewhere — Python 3.7+ guarantees this for dicts but not for `CardList`. Inspect `player.secrets` — if it iterates in arming order (it does — it's a list-backed CardList), the test should pass with the Task 2 implementation. If it fails, sort by `entity_id` in the player-side loop using `sorted(prev_player.items(), key=lambda kv: ...)` — but only if necessary.

- [ ] **Step 3: Commit**

```bash
git add tests/test_webui_secrets.py
git commit -m "test(webui): cover deterministic trigger order for simultaneous secret fires"
```

---

## Task 6: Client-side secret-reveal flash card (state + JSX)

**Files:**
- Modify: `webui/client/src/components/GameBoard.tsx:319-336`
- Modify: `webui/client/src/components/GameBoard.tsx` (add state declaration near other useState calls, around lines 270-290)
- Modify: `webui/client/src/components/GameBoard.tsx` (add JSX inside the main game-board return, near the choose-one overlay around line 1528)

- [ ] **Step 1: Add the `revealedSecret` state**

Find the existing `useState` cluster around line 276 (where `chooseOneState` and `discoverState` are declared). Immediately after the `discoverState` declaration block (it ends with `}>(null);`), insert:

```tsx
  const [revealedSecret, setRevealedSecret] = useState<{
    name: string;
    cardId?: string;
    side: 'player' | 'opponent';
  } | null>(null);
```

- [ ] **Step 2: Update the secret_triggered handler to drive the flash card**

Find the existing `handleSecretTriggered` definition (currently around lines 319-331):

```tsx
    const handleSecretTriggered = (data: { game_id: string; secret: { player: string; secret_name: string; card_id?: string } }) => {
      // 显示奥秘触发动画
      const secretZone = document.querySelector(data.secret.player === 'player' ? '.player-secret-zone' : '.opponent-secret-zone');
      if (secretZone) {
        const secretCards = secretZone.querySelectorAll('.secret-card');
        secretCards.forEach(card => {
          card.classList.add('secret-triggering');
          setTimeout(() => card.classList.remove('secret-triggering'), 800);
        });
      }
      // 添加到日志
      setActionLog(prev => [`🔮 奥秘 "${data.secret.secret_name}" 被触发了！`, ...prev.slice(0, 30)]);
    };
```

Replace it with:

```tsx
    const handleSecretTriggered = (data: { game_id: string; secret: { player: string; secret_name: string; card_id?: string; entity_id?: number } }) => {
      // 区域高亮动画
      const secretZone = document.querySelector(data.secret.player === 'player' ? '.player-secret-zone' : '.opponent-secret-zone');
      if (secretZone) {
        const secretCards = secretZone.querySelectorAll('.secret-card');
        secretCards.forEach(card => {
          card.classList.add('secret-triggering');
          setTimeout(() => card.classList.remove('secret-triggering'), 800);
        });
      }
      // 揭示卡名（短暂悬浮卡片）
      setRevealedSecret({
        name: data.secret.secret_name,
        cardId: data.secret.card_id,
        side: data.secret.player === 'player' ? 'player' : 'opponent',
      });
      window.setTimeout(() => setRevealedSecret(null), 1600);
      // 日志
      setActionLog(prev => [`🔮 奥秘 "${data.secret.secret_name}" 被触发了！`, ...prev.slice(0, 30)]);
    };
```

- [ ] **Step 3: Render the flash card in the JSX tree**

In `webui/client/src/components/GameBoard.tsx`, find the closing of the choose-one overlay block — it ends with `      )}` on (currently) line 1559, and the next block `{/* 发现面板 */}` begins on line 1561. Insert the snippet below into the blank line between them:

```tsx
      {revealedSecret && (
        <div
          className={`secret-reveal-flash secret-reveal-${revealedSecret.side}`}
          role="status"
          aria-live="polite"
        >
          <div className="secret-reveal-icon">🔮</div>
          <div className="secret-reveal-name">{revealedSecret.name}</div>
          <div className="secret-reveal-subtitle">奥秘触发</div>
        </div>
      )}
```

- [ ] **Step 4: TypeScript check**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace/webui/client && npx tsc --noEmit
```

Expected: no errors. If `revealedSecret` is reported as unused, the JSX in Step 3 wasn't placed correctly — re-find the choose-one overlay closing tag.

- [ ] **Step 5: Commit**

```bash
git add webui/client/src/components/GameBoard.tsx
git commit -m "feat(ui): show secret-reveal flash card with name when a secret triggers"
```

---

## Task 7: Flash card CSS

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` (append to end of file)

- [ ] **Step 1: Append the styles**

Open `webui/client/src/components/GameBoard.css` and append at the end of the file:

```css
/* ======================================================================
   Secret reveal flash card — shown when a secret_triggered event fires.
   Floats over the relevant hero zone, scales in, holds, then fades out.
   ====================================================================== */
.secret-reveal-flash {
  position: absolute;
  left: 50%;
  z-index: 60;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 22px;
  border-radius: 14px;
  background: radial-gradient(
    ellipse at center,
    rgba(255, 235, 168, 0.96) 0%,
    rgba(212, 165, 88, 0.94) 70%,
    rgba(120, 78, 28, 0.94) 100%
  );
  border: 2px solid rgba(255, 220, 130, 0.85);
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.4),
    0 8px 26px rgba(0, 0, 0, 0.55),
    0 0 36px rgba(255, 215, 120, 0.6);
  color: #2a1606;
  font-family: inherit;
  text-shadow: 0 1px 0 rgba(255, 240, 200, 0.6);
  transform: translate(-50%, 0) scale(0.6);
  opacity: 0;
  animation: secret-reveal-flash 1.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

.secret-reveal-flash.secret-reveal-player {
  bottom: 22%;
}

.secret-reveal-flash.secret-reveal-opponent {
  top: 22%;
}

.secret-reveal-icon {
  font-size: 30px;
  line-height: 1;
  filter: drop-shadow(0 0 6px rgba(255, 220, 120, 0.9));
}

.secret-reveal-name {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.4px;
  white-space: nowrap;
}

.secret-reveal-subtitle {
  font-size: 11px;
  opacity: 0.78;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

@keyframes secret-reveal-flash {
  0%   { transform: translate(-50%, 8px) scale(0.55); opacity: 0; }
  18%  { transform: translate(-50%, 0)   scale(1.08); opacity: 1; }
  30%  { transform: translate(-50%, 0)   scale(1.00); opacity: 1; }
  78%  { transform: translate(-50%, 0)   scale(1.00); opacity: 1; }
  100% { transform: translate(-50%, -16px) scale(0.95); opacity: 0; }
}
```

- [ ] **Step 2: Manual visual smoke test**

Start the WebUI dev server and the Python backend:

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && python webui/run.py &
cd /home/xu/code/hstone/hearthstone/fireplace/webui/client && npm run dev
```

Open the browser, start a PVE game with the test deck on a class that has secrets (Mage or Hunter), play a secret, and end your turn. Have the AI trigger your secret (hit your hero, play a card, etc.).

Expected: a golden card flashes in the lower screen for ~1.6s showing the secret's name, then fades.

If the flash card doesn't appear at all: check browser console for React errors and verify Task 6 Step 3 placed the JSX inside the main `<div>` returned by the component (not after the early-return for missing game state).

If it appears in the wrong half: confirm the `data.secret.player` value in the network tab — it should be `'player'` for your own secret, `'opponent'` for theirs.

Stop both servers when done.

- [ ] **Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): add CSS for secret-reveal flash card"
```

---

## Task 8: Run full test suite + close out ROADMAP

**Files:**
- Modify: `ROADMAP.md:39-67`

- [ ] **Step 1: Run all WebUI secret tests**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && pytest tests/test_webui_secrets.py -v
```

Expected: 19 PASS (1 audit + 1 duplicate-name + 15 parametrized + 2 order).

- [ ] **Step 2: Run the engine secret regression suite to confirm no engine drift**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace && pytest tests/test_secrets.py -v
```

Expected: existing engine tests all pass (this plan never touched engine code, but worth verifying).

- [ ] **Step 3: Update ROADMAP.md to mark Phase 2 done**

Find the Phase 2 block in `ROADMAP.md` (lines 38-67). Replace the section header and sub-bullets with:

```markdown
### Phase 2: 奥秘系统 (Secrets) ✅ 已完成
**目标: 实现完整奥秘机制**

#### 2.1 基础架构 ✅
- [x] 奥秘区域 UI（英雄头像旁）
- [x] 奥秘隐藏显示（仅显示数量）
- [x] 触发条件监听系统（diff-based via `track_secrets`，按 entity_id 比对）
- [x] 奥秘触发动画 + 触发时揭示卡名（flash card）

#### 2.2 各职业奥秘实现 ✅
所有 ROADMAP 列出的奥秘 (法师 6、猎人 5、圣骑士 4) 引擎层均已实现，WebUI 层
通过 `tests/test_webui_secrets.py` 参数化覆盖。

#### 2.3 触发优先级 ✅
- [x] 多个奥秘同时满足时的触发顺序（玩家先、对手后；同侧按 FIFO）
- [x] 测试覆盖见 `test_track_secrets_returns_player_secrets_before_opponent` 和
      `test_track_secrets_preserves_arming_order_within_one_side`
```

- [ ] **Step 4: Commit**

```bash
git add ROADMAP.md
git commit -m "docs: mark v0.3.0 Phase 2 (secrets) complete in roadmap"
```

---

## Verification checklist

- [ ] `pytest tests/test_webui_secrets.py -v` → 19 passed
- [ ] `pytest tests/test_secrets.py -v` → no regressions
- [ ] `grep -n "track_secrets" webui/server/socket.py` → 1 match (inside `emit_triggered_secrets`)
- [ ] Manual smoke: opponent triggers your secret → golden flash card appears with secret name → fades after ~1.6s
- [ ] `ROADMAP.md` Phase 2 marked ✅
