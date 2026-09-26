# Grass rendering in top-down farming / life-sim games

Deep-read research for the grass overhaul. Focus games: **Stardew Valley, Rune Factory (3/4/5),
Fields of Mistria, Dinkum, Roots of Pacha, Sun Haven.**

Per game we want: tile size + grid; base tile vs autotile vs base-color-plus-decals; grass detail
tufts/blades/flowers as scattered decals (density, random placement/rotation/variant); color
variation (variants / hue jitter / seasonal / gradients); transitions to dirt/path/water/sand;
animation (sway — frames vs shader — and player reaction); depth/layering (shadow, overlap with
player); and THE key question — what specifically makes the grass read as lush/polished rather than
a flat repeating tile.

**CONFIRMED** = stated by a cited source. **INFERENCE** = my reading of screenshots/rips/mechanics
(flagged). Uncertainty is called out explicitly.

---

## Source table (URL → concrete technique → cost/complexity → fits our Unity tile-PNG + shader game?)

| # | Source (URL) | Game | Concrete technique it reveals | Cost / complexity | Fits us? |
|---|--------------|------|-------------------------------|-------------------|----------|
| 1 | raw.githubusercontent.com/veywrn/StardewValley/.../TerrainFeatures/Grass.cs (decompiled source) | Stardew | Grass tufts are a **separate terrain feature** over the base ground: up to **4 blades/tile in a 2×2 sub-grid**, each blade one of **3 variants** (15×20px), per-blade offset arrays; **seasonal recolor = row offset in one sheet** (spring 0 / summer 20 / fall 40 / cave 60 / frost 80 / lava 100); **per-tuft rotational sway** (shake, maxShake=π/8, rate=π/80, decay=π/350) triggered by **player walking through** (doCollisionAction + "grassyStep" sound) | Low-med: a scatter layer of small blade sprites + a rotate-on-collision shader/transform | YES — maps cleanly to a decal layer + vertex/rotation shader over our PNG tiles |

---

<!-- Sections appended per game as research proceeds -->

## 1. Stardew Valley

Stardew has **two distinct grass systems** that stack, and the distinction is the biggest single lesson:

**(A) The base ground grass = a hand-painted 16×16 tilemap.** All outdoor ground is drawn from
per-season outdoor tilesheets (`spring_outdoorsTileSheet`, `summer_…`, `fall_…`, `winter_…`) placed
in Tiled maps. Tile size is **16×16 px** (source), rendered at 4× on screen. This is NOT autotiled
grass generated at runtime — it is **hand-authored variety**: the tilesheet contains many grass tile
variants (plain, with pebbles, small flowers, darker/lighter clumps, dirt fringes) that the map
artist scatters by hand so the field never reads as one repeating cell. Seasonal look = a *different
tilesheet* swapped per season (spring lush green, summer yellow-green, fall orange, winter tan/snow).
*CONFIRMED (Modding:Maps + tilesheet mods) that maps are 16px Tiled tilesheets; INFERENCE that the
"lush" read comes mostly from hand-placed tile variety — consistent with all tilesheet rips.*

**(B) The grass terrain feature = scattered swaying tufts on top.** This is the spreadable grass you
grow/scythe for hay. CONFIRMED from decompiled `Grass.cs`:
- **6 grass types**: springGrass(1), caveGrass(2), frostGrass(3), lavaGrass(4), caveGrass2(5), cobweb(6).
- Each grass tile holds **up to 4 weeds/blades** (`numberOfWeeds`, max 4), laid out in a **2×2 grid**
  within the tile — so density per cell is randomized 1–4.
- Each blade is drawn from `new Rectangle(whichWeed[i]*15, grassSourceOffset, 15, 20)` → **3 horizontal
  variants**, each **15px wide × 20px tall** (taller than the 16px tile → blades stick up above the cell).
- **Seasonal/type recolor is a vertical ROW OFFSET into a single sheet** (`grassSourceOffset`): spring 0,
  summer 20, fall 40, cave 60, frost 80, lava 100. One texture, offset picks the palette — cheap.
- Per-blade positional jitter via `offset1..offset4` arrays (each of the 4 slots has its own wobble),
  so tufts don't line up.

**Animation / player reaction (the polish):** grass **sways by per-tuft rotation**, not sprite frames.
`shake()` sets `shakeRotation` with `maximumShake = π/8`, `defaultShakeRate = π/80`, and it decays at
`π/350` in `tickUpdate()`. Critically the sway is **triggered by the player walking through**:
`doCollisionAction()` calls `shake()` with rotation scaled by the player's collision speed/velocity and
plays the `"grassyStep"` sound. So tufts bend away from the player and spring back — that reactive bend
is a large part of why the field feels alive. *(Ambient/weather wind on grass is minor; the dominant
motion is walk-through reaction. CONFIRMED shake is collision-driven; ambient wind not evident in Grass.cs.)*

**Transitions:** grass→dirt/path/water edges are **hand-painted transition tiles in the tilesheet**
(fringe tiles with grass overhanging dirt), not a runtime autotiler. Tilled soil (hoe dirt) is its own
terrain feature drawn over the grass with its own autotiled 16-tile border set.

**Depth/layering:** blades are 20px tall over a 16px cell so they overlap upward; player draws over/under
by Y-sort. No separate drop shadow on individual blades (the base tile art bakes in shading).

**What makes it read lush (not flat):** (1) hand-painted base-tile *variety* + seasonal tilesheet swap;
(2) a scatter layer of taller tufts at randomized density (1–4) and 3 variants with per-slot jitter;
(3) **reactive per-tuft bend when you walk through**, with a footstep sound. It is deliberately NOT a
single repeating grass tile.

**Fits us?** Very well. We already load 16px PNG tiles per cell; we can (a) author several base grass
tile variants + value jitter, (b) add a scatter decal layer of 2–3 tuft sprites at randomized
density/rotation, and (c) add a walk-through rotational bend (shader or per-decal transform) + a grass
footstep sound. The row-offset-per-season trick is trivially portable.
