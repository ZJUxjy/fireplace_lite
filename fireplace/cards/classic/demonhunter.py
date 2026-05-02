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


##
# Darkmoon Faire CORRUPT cards (additional)
# Each card declares `corrupt_form` pointing to its corrupted-state ID.

class DMF_061:
    """Faire Arborist"""
    # 3-cost minion. Choose One — Draw a card; or Summon a 2/2 Treant.
    # Corrupt: Do both.
    choose = ("DMF_061a", "DMF_061b")
    corrupt_form = "DMF_061t"


class DMF_061a:
    play = Draw(CONTROLLER)


class DMF_061b:
    play = Summon(CONTROLLER, "DMF_061t2")  # 2/2 Treant


class DMF_061t:
    """Faire Arborist (Corrupted)"""
    # Battlecry: Summon a 2/2 Treant. Draw a card.
    play = Summon(CONTROLLER, "DMF_061t2"), Draw(CONTROLLER)


class DMF_244:
    """Day at the Faire"""
    # Spell. Summon 3 Silver Hand Recruits. Corrupt: 5 instead.
    play = Summon(CONTROLLER, "CS2_101t") * 3
    corrupt_form = "DMF_244t"


class DMF_244t:
    """Day at the Faire (Corrupted)"""
    play = Summon(CONTROLLER, "CS2_101t") * 5


class DMF_703:
    """Pit Master"""
    # 3-cost. Battlecry: Summon a 3/2 Duelist. Corrupt: Summon two.
    play = Summon(CONTROLLER, "DMF_703t2")
    corrupt_form = "DMF_703t"


class DMF_703t:
    """Pit Master (Corrupted)"""
    play = Summon(CONTROLLER, "DMF_703t2") * 2


##
# Additional OUTCAST cards from various expansions.
# Effects are simplified where they require mechanics we haven't implemented
# (in-hand cost mods, Excavate, Spellburst, Corpses, look-at-opponent-hand).


class BAR_333:
    """Kurtrus Ashfallen"""
    # Battlecry: Attack the left and right-most enemy minions. Outcast: Immune this turn.
    play = (
        Attack(SELF, RANDOM_ENEMY_MINION),
        Attack(SELF, RANDOM_ENEMY_MINION),
    )
    outcast = Buff(FRIENDLY_HERO, "BAR_333e")


class BAR_333e:
    tags = {GameTag.CANT_BE_DAMAGED: True}
    events = OWN_TURN_END.on(Destroy(SELF))


class BTA_03:
    """Baduu, Outcast"""
    # Battlecry: Destroy an enemy minion. Outcast: Gain Stealth and Poisonous.
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    play = Destroy(TARGET)
    outcast = Buff(SELF, "BTA_03e")


class BTA_03e:
    tags = {GameTag.STEALTH: True, GameTag.POISONOUS: True}


class BTA_05:
    """Sklibb, Outcast"""
    # Adjacent minions have +1 Attack and Taunt. Outcast: Summon two 0/6 Glowcap Mushrooms.
    update = Refresh(ADJACENT(SELF), {GameTag.ATK: 1, GameTag.TAUNT: True})
    outcast = Summon(CONTROLLER, "BTA_05t") * 2


class BTA_05t:
    """Glowcap Mushroom"""
    pass


class BTA_06:
    """Sklibb, Demon Hunter"""
    # Aura: other friendly minions +2 Attack. Outcast: Summon 3 1/1 Illidari with Rush.
    update = Refresh(FRIENDLY_MINIONS - SELF, {GameTag.ATK: 2})
    outcast = Summon(CONTROLLER, "BT_036t") * 3


class BTA_07:
    """Karnuk, Outcast"""
    # Lifesteal. Your healing is doubled. Outcast: Summon a 2/5 Imprisoned Homunculus.
    # (Healing-doubling not implemented — treat as plain lifesteal.)
    outcast = Summon(CONTROLLER, "BTA_07t")


class BTA_07t:
    """Imprisoned Homunculus"""
    pass


class BTA_08:
    """Karnuk, Demon Hunter"""
    outcast = Summon(CONTROLLER, "BTA_08t")


class BTA_08t:
    """Imprisoned Antaen"""
    pass


class BTA_09:
    """Shalja, Outcast"""
    # Windfury, Rush. Outcast: Add 3 random Shaman spells to your hand.
    outcast = Give(CONTROLLER, RandomSpell(card_class=CardClass.SHAMAN)) * 3


class BTA_10:
    """Shalja, Demon Hunter"""
    # Outcast: Equip a random weapon and add 3 more to your hand.
    outcast = (
        Summon(CONTROLLER, RandomWeapon()),
        Give(CONTROLLER, RandomWeapon()) * 3,
    )


class CATA_533:
    """Flash Flood"""
    # 5-cost spell. Deal 5 to opponent's leftmost and rightmost minions.
    # Outcast: Do it again.
    play = (
        Hit(RANDOM_ENEMY_MINION, 5),
        Hit(RANDOM_ENEMY_MINION, 5),
    )
    outcast = (
        Hit(RANDOM_ENEMY_MINION, 5),
        Hit(RANDOM_ENEMY_MINION, 5),
    )


class END_005:
    """Bygone Echoes"""
    # Summon a random 4-Cost minion. Outcast: And another. (Skip Corpses spend.)
    play = Summon(CONTROLLER, RandomMinion(cost=4))
    outcast = Summon(CONTROLLER, RandomMinion(cost=4))


class GDB_116:
    """Eldritch Being"""
    # Outcast and Spellburst: Shuffle your hand. (Spellburst not implemented;
    # only Outcast variant fires here.)
    outcast = Shuffle(CONTROLLER, FRIENDLY_HAND)


class RLK_207:
    """Fierce Outsider"""
    # Rush. Outcast: Your next Outcast card costs (1) less.
    # (In-hand cost mod skipped — no effect at engine level.)
    pass


class SCH_356:
    """Glide"""
    # Spell. Shuffle your hand into your deck. Draw 4 cards. Outcast: opponent same.
    play = (
        Shuffle(CONTROLLER, FRIENDLY_HAND),
        Draw(CONTROLLER) * 4,
    )
    outcast = (
        Shuffle(CONTROLLER, FRIENDLY_HAND),
        Draw(CONTROLLER) * 4,
        Shuffle(OPPONENT, ENEMY_HAND),
        Draw(OPPONENT) * 4,
    )


class SCH_603:
    """Star Student Stelina"""
    # Outcast: Look at 3 enemy hand cards, shuffle 1 into deck.
    # (Look-at-opponent-hand UI not implemented — fallback: shuffle 1 random.)
    outcast = Bounce(RANDOM(ENEMY_HAND))


class SCH_702:
    """Felosophy"""
    # 1-cost spell. Copy the lowest Cost Demon in your hand. Outcast: both +1/+1.
    play = Give(CONTROLLER, ExactCopy(LOWEST_COST(FRIENDLY_HAND + DEMON)))
    outcast = (
        Give(CONTROLLER, ExactCopy(LOWEST_COST(FRIENDLY_HAND + DEMON))),
        Buff(FRIENDLY_HAND + DEMON, "SCH_702e"),
    )


SCH_702e = buff(atk=1, health=1)


class SCH_705:
    """Vilefiend Trainer"""
    # 4-cost minion. Outcast: Summon two 1/1 Demons. (Use vanilla 1/1 demon.)
    outcast = Summon(CONTROLLER, "SCH_705t") * 2


class SCH_705t:
    """Vilefiend"""
    pass


class SW_452:
    """Chaos Leech"""
    # 3-cost spell. Lifesteal. Deal 3 damage to a minion. Outcast: 5 instead.
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = Hit(TARGET, 3)
    outcast = Hit(TARGET, 5)


class TIME_021:
    """Doomsday Prepper"""
    # 5-cost minion. Outcast: Your hero is Immune until your next turn.
    outcast = Buff(FRIENDLY_HERO, "TIME_021e")


class TIME_021e:
    tags = {GameTag.CANT_BE_DAMAGED: True}
    events = OWN_TURN_BEGIN.on(Destroy(SELF))


class TOY_640:
    """Workshop Mishap"""
    # 4-cost spell. Deal 5 damage to a minion. Outcast: Gain Lifesteal.
    # (Excess-damage-to-neighbors skipped.)
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = Hit(TARGET, 5)
    outcast = Hit(TARGET, 5), Heal(FRIENDLY_HERO, 5)


class TOY_643:
    """Blind Box"""
    # 2-cost spell. Get 2 random Demons. Outcast: Discover them instead.
    play = Give(CONTROLLER, RandomDemon()) * 2
    outcast = Give(CONTROLLER, RandomDemon()) * 2  # simplified: same


class TOY_913:
    """Ci'Cigi"""
    # Battlecry/Outcast/Deathrattle: Get a random first-edition DH card.
    # (Approximated as a random DH card.)
    play = Give(CONTROLLER, RandomCollectible(card_class=CardClass.DEMONHUNTER))
    outcast = Give(CONTROLLER, RandomCollectible(card_class=CardClass.DEMONHUNTER))
    deathrattle = Give(CONTROLLER, RandomCollectible(card_class=CardClass.DEMONHUNTER))


class VAC_928:
    """Paraglide"""
    # 3-cost spell. Both players draw 3 cards. Outcast: Only you do.
    play = Draw(CONTROLLER) * 3, Draw(OPPONENT) * 3
    outcast = Draw(CONTROLLER) * 3


class WW_406:
    """Midnight Wolf"""
    # 6-cost minion. Rush. Outcast: Summon a copy of this.
    outcast = Summon(CONTROLLER, ExactCopy(SELF))
