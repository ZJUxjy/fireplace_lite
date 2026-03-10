import { socketService } from './socket';

export type CardData = {
  name: string;
  cost: number;
  atk?: number;
  health?: number;
  text?: string;
  race?: string;
  mechanics?: string[];
};

export type MinionData = {
  name: string;
  atk: number;
  health: number;
  can_attack?: boolean;
  taunt?: boolean;
};

export type GameState = {
  turn: number;
  current_player: string;
  player: {
    hero: string;
    health: number;
    max_health: number;
    mana: number;
    max_mana: number;
    deck: number;
    hand: CardData[];
    field: MinionData[];
    can_end_turn: boolean;
  };
  opponent: {
    hero: string;
    health: number;
    deck: number;
    hand_count: number;
    field: MinionData[];
    has_taunt?: boolean;
  };
};

class GameService {
  private gameId: string | null = null;
  private gameStateCallback: ((data: { game_id: string; state: GameState }) => void) | null = null;

  createGame(mode: string, playerClass: string = 'random') {
    socketService.connect();
    // 设置重连后重新加入房间的逻辑
    socketService.onReconnect(() => {
      if (this.gameId) {
        console.log('[GameService] Reconnected, rejoining game:', this.gameId);
        socketService.emit('rejoin_game', { game_id: this.gameId });
      }
    });
    socketService.emit('create_game', { mode, player_class: playerClass });
  }

  endTurn() {
    if (this.gameId) {
      socketService.emit('end_turn', { game_id: this.gameId });
    }
  }

  playCard(cardIndex: number, targetId?: string) {
    if (this.gameId) {
      socketService.emit('play_card', {
        game_id: this.gameId,
        card_index: cardIndex,
        target_id: targetId
      });
    }
  }

  attack(attackerIndex: number, targetId: string) {
    if (this.gameId) {
      socketService.emit('attack', {
        game_id: this.gameId,
        attacker_index: attackerIndex,
        target_id: targetId
      });
    }
  }

  setGameId(id: string) {
    this.gameId = id;
  }

  getGameId(): string | null {
    return this.gameId;
  }

  onGameState(callback: (data: { game_id: string; state: GameState }) => void) {
    this.gameStateCallback = callback;
    socketService.on('game_state', (data) => {
      console.log('[GameService] Raw game_state data:', data);
      const gameData = data as { game_id?: string; state: GameState };
      // 如果没有 game_id，使用已保存的 gameId
      if (!gameData.game_id) {
        console.log('[GameService] No game_id in data, using saved:', this.gameId);
        gameData.game_id = this.gameId || '';
      } else {
        this.setGameId(gameData.game_id);
      }
      callback(gameData as { game_id: string; state: GameState });
    });
  }

  onError(callback: (data: { message: string }) => void) {
    socketService.on('error', callback);
  }

  cleanup() {
    socketService.disconnect();
    this.gameId = null;
    this.gameStateCallback = null;
  }
}

export const gameService = new GameService();
