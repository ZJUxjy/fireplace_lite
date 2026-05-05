from hearthstone.enums import Zone

from ..utils import *


def _is_dragon(card):
    return Race.DRAGON in getattr(card, "races", [])


class MIS_305_DelayedProductChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(
            self.source,
            [Summon(self.player, card).then(Dormant(Summon.CARD, 2))],
        )
        self.trigger_choice_callback()


class MIS_305_DelayedProduct(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = (RandomMinion(cost=range(8, 100)) * 3).evaluate(source)
        return source.game.queue_actions(
            source, [MIS_305_DelayedProductChoice(player, cards)]
        )


class MIS_919_CopyEnemy(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        copy = ExactCopy(TARGET).copy(source, target)
        return source.game.queue_actions(
            source,
            [
                Buff(
                    copy,
                    "MIS_919e",
                    atk=1 - copy.atk,
                    max_health=1 - copy.max_health,
                    cost=1 - copy.cost,
                ),
                Give(source.controller, copy),
            ],
        )


class TOY_383_Raza(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        dead_minions = [
            card for card in player.graveyard if card.type == CardType.MINION
        ]
        if len(dead_minions) > 5:
            dead_minions = source.game.random.sample(dead_minions, 5)
        actions = []
        for dead_minion in dead_minions[:5]:
            copy = player.card(dead_minion.id, source=source)
            actions.append(Buff(copy, "TOY_383e2", cost=-copy.cost))
            actions.append(Shuffle(player, copy))
        return source.game.queue_actions(source, actions)


class TOY_385_TimewinderZarimi(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if getattr(player, "_timewinder_zarimi_used", False):
            return
        dragons_played = [
            card
            for card in player.cards_played_this_game
            if card is not source and card.id != source.id and _is_dragon(card)
        ]
        if len(dragons_played) >= 8:
            player._timewinder_zarimi_used = True
            source.game.next_players.insert(0, player)
            source.game.manager.targeted_action(self, source, player)


class TOY_387_ScaleReplica(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        dragons = [
            card
            for card in player.deck
            if card.type == CardType.MINION and _is_dragon(card)
        ]
        if not dragons:
            return
        lowest = min(dragons, key=lambda card: card.cost)
        highest = max(dragons, key=lambda card: card.cost)
        actions = [ForceDraw(lowest)]
        if highest is not lowest:
            actions.append(ForceDraw(highest))
        return source.game.queue_actions(source, actions)


class TOY_388_ChalkArtist(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.deck if card.type == CardType.MINION]
        if not minions:
            return
        original = source.game.random.choice(minions)
        original_cost = original.cost
        original_atk = original.atk
        original_health = original.max_health
        source.game.queue_actions(source, [ForceDraw(original)])
        legendary = RandomLegendaryMinion().evaluate(source)
        if not legendary:
            return
        legendary = legendary[0]
        original.zone = Zone.SETASIDE
        return source.game.queue_actions(
            source,
            [
                Buff(
                    legendary,
                    "TOY_388e",
                    atk=original_atk - legendary.atk,
                    max_health=original_health - legendary.max_health,
                    cost=original_cost - legendary.cost,
                ),
                Give(player, legendary),
            ],
        )


class TOY_714_FlyOffTheShelves(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for _ in range(1 + len([card for card in player.hand if _is_dragon(card)])):
            actions.append(Hit(ENEMY_MINIONS, 1))
        return source.game.queue_actions(source, actions)


class TOY_879_Repackage(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [
            card
            for card in list(player.field) + list(player.opponent.field)
            if card.type == CardType.MINION
        ]
        box = player.opponent.card("TOY_879t", source=source)
        box._repackaged_minion_ids = [card.id for card in minions]
        for minion in minions:
            minion.zone = Zone.SETASIDE
            source.game.manager.targeted_action(self, source, minion)
        return source.game.queue_actions(source, [Shuffle(player.opponent, box)])


class TOY_879t_OpenBox(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = [
            Give(player, card_id)
            for card_id in getattr(source, "_repackaged_minion_ids", [])
        ]
        return source.game.queue_actions(source, actions)


##
# Minions

# TOY_380: Clay Matriarch (6费 3/7 龙)
# 微缩。嘲讽。亡语：召唤一个4/4有虚空的黏土幼龙
class TOY_380:
    """Clay Matriarch"""

    miniaturize_mini = "TOY_380t"

    tags = {GameTag.TAUNT: True}

    deathrattle = Summon(CONTROLLER, "TOY_380t2")


class TOY_380t:
    """Clay Matriarch"""

    tags = TOY_380.tags
    deathrattle = TOY_380.deathrattle


# TOY_380t2: Clay Whelp (4费 4/4 虚空)
class TOY_380t2:
    """Clay Whelp"""

    tags = {GameTag.ELUSIVE: True}


class TOY_381:
    """Papercraft Angel"""

    update = Refresh(FRIENDLY_HERO_POWER, {GameTag.COST: SET(0)})


class TOY_382:
    """Careless Crafter"""

    deathrattle = Give(CONTROLLER, "TOY_382t") * 2


class TOY_383:
    """Raza the Resealed"""

    play = TOY_383_Raza(CONTROLLER)


class TOY_385:
    """Timewinder Zarimi"""

    play = TOY_385_TimewinderZarimi(CONTROLLER)


class TOY_387:
    """Scale Replica"""

    play = TOY_387_ScaleReplica(CONTROLLER)


class TOY_388:
    """Chalk Artist"""

    play = TOY_388_ChalkArtist(CONTROLLER)


##
# Locations


class MIS_919:
    """Puppet Theatre"""

    activate = MIS_919_CopyEnemy(TARGET)


##
# Spells


class MIS_305:
    """Delayed Product"""

    play = MIS_305_DelayedProduct(CONTROLLER)


class MIS_714:
    """Funhouse Mirror"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Summon(CONTROLLER, ExactCopy(TARGET)).then(Attack(Summon.CARD, TARGET))


class TOY_382t:
    """Bandage"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Heal(TARGET, 3)


class TOY_384:
    """Purifying Power"""

    play = Silence(FRIENDLY_MINIONS), Buff(FRIENDLY_MINIONS, "TOY_384e")


class TOY_714:
    """Fly Off the Shelves"""

    play = TOY_714_FlyOffTheShelves(CONTROLLER)


class TOY_879:
    """Repackage"""

    play = TOY_879_Repackage(CONTROLLER)


class TOY_879t:
    """Cardboard Box"""

    play = TOY_879t_OpenBox(CONTROLLER)


##
# Buffs


@custom_card
class MIS_919e:
    tags = {
        GameTag.CARDNAME: "Under Study",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


@custom_card
class TOY_383e2:
    tags = {
        GameTag.CARDNAME: "Resealed",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


TOY_384e = buff(+1, +2)


@custom_card
class TOY_388e:
    tags = {
        GameTag.CARDNAME: "Chalked Up",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
