from ..utils import *


class ETC_071_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        players = (player, player.opponent)
        for target in players:
            source.game.queue_actions(source, [Draw(target), Draw(target)])
        for target in players:
            discards = [Discard(card) for card in list(target.hand[-2:])]
            source.game.queue_actions(source, discards)
        for target in players:
            source.game.queue_actions(source, [Mill(target), Mill(target)])


class ETC_071:
    """Rin, Orchestrator of Doom"""

    deathrattle = ETC_071_Deathrattle(CONTROLLER)


class ETC_086:
    """Amplified Elekk"""

    deathrattle = Hit(ENEMY_MINIONS, 3)


class ETC_104:
    """Crowd Surfer"""

    deathrattle = Buff(RANDOM(ALL_MINIONS - SELF), "ETC_104e")


class ETC_104e:
    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1, GameTag.DEATHRATTLE: True}
    deathrattle = Buff(RANDOM(ALL_MINIONS - OWNER), "ETC_104e")


class ETC_317_Improve(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        weapon._etc_317_bonus = getattr(weapon, "_etc_317_bonus", 0) + 1
        source.game.manager.targeted_action(self, source, weapon)


class ETC_317_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        amount = getattr(weapon, "_etc_317_bonus", 0)
        if amount:
            return source.game.queue_actions(
                source,
                [
                    Buff(
                        RANDOM(FRIENDLY_MINIONS),
                        "ETC_317e",
                        atk=amount,
                        max_health=amount,
                    )
                ],
            )


class ETC_317:
    """Disco Maul"""

    events = Play(CONTROLLER, MINION).after(ETC_317_Improve(SELF))
    deathrattle = ETC_317_Deathrattle(SELF)


class ETC_321:
    """Annoy-o-Troupe"""

    deathrattle = Summon(CONTROLLER, "GVG_085") * 3


class ETC_328:
    """Lead Dancer"""

    deathrattle = Summon(CONTROLLER, RANDOM(FRIENDLY_DECK + MINION + (ATK < ATK(SELF))))


class ETC_329_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, kangor):
        minions = [card for card in kangor.controller.hand if card.type == CardType.MINION]
        if minions:
            minion = kangor.game.random.choice(minions)
            minion._summon_index = getattr(kangor, "_dead_position", None)
            minion.zone = Zone.PLAY
            minion.lifesteal = True
            kangor.zone = Zone.HAND
            kangor.game.manager.targeted_action(self, source, minion)


class ETC_329:
    """Kangor, Dancing King"""

    deathrattle = ETC_329_Deathrattle(SELF)


class ETC_349:
    """Unpopular Has-Been"""

    deathrattle = Summon(CONTROLLER, RandomMinion(cost=5))


class ETC_382:
    """Free Spirit"""

    play = deathrattle = Buff(CONTROLLER, "ETC_382e")


@custom_card
class ETC_382e:
    tags = {
        GameTag.CARDNAME: "Free Spirit",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    events = Activate(CONTROLLER, FRIENDLY_HERO_POWER).after(GainArmor(FRIENDLY_HERO, 1))


class ETC_385:
    """Groovy Cat"""

    play = deathrattle = Buff(CONTROLLER, "ETC_385e")


@custom_card
class ETC_385e:
    tags = {
        GameTag.CARDNAME: "Groovy Cat",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    events = Activate(CONTROLLER, FRIENDLY_HERO_POWER).after(Buff(FRIENDLY_HERO, "ETC_385e2"))


@custom_card
class ETC_385e2:
    tags = {
        GameTag.CARDNAME: "Groovy Cat",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 1,
    }


class ETC_388_Improve(TargetedAction):
    TARGET = ActionArg()
    CARD = ActionArg()

    def do(self, source, weapon, card):
        if card.cost >= 5:
            weapon._etc_388_ancients = getattr(weapon, "_etc_388_ancients", 0) + 1
            source.game.manager.targeted_action(self, source, weapon)


class ETC_388_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        count = getattr(weapon, "_etc_388_ancients", 0)
        if count:
            return source.game.queue_actions(
                source,
                [Summon(weapon.controller, "TTN_903t4") for _ in range(count)],
            )


class ETC_388:
    """Timber Tambourine"""

    events = Play(CONTROLLER).after(ETC_388_Improve(SELF, Play.CARD))
    deathrattle = ETC_388_Deathrattle(SELF)


class ETC_405_Improve(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        weapon._etc_405_draws = getattr(weapon, "_etc_405_draws", 1) + 1
        source.game.manager.targeted_action(self, source, weapon)


class ETC_405_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        count = getattr(weapon, "_etc_405_draws", 1)
        return source.game.queue_actions(source, [Draw(weapon.controller) for _ in range(count)])


class ETC_405:
    """Glaivetar"""

    events = Play(CONTROLLER, PLAY_OUTCAST).after(ETC_405_Improve(SELF))
    deathrattle = ETC_405_Deathrattle(SELF)


class ETC_423_Improve(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        if source.controller is weapon.controller and source.game.current_player is weapon.controller:
            weapon._etc_423_stats = getattr(weapon, "_etc_423_stats", 1) + 1
            source.game.manager.targeted_action(self, source, weapon)


class ETC_423_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        stats = getattr(weapon, "_etc_423_stats", 1)
        return source.game.queue_actions(
            source,
            [Summon(weapon.controller, Buff("ETC_423t", "ETC_423e", atk=stats - 1, max_health=stats - 1))],
        )


class ETC_423:
    """Arcanite Ripper"""

    events = (Damage(FRIENDLY_HERO).on(ETC_423_Improve(SELF)), Heal(FRIENDLY_HERO).on(ETC_423_Improve(SELF)))
    deathrattle = ETC_423_Deathrattle(SELF)


@custom_card
class ETC_423e:
    tags = {
        GameTag.CARDNAME: "Arcanite Ripper",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


class ETC_425_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, opponent):
        bots = [opponent.card("ETC_425t", source=source) for _ in range(2)]
        source._etc_425_bots = bots
        return source.game.queue_actions(source, [Give(opponent, bot) for bot in bots])


class ETC_425_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, pozzik):
        bots = [bot for bot in getattr(pozzik, "_etc_425_bots", []) if bot.zone == Zone.HAND]
        for bot in bots:
            bot.zone = Zone.SETASIDE
            bot.controller = pozzik.controller
        return source.game.queue_actions(source, [Summon(pozzik.controller, bot) for bot in bots])


class ETC_425:
    """Pozzik, Audio Engineer"""

    play = ETC_425_Play(OPPONENT)
    deathrattle = ETC_425_Deathrattle(SELF)


class ETC_518_Improve(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        weapon._etc_518_mana = getattr(weapon, "_etc_518_mana", 1) + 1
        source.game.manager.targeted_action(self, source, weapon)


class ETC_518_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        amount = getattr(weapon, "_etc_518_mana", 1)
        return source.game.queue_actions(source, [FillMana(weapon.controller, amount)])


class ETC_518:
    """Record Scratcher"""

    events = Play(CONTROLLER, COMBO).after(ETC_518_Improve(SELF))
    deathrattle = ETC_518_Deathrattle(SELF)


class ETC_520_Improve(TargetedAction):
    TARGET = ActionArg()
    AMOUNT = IntArg()

    def do(self, source, weapon, amount):
        weapon._etc_520_damage = getattr(weapon, "_etc_520_damage", 1) + amount
        source.game.manager.targeted_action(self, source, weapon)


class ETC_520_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        amount = getattr(weapon, "_etc_520_damage", 1)
        return source.game.queue_actions(source, [Hit(ALL_MINIONS, amount)])


class ETC_520:
    """Kodohide Drumkit"""

    events = GainArmor(FRIENDLY_HERO).on(ETC_520_Improve(SELF, GainArmor.AMOUNT))
    deathrattle = ETC_520_Deathrattle(SELF)


class ETC_526:
    """Cage Head"""

    deathrattle = Summon(CONTROLLER, "ETC_526t")


class ETC_536:
    """Audio Splitter"""

    deathrattle = Give(CONTROLLER, Copy(HIGHEST_COST(FRIENDLY_HAND + SPELL)))


class ETC_813_Improve(TargetedAction):
    TARGET = ActionArg()
    AMOUNT = IntArg()

    def do(self, source, weapon, amount):
        weapon._etc_813_discount = getattr(weapon, "_etc_813_discount", 1) + amount
        source.game.manager.targeted_action(self, source, weapon)


class ETC_813:
    """Jazz Bass"""

    events = Overload(CONTROLLER).on(ETC_813_Improve(SELF, Overload.AMOUNT))
    deathrattle = Buff(CONTROLLER, "ETC_813e", cost=Attr(SELF, "_etc_813_discount"))


@custom_card
class ETC_813e:
    tags = {
        GameTag.CARDNAME: "Jazz Bass",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    update = Refresh(
        FRIENDLY_HAND + SPELL,
        {GameTag.COST: lambda self, i: -getattr(self, "_xcost", 1)},
    )
    events = Play(CONTROLLER, SPELL).after(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))


class ETC_832_Improve(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        weapon._etc_832_cost = getattr(weapon, "_etc_832_cost", 8) + 1
        source.game.manager.targeted_action(self, source, weapon)


class ETC_832_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        cost = getattr(weapon, "_etc_832_cost", 8)
        return source.game.queue_actions(
            source, [Summon(weapon.controller, RandomBeast(cost=cost))]
        )


class ETC_832:
    """Jungle Jammer"""

    events = Play(CONTROLLER, SPELL).after(ETC_832_Improve(SELF))
    deathrattle = ETC_832_Deathrattle(SELF)
