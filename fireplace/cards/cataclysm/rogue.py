from ..utils import *
from hearthstone.enums import GameTag


##
# Minions

# CATA_154: Sinestra (希奈丝特拉)
# 6 cost 5/5 Dragon
# <b>Colossal +2</b>
# Your other class spells are cast twice.
class CATA_154:
    # Colossal minion - triggers when played
    play = Summon(CONTROLLER, "CATA_154t1") * 2, Buff(CONTROLLER, "CATA_154e")


CATA_154e = buff(echo=True)  # Spells cost 0 extra but echo effect


# CATA_158: Maniacal Follower (癫狂的追随者)
# 3 cost 3/1
# <b>Stealth</b>. <b>Deathrattle:</b> <b>Herald</b>.
class CATA_158:
    deathrattle = Summon(CONTROLLER, "CATA_158t")


# CATA_200: Agent of the Old Ones (古神的眼线)
# 1 cost 2/1 Murloc
# <b>Battlecry:</b> Choose a card in your hand. Transform it into a Lucky Coin.
class CATA_200:
    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Morph(TARGET, "GAME_005")


# CATA_201: Twilight Mistress (暮光主母)
# 9 cost 4/12 Dragon
# <b>Battlecry:</b> Return all enemy minions to their owner's hand.
class CATA_201:
    play = Bounce(ENEMY_MINIONS)


# CATA_481: Iso'rath (厄索拉斯)
# 5 cost 5/3
# <b>Battlecry:</b> Swallow 2 random cards from opponent's hand, then <b>Dormant</b> for 2 turns.
# <b>Deathrattle:</b> Return the swallowed cards.
# Note: Dormant is complex to implement - simplified to just deathrattle
class CATA_481:
    deathrattle = (
        Give(OPPONENT, RANDOM(ENEMY_HAND)),
        Give(OPPONENT, RANDOM(ENEMY_HAND)),
    )


# CATA_786: Chaos Supplicant (混沌祈求者)
# 4 cost 3/5
# After you cast a spell, randomly cast a spell from another class that costs the same.
class CATA_786:
    events = OWN_SPELL_PLAY.after(
        CastSpell(RandomSpell(card_class=ANOTHER_CLASS))
    )


##
# Spells

# CATA_202: Stolen Power (能量窃取)
# 3 cost
# Discover a <b>Twisted</b> card from another class.
class CATA_202:
    play = Discover(CONTROLLER, RandomCard(type=CardType.SPELL, card_class=ANOTHER_CLASS))


# CATA_203: Garona's Last Stand (迦罗娜的奋战)
# 2 cost
# <b>Tradeable</b>
# Destroy a <b>Legendary</b> minion.
class CATA_203:
    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_LEGENDARY_TARGET: 0,
    }
    play = Destroy(TARGET)


# CATA_215: Daze (眩晕)
# 3 cost
# Return an enemy minion to its owner's hand. It can't be used next turn.
class CATA_215:
    requirements = {
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Bounce(TARGET), Buff(TARGET, "CATA_215e")


class CATA_215e:
    events = OWN_TURN_BEGIN.on(UnsetTag(SELF, GameTag.CANT_ATTACK))


# CATA_785: Rite of Twilight (暮光祭礼)
# 2 cost
# <b>Herald</b>. <b>Combo:</b> Deal $3 damage.
class CATA_785:
    play = Hit(TARGET, 3)
    combo = Hit(TARGET, 3)
