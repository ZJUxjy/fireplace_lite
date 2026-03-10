import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { gameService, GameState } from '../services/gameService';
import './GameBoard.css';

interface GameBoardProps {
  mode: string;
  onBack: () => void;
}

export function GameBoard({ mode, onBack }: GameBoardProps) {
  const { t } = useTranslation();
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [connecting, setConnecting] = useState(true);

  useEffect(() => {
    gameService.createGame(mode);

    gameService.onGameState((data) => {
      setGameState(data.state);
      setConnecting(false);
    });

    gameService.onError((data) => {
      console.error('Game error:', data.message);
      setConnecting(false);
    });

    return () => {
      gameService.cleanup();
    };
  }, [mode]);

  const handleEndTurn = () => {
    gameService.endTurn();
  };

  if (connecting || !gameState) {
    return (
      <div className="game-board loading">
        <div className="loading-spinner">Loading...</div>
        <button className="back-btn" onClick={onBack}>← Back</button>
      </div>
    );
  }

  const isMyTurn = gameState.current_player === 'player1';

  return (
    <div className="game-board">
      {/* 对手区域 */}
      <div className="opponent-area">
        <div className="opponent-info">
          <div className="hero-portrait opponent">
            <span className="hero-icon">🧙</span>
          </div>
          <div className="hero-details">
            <div className="hero-name">{gameState.opponent.hero}</div>
            <div className="hero-health">❤️ {gameState.opponent.health}</div>
          </div>
        </div>
        <div className="deck-info">
          <span className="deck-count">🔴 {gameState.opponent.deck}</span>
        </div>
        <div className="opponent-hand">
          {Array(gameState.opponent.hand_count).fill(0).map((_, i) => (
            <div key={i} className="card-back" />
          ))}
        </div>
      </div>

      {/* 对手战场 */}
      <div className="battle-field opponent-field">
        {gameState.opponent.field.map((minion, i) => (
          <div key={i} className="minion opponent-minion">
            <div className="minion-stats">
              <span className="minion-atk">{minion.atk}</span>
            </div>
            <div className="minion-name">{minion.name}</div>
            <div className="minion-stats">
              <span className="minion-health">{minion.health}</span>
            </div>
          </div>
        ))}
        {gameState.opponent.field.length === 0 && (
          <div className="empty-field">-</div>
        )}
      </div>

      {/* 己方战场 */}
      <div className="battle-field player-field">
        {gameState.player.field.map((minion, i) => (
          <div key={i} className="minion player-minion">
            <div className="minion-stats">
              <span className="minion-atk">{minion.atk}</span>
            </div>
            <div className="minion-name">{minion.name}</div>
            <div className="minion-stats">
              <span className="minion-health">{minion.health}</span>
            </div>
          </div>
        ))}
        {gameState.player.field.length === 0 && (
          <div className="empty-field">-</div>
        )}
      </div>

      {/* 玩家区域 */}
      <div className="player-area">
        <div className="player-hand">
          {gameState.player.hand.map((cardName, i) => (
            <div key={i} className="card playable">
              <div className="card-cost">{i + 1}</div>
              <div className="card-name">{cardName}</div>
            </div>
          ))}
        </div>
        <div className="player-info">
          <div className="mana-crystal">
            💎 {gameState.player.mana}/{gameState.player.max_mana}
          </div>
          <div className="hero-portrait player">
            <span className="hero-icon">🧙</span>
          </div>
          <div className="hero-details">
            <div className="hero-name">{gameState.player.hero}</div>
            <div className="hero-health">❤️ {gameState.player.health}</div>
          </div>
        </div>
      </div>

      {/* 控制面板 */}
      <div className="control-panel">
        <div className="turn-indicator">
          {isMyTurn ? t('game.yourTurn') : t('game.opponentTurn')}
        </div>
        <button
          className="end-turn-btn"
          onClick={handleEndTurn}
          disabled={!isMyTurn || !gameState.player.can_end_turn}
        >
          {t('game.endTurn')}
        </button>
        <button className="concede-btn">{t('game.concede')}</button>
        <button className="back-btn" onClick={onBack}>←</button>
      </div>
    </div>
  );
}
