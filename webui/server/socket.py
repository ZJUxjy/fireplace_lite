from flask_socketio import emit, join_room
from .game import manager
import random

# 全局 socketio 实例
_socketio = None


def run_ai_turn(game_id):
    """执行 AI 回合"""
    global _socketio
    from flask_socketio import emit

    if game_id not in manager.games:
        print(f"[AI] Game {game_id} not found")
        return

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

    # 发送最终游戏状态
    state = manager.get_game_state(game_id)
    print(f"[AI] Sending state, current_player in state: {state.get('current_player')}")
    if _socketio:
        _socketio.emit('game_state', {'game_id': game_id, 'state': state}, room=game_id)
        print(f"[AI] State emitted to room {game_id}")
    else:
        print(f"[AI] Warning: _socketio not initialized")


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
        player_class = data.get('player_class', 'random')
        game_id = manager.create_game(player_class, mode=mode)
        join_room(game_id)

        # 如果是 PVE 模式且AI先手，立即执行AI回合
        if mode == "pve":
            g = manager.games[game_id]
            game = g["game"]
            if game.current_player == g["players"][1]:
                import threading
                ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
                ai_thread.daemon = True
                ai_thread.start()

        state = manager.get_game_state(game_id)
        emit('game_state', {'game_id': game_id, 'state': state})

    @socketio.on('end_turn')
    def handle_end_turn(data):
        game_id = data.get('game_id')
        if game_id in manager.games:
            g = manager.games[game_id]
            game = g["game"]
            game.end_turn()
            print(f"[Server] Player ended turn, now is {game.current_player}")

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
            emit('game_state', {'game_id': game_id, 'state': state})

    @socketio.on('play_card')
    def handle_play_card(data):
        game_id = data.get('game_id')
        card_index = data.get('card_index')
        target_id = data.get('target_id')

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
                targets = list(card.targets)
                if targets:
                    target = targets[0] if target_id == "hero" else targets[int(target_id) - 1]

            try:
                card.play(target=target)
                state = manager.get_game_state(game_id)
                emit('game_state', {'game_id': game_id, 'state': state})

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

        if target_id == "hero":
            target = opponent.hero
        elif target_id.startswith("minion-"):
            # Frontend sends "minion-0", "minion-1", etc. (direct field index)
            minion_index = int(target_id.split("-")[1])
            target = opponent.field[minion_index]
        else:
            # Legacy format
            target = opponent.field[int(target_id)]

        try:
            attacker.attack(target)
            state = manager.get_game_state(game_id)
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
