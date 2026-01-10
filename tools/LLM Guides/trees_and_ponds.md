Lakes & Forests Guide (Zone Generation)

This guide defines how to generate lakes and forests that look intentional and organic on a grid, with deterministic results under a shared seed.

The goals:

Shape language: lakes and forests should read as areas, not sprinkled props.

Edges matter: the shoreline and forest edge do most of the visual work.

Gradients: density should vary (core dense, edge sparse), not uniform.

Relationships: lakes influence nearby vegetation; forests create clearings and trails.

Determinism Rules (Non-Negotiable)

Every decision must be derived from seed + coordinates (or a seeded RNG stream).

Prefer noise fields and stamped shapes over random.scatter for major features.

Avoid patterns that look repeated: if you stamp multiple lakes, vary:

size, eccentricity, shoreline roughness, and orientation (still grid aligned).

LAKES
What a “good lake” needs

A lake is not just “water tiles”:

Deep interior (water_deep)

Shallow rim (water_shallow) with variable thickness

Shore ring: sand (beachy) or mud (swampy) with occasional breaks

Vegetation response:

reeds along muddy shores

sparse grass near sandy shores

occasional lily pads / driftwood / rocks

Negative space: a small clearing or path that approaches the lake (not every time, but often)

Lake placement: where and how many

Per 512×512 zone (tune per biome):

Meadow-ish zones: 2–5 lakes/ponds

Forest zones: 1–3 lakes + 2–6 small ponds

Swamp zones: more water, but broken into pools and channels

Place lakes using one of these strategies:

Edge anchoring: some lakes should be near zone edges so they feel like part of a larger world.

Rule of thirds: avoid “all lakes in corners” or “all lakes centered”.

Keep-away radius from the town square / major hub roads unless it’s a planned landmark.

Shape generation (recommended approach)

Use a stamped “organic blob” with shoreline noise:

Step A: Create a lake mask

Choose center (cx, cy) and base radius r.

For each cell within r * 1.6, compute:

dist = sqrt(dx^2 + dy^2)

local_r = r * (1 + Σ bump_i * sin(freq_i*angle + phase_i))

plus a small coordinate noise term (seeded) to break symmetry

Mark as “inside lake” when dist <= local_r.

Step B: Deep vs shallow

water_deep for dist <= local_r * 0.55–0.70 (vary per lake)

water_shallow for the remaining inside ring, but vary thickness:

shoreline thickness should change around the lake (bays vs steep drops)

Step C: Shore ring
Around every shallow cell, paint a shore tile:

If biome is meadow/forest: mostly sand

If biome is swampy: mostly mud

Do not make a perfect ring—allow interruptions and small spits.

Shore decoration (what to put where)

Along the shore, do clumps, not singles.

Rules

Reeds: spawn in streaks on muddy shores, not evenly spaced.

Rocks: a few clusters on sand or rocky edges.

Driftwood / logs: occasional, near forested banks.

Flowers: do NOT “just attract bees visually”. Flowers are ecology hooks:

place them as patches near lake-adjacent clearings, not as confetti across the entire map.

Clump algorithm

Pick 8–20 “shore anchor points” (cells on shore ring).

For each anchor, grow a tiny patch via a 10–40 step random walk (seeded).

Validate walkability if needed.

Connectivity: make the lake feel used

At least half of lakes should have one of:

a small approach path (dirt/stone) that ends near shore

a clearing near shore (less vegetation, maybe a bench/sign)

a tiny fishing spot (a 3×3 or 5×5 intentional area)

This is what keeps lakes from looking like random paint blobs.

FORESTS
What a “good forest” needs

A forest is not scattered trees.
It’s:

Masses of trees (core)

Edge gradient (sparser edge, bushes/grass transition)

Clearings (intentional empty spaces)

Understory: bushes, mushrooms, fallen logs

Trails/corridors: places you can see through and move through

Forest placement: big shapes first

Per 512×512 zone:

1–3 major forest masses (even in meadow zones you can have “tree lines”)

plus small groves as accents

Forests should:

align with roads and landmarks (leave visibility around roads)

respond to lakes (denser on some banks, open meadow on others)

Forest density field (do this instead of scatter)

Create a continuous forest_density(x,y) in [0,1] using noise:

Low frequency noise for broad regions

Optionally add a “falloff” from forest center(s)

Then define:

core where density > 0.70

mid where density 0.45–0.70

edge where density 0.20–0.45

outside forest < 0.20

Tree placement by band

Core: many trees, but still leave tiny gaps

Mid: mix trees + bushes

Edge: bushes, tall grass, occasional tree

Avoid the “confetti” look

Never do “place 500 trees randomly across the whole zone”.
Instead:

Choose forest polygons/masks

Place trees inside mask, with density controlled by the field.

Clearings (forests need negative space)

Add 2–6 clearings in a forested zone:

clearings should be 10–30 tiles radius (vary)

some should connect to roads/trails

put a feature in 1–2 of them (log pile, stump circle, mushroom ring, small campsite)

Trails through forest

Even if your main roads are straight, trails can be slightly organic:

carve a 2–3 tile wide trail that meanders

occasionally widen into a 5×5 “rest spot”

avoid making trails that dead-end into dense tree walls (unless it’s intentional)

Understory and forest props

Forests look dead without understory.

Recommended distribution (within forest mask)

Bushes: common in edge/mid

Mushrooms: clusters in mid/core

Fallen logs/stumps: occasional, near clearings and along trails

Rocks: rare unless rocky biome

Cluster rule
Every “small prop” should spawn in patches, not singles:

pick patch centers

grow via random walk or small blob stamp

keep patches 8–25 tiles across for visual readability

Lake + Forest Interaction Rules (These make it look designed)

When a lake exists:

One bank can be “forested shore” (trees closer to water, logs, mushrooms)

Another bank can be “meadow shore” (grass/flowers patches)

Another can be “muddy shore” (reeds)

Do not make every shore identical.

Practical rule:

Split shoreline into 3–5 arcs (by angle) and assign a shore style per arc.

Common Failure Modes and Fixes

1) “All lakes look the same”

Vary: radius, bump count, shallow thickness, shore tile type, and whether it has an approach path.

2) “Forest = random dots”

Replace with: mask + density field + band rules.

3) “Too clean / too geometric”

Add shoreline noise and forest edge noise (small “nibbles” and “spurs”).

4) “Everything evenly distributed”

Introduce gradients and clumps.

Force some regions to be sparse and some dense.

Minimal Implementation Skeleton (pseudocode)
# Lakes
lake_centers = pick_centers(seed, count=3, avoid=[hub_bbox, major_roads])
for (cx, cy, r) in lake_centers:
    mask = organic_blob_mask(cx, cy, r, seed)
    paint_deep_shallow(mask)
    paint_shore_ring(mask, style=pick_shore_style(seed, cx, cy))
    decorate_shore(mask, clumps=True)

# Forests
forest_regions = pick_forest_masses(seed, count=2)
density = noise_field(seed, scale=large) + falloff_from_regions(forest_regions)
forest_mask = density > 0.25

place_trees_by_density(forest_mask, density, band_rules=True)
place_understory_patches(forest_mask, density, clearings=True, trails=True)

# Interactions
for lake in lakes:
    adjust_forest_density_near_lake(lake, style_by_shore_arc=True)

Output Checklist (before exporting the zone)

Lakes:

 Has deep + shallow, not just one water tile

 Has shore ring (sand/mud) with variation

 Has at least one nearby “used” feature (path/clearing/fishing spot) for some lakes

 Shore decor appears in clumps, not sprinkled

Forests:

 Trees form masses, not uniform scatter

 Forest edge is visibly sparser than core

 Contains clearings

 Contains understory patches (bush/mushroom/log), not singletons

 Trails/corridors exist through dense areas (or dense areas are intentionally blocked)