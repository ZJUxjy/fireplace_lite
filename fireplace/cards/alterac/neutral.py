from ..utils import *
from hearthstone.enums import SpellSchool


AV_113_SECRETS = [
    "AV_113t1",
    "AV_113t2",
    "AV_113t3",
    "AV_113t7",
    "AV_113t8",
    "AV_113t9",
]


class AV_113_Play(MultipleChoice):
    choose_times = 2

    def _secret_pool(self):
        active = {secret.id for secret in self.player.secrets}
        chosen = {card.id for card in self.choosed_cards}
        return [
            self.player.card(card_id, source=self.source)
            for card_id in AV_113_SECRETS
            if card_id not in active and card_id not in chosen
        ]

    def do_step1(self):
        pool = self._secret_pool()
        self.cards = self.source.game.random.sample(pool, min(3, len(pool)))

    def do_step2(self):
        pool = self._secret_pool()
        self.cards = self.source.game.random.sample(pool, min(3, len(pool)))

    def done(self):
        return self.source.game.queue_actions(
            self.source, [Summon(self.player, card) for card in self.choosed_cards]
        )


class AV_113:
    """Beaststalker Tavish"""

    play = AV_113_Play(CONTROLLER)


class AV_101_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        frost_spells = [
            card
            for card in player.deck
            if card.type == CardType.SPELL
            and getattr(getattr(card, "data", None), "spell_school", None)
            == SpellSchool.FROST
        ]
        if frost_spells:
            return source.game.queue_actions(
                source, [Draw(player, source.game.random.choice(frost_spells))]
            )


class AV_101:
    """Herald of Lokholar"""

    play = AV_101_Play(CONTROLLER)


class AV_102:
    """Popsicooler"""

    deathrattle = Freeze(RANDOM(ENEMY_MINIONS - DEAD) * 2)


class AV_112:
    """Snowblind Harpy"""

    play = Find(
        FRIENDLY_HAND
        + SPELL
        + FuncSelector(
            lambda entities, source: [
                card
                for card in entities
                if getattr(getattr(card, "data", None), "spell_school", None)
                == SpellSchool.FROST
            ]
        )
    ) & GainArmor(FRIENDLY_HERO, 5)


AV_114e = buff(cost=-1)


class AV_114:
    """Shivering Sorceress"""

    play = Buff(HIGHEST_COST(FRIENDLY_HAND + SPELL), "AV_114e")


class AV_115:
    """Amplified Snowflurry"""

    play = Buff(CONTROLLER, "AV_115e")


class AV_115e:
    update = Refresh(FRIENDLY_HERO_POWER, {GameTag.COST: SET(0)})
    events = Activate(CONTROLLER, FRIENDLY_HERO_POWER).after(
        Freeze(Activate.TARGET), Destroy(SELF)
    )


class AV_125:
    """Tower Sergeant"""

    play = (Count(FRIENDLY_MINIONS - SELF) >= 2) & Buff(SELF, "AV_125e")


AV_125e = buff(+2, +2)


class AV_126:
    """Bunker Sergeant"""

    play = (Count(ENEMY_MINIONS) >= 2) & Hit(ENEMY_MINIONS, 1)


class AV_130:
    """Legionnaire"""

    deathrattle = Buff(FRIENDLY_HAND + MINION, "AV_130e")


AV_130e = buff(+2, +2)


class AV_143_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if source.health != 0:
            return source.game.queue_actions(source, [Summon(player, "AV_143")])


class AV_143:
    """Korrak the Bloodrager"""

    deathrattle = AV_143_Deathrattle(CONTROLLER)


class AV_100_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.deck if card.type == CardType.MINION]
        if minions and all(source.cost > card.cost for card in minions):
            return source.game.queue_actions(
                source, [Summon(player, source.game.random.choice(minions))]
            )


class AV_100:
    """Drek'Thar"""

    play = AV_100_Play(CONTROLLER)


class AV_211:
    """Dire Frostwolf"""

    deathrattle = Summon(CONTROLLER, "AV_211t")


class AV_309:
    """Piggyback Imp"""

    deathrattle = Summon(CONTROLLER, "AV_309t")


class AV_325:
    """Undying Disciple"""

    deathrattle = Hit(ENEMY_MINIONS, ATK(SELF))


class AV_328_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for school in (SpellSchool.HOLY, SpellSchool.SHADOW):
            spells = [
                card
                for card in player.deck
                if card.type == CardType.SPELL
                and getattr(getattr(card, "data", None), "spell_school", None)
                == school
            ]
            if spells:
                actions.append(Draw(player, source.game.random.choice(spells)))
        return source.game.queue_actions(source, actions)


class AV_328:
    """Spirit Guide"""

    deathrattle = AV_328_Deathrattle(CONTROLLER)


class AV_331_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        source._najak_stolen_minion = target
        source._najak_original_controller = target.controller
        return source.game.queue_actions(source, [Steal(target)])


class AV_331_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        stolen = getattr(source, "_najak_stolen_minion", None)
        controller = getattr(source, "_najak_original_controller", None)
        if stolen and controller and stolen.zone == Zone.PLAY:
            return source.game.queue_actions(source, [Steal(stolen, controller)])


class AV_331:
    """Najak Hexxen"""

    requirements = {
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = AV_331_Play(TARGET)
    deathrattle = AV_331_Deathrattle(CONTROLLER)


class AV_334:
    """Stormpike Battle Ram"""

    deathrattle = Buff(CONTROLLER, "AV_334e")


class AV_334e:
    events = Play(CONTROLLER, BEAST).on(Destroy(SELF))
    update = Refresh(FRIENDLY_HAND + BEAST, {GameTag.COST: -2})


class AV_337:
    """Mountain Bear"""

    deathrattle = Summon(CONTROLLER, "AV_337t") * 2


class AV_341:
    """Cavalry Horn"""

    deathrattle = Summon(CONTROLLER, LOWEST_COST(FRIENDLY_HAND + MINION))
