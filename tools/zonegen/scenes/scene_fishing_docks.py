#!/usr/bin/env python3
"""Scene — FISHING HAMLET (the Bee Meadow's SW cove): two full-home cottages drowsing above the
water, a plank DOCK running south over the cove with mooring posts, a lantern and moored boats,
and working-shore clutter — fish crates in a row, barrels, drying nets' worth of driftwood and
reeds. No NPC yet: fishing is a future slice (the village fisherman already says so).

`place_fishing_hamlet(b, ox, oy)` is the composable piece (the place_boat_store pattern): cottages
on the grass at/above oy, the dock walking SOUTH (y decreasing) from oy into whatever water the
caller laid. Renders to tools/_generated/previews/zones/bee_meadow_20/scenes/fishing_docks.png.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                        # noqa: E402
from features.terrain import lake, path                    # noqa: E402
from scene_cottage import place_cottage, place_cottage_north  # noqa: E402


def _water_put(b, oid, x, y, **k):
    """Stand an object in the water (un-reserve its footprint first) — the dock-furniture idiom."""
    fw, fh = b.footprint(oid)
    if not all(b.in_bounds(x + dx, y + dy) for dx in range(fw) for dy in range(fh)):
        return False
    for dx in range(fw):
        for dy in range(fh):
            b.reserved[y + dy][x + dx] = False
    return b.place_occupant(oid, x, y, surface="water", **k)


def _dock(b, x0, oy, max_len=14, direction=-1):
    """A 2-wide plank dock from oy walking into the water (direction -1 = south/y-decreasing,
    +1 = north/y-increasing). Decks EVERY cell to the last water cell — land cells become a
    BOARDWALK ramp, so the pier always connects visually to the shore instead of floating
    detached when the waterline wanders. Refuses to build at all if there's no water within
    max_len (returns None). Mooring posts every 3, a lantern midway, a boat at the far end."""
    span = range(oy, oy + direction * max_len, direction)
    water_ys = [y for y in span
                if b.in_bounds(x0, y) and (b.surface[y][x0] == "water" or
                                           b.surface[y][x0 + 1] == "water")]
    if not water_ys:
        return None
    end = min(water_ys) if direction < 0 else max(water_ys)
    for y in range(oy, end + direction, direction):
        for x in (x0, x0 + 1):
            if not b.in_bounds(x, y):
                continue
            if b.surface[y][x] == "water" or b.is_free(x, y):
                b.set_ground(x, y, "bridge_wood", surface="path")
                b.reserved[y][x] = False
    for y in range(oy + 2 * direction, end - direction, 3 * direction):
        _water_put(b, "mooring_post", x0 - 1, y)
        _water_put(b, "mooring_post", x0 + 2, y)
    _water_put(b, "lantern", x0 + 2, (oy + end) // 2)
    _water_put(b, "boat", x0 - 1, end)
    return end


def place_fishing_hamlet(b, ox, n_shore_y, s_shore_y):
    """The SPLIT-SHORE hamlet: the open-to-the-sea inlet runs between two shores with one
    home on EACH — the north cottage opens SOUTH onto its quay, the south cottage opens
    NORTH onto its own (doors face the WATER, not compass south). A dock off each shore, a
    plank footbridge over the east narrows, the catch and gear split between the quays.
    `n_shore_y` = the north shore row (water just south of it); `s_shore_y` = the south
    shore row (water just north of it). The caller supplies the inlet water."""
    from features.terrain import bridge

    # PRECEDENCE: quay paths first (door columns are deterministic: south-door plan ox+10,
    # north-door plan ox+4).
    path(b, (ox + 11, n_shore_y + 4), (ox + 19, n_shore_y + 1), width=1, tile="dirt",
         wobble=0.05, seed=ox + 1)
    path(b, (ox + 9, s_shore_y - 3), (ox + 12, s_shore_y - 1), width=1, tile="dirt",
         wobble=0.05, seed=ox + 2)

    # NORTH shore: the fisher's cottage (south door → the water) + the main dock. Dock
    # lengths stop MID-water — a pier that reaches the far shore is a bridge, not a dock.
    place_cottage(b, ox, n_shore_y + 8, npc="fisher_down", yard_style="small_plot")
    _dock(b, ox + 18, n_shore_y, max_len=6, direction=-1)

    # SOUTH shore: the second home opens NORTH onto the inlet (the north-door plan) + its dock.
    place_cottage_north(b, ox + 1, s_shore_y - 13, npc="farmer_down")
    _dock(b, ox + 11, s_shore_y, max_len=5, direction=+1)

    # The FOOTBRIDGE over the east narrows — the two shores are one hamlet, not neighbors
    # across a moat.
    bridge(b, (ox + 26, s_shore_y), (ox + 26, n_shore_y))

    # NORTH QUAY (the working side): the catch crated in a row, a heaped net, barrels, light.
    for i in range(3):
        if b.is_free(ox + 14 + i, n_shore_y + 1):
            b.place_occupant("fish_crate", ox + 14 + i, n_shore_y + 1)
    for x, y in [(ox + 21, n_shore_y + 2), (ox + 12, n_shore_y + 1)]:
        if b.is_free(x, y):
            b.place_occupant("net_pile", x, y)
    if b.is_free(ox + 22, n_shore_y + 3):
        b.place_occupant("barrel", ox + 22, n_shore_y + 3)
    for lx, ly in [(ox + 16, n_shore_y + 3), (ox + 13, n_shore_y + 3), (ox + 16, n_shore_y + 5)]:
        if b.is_free(lx, ly) and b.surface[ly][lx] == "grass":
            b.place_occupant("lamp_post", lx, ly)  # beside the quay path, never ON it
            break
    if b.is_free(ox + 24, n_shore_y + 2):
        b.place_occupant("campfire", ox + 24, n_shore_y + 2)

    # SOUTH QUAY (the drying side — it gets the sun): rack row + the lobster pots.
    for i in range(2):
        if b.is_free(ox + 15 + i * 3, s_shore_y - 1) and b.is_free(ox + 16 + i * 3, s_shore_y - 1):
            b.place_occupant("drying_rack_fish", ox + 15 + i * 3, s_shore_y - 1)
    for i in range(3):
        if b.is_free(ox + 21 + i, s_shore_y - 2):
            b.place_occupant("lobster_pot", ox + 21 + i, s_shore_y - 2)
    if b.is_free(ox + 19, s_shore_y - 2):
        b.place_occupant("barrel", ox + 19, s_shore_y - 2)
    if b.is_free(ox + 25, s_shore_y - 3):
        b.place_occupant("seashell_pile", ox + 25, s_shore_y - 3)

    # Lived-in: laundry strung BESIDE the south home (east side, catching the sea wind),
    # driftwood the tide left.
    for lx in range(ox + 17, ox + 24):
        if b.is_free(lx, s_shore_y - 9) and b.is_free(lx + 1, s_shore_y - 9):
            b.place_occupant("laundry_line", lx, s_shore_y - 9)
            break
    if b.is_free(ox + 8, n_shore_y + 1):
        b.place_occupant("driftwood", ox + 8, n_shore_y + 1)

    # THE DOMESTIC LAYER (settlements research §3: every home answers "how does this
    # household eat?", and the props sit BETWEEN the door and the work source).
    # North household (the fisher): firewood work — log pile + chopping stump on the
    # inland side of the cottage, where the wood comes FROM.
    for wx, wy in [(ox - 2, n_shore_y + 10), (ox - 1, n_shore_y + 12), (ox + 21, n_shore_y + 9)]:
        if b.in_bounds(wx, wy) and b.is_free(wx, wy) and b.surface[wy][wx] == "grass" \
           and b.in_bounds(wx + 1, wy) and b.is_free(wx + 1, wy):
            b.place_occupant("log_pile", wx, wy)
            if b.is_free(wx + 1, wy + 1) and b.surface[wy + 1][wx + 1] == "grass":
                b.place_occupant("stump", wx + 1, wy + 1)
            break
    # South household: the kitchen garden — berry ROWS beside the house's east wall
    # (planted, not wild; below the laundry so the yard reads as one worked strip).
    # Anchored INSIDE the house's rows so it can't fall off a small scene canvas
    # (the first version sat at s_shore_y-15 = off-grid here and vanished silently).
    for i in range(4):
        gx = ox + 19 + (i % 2) * 2
        gyy = s_shore_y - 11 - (i // 2) * 2
        if b.in_bounds(gx, gyy) and b.is_free(gx, gyy) and b.surface[gyy][gx] == "grass":
            b.place_occupant("wild_berry_bush", gx, gyy)
    for wx, wy in [(ox + 16, s_shore_y - 5), (ox + 18, s_shore_y - 6), (ox + 15, s_shore_y - 7)]:
        if b.in_bounds(wx, wy) and b.is_free(wx, wy) and b.surface[wy][wx] == "grass" \
           and all(b.is_free(wx + qx, wy + qy) for qx in (0, 1) for qy in (0, 1)
                   if b.in_bounds(wx + qx, wy + qy)):
            b.place_occupant("well", wx, wy)
            break
    # The COMMONS made sittable (settlements §2: fire + seats = the hamlet's evening):
    # two log seats pulled up to the campfire on the north quay.
    for sx, sy in [(ox + 23, n_shore_y + 3), (ox + 25, n_shore_y + 1), (ox + 23, n_shore_y + 1)]:
        if b.in_bounds(sx, sy) and b.is_free(sx, sy) and b.surface[sy][sx] == "grass":
            b.place_occupant("log_seat", sx, sy)
    # Shore lanes: each quay's worn trace continues to the footbridge foot — the two
    # shores are one hamlet's street, not two dead ends. Painted cell-by-cell on FREE
    # grass only, weaving around the gear (a real footpath dodges the crates; a ruled
    # path() through a prop row just threads them).
    for y_base, step in ((n_shore_y + 1, 1), (s_shore_y - 1, -1)):
        for x in range(ox + 13, ox + 26):
            for yy in (y_base, y_base + step):
                if b.in_bounds(x, yy) and b.surface[yy][x] == "grass" \
                   and b.ground[yy][x] == "grass" and b.is_free(x, yy):
                    b.set_ground(x, yy, "dirt")
                    break

    # LIVING DRESSING (render-only): dragonflies hawking over the inlet.
    b.place_bug("dragonfly", ox + 8.0, (n_shore_y + s_shore_y) / 2.0, scale=1.2)
    b.place_bug("dragonfly", ox + 30.0, (n_shore_y + s_shore_y) / 2.0 + 2, scale=1.0)

    # The inlet itself: lily pads in the calm shallows off the quays.
    rng = random.Random(n_shore_y * 7 + ox)
    placed_pads = 0
    for y in range(n_shore_y - 1, s_shore_y, -1):
        for x in range(ox + 2, ox + 32, 3):
            if placed_pads >= 4:
                break
            if b.in_bounds(x, y) and b.surface[y][x] == "water" \
               and b.ground[y][x] == "water_shallow" and rng.random() < 0.3:
                b.reserved[y][x] = False
                if b.place_occupant("lily_pad", x, y, surface="water"):
                    placed_pads += 1
                b.reserve(x, y, surface="water")
    return n_shore_y


PREVIEW = "zones/bee_meadow_20/scenes"
SCALE = 5


def build():
    b = ZoneBuilder("scene_fishing_docks", 52, 56, base_tile="grass", name="Fishing hamlet", biome="coast")
    # The INLET: an arm of the sea done the way water actually sits in land (the old
    # version was a sine PIPE — read as stacked rectangles). Coasts research §2: banks
    # are ASYMMETRIC (each gets its own noise), the MOUTH flares open at the sea end,
    # the head narrows and goes still (mud + reeds, §5: mud only where the energy stops).
    import math
    from features.terrain import _vnoise
    nb_n = _vnoise(91)   # north bank wander
    nb_s = _vnoise(92)   # south bank wander (independent — never a mirrored channel)
    for x in range(0, 41):
        cy = 22 + 2.2 * math.sin(x / 9.0 + 1.3) + (nb_n(x * 0.11, 3.0) - 0.5) * 3.0
        base = 5.0 * (1.0 - max(0, x - 28) / 18.0)          # narrowing toward the head
        base += max(0, 8 - x) * 0.45                        # the mouth FLARES at the sea
        h_n = base + (nb_n(x * 0.13, 0.0) - 0.5) * 3.2
        h_s = base + (nb_s(x * 0.13, 0.0) - 0.5) * 3.2
        if h_n + h_s < 2.0:                                 # the head pinches out
            break
        for y in range(int(cy - h_s - 2), int(cy + h_n + 3)):
            if not b.in_bounds(x, y):
                continue
            dy = y - cy
            inside = (-h_s <= dy <= h_n)
            if inside:
                depth = min(h_n - dy, dy + h_s)
                deep = depth > 1.8 and x < 32
                b.set_ground(x, y, "water_deep" if deep else "water_shallow", surface="water")
                b.reserve(x, y, surface="water")
            elif b.surface[y][x] == "grass" and (-h_s - 1.6 <= dy <= h_n + 1.6):
                b.set_ground(x, y, "sand")
    # The still HEAD: mud FLATS in the last shallows — three coherent banks, not a
    # per-cell checker — east of the footbridge line (x>=34; mud under the bridge
    # punched plank holes), reeds crowding the rims.
    rngh = random.Random(93)
    shallows = [(x, y) for y in range(14, 30) for x in range(34, 41)
                if b.in_bounds(x, y) and b.ground[y][x] == "water_shallow"]
    for _ in range(3):
        if not shallows:
            break
        sx, sy = shallows[rngh.randrange(len(shallows))]
        for (mx, my) in [(sx, sy), (sx + 1, sy), (sx, sy + 1), (sx - 1, sy), (sx, sy - 1),
                         (sx + 1, sy + 1)]:
            if b.in_bounds(mx, my) and b.ground[my][mx] == "water_shallow" \
               and rngh.random() < 0.8:
                b.set_ground(mx, my, "mud", surface="grass")
                b.reserved[my][mx] = False
                if (mx, my) in shallows:
                    shallows.remove((mx, my))
    for y in range(13, 31):
        for x in range(33, 42):
            if b.in_bounds(x, y) and b.ground[y][x] == "sand" and rngh.random() < 0.3:
                b.reserved[y][x] = False
                if b.is_free(x, y):
                    b.place_occupant("reeds", x, y)
    # East meadow floor — no screen of pure void beyond the head.
    for y in range(1, b.H - 1):
        for x in range(42, b.W - 1):
            if b.surface[y][x] == "grass" and b.is_free(x, y) and rngh.random() < 0.012:
                b.place_occupant(rngh.choice(["tall_grass", "flower_wild", "dandelion", "bush"]),
                                 x, y)
    place_fishing_hamlet(b, 6, 30, 14)
    b.spawn = [28, 34]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
