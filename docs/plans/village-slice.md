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
- **Now (2026-10-07):** Stage 1.0 is done — the equivalence check and the two-step behaviour check are proven, the
  "before" numbers are measured and written up (`docs/product/investigations/stage1-before-2026-10-06/README.md`), and
  the three late-join faults the player tests found are fixed and proven.
- **Next (2026-10-08, paused while the owner uses Unity):** with the machine free — the Unity build and Stage 1.3's
  integration checks (both late-join gate halves on the bench village with food at start; parts 1 and 2 are committed
  but not yet deployed), the one-pass change's timing re-run (its equivalence passed; uncommitted in `SwarmVisual.cs`),
  then the whole-zone ecology baseline, the costs (measured first), and the four "wrong numbers" one at a time.
  Done: Stage 1.1; Stage 1.2 and its drag fix; Stage 1.3 parts 1–2 in code. Waiting on the owner: the missing shaders
  in built copies (BACKLOG). Open, not scheduled: the startup resync loop (seed 75 reproduces it); slow frames that are
  not the bugs.
- **The owner's answers (2026-10-07):** the behaviour check becomes a two-step check; the three late-join fixes now,
  as their own change; the windowed tour whenever suits.
- **Stage 1.1 started (2026-10-07, the owner's go-ahead).** Each step is a pair of builds that differ only by that
  step (a base built from HEAD, then the step) and the equivalence check both ways round, 300 s each way, on the bench
  village; one commit per step:
  1. **The food lookup through a cell index** (`FoodGrid`), one lookup per group: also proven against the full scan on
     80,195 random queries (`sim-determinism --food-index-test`; a planted fault caught); IDENTICAL both ways (2,417 /
     2,403 live ticks), with 1,333 / 1,231 landings at food in the windows.
  2. **The state check reads each bug directly** (`FoldStateHash`, no snapshot record per bug per tick): IDENTICAL
     (2,409 / 2,427).
  3. **Groups and bugs kept sorted** (`SortedIdTable`: a new sorted array after any change, never edited; the drawing
     and the sting check too): IDENTICAL (2,527 / 2,536), through 264 / 243 group births, merges and splits.
  4. **Reused per-tick lists, and the applied events removed in one cut** (they are always the front of the sorted
     waiting list; the old per-event `RemoveAll` scanned the whole list per event): IDENTICAL (2,539 / 2,537).
  5. **The strike check's reused lists** (the hunting groups, prey and predator copies, the claimed set, the victims):
     IDENTICAL (2,579 / 2,578; 2,653 / 1,414 reports).
  The batch is measured against the "before" numbers once step 5 passes; one behaviour check covers the identical
  batch (they are bit-identical by the equivalence check, so it is a confirmation), and the ordinal-order change gets
  its own.
- **Steps 1–5 measured (2026-10-07):** `docs/product/investigations/stage1.1-after-2026-10-07.md`. Per tick (release,
  fixed count, typical / slow): 1,000 bugs 2.7 / 4.5 → 0.56 / 1.06 ms; 2,000 bugs 6.0 / 10.0 → 1.06 / 2.0 ms (target
  2 / 4 ✓); 4,000 bugs 13.3 / 29.9 → 2.1 / 3.5 ms (target slow ≤ 6 ✓). The natural village at four times its bugs now
  keeps up (60.4 ticks a second; 32.8 before); at 2,000–3,000 bugs its tick went from 65 to 2.6 ms. Memory thrown away
  per tick: 1,705 → ~40–54 KB at 4,000 bugs — not yet zero.
  6. **Ordinal order** (the deliberate behaviour change): the three simulation sorts (the groups, the hunting groups,
     the players) plus the hit and net lists, which now use the server's byte order. Equivalence: IDENTICAL with the old
     build in charge (2,579 live ticks) — on this computer the old order and ordinal agree for the ids in use. Its
     behaviour check (the plan's) runs with the batch's: five fresh seeds (21–25), three builds interleaved (before
     Stage 1.1, after step 5, after step 6), so both comparisons share the step-5 runs.
     **Its behaviour runs (2026-10-07):** both equivalence directions IDENTICAL (2,579 live ticks each). Two of the 15
     behaviour runs were broken and run again (one by the machine stalling: client and server slowed together, no
     errors; one by the startup fault in the BACKLOG, which also hit the before-1.1 build). Then: steps 1–5 vs before
     1.1 — one SUSPECT (butterfly breeding share +104%, 5/5 seeds, 3.1 se); step 6 vs step 5 — one FLAG (centipede hits
     on the player +115%, 5/5 seeds, 4.7 se, from 13 to 28 events). Both builds of each pair are identical in the
     simulation, and hits on the player are detected from drawn positions (frame timing) outside the equivalence check;
     the runs went in a fixed order per seed (before 1.1, step 5, step 6), and the centipede hits rise with that order
     on every seed (totals 5 / 13 / 28). **Decided before the next runs:** the two-step rule's step 2 for both
     comparisons — five fresh seeds (26–30), the three builds with the order rotated per seed (26: step 6, step 5,
     before; 27: step 5, before, step 6; 28: before, step 6, step 5; 29: step 6, before, step 5; 30: step 5, step 6,
     before) — then `--confirm` over all ten seeds for both comparisons, the same bars; plus the centipede hits by run
     position over the ten seeds. A flag that holds there is investigated as a real change.
     **Result:** nothing flagged over the ten seeds in either comparison (pace 0.48% and 0.33% apart). In the rotated
     round step 6 had the fewest centipede hits (2, against 10 for step 5 and 13 before 1.1), and by run position the
     hits were 7 / 10 / 8: the step-1 flag was chance on very few events. Steps 1–5 and step 6 pass their behaviour
     checks. From now on the build order is rotated per seed (`stage1-before-2026-10-06/behaviour-check.md`, item 8).
  7. **No memory per tick, found:** the counter RNG turned the group id into a new byte array on every roll
     (`Encoding.UTF8.GetBytes`, per bug per tick) — about 11 bytes per bug per tick, the size the game measured; now
     folded in place, byte for byte the same (`sim-determinism --alloc-test`: 160,052 hashes equal to the old ones,
     including other alphabets and broken surrogates; the per-bug sim, hunting and feeding included, allocates 0 bytes
     per tick; the four simulation tests' final hashes equal the old code's). Also the player cells and the hunting
     groups are copied into reused lists instead of read through an iterator made every tick. Equivalence against
     step 6: IDENTICAL both ways (2,579 / 2,577 live ticks). Memory per tick, development build at 1,000 / 2,000 /
     4,000 bugs: in the 5-second windows without the 10-second snapshot, frames with a tick allocate +0.4 / +3.0 /
     −0.2 KB more than frames without one (noise; at the median they allocate less), against ~11 / 15 / 36 KB before.
     **No memory per tick: met.** What remains is the authority's full snapshot every 10 s (~63 KB per tick averaged
     over its windows at 4,000 bugs; the send-on-join change removes it) and drawing's own per-frame memory (1–7 KB a
     frame, growing with bugs; Stage 1.2).
- **Stage 1.2 started (2026-10-07) — the design, from the code** (`perf-tuning` loop; measured first: at 4,000 bugs the
  centipede trails cost ~3.2 ms a frame, 241 trails each inserting at the front of a list of up to ~150 head points
  and walking it once per body part with a square root per step; moving the sprites ~0.8 ms):
  1. **In view or not, per group, each frame:** the camera's view (orthographic) grown by a margin, against a box
     around the group's bugs over its last two ticks, grown by the body length for centipedes and millipedes. No
     camera → everything counts as in view (today's behaviour).
  2. **Out of view, the group's object is switched off** (its bugs, shadows, glows and trails hidden; no per-frame
     work). Only freezing the sprites would leave ghosts: the sprites hang on the group's object, so a player walking
     back to where a group was would see its frozen bugs. **Back in view:** switched on, every bug placed at its drawn
     position, every trail rebuilt as a straight body behind its head along its motion.
  3. **The drawn position as one function** (`BugVisual.DrawnPosition`): the blend between the two positions the
     last drawn frame used (kept per bug at each tick — the same values the drawing uses today, kept even when no
     frame draws the bug), plus the strike jab and the float; the float's phase comes from the clock instead of a
     timer advanced only by drawing. The sting check, the flash/jab picking and the hit area read it for every bug, in
     view or not, with the last frame's blend fraction and time — so a remote player off the computer-in-charge's
     screen is tested against where the bugs really are, never frozen sprites.
  4. **Trails in a ring:** a fixed ring of recorded head points, each with the distance travelled when it was
     recorded, so placing the seven parts is one pass and trimming is constant time; no memory per frame. Renderer
     writes (sorting order, tint, flap frame) only when the value changes.
  **Checks, decided before running:** a headless compile; the equivalence check both ways (the simulation is untouched,
  so IDENTICAL, in-charge reports included); the drawing cost at 1,000 / 2,000 / 4,000 bugs (headless) and the
  windowed tour at 2,000 / 4,000 against the before numbers (target at 2,000: slow ≤ 2 ms); **the two-player sting
  test** — the stung player out of the in-charge computer's view, old build against new, hits on that player counted
  (passes if the new build stings it at a comparable rate, not zero); the behaviour check, build order rotated.
  **First results (2026-10-07):** headless compile clean; equivalence IDENTICAL both ways (2,521 / 2,520 live ticks); the
  bug drawing per frame (headless, the camera's view) at 1,000 / 2,000 / 4,000 bugs: 1.19 / 2.11 / 3.98 ms → 0.03 /
  0.07 / 0.13 ms typical (trails 3.1 → 0.05 ms a frame at 4,000). The simulation tick read 10–30% higher in every part,
  the untouched ones too (state check, strikes, food lookup): the headless client now runs ~3,200 frames a second instead
  of ~220, and those frames compete with the tick — so ticks are compared with the frame rate held.
  **Second round, rules decided before it runs:** the base build is HEAD's four files plus the sting record (both builds
  log stings the same way; `-fps`, `-drawcheck` and the second player are test-only and shared). (1) Equivalence both ways,
  IDENTICAL. (2) **The side-by-side check** (`-drawcheck`: every group still drawn, and every tick every bug's on-demand
  drawn position compared with its sprite), 2,000 bugs at normal speed and 1,000 at 6×, 300 s each: passes if no position
  is more than 0.05 cells (a twentieth of a cell) from its sprite. (3) The tick at 60 frames a second, old and new
  interleaved, 1,000 / 2,000 / 4,000 bugs: passes if no part of the simulation tick is more than 10% slower. (4) **The
  two-player sting test:** 1,000 held bugs at 6×, the computer in charge (E) at the south edge (126, 2), the second
  player (F) at the zone's spawn, where centipedes come (all 98 hits on the standing player in the 30 behaviour runs were
  centipedes there); seeds 31–33, old and new in rotated order, 600 s each; stings on F counted from E's report log:
  passes if the new build stings F on every seed the old one does and its total is within half to twice the old one's.
  (5) The behaviour check (two steps), seeds 41–45, the order rotated.
  **Added during the round (2026-10-07, 20:55, before the sting results were all in):** the first at-spawn sting run
  (old build, seed 31) had no sting on F and no centipede hit on anyone, so in case the at-spawn test turns out to
  compare zero with zero, a walking variant runs too: F walks the bench route through the busiest feeding spots (all far
  from E's view), seeds 31–33, old and new rotated, the same pass rule. (The side-by-side runs had not started: the
  flag `--client-flags -drawcheck` needs "=" because its value starts with a dash; re-run as decided.)
  **Results so far:** (1) equivalence IDENTICAL both ways (2,518 / 2,512 live ticks). (3) **failed as written:** at 60
  frames a second the simulation tick is 9–13% slower (1,000 bugs 0.69 → 0.78 ms; 2,000 1.35 → 1.48; 4,000 2.64 → 2.87),
  the slow tick 19–58% slower (still inside Stage 1's targets), and parts whose code didn't change slowed too (state
  check +7–14%, strikes +6–20%); the processor time per second of play (ticks plus drawing) fell 87% (2,000 bugs:
  156 → 21 ms). The suspected cause, the old build's drawing keeping every bug's data in the processor's cache for the
  next tick, is being tested (the cache test). (4) at the spawn: **passed** — stings on F old 0 / 138 / 16 (154), new
  38 / 4 / 107 (149). (5) **flagged:** flies landed −49%, landings started −50%, fly breeding share −54% (5/5 seeds,
  ~5 standard errors), fly feeding a suspect −54%; pace equal (58.2 ticks a second both); the frame rates were not
  (~740 frames a second old, ~3,600 new, uncapped headless). The simulation is identical, so the server's fly groups
  spent less time at food: something the server receives differed. **Decided before running (23:30):** (a) the behaviour
  check again with both builds held to 60 frames a second, seeds 46–50, rotated — nothing flagged = the culling doesn't
  change behaviour at a monitor's frame rate; a flag = Stage 1.2 changes behaviour and is investigated before it is
  committed; (b) the old build against itself, uncapped and at 60 frames a second, seeds 51–55, rotated — flies
  flagged the same way = the in-charge computer's frame rate alone changes the ecology, a fault of its own (players'
  frame rates differ), recorded in the BACKLOG to investigate.
  **(a) and (b), 2026-10-08:** (a) at 60 frames a second, old against new: **nothing flagged** — the fly differences are
  gone; two SUSPECTs, centipede eating share and starts +23% (5/5 seeds, 3.2–3.3 standard errors). (b) the old build
  uncapped (~740 frames a second) against itself at 60: nothing flagged, no suspect. The game itself syncs to the monitor
  by default (Windows uses the Ultra quality level, vSync on). **Decided before running (04:35):** (a) step 2 as the rule
  says — five fresh seeds (56–60) of both builds at 60, rotated, then `--confirm` over all ten; (c) the new build
  uncapped (~3,600 frames a second) against itself at 60, seeds 61–65, rotated: flies flagged the same way = the fly drop
  comes from that extreme frame rate (a game synced to the monitor never runs there), recorded in the BACKLOG; not
  flagged = the drop needs the change and the uncapped rate together, investigated before Stage 1.2 is committed.
  **Results (2026-10-08):** (a) step 2, ten seeds: **nothing flagged** (the centipede suspects cleared; pace 0.07% apart).
  (c) the new build uncapped against itself at 60: not flagged, but two SUSPECTs the same way as the uncapped fly drop —
  flies landed −58%, landings started −57% (5/5 seeds, 3.2–3.3 standard errors). Neither of the two outcomes decided
  above; the two-step rule's step 2 settles a suspect, so **decided (08:10):** (c) step 2, seeds 66–70, rotated,
  `--confirm` over ten — confirmed = the fly drop comes from the extreme frame rate (BACKLOG) and Stage 1.2 is
  committed; cleared = the drop is investigated before the commit.
  **(c) step 2: cleared** — nothing flagged over ten seeds. So the uncapped fly flag (old against new, seeds 41–45) is
  explained neither by the change at a monitor's frame rate (a) nor by the frame rate alone (b, c). **The investigation,
  decided (09:55):** the same step 2 that settled the doubtful step-1 flag of 2026-10-07 — the uncapped comparison, old
  against new, five fresh seeds (71–75) rotated, `--confirm` over all ten: confirmed = a real interaction between the
  change and a very high frame rate, whose mechanism is found before the commit; cleared = the first flag was chance
  (like the centipede flag of 2026-10-07) and Stage 1.2 is committed.
  **The uncapped step 2 (2026-10-08): cleared** — nothing flagged over ten seeds (41–45, 71–74, 76; pace 0.31% apart).
  Seed 75 broke twice with the old build (the startup fault, BACKLOG: a reproducer) and the first seed-76 pair broke
  while another project's containers started on the machine; both set aside, as the rules say. Fly landing still leans
  down (−48%, 8 of 10 seeds, 3.1 standard errors — under the bar; it is one of the rarest behaviours, where the check is
  coarse), while the server's fly feeding and breeding show no difference (−20% / −22%, under 1 standard error): watched
  in the next behaviour checks. **Stage 1.2 is committed as tested.** Two rules failed as written and are explained
  (the tick at 60 frames a second: half added work, half a colder cache; the start-up positions: the group objects'
  glide). Next, with the owner's yes (2026-10-08): the group objects stop gliding; then the tick's two passes over each
  group's bugs become one.
- **1.2 follow-up 1, the group objects stay put (2026-10-08; the owner's yes, as long as the game still works the same):**
  the group's object is placed once at creation; its per-frame glide (`SwarmVisual.Update`) is gone; the attack sound
  plays at the group's simulated centre. **Checks, decided before running:** equivalence both ways, IDENTICAL; the
  side-by-side check at 2,000 bugs (normal speed) and 1,000 at 6×: no position more than 0.05 cells from its sprite,
  start-up included; a windowed run with the game's own pictures, looked at.
  **Results:** equivalence IDENTICAL both ways (2,574 / 2,577 live ticks); the side-by-side check 0 of 4.6 million
  (2,000 bugs) and 0 of 14.9 million (1,000 at 6×) positions more than 0.05 cells off, largest 0.049, start-up included;
  the pictures look right (centipede bodies trailing their heads, flies, butterflies, a wasp at the hives). **Passed.**
  The logs showed an old, separate fault: every built copy of the game misses three custom shaders (BACKLOG; asked).
- **1.2 follow-up 2, one pass per group per tick (2026-10-08):** each bug's drawn positions are captured inside the loop
  that simulates it, instead of in a pass of their own before it (the capture reads only the bug's own position, so the
  results are the same, with one walk over the group's bugs instead of two). **Checks, decided before running:**
  equivalence both ways, IDENTICAL; the tick at 60 frames a second, old and new interleaved (order rotated) at 1,000 /
  2,000 / 4,000 bugs: passes if the group tick (`Sim.SwarmTick`) is faster, or no more than 2% slower, at every count.
  **First round (2026-10-08, 13:20–13:55): equivalence IDENTICAL both ways (2,543 / 2,578 live ticks); the timing is
  spoiled** — the new build read slower at every count (+4 / +21 / +26%), but so did the parts it doesn't touch (food
  lookup +9 / +18 / +30%, strikes +9 / +19 / +17%, state check +2 / +16 / +19%), and the Unity Editor was found open
  using ~1.4 processor cores. Not judged; the timing is re-run on a quiet machine (and builds wait while the Editor holds
  the project). **The re-run (2026-10-09), decided before it runs:** the same builds (`SyncTest_base14` against
  `SyncTest_onepass`, against the now-deployed Stage 1.3 server — both face the same server), at each count the order
  old, new, new, old (mirrored, so a slow patch falls on both), each part judged on the mean of the two runs per build;
  the same pass rule.
- **The late-join fixes (2026-10-07, the owner's yes):** the three causes fixed as proposed, plus the drift-check
  resync, which sent no collision map at all — every package now sends its own map as of its snapshot, from one place,
  and the client re-arms the map wait on each package. Six Go tests; every gate passed (Go, seven sim-determinism
  modes, both late-join halves). On the world where the faults reproduced: plain joins with a fence gnawed in the
  window 5 of 5 identical (before: 3 of 4 out of step), same-account rejoins 5 of 5 identical (before: all out of step),
  run 3 replayed twice, every player identical. Cause C's trigger did not occur (residual noted). The player script
  now clears every player's old files (a stale P3 file was being compared). Details: the investigation's Outcome.
- **The windowed tour (2026-10-07, 07:16–07:27):** the first check with `-screenshot` showed the TITLE screen
  (`OpeningSequence`, removed only when Start is pressed) still over the game — the first overlay fix had hidden only
  the character select; the rig now removes both (test code only), and the pictures show the village with the
  player walking its route. Release build, 300 s each, frame and drawing times per frame (typical / worst 1 in 100):
  2,000 bugs: frame 4.0 / 14.1 ms, bug drawing 3.2 / 5.3 ms, 173 of 67,852 frames over 16.7 ms; 4,000 bugs: frame
  6.7 / 29.9 ms, bug drawing 5.3 / 8.9 ms, 2,539 of 36,848 frames over 16.7 ms (targets at 2,000: drawing 2 ms worst).
  The game's own world menu ("Play" and a mode list) stays on screen after entering — nothing in the game hides it.
  Results: `tools/_generated/scaling/2026-10-07-tour/` (with the pictures).
- **The two-step behaviour check (2026-10-07), its rules set before its validation:** step 1, five seeds: flagged as
  before (all one way, over 4 standard errors, over 15%); a SUSPECT when all one way, over 15% and over the 5%
  critical t for the seeds (2.78 at five; a textbook bar, not one picked from the results). Step 2, only for
  suspects: five fresh seeds of both builds, interleaved; confirmed when, over all ten, the change goes the same way
  on at least nine, is over 4 standard errors and over 15%. On the existing data: the same-build pair raises no
  suspect (exit 0); the longer-eating copy raises two (centipede eating +65%, wasp eating +128%, 3.7 standard errors
  each). **Validation, decided before it runs:** step 2 on seeds 16–20 must CONFIRM centipede eating going up.
  **PASSED (2026-10-07, 09:48):** centipede eating confirmed, +81%, up on all ten seeds, 6.6 standard errors; pace
  0.02% apart; no broken runs. Wasp eating (+114%) was not confirmed (seven of ten seeds, 2.3 standard errors): wasps
  are few, so their behaviour stays below what the check can see — the coarse net's limit, as written down. **Stage
  1.0 is done.**
- **Waiting on the owner:** "publish"; the OK to delete the rehearsal page.

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
  - **The behaviour check, first two calibrations: both failed, and the check was redesigned twice.**
    - Natural ecology, 5 + 3 seeds of the same build: 14 false alarms, because the village's first days go different
      ways from seed to seed. So the check moved to held-count runs (`s10_behave_1000`) and judged only changes that
      are clear (over 4 standard errors) and sizeable (over 15%).
    - Held count, 280 s runs (5 base seeds, 3 same-build seeds, 3 seeds of the radius-4.0 copy; the PC restarted
      during the last run, which was re-run): a false alarm on the same build (wasp attacks "vanished" on the other
      seeds), and the planted change missed. Three causes: the runs reached only game-day 1, which the check skips,
      so the server half judged nothing; the seeds differ so much that group averages hide real changes (seed by
      seed, flies landed more and wasps attacked less on all three seeds); and the "too rare" rule counted bug-ticks,
      so one wasp attacking for a long time looked well counted.
    - Redesigned: paired by seed, a change must go the same way on every seed; the client tally counts each state's
      starts and "too rare" counts those; 600 s runs. 16 unit tests; both test builds rebuilt (no errors); a 2-minute
      trial wrote the new columns (one wasp attack start = 1,455 bug-ticks; centipede attacks 11 starts = 48,991).
  - **The owner (2026-10-06):** go ahead with the redesign; each zone will get a chosen starting seed; the power-plan
    cap for the slower-computer runs is allowed; bug counts will be chosen by feel once the limits are known.
  - **The paired calibration (15 runs of 600 s, seeds 1–5; base, radius-4.0 copy, base again; every run reached
    game-day 4):** the same build against itself: **0 false alarms** (38 measures judged; the other 199 are true zeros,
    such as births in a held run or beetles hunting). The radius-4.0 copy: **not caught** under the rule set before the
    runs. Its effect is there, in the right direction (wasps starting to land +155% on all five seeds, 2.6 standard
    errors; centipedes landing +97%, flies +22%), but under the bar. **Why:** a seed does not make a run repeat. For
    most measures the same seed run twice differs about as much as two seeds do (wasps landing, seed 1: 0.25 then
    10.92 per 1,000 bug-ticks); only what the layout fixes repeats (centipede strikes: same-seed spread a tenth of the
    seed-to-seed spread). Landing is rare in held runs (flies are landed 0.04% of the time), so a change to it hides in
    that noise. Results: `tools/_generated/scaling/2026-10-06-paired/` (`check_control.md`, `check_planted4.md`).
    **Open:** what the behaviour check must prove, and how (the owner's call on the acceptance line; my proposal is in
    the report of 2026-10-06).
  - **Found after the crash: the bench zone kept a crashed run's settings.** `run_config.py` patches the zone's
    `zone.json` and puts it back afterwards from a copy taken at the start; the PC restart (11:51) stopped the run
    before that, and every run since took its starting copy from the patched file. The bench zone is git-ignored, so
    the "is the data as committed" check never saw it. It kept the 1,000-bug test's starting numbers, the held count,
    seed 3 and the 6× speed. Today's held runs used exactly those settings anyway, so their results stand (the
    earlier natural runs of the morning bred normally, so the bench was clean then). The bench was rebuilt from
    `village_21_B` (`make_bench_zone.py`), and Stage 1.0e's script rebuilds it before every run. **The lasting guard
    (the owner's yes, built the same day):** each run saves its before-copy to disk first and deletes it only after
    restoring; a run that finds one refuses to start, and `run_config.py --restore-leftover` puts every file back
    (6 tests, `tools/ecology/test_run_config_guard.py`).
  - **The owner's answers (2026-10-06):** (1) the behaviour check becomes a coarse safety net with its limits written
    down, and any speed-up that uses a different method gets a side-by-side check (old against new on the same
    state) built with it; (2) a test that proves the check can catch something, after block A; (3) a lasting guard
    in `run_config.py`.
  - **The catching test, decided before it runs:** config `s10_behave_1000_hunt` (centipedes half as fed by each
    kill, `feed_per_kill` 45 → 22.5), seeds 1–5, 600 s, against the base runs. **Passes only if** the check flags at
    least one of centipede strikes per 10,000 bug-ticks, prey claimed per 10,000, or fly kills per centipede bug-day,
    going UP. Not "hunting twice as often" (as first proposed): centipedes already chase 91% of the time and wasps
    99%. Strikes come in bursts that end when the group is full (a quarter of the gaps between strikes sit at the
    4-second cooldown, the longest tenth are over 3 minutes), so how full each kill makes them sets the strike
    count; a longer cooldown would move strikes only 1–6%.
  - **The catching test, first try: inconclusive.** One flag, and not a predicted one: flies breeding 46% less on
    all five seeds (fly feeding −37%, under the bar). Centipede strikes did not rise (−3%); their kills fell 26%
    (not flagged): the prediction was wrong. And the comparison was unfair: the test runs (evening) were compared
    with base runs from the afternoon, and the machine had slowed — the client kept 58.8 ticks/s against 59.7–60.4,
    which over a run leaves it about 70 game-seconds behind the zone. **My mistake: the runs must be interleaved.**
    The check now refuses groups whose client pace differs by over 1% (the afternoon pair: 0.24% apart; this test:
    1.30%, refused), with a test.
  - **The catching test, second try, decided before it runs:** base and half-fed runs interleaved on fresh seeds
    6–10 (block B, step 3). **Passes only if** the pace gate passes AND the check flags fly breeding or fly feeding
    going DOWN (what the first try showed). If the pace gate passes and nothing is flagged, the first try's flag was
    the slower machine, and the catching test has failed.
  - **Block B, the player tests** (`tools/run_players.sh` on the bench village as authored, normal speed, the base
    build; results in `tools/_generated/players/2026-10-07T0052…`, `…0056…`, `…0101…`):
    - 2 players, one walking a route: IDENTICAL (2,054 live ticks).
    - 3 players, the one in charge leaving at 120 s: charge passed on twice; every pair IDENTICAL (1,065 and 2,553).
    - 3 players, P2 leaving at 100 s and rejoining as the same account: P1 and P3 IDENTICAL (2,557 ticks), but **P2
      was out of step from its first live tick in BOTH sessions** (ticks 96 and 1,087), with the same bug count as
      the others, until the server's drift check resynced it about 20 s later (ticks 280 and 1,180). The other late
      joiners today (same early snapshot, same 155 groups made before replay) were identical from their first tick.
      **A real late-join fault, cause not yet known**; finding it needs per-bug traces. Asked the owner.
    - Found on the way: my batch scripts logged `echo "$(date) … exit=$?"`, which reports `date`'s exit code, not
      the run's — so every "exit=0" in today's batch logs was the clock's. Every run was re-checked from the
      measuring script's own log ("run_config exit 0" in all 34 finished runs); the player script itself returns
      the right code (1 for the rejoin run). Later scripts save `$?` first.
  - **Block B, the slower computer:** two P-cores plus the processor capped at 50% (Windows power plan; set 18:06, put
    back to 100% at 18:17 and checked). Typical / worst 1 in 100 per tick: 2,000 bugs 7.1 / 13.3 ms (two cores alone
    7.5 / 12.6; normal 6.0 / 10.0); 1,000 bugs 3.2 / 6.0 (two cores alone 3.4 / 10.6). The cap made no clear
    difference, so it probably did not lower this processor's clock (some Intel desktop chips mostly ignore it or
    only drop the boost). Not claimed as a slower-computer result until the clock is measured during a capped run.
  - **The catching test, second try: FAILED** (by the rule set before it ran). Interleaved, seeds 6–10, the pace gate
    passed (0.01% apart), and nothing was flagged: fly breeding −10% and feeding −12% (not the same way on every
    seed), centipede strikes −8%, kills +9%. So the first try's 46% drop in fly breeding was the slower machine, not
    the change — the pace gate was needed — and halving how full a kill makes a centipede barely changes behaviour in
    held runs. The check has still not been shown to catch a real change; a third try needs a change whose effect is
    certain from the code, not from my reading of the ecology (proposed to the owner).
  - **The catching test, third try, decided before it runs (2026-10-06 night):** a change whose effect is certain from
    the code: bugs stay on a corpse for 50 ticks instead of 25 (`BugAgent.FeedTicks`, `BugAgent.cs:63`), so the time
    centipedes spend eating should roughly double (the check sees 35% there). Both builds made from the same code, the
    one constant apart; base and changed copy interleaved on fresh seeds 11–15, 600 s held runs. **Passes only if** the
    pace gate passes AND the check flags centipede eating time (`client.eating_per_1k`) going UP.
  - **The catching test, third try: FAILED, narrowly.** The change did what the code says: centipede eating time
    **+65%, up on all five seeds** — but at **3.7 standard errors**, under the bar of 4, so not flagged. The pace gate
    passed (0.11% apart). On the way, one run (the changed copy, seed 12) was a **broken client**: stuck at tick 0
    for 5 s, then in a resync loop for the whole run ("PROTOCOL VIOLATION: Old event not applied", 3,891 times; 2.9
    ticks/s); it was set aside (`…/2026-10-06-paired/invalid/`) and both builds re-run on seed 12, as the rule's five
    seeds required. The pace gate now names such a run ("BROKEN RUN", under 90% of the median pace; 17 tests).
    **Conclusion:** with five seeds and a bar of 4, the check misses even a certain +65% change; the limits written
    down from the same-build runs were too optimistic (about half the real ones). Not loosened after the fact; the
    choices go to the owner (more seeds, longer runs, or a two-step check).
  - **A fourth fault found (not investigated):** a client whose simulation is still at tick 0 five seconds into a
    zone resyncs, then keeps meeting events for ticks it has already passed and resyncs again for the whole run
    (1 of 79 runs today). The same slow-start family as the late-join cause C.
  - **The windowed tour: stopped at the owner's request** (20:28). The game ran the tour, but the character-select
    overlay stayed drawn over it: a test enters the world directly, and the overlay hides only when a player picks a
    character. Fixed in test code only (the rig hides it; `-screenshot <s>` saves the game's own picture so a windowed
    run can be checked without capturing the owner's screen); the release build compiles (0 errors). The stopped run
    left its settings in the bench zone and the leftover guard did its job: the next run refused, and
    `--restore-leftover` put every file back. The tour's numbers are not used; it runs again when the owner says.
  - **The rejoin fault: investigated** (`docs/product/investigations/latejoin-rejoin-divergence.md`, READY TO
    IMPLEMENT pending the owner): reproduced on run 3's world (6 of 8 plain joins and every rejoin out of step) with
    traces covering the whole join. **Three causes**, each a piece of the join that doesn't describe the snapshot's
    moment: (B) the bug collision map is sent as of now, so a fence a centipede chews through between the snapshot
    and the join is already gone in the joiner's replay; (A) a departed player's position is removed on receipt,
    outside the ordered stream, and a same-account rejoin brings back a phantom of itself; (C) a join in the zone's
    first ~10 s can get a stand-in instead of a snapshot (the authority's first snapshot is skipped while its sim is at
    tick 0). Every out-of-step session today has exactly one of them. Fixes proposed; the owner decides.
  - **The rejoin fault: investigation started** (the owner's yes, 2026-10-06):
    `docs/product/investigations/latejoin-rejoin-divergence.md` (draft). The rejoin session has an evidenced cause (a
    departed player's position is removed on receipt, outside the ordered stream, and a same-account rejoin brings
    the old position back through the snapshot); the first session is not explained yet; the reproduction runs
    after the windowed tour.
  - **Stage 1.0e started (block A, headless, 13 runs):** natural 1× and 4× (release build, clean; 4× breakdown on the
    development build; behaviour at both), fixed 1,000 / 2,000 / 4,000 at normal speed (release clean, development
    breakdown), and two-core runs at 1,000 and 2,000. Results: `tools/_generated/scaling/2026-10-06-before/`.
    **Done** (all 13 ran cleanly). The player's computer per tick at normal speed, typical / worst 1 in 100: 1,000
    bugs 2.7 / 4.5 ms; 2,000 bugs 6.0 / 10.0 ms; 4,000 bugs 13.3 / 29.9 ms (targets at 2,000: 2 / 4 ms). Written up at
    the end of 1.0e.

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
- **Added 2026-10-07 (from watching the test runs):** predators keep attacking flies far too long; nothing shows when a
  bug attacks; the player was seldom hurt, so the bugs offered little threat. So tuning starts with **behaviour,
  tuned until it is fun** (how each bug hunts, attacks and fights, tried in the arena), and only then the ecology's
  other levers. The bugs' combat needs an overhaul — that is Stage 3, steps 3 and 6 (the earlier plan's C1–C12),
  with a visible sign when a bug attacks another bug added to it.
- **Added 2026-10-06:** zones probably won't need very many bugs; the scaling work shows what the engine can do, and
  the owner then picks each zone's count by how it plays. The game will have minimum hardware requirements, so
  the slower-computer target is a minimum specification, not every older machine. Each zone will start from a chosen
  seed (the best one found for it).

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
  2026-10-04), it is allowed, named as a behaviour change in its commit, and judged by a **side-by-side check** built
  with it (the old and new methods answer the same questions on the same state, every tick, and every disagreement is
  counted), with the behaviour check as the coarse net over the whole game (the owner's choice, 2026-10-06).
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
  Windows power plan is a machine-wide setting: the owner allowed it (2026-10-06), restored right after each use.
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
- **Order:** **behaviour first, until it is fun** (the owner's direction, 2026-10-07): each bug's hunting, attacks and
  fight — how long a predator stays on its prey, how often and how fairly the player is hit, the signs before and
  during an attack — designed and tried in the arena (Stage 3, steps 3 and 6). Then structural breaks (anything that can't work: food out of reach, instant breeding, a frozen habitat;
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
- **Behaviour tally** (`-behaviour`; since 2026-10-06 it also counts each state's starts): after each tick, per
  species, bug-ticks in total and while hunting
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
  species per 1,000 bug-ticks and per bug-day; the baseline is the noise-floor seeds; unit-tested. *Revised
  2026-10-06 after the first noise-floor runs:* a metric is flagged only when the change is both clear (over 4
  standard errors of the difference, from both groups' spread) and large enough to matter (over 15%); a metric with
  fewer than 20 counted events is "too rare to judge"; a frequent one that appears or vanishes is flagged. And the
  check runs with the bug count held (`s10_behave_1000`: about 1,000 bugs, `hold_population`, 6× speed), because in
  natural runs the village's first days go different ways from seed to seed (in some seeds the flies die out, in
  others they breed): five plus three seeds of the SAME build raised 14 false alarms under the first rule. Small exact
  differences are the equivalence check's job. *Revised again 2026-10-06 after the first held-count calibration
  failed both ways* (a false alarm on the same build; the planted change missed): **paired by seed** — both builds run
  on the same seeds and each seed's difference is judged; a change counts when it goes the same way on every seed, is
  over 4 standard errors of those differences and over 15%. A seed sets where everything starts, and that alone moved
  wasp attacks from none (three seeds) to 59,000 bug-ticks (another); seed by seed, the planted change was plain
  (flies landing more and wasps attacking less on every seed). The client tally also counts how often each state
  STARTS, and "too rare" counts starts (one wasp attack had made 1,455 bug-ticks). Runs last 600 s, so the server's
  daily lines reach day 3 (the 280 s runs reached only day 1, which is skipped, so the server half judged nothing).
- **`scaling_study.py`** reads the cost files and reports percentiles, frames over 16.7 ms, allocations and the snapshot
  timing; options for the perf mode, a windowed run and a route.
- **`tools/run_players.sh N`:** two to four test players, staggered, with roles (in charge, wanderers), an optional
  authority leave and reconnect, and one combined report.
- **`tools/run_gates.sh`:** Go tests, every sim-determinism mode, both late-join halves on the bench (wiped first), and
  the equivalence check when two builds are given; a pass/fail table and real exit codes (no pipes that hide them).

**1.0d — proving the checks:**
- The same build copied twice: the equivalence check says IDENTICAL both ways round, over a window with real activity
  (merges, hunts, feeding, a late join), counted from the tally so a quiet window can't pass.
- A build with a planted one-line change (the food-lookup radius 2.5 → 2.6): caught by the equivalence check. The
  behaviour check: the same build run again on the same seeds must pass, and a meaningful change in a common
  behaviour must be flagged (centipedes half as fed by each kill; the radius 2.5 → 4.0 change was below its limits,
  see PROGRESS). Its role since 2026-10-06 (the owner's choice): a coarse safety net, with the smallest change it can
  see written down per behaviour (`docs/product/investigations/stage1-before-2026-10-06/behaviour-check.md`).
- Five seeds of the current build: the noise floor for every metric, recorded (held count, `s10_behave_1000`).
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
- **Re-checked against the code, 2026-10-08** (before any code; `.claude/complex-change-review.md` stage 1): the five
  setup scans are called from subscribe (`handlers_world.go:38-43`), restore (`world_save.go:422-426`) and the import
  (`zone_persist.go:186-190`), as above — plus a debug "spawn an occupant" path (`handlers_env.go:249`) that registers a
  placed tree the way placement does (placement, not chunk loading: unchanged). MatchInit restores or imports
  (`match.go:323/326`), then spawns the starting groups and carrion only when no groups were restored
  (`match.go:338-341`); `spawnInitialSwarms` empties each species' group list (`match.go:1830`), so nest groups founded
  during a test zone's restore are dropped from the count today. The first player is told there are no earlier events
  (`LastEventSeq: -1`, `match.go:633`) with a seed baseline of the groups; the full reset of the zone's sync state runs
  only when the last player leaves (`match.go:791-803`). The client never calls `HydrateFood`; a late joiner's food comes
  in the snapshot (`HydrateFoodExact`, `SwarmManager.cs:2005-2010`), the first player's from nowhere. **Split:** the
  server work (the helper, `loadWholeZone`, the kept group lists, the sync reset at the end of MatchInit, the zone's
  food list in the first player's bootstrap message, the server's bounds guards, the two costs) is built and tested in
  Docker; the client work (applying that food list, clamping chunk requests) waits for a Unity build.
- **The independent review (2026-10-08, a fresh-context agent; its load-bearing claims re-read in the code):**
  (1) the server-made bootstrap snapshot carries no food (`match.go:3008-3014`) and an early joiner gets exactly that
  (`:3182`) — so the first player's food list must go into that snapshot too, from the same builder, or the first player
  and an early joiner diverge (clients stay consistent today only because neither gets food); (2) the "first player"
  gap exists today already: start-up spawns and carrion emit events at MatchInit, and the empty-zone pause clears queued
  events but keeps the counter and the log (`match.go:876-883`) — the change widens it, the reset fixes both; (3) the
  save path needs bounds too: restore splits coordinates with truncating division and remainder (`world_save.go:396,
  413`), so an out-of-zone edit west or south would index an array with a negative number and stop the zone starting;
  edits on phantom chunks are saved, and placement accepts phantom chunks — guard the save build, the restore and
  placement as well as subscribe and the blocked checks; (4) the food list: ground items with food value and stations
  with fill, ids and positions exactly as the food events give them, sorted by id, applied on the client by clearing
  then `HydrateFoodExact`; (5) **a behaviour change, not only a cost:** an unloaded chunk counts as a wall for the
  server's groups (`state.go:608-610`) and its food is invisible, so the ecology will shift — measured on its own; (6)
  costs to add: the first autosave copies every chunk from disk, start-up runs five JSON passes per chunk (one anchor
  list per chunk would do), every fruit tree's ledger events go to every client, the collision map's per-cell decode on
  every join; (7) `crawler_lab/zone.json` says 96×96 over a 4×4 grid of chunk files; (8) docs that go stale (invariant 6
  in `complex-change-review.md`, the lazy-loading comments, the memory note). **Order:** the server pieces that keep
  every client consistent first (the helper, `loadWholeZone`, the kept group lists, the sync reset at the end of
  MatchInit, the bounds guards incl. save and placement), unit-tested in Docker; then the food list on both bootstrap
  paths with its client half (a Unity build, the `frontier-sync` recipe, both late-join gate halves); then the costs.
- **Stage 1.3, part 1 — the server's whole zone, written and unit-tested (2026-10-08, while the owner had Unity; not
  yet deployed):** `initChunkRegistries` (the one setup helper, at subscribe, restore and import); `loadWholeZone` at
  the end of MatchInit's set-up; `spawnInitialSwarms` keeps groups already listed; `WorldState.resetZoneSync` at the end
  of MatchInit and on the last player's leaving; `ChunkInZone` / `CellInZone`: outside the zone's grid every cell is a
  wall, nothing is placed, stored or saved, a restored out-of-zone edit is left out with a warning, and a chunk request
  there is answered with display-only grass (today's look beyond the edge kept). Six Go tests
  (`whole_zone_test.go`), each failing on the old code (a restore panic, a dropped group list, events left at start, a
  walkable phantom chunk, a saved phantom edit, a partial zone); all Go tests pass. **Not yet run, needing the server
  deployed and the machine free:** both late-join gate halves, the equivalence check, and the whole-zone baseline that
  measures the ecology change; then part 2 (the food list in both bootstraps, with its client half) and the costs.
- **Stage 1.3, part 2 — the zone's food in both bootstraps (2026-10-08; server unit-tested, client written but not yet
  compiled — Unity was in use):** a better route than the review's (rebuilding the list from item positions would put
  fallen fruit at the item's cell where its event named the tree's): the server keeps `FoodLedger`, the food registry
  the events build, in `AddFoodEvent` with the client's rules, so it equals every client's by construction; restored
  food is added once at MatchInit at its own cell; `foodBootstrapList` goes in the first player's `ZoneAuthorityMessage`
  and in the server-made bootstrap snapshot for an early joiner. Client: `ProcessZoneAuthority` clears the registry and
  hydrates before the first tick (both callers carry the list). Three Go tests (the client's rules, seeding only
  restored food, the same list for an early joiner); all Go tests pass (the persistence-classification guard caught the
  new field: per-run). Known gap: a client that becomes the one in charge from the tick broadcast has no list. **Still
  to run, with the machine free:** a Unity build, both late-join gate halves (non-vacuous: a zone with food at start),
  the equivalence check, the whole-zone baseline.
- **Stage 1.3 parts 1–2 checked (2026-10-09, the new server deployed, the client built — no compile errors):** both
  late-join gate halves `SYNC: IDENTICAL` on the bench village (co-located 202,192 shared-bug states / 233 ticks;
  spawn-apart 214,670 / 241, disjoint chunk sets asserted); the server logged the whole zone loaded (8 × 8 chunks). The
  first player's food message went only to a debug file these builds don't fill, and a gate passes even if neither
  side gets food — so a confirming run logs it to the main log: the first player hydrated 63 entries from its bootstrap,
  the joiner 68 from the snapshot, `SYNC: IDENTICAL` (211,431). The equivalence check doesn't apply (a server change:
  both clients face the same server). Next: the one-pass timing re-run, then the whole-zone baseline.

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
