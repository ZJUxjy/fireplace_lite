from ..utils import *


FEL_SPELL_CARDS = [
    "BAR_891",
    "BT_035",
    "BT_514",
    "BT_235",
]


def _kindred(card):
    for played in getattr(card.controller, "cards_played_last_turn", []):
        if card.type == CardType.MINION and played.type == CardType.MINION:
            if set(card.races).intersection(played.races):
                return True
    return False


class DINO_137_DiscountAdjacent(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, saucier):
        index = getattr(saucier, "played_from_hand_index", None)
        if index is None:
            return
        hand = saucier.controller.hand
        targets = []
        if index - 1 >= 0 and index - 1 < len(hand):
            targets.append(hand[index - 1])
        if index < len(hand):
            targets.append(hand[index])
        return source.game.queue_actions(
            source, [Buff(card, "DINO_137e") for card in targets]
        )


class DINO_138_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if not _kindred(source):
            return
        enemies = list(player.opponent.field)
        if not enemies:
            return
        targets = [enemies[0]]
        if enemies[-1] is not enemies[0]:
            targets.append(enemies[-1])
        return source.game.queue_actions(source, [Hit(target, 6) for target in targets])


class TLC_631_AddProgress(TargetedAction):
    TARGET = ActionArg()
    AMOUNT = IntArg()

    def do(self, source, target, amount):
        if amount != 2 or not source.controller.current_player:
            return
        return source.game.queue_actions(source, [AddProgress(source, source)])


class TLC_631_BonusDamage(TargetedAction):
    TARGET = ActionArg()
    AMOUNT = IntArg()

    def do(self, source, target, amount):
        if amount != 2 or getattr(source, "_tlc_631_bonus_active", False):
            return
        source._tlc_631_bonus_active = True
        source.game.queue_actions(source, [Hit(target, 2)])
        source._tlc_631_bonus_active = False


class TLC_633_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if not target.races:
            return
        return source.game.queue_actions(source, [Hit(target, 6)])


class TLC_841_JarHand(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for card in list(player.hand):
            if card.type != CardType.MINION:
                continue
            card.zone = Zone.SETASIDE
            jar = player.card("TLC_841t", source=source)
            jar._tlc_841_stored = card
            actions.append(Give(player, jar))
        return source.game.queue_actions(source, actions)


class TLC_841_Release(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, jar):
        stored = getattr(jar, "_tlc_841_stored", None)
        if stored:
            return source.game.queue_actions(source, [Summon(jar.controller, stored)])


class TLC_900_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        remaining = [other.id for other in self.cards if other is not card]
        card._tlc_900_remaining = remaining
        actions = [Give(self.player, card)]
        if remaining:
            actions.append(Buff(self.player, "TLC_900e"))
        self.source.game.queue_actions(self.source, actions)
        self.trigger_choice_callback()


class TLC_900_FollowupChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class TLC_900_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = [player.card(card_id, source=source) for card_id in FEL_SPELL_CARDS]
        source.game.random.shuffle(cards)
        return source.game.queue_actions(source, [TLC_900_Choice(player, cards[:3])])


class TLC_900_Followup(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, player, card):
        remaining = getattr(card, "_tlc_900_remaining", None)
        if not remaining:
            return
        owner = source.controller
        cards = [owner.card(card_id, source=source) for card_id in remaining]
        source.game.queue_actions(
            source,
            [Destroy(SELF), TLC_900_FollowupChoice(owner, cards)],
        )


class TLC_901_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        races = set(target.races)
        targets = [
            minion
            for minion in source.game.board
            if races.intersection(minion.races)
        ]
        return source.game.queue_actions(source, [Hit(minion, 3) for minion in targets])


class TLC_903_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if _kindred(source):
            return source.game.queue_actions(source, [Buff(player.hero, "TLC_903e")])


class DINO_136:
    """Horn of Feasting"""

    play = Summon(CONTROLLER, "DINO_136t") * 3
    outcast = Summon(CONTROLLER, "DINO_136t").then(Buff(Summon.CARD, "DINO_136e")) * 3


DINO_136e = buff(immune_while_attacking=True)


class DINO_136t:
    """Ravenous Raptor"""

    tags = {GameTag.RUSH: True}


class DINO_137:
    """Skittish Saucier"""

    play = DINO_137_DiscountAdjacent(SELF)


@custom_card
class DINO_137e:
    tags = {
        GameTag.CARDNAME: "Prepared Serving",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


class DINO_138:
    """Diabolus Rex"""

    play = DINO_138_Play(CONTROLLER)


class TLC_630:
    """Gorishi Wasp"""

    tags = {GameTag.RUSH: True}
    events = Damage(SELF).on(Give(CONTROLLER, "TLC_630t"))


class TLC_630t:
    """Gorishi Stinger"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = Hit(TARGET, 2), Summon(CONTROLLER, "TLC_903t")


class TLC_631:
    """Unleash the Colossus"""

    quest = Damage(ENEMY_CHARACTERS).on(
        TLC_631_AddProgress(Damage.TARGET, Damage.AMOUNT)
    )
    reward = Give(CONTROLLER, "TLC_631t")


class TLC_631t:
    """Gorishi Colossus"""

    play = Buff(CONTROLLER, "TLC_631e")


class TLC_631e:
    events = Damage(ENEMY_CHARACTERS).on(
        TLC_631_BonusDamage(Damage.TARGET, Damage.AMOUNT)
    )


class TLC_633:
    """Bugsquasher"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_633_Play(TARGET)


class TLC_833:
    """Insect Claw"""

    events = Attack(FRIENDLY_HERO).after(Summon(CONTROLLER, "TLC_903t"))


class TLC_840:
    """Gorishi Tunneler"""

    events = Attack(SELF).after(Hit(ENEMY_HERO, 2))


class TLC_841:
    """Entomologist Toru"""

    play = TLC_841_JarHand(CONTROLLER)


class TLC_841t:
    """Specimen Jar"""

    tags = {GameTag.DEATHRATTLE: True}
    deathrattle = TLC_841_Release(SELF)


class TLC_900:
    """Hive Map"""

    play = TLC_900_Play(CONTROLLER)


class TLC_900e:
    events = Play(CONTROLLER).after(TLC_900_Followup(SELF, Play.CARD))


class TLC_901:
    """Fumigate"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TLC_901_Play(TARGET)


class TLC_902:
    """Infestation"""

    play = Give(CONTROLLER, "TLC_630t") * 2


class TLC_903:
    """Silithid Queen"""

    tags = {GameTag.RUSH: True}
    play = TLC_903_Play(CONTROLLER)


class TLC_903e:
    events = OWN_TURN_END.on(Destroy(SELF))
    tags = {
        GameTag.ATK: 5,
    }


class TLC_903t:
    """Silithid Grub"""

    tags = {GameTag.RUSH: True}
