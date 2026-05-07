"""Tests for the keyword field on the catalog payload.

These tests exercise the contract laid out in
openspec/changes/card-keyword-detection/specs/card-keywords/spec.md:

- Every implemented collectible card has a `keywords: list[str]` field.
- The list values come from `GameTag` boolean tags, not from card text.
- The list is always present (never null) and never contains card names.
- Every value is one of the 13 canonical identifiers."""
import pytest


CANONICAL_KEYWORDS = {
    "TAUNT", "BATTLECRY", "DEATHRATTLE", "CHARGE", "RUSH",
    "DIVINE_SHIELD", "WINDFURY", "STEALTH", "POISONOUS",
    "LIFESTEAL", "SECRET", "SPELLPOWER", "COMBO", "COLOSSAL",
}


@pytest.fixture(scope="module")
def catalog_by_id():
    from webui.server.card_catalog import build_catalog
    cat = build_catalog()
    return {c["id"]: c for c in cat["cards"]}


# ---------------------------------------------------------------------------
# One canonical card per identifier — sourced from `build_catalog()` itself
# during scaffolding, so we know each id ships in the catalog and carries the
# tag in question. If the underlying XML changes such that any of these go
# missing, the test surfaces it loud and clear.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("card_id, keyword", [
    ("EX1_390", "TAUNT"),          # Tauren Warrior
    ("CS2_188", "BATTLECRY"),      # Abusive Sergeant
    ("FP1_007", "DEATHRATTLE"),    # Nerubian Egg
    ("CS2_124", "CHARGE"),         # Wolfrider
    ("BOT_020", "RUSH"),           # Skaterbot
    ("EX1_008", "DIVINE_SHIELD"),  # Argent Squire
    ("CFM_666", "WINDFURY"),       # Grook Fu Master
    ("EX1_010", "STEALTH"),        # Worgen Infiltrator
    ("BOT_035", "POISONOUS"),      # Venomizer
    ("BOT_050", "LIFESTEAL"),      # Rusty Recycler (also has TAUNT)
    ("EX1_287", "SECRET"),         # Counterspell
    ("CS2_142", "SPELLPOWER"),     # Kobold Geomancer
    ("CS2_073", "COMBO"),          # Cold Blood
    ("CATA_150", "COLOSSAL"),      # Ragnaros, the Great Fire
])
def test_card_carries_expected_keyword(catalog_by_id, card_id, keyword):
    card = catalog_by_id.get(card_id)
    assert card is not None, f"{card_id} missing from catalog"
    assert keyword in card["keywords"], (
        f"{card_id} ({card['name_en']}) expected to carry {keyword}, "
        f"got keywords={card['keywords']!r}"
    )


# ---------------------------------------------------------------------------
# Cards that should NOT have keywords — vanilla minions / pure-effect spells
# / aura-only minions / cards whose text mentions a keyword but whose tag is
# not set.
# ---------------------------------------------------------------------------

def test_vanilla_minion_has_empty_keywords(catalog_by_id):
    boulderfist = catalog_by_id.get("CS2_200")  # Boulderfist Ogre
    assert boulderfist is not None
    assert boulderfist["keywords"] == []


def test_aura_minion_does_not_register_as_keyword_card(catalog_by_id):
    """Stormwind Champion gives a +1/+1 aura — not a keyword in our list."""
    stormwind = catalog_by_id.get("CS2_222")
    assert stormwind is not None
    assert stormwind["keywords"] == []


def test_brann_text_mentions_battlecry_but_has_no_battlecry_tag(catalog_by_id):
    """Brann Bronzebeard's rules text contains '战吼' but he himself does NOT
    have the BATTLECRY tag — he doubles other Battlecries. This is the
    canonical false-positive that substring detection would have produced."""
    brann = catalog_by_id.get("LOE_077")
    assert brann is not None
    assert "战吼" in brann["text_zh"]
    assert "BATTLECRY" not in brann["keywords"]


# ---------------------------------------------------------------------------
# Mana Wyrm — explicitly the bug that motivated this change.
# ---------------------------------------------------------------------------

def test_mana_wyrm_has_no_keywords(catalog_by_id):
    mw = catalog_by_id.get("NEW1_012")
    assert mw is not None
    assert mw["keywords"] == []


def test_no_card_carries_card_name_as_keyword(catalog_by_id):
    """Belt-and-braces: no row anywhere claims '法力浮龙' / 'Mana Wyrm'."""
    for cid, card in catalog_by_id.items():
        kws = card["keywords"]
        assert "法力浮龙" not in kws, f"{cid} has card-name as keyword"
        assert "Mana Wyrm" not in kws, f"{cid} has card-name as keyword"
        assert "MANA_WYRM" not in kws, f"{cid} has card-name as keyword"


# ---------------------------------------------------------------------------
# Universal invariants across the entire catalog.
# ---------------------------------------------------------------------------

def test_every_card_has_keywords_list(catalog_by_id):
    """Field is always present, always a list, never null."""
    for cid, card in catalog_by_id.items():
        assert "keywords" in card, f"{cid} missing keywords field"
        assert isinstance(card["keywords"], list), f"{cid} keywords not a list"


def test_every_keyword_value_is_canonical(catalog_by_id):
    """No leakage of internal/cosmetic GameTag names into the catalog."""
    for cid, card in catalog_by_id.items():
        for kw in card["keywords"]:
            assert kw in CANONICAL_KEYWORDS, (
                f"{cid} ({card['name_en']}) has non-canonical keyword {kw!r}"
            )
