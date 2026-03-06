#!/usr/bin/env python3
"""
Fireplace 交互式 CLI 游戏
玩家 vs AI 模式
"""

import sys
from fireplace import cards
from fireplace.game import Game
from fireplace.player import Player
from fireplace.utils import random_class, random_draft
from fireplace.exceptions import GameOver


def clear_screen():
    """清屏"""
    print("\033[2J\033[H", end="")


def print_separator(char="=", length=55):
    """打印分隔线"""
    print(char * length)


def get_card_display(card):
    """获取卡牌简短显示"""
    name = str(card)
    cost = card.cost

    if hasattr(card, 'atk') and hasattr(card, 'health'):
        # 随从或英雄
        return f"{name} ({cost}费) [{card.atk}/{card.health}]"
    elif hasattr(card, 'durability'):
        # 武器
        return f"{name} ({cost}费) [{card.atk}/{card.durability}]"
    else:
        # 法术
        return f"{name} ({cost}费)"


def display_game(game, player):
    """显示游戏状态"""
    clear_screen()
    print_separator()
    print(f"回合 {game.turn} - {'你的回合' if game.current_player == player else '对手回合'}")
    print_separator()

    opponent = player.opponent

    # 对手信息
    hero = opponent.hero
    print(f"对手: {hero} ({hero.health}/{hero.max_health}) | "
          f"法力: {opponent.mana}/{opponent.max_mana} | "
          f"手牌: {len(opponent.hand)} 张 | "
          f"牌库: {len(opponent.deck)} 张")

    # 对手场上
    if opponent.field:
        field_str = " | ".join([f"[{m.atk}/{m.health}] {m}" for m in opponent.field])
        print(f"场上: {field_str}")
    else:
        print("场上: (空)")
    print_separator("-")

    # 玩家场上
    if player.field:
        field_str = " | ".join([f"[{m.atk}/{m.health}] {m}" for m in player.field])
        print(f"你的场上: {field_str}")
    else:
        print("你的场上: (空)")

    # 玩家信息
    hero = player.hero
    print(f"你: {hero} ({hero.health}/{hero.max_health}) | "
          f"法力: {player.mana}/{player.max_mana} | "
          f"手牌: {len(player.hand)} 张 | "
          f"牌库: {len(player.deck)} 张")

    print_separator("-")

    # 手牌
    print("你的手牌:")
    for i, card in enumerate(player.hand, 1):
        playable = "✓" if card.is_playable() else "✗"
        print(f"  [{i}] {get_card_display(card)} {playable}")

    print_separator()

    # 命令提示
    print("命令: play <编号> | attack <攻击者编号> <目标编号> | hero | end | help | quit")
    print("编号说明: 0=英雄, 1-7=随从位置(从左到右)")

    # 显示当前可执行的操作
    playable_cards = [i+1 for i, c in enumerate(player.hand) if c.is_playable()]
    attackers = [c for c in player.characters if c.can_attack()]
    heropower_usable = player.hero.power.is_usable()

    hints = []
    if playable_cards:
        hints.append(f"可打出的牌: {playable_cards}")
    if attackers:
        attacker_names = ["英雄" if a == player.hero else str(a) for a in attackers]
        hints.append(f"可攻击: {attacker_names}")
    if heropower_usable:
        hints.append("英雄技能可用")
    if not hints:
        hints.append("无可用操作，建议输入 end 结束回合")

    print("提示: " + " | ".join(hints))


def display_targets(player, target_type="all"):
    """显示可选目标"""
    opponent = player.opponent

    print("目标编号:")
    print("  [0] 敌方英雄")

    for i, minion in enumerate(opponent.field, 1):
        print(f"  [{i}] 敌方 [{minion.atk}/{minion.health}] {minion}")

    if target_type == "all":
        print(f"  [H] 己方英雄")
        for i, minion in enumerate(player.field, 1):
            print(f"  [F{i}] 己方 [{minion.atk}/{minion.health}] {minion}")


def display_attackers(player):
    """显示可攻击的单位"""
    print("己方角色:")
    print(f"  [0] 英雄 {'✓' if player.hero.can_attack() else '✗'}")

    for i, minion in enumerate(player.field, 1):
        can_atk = "✓" if minion.can_attack() else "✗"
        print(f"  [{i}] [{minion.atk}/{minion.health}] {minion} {can_atk}")


def parse_target(target_str, player, targets):
    """解析目标字符串"""
    target_str = target_str.strip().upper()

    if target_str == "0":
        return player.opponent.hero
    elif target_str.startswith("F"):
        # 己方随从
        idx = int(target_str[1:]) - 1
        if 0 <= idx < len(player.field):
            return player.field[idx]
    elif target_str == "H":
        return player.hero
    else:
        # 敌方随从
        try:
            idx = int(target_str) - 1
            if 0 <= idx < len(player.opponent.field):
                return player.opponent.field[idx]
        except ValueError:
            pass

    return None


def play_card(player, card_index):
    """打出卡牌"""
    if card_index < 1 or card_index > len(player.hand):
        print("错误: 无效的手牌编号")
        return False

    card = player.hand[card_index - 1]

    if not card.is_playable():
        print(f"错误: 无法打出 {card}（法力不足或条件不满足）")
        return False

    target = None
    if card.requires_target():
        display_targets(player)
        target_str = input("选择目标: ").strip()
        targets = list(card.targets)
        target = parse_target(target_str, player, targets)
        if target is None or target not in targets:
            print("错误: 无效目标")
            return False

    # 处理选择卡（如抉择）
    choose = None
    if card.must_choose_one:
        print("选择一个选项:")
        for i, c in enumerate(card.choose_cards, 1):
            print(f"  [{i}] {c}")
        choice_idx = input("选择: ").strip()
        try:
            idx = int(choice_idx) - 1
            if 0 <= idx < len(card.choose_cards):
                choose = card.choose_cards[idx]
        except ValueError:
            print("错误: 无效选择")
            return False

    try:
        card.play(target=target, choose=choose)
        print(f"打出了 {card}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False


def attack(player, attacker_str, target_str):
    """攻击"""
    # 解析攻击者
    attacker = None
    try:
        idx = int(attacker_str)
        if idx == 0:
            attacker = player.hero
        elif 1 <= idx <= len(player.field):
            attacker = player.field[idx - 1]
    except ValueError:
        print("错误: 无效的攻击者编号")
        return False

    if attacker is None:
        print("错误: 找不到攻击者")
        return False

    if not attacker.can_attack():
        print(f"错误: {attacker} 无法攻击")
        return False

    # 解析目标
    targets = list(attacker.targets)
    target = parse_target(target_str, player, targets)

    if target is None or target not in targets:
        print("错误: 无效目标")
        return False

    try:
        attacker.attack(target)
        print(f"{attacker} 攻击了 {target}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False


def use_hero_power(player):
    """使用英雄技能"""
    heropower = player.hero.power

    if not heropower.is_usable():
        print("错误: 英雄技能不可用（法力不足或已使用）")
        return False

    target = None
    if heropower.requires_target():
        display_targets(player)
        target_str = input("选择目标: ").strip()
        targets = list(heropower.targets)
        target = parse_target(target_str, player, targets)
        if target is None or target not in targets:
            print("错误: 无效目标")
            return False

    # 处理选择
    choose = None
    if heropower.must_choose_one:
        print("选择一个选项:")
        for i, c in enumerate(heropower.choose_cards, 1):
            print(f"  [{i}] {c}")
        choice_str = input("选择: ").strip()
        try:
            idx = int(choice_str) - 1
            if 0 <= idx < len(heropower.choose_cards):
                choose = heropower.choose_cards[idx]
        except ValueError:
            print("错误: 无效选择")
            return False

    try:
        heropower.use(target=target, choose=choose)
        print(f"使用了英雄技能: {heropower}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False


def ai_turn(game, ai_player):
    """AI 回合（简单随机策略）"""
    import random

    print(f"\n=== AI ({ai_player.hero}) 的回合 ===")

    # 处理选择
    while ai_player.choice:
        choice = random.choice(ai_player.choice.cards)
        print(f"AI 选择了: {choice}")
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
            print(f"AI 使用了英雄技能")
        except:
            pass

    # 打牌
    playable_cards = [c for c in ai_player.hand if c.is_playable()]
    random.shuffle(playable_cards)
    for card in playable_cards[:3]:  # 最多打3张
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
            print(f"AI 打出了: {card}")
        except:
            pass

        # 处理选择
        while ai_player.choice:
            choice = random.choice(ai_player.choice.cards)
            ai_player.choice.choose(choice)

    # 攻击
    attackers = [c for c in ai_player.characters if c.can_attack()]
    random.shuffle(attackers)
    for attacker in attackers[:3]:  # 最多攻击3次
        if not attacker.can_attack():
            continue
        targets = list(attacker.targets)
        if targets:
            target = random.choice(targets)
            try:
                attacker.attack(target)
                print(f"AI 的 {attacker} 攻击了 {target}")
            except:
                pass

    print("AI 结束回合")
    game.end_turn()


def show_help():
    """显示帮助"""
    print("""
命令帮助:
  play <编号>      - 打出手牌（编号见手牌列表）
  attack <攻击者> <目标> - 攻击
                    攻击者: 0=英雄, 1-7=随从位置
                    目标: 0=敌方英雄, 1-7=敌方随从, H=己方英雄, F1-F7=己方随从
  hero [目标]      - 使用英雄技能
  end              - 结束回合
  status           - 重新显示场况
  help             - 显示此帮助
  quit             - 退出游戏
""")


def player_turn(game, player):
    """玩家回合"""
    while True:
        display_game(game, player)

        # 处理选择（如发现）
        while player.choice:
            print("\n请选择:")
            for i, c in enumerate(player.choice.cards, 1):
                print(f"  [{i}] {get_card_display(c)}")
            choice_str = input("选择编号: ").strip()
            try:
                idx = int(choice_str) - 1
                if 0 <= idx < len(player.choice.cards):
                    player.choice.choose(player.choice.cards[idx])
            except ValueError:
                print("无效选择")

            display_game(game, player)

        try:
            cmd = input("\n> ").strip().lower()
        except EOFError:
            print("\n退出游戏")
            sys.exit(0)

        if not cmd:
            continue

        parts = cmd.split()
        action = parts[0]

        if action == "play":
            if len(parts) < 2:
                print("用法: play <手牌编号>")
                continue
            try:
                idx = int(parts[1])
                play_card(player, idx)
            except ValueError:
                print("错误: 请输入数字编号")

        elif action == "attack":
            if len(parts) < 3:
                print("用法: attack <攻击者> <目标>")
                print("  攻击者: 0=英雄, 1-7=场上随从位置")
                print("  目标: 0=敌方英雄, 1-7=敌方随从")
                continue
            attack(player, parts[1], parts[2])

        elif action == "hero":
            use_hero_power()

        elif action == "end":
            print("结束回合")
            game.end_turn()
            break

        elif action == "status":
            continue  # 循环会重新显示

        elif action == "help":
            show_help()
            input("按回车继续...")

        elif action == "quit" or action == "exit":
            print("退出游戏")
            sys.exit(0)

        else:
            print(f"未知命令: {action}。输入 'help' 查看帮助。")


def main():
    """主函数"""
    print("正在初始化卡牌数据库...")
    cards.db.initialize()
    print(f"已加载 {len(cards.db)} 张卡牌\n")

    # 随机选择职业和卡组
    player_class = random_class()
    ai_class = random_class()

    print(f"你的职业: {player_class.name}")
    print(f"对手职业: {ai_class.name}\n")

    player_deck = random_draft(player_class)
    ai_deck = random_draft(ai_class)

    # 创建玩家
    player = Player("你", player_deck, player_class.default_hero)
    ai = Player("AI", ai_deck, ai_class.default_hero)

    # 创建游戏
    game = Game(players=(player, ai))

    print("游戏开始!")
    input("按回车继续...")

    # 开始游戏（跳过换牌）
    game.start()

    # 跳过换牌阶段
    for p in game.players:
        if p.choice:
            p.choice.choose()  # 不换任何牌

    # 游戏主循环
    try:
        while True:
            if game.current_player == player:
                player_turn(game, player)
            else:
                ai_turn(game, game.current_player)
    except GameOver:
        print_separator()
        print("游戏结束!")
        print_separator()

        if player.playstate.name == "WON":
            print("恭喜你赢了!")
        elif player.playstate.name == "LOST":
            print("你输了!")
        elif player.playstate.name == "TIED":
            print("平局!")

        print(f"总回合数: {game.turn}")


if __name__ == "__main__":
    main()
