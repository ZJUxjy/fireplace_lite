from ..utils import *


##
# Minions


class BT_142:
    """Shadowhoof Slayer"""

    # <b>Battlecry:</b> Give your hero +1_Attack this turn.
    play = Buff(CONTROLLER, "BT_142e")


BT_142e = buff(atk=1)


class BT_323:
    """Sightless Watcher"""

    # <b>Battlecry:</b> Look at 3 cards in your deck. Choose one to put on top.
    play = Choice(CONTROLLER, RANDOM(DeDuplicate(FRIENDLY_DECK)) * 3).then(
        PutOnTop(CONTROLLER, Choice.CARD)
    )


class BT_352:
    """Satyr Overseer"""

    # After your hero attacks, summon a 2/2 Satyr.
    events = Attack(FRIENDLY_HERO).after(Summon(CONTROLLER, "BT_352t"))


class BT_495:
    """Glaivebound Adept"""

    # <b>Battlecry:</b> If your hero attacked this turn, deal 4 damage.
    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE_AND_HERO_ATTACKED_THIS_TURN: 0,
    }
    powered_up = NUM_ATTACKS_THIS_TURN(FRIENDLY_HERO) > 0
    play = Hit(TARGET, 4)


##
# Spells


class BT_035:
    """Chaos Strike"""

    # Give your hero +2_Attack this turn. Draw a card.
    play = Buff(FRIENDLY_HERO, "BT_035e"), Draw(CONTROLLER)


BT_035e = buff(atk=2)


class BT_036:
    """Coordinated Strike"""

    # Summon three 1/1_Illidari with <b>Rush</b>.
    play = Summon(CONTROLLER, "BT_036t") * 3


class BT_235:
    """Chaos Nova"""

    # Deal $4 damage to all_minions.
    play = Hit(ALL_MINIONS, 4)


class BT_512:
    """Inner Demon"""

    # Give your hero +8_Attack this turn.
    play = Buff(FRIENDLY_HERO, "BT_512e")


BT_512e = buff(atk=8)


class BT_740:
    """Soul Cleave"""

    # <b>Lifesteal</b> Deal $2 damage to two random enemy minions.
    requirements = {PlayReq.REQ_MINIMUM_ENEMY_MINIONS: 1}
    play = Hit(RANDOM_ENEMY_MINION * 2, 2)


##
# Outcast cards from various expansions


class BAR_328:
    """Vengeful Spirit"""

    # Outcast: Draw 2 Deathrattle minions. (Simplified: draw 2 cards.)
    outcast = Draw(CONTROLLER), Draw(CONTROLLER)


class CS3_017:
    """Gan'arg Glaivesmith"""

    # Outcast: Give your hero +3 Attack this turn.
    outcast = Buff(FRIENDLY_HERO, "CS3_017e")


CS3_017e = buff(atk=3)


class DMF_227:
    """Dreadlord's Bite"""

    # Outcast: Deal 1 damage to all enemies.
    outcast = Hit(ENEMY_CHARACTERS, 1)
