# Tool-animation feel overhaul — research + proposed plan (PLAN ONLY, not built)

**Status:** PROPOSED design, evidence-backed (3 deep-research agents + 1 adversarial cold-critic, ~20
deep-read sources, 3 open-source codebases studied, load-bearing claims re-verified against our code).
Graduates to `architecture_*` once built + verified. Owner: "swings feel natural and the movements make
sense — you don't swing a shovel, you do a scooping motion."

## The problem (verified in `PlayerToolAnimator.cs`)
One procedural animator moves the tool's SINGLE icon (grip bottom-left, head top-right) around a `ToolPivot`
at the player center — rotation + translation + `localScale` only; no per-frame art, no body/arm rig. It has
4 motions, and **`Swing` is shared by axe/pickaxe/shovel/hoe/sword** — a shovel swings like a sword. Each is
one symmetric pivot rotation (`aimAngle+half → aimAngle−half`) with ease-OUT quadratic, ~0.18–0.30s, and has
**no anticipation, follow-through, overshoot, squash, or contact-timed impact**. That's the clunk.

## Verified constraints (the plan MUST live inside these — from real code)
- **`breakClickInterval = 0.25s`** (`BreakingController`): hold-to-break sends a swing every 250ms via
  `PlayerToolAnimator.Play`, which **hard-interrupts** the prior coroutine and snaps the pivot to
  `aimAngle+half` (`AnimateRoutine:258`). So **every phase (windup+strike+contact+hitstop+settle) must fit
  ≤ 250ms**, or the next swing interrupts before contact fires. Lengthening heavy swings to 0.4s (as naive
  advice suggests) would make heavy tools *windup-loop with no impact*.
- **The impact stack ALREADY EXISTS.** `BreakingController.PlayHitFeedback` (`:126-155`) already fires the
  flash (`HitFlash`), camera shake (`CameraFollow.AddShake(0.28)`), plant bend/wobble (`HitWobble`, veg-only),
  leaf/chip burst (`HitBurst`), and pitched SFX — but on the **server break tick**, not the swing's contact.
  `ToolUseController` fires the shovel/dig dust at **click-start (t=0)**. Net/water/scythe fire nothing. So
  there are **three inconsistent feedback-timing regimes** and the "impact stack" is ~80% built.
- **`CameraFollow.AddShake(amount)`** takes only an amount; `traumaDecay`(3.5), `shakeFrequency`(22),
  `maxShake`(0.22) are single global fields; shake is `trauma²`, translation-only, no rotation, no direction.
- `_held` sits at `localRotation −45°` **inside** the rotating pivot → non-uniform `localScale` there
  **shears**, it doesn't squash.

## Research toolkit (source-backed — see the research agents' source tables)
**Procedural 4-phase profile** (Cooper "12 principles for games"; Febucci easing; Chou springs; Eiserloh
curve-mixing; SLYNYRD/MoCap phase-timings): **Anticipation** (short, ~10–20%, ease-out-back rotating BACKWARD
— keep tiny to avoid input lag; use the "squash-while-already-moving" trick for the *look* of windup without
lag) → **Action** (accelerate INTO contact — *ease-IN*, this REVERSES today's ease-out) → **Contact**
(hitstop + impact stack + squash) → **Follow-through/settle** (ease-out-back overshoot `s=1.70158`, then a
**spring** settle — Chou's *implicit closed-form* `Δ=1+2hζω+h²ω²`, ζ≈0.35–0.5, f≈3–5Hz; interruptible, so
mash-safe). Squash via **stretch along the sprite's own grip→head axis** (not pivot-space scale). Skip
elastic/bounce (too slow for 0.2s) and DOTween (GC) — pure easing math + one spring.

**The contact frame is GEOMETRIC, not a fixed %.** The tool points at the target when the eased pivot angle
**crosses `aimAngle`**: ease-out → t≈0.29, ease-in → t≈0.79 (a hardcoded "65%" is wrong and fires the flash
off-target). **Fire an `OnToolContact()` when the tool head reaches the target cell / the pivot crosses aim.**

**Per-tool motion spec** (transform-only; A=aim, P=perpendicular; families so 6 tools read as 6 motions):
| Tool | Motion (phases) | Terminal beat | Lunge |
|------|-----------------|---------------|-------|
| **Shovel** | thrust head in along A (scale↓0.9 = into ground) → **rotate head UP-and-back about the grip** (scale↑1.1 = lift toward viewer) | scoop-lift | small, on thrust |
| **Axe/Pickaxe** | overhead/back wind-up → fast DOWN arc along A | **impact HOLD ~150–200ms** | small |
| **Hoe** | raise → chop-down along A → **DRAG whole sprite back along −A** | drag-back | no |
| **Scythe/Net** | wind-up to −P → **wide ~180° arc** −P·A·+P → follow-through past +P | sweep-through | no |
| **Watering** | present → tilt spout down → **sustained POUR HOLD ~400–500ms** (water FX here) → tip back | pour-hold | no |
| **Sword** | wind-up to −P → wide arc across A **+ forward LUNGE** (translate rig along A) → follow-through; alternate lead side | sweep-through | **yes** |

Distinguishers with only transforms: **arc-plane** (down/along-aim vs across-aim), **terminal beat** (HOLD vs
DRAG vs SWEEP-through vs POUR-hold), and **lunge y/n**. *Limits (can't do): true out-of-plane 3D, sprite
deform/smear (fake with a trail/ghost), body/arm recue — so the tool transform must carry ALL readability →
arcs must be WIDE and windups CLEAR or they read as nothing.*

**Impact stack (retime the EXISTING one to `OnToolContact`, gated on the local breakable∧in-range∧tool
checks so air/invalid swings don't juice):** per-object **hitstop 40–70ms** for hold-to-break (NOT 130 — it'd
eat the 250ms cadence; NEVER global `Time.timeScale` — stutters other players' interpolation on this client;
freeze only the swing + target) + trauma shake (add a **directional kick toward the struck cell** per
Eiserloh/Vlambeer) + the existing flash/wobble/burst + pitched SFX (jitter pitch to avoid machine-gun
sameness). All cosmetic, **no ledger event, outside the deterministic sim** (`frontier-sync` rule).

## Candidate approaches (≥4 scored — hard choice = how to implement in the animator)
| # | Approach | Motion distinctness | Dev cost | Headless-buildable (no Editor asset) | Mash/interrupt robustness | Fits coroutine arch | Verdict |
|---|----------|:---:|:---:|:---:|:---:|:---:|---------|
| A | Data-driven **phase-profile** (ordered phases: target angle/offset/scale + easing + dur) walked by the coroutine | High | Med | **Yes** | Med (needs blend-from-current) | Yes | strong |
| B | **Spring-only** (impulse nudges at phase boundaries) | **Low** (can't author "scoop-lift-back") | Med | Yes | High | Partial (replaces coroutine) | reject as sole |
| C | **AnimationCurve per tool** (Editor-authored assets) | High | Med-High | **No** (Editor authoring; curves don't port) | Med | Yes | reject |
| D | **HYBRID** — authored phase profiles up to contact + **spring** settle/squash + one `OnToolContact` | High | Med-High | **Yes** | **High** | Yes | **PICK** |
| E | **Baked per-frame per-direction sprite art** (genre standard) | Highest | **Very High** (art per tool×dir) | No | High | No (breaks icon system) | reject |

**Pick D.** Authored phases give the *distinct readable* motions a spring can't (the scoop-lift-and-back
shape); the spring owns ONLY the follow-through/squash-return (impulse at the contact boundary); one
`OnToolContact` unifies the feedback. Headless-buildable (pure code/data, no Editor assets), mash-safe.

## Proposed build — two phases (do Phase 1, evaluate, then Phase 2)
**Phase 1 — the 80/20 (≈1 day, determinism-free, most of the felt "juice"):**
1. On the shared swing: add a short anticipation (~15% back-rotate, **blended from the current pivot angle** to
   kill the 250ms snap-pop) + **reverse the easing to accelerate-into-contact** + one **ease-out-back
   overshoot** on the settle. Pure math, no springs/squash yet.
2. **Retime `PlayHitFeedback` → an angle-crossing `OnToolContact`**; remove it from the break tick (no
   double-fire); route the shovel/dig dust through the same callback. **Gate on the existing local
   breakable/in-range/tool checks** (no juicing air swings — a regression guard + determinism-safe).
3. Extend `CameraFollow.AddShake(amount, decay, dirKick)` for the directional kick + per-hit decay; reconcile
   with the shipped 0.28 baseline.
4. Enable a brief **down-strike trail/stretched-ghost** (today Sweep-only) so the whippier arc reads, not
   teleports. Cap hold-to-break hitstop 40–70ms; enforce `contact+hitstop+settle ≤ breakClickInterval`.

**Phase 2 — per-tool bespoke motions + polish:**
5. A `MotionProfile` data model (ordered phases + contact spec + terminal-beat type) replacing the 4 enum
   kinds. Author the 6 per-tool motions from the table (shovel scoop, axe/pick chop+HOLD, hoe drag, scythe/net
   wide sweep, watering pour-hold, sword slash+lunge). Sustained tools (watering) need a **dwell/HOLD** in the
   tween, and a re-click guard on the pour FX.
6. Squash/stretch **along the grip→head axis** (spring-driven, implicit form).
7. If heavy tools want more weight than 250ms allows, **scale `breakClickInterval` per tool weight in
   lockstep** (heavier = slower cadence) rather than overrunning the cadence.
8. (Nice-to-have) lean the existing player-body sprite (step/recoil) as cheap secondary motion.

## Certainty assessment (design-time; MIN-aggregated)
| # | Dimension | Score | Band | Evidence | Falsifier | To raise |
|---|-----------|:---:|------|----------|-----------|----------|
| 1 | Requirements fidelity | 88 | Strong | Owner verbatim "shovel scoops not swings"; per-tool motions + families deliver distinct sensible motions | Owner wanted body/character animation, not just the tool | confirm scope (tool-only) with owner |
| 2 | Comprehension | 90 | Strong | Re-read `PlayerToolAnimator`/`BreakingController`/`CameraFollow`/`ToolUseController`; found the existing stack + the 250ms cadence + the −45° shear + the 3 feedback regimes | A 4th feedback path exists I didn't grep | grep all `HitBurst.Play`/`AddShake` callers |
| 3 | Design quality | 85 | Strong | Hybrid D scored vs 4; reuses the existing stack (retime not rebuild); phased 80/20-first; grounded in ~20 sources + a critic pass | A simpler model (springs-only) suffices | Phase-1 spike proves the phase-profile need |
| 4 | Sync & determinism | 92 | Strong | All cosmetic, client-local, no ledger/hash (`frontier-sync`); hitstop is per-object not `Time.timeScale`; contact RNG local | A feedback path reads/writes sim state | confirm no `HitBurst`/shake touches hashed state (it doesn't today) |
| 5 | Correctness | 74 | Plausible | Contact=angle-crossing (t≈0.29/0.79 verified), easing reversal, hitstop cap, shear fix, spring implicit form — all reasoned + code-checked, none built | An easing/curve number feels wrong in-engine | the Phase-1 spike |
| 6 | Blast radius | 80 | Strong | Touches `PlayerToolAnimator` + retimes `BreakingController` feedback + extends `AddShake`; all client cosmetic; combat swings share the animator (must not regress sword/spear) | Retiming breaks combat feedback timing | test combat + farming both |
| — | **Design confidence (weakest = Correctness: unbuilt feel)** | **80** | | feel is unprovable on paper — the spike is the gate | | build Phase 1 + owner eye |

**Verification: PENDING (a spike is the only real gate).** "Feel" can't be proven by a critic — only an
in-engine Phase-1 prototype + the owner's eye. **Residual:** a 2nd cold-critic pass on THIS revised plan
(cheap; the skill recommends re-critic after a big revision — I incorporated ~12 corrections). Not a blocker
for presenting; worth one pass before building.

## Owner-taste decisions (surfaced, not guessed)
- **Scope:** tool-only motion (this plan), or also lean/step the **player body**? (Body is a nice-to-have here
  but a bigger lift.)
- **Hitstop on farming taps:** in or out? A micro-freeze sells impact but can feel sluggish when rapidly
  hoeing/watering. Recommend: ON for break/chop (weighty), OFF or ~30ms for hoe/water (light/rapid).
- **Heavy = slower?** Scaling `breakClickInterval` by tool weight makes an axe swing slower + weightier than a
  hoe. Good game-feel, but changes break-DPS pacing — owner call.
- **Phasing:** do Phase 1 (cheap 80/20) and evaluate before committing to the per-tool Phase 2? (Recommended —
  matches the iterative style; Phase 1 alone likely resolves most of the "clunky" complaint.)
