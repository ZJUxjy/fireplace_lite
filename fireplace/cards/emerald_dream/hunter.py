# Hunter cards from EMERALD_DREAM expansion
from ..utils import *


ANIMAL_COMPANIONS = ["NEW1_032", "NEW1_033", "NEW1_034"]


def _friendly_hand_beasts(player):
    return [
        card
        for card in player.hand
        if card.type == CardType.MINION and card.race == Race.BEAST
    ]


class EDR_014_AttackIfDiscounted(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if source.cost > 3:
            return
        enemies = list(player.opponent.field)
        source.game.random.shuffle(enemies)
        return source.game.queue_actions(
            source, [Attack(source, enemy) for enemy in enemies[:2]]
        )


class EDR_226_Imbue(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        player._edr_850p_amount = getattr(player, "_edr_850p_amount", 0) + 1
        if player.hero.power.id != "EDR_850p":
            return source.game.queue_actions(source, [Summon(player, "EDR_850p")])


class EDR_261_Buff(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        return source.game.queue_actions(source, [Buff(target, "EDR_261e")])


class EDR_262_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        actions = [Hit(target, 3)]
        if target.health <= 3:
            actions.append(Summon(source.controller, "EDR_850pe"))
        return source.game.queue_actions(source, actions)


class EDR_416_SummonSheep(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [Summon(player, "EDR_416t").then(Dormant(Summon.CARD, 2))]
        )


class EDR_480_DoubleBeastAttackDamage(TargetedAction):
    ATTACKER = ActionArg()
    DEFENDER = ActionArg()

    def do(self, source, attacker, defender):
        if attacker.controller != source.controller or attacker.race != Race.BEAST:
            return
        return source.game.queue_actions(attacker, [Hit(defender, attacker.atk)])


class EDR_481_SummonCopy(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if source.atk < 4:
            return
        return source.game.queue_actions(source, [Summon(player, ExactCopy(SELF))])


class EDR_850p_BuffBeast(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        beasts = _friendly_hand_beasts(player)
        if not beasts:
            return
        target = source.game.random.choice(beasts)
        amount = getattr(player, "_edr_850p_amount", 1)
        return source.game.queue_actions(
            source,
            [
                Buff(target, "EDR_850pe1", amount=amount),
                Buff(target, "EDR_850pe5", amount=3),
            ],
        )


class EDR_853_SummonCompanion(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source, [Summon(player, source.game.random.choice(ANIMAL_COMPANIONS))]
        )


class FIR_953_SplitDamage(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, hound):
        if hound.zone != Zone.PLAY:
            return
        return source.game.queue_actions(
            hound, [Hit(RANDOM_ENEMY_CHARACTER, 1) for _ in range(hound.atk)]
        )


class FIR_960_CopyLowestBeast(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        beasts = _friendly_hand_beasts(player)
        if not beasts:
            return
        lowest_cost = min(card.cost for card in beasts)
        lowest = [card for card in beasts if card.cost == lowest_cost]
        copy = ExactCopy(TARGET).copy(source, source.game.random.choice(lowest))
        return source.game.queue_actions(
            source, [Give(player, copy)]
        )


##
# Minions


class EDR_014:
    """Verdant Dreamsaber"""

    play = EDR_014_AttackIfDiscounted(CONTROLLER)


class EDR_226:
    """Exotic Houndmaster"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + BEAST)), EDR_226_Imbue(CONTROLLER)


class EDR_227:
    """Umbraclaw"""

    rush = True
    deathrattle = EDR_226_Imbue(CONTROLLER)


class EDR_416:
    """Shepherd's Crook"""

    events = Attack(FRIENDLY_HERO).after(EDR_416_SummonSheep(CONTROLLER))


class EDR_416t:
    """Sleepy Sheep"""

    taunt = True


class EDR_480:
    """Goldrinn"""

    rush = True
    events = Attack(FRIENDLY_MINIONS + BEAST).on(
        EDR_480_DoubleBeastAttackDamage(Attack.ATTACKER, Attack.DEFENDER)
    )


class EDR_480e:
    """Greatwolf's Ferocity"""

    pass


class EDR_481:
    """Mythical Runebear"""

    taunt = True
    play = EDR_481_SummonCopy(CONTROLLER)


class EDR_853:
    """Broll Bearmantle"""

    events = Play(CONTROLLER, SPELL).after(EDR_853_SummonCompanion(CONTROLLER))


class EDR_853e:
    """Verdant Dreamsaber"""

    tags = {GameTag.ATK: 1, GameTag.HEALTH: 1}


##
# Spells


class EDR_261:
    """Amphibian's Spirit"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = EDR_261_Buff(TARGET)


class EDR_261e:
    """Amphibian's Spirit"""

    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2, GameTag.DEATHRATTLE: True}
    deathrattle = Buff(RANDOM_FRIENDLY_MINION, "EDR_261e")


class EDR_262:
    """Spirit Bond"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = EDR_262_Play(TARGET)


class EDR_263:
    """Grace of the Greatwolf"""

    play = Choice(CONTROLLER, ["EDR_263a", "EDR_263b"]).then(
        Battlecry(Choice.CARD, None)
    )


class EDR_263a:
    """Greatwolf's Ferocity"""

    play = Hit(ENEMY_HERO, 4)


class EDR_263b:
    """Greatwolf's Guidance"""

    play = Summon(CONTROLLER, "EDR_850pe") * 2


class EDR_850p:
    """Blessing of the Wolf"""

    activate = EDR_850p_BuffBeast(CONTROLLER)


class EDR_850pe:
    """Playful Pup"""

    rush = True


class EDR_850pe1:
    """Goldrinn's Courage"""

    def atk(self, atk):
        return atk + self.amount


class EDR_850pe5:
    """Great Wolf's Howl"""

    def cost(self, cost):
        return cost - self.amount


class FIR_909:
    """Bursting Shot"""

    play = Hit(RANDOM_ENEMY_CHARACTER, 2) * 3


class FIR_953:
    """Magma Hound"""

    rush = True
    events = Attack(SELF, MINION).after(FIR_953_SplitDamage(SELF))


class FIR_960:
    """Tending Dragonkin"""

    play = FIR_960_CopyLowestBeast(CONTROLLER)


##
# Dream Cards (from EDR_100 and EDR_101)


class EDR_100t10:
    """Nightmare Scales"""

    divine_shield = True


class EDR_100t10e:
    """Nightmare Scales"""

    pass


class EDR_101t:
    """Blinding Carapace"""

    divine_shield = True
    rush = True


class EDR_101t1:
    """Blinding Carapace"""

    divine_shield = True
    lifesteal = True


class EDR_101t2:
    """Blinding Carapace"""

    divine_shield = True
    reborn = True


class EDR_101t3:
    """Blinding Carapace"""

    divine_shield = True
    taunt = True


class EDR_101t4:
    """Blinding Carapace"""

    divine_shield = True
    poisonous = True


class EDR_101t5:
    """Blinding Carapace"""

    rush = True
    lifesteal = True


class EDR_101t6:
    """Blinding Carapace"""

    rush = True
    reborn = True


class EDR_101t7:
    """Blinding Carapace"""

    rush = True
    taunt = True


class EDR_101t8:
    """Blinding Carapace"""

    rush = True
    poisonous = True


class EDR_101t9:
    """Blinding Carapace"""

    lifesteal = True
    reborn = True


class EDR_101t10:
    """Blinding Carapace"""

    lifesteal = True
    taunt = True


class EDR_101t11:
    """Blinding Carapace"""

    lifesteal = True
    poisonous = True


class EDR_101t12:
    """Blinding Carapace"""

    reborn = True
    taunt = True


class EDR_101t13:
    """Blinding Carapace"""

    reborn = True
    poisonous = True


class EDR_101t14:
    """Blinding Carapace"""

    taunt = True
    poisonous = True
