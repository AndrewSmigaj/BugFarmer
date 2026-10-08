# The behaviour check: what it can see (Stage 1.0d, 2026-10-06)

Part of `docs/plans/village-slice.md`, Stage 1.0. The tool is `tools/ecology/behaviour_check.py` (tests:
`tools/ecology/test_behaviour_check.py`); how to run it is in the `test-changes` skill, §3.4.

## What it is for
Stage 1 makes the bug simulation faster without changing what the bugs do. Three checks share that job:
- **The equivalence check** (`tools/netcode/equiv_check.py`): for a speed-up that should give exactly the same
  results, two builds must produce identical fingerprints every tick. Proven 2026-10-06 (a 2.5 → 2.6 change to one
  radius was caught from the first tick).
- **A side-by-side check, built with each speed-up that uses a different method:** the old and new methods answer
  the same questions on the same state, every tick, and every disagreement is counted. Far more sensitive than
  comparing whole runs, because it never depends on two runs unfolding alike.
- **The behaviour check (this page): a coarse safety net** over the whole game. It runs the old and new builds on
  the same five seeds with the bug count held steady, and flags a behaviour only when it changed the same way on
  every seed, by over 4 standard errors of the per-seed differences and by over 15%. The owner chose this role on
  2026-10-06, after the calibration below showed what it can and cannot see.

## Why it is a coarse net
- **A seed fixes where everything starts, not how a run unfolds.** For most behaviours, the same build on the same
  seed run twice differs about as much as two different seeds do (wasps landing at food, seed 1: 0.25 then 10.92 per
  1,000 bug-ticks). Only what the layout decides repeats closely (centipede strikes: the repeat spread is a tenth of
  the seed-to-seed spread). So each check needs several runs, and rare behaviours stay noisy.
- **Rare behaviours need big changes to show.** Flies are landed at food 0.04% of the time in these runs; a change to
  landing must more than double it before five seeds can tell.

## The smallest change it can see, per behaviour
*Caution (2026-10-06, after the third catching test): these limits are about half the real ones.*
From the same build run twice on seeds 1–5 (held count of about 1,000 bugs, 600 s runs at 6× speed, game-days 2–4):
the change needed to clear both the 4-standard-error bar and the 15% floor. The last column is the food-radius
2.5 → 4.0 copy, which the check did NOT flag: every change there is under its limit. Behaviours that never happen in
these runs (births in a held run, beetles and millipedes hunting) are left out.

| species | measure | base mean | smallest change it can see | radius-4.0 copy |
|---|---|---|---|---|
| butterfly_meadow | curious_per_1k (client) | 71.9 | 30% | +12%, 4 up / 1 down of 5 seeds, 0.8 se |
| butterfly_meadow | curious_starts_per_10k (client) | 0.0417 | 27% | +23%, 4 up / 1 down of 5 seeds, 1.3 se |
| butterfly_meadow | breed_per_1k (server) | 54.7 | 118% | +7%, 3 up / 2 down of 5 seeds, 0.1 se |
| butterfly_meadow | feed_per_1k (server) | 18.8 | 81% | +14%, 3 up / 2 down of 5 seeds, 0.4 se |
| centipede_garden | attack_per_1k (client) | 302 | 52% | -8%, 2 up / 3 down of 5 seeds, 0.4 se |
| centipede_garden | attack_starts_per_10k (client) | 0.1 | 114% | +5%, 2 up / 3 down of 5 seeds, 0.2 se |
| centipede_garden | corpses_per_10k (client) | 0.915 | 36% | -1%, 3 up / 2 down of 5 seeds, 0.1 se |
| centipede_garden | eating_per_1k (client) | 2.97 | 35% | +1%, 3 up / 2 down of 5 seeds, 0.1 se |
| centipede_garden | eating_starts_per_10k (client) | 1.19 | 35% | +1%, 3 up / 2 down of 5 seeds, 0.1 se |
| centipede_garden | hunting_per_1k (client) | 915 | 15% | +4%, 4 up / 1 down of 5 seeds, 1.5 se |
| centipede_garden | hunting_starts_per_10k (client) | 2.34 | 28% | -5%, 2 up / 3 down of 5 seeds, 0.5 se |
| centipede_garden | landed_per_1k (client) | 0.66 | 235% | +97%, 4 up / 1 down of 5 seeds, 1.8 se |
| centipede_garden | landed_starts_per_10k (client) | 0.22 | 149% | +80%, 3 up / 2 down of 5 seeds, 1.6 se |
| centipede_garden | lunge_per_1k (client) | 14 | 44% | -6%, 2 up / 3 down of 5 seeds, 0.3 se |
| centipede_garden | lunge_starts_per_10k (client) | 34.6 | 46% | -6%, 2 up / 3 down of 5 seeds, 0.3 se |
| centipede_garden | prey_claimed_per_10k (client) | 5.81 | 20% | -6%, 2 up / 3 down of 5 seeds, 1.3 se |
| centipede_garden | strikes_per_10k (client) | 5.81 | 20% | -6%, 2 up / 3 down of 5 seeds, 1.3 se |
| centipede_garden | windup_per_1k (client) | 27.7 | 46% | -6%, 2 up / 3 down of 5 seeds, 0.3 se |
| centipede_garden | windup_starts_per_10k (client) | 34.6 | 46% | -6%, 2 up / 3 down of 5 seeds, 0.3 se |
| centipede_garden | kills_fly_common_per_bugday (server) | 0.978 | 58% | -13%, 2 up / 3 down of 5 seeds, 0.8 se |
| fly_common | flee_per_1k (client) | 0.0886 | 238% | +14%, 3 up / 2 down of 5 seeds, 0.2 se |
| fly_common | flee_starts_per_10k (client) | 0.126 | 233% | +15%, 3 up / 2 down of 5 seeds, 0.2 se |
| fly_common | landed_per_1k (client) | 0.354 | 254% | +22%, 4 up / 1 down of 5 seeds, 0.4 se |
| fly_common | landed_starts_per_10k (client) | 0.202 | 246% | +17%, 4 up / 1 down of 5 seeds, 0.3 se |
| fly_common | breed_per_1k (server) | 1.48 | 185% | +11%, 1 up / 4 down of 5 seeds, 0.3 se |
| fly_common | d_predation_per_bugday (server) | 0.0871 | 66% | -16%, 2 up / 3 down of 5 seeds, 0.8 se |
| fly_common | feed_per_1k (server) | 2.74 | 184% | +7%, 2 up / 3 down of 5 seeds, 0.2 se |
| wasp_common | corpses_per_10k (client) | 0.128 | 151% | +34%, 4 up / 1 down of 5 seeds, 0.8 se |
| wasp_common | eating_per_1k (client) | 0.427 | 232% | +43%, 4 up / 1 down of 5 seeds, 0.7 se |
| wasp_common | eating_starts_per_10k (client) | 0.172 | 259% | +39%, 4 up / 1 down of 5 seeds, 0.7 se |
| wasp_common | hunting_per_1k (client) | 991 | 15% | -1%, 1 up / 4 down of 5 seeds, 1.9 se |
| wasp_common | hunting_starts_per_10k (client) | 1.08 | 133% | +18%, 3 up / 2 down of 5 seeds, 0.6 se |
| wasp_common | landed_per_1k (client) | 3.68 | 232% | +108%, 4 up / 1 down of 5 seeds, 2.0 se |
| wasp_common | landed_starts_per_10k (client) | 1.16 | 277% | +155%, 5 up / 0 down of 5 seeds, 2.6 se |
| wasp_common | prey_claimed_per_10k (client) | 1.76 | 186% | -22%, 2 up / 3 down of 5 seeds, 0.6 se |
| wasp_common | strikes_per_10k (client) | 1.76 | 186% | -22%, 2 up / 3 down of 5 seeds, 0.6 se |
| wasp_common | kills_fly_common_per_bugday (server) | 0.278 | 113% | -34%, 2 up / 3 down of 5 seeds, 1.1 se |
| wasp_common | trip_home_per_bugday (server) | 0.2 | 151% | -31%, 3 up / 2 down of 5 seeds, 0.7 se |

`client` = counted on the player's computer (per 1,000 bug-ticks in a state, or per 10,000 bug-ticks for starts and
reports); `server` = the server's daily counts (per bug-day, or per 1,000 bug-ticks for feeding and breeding).

## The calibration, in order
1. **Natural ecology, 3 game-days, 5 + 3 seeds of the same build:** 14 false alarms under a "±3 standard deviations"
   rule: the village's first days go different ways from seed to seed.
2. **Held count, 280 s, unpaired:** a false alarm on the same build and the radius change missed. The runs reached
   only game-day 1 (skipped), so the server half judged nothing; group averages over different seeds hid the change;
   "too rare" counted bug-ticks, so one long wasp attack looked well counted.
3. **Held count, 600 s, paired by seed, starts counted** (15 runs: base, radius 4.0, base again):
   **no false alarms** (38 behaviours judged); **the radius change not caught** (under the limits above).
4. **The catching test (decided before it ran):** centipedes half as fed by each kill (`feed_per_kill` 45 → 22.5,
   config `s10_behave_1000_hunt`), seeds 1–5, against the base runs. It passes only if the check flags centipede
   strikes, prey claimed, or fly kills going up. **Inconclusive:** strikes did not rise and kills fell 26% (my
   prediction was wrong); the one flag was flies breeding 46% less on every seed. But the test runs were compared
   with base runs made hours earlier on a machine that had slowed (client 58.8 against 59.7–60.4 ticks/s), so the
   check now has a **pace gate** (groups more than 1% apart in client pace are not compared) and the rule is: run
   the two builds interleaved, in one session.
5. **The catching test again** (decided before it ran): interleaved, fresh seeds 6–10; passes only if the pace gate
   passes and fly breeding or feeding is flagged going down. **Failed:** the pace gate passed (0.01% apart) and
   nothing was flagged (fly breeding −10%, feeding −12%, centipede strikes −8%, kills +9%, none the same way on
   every seed). So the first try's flag was the slower machine, and this change barely moves behaviour in held
   runs. **The check has not yet been shown to catch a real change.**
6. **The catching test, third try** (decided before it ran): bugs stay on a corpse for 50 ticks instead of 25
   (`BugAgent.FeedTicks`), both builds from the same code; interleaved, fresh seeds 11–15. Passes only if the pace
   gate passes and centipede eating time is flagged going up. **Failed, narrowly:** eating time +65%, up on all five
   seeds, at 3.7 standard errors (the bar is 4); pace 0.11% apart. One run was a broken client (a resync loop from
   tick 0, 2.9 ticks/s), set aside and re-run; the pace gate now names such runs.
7. **The two-step check (the owner's choice, 2026-10-07):** step 1 marks a change that goes the same way on all five
   seeds, over 15% and over 2.78 standard errors (the textbook 5% bar for five seeds) as a SUSPECT; step 2 runs five
   fresh seeds and confirms it over all ten (the same way on at least nine, over 4 standard errors, over 15%). On the
   existing runs the same-build pair raises no suspect and the longer-eating copy raises two (centipede eating +65%,
   wasp eating +128%). **Validation passed (2026-10-07):** step 2 on seeds 16–20 confirmed centipede eating, +81%,
   up on all ten seeds at 6.6 standard errors. Wasp eating (+114%) was not confirmed (seven of ten seeds, 2.3 standard
   errors): a real change in a rare, noisy behaviour stays below what the check can see. **The check is proven for
   common behaviours; for rare ones, the side-by-side check is the tool.**

8. **First real use (Stage 1.1, 2026-10-07):** the identical steps 1–5 against the build before Stage 1.1, and the
   ordinal-order change (step 6, identical in the simulation by the equivalence check) against step 5; seeds 21–25,
   the three builds always in the same order per seed. Step 1 raised one SUSPECT for the batch (butterfly breeding
   share +104%) and one FLAG for step 6: centipede hits on the player +115%, up on all five seeds at 4.7 standard
   errors — from 13 events to 28. Both builds of each pair are identical in the simulation, and hits on the player are
   detected from drawn positions, which depend on frame timing. Step 2 on seeds 26–30, with the build order rotated
   per seed (decided and committed before it ran): **nothing flagged over the ten seeds in either comparison**; in the
   rotated round step 6 had the fewest centipede hits (2, against 10 and 13), and the hits by run position were
   7 / 10 / 8. So the step-1 flag was chance on very few events. What it shows: (a) a metric is judged when either
   side reaches the 20-event floor, so 13 events on one side were enough to be judged — requiring the floor on both
   sides is a candidate for the next calibration, not changed now; (b) **the build order is rotated per seed from now
   on** (a fixed order can only add a bias, never remove one). Two of the 30 runs were broken (one machine stall, one
   startup fault, `../../BACKLOG.md`) and run again; one more run hit the startup fault and recovered at full pace.

**Where this leaves the check (2026-10-06):** it raises no false alarms, and it misses even a certain, consistent
+65% change with five seeds. The "smallest change it can see" table above was worked out from the same-build runs
and is about half the real figure (it predicted 35% for centipede eating; a real +65% fell short). Ways to make it
useful, for the owner to choose: more seeds (ten per side: about 3¾ hours of runs per check), longer runs, or a two-step
check (a lower bar marks a change as suspect, and five fresh seeds must confirm it).

Raw runs: `tools/_generated/scaling/2026-10-06-paired/` (git-ignored; `check_control.md`, `check_planted4.md`).
