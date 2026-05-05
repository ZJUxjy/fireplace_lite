from hearthstone.enums import SpellSchool
from ..utils import *


_TOY_SOLDIERS = (
    "TOY_814t",
    "TOY_814t2",
    "TOY_814t3",
    "TOY_814t4",
    "TOY_814t5",
    "TOY_814t6",
    "TOY_814t7",
    "TOY_814t8",
)


def _tar_slime_attack(card, amount):
    if card.controller is not card.game.current_player:
        return amount + 2
    return amount


def _playhouse_giant_cost(card, cost):
    return max(0, cost - getattr(card.controller, "cards_drawn_this_game", 0))


def _stat_delta(card, atk=None, health=None):
    kwargs = {}
    if atk is not None:
        kwargs["atk"] = atk - card.atk
    if health is not None:
        kwargs["max_health"] = health - card.health
    return kwargs


class MIS_026_DorianCopy(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, drawn):
        if drawn.type != CardType.MINION:
            return
        copy = ExactCopy(TARGET).copy(source, drawn)
        return source.game.queue_actions(
            source,
            [
                Give(
                    source.controller,
                    Buff(
                        copy,
                        "MIS_026e",
                        atk=1 - copy.atk,
                        max_health=1 - copy.health,
                        cost=1 - copy.cost,
                    ),
                )
            ],
        )


class MIS_916_ProGamer(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        winner = source.game.random.choice((player, player.opponent))
        return source.game.queue_actions(source, [Draw(winner), Draw(winner)])


class TOY_054_MarkSpellCast(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        card._card_grader_spell_cast = True


class TOY_054_DeckChoice(Choice):
    def choose(self, card):
        if card not in self.cards:
            raise InvalidAction(
                "%r is not a valid choice (one of %r)" % (card, self.cards)
            )
        self.player.choice = None
        self.source.game.queue_actions(self.source, [Give(self.player, card)])
        self.trigger_choice_callback()


class TOY_054_CardGrader(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if not getattr(source, "_card_grader_spell_cast", False):
            return
        cards = list(player.deck)
        if len(cards) > 3:
            cards = source.game.random.sample(cards, 3)
        return source.game.queue_actions(source, [TOY_054_DeckChoice(player, cards)])


class TOY_386_GiftwrappedWhelp(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        dragons = [card for card in player.hand if Race.DRAGON in card.races]
        if not dragons:
            return
        dragon = source.game.random.choice(dragons)
        return source.game.queue_actions(
            source,
            [
                Buff(source, "TOY_386e", atk=1, max_health=1),
                Buff(dragon, "TOY_386e", atk=1, max_health=1),
            ],
        )


class TOY_390_ClearancePromoter(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = [card for card in player.hand if card.type == CardType.SPELL]
        actions = [Buff(card, "TOY_390e") for card in spells[:2]]
        return source.game.queue_actions(source, actions)


class TOY_391_CaricatureArtist(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [
            card
            for card in player.deck
            if card.type == CardType.MINION and card.cost >= 5
        ]
        if not minions:
            return
        card = source.game.random.choice(minions)
        return source.game.queue_actions(
            source, [ForceDraw(card), Buff(card, "TOY_391e")]
        )


class TOY_509_WindUpMusician(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = getattr(source, "_wind_up_damage", None)
        if amount is None:
            amount = source.data.tags.get(GameTag.TAG_SCRIPT_DATA_NUM_1, 1)
        return source.game.queue_actions(source, [Hit(player.opponent.field, amount)])


class TOY_517_DrawRush(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        rush_minions = [
            card
            for card in player.deck
            if card.type == CardType.MINION and card.data.tags.get(GameTag.RUSH)
        ]
        if rush_minions:
            return source.game.queue_actions(source, [ForceDraw(rush_minions[0])])


class TOY_520_CastSecrets(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        pool = [
            card_id
            for card_id, data in db.items()
            if data.collectible
            and data.type == CardType.SPELL
            and data.tags.get(GameTag.SECRET)
            and (not source.game.is_standard or data.is_standard)
        ]
        if not pool:
            return
        source.game.random.shuffle(pool)
        cards = []
        for card_id in pool:
            if len(cards) == 2:
                break
            if card_id not in [card.id for card in player.secrets]:
                cards.append(player.card(card_id, source=source))
        player._observer_of_mysteries_secrets = cards
        return source.game.queue_actions(
            source, [Summon(player, card) for card in cards]
        )


class TOY_520_RemoveSecrets(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        secrets = getattr(player, "_observer_of_mysteries_secrets", [])
        actions = [Remove(secret) for secret in secrets if secret.zone == Zone.SECRET]
        player._observer_of_mysteries_secrets = []
        return source.game.queue_actions(source, actions)


class TOY_531_Lina(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, spell):
        player = source.controller
        amount = spell.cost
        actions = []
        while len(player.field) + len(actions) < source.game.MAX_MINIONS_ON_FIELD:
            actions.append(Summon(player, RandomMinion(cost=amount)))
        return source.game.queue_actions(source, actions)


class TOY_703_Colifero(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.deck if card.type == CardType.MINION]
        if not minions:
            return
        card = source.game.random.choice(minions)
        actions = [ForceDraw(card)]
        for minion in player.field:
            if minion is not source:
                actions.append(
                    Morph(minion, ExactCopy(TARGET).copy(source, card))
                )
        return source.game.queue_actions(source, actions)


class TOY_814_Bucket(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        return source.game.queue_actions(
            source,
            [
                Summon(player, source.game.random.choice(_TOY_SOLDIERS))
                for _ in range(5)
            ],
        )


class TOY_820_Animatronic(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, minion):
        candidates = [
            card
            for card in source.game.board
            if card.type == CardType.MINION
            and card is not minion
            and not card.dead
            and not card.dormant
            and card.atk < minion.atk
        ]
        if candidates:
            return source.game.queue_actions(
                source, [Destroy(source.game.random.choice(candidates))]
            )


class TOY_878_Cosplay(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, played):
        if not source.zone == Zone.PLAY:
            return
        copy = ExactCopy(TARGET).copy(source, played)
        return source.game.queue_actions(
            source,
            [
                Morph(source, Buff(copy, "TOY_878e", **_stat_delta(copy, 3, 4)))
            ],
        )


class TOY_891_WorkshopJanitor(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if any(card.type == CardType.LOCATION for card in player.field):
            return source.game.queue_actions(source, [Draw(player), Draw(player)])


class TOY_893_NestingGolem(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, golem):
        if golem.atk <= 1 or golem.health <= 1:
            return
        return source.game.queue_actions(
            source,
            [
                Summon(golem.controller, golem.id).then(
                    Buff(Summon.CARD, "TOY_893e", atk=-1, max_health=-1)
                )
            ],
        )


class TOY_894_SwapAttack(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        source_atk = source.atk
        target_atk = target.atk
        return source.game.queue_actions(
            source,
            [
                Buff(source, "TOY_894e", atk=target_atk - source_atk),
                Buff(target, "TOY_894e", atk=source_atk - target_atk),
            ],
        )


class TOY_895_SwapHealth(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        source_health = source.health
        target_health = target.health
        return source.game.queue_actions(
            source,
            [
                Buff(source, "TOY_895e", max_health=target_health - source_health),
                Buff(target, "TOY_895e", max_health=source_health - target_health),
            ],
        )


class TOY_896_SwapStats(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        source_stats = (source.atk, source.health)
        target_stats = (target.atk, target.health)
        return source.game.queue_actions(
            source,
            [
                Buff(
                    source,
                    "TOY_896e",
                    atk=target_stats[0] - source_stats[0],
                    max_health=target_stats[1] - source_stats[1],
                ),
                Buff(
                    target,
                    "TOY_896e",
                    atk=source_stats[0] - target_stats[0],
                    max_health=source_stats[1] - target_stats[1],
                ),
            ],
        )


class TOY_897_FloppyHydra(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, hydra):
        copy = ExactCopy(TARGET).copy(source, hydra)
        return source.game.queue_actions(
            source,
            [
                Buff(copy, "TOY_897e", atk=copy.atk, max_health=copy.health),
                Shuffle(hydra.controller, copy),
            ],
        )


class TOY_960_Joymancer(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        actions = []
        for card in player.cards_played_this_game:
            if card.type == CardType.MINION and (card.atk == 1 or card.health == 1):
                actions.append(Give(player, ExactCopy(TARGET).copy(source, card)))
        return source.game.queue_actions(source, actions)


##
# Minions


class MIS_025:
    """The Replicator-inator"""

    miniaturize_mini = "MIS_025t"
    events = Play(CONTROLLER, MINION + (ATK == Attr(SELF, GameTag.ATK))).on(
        Summon(CONTROLLER, Copy(Play.CARD))
    )


class MIS_026:
    """Puppetmaster Dorian"""

    events = Draw(CONTROLLER).on(MIS_026_DorianCopy(Draw.CARD))


class MIS_308:
    """Explodineer"""

    events = OWN_TURN_END.on(Shuffle(OPPONENT, "BOT_511t"))


class MIS_314:
    """Building-Block Golem"""

    deathrattle = Summon(CONTROLLER, RandomMinion(cost=1)) * 3


class MIS_916:
    """Pro Gamer"""

    play = MIS_916_ProGamer(CONTROLLER)


class TOY_000:
    """Tar Slime"""

    update = Refresh(SELF, {GameTag.ATK: _tar_slime_attack})


class TOY_006:
    """Scarab Keychain"""

    play = Discover(CONTROLLER, RandomCard(cost=2))


class TOY_054:
    """Card Grader"""

    play = TOY_054_CardGrader(CONTROLLER)

    class Hand:
        events = Play(CONTROLLER, SPELL).on(TOY_054_MarkSpellCast(SELF))


class TOY_307:
    """Sweetened Snowflurry"""

    miniaturize_mini = "TOY_307t"
    play = Give(CONTROLLER, RandomSpell(spell_school=SpellSchool.FROST)) * 2


class TOY_312:
    """Nostalgic Gnome"""

    miniaturize_mini = "TOY_312t"
    tags = {GameTag.RUSH: True}
    events = Attack(SELF).after(Dead(Attack.DEFENDER) & Draw(CONTROLLER))


class TOY_330:
    """Zilliax Deluxe 3000"""


class TOY_340:
    """Nostalgic Initiate"""

    miniaturize_mini = "TOY_340t1"
    events = OWN_SPELL_PLAY.on(Buff(SELF, "TOY_340e"), Destroy(SELF))


class TOY_341:
    """Nostalgic Clown"""

    miniaturize_mini = "TOY_341t"

    def play(self):
        if self.controller.hero_power.activations_this_turn >= 1:
            yield SetTags(SELF, {GameTag.TAUNT: True, GameTag.DIVINE_SHIELD: True})


class TOY_386:
    """Giftwrapped Whelp"""

    play = TOY_386_GiftwrappedWhelp(CONTROLLER)


class TOY_390:
    """Clearance Promoter"""

    deathrattle = TOY_390_ClearancePromoter(CONTROLLER)


class TOY_391:
    """Caricature Artist"""

    play = TOY_391_CaricatureArtist(CONTROLLER)


class TOY_509:
    """Wind-Up Musician"""

    play = TOY_509_WindUpMusician(CONTROLLER)


class TOY_517:
    """Plucky Paintfin"""

    tags = {GameTag.POISONOUS: True}
    play = TOY_517_DrawRush(CONTROLLER)


class TOY_518:
    """Treasure Distributor"""

    events = Summon(CONTROLLER, PIRATE).after(Buff(Summon.CARD, "TOY_518e"))


class TOY_520:
    """Observer of Mysteries"""

    play = TOY_520_CastSecrets(CONTROLLER)
    events = OWN_TURN_BEGIN.on(TOY_520_RemoveSecrets(CONTROLLER))


class TOY_528:
    """Sing-Along Buddy"""

    update = Refresh(CONTROLLER, {GameTag.HERO_POWER_DOUBLE: 1})


class TOY_530:
    """Playhouse Giant"""

    class Hand:
        update = Refresh(SELF, {GameTag.COST: _playhouse_giant_cost})


class TOY_531:
    """Li'Na, Shop Manager"""

    events = Play(CONTROLLER, SPELL).after(TOY_531_Lina(Play.CARD))


class TOY_601:
    """Factory Assemblybot"""

    miniaturize_mini = "TOY_601t"
    events = OWN_TURN_END.on(Summon(CONTROLLER, "TOY_601t"))


class TOY_601t:
    """Assembly Bot"""

    tags = {GameTag.RUSH: True}


class TOY_646:
    """Messmaker"""

    deathrattle = Hit(ENEMY_CHARACTERS, 1)


class TOY_670:
    """Giggling Toymaker"""

    deathrattle = Summon(CONTROLLER, "GVG_085") * 2


class TOY_700:
    """Splendiferous Whizbang"""


class TOY_703:
    """Colifero the Artist"""

    play = TOY_703_Colifero(CONTROLLER)


class TOY_814:
    """Bucket of Soldiers"""

    deathrattle = TOY_814_Bucket(CONTROLLER)


class TOY_820:
    """Forgotten Animatronic"""

    events = OWN_TURN_END.on(TOY_820_Animatronic(SELF))


class TOY_866:
    """Corridor Sleeper"""

    tags = {GameTag.DORMANT: True}
    progress_total = 7
    dormant_events = Death(MINION).on(AddProgress(SELF, Death.ENTITY))
    reward = Awaken(SELF)


class TOY_878:
    """Cosplay Contestant"""

    events = Play(OPPONENT, MINION).after(TOY_878_Cosplay(Play.CARD))


class TOY_891:
    """Workshop Janitor"""

    play = TOY_891_WorkshopJanitor(CONTROLLER)


class TOY_893:
    """Nesting Golem"""

    deathrattle = TOY_893_NestingGolem(SELF)


class TOY_894:
    """Origami Frog"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TOY_894_SwapAttack(TARGET)


class TOY_895:
    """Origami Crane"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TOY_895_SwapHealth(TARGET)


class TOY_896:
    """Origami Dragon"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = TOY_896_SwapStats(TARGET)


class TOY_897:
    """Floppy Hydra"""

    deathrattle = TOY_897_FloppyHydra(SELF)


class TOY_943:
    """Rumble Enthusiast"""

    events = Play(CONTROLLER, PLAY_LEFT_MOST | PLAY_RIGHT_MOST).after(
        Hit(RANDOM_ENEMY_CHARACTER, 1)
    )


class TOY_960:
    """Joymancer Jepetto"""

    play = TOY_960_Joymancer(CONTROLLER)


##
# Buffs


MIS_026e = buff()
TOY_340e = buff(+2, +2)
TOY_386e = buff()
TOY_390e = buff(cost=-1)
TOY_391e = buff()
TOY_518e = buff(atk=1)
TOY_878e = buff()
TOY_894e = buff()
TOY_895e = buff()
TOY_896e = buff()


@custom_card
class TOY_893e:
    tags = {
        GameTag.CARDNAME: "Nested",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }


@custom_card
class TOY_897e:
    tags = {
        GameTag.CARDNAME: "Floppy",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
