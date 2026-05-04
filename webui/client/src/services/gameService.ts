import { socketService } from './socket';

export type CardData = {
  id?: string;
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
  must_choose_one?: boolean;
  choose_cards?: CardData[];
  type?: string;
  base_damage?: number;
  is_damage_spell?: boolean;
  is_hero_card?: boolean;
  summon_as_minion?: boolean;
  is_tradeable?: boolean;
  is_miniaturize?: boolean;
  has_quickdraw?: boolean;
  quickdraw_active?: boolean;
  has_outcast?: boolean;
  has_corrupt?: boolean;
  has_infuse?: boolean;
  infuse_progress?: number;
  infuse_threshold?: number;
};

export type TitanAbilityData = {
  index: number;
  name: string;
  text?: string;
  is_used: boolean;
  requires_target: boolean;
  valid_targets?: string[];
};

export type MinionData = {
  name: string;
  atk: number;
  health: number;
  max_health: number;
  base_atk?: number;
  base_health?: number;
  can_attack?: boolean;
  taunt?: boolean;
  has_deathrattle?: boolean;
  divine_shield?: boolean;
  stealth?: boolean;
  windfury?: boolean;
  frozen?: boolean;
  poisonous?: boolean;
  charge?: boolean;
  rush?: boolean;
  turns_in_play?: number;
  immune?: boolean;
  silenced?: boolean;
  enraged?: boolean;
  text?: string;
  race?: string;
  mechanics?: string[];
  is_titan?: boolean;
  titan_abilities?: TitanAbilityData[];
  titan_ability_cooldown?: boolean;
};

export type WeaponData = {
  name: string;
  atk: number;
  durability: number;
  max_durability: number;
};

export type LocationData = {
  id?: string;
  name: string;
  text?: string;
  durability: number;
  max_durability: number;
  cooldown: boolean;
  is_usable: boolean;
  requires_target: boolean;
  valid_targets?: string[];
};

export type HeroPowerData = {
  id?: string;
  name: string;
  cost: number;
  is_usable: boolean;
  requires_target: boolean;
  description: string;
  valid_targets?: string[];
  is_passive?: boolean;
  must_choose_one?: boolean;
  choose_cards?: CardData[];
  is_summon?: boolean;
  is_life_tap?: boolean;
  health_cost?: number;
  is_totemic_call?: boolean;
};

export type LogEntry = {
  timestamp: string;
  type: string;
  message: string;
  details?: Record<string, unknown>;
};

export type SecretData = {
  name: string;
  id?: string;
  text?: string;
};

export type ChoiceData = {
  type: 'discover' | 'choose_one' | 'mulligan';
  cards: CardData[];
  source: string;
};

export type GameState = {
  turn: number;
  current_player: string;
  turn_remaining?: number;
  turn_timeout?: number;
  game_over?: boolean;
  winner?: string;
  player: {
    hero: string;
    hero_id?: string;
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
    locations?: LocationData[];
    fatigue_counter?: number;
    hand_size?: number;
    max_hand_size?: number;
    field_size?: number;
    max_field_size?: number;
    secrets?: SecretData[];
    secret_count: number;
    max_secrets?: number;
    overload_locked?: number;
    overloaded?: number;
    combo_active?: boolean;
    cards_played_this_turn?: number;
    temp_mana?: number;
    used_mana?: number;
    choice?: ChoiceData | null;
    // Modern mechanic resource counters (default 0 — only render when > 0)
    corpses?: number;
    herald_count?: number;
    imbue_count?: number;
    excavate_count?: number;
    starship_pieces?: number;
    is_building_starship?: boolean;
    dark_gifts_given?: number;
    jade_golem?: number;
  };
  opponent: {
    hero: string;
    hero_id?: string;
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
    locations?: LocationData[];
    fatigue_counter?: number;
    secret_count: number;
    overload_locked?: number;
    overloaded?: number;
    // Mirror modern resource counters for opponent
    corpses?: number;
    herald_count?: number;
    imbue_count?: number;
    excavate_count?: number;
    starship_pieces?: number;
    is_building_starship?: boolean;
    dark_gifts_given?: number;
    jade_golem?: number;
  };
  logs: LogEntry[];
};

class GameService {
  private gameId: string | null = null;

  createGame(mode: string, playerClass: string = 'random', testDeck: boolean = false, deckCode?: string) {
    socketService.connect();
    // 设置重连后重新加入房间的逻辑
    socketService.onReconnect(() => {
      if (this.gameId) {
        console.log('[GameService] Reconnected, rejoining game:', this.gameId);
        socketService.emit('rejoin_game', { game_id: this.gameId });
      }
    });

    // 如果有卡组代码，使用create_game_with_deck事件
    if (deckCode) {
      socketService.emit('create_game_with_deck', { mode, deck_code: deckCode });
    } else {
      socketService.emit('create_game', { mode, player_class: playerClass, test_deck: testDeck });
    }
  }

  endTurn() {
    if (this.gameId) {
      socketService.emit('end_turn', { game_id: this.gameId });
    }
  }

  playCard(cardIndex: number, targetId?: string, chooseCardId?: string) {
    if (this.gameId) {
      socketService.emit('play_card', {
        game_id: this.gameId,
        card_index: cardIndex,
        target_id: targetId,
        choose_card_id: chooseCardId
      });
    }
  }

  useHeroPower(targetId?: string, chooseCardId?: string) {
    if (this.gameId) {
      socketService.emit('use_hero_power', {
        game_id: this.gameId,
        target_id: targetId,
        choose_card_id: chooseCardId,
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

  useTitanAbility(minionIndex: number, abilityIndex: number, targetId?: string) {
    if (this.gameId) {
      socketService.emit('use_titan_ability', {
        game_id: this.gameId,
        minion_index: minionIndex,
        ability_index: abilityIndex,
        target_id: targetId,
      });
    }
  }

  tradeCard(cardIndex: number) {
    if (this.gameId) {
      socketService.emit('trade_card', {
        game_id: this.gameId,
        card_index: cardIndex,
      });
    }
  }

  useLocation(locationIndex: number, targetId?: string) {
    if (this.gameId) {
      socketService.emit('use_location', {
        game_id: this.gameId,
        location_index: locationIndex,
        target_id: targetId,
      });
    }
  }

  onCardTraded(callback: (data: { game_id: string; player: string; card_name: string; card_id: string }) => void) {
    socketService.on('card_traded', (data) => callback(data as { game_id: string; player: string; card_name: string; card_id: string }));
  }

  makeChoice(cardIndex: number) {
    if (this.gameId) {
      console.log('[GameService] Making choice:', cardIndex);
      socketService.emit('make_choice', {
        game_id: this.gameId,
        card_index: cardIndex
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

  onSecretTriggered(callback: (data: { game_id: string; secret: { player: string; secret_name: string; card_id?: string } }) => void) {
    socketService.on('secret_triggered', (data) => callback(data as { game_id: string; secret: { player: string; secret_name: string; card_id?: string } }));
  }

  onFatigueDamage(callback: (data: { game_id: string; fatigue: { player: string; damage: number; counter: number; message: string } }) => void) {
    socketService.on('fatigue_damage', callback);
  }

  onHeroTransformed(callback: (data: { game_id: string; player: string; hero_id: string; hero_name: string }) => void) {
    socketService.on('hero_transformed', (data) => callback(data as { game_id: string; player: string; hero_id: string; hero_name: string }));
  }

  cleanup() {
    socketService.disconnect();
    this.gameId = null;
  }
}

export const gameService = new GameService();
