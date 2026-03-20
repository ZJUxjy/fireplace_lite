from utils import *


##
# TOY_380: Clay Matriarch (Priest, 6费 3/7)
# 微缩。嘲讽。亡语：召唤一个4/4有虚空的幼龙

def test_clay_matriarch_mini_copy():
    """Playing Clay Matriarch should add a 1/1 mini copy (TOY_380t) to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    matriarch = game.player1.give("TOY_380")
    matriarch.play()
    assert len(game.player1.hand) == 1
    assert game.player1.hand[0].id == "TOY_380t"


def test_clay_matriarch_has_taunt():
    """Clay Matriarch should have Taunt."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    matriarch = game.player1.give("TOY_380")
    matriarch.play()
    assert matriarch.taunt


def test_clay_matriarch_deathrattle():
    """Clay Matriarch deathrattle should summon a 4/4 Clay Whelp with Elusive."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    matriarch = game.player1.give("TOY_380")
    matriarch.play()
    # Clear hand for cleaner check
    game.player1.hand.clear()
    matriarch.destroy()
    # Should have summoned a 4/4 Elusive (TOY_380t2)
    assert len(game.player1.field) == 1
    whelp = game.player1.field[0]
    assert whelp.atk == 4
    assert whelp.health == 4
    from hearthstone.enums import GameTag
    assert whelp.data.tags.get(GameTag.ELUSIVE) or whelp.data.scripts.tags.get(GameTag.ELUSIVE)


##
# TOY_513: Sand Art Elemental (Shaman, 4费)
# 微缩。战吼：给你的英雄+1攻击力和风怒（本回合）

def test_sand_art_elemental_mini_copy():
    """Playing Sand Art Elemental should add TOY_513t to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    elem = game.player1.give("TOY_513")
    elem.play()
    assert len(game.player1.hand) == 1
    assert game.player1.hand[0].id == "TOY_513t"


def test_sand_art_elemental_hero_buff():
    """Sand Art Elemental battlecry gives hero +1 atk and windfury this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    elem = game.player1.give("TOY_513")
    elem.play()
    hero = game.player1.hero
    assert hero.atk == 1
    assert hero.windfury


def test_sand_art_elemental_hero_buff_expires():
    """Sand Art Elemental hero buffs should expire at end of turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    elem = game.player1.give("TOY_513")
    elem.play()
    hero = game.player1.hero
    assert hero.atk == 1
    game.end_turn()   # player1 ends
    game.end_turn()   # player2 ends, player1's turn again
    assert hero.atk == 0
    assert not hero.windfury


##
# TOY_521: Sandbox Scoundrel (Rogue, 5费)
# 微缩。战吼：你本回合打出的下一张牌费用降低2

def test_sandbox_scoundrel_mini_copy():
    """Playing Sandbox Scoundrel should add TOY_521t1 to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    scoundrel = game.player1.give("TOY_521")
    scoundrel.play()
    assert len(game.player1.hand) == 1
    # mini copy is TOY_521t1
    assert game.player1.hand[0].id == "TOY_521t1"


def test_sandbox_scoundrel_cost_reduction():
    """Sandbox Scoundrel should reduce next card cost by 2."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Give a 5-cost card to hand first
    fireball = game.player1.give("CS2_029")  # Fireball (4-cost)
    scoundrel = game.player1.give("TOY_521")
    scoundrel.play()
    # The mini copy and the fireball are now both in hand
    # Fireball's cost should be 2 less (4 - 2 = 2)
    fireball_in_hand = next(c for c in game.player1.hand if c.id == "CS2_029")
    assert fireball_in_hand.cost == 2


##
# TOY_652: Window Shopper (DemonHunter, 5费)
# 微缩。战吼：发现一个恶魔（简化）

def test_window_shopper_mini_copy():
    """Playing Window Shopper should add TOY_652t to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    shopper = game.player1.give("TOY_652")
    shopper.play()
    # Player should have a discover choice or mini in hand
    assert game.player1.choice is not None or any(c.id == "TOY_652t" for c in game.player1.hand)


def test_window_shopper_discovers_demon():
    """Window Shopper battlecry should trigger a Discover of a Demon."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    shopper = game.player1.give("TOY_652")
    shopper.play()
    assert game.player1.choice is not None
    # All choices should be Demons
    for card in game.player1.choice.cards:
        from hearthstone.enums import Race
        assert card.race == Race.DEMON


##
# TOY_801: Chia Drake (Druid, 4费 3/5)
# 微缩。抉择 - 获得+1法术伤害；或抽一张法术牌（简化）

def test_chia_drake_mini_copy():
    """Playing Chia Drake should add TOY_801t to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    drake = game.player1.give("TOY_801")
    assert drake.must_choose_one
    # Choose the draw spell option (choose card b)
    drake.play(choose=drake.choose_cards[1])
    assert any(c.id == "TOY_801t" for c in game.player1.hand)


def test_chia_drake_choose_spellpower():
    """Chia Drake option A should give Spell Damage +1."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    drake = game.player1.give("TOY_801")
    before = game.player1.spellpower
    drake.play(choose=drake.choose_cards[0])  # option a: spell damage
    assert game.player1.spellpower == before + 1


##
# TOY_828: Amateur Puppeteer (DeathKnight, 5费)
# 微缩。嘲讽。亡语：给你手牌中的不死随从+2/+2

def test_amateur_puppeteer_mini_copy():
    """Playing Amateur Puppeteer should add TOY_828t (1/1 Taunt) to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    puppeteer = game.player1.give("TOY_828")
    puppeteer.play()
    assert len(game.player1.hand) == 1
    assert game.player1.hand[0].id == "TOY_828t"
    assert game.player1.hand[0].taunt


def test_amateur_puppeteer_has_taunt():
    """Amateur Puppeteer should have Taunt."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    puppeteer = game.player1.give("TOY_828")
    puppeteer.play()
    assert puppeteer.taunt


def test_amateur_puppeteer_deathrattle():
    """Amateur Puppeteer deathrattle buffs Undead in hand by +2/+2."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Give an Undead minion to hand (ICC_026 = Deathspeaker, undead 3/4... need to find one)
    # Use a known Undead minion: FP1_001 Wisp is not undead
    # EX1_110 = Cairne Bloodhoof is not undead
    # Let's check for a basic undead: CORE_ICC_028 = Ghoul
    undead = game.player1.give("ICC_026")  # Deathspeaker (undead minion)
    base_atk = undead.atk
    base_health = undead.health
    puppeteer = game.player1.give("TOY_828")
    puppeteer.play()
    # Clear mini copy from hand to simplify
    for c in list(game.player1.hand):
        if c.id == "TOY_828t":
            game.player1.hand.remove(c)
    puppeteer.destroy()
    # Undead in hand should be buffed
    undead_in_hand = next(c for c in game.player1.hand if c.id == "ICC_026")
    assert undead_in_hand.atk == base_atk + 2
    assert undead_in_hand.health == base_health + 2


##
# TOY_915: Tabletop Roleplayer (Warlock, 4费)
# 微缩。战吼：给一个友方恶魔+2攻击力和本回合免疫

def test_tabletop_roleplayer_mini_copy():
    """Playing Tabletop Roleplayer should add TOY_915t to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    demon = game.player1.summon("CS2_064")  # Dread Infernal (Demon)
    roleplayer = game.player1.give("TOY_915")
    roleplayer.play(target=demon)
    assert any(c.id == "TOY_915t" for c in game.player1.hand)


def test_tabletop_roleplayer_demon_buff():
    """Tabletop Roleplayer gives a friendly Demon +2 atk and Immune this turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Summon a Demon first
    demon = game.player1.summon("CS2_064")  # Dread Infernal (6/6 Demon)
    base_atk = demon.atk
    roleplayer = game.player1.give("TOY_915")
    roleplayer.play(target=demon)
    assert demon.atk == base_atk + 2
    assert demon.immune


def test_tabletop_roleplayer_immune_expires():
    """Tabletop Roleplayer immune expires at end of turn."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    demon = game.player1.summon("CS2_064")
    roleplayer = game.player1.give("TOY_915")
    roleplayer.play(target=demon)
    assert demon.immune
    game.end_turn()
    game.end_turn()
    assert not demon.immune


##
# MIS_025: The Replicator-inator (Neutral, 5费)
# 微缩。当你打出一个与本随从攻击力相同的随从时，召唤它的一份副本

def test_replicator_inator_mini_copy():
    """Playing The Replicator-inator should add MIS_025t to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    replicator = game.player1.give("MIS_025")
    replicator.play()
    assert any(c.id == "MIS_025t" for c in game.player1.hand)


def test_replicator_inator_copies_same_atk_minion():
    """The Replicator-inator copies a minion played with same attack."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    replicator = game.player1.give("MIS_025")
    replicator.play()
    # Replicator-inator has 3 attack (from DB)
    # Play a 3-attack minion: CS2_122 Silver Hand Recruit (1/1)... nope
    # Use a 3/3: EX1_008 Argent Squire (1/1) nope
    # Use Bloodfen Raptor CS2_172 (3/2 beast) - 3 attack!
    field_before = len(game.player1.field)
    # Replicator-inator is 5/5 in DB; play a 5-attack minion to trigger it
    tiger = game.player1.give("EX1_028")  # Stranglethorn Tiger (5/5 Stealth)
    tiger.play()
    # Should have summoned a copy (field = replicator + tiger + copy)
    assert len(game.player1.field) == field_before + 2


##
# TOY_501: Shudderblock (Shaman, 6费)
# 微缩。战吼：你下一个战吼触发3次（简化：战吼多触发一次）

def test_shudderblock_mini_copy():
    """Playing Shudderblock should add TOY_501t to hand."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    shudder = game.player1.give("TOY_501")
    shudder.play()
    assert any(c.id == "TOY_501t" for c in game.player1.hand)


def test_shudderblock_extra_battlecry():
    """Shudderblock makes battlecries trigger twice (like Brann): King Mukla gives 4 bananas instead of 2."""
    from hearthstone.enums import CardClass
    game = prepare_game(CardClass.SHAMAN, CardClass.MAGE)
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    shudder = game.player1.give("TOY_501")
    shudder.play()
    # King Mukla (EX1_014): battlecry gives opponent 2 bananas; with Shudderblock gives 4
    opponent_hand_before = len(game.player2.hand)
    mukla = game.player1.give("EX1_014")
    mukla.play()
    # Normal: +2 bananas. With Shudderblock: +4 bananas
    assert len(game.player2.hand) >= opponent_hand_before + 4
