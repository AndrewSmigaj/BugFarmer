"""The master palette: every hand-drawn sprite uses ONLY these colours.

Each material is a RAMP, darkest -> lightest. Ramps are hue-shifted the way pixel artists do it:
shadows lean cool (toward blue/purple), highlights lean warm (toward yellow), saturation peaks in the
middle. Light comes from the TOP-LEFT everywhere (style.json), so index 0 is "facing away from the
light" and the last index is "facing the light".

Why one shared palette: the old per-sprite k-means cleaner gave every sprite its own 20 colours, so the
431 object sprites used 8,226 distinct colours between them and nothing matched. One palette is the
single biggest thing that makes different sprites look like one game.
"""

# Outlines are a dark warm purple-brown, never pure black (matches the current art's rims).
OUTLINE = (34, 24, 32)
OUTLINE_SOFT = (58, 40, 46)

RAMPS = {
    # wood (planks, handles, chests, trunks)
    "wood":    [(58, 30, 34), (100, 52, 40), (150, 84, 50), (194, 122, 66), (228, 170, 100)],
    # bark: cooler, greyer than planks so trunks don't read as furniture
    "bark":    [(44, 32, 36), (72, 50, 46), (104, 72, 56), (138, 100, 70), (170, 132, 92)],
    # iron / steel fittings (cool)
    "iron":    [(40, 42, 58), (70, 76, 96), (110, 118, 138), (158, 168, 184), (212, 220, 228)],
    # copper (tools, bars)
    "copper":  [(72, 32, 36), (128, 58, 44), (184, 96, 58), (222, 142, 86), (246, 194, 138)],
    # brass / gold (locks, trims)
    "gold":    [(96, 60, 36), (166, 112, 44), (216, 168, 68), (246, 218, 124), (252, 244, 196)],
    # ground grass
    "grass":   [(34, 70, 54), (52, 100, 56), (78, 132, 60), (112, 162, 68), (158, 194, 86)],
    # tree leaves (deeper, cooler than ground grass so canopies separate from the lawn)
    "leaf":    [(26, 50, 50), (38, 82, 58), (62, 118, 60), (110, 162, 64), (184, 208, 92)],
    # dirt / soil
    "dirt":    [(70, 44, 40), (102, 68, 50), (136, 96, 64), (166, 126, 84), (194, 158, 112)],
    # stone / pebbles
    "stone":   [(56, 54, 66), (88, 86, 98), (128, 124, 132), (170, 166, 168), (208, 204, 198)],
    # skin (warm)
    "skin":    [(108, 56, 56), (170, 98, 80), (216, 144, 110), (242, 188, 150), (252, 222, 190)],
    # auburn hair (matches the approved base)
    "hair":    [(62, 28, 30), (108, 44, 34), (160, 70, 40), (204, 106, 56), (232, 152, 88)],
    # cloth: linen / undyed (the base's tank top + shorts)
    "linen":   [(122, 98, 84), (168, 144, 118), (208, 190, 158), (234, 222, 194), (250, 244, 226)],
    # cloth: blue (work clothes)
    "blue":    [(34, 38, 68), (52, 66, 106), (76, 102, 146), (116, 148, 182), (170, 196, 214)],
    # cloth: red
    "red":     [(80, 28, 42), (132, 46, 52), (184, 78, 62), (222, 124, 90), (246, 176, 136)],
    # honey / amber
    "honey":   [(112, 52, 32), (178, 92, 34), (226, 144, 44), (250, 196, 92), (254, 234, 170)],
    # beetle chitin: near-black with a cool sheen
    "chitin":  [(22, 18, 28), (38, 32, 48), (62, 56, 80), (98, 96, 126), (158, 162, 190)],
    # the burying beetle's orange bands
    "orange":  [(118, 44, 30), (180, 80, 34), (226, 124, 44), (248, 172, 80), (254, 214, 140)],
    # blossom pink + white
    "pink":    [(128, 54, 84), (186, 90, 124), (228, 140, 164), (248, 190, 204), (254, 232, 236)],
    # glass / glaze (jars)
    "glass":   [(64, 84, 108), (104, 136, 160), (156, 190, 206), (206, 228, 234), (244, 250, 250)],
    # UI parchment
    "parch":   [(112, 78, 58), (170, 132, 92), (212, 180, 130), (234, 210, 162), (248, 234, 198)],
    # heart red (UI) — shares the red family but punchier
    "heart":   [(74, 20, 36), (150, 32, 48), (212, 58, 60), (242, 110, 96), (254, 190, 170)],
    # the approved bronze armour (warm gold-bronze), for the modular armour test
    "bronze":  [(60, 34, 24), (112, 70, 34), (170, 116, 48), (218, 168, 72), (246, 218, 132)],
}

EXTRA = {
    "outline": OUTLINE,
    "outline_soft": OUTLINE_SOFT,
    "eye": (30, 24, 40),
    "white": (250, 250, 244),
    "mouth": (150, 72, 70),
    "outline_leaf": (20, 38, 40),
}


def ramp(name):
    return RAMPS[name]


def all_colours():
    """Every colour in the master palette (for the lint)."""
    cols = set(EXTRA.values())
    for r in RAMPS.values():
        cols.update(r)
    return cols
