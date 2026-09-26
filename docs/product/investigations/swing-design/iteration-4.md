# Iteration 4 — Responsive, weight in the recovery
**Parent:** Cooper, *Animation Principles for Games* (`sources/06`) — "A sword that swings immediately might
look light, so it is the game animator's task to add that weight at the end in the follow-through."
**What it is:** almost no anticipation (12% of the swing), then the entire remaining budget spent on an
**overshoot scaled by weight** — the axe carries far past the target, the net barely at all. The deliberate
opposite of iteration 3. No freeze; impact treatment stays isolated in iteration 2.

## Prediction — written BEFORE rendering
1. **The overshoot is the first weight cue in the lab that is a real function of `weight` AND visible.** The
   heavier tool should travel visibly further past the dummy. Iteration 3's weight knob was a recovery *rate*,
   which is a change in a change and reads as nothing; a difference in *where the tool ends up* is a difference
   in a position, and positions are what a viewer can see. I expect this to be the first render where the four
   tools differ by motion rather than by silhouette.
2. **The strike will still teleport**, for iteration 3's reason — a fast arc on a rotating sprite is a big
   per-frame angle jump regardless of which end of the swing the time is spent on. Front-loading vs
   back-loading the budget doesn't change that a 50-degree arc in ~2 frames is 25 degrees a frame. The fix for
   that is smear or more frames, not timing, and I expect this iteration to demonstrate it isn't a timing
   problem at all.
3. **The axe will overshoot too far and look broken.** `aim - half - half*(0.30+0.50w)` with w=1.0 puts it
   around -100 degrees, and `ease_out_back` overshoots *past* its own target, so worse. At that angle the tool
   points down and behind the player. I expect it to read as dropping the axe rather than following through.
4. **The front-facing character will be worse hit than the side one**, because its -60 degree aim offset stacks
   with the overshoot and drives the tool across the body — the sorting artefact from iteration 1, now with the
   biggest angles in the lab behind it.
5. If 1 and 3 are both right, the lesson is that **overshoot needs a clamp**, and the interesting question
   becomes what the clamp is measured against — the body, or the arc.

**Confidence:** high on 2 and 3, and 1 is the claim actually worth testing.

## What I actually see
| tool | start | furthest past aim | settles at | max frame jump |
|------|-------|------------------|-----------|----------------|
| sword | +50 | **-78.3** | -71.2 | 41.2 deg |
| axe | +55 | **-108.9** | -99.0 | 29.0 deg |
| net | +45 | -66.8 | -60.8 | 29.7 deg |
| hoe | +45 | -80.4 | -73.1 | 30.1 deg |

**Prediction 1 confirmed — this is the first render where the tools differ by MOTION.** The axe visibly
travels further past the dummy than the sword, and the net barely past at all. A difference in where a thing
ends up is a difference a viewer can see; iteration 3's recovery-*rate* knob was a change in a change and read
as nothing.

**Prediction 2 confirmed.** 41 degrees in one frame on the sword. Front-loading versus back-loading the time
budget changes nothing about this, which settles it: **the teleport is not a timing problem.** It is an
angular-velocity-versus-framerate problem, and the fixes are smear or subframe ghosts, not a different curve.

**Prediction 3 confirmed, and worse than predicted.** At t=0.48 the axe is at -101 degrees, drawn to the lower
left of the character with nothing connecting it — on the front-facing character it reads as an axe lying in
the grass beside him, not an axe he is holding.

**Prediction 4 confirmed.** The front character's -60 degree aim offset stacks with the overshoot; the tool
leaves the body entirely.

**The unpredicted finding, and it applies to every approach including the shipped one.**
`ease_out_back` **settles at the exaggerated end value** — it doesn't overshoot *past a rest* and come back, it
overshoots past its target and then sits at the target, which is already the exaggerated angle. So the sword
spends t=0.47 to t=1.00 — over half its animation — with the blade lying across the character's legs. I
implemented overshoot as a *destination* rather than as a transient. Cooper's follow-through returns to a
neutral idle; mine has no return.

**And the lab has been hiding this from me.** The loop restarts at t=0, so an approach's end pose costs it
nothing here. The game does not do that: `RestoreIdle()` (`PlayerToolAnimator.cs:204-222`) sets
`localRotation`, `localPosition` and `localScale` **directly, with no lerp**, so the tool cuts instantly from
its swing-end pose to the idle pose (`IdleAngle = -35`, `IdleOffset = 0.4`, `IdleScale = 0.75` — smaller at
rest than mid-swing, per the comment at :183). Every swing ends in a pop, and the pop is as big as the gap
between where the swing left the tool and -35 degrees. Iteration 1's sword ends at -50, a 15 degree pop.
**Iteration 4's axe ends at -99: a 64 degree pop plus a size change.** So the more faithfully I follow Cooper's
advice, the worse the exit gets — because the advice assumes a follow-through that returns, and this codebase
has no return, only a cut.

## One improvement
**Make the swing end where the idle pose is.** Either land the recovery on `IdleAngle` so the restore is
invisible, or give `RestoreIdle` a short blend so a swing can end anywhere. The first is free and the second is
more flexible; both beat what exists. This is worth more than any of the four arcs compared so far, because it
is a defect in every one of them and it is the last thing the player sees each swing.

**Harness gap to fix before iteration 5:** the lab must play a swing and then hold the **idle pose**, so the
exit is visible instead of hidden by the loop.
