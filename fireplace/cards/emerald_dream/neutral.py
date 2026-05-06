# Neutral cards from EMERALD_DREAM expansion
from ..utils import *
from hearthstone.enums import SpellSchool


##
# Minions


class EDR_000:
    """Ysera, Emerald Aspect"""

    events = OWN_TURN_BEGIN.on(
        Give(CONTROLLER, RandomSpell())
    )


class EDR_001:
    """Hopeful Dryad"""

    divine_shield = True
    play = Give(CONTROLLER, RandomCard())


class CORE_EDR_001:
    """Babbling Bookcase"""

    play = Give(CONTROLLER, RandomSpell(card_class=CardClass.MAGE)) * 2


class CORE_EDR_003_DrawCorpseSpender(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spenders = [
            card
            for card in player.deck
            if "Spend" in card.description and "Corpse" in card.description
        ]
        if spenders:
            return source.game.queue_actions(
                source, [ForceDraw(source.game.random.choice(spenders))]
            )


class CORE_EDR_003_GainCorpse(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, falric):
        falric.controller.corpses = getattr(falric.controller, "corpses", 0) + 2


class CORE_EDR_003:
    """Falric"""

    play = CORE_EDR_003_DrawCorpseSpender(CONTROLLER)
    events = Death(FRIENDLY + MINION - SELF).on(CORE_EDR_003_GainCorpse(SELF))


class CORE_EDR_004_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        if getattr(self.source, "_core_edr_004_discount", False):
            self.source.game.queue_actions(self.source, [Buff(card, "CORE_EDR_004e")])
        self.source.game.queue_actions(self.source, [EDR_DarkGift(card), Give(self.player, card)])
        self.trigger_choice_callback()


class CORE_EDR_004_Discover(TargetedAction):
    TARGET = ActionArg()

    def _card_races(self, card):
        races = set(getattr(card, "races", []) or [])
        races.update(getattr(getattr(card, "data", None), "races", []) or [])
        return races

    def _kindred(self, source):
        source_races = self._card_races(source)
        return any(
            played.type == CardType.MINION
            and source_races.intersection(self._card_races(played))
            for played in getattr(source.controller, "cards_played_last_turn", [])
        )

    def do(self, source, player):
        source._core_edr_004_discount = self._kindred(source)
        cards = []
        for card_id, data in db.items():
            if (
                data.collectible
                and data.type == CardType.MINION
                and Race.BEAST in data.races
                and (not source.game.is_standard or data.is_standard)
            ):
                cards.append(player.card(card_id, source=source))
        source.game.random.shuffle(cards)
        return source.game.queue_actions(source, [CORE_EDR_004_Choice(player, cards[:3])])


@custom_card
class CORE_EDR_004e:
    tags = {
        GameTag.CARDNAME: "Raptor Herald",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


class CORE_EDR_004:
    """Raptor Herald"""

    play = CORE_EDR_004_Discover(CONTROLLER)


class EDR_102:
    """Treacherous Tormentor"""

    battlecry = Discover(RandomMinion(rarity=Rarity.LEGENDARY))


class EDR_102t:
    """Dark Gift"""

    deathrattle = Buff(FRIENDLY_MINIONS, "+2/+2")


@custom_card
class EDR_DG_ATTACK_LIFESTEAL:
    """Dark Gift"""

    tags = {
        GameTag.CARDNAME: "Dark Gift",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 3,
        GameTag.LIFESTEAL: 1,
    }
    lifesteal = True


@custom_card
class EDR_DG_HEALTH_TAUNT:
    """Dark Gift"""

    tags = {
        GameTag.CARDNAME: "Dark Gift",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.HEALTH: 4,
        GameTag.TAUNT: 1,
    }
    taunt = True


@custom_card
class EDR_DG_CHARGE:
    """Dark Gift"""

    tags = {
        GameTag.CARDNAME: "Dark Gift",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.CHARGE: 1,
    }
    charge = True


@custom_card
class EDR_DG_REBORN:
    """Dark Gift"""

    tags = {
        GameTag.CARDNAME: "Dark Gift",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.REBORN: 1,
    }
    reborn = True


class EDR_105:
    """Creature of Madness"""

    battlecry = Discover(RandomMinion(cost=3))


class EDR_110:
    """Sporegnasher"""

    deathrattle = Hit(RANDOM(ENEMY_MINIONS), 1)


class EDR_254:
    """Animated Moonwell"""

    events = Attack(SELF).on(Heal(TARGET, 1))


class EDR_254e1:
    """Overflowing"""

    pass


class EDR_260:
    """Illusory Greenwing"""

    deathrattle = Shuffle(CONTROLLER, "EDR_260t") * 2


class EDR_260t:
    """Illusion"""

    draw = Summon(CONTROLLER, SELF)


class EDR_260te:
    """Illusion"""

    pass


class EDR_453:
    """Briarspawn Drake"""

    events = OWN_TURN_END.on(Damage(RANDOM_ENEMY_MINION, 1))


class EDR_469:
    """Slumbering Sprite"""

    events = OWN_TURN_BEGIN.on(Buff(SELF, "EDR_469e"))


class EDR_469e:
    """Knighttime"""

    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


class EDR_470:
    """Barkshield Sentinel"""

    events = Attack(SELF).on(Buff(SELF, "EDR_470e"))


class EDR_470e:
    """Alert"""

    tags = {GameTag.ATK: 1}


class EDR_484:
    """Scavenging Flytrap"""

    events = Death(FRIENDLY_MINIONS).on(Buff(SELF, "EDR_484e"))


class EDR_484e:
    """Scavenging"""

    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


class EDR_486:
    """Scorching Observer"""

    rush = True
    lifesteal = True


class EDR_492:
    """Mother Duck"""

    play = Summon(CONTROLLER, "EDR_492t") * 3


class EDR_492t:
    """Duckling"""

    rush = True


class EDR_493e:
    """Demon Cost"""

    pass


class EDR_495:
    """Twisted Treant"""

    deathrattle = Buff(RANDOM(FRIENDLY_HAND + MINION), "EDR_495e"), Buff(
        RANDOM(ENEMY_HAND + MINION), "EDR_495e"
    )


EDR_495e = buff(atk=-2)


class EDR_500:
    """Fleeing Treant"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")
    events = OWN_TURN_END.on(Buff(SELF, "EDR_500e"))


class EDR_500e:
    """Run, Forest!"""

    pass


class EDR_530:
    """Daydreaming Pixie"""

    events = OWN_TURN_END.on(Give(CONTROLLER, RandomSpell()))


class EDR_571:
    """Fae Trickster"""

    deathrattle = Give(CONTROLLER, RandomSpell(cost=5))


class EDR_572:
    """Tormented Dreadwing"""

    deathrattle = Draw(CONTROLLER).then(
        Buff(Draw.TARGET, "-1")
    ) * 2


class EDR_598:
    """Dream Rager"""

    events = Death(FRIENDLY_MINIONS).on(Buff(SELF, "+3/+1"))


class EDR_780:
    """Bloodthistle Illusionist"""

    play = Summon(CONTROLLER, "EDR_780")


class EDR_780e:
    """Illusion?"""

    pass


class EDR_780e1:
    """Illusion?"""

    pass


class EDR_800:
    """Flutterwing Guardian"""

    divine_shield = True
    taunt = True
    battlecry = Summon(CONTROLLER, "CS2_101t")


class EDR_812e:
    """Unholy Corruption"""

    pass


class EDR_812e1:
    """Bloody Corruption"""

    pass


class EDR_844:
    """Naralex, Herald of the Flights"""

    events = OWN_TURN_BEGIN.on(Summon(CONTROLLER, RandomMinion(cost=3)))


class EDR_846t1:
    """Corrupted Nightmare"""

    play = Buff(TARGET, "+5/+5")


class EDR_846t1e:
    """Nightmare"""

    pass


class EDR_846t2:
    """Corrupted Dream"""

    deathrattle = Shuffle(TARGET, Copy(TARGET))


class EDR_846t3:
    """Corrupted Laughing Sister"""

    elusive = True


class EDR_846t3e:
    """Laughing"""

    pass


class EDR_846t4:
    """Corrupted Awakening"""

    play = Damage(ENEMY_MINIONS + ENEMY_HERO, 5)


class EDR_846t5:
    """Corrupted Drake"""

    deathrattle = Damage(ENEMY_MINIONS + ENEMY_HERO, 1)


class EDR_846te2:
    """Eternal Nightmare"""

    pass


class EDR_846:
    """Shaladrassil"""

    class Hand:
        events = OWN_TURN_BEGIN.on(
            Summon(CONTROLLER, RandomMinion(cost=3))
        )


class EDR_846t1e:
    """Nightmare"""

    pass


class EDR_846t3e:
    """Laughing"""

    pass


class EDR_846te2:
    """Eternal Nightmare"""

    pass


class EDR_849:
    """Dreambound Raptor"""

    events = Play(ALL_MINIONS).on(Buff(Play.TARGET, "CS2_101e"))


class EDR_852:
    """Bitterbloom Knight"""

    deathrattle = Summon(CONTROLLER, "CS2_101t")


class EDR_856:
    """Nightmare Lord Xavius"""

    battlecry = Discover(RANDOM_FRIENDLY_MINION).then(
        Buff(Discover.TARGET, "CS2_101e")
    )


class EDR_860:
    """Resplendent Dreamweaver"""

    events = OWN_TURN_END.on(Buff(RANDOM_FRIENDLY_MINION, "CS2_101e"))


class EDR_861:
    """Tranquil Treant"""

    taunt = True
    deathrattle = GainMana(CONTROLLER, 1), GainMana(OPPONENT, 1)


class EDR_873:
    """Envoy of the Glade"""

    taunt = True


class EDR_888:
    """Malorne the Waywatcher"""

    battlecry = Discover(RandomMinion(rarity=Rarity.LEGENDARY, race=Race.BEAST))
    deathrattle = Shuffle(CONTROLLER, "EDR_888")


class EDR_889:
    """Petal Peddler"""

    events = OWN_TURN_END.on(Buff(RANDOM_OTHER_FRIENDLY_MINION, "CS2_101e"))


class EDR_889e:
    """Flowery"""

    pass


class EDR_940_MageEndTurn(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        wisps = len(player.field.filter(id="EDR_851t"))
        return source.game.queue_actions(source, [GainArmor(player.hero, 1 + wisps)])


class EDR_940:
    """Merry Moonkin"""

    events = OWN_TURN_END.on(EDR_940_MageEndTurn(CONTROLLER))


class EDR_942:
    """Curious Cumulus"""

    deathrattle = Summon(CONTROLLER, RandomMinion(cost=4))
    events = OWN_TURN_END.on(GainArmor(FRIENDLY_HERO, 1))


class EDR_950:
    """Sharp-Eyed Lookout"""

    play = Draw(CONTROLLER).then(Buff(Draw.TARGET, "EDR_950e1"))


class EDR_950e1:
    tags = {GameTag.COST: -1}


class EDR_971:
    """Critter Caretaker"""

    events = OWN_TURN_END.on(Heal(ALL_HEROES, 3))


class EDR_978_BottomDeck(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if len(player.deck) >= player.max_deck_size:
            return
        card = player.card("EDR_978", source=source)
        card.cost = 1
        card._summon_index = 0
        card.zone = Zone.DECK
        card._summon_index = None


class EDR_978:
    """Meadowstrider"""

    deathrattle = EDR_978_BottomDeck(CONTROLLER)


class EDR_979:
    """Ancient of Yore"""

    events = OWN_TURN_BEGIN.on(Buff(SELF, "+3/+3"))
    deathrattle = Draw(CONTROLLER) * 2


class EDR_979e:
    """Ancient Slumber"""

    pass


class EDR_979e2:
    """Ancient Draw"""

    pass


class EDR_999:
    """Gnawing Greenfin"""

    battlecry = Summon(CONTROLLER, RandomMurloc())


class EDR_COIN1:
    """The Coin"""

    play = GainMana(CONTROLLER, 1)


class EDR_COIN2:
    """The Coin"""

    play = GainMana(CONTROLLER, 1)


class FIR_777e2:
    """Amirdrassil's Agony"""

    tags = {GameTag.ATK: 3, GameTag.HEALTH: 3}


class FIR_918e1:
    """Elune's Light"""

    tags = {GameTag.ATK: 3, GameTag.HEALTH: 3}


class FIR_919e:
    """Everburning"""

    tags = {
        GameTag.CARDNAME: "Everburning",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = OWN_TURN_END.on(Give(CONTROLLER, "FIR_919"), Destroy(SELF))


class FIR_921:
    """Petal Picker"""

    deathrattle = Give(CONTROLLER, RandomCard())


class FIR_921e:
    """Mana Bloom"""

    pass


class FIR_921e:
    """Mana Bloom"""

    pass


class FIR_929_DrawFireSpell(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        fire_spells = [
            card
            for card in player.deck
            if card.type == CardType.SPELL
            and getattr(getattr(card, "data", None), "spell_school", None)
            == SpellSchool.FIRE
        ]
        if fire_spells:
            return source.game.queue_actions(
                source, [ForceDraw(source.game.random.choice(fire_spells))]
            )


class FIR_929:
    """Living Flame"""

    deathrattle = FIR_929_DrawFireSpell(CONTROLLER)
    events = Damage(SELF).on(Buff(SELF, "+2/+1"))


class FIR_940:
    """Zaqali Flamemancer"""

    events = Attack(SELF).on(Damage(ENEMY_MINIONS, 1))


class FIR_958_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = 4 if source.game.current_player is player.opponent else 1
        return source.game.queue_actions(source, [Hit(ENEMY_CHARACTERS, amount)])


class FIR_958:
    """Tindral Sageswift"""

    deathrattle = FIR_958_Deathrattle(CONTROLLER)


class FIR_959:
    """Fyrakk the Blazing"""

    events = Attack(SELF).on(Damage(RANDOM_ENEMY_CHARACTER, 3))


# Card IDs that need to be handled separately


class EDR_060e:
    """Ward of Earth"""
    pass


class EDR_100t:
    """Waking Terror"""

    lifesteal = True
    events = Attack(SELF).on(Buff(SELF, "+3/+3"))


class EDR_100t1:
    """Well Rested"""

    elusive = True
    events = OWN_TURN_BEGIN.on(Buff(SELF, "+2/+2"))


class EDR_100t13:
    """Harpy's Talons"""

    divine_shield = True
    windfury = True


class EDR_100t13e:
    """Harpy's Talons"""

    pass


class EDR_100t2:
    """Short Claws"""

    events = OWN_TURN_BEGIN.on(Buff(SELF, "-2"))


class EDR_100t3:
    """Bundled Up"""

    taunt = True
    events = OWN_TURN_BEGIN.on(Buff(SELF, "+4"))


class EDR_100t4:
    """Inner Demons"""

    deathrattle = Draw(CONTROLLER) * 2


class EDR_100t5:
    """Living Nightmare"""

    events = Play(CONTROLLER).on(Summon(CONTROLLER, "EDR_100t5"))


class EDR_100t5e2:
    """Tiny Nightmare"""

    pass


class EDR_100t5e5:
    """Living Nightmare"""

    pass


class EDR_100t6:
    """Sleepwalker"""

    charge = True


class EDR_100t7:
    """Rude Awakening"""

    events = Play(CONTROLLER).on(Play.CARD)


class EDR_100t8:
    """Sweet Dreams"""

    events = OWN_TURN_BEGIN.on(Buff(SELF, "+4/+5"))


class EDR_100t9:
    """Persisting Horror"""

    reborn = True


class EDR_100t1e:
    """Well Rested"""

    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


class EDR_100t2e:
    """Short Claws"""

    tags = {GameTag.ATK: -2}


class EDR_100t3e:
    """Bundled Up"""

    tags = {GameTag.HEALTH: 4}


class EDR_100t4e:
    """Inner Demons"""
    pass


class EDR_100t5e:
    """Living Nightmare"""
    pass


class EDR_100t6e:
    """Sneaky Sleepwalking"""
    stealth = True


class EDR_100t7e:
    """Rude Awakening"""
    pass


class EDR_100t8e:
    """Turtled Up"""

    tags = {GameTag.HEALTH: 5}


class EDR_100t8e1:
    """Sweet Dreams"""

    tags = {GameTag.ATK: 4, GameTag.HEALTH: 5}


class EDR_100t9e:
    """Persisting Horror"""
    reborn = True


class EDR_100t10e:
    """Nightmare Scales"""
    divine_shield = True


class EDR_100te:
    """Waking Terror"""
    lifesteal = True
