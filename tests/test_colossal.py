from utils import *


# 1. Field space validation
def test_colossal_requires_space():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # Fill field with 5 minions; CATA_432 has COLOSSAL=4 → needs 5 slots total (1 body + 4 limbs)
    # 5 existing + 5 needed = 10 > MAX_MINIONS_ON_FIELD(7), should NOT be summonable
    for _ in range(5):
        game.player1.give(WISP).play()
    assert len(game.player1.field) == 5
    chromatus = game.player1.give("CATA_432")
    assert not chromatus.is_summonable()


def test_colossal_just_fits():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    # With 2 minions already on field: 2 + 1 body + 4 limbs = 7 = MAX → still fits (< MAX check)
    for _ in range(2):
        game.player1.give(WISP).play()
    assert len(game.player1.field) == 2
    chromatus = game.player1.give("CATA_432")
    assert chromatus.is_summonable()


# 2. Limb positioning for Chromatus
def test_chromatus_limb_positions():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    chromatus = game.player1.give("CATA_432")
    chromatus.play()
    # Expected layout: [green(t1), red(t2), Chromatus, blue(t3), bronze(t4)]
    field = game.player1.field
    assert len(field) == 5
    assert field[0].id == "CATA_432t1"  # green head (left)
    assert field[1].id == "CATA_432t2"  # red head (left)
    assert field[2].id == "CATA_432"    # body in middle
    assert field[3].id == "CATA_432t3"  # blue head (right)
    assert field[4].id == "CATA_432t4"  # bronze head (right)


# 3. Body death kills all limbs
def test_colossal_body_death_kills_limbs():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    chromatus = game.player1.give("CATA_432")
    chromatus.play()
    field_before = list(game.player1.field)
    assert len(field_before) == 5
    # Kill the body
    chromatus.destroy()
    assert len(game.player1.field) == 0


# 4. Limb deathrattle modifies body's tags
def test_chromatus_green_head_deathrattle():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    chromatus = game.player1.give("CATA_432")
    chromatus.play()
    assert chromatus.taunt
    # Kill the green head (index 0)
    green_head = game.player1.field[0]
    assert green_head.id == "CATA_432t1"
    green_head.destroy()
    assert not chromatus.taunt


def test_chromatus_red_head_deathrattle():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    chromatus = game.player1.give("CATA_432")
    chromatus.play()
    assert chromatus.lifesteal
    red_head = game.player1.field[1]
    assert red_head.id == "CATA_432t2"
    red_head.destroy()
    assert not chromatus.lifesteal


# 5. Gul'dan arm is on left
def test_guldan_arm_on_left():
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    guldan = game.player1.give("CATA_726")
    guldan.play()
    # Expected: [arm(t), Gul'dan, soldier(t1)]
    field = game.player1.field
    assert len(field) == 3
    assert field[0].id == "CATA_726t"   # arm on left
    assert field[1].id == "CATA_726"    # body
    assert field[2].id == "CATA_726t1"  # soldier on right
