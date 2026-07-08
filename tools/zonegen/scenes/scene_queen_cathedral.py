#!/usr/bin/env python3
"""Scene — THE QUEEN'S CATHEDRAL (ant_colony_40's showpiece; zone-craft crafted scene).

The colony's deep heart and the zone's SURPRISE (the doc's inversion): not a horror pit but the
most BEAUTIFUL room underground — a fungus-garden cathedral, softly glowing, ordered. The Queen
sits raised at the centre on a dirt-block throne-mound; a RING of royal-jelly piles around her;
glow-mushroom garden ARCS along the dome; stone-block floor COLUMNS (D22 — no ceilings, the blocks
form floor pillars); warrior guards posted; the Royal Vault gated on one flank. Deliberate,
near-symmetric composition — NOT scatter.

`place_queen_cathedral(b, cx, cy)` = the composable piece (the ZONE carves the dome; this places
the throne, gardens, columns, guards, vault). Standalone build() carves a dome for the preview.
Renders to previews/zones/ant_colony_40/scenes/.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                          # noqa: E402
from features.cave import carve_cavern                                       # noqa: E402

PREVIEW = "zones/ant_colony_40/scenes"
SCALE = 5


def _occ(b, oid, x, y, reserve=True):
    if b.in_bounds(x, y) and b.is_free(x, y):
        try:
            return b.place_occupant(oid, x, y, surface=None, reserve=reserve) or True
        except Exception:
            return False
    return False


def place_queen_cathedral(b, cx, cy, R=16):
    """A CRUCIFORM cathedral carved into the deep rock — the colony's showpiece. A processional NAVE
    runs from the north narthex down to the south APSE, where the Queen sits raised on a TIERED dais
    before a glowing crystal REREDOS; a receding COLONNADE of stone pillars frames the nave; the E/W
    TRANSEPTS are side chapels (W = cultivated glow-garden, E = the Royal Vault). Light is densest at
    the apse and along the aisle. Axis: HIGH-y = north entry, LOW-y = south (deep) apse. Caller has
    carved the cruciform dome; this places the architecture + court."""
    throne_y = cy - 9
    cross_y = cy + 4                              # the crossing = the E/W transept-lobe centres
    # --- 1. COLONNADE: paired stone pillars in receding rows framing the 11-wide nave -------------
    for ny in range(cy + 9, throne_y + 4, -3):
        for sx in (-5, 5):
            _occ(b, "stone_block", cx + sx, ny)
    # --- 2. APSE: a 3-tier dirt-block dais stepping UP (south) to the Queen's platform ------------
    for (dy, r) in [(3, 5), (2, 4), (1, 2)]:
        for dx in range(-r, r + 1):
            _occ(b, "dirt_block", cx + dx, throne_y + dy)
    b.place_bug("ant_queen", cx, throne_y, scale=5.0)
    # --- 3. REREDOS: the throne's glowing backdrop — crystal + glow between flanking pillars ------
    for dx in range(-4, 5):
        _occ(b, "crystal_small" if dx % 2 == 0 else "mushroom_glow", cx + dx, throne_y - 3, reserve=False)
    for dx in (-5, 5):
        _occ(b, "stone_block", cx + dx, throne_y - 3)
    # --- 4. TRANSEPT CHAPELS (E/W side lobes) off the crossing ------------------------------------
    wt, et = (cx - 13, cross_y), (cx + 13, cross_y)
    for (tx, ty) in (wt, et):                    # pillared "doorways" into each chapel
        for dy in (-3, 3):
            _occ(b, "stone_block", tx, ty + dy)
    for a in range(0, 360, 45):                  # W chapel: a cultivated glow-mushroom garden ring
        _occ(b, "mushroom_glow" if a % 90 else "mushroom_inkcap",
             wt[0] + int(round(4 * math.cos(math.radians(a)))),
             wt[1] + int(round(3 * math.sin(math.radians(a)))), reserve=False)
    _occ(b, "chest_iron", et[0] + 1, et[1])      # E chapel: the Royal Vault
    for a in range(0, 360, 72):                  # jelly stored in the vault chapel
        _occ(b, "royal_jelly_pile", et[0] + int(round(3 * math.cos(math.radians(a)))),
             et[1] + int(round(2 * math.sin(math.radians(a)))), reserve=False)
    # --- 5. THE COURT: jelly offerings at the dais foot, tended brood, guards ---------------------
    for dx in (-3, -1, 1, 3):                     # graded royal-jelly offering piles at the foot
        _occ(b, "royal_jelly_pile", cx + dx, throne_y + 4, reserve=False)
    for (bx, by) in [(cx - 4, throne_y + 5), (cx + 4, throne_y + 5)]:  # tended brood clutches
        _occ(b, "ant_brood", bx, by, reserve=False); _occ(b, "ant_eggs", bx + 1, by, reserve=False)
    for sx in (-4, 4):                            # warrior guards flanking the throne
        b.place_bug("ant_worker", cx + sx, throne_y + 2, scale=2.8)
    for sx in (-3, 3):                            # guards at the narthex (nave entry, north)
        b.place_bug("ant_worker", cx + sx, cy + 10, scale=2.8)
    # --- 6. LIGHT: a glow runner lining the processional aisle (dimmer than the apse) -------------
    for ny in range(cy + 8, throne_y + 4, -2):
        for sx in (-3, 3):
            _occ(b, "mushroom_glow", cx + sx, ny, reserve=False)
    # --- 7. floor dressing: moss + pale mushrooms in the side aisles ------------------------------
    for (mx, my) in [(cx - 8, cy + 2), (cx + 8, cy + 2), (cx - 8, cy - 3), (cx + 8, cy - 3)]:
        _occ(b, "moss_clump" if (mx + my) % 2 else "mushroom_inkcap", mx, my, reserve=False)
    # === PASS B — threshold, aisle light & richer chapels ========================================
    # processional AISLE RUNNER: a laid stone path down the nave centre, leading the eye to the apse
    for ny in range(cy + 11, throne_y + 4, -1):
        for dx in (-1, 0, 1):
            if b.in_bounds(cx + dx, ny) and b.is_free(cx + dx, ny):
                b.set_ground(cx + dx, ny, "stone_path")
    # NARTHEX GATE: flanking pillars extending the colonnade to the nave entry (a doorway from the trunk)
    for sx in (-5, 5):
        _occ(b, "stone_block", cx + sx, cy + 10); _occ(b, "stone_block", cx + sx, cy + 11)
    # THRONE HALO: a tight frame of light around the Queen (the cathedral's brightest point)
    for (dx, dy) in [(-3, 0), (3, 0), (-2, -1), (2, -1), (0, -2)]:
        _occ(b, "mushroom_glow", cx + dx, throne_y + dy, reserve=False)
    # richer W chapel — a fungus ALTAR; richer E vault — framing pillars + a treasure gleam
    _occ(b, "quartz_block", wt[0], wt[1] - 1)                 # pale altar stone in the glow-garden
    _occ(b, "mushroom_glow", wt[0], wt[1], reserve=False)
    for dy in (-1, 1):
        _occ(b, "stone_block", et[0] - 1, et[1] + dy)         # pillars framing the vault chest
    _occ(b, "crystal_small", et[0] + 1, et[1] - 1, reserve=False)  # treasure gleam
    return (cx, cy, throne_y)


def build():
    W, H = 46, 40
    b = ZoneBuilder("scene_queen_cathedral", W, H, base_tile="dirt", name="Queen's Cathedral", biome="cave")
    for y in range(H):
        for x in range(W):
            b.place_occupant("dirt_block", x, y)          # solid soil the dome is carved from
    cx, cy = W // 2, H // 2
    # cruciform: main lobe + E/W transepts (cy+4) + north narthex (cy+11) + south apse (cy-10)
    for (ccx, ccy, sz) in [(cx, cy, 16), (cx - 13, cy + 4, 10), (cx + 13, cy + 4, 10),
                           (cx, cy + 11, 8), (cx, cy - 10, 7)]:
        for (ox, oy) in carve_cavern(b, ccx, ccy, shape="lobed", size=sz, seed=ccx):
            if b.occ.get((ox, oy)):
                del b.occ[(ox, oy)]; b.reserved[oy][ox] = False
            b.set_ground(ox, oy, "cave_floor")
    place_queen_cathedral(b, cx, cy, R=15)
    b.spawn = [cx, 3]
    return b


if __name__ == "__main__":
    from scene_preview import render
    b = build()
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    render(b, __file__, PREVIEW, SCALE)
