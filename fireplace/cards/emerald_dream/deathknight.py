# Death Knight cards from EMERALD_DREAM expansion
from ..utils import *


LOWEST_HEALTH = lambda sel: RANDOM(
    sel + (CURRENT_HEALTH == OpAttr(sel, "health", min))
)

_EDR_UNHOLY_RUNE_CARDS = {
    "EDR_811",
    "EDR_813",
    "EDR_813a",
    "EDR_813b",
    "EDR_815",
    "EDR_816",
    "EDR_817",
    "EDR_818",
    "FIR_951",
}

_EDR_BLOOD_RUNE_CARDS = {
    "EDR_810",
    "EDR_812",
    "EDR_814",
    "EDR_819",
    "FIR_900",
    "FIR_901",
}


def _collectible_minions(source, predicate=lambda data: True):
    cards = []
    for card_id, data in db.items():
        if (
            data.collectible
            and data.type == CardType.MINION
            and (not source.game.is_standard or data.is_standard)
            and predicate(data)
        ):
            card = source.controller.card(card_id, source=source)
            if predicate(card):
                cards.append(card)
    source.game.random.shuffle(cards)
    return cards[:3]


class EDR_810_LeechSteal(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, leech):
        player = leech.controller
        enemies = list(player.opponent.characters)
        if not enemies:
            return
        target = min(enemies, key=lambda card: card.health)
        amount = 1 + sum(1 for card in player.field if card.id == "EDR_810")
        return source.game.queue_actions(
            source, [Hit(target, amount), Heal(player.hero, amount)]
        )


class EDR_811_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        if getattr(self.source, "_edr_811_dark_gift", False):
            card._dark_gift = True
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class EDR_811_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spend = getattr(player, "corpses", 0) >= 2
        if spend:
            player.corpses -= 2
        source._edr_811_dark_gift = spend
        cards = _collectible_minions(source, lambda data: Race.UNDEAD in data.races)
        return source.game.queue_actions(source, [EDR_811_Choice(player, cards)])


class EDR_812_Battlecry(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        if not weapon.controller.cards_played_this_game:
            return
        last = weapon.controller.cards_played_this_game[-1]
        actions = []
        if last.id in _EDR_UNHOLY_RUNE_CARDS:
            actions.append(Buff(weapon, "EDR_812e2"))
        if last.id in _EDR_BLOOD_RUNE_CARDS:
            actions.append(Buff(weapon, "EDR_812e3"))
        return source.game.queue_actions(source, actions)


class EDR_813b_Damage(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        player = source.controller
        if getattr(player, "corpses", 0) < 2:
            return
        player.corpses -= 2
        return source.game.queue_actions(source, [Hit(target, 4)])


class EDR_815_SpendCorpses(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, minion):
        player = source.controller
        if getattr(player, "corpses", 0) < 2:
            return
        player.corpses -= 2
        return source.game.queue_actions(source, [Hit(minion, 3)])


class EDR_818_Split(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, nythendra):
        spaces = source.game.MAX_MINIONS_ON_FIELD - len(nythendra.controller.field)
        amount = min(max(1, nythendra.atk), spaces)
        return source.game.queue_actions(
            source, [Summon(nythendra.controller, "EDR_818t") for _ in range(amount)]
        )


class EDR_818_Reform(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        beetles = list(player.field.filter(id="EDR_818t"))
        if not beetles:
            return
        actions = [Remove(beetle) for beetle in beetles]
        actions.append(Summon(player, "EDR_818"))
        return source.game.queue_actions(source, actions)


class EDR_819_AttackAll(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, ursoc):
        others = [minion for minion in source.game.board if minion is not ursoc]
        killed = []
        actions = []
        for minion in others:
            if minion.health <= ursoc.atk:
                killed.append(ExactCopy(TARGET).copy(source, minion))
            actions.extend([Hit(minion, ursoc.atk), Hit(ursoc, minion.atk)])
        ursoc._edr_819_killed = killed
        return source.game.queue_actions(source, actions)


class EDR_819_Resurrect(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, ursoc):
        killed = getattr(ursoc, "_edr_819_killed", [])
        return source.game.queue_actions(
            source, [Summon(ursoc.controller, copy) for copy in killed]
        )


class FIR_900_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        card._dark_gift = True
        self.source.game.queue_actions(
            self.source, [Buff(card, "FIR_900e"), Give(self.player, card)]
        )
        self.trigger_choice_callback()


class FIR_900_Discover(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = _collectible_minions(source)
        return source.game.queue_actions(source, [FIR_900_Choice(player, cards)])


class FIR_901_Battlecry(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if any(
            card.type == CardType.MINION and getattr(card, "_dark_gift", False)
            for card in player.hand
        ):
            return source.game.queue_actions(
                source, [Summon(player, "FIR_901t"), Summon(player, "FIR_901t")]
            )


class FIR_951_SpendCorpses(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, volcoross):
        player = volcoross.controller
        amount = 0
        for spend in (30, 20, 10):
            if getattr(player, "corpses", 0) >= spend:
                amount = spend
                break
        if not amount:
            return
        player.corpses -= amount
        return source.game.queue_actions(
            source, [Buff(volcoross, "FIR_951e", atk=amount, max_health=amount)]
        )


##
# Minions


class EDR_810:
    """Hideous Husk"""

    play = Summon(CONTROLLER, "EDR_810t") * 2


class EDR_810t:
    """Bloated Leech"""

    events = OWN_TURN_END.on(EDR_810_LeechSteal(SELF))


class EDR_811:
    """Rite of Atrocity"""

    play = EDR_811_Discover(CONTROLLER)


class EDR_812:
    """Grotesque Runeblade"""

    tags = {GameTag.LIFESTEAL: True}
    play = EDR_812_Battlecry(SELF)


class EDR_813:
    """Morbid Swarm"""

    choose = ("EDR_813a", "EDR_813b")
    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }


class EDR_813a:
    """Contaminated Colony"""

    play = Summon(CONTROLLER, "EDR_813at") * 2


class EDR_813at:
    """Ant Husk"""


class EDR_813b:
    """Bug Bites"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = EDR_813b_Damage(TARGET)


class EDR_814:
    """Infested Breath"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 2), Summon(CONTROLLER, "EDR_810t")


class EDR_815:
    """Corpse Flower"""

    events = Summon(OPPONENT, MINION).after(EDR_815_SpendCorpses(Summon.CARD))


class EDR_816:
    """Monstrous Mosquito"""

    events = OWN_TURN_END.on(Buff(FRIENDLY_MINIONS - SELF, "EDR_816e"))


class EDR_817:
    """Sanguine Infestation"""

    play = Draw(CONTROLLER) * 2, Summon(CONTROLLER, "EDR_810t") * 2


class EDR_818:
    """Nythendra"""

    tags = {GameTag.TAUNT: True}
    deathrattle = EDR_818_Split(SELF)


class EDR_818t:
    """Nythendric Beetle"""

    events = OWN_TURN_BEGIN.on(EDR_818_Reform(CONTROLLER))


class EDR_819:
    """Ursoc"""

    play = EDR_819_AttackAll(SELF)
    deathrattle = EDR_819_Resurrect(SELF)


class FIR_900:
    """Cremate"""

    play = FIR_900_Discover(CONTROLLER)


class FIR_901:
    """Frostburn Matriarch"""

    play = FIR_901_Battlecry(CONTROLLER)


class FIR_901t:
    """Frostburn Broodling"""

    tags = {GameTag.TAUNT: True}


class FIR_951:
    """Volcoross"""

    tags = {
        GameTag.RUSH: True,
        GameTag.TAUNT: True,
    }
    play = FIR_951_SpendCorpses(SELF)


class FIR_951t2:
    """Tail Smash"""

    play = FIR_951_SpendCorpses(CONTROLLER)


class FIR_951t3:
    """Fiery Chomp"""

    play = FIR_951_SpendCorpses(CONTROLLER)


class FIR_951t4:
    """Lava Wave"""

    play = FIR_951_SpendCorpses(CONTROLLER)


##
# Buffs


EDR_816e = buff(atk=1)


@custom_card
class EDR_812e2:
    tags = {
        GameTag.CARDNAME: "Unholy Corruption",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 1,
    }


@custom_card
class EDR_812e3:
    tags = {
        GameTag.CARDNAME: "Bloody Corruption",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.HEALTH: 1,
    }


@custom_card
class FIR_900e:
    tags = {
        GameTag.CARDNAME: "Cremated",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -2,
    }


@custom_card
class FIR_951e:
    tags = {
        GameTag.CARDNAME: "Volcanic Power",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
