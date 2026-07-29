# Swing design — what the research says, and the five approaches

Written **before** any iteration is implemented, so the five can't quietly collapse into five tunings of
whichever one happened to work first. Each has a **different parent**; approaches with different origins
can't converge by accident.

Evidence: `sources/01`–`10`. Dead ends: `sources/00-dead-ends.md`.

---

## What we have today
`PlayerToolAnimator.cs` rotates a `ToolPivot` at the player's centre; `HeldTool` hangs off it at the profile's
offset. Seven `AnimKind` cases, each a hand-written 3-or-4-segment lerp with per-kind easing. Contact fires at
a segment boundary. A `TrailRenderer` rides the tool head. Since yesterday the hand rides the handle too, at a
per-tool measured grip.

It is competent and it is entirely **authored** — every number was chosen by hand, per tool.

## The central finding: a real contradiction
The two most authoritative sources disagree about where the time goes.

- **Stardew** front-loads: 55ms + 45ms of a ~200ms swing is wind-up, then four fast frames. Roughly **half the
  swing is anticipation** (`sources/03`).
- **Cooper** (AC, Uncharted) says the opposite for *player-initiated* attacks: "Too long and the move will feel
  unresponsive, removing agency from the player" — and "A sword that swings immediately might look light, so
  it is the game animator's task to add that weight at the end in the follow-through" (`sources/06`).

Both ship successfully. This is a genuine fork, not a right answer, and it deserves two of the five slots.

Our current code sits nearer Cooper — 15% anticipation on Swing — but then spends its weight budget on an
overshoot rather than an exaggerated recovery.

## What everyone agrees on
- **Something must happen AT contact.** Hitstop exists so the eye can register the collision (`07`), scales
  with power and needs a cap (`08`), and Dead Cells pairs a 1-frame freeze with a time-scale dip (`04`).
  We currently hold the tool's *angle* on Chop only, and never pause anything.
- **Overshoot when stopping**, scaled by speed (`01`).
- **A smear sells a fast arc**, one or two frames only, never every frame (`01`, `09`).

## Constraint the single-player sources don't know about
This is a **multiplayer** game. Hitstop must be a **local visual freeze of the tool and hand only** — never
the sim, never the player's position, never anything feeding `ComputeStateHash`. Sakurai's own warning is
about freezing creating exploit windows (`08`); ours is stronger, because a freeze that touched sim state
would desync clients outright.

---

## The five approaches

**1 — Faithful baseline.** *Parent: the existing codebase.*
What we have now, with the hand fix, rendered properly in a scene. Exists so the other four have something
honest to be compared against, and so "better" is a claim with a control.

**2 — Impact-first.** *Parent: fighting games — Sakurai, CritPoints, Dead Cells.*
Keep the current arcs; add everything that happens at the moment of contact. A 2–3 frame freeze of tool and
hand, a 1-frame vibration, damage-scaled duration with a hard cap. Tests the claim that contact, not the arc,
is where impact lives.

**3 — Anticipation-heavy.** *Parent: Stardew Valley's measured frame data.*
Re-time to Stardew's distribution: roughly half the swing in wind-up, then a fast strike, with recovery
length as the per-tool weight knob. Deliberately the opposite of 4.

**4 — Responsive, weight-in-recovery.** *Parent: Cooper's animation-principles-for-games.*
Strike on the first frame with almost no wind-up; spend the entire budget on an exaggerated follow-through,
with a separate earlier "player regains control" point so responsiveness isn't hostage to the visual.

**5 — Procedural spring.** *Parent: Orange Duck's spring maths.*
Delete the authored segments. Drive the pivot angle with a damped spring toward a moving target; weight
becomes `(frequency, damping_ratio)` per tool instead of four hand-tuned tables. Under-damping produces the
overshoot for free. Known risk: a spring has no guaranteed contact time, so contact must be triggered
explicitly rather than falling out of a segment boundary.

**Smearing** (`09`) is deliberately *not* an approach — it's a visual layer that could ride any of them. If
one of the five wins, smear gets tested on top of the winner rather than muddying the comparison.

---

## How each will be judged
Each iteration writes `iteration-N.md` with three separate sections:

- **Prediction** — written *before* the gif is rendered.
- **What I actually see** — observation of the render, not restatement of intent. This is the section I keep
  failing at; it exists to make a wrong call legible rather than smoothed over.
- **One improvement.**

Every demo shows **both the side and the front-facing sprite**, four tools (sword, axe, net, hoe), framed so
the character and the whole arc fill the frame.

## Success would look like
Four tools that are told apart at a glance with no per-tool animation authored, a contact moment the eye can
register at sprite size, and no reliance on anything that would desync a second client.
