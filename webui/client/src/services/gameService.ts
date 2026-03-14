import { socketService } from './socket';

export type CardData = {
  name: string;
  cost: number;
  is_playable?: boolean;
  atk?: number;
  health?: number;
  text?: string;
  race?: string;
  mechanics?: string[];
  requires_target?: boolean;
  valid_targets?: string[];
  lifesteal?: boolean;
  has_combo?: boolean;
  poisonous?: boolean;
};

export type MinionData = {
  name: string;
  atk: number;
  health: number;
  can_attack?: boolean;
  taunt?: boolean;
  has_deathrattle?: boolean;
  divine_shield?: boolean;
  stealth?: boolean;
  windfury?: boolean;
  frozen?: boolean;
  poisonous?: boolean;
  text?: string;
  race?: string;
  mechanics?: string[];
};

export type WeaponData = {
  name: string;
  atk: number;
  durability: number;
  max_durability: number;
};

export type HeroPowerData = {
  name: string;
  cost: number;
  is_usable: boolean;
  requires_target: boolean;
  description: string;
  valid_targets?: string[];
};

export type LogEntry = {
  timestamp: string;
  type: string;
  message: string;
  details?: Record<string, unknown>;
};

export type GameState = {
  turn: number;
  current_player: string;
  player: {
    hero: string;
    health: number;
    max_health: number;
    armor: number;
    mana: number;
    max_mana: number;
    spell_power: number;
    deck: number;
    hand: CardData[];
    field: MinionData[];
    can_end_turn: boolean;
    hero_power: HeroPowerData;
    weapon: WeaponData | null;
  };
  opponent: {
    hero: string;
    health: number;
    max_health: number;
    armor: number;
    mana: number;
    max_mana: number;
    spell_power: number;
    deck: number;
    hand_count: number;
    field: MinionData[];
    has_taunt?: boolean;
    hero_power: HeroPowerData;
    weapon: WeaponData | null;
  };
  logs: LogEntry[];
};

class GameService {
  private gameId: string | null = null;

  createGame(mode: string, playerClass: string = 'random', testDeck: boolean = false) {
    socketService.connect();
    // 设置重连后重新加入房间的逻辑
    socketService.onReconnect(() => {
      if (this.gameId) {
        console.log('[GameService] Reconnected, rejoining game:', this.gameId);
        socketService.emit('rejoin_game', { game_id: this.gameId });
      }
    });
    socketService.emit('create_game', { mode, player_class: playerClass, test_deck: testDeck });
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

  useHeroPower(targetId?: string) {
    if (this.gameId) {
      socketService.emit('use_hero_power', {
        game_id: this.gameId,
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

  weaponAttack(targetId: string) {
    if (this.gameId) {
      socketService.emit('weapon_attack', {
        game_id: this.gameId,
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
    socketService.on('error', (data) => callback(data as { message: string }));
  }

  cleanup() {
    socketService.disconnect();
    this.gameId = null;
  }
}

export const gameService = new GameService();
