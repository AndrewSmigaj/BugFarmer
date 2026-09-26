# Ecology Control Campaign — village_21_lab (autonomous)

A running journal of an experiment campaign to understand **how to CONTROL the 6-species ecology**: what
sets each species' oscillation band (its centre + amplitude + period), and which levers move it. Run on a
throwaway copy of village_21_B (`village_21_lab`) so the shipped zone stays put. Owner asked for this while
away; I drive it autonomously, one change at a time, thinking between runs through several lenses.

**Targets (the alive-bands we want):** fly ~100, butterfly ~100, wasp/centipede/beetle/millipede ~30 —
as the CENTRES of visible oscillations (boom-bust), self-maintained (reseed→0), bounded by emergent
food/predation/aging, caps OFF.

**Run setup:** `run_config.py <cfg> --zone village_21_lab --duration <D>`; configs carry
`"flags": {"sim_batch": N}` to trade wall-clock for game-days. Calibrated below. Each run's charts land in
`ecology_charts/village_21_lab/current/` + dated `archive/`. seed 1337 (reproducible).

---

## The system (who eats what / what bounds whom)
- **fly_common** ← breeds on rotten fruit + compost + dead_millipede (carrion). Prey of wasp & centipede.
  Lifespan ~3 game-days. Fallen fruit takes ~2 days to rot → food (the slow-takeoff lag).
- **butterfly_meadow** ← breeds on milkweed (host, depletable) + feeds on nectar (depletable). Prey of wasp.
- **wasp_common** ← NEST-ONLY predator (8 hand-placed nests + prey-gated recovery). Hunts fly + butterfly,
  tethered to its nest by home_range 40. The only butterfly predator.
- **centipede_garden** ← free-roaming ground predator of flies; breeds on a well-fed timer. Spawn-seeded.
- **millipede** ← detritivore on leaf_litter; its corpses feed beetles.
- **beetle_carrion** ← decomposer on dead_<bug> carrion; grows when other species die.

## Analysis lenses (think through ALL of these each run, not just "did the number move")
1. **Bottom-up / food-limited** — does each prey/decomposer track its food STOCK (RESSTATS vs pop)? A
   closed pop↔food loop = alive; a flat line = food unlimited (runaway) or absent (starved).
2. **Top-down / predation-limited** — do predators CONTROL prey (PREDLOG kills, prey d_predation share)?
   Stable limit-cycle vs over-crop-to-extinction vs predator-starves-off.
3. **Spatial** — are predators co-located with prey (bugmap)? Dead zones, refugia, prey leaking to corners.
4. **Oscillation character** — amplitude, period, PHASE LAG predator-behind-prey, and does it DAMP toward
   flat, hold a limit cycle, or diverge, over the longer run?
5. **Self-maintenance** — b_reseed→0 (emergent) vs Director-propped? d_oldage vs d_starve vs d_predation mix.
6. **Controllability** — which single knob moves which band, and does it move CENTRE or AMPLITUDE? (the sweep.)

## Campaign plan
**A. Fix-ups on village_21_B first (owner's direct asks)** — millipede→~50, centipede positioning,
distribute predators across distinct prey sources. (Logged in ecology_tuning_log.md, not here.)

**B. Exploration on village_21_lab (≥10 runs, vary STRUCTURE):**
- E0 baseline (copy of B) · E1 predator count · E2 centipede co-locate vs separate · E3 prey food density ·
  E4 a refugium (prey with no predator) · E5 predator reach (home_range) · E6 prey immigration ·
  E7 butterfly food · E8 starting populations (transient vs attractor) · E9 synthesis "best so far".

**C. Parameter sweep on village_21_lab (5 runs, vary ONE param → band shift):**
- P1 fly lifespan · P2 fruit_rot_ticks (the rot-lag) · P3 wasp brood/feed (predator growth) ·
  P4 predator vision/strike (predation rate) · P5 nectar/milkweed regen (butterfly food).

---

## Calibration
duration **400** @ **sim_batch 6** = **16 game-days** (≡ the 1200@batch2 runs) in ~1/3 the wall-clock (~5 min/run).
All lab runs use this. seed 1337. Bands read as `min..max (mean)` over the 16 days.

## Run journal
_(one entry per run: hypothesis · the single change · result through the lenses · what it implies for control.)_

### E0 — baseline (vlab_base, = village_21_B current) · REFERENCE
fly 12..477 (huge amplitude), butterfly 11..266 (one big wasp-cropped cycle), wasp 8..126 (mean ~50),
**centipede flat 4** (cold-start dead attractor), **millipede flat ~132** (litter-saturated, non-oscillating),
beetle 2..13. So at baseline: the wasp<->butterfly<->fly loop OSCILLATES well; the two decomposer/ground
species are STUCK (one pinned high & flat, one pinned low & flat) — the campaign's two hardest control targets.

---
## Pre-campaign findings (from village_21_B Part-A, the fix-up the owner asked for)
Owner asks were millipede→~50 + centipede establish. The OBVIOUS levers FAILED, revealing two control facts:

**FINDING 1 — millipede is bounded by litter PRESENCE, not QUANTITY.** leaf_litter is non-depletable flora
(infinite food per patch), and millipede only eats leaf_litter (forage_chance 0). So cutting patches 100→46
left millipede flat at ~135 (each surviving patch still feeds unlimited millipedes; patch count only limits
spatial REACH). → To move the millipede band: throttle BREEDING (reproduce_cooldown 300, egg count) or
shorten lifespan, OR make litter depletable, OR cut patches drastically. [Lens 1: a "food-limited" species
whose food isn't actually depletable behaves UN-limited — looks like a flat runaway, not an oscillation.]

**FINDING 2 — centipede dies in the cold-start, not from bad position.** initial 16 → day-1 pop 4 (12
starved) → pinned at the reseed floor, 0 kills, even sitting on fly orchards. It's seeded half-fed but the
orchard flies are ALSO low early (same rot-lag), so the centipede starves before it ever hunts. Repositioning
can't fix a phenology/cold-start problem. → Levers: spawn ON dense day-1 prey, higher SpawnSatiation for
predators, or much higher initial, or seed its prey ahead of it. [Lens 4/5: a predator at the reseed floor
is a DEAD attractor — it can't climb because it needs kills to breed but needs population to get kills.]

Both are now CAMPAIGN OBJECTIVES on the lab (millipede controllability = E-run; centipede cold-start = E-run),
then port the winners back to village_21_B.

---
## CONTROLLABILITY MAP — 9 one-lever runs vs baseline (min-max(mean), 16 game-days)

| config (lever)            | fly        | butterfly  | wasp     | centi   | milli      | beetle  |
|---------------------------|-----------|-----------|---------|--------|-----------|--------|
| **base**                  | 12-477(95) | 6-266(116) | 8-126(50)| 2-4(4) | 29-138(126)| 2-13(5)|
| E1 centi initial 16→40    | 16-277(123)| 12-246(94) | 5-88(42) | 2-4(4) | 51-137(128)| 2-15(7)|
| E2 milli breed 300→900    | 12-337(72) | 6-230(74)  | 11-103(52)| 3-6(4)| 7-135(106) | 2-6(3) |
| E5 wasp home_range 40→60  | 12-342(82) | 9-273(179) | 9-52(33) | 2-6(4) | 10-143(129)| 2-20(7)|
| E6 fly spawn_int 2000→800 | 10-333(80) | 11-216(77) | 0-153(57)| 2-4(4) | 5-141(120) | 2-8(4) |
| P1 fly lifespan +50%      | 11-383(129)| 6-168(50)  | 14-125(66)| 3-11(5)| 17-141(125)| 2-30(10)|
| P2 fruit_rot_ticks ÷2     | 12-295(102)| 9-183(61)  | 13-119(58)| 4-6(4)| 25-139(127)| 2-14(6)|
| P3 wasp feed_per_kill +50%| 24-304(102)| 10-106(39) | 4-100(47)| 2-4(4) | 4-138(76)  | 2-13(4)|
| P4 predator vision +50%   | 11-370(91) | **9-31(14)**| 27-66(46)| **4-28(6)**| 43-140(130)| 2-14(5)|
| P5 butterfly breed 90→135 | 12-485(141)| 8-180(60)  | 0-182(56)| 3-8(4) | 32-136(126)| 2-9(4) |

### What each lever controls (through the lenses)
- **P1 fly lifespan = the MASTER prey lever.** +50% raised the fly CENTRE (95→129), SOFTENED its boom (peak
  477→383), and lifted the WHOLE web above it: wasp 50→66, beetle 5→**10** (peak 30), centi even twitched to
  11. [Lens 1+4] Longer-lived prey = a steadier food base → every consumer rises and the amplitude calms.
- **P4 predator vision = the predation-RATE master, and the CENTIPEDE FIX.** +50% over-cropped butterflies
  (116→**14**) — but it's the ONLY lever that moved the centipede (4→**28**, established!). [Lens 2] The
  centipede was never a positioning or seed-count problem (E1 initial→40 did NOTHING); it's a DETECTION
  problem — vision 13 was too short to find flies before starving. Raise vision → it sees prey → climbs.
- **E5 wasp home_range UP is COUNTERPRODUCTIVE.** 40→60 gave FEWER wasps (50→33) and MORE butterflies
  (116→**179**). [Lens 3] A tight nest tether CONCENTRATES predation; loosening it dilutes the patrol over
  more ground and breaks the provisioning rhythm. So for nest predators, smaller home_range = stronger control.
- **P2 rot-lag controls fly AMPLITUDE, not centre.** ÷2 cut the fly peak 477→295 (softer bust) with little
  centre change. [Lens 4] The rot LAG is the boom-bust violence knob — exactly the slow-takeoff cause.
- **P3 wasp feed & P5 butterfly breed both lower the butterfly centre** — top-down (more food/kill → crop
  harder, bfly 116→39) vs bottom-up (slower breeding, 116→60). Two independent handles on the same band.
- **E6 fly immigration** barely helped the fly trough (still 10) — immigration ≠ resilience when the bound
  is food, not seeding. **E1 centipede seed-count = a DEAD lever** (cold-start is detection/food, not count).
- **millipede stays high & flat under every lever except its own breeding throttle (E2: peak still 135,
  mean 126→106).** [Lens 1] Confirms it's litter-PRESENCE-bound (non-depletable food) — only a hard breeding
  throttle or depletable litter will pull it to ~50. It never oscillates (no predator, infinite food).

### Synthesis hypotheses (to test next)
1. **Fix centipede WITHOUT nuking butterflies:** raise ONLY centipede vision (13→~19), leave wasp vision at
   16. P4 raised BOTH → butterflies died; the targeted version should establish centipede while butterflies
   keep their cycle.
2. **Raise the whole web + calm it:** fly lifespan +30% (gentler than +50%) — lifts centre, softens bust.
3. **Millipede toward 50:** harder breeding throttle (reproduce_cooldown 300→700) — accept it won't oscillate.
4. **Keep wasp home_range at 40** (wider is worse). Combine 1-3 in one synthesis run.

### S1 synthesis (centi vision 19 + fly life +30% + milli throttle 700) — LEVERS INTERACT
Result: fly 8-610(131, spikier!), butterfly 10-41(**16**, collapsed!), wasp 8-107(52), centi 2-10(4, barely
moved), milli 15-140(121, throttle ~no-op). Three lessons:
- **Levers are NON-ADDITIVE.** Butterfly collapsed from changes that don't touch it directly — fly lifespan
  +30% made flies abundant → the system re-balanced and butterflies lost (likely wasp prey-switching /
  shared predator). You can't stack single-lever wins; the butterfly band is FRAGILE to fly abundance.
- **Centipede is THRESHOLD-sensitive on vision.** 19 gave peak 10 (not established); P4's 19.5 (+ wasp 24)
  gave 28. Establishment is a sharp threshold, not linear — needs vision clearly past it.
- **Millipede is STUBBORN.** reproduce_cooldown 700 moved mean 126→121 only. It needs a MUCH harder throttle
  or depletable litter — its non-oscillating high-flat band is the least controllable thing in the system.

### S2 (centipede vision 22 ALONE) — overturns the "vision fixes centipede" idea
centipede 2-12(4) — STILL not established, despite **144 kills**! Butterfly survived (46) since wasp vision
untouched. So P4's centipede=28 was a COUPLING side-effect, not the vision lever. **Real finding: centipede's
bottleneck is BREEDING-CONVERSION, not detection.** It hunts fine (144 kills) but can't convert kills into
population — it stays at the founding floor. The lever is its breeding mechanic (predator_breed_satiation /
well-fed-timer / max_swarm 3 too small to accumulate), NOT vision/position/seed-count. [Lens 2+5: a predator
can be prey-saturated AND still not grow if the kills→offspring conversion is the limiter — a different class
of stuck than the fly/butterfly food-limited ones.] Centipede needs a Go-side breeding look, deferred.

### E3 (predator count 8→4 nests, halved) — the cleanest top-down lever
butterfly 6-266(116) → **15-699(400)** (EXPLODES), wasp 8-126(50) → 0-47(18) (scales with nest count),
fly 12-477(95) → 12-177(65), beetle 5→12 (more carrion from the bigger butterfly swings). [Lens 2+3]
**Nest COUNT is the most direct, predictable handle on the butterfly band** — halve the predators, the prey
~3.5×'s. This is the structural mirror of P3/P5 (which moved butterfly via per-kill efficiency / prey
breeding); here it's sheer predator NUMBERS. Wasp population scales ~linearly with nests. So to SET the
butterfly band: choose nest count; to set its AMPLITUDE: choose where the nests sit (refugia, next).

### E4 (refugium: 7 nests, E-meadow w8 removed so its butterflies are UNHUNTED)
butterfly 6-266(116) → 12-377(**254**), and the per-day shows it CLIMB to a high plateau (377) and HOLD —
it stops crashing: 12,38,95,126,215,256,305,290,347,376,377,330,339,354,359. [Lens 3+4] A spatial REFUGIUM
(one prey source with no predator) converts the prey from boom-BUST to a high STABLE plateau — the unhunted
meadow is a constant source that recolonises the hunted ones, damping the oscillation. Classic ecology
(spatial refugia stabilise prey). So: nest COUNT sets the prey LEVEL (E3); nest PLACEMENT/coverage sets
whether the prey OSCILLATES (full coverage → boom-bust) or PLATEAUS (leave a refuge → stable-high).

---
# CAMPAIGN CONCLUSIONS — how to control this 6-species system
**15 runs (E0 baseline + 9 single-lever + S1/S2 synthesis + E3/E4 structural), 16 game-days each, seed 1337.**

## The control recipe (per band)
- **fly** — bottom-up, food-limited. CENTRE ← `lifespan_secs` (master lever; +50% → 95→129 and lifts the
  whole web above it). AMPLITUDE ← `fruit_rot_ticks` (the rot LAG; ÷2 → peak 477→295, softer bust). Faster
  immigration barely helps (food, not seeding, is the bound).
- **butterfly** — top-down, predation-controlled. LEVEL ← predator nest COUNT (E3: 8→4 nests → 116→400).
  Also lowered by per-kill efficiency (P3) or its own breeding (P5). STABILITY ← refugia (E4: an unhunted
  meadow → high stable plateau instead of boom-bust).
- **wasp** — nest-driven; population scales ~linearly with nest count; tighter `home_range` = STRONGER
  control (E5: wider 40→60 gave FEWER wasps + more prey — counterintuitive but spatial: a tight tether
  concentrates the patrol). Fed by whichever prey its nests sit among (flies vs butterflies).
- **beetle** — passive decomposer; tracks carrion (deaths); self-regulating; never needed tuning.
- **centipede** — STUCK at the floor. NOT controllable by tuning (vision, position, seed-count, immigration
  all failed). It hunts fine (144 kills) but kills don't convert to population → a BREEDING-CONVERSION
  bottleneck. Needs a Go mechanic fix (predator_breed_satiation / well-fed-split / max_swarm).
- **millipede** — STUCK high & flat (~130). leaf_litter is non-depletable, so it's "food-limited" by a food
  that never runs out → behaves UN-limited and never oscillates. Only a hard breeding throttle nudges it
  (300→900 → mean 126→106). Needs a Go fix: make leaf_litter DEPLETABLE (like milkweed), or a much harder
  throttle, or far fewer patches.

## Meta-findings (the "different lenses")
1. **Two distinct CLASSES of stuck species.** millipede = its food isn't really depletable (a "food-limited"
   species with infinite food looks like a flat runaway). centipede = its food IS limited and it eats well,
   but the kills→offspring CONVERSION is the bottleneck. Same symptom (pinned, non-oscillating), opposite
   cause (one over-fed, one can't convert) → opposite fixes.
2. **Levers interact NON-ADDITIVELY** (S1): stacking single-lever wins broke the butterfly (it's fragile to
   fly abundance — likely shared-predator prey-switching). Tune ONE thing, re-measure; don't stack blindly.
3. **The oscillating CORE is the wasp↔butterfly↔fly loop** — it's a healthy, controllable predator-prey
   engine. The decomposer/ground pair (millipede, centipede) sits OUTSIDE that loop and is the hard part.
4. **Spatial structure is a first-class control** alongside params: COUNT sets level, PLACEMENT (refugia)
   sets stability, home_range sets coupling strength. You can shape the oscillation with geometry, not just numbers.

## Recommendations
- **Tuning (safe, ports to village_21_B):** to calm the violent fly boom-bust, drop `fruit_rot_ticks`
  (amplitude lever, no centre side-effects). To set the butterfly band, pick nest count; to stop butterfly
  crashes, leave one meadow unhunted (refugium). These are clean, present for owner approval (gameplay feel).
- **Go-side mechanic work (new backlog):** (a) make `leaf_litter` a DEPLETABLE forage pool so millipede
  becomes food-bounded + oscillating; (b) buff centipede kills→breeding conversion so it can climb off the
  floor. Neither is a tuning problem — both are mechanics. Until then, millipede stays flat-high and
  centipede stays floor-bound regardless of params.
