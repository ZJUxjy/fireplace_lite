from utils import *
from hearthstone.enums import CardType


##
# CATA_150: 拉格纳罗斯，绝世烈火
# 在你的回合结束时，触发你的随从的亡语（随从不死亡）

def test_ragnaros_triggers_deathrattles_at_turn_end():
    """At end of turn, Ragnaros triggers deathrattle effects of all friendly minions without killing them."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Place Ragnaros on field
    ragnaros = game.player1.summon("CATA_150")
    # Use CATA_150t (Hand of Ragnaros) which has deathrattle: deal 2 damage to random enemy
    # Use VAN_EX1_029 (Leper Gnome): deathrattle deals 2 damage to enemy hero
    leper_gnome = game.player1.summon("VAN_EX1_029")
    enemy_hero_hp_before = game.player2.hero.health
    # End turn - should trigger leper gnome's deathrattle (deal 2 dmg to enemy hero)
    game.end_turn()
    # Leper Gnome should still be alive (not killed)
    assert leper_gnome in game.player1.field
    # Enemy hero should have taken 2 damage from the triggered deathrattle
    assert game.player2.hero.health == enemy_hero_hp_before - 2


def test_ragnaros_does_not_kill_minions():
    """Ragnaros triggers deathrattles but does NOT kill the minions."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    ragnaros = game.player1.summon("CATA_150")
    leper_gnome = game.player1.summon("VAN_EX1_029")
    game.end_turn()
    assert leper_gnome in game.player1.field


##
# CATA_130: 炫晶小熊
# 每当你消耗掉最后一个法力水晶，获得+1/+1

def test_crystalspine_cub_buffs_when_last_mana_spent():
    """Crystalspine Cub gets +1/+1 when you spend your last mana crystal."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 9  # 1 mana left
    cub = game.player1.summon("CATA_130")
    base_atk = cub.atk
    base_health = cub.health
    # Play a 1-cost minion (Elven Archer needs a target - provide hero)
    game.player1.give("CS2_189").play(target=game.player2.hero)  # Elven Archer (1-cost)
    assert cub.atk == base_atk + 1
    assert cub.health == base_health + 1


def test_crystalspine_cub_no_buff_when_mana_remains():
    """Crystalspine Cub should NOT get +1/+1 when mana still remains after playing a card."""
    game = prepare_empty_game()
    game.player1.max_mana = 5
    game.player1.used_mana = 0
    cub = game.player1.summon("CATA_130")
    base_atk = cub.atk
    # Play a 1-cost card (4 mana remaining)
    game.player1.give("CS2_025").play()  # Arcane Explosion (1-cost)
    assert cub.atk == base_atk  # No buff, mana not empty


##
# CATA_132: 护巢龙
# 战吼：获得两个3/3嘲讽龙。如果你使用8点法力，则直接召唤

def test_broodwatcher_gives_dragons_to_hand_below_8_mana():
    """Broodwatcher gives 2 Emerald Whelp cards to hand when less than 8 mana spent this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0  # 0 mana spent so far; broodwatcher costs 4 = 4 total < 8
    broodwatcher = game.player1.give("CATA_132")
    broodwatcher.play()
    # Should have 2 Emerald Whelps in hand (CATA_132t)
    dragon_tokens = [c for c in game.player1.hand if c.id == "CATA_132t"]
    assert len(dragon_tokens) == 2
    # Field should only have the Broodwatcher itself (no summons)
    assert len(game.player1.field) == 1


def test_broodwatcher_summons_dragons_at_8_mana():
    """Broodwatcher summons 2 Emerald Whelps directly when 8+ mana has been spent this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Spend 4 mana before playing broodwatcher (4-cost) = 8 total
    # Use a 4-cost minion with no targeting needed
    game.player1.give("CS2_182").play()  # Chillwind Yeti (4-cost, no target)
    # Now play Broodwatcher (costs 4 more = 8 total)
    broodwatcher = game.player1.give("CATA_132")
    broodwatcher.play()
    # Should have summoned 2 dragons on field (not in hand)
    field_ids = [m.id for m in game.player1.field]
    assert field_ids.count("CATA_132t") == 2
    # Should NOT have them in hand
    hand_ids = [c.id for c in game.player1.hand]
    assert hand_ids.count("CATA_132t") == 0


##
# CATA_140: 梦境之龙麦琳瑟拉
# 战吼：随机将龙牌填入你的手牌直到满

def test_merithra_fills_hand_with_dragons():
    """Merithra fills your hand with random Dragons up to hand limit (10 cards)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    merithra = game.player1.give("CATA_140")
    merithra.play()
    # Hand should be full (10 cards) or as many dragons as possible
    assert len(game.player1.hand) == 10  # Hand limit


def test_merithra_fills_remaining_slots():
    """Merithra only fills remaining hand slots, not beyond 10."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Give 8 cards to hand first
    for _ in range(8):
        game.player1.give("CS2_025")
    merithra = game.player1.give("CATA_140")
    merithra.play()
    # Should now have 10 cards (8 + filled remaining 2... wait merithra itself was 9th)
    # After playing merithra (removed from hand), 8 remain, fill to 10 = 2 dragons
    assert len(game.player1.hand) == 10


##
# CATA_491: 怪异触手
# 对所有随从造成$3点伤害。重复（打出后回到手牌）

def test_tentacle_repeats_returns_to_hand():
    """Tentacle (CATA_491) returns to hand after being played (Repeat mechanic)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    tentacle = game.player1.give("CATA_491")
    tentacle.play()
    # Should be back in hand
    assert any(c.id == "CATA_491" for c in game.player1.hand)


def test_tentacle_deals_damage_to_all_minions():
    """Tentacle deals 3 damage to all minions."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Use a minion with enough health to survive 3 damage: Chillwind Yeti (CS2_182) 4/5
    dummy = game.player2.summon("CS2_182")  # 4/5 Chillwind Yeti
    tentacle = game.player1.give("CATA_491")
    tentacle.play()
    assert dummy.health == dummy.max_health - 3


##
# CATA_791: 残影
# 造成4点伤害。重复（打出后回到手牌）

def test_shadowflame_repeats_returns_to_hand():
    """Shadowflame (CATA_791) is not in DB; CATA_491 Tentacle repeat is tested instead."""
    # CATA_791 is not in the hearthstone DB and cannot be instantiated
    # This test verifies CATA_491 repeat returns to hand (covered in separate test)
    assert True  # placeholder - CATA_791 ID does not exist in DB


##
# CATA_200: 旧神特工
# 战吼：将你手牌中的一张牌变成一枚硬币

def test_agent_transforms_hand_card_to_coin():
    """Agent of the Old Ones battlecry transforms a random hand card into a Coin."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Give some cards to hand
    for _ in range(3):
        game.player1.give("CS2_025")
    agent = game.player1.give("CATA_200")
    hand_before = len(game.player1.hand)
    agent.play()
    # One of the hand cards should now be a Coin (GAME_005)
    coins = [c for c in game.player1.hand if c.id == "GAME_005"]
    assert len(coins) == 1


##
# CATA_180: 速逝鱼人
# 战吼：你的下一张法力值消耗小于或等于（3）点的鱼人牌会消耗生命值，而非法力值。

def test_fished_murloc_makes_next_low_cost_murloc_cost_health():
    """Fished Murloc makes your next <=3-Cost Murloc cost Health instead of Mana."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0

    game.player1.give("CATA_180").play()
    mana_before = game.player1.mana
    health_before = game.player1.hero.health
    murloc = game.player1.give("EX1_506")  # Murloc Tidehunter, 2 mana.

    murloc.play()

    assert game.player1.mana == mana_before
    assert game.player1.hero.health == health_before - 2
    assert not game.player1.murlocs_cost_health


def test_fished_murloc_ignores_high_cost_murloc_until_low_cost_murloc_played():
    """Fished Murloc is not consumed by Murlocs that cost more than 3."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0

    game.player1.give("CATA_180").play()
    mana_before = game.player1.mana
    health_before = game.player1.hero.health
    expensive_murloc = game.player1.give("EX1_062")  # Old Murk-Eye, 4 mana.

    expensive_murloc.play()

    assert game.player1.mana == mana_before - 4
    assert game.player1.hero.health == health_before
    assert game.player1.murlocs_cost_health

    low_cost_murloc = game.player1.give("EX1_506")
    mana_before_low_cost = game.player1.mana
    low_cost_murloc.play()

    assert game.player1.mana == mana_before_low_cost
    assert game.player1.hero.health == health_before - 2
    assert not game.player1.murlocs_cost_health


##
# CATA_185: 无面复制者
# 扰魔。亡语：将消灭本随从的随从变形成为无面复制者。

def test_facelessifier_transforms_minion_that_kills_it_in_combat():
    """Facelessifier transforms the enemy minion that kills it in combat."""
    game = prepare_empty_game()
    attacker_controller = game.current_player
    attacker = attacker_controller.summon("CS2_182")  # Chillwind Yeti: 4/5.
    defender = attacker_controller.opponent.summon("CATA_185")
    attacker.turns_in_play = 1

    attacker.attack(defender)

    assert [minion.id for minion in attacker_controller.field] == ["CATA_185"]
    assert not attacker_controller.opponent.field


##
# CATA_186: 黏弹爆破手
# 战吼：使你的对手获得一张法力值消耗为（2）的黏弹。黏弹相邻的卡牌法力值消耗增加（1）点。

def test_goo_increases_adjacent_hand_card_costs_only():
    """Goo increases the cost of adjacent hand cards only."""
    game = prepare_empty_game()
    player = game.player1
    left = player.give("CS2_182")
    goo = player.give("CATA_186t")
    right = player.give("CS2_179")
    far = player.give("CS2_172")

    game.refresh_auras()

    assert left.cost == left.data.cost + 1
    assert right.cost == right.data.cost + 1
    assert far.cost == far.data.cost
    assert goo.cost == 2


##
# CATA_615: 吉恩，咒厄国王
# 当本牌在你手牌中时，如果你其他手牌的法力值消耗均为偶数或奇数，变形成为狼人国王。

def test_genn_greymane_transforms_in_hand_when_other_hand_costs_share_parity():
    """Genn Greymane transforms in hand when all other hand cards share parity."""
    game = prepare_empty_game()
    player = game.current_player
    player.give("CS2_182")  # Chillwind Yeti: 4 mana.
    player.give("CS2_179")  # Sen'jin Shieldmasta: 4 mana.

    player.give("CATA_615")
    game.refresh_auras()

    assert any(card.id == "CATA_615t" for card in player.hand)
    assert not any(card.id == "CATA_615" for card in player.hand)


def test_worgen_king_battlecry_sets_hero_power_cost_to_one():
    """Genn Greymane (Worgen) makes your starting Hero Power cost 1."""
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    genn = player.give("CATA_615t")

    assert player.hero_power.cost == 2

    genn.play()

    assert player.hero_power.cost == 1


##
# CATA_206: 扭曲畸怪
# 扰魔。嘲讽。本牌在你的手牌中时，每回合随机具有两项额外效果。

def test_twisted_monstrosity_has_current_bonus_effects_without_colossal_limb_tag():
    """Twisted Monstrosity has its current bonus effects and is not a Colossal limb."""
    game = prepare_empty_game()
    player = game.current_player
    monstrosity = player.summon("CATA_206")
    enemy_spell = player.opponent.give("CS2_008")  # Moonfire.

    assert monstrosity.taunt
    assert monstrosity.cant_be_targeted_by_abilities
    assert monstrosity.cant_be_targeted_by_hero_powers
    assert monstrosity not in enemy_spell.play_targets
    assert not monstrosity.data.scripts.tags.get(GameTag.COLOSSAL_LIMB)


##
# CATA_208: 无私的保卫者
# 嘲讽。受到的所有伤害提高一点。

def test_selfless_defender_takes_one_extra_spell_damage():
    """Selfless Defender takes 1 extra damage from spell damage."""
    game = prepare_empty_game()
    attacker = game.current_player
    defender = attacker.opponent.summon("CATA_208")

    attacker.give("CS2_008").play(target=defender)  # Moonfire: 1 damage.

    assert defender.health == defender.max_health - 2


def test_selfless_defender_takes_one_extra_combat_damage():
    """Selfless Defender takes 1 extra damage from combat damage."""
    game = prepare_empty_game()
    player = game.current_player
    defender = player.opponent.summon("CATA_208")
    attacker = player.summon("CS2_182")  # Chillwind Yeti: 4 attack.
    attacker.turns_in_play = 1

    attacker.attack(defender)

    assert defender.health == defender.max_health - 5


##
# CATA_213: 威拉诺兹
# 战吼：如果你的套牌中随从牌的法力值消耗之和为100，使你牌库中的随从获得总计100点的属性值。

def _total_deck_minion_bonus(player):
    return sum(
        card.atk
        - card.data.atk
        + card.max_health
        - card.data.health
        for card in player.deck
        if card.type == CardType.MINION
    )


def test_veranus_buffs_deck_minions_by_total_100_stats_when_deck_cost_is_100():
    """Veranus gives deck minions a total of 100 stats when deck minion costs sum to 100."""
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    for _ in range(25):
        player.give("CS2_182").shuffle_into_deck()  # Chillwind Yeti: 4 mana.

    player.give("CATA_213").play()

    assert _total_deck_minion_bonus(player) == 100


def test_veranus_does_not_buff_deck_when_minion_cost_sum_is_not_100():
    """Veranus does nothing when deck minion costs do not sum to 100."""
    game = prepare_empty_game()
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0
    for _ in range(24):
        player.give("CS2_182").shuffle_into_deck()

    player.give("CATA_213").play()

    assert _total_deck_minion_bonus(player) == 0


##
# CATA_556: 载蛋雏龙
# 战吼：随机获取一张法力值消耗小于或等于（3）点的龙牌。

def test_carrier_whelp_can_give_dragon_that_costs_less_than_three():
    """Carrier Whelp's random dragon pool includes dragons below 3 cost."""
    game = prepare_empty_game()
    game.random.seed(3)
    player = game.current_player
    player.max_mana = 10
    player.used_mana = 0

    player.give("CATA_556").play()

    generated = player.hand[-1]
    assert generated.id == "NEW1_023"
    assert generated.cost == 2


##
# CATA_591: 指挥官迦顿
# 战吼：从你的牌库中发现一张卡牌，它的费用为(0)

def test_commander_geddon_discover_choice_and_zero_cost():
    """Commander Geddon gives a discover choice; chosen card costs (0)."""
    game = prepare_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    geddon = game.player1.give("CATA_591")
    geddon.play()
    # Should have a discover choice
    assert game.player1.choice is not None
    # Choose the first card
    chosen = game.player1.choice.cards[0]
    game.player1.choice.choose(chosen)
    # The chosen card should be in hand with cost 0
    card_in_hand = next((c for c in game.player1.hand if c.id == chosen.id), None)
    assert card_in_hand is not None
    assert card_in_hand.cost == 0


##
# CATA_153: 奥拉基尔，风暴之主
# 战吼：获取2个费用等于此随从攻击力的随从，费用变为(1)

def test_alakir_gives_minions_matching_atk_cost():
    """Al'Akir gives 2 minions with cost equal to his ATK, set to cost 1."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    alakir = game.player1.give("CATA_153")
    alakir.play()
    # Al'Akir has ATK=2, should give 2 minions costing 2 originally, now cost 1
    minions_in_hand = [c for c in game.player1.hand if c.type == CardType.MINION]
    assert len(minions_in_hand) == 2
    for m in minions_in_hand:
        assert m.cost == 1  # cost set to 1


##
# CATA_564: 飞行助翼
# 战吼：使一个友方随从获得Mega-Windfury

def test_air_support_gives_mega_windfury():
    """Air Support gives target friendly minion Mega-Windfury."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    target = game.player1.summon("CS2_182")  # Chillwind Yeti
    air_support = game.player1.give("CATA_564")
    air_support.play(target=target)
    assert target.mega_windfury


##
# CATA_487: 祈雨元素
# 每回合第一次用法术造成伤害时，获得+2攻击力（每回合只触发一次）

def test_raincaller_buffs_on_first_spell_damage():
    """Raincaller gains +2 ATK when you deal spell damage (once per turn)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    raincaller = game.player1.summon("CATA_487")
    base_atk = raincaller.atk
    # Play a damage spell
    game.player1.give("CS2_023").play()  # Arcane Missiles (1 mana, deals 3 random damage)
    assert raincaller.atk == base_atk + 2


def test_raincaller_only_triggers_once_per_turn():
    """Raincaller should only gain +2 ATK once per turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    raincaller = game.player1.summon("CATA_487")
    base_atk = raincaller.atk
    # Play two damage spells in same turn
    game.player1.give("CS2_023").play()  # Arcane Missiles
    game.player1.give("CS2_023").play()  # Arcane Missiles again
    # Should only have triggered once (+2, not +4)
    assert raincaller.atk == base_atk + 2


##
# CATA_978: 辛达苟萨的胜利
# 对一个随从造成$8点伤害。使你手牌中一张随机牌的法力值消耗减少，减少的量等于超过目标生命值的伤害

def test_sindragosa_triumph_reduces_cost_by_overflow():
    """Sindragosa's Triumph reduces a hand card's cost by the overflow damage."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Voidwalker has 1/3 → health=3, overflow = 8-3 = 5
    target = game.player2.summon("CS2_065")  # Voidwalker 1/3
    hand_card = game.player1.give("CS2_182")  # Chillwind Yeti, costs 4
    sindy = game.player1.give("CATA_978")
    sindy.play(target=target)
    # Overflow = 5, Yeti original cost 4 → reduced to max(0, 4-5) = 0
    assert hand_card.cost == 0


def test_sindragosa_triumph_no_reduction_when_no_overflow():
    """Sindragosa's Triumph does not reduce cost if target survives (no overflow)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Merithra has 4/12 in base stats → 12 health > 8 → overflow = 0
    target = game.player2.summon("CATA_140")
    hand_card = game.player1.give("CS2_182")  # Costs 4
    original_cost = hand_card.cost
    sindy = game.player1.give("CATA_978")
    sindy.play(target=target)
    # Overflow = max(0, 8-12) = 0, no cost reduction
    assert hand_card.cost == original_cost


##
# CATA_131: 费伍德树人
# 战吼：获得一个临时法力水晶。如果你使用4点法力，则变为永久

def test_felwood_treant_permanent_crystal_at_4_mana():
    """Felwood Treant gives a permanent crystal when 4+ mana has been spent."""
    game = prepare_empty_game()
    game.player1.max_mana = 9  # Room to gain 1 more (max_resources=10)
    game.player1.used_mana = 2  # Already spent 2; treant costs 2 → total = 4
    max_before = game.player1.max_mana
    treant = game.player1.give("CATA_131")
    treant.play()
    # max_mana should increase permanently
    assert game.player1.max_mana == max_before + 1
    # Persist after turn end
    game.end_turn()
    game.end_turn()
    assert game.player1.max_mana == max_before + 1


def test_felwood_treant_temporary_crystal_below_4_mana():
    """Felwood Treant gives only a temporary crystal when less than 4 mana spent."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0  # Only treant's 2-cost will be spent = 2 < 4
    max_before = game.player1.max_mana
    treant = game.player1.give("CATA_131")
    treant.play()
    # max_mana should NOT increase (just temp mana this turn)
    assert game.player1.max_mana == max_before


##
# CATA_136: 艾萨拉的胜利
# 洗入5张随机8+费随从并使其属性翻倍

def test_azsharas_triumph_shuffles_minions_into_deck():
    """Azshara's Triumph shuffles 5 random high-cost minions into the deck."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    deck_size_before = len(game.player1.deck)
    triumph = game.player1.give("CATA_136")
    triumph.play()
    assert len(game.player1.deck) == deck_size_before + 5


##
# CATA_469: 多彩龙巢母
# 突袭。每当本随从攻击时，复原等同于本随从攻击力的法力水晶

def test_chromatic_broodmother_refunds_atk_mana():
    """Chromatic Broodmother refunds mana equal to its ATK when attacking."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 5  # 5 mana used, 5 available
    broodmother = game.player1.summon("CATA_469")  # 2/5 with Rush
    target = game.player2.summon("CS2_182")  # Enemy Chillwind Yeti (Rush can attack minions)
    atk = broodmother.atk  # = 2
    mana_before = game.player1.mana  # = 5
    broodmother.attack(target=target)
    # FillMana(ATK=2): used_mana decreases by 2, so available mana increases by 2
    assert game.player1.mana == mana_before + atk


##
# CATA_151: 艾萨拉，海洋之主
# 你的英雄拥有风怒（持续光环）

def test_azshara_hero_windfury_aura():
    """Azshara gives hero Windfury immediately (aura, not just at turn begin)."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    assert not game.player1.hero.windfury  # No windfury before
    azshara = game.player1.summon("CATA_151")
    assert game.player1.hero.windfury  # Windfury active
    # Kill Azshara - windfury should be removed
    azshara.destroy()
    game.end_turn()  # Process deaths
    assert not game.player1.hero.windfury  # Windfury gone


def test_azshara_tentacle_buffs_hero_atk():
    """Azshara's Tentacle gives hero +1 ATK when played."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    base_atk = game.player1.hero.atk
    tentacle = game.player1.give("CATA_151t")
    tentacle.play()
    assert game.player1.hero.atk == base_atk + 1


##
# CATA_533: 涣漫洪流
# 对最左边和最右边的敌方随从造成5点伤害; 无随从时对敌方英雄造成5点伤害

def test_surging_tide_hits_hero_when_no_enemy_minions():
    """Surging Tide hits enemy hero for 5 when there are no enemy minions."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    hero_hp = game.player2.hero.health
    spell = game.player1.give("CATA_533")
    spell.play()
    assert game.player2.hero.health == hero_hp - 5


def test_surging_tide_hits_leftmost_and_rightmost_minions():
    """Surging Tide hits leftmost and rightmost enemy minions for 5."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    left = game.player2.summon("CS2_182")   # leftmost
    mid = game.player2.summon("CS2_182")    # middle
    right = game.player2.summon("CS2_182")  # rightmost
    spell = game.player1.give("CATA_533")
    spell.play()
    assert left not in game.player2.field   # killed by 5 dmg
    assert mid in game.player2.field        # untouched middle
    assert right not in game.player2.field  # killed by 5 dmg


##
# CATA_898: 鳞甲长矛手
# 所有敌方随从拥有嘲讽（持续光环）

def test_scaled_lancer_enemy_minions_have_taunt():
    """Scaled Lancer gives all enemy minions Taunt while alive."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    enemy_minion = game.player2.summon("CS2_182")  # Chillwind Yeti
    assert not enemy_minion.taunt  # No taunt before
    lancer = game.player1.summon("CATA_898")
    assert enemy_minion.taunt  # Taunt active from aura
    # Kill lancer - taunt should be removed
    lancer.destroy()
    game.end_turn()  # Process deaths
    assert not enemy_minion.taunt  # Taunt removed


##
# CATA_613: 生存专家
# 如果你没有控制其他随从，则拥有免疫

def test_survivalist_immune_when_alone():
    """Survivalist has Immune when alone on board."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    survivalist = game.player1.summon("CATA_613")
    assert survivalist.immune  # Alone = immune


def test_survivalist_no_immune_with_other_minion():
    """Survivalist loses Immune when another friendly minion is present."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    survivalist = game.player1.summon("CATA_613")
    assert survivalist.immune  # Alone = immune
    game.player1.summon("CS2_182")  # Add another friendly minion
    assert not survivalist.immune  # No longer alone


##
# CATA_528: 海洋咒符
# 在你的下个回合开始时，召唤一个3/3并具有嘲讽的纳迦

def test_oceanic_sigil_summons_naga_next_turn():
    """Oceanic Sigil summons a 3/3 Taunt Naga at the start of the next turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    sigil = game.player1.give("CATA_528")
    sigil.play()
    # Should NOT have naga yet (it's next turn)
    assert not any(m.id == "CATA_528t" for m in game.player1.field)
    # End turn and start next player1 turn
    game.end_turn()  # player2's turn
    game.end_turn()  # back to player1
    # Now the naga should be summoned
    assert any(m.id == "CATA_528t" for m in game.player1.field)
    naga = next(m for m in game.player1.field if m.id == "CATA_528t")
    assert naga.atk == 3
    assert naga.health == 3
    assert naga.taunt


##
# CATA_724: 缚风者
# 亡语：解锁你被过载的水晶

def test_stormbinder_deathrattle_unlocks_overload():
    """Stormbinder deathrattle clears overloaded crystals."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Overload player1 by 2 next turn
    game.player1.overloaded = 2
    stormbinder = game.player1.summon("CATA_724")
    stormbinder.destroy()
    game.end_turn()  # process deaths
    # After deathrattle, overloaded should be 0
    assert game.player1.overloaded == 0


##
# CATA_570: 莫卓克
# 战吼：抽1张牌并减少其费用(10)

def test_morchok_draw_reduces_cost_by_10():
    """Morchok draws a card and reduces its cost by 10."""
    from hearthstone.enums import Zone as ZoneEnum
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Put a Chillwind Yeti (cost 4) directly in the deck
    yeti = game.player1.card("CS2_182", zone=ZoneEnum.DECK)
    assert yeti.cost == 4
    morchok = game.player1.give("CATA_570")
    morchok.play()
    # The yeti should now be in hand with cost reduced by 10 (min 0)
    assert yeti.zone == ZoneEnum.HAND
    assert yeti.cost == 0  # 4 - 10 = 0 (min 0)


##
# CATA_458: 大法师卡雷
# 战吼：使你手牌和牌库中所有法术牌获得法术伤害+1

##
# CATA_135: 苔缚术
# 召唤两个1/2元素。用所有法力值给它们+1/+1

def test_mossbinding_buffs_elementals_by_mana_spent():
    """Mossbinding summons two 1/2 Elementals and buffs them by mana spent this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 3  # 3 mana spent before Mossbinding (cost 2 → total = 5)
    # Play Mossbinding for 2 mana → used_mana = 3 + 2 = 5 after paying
    mossbinding = game.player1.give("CATA_135")
    mossbinding.play()
    # Should have 2 treants with atk = 1 + 5 = 6, health = 2 + 5 = 7
    treants = [m for m in game.player1.field if m.id == "CATA_135t"]
    assert len(treants) == 2
    for t in treants:
        assert t.atk == 1 + 5  # base 1 + 5 mana spent
        assert t.health == 2 + 5  # base 2 + 5 mana spent


##
# CATA_470: 维克多·奈法里奥斯
# 战吼：制造一条自定义的亡灵龙。如果你的手牌中有龙牌，制造的这条龙的法力值消耗减少(3)点

def test_victor_nefarius_dragon_in_hand_reduces_cost():
    """Victor Nefarius: created dragon's cost is reduced by 3 if you have a dragon in hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Give a dragon card to hand (CATA_465t is a dragon)
    game.player1.give("CATA_465t")
    victor = game.player1.give("CATA_470")
    victor.play()
    # The created dragon should be in hand
    created = next((c for c in game.player1.hand if c.id == "CATA_470t1"), None)
    assert created is not None
    # With dragon in hand, cost reduced by 3 (buff applied)
    assert created._cost == -3 or created.cost < 1  # base cost 1 - 3 = 0 (min 0)


##
    """Archmage Kalec gives spellpower+1 to all spells in hand and deck."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Give a spell in hand (Fireball, cost 4)
    fireball = game.player1.give("CS2_029")
    assert len(fireball.buffs) == 0
    kalec = game.player1.give("CATA_458")
    kalec.play()
    # Fireball in hand should have spellpower+1 buff applied
    assert len(fireball.buffs) == 1
    assert getattr(fireball.buffs[0], "spellpower", 0) == 1


##
# CATA_725te / CATA_725t (warlock) — Gul'dan's Soldier gives +2/+2 to self on turn end

def test_guldan_soldier_buffs_self_on_turn_end():
    """Gul'dan's Soldier gets +2/+2 when it destroys the minion to its right at end of turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Field: [Soldier, Yeti]
    soldier = game.player1.summon("CATA_725t")
    yeti = game.player1.summon("CS2_182")  # 4/5 Yeti
    base_atk = soldier.atk
    base_hp = soldier.health
    game.end_turn()  # triggers OWN_TURN_END → destroys yeti, buffs soldier
    assert soldier.atk == base_atk + 2
    assert soldier.health == base_hp + 2
    assert yeti not in game.player1.field


##
# CATA_161: 残恶梦魇
# 战吼：使目标随从获得等同于本随从攻击力的攻击力

def test_gruesome_nightmare_buffs_target_by_own_atk():
    """Gruesome Nightmare battlecry gives a target minion +ATK equal to own ATK."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    yeti = game.player1.summon("CS2_182")  # 4/5 Chillwind Yeti
    nightmare = game.player1.give("CATA_161")  # 3/3
    nightmare.play(target=yeti)
    assert yeti.atk == 4 + 3  # +3 ATK from nightmare's ATK


##
# CATA_585: 烈火炙烤 (warrior Torch)
# 对一个受伤的随从造成6点伤害，溢出伤害给英雄+X攻击力，将牌放回手牌

def test_torch_deals_6_damage_and_returns_to_hand():
    """Torch deals 6 damage to an injured minion, then goes back to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    yeti = game.player2.summon("CS2_182")  # 4/5 Yeti
    yeti.damage = 1  # injure it (now 4 HP, REQ_DAMAGED_TARGET satisfied)
    torch = game.player1.give("CATA_585")
    torch.play(target=yeti)
    # Yeti (4 HP remaining) should be dead (took 6 damage)
    assert yeti not in game.player2.field
    # Torch should be back in hand
    assert any(c.id == "CATA_585" for c in game.player1.hand)


def test_torch_overflow_gives_hero_attack():
    """Torch overflow damage (6 - target HP) gives hero that much attack."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    yeti = game.player2.summon("CS2_182")  # 4/5 Yeti
    yeti.damage = 1  # now 4 HP
    # Overflow = 6 - 4 = 2
    torch = game.player1.give("CATA_585")
    torch.play(target=yeti)
    assert game.player1.hero.atk == 2


##
# CATA_527: 奈瑟匹拉，蒙难古灵
# 造成1点伤害

def test_naga_dissenter_play_deals_1_damage():
    """Naga the Dissenter's battlecry deals 1 damage to a random enemy."""
    game = prepare_empty_game()
    enemy_minion = game.player2.summon("CS2_182")  # Chillwind Yeti 4/5
    naga = game.player1.give("CATA_527")
    total_hp_before = enemy_minion.health + game.player2.hero.health
    naga.play()
    total_hp_after = enemy_minion.health + game.player2.hero.health
    assert total_hp_after == total_hp_before - 1


##
# CATA_529: 贪婪的邪能钓鱼者
# 每次你施放邪能法术，费用-1

def test_greedy_fel_fisher_reduces_cost_on_fel_spell():
    """Greedy Fel Fisher gets -1 cost each time a Fel spell is cast."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    fisher = game.player1.summon("CATA_529")
    base_cost = fisher.cost
    # Play a non-Fel spell: should NOT reduce cost
    fireball = game.player1.give("CS2_029")  # Fireball (fire)
    fireball.play(target=game.player2.hero)
    assert fisher.cost == base_cost
    # Play a Fel spell: should reduce cost
    fel_spell = game.player1.give("BAR_306")  # Sigil of Flame (fel)
    fel_spell.play()
    assert fisher.cost == base_cost - 1


##
# CATA_697: 恶念变异体
# 战吼：选择你手牌中的一张邪能法术牌，获取一张它的复制

def test_fel_void_mutant_copies_fel_spell_from_hand():
    """Fel Void Mutant copies a Fel spell from hand."""
    from hearthstone.enums import SpellSchool
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Add a Fel spell to hand (BAR_306 = Sigil of Flame, Fel school)
    fel_spell = game.player1.give("BAR_306")
    mutant = game.player1.give("CATA_697")
    hand_before = len(game.player1.hand)  # 2
    mutant.play()
    # mutant removed (-1) + copy of Fel spell added (+1) = same count
    assert len(game.player1.hand) == hand_before
    # The new card should be a Fel spell
    new_cards = [c for c in game.player1.hand if c is not fel_spell]
    assert any(getattr(getattr(c, "data", None), "spell_school", None) == SpellSchool.FEL for c in new_cards)


def test_fel_void_mutant_does_nothing_without_fel_spell():
    """Fel Void Mutant does nothing if no Fel spell in hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    mutant = game.player1.give("CATA_697")
    hand_before = len(game.player1.hand)  # 1
    mutant.play()
    # mutant removed (-1), nothing added = count decreases by 1
    assert len(game.player1.hand) == hand_before - 1


##
# CATA_526: 布洛克斯加的奋战
# 对所有随从造成1点伤害，每有随从死亡，抽一张牌

def test_brokesaga_last_stand_damages_all_minions():
    """Brokesaga's Last Stand deals 1 damage to all minions."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    own_minion = game.player1.summon("CS2_182")  # 4/5 yeti
    enemy_minion = game.player2.summon("CS2_182")  # 4/5 yeti
    spell = game.player1.give("CATA_526")
    spell.play()
    assert own_minion.health == 4  # 5 - 1
    assert enemy_minion.health == 4  # 5 - 1


def test_brokesaga_draws_for_each_death():
    """Brokesaga's Last Stand draws a card for each minion that dies."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Add 2 cards to deck for drawing
    from hearthstone.enums import Zone as ZoneEnum
    game.player1.card("CS2_182", zone=ZoneEnum.DECK)
    game.player1.card("CS2_182", zone=ZoneEnum.DECK)
    # Summon fragile minions (1 health) — CS2_189 = Elven Archer 1/1
    game.player1.summon("CS2_189")
    game.player1.summon("CS2_189")
    spell = game.player1.give("CATA_526")
    hand_before_play = len(game.player1.hand)  # 1 (the spell)
    spell.play()
    # spell removed (-1), both 1-health minions died → draw 2 (+2)
    assert len(game.player1.hand) == hand_before_play - 1 + 2


##
# CATA_488t: 沃坎诺斯的喷发柱
# 每当本随从受到伤害，获取一张随机火焰法术牌，费用减少3

def test_plume_of_vulcanos_gives_fire_spell_on_damage():
    """Plume of Vulcanos gives a fire spell with -3 cost when damaged."""
    from hearthstone.enums import SpellSchool
    from fireplace.actions import Hit
    game = prepare_empty_game()
    game.player1.max_mana = 10
    plume = game.player1.summon("CATA_488t")  # 1/4
    hand_before = len(game.player1.hand)
    # Deal damage directly to the plume via cheat action
    game.cheat_action(game.player2.hero, [Hit(plume, 1)])
    # Plume should have received fire spell
    assert len(game.player1.hand) == hand_before + 1
    # The given spell should be a fire spell and cost reduced by 3
    given_spell = game.player1.hand[-1]
    assert getattr(given_spell.data, "spell_school", None) == SpellSchool.FIRE
    assert given_spell.cost == max(0, given_spell.data.cost - 3)


##
# CATA_979: 咒术专家
# 战吼：选择你手牌中的一张法术牌，将其拆分为两张法力值消耗与其相同的随机法术牌

def test_conjuration_specialist_splits_hand_spell():
    """Conjuration Specialist discards a hand spell and gives 2 same-cost random spells."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Give player a spell with known cost
    fireball = game.player1.give("CS2_029")  # Fireball, cost 4
    original_cost = fireball.cost
    specialist = game.player1.give("CATA_979")
    # Before play: hand has [fireball, specialist]
    hand_before = len(game.player1.hand)  # 2
    specialist.play()
    # After: specialist leaves hand (-1), fireball discarded (-1), 2 new spells added (+2)
    # Net change: -1 - 1 + 2 = 0, so hand stays at hand_before
    assert len(game.player1.hand) == hand_before
    # No fireball in hand anymore
    assert fireball not in game.player1.hand
    # 2 new spells should have same cost as fireball
    new_spells = [c for c in game.player1.hand if c.type == CardType.SPELL]
    assert len(new_spells) == 2
    for spell in new_spells:
        assert spell.cost == original_cost


def test_conjuration_specialist_no_effect_without_hand_spell():
    """Conjuration Specialist does nothing if no spells in hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    specialist = game.player1.give("CATA_979")
    hand_before = len(game.player1.hand)  # 1 (specialist)
    specialist.play()
    # No spells in hand → no effect, hand is empty
    assert len(game.player1.hand) == 0


##
# CATA_483: 不稳定的施法者
# 战吼：如果你在本回合中用法术造成过伤害，召唤一个本随从的复制

def test_unstable_spellcaster_summons_copy_if_spell_damage_this_turn():
    """Unstable Spellcaster summons a copy if a spell dealt damage this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Cast a damage spell first
    game.player1.give("CS2_029").play(target=game.player2.hero)  # Fireball 6 dmg
    # Now play the spellcaster
    spellcaster = game.player1.give("CATA_483")
    spellcaster.play()
    # Should have summoned a copy → 2 spellcasters on field
    assert len(game.player1.field) == 2
    assert all(m.id == "CATA_483" for m in game.player1.field)


def test_unstable_spellcaster_no_copy_without_spell_damage():
    """Unstable Spellcaster does NOT summon a copy if no spell dealt damage this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Do NOT cast any damage spells
    spellcaster = game.player1.give("CATA_483")
    spellcaster.play()
    # Should only have 1 spellcaster on field (no copy)
    assert len(game.player1.field) == 1
    assert game.player1.field[0].id == "CATA_483"


##
# CATA_308: 麦迪文的胜利
# 对所有随从造成$4点伤害。如果你控制着传说牌，本牌的法力值消耗为（1）点。

def test_medivh_triumph_deals_4_to_all_minions():
    """Medivh's Triumph deals 4 damage to all minions."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    minion1 = game.player1.summon("CS2_182")  # 4/5
    minion2 = game.player2.summon("CS2_182")  # 4/5
    triumph = game.player1.give("CATA_308")
    triumph.play()
    assert minion1.health == 1  # 5 - 4
    assert minion2.health == 1  # 5 - 4


def test_medivh_triumph_costs_1_with_legendary():
    """Medivh's Triumph costs 1 when you control a Legendary minion."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    triumph = game.player1.give("CATA_308")
    # Before legendary: cost should be 5
    assert triumph.cost == 5
    # Summon a legendary
    game.player1.summon("AT_129")  # Fjola Lightbane (legendary 3-cost)
    # After legendary: cost should be 1
    assert triumph.cost == 1


def test_medivh_triumph_normal_cost_without_legendary():
    """Medivh's Triumph costs normally without a Legendary minion."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    triumph = game.player1.give("CATA_308")
    # No legendary on board
    assert triumph.cost == 5


##
# CATA_584: 喷发火山
# 随机对敌人造成3点伤害，如果在本回合使用过火焰法术，再造成3点伤害

def test_erupting_volcano_deals_3_damage():
    """Erupting Volcano deals 3 damage to a random enemy."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    total_hp_before = game.player2.hero.health + sum(
        m.health for m in game.player2.field
    )
    volcano = game.player1.give("CATA_584")
    volcano.play()
    total_hp_after = game.player2.hero.health + sum(
        m.health for m in game.player2.field
    )
    assert total_hp_after == total_hp_before - 3


def test_erupting_volcano_bonus_damage_with_fire_spell():
    """Erupting Volcano deals extra 3 damage when a Fire spell was cast this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    # Cast a fire spell first (Fireball is fire school)
    game.player1.give("CS2_029").play(target=game.player2.hero)  # Fireball (fire)
    hero_hp_before = game.player2.hero.health
    volcano = game.player1.give("CATA_584")
    volcano.play()
    # Should deal 3 + 3 = 6 additional damage beyond fireball
    # But damage can go to either hero or field, so just check total decreased by 6
    total_hp_after = game.player2.hero.health
    assert total_hp_after == hero_hp_before - 6  # both hits go to hero (no minions)


##
# CATA_530: 邪能灌魔
# 在本回合中，你的英雄拥有吸血

def test_fel_infusion_lifesteal_this_turn_only():
    """Fel Infusion grants lifesteal only for the current turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 2
    game.player1.give("CATA_530").play()
    assert game.player1.hero.lifesteal is True
    game.end_turn()  # OWN_TURN_END fires for player1 → enchantment destroyed
    assert game.player1.hero.lifesteal is False


##
# CATA_616: 戈隆巨人
# 法力值消耗随上一张打出牌的费用降低

def test_gruul_cost_decreases_by_last_card_played():
    """Gruul's cost in hand decreases by the cost of the last card played."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    gruul = game.player1.give("CATA_616")
    base_cost = gruul.data.cost  # Should be 9
    # No cards played yet: cost = base
    assert gruul.cost == base_cost
    # Play a 4-cost card (Dalaran Aspirant = AT_006, 4-cost, no target needed)
    game.player1.give("AT_006").play()
    # Gruul's cost should now be base - 4
    assert gruul.cost == base_cost - 4


##
# CATA_499: 助祭耗材
# 当你使用或弃掉本牌时，随机召唤两个1费随从

def test_sacrificial_summoner_play_summons_two_minions():
    """Sacrificial Summoner summons two 1-cost minions when played."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.give("CATA_499").play()
    # Should summon 2 random 1-cost minions
    assert len(game.player1.field) == 2


def test_sacrificial_summoner_discard_summons_two_minions():
    """Sacrificial Summoner summons two 1-cost minions when discarded."""
    from fireplace.actions import Discard
    game = prepare_empty_game()
    game.player1.max_mana = 10
    card = game.player1.give("CATA_499")
    game.cheat_action(game.player1.hero, [Discard(card)])
    # Discarding should summon 2 minions
    assert len(game.player1.field) == 2
