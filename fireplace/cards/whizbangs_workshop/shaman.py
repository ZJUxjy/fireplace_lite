from hearthstone.enums import Zone

from ..utils import *


class MIS_307_SummonTinyfin(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        tinyfin = source.controller.card("MIS_307t", source=source)
        actions = []
        if tinyfin.atk != target.atk or tinyfin.max_health != target.max_health:
            actions.append(
                Buff(
                    tinyfin,
                    "MIS_307e",
                    atk=target.atk - tinyfin.atk,
                    max_health=target.max_health - tinyfin.max_health,
                )
            )
        actions.append(Summon(source.controller, tinyfin))
        return source.game.queue_actions(source, actions)


class TOY_046_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source,
            [
                Buff(
                    card,
                    "TOY_046e",
                    atk=7 - card.atk,
                    max_health=7 - card.max_health,
                ),
                Give(self.player, card),
            ],
        )
        self.trigger_choice_callback()


class TOY_046_IncredibleValue(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = (RandomMinion(cost=4) * 3).evaluate(source)
        return source.game.queue_actions(source, [TOY_046_Choice(player, cards)])


class TOY_500_Volcano(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        for _ in range(10):
            minions = list(player.field) + list(player.opponent.field)
            if not minions:
                break
            target = source.game.random.choice(minions)
            source.game.queue_actions(source, [Hit(target, 1)])


class TOY_501_Shudderblock(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        player._shudderblock_next_battlecry_repeats = 2
        source.game.manager.targeted_action(self, source, player)


class TOY_504_Hagatha(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = [
            card
            for card in list(player.deck)
            if card.type == CardType.SPELL and card.cost >= 5
        ][:2]
        actions = []
        for spell in spells:
            spell.draw()
            spell.zone = Zone.SETASIDE
            slime = player.card("TOY_504t", source=source)
            slime._hagatha_spell_id = spell.id
            actions.append(Give(player, slime))
        return source.game.queue_actions(source, actions)


class TOY_504t_CastStoredSpell(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spell_id = getattr(source, "_hagatha_spell_id", None)
        if not spell_id:
            return
        spell = player.card(spell_id, source=source)
        return source.game.queue_actions(
            source, [CastSpellTargetsEnemiesIfPossible(spell)]
        )


class TOY_507_DrawBattlecry(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [
            card
            for card in player.deck
            if card.type == CardType.MINION and card.has_battlecry
        ]
        if not minions:
            return
        card = source.game.random.choice(minions)
        return source.game.queue_actions(
            source, [ForceDraw(card), Buff(card, "TOY_507e")]
        )


##
# Minions


class MIS_306:
    """Rocket Hopper"""


class MIS_307:
    """Murloc Growfin"""

    play = Give(CONTROLLER, "MIS_307t1"), MIS_307_SummonTinyfin(SELF)


class MIS_307t1:
    """Murloc Growfin"""

    play = MIS_307_SummonTinyfin(SELF)


class TOY_501:
    """Shudderblock"""

    play = TOY_501_Shudderblock(CONTROLLER)


class TOY_501t:
    """Shudderblock"""

    play = TOY_501.play


class TOY_503:
    """Shining Sentinel"""

    tags = {GameTag.TAUNT: True, GameTag.ELUSIVE: True}
    play = Summon(CONTROLLER, ExactCopy(SELF))


class TOY_504:
    """Hagatha the Fabled"""

    play = TOY_504_Hagatha(CONTROLLER)


class TOY_504t:
    """Fairy Tale Slime"""

    play = TOY_504t_CastStoredSpell(CONTROLLER)


class TOY_513:
    """Sand Art Elemental"""

    miniaturize_mini = "TOY_513t"
    play = Buff(FRIENDLY_HERO, "TOY_513e")


class TOY_513t:
    """Sand Art Elemental"""

    play = TOY_513.play


##
# Locations


class TOY_507:
    """Fairy Tale Forest"""

    activate = TOY_507_DrawBattlecry(CONTROLLER)


##
# Spells


class MIS_701:
    """Wave of Nostalgia"""

    play = Morph(ALL_MINIONS, RandomLegendaryMinion(is_standard=False))


class TOY_046:
    """Incredible Value"""

    play = TOY_046_IncredibleValue(CONTROLLER)


class TOY_500:
    """Baking Soda Volcano"""

    play = TOY_500_Volcano(CONTROLLER)


class TOY_506:
    """Once Upon a Time..."""

    play = (
        Summon(CONTROLLER, RandomBeast(cost=3)),
        Summon(CONTROLLER, RandomDragon(cost=3)),
        Summon(CONTROLLER, RandomElemental(cost=3)),
        Summon(CONTROLLER, RandomMurloc(cost=3)),
    )


class TOY_508:
    """Pop-Up Book"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 2), Summon(CONTROLLER, "hexfrog") * 2


class TOY_877:
    """Wish Upon a Star"""

    play = (
        Buff(FRIENDLY_HAND + MINION, "TOY_877e"),
        Buff(FRIENDLY_DECK + MINION, "TOY_877e"),
        Buff(FRIENDLY_MINIONS, "TOY_877e"),
    )


@custom_card
class MIS_307e:
    tags = {
        GameTag.CARDNAME: "Molded Tinyfin Stats",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


@custom_card
class TOY_046e:
    tags = {
        GameTag.CARDNAME: "Incredible Value",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


@custom_card
class TOY_507e:
    tags = {
        GameTag.CARDNAME: "In the Woods",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -1,
    }


@custom_card
class TOY_513e:
    tags = {
        GameTag.CARDNAME: "Sand Art Elemental Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.TAG_ONE_TURN_EFFECT: True,
        GameTag.ATK: 1,
        GameTag.WINDFURY: True,
    }

    events = OWN_TURN_END.on(Destroy(SELF))


@custom_card
class TOY_877e:
    tags = {
        GameTag.CARDNAME: "Starry-Eyed",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 2,
        GameTag.HEALTH: 3,
    }
