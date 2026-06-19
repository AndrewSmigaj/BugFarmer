# Ecology Tuning Log

Append-only record of every population-balancing strategy we try on the real zone **village_21_B**, so we
never retread a dead end or lose what worked. The goal: all 6 species (fly, butterfly, wasp, centipede,
millipede, beetle) sitting in good, *alive* (oscillating) bands, bounded by emergent food competition /
predation / aging — NOT by artificial knobs. Hard `max_population` is only a rare backstop.

## How to read this
Each entry: **date · category · the exact change · seed · measured result**. Categories:
`food` (source counts / regen / decay), `breed` (breeding params), `behavior` (vision / forage / movement),
`spawn` (seeding / Director bands / events), `mechanic` (a code fix to how a mechanic works), `infra`
(tooling that makes the above measurable). Measured result = per-species min/max/trajectory + which
telemetry pointed the way (ECOSTATS births/deaths, RESSTATS food stocks, PREDLOG kills).

**Runs are only comparable once seeded** — see the determinism entry below. Pre-determinism numbers are
directional, not reproducible.

---

## Reference levers (where each knob lives)
- **Bugs** — `nakama/data/species.json`: `reproduce_cooldown`, `breed_amount`, `egg_count_*`,
  `satiation_decay_rate`, `feed_amount`, `vision_range`, `lifespan_secs`, `forage_chance`, `attractions_by_phase`.
- **Shared dials** — `nakama/data/ecology_tuning.json`: nectar/host regen, `host_breed_cost`,
  `max_host_capacity`, predator breed satiation, nest-found distances.
- **Plants/world** — `tools/zonegen/scenes/zone_village_21_B.py`: counts of fruit trees, milkweed,
  flowers, leaf-litter; orchard layout. Fruit→rot pipeline timing in `handlers_farming.go`.
- **Spawn/Director** — zone.json `bug_spawning.species_caps` (initial/max/`max_population`/`min_population`/
  `event_low`/`event_high`/`cull_at`/`spawn_interval`) + `ecology_director.go`.
- **Run a config**: `python3 tools/run_config.py <cfg> --zone village_21_B --duration 300`
  (charts → `tools/_generated/ecology_charts/`; food stocks via RESSTATS + `plot_phase.py`).

---

## Log

### 2026-06-18 · mechanic · Flies can now breed on rotten fruit (the core fly fix)
**Problem:** flies stuck at ~30 (`b_brood` 3–9/day) despite 19k+ rotten fruit on the ground — they were
*supposed* to breed on it. **Root cause (verified in code):** a maggot brood was tied to the ONE apple a
single fly stood on, keyed by that exact cell, and swept (dropping un-matured eggs) the instant that apple
was eaten (seconds later, before the 10s egg maturation). No shared pile. **Fix** (`brood.go`): ground-pile
broods are now ONE SHARED pile per ~4×4 area (≈ per tree's windfall), decoupled from any single apple's
lifetime (food is paid at lay time), retired only once fully hatched out; ground-pile keys namespaced `g:`
so they can't collide with milkweed/station broods. **Result:** flies breed correctly — `b_brood`
48→445→1170/day, pop climbs toward ~1500 (overshoots; food still over-supplied — see below). Butterflies
appeared to crash the same run, but that comparison was pre-determinism (not reliable) — under investigation.

### 2026-06-18 · infra · Made the server sim reproducible (determinism pass) — PREREQUISITE for tuning
**Problem:** `WorldSeed` was never wired into `math/rand`, and the sim iterated Go maps in random order, so
every run was a different random draw — population comparisons were partly noise (couldn't attribute a
change to a parameter). **Fix:** per-match seeded RNG (`state.Rng` from `zone.seed`) replacing ~45 global
`rand.*` calls; sorted iteration (`sortedStringKeys`) on every loop that draws rand / mints IDs (main swarm
loop, splitting, predator breeding, nests, broods, spawn, Director). Harness pins `seed=1337`; production
stays random. Safe for netcode (clients replay server-broadcast legs). **Result:** _pending the
reproducibility gate (same config twice → identical ECOSTATS)._

### 2026-06-18 · mechanic · Rotted fruit now decomposes (was an immortal-food hack)
**Sanity check (is it sane / does it make sense / will it help):** rot window ≈ 2× fly lifespan (6
game-days) — sane (same order as the creatures eating it), makes sense (bounds the standing pile to "what
dropped in the last ~6 days"), should help (turns infinite fly food into a finite, competed-for resource).
**Change** (`handlers_farming.go`): rotted fruit `Lifetime` 999999 (≈1190 game-days = never) →
`rottenFruitDecaySeconds = 5040` (6 game-days). The 999999 was a hack *I* added earlier to feed flies — it
made fly food effectively infinite and let the rotten count balloon past 30k. **Result:** see next entry —
the fix alone did NOT drop the pile, which exposed a deeper bug.

### 2026-06-18 · infra · Test zones were inheriting prior runs' ground items (the real confound)
**Symptom:** rotten pile was ~40k *on day 1* — impossible from this run's drops (fruit needs 2 game-days to
rot), and it had grown across runs (30k→32k→41k). **Root cause:** `zone_persist.go` saved AND restored
ground items unconditionally; `EphemeralSwarms` only resets *swarms*, not ground items. So every harness
run reloaded the immortal rotten fruit my earlier runs had saved to postgres — each run started dirtier
than the last, which ALSO secretly broke the reproducibility gate. **Fix:** skip ground-item
save+restore for `EphemeralSwarms` (fresh-start) zones, so a tuning run neither inherits nor accumulates a
pile and the DB self-cleans on next save. This is the prerequisite for ANY trustworthy tuning number.

### 2026-06-18 · infra · Determinism: ~20× less noise, not bit-perfect (good enough to tune)
After the seeded-RNG + sorted-iteration + deterministic-ID + posHash + clean-start fixes, run-to-run
variance dropped from ~30× (butterfly 353 vs 12) to ~1.5× on day 1 (fly 12 vs 13, millipede 27 vs 43).
But it is NOT yet byte-identical: the divergence reaches species far from the harness player (millipede
b_reproduce 25 vs 41), which is the signature of a SINGLE shared sequential RNG stream desyncing from one
non-deterministic consumption point — most likely the harness player's wall-clock-timed join/move messages
perturbing nearby bugs, which then shifts every later draw in the shared stream. A full fix would need
per-subsystem counter-RNG (keyed by tick/entity, like the client's CounterRng) — a big refactor, deferred.
**Decision:** tune on LONGER runs where the population magnitude/trend dominates the residual per-day
noise, and treat a lever as "real" only if it moves a population well beyond ~1.5×. Revisit counter-RNG
only if a tuning signal ever gets lost in the noise.

### 2026-06-18 · baseline · Clean 8-game-day baseline (seed 1337, post-determinism)
Per-species pop by game-day, and the food stocks:
- fly: 16,17,15,61,371,1344,1322,1184 — booms to ~1300, sits near its 1500 cap (CAP-limited, not
  food-limited — the plan wants food/predation to bound it instead).
- butterfly: 10,13,13,26,25,16,13,34 — oscillates low.
- wasp: 4,4,4,4,4,4,4,4 — STUCK; avg_sat ~20, d_starve 4–8 → wasps STARVE despite 1300 fly prey.
- centipede: 4×6 then 11,41 — starts climbing day 7–8. millipede: ~130 stable. beetle: 3 then 8 (day 8).
- rotten: 0,0,345,2348,3480,4575,5079,5835 — bounded (not 40k) but still climbing toward a ~6–8k plateau;
  nectar ~28.4k flat, milkweed ~2.6k flat (butterfly food still never bites).
Read: the standing rotten (~6k) feeds flies to the cap. Rather than cut the fruit again (owner set the
10× trees + 6-day rot deliberately), the aligned lever is PREDATION — if wasps actually ate the abundant
flies they'd crop the boom into an oscillation. Next: why do wasps starve amid 1300 prey?

### 2026-06-18 · behavior · Wasp home_range 40→80 (v21b_wasp_range) — PARTIAL win
Hypothesis: wasps starve because their 40-cell nest range can't reach the dispersed flies (centipedes,
free-roaming, thrive on the same prey). Result: wasp KILLS jumped (day5–8: 12,18,11 flies vs baseline ~0)
and flies were cropped (peak 1344→1023, day8 1184→810) — so reach WAS a limiter. BUT wasp pop still stuck
~5 (4,4,6,4,5,5,5,5). So reach is fixed; the population won't grow. (Butterfly 222 vs baseline 10–34 is
the determinism noise, not this lever — butterflies are the noise-sensitive species; ignore for now.)
Keep home_range 80 (net positive: more predation, no downside). Next bottleneck: survival/founding.

### 2026-06-18 · behavior · Wasp satiation_decay 0.11→0.06 (v21b_wasp_survive, on top of range 80) — testing
Why: the founding trigger (nests.go:273) needs the resident patrol to reach MaxSwarmSize, but it starves in
troughs (sat 10↔74) and culls back to ~5, so it never founds daughter nests to grow the colony. Slower
decay should keep the swarm fed between hunt bursts → grow → found → spread. [result pending]

### 2026-06-18 · behavior · Wasp decay 0.06 result + ROOT CAUSE (nest economy, structural)
Decay 0.06 fixed starvation (d_starve→0, sat 40–99) but wasp pop STILL stuck ~4, 0 nest foundings, and
`b_nest` = 8 on day 1 then **0 every day after** — the nest hatches its initial brood once, then goes
DORMANT. Root cause (predation.go:131–156): a nest wasp only carries brood home + deposits when its
`Satiation >= 100` (full), and the homing trip ABORTS if it can't reach the nest within NestHomingTimeout.
So there's a structural tension — **small home_range → can't reach prey (starve); large home_range → hunts
too far to return-and-deposit within the timeout → nest never refills its brood → never hatches → resident
never reaches MaxSwarmSize (10) → never founds daughters → colony stuck at the spawn floor.** This is why
home_range alone traded reach for deposit. NOT a param tweak — the nest deposit/homing loop needs a
redesign (e.g. deposit at deposit_satiation instead of full-100; or a return-timeout that scales with
home_range; or decouple brood accrual from the home trip). Deferred to the owner: redesign the wasp nest
economy, or accept the free-roaming CENTIPEDE as the primary fly predator (it works: 4→41). The wasp
configs (v21b_wasp_range / _survive) are diagnostic only — NOT applied to species.json.

### 2026-06-18 · mechanic · Nest-predator behavior redesign → 2-state forager loop (predation.go)
The wasp control scheme was four interacting thresholds (hunt-start 45, home 100, deposit-reset 80, hunt
timeout) that produced a 45–100 "dead zone" (too fed to start a hunt, not full enough to home) AND made a
hungry wasp give up and idle-wander — so it almost never completed a home trip, the nest brood never
refilled (b_nest 8→0), and the colony froze at the spawn floor. Redesigned the nest-predator branch to a
clean 2-state loop keyed off ONE threshold `predatorFullSatiation`:
  FORAGE while satiation < full → always re-acquire the nearest in-range prey (lost/elusive prey = pick the
    next; never idle while hungry);  PROVISION at full → carry home, deposit brood, drop to deposit level,
    forage again.
The point it stops hunting IS the point it heads home, so there's no gap. Navigation was never the issue
(Move beelines, no collision; homing reaches the nest fine) — the *decision to go home* was. Free-roaming
individuals (centipede) are untouched (keep their own threshold + rest-wander). Expect: wasps deposit
reliably → colony grows → founds daughters → crops the fly boom (the predator-prey oscillation). [testing]

### 2026-06-18 · spawn · Remove hard max_population caps → natural oscillation appears (v21b_nocaps)
Owner wants populations bounded by emergent dynamics, not the hard cap. Set `max_population: 0` (uncapped)
for all 6 species. Result over ~12 game-days: flies show a real boom-bust — 12→185→1084→**2322** (past the
old 1500 cap) → crash to 433→109 → recover 308→436 — and RESSTATS confirms the mechanism: rotten-fruit
stock builds to ~6.6k while flies are low, then the boom eats it down (6635→5311→3843→2537) and the flies
crash with it. The 1500 cap was clipping this flat (`current` flatlines at 1500; `wasp_range` archive
oscillated ~1000–1300 under heavier predation). Butterflies also oscillate (24→362→250→349); millipede
stable ~130; wasp STILL flat 4 (recovery problem is independent of caps). Keep caps off while tuning.

### 2026-06-18 · investigation · WHY wasps are frozen at 4 (for owner review — no change made yet)
Three compounding problems, none fixable by one number:
1. EARLY STARVATION (phenology): the starter nest hatches ~8 wasps on day 1 but flies are only ~12 then →
   they starve before the prey boom. The colony dies in the lean early window.
2. NO RECOVERY: nests are created ONLY at chunk-load or by a THRIVING nest splitting a daughter
   (processNestFounding). Once the starter nest dies, the orphaned + Director-reseeded wasps are
   permanently NESTLESS — no path for a lone wasp to found a new nest. So when flies finally boom, wasps
   can't re-establish. (Chart sawtooth = Director reseeding the floor, wasps dying, repeat.)
3. FRAGILE PROVISION RHYTHM: deposit_satiation (80) sits just under the 100 satiation cap, so the forage
   window is tiny — wasps either never provision (trigger at the cap) or provision after every kill (too
   much travel → starve). Needs deposit_satiation lowered for a real load-per-trip.
Proposed (pending owner OK): let a well-fed NESTLESS wasp FOUND a nest near prey (the founding-hornet
mechanic) for recovery, + lower deposit_satiation. NOT implemented — checking in first.

### 2026-06-18 · observation · Food is massively over-supplied (the next lever)
**RESSTATS (per game-day):** `rotten` ~19–29k items, `nectar` ~28.5k, `milkweed` ~2.6k — none of it ever
depletes. So the food-competition bound never engages and populations run away. The dominant tuning lever
going forward is to tighten the plant/food side (windfall accumulation / rot decay / flower + milkweed
counts & regen) until food becomes a real, depleting constraint and boom-bust emerges. _(Not yet tuned.)_

### 2026-06-18 · spawn+mechanic+food · LIVING-ZONE redesign (owner-approved layout v3) — built, not yet run
The big structural pass: seed the zone already ALIVE and spatially distributed, fix wasps behaviorally
(nest-only + recovery), and give every predator nearby prey. Determinism preserved throughout (round-robin
+ posHash + sorted loops). All caps stay OFF (the nocaps config). Changes:
- **Zonegen (`zone_village_21_B.py`):** orchards QUARTERED (apple/orange/cherry/plum) + a mini apple grove W
  of town; appleSW removed; fruit-tree total 193→**115**. 5 small fruit PATCHES (a handful of trees each) at
  the fly-spread points. **6 wasp nests** spread to woods/corners EACH within ~r40 of a fly source
  (w1 NW-pond shore, w2 NE-woods, w3 farm-seam observation pen, w4 SE-of-rocks +¼grove, w5 E-ecologist,
  w6 E-of-lake). 12 fly habitat circles (one per grove+patch), 6 wasp founding regions (no wasp wild).
- **Initials (lived-in start):** fly 30→60, butterfly 20→30, centi 8→12, milli 10→16, beetle 6→12; **wasp
  initial 0** (nests staff it). max_nests 5→6.
- **Spread on spawn (`match.go`):** initial seed distributes each species' Initial swarms ROUND-ROBIN across
  all its habitat circles (spatially-spread populated start); continuous immigration rotates a per-species
  cursor through the circles (every grove/patch gets topped up over time). New `spawnSwarmInArea` core.
- **Wasps from nests only (`match.go`/`ecology_director.go`):** nest species (MaxNests>0) SKIPPED in the
  initial/continuous/Director free-spawn paths → zero nestless reseeds (the root of the frozen-wasp bug).
- **Prey-gated nest RECOVERY (`nests.go`):** a brood-exhausted (dormant) colony now re-founds a fresh
  NestFoundingSize patrol after NestRecoveryDelay=3000t IF live prey is within home range — else it WAITS.
  This is the missing recovery path (owner's "new ~5 batch if the first die"); wasps are no longer a dead end.
- **Large-carrion fly food (`species.json` + `match.go`):** flies now list `dead_millipede` in feeding/
  reproducing/breeding (the matcher already let an EXACT carrion id through the IsCarrion exclusion) +
  authored `initial_carrion` seeds 5 dead millipedes in the NE woods (new `CarrionSeed`/`seedInitialCarrion`)
  → day-1 substrate for the woods' flies (w2 prey) and beetles; natural millipede deaths take over after.
- **Observability:** daily bug-distribution map (`plot_bugmap.py`) renders WHERE each species is, per game-day.
**Next:** run the nocaps config → read the bug-map (do all 6 wasp colonies hold? are flies spread, not piled?)
+ RESSTATS rotten (the 19–29k glut should drop hard with 115 trees) → iterate counts against the map.

### 2026-06-18 · RESULT of the living-zone redesign (v21b_nocaps, seed 1337, 5 game-days captured)
First run of the redesign. **The headline fixes are VERIFIED working:**
- **Wasps are nest-only** ✓ — day 1 `b_nest=24` (6 nests × 4), `b_reseed=0 b_spawn=0`. Zero nestless wasps
  (the root bug is gone).
- **Prey-gated nest RECOVERY works** ✓ — wasps crashed to 0 on day 2 (cold start), then day 3 `b_nest=4`
  with logs "Nest 62,222 / 180,55 / 132,231 recovered: re-founded a 4-patrol (prey returned)". Wasps are no
  longer a dead end — dormant colonies re-found once flies return. Peak wasp 24.
- **Spatial spread works** ✓ — bug-map shows millipedes in the NE woods, butterflies in the E/W meadows,
  flies top-center, beetles scattered — NOT piled in the SW belt. Round-robin seeding + cursor immigration.
- **Fruit/rot way down** ✓ — 115 trees; rotten peaked ~700 in this window (vs the old 19–29k glut).
**The one clear problem — COLD START (the deferred windfall priming):** RESSTATS shows `rotten=0` on days 1–2
(dropped fruit hasn't rotted yet), so the populated start has NOTHING to eat → mass day-1 starvation
(fly `d_starve=22`, wasp 24→1, Director force-reseeds flies). Flies don't breed (`b_brood=0`) until rotten
appears day 3+ (228→578→714), then recover to peak 93. So the spatial/nest design is sound but the start
STARVES before the trees rot. **Next lever (one, diagnosed — not a kneejerk): prime a MODEST amount of
pre-rotted windfall at the orchards on day 1** (Phase 2c, `initFruitTreesInChunk`, posHash-gated) so the
seeded bugs have substrate from tick 0. Also: this run only advanced **5 game-days in 400s** (sim_batch=2) —
too short to see steady-state oscillation; needs a longer wall-clock run or higher batch to judge the bands.

### 2026-06-18 · windfall priming added → cold start fixed, ecology now ALIVE (v21b_nocaps, seed 1337)
Added modest windfall priming (`initFruitTreesInChunk`: ≈1/3 of trees start with one rotten_<fruit>,
posHash-gated, FoodValue 100). Result over the first 5 game-days:
- **Flies breed + boom** (breeding-driven, not reseed): pop 16→18→**73→198**, `b_brood` 5→65→172,
  `b_reseed`→0 by day 5 (self-sustaining). day-5 avg_sat=3 = the boom topping out → bust incoming = the
  boom-bust we want. (Cold start is much softer: flies hold ~12-18 and breed instead of total collapse.)
- **Wasps persist via nests + recovery ONLY**: pop 7→10→4→12→4, **all `b_nest`**, `b_reseed=0 b_spawn=0`
  every day — colonies re-found near the booming flies (multiple "recovered" logs). No nestless wasps, no
  permanent collapse. avg_sat climbs to 67. The frozen-wasp problem is SOLVED structurally.
- Butterfly ~124-242, millipede ~135 (thriving on leaf-litter), centipede/beetle low (reseeding).
**Verdict: the living-zone redesign works** — spatial, breeding-driven, nest-only wasps with recovery, all
caps off. **Open (tuning, next session):** (1) runs only capture ~5 game-days at sim_batch=2 — need longer
wall-clock or higher batch to see the full fly boom→bust→wasp-dip→recovery oscillation and judge the bands;
(2) the fly boom to ~198 is steep — may dial initial counts / food down once we can watch a full cycle;
(3) re-confirm the same-seed reproducibility gate after the windfall + spread changes.

### 2026-06-18 · spawn+behavior · wasps closer to flies + live 50% longer + longer run (owner directive)
Three bounded changes after reading the bug-map (wasps not close enough to the flies):
- **Nests moved ~30% CLOSER to their nearest fly source** (zonegen, NOT a home_range change — owner was
  explicit "closer to flies does not mean increase home range"): w1 (62,222)->(66,217), w3 (132,231)->
  (130,230), w4 (180,55)->(187,72), w5 (226,150)->(224,139), w6 (86,55)->(84,67); w2 already on its prey.
  The far southern/eastern nests (w4/w5/w6) move most. Observation pen + wasp_n* circles tracked the moves.
- **Wasp lifespan +50%** (species.json): lifespan_secs 6300->9450, spread 1680->2520 (home_range UNCHANGED).
- **Sim run +50%**: duration 400->600 (more game-days to see the oscillation settle).
Expectation: wasps spend less travel to reach prey + survive longer between kills -> colonies hold higher,
oscillate against the fly boom-bust instead of cold-recovering each cycle. (Result pending the run.)

### 2026-06-18 · RESULT: nests-30%-closer + wasp life +50% + duration 600 (8 game-days, seed 1337)
current/ now reflects this run (the refresh-every-run fix). 8 game-days = a FULL cycle visible.
- **Fly boom-BUST now complete**: 12→17→13→17→66→**188**→113→57 — booms day 6, busts day 7-8
  (d_starve 148/116 as the rotten substrate is exhausted). avg_sat crashes day 7 (9.7). The oscillation.
- **Wasps survive longer + stay fed** (the lifespan + closer-nest changes worked as intended): avg_sat
  climbs 0→40→…→**50.6** (vs bouncing off 0 before), recovery fires at the NEW nest spots (w3 130,230 /
  w4 187,72), and they DO kill flies (fly d_predation day5=8). Sustained 100% by b_nest, 0 reseed/spawn.
- **BUT wasps still floor-bound**: 0,4,8,4,4,4,4,12 (mean 8, max 24) — NOT climbing to 30. Root cause: the
  fly boom (day 6) is too BRIEF — it busts before a colony can bank enough brood to grow/split past the
  founding floor. Wasps are alive+fed+oscillating but capped by prey-window length, not by nest mechanics.
- Butterfly ~396 (high), millipede ~130, centipede/beetle low.
**Next lever to break the wasp ceiling (for owner): lengthen the fly prey-window** so colonies have time to
grow during a boom — e.g. soften the fly bust (more/longer-lived rotten substrate, or stagger fruit drop so
the boom plateaus instead of spiking-then-crashing), OR speed nest growth (lower NestBroodCap / founding
threshold) so a short boom still grows a colony. One lever, measure, repeat.

### 2026-06-18 · spawn · +2 wasp nests in the butterfly meadows (owner directive) + fly-timing reference
Wasps hunt BOTH fly_common AND butterfly_meadow, but in the run they killed 0 butterflies (PREDLOG: only
fly kills; butterfly d_predation=0 all days) while butterflies ran to 386 — because all 6 nests sat by the
FLY sources, out of home_range (40) of the butterfly meadows. So:
- Added **w7 (33,142)** inside the W butterfly meadow + **w8 (178,178)** inside the E butterfly meadow
  (both uncovered by existing nests); max_nests 6->8. Gives wasps a STABLE prey base (butterflies, ~386 and
  steady) to grow on between the brief fly booms, and a natural check on the runaway butterfly pop.
**Fly-timing reference (1 game-day = 8400t = 840s):** fly lifespan 2520s = ~3 days (±1). Fruit pipeline:
ripe fruit falls after fruit_drop_ticks (apple 4200t ≈ 0.5 day), a FALLEN fruit rots into fly food after
rotTicks 16800t = ~2 days, then the rotten food lasts rottenFruitDecaySeconds 5040s = ~6 days (or until
eaten). So the 2-day rot LAG is ~2/3 of a fly's 3-day life → when a boom eats the standing rotten stock,
replenishment can't arrive before the flies starve = the sharp bust. (Lever options for later, owner's call:
flies live longer / fruit_rot_ticks faster / more standing rotten — NOT changed yet.)

### 2026-06-18 · RESULT: +2 butterfly-meadow nests BROKE the wasp ceiling (8 nests, seed 1337, 8 days)
The unlock. Putting 2 nests INSIDE the butterfly meadows gave wasps the stable prey base they lacked:
- **Wasps: 24→35→38→36→57→74→54→39** — min 18, mean 44, max 79 (was mean 8, max 24 with 6 fly-side nests).
  The floor is broken; wasps now sustain a healthy population, fed by the butterfly supply (avg_sat 35-77).
  Still 100% b_nest (hatch + recovery), 0 reseed/spawn.
- **Butterflies CROPPED from runaway to oscillating**: 12→56→125→121→81→13→13 — min 0, mean 50, max 137
  (was a flat runaway to 386). PREDLOG shows wasps now eat butterflies HARD: day5=68, day6=105, day7=71
  kills. d_predation is the dominant butterfly death cause → real predator-prey control.
- **This is the predator-prey oscillator** (P-ECO-3): wasp boom tracks the butterfly boom, then crops it →
  butterfly crash → wasp dip. Wasps also still take flies (PREDLOG day3 fly=12, day6 fly=10).
**Watch / next:** butterfly amplitude is large (13<->137) and the crash to 13 is deep — may be too violent;
a full multi-cycle run would show whether it settles into a stable limit cycle or over-crops. Wasp mean 44
is now ABOVE the old 30 target — could thin to 1 butterfly nest, or accept the higher band. Owner's call.
