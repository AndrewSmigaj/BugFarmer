# Iteration 5 — Procedural spring
**Parent:** Orange Duck, *Spring-It-On* (`sources/05`).
**What it is:** the authored segments are deleted. The pivot angle is driven by a damped spring toward a target
that moves once (wind-up target → strike target at 18%). Weight becomes `(frequency, damping ratio)` per tool —
`freq = 5.5 - 3.0*w`, `ratio = 0.45 + 0.35*w` — instead of four hand-tuned segment tables.

## Prediction — written BEFORE rendering
1. **This should structurally fix iteration 4's worst defect.** A spring's overshoot is a *transient*: it goes
   past the target and comes back. `ease_out_back` settles *at* the exaggerated value. So the tool should end
   near its target rather than lying across the character's legs — and the exit pop should be small, comparable
   to iteration 1's, without anyone tuning it. This is the claim worth testing.
2. **The axe will not finish its swing.** `freq = 5.5 - 3.0*1.0 = 2.5 Hz` is a period of 0.4s, and the axe's
   swing is 0.34s. Under one full period, heavily damped (ratio 0.80) — I expect it to still be travelling when
   the animation ends, stopping somewhere short of the target. That is the classic failure of putting a spring
   in a fixed-length window: the spring doesn't know about the deadline.
3. **If 2 is right, weight differentiation comes out backwards.** The heavy tool would cover *less* arc than
   the light one, so an axe would swing a shorter distance than a net — the opposite of weight.
4. **The teleport will be gone or much reduced**, because a spring's velocity is continuous — it accelerates
   into the strike instead of jumping. This is the first approach that could actually fix it, and it fixes it
   for a reason (continuous velocity), not by tuning.
5. **There is no contact time.** `DESIGN.md` flagged this before implementation: a spring has no segment
   boundary to fire contact on, so the hit would have to be triggered by angle threshold or by a separate
   timer. This is a design cost, not a render defect, and the render can't show it.
6. **The smear threshold `abs(v) > 900` is an arbitrary number in arbitrary units** and I expect it to be
   wrong — firing never, or on nearly every frame.

**Confidence:** high on 2 and 5, and 1 is what this approach is for.

## What I actually see
| tool | target | furthest reached | settles at | shortfall | max frame jump | smear |
|------|--------|-----------------|-----------|-----------|----------------|-------|
| sword | -50.0 | -62.1 | -56.2 | -6.2 | **20.0** | 5/18 |
| axe | -55.0 | -55.1 | -55.1 | -0.1 | **9.2** | 0/30 |
| net | -45.0 | -59.5 | -42.7 | +2.3 | **20.6** | 6/22 |
| hoe | -45.0 | -49.1 | -49.1 | -4.1 | **11.8** | 3/21 |

**Prediction 1 confirmed — the structural win is real.** The sword reaches -62.1 and comes back to -56.2: the
overshoot is a *transient that returns*, which is exactly what `ease_out_back` cannot do. And it falls out of
the maths; nobody tuned it. Exit pop against the game's `IDLE_ANGLE`:

| approach | sword | axe | net | hoe |
|----------|-------|-----|-----|-----|
| 1 baseline | 15.0 | 20.0 | 10.0 | 23.0 |
| 4 Cooper | 36.2 | **64.0** | 25.8 | 38.1 |
| 5 spring | 21.2 | 20.1 | **7.7** | **14.1** |

The spring lands closest to rest overall without anyone aiming it there.

**Prediction 4 confirmed, and this is the headline.** Max single-frame jump roughly **halves**: 9-21 degrees
against iteration 3's 29-44 and iteration 4's 29-41. The teleport is a symptom of discontinuous velocity, and a
spring has continuous velocity by construction. No authored curve in this lab achieved that, and none could
without hand-tuning each segment boundary.

**Prediction 2 was wrong, and I was wrong for an instructive reason.** I predicted the axe wouldn't finish —
2.5 Hz is a 0.4s period against a 0.34s swing. It lands on **-55.1 against a -55.0 target**. I confused the
*undamped period* with *time to converge*: at ratio 0.80 the axe is near critically damped, and a critically
damped system converges monotonically without needing a full oscillation. The period was the wrong number to
reason from.

**Prediction 3 is moot, but the weight mapping is backwards.** Overshoot past target: sword 12.1, net 14.5,
hoe 4.1, axe **0.1**. The *light* tools ring and the heavy axe doesn't move past its target at all — because
`ratio = 0.45 + 0.35*w` maps heavy to *more damped*. But a heavy tool should be **hard to stop**, which is
*less* damping, not more. The parameterisation has weight inverted. That's a mapping error inside a sound
model, not a problem with springs.

**Prediction 6 half right.** Smear fires 0/30 on the axe and 5-6 on sword and net — not degenerate, but the
heaviest, most impactful tool is the one that never smears. `abs(v) > 900` is a raw threshold on an
un-normalised unit, so it means different things per tool.

**Unpredicted: the spring has no anticipation at all.** The sword sits at +50 from t=0.00 to t=0.12 and is
still at +46 at t=0.24. The spring starts *at* its wind-up target, so it has nothing to do until the target
moves at 18% — the same dead wind-up as iteration 3, for a completely different reason. A spring only animates
a gap between where it is and where it's going; give it none and it sits still.

## One improvement
**Invert the weight mapping and give the spring a gap to close.** Heavy = *lower* damping ratio (momentum,
hard to arrest) rather than higher, and start the wind-up target beyond the rest pose so the spring has real
distance to travel during anticipation. Both are one-line changes to a model that has already earned its place
by halving the frame jump and returning to rest on its own.
