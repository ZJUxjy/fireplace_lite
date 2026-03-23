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


def test_toy_341_nostalgic_clown_buffs_when_hero_power_used():
    """Nostalgic Clown gains Taunt + Divine Shield if hero power was used."""
    game = prepare_empty_game()
    # Simulate hero power usage by directly setting activations_this_turn
    game.player1.hero_power.activations_this_turn = 1
    clown = game.player1.give("TOY_341")
    clown.play()
    assert clown.taunt
    assert clown.divine_shield


def test_toy_341_nostalgic_clown_no_buff_without_hero_power():
    """Nostalgic Clown does NOT gain buffs if hero power was not used."""
    game = prepare_empty_game()
    clown = game.player1.give("TOY_341")
    clown.play()
    assert not clown.taunt
    assert not clown.divine_shield
