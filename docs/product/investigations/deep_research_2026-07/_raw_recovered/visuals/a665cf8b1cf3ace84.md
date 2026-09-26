I'll start by reading the target document in full and exploring the repo structure in parallel.

---

I've read the doc. Now let me ground the repo claims and load web research tools in parallel.

---

Now let me dig into the repo persistence/client path and fire off the key web research in parallel.

---

Strong signal already. Let me verify the URP Sprite Light claim against the actual Unity 6 docs, check the client light setup, examine the save/persistence format, and research the recompute-cost and Necesse claims.

---

Two big findings emerging: the client ALREADY uses a Multiply-blend global light, and the collision map is server-derived (not authored save data). Let me read the day/night controller in full and verify the URP Sprite-light-runtime-texture claim with a concrete source.

---

The DayNightController comment (lines 68-71) is a smoking gun: the client ALREADY accumulates global lights into a Multiply blend texture. Let me verify how URP 2D lights actually combine within/across blend styles, whether a global light can be masked per-cell, and research the darkness techniques the doc omits.

---

Unity's own docs confirm the critical constraints. Let me verify the roof-mask persistence gap concretely: does the zone save format persist any per-cell mask today, or only ground + occupants?

---

I have everything I need. Repo grounding confirms the persistence gap and the pre-existing Multiply global; Unity's own docs confirm the URP constraints that break the doc's headline render path. Here is the assessment.

---

# Adversarial review: `research_lighting_dark_underground.md`

I read the doc in full, grounded every repo claim it makes, and verified the two load-bearing technical assertions against Unity's own URP docs. There are real, material problems — three of them are not "unproven," they are **affirmatively wrong** and would send the design phase off to score a candidate that can't be built as written.

## Findings, most-material first

### 1. Mechanism-2's headline render path is impossible with URP global lights. "Sun applies ONLY to roofless cells" cannot be done with the day/night Global Light2D.
- **What's wrong:** §4 mechanism-2 and §6 say the fix is "sun (day/night Global) applies ONLY to roofless cells; roofed cells fall to a dark cave-ambient floor." §7 route 2 then sells "One Sprite Light 2D … on a Multiply blend … composites with the existing Global + point lights for free … Lowest-risk." This is the single most important claim in the doc and it is contradicted by URP's design.
- **Evidence:**
  - Unity 6000.4 *Light 2D component reference*: **"Global Lights cannot be given sprites, cookies, or masks. They are uniform across targeted areas,"** and **"Only one global Light can be used per Blend Style, and per sorting layer."** (https://docs.unity3d.com/6000.4/Documentation/Manual/urp/2DLightProperties.html) A Global Light2D is all-or-nothing across the sorting layer — there is no per-cell "apply sun only where roofless." So mechanism-2 as literally described ("sun only on roofless cells") is not achievable by configuring the existing global.
  - URP *Light Blend Styles* doc: **Multiply "Darkens the sprite by reducing brightness"** and blend mode "controls the way a Sprite is lit by light" — i.e. Multiply is how the **accumulated** light texture is applied to sprites, not how two lights combine. Lights within a blend style combine by **Overlap Operation (Additive / Alpha Blend)** (https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@7.2/manual/LightBlendStyles.html). So "put a Sprite Light on Multiply to darken a region and it composites with the global for free" mis-models the pipeline: with **Additive** overlap a dark/black sprite light adds ~0 and cannot pull a cell below the global's white fill (no darkening at all); only **Alpha-Blend overlap + a Light Order that overwrites the global** darkens — which fights the "one global per blend style" rule and is emphatically not "for free."
  - The repo already learned this the hard way: `BugFarmerClient/Assets/Scripts/World/DayNightController.cs:68-71` — *"URP 2D accumulates all global lights into the Multiply blend texture, so a stray scene global at full intensity pins the world bright and defeats the night ramp (the long-standing 'night isn't dark' bug…)."* The project's ambient is **already one Multiply-blend global**; the doc never mentions this and treats the Multiply blend slot as unused.
- **Fix:** Correct §7. The **custom fullscreen Blit ScriptableRendererFeature** (route 1) that samples the roof/darkness lightmap and multiplies it into camera color is the *only* route that actually delivers "sun only where roofless"; the Sprite-Light-Multiply route (currently sold as "lowest-risk" and the recommended start in §10.3) should be **demoted or struck**, with a note on the single-global-per-blend-style / uniform-global constraint and the existing Multiply global in DayNightController. The ranking in §10 is currently inverted.

### 2. The roof-mask persistence + netcode path is a hand-wave, and the "reads it like OpCode 106" analogy is factually wrong.
- **What's wrong:** §6/§8/§10.2 say "Emit a per-cell `roofed` mask into the saved zone … Ship it in the save; **client reads it like it already reads the zone collision map via OpCode 106**." That analogy is doubly false, and it hides an entire from-scratch data pipeline.
- **Evidence:**
  - OpCode 106 does **not** carry authored save data — it carries a **server-derived set**: `nakama/modules/world/match.go:2793-2794` calls `state.BlocksBugsCells()` and marshals it; `state.go:706` computes that set; it's derived from occupant `World.BlocksBugs` (`entities.go:118`, `handlers_world.go:543/680`). The client just hydrates the received cell arrays: `TilemapManager.cs:1241-1246`. There is **no existing "authored per-cell mask flows from save to client" pipeline** to piggyback on.
  - The save format has **exactly two per-cell arrays and no room for a third**: `tools/zonegen/zonebuilder.py` `save()` writes `json.dump({"chunk_x":…, "chunk_y":…, "ground": ground, "occupants": occ})` — only `ground` + `occupants`. The builder's other two masks (`surface`, `reserved`) are **authoring-only and dropped on save** (docstring lines 7-8; they never appear in the chunk dump).
  - zonegen has **no roof concept at all**: `tools/zonegen/features/cave.py` `carve_tunnel`/`carve_cavern` return a *local* `carved` set; `fill_solid` just places block occupants in non-carved cells. Nothing marks or retains "this open cell is roofed," and nothing persists it.
- **Fix:** Add a real "roof-mask data path" section spanning all five hops the doc currently elides: (a) a builder API to record roofed cells (a third grid, or derive `roofed = interior-of-a-carved-region` at save), (b) a new per-cell `roofed` array in `chunk_X_Y.json`, (c) a Go loader change to parse it into the chunk struct, (d) a **new** OpCode (or fold into chunk sync) — 106 is the wrong wire since it ships a derived set, and (e) client hydration/storage parallel to `_blocksBugsZoneWide`. Call it what it is: a new end-to-end feature, not "like the collision map."

### 3. "Full 256² recompute is sub-millisecond" is asserted with zero benchmark and is likely false on the implied HashSet path.
- **What's wrong:** §5/§8/§10.1 lean the entire "no incremental machinery needed" conclusion on "full recompute is sub-millisecond," with no measurement and no mention of Burst/jobs/array layout.
- **Evidence:** The signal the doc names is the `HashSet<Vector2Int> _blocksBugsZoneWide` (§4, and `TilemapManager.cs:40`). A 4-pass directional sweep (5B) over 65,536 cells is ~262k cell updates, each probing neighbor solidity — on the order of ~1M `HashSet<Vector2Int>.Contains` calls per recompute, each hashing/boxing a struct through Unity's Mono/IL2CPP. That is realistically **multiple milliseconds + GC pressure**, not sub-ms. Corroborating that tile-flood lighting is *not* trivially cheap: Terraria ships a dedicated **Multicore Lighting** option precisely because lighting recompute is its heaviest CPU task (https://terraria.fandom.com/wiki/Settings). "Sub-ms" is only plausible with a flat `byte[]`/`NativeArray` solid grid and ideally Burst — none of which the doc specifies; it explicitly hands you the HashSet.
- **Fix:** Either benchmark it and cite the number, or (better) spec the implementation the claim requires: convert the HashSet to a flat `byte[65536]` grid once per zone, run the sweep/BFS over the array, and note Burst/Job as the fallback. Until then, drop "sub-millisecond" or mark it "target, unverified — must measure." The per-frame-window-recompute option in §8 especially needs this, since a multi-ms flood at 60 fps is a real frame cost.

### 4. Missing failure mode: the compositing ORDER between the static multiply-darkness overlay and the moving additive carried light is unspecified — and as drawn it re-darkens torch pools to black.
- **What's wrong:** §4/§7 present "two clean layers": mechanisms 1&2 = a **Multiply** darkness overlay, mechanism 3 = **additive** carried light that "composites over the top." But it never states the order of operations, and the naive reading breaks. If the darkness lightmap is a fullscreen Multiply applied *last*, the frame math is `(scene + torch_light) × darkness`; in a roofed cell `darkness ≈ 0`, so even a lit torch pool → black. The carried player/lamp lights are **moving additive Light2Ds** (`LampLight.cs` `PlayerNightLight` / `LampLight`), i.e. they live *inside* the existing light accumulation, not "over the top" of a post-multiply.
- **Evidence:** `LampLight.cs` (whole file): lamps and the player night light are runtime `Light2D` point lights driven by `DayNightController.Daylight`; the flashlight cone is another `Light2D`. These are additive contributors to the same Multiply blend texture as the global — so a subsequent multiply-darkness overlay would multiply their result back down. Unity docs (finding 1) confirm within-blend-style combination is additive/alpha, not "additive layer floating above a separate multiply."
- **Fix:** The doc must specify that to let carried lights punch through roofed dark, the moving light must be composited **into the lightmap before the multiply** (mechanism-3 feeds the same lightmap the flood writes) — which contradicts "static, recompute only on dig" and forces a per-frame carried-light pass. Add an explicit "order of operations / how a torch reveals a dark cell" subsection resolving this; it is the central unsolved compositing question and the doc currently declares it "clean" without solving it.

### 5. A cheaper/cleaner shipped technique is under-weighted (GPU blur-as-propagation) and two simpler models are omitted entirely.
- **What's wrong:** The doc commits to CPU per-cell flood (§5A/5B) as primary and files the GPU **blur-as-propagation** route (§7b, BigDaddyGameDev) under "won't port → upgrade path." Given findings 1 and 3, that ranking is backwards: rendering the solid/roof mask to a RenderTexture and running a separable Gaussian in a shader (a) *is* the smooth propagation, (b) runs on GPU so the whole "is the CPU flood sub-ms" question evaporates, and (c) is exactly the kind of blit feature finding 1 shows you need anyway. The doc dismisses it on "the C# won't compile under 2D Renderer" — but that's about the *sample code*, not the technique.
- **Evidence / omitted references I read:**
  - **Don't Starve** ships the simplest viable model for the "carried light in caves" case: a **full-screen darkness filter with additive light-holes subtracted wherever lights exist** (https://dontstarve.fandom.com/wiki/Light_Tab and Klei dev/light discussions). The doc never considers a single soft radial around the player as the cave-darkness primitive — it jumps straight to per-cell lightmaps.
  - **Core Keeper** (a genuinely-top-down dark-cave game the doc omits) is **internally 3D**, which is how it gets its lighting, and it uses **"roof lights / ceiling holes" — natural light generated from cave ceilings** (https://core-keeper.fandom.com/wiki/Roof_light, https://core-keeper.fandom.com/wiki/Light_sources). That argues your binary `roofed` bit should probably be a **scalar** (partial roof → shafts of daylight), which the doc's on/off model can't express.
- **Fix:** Add Core Keeper and Don't Starve to §9 with their techniques, promote the GPU blur/blit route to a co-primary candidate (not "upgrade path"), and add an open question on scalar-vs-binary roof (ceiling holes / light shafts).

### 6. Lesser: multi-cell footprint occupants straddling the cave mouth.
- **What's wrong:** §11 asks owner-taste questions but never raises the seam where a **multi-cell occupant** (a tree, a house) is anchored in a roofed/dark cell but its footprint/sprite extends into a lit cell. A screen-space multiply overlay darkens per-pixel (fine), but a large occupant anchored on the dark side reads uniformly dark even where it visually overlaps open ground — and per-cell darkness values will step across the sprite unless bilinear upscale is guaranteed at the occupant layer too.
- **Evidence:** Occupants have footprints (`zonebuilder.py` `footprint`/`place_occupant` write anchor + footprint cells); the doc's lightmap is per-cell and it never states occupants sample it per-pixel vs per-anchor-cell.
- **Fix:** One line in §7 stating occupant sprites are darkened by the same screen-space bilinear lightmap (per-pixel), not by their anchor cell — and a note that tall/edge occupants at cave mouths are an authored-placement concern.

## What the doc gets right (so the critique is calibrated)
- Discarding inverse-square (§5C) as a *propagation* model is correct — it ignores walls; keeping only its "multiply a bilinear lightmap" step is the right read.
- The top-down ≠ side-view insight (§3) and the darkness-from-solids inversion for buried blocks (mechanism-1) are sound and genuinely load-bearing.
- Not modeling 160×160 cells as individual Light2Ds/shadow casters (§7 "don'ts") is correct.
- Determinism analysis (§8) is fine: darkness is client-cosmetic and touches no sim state.

## Verdict
**Not ship-ready for the design phase as written — material gaps.** It's a competent research doc, but it carries three defects that would corrupt the candidate-scoring it feeds: the mechanism-2 render path it recommends ("global sun only on roofless cells" + Sprite-Light-Multiply "for free") **cannot be built with URP global lights**; the roof-mask "ships in the save, read like OpCode 106" path is **factually wrong and hides a full new persistence+netcode feature**; and the "sub-millisecond" perf claim that justifies "no incremental machinery" is **unbenchmarked and likely false on the HashSet it names**. Fix findings 1–4 (correct the render path, spell out the roof-mask data pipeline, benchmark or re-spec the flood, and resolve the darkness/carried-light compositing order) and it's ready to drive a design phase.