# Grass Rendering in 2D Sandbox / Survival / Crafting Games — Research

Research for the grass-overhaul design. Target look named by owner: **Necesse**.
Our engine: Unity 2D top-down farming game; tiles are ~16px PNGs rendered per-cell; shaders allowed.

Games covered: Terraria (side-view, but grass-blade-overlay + wind is highly relevant), Core Keeper,
Necesse, Don't Starve, Forager, Moonlighter.

Status: IN PROGRESS — findings appended per source as research proceeds.

---

## SOURCE TABLE

| # | Game | Source URL | Concrete technique | Cost/complexity | Fits Unity tile-PNG (+shader)? |
|---|------|-----------|--------------------|-----------------|-------------------------------|
| _(filled in as sources are read)_ |

---

## Per-game findings

### TERRARIA (side-view, but the grass-blade-overlay + wind technique is the key reference)

**Tile size + grid:** 16×16 px tiles. Everything is on a 16px grid. (CONFIRMED — Terraria native tile is 16×16.)

**Is grass a base tile, autotiled, or base+overlay?** BOTH autotiled base AND scattered overlay:
- The grass BLOCK itself is **autotiled and biome-specific** — forest grass, corrupt grass, crimson grass,
  jungle grass (grows on mud, not dirt), hallowed grass, ash grass, mushroom grass. Each biome recolors the
  whole grass block set. (CONFIRMED, `terraria.wiki.gg/wiki/Grass`.)
- On TOP of the flat grass block, **separate decorative "wild plants" grow as their own tiles**: tall grass
  tufts, weeds, flowers, herbs, mushrooms, vines hanging below. "Weeds and flowers grow naturally on the
  different types of grass on the surface." These are the tall silhouette detail — the base block is short/flat,
  the *plants* give height and life. (CONFIRMED.)

**Grass spread / edges:** Grass spreads only to an adjacent block within the 8 surrounding tiles, and only if
that block has open (non-enclosed) space next to it — so grass creeps along exposed dirt surfaces and stops
where buried. Meets dirt/stone by autotile framing (a fringe/blend edge tile). (CONFIRMED.)

**Animation — THE key part:** Terraria added a **wind system in 1.4 (Journey's End)**. Wind blows east or
west, `windSpeedCurrent`/`windSpeedTarget`, 0–60 mph; a "Windy Day" event triggers above 20 mph. Wind sways:
**all tall grasses, plants (herbs/mushrooms/acorns), vines, tree tops + dropped leaves, banners, lanterns,
kites, pinwheels**. It is a **visual-only ambient effect** (no gameplay impact). Leaves drop more frequently
at higher wind speed and the leaves themselves drift with wind. (CONFIRMED, `terraria.wiki.gg/wiki/Wind`.)

**HOW the sway is implemented (concrete, portable):** Terraria has **NO vertex shaders** — the sway is
**CPU-driven in `TileDrawing`**. Foliage/vine tiles are registered as special draw points via
`TileDrawing.AddSpecialPoint(...)` with `TileCounterType.MultiTileVine`; single 1×1 swayers use
`TileID.Sets.WindSwayBasic`. Each frame the draw code **rotates/skews the sprite quad** so the TOP of the
tile leans with the wind while the BASE stays anchored (`dontRotateTopTiles` toggles which cells rotate).
Tunable params: `windPushPowerX`, `windPushPowerY`, `overrideWindCycle`, `totalWindMultiplier`. Player
walking through also pushes the foliage (same special-point path handles wind AND player interaction).
(CONFIRMED — tModLoader `TileDrawing` API + PR #4429 "Multi-Tile Wind Sway".)
→ Takeaway: the sway is a **per-sprite skew/rotation anchored at the bottom edge**, phase offset per tile,
driven by a global wind value + a per-tile position offset. This is exactly what a cheap Unity sprite
**vertex/skew shader** does — no CPU cost needed on our side.

**Directly-portable Unity confirmation:** the well-known **"2D wind sway" shader** (GodotShaders, ported in
the itch.io *Interactive Foliage* asset) does precisely this: a vertex shader **skews the sprite by UV.y**
(top of the sprite displaces, bottom pinned) using a **sine wave over time + world-position offset**, and
adds a **velocity-based skew from the player** so grass bends away as you run through it. Materials are set
"local to scene" so each tuft has an **independent phase** (no uniform marching). Trivially cheap; the exact
same shader runs in Unity URP/built-in. (CONFIRMED technique; engine-agnostic.)

**What makes Terraria grass read as alive (not a flat repeat):** it's NOT the base block — it's the (1) tall
**overlay plants/tufts/flowers of varied silhouette** breaking the flat top edge, plus (2) **hanging vines**
below ledges, plus (3) the whole thing **swaying in wind + reacting to the player**. The base grass block is
almost plain; the life comes entirely from scattered tall foliage decals that MOVE.

---

### NECESSE (top-down; the OWNER'S NAMED TARGET LOOK)

**Tile size + grid:** **32×32 px tiles** (higher-res than Terraria's 16px). CONFIRMED by dev — the grass
spritesheet is 32×224 = seven 32×32 sprites. (`steamcommunity.com/app/1169040` grass-texture thread,
developer "Fair".)

**Is grass a base tile, autotiled, or base+overlay? — THE load-bearing finding:** the grass tile is a
**flat base tile with SEVEN variant sprites, and a random variant is picked per grass cell**. Dev Fair,
verbatim: *"the grass tile texture is a spritesheet of 32×32 resolution sprites… A random one is then picked
for each grass tile."* This **per-tile random-variant selection is the single biggest reason Necesse grass
doesn't read as a repeating stamp** — every cell is one of 7 subtly different tufts. (CONFIRMED, dev quote.)

**Variants / color:** two authored *kinds* of grass — normal grass and a **darker "overgrown grass"**
variant (planted with Overgrown Grass Seeds) — on top of the 7 texture variants per kind. Each **biome
recolors the ground/grass** (forest green, snow white, desert sand, swamp) — biome determines "how the
surface will look." (CONFIRMED, `necessewiki.com/Grass_Tile`, `/Biomes`.)

**Grass detail overlays (scattered ON TOP):** Necesse scatters a dense set of **separate plant/decoration
sprites** on the grass — tall grass tufts, **sunflowers, firmone, blueberry bushes, oak/spruce saplings**,
and other purely-decorative plants — "plants mostly grow naturally in all biomes." Grass "slowly spreads to
nearby dirt tiles." So the look = flat 7-variant base + a scatter layer of taller flowers/bushes/tufts.
(CONFIRMED, `necessewiki.com/Plants`, `/Forest_Biome`.)

**Transitions/edges:** not documented in dev sources I found — INFERENCE (flag uncertain): Necesse visibly
uses **soft/feathered autotile borders** where grass meets sand/dirt/water (the frequent player critique is
that the pixel art is "too smooth / blurry," consistent with anti-aliased/blended transition tiles rather
than hard 16px steps). Treat as inference, not confirmed.

**Animation:** no authoritative source found confirming grass sway in Necesse — UNCERTAIN. Water surface and
trees appear to have gentle animation; whether the grass tufts themselves sway is UNVERIFIED. Do not assume
Necesse's "alive" quality comes from motion; the confirmed drivers are (a) 7 random variants/tile and
(b) dense decorative-plant scatter.

**Depth/layering:** taller decorations (bushes, saplings, flowers) draw ABOVE the flat grass and Y-sort with
entities; the base grass is a floor layer. (INFERENCE from how top-down tile games layer; not a cited quote.)

**What makes Necesse grass read as lush (the target):** CONFIRMED = **(1) 7 randomized base-tile variants per
cell** (kills the repeat) + **(2) a dense scatter of varied, taller decorative plants** (sunflowers, bushes,
tufts, saplings) that break the flat floor with silhouette and brighter accent color + **(3) per-biome
recolor + a darker "overgrown" second grass**. The base is deliberately simple; variety + scatter do the work.
→ For us this is the cheapest highest-impact recipe: author ~6–8 grass variant PNGs and pick one per cell,
then scatter tuft/flower decals.

---

## Top takeaways for us
(Agent covered Terraria + Necesse deeply before an API failure; Core Keeper / Don't Starve / Forager /
Moonlighter not yet covered — lower priority, they confirm the same pattern. Distilled by me from the above.)
1. **Necesse (the owner's target) is confirmed the "cheap + high-impact" recipe:** a flat base grass tile with
   **~7 variant sprites picked at RANDOM per cell** (dev quote) + a **dense scatter of taller decorative
   plants** (flowers, bushes, tufts, saplings) + **per-biome recolor** + a 2nd darker "overgrown" grass. The
   base is deliberately simple; **variety-per-cell + scatter do the work.** Necesse grass may NOT even sway —
   its lushness is variants + scatter, not motion.
2. **Terraria is the WIND reference:** sway = **per-sprite skew/rotation anchored at the bottom edge**, top
   leans with a global wind value, **per-tile position phase offset** (no unison), and the **player pushes
   foliage** through the same path. Terraria does it CPU-side; the identical effect is a trivial **2D vertex/
   skew shader** (skew by UV.y, sine-over-time + world-pos offset, + player-velocity bend). Engine-agnostic → runs in Unity.
3. Across both: the **base grass block is almost plain**; life comes from **taller scattered foliage of varied
   silhouette** that (Terraria) MOVES. Necesse gets there with variety+density even mostly static.
4. Direct implication for us (we use ONE flat tile, no variants, sparse scatter): the single biggest wins are
   **(a) many grass-tile variants + random-per-cell selection** and **(b) a proper dense tuft/flower scatter
   layer** — before any shader work.
