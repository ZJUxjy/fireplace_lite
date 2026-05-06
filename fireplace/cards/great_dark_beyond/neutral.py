from ..utils import *
from hearthstone.enums import SpellSchool


class SC_000:
    """Spawning Pool"""

    activate = Give(CONTROLLER, "SC_010")
    deathrattle = GiveRush(FRIENDLY_MINIONS + FuncSelector(
        lambda entities, source: [
            entity
            for entity in entities
            if getattr(getattr(entity, "data", None), "tags", {}).get(GameTag.ZERG)
        ]
    ))


SC_ZERG_MINIONS = FRIENDLY_MINIONS + FuncSelector(
    lambda entities, source: [
        entity
        for entity in entities
        if getattr(getattr(entity, "data", None), "tags", {}).get(GameTag.ZERG)
    ]
)

SC_PROTOSS_HAND_OR_DECK = FRIENDLY + (IN_HAND | IN_DECK) + FuncSelector(
    lambda entities, source: [
        entity
        for entity in entities
        if getattr(getattr(entity, "data", None), "tags", {}).get(GameTag.PROTOSS)
    ]
)


class SC_002:
    """Infestor"""

    deathrattle = Buff(CONTROLLER, "SC_002e")


@custom_card
class SC_002e:
    tags = {
        GameTag.CARDNAME: "For the Swarm",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    update = Refresh(SC_ZERG_MINIONS, {GameTag.ATK: +1})


class SC_019:
    """Ultralisk Cavern"""

    activate = Hit(ENEMY_CHARACTERS, 1)
    deathrattle = Summon(CONTROLLER, "SC_006")


class SC_762_GetProtossMinions(TargetedAction):
    TARGET = ActionArg()

    def _pool(self, source):
        pool = [
            card_id
            for card_id, data in db.items()
            if data.collectible
            and data.type == CardType.MINION
            and data.tags.get(GameTag.PROTOSS)
            and (not source.game.is_standard or data.is_standard)
        ]
        if not pool and source.game.is_standard:
            pool = [
                card_id
                for card_id, data in db.items()
                if data.collectible
                and data.type == CardType.MINION
                and data.tags.get(GameTag.PROTOSS)
            ]
        return pool

    def do(self, source, player):
        pool = self._pool(source)
        if not pool:
            return
        return source.game.queue_actions(
            source, [Give(player, source.game.random.choice(pool)) for _ in range(2)]
        )


class SC_762:
    """Mothership"""

    play = deathrattle = SC_762_GetProtossMinions(CONTROLLER)


class SC_764:
    """Sentry"""

    deathrattle = Buff(CONTROLLER, "SC_764e")


@custom_card
class SC_764e:
    tags = {
        GameTag.CARDNAME: "Sentry",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    update = Refresh(SC_PROTOSS_HAND_OR_DECK, {GameTag.COST: -1})


GDB_117_CREWMATES = [
    "GDB_471t",
    "GDB_471t2",
    "GDB_471t3",
    "GDB_471t4",
    "GDB_471t5",
    "GDB_471t6",
    "GDB_471t7",
    "GDB_471t8",
]


class GDB_100:
    """Arkonite Defense Crystal"""

    deathrattle = GainArmor(FRIENDLY_HERO, 4)


class GDB_111:
    """Biopod"""

    deathrattle = Hit(RANDOM_ENEMY_CHARACTER, ATK(SELF))


class GDB_112_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [Summon(player, RandomMinion(cost=min(source.atk, 10)))]
        )


class GDB_112:
    """Soulbound Spire"""

    deathrattle = GDB_112_Deathrattle(CONTROLLER)


class GDB_117_DrawCrewmates(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        crewmates = [card for card in player.deck if card.id in GDB_117_CREWMATES]
        source.game.random.shuffle(crewmates)
        return source.game.queue_actions(
            source, [ForceDraw(card) for card in crewmates[:2]]
        )


class GDB_117:
    """Dirdra, Rebel Captain"""

    play = Shuffle(CONTROLLER, GDB_117_CREWMATES)
    deathrattle = GDB_117_DrawCrewmates(CONTROLLER)


class GDB_131_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        for card in list(player.cards_played_this_game):
            if card is source or card.id == source.id:
                continue
            if card.type != CardType.MINION or Race.DRAENEI not in card.races:
                continue
            actions = list(card.get_actions("play")) + list(card.get_actions("deathrattle"))
            if actions:
                source.game.queue_actions(card, actions)


class GDB_131:
    """Velen, Leader of the Exiled"""

    deathrattle = GDB_131_Deathrattle(CONTROLLER)


class GDB_141:
    """Yrel, Beacon of Hope"""

    deathrattle = Give(CONTROLLER, "BT_011"), Give(CONTROLLER, "BT_024"), Give(CONTROLLER, "BT_025")


class GDB_226:
    """Hostile Invader"""

    play = Hit(ALL_MINIONS - SELF, 2)
    events = Play(CONTROLLER, SPELL).after(Hit(ALL_MINIONS - SELF, 2))
    deathrattle = Hit(ALL_MINIONS - SELF, 2)


class GDB_331:
    """Splitting Spacerock"""

    deathrattle = Summon(CONTROLLER, "GDB_331t1") * 2


class GDB_331t1:
    """Splitting Boulder"""

    deathrattle = Summon(CONTROLLER, "GDB_331t2") * 2


class GDB_331t2:
    """Splitting Stone"""

    deathrattle = Summon(CONTROLLER, "GDB_331t3") * 2


class GDB_333:
    """Space Pirate"""

    deathrattle = Buff(CONTROLLER, "GDB_333e")


@custom_card
class GDB_333e:
    tags = {
        GameTag.CARDNAME: "Space Pirate",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    update = Refresh(FRIENDLY_HAND + WEAPON, {GameTag.COST: -1})
    events = Play(CONTROLLER, WEAPON).after(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))


class GDB_136t_Absorb(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, location, spell):
        location._gdb_136t_spell = source.controller.card(spell.id, source=source)


class GDB_136t_CastAbsorbed(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, location):
        spell = getattr(location, "_gdb_136t_spell", None)
        if spell:
            return source.game.queue_actions(source, [CastSpell(spell)])


class GDB_136t:
    """The Galaxy's Lens"""

    events = Play(CONTROLLER, SPELL).after(GDB_136t_Absorb(SELF, Play.CARD))
    activate = GDB_136t_CastAbsorbed(SELF)


class GDB_447:
    """Farseer Nobundo"""

    deathrattle = Summon(CONTROLLER, "GDB_136t")


class GDB_468_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        candidates = [
            card
            for card in player.graveyard
            if (
                card is not source
                and card.id != source.id
                and card.type == CardType.MINION
                and card.has_deathrattle
            )
        ]
        if candidates:
            card = source.game.random.choice(candidates)
            copy = ExactCopy(TARGET).copy(source, card)
            return source.game.queue_actions(source, [Summon(player, copy)])


class GDB_468:
    """Wakener of Souls"""

    deathrattle = GDB_468_Deathrattle(CONTROLLER)


class GDB_454:
    """Overzealous Healer"""

    deathrattle = Heal(ENEMY_HERO, 6)
    events = Play(CONTROLLER, SPELL).after(Silence(SELF))


class GDB_721:
    """Interstellar Wayfarer"""

    play = deathrattle = Buff(CONTROLLER, "GDB_721e")


@custom_card
class GDB_721e:
    tags = {
        GameTag.CARDNAME: "Interstellar Wayfarer",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    update = Refresh(FRIENDLY + (IN_HAND | IN_DECK) + LIBRAM, {GameTag.COST: -1})


class GDB_726:
    """Interstellar Starslicer"""

    play = deathrattle = Buff(CONTROLLER, "GDB_721e")


class GDB_840_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        enemies = [
            character
            for character in player.opponent.characters
            if not getattr(character, "dead", False)
        ]
        actions = [Summon(player, "GDB_840t")]
        if enemies:
            target = min(enemies, key=lambda character: (character.health, character.id))
            actions[0] = actions[0].then(Attack(Summon.CARD, target))
        return source.game.queue_actions(source, actions)


class GDB_840:
    """Extraterrestrial Egg"""

    deathrattle = GDB_840_Deathrattle(CONTROLLER)


class GDB_862:
    """Galactic Crusader"""

    deathrattle = Give(CONTROLLER, RandomSpell(spell_school=SpellSchool.HOLY)).then(
        Buff(Give.CARD, "GDB_862e")
    ) * 2


@custom_card
class GDB_862e:
    tags = {
        GameTag.CARDNAME: "Galactic Crusader",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.COST: -3,
    }


class GDB_877_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        position = getattr(source, "_dead_position", None)
        if position is None:
            return
        adjacent = []
        if position > 0 and position - 1 < len(player.field):
            adjacent.append(player.field[position - 1])
        if position < len(player.field):
            adjacent.append(player.field[position])
        actions = []
        for minion in adjacent:
            actions.append(Buff(minion, "GDB_877e"))
            actions.append(GiveRush(minion))
        if actions:
            return source.game.queue_actions(source, actions)


class GDB_877:
    """Escape Pod"""

    deathrattle = GDB_877_Deathrattle(CONTROLLER)


GDB_877e = buff(+1, +1)


class GDB_722_BuffHandDraenei(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        draenei = [
            card
            for card in player.hand
            if card.type == CardType.MINION and Race.DRAENEI in card.races
        ]
        return source.game.queue_actions(source, [Buff(card, "GDB_722e") for card in draenei])


class GDB_722:
    """Crimson Commander"""

    play = GDB_722_BuffHandDraenei(CONTROLLER)
    deathrattle = GDB_722_BuffHandDraenei(CONTROLLER)


GDB_722e = buff(+2, +1)
