from hearthstone.enums import SpellSchool

from ..utils import *


class _CostMod:
    def __init__(self, func):
        self.func = func

    def evaluate(self, source):
        return self.func(source)


def _holy_spells_played(player, current_turn_only=False):
    return [
        card for card in player.cards_played_this_game
        if card.type == CardType.SPELL
        and getattr(getattr(card, "data", None), "spell_school", None)
        == SpellSchool.HOLY
        and (
            not current_turn_only
            or getattr(card, "turn_played", None) == player.game.turn
        )
    ]


def _holy_glowsticks_cost(entity):
    if _holy_spells_played(entity.controller, current_turn_only=True):
        return 1 - entity.data.cost
    return 0


def _flickering_lightbot_cost(entity):
    return -len(_holy_spells_played(entity.controller))


def _aura_cards(entities, source):
    return [
        card for card in entities
        if card.type == CardType.SPELL
        and (
            card.data.tags.get(GameTag.AURA)
            or card.data.tags.get(GameTag.PALADIN_AURA)
        )
    ]


AURA_SPELL = FuncSelector(_aura_cards)


class TOY_808_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        turns = 3 + getattr(source, "_aura_duration_bonus", 0)
        return source.game.queue_actions(
            source, [Buff(player, "TOY_808e", _crafter_aura_turns_remaining=turns)]
        )


class TOY_809_IncreaseAuras(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        for card in player.hand + player.deck:
            if card.type == CardType.SPELL and (
                card.data.tags.get(GameTag.AURA)
                or card.data.tags.get(GameTag.PALADIN_AURA)
            ):
                card._aura_duration_bonus = (
                    getattr(card, "_aura_duration_bonus", 0) + 1
                )
                source.game.manager.targeted_action(self, source, card)
        for buff in list(player.buffs):
            if buff.id == "TOY_808e":
                buff._crafter_aura_turns_remaining = (
                    getattr(buff, "_crafter_aura_turns_remaining", 3) + 1
                )
                source.game.manager.targeted_action(self, source, buff)


class TOY_812_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        summoned = set()
        for selector in (DIVINE_SHIELD, RUSH, TAUNT):
            candidates = [
                card for card in player.deck
                if card.type == CardType.MINION
                and card not in summoned
                and selector.eval([card], source)
            ]
            if candidates:
                card = source.game.random.choice(candidates)
                summoned.add(card)
                actions.append(Summon(player, card))
        return source.game.queue_actions(source, actions)


class TOY_813_SetStats(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        return source.game.queue_actions(
            source,
            [
                Buff(
                    target,
                    "TOY_813e3",
                    atk=source.atk - target.atk,
                    max_health=source.max_health - target.max_health,
                )
            ],
        )


class TOY_880_SummonCopies(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        count = max(1, min(4, getattr(source, "_wind_up_copies", 1)))
        actions = [Summon(player, ExactCopy(SELF)) for _ in range(count)]
        return source.game.queue_actions(source, actions)


##
# Minions


class MIS_918:
    """Flickering Lightbot"""

    cost_mod = _CostMod(_flickering_lightbot_cost)
    play = Give(CONTROLLER, "MIS_918t")


class MIS_918t:
    """Flickering Lightbot"""

    cost_mod = _CostMod(_flickering_lightbot_cost)


@custom_card
class TOY_716t:
    tags = {
        GameTag.CARDNAME: "Sale Bot",
        GameTag.CARDTYPE: CardType.MINION,
        GameTag.COST: 1,
        GameTag.ATK: 1,
        GameTag.HEALTH: 2,
        GameTag.CARDRACE: Race.MECHANICAL,
        GameTag.DIVINE_SHIELD: True,
        GameTag.TAUNT: True,
    }


class TOY_809:
    """Cardboard Golem"""

    play = TOY_809_IncreaseAuras(CONTROLLER)


class TOY_811:
    """Tigress Plushy"""

    miniaturize_mini = "TOY_811t"
    tags = {
        GameTag.RUSH: True,
        GameTag.LIFESTEAL: True,
        GameTag.DIVINE_SHIELD: True,
    }


class TOY_811t:
    """Tigress Plushy"""

    tags = TOY_811.tags


class TOY_812:
    """Pipsi Painthoof"""

    deathrattle = TOY_812_Deathrattle(CONTROLLER)


class TOY_813:
    """Toy Captain Tarim"""

    miniaturize_mini = "TOY_813t"
    tags = {GameTag.TAUNT: True}
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TOY_813_SetStats(TARGET)


class TOY_813t:
    """Toy Captain Tarim"""

    tags = TOY_813.tags
    requirements = TOY_813.requirements
    play = TOY_813.play


class TOY_880:
    """Wind-Up Enforcer"""

    tags = {GameTag.TRADEABLE: True}
    play = TOY_880_SummonCopies(CONTROLLER)


class TOY_882:
    """Trinket Artist"""

    play = (
        ForceDraw(RANDOM(FRIENDLY_DECK + MINION + DIVINE_SHIELD)),
        ForceDraw(RANDOM(FRIENDLY_DECK + AURA_SPELL)),
    )


##
# Weapons


class TOY_810:
    """Painter's Virtue"""

    tags = {GameTag.LIFESTEAL: True}
    events = Attack(FRIENDLY_HERO).after(Buff(FRIENDLY_HAND + MINION, "TOY_810e"))


##
# Spells


class MIS_700:
    """Whack-A-Gnoll"""

    play = Discover(CONTROLLER, RandomWeapon(card_class=CardClass.PALADIN)).then(
        Give(CONTROLLER, Buff(Discover.CARD, "MIS_700e"))
    )


class MIS_709:
    """Holy Glowsticks"""

    tags = {GameTag.LIFESTEAL: True}
    cost_mod = _CostMod(_holy_glowsticks_cost)
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 4)


class TOY_716:
    """Flash Sale"""

    play = Summon(CONTROLLER, "TOY_716t"), Buff(FRIENDLY_MINIONS, "TOY_716e")


class TOY_808:
    """Crafter's Aura"""

    play = TOY_808_Play(CONTROLLER)


class TOY_881:
    """Fancy Packaging"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET + DIVINE_SHIELD, "TOY_881e")


##
# Buffs


MIS_700e = buff(+1, +1)
TOY_716e = buff(+1, +2)
TOY_810e = buff(+1, +1)
TOY_881e = buff(+2, +3)


@custom_card
class TOY_813e3:
    tags = {
        GameTag.CARDNAME: "Toytanic",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


@custom_card
class TOY_808e:
    def _tick_duration(self, *args):
        if getattr(self, "_crafter_aura_last_tick_turn", None) == self.game.turn:
            return None
        self._crafter_aura_last_tick_turn = self.game.turn
        self._crafter_aura_turns_remaining = getattr(
            self, "_crafter_aura_turns_remaining", 3
        ) - 1
        if self._crafter_aura_turns_remaining <= 0:
            self._crafter_aura_expired = True
        return None

    def _destroy_if_expired(self, *args):
        if getattr(self, "_crafter_aura_expired", False):
            return Destroy(SELF)
        return None

    tags = {
        GameTag.CARDNAME: "Crafter's Aura",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = [
        OWN_TURN_END.on(Summon(CONTROLLER, RandomMinion(cost=6))),
        OWN_TURN_END.on(_tick_duration),
        OWN_TURN_BEGIN.on(_destroy_if_expired),
    ]
