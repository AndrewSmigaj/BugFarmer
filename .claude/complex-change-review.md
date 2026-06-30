# Complex-change review — steering a coding agent through hard changes in BugFarmer

A manager's prompt-loop playbook for managing Claude through hard DESIGN/IMPLEMENTATION tasks in THIS
large, intricate codebase — where the agent breaks things by **mis-modelling the system**, not by
hallucinating facts. Structure: lifecycle **STAGES × FAILURE MODES**, with BugFarmer's own invariants
baked in as checks.

Companions: `lenses.md` (the lens catalog — what to look at), the `certainty-assessment` skill (the SCORING
LAYER — turns this matrix's answers into an evidence-anchored, MIN-aggregated numeric table; "score CAUSE / FIX
/ TEST separately" is its job, generalized), and the `test-changes` skill (the EXECUTION GATES — the only
model-independent ground truth). Reusable for any complex BugFarmer change.

## The 7 ways a coding agent breaks THIS codebase (each = a real miss we hit)
- **FM1 INCOMPLETE COMPREHENSION** — acts on a partial mental model; didn't trace the real data flow /
  lifecycle / all call sites. (proposed `BlocksBugsCells` without seeing `state.Chunks` is lazy-loaded →
  empty on first join)
- **FM2 FORGOTTEN / MISSED CONCERN (completeness)** — fixed the first site, missed a second emit point, an
  edge path, or a cross-cutting invariant. (the "you forgot about X" failure)
- **FM3 ARCHITECTURAL MIS-FIT** — violates a system invariant / layering / data-scope / established
  pattern. (read view-scoped collision inside a zone-wide sim → the Phase 1b desync)
- **FM4 BLAST-RADIUS BLINDNESS** — didn't see what else the change touches (other consumers, contracts,
  replay).
- **FM5 VERIFICATION THEATER** — "tested" something that didn't exercise the change, the test TOOL is itself
  wrong, or the test's precondition silently didn't hold. (leg/bug-id parser collision; spawn-apart entry
  rejected)
- **FM6 STALE GROUNDING** — relied on a doc / memory / sub-agent summary that had drifted from the code.
  (the "96% broken" stale audit)
- **FM7 PREMATURE CONVERGENCE** — shipped the first design without weighing a simpler/better-fitting
  alternative.

## How to RUN it (the few rules that actually move quality; everything else is SWE)
- Prefer a **FRESH context / SEPARATE agent** for the review — an agent reviewing its OWN plan defends it
  (intrinsic self-review is the weak form; independent verification is markedly stronger).
- **EVIDENCE or it didn't happen**: every answer cites `file:line` or command output. Bare assertion =
  UNKNOWN, not PASS. Memory / docs / sub-agent summaries are not evidence — re-confirm against current code
  (it drifts).
- The **EXECUTION GATES** (sync harness + fixtures, `go test`, sim-determinism) are the only
  model-INDEPENDENT arbiter; the prompts raise the floor, the gates decide. "Compiled / ran once" ≠
  "property holds" — name the property and how it was shown.
- **Confidence % is overconfident + uncalibrated** — use it only to RANK where to dig, NEVER as the gate; a
  high % with thin evidence is a RED flag. Score CAUSE / FIX / TEST separately (independent).
- **SCALE to blast radius**: mechanical edit → a couple checks; architectural / determinism / contract /
  test-tool change → the full matrix + a fresh-context review pass.

## THE MATRIX — at each STAGE, fire the FAILURE-MODE prompts that are live there
Each cell is a prompt the agent answers WITH EVIDENCE. A weak or UNKNOWN load-bearing answer blocks that
stage's exit gate.

### STAGE 1 · UNDERSTAND  — exit gate: a correct, evidenced mental model of the affected subsystem
- **[FM1]** Trace the REAL data flow for what you'll touch: who writes it, who reads it, WHEN, and is it
  populated/valid at YOUR read point? Cite `file:line` per hop. (the lazy-load / init-order class)
- **[FM1]** Grep and PASTE every caller / consumer / emit-site of the thing you'll change. "Only one
  caller" is a claim to PROVE, not assume.
- **[FM2]** Which subsystem invariants must you not break, and where is each enforced? (use the BugFarmer
  checklist below — which apply here?)
- **[FM6]** Which load-bearing facts came from a doc / memory / sub-agent rather than code you read THIS
  pass? Re-verify each against current code.

### STAGE 2 · DESIGN  — exit gate: an approach proven to fit the architecture, chosen over an alternative
- **[FM3]** Which existing PATTERN does this mirror (cite it — the food-registry, the ledger-event flow)?
  If inventing, why is no pattern reusable?
- **[FM3]** For each applicable invariant, HOW does the design preserve it? (esp. DATA SCOPE — zone-wide
  sim vs view-scoped render; authority-only writes; frontier-gated vs on-receipt.)
- **[FM7]** What alternative did you reject and why? Is there a simpler design consistent with the codebase?
- **[FM4]** What does this ripple into — other consumers, the server↔client contract, persistence,
  late-join/replay?

### STAGE 3 · IMPLEMENT  — exit gate: complete + locally correct at EVERY site
- **[FM2]** Did you change ALL the sites Stage 1 enumerated, not just the first? (centralize shared logic vs
  N copies — the `broadcastWorldUpdate` single-emit lesson.)
- **[FM1]** Real shapes / units / scale at each edit (fixed-point not float; ×1000; cross-boundary
  type/enum match)?
- **[FM2]** Determinism at the edit: idempotent under replay/re-join? applied at `evt.tick`? deterministic
  iteration order (`sortedStringKeys`)?
- **[FM4]** What existing behavior NEAR each edit could shift as a side effect?

### STAGE 4 · VERIFY  — exit gate: a property proven by a model-independent gate on a clean setup
- **[FM5]** Does the test EXERCISE the change? Give the concrete input that FAILS if the change is reverted
  — is it in the test?
- **[FM5]** Does the test TOOL have its own correctness assumptions (parser / comparison / sampling /
  row-type)? Prove it can't false-pass/false-fail. (the leg-collision class)
- **[FM5]** Did the test PRECONDITIONS actually hold THIS run (fresh match, pinned seed, clients really
  disjoint, entity present)? Quote the evidence. (the rejected-entry class)
- **[FM5]** Which gate here is model-independent ground truth, and did it pass on a fresh/clean setup?
- **[FM2]** What did you NOT verify (residual) + which later gate catches it?

### STAGE 5 · LAND  — exit gate: coherent, reconciled, revertible
- **[FM6]** Which docs / invariants / comments does this change now make FALSE? Update them (BACKLOG, the
  architecture doc).
- **[FM4]** Is the commit self-coherent and revertible on its own?

## BugFarmer invariant checklist (the "baked-in" checks — name the enforcement point for each)
1. **SIM-INPUT RULE**: anything the bug sim READS = frontier-gated ledger event OR join/resync snapshot,
   NEVER a chunk-scoped on-receipt message (`WorldUpdate` 46 / `SwarmUpdate` metadata = cosmetic only). One
   sanctioned exception: join-time bootstrap hydration superseded by snapshot+events (`HydrateFood`).
   [`architecture_swarm_sync.md`]
2. **FIXED-POINT, not float**, in the sim; `FixedPoint operator* = a*b/1000` (the radius² scale landmine).
3. **DETERMINISTIC ITERATION**: any loop that draws `state.Rng` / mints ids / grabs a depletable resource
   iterates `sortedStringKeys` (Go) or explicitly ordered keys (C#) — never raw map order.
4. **AUTHORITY-ONLY writes**; followers REPLAY; detect-don't-remove (kills ride `BUG_REMOVED` on every
   client at the event tick, including the authority).
5. **DATA SCOPE**: zone-wide sim reads zone-COMPLETE data; rendering + player-collision stay view-scoped.
6. **SERVER CHUNKS LOAD LAZILY** — a zone-complete scan must read the full grid from disk, not
   `state.Chunks`. [`server-chunks-lazy-loaded` memory]
7. **SNAPSHOT/REPLAY COHERENCE**: entities created in the snapshot-lag window are minted by REPLAY at
   `evt.tick`, not prespawned from live metadata count. (the #127 class)
8. **CANONICAL ENTITY DATA** in `nakama/data/entities/*`; publish to the client; never hand-edit the client
   copy.
9. **EVEN-WIDTH occupant footprint-X shift**, applied in BOTH the game and `make_scene`.
10. **MESSAGE CONTRACT**: server `messages.go` opcodes/fields ↔ client `*Messages.cs` in sync; `JsonUtility`
    ignores unknown fields (additive is safe; renames/removals are not).
11. **TESTS ARE DURABLE ARTIFACTS**: fresh match (`docker compose up -d --force-recreate builder nakama`) +
    pinned seed before a definitive sync run; a build DEPLOY is not a restart.

## DYNAMIC PROMPTS — generation recipe (the matrix is static; THESE are generated per-change)
For the change at hand, enumerate and turn each into "assess certainty that <property>, with evidence +
falsifier":
- per **INVARIANT** the system holds → "…<invariant> is preserved under <specific scenario>."
- per **EXTERNAL INPUT** consumed → "…<input> is present / correct / identical-across-clients at <read
  point>."
- per **TEST GATE** → "…<gate> would FAIL if the fix were reverted (non-vacuous)."
- per **CROSS-BOUNDARY contract** → "…both sides agree on <field/units> after the change."
- per **STATE MUTATION** → "…it's idempotent under replay/re-join."

### Worked example (the determinism-hardening dogfood)
- #127: assess certainty a bug reproduced during B's replay window has IDENTICAL `(x,y,vx,vy)` on A and B
  at every common tick — trace its creation tick on BOTH; falsifier?
- #127: assess the fix doesn't regress the no-snapshot bootstrap path OR `SWARM_SPLIT` — which paths share
  `SpawnSwarmFromMetadata`/`SpawnInitialBugs`/`SpawnBugAt`?
- harness: assess the fixed diff parses ONLY bug rows — what guarantees a 14-col leg row can't be keyed as
  a bug? (fixture with a leg row whose `hasLeg` digit == a real bug id)
- harness: assess the hash-stream gate can't false-fail — are A & B bug SETS provably equal at common ticks?
- guide: assess the ledger-event glossary is COMPLETE — diff `messages.go` const block ↔ client
  `ProcessInfluenceEvent` switch ↔ server emit sites.

## The loop
1. Coding agent produces/updates a plan for the change.
2. A review pass (ideally fresh-context/separate agent) fires the MATRIX cells for the change's stage + the
   generated dynamic prompts.
3. Any BROKEN / unmitigated RISK / weak-evidence load-bearing answer → investigate, revise, re-fire (don't
   lean on the %).
4. Only an all-evidence-PASS (residuals explicitly gated to a later execution gate) advances to the next
   stage.
5. After code: re-fire STAGE-4 (VERIFY) cells before trusting ANY green result — the execution gates are
   the arbiter.
