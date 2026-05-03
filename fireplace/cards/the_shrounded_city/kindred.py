from ..utils import *


##
# KINDRED (Year of the Raptor / The Lost City). Conditional bonus that
# fires when the controller already has another minion of the same race
# on the board at play time. Engine support: PlayableCard.play_kindred
# checks the race overlap; actions.Play.do triggers the `kindred` script
# additively to any battlecry.


# DINO_138 — Diabolus Rex (Demon Hunter 6-cost legendary, Beast).
# Kindred: Deal 6 damage to your opponent's left and right-most minions.
# Simplified: deal 6 to two random enemy minions (no leftmost/rightmost
# selectors in fireplace).
class DINO_138:
    """Diabolus Rex"""
    kindred = Hit(RANDOM_ENEMY_MINION, 6), Hit(RANDOM_ENEMY_MINION, 6)


# DINO_404 — Firegill (Paladin 2-cost, Murloc).
# Kindred: Give your other minions Rush.
class DINO_404:
    """Firegill"""
    kindred = SetTags(FRIENDLY_MINIONS - SELF, {GameTag.RUSH: True})


# DINO_413 — Chillspine Stegodon (Shaman 4-cost, Beast).
# Battlecry: Deal 2 damage to two random enemy minions. Kindred: And Freeze them.
# Simplified: Kindred freezes two random enemy minions (which approximates
# "the same minions" since we can't easily reference the battlecry's targets).
class DINO_413:
    """Chillspine Stegodon"""
    play = Hit(RANDOM_ENEMY_MINION, 2), Hit(RANDOM_ENEMY_MINION, 2)
    kindred = Freeze(RANDOM_ENEMY_MINION), Freeze(RANDOM_ENEMY_MINION)


# TLC_102 — Torga (Neutral 4-cost, Beast).
# Kindred: Restore 4 Health to your hero. (Simplified — actual card text
# may differ, this is a representative implementation.)
class TLC_102:
    """Torga"""
    kindred = Heal(FRIENDLY_HERO, 4)


# TLC_107 — Stormbrewer (Neutral 5-cost, Elemental).
# Kindred: Deal 3 damage to all enemy minions.
class TLC_107:
    """Stormbrewer"""
    kindred = Hit(ENEMY_MINIONS, 3)


# TLC_223 — Volcanic Thrasher (Shaman 3-cost, Elemental).
# Kindred: +2/+2.
class TLC_223:
    """Volcanic Thrasher"""
    kindred = Buff(SELF, "TLC_223e")


TLC_223e = buff(atk=2, health=2)


# TLC_226 — Conjured Bookkeeper (Mage 3-cost, Elemental).
# Kindred: Draw a card.
class TLC_226:
    """Conjured Bookkeeper"""
    kindred = Draw(CONTROLLER)


# TLC_243 — Whirling Stormdrake (Neutral 9-cost, Elemental).
# Kindred: Deal damage equal to its Attack to a random enemy. (Simplified
# to a flat 6 — modeling "this card's atk" needs ATK(SELF) at trigger time.)
class TLC_243:
    """Whirling Stormdrake"""
    kindred = Hit(RANDOM_ENEMY_CHARACTER, 6)
