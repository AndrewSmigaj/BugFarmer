#!/usr/bin/env python3
"""ZONE — BEE MEADOW (2,0 · bee_meadow_20): the EASY flower coast west of the village.
Design contract: docs/product/zones/bee_meadow_20.md. Geometry contract with village_21_B:
the ROAD exits our EAST edge at y=124 (their west lane reaches (2,124)); the STREAM exits
east at y=76 (they declare it entering at (0,76), feeding their lake).

Compose-in-place (the zone_village_21_B pattern): sea/beach → stream + lakes → roads +
BRIDGES (smooth once) → the bee farm + the fishing hamlet (the REAL pieces) → gardens →
meadows/forests/scatter → bug_spawning → grid/neighbors → save.

  python3 tools/zonegen/scenes/zone_bee_meadow_20.py           # build + lint + render preview
  python3 tools/zonegen/scenes/zone_bee_meadow_20.py --save    # also write nakama/data/zones/
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                    # noqa: E402
from render import render_builder                                      # noqa: E402
from features.terrain import (stream, lake, pond, forest, path,        # noqa: E402
                              smooth_paths, bridge, shore_dress, rock_mass,
                              gradient_field)
from features.garden import flower_patch                               # noqa: E402
from features.scatter import scatter                                   # noqa: E402
from scene_beach_cove import sea_edge, dress_beach, place_beach_landmarks, backshore  # noqa: E402
from scene_fishing_docks import place_fishing_hamlet, _dock            # noqa: E402
from scene_beekeeper_cottage import place_bee_farm                     # noqa: E402

W = H = 256
ROAD_Y = 124   # east-edge road row (village contract)
STREAM_Y = 76  # east-edge stream row (village contract)


def _water_span(b, fixed, lo, hi, *, row=True):
    """The [min,max] extent of water cells on a row (row=True: y=fixed, x in lo..hi) or a column.
    Returns None if the scan line holds no water — the bridge caller must then rethink."""
    cells = []
    for v in range(lo, hi + 1):
        x, y = (v, fixed) if row else (fixed, v)
        if b.in_bounds(x, y) and b.surface[y][x] == "water":
            cells.append(v)
    return (min(cells), max(cells)) if cells else None


def build():
    b = ZoneBuilder("bee_meadow_20", W, H, base_tile="grass", seed=20, name="Bee Meadow",
                    biome="meadow")
    rng = random.Random(20)

    # ---- 1. WATER ----------------------------------------------------------
    # The SEA (west boundary): coves at the hamlet bay (y≈64), mid-coast (y≈141) and the
    # north beach (y≈205); the tease island off the point between the first two.
    beach = sea_edge(b, water_w=11, sand_w=6,
                     coves=((0.25, 9), (0.55, 8), (0.80, 11)), island=(0.40, 4), seed=7)
    # THE INLET (the hamlet's harbor): a TRUE arm of the sea — carved east from the SW cove
    # through the sand bar, widening into a basin where the docks sit. Open water end to end:
    # a boat can row from the docks out past the buoys. (The old landlocked bay was a bug.)
    # Banks get INDEPENDENT noise (coasts §2 — never a mirrored pipe) and the mouth flares,
    # but each bank is clamped ±2 so the hamlet's shore-row contract (55/69) holds.
    import math as _m
    from features.terrain import _vnoise as _vn
    in_n, in_s = _vn(86), _vn(87)
    for x in range(10, 53):
        cy = 62 + int(round(1.5 * _m.sin(x / 7.0)))
        base = 4 if x < 38 else 6                       # the arm, then the basin bulge
        flare = max(0, 16 - x) * 0.3                    # the mouth opens at the sea
        h_n = base + flare + max(-2, min(2, (in_n(x * 0.13, 0.0) - 0.5) * 4.0))
        h_s = base + flare + max(-2, min(2, (in_s(x * 0.13, 0.0) - 0.5) * 4.0))
        for y in range(int(cy - h_s - 2), int(cy + h_n + 3)):
            if not b.in_bounds(x, y):
                continue
            dy = y - cy
            if -h_s <= dy <= h_n:
                depth = min(h_n - dy, dy + h_s)
                b.set_ground(x, y, "water_deep" if depth > 1.8 else "water_shallow",
                             surface="water")
                b.reserve(x, y, surface="water")
            elif b.surface[y][x] == "grass" and (-h_s - 1.7 <= dy <= h_n + 1.7):
                b.set_ground(x, y, "sand")

    # The STREAM: rises at a NW spring pondlet, descends south-east through the west-center,
    # then runs east to the village at STREAM_Y. Laid as chained segments so the course is
    # controlled (one road crossing, one footpath crossing) but still meanders.
    pond(b, 38, 208, 5, 4, seed=22)                       # the spring
    for seg_start, seg_end, sw_ in [((38, 204), (58, 172), 2), ((58, 172), (76, 142), 2),
                                    ((76, 142), (92, 108), 3), ((92, 108), (150, 84), 3),
                                    ((150, 84), (255, STREAM_Y), 3)]:
        # the LOW run widens to 3 (cold-grade: a 1-cell alternating checker staircase
        # reads as a blue zipper, not water — rivers only widen, coasts research §2)
        stream(b, seg_start, seg_end, width=sw_, seed=23, wobble=0.25)
    # THE EDGE SEAM: stream() stops within a cell of its endpoint — stamp the last column so the
    # water actually TOUCHES x=255 at the contract row (the village declares it entering at (0,76)).
    for sx in (253, 254, 255):
        for sy in (STREAM_Y - 1, STREAM_Y, STREAM_Y + 1):
            b.set_ground(sx, sy, "water_shallow" if sy != STREAM_Y else "water_deep", surface="water")
            b.reserve(sx, sy, surface="water")

    # The BIG FISHING LAKE (south-center) + the NE pond.
    fl = lake(b, 152, 42, 15, seed=24, shore="sand", reeds=14)
    shore_dress(b, fl, [(150, 260, "sand"), (260, 40, "reeds"), (40, 150, "forest")], seed=25)
    pond(b, 212, 204, 7, 5, seed=26)

    # ---- 1b. THE SOUTH GRADIENT (owner design, 2026-07-06) ---------------------
    # "there is no ant colony in the zone... wanted it to start getting dirty and rocky
    # on a gradient not suddenly having the dirt wall." NO ants, NO set-piece: the meadow
    # itself dirties and roughens toward the south edge (C12), mineable dirt masses with
    # rocky cores sit EMBEDDED in the dirtiest part, and patchy village-style woods with
    # real clear areas hold the band's east (C13: no blob stamps, no even spacing).
    gradient_field(b, 0, 0, 255, 36, edge="s", seed=70,
                   ground="dirt", rocky="stone_floor",
                   scale=0.055, noise_amp=0.62, warp=7.0)
    COMMONS = [("ore_coal_block", 2, 3, 6, "any"), ("ore_copper_block", 2, 3, 5, "any")]
    # Masses: size-varied ~6:1, irregular longitudes/latitudes, one true CLUSTER
    # (two overlapping so their shapes merge) — never a row of same-size discs.
    # Bigger gray hearts (core_at 0.34) so the earthworks READ against the dirt field.
    rock_mass(b, 74, 10, 15, 8, seed=60, shell="dirt_block", floor="dirt",
              core="stone_block", core_at=0.34, gap_chance=0.07, core_noise=0.22,
              vein_spec=[("ore_coal_block", 4, 4, 7, "any"), ("ore_copper_block", 3, 3, 6, "any"),
                         ("ore_iron_block", 2, 3, 4, "core"),
                         ("ore_silver_block", 1, 2, 3, "core")])            # the anchor + the ONE deep rare
    rock_mass(b, 148, 9, 9, 6, seed=61, shell="dirt_block", floor="dirt",
              core="stone_block", core_at=0.34, gap_chance=0.07, core_noise=0.22,
              vein_spec=[("ore_coal_block", 3, 4, 6, "any"),
                         ("ore_copper_block", 3, 3, 5, "any")])             # cluster, main
    rock_mass(b, 159, 15, 6, 4, seed=62, shell="dirt_block", floor="dirt",
              gap_chance=0.14, core_noise=0.0,
              vein_spec=[("ore_coal_block", 2, 3, 5, "any")])               # cluster, shoulder (merges)
    rock_mass(b, 113, 16, 6, 4, seed=63, shell="dirt_block", floor="dirt",
              core="stone_block", core_at=0.38, gap_chance=0.12, core_noise=0.2,
              vein_spec=COMMONS)                                            # mid single
    rock_mass(b, 199, 6, 4, 3, seed=64, shell="dirt_block", floor="dirt",
              gap_chance=0.16,
              vein_spec=[("ore_copper_block", 1, 3, 4, "any")])             # small east outlier
    # Patchy WOODS on the band's east — the village recipe (forest() falloff, mixed
    # species, density ~0.45-0.55, NO forced dirt floor: the gradient already dirties
    # the ground) — three stands of different sizes with genuine CLEAR AREAS between.
    forest(b, 178, 28, 14, 9, density=0.5, seed=71)
    forest(b, 209, 15, 6, 4, density=0.45, seed=72,
           species=("tree_oak", "tree_oak", "tree_pine"))
    forest(b, 237, 29, 10, 7, density=0.55, seed=73,
           species=("tree_pine", "tree_pine", "tree_oak"))
    # ...and the fray: lone trees in the clear areas between stands (real wood edges
    # shed outliers — a stand that ends at its own rim reads as a cutout).
    scatter(b, 160, 6, 252, 38, {"tree_oak": 2, "tree_pine": 1},
            density=0.006, min_spacing=5, seed=76)
    # TORN-GROUND RUBBLE — the field itself is mineable in flecks, not just at the
    # masses: lone dirt blocks shed across the deep-dirt plain, stone rubble wherever
    # rock grins through (so stone_floor reads as OUTCROP, not paving). Sparse enough
    # that every screen stays walkable.
    rng_r = random.Random(78)
    for y in range(0, 15):
        for x in range(42, 253):
            g = b.ground[y][x]
            if g == "dirt" and rng_r.random() < 0.011 and b.is_free(x, y):
                b.place_occupant("dirt_block", x, y)
            elif g == "stone_floor" and rng_r.random() < 0.16 and b.is_free(x, y):
                b.place_occupant("stone_block", x, y)
    # The band's own flora — DRY things clumped where the ground is torn (tall grass
    # drifts, dead bushes, a tumbleweed or two), thinning north with the gradient.
    scatter(b, 44, 2, 250, 16, {"tall_grass": 5, "dead_bush": 3, "tumbleweed": 1},
            density=0.09, min_spacing=2, seed=74, clumping=0.7, cluster_radius=5)
    scatter(b, 44, 16, 250, 30, {"tall_grass": 4, "dead_bush": 1},
            density=0.02, min_spacing=3, seed=75, clumping=0.6, cluster_radius=4)
    scatter(b, 188, 2, 252, 13, {"tall_grass": 4, "dead_bush": 3, "tumbleweed": 2},
            density=0.05, min_spacing=2, seed=77, clumping=0.65, cluster_radius=4)  # SE corner isn't a void
    # A couple of skeletal trees + old stumps in the dirt — something died here slowly.
    for oid, tx_, ty_ in [("tree_dead", 92, 12), ("tree_dead", 170, 7),
                          ("stump", 128, 10), ("stump", 61, 17), ("log_fallen", 137, 19)]:
        for ddx in (0, 1, -1, 2, -2, 3, -3):
            if b.in_bounds(tx_ + ddx, ty_) and b.is_free(tx_ + ddx, ty_) \
               and b.surface[ty_][tx_ + ddx] == "grass":
                b.place_occupant(oid, tx_ + ddx, ty_)
                break

    # ---- 1c. THE ROCKY GORGE (the stream's east exit) -------------------------
    # The stream cuts THROUGH rock (masses pressed on both banks; the channel is reserved
    # water so the fill stops at it). Ore: doctrine veins ONLY — commons throughout + the
    # rares as few, short, core-band runs (owner correction 2026-07-06: no hand-set lines).
    rock_mass(b, 224, 90, 9, 7, seed=54, shell="stone_block", floor="stone_floor",
              core="stone_block",
              vein_spec=COMMONS + [("ore_iron_block", 1, 3, 4, "any"),
                                   ("ore_silver_block", 1, 2, 3, "core")])
    rock_mass(b, 231, 66, 9, 7, seed=55, shell="stone_block", floor="stone_floor",
              core="stone_block",
              vein_spec=COMMONS + [("ore_gold_block", 1, 2, 3, "core"),
                                   ("ore_ruby_block", 1, 2, 2, "core")])
    # THE GORGE READS AS A CUT (cold-grade: "two concrete pads beside a ditch" — no
    # landform). Overhead can't do cliffs, so the CUT is told in materials: a stone
    # LIP hugging both banks through the notch, boulder rim blocks grinning over the
    # water (the gap-toothed 30%, banks stay walkable), scree bleeding outward.
    rng_g = random.Random(96)
    for y in range(58, 104):
        for x in range(205, 251):
            if not b.in_bounds(x, y) or b.surface[y][x] != "grass":
                continue
            near_w = any(b.in_bounds(x + dx, y + dy) and b.surface[y + dy][x + dx] == "water"
                         for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if near_w and b.ground[y][x] in ("grass", "dirt"):
                b.set_ground(x, y, "stone_floor")
                if rng_g.random() < 0.3 and b.is_free(x, y):
                    b.place_occupant("stone_block", x, y)
            elif b.ground[y][x] == "grass" and rng_g.random() < 0.20 \
                and any(b.in_bounds(x + dx, y + dy) and b.ground[y + dy][x + dx] == "stone_floor"
                        for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                b.set_ground(x, y, "stone_floor")         # the scree apron widens
    # THE FRESH CLAIM — micro-story 2: somebody staked the gorge and left in a hurry
    # (deliberately UNTIDY — the C6 rule-bend: abandonment is the story, rows are for work).
    # LENS FIX (Storyteller): the props CLUSTER as one campsite — a story scattered over ten
    # cells reads as unrelated litter. Sign, pile and crate within a 3-cell huddle at the
    # north mass's west foot.
    claim_anchor = None
    for sdx in range(0, 8):
        if b.is_free(211 + sdx, 96) and b.surface[96][211 + sdx] == "grass":
            b.place_occupant("signpost", 211 + sdx, 96,
                             text="CLAIM — J. Halloway.\nBack by spring.")
            claim_anchor = (211 + sdx, 96)
            break
    if claim_anchor:
        ax_, ay_ = claim_anchor
        for oid, dx_, dy_ in [("ore_pile", 1, -1), ("crate", -2, 0), ("ore_pile", 2, 1)]:
            if b.in_bounds(ax_ + dx_, ay_ + dy_) and b.is_free(ax_ + dx_, ay_ + dy_):
                b.place_occupant(oid, ax_ + dx_, ay_ + dy_)

    # ---- 2. ROADS + BRIDGES (then smooth ONCE) ------------------------------
    # Roads are laid through WAYPOINTS (cold-grade BROKEN: path()'s goal-pull flattens
    # any long single segment into a ruler line — the east road was a 145-cell runway).
    # Real roads drift; only the last cells at a contract edge run true.
    span = _water_span(b, ROAD_Y, 60, 130)
    assert span, "the stream must cross the road row"
    east_bank, west_bank = span[1] + 1, span[0] - 1
    for a, c in [((255, ROAD_Y), (232, ROAD_Y)),          # hold the contract row off the edge
                 ((232, ROAD_Y), (207, ROAD_Y - 4)),      # ...then drift
                 ((207, ROAD_Y - 4), (176, ROAD_Y + 3)),
                 ((176, ROAD_Y + 3), (east_bank + 2, ROAD_Y))]:
        path(b, a, c, width=2, tile="dirt", wobble=0.22, seed=27 + a[0] % 7)
    for by in (ROAD_Y, ROAD_Y + 1):                       # a 2-wide deck matching the road
        bridge(b, (east_bank + 1, by), (west_bank - 1, by))
    # BUTT the road to its own bridge (cold-grade: the artery visibly disconnected at
    # its one crossing) — both approaches, both deck rows, painted explicitly.
    for by in (ROAD_Y, ROAD_Y + 1):
        # Walk outward from each row's ACTUAL deck ends (they shift per row on a
        # diagonal stream) painting dirt until the roadbed is met — no fixed offsets,
        # no one-cell grass gaps at a bridge shoulder.
        xs = [x for x in range(west_bank - 6, east_bank + 7)
              if b.in_bounds(x, by) and b.ground[by][x] == "bridge_wood"]
        for step, edge in ((1, max(xs)), (-1, min(xs))) if xs else ():
            bx_, n = edge + step, 0
            while n < 5 and b.in_bounds(bx_, by) and b.surface[by][bx_] != "water" \
                    and b.ground[by][bx_] not in ("dirt", "bridge_wood"):
                b.set_ground(bx_, by, "dirt", surface="path")
                bx_ += step
                n += 1
    for a, c in [((west_bank - 1, ROAD_Y), (66, ROAD_Y - 6)),
                 ((66, ROAD_Y - 6), (52, 104))]:
        path(b, a, c, width=2, tile="dirt", wobble=0.2, seed=28 + a[1] % 5,
             taper_ends=(0 if a[0] > 70 else 4))           # dwindles toward the hamlet

    # The farm spur: north from the road to Maren's gate (the farm sits north of the road) —
    # stop a cell short of the fence row, then a single doorstep cell kisses the gate.
    path(b, (137, ROAD_Y + 1), (137, 142), width=2, tile="dirt", wobble=0.05, seed=29)
    b.set_ground(137, 143, "dirt", surface="path")

    # The hamlet spur: from the west leg down to the north quay by the footbridge.
    path(b, (52, 104), (50, 72), width=1, tile="dirt", wobble=0.08, seed=30, taper_ends=2)

    # The north-band footpath: up the west side, bridging the stream's descent —
    # waypointed like everything else (it was the worst ruler line on the map:
    # 90 cells of perfectly vertical 1-wide stripe).
    cspan = _water_span(b, 56, 140, 200, row=False)
    if cspan:
        s0, s1 = cspan
        path(b, (56, 128), (52, 146), width=1, tile="dirt", wobble=0.14, seed=31)
        path(b, (52, 146), (56, s0 - 1), width=1, tile="dirt", wobble=0.14, seed=131)
        bridge(b, (56, s0 - 1), (56, s1 + 1))
        path(b, (56, s1 + 1), (61, 182), width=1, tile="dirt", wobble=0.14, seed=32)
        path(b, (61, 182), (60, 196), width=1, tile="dirt", wobble=0.14, seed=132, taper_ends=3)
    smooth_paths(b)
    # ROAD-EDGE WEAR: dither the band's knife edges — dirt treads bleeding off the
    # sides (ground-only; the roadbed itself is untouched, so connectivity holds).
    rng_w = random.Random(88)
    for y in range(1, 255):
        for x in range(1, 255):
            if b.surface[y][x] == "path" and b.ground[y][x] == "dirt":
                open_nb = [(nx, ny) for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                           if b.surface[ny][nx] == "grass" and b.ground[ny][nx] == "grass"
                           and not b.reserved[ny][nx] and (nx, ny) not in b.occ]
                if open_nb and rng_w.random() < 0.16:
                    nx, ny = open_nb[rng_w.randrange(len(open_nb))]
                    b.set_ground(nx, ny, "dirt")          # a tread worn off the edge

    # ---- 3. BUILDINGS (the real pieces) -------------------------------------
    place_bee_farm(b, 100, 124)          # apiary x124-150 y144-162, cottage NW, gate at (137,144)
    # Connect the cottage's FRONT gate to the road T (cold-grade: the house was an
    # island — its cobble stub died one cell past the fence). A hand-walked worn
    # trace, not path(): it has to WEAVE through the farm's flower ring, and dodging
    # planted flowers is what a real footpath does anyway.
    rng_c = random.Random(90)
    cx_, cy_ = 110, 140
    while (cx_, cy_) != (133, 128) and cy_ >= 127:
        for cell in ((cx_, cy_), (cx_ + 1, cy_)):
            x_, y_ = cell
            if b.in_bounds(x_, y_) and b.surface[y_][x_] == "grass" \
               and b.ground[y_][x_] == "grass" and b.is_free(x_, y_):
                b.set_ground(x_, y_, "dirt")
        if cx_ < 133 and (cy_ <= 128 or rng_c.random() < 0.65):
            cx_ += 1
        else:
            cy_ -= 1
    place_fishing_hamlet(b, 24, 69, 55)  # split shores across the inlet, footbridge at x50

    # The lake dock: a stub pier + moored boat on the fishing lake's north shore.
    _dock(b, 150, 60, max_len=9)

    # ---- 4. MEADOWS, FORESTS, WILDLIFE ANCHORS ------------------------------
    common = ["flower_red", "flower_blue", "flower_yellow", "flower_wild", "clover", "dandelion"]
    rarer = ["lavender", "chamomile", "poppy", "sunflower"]
    # The great meadows: east of the farm, the road margins, and the north band.
    flower_patch(b, 160, 100, 250, 150, common + rarer, 90, seed=33)
    flower_patch(b, 170, 155, 246, 195, common, 60, seed=34)
    flower_patch(b, 70, 150, 118, 200, common + rarer, 40, seed=35)
    flower_patch(b, 96, 88, 150, 118, common, 30, seed=36)
    flower_patch(b, 60, 210, 130, 244, common, 36, seed=37)
    flower_patch(b, 66, 32, 160, 52, common, 34, seed=46)   # the south meadow, above the gradient
    # Milkweed clumps (butterfly breeding hosts).
    for mx, my in [(180, 160), (183, 158), (186, 162), (84, 176), (87, 174), (90, 178)]:
        if b.is_free(mx, my):
            b.place_occupant("milkweed", mx, my)

    # WILDFLOWER / CLOVER / TALL-GRASS DRIFTS (cold-grade BROKEN: "the zone's namesake
    # is empty lawn" — a Bee Meadow whose flowers lived inside one fence). flower_patch
    # spreads singles that vanish at zoom; a DRIFT is one readable MASS — an elliptical
    # blob with a dominant species, dense core, ragged rim. One on nearly every screen
    # of open grass; the meadow between them stays meadow (no noise-soup).
    rng_d = random.Random(80)

    def _drift(cx, cy, r, dom, accent):
        for dy in range(-r - 1, r + 2):
            for dx in range(-r - 1, r + 2):
                x, y = cx + dx, cy + dy
                if not b.in_bounds(x, y) or b.surface[y][x] != "grass" \
                   or b.ground[y][x] != "grass" or not b.is_free(x, y):
                    continue
                d = (dx * dx + dy * dy) ** 0.5 / (r + 0.001)
                if d <= 1.15 and rng_d.random() < 0.55 * max(0.0, 1.0 - d) + 0.08:
                    b.place_occupant(dom if rng_d.random() < 0.75 else accent, x, y)

    MIXES = [("clover", "flower_wild"), ("poppy", "flower_red"),
             ("tall_grass", "dandelion"), ("lavender", "chamomile"),
             ("flower_yellow", "dandelion"), ("flower_blue", "flower_wild")]
    for i, (dx_, dy_, r_) in enumerate([
            # the east meadow (the road's country)
            (168, 100, 5), (182, 106, 4), (198, 100, 6), (214, 103, 4), (232, 99, 5),
            (244, 104, 3), (226, 110, 4),
            # east of the farm / below the road
            (160, 142, 4), (175, 140, 5), (196, 138, 4), (230, 140, 6), (246, 142, 3),
            # the south-east shoulder (around the big stand)
            (172, 158, 4), (168, 186, 5), (170, 196, 4), (200, 196, 5), (232, 196, 4),
            # west of the farm
            (70, 96, 5), (88, 104, 4), (112, 94, 5), (76, 112, 4),
            # the south-west meadows
            (94, 160, 5), (70, 176, 4), (96, 186, 5), (116, 176, 4), (120, 196, 4),
            # north-center, between the glade and the pond
            (146, 200, 4), (170, 210, 5), (196, 214, 4), (196, 242, 4),
            # the south meadow above the gradient
            (84, 40, 4), (118, 46, 5), (140, 36, 4)]):
        dom, accent = MIXES[i % len(MIXES)]
        _drift(dx_, dy_, r_, dom, accent)

    # Forests (dark forest floors — dirt=True): the NE stand, the stream-bank strip, the
    # north-west band, and TWO NEW NORTH STANDS framing the top of the zone. The gap between
    # the north stands is deliberate — travellers pass through here, and the open corridor
    # around y≈200-215 stays wide and readable.
    forest(b, 214, 172, 26, 18, seed=38, density=0.55, dirt=True)
    forest(b, 176, 96, 18, 8, seed=39, density=0.5, dirt=True)
    forest(b, 42, 182, 16, 12, seed=40, density=0.55, dirt=True)
    forest(b, 158, 236, 26, 13, seed=48, density=0.6, dirt=True)
    forest(b, 96, 232, 15, 11, seed=49, density=0.55, dirt=True)
    # Every big stand FRAYS (cold-grade: blob outlines read as cutouts): lone outlier
    # trees shed into the surrounding grass.
    scatter(b, 185, 150, 248, 196, {"tree_oak": 2, "tree_pine": 1}, density=0.004,
            min_spacing=5, seed=58)
    scatter(b, 152, 86, 205, 110, {"tree_oak": 2, "tree_pine": 1}, density=0.004,
            min_spacing=5, seed=59)
    scatter(b, 24, 168, 64, 200, {"tree_pine": 2, "tree_oak": 1}, density=0.004,
            min_spacing=5, seed=66)
    # THE HONEY GLADE — the clearing between the north stands: a wild hive in a ring of
    # flowers (you hear it before you see it). Overhead can't do hilltops; it CAN do glades.
    flower_patch(b, 118, 224, 142, 244, common + rarer, 26, seed=50)
    _glade_hive = (128, 234)
    # THE MUSHROOM HOLLOW — the damp clearing between the NW band and the west north stand.
    scatter(b, 62, 206, 88, 226,
            {"mushroom_brown": 4, "mushroom_chanterelle": 2, "leaf_litter": 4, "fern": 3},
            density=0.07, min_spacing=2, seed=56, surfaces=("grass",))
    # Forest floor: leaf litter (millipede food) + mushrooms in each stand.
    for (x0, y0, x1, y1, sd) in [(190, 156, 240, 190, 41), (160, 88, 194, 104, 42),
                                 (28, 172, 58, 194, 43), (146, 226, 184, 248, 57)]:
        scatter(b, x0, y0, x1, y1,
                {"leaf_litter": 5, "mushroom_brown": 2, "fern": 3, "tall_grass": 2},
                density=0.05, min_spacing=2, seed=sd, surfaces=("grass",))

    # STREAM BANKS LIVE (cold-grade: raw knife-edge grass-to-water for most of the
    # run): reeds and tufts every few cells beside the water — the low run and the
    # descent both, stopping where the gorge's stone lip takes over (x<205).
    rng_s = random.Random(97)
    for x0_, x1_, y0_, y1_ in [(88, 205, 60, 116), (30, 92, 100, 208)]:
        for y in range(y0_, y1_):
            for x in range(x0_, x1_):
                if b.surface[y][x] != "grass" or b.ground[y][x] != "grass" \
                   or not b.is_free(x, y):
                    continue
                if any(b.in_bounds(x + dx, y + dy) and b.surface[y + dy][x + dx] == "water"
                       for dx in (-1, 0, 1) for dy in (-1, 0, 1)) \
                   and rng_s.random() < 0.22:
                    b.place_occupant(rng_s.choice(["reeds", "tall_grass", "reeds", "clover"]),
                                     x, y)

    # WILD HIVES + WASP NESTS are ECOLOGY ANCHORS — never skip one silently; spiral to the
    # nearest free grass cell if the exact spot got taken by a tree/flower.
    def _place_near(oid, x, y, r=5):
        for d in range(r + 1):
            for dy in range(-d, d + 1):
                for dx in range(-d, d + 1):
                    if max(abs(dx), abs(dy)) == d and b.in_bounds(x + dx, y + dy) \
                       and b.surface[y + dy][x + dx] == "grass" and b.is_free(x + dx, y + dy):
                        return b.place_occupant(oid, x + dx, y + dy)
        raise SystemExit(f"no free cell near ({x},{y}) for {oid} — rework the layout")

    # The free colonies (each auto-founds; the flowers nearby are their economy) — including
    # the honey-glade hive between the north stands.
    for hx, hy in [(168, 152), (206, 112), (78, 202), _glade_hive]:   # (206,112) = the Humming Oak's colony
        _place_near("bee_hive_wild", hx, hy)
    # The raiders, at forest edges AWAY from the farm (this is the EASY zone).
    for wx, wy in [(232, 158), (186, 90)]:
        _place_near("wasp_nest", wx, wy)

    # WILD FRUIT CLUMPS (owner Q: "are there enough patches of fruit trees?" — there
    # weren't; only Maren's two). Three small clusters, each near a route so they're
    # found: windfalls feed flies TODAY and the ants foraging up from the south TOMORROW
    # (they collect dead bugs + food), blossom forage for the bees either way.
    for fx, fy, sp in [(150, 214, "tree_apple"), (153, 211, "tree_cherry"),   # the corridor snack
                       (142, 132, "tree_plum"), (145, 130, "tree_plum"),      # the fork pair, N of the road
                       (100, 44, "tree_orange"), (104, 42, "tree_apple")]:    # the south-meadow pair
        _place_near(sp, fx, fy)

    # THE WAYSTONE — the entrance landmark (settlements research §5: one distinct
    # silhouette per approach axis, before the houses): an old standing stone where
    # the road tops the last rise, a bench a traveler actually uses, flowers let grow.
    _place_near("standing_stone", 243, 118)
    _place_near("bench", 245, 120, r=3)
    for wfx, wfy in [(242, 120), (245, 117), (240, 118)]:
        if b.in_bounds(wfx, wfy) and b.is_free(wfx, wfy) and b.surface[wfy][wfx] == "grass":
            b.place_occupant(rng.choice(["flower_wild", "poppy", "lavender"]), wfx, wfy)

    # THE HUMMING OAK — the mid-road beat (composition research: an interest beat every
    # 20-40 tiles; the road ran ~100 flat ones). Two oaks over a roadside wild hive in
    # deep grass — you HEAR this place first. The whole beat sits SOUTH of the drifted
    # roadbed with 2 cells' clearance (tall sprites draw north over a road above them).
    _place_near("tree_oak", 204, 114)
    _place_near("tree_oak", 209, 112)
    for gx, gy in [(203, 111), (207, 113), (210, 113), (205, 109), (208, 115)]:
        if b.in_bounds(gx, gy) and b.is_free(gx, gy) and b.surface[gy][gx] == "grass":
            b.place_occupant("tall_grass", gx, gy)
    # ...and the road-clearing story a little west: the stump + log the crew left.
    _place_near("stump", 178, 121, r=3)
    _place_near("log_fallen", 180, 122, r=3)

    # The beach set + the coast's NAMED features: the shipwreck at the mid-coast cove, the
    # picnic spot on the north beach, buoys off the cove mouths, the bottle on the island.
    dress_beach(b, beach, seed=44, density=0.07)   # wrack in CLUSTERS, not lone singles
    place_beach_landmarks(b, beach, wreck_y=141, picnic_y=206, buoy_ys=(64, 141),
                          bottle_island=(5, 102), pool_y=199)
    backshore(b, beach, path_y=None, seed=45, depth=10)   # dune scrub only — roads exist

    # WAYFINDING — signposts WITH TEXT at the junctions (arriving must read instantly).
    # (The old "ground hums / mind the mounds" warning + gag mound went with the ant
    # content — owner 2026-07-06: no ants in this zone.)
    for sx, sy, txt in [
        (249, ROAD_Y + 3, "BEE MEADOW — the flower coast.\nThe Village →"),
        (135, ROAD_Y + 3, "↑ Maren's Bee Farm\n↓ Dragonfly Lake\n→ The Village"),
        (57, 108, "↓ Gullwash Landing — mind the tide."),
    ]:
        placed_sign = False
        for dy in (0, 1, -1):
            for dx in range(0, 9):
                if b.is_free(sx + dx, sy + dy) and b.surface[sy + dy][sx + dx] == "grass":
                    b.place_occupant("signpost", sx + dx, sy + dy, text=txt)
                    placed_sign = True
                    break
            if placed_sign:
                break
    for lx, ly in [(247, ROAD_Y - 2), (98, ROAD_Y - 2)]:
        if b.is_free(lx, ly):
            b.place_occupant("lamp_post", lx, ly)

    # WATER DRESSING — reeds wherever shallow water meets grass (stream banks, lake rims,
    # the ponds; the sea keeps its own beach treatment), lily pads on the calm lake shallows.
    rng_w = random.Random(47)
    reeds_n = pads_n = 0
    for y in range(4, H - 4):
        for x in range(30, W - 4):
            if b.ground[y][x] != "water_shallow" or not b.in_bounds(x, y):
                continue
            nb_grass = any(b.in_bounds(x + dx, y + dy) and b.surface[y + dy][x + dx] == "grass"
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if nb_grass and reeds_n < 90 and rng_w.random() < 0.05:
                b.reserved[y][x] = False
                if b.place_occupant("reeds", x, y, surface="water"):
                    reeds_n += 1
                b.reserve(x, y, surface="water")
            elif not nb_grass and pads_n < 10 and 100 < x < 240 and rng_w.random() < 0.02:
                b.reserved[y][x] = False
                if b.place_occupant("lily_pad", x, y, surface="water"):
                    pads_n += 1
                b.reserve(x, y, surface="water")

    # The NE pond is the QUIET SPOT: a bench facing the water under the evening fireflies.
    for bx, by in [(220, 198), (221, 197), (219, 197)]:
        if b.is_free(bx, by):
            b.place_occupant("bench", bx, by)
            break

    # The south-east fills: a wild-berry thicket + driftwood washed up the stream mouth.
    for tx, ty in [(214, 54), (217, 56), (212, 57), (219, 53), (215, 50)]:
        if b.is_free(tx, ty):
            b.place_occupant("wild_berry_bush", tx, ty)
    for dx, dy in [(246, 72), (240, 80)]:
        if b.in_bounds(dx, dy) and b.surface[dy][dx] == "grass" and b.is_free(dx, dy):
            b.place_occupant("driftwood", dx, dy)

    scatter(b, 60, 40, 250, 246,
            {"bush": 3, "tall_grass": 5, "wild_berry_bush": 1, "dandelion": 2, "clover": 2},
            density=0.02, min_spacing=3, seed=45, surfaces=("grass",))

    # ---- 5. BUG SPAWNING ----------------------------------------------------
    b.bug_spawning = {
        "static": False,
        "species_caps": {
            # Bees are NEST-FOUNDED ONLY: never free-spawned, never Director-reseeded (min 0).
            # 3 wild hives + Maren's 5 boxes = room under max_nests 8 for a full apiary.
            "bee_honey":        {"initial": 0, "max": 15, "swarm_size": 4, "max_population": 60,
                                 "min_population": 0, "cull_at": 0, "max_nests": 10,
                                 "spawn_interval": 999999.0},
            "butterfly_meadow": {"initial": 6, "max": 20, "swarm_size": 6, "max_population": 90,
                                 "min_population": 10, "event_low": 20, "event_high": 60,
                                 "cull_at": 80, "spawn_interval": 600.0},
            "fly_common":       {"initial": 3, "max": 10, "swarm_size": 6, "max_population": 60,
                                 "min_population": 6, "spawn_interval": 600.0},
            # Wasps come from their 2 forest nests (raiders); the Director may cull, never seed.
            "wasp_common":      {"initial": 0, "max": 6, "swarm_size": 5, "max_population": 24,
                                 "min_population": 0, "cull_at": 20, "max_nests": 3,
                                 "spawn_interval": 999999.0},
            "dragonfly_blue":   {"initial": 2, "max": 4, "swarm_size": 2, "max_population": 8,
                                 "min_population": 1, "spawn_interval": 1200.0},
            "firefly":          {"initial": 4, "max": 8, "swarm_size": 5, "max_population": 40,
                                 "min_population": 4, "spawn_interval": 900.0},
            "millipede":        {"initial": 2, "max": 6, "swarm_size": 1, "max_population": 16,
                                 "min_population": 2, "spawn_interval": 1200.0},
            "beetle_carrion":   {"initial": 1, "max": 4, "swarm_size": 1, "max_population": 10,
                                 "min_population": 1, "spawn_interval": 1200.0},
        },
        "spawn_areas": [
            {"id": "meadow_e",  "species": ["butterfly_meadow"], "type": "circle", "cx": 200, "cy": 125, "radius": 16},
            {"id": "meadow_n",  "species": ["butterfly_meadow"], "type": "circle", "cx": 95,  "cy": 175, "radius": 14},
            {"id": "farm_fly",  "species": ["fly_common"],       "type": "circle", "cx": 140, "cy": 132, "radius": 10},
            {"id": "bay_fly",   "species": ["fly_common"],       "type": "circle", "cx": 52,  "cy": 96,  "radius": 9},
            {"id": "lake_drag", "species": ["dragonfly_blue"],   "type": "circle", "cx": 152, "cy": 64,  "radius": 9},
            {"id": "stream_ff", "species": ["firefly"],          "type": "circle", "cx": 120, "cy": 96,  "radius": 10},
            {"id": "spring_ff", "species": ["firefly"],          "type": "circle", "cx": 52,  "cy": 196, "radius": 9},
            {"id": "wood_mill", "species": ["millipede"],        "type": "circle", "cx": 214, "cy": 170, "radius": 12},
            {"id": "wood_beet", "species": ["beetle_carrion"],   "type": "circle", "cx": 180, "cy": 96,  "radius": 9},
        ],
        "initial_carrion": [
            {"item": "dead_fly", "x": 182, "y": 98, "count": 2},
            {"item": "dead_millipede", "x": 216, "y": 168, "count": 1},
        ],
    }

    # Arriving from the village reads naturally: spawn on the road just inside the east edge.
    b.spawn = [246, ROAD_Y + 2]
    b.grid = (2, 0)
    b.neighbors = {"east": "village_21_B"}
    return b


PREVIEW = "zones/bee_meadow_20"
SCALE = 2


if __name__ == "__main__":
    b = build()
    defects = b.lint()
    print("LINT:", *(["0 defects ✓"] if not defects else ["\n  - " + "\n  - ".join(defects)]))
    print("warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    zdir = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "zones", "bee_meadow_20"))
    os.makedirs(zdir, exist_ok=True)
    render_builder(b, os.path.join(zdir, "full.png"), scale=2)
    print("preview ->", os.path.join(zdir, "full.png"))
    if "--save" in sys.argv:
        out_dir = b.save()
        print("saved ->", out_dir)
