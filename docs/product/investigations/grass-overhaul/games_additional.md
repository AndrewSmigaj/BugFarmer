# Grass rendering — ADDITIONAL games (breadth pass)

Companion to `games_farming_sims.md` (Stardew + others) and `games_sandbox_survival.md`
(Terraria + Necesse). We already have DEEP findings on **Stardew, Terraria, Necesse** — this doc
covers the REMAINING games for breadth:

**Rune Factory (4/5) · Dinkum · Fields of Mistria · Roots of Pacha · Sun Haven · Core Keeper ·
Don't Starve · Forager · Moonlighter.**

Our engine: Unity 2D top-down farming game; tiles are ~16–32px PNGs rendered per-cell; shaders allowed.

**CONFIRMED** = stated/shown by a cited source. **INFERENCE** = my reading of screenshots/rips/mechanics
(flagged). Uncertainty called out explicitly. It is fine to record that a game's grass is flat/unremarkable
if that's the truth.

---

## SOURCE TABLE (URL → concrete technique → cost → fits a Unity tile-PNG(+shader) game?)

| # | Game | Source URL | Concrete technique it reveals | Cost/complexity | Fits us? |
|---|------|-----------|-------------------------------|-----------------|----------|
| 1 | Don't Starve | gamedev.net/forums/topic/700216 (via search summary; page 403'd on direct fetch) | Big hand-drawn ground texture per terrain w/ baked cracks/pits; **~5–6 texture variants/terrain picked pseudo-randomly**; **organic hand-drawn borders that weave between terrains, conforming to the edge** (not grid-aligned) | Med (border overlay + noise mask) | Border idea YES (fringe/alpha-mask edge overlay perturbed by noise); "one huge texture" NO for per-cell PNG |
| 2 | Don't Starve | dontstarve.wiki.gg/wiki/Grass_Turf (fetched) | Turf/grass is a discrete placeable/harvestable "chunk of ground"; ground detail lives in the texture, foliage is separate objects | Low | Confirms scatter-objects-on-floor model |
| 3 | Fields of Mistria | fieldsofmistria.wiki.gg/wiki/Field_Grass_2_Blades (fetched) | First-class **grass-detail decals** placed on grass tiles: "2 blades", flower, single-flower — each crafted, each with **4 SEASONAL variant sprites**; filed under Furniture→Ground | Low | YES — build the scatter layer as a CATALOG of tuft/flower/blade decals w/ seasonal recolor |
| 4 | Fields of Mistria | en.wikipedia.org/wiki/Fields_of_Mistria + fieldsofmistria.com/team (search) | GameMaker; dedicated lead pixel artist/animator; praised animation. Base = hand-authored tilemap (inference) | — | Confirms Stardew-lineage base + strong decal/animation layer |
| 5 | SLYNYRD (method) | slynyrd.com/blog/2019/8/27/pixelblog-20-top-down-tiles (fetched) | The canonical top-down-tile method these games follow: **16px common (≤32 "overkill")**; single grass tile = monotonous → mix flat + varied-density textured patches + **occasional flower variants**; dedicated **connection/transition tiles** to merge grass↔dirt; **few colors** per texture (too many = blurry); use negative space | Low | YES — direct authoring recipe for our PNG tiles |
| 6 | Sun Haven | sunhaven.wiki.gg/wiki/Floor_Tiles (fetched) | Grass "variants" (Grassy Flower / Grassy Stoney floor) are a **placeable décor/crafting** system, not the base renderer | Low | Confirms base-tilemap + placeable-grass-floor pattern; low new info |
| 7 | Core Keeper | core-keeper wiki: Biomes / Azeos' Wilderness / Meadow (search) | Grass = biome **Grass Block** floor; strong **per-biome recolor** (Meadow = orange/yellow, fireflies); scatter of **Tall Grass / Meadow Bush / Meadow Tree**; Unity | Low-med | YES — biome recolor + tall-foliage scatter over a plainish floor |
| 8 | Forager | en.wikipedia.org/wiki/Forager + Forager wiki Lands (search) | Deliberately **FLAT** grass; biomes = **floor recolor only** (green/orange/blue/dark/red); objects on top; GameMaker | Very low | Counter-example (the flat look we're leaving); only carry-over = cheap biome recolor |
| 9 | Moonlighter | 80.lv/articles/moonlighter-building-pixel-art-preparing-for-switch (fetched) | **"mesh deformations that look like pixel art"** + custom shaders for motion; NO dynamic lighting/normal maps (sprite superposition instead) | Med (shader) | YES for animation: **pixel-snapped vertex/skew deformation** for sway (not frames) |
| 10 | Dinkum | en.wikipedia.org/wiki/Dinkum + gamepressure (search) | 3D toy-like world (Unity/DX11) → grass = **billboard/detail-mesh 3D grass**, wind + player-bend shader | — (3D) | Behavioral spec only (tufts sway w/ per-instance phase, bend from player); render model N/A to 2D PNG |
| 11 | Roots of Pacha | ScreenRant / pixelsandcocoa reviews (search) | Stardew-lineage pixel art + seasonal palette shifts; no teardown | Low | Confirms genre standard (hand-painted variety + scatter + seasonal recolor) |
| 12 | Rune Factory 4/5 | en.wikipedia.org/wiki/Rune_Factory_5 + nexusmods RF5 texture mods (search) | 3D games — tiling grass texture + 3D grass-tuft meshes + wind shader | — (3D) | Essentially N/A to 2D PNG; behavioral spec only |

*Blocked on direct fetch (fandom 402/403, kleiforums 403, gamedev.net 403, gamemaker.io 403, grokipedia 403,
atma.gg 403): relied on WebSearch content summaries of those real pages — flagged inline as such.*

---

<!-- Per-game sections appended as research proceeds -->

## Don't Starve / Don't Starve Together (top-down-ish, hand-drawn)

Art direction is Tim Burton / Edward Gorey woodcut — a totally different palette from our game, but the
GROUND-BLENDING technique is a strong reference for "organic, non-gridded" edges.

**Base ground:** each terrain type (grass/grassland, forest, rocky, marsh, savanna, tundra…) is a
**large repeating ground TEXTURE with hand-drawn cracks/bumps/pits**, not a tiny 16px cell. It is drawn
on a floor mesh. There are roughly **5–6 texture variations per terrain type, selected pseudo-randomly**
across the map so the big texture doesn't obviously repeat. *(CONFIRMED via the GameDev.net teardown
thread summary — "a range of about 5 or 6 tile variations per element, get selected pseudo-randomly";
"gorgeously drawn cracks, bumps and pits.")*

**Transitions/edges — the headline technique:** boundaries between two terrain types **weave organically
in an irregular, hand-drawn line, NOT on the tile grid.** Each terrain has a **hand-drawn/sketched border
strip that conforms to (wraps around) the edge** of its region, so grass meets forest with a ragged inked
fringe rather than a stair-stepped tile seam. *(CONFIRMED, GameDev.net thread summary: "terrain boundaries
weave smoothly between neighboring terrain types in an organic fashion, with a border of each terrain that
appears hand-drawn and sketched, yet conforms to the boundary of the terrain wrapping around its edge.")*
Mechanically this is an **alpha-blended overlay layer**: the base ground of terrain A fills the region, and
a border/fringe texture of terrain A is drawn (with a soft/irregular alpha mask following a noise-perturbed
boundary curve) over the seam onto the neighbor. *(INFERENCE — the exact mask/shader is not stated in the
sources I could reach; the "weaving organic hand-drawn border that conforms to the edge" is the confirmed
observable, and an alpha-masked fringe overlay is the standard way to produce it.)*

**Detail/scatter:** turf/grass tufts, saplings, flint, berry bushes, spider dens etc. are separate world
objects placed on top (Perlin-driven distribution) — the ground texture itself carries most of the
"drawn" detail rather than a dense small-decal layer. Grass is also a harvestable object (grass tuft) that
is a distinct sprite, not part of the floor. *(CONFIRMED that turfs are placeable/harvestable discrete
items via dontstarve.wiki.gg Grass Turf; INFERENCE on distribution.)*

**Animation:** the GROUND does not sway. Motion comes from swaying grass-tuft/tree objects and ambient
wind on foliage sprites. *(INFERENCE from gameplay footage; ground turf is static.)*

**What makes it read rich (not a flat repeat):** (1) a **big, richly hand-drawn ground texture** with
baked cracks/pits (detail lives in the texture, not tiny cells), (2) **5–6 random variants per terrain**,
and above all (3) **irregular hand-drawn organic borders** between terrain types that hide the grid
entirely. The lesson for us: a **non-gridded, noise-perturbed fringe overlay at biome/material seams** is
what erases "tilemap" feel — even more than the base tile.

**Fits us?** The border technique is portable (an overlapping fringe-decal or an alpha-mask edge shader at
grass↔dirt/sand/water seams, perturbed by noise so the seam isn't straight). The "one huge texture per
terrain" model does NOT fit our per-cell PNG grid — for us the equivalent is many base variants + an
irregular fringe overlay. HIGH-VALUE takeaway: hide the grid at the EDGES, not just the field.

## Fields of Mistria (top-down pixel, GameMaker; the current "gold standard" cozy sim)

Engine: **GameMaker**; lead pixel artist/animator Alina Sechkin. Widely praised at 2024 EA launch for its
animation polish. Base tile grid reads as **16px-class hand-authored tilemap** (Stardew lineage).
*(CONFIRMED engine + team via en.wikipedia.org/wiki/Fields_of_Mistria and fieldsofmistria.com/team; base
tile size is INFERENCE from sprite rips / spriters-resource.)*

**Base grass:** hand-painted tilemap of grass with authored variety (like Stardew), NOT a single repeated
cell — INFERENCE from screenshots/rips (no dev quote reached). The farm "grass" is also a gameplay layer
you can grow/clear (Grass Starter item, grass spreads/respawns). *(CONFIRMED grass is a growable gameplay
terrain via wiki Grass Starter / "Can't plant grass" Steam threads.)*

**Detail/scatter — CONFIRMED and notable:** Mistria ships a whole **library of placeable grass-DETAIL
decals** that sit on top of a grass tile — e.g. **"Field Grass 2 Blades" (adds two blade tufts),
"Field Grass Flower", "Grass Tile Flower" (single flower)** — each crafted from **Sod** via woodcrafting,
each with **FOUR SEASONAL variant sprites (spring/summer/fall/winter)**, filed under Furniture → Farm &
Outdoor → **Ground**. *(CONFIRMED, fieldsofmistria.wiki.gg/wiki/Field_Grass_2_Blades.)* Wild equivalents
(field grass flowers) also spawn naturally on grass. So the detail layer is an explicit, first-class
**tuft/flower/blade decal system** — exactly the "scatter on top of base" pattern, here even exposed to the
player as décor with seasonal recolors.

**Color:** per-season look (the four seasonal decal sets confirm a strong seasonal palette; base tilemap is
likely season-swapped like Stardew — INFERENCE).

**Animation:** Mistria's foliage/grass visibly **sways and reacts** in-game and reviews single out the
animation, but I found **no dev source stating the mechanism** — treat "grass sways / parts around the
player" as **INFERENCE from footage, UNCONFIRMED mechanism**. Given GameMaker, most likely a shader or
per-sprite skew, same family as Stardew/Terraria. Flag as uncertain.

**What makes it read lush:** hand-authored base variety + a **rich, seasonal tuft/flower decal layer** (so
first-class the player can place it) + strong animation polish. **Fits us extremely well** — it is
essentially the Stardew recipe with a bigger, seasonal decal catalog. Takeaway: make the scatter layer a
proper CATALOG of blade/flower/tuft decals with seasonal recolors, not one tuft sprite.

## Sun Haven (top-down pixel, Unity; Stardew-like, higher-res)

**Base grass:** hand-authored tilemap (Stardew lineage), Unity. No published art teardown found.
*(INFERENCE from genre + screenshots.)*

**Placeable floors:** the visible "grass floor" *variants* are a **crafting/décor system** — e.g.
**Grassy Flower Floor Tile**, **Grassy Stoney Floor Tile** (each = Simple Earth Fertilizer + 50 Stone),
Sand Floor Tile, etc. — placed to CLEAR/decorate ground (they "prevent trees from growing"). These are
décor overlays, not the base terrain renderer. *(CONFIRMED, sunhaven.wiki.gg/wiki/Floor_Tiles.)*

**Transitions/animation/depth:** no confirmed sources. UNVERIFIED — do not rely on Sun Haven for the sway
or transition question. **Low research value for us**; it mainly re-confirms the "base tilemap + placeable
grass-detail floors" pattern shared by Stardew/Mistria.

## Core Keeper (top-down pixel, Unity; underground biomes)

Mostly a dark underground game (dirt/stone floors), but it HAS grassy biomes and they follow the
base-block + scatter pattern.

**Base grass:** **Grass Block** is a floor/ground block; **Azeos' Wilderness** (the "nature" biome beyond
the Great Wall) is "primarily composed of Grass Blocks… high density of grass and mold." Each biome has its
own recolored floor block. *(CONFIRMED, core-keeper wiki via search: Azeos' Wilderness / Biomes.)*

**Color / biome recolor:** strong per-biome recolor — e.g. the **Meadow** sub-biome is a yellow/orange
scheme (orange meadow grasses, yellow trees, lit by fireflies). Blocks are biome-specific: **Meadow Block,
Meadow Tree, Meadow Bush, Tall Meadow Grass.** *(CONFIRMED, search summary of Core Keeper Biomes.)*

**Detail/scatter:** separate **Tall Grass** and **bush/tree** objects grow on the grass floor (Tall Grass
is a harvestable that drops fiber; Tall Meadow Grass in the meadow) — a scatter layer of taller foliage on
top of the flat floor block. *(CONFIRMED, Core Keeper wiki Tall Grass / Meadow blocks.)* Being Unity + a
mostly-orthogonal top-down floor, ground blocks are almost certainly **autotiled** at biome edges
(INFERENCE — not a cited quote).

**Animation/depth:** no confirmed sway on the ground; the "alive" feel of the meadow comes from **ambient
critters/fireflies + tall foliage**, not floor motion (INFERENCE).

**What makes it read:** biome-recolored floor block + scatter of tall grass/bushes/trees + ambient light
(fireflies). Fits us as another vote for **biome recolor + tall-foliage scatter**; Core Keeper's own base
floor is fairly plain.

## Forager (top-down pixel, GameMaker; deliberately flat/minimalist)

**Honest read: Forager's grass is intentionally FLAT and minimalist — the counter-example.** Its clean look
comes from simplicity, not lush detail.

**Base grass:** near-flat green floor tiles; biomes are distinguished purely by **floor recolor** — Grass
(green), Desert (orange), Winter (light blue), Graveyard (dark), Fire (red). The Grass Biome is a 3×3 grid
of green-floored islands. *(CONFIRMED, en.wikipedia.org/wiki/Forager + Forager wiki Lands/Grass Biome via
search summary.)* Very few base variants; the aesthetic is deliberately clean/minimal.

**Detail/scatter:** resources (bushes, trees, flowers, rocks) sit on top as discrete harvestable objects,
but the *ground itself* carries almost no per-cell detail. *(CONFIRMED objects exist; INFERENCE that the
ground is near-plain.)*

**Animation/transitions:** minimal; edges between island biomes are simple. No notable grass sway.
*(INFERENCE from footage.)*

**Takeaway for us:** Forager shows the floor **recolor-per-biome** trick alone reads fine for a
*minimalist* style — but it is exactly the flat look we're trying to move BEYOND. Use only as the "what NOT
to do if you want lush" reference; its one portable idea is cheap biome recolor from one base.

## Moonlighter (top-down pixel, Unity; the "hi-bit pixel via shaders" reference)

Dungeon/shop ARPG, not a farming sim — grass/overworld is a minor part, so LOW value on the grass
question specifically. But it's a strong reference for the **animation-without-breaking-pixel-art** problem.

**Technique — CONFIRMED (Digital Sun dev interview, 80.lv):** they use **"custom shaders, mesh
deformations that look like pixel art, and camera post-processing"** to get effects "impossible in actual
retro systems." Notably they **do NOT use dynamic lighting or normal maps** — they fake light with
**superposition of sprites**. *(CONFIRMED, 80.lv "Moonlighter: Building Pixel Art & Preparing for Switch",
Javier Giménez.)*

**The transferable nugget: "mesh deformations that look like pixel art."** Instead of authoring animation
frames, they **deform the sprite MESH** (skew/wobble vertices) for wind/water/foliage motion, but keep the
result reading as clean pixel art (pixel-snapped). This is exactly the family of technique we'd use for
grass sway — a **vertex/skew deformation shader with pixel-snapping** so the swaying tuft never turns into
sub-pixel mush. *(CONFIRMED they use mesh deformation; INFERENCE that grass specifically uses it — the
interview didn't isolate grass.)*

**Base grass / scatter / transitions:** not documented; Moonlighter's world is mostly authored dungeon/town
tiles. UNVERIFIED — don't cite Moonlighter for the base-tile or transition questions.

**Fits us?** The *idea* fits well: animate via **pixel-snapped vertex deformation** (a shader), not frames —
same conclusion as Terraria. Moonlighter's other lesson (fake lighting by sprite superposition, no normal
maps) is a separate topic from grass.

## Dinkum (top-down camera but 3D world, Unity; NOT a 2D tile game)

**Important caveat: Dinkum is 3D, not 2D tiles.** "Simple but attractive three-dimensional graphics…
heavily simplified models that resemble toys," Unity + DX11. *(CONFIRMED, en.wikipedia.org/wiki/Dinkum,
gamepressure.)* So its grass is **3D detail-mesh / billboard grass on a 3D terrain**, not per-cell PNGs.

**Grass rendering (INFERENCE from the Unity 3D-grass norm + Dinkum footage):** grass tufts are **billboard
quads** (camera-facing textured quads) or short detail meshes scattered on the terrain, **GPU-instanced**,
with a **wind vertex shader** swaying the tops and typically a **player-bending "grass bending" shader**
(cf. the well-known Unity `GrassBending` approach) that pushes tufts aside as you walk. This is the standard
Unity toolchain for exactly this look. *(INFERENCE — no Dinkum dev source found on the exact shader;
flagged.)*

**Relevance to us:** LIMITED because we're 2D-PNG, not 3D. But the *behavioral* spec is the same one every
other game converges on and worth stealing conceptually: **many small tufts, each swaying on a wind field
with per-instance phase, that bend away from the player.** We just implement it in 2D (skew shader) instead
of 3D billboards.

## Roots of Pacha (top-down pixel, Stardew-lineage)

Stone-Age co-op farming sim, "gorgeous pixel art," vibrant warm palette, **seasonal environment shifts**.
*(CONFIRMED art style + seasonal shifts via reviews — ScreenRant, GameLuster/pixelsandcocoa; NO art
teardown found.)*

**Base grass / scatter / transitions / animation:** no confirmed technical sources. From genre + footage
(INFERENCE): a **hand-authored 16px-class tilemap** with authored variety + a scatter of flower/tuft
objects + seasonal palette swap — i.e. the **Stardew recipe** again. Do not rely on Roots of Pacha for any
specific mechanism; it's another data point that the farming-sim genre standard = hand-painted variety +
scatter + seasonal recolor, not runtime autotiled grass. LOW independent research value.

## Rune Factory 4 / 5 (3D games — least relevant)

**Both are 3D, not 2D tiles.** RF4 = 3D models on a mostly-fixed camera (3DS/Switch); RF5 = fully 3D open
world. *(CONFIRMED via en.wikipedia.org/wiki/Rune_Factory_5 + modding sites showing 3D models + textures,
e.g. nexusmods RF5 texture mods.)* Grass = **3D terrain with a tiling grass TEXTURE plus 3D grass-tuft
detail meshes** that sway with a wind shader — the standard 3D-engine approach.

**Relevance to us: essentially NONE for a 2D-PNG pipeline.** The only carry-over is the universal
behavioral spec (tufts sway on a wind field, denser near the player). Recorded here for completeness /
to close the list; not a source to design from.

---

## Top takeaways for us

Covered 9 games (6+ deeply enough to be useful; several thin because indie games rarely publish art
teardowns). The pattern from Stardew/Necesse/Terraria mostly HOLDS — **base variety + scatter decals +
bottom-anchored sway** — but this pass surfaced a few things that DIFFER or sharpen it:

1. **The genre standard is confirmed and boring-in-a-good-way:** hand-authored base tilemap variety +
   a scatter of tuft/flower decals + seasonal palette swap. Stardew, Fields of Mistria, Sun Haven, Roots
   of Pacha all do this. It's the safe, proven recipe — variants + scatter, NOT runtime-autotiled grass.

2. **NEW / differs — hide the grid at the EDGES, not just the field (Don't Starve).** The single most
   distinctive thing DS does is **irregular, hand-drawn, noise-perturbed borders that weave between terrain
   types off the tile grid** (~5–6 variants/terrain picked randomly too). Our Stardew/Necesse notes were
   all about the *field*; DS says the biggest "not-a-tilemap" win is an **organic fringe overlay at
   grass↔dirt/sand/water seams** (alpha-mask edge, perturbed so the seam isn't a straight stair-step). This
   is a distinct, high-value idea we didn't have.

3. **NEW — make the scatter a CATALOG with seasonal recolor, and consider exposing it (Fields of Mistria).**
   FoM's grass detail isn't one tuft sprite — it's a **library** ("2 blades", "flower", "single flower", …),
   each with **4 seasonal variants**, first-class enough to be player-placeable décor. Vote for a *set* of
   blade/flower/tuft decals with season recolors, not a single tuft.

4. **NEW — animate via pixel-snapped MESH/vertex deformation, not frames (Moonlighter + Terraria agree).**
   Moonlighter explicitly uses **"mesh deformations that look like pixel art."** Combined with Terraria's
   bottom-anchored skew, the confirmed best-practice for sway is a **vertex/skew shader that pixel-snaps** so
   the tuft stays crisp — cheap, and the whole industry converges here. No frame animation needed.

5. **Biome recolor from one base is cheap and universal (Core Keeper, Forager, all of them).** A single
   grass base + per-biome hue/value recolor (Core Keeper's Meadow = orange; Forager's 5 flat biome colors)
   is a trivial, ubiquitous trick. Fine as a *layer* on top of variety — but Forager proves recolor ALONE =
   the flat look we're trying to escape.

6. **The "alive" feel is scatter + motion + ambient life, rarely the base tile.** Across every game the base
   grass block is fairly plain; lushness comes from (a) **taller scattered foliage of varied silhouette**,
   (b) **that foliage MOVING** (wind + player-bend), and (c) ambient extras (Core Keeper's fireflies). Design
   effort should go to the scatter/animation layer, not a fancier base cell.

7. **3D games (Dinkum, Rune Factory 4/5) are NOT reference material for our render** — they use 3D
   billboard/detail-mesh grass. They only reconfirm the universal *behavioral* spec: many tufts, per-instance
   wind phase, **bend away from the player** (Unity `GrassBending`-style). Implement in 2D as a skew shader.

8. **Honest negatives:** Sun Haven, Roots of Pacha add little beyond "genre standard"; Moonlighter/Dinkum/RF
   are off-genre (dungeon / 3D). Forager is a deliberate flat counter-example. The two genuinely new,
   high-value ideas from THIS pass are **(#2) organic noise-perturbed edge fringes** and **(#3) a seasonal
   decal catalog** — plus **(#4)** hardening the "sway = pixel-snapped vertex skew" conclusion.

**Source count:** 12 sources logged (5 deep-read in full via WebFetch: DS Grass Turf, FoM Field Grass decal,
SLYNYRD method, Sun Haven floors, Moonlighter 80.lv interview; ~7 more extracted from WebSearch summaries of
real wiki/forum/encyclopedia pages that blocked direct fetch — flagged in the table). Several fandom/forum/
dev pages 402/403'd; where a claim rests only on a search summary it is marked, and inference is separated
from confirmed throughout.
