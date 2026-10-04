# Plan — Finishing the bugs, their behaviour, where they live, and the items (2026-10-03)

> Finish this part of the game properly, with the owner: **improve, don't replace**. The game stays the game; a
> change to something that works needs a good, stated reason. This is the umbrella plan. Each piece of building work
> gets its own committed plan in `docs/plans/` before it starts; the first is `review-app.md`, written in Part 0.

## PROGRESS (newest last; the resume pointer)
- **2026-10-03 (evening):** rebuilt after the WSL shutdown. Nothing built yet. The repo is clean at `1b60ac2d` and
  pushed; `main` lacks 2 commits (merged in Part 0).
  - **Inputs, re-checked against the files by me:**
    - three code surveys;
    - two cold critiques;
    - the app design;
    - UV research;
    - a combat survey;
    - research on creature behaviour in other games and on how studios plan design work.
  - **The owner's feedback on the plan (2026-10-03):**
    - ecosystems should fluctuate like the real world, surges and collapses included; players may wipe things out,
      and the Ecologist rewards bringing them back;
    - improve, don't replace;
    - as much as possible on players' computers, not the server, with real numbers on scaling (including whether
      zones should be 4× bigger);
    - swarms must NOT all attack at once;
    - no calendar-based cadence;
    - explain ideas plainly, without name-dropping other studios;
    - the arena must let the owner release bugs, watch, or jump in and fight.
  - **Corrections from the owner's own records:**
    - the private plot's "idle" design exists (`docs/product/design/game_design.md` §11), so that question is gone;
    - D46's "attack all at once" follows a sentence in the owner's 2026-09-27 message, which they now say meant the
      opposite. It is corrected in Part 0 with a dated note.
- **2026-10-04:** the owner's answers to the explanations:
  - the village is the first slice, until its population charts are right;
  - group attacks are designed per bug: more attackers when provoked, taking turns, never all at once;
  - danger must be real, with the village relatively easy and harder outward;
  - black-ant soldiers patrol, and a far more dangerous deep ant lives in its own colonies;
  - colonies spanning two zones need excellent transfer between zones, or merged zones;
  - natural barriers separate zones of different difficulty;
  - improve the population system (my improvement list is D0b);
  - scaling is measured with a single player, then several players on one machine.
  Part 0 was started (one read-only status check) and stopped when the owner returned to planning. Nothing was
  changed.
- **2026-10-04, the overnight run started** (the owner approved; I'm on auto).
  - **Step 0:** the drive was readable; git clean at `1b60ac2d`; the Editor closed; the 10 world backups copied and
    verified into `BugFarmer_backups/world_keep_2026-10-04/`.
  - **Part 0:**
    - D83 written and checked for the owner's own wording (0 matches); the D46 and D82 notes added;
    - the three lineup rows given `decided`;
    - §03 and §04 set to rework, and P6 labelled;
    - the overview's and `architecture_combat.md`'s swarm rule corrected;
    - `architecture_bug_behaviour.md` marked;
    - the Bug Stick row rewritten (the items builder still passes);
    - BACKLOG corrected (black ants, dragonfly, firefly) and a rewording item added;
    - the research file's three fixes and the bolas note applied;
    - memory updated;
    - `review-app.md` written.
    Then: commit, push, merge into `main`.

## Certainty assessment (the `certainty-assessment` method; scores read off evidence; judged by the weakest design row)
| # | Dimension | Score now | Evidence | What raises it |
|---|---|---|---|---|
| 1 | Matches what the owner asked | 86 Strong | The owner's answers of 3 and 4 October applied: fluctuating ecosystems, improve-not-replace, per-bug group attacks, real danger, client-first, the arena, the village slice and dry run, ants, barriers, water, playable variants, no calendar. **No questions are open now.** Later decisions (zone size, the two-zone ant colony, each system's design) come with their evidence. | The owner's sign-off on each slice |
| 2 | Understanding of the game as it stands | 88 Strong | Read this pass, among others: `match.go:1333` (chasing switches off the bug's other work); `ecology_stats.go:42-51` (no player-kill or catch cause); `SwarmManager.cs:895-904` (exact hits only for the authority's own player); `handlers_player.go:17` (1 s shared invulnerability); `nests.go` (food-driven brood, 1 egg per trip, a bank of 9, re-hatch and re-found); `game_design.md` §11 (idle design) | The audit (D1) |
| 3 | The process finds great design, not slop | 76 Plausible | A finished slice before going wide; the owner plays it; playable variants for feel; a "what the player sees" check; every rule cites the owner or is labelled my proposal | The first slice played by the owner |
| 4 | The behaviour approach is sound and *improves* what exists | 78 Plausible | Keeps the food-driven population model untouched. Changes only *why* a bug fights and what it does after. Don't Starve's spider brain checked in its source, used for structure only. | The slice build and the owner's play |
| 5 | Fits the synced simulation and its costs | 65 Plausible | The recipe is known. The costs at 2× and 4× bug counts and zone size are unmeasured. Several systems still run on the server. | **S1, the scaling study** |
| 6 | Ecosystems behave as the owner wants: cycles, surges, collapses, a way back | 72 Plausible | The village cycles in bands when tuned (owner, 2026-10-03); reseeds bring species back. Player pressure is unmeasured, and kills and catches aren't recorded. | **S2, the pressure runs** |
| 7 | The owner's marks and the repo stay safe | 85 Strong | Export, rehearsal of the exact risky step, comparison, a tested restore; repo-only saving | The rehearsal |
| 8 | Project management | 74 Plausible | Milestones defined by what they prove, not by dates; a risk table; work-in-progress limits; two definitions of done | The first slice's real effort |
| 9 | Fits the owner's time | 75 Plausible | Batches when ready; plays at each milestone; explanations as pages in the app | Adjust after the first two batches |
| 10 | Art and readability dependency | 65 Plausible | Placeholder readability in the slice; an art list per system | A readability check in the slice |
| 11 | **The overnight run is safe and won't stall** | 85 Strong | Checked tonight: the PC never sleeps (powercfg 0); the database is in Docker's volume, not on C:; backup retention keeps the daily newest (`backup.go:12`); the ecology tool wipes the tested zone's save, so the bench copy only (`run_config.py:162-173`); the Editor is closed; the hook gates are known (`manifest.json`); commit and push after every step; a stop on drive loss | The run itself; the morning PROGRESS log |

- **Design confidence ≈ 65**, held down by rows 5 and 6. Both are measured, not argued, by S1 and S2, which run
  first.
- **Verification is pending** (normal at plan time). The gates are in "Test plan".

## Context / why
The owner wants this part of the game finished, and much of it is half done. Today showed four problems:
- reviewing in the terminal doesn't work;
- the write-ups were natural history, not game design;
- rules were made out of guidelines and examples;
- bug behaviour was treated apart from combat, though for the player they are one thing.

**Verified state of the code and data (2026-10-03):**
- **Ants.** The real ant zone has no colony (no `ant_brood`, though its design asks for 2–3). It is topped up every
  10 s (`match.go:1562`). It has no prey for its centipede. Trails run only in `ant_lab`, as whole groups.
- **Ecology.**
  - Births come from food: eggs per trip home, brood that hatches, nests that re-hatch and re-found (`nests.go`).
  - Populations cycle; caps and director reseeds exist.
  - Known breaks:
    - the firefly can't breed;
    - predators breed at spawn;
    - carcasses last 60 s;
    - no night;
    - no time or rain in the simulation;
    - no crossing between zones;
    - player kills and catches aren't recorded.
- **Combat.**
  - Two attack styles.
  - Three separate ways to start a fight; chasing switches off the bug's other work.
  - Exact hit checks only for the authority's own player.
  - The arena is peaceful.
  - Not built: stamina, lasting effects, armour stats, ranged weapons.
  - Killing a nest's bugs doesn't call its defenders (`nests.go:658` is called only on nest damage or a harvest).
- **Docs to correct.**
  - §04 "As built".
  - A BACKLOG line.
  - The Bug Stick row.
  - `architecture_bug_behaviour.md`.
  - §03 P6 ("every danger warns first" was my rule).
  - D46's "all at once".
  - My memory note.
  - Stale combat docs.
- **Review pages.**
  - All marks are on the items page.
  - 227 removed item ids have hidden marks.
  - There's no zone registry; only 4 of 20 zones have maps.
- **Items.**
  - The 28 "cut" items placed in zones are my recommendations only.
  - 82 of 83 weapon rows are undecided (D75 settled the rules).
  - Three weapons marks from today.
- **Design sections.** §02, §05, §07, §15 and §18 are stubs; §01 Q1 is open.
- **Zone scaffolding.** The gate checks reading, not outputs. zone-craft still says to use the pop-up question tool
  and to decide on a timeout.

## Requirements (the owner's, restated and dated)
- **One review app** for zones (maps drawn in code, every bug there), bugs, items with settled cuts archived, and design
  sections. Feedback sits beside what it's about; a zone's high-level map is approved first. **Explanations live there
  too**, with diagrams (2026-10-03).
- **Improve, don't replace.** Finishing means improving what exists; a change to something that works needs a good
  reason (2026-10-03).
- **Ecosystems fluctuate like real ones.**
  - Cycles within rough bands, surges and collapses (2026-10-03).
  - Players may tip them or wipe a species out; that's their choice (D62).
  - The Ecologist rewards bringing things back (2026-10-03).
  - The village already cycles when tuned, sometimes spikes against its cap, sometimes dies out until the next reseed
    (2026-10-03).
- **Bug behaviour serves two goals:** the ecosystem, and fun combat (2026-10-03).
- **As much as possible runs on the players' computers.** The server is where bottlenecks happen. Real numbers on
  scaling, including whether zones should be 4× bigger (twice as wide and tall) with 4× the bugs (2026-10-03).
- **Combat** (§00, decided).
  - Combat matters; defence is critical.
  - Starter zones are cosy, nights more dangerous, danger rises outward.
  - Wind-ups are bug by bug.
  - You fight to sell bodies or to catch bugs to farm.
  - Big subdued bugs are dragged.
  - Dying costs little.
  - Stamina is allowed.
  - Bosses are grown adults, only where a fight is fun (D46).
- **Warnings depend on the critter** (2026-10-03).
- **Group attacks are designed per bug.** Not all at once, and not a fixed "one or two": provoking a wasp nest brings
  more attackers, who swoop in and out in turn (2026-10-03).
- **Danger is real.** The village is relatively easy but dangerous enough to make you want armour and a sword; the
  challenge jumps outward. Choose dangerous bugs and give them dangerous behaviour, but bugs keep pursuing their goals
  while they fight (2026-10-03).
- **Ants** (2026-10-03).
  - Trails form from scouts; laying is driven by food brought home; workers and warriors; herding means steering
    taps.
  - Black-ant workers mostly ignore you unless attacked beyond a poke.
  - Black-ant soldiers attack intruders and are around the colony, not only after a theft.
  - A second, far more dangerous ant lives deep underground in its own colonies (fire ants or a better fit).
  - Colonies span two zones, so cross-zone transfer must be excellent, or the zones are merged.
- **Natural barriers separate zones of different difficulty:** rivers to bridge (some shallow places) and stone or dirt
  ridges. They hold back players and wandering bugs alike (2026-10-03).
- **Subduing:** more nets, sprays, and stuns from non-lethal bug sticks that look like billy clubs (2026-10-03).
- **The arena:** release bugs from a list, in a chosen number, or place a station (a compost bin for flies); watch as
  an observer or jump in and fight (2026-10-03).
- **UV light** if it earns its slot across several dangerous bugs; **goggles** with a real use; **ranged weapons
  (bows)** return, with arrows from stingers and mosquito needles; few, non-gross bug-part weapons (2026-10-03).
- **The private plot is the idle home farm** (game_design.md §11).
  - Slow, capped automation.
  - Decorations give small production boosts, less for each duplicate, up to a cap; the happiness panel (P26).
  - No automated combat.
- **Guidelines are strong defaults.** Think for yourself; explain plainly; no name-dropping (2026-10-03).
- **The repo is the only save place; git and file moves allow no guesses** (2026-10-03).

## How we work
- **Saving.**
  - Commit and push after each finished step. Check the drive first; if it's unreadable, stop and tell the owner.
  - At most two helpers read C: at once.
  - The only writes outside the repo: memory notes, the scratchpad, and the dated export of the owner's marks in
    `C:/Users/emily/BugFarmer_backups/` (out of the public repo).
- **The owner reviews in the app.**
  - Explanations are pages there, with diagrams.
  - Questions are plain text, never a pop-up tool.
  - Marked rows are never edited quietly.
- **Every rule cites a dated owner decision or is labelled "my proposal".** A fresh reviewer checks everything first.
- **Pace is set by the work, not the calendar.**
  - A review batch goes to the owner whenever a coherent set is ready (held until then, not dripped).
  - A playable milestone goes to the owner whenever a slice passes its done check.
- **Limits:** at most 2 systems being designed, 2 being built, and 2 things waiting on the owner.
- **Two definitions of done.**
  - **Designed:** goals, feel bars, the chosen variant, a decision entry.
  - **Built:**
    - the determinism and performance gates pass;
    - the ecology runs look right;
    - the recording is approved;
    - the owner has played it.
- **Every behaviour gets a "what the player sees" column.** Invisible complexity is cut unless it's free.

## What I need from you, and when
1. **Now:** the questions at the end.
2. **Before the app is published:** pause marking for about 20 minutes, and confirm nothing is waiting to save.
3. **After publishing:** one test note, and a short look-over.
4. **From then on:** review batches in the app when they're ready, and play each slice when it's ready.

## The order of work
- **M0:** Part 0 (records, saving, merge into `main`) → Part A (the app) → Part B's conversation.
- **M1, measurements by me, alongside Part A** (no owner time):
  - **S1, the scaling study:** real numbers instead of guesses.
    - Measured: client CPU per frame, the late-join snapshot size, bandwidth per player, and the server tick time.
    - At 1×, 2× and 4× today's bug counts, and on a 256 vs 512 zone (the owner's 4× idea).
    - First a single player on this machine, then several players run on the same machine.
    - Frame rate and frame time are measured too, then profiled to find the real bottleneck.
    - **The server side reuses what exists** (`perf-tuning` skill): the built-in profiler (`profile` flag →
      PERFSTATS and PERFSYS lines), `plot_perf.py`, and the `current/index.html` dashboard:
      - per-species CPU;
      - un-measured time;
      - memory clean-up pauses;
      - broadcast bytes against the 100 ms-per-tick budget;
      - the skill's own "scaling sweep" across bug counts.
    - **New for the players' side:**
      - per-tick timing of the bug simulation inside the headless test player, which needs no graphics;
      - frame rate and frame time from a run with real drawing (the same mode as the capture trial, S3).
    - Measuring adds no cost to the simulation and isn't part of its state; it's checked with `sim-determinism`.
    - It also informs merging the two ant zones.
    - Each system still running on the server gets its cost measured, plus what it would cost on players'
      computers. The goal is to move as much as possible to clients.
    - It includes the trial in `individual_ecology_redesign.md` §5: food that regrows identically on every computer.
    - The results go to the owner as a page in the app, with a recommendation on zone size.
  - **S2, the pressure runs:**
    - the ecology stats learn to count player kills and catches;
    - scripted players over-hunt, over-farm and hoard in the headless village runs.
    - The question is *what happens*, not how to stop it: how fast collapses come, what warning signs come first, how
      species come back. That shapes the Ecologist's warnings and rebalancing quests. Nothing is prevented; players
      may tip the ecosystem.
  - **S3, the combat arena and capture** (see C11): the arena with its spawn list, stations, observer mode and
    fight mode; a scripted fighter that measures hits; screen capture for recordings.
- **M2, the first finished slice: the village's bug life** (decided by the owner, 2026-10-03; done when its
  population charts are right). Its existing, tuned food web (flies, butterflies, wasps, centipedes, millipedes,
  carrion beetles), improved to the final bar:
  - wasp nest defence and combat redone on the new model;
  - the centipede as the first real fight;
  - the fly farm with catching and subduing;
  - fair hits;
  - known breaks fixed.
  It's the first thing players meet, holds livestock, danger and nests, and already has tuning runs to compare against.
  **The owner plays it.** The village's *layout* redesign (D53) stays with the zone process, separately.
- **M3, the template:** what the slice taught becomes the kit for the rest: behaviour parts, how dangers are signalled,
  tuning settings, arena scenarios, pressure checks, both definitions of done.
- **M4, the next slices:**
  - **The ants as the second slice:** their own colony system (castes, trails, growth, steering), with real nests in
    the Ant Tunnels and crossing into neighbouring zones.
  - Then bees, wasps and hornets beyond the village, butterflies and moths, centipedes and millipedes, spiders and
    harvestmen, beetles, dragonflies, scorpions, mantises, crickets and locusts, fireflies and glowworms, mosquitoes,
    and water life.
  - Each zone's bug list becomes firm as its species land. Ecology tuning runs continuously.
- **Items:** the weapons batch and the UV light early; each slice's core items with the slice; decorations after the
  plot design (§15).

## Key risks
| Risk | Retired by |
|---|---|
| Too much still on the server limits how many players can join | S1, then the server review (D4) |
| Bigger zones or more bugs overload players' computers | S1's numbers before any size change |
| Player pressure makes ecosystems dead or meaningless with no way back | S2 results shape the Ecologist's warnings and quests, and the reseed and recovery paths |
| Unfair combat for players other than the zone authority | C1, early in the slice |
| Behaviour unreadable without final art | Placeholder readability in the slice |
| Owner review load | Batches when ready; limits on work in progress |
| The drive drops mid-operation | The stop rule; rehearsal before publishing |

## Part 0 — Make the record honest, then save (about 45 minutes; nothing republished)
1. **D83, in my words** (no quotes), with the dated owner decisions:
   - herding means steering;
   - trails form from scouts;
   - colony growth from food;
   - workers and warriors;
   - game first;
   - improve, don't replace;
   - ecosystems fluctuate, collapse and recover, and the Ecologist rewards rebalancing;
   - as much as possible on players' computers;
   - bug behaviour serves ecology and combat together;
   - warnings depend on the critter;
   - **group attacks designed per bug:** more attackers when provoked, taking turns swooping in and out, never all at
     once;
   - danger is real (the village relatively easy, the challenge jumping outward);
   - black-ant soldiers patrol, and a far more dangerous deep ant lives in its own colonies;
   - natural barriers separate zones of different difficulty;
   - shallow water stops walking bugs and deep water stops all bugs (§01 Q1, answered 2026-10-04);
   - the village is the first slice and the dry-run zone;
   - the zone-design conversation happens in the app;
   - the subduing tools;
   - the arena's requirements;
   - UV and goggles with real uses;
   - ranged weapons back;
   - few, non-gross bug-part weapons.
   **D46 gets a dated correction note:** its "all at once" followed a sentence in the 2026-09-27 message, and the
   owner clarified on 2026-10-03 that they meant the opposite. The three lineup marks get `decided` dates.
2. **§03 and §04 back to `rework`.**
   - §03 P6 is labelled "my proposal, not adopted".
   - `architecture_bug_behaviour.md`: "Real biology first" becomes "Game first"; follow-the-player marked replaced.
   - `overview.md:411` ("to change: only lunges should warn") is checked against D46's correction.
3. **The Bug Stick row** (unmarked, checked):
   - taps steer ants;
   - hits stun and subdue bigger bugs, non-lethally, like a billy club;
   - other walkers are decided with their own systems.
   The BACKLOG's ant line is fixed. The marked weapon rows wait for the weapons batch.
4. **The candidates file's three wording fixes and one note** (`/home/emily/bugfarmer_rescue_2026-10-03/tz2_fix.py`
   entries 1–3; the bolas spider's family was cut).
5. **Memory.** `bestiary-ecology-review.md` corrected. New lessons: herding read literally; a guideline made a rule;
   natural history instead of game design; a pattern made universal; behaviour designed apart from combat;
   "keep in band" made a goal when the owner wants real fluctuation; calendar pacing; name-dropping instead of
   explaining.
6. **Committed plans:** `docs/plans/finish-bugs-zones-items.md` (this file) and `docs/plans/review-app.md`, indexed,
   with a ROADMAP pointer.
7. **Commit, push and merge into `main`** per `.claude/git-guidelines.md` (`status` clean, a plain `merge --no-ff`,
   push, check `main` equals `origin/main`, back to the feature branch).

## Part A — The review app (about a full day; published only after a rehearsal; plan: `review-app.md`)
*(Unchanged from the reviewed design: checked facts, data, accounting, one source of truth, feedback storage,
views, maps, tests and the step-by-step publish with export, rehearsal and comparison.)*
- **Where it lives:** one file of about 1.5 MB at the items page's address
  (https://claude.ai/artifact/L9ftJfjRfcFD3yAB66qenD), so every mark carries over.
- **Data:** `docs/gdd/data/{zones,bugs,phrases}.jsonl`. Zone links are "proposed" until signed off; a bug may wait for
  its zone (D79). Built-zone maps are generated at build time.
- **The builder proves on every build:**
  - complete accounting;
  - ids valid;
  - neighbours adjacent;
  - the map round trip;
  - north up;
  - stable keys;
  - no "approved" field in the data;
  - the format rules;
  - under 15 MB.
- **Feedback storage:**
  - marks unchanged at `marks/<group>/items/<id>`;
  - notes at `notes/<kind>/items/<id>`;
  - approvals at `signoff/<kind>/items/<id>`, with fingerprints;
  - "Older notes" for removed rows.
- **Views:** Zones, Bugs, Items (with Archive), Design, Status, and **Explain**. Explain is new: pages that explain a
  design idea plainly, with diagrams and real numbers, for example S1's results, the behaviour model and the slice
  choice.
- **Tests:** `tools/gdd/tests/` (stress, builder, screenshots) and `marks_restore.py`.
- **Publishing:**
  1. Tests pass and screenshots are taken.
  2. The owner pauses marking.
  3. Export to `BugFarmer_backups`.
  4. Rehearse the exact step on a throwaway page.
  5. Publish with the address.
  6. Re-export and compare every field.
  7. A test note, then the owner's note.
  8. The old GDD page becomes a "moved" notice, and the docs are updated.
  If any step fails: stop, roll back, tell the owner.

## Part B — Zone-design scaffolding, with the owner (before any zone maps or bug lists)
- **I bring:** an inventory, the 21 corrections and endorsed principles, the 15 recorded failures, and what's out of
  date (as a page in the app, or in chat until it's published).
- **The owner decides:** principles, steps, approval points, and what agents hand in.
- **My starting proposal** (theirs to change): purpose, map and bug list → brief → landmark options → build → a fresh
  grader at game zoom → sign-off. A zone is designed together with the behaviour of its key bugs.
- **A design rule the owner set (2026-10-03):** zones of different difficulty are separated by natural barriers:
  rivers that need a bridge (with some shallow places) and stone or dirt ridges. These hold back players and wandering
  bugs alike. The zone checks verify each barrier and each crossing point. This ties to §01 Q1 (water and crawling
  bugs).
- **I build:**
  - the process;
  - the schematic layout format;
  - the zone bible template (`docs/gdd/zones/`);
  - zone-craft fixes (no pop-up questions, no timeout rule, a fresh grader, the app);
  - author-zone fixes;
  - builder checks: roads, matching openings, counted placements, ore, game-zoom crops, ecology placement;
  - the output gate (fail-open, self-tested, checked in a fresh session);
  - short task cards.
- **Bar:** the owner judges the dry run good.

## Part C — Which bugs live where
- **Now, in the app:** every zone's list, labelled provisional.
- **Firm, zone by zone, as each zone is designed with its species.**
  - Inputs: the registry, a one-line player role per bug, §01 Q1.
  - Candidate species are offered where variety is thin (three or four new is a target).
- **Bar:**
  - every bug has a job for the player there;
  - its food, its breeding place and what keeps it in check are present, or it's marked as coming in from a
    neighbour;
  - no two bugs share a role without a reason.
  After sign-off, §03 and §04's lists are generated from the registry.

## Part D — Bug behaviour: improve what exists so it serves the ecosystem and the fight
**D0. The behaviour model** (my proposal; the population model is NOT changed).
- **What stays exactly as it is:** how populations rise and fall.
  - Births come from food: eggs laid per trip home, brood that hatches, nests that re-hatch and re-found.
  - Deaths come from predation, starvation and old age.
  - Caps and reseeds stay as safety nets.
  - These make today's village cycle, spike and sometimes die out until reseeded. That is what the owner wants, and
    it stays.
- **What changes is *why* a bug fights and what it does after.** Each species gets a reason to fight drawn from its
  life:
  - its nest disturbed;
  - its brood threatened;
  - hunger (a blood-feeder wants you);
  - its territory at the hour it hunts;
  - a nestmate hurt nearby (same nest only).
  Plain closeness to a player is also a reason, for the species whose nature it is (hunters and hostile bugs; see
  D0c). **Danger stays real:** the village is relatively easy but dangerous enough to want armour and a sword, and
  the challenge jumps outward. The change is that bugs keep pursuing their goals while they fight.
- **After a fight, the bug goes back to what it was doing:** home, carrying food, its trail. A leash (time since its
  last strike, distance from home, a target it can't reach) guarantees the player can get away.
- **Nest defence is sized by the colony's real numbers.** When a nest is disturbed, the defenders that come out are
  its actual residents (and soldiers, where the species has them). So a booming colony boils over, and one that just
  crashed barely defends. Killing defenders really shrinks the colony, which must rebuild from food. The fight reads
  the ecology, and the fight changes the ecology. (This replaces nothing in the population model.)
- **Structure:** one priority list per bug, checked a few times a second: survival → duty (defend, alarm, hunt when
  hungry, carry food home, lay) → routine for the time of day → wander near home. It replaces today's three separate
  ways of starting a fight.
- **Livestock:** a calmed or kept colony is a visible state. Harvesting has a cost, which timing can lower (foragers
  home at night).

**D0b. Improving the population system (all checked in code, 2026-10-04).**
- **Fixes for wrong numbers:**
  - nests come alive only when a player first nears them (`nests.go:57-61`), so they should all live from the start;
  - predators can breed at spawn (born at 50, tuned breed threshold 32: `ecology_tuning.json:7`, `match.go:2214`);
  - the starvation re-arm uses a fixed 60 instead of the tuned 90 (`match.go:2238`), so the next die-off comes after
    40 s, not 10;
  - split-off groups never carry food home (`predation.go:189`);
  - merges can swallow a nest's group (ROADMAP latent bug 4);
  - carcasses last only 60 s;
  - the firefly has no food.
- **Richer cycles:**
  - recovery by newcomers from neighbouring zones or surviving breeding grounds instead of reseeding from nowhere;
  - time and weather in bug lives;
  - colonies that react to their own state (hungry → farther foraging; thriving → daughter nests; starving → weak
    defence);
  - natural crowding limits (nest sites, spacing, food competition), with caps as the last safety net;
  - player kills and catches recorded;
  - colony health visible in the world.
- Each change is compared against today's village charts, one at a time.

**D0c. Fight design per species (my proposal, 2026-10-04).** Three settings each:
- **Temperament:** calm, defensive, hunter, or hostile.
- **Triggers:** hit; nest touched; alarm; territory at its active hour; hunger.
- **Escalation:**
  - its moves (C3);
  - an attack count that grows with anger, attackers taking turns swooping in and out;
  - a leash, then back to its goal.
- The mix shifts by ring: village mostly calm and defensive, plus wasps, the night centipede and hornets at lights;
  further out, hunters and hostile bugs.
- Ants: workers calm; soldiers defensive patrols; fire ants hostile (recommended as the deep ant; army ants have no
  fixed colony).
- The two-zone colony: solid transfer between zones, or merged zones. Decided after S1.

**D1. Honest audit**, system by system: what it does, how it looks, what's broken, and the "what the player sees"
column. Docs corrected. Heavy runs only when the drive is stable.

**D2. Design sections written with the owner first:**
- §05, farming;
- §07, combat: the player's kit, damage, subduing and catching, lasting effects, protections, danger by ring;
- §18, time and weather;
- §02, enough progression to set combat numbers per ring.
§15 comes before the decorations.

**D3. Principles and feel bars**, signed off. Examples to agree:
- what a bug is doing reads in about 2 seconds;
- losing a fight feels like your own mistake;
- a calmed colony is safe to work.

**D4. Engineering gates, in order:**
1. S1's numbers decide what moves to players' computers and the zone size.
2. **The server review:** a table of every server system, each marked keep or move with the measured cost. As much
   as possible moves.
3. Time and rain enter the simulation (after §18).
4. Real bug transfer between zones (before ants forage into neighbouring zones).

The budgets every design states: server tick, client CPU and bandwidth from S1. The multiplayer cases every design
covers: two players, a late join, a change of the computer in charge, a zone border, a reconnect.

**D5. A game-first bug sheet,** shown on one worked bug first. It has three faces: ecology, encounter (its reason to
fight, its danger signal or none, its moves, what answers it, its ring, what it does after) and farming. Plus:
- the player's verb;
- the two tests (the moment only this bug creates; what we lose without it);
- the "what the player sees" column;
- simulated versus stand-in;
- the art list;
- biology in one line.

**D6. The design loop per system:**
1. Audit and research.
2. Options with diagrams.
3. Owner session.
4. Two or three playable variants in the arena for anything about feel.
5. Write-up, fresh review, approval.
6. Its own build plan (`frontier-sync`, `complex-change-review.md`).
7. Build.
8. Pressure runs.
9. The owner plays it.
10. Per-bug details.
11. Sign-off.

The order comes from the registry's families, every family once; known breaks join their system.

**D7. Ecosystems per zone.** A food-web diagram in the app. Tuning per `ecology-tuning`: the real zones, one change
at a time, logged.
- **The bar, in the owner's terms:**
  - without players, each species' numbers rise and fall in a living cycle (not a flat line pinned at a cap, not a
    permanent crash), over about 48 game-days;
  - occasional surges and die-offs are fine;
  - a species that dies out can come back through reseeding or neighbours.
  - With the pressure bots running, collapses are allowed. What we check is that they show warning signs the Ecologist
    can read, and that there's a way back the Ecologist's quests can reward.
- **Bands are proposed by me and approved by the owner.** The director's rain lever is aligned with "weather is a
  lever of last resort".

## The combat groundwork — review and redesign (owner-approved directions, 2026-10-03)
**Keep:**
- health outside the shared simulation;
- attacks and weapons as data;
- hits checked against what's on screen;
- one gate and damage funnel;
- dodge invulnerability decided by the server;
- smoke calming in the per-bug simulation.

**Redesign** (owner: "do whatever will be best"):
- **C1. Hits that are fair and fast for every player.** Today only the zone's authority computer judges stings, and
  only its own player exactly (`SwarmManager.cs:895-904`). The redesign, for fast combat:
  - each player's own computer judges hits on itself, because it alone knows exactly where it is, frame by frame;
  - all computers run the identical bug simulation, so they agree on where every bug is;
  - the server checks loosely (bug alive, roughly in range, cooldowns, dodge invulnerability) and applies the damage;
  - players' attacks on bugs work the same way they already do (the attacker's computer picks the bugs, the server
    checks reach);
  - ranged shots work the same way;
  - lost wind-ups when the computer in charge changes go away.
  - Proof: a two-player test where both players dodge the same attacks, with each player's hit record compared
    against what they saw.
- **C2. One reason-driven way for bugs to start a fight** (D0). Examples of what the player would see:
  - *Paper wasp:* a forager on your cabbages ignores you unless you swing at it. Swat it and it fights back, and
    nestmates within a short range join. Walk past its nest and a couple of guards come out to look. Hit the nest and
    every wasp home comes out. All of them go home after.
  - *Centipede:* by day it hides under its log and only strikes if you lift or break the log. At night it hunts its
    patch, and a player crossing it gets lunged at. Hungry ones range farther.
  - *Black ants:*
    - workers ignore you unless you really attack them (a bug-stick tap steers them; it doesn't anger them);
    - soldiers patrol the colony and the trails, and attack intruders who come close;
    - break into the mound, and as many soldiers as the colony really has pour out, chase you to the edge of their
      range, then go home.
  - *Fire ants* (the deep, dangerous ant): hostile on sight near their colonies.
  - *Mosquitoes:* hungry ones come for your blood. Fed ones leave to rest, so a swarm thins as it feeds.
  - Killing a nest's bugs now alerts that nest. Today only damaging the nest does.
- **C3. About ten reusable bug moves**, set up like the weapon moves. Each has an optional cue (per critter), the
  strike, a recovery window, a cooldown and its effect. The moves:
  - dive-sting;
  - lunge-bite;
  - grab-then-sting;
  - pounce;
  - drop on a line;
  - web tangle;
  - spray cone;
  - charge-and-throw;
  - claw pinch;
  - blood-drain.
- **C4. Group attacks designed per bug** (owner, 2026-10-03): never all at once, never a fixed count. How many attack at
  once grows with the group's anger (a lightly provoked nest sends one or two; a nest you keep hitting sends more),
  and attackers swoop in and out in turn. This builds on today's staggered orbit-and-dive (`BugAgent.AttackMove`).
  - The damage funnel's one-hit-per-swarm cooldown and the 1 s shared invulnerability are retuned around it, and
    around stamina.
  - D46 is corrected in Part 0.
- **C5. Subduing as the second way to win.** Throw more nets, spray it, stun it with the billy-club bug stick. A subdue
  meter (today's calm meter, extended) fills, and the bug becomes visibly subdued: caught if small, dragged if big
  (D46, P15). It ties combat to farming.
- **C6. Lasting effects:** venom, poison, acid, web slow and knock-down, with the protections (Sting, Venom, Acid, D76),
  armour values and the potions (D54). Server-side, kept out of the simulation like health.
- **C7. Hit feel:** a short pause on hits, knock-back by weight, light bugs interrupted mid-wind-up while heavy ones
  push through, death reads, stamina (P14) with the dodge retuned.
- **C8. Bows and ranged combat:**
  - the shooter's computer detects hits, and the server checks;
  - bugs respond to being shot: the attacker becomes their target, fliers close in, crawlers give up on a target they
    can't reach;
  - arrows from the Bug Extractor.
- **C9. Groups (decided by me, as the owner asked):** C4's anger-scaled, taking-turns count applies to packs
  (centipedes, soldier ants) and swarms alike. Those waiting circle and menace. The count and its growth are set per
  species and tuned in the arena.
- **C10. Night and placement:**
  - really nocturnal bugs marked;
  - the stronger tiers placed in their zones (they spawn nowhere today);
  - bosses grown from thriving populations (P13).
- **C11. The arena** (owner's requirements):
  - a non-peaceful arena with a spawn panel: pick bugs from a list and a number, release them, or place a station (a
    compost bin, fruit) and let them come;
  - **observer mode:** a free camera, unseen by bugs, time controls including night;
  - **fight mode:** jump in with any gear;
  - a peace toggle;
  - a scripted fighter that measures hit rates, time-to-kill and time-to-die;
  - a combat-numbers page in the app per ring and gear tier (today a platinum sword does 28 against a 16-HP giant
    centipede).
- **C12. Fix the stale combat docs:** skill lines 14–18, 31–32 and 35; `architecture_combat.md:146-149`;
  `SwarmManager.cs:797-800`.

**Where these land:**
- **The village slice:** C1, C2, C3 (wasp and centipede moves), C4, C5, C7, C11.
- **§07:** C6 and the numbers.
- **When their systems come up:** the rest.

## Part E — Items
- **The weapons batch.**
  - Rows brought in line with D75.
  - Today's three marks answered.
  - A ranged family (bows) in place of eight metal bows, with arrows from stingers and mosquito needles (D18). The
    needle row's cut rested on D74's coatings, not on arrows.
- **The UV flashlight**, designed for play and flavoured by real facts.
  - **What glows:** scorpions, millipedes, paper-wasp nests, huntsmen, and harvestmen faintly.
  - **What doesn't:** hornets, centipedes, ants, mosquitoes, widows. Wolf spiders show by eyeshine in the headlamp.
  - **Real side effects:** scorpions shy from UV; dead ones glow; UV draws moths (D63).
  - **Goggles** only with a real use.
- **Each slice's core items with the slice:** for the village, nets, smoker, the bug stick and the compost bin.
- **Decorations after §15**, by happiness group (seating, lighting, plants, art, textiles, outfits on mannequins),
  following the idle design (game_design.md §11) and P26. Stations with §10.
- **The 28 cut-recommended items in zones** go to the owner as one list; nothing is removed without them.

## The owner's answers (2026-10-04)
1. **Order:** wait; the zone-design conversation happens in the app once it's published.
2. **Sign-off size:** one per zone (map plus list), one per behaviour system, and items by kind.
3. **The dry-run zone:** the village.
4. **The first slice:** the village.
5. **Water:** shallow water stops bugs that walk; deep water stops all bugs, fliers included. This becomes a §01
   decision in D83. The old problem of flies getting stuck at shorelines (the 2026-06-11 playtest) has to be solved by
   steering: fliers turn away from deep water instead of piling up against it. This is a slice task, with a test.
6. **Feel options:** written options with diagrams, plus playable variants in the arena for anything about feel.

## The overnight run (the owner is away; I'm on auto) — scope, order, stop rules
**Checked tonight, read only:**
- **The PC never sleeps or hibernates** (powercfg: 0, on High performance). The earlier pauses weren't sleep. The WSL
  settings use mirrored networking (`.wslconfig`), unproven as the cause and left unchanged.
- **The database is down** (Postgres exited 255 about 8 hours ago, at the WSL shutdown), so Nakama keeps restarting.
  Its data is in the Docker volume `pgdata`, not on C:.
- **The ecology test tool deletes the tested zone's save** (`run_config.py:162-173`).
- **Server starts make a backup;** retention keeps the newest 10, plus the newest of each of the last 7 days and 4
  weeks (`backup.go:12`). 12 backups exist; the newest is from 2026-10-01.
- **The Unity Editor is closed** (no lockfile). The test player was built at 20:34 on 2026-09-30, 17 minutes before
  the last client commit `5e16fe00` (character entry and crossing), so it may be stale.
- **Hook gates:**
  - `nakama/modules/world/*.go` needs frontier-sync, bug-spawning, perf-tuning and test-changes read;
  - `docker compose` needs run-backend;
  - `run_config` needs ecology-tuning;
  - Unity builds and test runners need test-changes;
  - the pre-commit doc-drift check refuses code without its mapped architecture doc.
- **Zone size:** the server reads it from data. The client hard-wires 256 in `DarknessOverlay.cs:21`,
  `TilemapManager.cs:31` and `WaterAnimated.shader:28`, so a 512 zone needs those raised first.

**The order** (each step is committed and pushed before the next; the PROGRESS log is updated after each):
0. **Preflight:**
   - the drive is readable;
   - `git status` is clean;
   - read the gate skills (run-backend, bug-spawning; the others are already read);
   - copy `BugFarmer_backups/world/*.json` into `BugFarmer_backups/world_keep_2026-10-04/` (copy only).
1. **Part 0.** Records, plans and memory, then commit, push and merge into `main` per the git guidelines.
2. **Part A, the app:**
   - data seeding, the builder, the template, the tests, the screenshots, all in tested commits;
   - a dry-run export of the marks to `BugFarmer_backups`;
   - the rehearsal on a throwaway artifact (made-up data only).
   **STOP before publishing over the real items address.** That waits for the owner's pause and confirmation in the
   morning.
3. **The server, for S1 and S2:**
   - `docker compose up -d` per run-backend;
   - verify Postgres is healthy, Nakama logs "module loaded", and the start-up backup was written;
   - if Postgres doesn't recover cleanly: STOP and report. No repair attempts; never `down -v`.
3b. **Rebuild the headless test player before any run.**
   - The Editor must be closed (no `BugFarmerClient/Temp/UnityLockfile`). Command: `Unity.exe -batchmode -quit
     -nographics -projectPath BugFarmerClient -executeMethod SyncTestBuild.Build`, with `-logFile` as a C:/ path.
   - Verify through the managed DLL: a fresh modification time, and `strings` finds `EnterWorldWithRetry` from commit
     `5e16fe00`.
   - If the Editor is open or the build fails: STOP the server-run steps, report, and continue with Part A only.
4. **A bench copy of the village**, made by a committed tool (`tools/ecology/make_bench_zone.py`): it copies
   `village_21_B`'s authored files into a lab zone at a lab grid square. **All overnight runs use the bench copy;
   the real village's save is never touched.** The tool refuses real zone ids.
   - The copy is named `bench_village` (the exact-prefix wipe `bench_village:` can't match `village_21_B`), with
     `"ephemeral_swarms": true` so it never keeps a save (bug-spawning skill).
   - Verify a fresh start in the log: "Seeded world with N swarms", N > 0.
5. **S1, the bug-count part:** profiled `run_config` runs on the bench village at 1×, 2× and 4× the caps, using the
   built-in profiler and dashboard. One run at a time.
   - Before each run, `git status` is clean. After each run, check that `nakama/data` was restored. If it wasn't:
     STOP and report (no `git checkout`).
   - The numbers go to `docs/product/investigations/scaling-2026-10-04/`.
   - The 512-zone part is reported as "needs the three 256 limits raised", and not changed tonight.
6. **S2, part 1:**
   - death causes for player kills and catches in `ecology_stats.go`, plus their call sites, with the mapped doc in
     the same commit;
   - Go tests in Docker;
   - a 48-game-day baseline run on the bench village (about 2 hours), giving the "before" population charts.
   The pressure bots need a new headless-player mode (C#), so they wait for the next session.
7. **Only if everything above finished:** run the two-player late-join check (co-located and spawn-apart) with the
   fresh build, as a health check of today's code.

**Stop rules:**
- If the drive can't be read, stop all work; the last push holds everything.
- If any gate fails, stop that line of work, record it in PROGRESS, and continue only with independent steps.
- Nothing destructive. No publishing over the real address. No paid image calls. No design decisions that belong to
  the owner.
- If a permission prompt blocks a step, it simply waits.

**Ready in the morning:**
- Part 0 done, with `main` up to date;
- the app built and rehearsed, ready to publish after the owner's pause;
- S1's bug-count numbers;
- the kill and catch causes;
- the village bench baseline charts;
- a short report in PROGRESS and in chat.

## Acceptance criteria (each with how it's verified)
- [ ] **Part 0 recorded.** D83 and the D46 correction checked against the owner's history; §03 and §04 at
  `rework`; the Bug Stick row changed after its marks were read. *Verified by:* the `git show` diff and grep.
- [ ] **`main` up to date.** *Verified by:* `git rev-parse main` = `origin/main`.
- [ ] **Marks intact; nothing the owner wrote vanishes.** *Verified by:* a field diff of the exports, and the "Older
  notes" count.
- [ ] **The app works.** *Verified by:* the accounting report, the planted-fault tests, the stress and screenshot runs,
  the rehearsal, and the owner's note read back.
- [ ] **S1 reported.** *Verified by:* a numbers page in the app (CPU, snapshot, bandwidth, tick at 1×, 2× and 4×, and
  256 vs 512), a cost per server system, and a hash match for the food trial.
- [ ] **S2 reported.** *Verified by:* kill and catch causes in ECOSTATS, and pressure runs showing collapse speed,
  warning signs and recovery.
- [ ] **S3 done.** *Verified by:* the arena with spawn panel, stations, observer and fight modes, used by the owner;
  the fighter bot's numbers; a captured clip.
- [ ] **The zone-design gate checks outputs.** *Verified by:* the hook self-test and a fresh-session block.
- [ ] **The village slice done.** *Verified by:*
  - the owner played and signed it off;
  - the late-join gate passed during fights and nest defence;
  - C1's two-player hit test;
  - 48-day runs showing living cycles and recovery;
  - the feel bars met.
- [ ] **Each later slice done:** the same checks, per slice.
- [ ] **Each zone's list and item batch settled.** *Verified by:* the owner's approvals and marks, D-entries, and
  `decided` dates.

## Deferred decisions
- **Mine, on evidence:** what moves to players' computers (from S1); per-system technical designs; the C1 cheating
  trade-off (co-op against the world, so loose server checks).
- **The owner's, later, each with its evidence:** zone size (after S1's numbers); merging the two ant zones or not
  (after S1); the behaviour principles and feel bars; each system's design and variant; each zone's list; item
  batches; band values. (Q1–Q6 were all answered on 2026-10-04.)

## Out of scope (separate plans later)
UI and onboarding, graphics and art production (no paid image calls here), audio, fishing, and the zone layout
rebuilds (roadmap Phase 2). Building the player's own kit (bows, stamina) gets its own build plans, scheduled
alongside.

## Files
- **New:**
  - `docs/plans/finish-bugs-zones-items.md`, `docs/plans/review-app.md`;
  - `tools/gdd/{build_app.py, app.template.html, app_save.js, app_views.js, app_maps.js, seed_registry.py, assign_keys.py, marks_diff.py, marks_restore.py}`;
  - `tools/gdd/tests/*`;
  - `docs/gdd/data/{zones,bugs,phrases}.jsonl`;
  - later: the arena zone and its spawn panel, the scaling and pressure scenarios, the fighter bot, the capture mode,
    `docs/gdd/zones/_TEMPLATE.md`, `docs/gdd/data/layouts/*.json`.
- **Changed:**
  - `CLAUDE.md`; `docs/gdd/README.md`;
  - `docs/gdd/*.md` (keys; §03 and §04 status; P6);
  - `docs/gdd/item_table.jsonl` (Bug Stick); `docs/gdd/bug_lineups.jsonl`;
  - `docs/product/economy/DECISIONS.md` (D83; the D46 note);
  - `docs/product/{ROADMAP,BACKLOG,CHANGELOG}.md`;
  - `docs/product/architecture/architecture_bug_behaviour.md`;
  - the candidates research file;
  - `docs/plans/README.md`;
  - `tools/gdd/build_page.py`; `tools/README.md`;
  - later: `ecology_stats.go`, the combat skill and docs, zone-craft and author-zone, `gate_authoring_edits.py`.

## Test plan
- **The app:** builder checks and planted faults; stress and screenshots; export, publish and diff; the test note.
- **S1:** profiled runs at each size, plus the food-trial hash match. **S2:** pressure runs with kill causes.
  **S3:** the arena and the fighter bot.
- **Behaviour:**
  - Go tests in Docker;
  - `sim-determinism`;
  - the late-join gate during the behaviour;
  - the two-player hit test (C1);
  - 48-day ecology runs;
  - the owner's play.
- **Before claiming anything done:** `certainty-assessment`.

---
## Conformance table (filled in as each part is finished)
| Acceptance criterion | Evidence (file:line / command output) | Test / gate |
|---|---|---|
| … | … | … |
