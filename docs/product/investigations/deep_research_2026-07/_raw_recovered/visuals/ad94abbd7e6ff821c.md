I'll load the web research tools and verify the repo claims in parallel.

---

Let me verify the repo claims and start web research in parallel.

---

Repo claims mostly verified. Let me confirm the save() format, the OpCode value, and dig into the critical URP 2D injection-point question.

---

Critical finding emerging on the URP 2D injection question. Let me verify the project's exact Unity/URP version and confirm the injection-point reference.

---

Project is Unity 6.2 (6000.2.9f1) / URP 17.2.0. The forum's "injection added in 6.4" note means the project is a version behind that capability. Let me nail down the URP 2D blend-style compositing math (load-bearing for the option ranking) and confirm the 2D lighting pass structure.

---

Let me fetch the official URP Light Blend Styles doc for the exact blend formula.

---

Let me fetch the blend-style formula from the redirected official URL.

---

Let me verify the torch/global blend-style assignments in the client code (load-bearing for the compositing critique).

---

I have enough to render verdicts. Let me do one final targeted confirmation on the torch blend-style default (whether LampLight sets a blend index anywhere) since it's load-bearing for the compositing critique.

---

# ADVERSARIAL COLD CRITIC — ROUND 2 VERDICT

I read the doc in full, verified every repo `file:line` it cites, and researched the actual URP 2D render-pass model against the project's real version (**Unity 6000.2.9f1 / URP 17.2.0** — confirmed in `ProjectVersion.txt` and `manifest.json:16`). Findings below.

---

## Round-1 fix verification

### FIX #1 — "Global skips roofed cells" removed; §7a compositing candidates
**VERDICT: The removal is correct, but the fix introduced a NEW technically-wrong claim and elevated it to "primary."**

The correction itself is right. `Light2D` globals are uniform, cookieless, one-per-blend-style — confirmed by the Unity Light2D reference and by the code: `DayNightController.cs:67-89` deliberately enforces *exactly one* enabled Multiply global (the "night isn't dark" fix). So "the global can't mask roofed cells" is verified correct.

But the replacement it reaches for is worse. §7 route 1 and §7a option **B** describe a *"Blit ScriptableRendererFeature that modifies the light field before it applies to sprites"* / *"injects the roofed/buried darkness into the light texture (before it multiplies sprites)."* **That injection point does not exist in the URP 2D Renderer at this project's version.** The 2D lighting pipeline runs as two internal phases — (1) draw the light render textures, (2) draw the renderers sampling them — *repeated per distinctly-lit set of Light Layers* ([Lights-2D-intro](https://docs.unity3d.com/6000.4/Documentation/Manual/urp/Lights-2D-intro.html)). A `ScriptableRendererFeature` can only inject at the coarse events — a Unity forum thread on exactly this ("How to inject a custom RenderPass in URP 2D that respects Sorting Layers") states *"the only available injection points are fixed events like AfterOpaque, BeforeRenderingTransparents, or AfterRenderingTransparents,"* a responder confirms *"this isn't currently supported"* (May 2025), and a later comment says support was *"added in unity 6.4"* (March 2026). **The project is on 6.2 — a version behind that capability.** So option B, billed in §7 as *"the primary route… the only one that can express roofed cells dark despite the sun,"* is the *least* feasible of the three on the actual engine.

Are the three candidates real or hand-waves? **A and C are real; B is the hand-wave.** Option A (compute your own lightmap, fullscreen multiply at AfterRenderingTransparents) is achievable. Option C (a Multiply-blend-style sprite-light darkness with additive torches) is achievable within the supported light system. Option B as literally written ("inject into the light-accumulation texture") is not achievable on 17.2. Note §7 route 1 hedges "into the light field / camera color" — the *camera-color* variant is feasible but is just option A (with A's black-torch caveat); the *light-field* variant is the infeasible one. That conflation is exactly the hand-wave.

### FIX #2 — Roof-mask as a real 5-hop feature + sky-seed enclosure-flood alternative
**VERDICT: 5-hop data path is fixed correctly. The flood alternative's fatal flaw is acknowledged but under-weighted — and it contradicts the doc's own §3.**

The 5-hop feature is verified against code: `zonebuilder.py` `save()` (lines 405-413) writes only `{"chunk_x","chunk_y","ground","occupants"}` — `surface`/`reserved` are authoring-only and dropped (docstring line 4-10). OpCode 106 is server-*derived* `state.BlocksBugsCells()` (`match.go:2793/2798`, `messages.go:150` `OpCodeZoneCollisionMap int64 = 106`), not authored save data. zonegen has no roof concept. All correct; "not a footnote" is justified.

The enclosure-flood alternative is where it's still weak. The doc flags the mouth problem ("a partially-open cave connected to the surface by a mouth would flood as 'exposed'") but treats it as a solvable edge case to "weigh in the design doc." **It is not an edge case — it is the normal case.** In a top-down farming game you *enter* tunnels from the surface, so essentially every reachable tunnel is connected to sky-seed cells through a mouth; a binary reachability flood therefore lights the *entire* tunnel as exposed. And the only obvious patch — attenuating the flood with distance from the mouth — *is exactly the horizontal sky-flood that §3 declares "meaningless in our top-down plane."* So §6a's flood alternative reintroduces the precise bug §3 is built to avoid. The doc never connects these two sections. This should be labeled "likely unusable for connected tunnels; authored roof needed," not presented as a co-equal candidate.

### FIX #3 — "Sub-millisecond" removed; flat byte[] + Burst fallback required
**VERDICT: Fixed correctly. Reasoning is sound and honestly hedged. One residual minor inaccuracy.**

§8 now says the sub-ms claim "was unbenchmarked and is likely FALSE on the data we hold," mandates converting the `HashSet<Vector2Int>` (`TilemapManager.cs:40`, verified) to a flat `byte[65536]`/`NativeArray` with Burst/Jobs fallback, and explicitly states "must be measured, not asserted." That's the right posture.

Residual: the mechanism cited — *"HashSet.Contains (struct hashing/boxing in Mono/IL2CPP)"* — is partly wrong. `Vector2Int` implements `IEquatable<Vector2Int>`, so `HashSet<Vector2Int>.Contains` uses `EqualityComparer<T>.Default` and **does not box or GC-allocate**. There's real hashing/cache-miss cost, but the "boxing → GC pressure" claim is a framework-level inaccuracy, and "~1M Contains → multiple ms" remains an estimate. The doc's conclusion (convert to a flat array, measure) is still right; the supporting detail is slightly off. Minor.

### FIX #4 — §7a as "the central risk requiring a spike"; is compositing actually solvable?
**VERDICT: Framing as the acceptance gate is good. It IS solvable — but the doc's own ranking points the spike at the wrong (least-feasible) option, and its core §4 premise is over-generalized.**

Yes, "a torch reveals a dark roofed cell to a warm pool while the rest stays black" is achievable in URP 2D **without a full custom 2D lighting pass.** URP 2D already composites blend styles as separate textures: the Multiply blend style darkens (`Modulate=1, Additive=0`) and the Additive blend style adds glow (`Modulate=0, Additive=1`), with additive applied *after* the multiply ([Light Blend Styles](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@8.1/manual/LightBlendStyles.html)). So an additive torch survives a multiply-blackened cell natively — that's the gate look, for free-ish, via option C. The doc's §4 argument that darkness×(scene+torch) "turns even a lit torch pool black," used to justify the whole "one unified light field before it applies" mandate, **is only true for a naive fullscreen post-multiply on the finished frame** — not for URP 2D's native two-blend-style composition. The doc never distinguishes these, so it overstates the difficulty and steers the design toward the heavy custom-pass route (B) as primary.

So: not a case where none of the three work. But the doc has the ranking inverted — it *demotes* the one that most naturally works (C) and *promotes* the one that can't be built on 17.2 (B).

---

## NEW material findings (ranked)

**N1 (MAJOR) — The designated "primary" render route is infeasible on the actual engine version; the ranking is inverted.** §7 route 1 / §7a option B (inject darkness into URP's light-accumulation texture before sprite lighting) has no injection point in URP 2D 17.2 / Unity 6.2 (evidence in Fix #1). §10 rec #3 makes this the primary route and the spike target. A design phase that starts by spiking the one route the engine can't express will burn the highest-risk budget on a dead end. Fix: make option C (Multiply-blend darkness sprite-light + additive torches) or option A (self-computed lightmap, fullscreen multiply) the primary; mark B as "requires Unity 6.4+; not available on our 6.2."

**N2 (MAJOR) — §4's "must resolve into one unified light field" is over-generalized.** URP 2D natively applies multiply-darkness and additive-glow as distinct blend-style textures (additive after multiply), so the "torch goes black" failure only occurs under a fullscreen post-multiply — not under the native path. The doc treats a unified custom light field as the *only* escape. This mis-frames the central risk and inflates scope.

**N3 (MEDIUM) — §10 rec #4 ("reveal with the existing `LampLight.cs` lights, fed per-cell darkness") is under-specified and partly self-contradictory.** `LampLight.cs:29-30` creates its `Light2D` and never sets `blendStyleIndex` (grep for `blendStyleIndex` across the client returns nothing) → it defaults to index 0, which in `Renderer2D.asset:34-37` is **Multiply**, the same blend style as the day/night global and the proposed darkness. On one shared Multiply texture, torch (raise) and darkness (lower) fight through the Overlap Operation — the doc's own §7-option-2 concern, now applying to the *existing* lights. Realizing the clean native composite requires moving torches to a dedicated **Additive** blend style — an unmentioned `LampLight.cs` change. And §7a option A (lightmap-baked light bubbles) would require abandoning URP `Light2D` torches entirely, directly contradicting rec #4's "use the existing lights." Neither cost is surfaced.

**N4 (MEDIUM) — §6a enclosure-flood reintroduces the §3 bug for the common case** (detailed under Fix #2). Should be downgraded from co-equal candidate to "authored roof needed; flood likely unusable for surface-connected tunnels."

**N5 (MINOR) — §8 boxing claim is wrong** (`Vector2Int : IEquatable`, no boxing on `Contains`); perf estimate still unbenchmarked but honestly hedged.

**N6 (MINOR) — version-citation mismatch.** §4 cites the **6000.4** (Unity 6.4) Light2D manual while the project is **6000.2** (`ProjectVersion.txt`). The uniform-global fact is version-stable, so no harm *there* — but it's precisely the 6.2-vs-6.4 gap that makes option B look reachable when it isn't. Pin doc references to 6.2 / URP 17.2 so the design phase doesn't inherit 6.4-only capabilities as assumptions.

---

## Ship-ready for the design phase?

**Not yet — one section blocks it, and it's the most important one.**

The roof-signal data path (§6/§6a hops), the perf section (§8), and the algorithm/source material (§5/§9) are ship-ready with only minor edits (the flood-alternative downgrade, the boxing nit). Those fixes genuinely landed.

But the render/compositing section — **§7, §7a, and §10 rec #3, which the doc itself designates as "the central risk" and "the acceptance gate for the whole feature"** — still carries a technically-wrong primary route and an inverted candidate ranking that would misdirect the very spike the doc says gates the design. Specifically: **the doc claims a Blit Renderer Feature can inject darkness "into the light texture before it multiplies sprites" and calls that the primary route, but the URP 2D two-phase lighting pipeline ([Lights-2D-intro]) plus the Unity forum thread on 2D custom-pass injection show that injection point does not exist until Unity 6.4, and this project is on 6.2.** Until §7/§7a/§10 are corrected to lead with option C/A, fold in the `LampLight.cs` blend-style integration cost (N3), and drop the §4 "unified field is mandatory" over-generalization (N2), the design phase would be built on a false render premise for its highest-risk component.

Fix N1–N4 and it's ready. As written, it's a 20-minute revision away, not ship-ready.

Sources:
- [Injection points reference for URP (RenderPassEvent)](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@17.0/manual/customize/custom-pass-injection-points.html)
- [How to inject a custom RenderPass in URP 2D that respects Sorting Layers (Unity Discussions)](https://discussions.unity.com/t/how-to-inject-a-custom-renderpass-in-urp-2d-that-respects-sorting-layers-and-order/1641674)
- [Introduction to the 2D Lighting system in URP (two-phase pipeline)](https://docs.unity3d.com/6000.4/Documentation/Manual/urp/Lights-2D-intro.html)
- [Light Blend Styles — Modulate/Additive factors (URP 8.1)](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@8.1/manual/LightBlendStyles.html)
- [Custom render pass workflow in URP](https://docs.unity3d.com/6000.0/Documentation/Manual/urp/renderer-features/custom-rendering-pass-workflow-in-urp.html)