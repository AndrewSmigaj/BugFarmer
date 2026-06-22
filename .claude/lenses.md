# Review Lenses — re-examination catalog (loop scaffolding)

A **lens** is a single perspective for re-examining work, with the question it forces. The point is to
beat tunnel vision: after a plan or a change, run it past several lenses deliberately. Each entry is sized
to be one step in an automated loop — e.g. an agent prompt:

> "Re-examine `<artifact>` through the **<lens>** lens: `<question>`. Report PASS / RISK / BROKEN with
> evidence (file:line). If RISK/BROKEN, propose the minimal fix."

Pick the lenses that fit the artifact; you rarely need all of them. The ones marked ★ have earned their
keep on this codebase (each caught a real, shipped-would-have-bitten issue).

## The lenses

- ★ **Requirements** — Does this *observably* satisfy what the user actually asked, not just "technically
  work"? (e.g. "*see* hornets attack individual flies" needs the visual, not only the correct kill.)
- ★ **Data / Contract** — Units, scales, serialization round-trips, fixed-point vs float, enum/string
  matches across a boundary. (Caught a ×1000 fixed-point radius-scale bug: threshold must use FixedPoint
  multiply, not raw int².)
- ★ **Timing / Ordering** — Races, on-receipt vs frontier-gated, who-mutates-when, tick alignment, message
  arrival order. (Confirmed BUG_REMOVED is frontier-gated → authority must not remove locally.)
- **Failure / Edge** — empty / missing / duplicate / stale inputs; entity vanished mid-operation; partial
  failure. (Prey id renumber between strike-select and apply → server validates alive ids.)
- ★ **Scale / Performance** — Cost per tick/frame at the *worst* realistic case (boom), on the *actual*
  deployment (a consumer host that's also playing). (Added a broad-phase before an O(P×Q) per-bug scan.)
- **Consistency / Idiom** — Is there an existing util/pattern to reuse? Does it read like the surrounding
  code? (Reused killBugsInSwarm, the catch/validate message pattern, _swarmLegs.)
- **Simpler-Alternative** — Is there a less complex way that still meets the requirement? Am I building two
  features where one would do?
- ★ **Verification** — Does the test actually EXERCISE the path, or can it false-pass? (A sync run with no
  strike is a *vacuous* green; a contaminated/persisted match gives *false* divergence. Assert the thing
  happened.)
- **Determinism** *(domain-specific here)* — float vs fixed-point; map/set iteration order; RNG draw order;
  cross-client + replay equivalence; nothing wall-clock. (The whole bug sim lives or dies on this.)
- **Docs / Drift** — What comments/docs/contracts does this change now make false? Reconcile at completion.
- **Blast-radius / Rollback** — If this is wrong, what breaks? Is each commit coherent and revertible? Does
  the interim state (between commits of an atomic change) still work? (Split the predation flip so predation
  never breaks mid-way.)
- **Security / Authority** — Who is allowed to do this? Is input validated? Can a client lie? (PredationStrike
  is authority-only + server-validated.)

## Notes for automating this
- A lens pass is cheap insurance before an expensive build/run. Run the high-value lenses (★) on any plan
  that touches sync, data formats, or the hot loop.
- Lenses compose with the project's existing gates (Go compile → `go test ./world/` → Unity build →
  fresh-match harness → `tools/sim-determinism`). Lenses find issues *before* the gates; the gates confirm.
- A skeptical sub-agent per lens (especially Verification + Data/Contract) catches things the author's
  tunnel vision misses — and has, on this codebase, including an error in another sub-agent's report
  (always re-verify load-bearing claims against the real code).
