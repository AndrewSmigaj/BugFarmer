I'll read the design doc in full and the two research docs, plus check the key source files referenced.

---

Now let me examine the actual source files to verify claims and reason about the design-level holes.

---

Let me verify the remaining as-built claims and check the zonegen roof/save details.

---

I've read the design doc in full, both research docs, and verified the load-bearing as-built facts against source. Findings below are ranked by severity, each with evidence and a fix. I focused on DESIGN/synthesis-level holes, not the already-vetted research facts.

---

## Finding 1 — [CRITICAL] HC3-A cannot produce *daytime* darkness, and the spike is rigged to not notice

**Problem.** HC3-A ("darkness on Multiply, torches on Additive," PICK, "keeps the `Light2D` torches") is described as an *additional* Multiply contribution living alongside the existing day/night global. That is physically incapable of darkening a roofed/buried cell while the surface is lit by day — the exact stated goal ("buried blocks dark, tunnels dark, **surface lit by day/night**," acceptance criteria line 222; mechanism 2 = dark "**regardless of the day/night sun**," line 54).

**Evidence (reasoning chain grounded in the engine + repo):**
- Within one URP 2D blend style, all `Light2D`s render **additively** into that style's single light-accumulation texture; the Multiply style then applies `spriteColor *= accumTex`. This is why the "night isn't dark" fix needed *exactly one* global and why "lit sprites with no global render black" (`DayNightController.cs:88` comment).
- The day/night global is on Multiply blend style index 0 (`DayNightController.cs:88` sets `intensity = 1f` at day; no `blendStyleIndex` is set *anywhere* in the client — verified by grep — so it defaults to index 0 = Multiply, `Renderer2D.asset:34`).
- A darkness field modeled as a `Light2D`/Sprite-Light on that **same** Multiply style can only **add** to `accumTex`. It cannot pull `accumTex` below the global's uniform daytime contribution of 1.0. So during the day, a roofed tunnel cell has `accumTex ≥ 1.0` → it renders **fully lit**. Darkness-from-solids (mechanism 1) fails the same way — buried rock sprites read lit at noon.
- The acceptance spike (lines 133-139) tests "a hand-authored per-cell darkness texture on a **Multiply Sprite Light** + a torch moved to Additive." It does **not** include the DayNightController global at day intensity 1.0. In isolation (no competing global) that spike passes trivially — and then the real integration fails at noon. The spike validates "torch punches through a dark texture" (which the Multiply/Additive split genuinely handles) but **not** "darkness overrides the uniform day global," which is the actual unsolved problem. The design silently conflates these two.

The research left this gap too (§4 correctly says the global "cannot take a per-cell mask" and "roofed darkness must be its own per-cell contribution" — but never reckons that an *additive* per-cell contribution can't subtract the global's daytime 1.0), and the design promoted it to a clean "native two-blend-style PICK."

**Fix.** Two coherent routes actually meet "daytime tunnels dark," and neither is HC3-A as written:
- (a) Put darkness on a **separate** multiply blend style (`Renderer2D.asset:40` "Multiply with Mask" is a second multiply texture that chain-multiplies the sprite), with the darkness light authored **inverted** (white=1 in lit cells, black=0 in dark cells) so it multiplies the global down to 0 in dark cells. Never specified by the design; constrained by the 4-style budget and one-global-per-style rule.
- (b) The **unified self-computed lightmap** (HC3-B) that *replaces* the global's role — bakes day/night ambient × roof × buried into one field. The design lists this as the *fallback*; it is in fact the only route that plainly satisfies the requirement.

Either way, HC3-A's "keep the existing global + just move torches to Additive, Low-med" framing is wrong. **Re-specify the spike to include a Global Light2D at intensity 1.0 on Multiply and prove a roofed cell stays black while an adjacent surface cell is fully lit AND a torch reveals the roofed cell.** Run that spike *before* committing to the recommendation — it will likely demote HC3-A and make HC3-B (or route (a)) primary.

---

## Finding 2 — [HIGH] Roof derivation covers only pre-carved OPEN cells → runtime digging re-opens the top-down bug

**Problem.** HC2's derive rule (line 88; research §6a step 1): "derive `roofed = interior of a carved underground region` at save() time." But caves are carved *out of solid rock*: `carve_tunnel`/`carve_cavern` "Returns the set of carved (**open**) cells" (`tools/zonegen/features/cave.py:43,72,79`); the surrounding rock stays solid (`fill_solid` block occupants). So only the authored **open** cells get `roof=1`. The underground is predominantly *solid*. When a player digs into that solid rock at runtime (BreakingController is real, and the client already updates the solid map via OpCode 106), the newly-opened cell is **not** in any carved set → `roof=0` → it reads as surface-open → **lit**. A player who digs a fresh chamber underground gets a *lit* chamber — the precise "tunnels read like fields" bug the whole feature exists to kill (research §3), now reintroduced at runtime.

Mechanism 1 (darkness-from-solids) only masks this for *small* pockets; a dug-out room's interior cells are far from solids → they get light → lit room.

**Fix.** Author roof as a dense mask over the **entire underground extent (solid + open)** — the RimWorld model the research actually cites ("per-cell roof grid *separate from walls*… mining leaves the roof bit," §6a), not "interior of carved regions." This also kills any hope of a sparse encoding (the mask must cover all solid underground cells you might ever dig), which raises HC2's data-volume cost and should be stated in the 5 hops.

---

## Finding 3 — [HIGH] Dropped required change: torches read global `Daylight` → a torch in a daytime tunnel emits nothing

**Problem.** `LampLight.cs:43`: `_light.intensity = _baseIntensity * (1f - DayNightController.Daylight)`. During the day, `Daylight = 1` (`DayNightController.cs:130,168` → returns 1 for t<0.42), so **every lamp/torch intensity is 0 during the day** — including one placed in a dark underground tunnel. So even after Findings 1-2 are fixed and the tunnel is correctly dark at noon, you **cannot light it** during the day: the torch is forced off by surface time-of-day. The tunnel is dark and un-lightable half the game's clock.

The research flagged this explicitly as one of *two* required `LampLight.cs` changes (research-look §1 integration finding; research-dark recommendation #4: "feed them per-cell **local** darkness (not global `Daylight`, which would leave lamps off underground during the day)"). **The design doc carried only the *first* required change** (move torches to Additive, HC3-A) **and silently dropped the second.** It appears nowhere in the HC list or the 5 hops.

**Fix.** Torch intensity must be driven by **per-cell local darkness**, e.g. `base * max(1 − Daylight, localDarkness[cell])`, so lamps light up underground regardless of surface time. Add this as an explicit HC3/data-path deliverable — it's load-bearing for the feature to function at all in daytime tunnels, and it's a second, non-trivial `LampLight.cs` + darkness-field-sampling change the design under-scoped.

---

## Finding 4 — [MED] Ordering/dependency error: Part II L1 depends on Part I's blend-style move, contradicting "Part II is independent"

**Problem.** The phasing says "Part II is independent and incremental: L1 (cheap, ship first)" (lines 216, 152) and Part I gates separately on the spike. But Part I moves lamps from Multiply → Additive (required per HC3-A and Finding 1's fix). Part II Phase L1 tunes **the lamp look** — Falloff Strength, baked cookies, flicker, and "dark colored ambient" so lamps "pop" (lines 153-155). All of that is tuned against the **current Multiply-lamp** behavior. Moving lamps to Additive changes that behavior (Finding 5), so any L1 tuning done first is invalidated and must be redone after Part I. The two parts are **not** independent; L1 has a hidden prerequisite on the Part I composite decision.

**Fix.** Sequence the lamp blend-style decision (Part I HC3 spike) **before** Part II L1 falloff/flicker/ambient tuning, or explicitly annotate that L1's lamp-look tuning must be (re)done against the post-Part-I Additive lamps.

---

## Finding 5 — [MED] The Multiply→Additive move is *not* behavior-preserving; the current warm-night look changes and the doc frames it as free

**Problem.** HC3-A rates the change "Low–med (+ move torches off default Multiply, a `LampLight.cs` change)" and says it "keeps the `Light2D` torches" — framing it as behavior-preserving plumbing. It isn't. Today lamps sit on Multiply: near a lamp `accumTex = global + lamp`, so the lamp **raises the multiply factor**, brightening the sprite *while preserving the sprite's own material colors* (warm-tinted modulation). Move the same lamp to Additive and you get `sprite*globalAmbient + lampColor`: a flat colored glow **added on top**, which washes toward the lamp color and blows out sprite detail in the bright core, and lights sprites the ambient has multiplied to near-black by adding a color rather than revealing material. The night look is materially altered (arguably necessary for torch-through-dark, but it is a *change*, not a keep). The design never surfaces that the existing warm-lamp-at-night look will shift.

**Fix.** Call this out as a look change requiring re-tuning (radius/intensity/color of every lamp, plus the Part II ambient), and fold it into the spike's acceptance ("does an Additive lamp at night still read as a warm cozy pool, not a washed-out disc?").

---

## Finding 6 — [MED] Part I darkness composite vs Part II post-processing order is unstated

**Problem.** The design treats Part I (darkness) and Part II (turn post on: Bloom/Tonemapping/LUT) as independent. If Part I lands as HC3-B (fullscreen Multiply blit at `AfterRenderingTransparents`), the **order** relative to the post stack is load-bearing: bloom/tonemapping run at `AfterRenderingPostProcessing`, so darkness-then-post means torch pools bloom correctly — but that's an interaction the design never states, and if anyone injects the darkness blit later it silently darkens post output. (For HC3-A the darkness is in the 2D light phase, before post, which is clean — another reason the A-vs-B choice isn't cosmetic.) "Independent" is overstated.

**Fix.** State the required injection ordering (darkness before post) as an explicit constraint in whichever composite wins, and add it to the acceptance rubric.

---

## Finding 7 — [LOW-MED] No save migration story for existing zones

**Problem.** Adding a `roof` key to `chunk_X_Y.json` (`zonebuilder.py save()` currently writes only `{chunk_x, chunk_y, ground, occupants}`, verified line 413). Every already-saved underground zone has no roof key; the Go loader will default missing → 0 (no roof) → **existing underground zones render fully lit** until regenerated. The design's phasing and acceptance never mention backfill/regeneration of shipped zones.

**Fix.** Add a migration/regeneration step (or a loader default that treats known-underground biomes conservatively) to the phasing, and note it in acceptance.

---

## Finding 8 — [LOW] HC1 never actually picks whole-zone vs windowed; camera-motion alignment unscored

**Problem.** HC1 measures cost "256² / window" and says "convert the HashSet to a flat array once/zone," but never decides whether the darkness field is whole-zone or a scrolling window. `_blocksBugsZoneWide` is zone-complete on join (`TilemapManager.cs:40`) and the roof set is proposed zone-complete too, so whole-zone is feasible and makes camera motion a non-issue — but the "window" language implies a scrolling buffer whose world-alignment as the camera moves is never scored (a real concern only for the HC3-B fullscreen-blit path, which is screen-space). Minor, but it's an unscored sub-decision the doc waves at twice.

**Fix.** State "whole-zone flat `byte[65536]`, world-anchored" explicitly (it's cheap — 64KB) and drop the "window" ambiguity, or scope the windowed path's world-to-screen realignment if HC3-B is chosen.

---

## Verdict

**Not sound enough to act on as written — one material design flaw.** Part II (the look stack) and the roof-data-path *shape* (5 hops, authored mask, reject the flood) are directionally solid and safe to start. But the headline of Part I — "PICK HC3-A native two-blend-style, spike it" — is the wrong gate: as literally specified (keep the day global on Multiply, add darkness as a Multiply light, move torches to Additive), it **cannot make roofed/buried cells dark while the surface is lit by day**, and the spike omits the day global so it can pass while the real feature fails at noon (Finding 1). Combined with the roof-coverage gap that re-lights runtime-dug chambers (Finding 2) and the dropped "lamps read global Daylight → off underground by day" change (Finding 3), the daytime-underground case — the core of the owner's request — is not actually delivered by the recommended path. Fix before acting: re-specify the spike to include the day-intensity global and prove daytime-dark-tunnel + torch-reveal together; that will likely demote HC3-A to fallback and promote HC3-B (or a separate multiply style) to primary — which changes the Part I ordering, cost, and the `LampLight.cs` work the design under-scoped.