# Player arm + tool-holding + swing — design (DRAFT, 2026-07-19)

## The ask (owner)
Make the player **hold** tools/weapons with a **bent elbow** (e.g. a sword held out in front), and **swing**
them **smoothly (not clunky)**, reusing our existing tool-sprite animator.

## Where we are (verified in `PlayerToolAnimator.cs`)
The equipped tool's **own sprite** is rotated/translated on a pivot at the **player CENTER**, with 7 motion
profiles (swing/chop/stab/sweep/till/scoop/pour). It **already does the swing craft well**: anticipation
(wind-back) → EaseIn-to-contact strike (peak velocity AT contact) → EaseOutBack follow-through overshoot, a
forward **lunge** at the strike (a proxy for arm extension), and a motion trail. The two gaps are *exactly* the
owner's asks:
1. The tool pivots at the **player center, not a hand** → the tool "floats" (telekinesis look).
2. There is **no arm** — the arm is baked into the flat, single-renderer paper-doll body → it can't bend the
   elbow or hold a tool out in front.

So we do **not** need to rebuild the swing (it's good). We need to add the **arm** and move the **pivot to the
hand**. (Research consensus, 10 sources: Terraria, Stardew, animation-craft guides.)

## Recommended design — a near-arm POSE layer, phase-locked to the tool arc
(Ranked #1 of 4 in the research: best quality-per-effort for our flatten pipeline + our sprite size;
Stardew-proven at exactly this structure.)

Add **one** separate **near-arm SpriteRenderer** (the arm nearest the camera), drawn **over the tool** so the
hand grips it, showing a small set of hand-authored bent-arm **poses** per direction:
- **HOLD** — bent elbow, forearm forward, hand out front. *(Idle: the tool grip sits at this pose's hand
  anchor → a bent-elbow sword held out in front. This alone satisfies the hold ask.)*
- **WIND-UP** — arm cocked back.
- **STRIKE** — arm extended (elbow straightens) at contact.
- **RECOVER** — arm re-bending back to hold.

During a swing, **swap the arm pose off the SAME normalized phase `t`** the tool animation already computes
(the anticipation/strike/follow boundaries already exist in `AnimateRoutine`) — **no new curve math.** The tool
keeps its existing easing/lunge/trail; the arm poses ride along in sync. The craft rule "elbow bent at rest →
extends on the strike → retracts on recovery" falls out for free from the pose set + the phase mapping.

**Smoothness lever (Stardew-proven): non-uniform per-pose durations** — e.g. ~150 ms wind-up hold → two fast
~40 ms strike frames → ~170 ms impact hold → ~75 ms recover. It's the *timing*, not more frames, that reads
smooth vs clunky. Our animator already uses phase fractions (antF/strF/holdF) — the poses map onto them.

### The one animator change
Move the tool pivot **origin** from the player center to the **arm pose's hand anchor** (per direction, per
pose). Keep everything else — the 7 profiles, easing, the lunge, the trail, the `_behindPlayer` draw-order
flip. The tool now swings from the hand at the end of the bent arm.

### The 4 facings
- **Down (front) / Up (back):** a foreshortened bent-arm pose (front = arm+tool ahead; back = behind, tool
  behind — reuse the existing `_behindPlayer` sort flip).
- **Left / Right (side):** the clearest bent-elbow profile — forearm forward, tool out ahead. Right = mirror
  of left (matches the base's right=mirror(left)).

### Art the pipeline must produce
Per direction × ~4 poses (hold/wind-up/strike/recover), each with a **hand-anchor pixel** marked; sleeve/skin
variants as needed. Small set (~4 poses × 3 unique dirs = ~12). Best authored **during the 64×128 upscale**
(the art is being redrawn anyway). The "arms" slot is promoted from a flat baked layer to a live
pose-swapping renderer. *(The AI side-run frames confirm gpt draws bent arms cleanly — so these poses can be
AI-assisted then hand-cleaned, fitting the pipeline.)*

### Networking / determinism
The swing is a **local animation triggered by the action event** — exactly like the current tool swing, which
already replays on remote players from the equipped item + action (`RemoteEntity` → `PlayerToolAnimator`). The
arm pose-swap animates locally on the same event → **no per-frame arm-state sync.** Client-cosmetic, zero
determinism exposure.

## Alternatives (why not)
- **#2 — Terraria-style procedural 2-bone rig** (separable upper-arm + forearm, dynamic elbow via a rotation +
  a 4-step stretch). Highest fluidity ceiling and tool-agnostic, BUT needs the pipeline to emit separable
  arm-segment sprites with pivot metadata, breaks the single-renderer flatten, and sub-pixel rotation looks
  mushy below ~64px. **Viable for the SIDE facings only, after the 64×128 upscale** — keep as a future upgrade
  if the pose approach isn't fluid enough.
- **#3 — single rigid pre-bent arm rotated at the shoulder.** Cheaper than poses but loses the extend/retract
  liveliness (the elbow can't straighten on the strike). Dominated by #1.
- **#4 — keep the arm baked in the body.** Rejected — can't bend the elbow or hold a tool out at all.

## Phased plan
1. **HOLD only** (cheapest visible win): author the bent-arm HOLD pose per direction + its hand anchor; move
   the tool pivot to the hand anchor. Idle now shows the sword held out front with a bent elbow. *(No swing
   changes yet — instant improvement.)*
2. **Swing poses:** add wind-up/strike/recover; phase-lock the pose-swap to the tool animation's `t`; tune the
   non-uniform per-pose timing.
3. **(Optional) side 2-bone rig** for extra fluidity on the profiles, later.

## Honest notes
- Additive, not a rewrite — the swing craft stays; we add an arm + a hand pivot.
- The one thing that needs new art is the arm-pose set (small).
- Full research (source table, verified-vs-inference, integration wiring) in the overnight scratchpad
  `arm_swing_research.md`.
