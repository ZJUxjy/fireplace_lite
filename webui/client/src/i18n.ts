import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  zhCN: {
    translation: {
      "game.title": "炉石传说",
      "game.mode.pve": "玩家 vs AI",
      "game.mode.pvp": "玩家 vs 玩家",
      "game.mode.ai": "AI vs AI",
      "game.yourTurn": "你的回合",
      "game.opponentTurn": "对手回合",
      "game.endTurn": "结束回合",
      "game.concede": "认输",
      "game.victory": "胜利",
      "game.defeat": "失败",
      "game.draw": "平局",
      "game.turn": "回合",
      "action.play": "打出",
      "action.attack": "攻击",
      "action.heroPower": "英雄技能",
      "card.cost": "费用",
      "card.attack": "攻击",
      "card.health": "生命",
      "ui.settings": "设置",
      "ui.language": "语言",
      "ui.startGame": "开始游戏",
      "ui.newGame": "新游戏",
      "ui.actionLog": "操作日志"
    }
  },
  enUS: {
    translation: {
      "game.title": "Hearthstone",
      "game.mode.pve": "Player vs AI",
      "game.mode.pvp": "Player vs Player",
      "game.mode.ai": "AI vs AI",
      "game.yourTurn": "Your Turn",
      "game.opponentTurn": "Opponent's Turn",
      "game.endTurn": "End Turn",
      "game.concede": "Concede",
      "game.victory": "Victory",
      "game.defeat": "Defeat",
      "game.draw": "Draw",
      "game.turn": "Turn",
      "action.play": "Play",
      "action.attack": "Attack",
      "action.heroPower": "Hero Power",
      "card.cost": "Cost",
      "card.attack": "Attack",
      "card.health": "Health",
      "ui.settings": "Settings",
      "ui.language": "Language",
      "ui.startGame": "Start Game",
      "ui.newGame": "New Game",
      "ui.actionLog": "Action Log"
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'zhCN',
    fallbackLng: 'enUS',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
