from ..utils import *


LOWEST_HEALTH = lambda sel: RANDOM(
    sel + (CURRENT_HEALTH == OpAttr(sel, "health", min))
)

TOY_913_FIRST_EDITION_DH = ("TOY_913t1", "TOY_913t2", "TOY_913t3")


def _return_policy_choices(entities, source):
    choices = [
        card
        for card in source.controller.cards_played_this_game
        if card.controller is source.controller and card.get_actions("deathrattle")
    ]
    if len(choices) > 3:
        return source.game.random.sample(choices, 3)
    return choices


RETURN_POLICY_CHOICES = FuncSelector(_return_policy_choices)


class MIS_102_ReturnPolicyChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Deathrattle(card)])
        self.trigger_choice_callback()


class TOY_640_WorkshopMishap(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        amount = source.get_damage(5, target)
        excess = 0
        if amount and not target.divine_shield and not target.immune:
            excess = max(0, amount - target.health)

        actions = [Hit(target, 5)]
        if excess:
            field = target.controller.field
            index = field.index(target)
            if index > 0:
                actions.append(Hit(field[index - 1], excess))
            if index < len(field) - 1:
                actions.append(Hit(field[index + 1], excess))
        source.game.queue_actions(source, actions)


##
# Minions


class MIS_710:
    """Sock Puppet Slitherspear"""

    update = Refresh(SELF, {GameTag.ATK: ATK(FRIENDLY_HERO)})


class MIS_911:
    """Gibbering Reject"""

    events = Attack(FRIENDLY_HERO).after(Summon(CONTROLLER, "MIS_911"))


class TOY_028:
    """Spirit of the Team"""

    tags = {GameTag.STEALTH: True}
    update = CurrentPlayer(CONTROLLER) & Refresh(FRIENDLY_HERO, {GameTag.ATK: +2})
    events = OWN_TURN_BEGIN.on(Unstealth(SELF))


class TOY_642:
    """Ball Hog"""

    tags = {GameTag.LIFESTEAL: True}
    play = deathrattle = Hit(LOWEST_HEALTH(ENEMY_CHARACTERS), 3)


class TOY_647:
    """Magtheridon, Unreleased"""

    tags = {GameTag.DORMANT: True}
    dormant_turns = 2
    dormant_events = OWN_TURN_END.on(Hit(ENEMY_CHARACTERS, 3))


class TOY_913:
    """Ci'Cigi"""

    play = outcast = deathrattle = Give(CONTROLLER, RandomID(*TOY_913_FIRST_EDITION_DH))


class TOY_652_AdjustDemon(TargetedAction):
    TARGET = ActionArg()
    CARD = ActionArg()

    def get_target_args(self, source, target):
        chosen = self._args[1].evaluate(source)
        return [chosen]

    def do(self, source, player, chosen):
        return source.game.queue_actions(
            source,
            [
                Buff(
                    chosen,
                    "TOY_652e",
                    atk=source.atk - chosen.atk,
                    max_health=source.max_health - chosen.max_health,
                ),
                Buff(chosen, "TOY_652e2", cost=source.cost - chosen.cost),
                Give(player, chosen),
            ],
        )


# TOY_652: Window Shopper (5费 6/5)
# 微缩。战吼：发现一个恶魔，将其属性值与法力值消耗变为与本随从相同
class TOY_652:
    """Window Shopper"""

    play = Discover(CONTROLLER, RandomMinion(race=Race.DEMON)).then(
        TOY_652_AdjustDemon(CONTROLLER, Discover.CARD)
    )


##
# Spells


class MIS_102:
    """Return Policy"""

    play = MIS_102_ReturnPolicyChoice(CONTROLLER, RETURN_POLICY_CHOICES)


class TOY_640:
    """Workshop Mishap"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TOY_640_WorkshopMishap(TARGET)
    outcast = Buff(SELF, "TOY_640e"), TOY_640_WorkshopMishap(TARGET)


@custom_card
class TOY_640e:
    tags = {
        GameTag.CARDNAME: "Workshop Mishap Lifesteal",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.LIFESTEAL: True,
    }


class TOY_643:
    """Blind Box"""

    play = Give(CONTROLLER, RandomDemon()) * 2
    outcast = Discover(CONTROLLER, RandomDemon()).then(
        Give(CONTROLLER, Discover.CARD),
        Discover(CONTROLLER, RandomDemon()).then(Give(CONTROLLER, Discover.CARD)),
    )


class TOY_644:
    """Red Card"""

    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = Dormant(TARGET, 2)


class TOY_645:
    """Lesser Opal Spellstone"""

    progress_total = 4
    play = Draw(CONTROLLER)
    reward = Morph(SELF, "TOY_645t")

    class Hand:
        events = Attack(FRIENDLY_HERO).after(AddProgress(SELF, Attack.ATTACKER))


class TOY_645t:
    """Opal Spellstone"""

    progress_total = 4
    play = Draw(CONTROLLER) * 2
    reward = Morph(SELF, "TOY_645t1")

    class Hand:
        events = Attack(FRIENDLY_HERO).after(AddProgress(SELF, Attack.ATTACKER))


class TOY_645t1:
    """Greater Opal Spellstone"""

    play = Draw(CONTROLLER) * 3


##
# Weapons


class TOY_641:
    """Umpire's Grasp"""

    deathrattle = ForceDraw(RANDOM(FRIENDLY_DECK + DEMON)).then(
        Buff(ForceDraw.TARGET, "TOY_641e")
    )


TOY_641e = buff(cost=-2)
