# Iteration 2 — Impact-first
**Parent:** fighting games — Sakurai (`sources/08`), CritPoints (`07`), Dead Cells (`04`).
**What it is:** iteration 1's arcs completely unchanged. The only addition is what happens **at contact**:
a freeze of the tool and hand, held longer for heavier tools (0.06 + 0.10*weight of the duration), capped.
Tests the claim that impact lives at the moment of connection, not in the arc.

**Multiplayer constraint:** the freeze is a held *display* frame only. It never touches the sim, the player's
position, or anything feeding ComputeStateHash — Sakurai's warning is about exploit windows, ours would be an
outright desync.

## Prediction — written BEFORE rendering
1. The sword and net will improve **most**, because iteration 1 gave them no marked moment at all. The axe
   will improve **least** — it already holds, so this partly duplicates what it has.
2. On the axe the two may **stack badly**: its existing 28% angle-hold plus a new freeze could read as a
   stall, making it feel sluggish rather than heavy.
3. Because the tool sprite doesn't change during a freeze, the pause may read as a **dropped frame or a stutter**
   rather than as impact — the fighting-game references all pair the freeze with a vibration or a flash, and I
   have only implemented the pause.
4. In a stills grid the freeze will show as **repeated identical frames**, which is a way to verify it fired.
5. Contact timing is my estimate per kind (0.65/0.55/0.50/0.50), not read from the game's onContact. If those
   are wrong the freeze will land visibly off the strike.

**Confidence:** high on 1 and 4, genuinely unsure on 3 — that is the whole question this iteration asks.

## What I actually see
**The freeze fires, and it is holding the wrong frame.** Measured per tool (angle at the freeze vs angle at
the declared contact time):

| tool | frozen frames | angle held | vs contact |
|------|---------------|-----------|-----------|
| sword | 1 | -29.9 deg | **30 deg PAST contact** |
| axe | 5 | 0.0 deg | 0 — but see below |
| net | 1 | -24.6 deg | 2 deg past |
| hoe | 3 | 0.0 / -2.3 / -4.3 deg | 0-4 past |

In the render this is visible directly: frame 11 has the sword horizontal, pointing at the dummy — that IS the
strike pose. Frame 12 is the one held, and the sword is already angled down past the dummy. So the pause lands
on the *recovery*, and reads as a hitch after the swing rather than a hit.

The cause is that `ease_out_back` leaves the contact angle **fast** — 30 degrees in one 11ms frame. I froze the
wall clock while the animation clock kept its sampled position, so whatever frame happened to be next got held.
Fighting games hold the **contact pose**; I held *the frame after* contact.

**Prediction 2 was right, and for a stronger reason than I gave.** I guessed the axe's existing hold and the
new freeze would "stack badly". They don't stack at all — `_shipped`'s chop returns `a = aim` for its whole
28% hold, so the five frozen frames are *already identical images*. The freeze makes a static hold longer and
changes nothing else. On the axe this addition is a no-op with a cost.

**Prediction 1 was wrong on the net.** I expected the net to gain most. Its freeze window (0.07 of a 0.25s
sweep, 17ms) is **shorter than one frame**, so it caught a single frame and the sweep still has no marked
moment. Worse, `sweep` has no meaningful contact time at all — the trail *is* the catch area, so "0.50" is an
invented number for a motion whose whole design is that no instant is special. Freezing a sweep is a category
error, not a tuning problem.

**What actually improved:** the hoe, the only tool where the freeze landed near contact, is long enough to see,
and doesn't duplicate an existing hold.

**Prediction 3 unresolved.** I can't tell whether a pause with no vibration reads as impact or as a dropped
frame, because on three of four tools the pause isn't landing where impact is. It needs re-testing after the
fix below.

## One improvement
**Freeze the pose, not the clock:** during the freeze window, clamp the angle and offset to their values at
the contact time, then resume. That is what makes the eye read a collision, and it costs one clamp. Its
corollary is that a freeze belongs only on motions that *have* an instant — sword, axe, hoe — and the net
should get a different treatment (a trail that lingers), not a pause.
