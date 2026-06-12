"""walk_candidates — THREE walk-cycle approaches for Andrew to pick from.

The shared base is the NEW true-profile side view (PROFILE_IDLE below):
narrow torso, one visible arm, overlapped legs, profile head with the eye at
the facing edge — replacing the old "narrowed front view" side sprite.

Candidates (all kill the vertical leg bob he disliked):
  A "stride"        hand-authored contacts: legs genuinely scissor fore/aft
                    in profile (light leg leads, then shading swaps); down
                    view alternates localized FOOT lifts (no head bob).
  B "bounce-lite"   A's keys + in-between frames -> 6-frame cycle at ~10fps.
  C "mechanical v2" pure transforms: leg half-COLUMN shifts (horizontal
                    stride read), boot-row-only lifts on down.

Run: python3 tools/player_sprites/walk_candidates.py
-> tools/_generated/previews/player/walk_candidates/{A,B,C}_{down,left}.gif
   + strips.png contact sheet
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from player_sprites import pixkit, body_frames  # noqa: E402
from player_sprites.palettes import CLASSES, SKIN_TONES  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, "..", "_generated", "previews",
                                    "player", "walk_candidates"))

# ---- the NEW true-profile side view (facing LEFT) -----------------------------
PROFILE_IDLE = """
................
.....oooooo.....
....oHHHHhho....
...oHHhhhhhho...
...oHhhhhhhho...
..oSShhhhhhho...
..oSSShhhhhho...
..oSeShhhhhho...
..osesshhhhgo...
..ozssshhhggo...
...ozsshhggo....
....ozsggo......
.....osso.......
....oTTTTTTo....
...oTttttttto...
...oTttttttuo...
...oSttttttuo...
...osttttttuo...
....otttttuo....
....ottttuuo....
....otttuuuo....
....ouuuuuuo....
....ovvvvvvo....
....oLllvvvo....
....oLllvvvo....
....olllvvvo....
....olllvvvo....
....ovllvvvo....
...oBbbbbvvo....
..oBbbbbbbvo....
..obbbbbbbbo....
..oooooooooo....
"""

# Candidate A, profile CONTACT pose: legs scissored fore/aft (front leg
# reaches left, back leg trails right; both feet point left).
A_LEFT_CONTACT_LEGS = """
....oLllvvvo....
...oLll.ovvo....
...oLlo..ovvo...
..oLlo...ovvo...
..oLlo...ovvo...
.oBbbo...ovvo...
.oBbbbo..ovvvo..
.obbbbo.obbbbo..
.ooooo..ooooo...
"""
A_LEG_ROW0 = 23  # the row A_LEFT_CONTACT_LEGS starts replacing


def _rows(grid):
    return pixkit.parse(grid)


def _replace_rows(base, repl_rows, row0):
    out = list(base)
    for i, r in enumerate(repl_rows):
        out[row0 + i] = r
    return out


def _swap_leg_shading(rows):
    """Alternate which leg LEADS by swapping the light/dark leg ramps."""
    table = str.maketrans({"L": "v", "l": "v", "v": "l"})
    out = []
    for y, r in enumerate(rows):
        out.append(r.translate(table) if y >= A_LEG_ROW0 else r)
    return out


def _shift_arm(rows, dx):
    """Shift the visible front arm (the S hand pixels + sleeve edge) by dx
    columns within the torso rows — a subtle pump."""
    out = list(rows)
    for y in (16, 17):
        r = list(out[y])
        # move the leading S/s one column
        for x in range(len(r)):
            if r[x] in "Ss":
                nx = max(1, min(14, x + dx))
                if r[nx] == "." or r[nx] in "tu":
                    r[x], r[nx] = ("t" if r[x] == "S" else "t"), r[x]
                break
        out[y] = "".join(r)
    return out


def _lift_boot_half(rows, half):
    """DOWN view: lift ONE boot 1px (boot rows only — a localized step, not
    the old whole-leg vertical bob). half: 'left'|'right'."""
    out = [list(r) for r in rows]
    w = len(rows[0])
    x0, x1 = (0, w // 2) if half == "left" else (w // 2, w)
    for y in range(29, 31 + 1):
        for x in range(x0, x1):
            out[y][x] = rows[y + 1][x] if y < 31 else "."
    return ["".join(r) for r in out]


def _shift_leg_columns(rows, front_dx, back_dx, row0=23, row1=31, split=8):
    """C: horizontal stride — shift the front-leg columns (x<split) and
    back-leg columns (x>=split) of the leg rows by dx each."""
    out = [list("." * len(rows[0])) for _ in rows]
    for y in range(len(rows)):
        if not (row0 <= y <= row1):
            out[y] = list(rows[y])
            continue
        for x, c in enumerate(rows[y]):
            if c == ".":
                continue
            dx = front_dx if x < split else back_dx
            nx = max(0, min(len(rows[0]) - 1, x + dx))
            out[y][nx] = c
    return ["".join(r) for r in out]


# ---- candidate frame builders (return {dir: [frames]}) -------------------------
def candidate_A():
    left = _rows(PROFILE_IDLE)
    contact = _replace_rows(left, _rows(A_LEFT_CONTACT_LEGS), A_LEG_ROW0)
    f0 = _shift_arm(contact, -1)
    f2 = _shift_arm(_swap_leg_shading(contact), +1)
    down = _rows(body_frames.DOWN_IDLE)
    d0 = _lift_boot_half(down, "right")
    d2 = _lift_boot_half(down, "left")
    return {"left": [f0, left, f2, left], "down": [d0, down, d2, down]}


def candidate_B():
    """A's keys + half-spread in-betweens -> 6 frames."""
    a = candidate_A()
    left = _rows(PROFILE_IDLE)
    half = _shift_leg_columns(left, -1, +1)          # half-spread in-between
    half_x = _swap_leg_shading(half)
    down = _rows(body_frames.DOWN_IDLE)
    return {
        "left": [a["left"][0], half, left, a["left"][2], half_x, left],
        "down": [a["down"][0], down, down, a["down"][2], down, down],
    }


def candidate_C():
    left = _rows(PROFILE_IDLE)
    f0 = _shift_leg_columns(left, -1, +1)
    f2 = _swap_leg_shading(_shift_leg_columns(left, 0, -1))
    down = _rows(body_frames.DOWN_IDLE)
    d0 = _lift_boot_half(down, "right")
    d2 = _lift_boot_half(down, "left")
    return {"left": [f0, left, f2, left], "down": [d0, down, d2, down]}


def main():
    hair, shirt, pants = CLASSES["farmer"][1], CLASSES["farmer"][2], CLASSES["farmer"][3]
    pal = pixkit.make_palette(skin=SKIN_TONES["default"], hair=hair,
                              shirt=shirt, pants=pants)
    cands = {"A": candidate_A(), "B": candidate_B(), "C": candidate_C()}
    strip_cells = []
    for name, dirs in cands.items():
        for d in ("left", "down"):
            frames = [pixkit.render(f, pal, mode="baked") for f in dirs[d]]
            ms = 100 if len(frames) == 6 else 140
            pixkit.walk_gif(frames, os.path.join(OUT, f"{name}_{d}.gif"),
                            scale=8, ms=ms)
            strip_cells += frames + ([None] * 0)
    # contact sheet: rows = candidate x dir
    flat = [c for c in strip_cells if c is not None]
    pixkit.save(pixkit.contact_sheet(flat, cols=6, scale=8),
                os.path.join(OUT, "strips.png"))
    print(f"candidates -> {OUT}")


if __name__ == "__main__":
    main()
