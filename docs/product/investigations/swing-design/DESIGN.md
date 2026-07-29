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

---

# RESULT — what the five iterations settled

Written after all five rendered. Scores are what the renders and the measurements show, not what I expected.

| | 1 baseline | 2 impact-first | 3 Stardew | 4 Cooper | 5 spring |
|---|---|---|---|---|---|
| max frame jump (sword) | 41 deg | 41 deg | **44 deg** | 41 deg | **20 deg** |
| overshoot returns to rest | no | no | no | **no — settles at the exaggerated value** | **yes** |
| exit pop vs `IdleAngle` (axe) | 20 deg | 20 deg | 20 deg | **64 deg** | 20 deg |
| weight visible in the motion | no | no | no | **yes** | yes, but **inverted** |
| tuning cost | 4 hand tables | 4 + contact times | 4 tables | 4 tables | **2 numbers per tool** |

## The pick: the spring (5), with grafts from 4 and 2

It wins on the two things no authored curve managed, and wins them **structurally** rather than by tuning:

- **It halves the per-frame angle jump** (20 deg vs 41-44). The "teleport" that iterations 3 and 4 both showed
  at opposite ends of the time budget was never a timing problem — it was discontinuous velocity, and a spring
  has continuous velocity by construction.
- **Its overshoot returns.** `ease_out_back` settles *at* the exaggerated end value, which is why iteration 4's
  sword spends half its animation with the blade across the character's legs. A spring goes past and comes back
  because that is what a spring is.
- It costs **two numbers per tool** instead of a hand-authored segment table, so a new weapon is free.

**Graft from 4 (Cooper):** weight expressed as a *difference in where the tool ends up* is the only weight cue
in the whole lab a viewer can actually see. Keep it — but invert the spring's mapping, because
`ratio = 0.45 + 0.35*w` makes the heavy axe the most damped when heavy should mean **hard to stop**.

**Graft from 2 (fighting games):** a freeze at contact, fixed to hold the **contact pose** rather than the next
frame — and only on tools that have a contact instant. A sweep does not; its trail is the catch area.

**Reject from 3 (Stardew):** the 50/20/30 frame distribution. Stardew's split is a split of *poses*; ported to a
rotating sprite it spends 50% of the time on 17% of the distance and reads as nothing happening.

## What the lab could not settle
- **Stardew vs Cooper on responsiveness.** A demo loop has no button press, so it shows which arc looks better,
  never which feels better to a player holding the button. That needs the game.
- **Whether a pause reads as impact or as a dropped frame** — iteration 2's freeze never landed on contact, so
  the question is still open.
- **Contact timing under a spring.** A spring has no segment boundary, so contact has to be fired by an angle
  threshold or a separate timer. Flagged before implementation; still true.

## The three defects worth more than the choice of arc
Found along the way, all present in the **shipped** animator, all independent of which approach wins:

1. **The swing has no exit.** `RestoreIdle()` (`PlayerToolAnimator.cs:204-222`) sets rotation, position and
   scale directly with **no lerp**, so every swing ends in a hard cut to `IdleAngle = -35` plus a scale change
   from 1.0 to `IdleScale = 0.75`. Either land the recovery on the idle pose or blend the restore.
2. **The tool draws through the body.** In the front view the arc carries the tool across the character's torso
   and, drawing on top, it appears to slice through him. `_behindPlayer` handles only the up-facing case; the
   sort needs to come from the **arc angle per frame**, not from facing.
3. **The hand disappears against its own armour.** Same metal, same value, sitting against the body. It needs a
   darker outline or a rim, or the floating-fist design stops reading as a hand at sprite size.

## Multiplayer, restated
Everything above is **presentation**. The freeze is a local hold of the tool and hand sprites; no approach here
touches player position, sim state, or `ComputeStateHash`. A hitstop that paused the sim would desync clients
outright — a stronger constraint than the exploit-window warning the fighting-game sources give.
