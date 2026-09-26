# Iteration 3 — Anticipation-heavy
**Parent:** Stardew Valley's measured frame data (`sources/03`).
**What it is:** re-timed to Stardew's distribution — **50% wind-up**, 20% strike, 30% recovery, with recovery
*length* as the per-tool weight knob (a heavy tool's recovery doesn't finish before the swing ends). Deliberately
the opposite of iteration 4.

Carries **no freeze** — impact treatment belongs to iteration 2 and to whatever wins. One variable at a time,
or the comparison is worthless.

## Prediction — written BEFORE rendering
1. **This will look better than iterations 1 and 2**, and I distrust that expectation, because it's the
   approach with the most reputable parent and I want it to win. Stating it so it's checkable.
2. The **wind-up will be clearly visible** — half the swing spent raising the tool is a lot at 30fps. Where
   iteration 1's 15% anticipation reads as "already swinging", this should read as a decision to swing.
3. **The strike will feel abrupt** — 20% of 0.20s is 40ms, three or four frames for the whole arc. I expect the
   tool to appear to teleport past the dummy rather than travel through it, which is exactly what the smear
   flag exists for.
4. The **weight differentiation will finally come from motion rather than sprite silhouette**, because the
   recovery divisor is the first thing in the lab that's actually a function of `weight`. The axe (w=1.0) gets
   a recovery stretched 2.5x, the net (w=0.1) almost none.
5. **The heavy tools will not return to rest.** `u = min(1, u/(0.4+0.6w))` means the axe's recovery is clipped
   at the end of the swing, so it should visibly *snap* back to neutral between reps. That's a bug I expect to
   see rather than a feature.
6. On a **0.20s sword** half of 200ms is 100ms of wind-up before anything happens. Cooper's objection is that
   this costs responsiveness; I expect it to *look* good here precisely because a demo loop has no input latency
   to feel. **The render cannot settle the Stardew-vs-Cooper question** — it can only show which looks better,
   not which feels better to a player holding the button. Recording that now so I don't overclaim later.

**Confidence:** high on 2 and 5, and 6 is the honest limit of this whole method.

## What I actually see
**The wind-up is invisible, and the reason is the most useful thing found so far.**

Measured across all four tools, the wind-up spends **50% of the time covering 17.4% of the distance**:

| tool | wind-up travel | total arc | biggest single-frame jump |
|------|---------------|-----------|--------------------------|
| sword | 17.3 deg | 100 deg | **44.2 deg** |
| axe | 19.2 deg | 110 deg | 28.6 deg |
| net | 15.6 deg | 90 deg | 34.4 deg |
| hoe | 15.8 deg | 90 deg | 35.1 deg |

In the render the first five sampled frames of the sword swing — t=0.00 through t=0.59, half the animation —
are the same pose. Seventeen degrees spread over nine frames is under two degrees a frame, which at this sprite
size is below one pixel of tip movement. The character stands there holding a sword up, then the sword is
suddenly on the other side.

**Prediction 1 was wrong, and I'm glad I wrote it down.** I expected this to look best because its parent is
the most reputable. It looks the worst of the three so far.

**The real finding: Stardew's 50/20/30 is a split of POSES, not of a continuous arc.** Stardew's wind-up frames
are *distinct drawings* — the character rears back, the whole silhouette changes. Copying the timing onto a
sprite that rotates continuously produces half a swing of nothing, because a rotation has no pose to hold, only
a position to be at. **Frame-data timings from a hand-drawn game do not transfer to a rotating sprite.** No
source warned about this because every source was describing drawn frames.

**Prediction 3 confirmed, hard.** The sword covers **44 degrees in one frame** at the strike. It teleports.

**Prediction 5 was wrong and backwards.** I predicted heavy tools would fail to return to rest. In fact
`min(1, u/(0.4+0.6w))` makes the *light* tools finish their recovery early — the net completes at 46% of its
recovery window and then sits still. The axe (w=1.0) is the only one that uses its full recovery. So the dwell
is on the light tools, which is the opposite of what weight should buy.

**Prediction 6 stands as the honest limit.** This render cannot settle Stardew-vs-Cooper. It shows the arc, not
the responsiveness — a demo loop has no button press to feel late.

## One improvement
Spend the wind-up on **distance, not time**: pull the tool back through a *large* angle (past the shoulder,
120-150 deg from the strike) so half the duration is also a real fraction of the travel. A continuous rotation
has to buy anticipation with degrees, since it has no drawn pose to hold.
