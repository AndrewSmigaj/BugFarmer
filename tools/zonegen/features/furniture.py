#!/usr/bin/env python3
"""Furniture COLLECTIONS — the authoring-side knowledge of "what to place", kept OUT of the
game's entity data (the game treats every placeable as an independent item; it does not know
or care that `sofa` and `sofa_fancy` are "the same thing, fancier").

A *collection* is a self-contained look/feel set: it maps a functional ROLE (the slot a room
template wants filled — a bed, some seating, a light) to a concrete entity id. A house picks a
collection; any role a collection doesn't define falls back to BASIC. Collections are modular —
add or remove one as a UNIT (a whole "tropical" / "modern" / "rustic" set), without touching the
templates or the game data. For now there are two: `basic` (plain, cheap) and `fancy` (upscale).

To add a collection later: define a new role->id dict (ideally in its own module) and register it
in COLLECTIONS. It only needs to list the roles where it differs from BASIC.
"""

# Plain / starter look. Defines EVERY role (the fallback floor for all collections).
BASIC = {
    # sleeping / bedroom
    "bed":        "bed_basic",
    "nightstand": "nightstand",
    "dresser":    "dresser",
    # seating
    "seating":    "chair_wood",      # a single dining/desk chair
    "stool":      "stool_wood",
    "lounge":     "sofa",            # the main couch
    "armchair":   "armchair",
    # surfaces
    "table":      "table_wood",      # dining / main table (2x2)
    "coffee_table": "coffee_table",
    "desk":       "desk",
    # storage / shelving
    "bookshelf":  "bookshelf",
    "chest":      "chest_wood",
    "cupboard":   "cupboard",
    # lighting
    "light":      "lamp_floor",      # floor lamp
    "light_table": "lamp_table",
    # soft furnishings / decor
    "rug":        "rug",
    "plant":      "potted_plant",
    "accent_small": "vase",
    "hearth":     "fireplace",
    "display":    "bug_terrarium",
    # kitchen
    "counter":    "counter",
    "sink":       "sink",
    "stove":      "stove_wood",
    "fridge":     "fridge",
    # roles with no plain version -> None means "skip it in a basic house"
    "clock":      None,
    "mirror":     None,
    "statue":     None,
}

# Upscale look. Only the roles that differ from BASIC; the rest fall back.
FANCY = {
    "bed":        "bed_fancy",
    "nightstand": "nightstand_fancy",
    "dresser":    "dresser_fancy",
    "seating":    "chair_fancy",
    "lounge":     "sofa_fancy",
    "armchair":   "armchair_fancy",
    "table":      "dining_table_fancy",
    "bookshelf":  "bookshelf_fancy",
    "chest":      "chest_iron",
    "light":      "lamp_floor_fancy",
    "light_table": "candelabra",
    "rug":        "rug_large",
    "plant":      "plant_large",
    "counter":    "counter_fancy",
    "stove":      "range_stove",
    "clock":      "grandfather_clock",
    "mirror":     "mirror_standing",
    "statue":     "statue_stone",
}

# The FLORAL set (the bee area — Maren's world; owner 2026-07-06 "a floral set for the
# bee area"). Only roles that differ from BASIC; footprints match role members.
FLORAL = {
    "bed":         "bed_floral",         # 2x4, matches bed_basic
    "seating":     "chair_floral",       # 1x1
    "table":       "table_floral",       # 2x2
    "dresser":     "dresser_floral",     # 2x1
    "light":       "lamp_floral",        # 1x1
    "rug":         "rug_floral",         # 2x2 flat
    "accent_small": "vase_floral",       # 1x1
    "bookshelf":   "bookshelf_floral",   # 2x1
}

# The STONE set (underground homes; owner: "a stone set underground (marble or
# something)"). Marble premium pieces (table_marble/bench_marble/bust_marble) exist as
# placeables for scene authors + a future "marble" collection; the stone set proper:
STONE = {
    "bed":         "bed_stone",          # 2x4
    "seating":     "stool_stone",        # 1x1
    "stool":       "stool_stone",        # 1x1
    "table":       "table_stone",        # 2x2
    "cupboard":    "cupboard_stone",     # 2x1
    "bookshelf":   "shelf_stone",        # 2x1
    "desk":        "desk_stone",         # 2x1
    "light":       "lamp_crystal",       # 1x1
    "statue":      "statue_stone",       # 1x1
    "chest":       "chest_mossy",        # underground flavor of the chest role
}

COLLECTIONS = {"basic": BASIC, "fancy": FANCY, "floral": FLORAL, "stone": STONE}


def pick(role, collection="basic"):
    """Resolve a role to a concrete entity id for the given collection. Falls back to BASIC
    for any role the collection doesn't define; returns None if the role is intentionally
    empty in this collection (the template should then skip it)."""
    c = COLLECTIONS.get(collection, BASIC)
    if role in c:
        return c[role]
    return BASIC.get(role)
