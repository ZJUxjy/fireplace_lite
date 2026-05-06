from ..utils import *


UNGORO_QUEST_REWARDS = [
    "UNG_116t",
    "UNG_920t1",
    "UNG_028t",
    "UNG_954t1",
    "UNG_940t8",
    "UNG_067t1",
    "UNG_942t",
    "UNG_829t1",
    "UNG_934t1",
]


def _kindred(card):
    for played in getattr(card.controller, "cards_played_last_turn", []):
        if card.type == CardType.MINION and played.type == CardType.MINION:
            if set(card.races).intersection(played.races):
                return True
        spell_school = card.tags.get(GameTag.SPELL_SCHOOL)
        if spell_school and played.tags.get(GameTag.SPELL_SCHOOL) == spell_school:
            return True
    return False


class TLC_RandomTauntMinion(TargetedAction):
    TARGET = ActionArg()
    COST = IntArg()

    def do(self, source, player, cost):
        cards = [
            card_id
            for card_id, data in db.items()
            if data.collectible
            and data.type == CardType.MINION
            and data.cost == cost
            and data.tags.get(GameTag.TAUNT)
            and (not source.game.is_standard or data.is_standard)
        ]
        if cards:
            source.game.random.shuffle(cards)
            return source.game.queue_actions(source, [Summon(player, cards[0])])


class TLC_606_GainIfDead(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if target.dead or target.zone == Zone.GRAVEYARD:
            return source.game.queue_actions(source, [GainArmor(source.controller.hero, 5)])


class TLC_602t_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        rewards = UNGORO_QUEST_REWARDS[:]
        source.game.random.shuffle(rewards)
        return source.game.queue_actions(
            source,
            [Give(player, reward) for reward in rewards[:2]]
            + [Shuffle(player, reward) for reward in rewards[2:]],
        )


class TLC_601_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = min(player.hero.armor, 5)
        player.hero.armor -= amount
        if amount:
            return source.game.queue_actions(source, [Hit(ALL_MINIONS, amount)])


class TLC_623_BuffDamaged(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        damaged = [minion for minion in player.field if minion.damage > 0]
        if damaged:
            return source.game.queue_actions(
                source, [Buff(source.game.random.choice(damaged), "TLC_623e")]
            )


class TLC_624_CopyDamaged(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for minion in list(player.field):
            if minion is source or minion.damage <= 0:
                continue
            copy = ExactCopy(TARGET).copy(source, minion)
            actions.append(Summon(player, copy).then(GiveRush(Summon.CARD)))
        return source.game.queue_actions(source, actions)


class TLC_632_SetPower(TargetedAction):
    TARGET = ActionArg()
    POWER = ActionArg()
    ORIGINAL = ActionArg()

    def do(self, source, player, power_id, original_power_id=None):
        original_power_id = original_power_id or player.hero.power.id
        player.hero.power.zone = Zone.SETASIDE
        power = player.card(power_id, source=source)
        power._tlc_632_original_power_id = original_power_id
        return source.game.queue_actions(source, [Summon(player, power)])


class TLC_632_Activate(TargetedAction):
    TARGET = ActionArg()
    POWER = ActionArg()

    def do(self, source, player, next_power_id):
        original_power_id = getattr(source, "_tlc_632_original_power_id", "HERO_01bp")
        actions = [Hit(RANDOM_ENEMY_CHARACTER, 8)]
        if next_power_id:
            actions.append(TLC_632_SetPower(player, next_power_id, original_power_id))
        else:
            actions.append(TLC_632_SetPower(player, original_power_id, original_power_id))
        return source.game.queue_actions(source, actions)


class DINO_400:
    """Barricade Basher"""

    events = GainArmor(FRIENDLY_HERO).on(
        Buff(SELF, "DINO_400e"), Attack(SELF, RANDOM_ENEMY_MINION)
    )


DINO_400e = buff(+2, +2)


class DINO_401:
    """The Great Dracorex"""

    events = Attack(SELF).after(Hit(ENEMY_MINIONS - Attack.DEFENDER, ATK(SELF)))


class DINO_433:
    """Guard Duty"""

    play = (
        TLC_RandomTauntMinion(CONTROLLER, 6),
        TLC_RandomTauntMinion(CONTROLLER, 4),
        TLC_RandomTauntMinion(CONTROLLER, 2),
    )


class TLC_478:
    """Axe of the Forefathers"""

    events = Attack(FRIENDLY_HERO).after(Hit(ALL_MINIONS, 1))


class TLC_600:
    """Windpeak Wyrm"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    play = Hit(TARGET, 5), GainArmor(FRIENDLY_HERO, 5)

    def cost(self, cost):
        if _kindred(self):
            return cost - 3
        return cost


class TLC_601:
    """Shellnado"""

    play = TLC_601_Play(CONTROLLER)


class TLC_602:
    """Enter the Lost City"""

    quest = OWN_TURN_BEGIN.on(AddProgress(SELF, SELF))
    reward = Give(CONTROLLER, "TLC_602t")


class TLC_602t:
    """Latorvius, Gaze of the City"""

    play = TLC_602t_Play(CONTROLLER)


class TLC_606:
    """Latorvian Armorer"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Hit(TARGET, 2), Deaths(), TLC_606_GainIfDead(TARGET)


class TLC_620:
    """Fortify"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = GainArmor(FRIENDLY_HERO, 3).then(Hit(TARGET, ARMOR(FRIENDLY_HERO)))


class TLC_622:
    """City Defenses"""

    play = Summon(CONTROLLER, "TLC_622t") * 2


TLC_622e = buff(atk=1)


class TLC_622t:
    """Steadfast Security"""

    events = Damage(SELF).on(Buff(SELF, "TLC_622e"))


class TLC_623:
    """Stonecarver"""

    events = OWN_TURN_END.on(TLC_623_BuffDamaged(CONTROLLER))


TLC_623e = buff(+2, +2)


class TLC_624:
    """Nablya, the Watcher"""

    play = TLC_624_CopyDamaged(CONTROLLER)


class TLC_632:
    """Story of Sulfuras"""

    play = TLC_632_SetPower(CONTROLLER, "TLC_632t")


class TLC_632t:
    """DIE, INSECT!"""

    activate = TLC_632_Activate(CONTROLLER, "TLC_632t2")


class TLC_632t2:
    """DIE, INSECT!"""

    activate = TLC_632_Activate(CONTROLLER, None)
