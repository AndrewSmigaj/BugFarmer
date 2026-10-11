# How a zone nobody is in keeps time — options and a recommendation (2026-10-10)

_Status: PROPOSED, revised after three cold critiques (§9) — for the owner to choose between G and C (§7). The
engineering detail of the chosen option gets its own critique rounds before it is built. Research: the three documents
beside this one. Nothing is built._

## 1. The question
**Decided (2026-09-26, D57, `docs/product/economy/DECISIONS.md:732`):** one world clock; the world stops only when no
player is online; **empty zones stay frozen**, while random border events still bring a few bugs from a frozen zone
into a neighbouring zone that has players. GDD §01 ("How it will work") and the ROADMAP add that a frozen zone catches
up when someone first arrives — its bugs eat, breed and die over the missed time, worked out on the server — and P6 adds
its crops, fruit, showers and machines.

**The owner's concern (2026-10-10):** the whole world stops when nobody is online, so players don't return to a farm
wrecked while they were away. While anyone plays, a zone nobody is in shouldn't simulate every bug, but coming back to
find that a fly farm or new milkweed hasn't grown would be poor. He suggested estimating from recent population data,
perhaps swarm by swarm from each swarm's access to food, asked for alternatives, and noted that the server could also
simulate empty zones itself.

**What "good" means here** (each a thing players disliked in a shipped game, from the research):
1. a farm that was fed grows, and one that ran out of food goes hungry — no freeze (Palworld, Minetest Game), and no
   growth without food (Cataclysm DDA's catch-up breeds animals without checking food — confirmed in its
   `monster::try_reproduce`, which also damps each missed birth with a falling chance);
2. **every** timed thing catches up, not some (Vintage Story's querns and tree taps, Valheim's smelters);
3. being away is neither better nor worse than being there (X3/X4's out-of-sight fights);
4. wild numbers still rise, fall and crash (averaging erases crashes);
5. nothing appears in front of the player (S.T.A.L.K.E.R. 2), and no bug is lost or invented at the hand-over (Rain
   World);
6. the player can see what happened (The Sims 3's chaos came from unexplained changes);
7. arriving is quick, however long the absence.

## 2. Our system as built (checked in the code, 2026-10-10; corrected after three critiques)
- **An empty zone stops completely, but stays in memory:** `MatchLoop` returns before anything runs when the zone has
  no players or presences (`nakama/modules/world/match.go:905`); an empty match is kept, not ended (`match.go:879`;
  Nakama's `match.max_empty_sec` is unset). Its tick count freezes. Its autosave runs only while occupied
  (`match.go:913-917`). The plan estimates ~50 MB per visited 512 zone, and records that under Host & Play — the server
  on a player's own computer, which is how Single Player runs — a zone left empty for a while is to be saved and
  unloaded (`docs/plans/village-slice.md`, Stage 1.3's costs).
- **The zone's clock is its own, and there is no world clock.** `TickCount` is per zone and saved (the keystone every
  saved stamp is measured against, `persist_classes.go:46`); clients take the time of day from it. Saved timers are
  stamps against it (death ticks, drought and rain stamps, think, hunt and strike ticks) or counters advanced per tick
  (item lifetimes, brood stages, station progress, starvation timers, the breeding and compost cooldowns). The ROADMAP's
  world-clock item lines up the time of day between zones through `DayOffsetTicks`; it is not a count of elapsed world
  time, so nothing today tells a zone how much time it missed.
- **Randomness is per run:** the zone's seed is random at every start unless its `zone.json` sets one
  (`match.go:233-238`; `persist_classes.go:49-50`: "cross-restart bit-reproducibility is a non-goal"), and one random
  stream serves every decision: offspring counts, reseed and immigration, split offsets, fruit drops, the think and
  forage rolls, the daily rain roll.
- **The server runs each swarm's life at the group level**, every tick (`match.go:1331` onward): choosing food
  (`FindNearbyFood`, the nearest hit), moving the swarm's centre (and relocating: flies jump to a new spot now and
  then), feeding at the food (`:1478`, `:1491`), breeding and brood (`brood.go`; a hatch joins a same-species swarm
  within 4 cells, `brood.go:18`), nests and nest founding, the daily rain roll (`match.go:1618`,
  `handlers_env.go:262`), the ecology director's rain, drought, cull and reseed (`match.go:1594`,
  `ecology_director.go`; nest species are never reseeded, they recover through their nests, `:49-55`), merges and
  splits once a minute, continuous immigration, and the centipede's gnawing through fences.
- **Deaths of age and hunger are schedules, not dice:** each bug's death tick is fixed at birth and carried with the bug
  (`assignDeathTicks`, `handlers_bugs.go:54`); starvation culls 10% of a swarm once it has spent 90 s at zero satiation
  (`ecology_tuning.json` `starvation_death_secs`, read at `match.go:2273`), then every 40 s while it still starves —
  the re-arm uses the compiled 60 − 10 s instead of the tuned value (`match.go:2283`), the "starvation timer" fix
  already in the plan's Stage 1.3.
- **What only the computer in charge reports, and so stops when a zone empties:** the hunters' kills
  (`applyPredationStrike`, `predation.go:478`), which also feed the hunter (its only food for wasps, hornets and
  dragonflies), drop one carcass per victim (`predation.go:501-511`) and start its feed pause (`:524-527`); and which
  corpses a hunter eats or leaves (`handleCorpseConsume`, `predation.go:552`). Hunting is paced per hunting swarm: only
  when hungry (about three kills to sated), a strike cooldown, the feed pause, a hunt timeout (`predation.go:20-26`).
  When a zone's last player leaves there is no computer in charge (`resetZoneSync` clears it, `state.go:746`), so a
  server loop left running would hunt nothing.
- **Every rule mixes the change with telling the players' computers** (influence events and broadcasts in the same
  functions). The sync state is reset when a zone empties (`resetZoneSync`, `state.go:739`, called at `match.go:831`);
  an event logged after that and before the next first player would leave a gap in the sequence that stalls that
  player. A player's cell change queues an event early in `MatchJoin` (`match.go:626`). The zone's food list changes
  only through events (`state.go:1050-1067`) and is seeded at `MatchInit` (`state.go:1103`, which only adds entries it
  doesn't know).
- **The first player into a zone gets its bugs re-created from the server's swarm records:** its `ZoneAuthority`
  message, built inside `MatchJoin`, carries the swarm seed baseline and the food list (`match.go:666-676`); bugs start
  at their swarm's centre. Each swarm carries per-bug death ticks and hit points keyed by bug id
  (`entities/swarm.go:47`, `:123`) and the ids of its removed bugs, a set that only grows (`:116`) — in live play too.
- **Entering a zone has a fixed time budget:** `world_enter`, including starting a zone's match, shares
  `zoneEntryBudget` (8 s, under Nakama's 10 s request limit; `rpc/world.go:413`, `:492`), with the zone's lock held
  meanwhile.
- **The ecology director treats farmed and wild bugs alike:** its cull takes from every swarm of a species
  (`ecology_director.go:105-143`) and its counts include penned swarms. **Nothing marks a swarm, pen or feeder as a
  player's farm** (no owner field on the swarm record, `nakama/modules/entities/swarm.go`).
- **Cost:** the whole 256 village with ~390 bugs costs the server 0.39 ms a tick on average, 8.2 ms at worst, with a
  player present (`tools/_generated/scaling/2026-10-09-structural/summary.md`); a 512 zone at ~1,600 bugs is not yet
  measured. A game-day is 8,400 ticks (`match.go:55`), 14 real minutes; a fly lives about 5,500 sim-seconds, about 6.5
  game-days.
- **The project's law:** each bug's own behaviour lives on the players' computers; the server keeps group-level rules
  (`architecture_swarm_sync.md` §0). The design document's server review (§19 P10, proposed) asks that anything moved
  off the server keep a server copy that agrees exactly; a kill rule for empty zones agrees only on average, so it
  needs the owner's ruling (§7, question 5).

## 3. The options
Scored 1 (poor) to 5 (good) on: **faithful** (a farm and the wild end up where the full game would have taken them,
crashes included); **cheap** (server work and memory while zones are empty, and the wait on arrival); **fits** (the law
above, lockstep determinism, and the decided frozen zones of D57); **build** (work to build and to keep in step with the
live rules); **player** (no freeze, no exploit, legible, quick).

| | Option | Faithful | Cheap | Fits | Build | Player |
|---|---|---|---|---|---|---|
| A | **Every empty zone keeps running in full** on the server, with a stand-in for the kills | 3 | 2 | 2 | 3 | 5 |
| B | **Replay the missed ticks in full on arrival**, with a stand-in for the kills | 3 | 1 | 3 | 3 | 1 |
| C | **Catch up on arrival in coarse steps** of the server's own group rules (the decided design) | 3 | 2 | 5 | 2 | 3 |
| D | **Project recent trends:** each species' recent growth rate carried forward | 2 | 5 | 4 | 4 | 2 |
| E | **Per swarm, from its food access** (the owner's idea): fed swarms grow toward what their food supports | 3 | 5 | 4 | 3 | 3 |
| F | **Draw the arrival state from the zone's long-run pattern**, learned from headless runs | 2 | 4 | 3 | 2 | 2 |
| G | **A world stepper:** the same coarse steps, run in the background on the world clock for every zone nobody is in, from a small group-level summary of each zone (no match, no chunks in memory) | 3 | 4 | 3 | 2 | 5 |

**Why each wins or loses:**
- **A** runs every zone's full loop all the time, with every zone's chunks in memory (~50 MB per 512 zone, against the
  plan's rule to unload empty zones on a player's own computer), still needs the kill stand-in (with no computer in
  charge, a full loop hunts nothing), and reverses D57.
- **B** replays a loop with no kills in it, and costs about 3.3 s per missed game-day at 256 (8,400 × 0.39 ms): an hour
  of play elsewhere means a 14-second wait, past the 8-second entry budget.
- **C** is the decided design. Its cost grows with the absence (a 100-game-day absence is ~800,000 swarm-steps), the
  zone's entry budget is a hard 8 s, zones nobody has visited since a server restart pile up unbounded gaps, and two
  neighbouring zones caught up at different moments make bugs crossing between them hard to keep in order.
- **D** is what averaging does: it predicts a mild dip where the real system crashes or booms, and can't see what
  changes during the absence (a feeder running empty).
- **E** is right about what drives a farm (food), so it is the heart of C and G; on its own it leaves out hunting,
  showers and nests.
- **F** forgets the player's own changes to the zone (any new pen, plot or feeder makes a learned pattern wrong) and
  goes stale after every tuning change.
- **G** keeps the cost of arriving independent of how long you were away, keeps every zone on one timeline (bugs
  crossing between empty zones arrive in order; border events read current numbers), lets the "while you were away"
  note simply accumulate, needs no match and no chunks for an empty zone, and is close to what Eco does (its server
  keeps the world's coarse layers running whether anyone is near). It **reverses D57's "empty zones stay frozen"** into
  "empty zones step along cheaply"; the owner raised it (the server simulating empty zones itself), so it is his call
  (§7, question 1). **The trade-off it keeps:** Eco runs one population model everywhere, so it has no hand-over; we
  keep two (each bug on the players' computers while a zone is occupied, groups on the server while it's empty), and
  pay for that with calibration and a careful hand-over.
- **Dropped after the second critique — a "linger"** (a zone keeping its full loop a few minutes after its last player
  leaves): with no computer in charge it hunts nothing, so prey get a free window after every departure, and every bug
  is re-created from its swarm's record on return anyway.

## 4. The recommendation: G, in detail
1. **The world clock (designed first; the ROADMAP's item covers only the time of day):** one count of world time,
   advancing only while anyone is online, kept outside the deterministic simulation, saved. Open points for its own
   design: one owner across the zones' matches (one server process; the character registry knows who is online); how an
   occupied zone's `TickCount` maps to it (Nakama doesn't catch up late ticks; test zones run faster than real time);
   how the single-player menu pause (§19 Q2) fits; start-up (the clock is the larger of its saved value and every
   zone's "current to" stamp). **Cut-over:** when G ships, every zone of the world is made current to the clock's
   start, so no zone owes time from before it.
2. **The world stepper:** one server-level worker that owns every zone of the world nobody is in. It works from each
   zone's **group summary** — swarms, nests and brood, food sources with their positions and levels, ground items,
   stations, crops, a walkability bitmap (a 512 × 512 zone is 32 KB of bits) — saved with the zone, not from a live
   match. When a zone's last player leaves, its match saves and hands the zone to the stepper (under Host & Play the
   match then unloads); when a player enters, the stepper hands the zone back current to that moment. Only the world's
   zones are stepped (a list from the neighbour graph or a manifest); test and bench zones never are, and a server
   switch turns stepping off for measurement runs.
3. **The step, on a fixed world-time grid** (one step per game-hour of world time, 35 real seconds), staggered across
   zones, within a fixed time slice per pass (S.T.A.L.K.E.R.'s A-Life updates a slice at a time), zones next to occupied
   ones first. **When behind:** the zone a player is heading into goes first; the bar sets how far behind any zone may
   fall and the most an arrival may wait.
   - **Every timed field advances,** driven by a nested classification of the saved state (each field a stamp, a
     counter, or untimed), enforced by a reflection test the way `TestPersistClassificationComplete` enforces the
     top-level one, so a new timed field can't be forgotten. The zone's `TickCount` advances by exactly the time
     stepped, so every stamp stays valid and the time of day matches the other zones. Where a closed form exists the
     step jumps there (regrowth to a cap; a timer's whole cycles with the remainder carried).
   - **Swarm by swarm, the live rules as pure state changes:** food in reach over the swarm's home range, shared fairly
     among the swarms at the same food; relocation at the live rate; feeding, breeding and brood counted in whole
     feed–breed–hatch cycles; death ticks and starvation exactly on their live schedules; splits by the live rule; the
     zone cap as live.
   - **The numbers stay sound:** inside a grid step, a queue of each thing's next event (a feeder empties, a shower
     starts, a nest hatches) cuts the step where something changes; predators and prey are coupled so counts can't go
     negative (losses in the denominator); births, deaths and kills are whole bugs; where a species' growth over one
     step would exceed about half its number, the step is split for it — as a fixed function of the state at the
     grid step's start.
   - **Hunting at its real pace:** per hunting swarm, kills ≤ the prey in its range, and ≤ what hunger, the cooldown, the
     feed pause and searching allow; each kill feeds the hunter (so it stops when sated) and drops a carcass; whether the
     hunter eats or leaves it follows the live roll. Only the search time is calibrated.
   - **The ecology director does exactly what it does live,** farms included — one rule both ways, so nothing is safer
     while you're away; whether farms should be treated differently is the owner's call (§7, questions 2–3).
   - **Randomness:** every draw the step makes is keyed by (zone's catch-up seed, grid step or event time, thing,
     purpose), so the result is byte-identical however the computing is scheduled (in one pass, or interrupted and
     resumed, or after a restart). The catch-up seed is a saved per-zone number used only by the step (an engineering
     choice); the live random stream stays per run; a non-zero `zone.json` seed wins for test zones.
   - **A step that fails changes nothing:** it computes into a copy and commits it with the zone's "current to" stamp
     in one go; a crash in the middle is caught at every entry point; a zone whose step keeps failing is frozen at its
     last good state, logged once, and reported. A test injects a failure.
4. **Saved as it goes:** the stepper writes each zone's save with its "current to" stamp on a fixed cadence; a bug
   leaving one zone for another is saved with its arrival record in one transaction (the ROADMAP's migration design),
   so a crash neither loses nor doubles it. Occupied zones publish a small, lock-protected summary (numbers near each
   border) for border events, so no zone reads another's live state.
5. **The hand-over, at the top of `MatchJoin` when the zone has no members, before anything else:** reset the sync
   state, clear and rebuild the food list from the zone's state, renumber each swarm's living bugs (with their death
   ticks and hit points carried to the new ids) and clear the removed set; then the ordinary bootstrap
   (`match.go:666-676`). The stepper's last partial step (from the grid to the arrival moment) is the one step cut off
   the grid. Tests: after the hand-over the event counter is 0, nothing is queued, the food list equals the rebuild, the
   death ticks and hit points are the same as a set, a first and a late joiner agree hash for hash, and two players
   entering in the same moment get one hand-over.
6. **Arrival:** nothing shows before the zone is current; bugs start at their swarm's centre, as for any first visitor
   today. A **"while you were away"** note (one new message) for the player's own things — the farm grew from 40 to 130
   flies; the feeder ran dry on day 3 and 25 starved; the crops got two showers — which needs the game to know what is
   the player's (§7, question 3).
7. **Weather:** the shower schedule becomes a fixed function of (the zone's catch-up seed, world day), live and in the
   step alike, so it no longer shares the bugs' random stream (every fixed-seed test run's numbers shift once, so the
   baselines are re-recorded); the director's rain and drought stay a lever of last resort (the GDD, 2026-09-28).

**The acceptance bar (proposed numbers, for the owner to confirm before the first run):**
- **Agreement with the full game,** from saved states of the 512 test zone: the full game (headless, a parked, peaceful
  observer) and the step, over 0.5, 2, 8 and 30 game-days, 40 seeds per span. Per species: the step's median end count
  inside the full game's own middle half of results, or within ±15% of its median; a **crash** = a species below 20%
  of its full-game median for 2 game-days or more, and the step's crash share within ±10 points of the full game's.
  Per region (the zone in 4 × 4 blocks): the same median rule. A penned, fed fly farm and an unfed one: the step's mean
  within ±10% of the full game's, either way. Routine tuning changes re-run a smaller set (2 and 8 game-days, 10 seeds);
  the full set before each sign-off.
- **Bookkeeping:** per species, start + births − deaths ± migrants = end, with unique bug ids; byte-identical saves
  whatever the computing schedule; a crash in the middle of stepping; the every-timed-field test; the hand-over tests;
  a zone emptied and refilled against one never emptied, over the same span, inside the same agreement rule.
- **Time and memory:** stepping 20 world zones ≤ 2% of one processor core on this PC (and measured on the slower one);
  each zone's group summary ≤ 1 MB in memory; no zone more than one game-day behind the clock; a first player's wait
  for the zone ≤ 2 s.
- **Run time:** 40 seeds × 40.5 game-days is ~1,620 game-days, about 380 hours at normal speed; at 30× with four
  isolated runs at once, about 3 hours. Stage 1.6 must reach that before this bar can run.

## 5. Smaller live issues found on the way (for the BACKLOG, whatever is chosen)
- The starvation re-arm ignores the tuned threshold (`match.go:2283`) — already the plan's "starvation timer" fix.
- Each swarm's set of removed bug ids only grows and travels in every baseline and save (`entities/swarm.go:116`).

## 6. What it costs to build (a first estimate; the real size is written in PROGRESS when it starts)
- **Large:** turning the live group rules into pure state changes with a separate "tell the players' computers" layer,
  in the determinism-gated server package, so every gate runs (`nakama/modules/world/CLAUDE.md`); it also makes the
  live code easier to test. The world stepper with its group summary and hand-offs. The nested timed-field
  classification and its test.
- **Medium:** the world clock; the catch-up seed and the "current to" stamp in the save; the stepper's saving and
  exactly-once migration; the hunting rate; the numerics (event queues, sound coupling, split steps); failure
  containment; the hand-over; the agreement harness and its runs.
- **Small:** the "while you were away" note; the weather schedule as a function; re-recording fixed-seed baselines.
- **Depends on:** Stage 1.6's fast runs; the server review (D58); the migration design for border crossings; the
  answer to question 3 for the note.

## 7. Questions for the owner
1. **G as recommended** — empty zones step along cheaply in the background on the world clock — which **reverses D57's
   "empty zones stay frozen"** (D57, GDD §01 and §19, the ROADMAP and the plan's summary would change)? Or keep D57:
   catch-up on arrival (C), with the waits and limits in §3?
2. **Farms while you're away in another zone:** you gave the reason for stopping the world when everyone logs out:
   players shouldn't return to a farm wrecked while they were away. While you're merely in another zone, recommended:
   the same rules as when you're there (fed → grows; feeder empty → hungry → losses; the director's culls and droughts
   count farms as they do live). A kinder rule for pens is a taste call.
3. **What makes something "yours"** (a pen, a plot, a released swarm)? The game doesn't know today; the note and any
   farm rule need it — likely a §05 (bug farming) question.
4. **A friend plays while you're logged off:** the world clock runs, so your farm keeps going (and can be hurt) while
   you're offline and they're online. Fine, or should a logged-off player's things wait for them? The shipped example
   is ARK's offline raid protection: a base is protected only after its last member has been offline 15 minutes (so
   nobody logs out mid-fight to escape). It needs question 3.
5. **Hunting while nobody is there:** a server-side kill rule matches the full game only on average (checked by the
   bar above), not kill for kill. Acceptable for empty zones?
6. **Centipedes gnawing fences while you're away:** live, they chew through a fence in about 16 s, and penned prey are
   easier targets. Include it (pens can be breached while you're in another zone), or keep pens safe in empty zones —
   given your reason for pausing at logout?
7. **Zones nobody has visited yet:** have they been living since the world was made (recommended: yes, every world zone
   is stepped from the start, which also means a single player's computer steps every zone — small, to be measured)?
8. **The acceptance bar's numbers** (§4): confirm or change.
9. **When it gets built:** recommended after Stage 1.6 (the fast runs to calibrate against) and the server review, the
   world clock first; calibrated after Stage 3's behaviour and hunting retune.

## 8. How sure I am (evidence-gated; revised)
| Claim | Certainty | Evidence | What would raise it |
|---|---|---|---|
| The server owns the group life cycle the step reuses | 90 | `match.go:1331-1617`, read | — |
| …and it can be turned into pure state changes at reasonable cost | 50 | every rule also sends events | Scope the refactor |
| The stand-in list is complete: kills, the hunter's feeding, carcasses, corpse eating | 85 | Every client-to-server opcode traced (round 1); the two re-read (`predation.go:478-556`) | A test that steps an empty zone and finds no other change missing |
| The step can match the full game's spread for farms and the wild | 40 | Super-individuals (Scheffer 1995) under the same rules; aggregation errors of 45–70% elsewhere; stand-ins run fast (Chenney) | The agreement runs |
| The step's numbers stay sound over 30 game-days | 50 | The maths research's rules, adopted in §4.3; not yet tried | A prototype over 30 days |
| A group summary is enough to step a zone (no chunks) | 45 | Food anchors, items, stations and crops are listable; walkability as a bitmap; unproven | Build the summary for the 512 test zone and step it |
| Stepping 20 zones fits 2% of a core, with saves | 40 | ~300 swarms × one step per 35 real seconds per zone; save cost unmeasured | Measure |
| The hand-over leaks nothing | 55 | The reset and bootstrap exist; the rebuild and renumbering don't | The hand-over tests |
| The world clock can be built as described | 50 | One server process, a registry of who is online; undesigned | Its design |
| Saving and migration are exactly once | 40 | The ROADMAP's transaction design; unbuilt | Its tests |
| A failing step is contained | 50 | Copy-then-commit is standard; unbuilt | The injected-failure test |
| G beats C for the player | 75 | C's growing cost against the 8 s entry budget; B's 3.3 s per game-day | The 512 server tick; a C prototype timing |
| **Overall (the lowest row)** | **40** | | The agreement runs and a prototype |

## 9. Critic log
- **Round 1 (2026-10-10), a fresh agent, verdict: material problems.** Accepted and folded in, each re-checked in the
  code first: the kills are not the only thing the computer in charge reports (the hunter's feeding, carcasses and
  corpse eating too); a reused rule leaks events into the next first player's stream and leaves the food list stale;
  the rules can't be reused as they stand; deaths of age and hunger are schedules, not dice; no world clock exists and
  the zone's clock needs a missed-time rule; the background step was missing as an option; A's memory cost was wrong;
  B needs the kill stand-in too; F's reasoning was off and the bar must reach 30 game-days; hunting saturates per swarm;
  exempting farms from the director would make being away safer; no "farm" exists in the code; frozen positions and
  deferred splits distort farms and the wild; shared food must be split fairly; gnawing needs a rule; calibrating from
  recent live play is unsound (a player present, few kills, manipulable — now calibrated headless); cross-zone order;
  the catch-up's time inside the match loop; weather can't be replayed from today's random stream; removed bug ids pile
  up; nest species aren't reseeded; a logged-off owner's farm; the cost claim and the step size; the bar's spans,
  seeds, two-sided farm test, observer and missing checks; an inflated certainty table; taste calls presented as
  decided.
- **Round 2 (2026-10-10), a fresh agent, verdict: material problems.** Accepted and folded in, re-checked first: the
  linger hunts nothing and re-creates every bug on return anyway, and as written it would stall the next first player —
  dropped, with the hand-over moved to the first player's join; stepped zones were never saved and had no "current to"
  stamp; the seed is random per run and kills are far from the only random draw; the starvation numbers were wrong
  (90 s, then every 40 s); the ROADMAP's world-clock item is only the time of day; the on-demand path sits inside an
  8-second entry budget; G reverses D57 — now said plainly; the step's numerics; corpse and relocation rules and
  hunger-limited hunting; the bar's seed count, tolerances and run time; the cost estimate; the nested timed-field
  classification; the owner's reason for pausing at logout in the questions; the zone cap in the step; citation fixes.
- **Round 3 (2026-10-10), a fresh agent, verdict: material problems.** Accepted and folded in, re-checked first:
  loading every zone at start-up would hold ~50 MB per 512 zone against the plan's rule to unload empty zones on a
  player's own computer, would block the server's start, and breaks tests and calls that assume a zone exists only once
  visited — replaced by a world stepper working from each zone's small group summary, with no match; the warm-up before
  the zone is drawn can't run faster than real time under the frontier rule — dropped (bugs start at their swarm's
  centre, as today); a failing step must change nothing (copy, then commit with the stamp; frozen after repeated
  failure); a policy for falling behind; steps on a fixed world-time grid with draws keyed by grid step, so splitting
  can't change results; the per-zone seed was wrongly credited to the owner's 2026-10-06 "starting seed" direction — now
  an engineering choice used only by the step, the live stream staying per run; the hand-over at the top of `MatchJoin`,
  with death ticks and hit points carried through renumbering; the step advances the zone's `TickCount`, and a cut-over
  rule; border events read a published summary, not another zone's live state; the bar now has numbers; the scores and
  certainty rows corrected; questions added (zones never visited, a single player's computer stepping every zone, ARK's
  offline protection as the precedent); D57's real file; two citations.
- **Next:** once the owner chooses, the chosen option's build design gets its own critique rounds until a round finds
  nothing material.
