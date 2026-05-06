from ..utils import *
from fireplace.cards import db
from fireplace import cards
from fireplace.utils import CardList
from hearthstone.enums import CardClass, SpellSchool


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


class AV_204_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = player.hero_attacks_this_game
        actions = []
        for _ in range(2):
            demon = player.card("AV_204t2", source=source)
            if amount:
                actions.append(Buff(demon, "AV_204e", atk=amount))
            actions.append(Summon(player, demon))
        return source.game.queue_actions(source, actions)


class AV_204:
    """Kurtrus, Demon-Render"""

    play = AV_204_Play(CONTROLLER)


class AV_205_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        player.max_resources = 20
        return source.game.queue_actions(
            source, [GainEmptyMana(player, 1), Draw(player)]
        )


class AV_205:
    """Wildheart Guff"""

    play = AV_205_Play(CONTROLLER)


class AV_206:
    """Lightforged Cariel"""

    play = Hit(ENEMY_CHARACTERS, 2), Summon(CONTROLLER, "AV_146")


class AV_207_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        deathrattles = [
            Deathrattle(card)
            for card in player.graveyard
            if card.type == CardType.MINION and card.has_deathrattle
        ]
        return source.game.queue_actions(source, deathrattles)


class AV_207:
    """Xyrella, the Devout"""

    play = AV_207_Play(CONTROLLER)


class AV_210_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spell_id = getattr(player, "_last_other_choose_one_spell", None)
        if spell_id:
            return source.game.queue_actions(source, [CastSpell(player.card(spell_id, source=source))])


class AV_210:
    """Pathmaker"""

    play = AV_210_Play(CONTROLLER)


class AV_219:
    """Ram Commander"""

    play = Give(CONTROLLER, "AV_219t") * 2


class AV_222:
    """Spammy Arcanist"""

    def play(self):
        yield Hit(ALL_MINIONS - SELF, 1)
        for _ in range(29):
            if Dead(ALL_MINIONS).check(self):
                yield Deaths()
                yield Hit(ALL_MINIONS - SELF, 1)
            else:
                break


class AV_223_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.deck if card.type == CardType.MINION]
        if minions and all(card.cost > source.cost for card in minions):
            return source.game.queue_actions(
                source, [Buff(card, "AV_223e") for card in minions]
            )


class AV_223:
    """Vanndar Stormpike"""

    play = AV_223_Play(CONTROLLER)


AV_223e = buff(cost=-3)


class AV_255:
    """Snowfall Guardian"""

    play = Freeze(ALL_MINIONS - SELF)


class AV_256:
    """Reflecto Engineer"""

    play = Buff((FRIENDLY_HAND | ENEMY_HAND) + MINION, "AV_256e")


AV_256e = AttackHealthSwapBuff()


class AV_257_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        frost_spells = [
            card
            for card in player.cards_played_this_game
            if card.type == CardType.SPELL
            and getattr(getattr(card, "data", None), "spell_school", None)
            == SpellSchool.FROST
        ]
        return source.game.queue_actions(
            source, [Summon(player, "AV_257t") for _ in frost_spells]
        )


class AV_257:
    """Bearon Gla'shear"""

    play = AV_257_Play(CONTROLLER)


class AV_257t:
    """Frozen Stagguard"""

    events = Damage(CHARACTER, None, SELF).on(Freeze(Damage.TARGET))


class AV_258_Play(MultipleChoice):
    choose_times = 2
    invocation_ids = ("AV_258t", "AV_258t2", "AV_258t3", "AV_258t4")

    def do_step1(self):
        chosen_ids = {card.id for card in self.choosed_cards}
        self.cards = CardList(
            self.player.card(card_id, source=self.source)
            for card_id in self.invocation_ids
            if card_id not in chosen_ids
        )

    def do_step2(self):
        self.do_step1()

    def done(self):
        actions = [
            CastSpell(card)
            for card in self.choosed_cards
        ]
        actions.append(GainArmor(self.source, 5))
        return self.source.game.queue_actions(self.source, actions)


class AV_258:
    """Bru'kan of the Elements"""

    play = AV_258_Play(CONTROLLER)


class AV_258t:
    """Earth Invocation"""

    play = Summon(CONTROLLER, "AV_258t6") * 2


class AV_258t2:
    """Water Invocation"""

    play = Heal(FRIENDLY_CHARACTERS, 6)


class AV_258t3:
    """Fire Invocation"""

    play = Hit(ENEMY_HERO, 6)


class AV_258t4:
    """Lightning Invocation"""

    play = Hit(ENEMY_MINIONS, 2)


class AV_258pt7_Activate(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        invocation_id = getattr(player, "_brukan_current_invocation", "AV_258t")
        next_index = (AV_258_Play.invocation_ids.index(invocation_id) + 1) % len(
            AV_258_Play.invocation_ids
        )
        player._brukan_current_invocation = AV_258_Play.invocation_ids[next_index]
        invocation = player.card(invocation_id, source=source)
        return source.game.queue_actions(source, [CastSpell(invocation)])


class AV_258pt7:
    """Command the Elements"""

    activate = AV_258pt7_Activate(CONTROLLER)


class AV_260:
    """Sleetbreaker"""

    play = Give(CONTROLLER, "AV_266")


class AV_262:
    """Warden of Chains"""

    play = Find(FRIENDLY_HAND + DEMON + (COST >= 5)) & Buff(SELF, "AV_262e2")


AV_262e2 = buff(+1, +2)


class AV_267_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        demons = [card for card in player.deck if card.type == CardType.MINION and Race.DEMON in card.races]
        if demons:
            demon = source.game.random.choice(demons)
            copy = player.card(demon.id, source=source)
            return source.game.queue_actions(
                source,
                [Morph(source, copy).then(Buff(Morph.CARD, "AV_267e"))],
            )


class AV_267:
    """Caria Felsoul"""

    play = AV_267_Play(CONTROLLER)


@custom_card
class AV_267e:
    tags = {
        GameTag.CARDNAME: "Felsoul",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    atk = SET(6)
    max_health = SET(6)


class AV_284_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = [card for card in player.deck if card.type == CardType.SPELL]
        actions = []
        for spell in spells[-2:]:
            actions.append(ForceDraw(spell))
        for spell, stat in zip(spells[-2:], (source.atk, source.health)):
            actions.append(Buff(spell, "AV_284e", cost=stat - spell.cost))
        if spells:
            actions.append(Buff(source, "AV_284e2", atk=spells[-2].cost - source.atk))
        if len(spells) > 1:
            actions.append(
                Buff(source, "AV_284e3", max_health=spells[-1].cost - source.health)
            )
        return source.game.queue_actions(source, actions)


class AV_284:
    """Balinda Stonehearth"""

    play = AV_284_Play(CONTROLLER)


AV_284e = buff()
AV_284e2 = buff()
AV_284e3 = buff()


FEL_SPELL = SPELL + FuncSelector(
    lambda entities, source: [
        entity
        for entity in entities
        if getattr(getattr(entity, "data", None), "spell_school", None)
        == SpellSchool.FEL
    ]
)


class AV_286:
    """Felwalker"""

    play = Find(FRIENDLY_HAND + FEL_SPELL) & CastSpell(HIGHEST_COST(FRIENDLY_HAND + FEL_SPELL))


class AV_294:
    """Clawfury Adept"""

    play = Buff(FRIENDLY_CHARACTERS - SELF, "AV_294e")


AV_294e = buff(atk=1)
AV_294e.events = REMOVED_IN_PLAY


class AV_296:
    """Pride Seeker"""

    play = Buff(CONTROLLER, "AV_296e")


class AV_296e:
    update = Refresh(FRIENDLY_HAND + CHOOSE_ONE, {GameTag.COST: -2})
    events = Play(CONTROLLER, CHOOSE_ONE).on(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))


class AV_308:
    """Grave Defiler"""

    play = Choice(CONTROLLER, FRIENDLY_HAND + FEL_SPELL).then(
        Give(CONTROLLER, Copy(Choice.CARD))
    )


class AV_312_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        player = source.controller
        cost = target.cost + 1
        candidates = [
            card
            for card in player.deck
            if card.type == CardType.MINION and card.cost == cost
        ]
        actions = [Destroy(target)]
        if candidates:
            actions.append(Summon(player, source.game.random.choice(candidates)))
        return source.game.queue_actions(source, actions)


class AV_312:
    """Sacrificial Summoner"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = AV_312_Play(TARGET)


class AV_313_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        honorable_targets = [
            (minion, minion.atk)
            for minion in player.opponent.field
            if minion.health == 1
        ]
        ret = source.game.queue_actions(source, [Hit(ENEMY_MINIONS, 1)])
        attack_gained = sum(atk for minion, atk in honorable_targets if minion.dead)
        if attack_gained:
            source.game.queue_actions(source, [Buff(source, "AV_313e", atk=attack_gained)])
        return ret


class AV_313:
    """Hollow Abomination"""

    play = AV_313_Play(CONTROLLER)


AV_313e = buff()


class CORE_GIL_653:
    """Woodcutter's Axe"""

    deathrattle = Buff(RANDOM_FRIENDLY_MINION, "CORE_GIL_653e")


@custom_card
class CORE_GIL_653e:
    tags = {
        GameTag.CARDNAME: "Woodcutter's Axe",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
        GameTag.ATK: 2,
        GameTag.HEALTH: 1,
    }


class AV_316:
    """Dreadlich Tamsin"""

    play = Hit(ALL_MINIONS, 3), Shuffle(CONTROLLER, "AV_316t4") * 3, Draw(CONTROLLER) * 3


class AV_316hp:
    """Chains of Dread"""

    activate = Shuffle(CONTROLLER, "AV_316t4"), Draw(CONTROLLER)


class AV_316t4:
    """Fel Rift"""

    draw = CAST_WHEN_DRAWN
    play = Summon(CONTROLLER, "AV_316t")


class CORE_GIL_667:
    """Rotten Applebaum"""

    deathrattle = Heal(FRIENDLY_HERO, 6)


class AV_323:
    """Scrapsmith"""

    play = Give(CONTROLLER, "AV_323t") * 2


class CORE_GVG_076:
    """Explosive Sheep"""

    deathrattle = Hit(ALL_MINIONS, 2)


class AV_335:
    """Ram Tamer"""

    play = Find(FRIENDLY_SECRETS) & (Buff(SELF, "AV_335e"), Stealth(SELF))


AV_335e = buff(+1, +1)


class CORE_ICC_019:
    """Skelemancer"""

    deathrattle = CurrentPlayer(OPPONENT) & Summon(CONTROLLER, "ICC_019t")


class AV_336_SummonBeast(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        beasts = [card for card in player.deck if card.type == CardType.MINION and Race.BEAST in card.races]
        if not beasts:
            return
        beast = source.game.random.choice(beasts)
        return source.game.queue_actions(
            source,
            [Summon(player, beast).then(GiveRush(Summon.CARD), Buff(Summon.CARD, "AV_336e"))],
        )


class AV_336:
    """Wing Commander Ichman"""

    play = AV_336_SummonBeast(CONTROLLER)


class AV_336e:
    events = Attack(OWNER, ALL_MINIONS).after(
        Dead(Attack.DEFENDER) & AV_336_SummonBeast(CONTROLLER)
    ), OWN_TURN_END.on(Destroy(SELF))


class CORE_ICC_021:
    """Exploding Bloatbat"""

    deathrattle = Hit(ENEMY_MINIONS, 2)


class AV_343_Draw(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = [card for card in player.deck if card.type == CardType.SPELL and card.cost <= 3]
        if not spells:
            return
        spell = source.game.random.choice(spells)
        return source.game.queue_actions(
            source, [ForceDraw(spell).then(Buff(ForceDraw.TARGET, "AV_343e"))]
        )


class AV_343:
    """Stonehearth Vindicator"""

    play = AV_343_Draw(CONTROLLER)


class AV_343e:
    cost = SET(0)
    events = REMOVED_IN_PLAY


class CORE_ICC_025:
    """Rattling Rascal"""

    play = Summon(CONTROLLER, "ICC_025t")
    deathrattle = Summon(OPPONENT, "ICC_025t")


class AV_403_Play(TargetedAction):
    TARGET = ActionArg()

    def _replacement_pool(self, source):
        cards.db.initialize()
        return [
            card_id
            for card_id, data in cards.db.items()
            if data.collectible
            and data.type == CardType.MINION
            and CardClass.ROGUE not in data.classes
            and CardClass.NEUTRAL not in data.classes
        ]

    def do(self, source, player):
        pool = self._replacement_pool(source)
        actions = []
        for minion in list(player.hand) + list(player.deck):
            if minion.type != CardType.MINION or not pool:
                continue
            replacement = player.card(source.game.random.choice(pool), source=source)
            actions.append(Morph(minion, replacement).then(Buff(Morph.CARD, "AV_403e2")))
        return source.game.queue_actions(source, actions)


class AV_403:
    """Cera'thine Fleetrunner"""

    play = AV_403_Play(CONTROLLER)


AV_403e2 = buff(cost=-2)


class CORE_ICC_027:
    """Bone Drake"""

    deathrattle = Give(CONTROLLER, RandomDragon())


class AV_711:
    """Double Agent"""

    powered_up = Find(FRIENDLY_HAND + OTHER_CLASS_CHARACTER)
    play = powered_up & Summon(CONTROLLER, ExactCopy(SELF))


class CORE_ICC_034:
    """Arrogant Crusader"""

    deathrattle = CurrentPlayer(OPPONENT) & Summon(CONTROLLER, "ICC_900t")


class BAR_030_Play(TargetedAction):
    TARGET = ActionArg()

    def _pool(self, source):
        cards.db.initialize()
        discover_classes = {source.controller.hero.card_class, CardClass.NEUTRAL}
        pool = []
        for card_id, data in cards.db.items():
            if not (
                data.collectible
                and (not source.game.is_standard or data.is_standard)
                and any(card_class in discover_classes for card_class in data.classes)
            ):
                continue
            card = source.controller.card(card_id, source=source)
            if (
                card.type == CardType.WEAPON
                or card.tags.get(GameTag.SECRET)
                or (card.type == CardType.MINION and Race.BEAST in card.races)
            ):
                pool.append(card_id)
        return pool

    def do(self, source, player):
        pool = self._pool(source)
        source.game.random.shuffle(pool)
        choices = [player.card(card_id, source=source) for card_id in pool[:3]]
        if choices:
            return source.game.queue_actions(source, [GenericChoice(player, choices)])


class BAR_030:
    """Pack Kodo"""

    play = BAR_030_Play(CONTROLLER)


class CORE_ICC_062:
    """Mountainfire Armor"""

    deathrattle = CurrentPlayer(OPPONENT) & GainArmor(FRIENDLY_HERO, 6)


class BAR_037_BuffCopies(TargetedAction):
    TARGET = ActionArg()
    CARD = ActionArg()

    def do(self, source, player, card):
        copies = [
            candidate
            for candidate in list(player.hand) + list(player.deck) + list(player.field)
            if candidate.id == card.id
        ]
        return source.game.queue_actions(
            source, [Buff(copy, "BAR_037e") for copy in copies]
        )


class BAR_037:
    """Warsong Wrangler"""

    play = Choice(CONTROLLER, DeDuplicate(FRIENDLY_DECK + BEAST)).then(
        Give(CONTROLLER, Choice.CARD), BAR_037_BuffCopies(CONTROLLER, Choice.CARD)
    )


BAR_037e = buff(+2, +1)


class CORE_ICC_064:
    """Blood Razor"""

    play = Hit(ALL_MINIONS, 1)
    deathrattle = Hit(ALL_MINIONS, 1)


class BAR_042_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = [card for card in player.deck if card.type == CardType.SPELL]
        if not spells:
            return
        spell = max(spells, key=lambda card: card.cost)
        return source.game.queue_actions(
            source,
            [
                ForceDraw(spell),
                Summon(player, RandomMinion(cost=spell.cost)),
            ],
        )


class BAR_042:
    """Primordial Protector"""

    play = BAR_042_Play(CONTROLLER)


class CORE_ICC_065:
    """Bone Baron"""

    deathrattle = Give(CONTROLLER, "ICC_026t") * 2


class BAR_045:
    """Arid Stormer"""

    play = ELEMENTAL_PLAYED_LAST_TURN & Buff(SELF, "BAR_045e")


BAR_045e = buff(rush=True, windfury=True)


class CORE_ICC_067:
    """Vryghoul"""

    deathrattle = CurrentPlayer(OPPONENT) & Summon(CONTROLLER, "ICC_900t")


class BAR_060:
    """Hog Rancher"""

    play = Summon(CONTROLLER, "BAR_060t")


class CORE_ICC_099:
    """Ticking Abomination"""

    deathrattle = Hit(FRIENDLY_MINIONS, 5)


class BAR_061:
    """Ratchet Privateer"""

    play = Buff(FRIENDLY_WEAPON, "BAR_061e")


BAR_061e = buff(atk=1)


class CORE_ICC_214:
    """Obsidian Statue"""

    deathrattle = Destroy(RANDOM_ENEMY_MINION)


class BAR_062:
    """Lushwater Murcenary"""

    play = Find(FRIENDLY_MINIONS + MURLOC) & Buff(SELF, "BAR_062e")


BAR_062e = buff(+1, +1)


class CORE_ICC_702:
    """Shallow Gravedigger"""

    deathrattle = Give(CONTROLLER, RandomMinion(deathrattle=True))


class BAR_064:
    """Talented Arcanist"""

    play = Buff(CONTROLLER, "BAR_064e")


class BAR_064e:
    update = Refresh(CONTROLLER, {GameTag.SPELLPOWER: 2})
    events = Play(CONTROLLER, SPELL).after(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))


class CORE_ICC_812:
    """Meat Wagon"""

    deathrattle = Summon(
        CONTROLLER, RANDOM(FRIENDLY_DECK + MINION + (ATK <= ATK(SELF)))
    )


class BAR_065:
    """Venomous Scorpid"""

    play = DISCOVER(RandomSpell())


class CORE_ICC_825:
    """Abominable Bowman"""

    deathrattle = Summon(CONTROLLER, Copy(FRIENDLY + KILLED + BEAST))


class BAR_069:
    """Injured Marauder"""

    play = Hit(SELF, 6)


class CORE_ICC_835:
    """Hadronox"""

    deathrattle = Summon(CONTROLLER, Copy(FRIENDLY + KILLED + TAUNT))


BAR_077_WATCH_POSTS = {"BAR_074", "BAR_075", "BAR_076"}


class BAR_077_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        watch_posts = []
        for collection in (
            player.field,
            player.graveyard,
            player.cards_played_this_game,
        ):
            for card in collection:
                if card.id in BAR_077_WATCH_POSTS and card not in watch_posts:
                    watch_posts.append(card)
        return source.game.queue_actions(
            source, [Summon(player, "BAR_077t") for _ in watch_posts]
        )


class BAR_077:
    """Kargal Battlescar"""

    play = BAR_077_Play(CONTROLLER)


class CORE_ICC_854:
    """Arfus"""

    entourage = LICH_KING_CARDS
    deathrattle = Give(CONTROLLER, RandomEntourage())


BAR_079_GOLEMS = ["BAR_079_m1", "BAR_079_m2", "BAR_079_m3"]
BAR_079_BASE_HERBS = [
    "BAR_079t4",
    "BAR_079t5",
    "BAR_079t6",
    "BAR_079t7",
    "BAR_079t8",
    "BAR_079t9",
]
BAR_079_BATTLECRY_HERBS = {
    1: [
        "BAR_079t10",
        "BAR_079t11",
        "BAR_079t12",
        "BAR_079t13",
        "BAR_079t14",
        "BAR_079t15",
    ],
    5: [
        "BAR_079t10b",
        "BAR_079t11",
        "BAR_079t12b",
        "BAR_079t13b",
        "BAR_079t14b",
        "BAR_079t15b",
    ],
    10: [
        "BAR_079t10",
        "BAR_079t11",
        "BAR_079t12c",
        "BAR_079t13c",
        "BAR_079t14c",
        "BAR_079t15c",
    ],
}


class BAR_079_KazakusAction(MultipleChoice):
    PLAYER = ActionArg()
    choose_times = 3

    def do_step1(self):
        self.cards = [self.player.card(card_id, source=self.source) for card_id in BAR_079_GOLEMS]

    def do_step2(self):
        self.golem_id = self.choosed_cards[0].id
        self.golem_cost = self.choosed_cards[0].cost
        herb_ids = BAR_079_BASE_HERBS + BAR_079_BATTLECRY_HERBS[self.golem_cost]
        self.cards = [self.player.card(card_id, source=self.source) for card_id in herb_ids]

    def do_step3(self):
        chosen = {card.id for card in self.choosed_cards}
        herb_ids = BAR_079_BASE_HERBS + BAR_079_BATTLECRY_HERBS[self.golem_cost]
        self.cards = [
            self.player.card(card_id, source=self.source)
            for card_id in herb_ids
            if card_id not in chosen
        ]

    def done(self):
        herbs = self.choosed_cards[1:]
        golem = self.player.card(self.golem_id, source=self.source)
        golem.custom_card = True

        def create_custom_card(card):
            play_actions = []
            for herb in herbs:
                herb_id = herb.id
                if herb_id in ("BAR_079t4",):
                    card.tags[GameTag.RUSH] = True
                elif herb_id in ("BAR_079t5",):
                    card.tags[GameTag.TAUNT] = True
                elif herb_id in ("BAR_079t6",):
                    card.tags[GameTag.DIVINE_SHIELD] = True
                elif herb_id in ("BAR_079t7",):
                    card.tags[GameTag.LIFESTEAL] = True
                elif herb_id in ("BAR_079t8",):
                    card.tags[GameTag.STEALTH] = True
                elif herb_id in ("BAR_079t9",):
                    card.tags[GameTag.POISONOUS] = True
                elif herb_id in ("BAR_079t10",):
                    play_actions.append(Buff(FRIENDLY_MINIONS - SELF, "BAR_079t10e"))
                elif herb_id in ("BAR_079t10b",):
                    play_actions.append(Buff(FRIENDLY_MINIONS - SELF, "BAR_079t10be"))
                elif herb_id in ("BAR_079t11",):
                    play_actions.append(Summon(CONTROLLER, ExactCopy(SELF)))
                elif herb_id in ("BAR_079t12",):
                    play_actions.append(Freeze(RANDOM_ENEMY_MINION))
                elif herb_id in ("BAR_079t12b",):
                    play_actions.append(Freeze(RANDOM_ENEMY_MINION * 2))
                elif herb_id in ("BAR_079t12c",):
                    play_actions.append(Freeze(ENEMY_MINIONS))
                elif herb_id in ("BAR_079t13",):
                    play_actions.append(Hit(RANDOM_ENEMY_MINION, 3))
                elif herb_id in ("BAR_079t13b",):
                    play_actions.append(Hit(RANDOM_ENEMY_MINION * 2, 3))
                elif herb_id in ("BAR_079t13c",):
                    play_actions.append(Hit(ENEMY_MINIONS, 3))
                elif herb_id in ("BAR_079t14",):
                    card.tags[GameTag.SPELLPOWER] = 1
                elif herb_id in ("BAR_079t14b",):
                    card.tags[GameTag.SPELLPOWER] = 2
                elif herb_id in ("BAR_079t14c",):
                    card.tags[GameTag.SPELLPOWER] = 4
                elif herb_id in ("BAR_079t15",):
                    play_actions.append(Draw(CONTROLLER))
                elif herb_id in ("BAR_079t15b",):
                    play_actions.append(Draw(CONTROLLER) * 2)
                elif herb_id in ("BAR_079t15c",):
                    play_actions.append(Draw(CONTROLLER) * 4)
            card.data.scripts.play = tuple(play_actions)
            card.tags[GameTag.CARDTEXT_ENTITY_0] = herbs[0].description
            card.tags[GameTag.CARDTEXT_ENTITY_1] = herbs[1].description

        golem.create_custom_card = create_custom_card
        golem.create_custom_card(golem)
        self.player.give(golem)


class BAR_079:
    """Kazakus, Golem Shaper"""

    powered_up = -Find(FRIENDLY_DECK + (COST == 4))
    play = powered_up & BAR_079_KazakusAction(CONTROLLER)


class CORE_LOE_012:
    """Tomb Pillager"""

    deathrattle = Give(CONTROLLER, THE_COIN)


class BAR_080_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        owner = target.controller
        hand_minions = [card for card in owner.hand if card.type == CardType.MINION]
        if not hand_minions:
            return
        replacement = source.game.random.choice(hand_minions)
        target_index = target.zone_position
        target.zone = Zone.HAND
        replacement._summon_index = target_index
        replacement.zone = Zone.PLAY
        replacement._summon_index = None
        source.game.manager.targeted_action(self, source, target, replacement)
        return replacement


class BAR_080:
    """Shadow Hunter Vol'jin"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = BAR_080_Play(TARGET)


class CORE_LOE_050:
    """Mounted Raptor"""

    deathrattle = Summon(CONTROLLER, RandomMinion(cost=1))


class BAR_081_Choice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
        )
        self.player.choice = None
        copy = self.player.card(card.id, source=self.source)
        self.source.game.queue_actions(
            self.source, [Give(self.player, copy), Draw(card.controller, card)]
        )
        self.trigger_choice_callback()


class BAR_081_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = list(player.opponent.deck)
        if len(cards) > 3:
            cards = source.game.random.sample(cards, 3)
        if cards:
            return source.game.queue_actions(source, [BAR_081_Choice(player, cards)])


class BAR_081:
    """Southsea Scoundrel"""

    play = BAR_081_Play(CONTROLLER)


class CORE_LOOT_413:
    """Plated Beetle"""

    deathrattle = GainArmor(FRIENDLY_HERO, 3)


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


class BAR_329:
    """Death Speaker Blackthorn"""

    play = Summon(CONTROLLER, RANDOM(FRIENDLY_DECK + MINION + DEATHRATTLE + (COST <= 5)) * 3)


class BAR_307:
    """Void Flayer"""

    play = Hit(RANDOM_ENEMY_MINION, 1) * Count(FRIENDLY_HAND + SPELL)


class BAR_330:
    """Tuskpiercer"""

    deathrattle = ForceDraw(RANDOM(FRIENDLY_DECK + MINION + DEATHRATTLE))


class BAR_333_AttackEdges(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        enemy_minions = player.opponent.field
        if not enemy_minions:
            return
        left = enemy_minions[0]
        right = enemy_minions[-1]
        actions = [Attack(source, left)]
        if left is not right:
            actions.append(Attack(source, right))
        return source.game.queue_actions(source, actions)


class BAR_333:
    """Kurtrus Ashfallen"""

    play = BAR_333_AttackEdges(CONTROLLER)
    outcast = Buff(SELF, "BAR_333e"), BAR_333_AttackEdges(CONTROLLER)


class BAR_333e:
    tags = {
        GameTag.CANT_BE_DAMAGED: True,
        GameTag.TAG_ONE_TURN_EFFECT: True,
    }


class BAR_535:
    """Thickhide Kodo"""

    deathrattle = GainArmor(FRIENDLY_HERO, 5)


class CORE_BAR_535:
    """Thickhide Kodo"""

    deathrattle = GainArmor(FRIENDLY_HERO, 5)


class CORE_BAR_551:
    """Barak Kodobane"""

    play = (
        ForceDraw(RANDOM(FRIENDLY_DECK + SPELL + (COST == 1))),
        ForceDraw(RANDOM(FRIENDLY_DECK + SPELL + (COST == 2))),
        ForceDraw(RANDOM(FRIENDLY_DECK + SPELL + (COST == 3))),
    )


class CORE_AT_047:
    """Draenei Totemcarver"""

    play = Buff(SELF, "AT_047e") * Count(FRIENDLY_MINIONS + TOTEM)


class CORE_AT_132:
    """Justicar Trueheart"""

    play = UPGRADE_HERO_POWER


class CORE_BOT_312:
    """Replicating Menace"""

    magnetic = MAGNETIC("BOT_312e")
    deathrattle = Summon(CONTROLLER, "BOT_312t") * 3


class CORE_BOT_083:
    """Toxicologist"""

    play = Buff(FRIENDLY_WEAPON, "BOT_083e")


class CORE_BOT_104:
    """Dyn-o-matic"""

    play = Hit(RANDOM(ALL_MINIONS - MECH), 1) * 5


class CORE_BOT_533:
    """Menacing Nimbus"""

    play = Give(CONTROLLER, RandomElemental())


class CORE_BT_304:
    """Enhanced Dreadlord"""

    deathrattle = Summon(CONTROLLER, "BT_304t")


class CORE_BT_323:
    """Sightless Watcher"""

    play = Choice(CONTROLLER, RANDOM(DeDuplicate(FRIENDLY_DECK)) * 3).then(
        PutOnTop(CONTROLLER, Choice.CARD)
    )


class CORE_BT_334:
    """Lady Liadrin"""

    play = Give(
        CONTROLLER, Copy(SHUFFLE(CARDS_PLAYED_THIS_GAME + CAST_ON_FRIENDLY_CHARACTERS))
    )


class CORE_BT_416:
    """Raging Felscreamer"""

    play = Buff(CONTROLLER, "BT_416e")


class CORE_BT_922:
    """Umberwing"""

    play = Summon(CONTROLLER, "BT_922t") * 2


class CORE_CATA_001:
    """Tichondrius"""

    update = Refresh(FRIENDLY_HERO, {GameTag.IMMUNE: True})
    play = Buff(CONTROLLER, "CORE_CATA_001e")


class CORE_CATA_001e:
    update = Refresh(FRIENDLY_HAND + DEMON, {GameTag.COST: SET(0)})
    events = Play(CONTROLLER, DEMON).on(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))


class CORE_CATA_002:
    """Calia Menethil"""

    play = Summon(CONTROLLER, Copy(HIGHEST_COST(FRIENDLY + KILLED + MINION)))


class CORE_CATA_006_SummonCost(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cost = getattr(getattr(source, "owner", None), "cost", 0)
        return source.game.queue_actions(source, [Summon(player, RandomMinion(cost=cost))])


class CORE_CATA_006:
    """Ulfar"""

    play = Buff(FRIENDLY_MINIONS - SELF, "CORE_CATA_006e")


class CORE_CATA_006e:
    tags = {GameTag.DEATHRATTLE: True}
    deathrattle = CORE_CATA_006_SummonCost(CONTROLLER)


class CORE_CFM_120:
    """Mistress of Mixtures"""

    deathrattle = Heal(ALL_HEROES, 4)


class CORE_CFM_753:
    """Grimestreet Outfitter"""

    play = Buff(FRIENDLY_HAND + MINION, "CFM_753e")


class CORE_CFM_790:
    """Dirty Rat"""

    play = Summon(OPPONENT, RANDOM(ENEMY_HAND + MINION))


class CORE_CS2_042:
    """Fire Elemental"""

    requirements = {PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Hit(TARGET, 4)


class CORE_CS2_064:
    """Dread Infernal"""

    play = Hit(ALL_CHARACTERS - SELF, 1)


class CORE_CS2_088:
    """Guardian of Kings"""

    play = Heal(FRIENDLY_HERO, 6)


class CORE_CS2_117:
    """Earthen Ring Farseer"""

    requirements = {PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Heal(TARGET, 3)


class CORE_CS2_181:
    """Injured Blademaster"""

    play = Hit(SELF, 4)


class CORE_CS2_188:
    """Abusive Sergeant"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Buff(TARGET, "CS2_188o")


class CORE_CS2_189:
    """Elven Archer"""

    requirements = {PlayReq.REQ_NONSELF_TARGET: 0, PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Hit(TARGET, 1)


class CORE_CS2_203:
    """Ironbeak Owl"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Silence(TARGET)


class CORE_CS3_008:
    """Bloodsail Deckhand"""

    play = Buff(CONTROLLER, "CORE_CS3_008e")


@custom_card
class CORE_CS3_008e:
    tags = {
        GameTag.CARDNAME: "Bloodsail Deckhand",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    update = Refresh(FRIENDLY_HAND + WEAPON, {GameTag.COST: -1})
    events = Play(CONTROLLER, WEAPON).after(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))


class CORE_CS3_012:
    """Nordrassil Druid"""

    play = Buff(CONTROLLER, "CORE_CS3_012e")


@custom_card
class CORE_CS3_012e:
    tags = {
        GameTag.CARDNAME: "Nordrassil Druid",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    update = Refresh(FRIENDLY_HAND + SPELL, {GameTag.COST: -3})
    events = Play(CONTROLLER, SPELL).after(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))


class CORE_DAL_086:
    """Sunreaver Spy"""

    powered_up = Find(FRIENDLY_SECRETS)
    play = powered_up & Buff(SELF, "DAL_086e")


class CORE_DAL_416:
    """Hench-Clan Burglar"""

    play = GenericChoice(CONTROLLER, RandomSpell(card_class=ANOTHER_CLASS) * 3)


class CORE_DAL_422_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = list(player.hand) + list(player.deck)
        return source.game.queue_actions(
            source, [Morph(card, RandomLegendaryMinion()) for card in cards]
        )


class CORE_DAL_422:
    """Arch-Villain Rafaam"""

    play = CORE_DAL_422_Play(CONTROLLER)


class CORE_DAL_609:
    """Kalecgos"""

    update = (Count(CARDS_PLAYED_THIS_TURN + SPELL) == 0) & Refresh(
        FRIENDLY_HAND + SPELL, buff="DAL_609e"
    )
    play = DISCOVER(RandomSpell())


class CORE_DAL_729:
    """Madame Lazul"""

    play = GenericChoice(CONTROLLER, Copy(RANDOM(DeDuplicate(ENEMY_HAND)) * 3))


class CORE_DMF_231_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, zai):
        player = zai.controller
        if not player.hand:
            return
        edges = [player.hand[0]]
        if player.hand[-1] is not player.hand[0]:
            edges.append(player.hand[-1])
        copies = [player.card(card.id, source=source) for card in edges]
        return source.game.queue_actions(source, [Give(player, card) for card in copies])


class CORE_DMF_231:
    """Zai, the Incredible"""

    play = CORE_DMF_231_Play(SELF)


class DMF_231(CORE_DMF_231):
    """Zai, the Incredible"""


class CORE_DMF_238:
    """Hammer of the Naaru"""

    play = Summon(CONTROLLER, "DMF_238t")


class DMF_238(CORE_DMF_238):
    """Hammer of the Naaru"""


class CORE_DMF_240:
    """Lothraxion the Redeemed"""

    play = Buff(CONTROLLER, "CORE_DMF_240e")


class DMF_240(CORE_DMF_240):
    """Lothraxion the Redeemed"""


@custom_card
class CORE_DMF_240e:
    tags = {
        GameTag.CARDNAME: "Lothraxion the Redeemed",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    events = Summon(CONTROLLER, ID("CS2_101t")).after(GiveDivineShield(Summon.CARD))


class CORE_DMF_521:
    """Sword Eater"""

    play = Summon(CONTROLLER, "DMF_521t")


class DMF_521(CORE_DMF_521):
    """Sword Eater"""


class CORE_DMF_733:
    """Kiri, Chosen of Elune"""

    play = Give(CONTROLLER, "DMF_058"), Give(CONTROLLER, "DMF_057")


class DMF_733(CORE_DMF_733):
    """Kiri, Chosen of Elune"""


class CORE_DRG_026:
    """Deathwing, Mad Aspect"""

    def play(self):
        entities = (ALL_MINIONS - SELF - DEAD).eval(self.game.live_entities, self)
        self.game.random.shuffle(entities)
        for entity in entities:
            if not self.dead and not entity.dead:
                yield Attack(self, entity)
                yield Deaths()


class CORE_DRG_037:
    """Flik Skyshiv"""

    requirements = {PlayReq.REQ_TARGET_IF_AVAILABLE: 0, PlayReq.REQ_MINION_TARGET: 0}
    play = Destroy(
        FilterSelector(
            lambda entity, source: getattr(entity, "id", None) == source.target.id
        )
    )


class CORE_DRG_090:
    """Murozond the Infinite"""

    play = Replay(Copy(CARDS_OPPONENT_PLAYED_LAST_TURN))


class CORE_DRG_226:
    """Amber Watcher"""

    requirements = {PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Heal(TARGET, 8)


class CORE_DRG_229:
    """Bronze Explorer"""

    play = DISCOVER(RandomDragon())


class CORE_EX1_002:
    """The Black Knight"""

    requirements = {
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_MUST_TARGET_TAUNTER: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Destroy(TARGET)


class CORE_EX1_005:
    """Big Game Hunter"""

    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_TARGET_MIN_ATTACK: 7,
    }
    play = Destroy(TARGET)


class CORE_EX1_011:
    """Voodoo Doctor"""

    requirements = {PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Heal(TARGET, 2)


class CORE_EX1_014:
    """King Mukla"""

    play = Give(OPPONENT, "EX1_014t") * 2


class CORE_EX1_043:
    """Twilight Drake"""

    play = Buff(SELF, "EX1_043e") * Count(FRIENDLY_HAND)


class CORE_EX1_046:
    """Dark Iron Dwarf"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Buff(TARGET, "EX1_046e")


class CORE_EX1_049:
    """Youthful Brewmaster"""

    requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_NONSELF_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Bounce(TARGET)


class CORE_EX1_050:
    """Coldlight Oracle"""

    play = Draw(ALL_PLAYERS) * 2


class CORE_EX1_059:
    """Crazed Alchemist"""

    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_IF_AVAILABLE: 0}
    play = Buff(TARGET, "EX1_059e")


class CORE_EX1_066:
    """Acidic Swamp Ooze"""

    play = Destroy(ENEMY_WEAPON)


class CORE_EX1_082:
    """Mad Bomber"""

    play = Hit(RANDOM_OTHER_CHARACTER, 1) * 3


class CORE_EX1_085:
    """Mind Control Tech"""

    play = (Count(ENEMY_MINIONS) >= 4) & Steal(RANDOM_ENEMY_MINION)


class CORE_EX1_093:
    """Defender of Argus"""

    play = Buff(SELF_ADJACENT, "EX1_093e")


class CORE_EX1_103:
    """Coldlight Seer"""

    play = Buff(FRIENDLY_MINIONS + MURLOC - SELF, "EX1_103e")


class CORE_EX1_116:
    """Leeroy Jenkins"""

    play = Summon(OPPONENT, "EX1_116t") * 2


class CORE_EX1_186:
    """SI:7 Infiltrator"""

    play = Destroy(RANDOM(ENEMY_SECRETS))


class CORE_EX1_188:
    """Barrens Stablehand"""

    play = Summon(CONTROLLER, RandomBeast())


class CORE_EX1_189:
    """Brightwing"""

    play = Give(CONTROLLER, RandomLegendaryMinion())


class CORE_EX1_190:
    """High Inquisitor Whitemane"""

    play = Summon(CONTROLLER, Copy(FRIENDLY + MINION + KILLED_THIS_TURN))


class CORE_EX1_193:
    """Psychic Conjurer"""

    play = Give(CONTROLLER, Copy(RANDOM(ENEMY_DECK)))


class CORE_EX1_195:
    """Kul Tiran Chaplain"""

    requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Buff(TARGET, "EX1_195e")


class CORE_EX1_198:
    """Natalie Seline"""

    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = (Buff(SELF, "EX1_198e", max_health=CURRENT_HEALTH(TARGET)), Destroy(TARGET))


class CORE_EX1_284:
    """Azure Drake"""

    play = Draw(CONTROLLER)


class CORE_EX1_304:
    """Void Terror"""

    play = (
        Buff(
            SELF,
            "EX1_304e",
            atk=ATK(SELF_ADJACENT),
            max_health=CURRENT_HEALTH(SELF_ADJACENT),
        ),
        Destroy(SELF_ADJACENT),
    )


class CORE_EX1_310:
    """Doomguard"""

    play = Discard(RANDOM(FRIENDLY_HAND) * 2)


class CORE_EX1_319:
    """Flame Imp"""

    play = Hit(FRIENDLY_HERO, 3)


class CORE_EX1_362:
    """Argent Protector"""

    requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_NONSELF_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = GiveDivineShield(TARGET)


class CORE_EX1_382:
    """Aldor Peacekeeper"""

    requirements = {
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Buff(TARGET, "EX1_382e")


class CORE_EX1_506:
    """Murloc Tidehunter"""

    play = Summon(CONTROLLER, "CORE_EX1_506a")


class CORE_EX1_564:
    """Faceless Manipulator"""

    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_NONSELF_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Morph(SELF, ExactCopy(TARGET))


class CORE_EX1_603:
    """Cruel Taskmaster"""

    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_NONSELF_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Buff(TARGET, "EX1_603e"), Hit(TARGET, 1)


class CORE_EX1_623:
    """Temple Enforcer"""

    requirements = {
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
    }
    play = Buff(TARGET, "EX1_623e")


HARTH_STONEBREW_HANDS = (
    ("CS2_029", "EX1_279", "EX1_571", "CS2_042", "EX1_559"),
    ("CS2_008", "CS2_013", "EX1_169", "EX1_284", "EX1_572"),
    ("CS2_231", "EX1_506", "EX1_595", "EX1_564", "EX1_298"),
)


class CORE_GIFT_01_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if getattr(player, "_harth_stonebrew_used", False):
            return
        player._harth_stonebrew_used = True
        for card in list(player.hand):
            card.zone = Zone.REMOVEDFROMGAME
            source.game.manager.targeted_action(self, source, card)
        hand = source.game.random.choice(HARTH_STONEBREW_HANDS)
        return source.game.queue_actions(source, [Give(player, card_id) for card_id in hand])


class CORE_GIFT_01:
    """Harth Stonebrew"""

    play = CORE_GIFT_01_Play(CONTROLLER)


class CORE_GIL_124:
    """Mossy Horror"""

    play = Destroy(ALL_MINIONS - SELF + (ATK <= 2))


class CORE_GIL_580:
    """Town Crier"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + RUSH))


class CORE_GIL_598:
    """Tess Greymane"""

    play = Replay(Copy(SHUFFLE(CARDS_PLAYED_THIS_GAME + OTHER_CLASS_CHARACTER)))


class CORE_GIL_622:
    """Lifedrinker"""

    play = Hit(ENEMY_HERO, 3), Heal(FRIENDLY_HERO, 3)


class CORE_GVG_053:
    """Shieldmaiden"""

    play = GainArmor(FRIENDLY_HERO, 5)


class CORE_GVG_110:
    """Dr. Boom"""

    play = SummonBothSides(CONTROLLER, "GVG_110t") * 2


class CORE_ICC_018:
    """Phantom Freebooter"""

    play = Find(FRIENDLY_WEAPON) & Buff(
        SELF,
        "ICC_018e",
        atk=ATK(FRIENDLY_WEAPON),
        max_health=CURRENT_DURABILITY(FRIENDLY_WEAPON),
    )


class CORE_ICC_026:
    """Grim Necromancer"""

    play = SummonBothSides(CONTROLLER, "ICC_026t") * 2


class CORE_ICC_028:
    """Sunborne Val'kyr"""

    play = Buff(SELF_ADJACENT, "ICC_028e")


class CORE_ICC_058:
    """Brrrloc"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    play = Freeze(TARGET)


class CORE_ICC_069:
    """Ghastly Conjurer"""

    play = Give(CONTROLLER, "CS2_027")


class CORE_ICC_092:
    """Acherus Veteran"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "ICC_092e")


class CORE_ICC_093:
    """Tuskarr Fisherman"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "ICC_093e")


class CORE_ICC_094:
    """Fallen Sun Cleric"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "ICC_094e")


class CORE_ICC_096:
    """Furnacefire Colossus"""

    play = Discard(IN_HAND + WEAPON).then(
        Buff(
            SELF,
            "ICC_096e",
            atk=ATK(Discard.TARGET),
            max_health=CURRENT_DURABILITY(Discard.TARGET),
        )
    )


class CORE_ICC_098:
    """Tomb Lurker"""

    play = Give(CONTROLLER, Copy(RANDOM(KILLED + MINION + DEATHRATTLE)))


class CORE_ICC_215:
    """Archbishop Benedictus"""

    play = Shuffle(CONTROLLER, ExactCopy(ENEMY_DECK))


class CORE_ICC_252:
    """Coldwraith"""

    requirements = {
        PlayReq.REQ_FROZEN_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Find(ENEMY + FROZEN) & Draw(CONTROLLER)


class CORE_ICC_257:
    """Corpse Raiser"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "ICC_257e")


class CORE_ICC_407:
    """Gnomeferatu"""

    play = Mill(OPPONENT)


class CORE_ICC_415:
    """Stitched Tracker"""

    play = GenericChoice(
        CONTROLLER, Copy(RANDOM(DeDuplicate(FRIENDLY_DECK + MINION)) * 3)
    )


class CORE_ICC_450:
    """Death Revenant"""

    play = Buff(SELF, "ICC_450e") * Count(ALL_MINIONS + DAMAGED)


class CORE_ICC_466:
    """Saronite Chain Gang"""

    play = Summon(CONTROLLER, ExactCopy(SELF))


class CORE_ICC_467:
    """Deathspeaker"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "ICC_467e")


class CORE_ICC_481:
    """Thrall, Deathseer"""

    play = Evolve(FRIENDLY_MINIONS, 2)


class CORE_ICC_701_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        targets = []
        for deck_player in source.game.players:
            targets.extend(
                card
                for card in list(deck_player.hand) + list(deck_player.deck)
                if card.type == CardType.SPELL and card.cost == 1
            )
        return source.game.queue_actions(source, [Destroy(card) for card in targets])


class CORE_ICC_701:
    """Skulking Geist"""

    play = CORE_ICC_701_Play(CONTROLLER)


class CORE_ICC_705:
    """Bonemare"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = Buff(TARGET, "ICC_705e")


class CORE_ICC_801:
    """Howling Commander"""

    play = ForceDraw(RANDOM(FRIENDLY_DECK + MINION + DIVINE_SHIELD))


class CORE_ICC_807:
    """Strongshell Scavenger"""

    play = Buff(FRIENDLY_MINIONS + TAUNT, "ICC_807e")


class CORE_ICC_810:
    """Deathaxe Punisher"""

    play = Buff(RANDOM(FRIENDLY_HAND + LIFESTEAL + MINION), "ICC_810e")


class CORE_ICC_811_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        enemy_class = player.opponent.hero.card_class
        if enemy_class == CardClass.NEUTRAL:
            return
        spells = list(player.hand.filter(type=CardType.SPELL))
        return source.game.queue_actions(
            source,
            [
                Morph(spell, RandomSpell(card_class=enemy_class))
                for spell in spells
            ],
        )


class CORE_ICC_811:
    """Lilian Voss"""

    play = CORE_ICC_811_Play(CONTROLLER)


class CORE_ICC_827:
    """Valeera the Hollow"""

    play = (
        Stealth(FRIENDLY_HERO),
        Buff(FRIENDLY_HERO, "ICC_827e3"),
        Give(CONTROLLER, "ICC_827t"),
    )


class ICC_827e3:
    events = OWN_TURN_BEGIN.on(Unstealth(OWNER), Destroy(SELF))


class ICC_827p:
    tags = {enums.PASSIVE_HERO_POWER: True}
    events = OWN_TURN_BEGIN.on(Give(CONTROLLER, "ICC_827t"))


class ICC_827t:
    requirements = {
        PlayReq.REQ_MUST_PLAY_OTHER_CARD_FIRST: 0,
    }

    class Hand:
        events = (
            Play(CONTROLLER).on(
                Morph(SELF, ExactCopy(Play.CARD)).then(Buff(Morph.CARD, "ICC_827e"))
            ),
            OWN_TURN_END.on(Destroy(SELF)),
        )
        update = Find(FRIENDLY_HERO_POWER - EXHAUSTED + ID("ICC_827p")) | Destroy(SELF)


class ICC_827e:
    class Hand:
        events = (
            Play(CONTROLLER).on(
                Morph(OWNER, ExactCopy(Play.CARD)).then(Buff(Morph.CARD, "ICC_827e"))
            ),
            OWN_TURN_END.on(Destroy(SELF)),
        )
        update = Find(FRIENDLY_HERO_POWER - EXHAUSTED + ID("ICC_827p")) | Destroy(SELF)

    events = REMOVED_IN_PLAY


class CORE_ICC_828:
    """Deathstalker Rexxar"""

    play = Hit(ENEMY_MINIONS, 2)


class CORE_ICC_829:
    """Uther of the Ebon Blade"""

    play = Summon(CONTROLLER, "ICC_829t")


class ICC_829p:
    requirements = {
        PlayReq.REQ_NUM_MINION_SLOTS: 1,
    }
    entourage = ["ICC_829t2", "ICC_829t3", "ICC_829t4", "ICC_829t5"]
    activate = Summon(CONTROLLER, RandomEntourage(exclude=FRIENDLY_MINIONS))
    update = FindAll(
        FRIENDLY_MINIONS + ID("ICC_829t2"),
        FRIENDLY_MINIONS + ID("ICC_829t3"),
        FRIENDLY_MINIONS + ID("ICC_829t4"),
        FRIENDLY_MINIONS + ID("ICC_829t5"),
    ) & Destroy(ENEMY_HERO)


class CORE_ICC_830:
    """Shadowreaper Anduin"""

    play = Destroy(ALL_MINIONS + (ATK >= 5))


class ICC_830p:
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    activate = Hit(TARGET, 2)
    events = Play(CONTROLLER).after(RefreshHeroPower(SELF))


class CORE_ICC_831:
    """Bloodreaver Gul'dan"""

    play = Summon(CONTROLLER, Copy(FRIENDLY + KILLED + DEMON))


class ICC_831p:
    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    activate = Hit(TARGET, 3)


class CORE_ICC_833:
    """Frost Lich Jaina"""

    play = Summon(CONTROLLER, "ICC_833t"), Buff(CONTROLLER, "ICC_833e")


class CORE_ICC_834:
    """Scourgelord Garrosh"""

    play = Summon(CONTROLLER, "ICC_834w")


class CORE_ICC_838:
    """Sindragosa"""

    play = SummonBothSides(CONTROLLER, "ICC_838t") * 2


class CORE_ICC_850:
    """Shadowblade"""

    play = Buff(FRIENDLY_HERO, "ICC_850e")


class ICC_850e:
    tags = {
        GameTag.CANT_BE_DAMAGED: True,
        GameTag.CANT_BE_TARGETED_BY_OPPONENTS: True,
    }
    events = OWN_TURN_END.on(Destroy(SELF))


class CORE_ICC_851:
    """Prince Keleseth"""

    play = Find(FRIENDLY_DECK + (COST == 2)) | Buff(FRIENDLY_DECK + MINION, "ICC_851e")


class CORE_ICC_852:
    """Prince Taldaram"""

    requirements = {
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_TARGET_IF_AVAILABLE_AND_NO_3_COST_CARD_IN_DECK: 0,
    }
    play = Morph(SELF, ExactCopy(TARGET)).then(Buff(Morph.CARD, "ICC_852e"))


class CORE_DMF_511:
    """Foxy Fraud"""

    play = Buff(CONTROLLER, "CORE_DMF_511e")


class DMF_511(CORE_DMF_511):
    """Foxy Fraud"""


@custom_card
class CORE_DMF_511e:
    tags = {
        GameTag.CARDNAME: "Foxy Fraud",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }

    update = Refresh(FRIENDLY_HAND + COMBO, {GameTag.COST: -2})
    events = Play(CONTROLLER, COMBO).after(Destroy(SELF)), OWN_TURN_END.on(Destroy(SELF))


class CORE_CFM_605:
    """Drakonid Operative"""

    powered_up = HOLDING_DRAGON
    play = powered_up & GenericChoice(
        CONTROLLER, Copy(RANDOM(DeDuplicate(ENEMY_DECK)) * 3)
    )


class CORE_CFM_751:
    """Abyssal Enforcer"""

    play = Hit(ALL_CHARACTERS - SELF, 3)


class CORE_CS3_003_Jail(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.opponent.hand if card.type == CardType.MINION]
        if minions:
            card = source.game.random.choice(minions)
            source._felsoul_jailed_card = card
            return source.game.queue_actions(source, [Discard(card)])


class CORE_CS3_003_Return(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        card = getattr(source, "_felsoul_jailed_card", None)
        if (
            card
            and card.zone == Zone.REMOVEDFROMGAME
            and len(card.controller.hand) < card.controller.max_hand_size
        ):
            card.zone = Zone.HAND
            source.game.manager.targeted_action(self, source, card)


class CORE_CS3_003:
    """Felsoul Jailer"""

    play = CORE_CS3_003_Jail(CONTROLLER)
    deathrattle = CORE_CS3_003_Return(CONTROLLER)


class CS3_003(CORE_CS3_003):
    """Felsoul Jailer"""


class CORE_DMF_067:
    """Prize Vendor"""

    play = Draw(CONTROLLER), Draw(OPPONENT)
    deathrattle = Draw(CONTROLLER), Draw(OPPONENT)


class DMF_067(CORE_DMF_067):
    """Prize Vendor"""


class CORE_DMF_194:
    """Redscale Dragontamer"""

    deathrattle = ForceDraw(RANDOM(FRIENDLY_DECK + DRAGON))


class DMF_194(CORE_DMF_194):
    """Redscale Dragontamer"""


class CORE_DMF_734:
    """Greybough"""

    deathrattle = Buff(RANDOM(FRIENDLY_MINIONS - SELF), "DMF_734e")


class DMF_734(CORE_DMF_734):
    """Greybough"""


class DMF_734e:
    tags = {GameTag.DEATHRATTLE: True}
    deathrattle = Summon(CONTROLLER, "DMF_734")


class CORE_EX1_012:
    """Bloodmage Thalnos"""

    deathrattle = Draw(CONTROLLER)


class CORE_EX1_016:
    """Sylvanas Windrunner"""

    deathrattle = Steal(RANDOM_ENEMY_MINION)


class CORE_EX1_096:
    """Loot Hoarder"""

    deathrattle = Draw(CONTROLLER)


class CORE_EX1_110:
    """Cairne Bloodhoof"""

    deathrattle = Summon(CONTROLLER, "EX1_110t")


class CORE_EX1_383:
    """Tirion Fordring"""

    deathrattle = Summon(CONTROLLER, "EX1_383t")


class CORE_EX1_534:
    """Savannah Highmane"""

    deathrattle = Summon(CONTROLLER, "EX1_534t") * 2


class CORE_FP1_007:
    """Nerubian Egg"""

    deathrattle = Summon(CONTROLLER, "FP1_007t")


class CORE_FP1_011:
    """Webspinner"""

    deathrattle = Give(CONTROLLER, RandomBeast())


class CORE_FP1_022:
    """Voidcaller"""

    deathrattle = Summon(CONTROLLER, RANDOM(FRIENDLY_HAND + DEMON))


class BAR_751:
    """Spawnpool Forager"""

    deathrattle = Summon(CONTROLLER, "BAR_751t")


BAR_915e = buff(+1, +1)


class BAR_915:
    """Kabal Outfitter"""

    play = Buff(RANDOM(FRIENDLY_MINIONS - SELF), "BAR_915e")
    deathrattle = Buff(RANDOM(FRIENDLY_MINIONS - SELF), "BAR_915e")


class BAR_310:
    """Lightshower Elemental"""

    deathrattle = Heal(FRIENDLY_CHARACTERS, 8)


class MAW_022_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards = list(player.opponent.hand)
        if not cards:
            return
        count = min(2, len(cards))
        copies = [
            player.card(card.id, source=source)
            for card in source.game.random.sample(cards, count)
        ]
        return source.game.queue_actions(source, [Give(player, copies)])


class MAW_022:
    """Incriminating Psychic"""

    deathrattle = MAW_022_Deathrattle(CONTROLLER)


class BAR_026:
    """Death's Head Cultist"""

    deathrattle = Heal(FRIENDLY_HERO, 4)


class BAR_313_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if any(character.healed_this_turn for character in player.characters):
            return source.game.queue_actions(source, [Buff(source, "BAR_313e")])


BAR_313e = buff(+3, +3)


class BAR_313:
    """Priest of An'she"""

    play = BAR_313_Play(CONTROLLER)


class BAR_315_StealStats(TargetedAction):
    TARGET = ActionArg()

    def _amount_to_steal(self, source_stat, target_stat):
        if source_stat > target_stat:
            return 0
        return min(target_stat, ((target_stat - source_stat) // 2) + 1)

    def do(self, source, target):
        atk = self._amount_to_steal(source.atk, target.atk)
        health = self._amount_to_steal(source.health, target.health)
        return source.game.queue_actions(
            source,
            [
                Buff(source, "BAR_315e3", atk=atk, max_health=health),
                Buff(target, "BAR_315e4", atk=-atk, max_health=-health),
            ],
        )


BAR_315e3 = buff()
BAR_315e4 = buff()


class BAR_315:
    """Serena Bloodfeather"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
    }
    play = BAR_315_StealStats(TARGET)


class BAR_316_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        amount = 4 if source.turn_drawn == source.game.turn else 2
        return source.game.queue_actions(source, [Hit(target, amount)])


class BAR_316:
    """Oil Rig Ambusher"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
    }
    play = BAR_316_Play(TARGET)


class BAR_334_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        frenzy_minions = [
            card
            for card in player.graveyard
            if card.type == CardType.MINION and card.data.tags.get(GameTag.FRENZY)
        ][-2:]
        actions = [Summon(player, minion) for minion in frenzy_minions]
        actions.append(Hit(ALL_MINIONS - SELF, 1))
        return source.game.queue_actions(source, actions)


class BAR_334:
    """Overlord Saurfang"""

    play = BAR_334_Play(CONTROLLER)


class BAR_544:
    """Reckless Apprentice"""

    play = PlayHeroPower(FRIENDLY_HERO_POWER, ENEMY_CHARACTERS)


class BAR_547:
    """Mordresh Fire Eye"""

    play = (Attr(CONTROLLER, GameTag.NUM_HERO_POWER_DAMAGE_THIS_GAME) >= 10) & Hit(
        ENEMY_CHARACTERS, 10
    )


class BAR_551:
    """Barak Kodobane"""

    play = (
        ForceDraw(RANDOM(FRIENDLY_DECK + SPELL + (COST == 1))),
        ForceDraw(RANDOM(FRIENDLY_DECK + SPELL + (COST == 2))),
        ForceDraw(RANDOM(FRIENDLY_DECK + SPELL + (COST == 3))),
    )


class BAR_721:
    """Mankrik"""

    play = Shuffle(CONTROLLER, "BAR_721t")


class BAR_721t_Draw(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source,
            [
                Destroy(source),
                Summon(player, "BAR_721t2").then(Attack(Summon.CARD, ENEMY_HERO)),
                Draw(player),
            ],
        )


class BAR_721t:
    """Olgra, Mankrik's Wife"""

    draw = BAR_721t_Draw(CONTROLLER)


class BAR_735_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = sum(character.healed_this_turn for character in player.characters)
        if amount:
            return source.game.queue_actions(source, [Hit(ENEMY_MINIONS, amount)])


class BAR_735:
    """Xyrella"""

    play = BAR_735_Play(CONTROLLER)


class BAR_743_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        nature_spells = [
            card
            for card in player.hand
            if card.type == CardType.SPELL
            and getattr(getattr(card, "data", None), "spell_school", None)
            == SpellSchool.NATURE
        ]
        if nature_spells:
            return source.game.queue_actions(source, [Buff(source, "BAR_743e")])


class BAR_743:
    """Toad of the Wilds"""

    play = BAR_743_Play(CONTROLLER)


BAR_743e = buff(health=2)


class BAR_745:
    """Hecklefang Hyena"""

    play = Hit(FRIENDLY_HERO, 3)


class BAR_748_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for minion in player.opponent.field:
            if minion.frozen:
                actions.append(Hit(minion, 4))
            else:
                actions.append(Freeze(minion))
        if actions:
            return source.game.queue_actions(source, actions)


class BAR_748:
    """Varden Dawngrasp"""

    play = BAR_748_Play(CONTROLLER)


class BAR_750:
    """Earth Revenant"""

    play = Hit(ENEMY_MINIONS, 1)


class BAR_840_Frenzy(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, combatant):
        if getattr(combatant, "_bar_840_frenzy_triggered", False):
            return
        combatant._bar_840_frenzy_triggered = True
        return source.game.queue_actions(source, [Hit(ALL_MINIONS - SELF, 1)])


class BAR_840:
    """Whirling Combatant"""

    play = Hit(ALL_MINIONS - SELF, 1)
    events = Damage(SELF).on(BAR_840_Frenzy(SELF))


class BAR_846:
    """Mor'shan Elite"""

    play = Find(FRIENDLY_HERO + (NUM_ATTACKS > 0)) & Summon(CONTROLLER, ExactCopy(SELF))


class BAR_848_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        if source.controller.elemental_played_last_turn:
            return source.game.queue_actions(source, [Morph(target, "hexfrog")])


class BAR_848:
    """Lilypad Lurker"""

    requirements = {
        PlayReq.REQ_TARGET_IF_AVAILABLE: 0,
        PlayReq.REQ_ENEMY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = BAR_848_Play(TARGET)


class BAR_854:
    """Kindling Elemental"""

    play = Buff(CONTROLLER, "BAR_854e")


class BAR_854e:
    update = Refresh(FRIENDLY_HAND + ELEMENTAL, {GameTag.COST: -1})
    events = Play(CONTROLLER, ELEMENTAL).on(Destroy(SELF))


class BAR_873_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        holy_spells = [
            card
            for card in player.deck
            if card.type == CardType.SPELL
            and getattr(getattr(card, "data", None), "spell_school", None)
            == SpellSchool.HOLY
        ]
        if holy_spells:
            return source.game.queue_actions(
                source, [Draw(player, source.game.random.choice(holy_spells))]
            )


class BAR_873:
    """Knight of Anointment"""

    play = BAR_873_Play(CONTROLLER)


class BAR_876:
    """Northwatch Commander"""

    play = Find(FRIENDLY_SECRETS) & Draw(CONTROLLER, RANDOM(FRIENDLY_DECK + MINION))


class BAR_879_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for secret in player.secrets[:]:
            soldier = player.card("BAR_879t", source=source)
            soldier._bar_879_secret = secret
            secret.zone = Zone.REMOVEDFROMGAME
            actions.append(Summon(player, soldier))
        if actions:
            return source.game.queue_actions(source, actions)


class BAR_879t_ReturnSecret(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, soldier):
        secret = getattr(soldier, "_bar_879_secret", None)
        if (
            secret
            and secret.zone == Zone.REMOVEDFROMGAME
            and secret.id not in [card.id for card in secret.controller.secrets]
            and len(secret.controller.secrets) < secret.game.MAX_SECRETS_ON_PLAY
        ):
            secret.zone = Zone.SECRET
            source.game.manager.targeted_action(self, source, secret)


class BAR_879:
    """Cannonmaster Smythe"""

    play = BAR_879_Play(CONTROLLER)


class BAR_879t:
    """Northwatch Soldier"""

    deathrattle = BAR_879t_ReturnSecret(SELF)


class CORE_OG_109:
    """Darkshire Librarian"""

    play = Discard(RANDOM(FRIENDLY_HAND))
    deathrattle = Draw(CONTROLLER)


class CORE_OG_241:
    """Possessed Villager"""

    deathrattle = Summon(CONTROLLER, "OG_241a")


class CS3_013:
    """Shadowed Spirit"""

    deathrattle = Hit(ENEMY_HERO, 3)


class LEG_CS3_013(CS3_013):
    """Shadowed Spirit"""


class CS3_024:
    """Taelan Fordring"""

    deathrattle = ForceDraw(HIGHEST_COST(FRIENDLY_DECK + MINION))


class DED_505_DrawSpellAndDamage(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = [card for card in player.deck if card.type == CardType.SPELL]
        if spells:
            spell = source.game.random.choice(spells)
            return source.game.queue_actions(
                source, [ForceDraw(spell), Hit(player.hero, spell.cost)]
            )


class DED_505:
    """Hullbreaker"""

    play = deathrattle = DED_505_DrawSpellAndDamage(CONTROLLER)


class DED_522:
    """Cookie the Cook"""

    deathrattle = Summon(CONTROLLER, "DED_522t")


class DEEP_005:
    """Obsidian Revenant"""

    deathrattle = Summon(
        CONTROLLER, RandomMinion(cost=[0, 1, 2, 3], deathrattle=True)
    ) * 2


class DEEP_012_StealWeapon(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, skulker):
        weapon = source.controller.weapon
        if weapon:
            skulker._deep_012_weapon = weapon
            atk = weapon.atk
            health = weapon.durability
            weapon.zone = Zone.REMOVEDFROMGAME
            return source.game.queue_actions(
                source,
                [Buff(skulker, "DEEP_012e", atk=atk, max_health=health)],
            )


class DEEP_012_ReturnWeapon(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, skulker):
        weapon = getattr(skulker, "_deep_012_weapon", None)
        if weapon and weapon.zone == Zone.REMOVEDFROMGAME:
            weapon.zone = Zone.PLAY
            source.game.manager.targeted_action(self, source, weapon)


class DEEP_012:
    """Shadestone Skulker"""

    play = DEEP_012_StealWeapon(SELF)
    deathrattle = DEEP_012_ReturnWeapon(SELF)


class DEEP_012e:
    tags = {
        GameTag.CARDNAME: "Shadestone Skulker",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


class DEEP_030:
    """Elementium Geode"""

    play = deathrattle = Draw(CONTROLLER), Hit(FRIENDLY_HERO, 2)


DEEP_035_BONUS_EFFECTS = (
    "UNG_999t10e",
    "UNG_999t2e",
    "UNG_999t3e",
    "UNG_999t4e",
    "UNG_999t5e",
    "UNG_999t6e",
    "UNG_999t7e",
    "UNG_999t8e",
    "UNG_999t13e",
    "UNG_999t14e",
)


class DEEP_035_RandomBonusEffect(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        buff = source.game.random.choice(DEEP_035_BONUS_EFFECTS)
        return source.game.queue_actions(source, [Buff(target, buff)])


class DEEP_035:
    """Iridescent Gyreworm"""

    deathrattle = DEEP_035_RandomBonusEffect(FRIENDLY_MINIONS)


class DEEP_036_DoubleElementals(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for card in list(player.hand) + list(player.deck):
            if Race.ELEMENTAL in card.races:
                actions.append(
                    Buff(card, "DEEP_036e", atk=card.atk, max_health=card.health)
                )
        if actions:
            return source.game.queue_actions(source, actions)


class DEEP_036:
    """Therazane"""

    deathrattle = DEEP_036_DoubleElementals(CONTROLLER)


class DEEP_036e:
    tags = {
        GameTag.CARDNAME: "Therazane",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


class DMF_069:
    """Claw Machine"""

    deathrattle = ForceDraw(RANDOM(FRIENDLY_DECK + MINION)).then(
        Buff(ForceDraw.TARGET, "DMF_069e")
    )


DMF_069e = buff(3, 3)


class DMF_085_FireMissiles(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for _ in range(4):
            targets = [target for target in player.opponent.characters if not target.dead]
            if targets:
                actions.append(Hit(source.game.random.choice(targets), 2))
        if actions:
            return source.game.queue_actions(source, actions)


class DMF_085:
    """Darkmoon Tonk"""

    deathrattle = DMF_085_FireMissiles(CONTROLLER)


class DMF_191:
    """Showstopper"""

    deathrattle = Silence(ALL_MINIONS)


class DMF_223:
    """Renowned Performer"""

    deathrattle = Summon(CONTROLLER, "DMF_223t") * 2


class DMF_514:
    """Ticket Master"""

    deathrattle = Shuffle(CONTROLLER, "DMF_514t") * 3


class DMF_514t:
    """Tickets"""

    draw = CAST_WHEN_DRAWN
    play = Summon(CONTROLLER, "DMF_514t2")


class DMF_523:
    """Bumper Car"""

    deathrattle = Give(CONTROLLER, "DMF_523t") * 2


class DMF_533:
    """Ring Matron"""

    deathrattle = Summon(CONTROLLER, "DMF_533t") * 2


class REV_012:
    """Bog Beast"""

    deathrattle = Summon(CONTROLLER, "REV_012t")


class REV_015:
    """Masked Reveler"""

    deathrattle = Summon(CONTROLLER, Copy(RANDOM(FRIENDLY_DECK + MINION))).then(
        Buff(Summon.CARD, "REV_015t")
    )


class REV_015t:
    atk = SET(2)
    max_health = SET(2)


class REV_251:
    """Sinrunner"""

    deathrattle = Destroy(RANDOM_ENEMY_MINION)


class REV_356:
    """Batty Guest"""

    deathrattle = Summon(CONTROLLER, "REV_350t")


class REV_374_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        shadow_spells = [
            card
            for card in player.hand
            if card.type == CardType.SPELL
            and getattr(getattr(card, "data", None), "spell_school", None)
            == SpellSchool.SHADOW
        ]
        if not shadow_spells:
            return
        highest_cost = max(card.cost for card in shadow_spells)
        candidates = [card for card in shadow_spells if card.cost == highest_cost]
        target = source.game.random.choice(candidates)
        return source.game.queue_actions(source, [Buff(target, "REV_374e")])


class REV_374:
    """Shadowborn"""

    deathrattle = REV_374_Deathrattle(CONTROLLER)


REV_374e = buff(cost=-3)


class REV_375:
    """Stoneborn General"""

    deathrattle = Summon(CONTROLLER, "REV_375t")


class REV_510:
    """Kryxis the Voracious"""

    play = Discard(FRIENDLY_HAND)
    deathrattle = Draw(CONTROLLER) * 3


class REV_829_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        secrets = list(player.secrets)
        if not secrets:
            return
        secret = source.game.random.choice(secrets)
        secret._events.append(Reveal(CARD(secret)).on(Summon(CONTROLLER, "REV_829")))
        return source.game.queue_actions(source, [Buff(secret, "REV_829e")])


class REV_829:
    """Halkias"""

    deathrattle = REV_829_Deathrattle(CONTROLLER)


class REV_829e:
    pass


class REV_845:
    """Volatile Skeleton"""

    deathrattle = Hit(RANDOM_ENEMY_CHARACTER, 2)


class REV_952:
    """Sinful Sous Chef"""

    deathrattle = Give(CONTROLLER, "CS2_101t") * 2


class REV_955:
    """Stewart the Steward"""

    deathrattle = Buff(CONTROLLER, "REV_955e")


class REV_955e:
    events = Summon(CONTROLLER, ID("CS2_101t")).after(
        Buff(Summon.CARD, "REV_955e2"), Destroy(SELF)
    )


class REV_955e2:
    tags = {GameTag.ATK: 3, GameTag.HEALTH: 3, GameTag.DEATHRATTLE: True}
    deathrattle = Buff(CONTROLLER, "REV_955e")


class RLK_082_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        card = player.card(source.id, source=source)
        card._costs_health = True
        return source.game.queue_actions(source, [Give(player, card)])


class LEG_RLK_082:
    """Deathbringer Saurfang"""

    deathrattle = RLK_082_Deathrattle(CONTROLLER)


class RLK_082(LEG_RLK_082):
    """Deathbringer Saurfang"""


class RLK_226_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if getattr(player, "corpses", 0) < 3:
            return
        player.corpses -= 3
        return source.game.queue_actions(source, [Summon(player, "RLK_226t")])


class LEG_RLK_226:
    """Ymirjar Deathbringer"""

    deathrattle = RLK_226_Deathrattle(CONTROLLER)


class RLK_226(LEG_RLK_226):
    """Ymirjar Deathbringer"""


class NX2_024:
    """Shambling Chow"""

    deathrattle = Hit(FRIENDLY_HERO, 4)


class NX2_025_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        cards.db.initialize()
        pool = []
        for card_id, data in db.items():
            if not data.collectible or (source.game.is_standard and not data.is_standard):
                continue
            card = player.card(card_id, source=source)
            if card.get_actions("outcast"):
                pool.append(card)
        if not pool:
            return
        source.game.random.shuffle(pool)
        return source.game.queue_actions(source, [Give(player, pool[0])])


class NX2_025:
    """Calamity's Grasp"""

    deathrattle = NX2_025_Deathrattle(CONTROLLER)


class NX2_032:
    """Lost Exarch"""

    deathrattle = SpendMana(CONTROLLER, CURRENT_MANA(CONTROLLER)).then(
        Summon(CONTROLLER, "NX2_032t") * SpendMana.AMOUNT
    )


NX2_034_HORSEMEN = ("NX2_034", "NX2_034t", "NX2_034t1", "NX2_034t2")
NX2_034_OTHER_HORSEMEN = ("NX2_034t", "NX2_034t1", "NX2_034t2")


class NX2_034_HorsemanDeathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        dead_horsemen = {
            card.id
            for card in player.graveyard
            if card.id in NX2_034_HORSEMEN
        }
        if set(NX2_034_HORSEMEN).issubset(dead_horsemen):
            return source.game.queue_actions(source, [Destroy(ENEMY_HERO)])


class NX2_034:
    """Rivendare, Warrider"""

    deathrattle = (
        Shuffle(CONTROLLER, "NX2_034t"),
        Shuffle(CONTROLLER, "NX2_034t1"),
        Shuffle(CONTROLLER, "NX2_034t2"),
        NX2_034_HorsemanDeathrattle(CONTROLLER),
    )


class NX2_034t:
    """Blaumeux, Faminerider"""

    deathrattle = NX2_034_HorsemanDeathrattle(CONTROLLER)


class NX2_034t1:
    """Korth'azz, Deathrider"""

    deathrattle = NX2_034_HorsemanDeathrattle(CONTROLLER)


class NX2_034t2:
    """Zeliek, Conquestrider"""

    deathrattle = NX2_034_HorsemanDeathrattle(CONTROLLER)


class ONY_028:
    """Mi'da, Pure Light"""

    deathrattle = Shuffle(CONTROLLER, "ONY_028t")


class ONY_028t:
    """Fragment of Mi'da"""

    draw = CAST_WHEN_DRAWN
    play = Summon(CONTROLLER, "ONY_028")


class RLK_086_StoreKill(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, weapon):
        defender = source.event_args[1]
        if defender.dead and defender.type == CardType.MINION:
            if not hasattr(weapon, "_rlk_086_killed_minions"):
                weapon._rlk_086_killed_minions = []
            weapon._rlk_086_killed_minions.append(defender.id)


class RLK_086_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = [
            Summon(player, minion_id)
            for minion_id in getattr(source, "_rlk_086_killed_minions", [])
        ]
        if actions:
            return source.game.queue_actions(source, actions)


class RLK_086:
    """Frostmourne"""

    events = Attack(FRIENDLY_HERO, ALL_MINIONS).after(RLK_086_StoreKill(SELF))
    deathrattle = RLK_086_Deathrattle(CONTROLLER)


class CORE_RLK_086(RLK_086):
    """Frostmourne"""


class RLK_029:
    """Shatterskin Gargoyle"""

    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 4)


class RLK_070:
    """Infected Peasant"""

    deathrattle = Summon(CONTROLLER, "RLK_070t")


class RLK_113:
    """Brittleskin Zombie"""

    deathrattle = CurrentPlayer(OPPONENT) & Hit(ENEMY_HERO, 3)


class RLK_217_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        deathrattle_minions = [
            card
            for card in player.deck
            if card.type == CardType.MINION
            and card.has_deathrattle
            and card.id != source.id
        ]
        if not deathrattle_minions:
            return
        card = source.game.random.choice(deathrattle_minions)
        copy = ExactCopy(TARGET).copy(source, card)
        return source.game.queue_actions(
            source,
            [
                Give(
                    player,
                    MultiBuff(copy, ["RLK_217e", "RLK_217e2"]),
                )
            ],
        )


class RLK_217:
    """Scourge Illusionist"""

    deathrattle = RLK_217_Deathrattle(CONTROLLER)


class RLK_217e:
    atk = SET(4)
    max_health = SET(4)


class RLK_217e2:
    cost = lambda self, cost: max(0, cost - 4)


class RLK_223:
    """Thassarian"""

    play = deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 2)


class RLK_511_Deathrattle(TargetedAction):
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
                source, [ForceDraw(source.game.random.choice(frost_spells))]
            )


class RLK_511:
    """Harbinger of Winter"""

    deathrattle = RLK_511_Deathrattle(CONTROLLER)


class RLK_540_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        undead = [
            card
            for card in player.hand
            if card.type == CardType.MINION and Race.UNDEAD in card.races
        ]
        if undead:
            card = source.game.random.choice(undead)
            source.rlk_540_discarded_copy = ExactCopy(TARGET).copy(source, card)
            return source.game.queue_actions(source, [Discard(card)])


class RLK_540_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        card = getattr(source, "rlk_540_discarded_copy", None)
        if card:
            return source.game.queue_actions(source, [Summon(player, card)])


class RLK_540:
    """Amorphous Slime"""

    play = RLK_540_Play(CONTROLLER)
    deathrattle = RLK_540_Deathrattle(CONTROLLER)


class RLK_542:
    """Arcsplitter"""

    deathrattle = Give(CONTROLLER, "RLK_843") * 2


class RLK_551:
    """Blightblood Berserker"""

    deathrattle = Hit(RANDOM(ENEMY_CHARACTERS), 3)


class RLK_554:
    """Harkener of Dread"""

    deathrattle = Summon(CONTROLLER, "RLK_554t")


class RLK_591e_Tick(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, aura):
        aura._rlk_591_turns = getattr(aura, "_rlk_591_turns", 3) - 1
        if aura._rlk_591_turns <= 0:
            aura.remove()
            return source.game.queue_actions(source, [Destroy(aura.owner.hero)])
        _rlk_591_mark_first(aura.owner)


class RLK_591e_ClearDiscount(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, aura, card):
        if getattr(card, "_rlk_591_discounted", False):
            card._rlk_591_discounted = False


def _rlk_591_mark_first(player):
    for card in player.hand:
        card._rlk_591_discounted = False
    if player.hand:
        player.hand[0]._rlk_591_discounted = True


class RLK_591e:
    update = Refresh(
        FRIENDLY_HAND
        + FilterSelector(
            lambda entity, source: getattr(entity, "_rlk_591_discounted", False)
        ),
        {GameTag.COST: SET(0)},
    )
    events = OWN_TURN_BEGIN.on(RLK_591e_Tick(SELF)), Play(CONTROLLER).after(
        RLK_591e_ClearDiscount(SELF, Play.CARD)
    )

    def apply(self, owner):
        self._rlk_591_turns = getattr(self, "_rlk_591_turns", 3)
        _rlk_591_mark_first(owner)


class RLK_591:
    """Bonelord Frostwhisper"""

    deathrattle = Buff(CONTROLLER, "RLK_591e")


class RLK_592:
    """Invincible"""

    play = deathrattle = Buff(
        RANDOM(
            FRIENDLY_MINIONS
            + FilterSelector(
                lambda entity, source: hasattr(entity, "races")
                and entity is not source
                and Race.UNDEAD in entity.races
            )
        ),
        "RLK_592e",
    ).then(Taunt(Buff.TARGET))


RLK_592e = buff(atk=5, health=5)


class RLK_604_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, minion):
        minion.zone = Zone.PLAY
        minion.dormant = True
        minion.damage = 0
        source.game.refresh_auras()
        source.game.manager.targeted_action(self, source, minion)


class RLK_604_Awaken(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, minion, card):
        if (
            card.type == CardType.SPELL
            and getattr(getattr(card, "data", None), "spell_school", None)
            == SpellSchool.FIRE
        ):
            return source.game.queue_actions(source, [Awaken(minion)])


class RLK_604:
    """Thori'belore"""

    deathrattle = RLK_604_Deathrattle(SELF)
    dormant_events = Play(CONTROLLER, SPELL).after(RLK_604_Awaken(SELF, Play.CARD))


class RLK_650:
    """Lingering Zombie"""

    deathrattle = Summon(CONTROLLER, "RLK_650t")


class RLK_650t:
    """Disarmed Zombie"""

    deathrattle = Summon(CONTROLLER, "RLK_650t2")


class RLK_653_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        candidates = [minion for minion in player.field if minion is not source]
        if candidates:
            target = source.game.random.choice(candidates)
            target.tags[GameTag.DEATHRATTLE] = True
            target.additional_deathrattles.append((Summon(CONTROLLER, "RLK_653"),))
            source.game.manager.targeted_action(self, source, target)


class RLK_653:
    """Infectious Ghoul"""

    deathrattle = RLK_653_Deathrattle(CONTROLLER)


class RLK_657:
    """Underking"""

    play = deathrattle = GainArmor(FRIENDLY_HERO, 6)


class RLK_708:
    """Chillfallen Baron"""

    play = deathrattle = Draw(CONTROLLER)


class RLK_713:
    """Lady Deathwhisper"""

    deathrattle = Give(
        CONTROLLER,
        Copy(
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
        ),
    )


class RLK_813:
    """Bonecaller"""

    deathrattle = Summon(CONTROLLER, "SCH_710t")


class RLK_830_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        undead = [
            card
            for card in player.deck
            if card.type == CardType.MINION and Race.UNDEAD in card.races
        ]
        if undead:
            card = source.game.random.choice(undead)
            copy = ExactCopy(TARGET).copy(source, card)
            return source.game.queue_actions(
                source, [ForceDraw(card), Summon(player, copy)]
            )


class RLK_830:
    """Flesh Behemoth"""

    deathrattle = RLK_830_Deathrattle(CONTROLLER)


class RLK_831:
    """Plaguespreader"""

    deathrattle = Morph(RANDOM(ENEMY_HAND + MINION), ExactCopy(SELF))


class RLK_833:
    """Foul Egg"""

    deathrattle = Summon(CONTROLLER, "RLK_833t")


class RLK_845:
    """Mind Eater"""

    deathrattle = Give(CONTROLLER, Copy(RANDOM(ENEMY_DECK)))


class RLK_914:
    """Umbral Geist"""

    deathrattle = Give(CONTROLLER, RandomSpell(spell_school=SpellSchool.SHADOW))


RLK_957e = buff(atk=2, health=1)


class RLK_957:
    """Wailing Banshee"""

    deathrattle = Buff(RANDOM(FRIENDLY_MINIONS - SELF + UNDEAD), "RLK_957e")


class SCH_147:
    """Boneweb Egg"""

    deathrattle = Summon(CONTROLLER, "SCH_147t") * 2
    discard = Deathrattle(SELF)


class SCH_244:
    """Teacher's Pet"""

    deathrattle = Summon(CONTROLLER, RandomMinion(cost=3, race=Race.BEAST))


class SCH_340:
    """Bloated Python"""

    deathrattle = Summon(CONTROLLER, "SCH_340t")


class SCH_426:
    """Infiltrator Lilian"""

    deathrattle = Summon(CONTROLLER, "SCH_426t").then(
        Attack(Summon.CARD, RANDOM_ENEMY_CHARACTER)
    )


class SCH_526:
    """Lord Barov"""

    play = Buff(ALL_MINIONS - SELF, "SCH_526e")
    deathrattle = Hit(ALL_MINIONS, 1)


class SCH_526e:
    max_health = SET(1)


class SCH_615:
    """Totem Goliath"""

    deathrattle = Summon(CONTROLLER, BASIC_TOTEMS)


class SCH_621_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if source.atk <= 1 or source.max_health <= 1:
            return
        rattlegore = ExactCopy(SELF).evaluate(source)[0]
        return source.game.queue_actions(
            source,
            [
                Summon(player, rattlegore).then(
                    Buff(
                        Summon.CARD,
                        "SCH_621e",
                        atk=-(source.atk - 8),
                        max_health=-(source.max_health - 8),
                    )
                )
            ],
        )


class SCH_621:
    """Rattlegore"""

    deathrattle = SCH_621_Deathrattle(CONTROLLER)


@custom_card
class SCH_621e:
    tags = {
        GameTag.CARDNAME: "Rattlegore",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


class SCH_707:
    """Fishy Flyer"""

    deathrattle = Give(CONTROLLER, "SCH_707t")


class SCH_708:
    """Sneaky Delinquent"""

    deathrattle = Give(CONTROLLER, "SCH_708t")


class SCH_709:
    """Smug Senior"""

    deathrattle = Give(CONTROLLER, "SCH_709t")


class SCH_711:
    """Plagued Protodrake"""

    deathrattle = Summon(CONTROLLER, RandomMinion(cost=7))


class SCH_714_RememberSpell(TargetedAction):
    TARGET = ActionArg()
    CARD = CardArg()

    def do(self, source, elekk, spell):
        remembered = getattr(elekk, "_sch_714_spells", [])
        remembered.append(ExactCopy(Play.CARD).evaluate(elekk)[0])
        elekk._sch_714_spells = remembered


class SCH_714_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = getattr(source, "_sch_714_spells", [])
        if spells:
            return source.game.queue_actions(source, [Shuffle(player, spells)])


class SCH_714:
    """Educated Elekk"""

    events = Play(ALL_PLAYERS, SPELL).after(SCH_714_RememberSpell(SELF, Play.CARD))
    deathrattle = SCH_714_Deathrattle(CONTROLLER)


class SW_006:
    """Stubborn Suspect"""

    deathrattle = Summon(CONTROLLER, RandomMinion(cost=3))


class SW_042:
    """Persistent Peddler"""

    deathrattle = Summon(CONTROLLER, RANDOM(FRIENDLY_DECK + ID("SW_042")))


class SW_069_Store(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, banker):
        if not banker.controller.deck:
            return
        stored = getattr(banker, "_sw_069_stored_cards", [])
        card = banker.game.random.choice(list(banker.controller.deck))
        card.zone = Zone.REMOVEDFROMGAME
        banker.game.manager.targeted_action(self, banker, card)
        stored.append(card)
        banker._sw_069_stored_cards = stored


class SW_069_Return(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        stored = getattr(source, "_sw_069_stored_cards", [])
        if stored:
            return source.game.queue_actions(source, [Give(player, stored)])


class SW_069:
    """Enthusiastic Banker"""

    events = OWN_TURN_END.on(SW_069_Store(SELF))
    deathrattle = SW_069_Return(CONTROLLER)


class SW_070:
    """Mailbox Dancer"""

    play = Give(CONTROLLER, THE_COIN)
    deathrattle = Give(OPPONENT, THE_COIN)


class SW_075_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        boars = [
            card
            for card in player.graveyard
            if card.id == "SW_075" and not getattr(card, "discarded", False)
        ]
        if len(boars) >= 7:
            sword = player.card("SW_075t", source=source, zone=Zone.SETASIDE)
            return source.game.queue_actions(source, [Summon(player, sword)])


class SW_075:
    """Elwynn Boar"""

    deathrattle = SW_075_Deathrattle(CONTROLLER)


class SW_323_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        rat_king = ExactCopy(SELF).evaluate(source)[0]
        return source.game.queue_actions(
            source,
            [Summon(player, rat_king).then(Dormant(Summon.CARD, 999))],
        )


class SW_323:
    """The Rat King"""

    progress_total = 5
    deathrattle = SW_323_Deathrattle(CONTROLLER)
    dormant_events = Death(FRIENDLY + MINION).on(AddProgress(SELF, Death.ENTITY))
    reward = Awaken(SELF)


class SW_434:
    """Loan Shark"""

    play = Give(OPPONENT, THE_COIN)
    deathrattle = Give(CONTROLLER, THE_COIN) * 2


class SW_455:
    """Rodent Nest"""

    deathrattle = Summon(CONTROLLER, "SW_455t") * 5


class SW_463:
    """Imported Tarantula"""

    deathrattle = Summon(CONTROLLER, "SW_463t") * 2


class TID_707_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        pool = [
            card_id
            for card_id, data in db.items()
            if data.collectible
            and data.type == CardType.SPELL
            and data.card_class == CardClass.MAGE
            and getattr(data, "spell_school", None) == SpellSchool.ARCANE
            and (not source.game.is_standard or data.is_standard)
        ]
        if len(pool) < 2 and source.game.is_standard:
            pool = [
                card_id
                for card_id, data in db.items()
                if data.collectible
                and data.type == CardType.SPELL
                and data.card_class == CardClass.MAGE
                and getattr(data, "spell_school", None) == SpellSchool.ARCANE
            ]
        cards = [
            player.card(card_id, source=source)
            for card_id in source.game.random.sample(pool, min(2, len(pool)))
        ]
        return source.game.queue_actions(
            source, [Give(player, card).then(Buff(Give.CARD, "TID_707e")) for card in cards]
        )


class TID_707:
    """Submerged Spacerock"""

    deathrattle = TID_707_Deathrattle(CONTROLLER)


class TID_707e:
    class Hand:
        events = OWN_TURN_END.on(Discard(OWNER))

    events = REMOVED_IN_PLAY


OZUMAT_TENTACLES = {
    "TID_711t",
    "TID_711t2",
    "TID_711t3",
    "TID_711t4",
    "TID_711t5",
    "TID_711t6",
}


class TID_711_Deathrattle(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        count = sum(1 for minion in player.field if minion.id in OZUMAT_TENTACLES)
        enemies = list(player.opponent.field)
        if count and enemies:
            targets = source.game.random.sample(enemies, min(count, len(enemies)))
            return source.game.queue_actions(source, [Destroy(target) for target in targets])


class TID_711:
    """Ozumat"""

    deathrattle = TID_711_Deathrattle(CONTROLLER)


class SW_068:
    """Mo'arg Forgefiend"""

    deathrattle = GainArmor(FRIENDLY_HERO, 8)


class SW_439:
    """Vibrant Squirrel"""

    deathrattle = Shuffle(CONTROLLER, "SW_439t") * 4


class SW_439t:
    """Acorn"""

    draw = CAST_WHEN_DRAWN
    play = Summon(CONTROLLER, "SW_439t2")


class TOY_100:
    """Gnomelia, S.A.F.E. Pilot"""

    events = Attack(SELF).on(CLEAVE)
    deathrattle = Hit(ENEMY_CHARACTERS, 2)


class CORE_TOY_100(TOY_100):
    """Gnomelia, S.A.F.E. Pilot"""


class WC_701:
    """Felrattler"""

    deathrattle = Hit(ENEMY_MINIONS, 1)


class CS3_001_DrawnMinion(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        drawn = source.event_args[1]
        if drawn.type == CardType.MINION:
            source.game.queue_actions(source, [Buff(drawn, "CS3_001e")])
            source.remove()


class CS3_001:
    """Aegwynn, the Guardian"""

    deathrattle = Buff(CONTROLLER, "CS3_001e2")


class LEG_CS3_001(CS3_001):
    """Aegwynn, the Guardian"""


class CS3_001e:
    tags = {GameTag.SPELLPOWER: 2, GameTag.DEATHRATTLE: True}
    deathrattle = Buff(CONTROLLER, "CS3_001e2")


class CS3_001e2:
    events = Draw(CONTROLLER, MINION).on(CS3_001_DrawnMinion(CONTROLLER))
