from hearthstone.enums import SpellSchool

from ..utils import *


##
# Minions


_BLOOD_RUNE_CARDS = {
    "TOY_824",
    "MIS_100",
    "MIS_101",
}
_FROST_RUNE_CARDS = {
    "TOY_821",
    "TOY_825",
    "TOY_825t",
    "TOY_825t2",
}
_UNHOLY_RUNE_CARDS = {
    "TOY_822",
    "TOY_823",
    "TOY_827",
    "TOY_828",
    "TOY_829",
    "TOY_830",
    "MIS_006",
    "MIS_006t",
}


def _started_with_any(player, ids):
    return any(card.id in ids for card in player.starting_deck)


class TOY_827_SpendCorpses(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if getattr(player, "corpses", 0) < 5:
            return
        player.corpses -= 5
        return source.game.queue_actions(source, [
            Summon(player, ExactCopy(SELF))
        ])


class TOY_827:
    """Shambling Zombietank"""

    tags = {GameTag.TAUNT: True}
    play = TOY_827_SpendCorpses(CONTROLLER)


class TOY_821_GainReborn(TargetedAction):
    TARGET = ActionArg()
    SPELL = ActionArg()

    def do(self, source, target, spell):
        if getattr(getattr(spell, "data", None), "spell_school", None) != SpellSchool.FROST:
            return
        return source.game.queue_actions(source, [
            GiveReborn(target)
        ])


class TOY_821:
    """Rambunctious Stuffy"""

    tags = {GameTag.RUSH: True}
    events = Play(CONTROLLER, SPELL).after(TOY_821_GainReborn(SELF, Play.CARD))


class TOY_824:
    """Darkthorn Quilter"""

    events = OWN_TURN_END.on(Hit(RANDOM(ENEMY_CHARACTERS), 1) * ATK(SELF))


class TOY_823_GainStartedRuneKeywords(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        player = target.controller
        actions = []
        if _started_with_any(player, _BLOOD_RUNE_CARDS):
            actions.append(SetTag(target, GameTag.LIFESTEAL))
        if _started_with_any(player, _FROST_RUNE_CARDS):
            actions.append(GiveReborn(target))
        if _started_with_any(player, _UNHOLY_RUNE_CARDS):
            actions.append(GiveRush(target))
        return source.game.queue_actions(source, actions)


class TOY_823:
    """Rainbow Seamstress"""

    play = TOY_823_GainStartedRuneKeywords(SELF)


# TOY_828: Amateur Puppeteer (5费 3/4)
# 微缩。嘲讽。亡语：给你手牌中的不死随从+2/+2
class TOY_828:
    """Amateur Puppeteer"""

    tags = {GameTag.TAUNT: True}

    deathrattle = Buff(FRIENDLY_HAND + UNDEAD, "TOY_828e")


@custom_card
class TOY_828e:
    tags = {
        GameTag.CARDNAME: "Amateur Puppeteer Buff",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 2,
        GameTag.HEALTH: 2,
    }


class TOY_830_StoreStitch(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, target, card):
        if not hasattr(target, "stitched_cards"):
            target.stitched_cards = []
            target.stitched_index = 0
        target.stitched_cards.append(card)


class TOY_830_AttachStitch(TargetedAction):
    TARGET = ActionArg()
    CARDS = ActionArg()
    INDEX = IntArg()

    def do(self, source, target, cards, index):
        buff = source.controller.card("TOY_830e", source=source)
        buff.source = source
        buff.stitched_cards = cards
        buff.stitched_index = index
        buff.apply(target)


class TOY_830_SummonStitch(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        cards = getattr(target, "stitched_cards", [])
        index = getattr(target, "stitched_index", 0)
        if index >= len(cards):
            return

        summon = Summon(target.controller, cards[index])
        if index + 1 < len(cards):
            summon = summon.then(
                TOY_830_AttachStitch(Summon.CARD, cards, index + 1)
            )
        return source.game.queue_actions(source, [summon])


class TOY_830:
    """Dr. Stitchensew"""

    play = Discover(CONTROLLER, RandomMinion(cost=5)).then(
        TOY_830_StoreStitch(SELF, Discover.CARD),
        Discover(CONTROLLER, RandomMinion(cost=3)).then(
            TOY_830_StoreStitch(SELF, Discover.CARD),
            Discover(CONTROLLER, RandomMinion(cost=1)).then(
                TOY_830_StoreStitch(SELF, Discover.CARD)
            )
        )
    )
    deathrattle = TOY_830_SummonStitch(SELF)


@custom_card
class TOY_830e:
    tags = {
        GameTag.CARDNAME: "Stitched Toys",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.DEATHRATTLE: True,
    }

    deathrattle = TOY_830_SummonStitch(SELF)


class MIS_006:
    """Toysnatching Geist"""

    play = Give(CONTROLLER, "MIS_006t"), Discover(
        CONTROLLER, RandomMinion(race=Race.UNDEAD)
    ).then(Give(CONTROLLER, Buff(Discover.CARD, "MIS_006e1", cost=-ATK(SELF))))


class MIS_006t:
    """Toysnatching Geist"""

    play = Discover(CONTROLLER, RandomMinion(race=Race.UNDEAD)).then(
        Give(CONTROLLER, Buff(Discover.CARD, "MIS_006e1", cost=-ATK(SELF)))
    )


@custom_card
class MIS_006e1:
    tags = {
        GameTag.CARDNAME: "Collection Bonus",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


##
# Spells


class TOY_822_CheapSpellPicker(RandomCardPicker):
    def __init__(self):
        super().__init__(
            collectible=True,
            type=CardType.SPELL,
            cost=range(5),
            card_class=CardClass.DEATHKNIGHT,
            is_standard=True,
        )

    def evaluate(self, source, cards=None):
        card_ids = self.find_cards(source)
        if len(card_ids) < self.count:
            card_ids = db.filter(
                collectible=True,
                type=CardType.SPELL,
                cost=range(5),
                card_class=CardClass.DEATHKNIGHT,
            )
        count = min(self.count, len(card_ids))
        picked = source.game.random.sample(card_ids, count)
        return [source.controller.card(card_id, source=source) for card_id in picked]

    def __mul__(self, other):
        ret = type(self)()
        ret.count = other
        return ret


class TOY_822:
    """Silk Stitching"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Discover(CONTROLLER, TOY_822_CheapSpellPicker()).then(
        StoringBuff(TARGET, "TOY_822e", Discover.CARD)
    )


@custom_card
class TOY_822e:
    tags = {
        GameTag.CARDNAME: "Darkness Within",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.DEATHRATTLE: True,
    }

    deathrattle = CastSpell(STORE_CARD)


class TOY_825:
    """Lesser Spinel Spellstone"""

    play = Buff(FRIENDLY_HAND + UNDEAD, "TOY_825e")
    progress_total = 5
    reward = Morph(SELF, "TOY_825t")

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))


class TOY_825t:
    """Spinel Spellstone"""

    play = Buff(FRIENDLY_HAND + UNDEAD, "TOY_825e2")
    progress_total = 5
    reward = Morph(SELF, "TOY_825t2")

    class Hand:
        events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))


class TOY_825t2:
    """Greater Spinel Spellstone"""

    play = Buff(FRIENDLY_HAND + UNDEAD, "TOY_825e3")


TOY_825e = buff(+1, +1)
TOY_825e2 = buff(+2, +2)
TOY_825e3 = buff(+3, +3)


class TOY_826:
    """Threads of Despair"""

    play = Buff(ALL_MINIONS, "TOY_826e")


@custom_card
class TOY_826e:
    tags = {
        GameTag.CARDNAME: "Threads of Despair",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.DEATHRATTLE: True,
    }

    deathrattle = Hit(ALL_MINIONS, 1)


class MIS_100:
    """Helm of Humiliation"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }

    play = Buff(TARGET, "MIS_100e", atk=-5, max_health=-5), Buff(
        RANDOM(FRIENDLY_HAND + MINION), "MIS_100e2", atk=5, max_health=5
    )


@custom_card
class MIS_100e:
    tags = {
        GameTag.CARDNAME: "Humiliated",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


@custom_card
class MIS_100e2:
    tags = {
        GameTag.CARDNAME: "Inspired",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


class TOY_829:
    """The Headless Horseman"""

    play = Destroy(HIGHEST_ATK(ENEMY_MINIONS)), Shuffle(CONTROLLER, "TOY_829t")


class TOY_829t:
    """Horseman's Head"""

    draw = CAST_WHEN_DRAWN
    play = Summon(CONTROLLER, "TOY_829hp")


class TOY_829hp:
    """Pulsing Pumpkins"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    activate = Hit(TARGET, 3), Discover(
        CONTROLLER, RandomMinion(race=Race.UNDEAD)
    ).then(Give(CONTROLLER, Discover.CARD))


class TOY_829hp3:
    """Pulsing Pumpkins"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }

    activate = Hit(TARGET, 3)


##
# Weapons


class MIS_101_GainDurability(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        player = weapon.controller
        if getattr(player, "corpses", 0) < 3:
            return
        player.corpses -= 3
        return source.game.queue_actions(source, [
            Buff(weapon, "MIS_101e")
        ])


class MIS_101:
    """Foamrender"""

    events = Attack(FRIENDLY_HERO).on(MIS_101_GainDurability(SELF))


MIS_101e = buff(health=1)
