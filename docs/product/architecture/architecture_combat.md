# Combat AI & challenge — design

**STATUS: M1 + M2 (wasp tiers) BUILT + gated; M3 = centipede tiers IN BUILD (2026-07-12).** The adopted
skeleton + the layers around it. As-built: [§ Milestone 1](#milestone-1--as-built) (foundation),
[§ Milestones 2–3](#milestones-23--as-built-enemy-tiers) (enemy tiers + nocturnal + aggro). *(M3 was briefly
built as caterpillars — a misread; stripped, now real centipede tiers.)*
Build plan: the session plan file (combat foundation + enemy roadmap). Evidence + alternatives:
[`../investigations/deep_research_2026-07/combat/`](../investigations/deep_research_2026-07/combat/)
(01 melee AI · 02 swarm AI · 03 challenge/effectiveness · 04 player combat & bosses). Runs inside the
deterministic swarm sim — see [`architecture_swarm_sync.md`](architecture_swarm_sync.md) §0.

## Owner decisions (2026-07-11)
- **Danger tone:** dangerous overall, but **starter zones stay cozy** (few dangerous things) → **`zone barriers`**
  backlogged (gate danger by zone).
- **Defensive verb: DODGE only** (no block/parry).
- **Threat zoning:** extra danger **at night** — nocturnal hunters that don't hunt by day; otherwise not zoned.
- **Bite-token pool = 2** (≤2 individual stings per swarm per attack-cooldown).
- **Bug→player damage is PER-INDIVIDUAL**, authority-decided (mirrors the predation strike); **swarm-of-1 dropped**.
  Crucial fact: **player HP is SIM-INERT** (`state.go:314`) — the strike is a server-authoritative event, NOT a
  client-hashed sim input, so it needs no ledger/hash/snapshot wiring (lower determinism risk than predation).
- **New enemy sprites: gpt-image-1.5 @ medium quality.**
- **Roadmap:** M1 foundation+arena → M2 wasp polish + medium/hard tiers → M3 medium/tough caterpillar → M4
  centipede regroup (grouped + staggered) → M5 docs + `combat-enemy` skill.

## The decided skeleton (owner-adopted 2026-07-11)
Three primitives, layered:

1. **Steering** — the low-level "how a bug moves." Simple vector math per bug: `seek` (toward target), `arrive`
   (slow into range, no overshoot), `pursue` (lead a moving player), `separation` (don't clump). Output = the
   *target* of the swarm's next movement leg. Cheap; deterministic in fixed-point with sorted-id neighbour sums.
2. **FSM brains** — each bug/swarm is in exactly one state: `Idle → Chase → Wind-up → Attack → Recover → Flee`,
   with data-driven transitions (see player → Chase; in range → Wind-up; hit → Flee). O(1), deterministic.
3. **Attack-token stage manager** — a central server-side bouncer per player: a small integer pool of **bite
   tokens** (**= 2**, owner) + a ring of surround **slots**. Only a token-holder may execute a damaging lunge;
   the other bugs still crowd/menace (scary) but can't all bite at once (fair). Slots assign nearest-free →
   emergent flanking with zero peer awareness. Difficulty = raise the token/slot budgets. Pure integer
   bookkeeping on the server; emits **no extra network bytes** — only its *outcomes* (a telegraph leg, a strike)
   travel.

These compose: the **stage manager** sits above per-bug **FSM brains** whose Attack/Chase states drive
**steering**, which sets the next `SWARM_SET_TARGET` leg.

## Adopted alongside the skeleton (owner-approved 2026-07-11)
*(These make the three actually work — without them "smarter enemies" is just "more unavoidable damage." The core
bundle is inseparable from the skeleton; the pacing + polish layers land in later milestones.)*

### Core bundle — ADOPTED (M1 foundation)
- **Three-phase attack timing** (anticipation → active → recovery, authored **integer ticks**). This is the
  *fairness contract*: a token-holder's bite has a visible **wind-up (≥ ~15 ticks)** you can react to, and a
  **recovery** window that's the player's free-hit. Without it the attack tokens are just unavoidable hits.
  Deterministic (tick counters), trivial to sync. **The tokens and the timing are one feature.**
- **Player dodge + i-frames** — the **load-bearing prerequisite**. Every enemy telegraph is meant to be
  answered by *something*; today the player has weapon swings but **no dodge/roll/block/parry** at all. A
  dodge/roll with front-loaded invulnerability (Gungeon-shape: ~0.5–0.7 s, i-frames on the first half) is the
  cheapest, most cozy-forgiving defensive verb and the one to add **first**. Netcode: client-predicts the move;
  the server owns an integer `invulnStart/EndTick` window it checks damage against. (Details: research doc 04.)
- **Threat table + aggro radius + leash** — target arbitration + the escape valve. Integer threat per
  (swarm, target); lures/torches/scarecrows are threat magnets that **peel** part of the swarm off the player;
  a **leash radius** guarantees retreat always works (a cozy game must let you walk away). Turns a blind
  pile-on into a placement puzzle the player out-plays.

### Pacing layer — recommend
- **Threat director** (L4D-style): a per-player intensity valve — rises with bites/nearby deaths, decays only
  when disengaged; Build-Up → Sustain(3–5 s) → Fade → **Relax(30–45 s)**. Varies **frequency, not damage**, so
  threat never curdles into fatigue — the key to staying *cozy* while adding danger. Reinforcements arrive from
  off-screen edges (directional pressure, not a teleport pile-on).

### Cheap steering polish — recommend
- **Sticky priority targeting + acquisition delay** — a bug keeps its target until it dies/leaves range/a
  higher-priority one appears. Fixes target *flicker* (both feel AND a determinism hazard on near-equal scores).
- **Boids separation** in the steering sum — the anti-clump force so a swarm reads as a spread cloud, not one dot.

### Deferred (phase 2, not now)
- **Utility AI for attack/target *selection*** (score considerations, argmax + momentum) — nice once a bug has
  several attacks to choose between; the FSM is enough for a first pass. Determinism-safe if argmax + stable
  tie-break (no weighted-random).
- **Enemy role/variety expansion** (spitter / broodmother / tank / latcher — function-over-stats) — this is a
  *content roadmap* (new species + new player counters), an owner scope call, not an AI-architecture primitive.

### Rejected (for now)
- **GOAP** — huge cost + biggest nondeterminism surface for tiny melee bugs. No.
- **Flow-field-tile pathfinding** (SupCom2-style) — overkill; our `SWARM_SET_TARGET` legs already give shared,
  instant, coordinated movement. Revisit only if we ever need thousands of independently-pathing bugs through
  complex obstacle mazes.

## Milestone 1 — as-built
Shipped 2026-07-11 (commits `combat M1.1`…`M1.4`). The foundation everything else reuses.

- **M1.1 — Arena + generalized debug spawner.** `nakama/data/zones/arena/` (from `tools/zonegen/scenes/zone_arena.py`
  — a 64×64 walled pen, `ephemeral_swarms`, generous caps so debug spawns don't hit the population gate, no
  auto-spawn). `WorldMenu.cs` "Arena" row. `DebugOverlay.cs` F8 is now a species **picker** (`<`/`>` cycle,
  `-`/`+` count, spawn-at-player) over `EntityDatabase.AllSpeciesIds()`. Server spawn path unchanged (ledgered).
- **M1.2 — Per-individual bug→player sting (the phantom fix).** Replaces the swarm-**centre** `checkBugAttacks`
  (which stung near the centroid — the reported phantom). The **authority** client runs `RunBugPlayerStrikes`
  (`SwarmManager.cs`, mirrors `RunPredationStrikes`): per-individual, in `stingRange` (1.5) + line-of-sight of a
  player cell, **≤2** claimed (the token pool), reported via **`BUG_PLAYER_STRIKE` (opcode 110)**. The server
  (`handleBugPlayerStrike`) re-gates authoritatively (authority-only, centre-range sanity, still-alive) and
  funnels through the existing `applyBugAttackToPlayer` (subdued / sting-immune / per-swarm cooldown / shared
  invuln). HP is **sim-inert** → no ledger/hash/snapshot wiring. `checkBugAttacks` is **retired from the loop**
  but kept (its unit tests exercise the shared funnel).
- **M1.3 — Player dodge + i-frames.** `PlayerController.cs`: **Space** dashes (13 bps / 0.22 s) in the move
  direction (or facing when still), client-predicted through `ResolveCollision`, and sends **`PLAYER_DODGE`
  (opcode 111)**. The server sets a **separate** `PlayerState.DodgeInvulnUntilTick` (5 ticks = 0.5 s; separate
  from `LastDamageTick` so it doesn't perturb regen), checked in `applyBugAttackToPlayer`. `PlayerHealth.cs`
  (sole sprite-color owner) blinks during the window.
- **M1.4 — Attack telegraph (two-beat).** `handleBugPlayerStrike` now **arms** a telegraphed sting instead of
  landing it: flash a `"windup"` telegraph now (reuses `broadcastBugTelegraph`; client already renders flash +
  hiss) and schedule the hit for `stingTelegraphTicks` later on `SwarmState.PendingStingPlayer/Tick` (server-only,
  sim-inert). `processPendingStings` (per tick) fires due stings, re-gating **range** (step-out counterplay) then
  the funnel (dodge/invuln). The pending-slot + per-swarm cooldown own the cadence, so the client re-reports on a
  light fixed throttle (`StingReportThrottleTicks` = 4).
  - **Deviation from design:** wind-up shipped at **12 ticks (1.2 s)**, not the doc's earlier "~15" — a readable-
    but-snappy default; it's a one-line tunable (`stingTelegraphTicks`) to dial in the arena playtest.
- **Verification.** Go unit tests `bug_player_strike_test.go` (applies / authority-only / centre-sanity /
  dodge-negates / step-out-whiffs / no-spam / dead-bug) + the full world suite green; the headless
  `sim-determinism` gate **PASS** (sting is sim-inert — the swarm sim core is untouched); plugin builds as a
  plugin. **PENDING (needs the rebuilt plugin deployed):** the 2-client `run_sync_latejoin.sh` regression run
  (co-located + disjoint) and the **owner arena playtest** (telegraph reads · dodge negates · no phantom · ≤2 bite
  · night enemies via the debug time control).

## Milestones 2–3 — as-built (enemy tiers)
Shipped 2026-07-11 (commits `Combat: nocturnal…`, `Combat M2+M3…`). Four new enemies on the M1 foundation, each
just DATA (`species.json` combat spec + `bugs.json` art + a carcass item) + a fresh gpt-image-1.5 sprite — no
per-enemy code. All are debug-spawnable in the arena immediately via the M1 species picker.

- **Nocturnal mechanic** (`BugSpecies.Nocturnal`): a genuinely night-active creature (a moth, a nocturnal beetle,
  etc.) lies low by day and is a full threat at night. Server-side + deterministic — `isNightForHunting`
  tracks the client's VISUAL night (deep night 0.58–0.88; active window `[0.55, 0.90)`, so the debug "Night"
  button t≈0.70 is night, "Evening"/"Noon"/"Morning" are day). Gates two things, both of which output only legs /
  server-authoritative HP (no new client-hashed sim input): the sting (`handleBugPlayerStrike` won't arm by day)
  and predator aggro (`predationThink` won't hunt/nest-defend by day). NOTE: don't flag a diurnal real species
  (wasps, hornets — seen by day) nocturnal; that reads as wrong.
- **M2 wasp tiers** (`category: swarm`, predation → inherit nest-defence + hunt + ambient sting):
  `wasp_soldier` (medium: dmg 2 / cd 1.6 / spd 2.6 / hp 5) and `hornet_giant` (hard, **diurnal** — real hornets
  are day-active: dmg 3 / cd 1.2 / spd 3.0 / hp 8).
- **M3 centipede tiers** (`category: individual` + predation → reuse the base centipede's **surge/lunge** attack;
  see § Milestone 3 below): `centipede_tiger` (medium) and `centipede_giant` (hard). *(An earlier build made these
  as caterpillars — a misread of the ask; caterpillars are butterfly/moth larvae, not combat enemies, and were
  stripped out 2026-07-12.)*
- **Player-aggro radius** (`aggroPlayerThink`, combat_aggro.go): any attack-capable swarm with `attack.aggro_enter > 0`
  chases the nearest player within that radius (capped by its vision), so it engages instead of wandering and hovers
  in range. Centipedes use it too — it closes them to `attack.lunge.trigger_range`, then the per-tick surge takes
  over. Defenders (`aggro_enter == 0`: bees/ants) don't proximity-chase. The chase speed is `attack.aggro_speed_mult`
  (see the dives section below). Server leg → deterministic.
- **Difficulty knobs** (no new code): `attack_damage` (per-hit) · `attack_cooldown` (frequency, floored by the 1 s
  shared invuln) · `base_speed` (+ `hunt_speed_mult`; for a centipede also scales lunge speed) · `vision_range` ·
  `max_hp` (hits-to-kill) · `min/max_swarm_size` · `nocturnal` · `sprite_family`/render scale (segmented crawlers).
  Add/tune an enemy → the **`combat-enemy` skill**.
- **Verified:** full Go world suite + `sim-determinism` PASS; sprites acceptance-checked at full res.
## Data-driven attack model (2026-07-12 refactor — the "maintainable for 50 bugs" pass)
Every player-facing combat behaviour is now a **per-species `attack{}` profile** in `species.json`
(`entities.AttackConfig`, mirroring `predation{}`) — no combat feel is hardcoded, so adding bug #51 is DATA:
- `style` (`contact` | `lunge`) · `damage` · `cooldown_secs` · `range` · **`telegraph_secs` (per-species
  telegraph)** · `is_sting` · `only_defending` · `aggro_enter`/`aggro_exit` · `lunge{trigger_range,
  surge_speed_mult, overshoot, surge_max_ticks, lead}`. `BugSpecies.AttackProfile()` is the one read point
  (backfills from the legacy top-level fields for un-migrated data).
- **ONE pipeline, cleanly split by file:** `bug_attack.go` = the bug→player attack subsystem (the
  authority-relayed strike/telegraph + the shared `bugAttackAllowed` gate every style passes through) ·
  `handlers_player.go` = pure player-HP (funnel/regen/dodge/faint) · `combat_aggro.go` = proximity pursuit ·
  `centipede.go` = the lunge *movement* choreography (its bite routes through `bug_attack.go`, params from
  `attack.lunge`). The old **two-detection-paths + split-aggro smell is resolved** — both the contact sting and
  the centipede lunge share the same gates + funnel (this closed a real bug: the surge skipped the nocturnal gate).
- **Phantom killed:** the authority client owns the two-beat (per-species `telegraph_secs`) + the precise
  per-individual range check against the LOCAL player's EXACT position; the server applies on `phase:"strike"`.
  No server-scheduled centre-fire.
- **Remaining follow-ups (small):** `checkBugAttacks` is retired but kept as a test-only funnel-driver (2 tests);
  the legacy top-level `attack_*` struct fields remain as normalize-input. Neither is on a production path.

## Individual attack AI: orbit-and-dive (2026-07-12 — "swoop in and attack")
Fixed two structural bugs the owner reported (*"wasps just bumble around … centipedes phantom-hit"*) and gave
enemies the **"solo divers within a bigger swarm, one or two at a time"** feel — as **real deterministic
per-bug movement**, not a cosmetic overlay. The root cause of the bumbling: wasps shipped `player_reaction:
"ignore"`, so each individual bug's AI wandered around the swarm centre and never engaged. Making the *centre*
chase faster + adding a cosmetic dart (the first pass) didn't fix it — the bugs themselves weren't attacking.
- **The real fix — individual attack MOVEMENT (`BugAgent.AttackMove`, hash-bearing, deterministic).** Wasps/
  hornets now ship `player_reaction: "attack"` + a `reaction_radius`. Each bug's AI (already had an "attack"
  branch, gated off) now runs an **orbit-and-dive**: most of a repeating cycle it HOVERS in a menacing cloud a
  `standoff` off the player (its natural darting hover, pulled toward the *player* instead of the swarm centre);
  during its own slice of the cycle it SWOOPS straight in at ~2× the hover dash (`DiveSpeedMult` — a committed
  dive, faster than the player's 5 c/s walk so it reads as an attack), then the cycle returns it to the hover
  (which peels it back out). The dive slice is **phase-offset per bug-id** (`(tick + bugId·13) % divePeriod <
  diveTicks`), so ~1–2 of the swarm dive at any instant — staggered, never a lockstep pile-on, and coordinated
  *without communication* (a shared deterministic formula). **Determinism:** a pure function of `(tick, bugId)` +
  the deterministic player CELL + fixed-point math, reusing the existing `MoveToward`/`UpdateMovement` primitives
  — so every client computes the identical `Agent.Position`, exactly like the flee/curious behaviours that
  already ship. No new snapshot state. Gated by `sim-determinism --attack-test` (a moving player drives it; two
  runs byte-identical, hash `FB80CE8997CF9EC3`).
- **Fast aggro (`attack.aggro_speed_mult`, server/deterministic).** Brings the whole cloud onto you so the
  individuals get within `reaction_radius` to engage: chase leg = `base_speed × aggro_speed_mult` (wasp `2.2 ×
  2.4 ≈ 5.3 > 5` walk; can't catch a *dodging* player at 13, by design). Same deterministic leg, faster speed.
- **Phantom killed — sting detected against the RENDERED sprite (client, authority-only, sim-inert).**
  `RunBugPlayerStrikes` (SwarmManager.cs) range-tests each bug's **rendered `Transform.position`** (via
  `GetAllBugsRenderedSorted`), not `Agent.Position`. For a 9 c/s centipede surge the sprite lags the sim ~1.4
  cells, so testing the sim pos fired the "hit" that far off-screen; the rendered read matches what you see. It
  feeds only server-bound strike REPORTS (HP is display-only) → never enters the hash. **The server-side
  centipede bite was DELETED** (centipede.go) — the last centre-fire phantom; the centipede connect is now
  client-detected (`style:"lunge"` → per-tick connect) like the wasp sting.
- **The sting layer is now thin.** The MOVEMENT does the swooping; `RunContactSting` only lands the telegraphed
  DAMAGE: it flashes an in-range diving bug (the dodge-able wind-up), then after `telegraph_secs` stings if a bug
  is STILL in rendered range (a dodge/step-out whiffs). `attack_tokens` = how many bugs flash/report at once; the
  server `cooldown_secs` is the real damage-rate gate. On connect the bug gets a small 0.35 hit-pop jab (the real
  swoop is the movement, so no big cosmetic dart). `lunge` bugs use their server surge as the dive.

### Combat knobs — dial any enemy's feel from `species.json` alone (no code)
| Knob | Where | Side | What it does |
|---|---|---|---|
| `player_reaction: "attack"` | top-level | client sim | turns ON the individual orbit-and-dive (vs `ignore`/`flee`/`curious`) |
| `reaction_radius` | top-level | client sim | how close a bug must be to the player to engage (per-bug alert range) |
| `attack.standoff` | attack{} | client sim | cells the hovering (non-diving) cloud keeps off the player |
| `attack.dive_period_secs` | attack{} | client sim | each bug's swoop cycle — shorter = dives more often (more divers at once) |
| `attack.dive_secs` | attack{} | client sim | how long a swoop lasts (must exceed `telegraph_secs` to land the sting) |
| `attack.aggro_enter`/`aggro_exit` | attack{} | server | the swarm-CENTRE proximity-chase radii (hysteresis). `0` = defender |
| `attack.aggro_speed_mult` | attack{} | server | centre chase speed = `base_speed × this` — brings the cloud onto you |
| `attack.range` | attack{} | both | hit/bite distance (the sting detection radius) |
| `attack.telegraph_secs` | attack{} | both | wind-up before the sting (the dodge window; the per-tier tell) |
| `attack.cooldown_secs` | attack{} | server | min seconds between hits from one swarm (the real damage-rate gate) |
| `attack.attack_tokens` | attack{} | client | max bugs that flash/sting at once (1–2) |
| `attack.dive_cooldown_secs` | attack{} | client | paces a swarm's sting reports |
| `attack.lunge{…}` | attack{} | server | the centipede surge choreography (`style:"lunge"` only) |
| `attack.damage · is_sting · only_defending · style` | attack{} | server | per-hit HP · bee-suit-negated? · defender-only? · `contact`\|`lunge` |
| `render_scale` | top-level | client | display size (e.g. `wasp_soldier: 0.5` — sprite read too big) |

The **client-sim** knobs (`player_reaction`, `reaction_radius`, `standoff`, `dive_*`) are HASH-BEARING — they
drive `Agent.Position`, so all clients must read the same published `species.json` + build (the same rule as
`movement_style`; `publish_entities.py` is the drift tripwire). The **client-detect** knobs (`attack_tokens`,
`dive_cooldown_secs`) only pace the authority's strike reports (sim-inert). Everything stays in ONE `attack{}`
block so a bug's whole combat feel is one place. `combat-enemy` skill authors it.

## Determinism & network model (why the "central arbiter" is cheap)
- The stage manager, FSMs, and steering are **server CPU**, run each tick as **integer/fixed-point** math with
  sorted iteration + `(tick, entityId)`-seeded randomness (never `rand()`). No floats in sim sums.
- They put bytes on the wire **only when a decision changes something** — a new **leg** (`SWARM_SET_TARGET`), a
  **telegraph**, a **strike** (`BUG_REMOVED`). Movement is sent as legs the client replays deterministically,
  **never per-bug-per-frame positions.** Verified against `match.go`: the only strictly-every-tick message is a
  tiny **frontier heartbeat** (OpCode 78); the swarm roster (OpCode 20) is one *(x,y,count,radius)* per swarm on
  change; influence events batch per tick. Traffic scales with **decision rate, not bug-count × framerate** —
  low single-digit KB/s even in a busy fight. (`Perf.AddRosterBytes`/`AddInfluenceBytes` already measure the
  real totals — a profiled combat run prints exact figures.)
- New sim-reads (aggro, telegraph windows, dodge i-frames) must ride the frontier-gated ledger per the
  `frontier-sync` recipe — authority decides, relays the observable via events; never a view-scoped read.

## Recommended build order
1. **Player dodge + i-frames** (the prerequisite — nothing else is fair without it).
2. **Three-phase attack timing** on one enemy in `feel_test` + the **attack-token pool** (1–2) → playtest the
   feel. This is the smallest slice that proves the whole loop.
3. **Threat table + aggro radius + leash** (escape + lures).
4. **FSM brains + steering (seek/arrive/pursue + separation + sticky targeting)** generalised across bugs.
5. **Threat director** pacing valve.
6. *(later)* Utility-AI attack selection; enemy-role/species expansion.

## Open questions (owner taste/scope — surfaced, not decided)
1. **How cozy vs. how threatening?** The token-pool size + telegraph length are the master dials. Stardew-mines-
   light, or genuinely dangerous at night / in caves?
2. **Defensive verb:** dodge-roll (recommended) as the one verb, or also **block / parry** later for tell-reading?
3. **Is threat zoned/opt-in?** Safe farm by day, danger in the wilds/caves/night — so players choose their
   challenge (Don't-Starve-style)? Or ambient everywhere?
4. **How far to expand the bestiary for combat** (spitter/broodmother/tank/latcher roles) vs. keep bugs mostly
   ambient? This sets how much of the "roles" content we build.
5. **Difficulty settings:** one global slider over these dials, or split (how-many-bugs vs. how-hard-they-hit)?
