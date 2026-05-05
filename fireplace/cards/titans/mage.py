from ..utils import *


##
# TTN_075: Norgannon (6费 3/8)
# 泰坦。使用技能后，其他技能效果翻倍

class TTN_075:
    """Norgannon"""

    tags = {GameTag.ELITE: True}

    titan_abilities = ["TTN_075t", "TTN_075t2", "TTN_075t3"]

    def ability_used(self):
        self._ttn_075_ability_multiplier = 2


def _ttn_075_multiplier(source):
    norgannon = getattr(source, "creator", None)
    if norgannon and norgannon.id == "TTN_075":
        return getattr(norgannon, "_ttn_075_ability_multiplier", 1)
    return 1


class TTN_075_Hit(TargetedAction):
    TARGET = ActionArg()
    AMOUNT = IntArg()

    def do(self, source, target, amount):
        return source.game.queue_actions(
            source, [Hit(target, amount * _ttn_075_multiplier(source))]
        )


class TTN_075_AncientKnowledge(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = _ttn_075_multiplier(source)
        actions = []
        for card in player.opponent.hand:
            actions.append(Buff(card, "TTN_075t2e", _ttn_075_cost_amount=amount))
        return source.game.queue_actions(source, actions)


class TTN_075_DestroyAncientKnowledge(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, buff):
        if buff.owner.controller.current_player:
            buff.remove()


# TTN_075t: Progenitor's Power - Deal 5 damage to a target
class TTN_075t:
    """Progenitor's Power"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    play = TTN_075_Hit(TARGET, 5)


# TTN_075t2: Ancient Knowledge - Enemy cards cost 1 more next turn
class TTN_075t2:
    """Ancient Knowledge"""

    play = TTN_075_AncientKnowledge(CONTROLLER)


@custom_card
class TTN_075t2e:
    tags = {
        GameTag.CARDNAME: "Ancient Knowledge",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = EndTurn().on(TTN_075_DestroyAncientKnowledge(SELF))

    def cost(self, value):
        if self.owner.controller.current_player:
            return value + getattr(self, "_ttn_075_cost_amount", 0)
        return value


# TTN_075t3: Unlimited Potential - Cast 1 random Mage secret
class TTN_075t3:
    """Unlimited Potential"""

    play = Summon(CONTROLLER, RandomSpell(secret=True, card_class=CardClass.MAGE))
