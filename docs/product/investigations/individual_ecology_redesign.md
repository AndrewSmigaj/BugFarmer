# Individual-level ecology & combat — design + feasibility (PROPOSED)

**Status:** PROPOSED (design for owner review; cold-critiqued once, findings folded in). Nothing built. Rollback
checkpoint = commit `3bd9bc4`.
**THE GOAL (owner's, settled — not mine to re-decide):** an individual wasp goes and kills an individual fly,
leaves a **real** corpse, and eats it until it disappears — with a chance it leaves the corpse behind instead.

**CPU feasibility (owner asked me to judge only this):** the full deterministic model is CPU-FEASIBLE — the sim
is a small delta over the render+movement already running; the spatial grid makes it trivial (§3.3). This is a
feasibility finding, NOT a direction decision.

**DIRECTION (hybrid vs full) = the OWNER'S call, NOT decided here.** (I wrongly recorded a "decision" to go full;
removed. The direction is the owner's; this doc only supplies the honest feasibility so they can choose.)
**Owner decision that drives it:** simulate the ecology + combat at the **individual** level (each bug its own
creature that hunts, eats, breeds, fights), **client-side deterministic**, server thinned to persistence — NOT
more server traffic. This doc is honest about what that actually costs.

---

## 1. The honest framing (corrected after review)
The **positional** sim is already individual + deterministic + in-sync: every client runs `BugAgent.SimulateTick`
per bug and `sim-determinism` proves byte-identical positions. **But the ecology *brain* is NOT client-side
today** — satiation, foraging, breeding, hunt/flee all run **server-side in float + shared-RNG** (`match.go:1218`
`deltaTime` float; `match.go:1378-1419` satiation/breed/forage float drains; `predation.go:445` `state.Rng`
hunt re-aim; `predation.go:15` "clients replay outputs, never decisions"). The **only** individual decision that
ships client-side is strike victim-selection (`SwarmManager.cs:607-696`).

So this is **not** an extension of a client decision-sim — it is a **from-scratch reimplementation of the entire
server ecology brain as a deterministic, fixed-point, counter-RNG sim that every client runs identically.** That
is the honest scope, and it's large. What we *reuse* is real but narrower than I first claimed: the deterministic
**position** substrate, the **ledger + authority-report + late-join** machinery, and the **watched-only** match
lifecycle. What we **rebuild deterministically**: satiation, forage (incl. a food field), breeding, hunt/flee,
the population director, nests, broods, and weather-response.

**The payoff that makes "no traffic" real:** once the whole sim is deterministic + closed, every client computes
the *same* kills/births/eats from the same inputs — so those need **no per-event messages at all** (they're
derived, not reported). Traffic actually goes *down* vs today (no per-swarm movement legs — bugs self-steer to
their own deterministic targets; no strike reports). The server only needs a **periodic persistence digest** +
the low-volume non-deterministic inputs (player cells — already synced; weather onset — already broadcast). This
is the strongest argument for the design, and it only holds if we commit to *full* determinism (no half-measures).

## 2. What "individual level" means
Each bug is an agent with its **own** hunger, goal + target (a specific food cell or a specific prey bug), a small
FSM (WANDER → SEEK-FOOD → EAT / SEEK-PREY → PURSUE → STRIKE → FEED → BREED → FLEE → DIE), and its own life (aging
is already per-bug via `DeathTick`). Populations become **emergent**. Combat's *decision/targeting* branch is the
same FSM (pursue a *player* instead of a *fly*); its *hit-resolution* stays separate (see §4-D).

## 3. Architecture
### 3.1 State + the closed deterministic sim
- **Per-bug sim state** (position, velocity, satiation, goal, target-id, FSM phase, breed-progress): client-side,
  deterministic (fixed-point + counter-RNG keyed on worldSeed/bugId/tick). Rides the join snapshot (extend
  `BugSampleData`; the `land_ticks` pattern).
- **Inputs a bug reads — all must be deterministic + zone-wide on every client:** other bugs' positions (already
  deterministic); player **cells** (already `PLAYER_CELL_ENTER`); **weather** (rain/drought — server-RNG
  scheduled today `handlers_env.go:224-240`, but `WeatherUntilTick` is already broadcast `messages.go:357` → sync
  the onset as a low-volume event); and **the food field** (§4-B — a new deterministic subsystem, the biggest
  Stage-0 build).
- **Outputs are DERIVED, not reported** (the closed-sim payoff): a kill/birth/eat is computed identically by every
  client → applied locally, no message. The **authority** client additionally emits a **periodic persistence
  digest** (population + per-bug state) so the server can save/load; not per-event.

### 3.2 Server role + authority + watched-only (verified)
The server thins to: persistence (save/load), spawn + hard caps, and the **population governor backstop** (§4-G).
It stops running the per-swarm ecology think. **Watched-only is confirmed correct** — the match hard-pauses at 0
presences (`match.go:833`), so unwatched zones already don't progress; moving the sim to clients stops no headless
ecology. Caveat (verified): the **authority client becomes load-bearing for a much bigger computation**, and
authority handoff must deterministically recompute the whole brain, not just positions (it already recomputes
positions correctly, so the machinery exists — but the surface grows).

### 3.3 The per-bug FSM + CPU
FSM as §2; steering = seek/arrive/flee/separation (fixed-point, already researched for combat). **CPU is the
weakest axis** — my first budget was too rosy. The real costs (per the critique): **threat/flee scanning can't be
throttled** (a bug must notice a predator/player *every* tick or it walks into them), the existing individual
path already runs nested O(P×Q) **plus a per-pair Bresenham raycast** (`SwarmManager.cs:653-668`) **plus per-tick
List/HashSet allocation**, and the cost is on **every** client (all run the identical think), so **low-end clients
are the gate.** Mitigations (deterministic): one shared **spatial-hash grid** for both throttled target-picks and
every-tick threat-scans (coarse), conditional raycasts (only for a committed strike, not every pair), and
**pooling** to kill GC. Whether this holds at ~300 bugs on a low-end client is a **profiling question**, not an
analysis one — it is the #1 thing the spike (§5) must answer.

## 4. The hard problems (honest — each with an approach; two are cracks that shape the approach)
| # | Problem | Why it's real (verified) | Approach |
|---|---|---|---|
| A | **It's a from-scratch deterministic port of the whole ecology brain**, not an extension | brain is server float+RNG (`match.go:1378-1419`, `predation.go:445`) | accept the scope; stage it; reuse only the position/ledger/authority substrate |
| B★ | **Food is continuous-float regen with NO event** — can't "ride the ledger like ground food" | `handlers_farming.go:1588/1645/1651` float regen; `match.go:1389/1405` float drains, no event | **Stage 0 = a deterministic FOOD FIELD**: fixed-point per-cell regen (closed-form from tick) + fixed-point consumption; a real subsystem. Gate: 2-client hash-identical field |
| C | **CPU at ~300 deciders on every (incl. low-end) client**, threat-scan every tick + raycasts + GC | `SwarmManager.cs:653-668` raycast/alloc | shared spatial grid + conditional raycast + pooling; **profile is the proof** (§5) |
| D★ | **Combat only HALF-unifies** — exact player pos isn't in the synced world | cell-only is deterministic; exact x/y is display/authority-only (`SwarmManager.cs:698-721`) | the DECISION branch unifies (reads player cell, deterministic); **hit-resolution + HP stay authority-reported + display-HP as today** — do not try to make HP emergent |
| E | **Populations re-tune (emergent)** | balance was tuned on swarm meters | new per-bug params; re-run `ecology-tuning`; keep the swarm path alive until the re-tune passes |
| F | **The Director/nests/broods governor is server-only + RNG** and is what stops crash/runaway | `ecology_director.go:64-73` RNG cull/reseed on zone pop; `nests.go`/`brood.go` stateful | **keep the Director as a deterministic (or server-backstop) population governor**; give the nest a single-owner consistency story (nest = persisted structure; the deposit decision is the individual's, applied to the server-owned nest via the digest) |
| G | **Determinism surface + snapshot size grow** | more per-bug state + food field | fixed-point/counter-RNG/sorted everywhere; extend `sim-determinism` to drive the full ecology; watch snapshot size (prior 256KB→8MB late-join incident) |

## 5. THE GO/NO-GO SPIKE (do this before committing to the full redesign)
The two cracks (B food-field determinism, C CPU) are empirical, not analytical. A **1-2 day Stage-0/1 spike**
answers them and de-risks the whole plan:
1. **Deterministic food field** — build the fixed-point per-cell regen+consume; run it under `sim-determinism` +
   2-client → must be **hash-identical**. Proves the determinism crack (B) is closable.
2. **Individual foraging on the real ~300-bug zone + `perf-tuning` profile** — bugs seek/eat their own food with
   the spatial grid + threat-scan-every-tick + pooling. Proves (or kills) the CPU claim (C) on a low-end target.
**If both pass:** proceed to the staged build (below) with high confidence. **If CPU fails:** fall back to the
hybrid (§8 Fork 3 — only watched/combat/predator bugs go individual; ambient flies stay aggregate). Either way we
learn the truth cheaply instead of committing to a big port on a hope.

### Staging (after the spike, each gated + reversible)
- **S0** deterministic food field (done in the spike). **S1** individual forage/feed (spike). **S2** individual
  predation (wasp visibly hunts+eats a fly) + the combat decision branch. **S3** individual breed/death → emergent
  populations + Director re-home + re-tune. **S4** thin the server, retire swarm-aggregate decisions. Keep the
  swarm path runnable until S3's re-tune passes.

## 6. Determinism plan
Fixed-point + counter-RNG + sorted iteration for every per-bug decision, the food field, breeding, and the
governor; inputs = ledger-synced world (food field, positions, player cells, weather). Closed sim → outputs
derived, not messaged; persistence via a periodic authority digest. Gates: extended `sim-determinism` (full
ecology, two-run identical) → **the S0/S1 spike's food-field + 2-client hash is the first hard gate**; the
2-client `run_sync_latejoin` (co-located + spawn-apart) `SYNC: IDENTICAL`; `perf-tuning` profile; Go tests for the
persist/digest path.

## 7. Certainty (post-critique — honest, lowered where the critic exposed thin evidence)
| # | Dimension | Score | Band | Evidence / Falsifier |
|---|---|:--:|---|---|
| 1 | Requirements | 86 | Strong | Satisfies the owner's ask (individual, synced, no traffic); the critic agrees the 3 constraints are satisfiable. Falsifier: they also want unwatched zones to progress (needs a server aggregate drift layer) |
| 2 | Comprehension | 76 | Plausible→Strong | Substrate verified at file:line; **I initially mis-scoped it as an "extension"** — corrected to a full brain port. Falsifier: another server-only input a bug needs that resists syncing |
| ★3 | Sync/determinism | 74 | Plausible | Closed-deterministic model is sound IF fully ported; the **food-field determinism is unproven** and the port is large. Falsifier: the food field or a governor value can't be made fixed-point-deterministic — the spike (§5.1) tests exactly this FIRST |
| 4 | Design quality | 78 | Plausible→Strong | Unifies the decision layer; reuses steering/ledger/authority; staged + spike-gated; combat correctly only half-unifies. Falsifier: the split-brain nest/Director consistency story doesn't hold |
| ★5 | Feasibility/CPU | 78 | Strong | Re-analysed concretely: the sim is a SMALL delta over the render+per-bug-movement already running (~24k ops/tick with grid+pooling ≈ <0.1% of a low-end CPU; §3.3). The critic's flags (threat-scan/raycast/GC) are solvable code-structure issues, not an algorithmic wall. Falsifier: the profile surprises us → the hybrid is the fallback |
| 6 | Blast radius | 64 | Plausible | Touches the whole ecology brain + food + persistence + the governor; contained by staging + the checkpoint + keeping the swarm path until S3. Falsifier: retiring the swarm decisions destabilises the tuned populations |
| ★7 | Determinism-port effort/risk | 70 | Plausible | The REAL work: port satiation/forage/breed/hunt/director/nests/broods float+RNG → fixed-point+counter-RNG + build the novel food field. Mechanical + gated, but large surface. Falsifier: the food field can't be made 2-client-identical — the §5.1 spike tests this FIRST |
| — | **Design confidence (weakest: Blast 64 / Determinism-port 70)** | **~72** | | CPU is no longer the concern; the food-field determinism spike (§5.1) is the gate that turns the port from Plausible to Strong |

**Verification: PENDING.** The honest read: this is **directionally right and hard**, gated on a cheap 1-2 day
spike that resolves the two empirical cracks (food-field determinism + CPU). Analysis has plateaued at ~68; the
spike is what moves it — up (commit to the full staged build) or sideways (the hybrid fallback).

## 8. Open forks for the owner
- **Fork 1 — unwatched zones:** freeze-in-save (matches today, simplest) vs a cheap server aggregate drift layer.
- **Fork 2 — persistence granularity:** per-bug digest (exact) vs re-derive from seed+population (cheaper).
- **Fork 3 — scope of "individual" (also the CPU fallback):** ALL species individual (flies too) vs a **hybrid** —
  combat/predators + anything you're watching go individual; dense ambient swarms (100 flies) stay aggregate. The
  hybrid is the natural landing spot if the CPU spike is tight.
