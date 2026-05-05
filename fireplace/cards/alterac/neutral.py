from ..utils import *
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
        return [
            card_id
            for card_id, data in cards.db.items()
            if data.collectible
            and (not source.game.is_standard or data.is_standard)
            and any(card_class in discover_classes for card_class in data.classes)
            and (
                data.type == CardType.WEAPON
                or data.tags.get(GameTag.SECRET)
                or (data.type == CardType.MINION and Race.BEAST in data.races)
            )
        ]

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


class BAR_330:
    """Tuskpiercer"""

    deathrattle = ForceDraw(RANDOM(FRIENDLY_DECK + MINION + DEATHRATTLE))


class BAR_535:
    """Thickhide Kodo"""

    deathrattle = GainArmor(FRIENDLY_HERO, 5)


class CORE_BAR_535:
    """Thickhide Kodo"""

    deathrattle = GainArmor(FRIENDLY_HERO, 5)


class CORE_BOT_312:
    """Replicating Menace"""

    magnetic = MAGNETIC("BOT_312e")
    deathrattle = Summon(CONTROLLER, "BOT_312t") * 3


class CORE_BT_304:
    """Enhanced Dreadlord"""

    deathrattle = Summon(CONTROLLER, "BT_304t")


class CORE_CFM_120:
    """Mistress of Mixtures"""

    deathrattle = Heal(ALL_HEROES, 4)


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


class BAR_026:
    """Death's Head Cultist"""

    deathrattle = Heal(FRIENDLY_HERO, 4)
