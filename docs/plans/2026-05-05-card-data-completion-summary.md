# Card Data Completion Summary

Date: 2026-05-05
Branch: `phase4-hero-cards`

## Scope

This branch continued the expansion-by-expansion card data implementation pass, with an emphasis on removing simplified behavior from implemented card scripts and covering the high-risk interactions with focused tests.

## Expansion Progress

### Emerald Dream

- Completed class implementations for Hunter, Mage, Paladin, Priest, Rogue, Shaman, Warrior, and Warlock.
- Stabilized random spell targeting behavior used by the expansion tests.
- Addressed self-review findings in the expansion follow-up commit.

Representative commits:

- `ae57e9e feat(emerald-dream): complete hunter cards`
- `93320b7 fix(emerald-dream): address self review findings`

### Lost City

- Completed class cards for Warrior, Death Knight, Demon Hunter, Druid, Hunter, Mage, Paladin, Priest, Rogue, Shaman, and Warlock.
- Completed neutral cards across the initial, utility, battlecry/deathrattle, and legendary batches.
- Addressed neutral review findings and declared the Ultragigasaur script.

Representative commits:

- `1b0200b feat(lost-city): complete warrior cards`
- `590f987 feat(lost-city): finish neutral legendary cards`
- `5b216a3 fix(lost-city): address neutral review findings`
- `91997d2 chore(lost-city): declare ultragigasaur script`

### Titans

- Modeled the remaining Titan/keeper-style ability behavior that had been simplified or incomplete.
- Covered Norgannon ability scaling, Yogg-Saron induced attacks, Sargeras portal scoping, Amitus damage capping, Argus positional aura behavior, V-07-TR-0N Prime repeated abilities, and Aman'Thul/Primus ability completion.

Verification run:

```bash
pytest tests/test_titans.py tests/test_miniaturize_titan.py -q --tb=short --show-capture=no
```

Result: 30 passed, 6 warnings.

Representative commits:

- `128cd0d fix(titans): model aggramar weapon abilities`
- `1d8cceb fix(titans): implement yogg induce insanity attacks`
- `8094aef fix(titans): model argus positional aura`
- `501b979 fix(titans): complete amanthul and primus abilities`

### Whizbang

- Adjusted Window Shopper's discovered Demon behavior.
- Added focused coverage for Chia Drake and Shudderblock semantics.

Verification run:

```bash
pytest tests/test_whizbangs_remaining.py -q --tb=short --show-capture=no
```

Result: 24 passed, 6 warnings.

Representative commits:

- `53e8b94 fix(whizbang): adjust window shopper discovered demon`
- `87ab229 test(whizbang): cover chia drake and shudderblock semantics`

### Time Travel

- Implemented the remaining future and location mechanics in the Time Travel test set.

Verification run:

```bash
pytest tests/test_timetravel.py -q --tb=short --show-capture=no
```

Result: 26 passed, 6 warnings.

Representative commit:

- `6af0014 fix(timetravel): implement future and location mechanics`

### Mean Streets of Gadgetzan

- Replaced Doppelgangster's simplified same-ID exact copies with the three real card-data variants: `CFM_668`, `CFM_668t`, and `CFM_668t2`.
- Preserved Shudderwock's replay behavior so replayed Doppelgangster battlecries still copy Shudderwock itself.
- Fixed Kazakus custom potion requirement merging for Python 3.8 compatibility by replacing the `dict | dict` operator with `copy()` plus `update()`.

Verification runs:

```bash
pytest tests/test_gangs.py -q --tb=short --show-capture=no
pytest tests/test_misc.py::test_doppelgangster_and_shudderwock -q --tb=short --show-capture=no
```

Results:

- `tests/test_gangs.py`: 21 passed, 6 warnings.
- `test_doppelgangster_and_shudderwock`: 1 passed, 6 warnings.

Representative commit:

- `5c51625 fix(gangs): summon doppelgangster token variants`

## Completion Checks

Implementation marker scan:

```bash
rg -n "TODO|simplified|not implemented|unimplemented" fireplace/cards --glob '!unimplemented/**'
```

Result: no output.

Known residual test risk:

- `tests/test_misc.py::test_event_queue_summon` currently fails when run alone with `len(game.player2.field) == 0` instead of `1`. This is outside the Gangs/Doppelgangster changes and was left unmodified.
- A combined run of `tests/test_gangs.py tests/test_misc.py::test_doppelgangster_and_shudderwock` once showed a non-reproducible `test_jade_blossom` state mismatch; `tests/test_gangs.py` and `tests/test_gangs.py::test_jade_blossom` both passed in fresh runs.

## Review Tracking

Self-review subagent tasks were opened after the completed expansion batches:

- Titans review: Arendt.
- Whizbang review: Anscombe.
- Time Travel review: Turing.
- Gangs review: Maxwell.

