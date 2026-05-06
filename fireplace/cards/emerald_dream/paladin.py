# Paladin cards from EMERALD_DREAM expansion
from ..utils import *


def _edr_started_in_deck(card):
    return card in getattr(card.controller, "starting_deck", [])


def _edr_deck_cards_not_started(player):
    return [card for card in player.deck if not _edr_started_in_deck(card)]


class EDR_251_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        started = [
            card
            for card in player.deck
            if card.type == CardType.SPELL and _edr_started_in_deck(card)
        ]
        generated = [
            card
            for card in player.deck
            if card.type == CardType.SPELL and not _edr_started_in_deck(card)
        ]
        actions = []
        if started:
            actions.append(ForceDraw(source.game.random.choice(started)))
        if generated:
            actions.append(ForceDraw(source.game.random.choice(generated)))
        return source.game.queue_actions(source, actions)


class EDR_252_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        buff = "EDR_252e1" if target.controller == source.controller else "EDR_252e"
        source.buff(target, buff)
        target.damage = 0
        source.game.manager.targeted_action(self, source, target)


class EDR_255_HitLowestEnemy(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        enemies = [card for card in player.opponent.characters if not card.dead]
        if not enemies:
            return
        lowest_health = min(card.health for card in enemies)
        candidates = [card for card in enemies if card.health == lowest_health]
        target = source.game.random.choice(candidates)
        return source.game.queue_actions(source, [Hit(target, 5)])


class EDR_256_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        generated = _edr_deck_cards_not_started(source.controller)
        if not generated:
            return
        drawn = source.game.random.choice(generated)
        return source.game.queue_actions(
            source, [ForceDraw(drawn), Buff(card, "EDR_256e")]
        )


class EDR_257_BuffSelf(TargetedAction):
    TARGET = ActionArg()
    BUFF = ActionArg()

    def do(self, source, player, buff):
        minion = source if source.zone == Zone.PLAY else source.parent_card
        actions = [Buff(minion, buff)]
        if buff == "EDR_257ae":
            actions.append(GiveDivineShield(minion))
        elif buff == "EDR_257be":
            actions.append(GiveLifesteal(minion))
        return source.game.queue_actions(source, actions)


class EDR_258_ReapplyDivineShield(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        hits = getattr(target, "_edr_258_divine_shield_hits", 0) + 1
        target._edr_258_divine_shield_hits = hits
        if hits < 3:
            return source.game.queue_actions(source, [GiveDivineShield(target)])
        target._edr_258_divine_shield_hits = 0


class EDR_259_CreateAura(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spells = [card for card in player.hand if card.type == CardType.SPELL]
        if not spells:
            return
        highest_cost = max(card.cost for card in spells)
        candidates = [card for card in spells if card.cost == highest_cost]
        spell = source.game.random.choice(candidates)
        spell.zone = Zone.SETASIDE
        return source.game.queue_actions(
            source, [Buff(player, "EDR_259e1", _edr_259_spell_id=spell.id)]
        )


class EDR_259e1_Cast(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        spell_id = getattr(source, "_edr_259_spell_id", None)
        if not spell_id:
            return
        spell = player.card(spell_id, source=source)
        return source.game.queue_actions(source, [CastSpell(spell)])


class EDR_259e1_Tick(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, aura):
        remaining = getattr(aura, "_edr_259_turns_remaining", 3) - 1
        aura._edr_259_turns_remaining = remaining
        if remaining <= 0:
            aura._edr_259_expired = True


class EDR_259e1_DestroyExpired(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, aura):
        if getattr(aura, "_edr_259_expired", False):
            aura.remove()
            source.game.manager.targeted_action(self, source, aura)


class EDR_445_Imbue(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        if player.hero.power.id != "EDR_445p":
            player.hero.power.zone = Zone.SETASIDE
            power = player.card("EDR_445p", source=source)
            power._edr_445_amount = 0
            source.game.queue_actions(source, [Summon(player, power)])
        player.hero.power._edr_445_amount = getattr(
            player.hero.power, "_edr_445_amount", 0
        ) + 1
        source.game.manager.targeted_action(self, source, player)


class EDR_264_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minion = RandomMinion(cost=2).evaluate(source)
        actions = []
        if minion:
            actions.append(Summon(player, minion).then(Taunt(Summon.CARD)))
        actions.append(EDR_445_Imbue(player))
        return source.game.queue_actions(source, actions)


class EDR_445p_ShufflePortals(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = getattr(source, "_edr_445_amount", 1)
        portals = []
        for _ in range(2):
            portal = player.card("EDR_445pt3", source=source)
            portal._edr_445_amount = amount
            portals.append(portal)
        return source.game.queue_actions(source, [Shuffle(player, portals)])


class EDR_445pt3_SummonDragon(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        amount = getattr(source, "_edr_445_amount", 1)
        dragon = RandomDragon(cost=amount).evaluate(source)
        if dragon:
            return source.game.queue_actions(source, [Summon(player, dragon)])


class FIR_914_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, target):
        amount = getattr(source, "_fir_914_amount", 1)
        return source.game.queue_actions(
            source, [Buff(target, "FIR_914e", amount=amount)]
        )


class FIR_914_Upgrade(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        amount = getattr(card, "_fir_914_amount", 1) + 1
        card._fir_914_amount = amount
        if amount >= 3:
            return source.game.queue_actions(source, [Discard(card)])


class FIR_941_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, player):
        minions = [card for card in player.deck if card.type == CardType.MINION]
        if not minions:
            return
        drawn = source.game.random.choice(minions)
        copy = ExactCopy(TARGET).copy(source, drawn)
        return source.game.queue_actions(
            source,
            [
                ForceDraw(drawn),
                Summon(player, copy).then(
                    Buff(Summon.CARD, "FIR_941e1"),
                    GiveDivineShield(Summon.CARD),
                ),
            ],
        )


class FIR_961_Play(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, card):
        holding_expensive_spell = any(
            hand_card.type == CardType.SPELL and hand_card.cost >= 5
            for hand_card in source.controller.hand
        )
        if holding_expensive_spell:
            return source.game.queue_actions(
                source, [GiveDivineShield(card), GiveLifesteal(card)]
            )


##
# Minions


class EDR_251:
    """Dragonscale Armaments"""

    play = EDR_251_Play(CONTROLLER)


class EDR_253:
    """Ursine Maul"""

    events = Attack(FRIENDLY_HERO).after(Draw(CONTROLLER))


class EDR_256:
    """Dreamwarden"""

    taunt = True
    play = EDR_256_Play(SELF)


class EDR_257:
    """Lightmender"""

    play = Choice(CONTROLLER, ["EDR_257a", "EDR_257b"]).then(Battlecry(Choice.CARD, None))


class EDR_257a:
    """Holy Bond"""

    play = EDR_257_BuffSelf(CONTROLLER, "EDR_257ae")


class EDR_257ae:
    """Holy Bonded"""

    tags = {GameTag.ATK: 3}


class EDR_257b:
    """Embrace of the Light"""

    play = EDR_257_BuffSelf(CONTROLLER, "EDR_257be")


class EDR_257be:
    """Light's Embrace"""

    tags = {GameTag.HEALTH: 3}


class EDR_258:
    """Toreth the Unbreaking"""

    divine_shield = True
    taunt = True
    events = LosesDivineShield(FRIENDLY_MINIONS).after(
        EDR_258_ReapplyDivineShield(LosesDivineShield.TARGET)
    )


class EDR_259:
    """Ursol"""

    taunt = True
    play = EDR_259_CreateAura(CONTROLLER)


class EDR_259e1:
    """Ursol's Aura"""

    tags = {
        GameTag.CARDNAME: "Ursol's Aura",
        GameTag.CARDTYPE: CardType.ENCHANTMENT,
    }
    events = [
        OWN_TURN_END.on(EDR_259e1_Cast(CONTROLLER)),
        OWN_TURN_END.on(EDR_259e1_Tick(SELF)),
        OWN_TURN_BEGIN.on(EDR_259e1_DestroyExpired(SELF)),
    ]


class EDR_451:
    """Goldpetal Drake"""

    play = EDR_445_Imbue(CONTROLLER)
    deathrattle = EDR_445_Imbue(CONTROLLER)


class EDR_256e:
    """Portalmancy"""

    tags = {GameTag.ATK: 2, GameTag.HEALTH: 2}


##
# Spells


class EDR_252:
    """Mark of Ursol"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = EDR_252_Play(TARGET)


class EDR_252e:
    """Mark of Ursol"""

    atk = SET(1)
    max_health = SET(1)


class EDR_252e1:
    """Might of Ursol"""

    atk = SET(3)
    max_health = SET(3)


class EDR_255:
    """Renewing Flames"""

    lifesteal = True
    play = EDR_255_HitLowestEnemy(CONTROLLER) * 2


class EDR_264:
    """Aegis of Light"""

    play = EDR_264_Play(CONTROLLER)


class EDR_445p:
    """Blessing of the Dragon"""

    activate = EDR_445p_ShufflePortals(CONTROLLER)


class EDR_445pt3:
    """Emerald Portal"""

    play = EDR_445pt3_SummonDragon(CONTROLLER)
    draw = CAST_WHEN_DRAWN


class FIR_914:
    """Smoldering Strength"""

    requirements = {
        PlayReq.REQ_TARGET_TO_PLAY: 0,
        PlayReq.REQ_FRIENDLY_TARGET: 0,
        PlayReq.REQ_MINION_TARGET: 0,
    }
    play = FIR_914_Play(TARGET)

    class Hand:
        events = OWN_TURN_BEGIN.on(FIR_914_Upgrade(SELF))


class FIR_914e:
    """Smoldering Strength"""

    atk = lambda self, i: i + self.amount
    max_health = lambda self, i: i + self.amount


class FIR_941:
    """Searing Reflection"""

    play = FIR_941_Play(CONTROLLER)


class FIR_941e1:
    """Searing Reflection"""

    atk = SET(8)
    max_health = SET(8)


class FIR_961:
    """Ashleaf Pixie"""

    play = FIR_961_Play(SELF)


##
# Minion Tokens


class EDR_271_GiveSpell(TargetedAction):
    TARGET = ActionArg()

    def do(self, source, treant):
        spell_id = getattr(treant, "_edr_271_spell_id", None)
        if spell_id:
            return source.game.queue_actions(source, [Give(treant.controller, spell_id)])


class EDR_271t:
    """Treant of Life"""

    deathrattle = EDR_271_GiveSpell(SELF)


class EDR_272:
    """Evergreen Stag"""

    elusive = True
    lifesteal = True
    taunt = True
