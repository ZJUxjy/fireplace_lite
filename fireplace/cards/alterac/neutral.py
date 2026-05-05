from ..utils import *
from hearthstone.enums import SpellSchool


class AV_101_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        frost_spells = [
            card
            for card in player.deck
            if card.type == CardType.SPELL
            and getattr(getattr(card, "data", None), "spell_school", None)
            == SpellSchool.FROST
        ]
        if frost_spells:
            return source.game.queue_actions(
                source, [Draw(player, source.game.random.choice(frost_spells))]
            )


class AV_101:
    """Herald of Lokholar"""

    play = AV_101_Play(CONTROLLER)


class AV_102:
    """Popsicooler"""

    deathrattle = Freeze(RANDOM(ENEMY_MINIONS - DEAD) * 2)


class AV_112:
    """Snowblind Harpy"""

    play = Find(
        FRIENDLY_HAND
        + SPELL
        + FuncSelector(
            lambda entities, source: [
                card
                for card in entities
                if getattr(getattr(card, "data", None), "spell_school", None)
                == SpellSchool.FROST
            ]
        )
    ) & GainArmor(FRIENDLY_HERO, 5)


class AV_130:
    """Legionnaire"""

    deathrattle = Buff(FRIENDLY_HAND + MINION, "AV_130e")


AV_130e = buff(+2, +2)


class AV_143_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if source.health != 0:
            return source.game.queue_actions(source, [Summon(player, "AV_143")])


class AV_143:
    """Korrak the Bloodrager"""

    deathrattle = AV_143_Deathrattle(CONTROLLER)


class AV_100_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.deck if card.type == CardType.MINION]
        if minions and all(source.cost > card.cost for card in minions):
            return source.game.queue_actions(
                source, [Summon(player, source.game.random.choice(minions))]
            )


class AV_100:
    """Drek'Thar"""

    play = AV_100_Play(CONTROLLER)


class AV_211:
    """Dire Frostwolf"""

    deathrattle = Summon(CONTROLLER, "AV_211t")


class AV_309:
    """Piggyback Imp"""

    deathrattle = Summon(CONTROLLER, "AV_309t")


class AV_325:
    """Undying Disciple"""

    deathrattle = Hit(ENEMY_MINIONS, ATK(SELF))
