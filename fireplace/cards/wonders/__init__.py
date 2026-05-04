"""Wonders set — Whizbang's Workshop bonus pack.

Many WONDERS cards are direct re-prints of older cards (Whispers of the Old
Gods, Mean Streets of Gadgetzan, etc.) and reuse the same mechanics:
C'Thun (already supported via Player.cthun), Jade Golem, basic battlecries.

This package provides scripts for the simple/tractable WONDERS cards. Cards
that need new mechanics (Echo, Joust, Adapt, full Inspire chains, dormant
revive triggers) remain unimplemented.
"""
from .neutral import *
from .druid import *
from .hunter import *
from .mage import *
from .paladin import *
from .priest import *
from .rogue import *
from .shaman import *
from .warlock import *
from .warrior import *
