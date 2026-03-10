from flask_socketio import emit, join_room
from .game import manager
import random
import time


def run_ai_turn(game_id):
    """执行 AI 回合"""
    if game_id not in manager.games:
        return

    g = manager.games[game_id]
    game = g["game"]
    ai_player = g["players"][1]  # AI 是第二个玩家

    # 如果当前不是 AI 回合，直接返回
    if game.current_player != ai_player:
        return

    # 延迟一点执行，让玩家看到对手回合开始
    time.sleep(0.5)

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
        except:
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
        except:
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
            except:
                pass

    # 结束 AI 回合
    game.end_turn()


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
            game = g["game"]
            game.end_turn()

            # 如果是 PVE 模式，执行 AI 回合
            if g["mode"] == "pve":
                # 在后台线程执行 AI
                import threading
                ai_thread = threading.Thread(target=run_ai_turn, args=(game_id,))
                ai_thread.daemon = True
                ai_thread.start()

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
                emit('game_state', {'state': state}, room=game_id)

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

        attacker = player.hero if attacker_index == 0 else player.field[attacker_index - 1]
        opponent = player.opponent

        target = opponent.hero if target_id == "hero" else opponent.field[int(target_id) - 1]

        try:
            attacker.attack(target)
            state = manager.get_game_state(game_id)
            emit('game_state', {'state': state}, room=game_id)

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
