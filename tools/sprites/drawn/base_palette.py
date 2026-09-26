"""The player base's palette — the base sprites' own colours (tools/_generated/player/bases/), cleaned into
light-to-dark ramps. One letter per colour so the base can be written and edited as a text grid.

Ramps run outline (darkest) -> highlight. Hue shifts: shadows lean red/purple, highlights lean yellow.
"""

def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

PAL = {
    ".": None,                                   # transparent
    # hair (auburn): outline, dark, mid-dark, mid, light, highlight
    "1": _hex("3a0a08"), "2": _hex("62140a"), "3": _hex("8a220c"),
    "4": _hex("ad3812"), "5": _hex("cf5418"), "6": _hex("e8782c"),
    # skin (orange tan): outline, shadow, mid-shadow, base, light, highlight
    "a": _hex("9c3110"), "b": _hex("d05a20"), "c": _hex("ec7d34"),
    "d": _hex("fb9a45"), "e": _hex("ffb456"), "f": _hex("ffc972"),
    # tank top (cream): outline, deep shadow, shadow, base, light
    "T": _hex("7c5a52"), "U": _hex("b9977e"), "V": _hex("e3cba0"),
    "W": _hex("f6e6bc"), "X": _hex("fff6d4"),
    # shorts (khaki): outline, shadow, mid, base, light
    "K": _hex("8a6440"), "L": _hex("c89a5e"), "M": _hex("dfb97a"),
    "N": _hex("efcd8c"), "P": _hex("fbdda0"),
    # face
    "@": _hex("1c0e14"),                         # pupil
    "w": _hex("fff8e8"),                         # eye white / catchlight
    "m": _hex("8e2e22"),                         # mouth
    "z": _hex("ff8a5c"),                         # blush
}

RAMPS = {
    "hair": "123456", "skin": "abcdef", "top": "TUVWX", "shorts": "KLMNP", "face": "@wmz",
}
