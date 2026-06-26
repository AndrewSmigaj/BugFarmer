# Feature guide: cliff edges, mine entrances & surface work-camps

How to author the **surface→underground transition** — the cliff face, the cave mouth, and the
open-air **work-camp** that clusters around a mine head. Worked example:
`tools/zonegen/scenes/scene_mine_entrance.py` (render it, read the PNG against §5).

> **Why this guide exists:** left alone an LLM lays a **flat** cliff line, a **ruler-straight** road,
> and **salt-and-peppers** props evenly across the grass (one tent here, an anvil there, a forge in a
> field). That reads as a debug dump, not a place people work. A real camp is a few **organised
> work-sites**, each a tight functional cluster, linked by trodden paths. The rules below are the
> nudges; build with them, then **look at the render and check the "tells" in §5.**

## 0. Orientation (the one that bit us)
**North = HIGH y = the TOP of the render** (`make_scene.py` flips Y; `zone.go` "+Y = north").
The **surface camp + cliff lip go at HIGH y**; the mine **descends toward LOW y** (deeper = south =
bottom). Author the entrance at high y and it renders north-up. *(We shipped this upside-down once by
putting the entrance at low y — the fix is always the ZONE, never the render flip.)*

## 1. The cliff / grass↔rock edge — IRREGULAR, with a broken base
The boundary where grass meets cut rock is **never a straight horizontal line**.
- Wobble it with a **noise field**: `surf_y[x] = base + round(amp * (noise-0.5)*2)` (amp ≈ 4–6 cells).
  Grass fills `y >= surf_y[x]`; rock is carved/filled below.
- **Break the base:** scatter a thin band of `rubble` (+ the odd `standing_stone`) in the 1–2 rows
  just *above* the rock line, so the cliff crumbles into the grass instead of meeting it cleanly.
- **Tell:** if the grass/rock seam is a flat ruler, raise the amplitude or re-seed.

## 2. The mine mouth + the descent (man-made, and it must SHOW why)
- The **cave mouth** is a `carve_cavern(shape="rocky")` bitten **up into** the cliff at the lip.
- The descent is a **STRAIGHT** `carve_tunnel(style="straight")` — straightness only reads as
  *intentional* when it carries **infrastructure**: lay `mine_rail` down the centre and `mine_support`
  timbers at intervals (every ~5 cells, flanking). A bare straight tunnel looks like a mistake.
- **Don't end in a symmetric hourglass.** Mouth → shaft → one big cavern, drawn dead-centre and
  mirror-symmetric, is the giveaway. Break it: **offset** the main cavern, use `shape="lobed"`, and
  branch a short **natural** side-tunnel to a small **side-dig** (`shape="rocky"`, a parked `mine_cart`).
- **Dress the void** (see caves.md §2–3): a still `place_pool` in a low spot, `mushroom_glow`/
  `mushroom_blue`, `crystal_small`, `bone_pile`, `rubble`, and a few staged `ore_pile`s.

## 3. The work-camp — ORGANISED clusters, never salt-and-pepper
A camp is **3–6 tight functional clusters** on the grass apron, each placed as a unit with its tools
**adjacent**, then linked to the road by trodden `trail`s. Place a cluster by an anchor `(cx, cy)` and
offset its members by a few cells — **do not** spread the same prop evenly across the field.

| Cluster | Anchor piece | Clustered with it (adjacent) | The rule it encodes |
|---|---|---|---|
| **Campsite** | `campfire_spit` | tents **RINGED** around the fire (not a row), `log_seat`s facing in, `cooking_pot` on the fire, `well`, `barrel`/`crate`/`chest_wood` | people sit *around* a fire; tents face it |
| **Smithy** | `forge` + `anvil` **side by side** | `coal_bin`, `water_bucket` (quench), `tool_rack`, `workbench`, fuel `keg`, `sign_anvil`, staged `ore_pile` | a forge is a workstation, not scattered furniture |
| **Mine-head** | the rail head at the mouth | `mine_cart` on the rail, `ore_pile`/`ore_sack`, `sign_camp`, `lantern`, `powder_keg`, `ladder` | the loading point sits **at** the mouth |
| **Processing** | `ore_sluice` **at the pond edge** | `pond` (+ `reeds` rim), staged `ore_pile`/`ore_sack`, `wheelbarrow` | a sluice needs water beside it |
| **Lumber yard** | `sawmill` | `sawhorse`×2, `lumber_rack`, `crate` | the **timber** for the mine supports is cut on-site |
| **Quarry scar** | `stonecutter` | `standing_stone`/`rubble` spoil, `sandstone_formation`, `ore_pile` | cut stone leaves a worked scar, not tidy rocks |
| **Storage** | `lumber_rack` | `crate`/`barrel` stacks, `notice_board` | bulk goods in one corner |

**Spacing rule:** members 1–3 cells apart inside a cluster; clusters far apart with **open ground +
paths** between them. The emptiness between clusters is what makes them read *as* clusters.

## 4. Roads, gates & lighting
- The **main road** runs from the **north edge** (the village neighbour) down to the **mine mouth**,
  and **MEANDERS** — a single smooth arc (`cx = mx + round(A*sin(t*k))`), never a straight column.
  Lay it **first** so clusters sit *beside* it. Use `roads.md`'s `terrain.path` for a full zone.
- **Gate the lip:** run a `fence_wood` guard-rail along the cliff edge flanking the mouth, leave the
  road/rail gap **open**, and frame it with `gate_wood`. Put a `signpost`/`sign_camp` where the road
  enters from the north.
- **Light the worked path:** `lamp_post`/`lantern` beside the road and at each cluster — a working
  camp is lit at night.
- **Trodden links:** thin `trail`s (dirt/path) from each cluster to the road — feet wear paths.

## 5. Build → render → review — the "tells" to check
```bash
python3 tools/zonegen/scenes/scene_mine_entrance.py    # build + render + print lint
```
Read the PNG (north at TOP) and verify:
- **Cliff edge is irregular** with a broken rubble base — not a flat line.
- **The descent is straight WITH rail + supports**; the cavern below is **off-centre / not a symmetric
  hourglass** (offset + a side-dig), and dressed (pool, glow, crystal, staged ore).
- **Every prop belongs to a cluster** — no lone anvil/tent/forge marooned in the grass. Tents ring the
  fire; forge+anvil are adjacent; the sluice is at the water.
- **The road meanders** from the north edge to the mouth and is gated + lit; paths link the clusters.
- **A few tree stands + clumped flora** (`vegetation.md`), not an even sprinkle.
- `b.lint()` clean, **0 placement warnings**, **0 missing_art** (placeholders mean a sprite is absent —
  e.g. `boulder` has none; use `standing_stone`/`rubble`).

New objects with no art render as labeled placeholders — log them in `docs/product/art_needed.md`
(add-object skill). Underground specifics (tunnels/caverns/ore/water) live in **caves.md**; the
road-angle/wander rules in **roads.md**; scatter density/clumping in **vegetation.md**.
