import { socketService } from './socket';

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
    hand: string[];
    field: { name: string; atk: number; health: number }[];
    can_end_turn: boolean;
  };
  opponent: {
    hero: string;
    health: number;
    deck: number;
    hand_count: number;
    field: { name: string; atk: number; health: number }[];
  };
};

class GameService {
  private gameId: string | null = null;

  createGame(mode: string, playerClass: string = 'random') {
    socketService.connect();
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
    socketService.on('game_state', (data) => {
      const gameData = data as { game_id: string; state: GameState };
      this.setGameId(gameData.game_id);
      callback(gameData);
    });
  }

  onError(callback: (data: { message: string }) => void) {
    socketService.on('error', callback);
  }

  cleanup() {
    socketService.disconnect();
    this.gameId = null;
  }
}

export const gameService = new GameService();
