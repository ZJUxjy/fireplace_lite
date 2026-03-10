from flask_socketio import emit, join_room
from .game import manager


def register_socket_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        emit('connected', {'status': 'connected'})

    @socketio.on('disconnect')
    def handle_disconnect():
        pass

    @socketio.on('create_game')
    def handle_create_game(data):
        mode = data.get('mode', 'pve')
        player_class = data.get('player_class', 'random')
        game_id = manager.create_game(player_class, mode=mode)
        join_room(game_id)
        state = manager.get_game_state(game_id)
        emit('game_state', {'game_id': game_id, 'state': state})

    @socketio.on('end_turn')
    def handle_end_turn(data):
        game_id = data.get('game_id')
        if game_id in manager.games:
            g = manager.games[game_id]
            g["game"].end_turn()
            state = manager.get_game_state(game_id)
            emit('game_state', {'state': state}, room=game_id)

    @socketio.on('play_card')
    def handle_play_card(data):
        game_id = data.get('game_id')
        card_index = data.get('card_index')
        target_id = data.get('target_id')

        g = manager.games[game_id]
        player = g["players"][0]

        if 0 <= card_index < len(player.hand):
            card = player.hand[card_index]
            target = None
            if target_id and card.requires_target():
                # 简化处理
                targets = list(card.targets)
                if targets:
                    target = targets[0] if target_id == "hero" else targets[int(target_id) - 1]

            try:
                card.play(target=target)
                state = manager.get_game_state(game_id)
                emit('game_state', {'state': state}, room=game_id)
            except Exception as e:
                emit('error', {'message': str(e)})

    @socketio.on('attack')
    def handle_attack(data):
        game_id = data.get('game_id')
        attacker_index = data.get('attacker_index')
        target_id = data.get('target_id')

        g = manager.games[game_id]
        player = g["players"][0]

        attacker = player.hero if attacker_index == 0 else player.field[attacker_index - 1]
        opponent = player.opponent

        target = opponent.hero if target_id == "hero" else opponent.field[int(target_id) - 1]

        try:
            attacker.attack(target)
            state = manager.get_game_state(game_id)
            emit('game_state', {'state': state}, room=game_id)
        except Exception as e:
            emit('error', {'message': str(e)})
