from utils import *
from hearthstone.enums import Zone


##
# neutral.py

def test_toy_312_nostalgic_gnome_draws_on_kill():
    """Nostalgic Gnome draws a card after killing a minion."""
    game = prepare_empty_game()
    gnome = game.player1.summon("TOY_312")  # 4/4 Rush
    target = game.player2.summon("CS2_189")  # Elven Archer 1/1
    # Add a card to deck so Draw has something to draw
    c = game.player1.card("CS2_029")
    c.zone = Zone.DECK
    hand_before = len(game.player1.hand)
    game.attack(gnome, target)
    assert target.dead
    assert len(game.player1.hand) == hand_before + 1


def test_toy_312_nostalgic_gnome_no_draw_on_non_lethal():
    """Nostalgic Gnome does NOT draw a card when attack is non-lethal."""
    game = prepare_empty_game()
    gnome = game.player1.summon("TOY_312")  # 4/4 Rush
    champ = game.player2.summon("CS2_222")  # Stormwind Champion 6/6
    c = game.player1.card("CS2_029")
    c.zone = Zone.DECK
    hand_before = len(game.player1.hand)
    game.attack(gnome, champ)
    assert not champ.dead
    assert len(game.player1.hand) == hand_before


def test_toy_341_nostalgic_clown_deals_damage_after_higher_cost_card():
    """Nostalgic Clown deals 4 if a higher Cost card was played while held."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    clown = game.player1.give("TOY_341")
    target = game.player2.summon("CS2_200")
    game.player1.give("CS2_200").play()
    game.player1.used_mana = 0
    clown.play(target=target)
    assert target.damage == 4


def test_toy_341_nostalgic_clown_no_damage_without_higher_cost_card():
    """Nostalgic Clown does not deal damage without the while-held condition."""
    game = prepare_empty_game()
    game.player1.max_mana = 10
    game.player1.used_mana = 0
    clown = game.player1.give("TOY_341")
    target = game.player2.summon("CS2_200")
    clown.play(target=target)
    assert target.damage == 0
