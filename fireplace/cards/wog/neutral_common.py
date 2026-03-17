from ..utils import *


##
# Minions


class OG_281:
    """Beckoner of Evil"""

    play = Buff(CTHUN, "OG_281e", atk=2, max_health=2)


class OG_283:
    """C'Thun's Chosen"""

    play = Buff(CTHUN, "OG_281e", atk=2, max_health=2)


class OG_284:
    """Twilight Geomancer"""

    play = Buff(CTHUN, "OG_284e")


OG_284e = buff(taunt=True)


class OG_286:
    """Twilight Elder"""

    events = OWN_TURN_END.on(Buff(CTHUN, "OG_281e", atk=1, max_health=1))


class OG_138:
    """Nerubian Prophet"""

    class Hand:
        events = OWN_TURN_BEGIN.on(Buff(SELF, "OG_138e"))


class OG_138e:
    events = REMOVED_IN_PLAY
    tags = {GameTag.COST: -1}


class OG_150:
    """Aberrant Berserker"""

    enrage = Refresh(SELF, buff="OG_150e")


OG_150e = buff(atk=2)


class OG_151:
    """Tentacle of N'Zoth"""

    deathrattle = Hit(ALL_MINIONS, 1)


class OG_156:
    """Bilefin Tidehunter"""

    play = Summon(CONTROLLER, "OG_156a")


class OG_158:
    """Zealous Initiate"""

    deathrattle = Buff(RANDOM_FRIENDLY_MINION, "OG_158e")


OG_158e = buff(+1, +1)


class OG_249:
    """Infested Tauren"""

    deathrattle = Summon(CONTROLLER, "OG_249a")


class OG_256:
    """Spawn of N'Zoth"""

    deathrattle = Buff(FRIENDLY_MINIONS, "OG_256e")


OG_256e = buff(+1, +1)


class OG_295:
    """Cult Apothecary"""

    play = Heal(FRIENDLY_HERO, Count(ENEMY_MINIONS) * 2)


class OG_323:
    """Polluted Hoarder"""

    deathrattle = Draw(CONTROLLER)


##
# Tokens (minions that are summoned by other cards)


class OG_006a:
    """Silver Hand Murloc"""
    tags = {}


class OG_031a:
    """Twilight Elemental"""
    tags = {}


class OG_061t:
    """Mastiff"""
    tags = {}


class OG_114a:
    """Icky Tentacle"""
    tags = {}


class OG_156a:
    """Ooze"""
    tags = {}


class OG_173a:
    """The Ancient One"""
    tags = {}


class OG_195c:
    """Wisp"""
    tags = {}


class OG_202c:
    """Slime"""
    tags = {}


class OG_216a:
    """Spider"""
    tags = {}


class OG_241a:
    """Shadowbeast"""
    tags = {}


class OG_249a:
    """Slime"""
    tags = {}


class OG_270a:
    """Nerubian Soldier"""
    tags = {}


class OG_272t:
    """Faceless Destroyer"""
    tags = {}


class OG_314b:
    """Slime"""
    tags = {}


class OG_318t:
    """Gnoll"""
    tags = {}


##
# Vanilla minions (no mechanics, just stats and keywords from tags)


class OG_141:
    """Faceless Behemoth"""
    # Vanilla minion - no special mechanics
    tags = {}


class OG_142:
    """Eldritch Horror"""
    # Vanilla minion - no special mechanics
    tags = {}


class OG_145:
    """Psych-o-Tron"""
    # Has Taunt and Divine Shield - these are in the card XML tags
    tags = {}


class OG_152:
    """Grotesque Dragonhawk"""
    # Has Windfury - this is in the card XML tags
    tags = {}


class OG_153:
    """Bog Creeper"""
    # Has Taunt - this is in the card XML tags
    tags = {}


class OG_247:
    """Twisted Worgen"""
    # Has Stealth - this is in the card XML tags
    tags = {}


class OG_248:
    """Am'gam Rager"""
    tags = {}


class OG_325:
    """Carrion Grub"""
    tags = {}


class OG_326:
    """Duskboar"""
    tags = {}


class OG_327:
    """Squirming Tentacle"""
    # Has Taunt - this is in the card XML tags
    tags = {}


class OG_340:
    """Soggoth the Slitherer"""
    # Has Taunt and Elusive - these are in the card XML tags
    tags = {}


##
# Enchantments (buffs that are applied by cards)


class OG_118e:
    """Renounce Darkness Deck Ench"""
    # Applied by OG_118 (Renounce Darkness) - makes cards cost (1) less
    events = REMOVED_IN_PLAY
    tags = {GameTag.COST: -1}


class OG_121e2:
    """Dark Power"""
    # Applied by Cho'gall - gives +5 damage to spell
    # This is applied to the spell damage
    tags = {}


class OG_202ae:
    """Y'Shaarj's Strength"""
    # Applied by Y'Shaarj
    tags = {}


class OG_281e:
    """Fanatic Devotion"""
    # Applied by C'Thun cards - gives +2/+2 to C'Thun
    # Note: This is handled via the buff function with atk=2, max_health=2
    tags = {}


class OG_282e:
    """Devotion of the Blade"""
    # Applied by a weapon buff
    tags = {}


class OG_290e:
    """Caller Devotion"""
    # Applied by cards that buff C'Thun
    tags = {}


class OG_293e:
    """Arrakoa Devotion"""
    # Applied by cards that buff C'Thun
    tags = {}


class OG_293f:
    """Dark Guardian"""
    # Applied by a card
    tags = {}


class OG_302e:
    """Soul Power"""
    # Applied by Usher of Souls - this is the C'Thun buff
    tags = {}


class OG_303e:
    """Sorcerous Devotion"""
    # Applied by cards that buff C'Thun
    tags = {}


class OG_312e:
    """Upgraded"""
    # Applied to weapon by N'Zoth's First Mate
    tags = {}


class OG_321e:
    """Power of Faith"""
    # Applied by a card
    tags = {}


class OG_339e:
    """Vassal's Subservience"""
    # Applied by a card
    tags = {}
