from hearthstone.enums import SpellSchool, Zone

from ..utils import *


def _is_demon(card):
    return Race.DEMON in getattr(getattr(card, "data", None), "races", [])


def _table_flip_cost(entity, cost):
    return max(0, cost - max(0, len(entity.controller.hand) - 1))


class MIS_027_DominoEffect(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        field = target.controller.field
        if target not in field:
            return
        start = field.index(target)
        if start == 0:
            direction = 1
        elif start == len(field) - 1:
            direction = -1
        else:
            direction = source.game.random.choice((-1, 1))

        amount = 2
        index = start
        while 0 <= index < len(field):
            current = field[index]
            source.game.queue_actions(source, [Hit(current, amount)])
            amount += 1
            index += direction


class MIS_703_Infernal(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        player.hero.damage = max(0, player.hero.max_health - 15)
        source.game.manager.targeted_action(self, source, player.hero)


class TOY_524_NemsyDraw(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        demons = [card for card in player.deck if _is_demon(card)]
        if not demons:
            return
        demon = source.game.random.choice(demons)
        source._nemsy_demon = demon
        return source.game.queue_actions(source, [ForceDraw(demon)])


class TOY_524_NemsySwap(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        demon = getattr(source, "_nemsy_demon", None)
        if demon is None or demon.zone != Zone.HAND:
            return
        source.game.queue_actions(source, [Summon(player, demon)])
        source.zone = Zone.HAND
        source.game.manager.targeted_action(self, source, demon)


class TOY_529_StartWheel(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        for card in list(player.deck):
            card.zone = Zone.REMOVEDFROMGAME
            source.game.manager.targeted_action(self, source, card)
        return source.game.queue_actions(
            source,
            [Buff(player.opponent, "TOY_529e1", _wheel_turns=5)],
        )


class TOY_529_Tick(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, buff):
        buff._wheel_turns = getattr(buff, "_wheel_turns", 5) - 1
        if buff._wheel_turns <= 0:
            buff.remove()
            return source.game.queue_actions(source, [Destroy(buff.owner.hero)])


class TOY_884_CraneGame(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        demons = [card for card in player.deck if _is_demon(card)][:2]
        return source.game.queue_actions(
            source,
            [Summon(player, player.card(demon.id, source=source)) for demon in demons],
        )


class TOY_886_Endgame(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        for card in reversed(player.graveyard):
            if _is_demon(card):
                return source.game.queue_actions(source, [Summon(player, card.id)])


class TOY_916_SketchArtist(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = [
            card
            for card in player.deck
            if card.type == CardType.SPELL
            and getattr(card.data, "spell_school", None) == SpellSchool.SHADOW
        ]
        if not spells:
            return
        spell = source.game.random.choice(spells)
        copy = player.card(spell.id, source=source)
        return source.game.queue_actions(
            source, [ForceDraw(spell), Give(player, Buff(copy, "TOY_916e"))]
        )


##
# Minions


class MIS_703:
    """INFERNAL!"""

    tags = {GameTag.TAUNT: True}
    play = MIS_703_Infernal(CONTROLLER)


class TOY_524:
    """Game Master Nemsy"""

    play = TOY_524_NemsyDraw(CONTROLLER)
    deathrattle = TOY_524_NemsySwap(CONTROLLER)


class TOY_526:
    """Malefic Rook"""

    play = Attack(SELF, FRIENDLY_HERO)


class TOY_914:
    """Wretched Queen"""

    tags = {GameTag.TAUNT: True}
    deathrattle = Summon(CONTROLLER, "TOY_914t") * 2


class TOY_915:
    """Tabletop Roleplayer"""

    miniaturize_mini = "TOY_915t"
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_WITH_RACE: Race.DEMON,
    }

    play = Buff(TARGET, "TOY_915e")


class TOY_915t:
    """Tabletop Roleplayer"""

    requirements = TOY_915.requirements
    play = TOY_915.play


class TOY_916:
    """Sketch Artist"""

    play = TOY_916_SketchArtist(CONTROLLER)


##
# Spells


class MIS_027:
    """Domino Effect"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = MIS_027_DominoEffect(TARGET)


class MIS_707:
    """Mass Production"""

    play = (
        Draw(CONTROLLER) * 2,
        Hit(FRIENDLY_HERO, 3),
        Shuffle(CONTROLLER, "MIS_707") * 2,
    )


class TOY_527:
    """Cursed Campaign"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "TOY_527e")


class TOY_529:
    """Wheel of DEATH!!!"""

    play = TOY_529_StartWheel(CONTROLLER)


class TOY_883:
    """Table Flip"""

    play = Hit(ENEMY_MINIONS, 3)

    class Hand:
        update = Refresh(SELF, {GameTag.COST: _table_flip_cost})


class TOY_884:
    """Crane Game"""

    play = TOY_884_CraneGame(CONTROLLER)


class TOY_886:
    """Endgame"""

    play = TOY_886_Endgame(CONTROLLER)


##
# Buffs


class TOY_527e:
    tags = {GameTag.DEATHRATTLE: True}
    deathrattle = Summon(CONTROLLER, Copy(OWNER)).then(Dormant(Summon.CARD, 2)) * 2


class TOY_529e1:
    events = OWN_TURN_BEGIN.on(TOY_529_Tick(SELF))


class TOY_915e:
    tags = {
        GameTag.TAG_ONE_TURN_EFFECT: True,
        GameTag.ATK: 2,
        GameTag.IMMUNE: True,
    }

    events = OWN_TURN_END.on(Destroy(SELF))


@custom_card
class TOY_916e:
    tags = {
        GameTag.CARDNAME: "Sketch",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    class Hand:
        events = OWN_TURN_END.on(Discard(OWNER))

    events = REMOVED_IN_PLAY
