from flask_socketio import emit, join_room
from hearthstone.enums import CardType
from .game import manager
import random
import time
import threading
from datetime import datetime

# 全局 socketio 实例
_socketio = None


def run_ai_turn(game_id):
    """执行 AI 回合"""
    global _socketio
    from flask_socketio import emit

    if game_id not in manager.games:
        print(f"[AI] Game {game_id} not found")
        return

    hand_snap = take_hand_snapshot(game_id)

    g = manager.games[game_id]
    game = g["game"]
    ai_player = g["players"][1]  # AI 是第二个玩家

    # 如果当前不是 AI 回合，直接返回
    if game.current_player != ai_player:
        print(f"[AI] Not AI turn, current: {game.current_player}")
        return

    print(f"[AI] Starting turn for {ai_player}")

    # 处理选择
    while ai_player.choice:
        choice = random.choice(ai_player.choice.cards)
        ai_player.choice.choose(choice)

    # 使用英雄技能
    heropower = ai_player.hero.power
    if heropower.is_usable() and random.random() < 0.3:
        target = None
        choose = None
        if heropower.requires_target():
            if heropower.targets:
                target = random.choice(list(heropower.targets))
        if heropower.must_choose_one:
            choose = random.choice(heropower.choose_cards)
        try:
            heropower.use(target=target, choose=choose)
            print(f"[AI] Used hero power")
        except Exception as e:
            print(f"[AI] Hero power failed: {e}")
            pass

    # 打牌
    playable_cards = [c for c in ai_player.hand if c.is_playable()]
    random.shuffle(playable_cards)
    for card in playable_cards[:3]:
        if not card.is_playable():
            continue

        target = None
        choose = None
        if card.requires_target():
            if card.targets:
                target = random.choice(list(card.targets))
        if card.must_choose_one:
            choose = random.choice(card.choose_cards)

        try:
            card.play(target=target, choose=choose)
            print(f"[AI] Played card: {card}")
        except Exception as e:
            print(f"[AI] Card play failed: {e}")
            pass

        # 处理选择
        while ai_player.choice:
            choice = random.choice(ai_player.choice.cards)
            ai_player.choice.choose(choice)

    # 攻击
    attackers = [c for c in ai_player.characters if c.can_attack()]
    random.shuffle(attackers)
    for attacker in attackers[:3]:
        if not attacker.can_attack():
            continue
        targets = list(attacker.targets)
        if targets:
            target = random.choice(targets)
            try:
                attacker.attack(target)
                print(f"[AI] Attacked with {attacker} -> {target}")
            except Exception as e:
                print(f"[AI] Attack failed: {e}")
                pass

    # 结束 AI 回合
    game.end_turn()
    print(f"[AI] Turn ended, current player: {game.current_player}")

    # 更新回合开始时间（玩家回合开始）
    manager.on_turn_start(game_id)

    # Schedule timeout check for human player's turn
    if game.current_player == g["players"][0]:
        schedule_timeout_check(game_id)

    # 发送最终游戏状态
    state = manager.get_game_state(game_id)

    # 检查奥秘触发
    emit_triggered_secrets(game_id, use_room=True)
    emit_fatigue_events(game_id, use_room=True)

    # 检测烧牌
    for burn in check_overdraw(game_id, hand_snap):
        manager.log_event(game_id, 'card_burned', burn['message'], burn)
        if _socketio:
            _socketio.emit('card_burned', {'game_id': game_id, 'burn': burn}, room=game_id)

    print(f"[AI] Sending state, current_player in state: {state.get('current_player')}")
    if _socketio:
        _socketio.emit('game_state', {'game_id': game_id, 'state': state}, room=game_id)
        print(f"[AI] State emitted to room {game_id}")
    else:
        print(f"[AI] Warning: _socketio not initialized")


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


def emit_fatigue_events(game_id, *, use_room=False):
    """检测并广播疲劳伤害事件"""
    events = manager.track_fatigue(game_id)
    for evt in events:
        manager.log_event(game_id, 'fatigue', evt['message'], evt)
        payload = {'game_id': game_id, 'fatigue': evt}
        if use_room:
            if _socketio:
                _socketio.emit('fatigue_damage', payload, room=game_id)
        else:
            emit('fatigue_damage', payload)
    return events


def take_hand_snapshot(game_id):
    """拍摄手牌/牌库快照，用于检测烧牌"""
    if game_id not in manager.games:
        return None
    g = manager.games[game_id]
    p = g["players"][0]
    return {"hand": len(p.hand), "deck": len(p.deck), "max_hand": p.max_hand_size}


def check_overdraw(game_id, snapshot):
    """对比快照检测烧牌事件"""
    if not snapshot or game_id not in manager.games:
        return []
    g = manager.games[game_id]
    p = g["players"][0]
    cur_deck = len(p.deck)
    cur_hand = len(p.hand)
    burned = []
    if snapshot["deck"] > cur_deck and cur_hand >= snapshot["max_hand"]:
        deck_diff = snapshot["deck"] - cur_deck
        for _ in range(deck_diff):
            burned.append({"player": "player", "message": "手牌已满，一张牌被烧毁了！"})
    return burned


def take_hand_cards_snapshot(game_id):
    """快照手牌卡牌，用于检测弃牌"""
    if game_id not in manager.games:
        return None
    g = manager.games[game_id]
    p = g["players"][0]
    return [(id(c), str(c), getattr(c, 'id', None)) for c in p.hand]


def check_discard(game_id, snapshot):
    """对比快照检测弃牌事件（术士弃牌机制）"""
    if not snapshot or game_id not in manager.games:
        return []
    g = manager.games[game_id]
    p = g["players"][0]
    current_ids = {id(c) for c in p.hand}
    discarded = []
    for obj_id, card_name, card_data_id in snapshot:
        if obj_id not in current_ids:
            discarded.append({
                "_obj_id": obj_id,
                "player": "player",
                "card_name": card_name,
                "card_id": card_data_id,
                "message": f"弃置了 {card_name}",
            })
    return discarded


def schedule_timeout_check(game_id):
    """启动后台线程，在回合超时后自动结束回合"""
    if game_id not in manager.games:
        return
    g = manager.games[game_id]
    timeout = g.get("turn_timeout", 75)

    def _timeout_worker():
        turn_start = g.get("turn_start_time")
        if not turn_start:
            return
        elapsed = (datetime.now() - turn_start).total_seconds()
        remaining = timeout - elapsed
        if remaining > 0:
            time.sleep(remaining + 0.5)

        # Re-check after sleep
        if game_id not in manager.games:
            return
        if not manager.check_turn_timeout(game_id):
            return

        g2 = manager.games[game_id]
        game = g2["game"]
        player = g2["players"][0]

        # Only auto-end if it's still the human player's turn
        if game.current_player != player:
            return

        manager.log_event(game_id, 'auto_end_turn', '回合超时，自动结束回合', {'turn': game.turn})

        hand_snap = take_hand_snapshot(game_id)
        game.end_turn()
        manager.on_turn_start(game_id)

        state = manager.get_game_state(game_id)
        emit_triggered_secrets(game_id, use_room=True)
        emit_fatigue_events(game_id, use_room=True)

        # 检测烧牌
        for burn in check_overdraw(game_id, hand_snap):
            manager.log_event(game_id, 'card_burned', burn['message'], burn)
            if _socketio:
                _socketio.emit('card_burned', {'game_id': game_id, 'burn': burn}, room=game_id)

        if _socketio:
            _socketio.emit('game_state', {'game_id': game_id, 'state': state}, room=game_id)

        # If PVE and now AI's turn, run AI
        if g2["mode"] == "pve" and game.current_player == g2["players"][1]:
            ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
            ai_thread.daemon = True
            ai_thread.start()

    t = threading.Thread(target=_timeout_worker)
    t.daemon = True
    t.start()


def register_socket_events(socketio):
    global _socketio
    _socketio = socketio

    @socketio.on('connect')
    def handle_connect():
        emit('connected', {'status': 'connected'})

    @socketio.on('disconnect')
    def handle_disconnect():
        pass

    @socketio.on('rejoin_game')
    def handle_rejoin_game(data):
        """处理重连后重新加入游戏房间"""
        game_id = data.get('game_id')
        print(f"[Server] Rejoin request for game: {game_id}")

        if game_id and game_id in manager.games:
            join_room(game_id)
            state = manager.get_game_state(game_id)
            print(f"[Server] Rejoin successful, sending state. Current player: {state.get('current_player')}")
            emit('game_state', {'game_id': game_id, 'state': state})
        else:
            print(f"[Server] Rejoin failed: game not found")
            emit('error', {'message': 'Game not found'})

    @socketio.on('create_game')
    def handle_create_game(data):
        mode = data.get('mode', 'pve')
        test_deck = data.get('test_deck', False)

        # Accept new-format player/opponent DeckSpec or fall back to legacy player_class
        if 'player' in data and 'opponent' in data:
            p1_spec = data['player']
            p2_spec = data['opponent']
        else:
            # Legacy payload (test fixtures may still use this)
            player_class = data.get('player_class', 'random')
            p1_spec = {'type': 'random', 'card_class': player_class.upper() if player_class != 'random' else 'ANY'}
            p2_spec = {'type': 'random', 'card_class': 'ANY'}

        try:
            game_id = manager.create_game(
                mode=mode,
                p1_spec=p1_spec,
                p2_spec=p2_spec,
                test_deck=test_deck,
            )
        except Exception as e:
            print(f"[create_game] failed: {e}")
            emit('create_game_error', {'error': str(e)})
            return

        join_room(game_id)

        if mode == "pve":
            g = manager.games[game_id]
            game = g["game"]
            if game.current_player == g["players"][1]:
                import threading
                ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
                ai_thread.daemon = True
                ai_thread.start()

        g = manager.games[game_id]
        game = g["game"]
        if game.current_player == g["players"][0]:
            schedule_timeout_check(game_id)

        state = manager.get_game_state(game_id)
        emit('game_state', {'game_id': game_id, 'state': state})

    @socketio.on('end_turn')
    def handle_end_turn(data):
        game_id = data.get('game_id')
        if game_id in manager.games:
            g = manager.games[game_id]
            game = g["game"]
            player = g["players"][0]

            # 记录结束回合日志
            manager.log_event(game_id, 'end_turn', f'{player} 结束了回合', {
                'player': str(player),
                'turn': game.turn
            })

            hand_snap = take_hand_snapshot(game_id)
            game.end_turn()
            print(f"[Server] Player ended turn, now is {game.current_player}")

            # 更新回合开始时间
            manager.on_turn_start(game_id)

            # Schedule timeout check for human player's turn
            if game.current_player == g["players"][0]:
                schedule_timeout_check(game_id)

            # 如果是 PVE 模式，执行 AI 回合
            if g["mode"] == "pve":
                # 在后台线程执行 AI
                import threading
                ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
                ai_thread.daemon = True
                ai_thread.start()
                print(f"[Server] AI thread started")

            # 发送切换到AI回合的状态
            state = manager.get_game_state(game_id)

            # 检查奥秘触发
            emit_triggered_secrets(game_id)
            emit_fatigue_events(game_id)

            # 检测烧牌
            for burn in check_overdraw(game_id, hand_snap):
                manager.log_event(game_id, 'card_burned', burn['message'], burn)
                emit('card_burned', {'game_id': game_id, 'burn': burn})

            emit('game_state', {'game_id': game_id, 'state': state})

    @socketio.on('play_card')
    def handle_play_card(data):
        game_id = data.get('game_id')
        card_index = data.get('card_index')
        target_id = data.get('target_id')
        choose_card_id = data.get('choose_card_id')

        g = manager.games[game_id]
        player = g["players"][0]

        if 0 <= card_index < len(player.hand):
            card = player.hand[card_index]

            # 检查卡牌是否可打
            if not card.is_playable():
                emit('error', {'message': f'{card} is not playable yet'})
                return

            target = None
            if target_id and card.requires_target():
                target = manager.get_target_by_id(game_id, target_id)

            # 处理 Choose One 抉择
            choose = None
            if choose_card_id and hasattr(card, 'must_choose_one') and card.must_choose_one:
                # 查找对应的抉择卡牌
                for choose_card in card.choose_cards:
                    if getattr(choose_card, 'id', str(choose_card)) == choose_card_id:
                        choose = choose_card
                        break

            try:
                # 记录出牌日志
                target_name = str(target) if target else None
                manager.log_event(game_id, 'play_card', f'{player} 打出了 {card}', {
                    'player': str(player),
                    'card': str(card),
                    'card_id': card.id if hasattr(card, 'id') else None,
                    'target': target_name,
                    'cost': card.cost
                })

                # 检查是否为奥秘
                is_secret = hasattr(card, 'data') and hasattr(card.data, 'secret') and card.data.secret

                opponent = player.opponent
                silenced_before = {id(m): getattr(m, 'silenced', False) for m in list(player.field) + list(opponent.field)}

                hand_snap = take_hand_snapshot(game_id)
                hand_cards_snap = take_hand_cards_snapshot(game_id)
                played_card_obj_id = id(card)
                is_hero_card = (
                    getattr(card, 'type', None) == CardType.HERO
                    and (getattr(getattr(card, 'data', None), 'armor', 0) or 0) > 0
                )
                old_hero_name = str(player.hero) if is_hero_card else None
                old_hero_id = getattr(player.hero, 'id', None) if is_hero_card else None
                hero_card_id = getattr(card, 'id', None) if is_hero_card else None
                hero_info = None
                card.play(target=target, choose=choose)

                if is_hero_card:
                    hero_info = {
                        'player': str(player),
                        'old_hero': old_hero_name,
                        'old_hero_id': old_hero_id,
                        'new_hero': str(player.hero),
                        'new_hero_id': getattr(player.hero, 'id', None),
                        'card_id': hero_card_id,
                        'hero_power': str(player.hero.power),
                        'hero_power_id': getattr(player.hero.power, 'id', None),
                        'armor': getattr(player.hero, 'armor', 0),
                    }
                    manager.log_event(
                        game_id,
                        'hero_transformed',
                        f'{player} 变身为 {player.hero}',
                        hero_info,
                    )

                # 检测沉默事件
                for m in list(player.field) + list(opponent.field):
                    if not silenced_before.get(id(m), False) and getattr(m, 'silenced', False):
                        manager.log_event(game_id, 'silence', f'{m} 被沉默了', {'minion': str(m), 'card_id': getattr(m, 'id', None)})

                # 记录战吼效果（如果有）
                if hasattr(card, 'has_battlecry') and card.has_battlecry:
                    manager.log_event(game_id, 'battlecry', f'{card} 的战吼效果触发', {
                        'card': str(card)
                    })

                # 记录奥秘使用效果
                if is_secret:
                    manager.log_event(game_id, 'secret_played', f'{player} 使用了奥秘 {card}', {
                        'player': str(player),
                        'card': str(card),
                        'card_id': card.id if hasattr(card, 'id') else None
                    })

                state = manager.get_game_state(game_id)

                # 检查奥秘触发
                emit_triggered_secrets(game_id)
                emit_fatigue_events(game_id)

                # 检测烧牌
                for burn in check_overdraw(game_id, hand_snap):
                    manager.log_event(game_id, 'card_burned', burn['message'], burn)
                    emit('card_burned', {'game_id': game_id, 'burn': burn})

                # 检测弃牌（术士机制）
                for d in check_discard(game_id, hand_cards_snap):
                    if d["_obj_id"] == played_card_obj_id:
                        continue  # skip the played card itself
                    manager.log_event(game_id, 'discard', d['message'], {'card_name': d['card_name'], 'card_id': d['card_id']})
                    emit('discard', {'game_id': game_id, 'discard': {'player': d['player'], 'card_name': d['card_name'], 'card_id': d['card_id'], 'message': d['message']}})

                emit('game_state', {'game_id': game_id, 'state': state})
                if hero_info:
                    emit('hero_transformed', {'game_id': game_id, 'hero': hero_info})

                # 如果是 PVE 模式且玩家打完牌后是 AI 回合，执行 AI
                if g["mode"] == "pve":
                    game = g["game"]
                    if game.current_player == g["players"][1]:
                        import threading
                        ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
                        ai_thread.daemon = True
                        ai_thread.start()

            except Exception as e:
                emit('error', {'message': str(e)})

    @socketio.on('use_hero_power')
    def handle_use_hero_power(data):
        """使用英雄技能"""
        game_id = data.get('game_id')
        target_id = data.get('target_id')
        choose_card_id = data.get('choose_card_id')

        if game_id not in manager.games:
            emit('error', {'message': 'Game not found'})
            return

        g = manager.games[game_id]
        player = g["players"][0]
        game = g["game"]

        # 检查是否是玩家回合
        if game.current_player != player:
            emit('error', {'message': 'Not your turn'})
            return

        heropower = player.hero.power

        # 检查技能是否可用
        if not heropower.is_usable():
            emit('error', {'message': 'Hero power is not usable'})
            return

        choose = None
        if getattr(heropower, 'must_choose_one', False):
            if choose_card_id:
                for choose_card in heropower.choose_cards:
                    if getattr(choose_card, 'id', str(choose_card)) == choose_card_id:
                        choose = choose_card
                        break
            if choose is None:
                emit('error', {'message': 'Invalid hero power choice'})
                return

        target = None
        target_source = choose if choose is not None and hasattr(choose, 'requires_target') else heropower
        requires_target = target_source.requires_target() if hasattr(target_source, 'requires_target') else False
        print(f"[Server] Hero power requires_target: {requires_target}, target_id: {target_id}")
        if requires_target:
            if target_id:
                target = manager.get_target_by_id(game_id, target_id)
                print(f"[Server] Resolved target: {target}")
            if not target:
                emit('error', {'message': 'Valid target required'})
                return
            if hasattr(target_source, 'targets') and target_source.targets and target not in target_source.targets:
                emit('error', {'message': 'Valid target required'})
                return

        try:
            # 记录英雄技能使用
            target_name = str(target) if target else None
            manager.log_event(game_id, 'hero_power', f'{player} 使用了英雄技能 {heropower}', {
                'player': str(player),
                'hero_power': str(heropower),
                'target': target_name,
                'cost': heropower.cost
            })

            heropower.use(target=target, choose=choose)
            print(f"[Server] Hero power used: {heropower} -> {target}")

            # 记录技能效果
            if target and hasattr(target, 'health'):
                manager.log_event(game_id, 'hero_power_effect', f'{heropower} 对 {target} 生效', {
                    'target': str(target),
                    'target_health': target.health
                })

            state = manager.get_game_state(game_id)

            # 检查奥秘触发
            emit_triggered_secrets(game_id)
            emit_fatigue_events(game_id)

            emit('game_state', {'game_id': game_id, 'state': state})

            # 如果是 PVE 模式且玩家使用技能后是 AI 回合，执行 AI
            if g["mode"] == "pve":
                if game.current_player == g["players"][1]:
                    import threading
                    ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
                    ai_thread.daemon = True
                    ai_thread.start()

        except Exception as e:
            emit('error', {'message': str(e)})

    @socketio.on('make_choice')
    def handle_make_choice(data):
        """Resolve the current engine choice by index and send updated state."""
        try:
            import traceback

            if not isinstance(data, dict):
                emit('error', {'message': 'Invalid request'})
                return

            game_id = data.get('game_id')
            card_index = data.get('card_index')

            if game_id not in manager.games:
                emit('error', {'message': 'Game not found'})
                return

            g = manager.games[game_id]
            player = g["players"][0]

            if not player.choice:
                emit('error', {'message': 'No active choice'})
                return

            if (
                isinstance(card_index, bool)
                or not isinstance(card_index, int)
                or card_index < 0
                or card_index >= len(player.choice.cards)
            ):
                emit('error', {'message': 'Invalid choice index'})
                return

            chosen = player.choice.cards[card_index]
            manager.log_event(game_id, 'choice', f'{player} 选择了 {chosen}', {
                'player': str(player),
                'choice': str(chosen),
                'card_id': getattr(chosen, 'id', None),
            })
            player.choice.choose(chosen)

            state = manager.get_game_state(game_id)
            emit('game_state', {'game_id': game_id, 'state': state})
        except Exception as e:
            print(f"[Server] make_choice failed: {e}")
            traceback.print_exc()
            emit('error', {'message': str(e)})

    @socketio.on('attack')
    def handle_attack(data):
        game_id = data.get('game_id')
        attacker_index = data.get('attacker_index')
        target_id = data.get('target_id')

        g = manager.games[game_id]
        player = g["players"][0]

        # Frontend sends field index directly (0, 1, 2, ...)
        attacker = player.field[attacker_index]
        opponent = player.opponent

        if target_id == "hero" or target_id == "opponent_hero":
            target = opponent.hero
        elif target_id.startswith("enemy_minion-"):
            # Frontend sends "enemy_minion-0", "enemy_minion-1", etc.
            minion_index = int(target_id.split("-")[1])
            target = opponent.field[minion_index]
        elif target_id.startswith("minion-"):
            # Legacy format - should be enemy minions
            minion_index = int(target_id.split("-")[1])
            target = opponent.field[minion_index]
        else:
            # Legacy format
            target = opponent.field[int(target_id)]

        try:
            # 记录攻击前状态
            target_health_before = target.health
            attacker_atk = attacker.atk

            # 记录攻击日志
            manager.log_event(game_id, 'attack', f'{attacker} 攻击了 {target}', {
                'attacker': str(attacker),
                'attacker_atk': attacker_atk,
                'target': str(target),
                'target_health_before': target_health_before
            })

            attacker.attack(target)

            # 记录攻击结果
            damage_dealt = min(attacker_atk, target_health_before)
            target_died = target.health <= 0 if hasattr(target, 'health') else False

            if target_died:
                manager.log_event(game_id, 'minion_died', f'{target} 被消灭了！', {
                    'minion': str(target),
                    'killed_by': str(attacker)
                })
            else:
                manager.log_event(game_id, 'damage', f'{target} 受到了 {damage_dealt} 点伤害', {
                    'target': str(target),
                    'damage': damage_dealt,
                    'health_remaining': target.health if hasattr(target, 'health') else None
                })

            # 检查攻击者是否死亡（反击伤害）
            if hasattr(attacker, 'health') and attacker.health <= 0:
                manager.log_event(game_id, 'minion_died', f'{attacker} 在战斗中死亡！', {
                    'minion': str(attacker)
                })

            state = manager.get_game_state(game_id)

            # 检查奥秘触发
            emit_triggered_secrets(game_id)
            emit_fatigue_events(game_id)

            emit('game_state', {'game_id': game_id, 'state': state})

            # 如果是 PVE 模式且玩家攻击后是 AI 回合，执行 AI
            if g["mode"] == "pve":
                game = g["game"]
                if game.current_player == g["players"][1]:
                    import threading
                    ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
                    ai_thread.daemon = True
                    ai_thread.start()

        except Exception as e:
            emit('error', {'message': str(e)})

    @socketio.on('use_titan_ability')
    def handle_use_titan_ability(data):
        """使用泰坦技能"""
        game_id = data.get('game_id')
        minion_index = data.get('minion_index')
        ability_index = data.get('ability_index')
        target_id = data.get('target_id')

        if game_id not in manager.games:
            emit('error', {'message': 'Game not found'})
            return

        g = manager.games[game_id]
        player = g["players"][0]
        game = g["game"]

        if game.current_player != player:
            emit('error', {'message': 'Not your turn'})
            return

        if minion_index is None or minion_index < 0 or minion_index >= len(player.field):
            emit('error', {'message': 'Invalid minion index'})
            return

        minion = player.field[minion_index]

        if not getattr(minion, 'titan_abilities', None):
            emit('error', {'message': 'Minion is not a Titan'})
            return

        target = None
        if target_id:
            target = manager.get_target_by_id(game_id, target_id)

        try:
            manager.log_event(game_id, 'titan_ability', f'{minion} 使用了泰坦技能 #{ability_index}', {
                'minion': str(minion),
                'ability_index': ability_index,
                'target': str(target) if target else None,
            })

            minion.use_titan_ability(ability_index, target=target)

            state = manager.get_game_state(game_id)
            emit('game_state', {'game_id': game_id, 'state': state})

        except Exception as e:
            emit('error', {'message': str(e)})

    @socketio.on('weapon_attack')
    def handle_weapon_attack(data):
        """使用武器攻击目标"""
        game_id = data.get('game_id')
        target_id = data.get('target_id')

        if game_id not in manager.games:
            emit('error', {'message': 'Game not found'})
            return

        g = manager.games[game_id]
        player = g["players"][0]
        game = g["game"]

        # 检查是否是玩家回合
        if game.current_player != player:
            emit('error', {'message': 'Not your turn'})
            return

        # 检查是否有武器
        weapon = player.hero.weapon
        if not weapon:
            emit('error', {'message': 'No weapon equipped'})
            return

        # 检查武器是否可以攻击
        if not player.hero.can_attack():
            emit('error', {'message': 'Cannot attack with weapon'})
            return

        opponent = player.opponent

        # 解析目标
        if target_id == "hero":
            target = opponent.hero
        elif target_id == "opponent_hero":
            target = opponent.hero
        elif target_id.startswith("minion-"):
            minion_index = int(target_id.split("-")[1])
            target = opponent.field[minion_index]
        elif target_id.startswith("enemy_minion-"):
            minion_index = int(target_id.split("-")[1])
            target = opponent.field[minion_index]
        else:
            emit('error', {'message': f'Invalid target: {target_id}'})
            return

        try:
            # 记录攻击前状态
            target_health_before = target.health if hasattr(target, 'health') else 0
            weapon_atk = weapon.atk
            weapon_durability_before = weapon.durability

            # 记录武器攻击日志
            manager.log_event(game_id, 'weapon_attack', f'{player} 使用 {weapon} 攻击了 {target}', {
                'player': str(player),
                'weapon': str(weapon),
                'weapon_atk': weapon_atk,
                'target': str(target),
                'target_health_before': target_health_before
            })

            # 执行攻击
            player.hero.attack(target)

            # 记录攻击结果
            damage_dealt = min(weapon_atk, target_health_before)
            target_died = hasattr(target, 'health') and target.health <= 0

            if target_died:
                manager.log_event(game_id, 'minion_died', f'{target} 被消灭了！', {
                    'minion': str(target),
                    'killed_by': str(weapon)
                })
            else:
                manager.log_event(game_id, 'damage', f'{target} 受到了 {damage_dealt} 点伤害', {
                    'target': str(target),
                    'damage': damage_dealt,
                    'health_remaining': target.health if hasattr(target, 'health') else None
                })

            # 检查武器是否破损
            if not player.hero.weapon or player.hero.weapon.durability <= 0:
                manager.log_event(game_id, 'weapon_broken', f'{weapon} 破损了！', {
                    'weapon': str(weapon)
                })

            state = manager.get_game_state(game_id)
            emit('game_state', {'game_id': game_id, 'state': state})

            # 如果是 PVE 模式且玩家攻击后是 AI 回合，执行 AI
            if g["mode"] == "pve":
                if game.current_player == g["players"][1]:
                    import threading
                    ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
                    ai_thread.daemon = True
                    ai_thread.start()

        except Exception as e:
            emit('error', {'message': str(e)})
