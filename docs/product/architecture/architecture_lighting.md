# Lighting — architecture & design (PROPOSED)

> **Status: DESIGN / PROPOSED — not yet built.** This doc holds the *decision*; the *evidence* lives in
> `docs/product/investigations/research_lighting_dark_underground.md` and `..._look.md` (each through two
> adversarial critic rounds). Sections graduate to "as-built" only when the code ships + the spike passes.
> **Engine (pinned): Unity 6000.2.9f1 / URP 17.2.0, 2D Renderer.** Do not assume Unity-6.4-only features.
> **Two goals:** (1) make underground areas dark (buried blocks + roofed tunnels) with an *organic* boundary;
> (2) make the lighting *look* good (vs the naive point/spot-light state today). **All darkness is COSMETIC →
> client-side → zero sim/determinism impact.**

## 0. What's proposed, in one paragraph

Compute a **client-side per-cell darkness field** from (a) the existing zone-wide solid map and (b) a **new
authored per-cell roof signal** emitted by zonegen (covering the whole underground extent so runtime-dug cells
stay dark); render it as a **pure roof+buried darkness MASK** — a fullscreen multiply of the lit frame (before
post) that carries **no** day/night term and is **opened back up wherever a carried light reaches** (lamps
stamp a coarse soft reach into the mask). This darkens a roofed cell even under the noon sun (a same-blend-style
additive darkness can't — it only adds, the trap an earlier draft fell into), while **keeping the existing
global light and every `Light2D`** (so day/night color, weather, the flashlight cone, and soft falloff all
survive) — lamps need only be driven by *local* darkness (not global daylight) so they work in daytime tunnels.
Separately, lift the *look* by a **context-split** polish stack: dark colored ambient for night/interiors/
underground; palette grade + soft glow + light-shafts for the daytime outdoor farm; plus soft falloff, light
flicker, contact-shadow grounding, and turning post-processing on (it's off today). The one hard technical risk
— proving, **with the daytime global present**, "a roofed cell stays black beside a lit surface cell AND a
torch reveals it, with no double-darkening at night" — is gated behind a **prototype spike** before the design
is called done.

## 1. The system as-built today (the pattern we extend — verified file:line)

- **Ambient / day-night:** `DayNightController.cs` creates/adopts exactly ONE Global `Light2D` (:66-89, the
  fix for the old "night isn't dark" bug — all globals accumulate into the **Multiply** blend texture,
  :68-71), ramps intensity/color every frame (:132-152) with a smoothstep day→dusk→night curve (:166-172),
  night floor `nightIntensity = 0.20` (:47), warm dawn/dusk `(1,0.80,0.58)` vs moonlit-blue night
  `(0.35,0.42,0.75)` (:48-49), and exposes static `Daylight` 0..1 (:52).
- **Placed/carried light:** `LampLight.cs` adds a Point `Light2D` (:29) whose `intensity =
  _baseIntensity * (1 − Daylight)` (:43) — **no flicker**, and **no `blendStyleIndex` set anywhere** in the
  client, so every light defaults to index 0 = **Multiply** (`Renderer2D.asset:34`). `PlayerNightLight` emits
  nothing unless a torch/lamp item is equipped (:96-99) — "Terraria-style," the established stance.
- **Materials:** one shared `Sprite-Lit-Default` on every world sprite (`LitMaterials.cs:23`) — flat, no
  normal/emission maps.
- **Renderer:** `Renderer2D.asset` — blend styles Multiply(ch0), Additive(ch0), Multiply-with-Mask(ch1),
  Additive-with-Mask(ch1) (:34-45); `m_HDREmulationScale: 1` (:31); `m_LightRenderTextureScale: 0.5` (:32,
  lights render half-res); `m_RendererFeatures: []` (:26, greenfield); `m_PostProcessData` assigned (:63).
- **Post-processing:** OFF — camera `m_RenderPostProcessing: 0` (`SampleScene.unity:898`),
  `UniversalRP.asset m_VolumeProfile: {fileID:0}`; the `DefaultVolumeProfile.asset` overrides are all
  `active:1` at no-op values (Bloom intensity 0, Tonemapping None, ColorLookup contribution 0, Vignette 0).
  **HDR is on** (`UniversalRP.asset:26 m_SupportsHDR:1`, camera `m_HDR:1`); grading mode is LDR
  (`m_ColorGradingMode:0`). **No Pixel Perfect Camera** in the project.
- **The darkness input:** the client already holds the zone-wide solid map as
  `HashSet<Vector2Int> _blocksBugsZoneWide` (`TilemapManager.cs:40`), hydrated by `HandleZoneCollisionMap`
  (:1239) from server OpCode 106 (a server-*derived* set, `match.go:2793`).
- **Save format:** `zonebuilder.py save()` writes only `{chunk_x, chunk_y, ground, occupants}` per chunk —
  there is **no per-cell roof array and no slot for one** (the builder's `surface`/`reserved` masks are
  authoring-only, dropped on save).

---

# PART I — Dark underground

The **top-down insight** (research §3): a tunnel and an open field both read "open" in the 2D plane, so
plane-openness cannot distinguish them — sub-problem (B) needs an authored roof signal, not a derived one.
Three cosmetic client-side mechanisms combine: **(1) darkness-from-solids** (buried blocks, from the solid
map), **(2) roofed-cell ambient** (tunnels, from an authored roof signal), **(3) carried/placed light**
(reveal). See research doc §4.

## HC1 — How is the per-cell darkness field computed?

| Candidate | Look fidelity | Perf (256² / window) | URP-2D 17.2 fit | Dev cost | Verdict |
|-----------|---------------|----------------------|-----------------|----------|---------|
| **A. Directional linear sweeps** (4 ordered passes, `max(cell, neighbor−decay)`; shipped Terraria "Color") | High — smooth radial, decays more through solids | Good on a **flat `byte[]`** grid; *bad* on the `HashSet` we hold (research §8 — several ms, must convert + measure) | Pure CPU → a `Texture2D`; fits any apply route | Low–med | **PICK (primary)** — simplest dense-window fit; convert the HashSet to a flat array once/zone |
| **B. Queue BFS flood** (SoA/Minecraft; removal-BFS for incremental digs) | High (same result) | Same as A; incremental removal-BFS is a cheaper dig update if profiling demands | Same | Med (removal-BFS bookkeeping) | **Keep as the incremental-update upgrade** if full-window recompute proves too costly |
| **C. GPU blur-as-propagation** (render solid/roof mask → separable Gaussian → the field) | High, inherently smooth | Moves cost **off the CPU** entirely | Fits the fullscreen-blit apply route (A-fallback); shader work | Med | **Keep as the perf escape hatch** — pairs with the unified-lightmap render route |
| **D. Inverse-square point sum** (realcoloride) | Wrong — ignores walls, no buried/roof concept | n/a | n/a | Low | **REJECT** — not a propagation model (research §5C) |

**Recommendation:** **A (directional sweeps on a WHOLE-ZONE flat `byte[W×H]`, world-anchored)** (256²=64 KB for
a standard zone; size by the actual chunk-multiple dims), measured;
escalate to **B** (incremental) or **C** (GPU) only if the measured cost warrants. Do NOT run the sweep over
the `HashSet` directly, and do NOT use a scrolling screen-space window — the solid map and roof set are both
zone-complete on join (`TilemapManager.cs:40`), so a world-anchored 64 KB field makes camera motion a
non-issue (design-critic Finding 8). (A screen-space buffer is only relevant to HC3-B's fullscreen blit, whose
world→screen sampling must then track the camera.)

## HC2 — Where does the roof signal come from?

| Candidate | Solves tunnels? | Boundary organic? | Persistence cost | Dev cost | Verdict |
|-----------|-----------------|-------------------|------------------|----------|---------|
| **A. Authored per-cell BINARY roof mask** (RimWorld model) — a `roofed` bit emitted by zonegen, independent of walls | Yes | Yes (whatever shape the builder paints) | New per-cell array in the save + wire + hydrate (the 5 hops, §I-data) | Med–high | **PICK if binary is enough** |
| **B. Authored SCALAR roof** (0..1) — same pipeline, a byte per cell; models **cave-mouth light shafts** (Core Keeper "ceiling holes") | Yes, + graded mouths | Yes, + soft gradient | Same array (byte vs bit) | Med–high | **DEFERRED** — owner chose binary for v1; upgrade later, no rework |
| **C. Derive from solids only** (mechanism 1 alone — no roof signal) | **No** — open tunnels read lit | n/a | Zero (already have the solid map) | Low | **REJECT for tunnels** — handles buried blocks only; keep as mechanism 1, not a tunnel solution |
| **D. Sparse sky-seed + enclosure flood** (client-derived) | **No** — surface-connected tunnels flood as "exposed" through their mouth (the common case); the only patch is the horizontal sky-flood §3 proves meaningless | — | ~Zero | Low | **REJECT** — reintroduces the exact top-down bug (research §6a) |

**Recommendation — RESOLVED: A, the authored BINARY mask** (decided 2026-07-08; owner wants "terraria dark"
+ simplicity). Scalar/ceiling-hole light shafts (B) are a **deferred nice-to-have**, not v1 — the pipeline is
the same (byte vs bit) so we can upgrade later without rework. The flood (D) is a documented dead-end. This is
a **new end-to-end feature** (below).

### The roof-signal data path (the 5 hops — this is real work, not a footnote)

1. **Builder API** (`tools/zonegen/`): record roofed cells over the **ENTIRE underground extent — solid rock
   AND carved open cells** (RimWorld model: roof is separate from walls; mining leaves the roof bit). **Do NOT
   derive `roofed = carved cells`** — `carve_tunnel`/`carve_cavern` return only the **open** cells
   (`cave.py:43,72,79`), so a player who digs *fresh solid rock* at runtime would open a cell with `roof=0` →
   it'd read as surface-lit (the top-down bug, reintroduced at runtime — design-critic Finding 2). Instead
   mark the roof over each underground region's **organically-bounded INTERIOR** (solid + open), so any dug
   cell inside stays roofed→dark. **This needs a new authoring primitive** (zonegen has no "underground
   region" concept today — only `ground`/`occupants` + authoring-only `surface`/`reserved`): a painted region
   / seeded flood / per-cell scalar. **NOT a bounding-box** — a rectangular roof produces a rectangular
   darkness edge, defeating the organic-boundary goal. **Consequence:** the mask can't be sparse (it must cover
   diggable solid cells) — this raises HC2's data volume; bit-pack the binary case. (Designing this primitive
   is itself a sub-task, not a footnote.)
2. **Save format**: add a per-cell `roof` array to `chunk_X_Y.json` (byte for scalar, or bit-packed for
   binary) — a new key alongside `ground`/`occupants` in `zonebuilder.py save()`.
3. **Go loader**: parse `roof` into the chunk struct (server-side; it only needs to *ship* it, not read it —
   darkness is client-only).
4. **Wire**: a **new OpCode** carrying the zone-complete roof set on join (mirror `sendZoneCollisionMap`'s
   shape, `match.go:2789`), OR fold into the existing chunk sync. **NOT** OpCode 106 (that ships a derived
   blocking set, not authored data).
5. **Client hydrate/store**: a per-cell roof store parallel to `_blocksBugsZoneWide`
   (`TilemapManager.cs:40`), consumed by the darkness compute (HC1).

## HC3 — How is the darkness field rendered / composited with carried light?

**Two load-bearing constraints (from the design-critic rounds):**
1. **Darken at noon.** The darkness must darken a roofed/buried cell **while the surface is fully lit by the
   daytime global** (`Daylight=1`, `DayNightController.cs:168`). Within one URP 2D blend style, `Light2D`s
   combine **additively** into that style's single accumulation texture, applied as `sprite × accum`. So a
   darkness "light" on the **same** Multiply style as the global can only **add** — it **cannot pull accum
   below the daytime 1.0** (confirmed by two critics + the `DayNightController.cs:88` "lit sprites with no
   global render black" behavior). Darkening the daytime global needs a **second multiply pass over the lit
   frame**, not an additive contribution.
2. **Don't fight the ambient, and don't re-darken torch pools.** The global already owns the day/night color
   ramp + weather + lightning (`DayNightController.cs:144-152`). So the darkness field must carry **NO day/night
   term** (or night double-darkens: 0.2×0.2), and a naive multiply of the *finished* frame turns lit torch
   pools black (research §4) — so the field must **open back up wherever a carried light reaches**.

These two constraints point to a **pure roof+buried darkness MASK, opened by carried-light reach, that keeps
the global and the `Light2D` lights intact.** Candidates:

| Candidate | Darkens at noon? | Torch pools survive? | Keeps `Light2D` lights (cone/falloff)? | URP-2D 17.2 fit | Verdict |
|-----------|:---:|:---:|:---:|-----------------|---------|
| **B′. Roof+buried darkness MASK, opened by light reach** → fullscreen Multiply blit **before post**. Field `D[cell] = max(roofBuriedDark[cell], lightReach[cell])`, where carried lamps/torches **stamp a coarse soft reach** into `D` (positions+radii known). Global + all lamps stay exactly as today. | **Yes** (multiplies the lit frame) | **Yes** (`D` lifts to ~1 where lights reach) | **Yes** — lamps/cone/flicker untouched | Works (supported injection point; `m_RendererFeatures:[]` greenfield); no day/night term in `D` → no double-darken | **PICK (primary)** |
| **A2. Second multiply blend style** ("Multiply-with-Mask", inverted 1=lit/0=dark → chain-multiply). | Yes | via Additive lamps | Partly (needs lamps→Additive) | URP-native, **but** the inverted field can't be fed by a global (globals take no cookie, research §7) → needs a **zone-covering Sprite `Light2D` cookie or a custom pass** + confirm the material samples both multiply passes | **Alternative** — cost higher than "just a blend style" |
| **B. Fully-baked unified lightmap** (bakes global day/night + weather + lights into one field; retires `Light2D`s). | Yes | baked | **No** — **kills the mouse-tracked flashlight cone + moots Part II L1**; must re-port the whole `DayNightController` color/weather/lightning ramp | Works | **Heavy fallback** — only if B′'s light-stamp can't reproduce smooth pools |
| **A. Same-Multiply-style additive darkness** | **No** (can't subtract) | — | — | trivial | **REJECT** (Finding-1 flaw) |
| **C. Mid-pipeline light-texture injection** | Yes | Yes | Yes | **NOT on 17.2** (Unity 6.4+) | **REJECT (our version)** |
| **D. Naive final-frame multiply, no light-opening** | Yes | **No** (pools black) | — | trivial | **REJECT** — B′ is D *plus* the light-opening fix |

**Recommendation:** **B′ (roof+buried mask opened by light reach)** — it darkens at noon, keeps the global +
every `Light2D` (so the flashlight cone, soft falloff, flicker, and all Part II L1 work survive), carries no
day/night term, and confines new work to the roof/buried darkening. **A2** is the URP-native alternative;
**B (fully-baked)** is the heavy fallback only if the coarse light-stamp can't match smooth pools. Do NOT
pursue same-style additive (A) or mid-pipeline injection (C).

**Required `LampLight.cs` change (one, not two — under B′).** Lamp intensity is `_baseIntensity * (1 − Daylight)`
(`:43`) → **every lamp is OFF during the day** (`Daylight=1`), so a torch in a *daytime* tunnel emits nothing
(Finding 3). Drive intensity by **per-cell LOCAL darkness, not global `Daylight`** — e.g.
`base * max(1 − Daylight, localDarkness[cell])`. Under B′ lamps **stay on the Multiply style** (no Additive
move, no re-tune — that cost only applies to A2/B). This is the least-invasive route.

## HC4 — How dark is "dark"? — RESOLVED (owner, 2026-07-08)

Owner: *"terraria dark in the underground, above ground very dark in the middle of the night like it is now."*
- **Underground = Terraria PITCH-BLACK** beyond the light bubble (darkness floor ≈ 0; unlit caves unnavigable —
  a torch is required, which matches the existing `LampLight.cs:98` stance and the owner's "no free glow" call).
- **Surface = the EXISTING day/night** — the current deep-night darkness (`nightIntensity = 0.20`) is what the
  owner wants; **do not change it.** The darkness system is *additive underground only*; it must not alter the
  surface night that already reads correctly.

## Determinism (Part I)

Untouched. Darkness reads the already-synced solid map + authored roof DATA (shipped in the save like
`ground`/`occupants`); it never enters `ComputeStateHash`, mints no ids, and adds no *sim* input. The roof
mask is authored content, not a runtime sim read. No `frontier-sync` recipe needed. (Confirm with the
`test-changes` 2-client parity anyway once built, per house rule — a data/format change to the save.)

## Cross-zone continuity (owner requirement 2026-07-07 — captured in BACKLOG.md)

Owner: *"lighting must be continuous ACROSS zone seams, not per-zone-isolated… no hard light/dark wall at the
seam, and a player straddling the edge sees one coherent light field."* Also (2026-07-06): *"the outside area
at the top… lit like any other day/night… we can make it dark past that point"* + *"all masses of ore block
should have the inner ones dark, wherever they are surrounded, like terraria."* The B′ model honors these:
- **The lit-surface half is continuous by construction** — day/night is one global driven by the shared server
  tick (`DayNightController.cs`), identical in every zone, so a lit surface strip matches its neighbor's.
- **The dark half is an AUTHORING edge-contract.** The darkness field is per-zone (computed from that zone's
  solid map + roof mask), so the shared edge cells between two zones must have **matching roof values** — a new
  row in the zone edge-contract discipline (same idea as terrain edge contracts in zone-craft). A surface zone's
  bottom edge and the underground zone's top edge must agree, so crossing the seam shows no light/dark wall.
- **The Terraria "inner surrounded blocks are dark" rule = mechanism 1** (darkness-from-solids) — it already
  darkens the interior of any block mass (ore masses on the surface included), no roof needed.
- **Open question:** does the game ever *render two zones simultaneously* at a seam, or is it a hidden swap
  (per BACKLOG "cross-zone movement — hidden swap")? If simultaneous, both zones' darkness fields must be
  computed and aligned at the boundary; if a hidden swap, only the edge-contract matters. **Verify the seam
  rendering model before building** — it decides whether cross-zone is an authoring contract (cheap) or a
  two-field-alignment problem (harder). Add to the spike's real-zone check: straddle a surface↔underground seam.

## The acceptance-gate spike (do this BEFORE calling Part I designed-done)

A throwaway Unity spike on 17.2. **It MUST include the real setup: a Global Light2D at intensity 1.0 on the
Multiply style (the daytime sun) + a `Light2D` lamp** — an earlier spec omitted the global, which would have
let the spike pass in isolation while the real feature failed at noon (the Finding-1 trap). The spike must
prove, simultaneously, for the **B′ primary** (roof+buried mask, opened by light reach, multiplied before
post):
1. **Daytime dark:** a roofed/buried cell renders **black** while an **adjacent surface cell is fully lit** by
   the day global — across an organic cave-mouth seam (the mask is *our* texture at our chosen res, so seam
   banding is a resolution choice, not the half-res light buffer).
2. **Torch reveals, pool survives:** a lamp/torch reveals that dark roofed cell to a **warm cozy pool** — i.e.
   the mask **lifts where the light reaches** so the multiply doesn't re-darken the pool (Finding 3/§4). Reads
   correctly at day *and* night.
3. **No double-darken:** the mask carries **no day/night term** — night looks right (global's 0.2 floor ×
   mask, not 0.2×0.2). Verify a night surface cell isn't over-dark.
4. **Lights intact & cost:** the flashlight cone + soft falloff still render (B′ keeps the `Light2D`s); the
   field recompute + upload is within frame budget (measure — research §8).

Test **B′** first. If the coarse light-stamp can't reproduce smooth pools, test the **fully-baked B**
(heavier). Optionally test **A2 (second multiply style)** to see if that URP-native route passes #1 (does the
Sprite-Lit material sample both multiply passes? does the inverted field need a Sprite-Light cookie?). These
resolve the load-bearing uncertainties the research could not — render-behavior questions only the engine can
answer.

---

# PART II — Making it look good

**The anchor is context-split** (research-look §3): darkness-first is the anchor for **night/interiors/
underground**; the **daytime outdoor** look is carried by **palette grade + warm/cool + soft glow +
light-shafts** (indie cozy games are generally bright/flat by day — one example, not a template). Post-processing
is OFF today — turning it on is the enabling step, but **dark-ambient tuning** (night/underground) and
**flicker** are the cheapest wins because they tune code that already exists. *(Owner note: aim for a distinct
BugFarmer look; don't over-match any single reference.)*

## Phased recipe (value-for-effort)

- **Phase L1 (tune existing code, cheap):** dark colored ambient for night/underground (tune
  `DayNightController`); **Falloff Strength** / baked soft cookies on the Point Light2Ds; **light flicker**
  (layered Perlin in `LampLight.cs Update()` — provably absent, `:43`).
- **Phase L2 (turn post on + ground):** enable post (camera flag + a real scene Global Volume — see config
  prereqs); subtle pixel-safe **Bloom** + **Vignette** + **Tonemapping**; **contact-shadow decal** grounding.
- **Phase L3 (mood + atmosphere):** **LUT color grade** (per-biome / per-weather); **god-ray light-shafts**
  (a common dawn/dusk cozy tell); dappled canopy + cloud shadows; in-beam dust/pollen particles.
- **Phase L4 (deferred/selective):** normal maps on hero surfaces only (owner decision); emission maps
  (needs new pipeline tooling, HC-L3).

## HC-L1 — Bloom & the pixel-art tension

| Candidate | Look | Pixel-art safety | Dev cost | Verdict |
|-----------|------|------------------|----------|---------|
| **Subtle whole-frame Bloom, high threshold + HDR emission** (only intended-bright pixels bloom) | Warm glow on lamps/glow | Safe if subtle | Low (native) | **PICK** |
| **Strong dreamy Bloom** | Washes crisp pixels; hurts top-down readability | Risky | Low | **REJECT** — too aggressive for our pixel look |
| **Layer-scoped Bloom** (only an emissive layer blooms) | Ideal control | Needs a **custom render pass / 2nd-camera composite** (URP Bloom is whole-camera) | High | **REJECT unless needed** — more work than emission tooling |
| **No Bloom** | Loses the glow tell | — | — | **REJECT** — glow is a core polish tell |

Plus **Pixel Perfect Camera**: the project has none. **RESOLVED (owner: try-and-see):** add it + subtle bloom
and evaluate at game zoom (PPC keeps pixels sharp but limits how soft bloom can be — a look call, judged in the
L2 pass, not a debate). Add **"readability at game zoom"** to the acceptance rubric.

## HC-L2 — Grounding (contact shadows)

| Candidate | Look | Pipeline fit | Verdict |
|-----------|------|--------------|---------|
| **Shared runtime contact-shadow decal** (tinted ellipse under grounded sprites) | Kills "pasted-on"; art-directable | **Only compliant path** — the sprite pipeline **forbids baked shadows** (`style.json`) | **PICK** |
| **Shadow Caster 2D** (real collider-silhouette cast) | Dramatic, but top-down casts long odd shadows | Available (shaders shipped); costs more; per-occupant setup | **Keep for select hero occupants only** |
| **Baked-into-sprite AO** | Cheapest at runtime | **Off the table** — pipeline acceptance forbids baked ground patch/shadow | **REJECT** |

## HC-L3 — Emission (glowing entities: `mushroom_glow`, lamps, fireflies)

| Candidate | Look | Cost (real) | Verdict |
|-----------|------|-------------|---------|
| **Bloom on bright pixels + a Point Light on the emitter** (no emission map) | Good-enough glow | Low — no new tooling | **PICK for now** |
| **Authored emission maps** (Secondary `_Emission` + HDR color) | Best glow | **High — needs NEW pipeline tooling** (the gpt-image-1 pipeline authors no emission channel; would add an emission-mask step to `pixelclean.py` or a hand-paint pass) | **DEFERRED** (owner 2026-07-08 — only if bloom-on-bright-pixels reads weak) |
| **No emissive treatment** | Glow entities stay flat | — | **REJECT** — leaves a visible gap |

## URP config prerequisites (verify before/with Phase L2)

(1) URP-asset HDR on (already — `m_SupportsHDR:1`); (2) **raise `Renderer2D.asset` HDR Emulation Scale** if
lamps (not just sprites) should bloom (currently 1 → 2D lights can't exceed 1; watch for banding if too high);
(3) **Color Grading Mode → HDR** if tonemapping (currently LDR `m_ColorGradingMode:0`); (4) LUT import:
Read/Write on, compression off, non-sRGB/bilinear (1024×32, matches `m_ColorGradingLutSize:32`); (5) camera
`m_RenderPostProcessing:1` + a real-valued scene Global Volume (the default profile is neutered).

---

# Decisions — RESOLVED (owner 2026-07-08)

All settled; no open owner questions remain for v1. Verbatim where the owner spoke:
- **How dark** — *"terraria dark in the underground, above ground very dark in the middle of the night like it
  is now."* → underground pitch-black; surface = the existing night, untouched. *(HC4)*
- **Roof: binary**, not scalar — matches "terraria dark" + simplicity; ceiling-hole light shafts deferred. *(HC2)*
- **Player light: torch required, no free glow** — owner: glowing without a torch *"would just be silly."*
  Keeps the existing `LampLight.cs:98` stance.
- **Mood: distinct BugFarmer look**, broadly like other indie systems. Owner: Apico was *"an example of one of
  many indie games with better lighting… not so you could hyperfocus on it and… over match."* **Do NOT treat
  Apico as the benchmark** — it's one reference; its concentric-ring (stepped radial falloff) is the technique
  worth borrowing, and it aligns with the Terraria/Minecraft stepped-light look we're already targeting. *(HC-L1)*
- **Emission tooling: deferred** — bloom-on-bright-pixels + a point light on glowers (`mushroom_glow` etc.) for
  v1; build the `pixelclean` emission-mask step only if that reads weak. *(HC-L3)*
- **Normal maps: skipped** — the research concluded flat ~16px top-down sprites barely benefit; not worth the
  cost. Revisit only for a specific hero surface if one ever calls for it. *(Phase L4)*
- **Pixel Perfect Camera / bloom: try-and-see** — add subtle bloom + a Pixel-Perfect Camera and evaluate at
  game zoom (owner is fine trying it); the spike/L2 pass judges it empirically. *(HC-L1)*

# Phasing / backlog

- **Part I** gates on the **acceptance spike** (B′ primary, day-global included). Order: spike → roof-signal
  data path (HC2 5 hops, whole-underground mask, + the new authoring primitive) → **save migration/regen of
  existing underground zones** (Finding 7 — a new `roof` key defaults missing→0 = lit, so shipped zones must be
  regenerated or the loader must treat known-underground biomes conservatively) → darkness compute (HC1-A,
  whole-zone flat array) → composite (B′, the mask + light-stamp) + the `LampLight.cs` local-darkness change →
  tune the floor (HC4 — RESOLVED pitch-black underground).
- **Part II** and Part I are **independent under the B′ primary** — B′ keeps the global + all `Light2D`s, so
  Part II Phase L1's lamp work (Falloff Strength / cookies / flicker) targets the same live `Light2D`s and is
  NOT invalidated. (The cross-dependency only appears if the spike forces a fallback: route **A2** moves lamps
  to Additive → L1 lamp tuning must run against the Additive lamps; the **fully-baked B** retires the
  `Light2D`s entirely → it would moot L1's per-light work AND the flashlight cone, so B is a last resort. So:
  ship L1 freely under B′; only re-sequence if the spike demotes to A2/B.) **Ordering constraint (Finding 6):**
  B′ is a fullscreen Multiply blit that MUST inject **before** the Part II post stack (bloom/tonemapping at
  `AfterRenderingPostProcessing`) so torch pools bloom rather than getting darkened after post.
- Add to `docs/product/BACKLOG.md` once the owner picks the taste answers.

# Acceptance criteria

- **Part I:** the spike demonstrates, **with the daytime global present**, a roofed cell black beside a
  fully-lit surface cell AND a torch revealing it to a warm pool (on 17.2); a real zone shows an organic
  open↔underground boundary (buried blocks dark, tunnels dark including **runtime-dug** chambers, surface lit
  by day/night); a lamp lights a **daytime** tunnel (Finding 3); existing underground zones are migrated/regen
  (Finding 7); digging updates darkness within a measured frame budget; `test-changes` 2-client parity green
  (save-format change).
- **Part II:** side-by-side before/after at game zoom shows the polish stack **without hurting readability**;
  each phase reproduces its reference tell (soft warm pools, flicker, grounded sprites, graded mood, shafts).
