# <img src="/logo.png" height="32" width="32"/> Fireplace
[![](https://img.shields.io/badge/python-3.10+-blue.svg)](https://peps.python.org/pep-0619/)
[![](https://img.shields.io/github/license/jleclanche/fireplace.svg)](https://github.com/jleclanche/fireplace/blob/master/LICENSE.md)
[![](https://github.com/jleclanche/fireplace/actions/workflows/build.yml/badge.svg)](https://github.com/jleclanche/fireplace/actions/workflows/build.yml)
[![codecov](https://codecov.io/github/jleclanche/fireplace/graph/badge.svg?token=FXDTJSKZL9)](https://codecov.io/github/jleclanche/fireplace)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Hearthstone simulator and implementation, written in Python.


## Cards Implementation

Now updated to [Patch 17.6.0.53261](https://hearthstone.wiki.gg/wiki/Patch_17.6.0.53261)
* **100%** Basic (153 of 153 cards)
* **100%** Classic (240 of 240 cards)
* **100%** Hall of Fame (35 of 35 cards)
* **100%** Curse of Naxxramas (30 of 30 cards)
* **100%** Goblins vs Gnomes (123 of 123 cards)
* **100%** Blackrock Mountain (31 of 31 cards)
* **100%** The Grand Tournament (132 of 132 cards)
* **100%** Hero Skins (33 of 33 cards)
* **100%** The League of Explorers (45 of 45 cards)
* **100%** Whispers of the Old Gods (134 of 134 cards)
* **100%** One Night in Karazhan (45 of 45 cards)
* **100%** Mean Streets of Gadgetzan (132 of 132 cards)
* **100%** Journey to Un'Goro (135 of 135 cards)
* **100%** Knights of the Frozen Throne (135 of 135 cards)
* **100%** Kobolds & Catacombs (135 of 135 cards)
* **100%** The Witchwood (129 of 129 cards)
* **100%** The Boomsday Project (136 of 136 cards)
* **100%** Rastakhan's Rumble (135 of 135 cards)
* **100%** Rise of Shadows (136 of 136 cards)
* **100%** Saviours of Uldum (135 of 135 cards)
* **100%** Descent of Dragons (140 of 140 cards)
* **100%** Galakrond's Awakening (35 of 35 cards)
* **100%** Ashes of Outlands (135 of 135 cards)
* **100%** Scholomance Academy (1 of 1 card)
* **100%** Demon Hunter Initiate (20 of 20 cards)

### The Shrouded City (In Progress)
* **10%** Warrior (2 of 20 cards implemented: DINO_400, DINO_401)

#### TODO
- [ ] Implement remaining 18 Warrior cards
  - [ ] DINO_433: Summon random (6), (4), and (2) cost Taunt minions
  - [ ] TLC_478: After hero attacks, deal 1 damage to all minions
  - [ ] TLC_600: Battlecry: Deal 5 damage, gain 5 armor. Finale: Cost (3) less
  - [ ] TLC_601: Spend up to 5 armor. Deal $1 damage to all minions per armor spent
  - [ ] TLC_602: Questline: Survive for 10 turns
  - [ ] TLC_602t: Battlecry: Get 2 random Quest rewards from Journey to Un'Goro
  - [ ] TLC_606: Battlecry: Deal 2 damage to an enemy minion. If it dies, gain 5 armor
  - [ ] TLC_620: Gain 3 armor. Deal damage to an enemy minion equal to your armor
  - [ ] TLC_622: Summon two 0/6 Guards with Taunt. Guards gain +1 attack when damaged
  - [ ] TLC_622e, TLC_622t: Related enchantments/tokens
  - [ ] TLC_623: End of turn: Give a random damaged friendly minion +2/+2
  - [ ] TLC_624: Battlecry: Summon copies of your damaged minions with Rush
  - [ ] TLC_632: Replace hero power with "Deal 8 damage to a random enemy" (2 uses)
- [ ] Implement LOCATION card type support
- [ ] Add tests for all implemented cards

## Requirements

* Python 3.10+


## Installation

> **Note**: This repository uses Git LFS (Large File Storage). Please install Git LFS before cloning: https://git-lfs.com

* `pip install .`
* download data: `aria2c -c -x 16 -s 16  https://raw.githubusercontent.com/HearthSim/hsdata/master/CardDefs.xml`

## Documentation

The [Fireplace Wiki](https://github.com/jleclanche/fireplace/wiki) is the best
source of documentation, along with the actual code.


## License

[![AGPLv3](https://www.gnu.org/graphics/agplv3-88x31.png)](http://choosealicense.com/licenses/agpl-3.0/)

Fireplace is licensed under the terms of the
[Affero GPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html) or any later version.


## Community

Fireplace is a [HearthSim](http://hearthsim.info/) project.
Join the community: <https://hearthsim.info/join/>
