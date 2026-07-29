# Iteration 1 — Faithful baseline
**Parent:** the existing codebase (`PlayerToolAnimator.cs`).
**What it is:** the shipped curves exactly, with the hand fix and proper framing. The control the other four
get compared against.
**Render:** `iteration-1.gif`

## Prediction — written BEFORE rendering
1. The four tools will be **hard to tell apart** at a glance. Sword and axe differ mostly in duration
   (0.20s vs 0.34s) and a 5-degree wind-up difference; at sprite size I expect that to read as "one is a bit
   slower", not as light vs heavy.
2. The **axe's impact hold will be the one thing that does read** — 28% of its duration frozen at contact.
3. **Contact will be invisible on the other three.**
4. The **net's sweep will look the flattest** — no overshoot, no hold, nothing marking a moment.
5. The **front-facing character will read worse than the side one**.
6. The hoe's drag-back should be visible as the tool pulling in toward the player after it bites.

**Confidence:** high on 1-3, low on 5 — I had never rendered the front view swinging.

## What I actually see
**Prediction 1 was wrong, and wrong for a reason I didn't anticipate.** The four tools are *easy* to tell
apart — but the differentiation comes almost entirely from the **tool sprites**, not the motion. The axe head
is a fat orange wedge, the net a grey bulb, the hoe a thin bar, the sword a pale blade. Silhouette does the
work the timing was supposed to do. So the motion is doing less than I assumed, and I would have credited the
curves for something the art was providing.

**Prediction 2 holds.** The axe genuinely dwells — in the sampled frames it sits at full extension across
consecutive samples where the others have already moved on.

**Prediction 5 was wrong.** The front-facing character reads *fine*, better than expected. Because the
character is armless and the tool is a separate rotating sprite, a front-facing figure with a tool sweeping
across their body doesn't look broken the way an armless figure with a rotating limb would. The floating-hand
design is carrying this.

**Something I did not predict, and it's the real finding:** on the front view the tool passes **across the
character's own body** at the mid-arc, and because the tool draws on top it looks like it's slicing through
his chest. Visible in the net and hoe rows especially. In the side view this never happens because the arc
sweeps into open space. That's a sorting problem the game solves with `_behindPlayer` for the up-facing case,
but the front view needs it mid-arc, not per-facing.

**Also unpredicted:** the hand is nearly invisible against bronze armour at this size — same metal, same
value, and it sits against the body. It reads as part of the breastplate rather than as a hand.

**Prediction 6 unverified** — the hoe's drag is hard to confirm from stills; needs the gif.

## One improvement
Depth-sort the tool against the body **per frame from the arc angle**, not per facing. When the tool's angle
carries it across the torso, draw it behind; when it swings out, draw it in front. That is a few lines, it
fixes the worst artefact in the render, and no source mentioned it because no source was animating a rotating
sprite over a character in a top-down view.
