# Plan — The village slice: a sound foundation, a village four times bigger, its bugs tuned (2026-10-04)

> **The one active plan.** It replaces the order of work in
> `docs/plans/finish-bugs-zones-items.md` (3–4 October; called "the earlier plan" below), which stays in the repo as the
> reference for its requirements and designs (Parts B–E, the behaviour model D0–D7, the combat groundwork C1–C12), and
> it replaces the morning plan of 4 October, archived as `docs/plans/archive/finishing-the-game.md`. It sits under
> [`ROADMAP.md`](../product/ROADMAP.md). Nothing here is decided automatically; the owner reviews every stage's results.

## In one screen (the owner reads this; everything below is the working detail)
**The goal:** the village rebuilt four times bigger (512 × 512), holding 1,000–2,000 bugs that feed, breed, hunt and
rise and fall on their own with no stutter; tuned; then played and signed off by you. What it teaches becomes the kit
for the zones around it (bees, ants and the rest), which come after.

**Already decided, not reopened:** every bug in a zone is simulated while anyone is in that zone, in step on every
player's computer (built June–July); bugs act only on what they sense nearby; zones with nobody in them pause; bug
behaviour lives on the players' computers.

**Wrong today (measured 2026-10-04):** the server sets up nests and food only near a player, so most of the village is
dead on the server; the players' computers waste ~23 of 27 ms per tick at ~3,300 bugs (mostly every bug checking
every piece of food in the zone); the full bug state is re-sent every 10 s whether anyone joins or not; four counting
faults (the centipede breeds and starves in a loop, and three more).

**The steps:**
- **0. Tidy:** this becomes the one plan; old plans archived; the tuning guides fixed so they can't wipe the real
  village save; the review app published when you say "publish".
- **1. The foundation** (my engineering; you see the numbers):
  - the measuring and checking tools first: cost per part, worst frames, a behaviour check, several players, a slower PC;
  - the waste cut on the players' computers: every behaviour kept, a different method allowed where it's better;
  - the server runs the whole zone; water stops bugs as you decided; the counting faults fixed; then a 48-game-day run
    of today's village (only its broken parts fixed; the real tuning happens at 512);
  - the bug state sent when someone joins instead of every 10 s (a slow safety copy stays until that's proven), and
    much smaller;
  - zones of 512 × 512, and a 512 test zone you walk around;
  - faster tuning runs, scored automatically; every server system costed, to decide what moves off the server.
  Done when 2,000 bugs run on this PC with no dropped frames, and within budget on a slowed-down one.
- **2. Your decisions on the numbers:** the bug budget, and what moves off the server.
- **3. The village at 512, with you:** first how we design zones (in the app) → map and bug list → layout → build, with
  each bug's behaviour and fight designed alongside and tried in the arena → the bug items → tuning → pressure tests →
  you play it and sign off → it replaces today's unfinished village. **3b:** the rest of the
  village (fishing, the Ecology tab, plots, tutorials, catching gear).
- **4.** The kit, then the next zones. **Alongside:** the design document's sections, in the order the village needs.

**What I need from you:** approval; "publish" when the items page is closed on your other devices. Along the way: the
Stage 1 targets, the bug budget and what moves off the server, a wording change to the zone-building rule (so natural
ground can be generated), the village's map and bug list, a navigation aid for big zones, each sign-off; and
whether I may delete the rehearsal page.

**How sure I am:** I would do this, in this order (90). That the design is right as written: 75. The weakest parts are
making a four-times-bigger village good to walk around and making tuning runs fast enough; both are tried early.

## Where we are (2026-10-04, evening)
- **Built and committed:** the review app (tested, rehearsed; publish waits for the owner), the measurement tools
  (`tools/ecology/scaling_study.py`, the bench village, per-part client timers), kill/catch stats, the fixed ecology
  test client.
- **Found today, verified in code and measurements:**
  1. **The server brings to life only the chunks a player has loaded** (`handlers_world.go:23-43`; unloaded ground is a
     wall for moving bugs, `state.go:607`). One player loads 25 of the village's 64 chunks, so about 40% of the village
     lives. The June tuning used a driver that loaded all 64; every run since 2026-07-18 measured a shrunken village.
     The bugs on the players' computers are simulated zone-wide by design (`architecture_swarm_sync.md` §0 and §12.3,
     built June–July); the server's set-up of nests and food and its walls for moving bugs were never made zone-wide
     (the ROADMAP's "zone-complete collision/loading" item). A fault against the design, not a design question.
  2. **The players' computers waste most of their bug time.** At ~3,300 bugs at normal speed a tick costs 27.4 ms
     (food lookup 15.0; strikes 4.3; state check 3.3; per-tick re-sorting 1.9; the rest of the bug movement 2.7), and
     every frame adds 6.5 ms (smoothing 3.2, re-sorted every frame; centipede trails 3.3, list shifting every frame) for
     every bug, visible or not.
  3. **The snapshot** is ~670 bytes a bug, re-sent every 10 seconds whether anyone joins or not, because the server keeps
     only 20 seconds of events (`state.go:1018`).
  4. **The centipede breeds and starves in a loop** (new groups start at satiety 50, breed at 32, no cooldown;
     `brood.go:350-357`, `handlers_bugs.go:109`, `predation.go:880`; since `05cca298`, 2026-07-18).
  5. **The tuning that worked** is the June 19 bake, which is what ships (`ecology_tuning_log.md`, "Phase-2 rebalance
     r2-r6 → BAKED"): flies ~112, butterflies ~45, millipedes ~19, wasps ~16, centipedes ~4, beetles ~3. Those runs had
     the whole zone loaded and the server deciding predation.

## The big picture: where this plan sits
| Track (ROADMAP) | Where it stands | Relation to this plan |
|---|---|---|
| **Phase 1 — the design document (GDD)** | 2 sections final, 3 waiting for review, 3 in rework, 16 drafted | Runs alongside; the village's sections first (see "Alongside") |
| **Phase 1 — bugs, behaviour, zones' bug lists, items** | the earlier plan (`finish-bugs-zones-items.md`) | **This plan** (the earlier plan's order of work replaced by the stages; its designs kept as reference) |
| **Phase 1 — art** | copper outfit approved (2026-09-26); the other seven picked outfits continue batch by batch, each asked for (ROADMAP:61-62); after the GDD sign-off: the remaining outfits, the 11 townspeople, then world and item art (a sizing rule first) | Unchanged; runs alongside. The 512 village's art list comes out of Stage 3 (each new bug uses an existing sprite or a placeholder until its batch) |
| **Phase 1 — engineering** (hosting, world clock, frozen-zone catch-up, reconnect, CI, the server review) | saves and backups done (D73); the rest not started | Whole-zone loading (Stage 1.3) is the roadmap's "zone-complete loading" item, and the server review (D58) is Stage 1.6; the rest stay on the roadmap, after this plan's Stage 1 |
| **Phase 1 — examine texts, polish audits, the item pass** | the item pass batches 1 and 3 settled; weapons batch open | Items for the village come with Stage 3 (Part E); the other batches continue in the app |
| **Phase 2 — the existing zones to final quality** | not started | **Stage 3 is its first zone** (the village), now at 512; Stage 4 continues it |
| **Phase 3 — new zones in rings** | not started | Stage 4, each at 512 through the same zone process |
| **Phase 4 — polish, balance, release** | not started | after Phase 3 |
| Open plans: grass phases 2–5, swing phase 6, repo-health P7 | paused | unchanged; picked up when their turn comes on the roadmap |

## Now (the resume pointer — update at the start and end of every session)
- **Now:** Stage 0's last step: publish the review app when the owner says "publish" (steps 1–3 done 2026-10-04:
  the plan home and archive, the records and D84, the plan's page).
- **Next:** Stage 1.0a (the server's hold-population switch and behaviour counts), then 1.0b–1.0e, as designed under
  "Stage 1.0 design" (reviewed against the code 2026-10-06).
- **Waiting on the owner:** approval of this plan; "publish"; the OK to delete the rehearsal page.

## PROGRESS (this plan; newest last — the history before it is in the earlier plan's PROGRESS)
- **2026-10-04 (evening):** written after the owner asked for one careful, coherent plan for the village slice (512 ×
  512, 1,000–2,000 bugs, the waste fixed first, the whole zone simulated). Built on three code surveys (what assumes 256;
  whole-zone loading; every plan and how they conflict), the day's measurements, the ecology history, and a cold
  review; every load-bearing claim re-checked in the code. Nothing in it is built yet.
- **2026-10-04 (late evening):** reorganised after the owner couldn't read the plan in the terminal: a one-screen summary
  on top; the earlier plan no longer copied in (it stays in the repo, linked); old plans to be archived (Stage 0). The
  owner's direction that optimisations keep every behaviour but may use different methods is folded into Stage 1 (a
  behaviour check alongside the equivalence check). Nothing cut from this plan's own content. A second cold review
  (about 45 code references checked, all correct) found ~25 text problems, all fixed after checking each against the
  files: "keep by default" for the server review (against D58 and D83) removed; the perf-tuning skill's identical-only
  rule and its real-save command added to Stage 0; the arena checks moved to a non-peaceful copy; the fallback made
  able to finish Stage 1; missed links and memory notes added to the archiving; dropped earlier-plan items restored.
- **2026-10-04 (night), Stage 0 steps 1–3 done** (`0b882826`, `165fbe7e`, and the plan page's commit):
  - this plan committed as `docs/plans/village-slice.md`; the earlier plan labelled section by section as done,
    replaced or reference; three plans archived with `git mv` (history kept) and every link updated, found by name
    and by description; the plans index grouped (active, reference, paused, archived); the grass plan's status
    corrected against its commit and the code;
  - the tuning and performance skills, the tuning log and the charts README no longer tell anyone to run
    `run_config.py` on the real village; the performance skill and the bug-budget page follow the owner's direction
    on optimisation; D84 written; the review-app plan records the passed rehearsal;
  - the plan's readable page published (link in Stage 0, step 3), built by `tools/gdd/build_plan_page.py`.
  - **Next:** Stage 1.0 (the behaviour check, the noise floor and the "before" numbers first); the publish waits for
    the owner.
- **2026-10-06, Stage 1.0 under way.** The owner: wiping the village's save is fine (it gets rebuilt), so the
  save-wipe rule was softened everywhere (`a7ba05da`). The Stage 1.0 design was reviewed against the code, then by a
  cold reviewer (13 findings, all checked and folded in: `902e1c01`).
  - **1.0a done** (`32a8eda4`): `hold_population` and `BEHAVSTATS`; 16 paired Go tests; a live hold-vs-control pair on
    the bench (2 game-days each) shows no births after day 1 and only predation deaths when held.
  - **1.0b/1.0c built:** the client probes (`Util/TestProbes.cs`, `Testing/TestRig.cs`, hooks in `SwarmManager`,
    `CentipedeTrail`, `PlayerController`, `HeadlessSyncTest`), a release build, and the scripts (`equiv_check.py`
    with 13 tests, `behaviour_check.py` with 8, `make_route.py`, `run_gates.sh`, `run_players.sh`, `wipe_zone.py`,
    and options in `run_sync_latejoin.sh`, `run_ecology_client.sh`, `run_config.py`, `scaling_study.py`). The base
    build for old-against-new checks is kept at `BugFarmerClient/Build/SyncTest_base/` (the rig, no optimisation).
  - **First smoke test** (bench, 2 game-days, clean mode): every file written; per tick p50 1.4 ms / p99 6.3 ms at
    ~270–890 bugs; the snapshot builds in 10–12 ms at ~590 KB; per-thread allocation counting isn't supported by the
    client's Mono (as the reviewer expected), the per-frame counter is, and shows ~170–450 KB of garbage per tick.
  - **The equivalence check proven:** the same build twice, both ways round, on the bench (3-minute runs, the
    player in charge with every test flag on): IDENTICAL, about 1,300 live ticks of fingerprints and 551 / 1,303
    detections and corpse reports. A build with the food-sensing radius planted at 2.6 instead of 2.5: DIVERGED both
    ways round, from the joiner's first live tick. The first same-build run exposed a flaw in the check (strike sends
    are paced by a local throttle that starts empty on a joiner), fixed by comparing detections instead.

## The owner's direction for this stage (2026-10-04)
- **The village is the first slice, and it becomes four times bigger** (twice as wide and tall: 512 × 512 cells), for a larger
  world; later zones follow at that size.
- **It holds 1,000–2,000 bugs to start; more is better.** No stutter: a tick that takes two frames is not acceptable.
- **Fix the waste first**, then decide how many bugs, then tune.
- **Optimise well and keep every behaviour working**; a different method (heuristic) is fine where it's better, as long
  as the game still works the same way.
- **The whole zone is simulated**, never only what one player has near them: long decided, and the only way every
  player stays in step (restated today, not new). Bugs still act only on what they can sense nearby. (Drawing stays
  limited to what's on screen; that's not simulation.)
- **Redesigning the village completely is fine**, using what exists as the base, iterated until it's good.
- **Test thoroughly, simulated like real:** the real client and server, the whole zone, real speed checks.
- **Tune for a functional ecosystem without players.** What players do to it, they do; disruption is fine.
- **One coherent plan** that ties into the rest of the planning, with no drifting between plans.

## The order of work
Each stage ends at a check that proves it; the owner reviews the results in the app. Stage 1's engineering can run
alongside Stage 3's first design steps (they don't depend on each other), but **no tuning starts before Stage 1 is done.**

### Stage 0 — one home for everything (short; every file move checked, nothing guessed)
1. **This plan becomes the only order of work,** committed as `docs/plans/village-slice.md`. ROADMAP keeps the phases
   and the owner's decisions (*what*); this plan is the *when*.
   - **The earlier plan** (`finish-bugs-zones-items.md`) stays where it is, as the reference for its requirements and
     designs. A banner at its top says its order of work is replaced by this plan, and its sections are labelled: the
     morning's order of work, certainty assessment, "what I need from you" and key risks *replaced by this plan*; Part
     0, Part A (apart from the publish) and the overnight run *done*; its context, requirements, "How we work", the
     owner's answers, acceptance criteria, deferred decisions, out of scope, files and test plan *reference, still in
     force*.
   - **Archived** into `docs/plans/archive/` with `git mv` (history kept), each with a dated line at its top saying what
     replaced it: `finishing-the-game.md` (replaced by this plan), `player-arm-and-wearables.md` and
     `player-sprite-and-wearable-creation.md` (both superseded in July). Every mention of them is found first, by file
     name with `git grep` (today: the plans index, BACKLOG, `architecture_bugs.md:1066,1071`,
     `architecture_swarm_sync.md:82`, and `player-arm-and-wearables.md:16`) and by description (`README.md:51` says
     "the two superseded player plans in `docs/plans/`"), and updated; the relative links inside each moved file are
     fixed for its new folder (`finishing-the-game.md:4-5` links `../product/ROADMAP.md` and
     `finish-bugs-zones-items.md`); a second search finds nothing left pointing at an old path.
   - **Kept in place, marked paused:** `grass-overhaul.md` (its top line says the plan shipped; what commit `5f6fc1d5`
     actually shipped is the tile variants and a simple tuft layer, so the line is corrected to say exactly that and
     to list what is still open, checked against the commit, not guessed), `swing-design-and-outfits.md` (phase 6
     open), `repo-health-enforcement.md` (P7 open). `review-app.md` stays until the publish is done (code comments
     point at it), then is marked done.
   - **The plans index** (`docs/plans/README.md`) in four groups: active (this plan), reference (the earlier plan,
     `review-app.md`), paused, archived; `docs/README.md`'s row for plans says the same.
   - **Pointers:** ROADMAP's Phase 1 line, the GDD README and BACKLOG point here instead of the earlier plan;
     CLAUDE.md's "Find depth in" list gains one line for this plan. BACKLOG gets one "Now" line at its top pointing
     here; each of its other "Now" headings is read and renamed "Later" only if it is no longer current work (items
     untouched); the art track's heading (`BACKLOG.md:12`) stays, since art runs alongside. The memory notes that call
     the earlier plan the live one (the index line in `MEMORY.md`, `finish-plan-resume.md`,
     `bestiary-ecology-review.md`) point here.
2. **Records made true, the ones this plan depends on:**
   - **the `ecology-tuning` skill stops telling a session to tune on `village_21_B`** with
     `run_config.py --zone village_21_B` (`SKILL.md:52-60`): that tool wipes the tested zone's save, so tuning runs on
     the bench copy only; the skill also gains today's facts (the whole zone must be alive, the client's clock at the
     zone's speed, the scaling-study tool);
   - **the `perf-tuning` skill** gets the same fix (its profiling command at `SKILL.md:15` also runs `run_config.py
     --zone village_21_B`), and its step 3 ("a perf change to the sim must produce BYTE-IDENTICAL results",
     `SKILL.md:42`) is brought in line with the owner's direction: every behaviour kept; identical where that comes
     naturally, proven by the equivalence check; a different method allowed where better, judged by the behaviour
     check. Every computer must still agree with every other; that part doesn't change;
   - the explanation page `docs/gdd/explain/04-bug-budget.md` (lines 36-38 promise "bit-identical results" for every
     fix) says the same;
   - the review-app plan, the earlier plan's PROGRESS and the plans index say the app is built and rehearsed;
   - the explanation page `02-first-slice.md` stops saying the village's layout is redesigned separately;
   - **a dated decision (D84)** records the owner's direction of 2026-10-04: the village rebuilt at 512 × 512 as the
     first slice, later zones at that size; layout before tuning; 1,000–2,000 bugs to start, more is better;
     optimisations keep every behaviour and may use different methods; tuning for a functional ecosystem without
     players. It cites the zone-wide simulation as the long-standing design it builds on (`architecture_swarm_sync.md`
     §0, §12.3), not as a new decision. §01's "Decided" list gains the zone size.
   - *Placed elsewhere:* the design-document corrections the survey found (D83's water answer in §01 and §04, §03's
     opening paragraph, the §02 and §18 stubs, one section order in the GDD README) go with the GDD work
     ("Alongside"); the stale combat docs (C12) go with Stage 3's combat work; the art-timing mismatch between
     ROADMAP:28 and ROADMAP:61-62 becomes a BACKLOG line for the art track.
3. **The plan as a readable page,** published privately so the owner can read it whole (the terminal cuts it off):
   **done 2026-10-04,** https://claude.ai/artifact/LGvYMWJWdgT8HBkjtD4Udp, built by `tools/gdd/build_plan_page.py`
   and republished at the end of each stage; it moves into the app once the app is published.
4. **Publish the review app** (the owner closes the items page on other devices and says "publish"; then export, publish,
   compare every mark, test note — the procedure rehearsed on 2026-10-04). From then on every review lives in the app,
   including this plan and the explanation pages. **Until it is published**, a review that is ready goes out as its own
   private page (as the explanation pages could), and moves into the app afterwards; no work waits on the publish
   except Part B's zone-design conversation, which the owner wants held in the app (the earlier plan's answer 1).

### Stage 1 — the foundation under the bugs (engineering; mine; the owner reviews the numbers)
Every change keeps **all computers in agreement** and passes the Go tests and both late-join gate halves before it is
kept. Each goes through the repo's own process first: `.claude/complex-change-review.md` (stages × failure modes, the
invariant checklist) for 1.1, 1.3 and 1.4; the `frontier-sync` recipe for anything the simulation reads; the
`perf-tuning` skill's safe-optimisation steps; a headless Unity compile for every client change. Two kinds of change,
kept apart:
- **Performance changes (1.1, 1.2) keep every behaviour working.** Most of them give exactly the same results by nature
  (the waste is repeated or copied work), and for those the equivalence check proves it cheaply. Where a different
  method is clearly better (faster or simpler, and the game still plays the same; the owner's direction of
  2026-10-04), it is allowed, named as a behaviour change in its commit, and judged by the behaviour check instead.
- **Structural changes (1.3–1.5)** change what happens, on purpose, and are measured as such.
Cheap, certain wins first; the size work, which depends on the village's new layout, last. Built in this order:

**1.0 — The rig and the checks, before any change** (reviewed against the code 2026-10-06; the full design is under
"Stage 1.0 design" below). Built and proven in this order, each piece tested before the next relies on it:
- **1.0a — the server side:** a test-zone switch that holds the bug count steady (no births, no ageing or starvation
  deaths, no top-ups; predation still kills, so hunting stays real; merges and splits keep running), one daily line of
  behaviour counts per species (feeding, eggs, trips home, nest defences, merges, splits, hits on players), and a clean
  start for every run.
- **1.0b — the client side** (one test build): per-tick and per-frame timings with p50 / p99 / max and allocations, a
  "clean" mode without the per-part timers (their own cost skews the numbers) and a "breakdown" mode with them; the
  snapshot's build time and size; a per-species tally of what the bugs are doing; the strike and corpse reports logged
  on every computer (shadow reports); a per-tick fingerprint log for the whole run (today's trace keeps only the last
  500 ticks); a scripted route for the test player (a wanderer headless, a camera tour when windowed); a release build
  beside the development one.
- **1.0c — the scripts:** each test player can run its own build; the equivalence check compares the fingerprint logs
  and the shadow reports; the behaviour check compares counts against the noise floor; the cost summary reports
  percentiles; one gate-runner; a launcher for two to four players.
- **1.0d — proving the checks:** two copies of the same build must come out identical, a build with a planted one-line
  change must be caught, five seeds give the noise floor, and a planted behaviour change must be flagged.
- **1.0e — the "before" numbers** on the 256 village's bench copy: natural runs at 1× and 4×, fixed counts of 1,000 /
  2,000 / 4,000 (clean and breakdown), the windowed tour, two players, the slower computer; written up for the owner.
- **The slower computer:** two cores by process affinity (no machine setting touched); the frequency cap through the
  Windows power plan is a machine-wide setting, so it is used only with the owner's OK and restored right after.
- **Every gate on bench zones by default, wiped before each run** (`run_sync_latejoin.sh` defaults to `village_21_B`; a
  bench zone has no neighbours, and wiping its save first means each run starts from the same state).

**1.1 — The client's bug simulation without waste** (one change per commit; each through the behaviour check, and the
ones meant to give identical results through the equivalence check too):
- one food lookup per group per tick, food kept in a grid of cells (the lookup checks only nearby cells, same tie-break);
- each group's living bugs and the zone's groups in sorted arrays, **replaced (never edited) when a bug or group is born,
  dies, merges or splits**, with the comparer named explicitly (`Comparer<string>.Default`, today's order); the
  hunt-preparation step keeps its value copy of last tick's prey positions (predators must all read last tick's
  positions whatever the order, `SwarmManager.cs:574-588`), into a reused buffer;
- the state check reads its numbers straight from each bug (today it builds a 31-field record per bug per tick);
- the strike check reuses buffers;
- no memory allocated per tick;
- **the ordinal-order item, after the identical changes, as its own deliberate behaviour change:** every string sort
  that feeds the simulation uses a plain character-by-character (ordinal) comparison instead of today's default, which
  follows each computer's language setting (nothing in the client pins it: no `InvariantCulture` setting). Today that
  is group ids in `SwarmManager.cs`'s eight `OrderBy(id => id)` loops and the hunting groups at `:652` (which decide
  which predator claims which prey), and player ids at `:975`; the full list comes from a fresh search when the change
  is made (bug ids are integers, `SwarmVisual.cs:26`, so they're unaffected). Group ids are `swarm_` plus eight hex
  characters (`handlers_bugs.go:102`), on which languages agree in practice, but nothing guarantees it. Ordinal removes
  that dependence and is faster; the processing order changes, so it is judged by the behaviour check, after every
  identical change has passed the equivalence check;
- **only if the targets are still missed after these,** different methods, each measured first and judged by the
  behaviour check (for example spreading each group's decisions over a few ticks instead of all of them every tick).
  None is done unless the numbers call for it.

**1.2 — The client's drawing without waste:** smoothing and centipede trails only for bugs on screen, **with each bug's
drawn position computed on demand for the sting check**, which reads drawn positions for every player in range
(`SwarmManager.cs:878-889`, `SwarmVisual.cs:868-876`), so remote players are never stung by frozen bugs (a two-player
test with the stung player off the in-charge computer's screen); no sorting for drawing; trails in a ring buffer, rebuilt
when their bug comes back into view. Then **the owner's feel check** on the 256 village at 4× bugs.

**1.3 — The structural server work, and every simulation input the slice needs:**
- the whole zone alive (Stage 1.3 design below), with the first player's start fixed and bounds guards;
- **the fallen-fruit pile bounded** (decay by expiry time instead of touching every item every tick; chunk-indexed item
  lookups on subscribe; a design cap on standing rotten fruit), since the whole zone and 512 multiply it;
- **the "wrong numbers":** the centipede breeding cooldown (a new or split-off group can't breed until it has eaten),
  the starvation re-arm using the tuned value, split-off groups carrying food home, merges that respect nests;
- **the water rule** (D83: shallow water stops walking bugs, deep water stops all; fliers turn away from deep water
  instead of piling at the shore — today water stops people only, `state.go:579-580`), with a **reachability map per way
  of moving** so groups never aim at food they can't reach across rivers and ridges;
- a save-format version bump for any new saved field;
- then **the whole-zone baseline on the real 256 village's bench copy**: 48 game-days, three seeds — does the June
  tuning hold with today's code? Only structural faults it shows are fixed now; the real tuning is done on the 512
  village (Stage 3), because tuning depends on where the food is.

**1.4 — The snapshot on demand, as a written state machine** (Stage 1.4 design below): any computer whose state matches
the majority can serve it; a timeout asks the next one; a slow safety snapshot (about every 60 s) stays until the
on-demand path has soaked; joiners within a few seconds share one snapshot; the computer in charge hands over if it is
outvoted or silent; built from a main-thread copy, serialised and compressed off the main thread; tested with added
network delay (not just localhost); its build time is a target.

**1.5 — Zones of 512 × 512, the size-aware part** (Stage 1.5 design below): the client learns the zone's size; the
darkness overlay, shore foam, tools and renders follow it; a guard on zone size (the fixed-point maths overflows past
~1,036 cells); a fingerprint of the authored layout in each save, so a changed layout is never loaded over an old save
without an explicit migration. Then the tiled 512 bench zone, the "after" numbers against the targets with two and
four players, and **the owner walks the 512 bench**. *(Crossing spans to 256 neighbours and the village's save
cut-over move to Stage 3's build step: they depend on the new layout.)*

**1.6 — Tuning tools, and the server review as a decision table:**
- running faster than 6× made to work with the client (`sim_batch`, recorded as breaking when the client's clock was
  wrong), and several isolated runs in parallel;
- the automatic scorecard per run and the comparison across seeds; population per region of the zone;
- the noise floor (Stage 1.0) re-measured at the faster speed, and the fast runs checked against a normal-speed run;
- **the server review (D58)** as a table of every server system with its measured cost: per the owner's decisions,
  each remaining server-side piece has to justify its place (D58) and as much as possible runs on the players'
  computers (D83), so the table says for each piece whether it moves, and if it stays, why. Any move becomes its own
  named stage with an estimate; §03 Q1's trial (food identical on two computers; bugs feeding for themselves on the
  players' computers at the target count) informs it.

**Fallback rule:** if 2,000 bugs miss the targets after 1.1–1.2, the starting budget becomes 1,000 while the remaining
cost is chased; Stage 1's check is then met at 1,000 (and the 4,000 row at 2,000), so the fallback lets the work move
on instead of blocking it.

*Stage 1 is done when* (targets mine; the owner confirms), on this PC, in the fixed-count scenario:
- at 2,000 bugs (1,000 under the fallback): the bug simulation per tick p50 ≤ 2 ms and p99 ≤ 4 ms; bug drawing per
  frame p99 ≤ 2 ms; no frame over 16.7 ms attributable to bugs; allocations per tick ≈ 0;
- at 4,000 bugs (2,000 under the fallback): p99 ≤ 6 ms per tick; on the slower-computer emulation at 2,000 bugs (1,000
  under the fallback): p99 ≤ 8 ms;
- the headless client holds the tuning speed at 2,000 bugs (1,000 under the fallback rule) for 48 game-days;
- a join: total bytes ≤ 1 MB and playable within 3 s (chunks, collision and roof maps, the snapshot); the snapshot's
  build ≤ 50 ms on the computer in charge;
- the server tick p99 ≤ 5 ms, autosave ticks included; data per player with four players ≤ 50 KB/s;
- every gate passes.

### Stage 2 — the bug budget (the owner decides)
From Stage 1's numbers: the measured cost per bug on this PC, with an allowance for a slower computer, the join size and
the server's broadcast per player. I bring a recommendation for the village (and the rule for later zones: bugs per area
of habitat), plus the server review's keep-or-move list; the owner sets both. The direction already given: 1,000–2,000
to start, more is better. **This is also where §03 Q1 is answered** (move the rest of each bug's life — feeding,
breeding, nests, eggs — to the players' computers piece by piece, all at once, or after a short trial; recommended: the
trial, which Stage 1.6 runs). Whatever moves, moves **before** the village is tuned, because tuning sets the numbers of
exactly those systems. The budget is the zone's total; **how it splits across species** waits for the village's bug list
(Stage 3, step 2) and comes from the budget sheet (under "How tuning works").

### Stage 3 — the village's bug life, four times bigger, through the whole zone process
**What it delivers:** the village rebuilt at 512 with its bugs: the layout, the bug list, each bug's behaviour and
fight, the bug items (nets, smoker, bug stick, compost bin), the ecosystem tuned over 48 game-days on three seeds, the
pressure runs, and the owner's play and sign-off. The rest of the village's systems are Stage 3b.

The zone process below, step by step, each reviewed in the app. It uses the current village as the base (its buildings
and scenes — `tools/zonegen/scenes/zone_village_21_B.py` and its 11 `scene_*` pieces — its food web and its tuning) and
redesigns it at 512, iterating until the owner is happy. **The layout comes before tuning** (tuning depends on where the
food is). The Parts B–E, D0–D7 and C1–C12 named in this stage are defined in the earlier plan
(`finish-bugs-zones-items.md`). Inside it, in order:
1. **Part B, first, in the app,** in full as the earlier plan lists it (what I bring, what the owner decides, and its
   "I build" list: the process, the schematic layout format, the zone bible template, the zone-craft and author-zone
   fixes, the builder checks for roads, openings, counted placements, ore, game-zoom crops and ecology placement, the
   output gate, self-tested and checked in a fresh session, a fresh grader, and short task cards), with these points
   settled: one zone process (the five existing versions merged into the one below; zone-craft's
   brief, options, lens pass and corrections ledger sit under its layout step); one home for each zone's design (my
   proposal: the GDD zone bible `docs/gdd/zones/<zone>.md`, which absorbs `docs/product/zones/<zone>.md`'s brief and
   as-built notes, with the registry `docs/gdd/data/` feeding the app); zone-craft's pop-up question and on-timeout
   rules replaced by plain-text questions; its gate checks outputs (the brief, the scene list, the options), not
   reading; the authoring guide and the author-zone skill point at the real village builder
   (`zone_village_21_B.py`, not the legacy `zone_village.py`, which must not be run) and at 512. The village is the dry
   run.
2. **The village's bug list** (step 2 of the process): today's 6 species, or the 13 that §04 P5 proposes (adding the
   blue dasher, firefly, honeybee, water strider, crayfish, and on the farm the silk moth and maybe the house cricket);
   the owner signs it off with the map. Each added species needs its behaviour built (Part D) and art (an existing
   sprite, or a placeholder until the art batches), so the list's size sets the slice's size. Each bug is designed on
   the game-first bug sheet (D5: its job, its fight, its farming, what the player sees), after the honest
   audit of what each existing system does (D1), and the principles and feel bars (D3) are agreed once, first. Once the
   list is signed off, the village's entries in §03 and §04 are generated from the registry (Part C).
3. **The combat arena (S3, C11)** before the behaviour work, so the feel of each bug's fight is tried in variants: the
   existing arena zone and its debug spawner (`nakama/data/zones/arena/`, the F8 picker; combat M1.1) grow the spawn
   panel with numbers and stations, observer and fight modes, the peace toggle and the fighter bot, plus the screen
   capture for recordings (S3) and the combat-numbers page per ring and gear tier in the app (C11).
4. **The layout at 512** (process step 4), with what four times the area needs:
   - **generated natural ground:** a builder feature that places terrain, plant cover and food sources by rule, at set
     densities, inside habitat areas the layout draws; the landmarks stay crafted scenes. CLAUDE.md's hard rule forbids
     "a monolithic prop-scatter `zone_*.py`". This is a different thing (a tested builder feature, driven by drawn
     habitats, each habitat checked against its food targets), but it touches that rule, so **the owner is asked to
     amend the rule's wording before it is built**;
   - **spawn areas** drawn from the same habitats, so where bugs start matches where their food is;
   - **getting around:** paths and corridors between areas, landmarks seen from a distance, and a navigation aid (a
     map or signposts; a design question for the owner with §01);
   - the natural barriers and the crossings to each neighbour (D83), placed along each edge's neighbour spans (Stage
     1.5 design).
5. **Build** (process step 5), including what depends on the layout: the crossings to the 256 neighbours (spans, the
   crossing controller, the entry strip; walked for real), the save cut-over (the layout fingerprint and a migration),
   the spawn-apart late-join gate re-pointed at 512 coordinates, and the memory of a 512 zone measured as it would be
   on a player's computer under Host & Play.
6. **The behaviour and combat work** for the village's bugs (Part D; the village's combat set C1–C5, C7, C9, C11),
   designed alongside steps 4–5 and tried in the arena, built in the build step and tuned with the ecosystem. It
   starts by correcting the stale combat docs (C12), each re-found first (the timers added on 2026-10-04 moved the
   `SwarmManager.cs` lines; for example the lunge comment near line 803 says the server owns the surge, while
   `architecture_combat.md` says a per-bug brain on the players' computers does; the code decides which is right).
   **Time of day and rain enter the bugs' lives** with it (D4.3, after §18; the village has night hunters), because
   they change the cycles that tuning sets; so do the richer-cycle pieces of D0b the village needs (colonies reacting
   to their own state, natural crowding limits), each compared against the village's charts one at a time.
7. **Its bug items** (nets, smoker, bug stick, compost bin; Part E).
8. **Tune, pressure, play** (process steps 6–8), with the population director's rain lever brought in line with
   weather being a lever of last resort (D7).
9. **The 512 village goes live,** replacing today's unfinished village and its save (wiping it is fine, owner
   2026-10-06; the automatic start-up backups, D73, keep a copy anyway).
   With it, new players start in the rebuilt village (D19; §01 "One village"; the dev menu's "Normal" world still
   opens the old `village_21`, `WorldMenu.cs:43,77`).

### Stage 3b — the rest of the village to final quality
After the bug-life sign-off, the village's share of ROADMAP Phase 2's systems, each through its own design, review and
build: catching gear and bug storage; fishing and the fisherman (D51, with §13); the ecology stations and the Ecology
tab; the tutorials; private plots and City Hall; cooking and potion basics; armour and stats with the progression
backbone. Their order is set with the owner when Stage 3 ends; the GDD sections each needs come first. Systems that are
not the village's alone (the progression backbone, armour) are designed once for the whole game here.

### Stage 4 — the kit, then the next zones
What the village taught becomes the kit (the bench copy, the run tools, the checklists, the bands). Then the zones
around the village (the bees and the others; the ants later), then the rest ring by ring (ROADMAP Phases 2 and 3), each
through the same process, each at 512; the order is chosen with the owner when the village is done. **Real bug
transfer between zones** (D4.4, the roadmap's swarm-level migration) is built before the first zone whose bugs cross a
border (the ants' colonies need it).

### Alongside, all the way: the design document
In the order the village needs them: §01 world (zone size and barriers), §03 bestiary and §04 ecology (with the bands),
§05 bug farming, §07 combat, §18 time and weather, §02 progression; then the rest. Section by section, in the app.
With them, the corrections the plans survey found: D83's water answer written into §01 and §04; §03's opening paragraph
no longer saying every danger warns first; the already-decided items cleared out of the §02 and §18 stubs; this
section order written into the GDD README. Art follows the ROADMAP's art row (the art track; this plan doesn't change
it).

## The zone process (every zone, the same steps; each reviewed in the app)
*One sign-off per zone covers the map and the bug list with its design (D83); the other steps are reviews, and the
owner's play is the last word. Behaviour comes before numbers (overview P10, D57).*
1. **Purpose and place.** What the zone is for, its ring and danger, its neighbours, the natural barriers to zones of
   different difficulty (rivers with bridges and shallows, ridges), where the crossings are.
2. **The bug list, with jobs.** Each bug's job for the player (livestock, danger, prey, a material), its place in the
   food web, the moment only it creates. From the registry.
3. **The ecosystem design.** A food-web diagram, and for each species:
   - its food, and where that food is (its habitat);
   - how it breeds (nest, brood, eggs per trip), what eats it, what it eats;
   - its share of the zone's bug budget, its target range and its character (a boom-and-bust prey, a predator that lags
     it, a steady scavenger);
   - what the player sees.
   *The zone's sign-off: the map (step 1), the bug list (step 2) and this design, together.*
4. **The layout.** Landmarks and habitats placed to serve the food web, through the zone-craft process (brief, landmark
   scenes, options, lens pass). Every habitat holds its species' food and is reachable. At 512 the natural ground is
   generated from rules (terrain, plant cover, food sources at set densities per habitat) and the landmarks are crafted
   scenes, so four times the area doesn't mean four times the hand placement.
5. **Build.** Zone files and data; the checks: barriers and crossings line up, every habitat reachable, food-source
   counts match the design, north-up render, save regenerated and verified.
6. **Tune** (below).
7. **Pressure.** Test players that hunt, farm and hoard (a new mode of the headless test player, built once in the village
   slice and reused): how fast collapses come, what warns first, how things come back. Nothing is tuned to stop
   players; this informs the Ecologist's warnings and quests.
8. **The owner plays it and signs it off.**

## How tuning works
- **What "tuned" means:** without players, every species keeps itself going (top-ups rare, after a crash only) and stays
  in the range set in step 3 of the zone process, with the character set there, over 48 game-days. Cycles are good; a
  flat line pinned at a cap is not; a crash is fine if it comes back. Players disrupting it is fine.
- **The rig:** the zone's bench copy (never the real save), the whole zone alive (Stage 1), the real game client in charge
  with its clock at the zone's speed, 48 game-days per run at the fastest speed the client keeps up with (6× today;
  20–30× after Stage 1 if proven: the server's `call_rate` 60 plus `sim_batch`, the client's `-timescale` to match), a fixed seed,
  two more seeds to confirm a result, and a check at normal speed now and then (a shorter run) that the fast runs tell
  the truth.
- **Reading a run** (charts in the app): population against the range; births by source (keeping itself going, or
  living on top-ups?); deaths by cause (what limits it); food against population; the cost per tick.
- **Order:** structural breaks first (anything that can't work: food out of reach, instant breeding, a frozen habitat;
  for the village, what's left of the earlier plan's D0b list after Stage 1.3 fixed the others: carcasses lasting 60 s
  and the firefly with no food), then from the bottom of the food web up: food supply → plant-eaters → predators →
  scavengers; each consumer and its food brought into range on their own before predators are added on top.
- **The `ecology-tuning` skill's hard rules hold:** one run at a time; a metric still drifting at the end of a run means
  a longer run, not a tuning change; caps are a backstop, never the bound; predators are placed near (not on) prey;
  every lever listed before one is chosen; one distinct name per run.
- **Levers per species:** food (amount, regrowth, placement), breeding (eggs per trip, brood size, hatch time,
  cooldowns), death (lifespan, starvation time), predation (hunting speed, strike cooldown, kills per strike), space
  (habitat size and placement). Caps and top-ups are the safety net, not the tuning.
- **Method:** one change per run, logged in `docs/product/ecology/ecology_tuning_log.md` with its chart and what it
  showed (the `ecology-tuning` skill, updated with today's facts). The owner sees each batch in the app.
- **Affordable runs (to be proven in Stage 1):** after Stage 1 the client simulates far faster than real time, so the rig
  should run at 20–30× (raising the zone's speed and the client's clock together, as today's 6× does) instead of 6×: a
  48-game-day run in about 25 minutes. Caution: the tuning skill records `sim_batch: 2` breaking the client (dropping to
  0 bugs, `SKILL.md:71-73`), measured when the client in fact ran at a sixth of the zone's pace (the clock fault fixed
  2026-10-04), so it is re-tested, not assumed; if it still breaks, the fix for that comes in Stage 1, or runs stay at 6×.
  Either way, checked against a normal-speed run that the fast runs tell the truth.
- **An automatic scorecard per run:** for each species, the share of time in its range, the number of cycles, the share
  of births that are top-ups, crashes and recoveries, and what limited it (deaths by cause). The owner reviews a verdict
  table with the charts, not raw logs.
- **Setting the ranges: a budget sheet per zone, before any run.** For each species: the food its habitats hold (from
  the layout's counts) and how fast it regrows, divided by what one bug eats, gives how many it can carry; for a
  predator, how many kills make one birth. The predicted level, give or take about half to double, is the first range;
  the zone's bug budget caps the total, with prey the most and predators the fewest. The owner sees the ranges in plain
  terms (about how many of each you'd see around a patch of their habitat), not as model numbers. The June figures are
  a sanity check only: they were tuned with performance first, on a smaller living area.
- **Runs per zone, kept within reach:** short screening runs (a few game-days, one seed) throw out bad settings first;
  survivors get the full 48 days on three seeds; differences smaller than the noise floor (Stage 1.6) don't count;
  populations are read per region too, so a species thriving in one corner and gone elsewhere shows; one 150-game-day
  run before the sign-off catches slow drifts. Several runs at once only on separate, isolated server stacks, once
  Stage 1.6 proves they don't disturb each other (the skill's one-run rule exists because `run_config` restarts the one
  shared server). Each zone gets a run budget, and the runs actually used are recorded.
- **The village's starting point:** the June 19 bake (what ships), scaled to the new zone's budget and habitats, then
  adjusted for what changed since (predation decided on the players' computers, centipede packs, a populated start,
  breeding from brood).

## Testing like real
- **Every change:** Go tests (Docker), the determinism replay, both late-join gate halves (players together and apart),
  and for the performance changes the behaviour check, plus the equivalence check (old and new builds side by side)
  for those meant to give identical results.
- **Every measurement:** the real client and server, the whole zone, one run at a time on a quiet machine, the numbers
  saved with the run.
- **Frame time with drawing:** the real player build run windowed on this PC (not headless) at the target bug counts.
- **Several players:** two and four players on one machine, one late-joining, one crossing a zone edge.
- **The owner's playtests** at the end of Stage 1 (feel, no stutter) and of Stage 3.

## How we stay on track
- **One active plan** (this one). New ideas go into the BACKLOG, or into this plan with the owner's yes, never into a new
  plan of their own.
- **Every session starts** by reading this plan's PROGRESS and its "Now" line, and ends by updating them, committing,
  pushing and merging `main`.
- **A stage isn't left** until its check passes or the owner moves it.
- **Reviews come in batches** in the app, when a coherent set is ready.
- **Limits on work in progress:** at most two things being designed, two being built, and two waiting on the owner.
- **Every commit names its stage** (for example "S1.1: food lookup per group"), so the history reads as the plan.
- **The owner can always see where things stand:** the plan's readable page (Stage 0) is republished at the end of
  each stage, with its "Now" line and PROGRESS current, so nothing needs reading in git or the terminal.
- **The earlier plan's "How we work" rules still hold:** the two definitions of done (designed; built); a "what the
  player sees" column for every behaviour; every rule cites a dated owner decision or is labelled my proposal; at most
  two helpers reading the drive at once; the repo is the only save place.
- **Each stage gets a size estimate when it starts and its actual size when it ends**, both in PROGRESS; later zones
  are planned from the village's real figures.
- **Fallbacks are written in advance** (1,000 bugs if 2,000 miss; the snapshot's fallbacks; runs stay at 6× if faster
  speeds fail), so a setback changes a number, not the plan.
- **A new finding mid-stage** (like 2026-10-04's half-alive village) goes into PROGRESS and to the owner in plain words
  with a proposed fix; the plan changes only with their yes.
- **Every earlier plan item has a place** (the register below); anything not in it is either done or in the BACKLOG.

## Where every earlier plan item went (the register)
| Earlier item (the earlier plan's unless noted) | Where it is now |
|---|---|
| Part A, the review app | built and rehearsed; the publish is Stage 0, step 4 |
| `finishing-the-game.md` (2026-10-04 morning) | merged into this plan; archived (Stage 0, step 1) |
| Part B, the zone-design scaffolding | Stage 3, step 1 |
| Part C, which bugs live where | the village: Stage 3, step 2; other zones: Stage 4, each with its zone |
| D0 the behaviour model, D0c fight design | Stage 3, step 6 for the village's bugs; later families in Stage 4 |
| D0b the wrong numbers | Stage 1.3 (nests alive with the whole zone, the centipede cooldown, the starvation re-arm, split-off groups carrying food, merges and nests); carcass time and the firefly's food in tuning's first pass |
| D0b richer cycles | newcomers from neighbours: Stage 4 (needs bug transfer, D4.4); time and weather, colonies reacting to their state, crowding limits: Stage 3, step 6, with the tuning; player kills and catches recorded: done (`05e14624`); colony health shown: Stage 3b (the Ecology tab) |
| D1 the audit, D3 principles and feel bars, D5 the bug sheet | Stage 3, step 2 |
| D2 the design sections | Alongside (the GDD order) |
| D4.1–D4.2 what moves to players' computers; the server review | Stage 1.6 and Stage 2 |
| D4.3 time and rain in the simulation | Stage 3, step 6 |
| D4.4 bug transfer between zones | Stage 4, before the first zone whose bugs cross a border |
| D6 the design loop; D7 ecosystems per zone | how Stage 3's steps are done; the zone process, steps 3 and 6 |
| C1–C5, C7, C9, C11 (the village's combat set) | Stage 3, steps 3 and 6 |
| C6 lasting effects; the combat numbers | §07 alongside; built with armour and stats (Stage 3b) |
| C8 bows and ranged combat | the weapons batch in the app (items track), after §07; built in Stage 3b or later, with its own build plan |
| C10 night and placement | the village's night hunters in Stage 3, step 6; other zones in Stage 4 |
| C12 the stale combat docs | Stage 3, step 6 (first thing in the combat work) |
| S1 the scaling study | Stage 1 (with the whole zone and the rig) |
| S2 the pressure bots | the zone process, step 7; built once in Stage 3 |
| S3 the arena and capture | Stage 3, step 3 |
| The water rule (D83) | Stage 1.3 |
| Part E: the weapons batch, the UV light, the 28 cut-recommended items | the items track in the app, alongside, at the owner's pace |
| Part E: the village's bug items | Stage 3, step 7 |
| Part E: decorations | after §15, with private plots (Stage 3b) |
| The sprite sizing rule (BACKLOG:57) | the art track; not a layout dependency (buildings and props are sized by their data; the rule covers items, tools, drops, effects, grass tufts and bugs) |
| Merging the two ant zones; the colony across two zones | Stage 4, decided once bug transfer is built |
| Grass phases 2–5, swing phase 6, repo-health P7 | paused; on the roadmap, picked up in their turn |
| The GDD corrections the plans survey found (D83 water in §01/§04, §03's opening, the §02/§18 stubs, the section order) | Alongside, with the GDD work |
| New players starting in the rebuilt village (D19) | Stage 3, step 9, when the 512 village goes live |
| The art-timing mismatch (ROADMAP:28 against :61-62) | a BACKLOG line for the art track (Stage 0, step 2) |
| Part C: §03/§04's lists generated from the registry after sign-off | the village: Stage 3, step 2; other zones: Stage 4 |
| D7: the director's rain lever as a last resort | Stage 3, step 8, with the tuning |
| S3: screen capture for recordings; C11: the combat-numbers page | Stage 3, step 3 |
| "How we work" (definitions of done, the "what the player sees" column, citing decisions) | still in force ("How we stay on track") |

## If this were my game: how certain I am
| Part | Certainty | Why, and what would change it |
|---|---|---|
| The overall order | 90 | It is what I would do: make the foundation sound and measured, then design and tune one zone end to end, then reuse what it taught |
| Fix the waste before setting the bug budget or tuning | 95 | Measured: ~23 of 27 ms per tick avoidable; tuning a half-alive, slow world wastes the tuning |
| The whole zone on the server | 90 | An ecosystem game must simulate its whole zone; the clients already do; the server cost measured small. Below 95 because it disturbs the first player's start (latent bug 3), fixed in the same change and proven by both gate halves |
| 1,000–2,000 bugs per zone after the fixes | 85 | The movement itself costs ~0.8 µs per bug, measured. Not yet measured: drawing with 2,000 bugs on screen, the sting check's on-demand positions, a slower computer. The fallback (1,000) is written in |
| The checks prove the fixes keep every behaviour | 80 | The behaviour check uses counters the game mostly already logs, judged against a measured noise floor; the equivalence check (needed because the replay can't see these parts) is new here, so it is built first and must catch a planted difference before it is trusted |
| The snapshot on demand, small | 80 | One reader on the server; fallbacks exist today. The risk is timing under real network delay, hence the delaying proxy and the safety snapshot kept until it has soaked |
| Zones 4× bigger (512) | 75 | Right for a bigger world and the server's original design size (`zone.go:85`); the code list is known. The real risk is making four times the area interesting and easy to get around (generated ground under drawn habitats, crafted landmarks, a navigation aid), which needs the owner's rule amendment and is proven on the village first |
| The zone process and the tuning method | 75 | The method worked in June; now with a budget sheet, a scorecard and a noise floor. Held down by run throughput (faster speeds unproven) and a coupled system |
| How long Stage 1 → Stage 3's tuning takes | 60 | A schedule risk, not a design one: §03 Q1 (if feeding and breeding move to the players' computers all at once, that is the largest single job, and it comes before tuning) and the 512 layout work |

Judged the `certainty-assessment` way (by the weakest load-bearing row, never an average): **if this were my game I
would do this, in this order (90); my confidence that the design is right as written is 75**, held down by the 512
layout work and tuning throughput. Both are tried early (the noise floor in Stage 1.0, the 512 bench in Stage 1.5,
the run speeds in Stage 1.6) before the village depends on them. Verification is pending, as it should be at plan time (the gates are
under Verification).

## Stage 1.0 design — the measuring and checking tools (checked in code 2026-10-06)
**What exists today** (each read in the code):
- **Client timers:** `PerfProfiler` keeps only running sums per part (`Util/PerfProfiler.cs:28-87`), updating a
  string-keyed table each time a part ends, so there are no percentiles, and the ~8.7 million food-lookup updates of the
  4× run add cost of their own. `client_perf.csv`'s `sim_ms` is `Sim.SwarmTick` only (`HeadlessSyncTest.cs:220`), not
  the whole tick. Nothing measures allocations (only the gen-0 collection count and the heap size). The drawing code
  (`Render.*`) runs in the headless player too; only Unity's own rendering doesn't.
- **The test build** (`Assets/Editor/SyncTestBuild.cs`) is a normal windowed Development player; "headless" comes only
  from `-batchmode -nographics`. There is no release build, camera path, frame-time log, or way to steer the player
  (`PlayerController` reads `Input.GetAxisRaw` directly, `PlayerController.cs:237-238`).
- **The sync test's trace keeps only the last 500 ticks** (`Debug/TickTraceBuffer.cs:17`), and every launch script uses
  one hard-coded build path.
- **Server logs:** `ECOSTATS`, `PREDLOG` and `RESSTATS` once per game-day; nothing counts food eaten, eggs, hatching,
  trips home or nest defence, and merges and splits are logged without species. The `static` zone flag stops spawning,
  merges, splits, the director and predator breeding (`match.go:2068`, `:2248`, `:2366`; `ecology_director.go:35`;
  `predation.go:870`), not breeding at food, hatching, nests, ageing or starvation.
- **Reports:** `RunPredationStrikes` reads only simulated positions, the collision map and the hunting list, with a
  report-only throttle (`SwarmManager.cs:647-731`); `RunCorpseConsumes` drains a temporary flag that isn't simulated
  state (`SwarmVisual.cs:844-857`, `BugAgent.cs:61`). Both can run on any computer without changing the simulation.
  Stings read drawn positions (`SwarmManager.cs:781` on), which depend on each computer's frames, so they can't be
  compared exactly; the behaviour check and Stage 1.2's two-player sting test cover them.

**1.0a — server** (test-zone only; real zones unchanged). *Revised after the cold review of 2026-10-06, each point
checked in the code.*
- **A clean start for every run.** A bench zone keeps no bugs or ground items between runs, but its save still holds
  and restores nests (with their resident pointing at a bug group that no longer exists), trees, food plants, broods
  and the clock (`world_save.go:155-196`), and a restored nest is never restaffed (`registerNestAt` returns early,
  `nests.go:94-96`). So every 1.0 script wipes the bench zone's save before a run (stop, delete, start), through one
  shared helper, as `run_config.py` already does (`run_config.py:162-183`).
- **`hold_population`** (a zone flag, off by default). When on: no births after the start, no natural deaths, no
  top-ups or culls, while merges and splits keep running (so their cost is measured):
  - `reproduceSwarm` skips only the birth (`layIntoBrood` / `growSwarm`) and keeps the meter, satiation and cooldown
    resets and the food cost (`match.go:91-96`, `:115-119`); skipping the whole function would leave the bug group
    breeding, and draining its plant, every tick (`match.go:1476-1498`);
  - `depositNestEgg` (`brood.go:199`), `hatchFromBrood` (`brood.go:302`), re-hatching, recovery and founding
    (`nests.go:146`, `:292`), `processNaturalDeath` (`match.go:2173`), `processStarvation` (`match.go:2221`),
    continuous spawning (`match.go:2067`) and the director (`ecology_director.go:35`) do nothing.
  - Nests are still staffed when their chunk first loads (until Stage 1.3 loads the whole zone), which is part of the
    starting count: in fixed-count runs the player stands still, so this happens in the first moments; a wandering
    player staffs nests as it reaches them, recorded as nest births.
  - Predation and player actions still remove bugs, so hunting stays real and the count drifts down slowly; each
    window records the actual count, and costs are per bug.
- **`BEHAVSTATS day= sp= …`**, once per species per game-day beside `ECOSTATS`, from the same never-hashed accumulator
  (`ecology_stats.go`), each counted where the server applies it: feeding ticks and breeding ticks at a food source
  (`match.go:1456-1479`); eggs laid (`brood.go:63`, `:202`); trips home completed and abandoned (`predation.go:196-207`);
  nest defences set off (the change into "defending", `predation.go:149`, `nests.go:673`); merges (`match.go:2300-2336`)
  and splits (`match.go:2471`); hits on players by bugs (`applyBugAttackToPlayer` returning true,
  `handlers_player.go:27-128`). Hatchings are already `ECOSTATS`' `b_brood`. Lines appear only at a day's end, so
  behaviour runs last whole game-days.
- **Go tests:** the flag stops every birth path and both natural death paths, keeps the resets and the food cost, and
  leaves merges, splits, predation and nest staffing on chunk load working; each counter counts its event once.

**1.0b — client** (one test build; everything behind a test flag, the game's own behaviour unchanged):
- **Cost recorder:** a stopwatch around each whole tick (outside the per-part timers) and a per-frame record (frame
  time, ticks run that frame, bug-drawing time), into arrays made once, so recording allocates nothing; per-window
  p50 / p99 / max and a whole-run histogram, written to `client_cost.csv` and `client_cost_summary.json`.
  `-perfmode clean|breakdown`: clean turns the per-part timers off.
- **Allocations:** `GC.GetAllocatedBytesForCurrentThread()` is tried first, but the client's Mono uses the Boehm
  collector, which likely reports 0; then Unity's `ProfilerRecorder` ("GC Allocated In Frame"), which works in
  Development builds only and per frame, so per-tick allocation is estimated from frames with one tick against frames
  with none. Allocations come from the Development build; timings judged against the targets come from the release
  build (where the Unity profiler markers are compiled out).
- **`client_perf.csv`** gains the whole tick (`Sim.Tick`) beside today's `sim_ms`; the snapshot build gets a timer and its
  size is recorded.
- **Behaviour tally** (`-behaviour`): after each tick, per species, bug-ticks in total and while hunting
  (`HuntTargetBugId`), landed, feeding on a corpse (`FeedUntilTick`), fleeing a player, attacking, curious and lunging
  (`CurrentBehavior`, `SurgePhase`); corpse feeds and lunges started (both have start-tick timestamps, `BugAgent.cs:63`,
  `:455-456`); reports made. Read-only over the bugs; written per window to `client_behaviour.csv`; never on in cost
  runs. (Prey fleeing a predator is decided on the server and counted there.)
- **Shadow reports** (`-shadowreports`): computers that aren't in charge run the predation-strike and corpse-consume
  passes in log-only mode, under the same "live" condition as the one in charge (`SwarmManager.cs:611`); every computer
  logs `tick,kind,ids` for each report it sends or would send. Not used in runs where the one in charge leaves.
  *Found in the first run (2026-10-06):* each computer paces a predator's strike reports with a local, report-only
  throttle that starts empty on a late joiner, so the same strikes come out at shifted ticks for as long as the
  predator keeps striking. So with the report log on, detection also runs while throttled and logs `detect` lines
  (what each predator could strike, from the simulated state alone); the equivalence check compares `detect` and
  `corpse`, not the paced sends. With the log off, the code path is exactly as before.
- **Fingerprint log** (`-hashlog`): every tick, the game's own state check, a test-only check over each bug's full
  record (the snapshot record: also landing, random-number state, movement intent, alert state, behaviour), and the bug
  count, for the whole run; resyncs and replays are marked in the log.
- **Route** (`-route <file>`): `PlayerController` gains a test-only scripted input, read before the UI-focus check
  (`PlayerController.cs:229-234`) and used only when set; a follower steers to each waypoint in turn, skips one it
  can't reach in 10 game-seconds, and after a faint (which sends the player back to spawn) heads for the nearest
  unvisited waypoint. `-vsyncoff` turns vSync off with no frame cap. Waypoints come from
  `tools/ecology/make_route.py <zone>`: the busiest clusters of food sources, each leg pathed on the player-blocking grid
  (water, walls, blocking objects; the village has 4,643 water cells) with a cell of clearance, at least 6 cells from an
  edge. Headless it is the wanderer; windowed, the camera follows it, so it is the tour. (Routes on 512 zones wait for
  Stage 1.5's crossing change: `CrossZoneController` stops the player at 255.)
- **`SyncTestBuild.BuildRelease`** → `Build/Release/` (no Development flag).

**1.0c — scripts:**
- **`PLAYER_A` / `PLAYER_B`** (build paths) in `run_sync_latejoin.sh` and the ecology launcher, with per-client output
  names so runs don't collide; every script wipes the bench zone's save before a run.
- **`tools/netcode/equiv_check.py`:** compares two fingerprint logs over every tick both computers were live (the first
  value kept for a tick seen twice), and the shadow reports from each computer's first live tick plus a warm-up as long
  as the longest strike cooldown; names the first difference. A run with a resync, a collision-map or replay timeout,
  or a reconstruction tripwire is inconclusive, never a pass. It applies only to builds with the same snapshot and
  message formats. Unit-tested with planted faults (like `test_sync_diff.py`).
- **`tools/ecology/behaviour_check.py`:** reads `client_behaviour.csv`, `BEHAVSTATS`, `ECOSTATS` and `PREDLOG`; rates per
  species per 1,000 bug-ticks and per bug-day; the baseline is the noise-floor seeds; a metric is flagged when the new
  mean falls outside the baseline mean ± 3 standard deviations, or when it goes to zero from nonzero (or the reverse);
  unit-tested.
- **`scaling_study.py`** reads the cost files and reports percentiles, frames over 16.7 ms, allocations and the snapshot
  timing; options for the perf mode, a windowed run and a route.
- **`tools/run_players.sh N`:** two to four test players, staggered, with roles (in charge, wanderers), an optional
  authority leave and reconnect, and one combined report.
- **`tools/run_gates.sh`:** Go tests, every sim-determinism mode, both late-join halves on the bench (wiped first), and
  the equivalence check when two builds are given; a pass/fail table and real exit codes (no pipes that hide them).

**1.0d — proving the checks:**
- The same build copied twice: the equivalence check says IDENTICAL both ways round, over a window with real activity
  (merges, hunts, feeding, a late join), counted from the tally so a quiet window can't pass.
- A build with a planted one-line change (the food-lookup radius 2.5 → 2.6): caught by the equivalence check, and by the
  behaviour check over the seeds.
- Five seeds of the current build: the noise floor for every metric, recorded.
- A fixed-count run holds its count: no births after the start-up moments, no ageing or starvation deaths
  (`ECOSTATS`).
- The test flags change nothing: in one run, the player in charge with every test flag on and a second player with
  only `-shadowreports` and `-hashlog` (same build): identical fingerprints and identical detections. (What the one in
  charge sends is unchanged by construction: the flags add logging and detection while throttled, never a send.)

**1.0e — the "before" numbers,** under `docs/product/investigations/stage1-before-<date>/` with a plain write-up: natural
runs at 1× and 4× (6× speed; cost and behaviour); fixed counts of 1,000 / 2,000 / 4,000 at normal speed, clean and
breakdown, on the release build; the windowed tour at 2,000 and 4,000; two players (one wandering), the authority
leaving, a reconnect; the slower computer.

## Stage 1.3 design — the whole zone on the server (checked in code 2026-10-04)
- **One setup helper** `initChunkRegistries` (the five scans in today's order: fruit trees, nests, host plants, forage
  pools, stations) used by subscribe (`handlers_world.go:38-43`), restore (`world_save.go:422-426`), the old-format
  import (`zone_persist.go:186-190`) and the new `loadWholeZone`. Every scan already skips what's registered, so running
  twice on a chunk is harmless.
- **`loadWholeZone`** walks the grid (Width÷32 × Height÷32) in a fixed order, skips chunks already loaded (which keeps
  restored edits), loads the rest (grass if a file is missing), and runs the setup. **It runs in MatchInit after the
  restore/import and after `spawnInitialSwarms` / `seedInitialCarrion`**: earlier, restore would skip edited chunks
  (`world_save.go:402`) and overwrite the new registries. The start-up spawn's reset of the group index
  (`match.go:1825`) keeps existing entries, so nest groups aren't dropped from the population count (an existing bug for
  test zones too).
- **The first player's start:** setup at MatchInit emits events (windfall fruit, nest groups) that today's empty-zone
  path clears while the event counter has moved on, and the first player is told there are no earlier events
  (`match.go:629`) — the roadmap's latent bug 3, which this change would trigger. Fix: reset the zone's sync state at the
  end of MatchInit (as the last player's leaving does, `match.go:786-800`), and give the first player the zone's food
  list through the existing hydrate path (restored food is missing from clients today too: `HydrateFood` is never
  called). This is a sync change: the `frontier-sync` recipe, both late-join gate halves.
- **Guards:** cells outside the zone are always walls (a bounds check in `isBlockedImpl` and the player check); chunk
  requests outside the zone are refused on the server and never made by the client (`TilemapManager.cs:214-222` isn't
  clamped today, which creates walkable "phantom" grass chunks).
- **Costs, measured after:** fruit trees decode their cell every tick (`handlers_farming.go:998`) → read from the
  chunk's cached anchor list instead; the collision and roof maps sent on each join re-read untouched chunks from disk
  (`state.go:802-811`, ~800 ms per join at 512 estimated) → served from memory once the whole zone is loaded; saves grow
  (the village's is 226 KB, mostly fallen fruit; up to ~1 MB a minute at 512 estimated) → measured, and trimmed if
  needed; memory ~50 MB per visited 512 zone (chunks are never unloaded) → fine on a hosted server, but under Host &
  Play the server runs on a player's computer, so a zone left empty for a while is saved and unloaded (added to the
  hosting track, measured in Stage 3's build step).
- **Empty zones stay frozen** (already built: `MatchLoop` returns early with no players, `match.go:869-880`); the
  catch-up on arrival stays on the roadmap and now has the whole zone it needs.

## Stage 1.4 design — the snapshot on demand (checked in code 2026-10-04)
**Today:** the computer in charge uploads a full snapshot every 10 s (`SnapshotInterval`, `SwarmManager.cs:117`) because
the server keeps only 200 ticks of events (`state.go:1018`) and a joiner needs "snapshot + every event since". The only
reader is the late-join send, which the resync request reuses (`handleSnapshotRequest`, `match.go:2832`); with no
snapshot, a joiner builds the bugs from the shared seed (`buildSwarmSeedBaseline`, `match.go:2894`, used at `:3081`).
Every ~30 s the server asks every member for its state check at one settled tick and resyncs any minority
(`checkDriftSampling`, `match.go:3236`), so it knows which computers agree. Charge moves only when its holder leaves (`match.go:779-813`).

**The server's side, per zone, as a written state machine:**
- *Idle* (a stored snapshot may exist, with its tick). A join or a resync request: if the stored snapshot is still
  covered by the event log, it is served at once with the events since (today's path). Otherwise → *Waiting*.
- *Waiting:* the player goes on the waiting list and a snapshot request (a new message with a request id) goes to the
  supplier: the computer in charge, unless it disagreed in the last drift round; then a member that agreed. Joiners who
  arrive meanwhile join the list, so one snapshot serves them all.
- The answer with the matching id: every waiting player gets it with the events since its tick; it is stored → *Idle*.
- No answer in time (about 2 s; measured), or the supplier leaves: the next agreeing member is asked once; then the
  stored safety snapshot if the log still covers it; else today's seed path, and the drift round pulls the joiner into
  step.

**The safety snapshot** stays, every ~60 s instead of 10, with the event log kept long enough to cover it (its memory
measured), until the on-demand path has passed the two-hour soak and the join tests; then it is kept or dropped on
those numbers.

**The supplier's side:** the request is handled at a tick boundary: a copy of the state on the main thread into plain
reused arrays (target ≤ 2 ms at 2,000 bugs), then packing and compression on a worker thread while the game runs on,
then the upload. The snapshot names the tick it describes.

**Packed and small:** a format version first; each group's fields once; each bug's fields as fixed-size numbers (no
names, no diagnostic fields, the lunge block only for bugs mid-lunge); then compressed. The server passes the bugs
through untouched (`json.RawMessage` today), so only the clients change; a client refuses a version it doesn't know
rather than misreading it. The 8 MB message limit (`nakama/data/local.yml:16`, the client's read cap in
`NetworkManager.cs`) stays as a ceiling.

**Charge follows capacity:** besides leaving, the server hands charge to an agreeing member when the computer in charge
disagrees in a drift round, or falls behind the zone's tick by more than a set amount (a lag figure added to what it
already reports), so a computer that can't keep up stops being the one the zone depends on.

**Tested:** both late-join gate halves; joins during merges, splits, hunts and lunges; two joiners within a second (one
snapshot); the supplier leaving while asked; each fallback forced; the deliberate-drift resync; added network delay
and loss through a delaying proxy (localhost hides timing faults); the two-hour soak with joins along the way.
**Targets:** no snapshot traffic between joins apart from the safety one; a join under 300 KB at 2,000 bugs; served
within 1 s locally; the build ≤ 50 ms.

## Stage 1.5 design — zones of 512 × 512 (checked in code 2026-10-04)
*Built in two parts: the size-aware pieces, the size guard and the layout fingerprint in Stage 1.5 (proven on the tiled
512 bench); the neighbour spans, the crossing and the village's save cut-over in Stage 3's build step, once the new
layout fixes where its edges and crossings are.*
**Already size-free:** the server reads width and height from `zone.json` (`zone.go:91-92`, `:227-232`) and its
original design was 512 (`zone.go:85`); the collision and roof maps are sparse lists (~200 KB for the village at 512);
swarm positions are per chunk; the bug simulation's fixed-point maths has ~4× headroom at 512 (`FixedPoint.cs:153-158`;
overflow only near 1,036 cells); the zone builder, the test-zone maker and the app's map encoder follow width/height.
**What changes:**
- **The client learns the zone's size** (today nothing tells it: `WorldInitMessage`, `messages.go:842-846`; the
  `world_enter` reply, `rpc/world.go:88-91`): width, height and each neighbour's span along the edge.
- **Neighbours as spans on an edge** (one grid slot per zone stays; each neighbour gets an offset along the shared
  edge; the rest of that edge is a natural barrier until the neighbour is rebuilt at 512, which is what the barrier rule
  of 2026-10-03 wants anyway). `zone_links_test.go:92-97` (which requires equal edge lengths) checks spans instead.
- **Crossing:** `CrossZoneController.cs` uses the zone's real size (today `ZoneMax = 255` and a soft wall at 254.5 would
  trap the player in the south-west quarter of a 512 village), maps the along-edge position through the span, and the
  server lands the player on the nearest walkable cell of the entry strip (the roadmap's "blocked zone entry" item).
  Tested by walking over a real edge between a 512 and a 256 test zone (today's crossing test calls the crossing code
  directly, so nothing tests the edge trigger itself).
- **Darkness overlay** (`DarknessOverlay.cs:21`) and **shore foam** (`TilemapManager.cs:31`, `WaterAnimated.shader:28`)
  sized from the zone; the overlay uploads only what changed.
- **Tools:** preview renders at 512 need a lower scale or tiles (`make_scene.py:169`: 1–2.4 GB at today's scales);
  `view_world.py` defaults; the app's map fallback; `make_bench_zone.py --tile 2`.
- **Guards and saves:** the server refuses a zone larger than the fixed-point maths allows (well under ~1,036 cells);
  each save records a fingerprint of the authored layout it was made on, and a save whose fingerprint doesn't match is
  never loaded over a changed layout without an explicit migration (the save format's version is bumped for it).
- **Docs the change touches:** `architecture_world.md`, `ARCHITECTURE.md`, `docs/gdd/01_world.md` (zone size),
  `overview.md`, the authoring README.

## Stage 1 design notes (how each fix keeps every behaviour)
- **Sorted lists.** A group's bugs live in `SwarmVisual._bugs` (a dictionary; every change is in `SwarmVisual.cs` at
  the add, remove, insert, clear and snapshot paths, lines 294, 648, 675, 688, 703, 717, 1017). They become a list kept
  in bug-id order, which every reader walks directly. The zone's groups (`SwarmManager._swarms`) are walked through a
  sorted collection using **the same comparer `OrderBy(id => id)` uses today** (`Comparer<string>.Default`), so the
  order is exactly the same while the identical changes are checked; the switch to an ordinal comparer comes after,
  as its own behaviour change (Stage 1.1's ordinal-order item).
- **Food lookup.** `BugAgent.TryFeedAtFood` calls `InfluenceManager.TryGetNearestFood(swarmCenter, 2.5)` per bug; the
  input is the group's centre and a constant radius (`BugAgent.cs:191`), so one call per group per tick, passed to its
  bugs, gives the same answer. The food registry (`InfluenceManager._food`) gains a cell index updated on
  `ITEM_ROTTED` / `FOOD_CONSUMED` / hydrate / clear; the lookup checks only cells within the radius and keeps the same
  tie-break (nearest, then the lower id), which is a total order, so the result can't change.
- **State check.** `ComputeStateHash` folds the same fields in the same order, read straight from each `BugAgent`
  instead of a `BugSampleData` record. The per-tick history of state checks stays as it is (the drift round asks for a
  past tick's value).
- **Drawing.** `InterpolateAllSwarms` / `SwarmVisual.Interpolate` and `CentipedeTrail.LateUpdate` skip bugs outside the
  camera's view (with a margin) and stop sorting; trails use a ring buffer, rebuilt when their bug comes back into
  view. One thing reads drawn positions: the sting check (`RenderedStingersInRange`), for every player in range. For
  bugs that are skipped, it computes the drawn position on demand by the same formula, so a player the computer in
  charge can't see is stung exactly as today.
- **Spreading a tick over frames** (only if a tick still costs more than ~3 ms at 2,000 bugs): the split falls only
  between whole groups, in the same order, and a new tick never starts before the last one finished, so nothing reads a
  half-finished state.
- **Proof:** for the changes meant to be identical, the equivalence check of Stage 1.0 (old and new builds side by
  side in one run, `tools/netcode/sync_diff.py` IDENTICAL, both ways round, the in-charge reports matching), plus the
  determinism replay for the movement code it covers; for every change, the behaviour check against the noise floor.

## Risks
| Risk | How it's handled |
|---|---|
| A performance change breaks sync between players | every computer runs the same code in the same order; both late-join gate halves and the drift round on every change; the equivalence check for the changes meant to be identical |
| A different method quietly changes how bugs behave | one per commit, named as a behaviour change; the behaviour check against the noise floor; the arena checks for rare moves |
| The equivalence check itself misses a difference | it must catch a deliberately planted one-line change before it is trusted; the in-charge reports are compared as well as the state checks |
| Tuning runs are too slow to finish a zone | screening runs, faster speeds proven against a normal-speed run, isolated parallel stacks if they prove independent, a run budget per zone |
| Whole-zone loading slows the server or bloats saves | measured after the change; the map is saved as differences only, but fallen fruit and the registries grow the save (village 226 KB today) and are trimmed if needed |
| Whole-zone loading in the wrong place loses edits or orphans swarms | it runs after the restore and the start-up spawn; Go tests for edits kept, no duplicated windfalls, nest groups counted |
| The first player stalls at a fresh zone (latent bug 3) | fixed in the same change: the zone's sync state reset at the end of start-up, the food list sent to the first player |
| One-time population jump on existing saves (never-visited chunks come alive) | expected and measured; tuning happens after |
| 512 zones break something that assumes 256 | the list from the code survey is fixed together, with a 512 test zone, the crossing test and the rewritten edge test |
| Crossing between a 512 village and 256 neighbours | the client learns sizes and spans; positions map through each neighbour's span; the server picks the nearest walkable entry cell |
| Authoring four times the area | natural ground generated from rules, landmarks crafted; the zone-craft gate unchanged |
| Tuning chases noise in a coupled system | ranges, not points; three seeds; one change per run; everything logged |
| Plans drift | one active plan, PROGRESS at every session's start and end, stage checks |
| The owner's review load | batches in the app, one stage at a time |

## Critical files
- **Server:** `nakama/modules/world/handlers_world.go` (chunk load + init), `match.go` (MatchInit, late-join, snapshot
  request, the edge entry check), `state.go` (blocking, the event log, the collision/roof map builders),
  `world_save.go` / `zone_persist.go` (restore order), `handlers_farming.go` (fruit trees per tick),
  `brood.go` / `handlers_bugs.go` / `predation.go` (centipede breeding), `messages.go` (zone size, the snapshot
  request), `zone.go` (neighbour spans), `zone_links_test.go`, `nakama/modules/rpc/world.go` (the enter reply).
- **Client:** `BugFarmerClient/Assets/Scripts/Entities/SwarmManager.cs`, `SwarmVisual.cs`, `Bugs/BugAgent.cs`,
  `Bugs/InfluenceManager.cs`, `Bugs/CentipedeTrail.cs`, `Player/CrossZoneController.cs`, `World/TilemapManager.cs`,
  `World/Rendering/DarknessOverlay.cs`, `WaterAnimated.shader`, `Networking/WorldManager.cs` / `BugMessages.cs`.
- **Tools:** `tools/ecology/{scaling_study.py, make_bench_zone.py, run_config.py}`, `tools/run_ecology_client.sh`,
  `tools/zonegen/` and `tools/make_scene.py` (512 renders), `tools/world/view_world.py`, `tools/gdd/` (maps).
- **Docs:** `docs/plans/village-slice.md` (this plan), `docs/plans/finish-bugs-zones-items.md` (the reference),
  `docs/plans/archive/`, `docs/plans/README.md`, `docs/README.md`, `docs/product/ROADMAP.md`, `docs/product/BACKLOG.md`,
  `docs/product/economy/DECISIONS.md` (D84), `architecture_swarm_sync.md`, `architecture_bugs.md`, the
  `ecology-tuning` skill.

## Acceptance criteria (each testable; a conformance-table row when done)
- [ ] **One active plan, old plans archived:** `docs/plans/README.md` lists one active plan; the three archived plans
  are in `docs/plans/archive/` with history kept; ROADMAP's Phase 1 line points here. *Check:* the files; `git log
  --follow` on each moved file; `git grep` finds no link to an old path.
- [ ] **The review app is published** at the items address with every mark intact. *Check:* the export diff (E0 = E1),
  the owner's test note read back.
- [ ] **The whole zone lives:** a run's food counts equal the zone's authored counts. *Check:* `RESSTATS` vs a census of
  the zone files (village today: 29 milkweed, 185 flowers, 129 fruit trees, 7 nests, 10 litter piles).
- [ ] **Every behaviour kept:** every Stage 1.1–1.2 change passes the behaviour check (no difference beyond the noise
  floor), and those meant to be identical pass the equivalence check (old and new builds in one run, `sync_diff`
  IDENTICAL over real activity, both ways round, the in-charge reports matching). *Check:* the checks' reports.
- [ ] **The performance targets** (Stage 1's check) on the 512 bench zone. *Check:* `scaling_study.py` summaries and the
  windowed frame-time run.
- [ ] **The snapshot on demand:** no snapshot traffic between joins apart from the safety one (until it is retired);
  join size under 300 KB at 2,000 bugs; both
  late-join gate halves; the time-out fallback tested. *Check:* the profiler's `snapshot_in_*` counters, the gates.
- [ ] **512 zones work:** a 512 zone loads, renders, collides, saves, and crosses to and from a 256 neighbour. *Check:* the
  crossing test, a north-up render, Go tests.
- [ ] **No centipede breed-and-starve loop.** *Check:* a Go test; centipede births vs starvation in a run.
- [ ] **The bug budget is set by the owner** from the measured numbers. *Check:* a dated decision in `DECISIONS.md`.
- [ ] **The village, rebuilt at 512, passes the zone process,** every species keeping itself going in range over 48
  game-days on three seeds, and the owner has played and signed it off. *Check:* the charts in the app, the sign-offs.

## Open decisions
- **Mine, on evidence:** the cell size of the food grid; whether spreading a tick over frames is needed (only if a tick
  still costs more than ~3 ms at 2,000 bugs); the snapshot's packed format; how a 512 zone's edge maps to a 256
  neighbour's until both are 512.
- **The owner's:** the Stage 1 targets (confirm or change); the bug budget (Stage 2); each zone-process sign-off; the
  wording change to CLAUDE.md's "never prop-scatter" rule so generated natural ground is allowed (Stage 3, step 4); a
  navigation aid for 512 zones (map or signposts); the village's bug list (6 or 13 species).

## Out of scope for this plan
- Rebuilding the other zones at 512 (each in its own turn, Stage 4).
- Simulating distant bugs in a cheaper, group-only way (only if a later target goes well past what Stage 1 delivers).
- Art production (the art track, ROADMAP's art row), hosting, audio.

## Verification (end to end)
1. Go tests in Docker; the determinism replay; the behaviour check for every Stage 1.1–1.2 change, and the equivalence
   check (old build against new, one run, both ways round) for those meant to be identical.
2. Both late-join gate halves on the 512 bench zone; the deliberate-drift resync drill.
3. `scaling_study.py` at 1,000 / 2,000 / 4,000 bugs on the 512 bench zone: per-part breakdown, join size, server tick.
4. The windowed real-drawing run: frame times at 2,000 bugs, worst frame recorded.
5. Two and four players on one machine; a crossing from the 512 village into a 256 neighbour and back.
6. The 48-game-day whole-zone baseline (three seeds) before tuning starts; its food counts match the zone's.
7. The owner's playtest at the end of Stage 1 and of Stage 3.

## The earlier plan (reference, not copied here)
`docs/plans/finish-bugs-zones-items.md` (3–4 October) holds the requirements and designs this plan points into: the
owner's requirements, Parts B–E, the behaviour model D0–D7 and the combat groundwork C1–C12. Its order of work, its
morning certainty assessment and its overnight run are replaced or done; Stage 0 labels them in the file itself. Every
one of its items has a place in this plan (the register above).

## Conformance table (filled in as each part is finished)
| Acceptance criterion | Evidence (file:line / command output) | Test / gate |
|---|---|---|
| … | … | … |
