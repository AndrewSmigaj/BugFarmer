I'll start by reading the target document in full, then verify each claimed fix against the actual codebase.

---

Now let me verify the code claims. Let me locate and read the key source files in parallel.

---

I couldn't find PlayerNightLight.cs there. Let me read the key files and search for it.

---

Let me verify the zonegen and client data-path claims, plus check the research docs and whether HC3-B's ambient-replacement scope is discussed anywhere.

---

Let me read the actual save() body and check the research doc for whether the ambient-replacement scope and the flashlight/movement concerns are discussed there.

---

I have everything I need. All claims verified against source. Here's my adversarial assessment.

---

## Round-2 verdict: the 5 claimed fixes

### Fix 1 — [CRITICAL] Daytime darkness → **LANDED** (mechanism sound), two caveats

**Rejection of same-style additive darkness: landed and correctly reasoned.** HC3 row A is now `REJECT — the Finding-1 flaw` (line 129), and the load-bearing paragraph (lines 114–123) states the real constraint correctly: within one blend style, `Light2D`s combine additively into that style's single accumulation texture, applied as `sprite × accum`, so a same-Multiply-style darkness can only add and can't pull below the daytime 1.0. This is technically correct for URP 2D, and it is corroborated in-tree: `DayNightController.cs:73` ("lit sprites with no global render black") confirms the Multiply accumulation **clears to black** and lights *add* into it. Good.

**Primary swapped to HC3-B (unified lightmap): landed and capable of daytime-dark.** B is a fullscreen **multiply blit of our own lightmap over the composited frame** at `AfterRenderingTransparents` (line 127). Because it multiplies the *finished lit color* rather than adding into the Multiply accumulation, it genuinely *can* drive a roofed cell to black regardless of the global's daytime 1.0 (`DayNightController.cs:88` = intensity 1f, `:168` Daylight=1 by day). The daytime-dark capability is real. This is not a reword — the render path is materially different from the rejected route.

**Spike now includes the day-global at 1.0: landed.** Lines 169–171: "It MUST include a Global Light2D at intensity 1.0 on the Multiply style … an earlier spec omitted it." This directly closes the round-1 trap. The three simultaneous acceptance conditions (daytime-dark across an organic seam, torch-reveal at day+night, cost) are correctly specified (172–176), and it tests B first then A2 (178–180). Correct posture.

**Caveat 1a — the A2 "second multiply style" claim: plausible at the shader level, but the doc flags the *wrong* (smaller) uncertainty.** URP 2D's `CombinedShapeLightShared.hlsl` combines up to 4 blend styles sequentially, each gated by `USE_SHAPE_LIGHT_TYPE_0..3`; two multiply-mode styles chain as `color × accum0 × accum2`. So "does the Sprite-Lit material sample both multiply passes" is answerable-**yes** and the doc is right to gate it behind the spike rather than assume it — it does *not* "lean on an unproven assumption" (B is the safe fallback). **But** the doc names material-sampling as A2's only risk (line 128) and misses the harder one: blend-style-2's accumulation **also clears to black and lights add into it** (same as style 0, per `DayNightController.cs:73`), so producing an "inverted 1=lit/0=dark" per-cell field requires *actively painting every lit cell to 1* — and you **cannot** feed that field with a global light, because the research doc itself establishes "Global lights are uniform, **no cookie**" (`research_lighting_dark_underground.md:234`). A2 would need a zone-covering *Sprite* `Light2D` whose cookie is the darkness texture (plausible, spike-resolvable) or a custom pass — at which point A2's advertised "Low–med, just move a blend style" cost (line 128) is understated. Not fatal (B is primary), but A2's "cheaper URP-native" framing is optimistic.

**Caveat 1b — "replaces the ambient's role" is an unresolved scope decision** — see NEW finding #1 below; it is the one thing I'd fix before locking the composite.

### Fix 2 — Roof covers dug cells → **LANDED (correctness), authoring mechanism still under-specified**

The Finding-2 correctness fix is present and *correct*: hop 1 (lines 94–101) says record roof over "the ENTIRE underground extent — solid rock AND carved open cells," explicitly "Do NOT derive `roofed = carved cells`," with the right justification — `carve_tunnel`/`carve_cavern` return **open cells only** (verified: `cave.py:43,72` "Returns the set of carved (open) cells"; `:79,111` same for caverns), so a runtime-dug fresh-rock cell would otherwise get `roof=0` and read surface-lit. The "mask can't be sparse → bit-pack" consequence (line 101) is also correct.

**But "paint/flood the roof over each region's bounding area" is still hand-wavy, and mildly self-contradictory.** The doc never says *how zonegen knows a region's underground extent*: there is no "underground region" concept in the builder today (`zonebuilder.py` holds only `ground`, `occ`, and authoring-only `surface`/`reserved`). "Bounding **area**" reads as a bbox — but a rectangular roof produces a **rectangular** darkness edge, which fights the doc's own top-line "organic boundary" goal (§0) and HC2's "whatever shape the builder paints" (line 84). What's actually meant is "the whole *interior* of an organically-bounded region, solids included" — a different, unspecified authoring primitive (seeded flood? painted region? per-cell scalar?). The correctness intent landed; the API is a to-be-designed hole, not a footnote. Won't block starting the data path, but flag it before someone implements a bbox.

### Fix 3 — Local-darkness torches → **LANDED and correct**

Lines 138–147 require lamps driven by "**per-cell LOCAL darkness, not global `Daylight`** — e.g. `base * max(1 − Daylight, localDarkness[cell])`." Verified against as-built: `LampLight.cs:43` is exactly `_baseIntensity * (1f - Daylight)`, i.e. **0 at day** (Daylight=1) → a daytime-tunnel torch emits nothing. The proposed `max(1−Daylight, localDarkness)` correctly fixes it. The doc also correctly handles the route split: under B the lamp bubbles are baked into the lightmap "subsuming both changes" (line 146), so the formula moves into the bake rather than `LampLight.cs`. Coherent.

### Fix 4 — Phasing dep + darkness-before-post + save migration → **all three present and coherent**

- **Darkness-before-post (Finding 6):** lines 265–267 — "if Part I lands as HC3-B (a fullscreen Multiply blit), it MUST inject **before** the Part II post stack … so torch pools bloom rather than getting darkened after post." Correct and stated as a hard constraint.
- **Save migration (Finding 7):** lines 257–260 + acceptance line 276 — new `roof` key "defaults missing→0 = lit, so shipped zones must be regenerated or the loader must treat known-underground biomes conservatively." Correct; verified the save today writes only `{chunk_x, chunk_y, ground, occupants}` (`zonebuilder.py:413`) with `surface`/`reserved` dropped (load re-derives them, `:437,:441`), so a missing-key default is a real hazard the doc now covers.
- **Phasing dependency (Finding 4):** lines 261–265 — L1 lamp tuning must run against post-Part-I Additive lamps if route A2 wins. Coherent *for A2*. **Incomplete for B** — see NEW finding #2.

### Fix 5 — Whole-zone field → **LANDED**

HC1 recommendation (line 73): "A (directional sweeps on a **WHOLE-ZONE flat `byte[65536]`, world-anchored**)," with 76–78 explaining the world-anchored 64 KB field makes camera motion a non-issue and correctly forbidding running the sweep over the `HashSet` directly (verified: the solid map is `HashSet<Vector2Int> _blocksBugsZoneWide`, `TilemapManager.cs:40`, zone-complete on join `:1241-1246`). Landed. *Minor:* `65536` hardcodes 256² — should be `W×H` (zones only need be chunk-multiples; a larger zone would overflow). Nit, not material.

---

## NEW material findings (ranked)

**#1 — "Unified lightmap replaces the ambient's role" is an unresolved fork that silently drags in the entire `DayNightController` color/weather/lightning ramp. (Highest — resolve before locking the composite.)**
The doc says B "**replaces the ambient's role**" (§0 line 15, Part-I intro line 20) and computes "= **day/night ambient** × roof × buried" (line 127). If taken literally, the global is replaced and the lightmap must now reproduce *everything the global does today*: the intensity ramp, the **dawn/dusk warm tint + moonlit-blue night** (`DayNightController.cs:144-145`), **rain overcast cool-desaturate** (`:146-147`), **drought warm-wash** (`:148-149`), and the **additive lightning flash** (`:140,150-151`). The doc enumerates *none* of this as scope — "day/night ambient" is a single hand-wave. Meanwhile the **spike keeps a global at intensity 1.0** (line 169), i.e. it tests the *opposite* architecture: global stays, lightmap is a pure darkness **mask** multiplied over it. These two readings are contradictory, and they matter for correctness, not just scope: if the global stays *and* the lightmap also carries a day/night term, night **double-darkens** (0.2 × 0.2). The doc must pick and state one:
- **(cheap, recommended)** global stays and owns all color/weather/lightning; lightmap is a **pure roof/buried darkness multiplier** with no day/night term — then delete the "replaces the ambient" / "day/night ambient ×" language, which is currently wrong; or
- **(expensive)** lightmap replaces the global — then port the full color/weather/lightning ramp into the bake and say so as scope.
Currently the prose says the expensive thing and the spike tests the cheap thing.

**#2 — Route B (the primary) retires *all* `Light2D` carried lights, which kills the flashlight cone and invalidates part of Part II L1 — unacknowledged.**
B's cost note is only "(+ retires Light2D torches; per-frame light pass; screen-space alignment)" (line 127). It does not reckon with two consequences:
- The player's **flashlight cone** is a shaped, mouse-tracked, per-frame-rotated `Light2D` (`LampLight.cs:69-118`, inner/outer angle 30/70°, smooth `ScreenToWorldPoint` aim). Baking it into a **per-cell** world-anchored `byte[]` field quantizes it to cell resolution and stamps/clears it every frame as the player moves → the smooth cone and smooth radial falloff are **lost**. Same for the moving player torch. The doc's own Part II sells "soft falloff" and smooth pools; B fights that.
- **Part II L1** explicitly tunes "**Falloff Strength / baked soft cookies on the Point `Light2D`s**" and "**light flicker … in `LampLight.cs Update()`**" (lines 195, 197). Under route B those Point `Light2D`s no longer exist for carried lights, so that L1 work targets a deleted substrate. Finding 4 (lines 261–265) only warns about the *A2/Additive* interaction; it should also state "if Part I lands as B, L1's per-`Light2D` falloff/cookie/flicker work must instead live inside the lightmap bake." The primary route quietly moots part of L1 and the entire flashlight tool (and Q7).

**#3 — A simpler composite the doc never considers: keep all `Light2D`s, add a *darkness-only* mask that the lights open back up.** The doc jumps from "same-style additive (rejected)" straight to "bake everything / retire the light system." A middle path: retain the global (day/night color) and all torch/cone `Light2D`s exactly as today, and add a fullscreen **darkness mask** (roof+buried only) multiplied in before post — where carried lights *also* deposit a cheap brightener into the mask at their known positions/radii (or the mask samples the 2D light accumulation) so torch pools reach ~1 and aren't re-darkened. This preserves smooth dynamic lights, the flashlight cone, and all of Part II L1, and confines new work to the roof/buried darkening. It needs the *same* spike to confirm the injection/sampling on 17.2, so it costs nothing to add as a third spike variant — and it dodges findings #1 and #2 entirely. Its omission is a real gap given B (the pick) carries the heaviest hidden scope.

**#4 — (minor) `byte[65536]` hardcodes 256²** (line 73) — should be `W×H`. And the spike's "half-res buffer must not band the seam" acceptance (line 173) really only bites route A2 / native lights; under B the darkness is *our* texture at our chosen res, so that clause is slightly mis-attributed. Neither blocks anything.

---

## Bottom line

The round-1 CRITICAL is genuinely fixed, not reworded: the same-style-additive route is rejected with correct URP reasoning, the primary is now a route that *can* darken at noon, the spike now includes the daytime global, and fixes 2–5 all landed (fix 2 with an under-specified authoring API, not a correctness hole). No fix regressed.

It is **sound to act on the two immediate steps**: run the spike and start the roof-signal data path (the 5 hops, whole-underground mask, save migration are correct). **But do not lock route B's "replaces the ambient" framing yet.** Before interpreting the spike result / committing the composite, the doc must (a) resolve the global-stays-vs-replaced fork in finding #1 — as written the prose and the spike describe different architectures and the "replaced" reading is an un-scoped port of the whole `DayNightController` color/weather/lightning ramp with a double-darkening hazard — and (b) acknowledge that route B deletes the flashlight cone and part of Part II L1 (finding #2), ideally by evaluating the keep-the-lights darkness-mask variant (finding #3) in the same spike. These are scope/decision gaps, not a "fails at noon" defect — a materially lower severity than round 1, but they will cause real churn if built literally as the prose reads.