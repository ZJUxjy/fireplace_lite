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


class AV_131_Hit(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        honorable_kill = target.type != CardType.HERO and target.health == 3
        ret = source.game.queue_actions(source, [Hit(target, 3)])
        if honorable_kill and target.dead:
            source.game.queue_actions(source, [Buff(source, "AV_131e")])
        return ret


class AV_131:
    """Knight-Captain"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_MINION_OR_ENEMY_HERO: 0,
    }
    play = AV_131_Hit(TARGET)


AV_131e = buff(+3, +3)


class AV_136:
    """Kobold Taskmaster"""

    play = Give(CONTROLLER, "AV_136t") * 2


class AV_136t:
    """Armor Scrap"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "AV_136e")


AV_136e = buff(health=2)


class AV_138:
    """Grimtotem Bounty Hunter"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Destroy(TARGET + LEGENDARY)


class AV_142t_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        mana = player.mana
        player.mana = 0
        bonuses = ("stats", "rush", "divine_shield", "taunt")
        actions = []
        for _ in range(mana):
            bonus = source.game.random.choice(bonuses)
            if bonus == "stats":
                actions.append(Buff(source, "AV_142te"))
            elif bonus == "rush":
                actions.append(GiveRush(source))
            elif bonus == "divine_shield":
                actions.append(GiveDivineShield(source))
            else:
                actions.append(Taunt(source))
        return source.game.queue_actions(source, actions)


class AV_142t:
    """Ivus, the Forest Lord"""

    play = AV_142t_Play(CONTROLLER)


AV_142te = buff(+2, +2)


class AV_143_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if source.health != 0:
            return source.game.queue_actions(source, [Summon(player, "AV_143")])


class AV_143:
    """Korrak the Bloodrager"""

    deathrattle = AV_143_Deathrattle(CONTROLLER)


class AV_145:
    """Captain Galvangar"""

    play = (Attr(CONTROLLER, "armor_gained_this_game") >= 15) & (
        Buff(SELF, "AV_145e"),
        GiveCharge(SELF),
    )


AV_145e = buff(+3, +3)


class AV_200_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells_by_school = {}
        for card in player.cards_played_this_game:
            if card.type != CardType.SPELL:
                continue
            school = getattr(getattr(card, "data", None), "spell_school", None)
            if school:
                spells_by_school.setdefault(school, []).append(card)
        actions = []
        for spells in spells_by_school.values():
            chosen = source.game.random.choice(spells)
            actions.append(
                CastSpellTargetsEnemiesIfPossible(player.card(chosen.id, source=source))
            )
        return source.game.queue_actions(source, actions)


class AV_200:
    """Magister Dawngrasp"""

    play = AV_200_Play(CONTROLLER)


class AV_202:
    """Rokara, the Valorous"""

    play = Summon(CONTROLLER, "AV_202t2")


class AV_203_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = list(source.game.board)
        actions = [Bounce(minion) for minion in minions]
        actions.extend([Summon(player, "AV_203t"), Summon(player, "AV_203t")])
        return source.game.queue_actions(source, actions)


class AV_203:
    """Shadowcrafter Scabbs"""

    play = AV_203_Play(CONTROLLER)


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


class AV_704:
    """Humongous Owl"""

    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS - DEAD), 8)


class BAR_027:
    """Darkspear Berserker"""

    deathrattle = Hit(FRIENDLY_HERO, 5)


class BAR_072:
    """Burning Blade Acolyte"""

    deathrattle = Summon(CONTROLLER, "BAR_072t")


BAR_324_POISONS = [
    "CORE_CS2_074",
    "CORE_ICC_221",
    "YOP_015",
    "BAR_318",
    "BAR_321",
]


class BAR_324_AddPoison(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        poison = source.game.random.choice(BAR_324_POISONS)
        return source.game.queue_actions(source, [Give(player, poison)])


class BAR_324:
    """Apothecary Helbrim"""

    play = BAR_324_AddPoison(CONTROLLER)
    deathrattle = BAR_324_AddPoison(CONTROLLER)


class BAR_325:
    """Razorboar"""

    deathrattle = Summon(CONTROLLER, RANDOM(FRIENDLY_HAND + DEATHRATTLE + (COST <= 3)))


class BAR_326:
    """Razorfen Beastmaster"""

    deathrattle = Summon(CONTROLLER, RANDOM(FRIENDLY_HAND + DEATHRATTLE + (COST <= 4)))


class BAR_310:
    """Lightshower Elemental"""

    deathrattle = Heal(FRIENDLY_CHARACTERS, 8)


class BAR_026:
    """Death's Head Cultist"""

    deathrattle = Heal(FRIENDLY_HERO, 4)
