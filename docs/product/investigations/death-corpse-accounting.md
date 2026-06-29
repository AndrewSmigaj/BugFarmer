# Investigation: #22 population plummets but barely any corpses — are they generated?
_status: READY (answered; one design choice for predation) · investigated 2026-06-28 · investigate-only_

## Debrief (read me first)
- **Direct answer:** corpses **ARE generated** for starvation & old-age (and director-culls). Verified: all
  three call `killBugsNaturally` → `spawnCarcass` (`handlers_combat.go:298`) which drops the species'
  `dead_<species>` ground item. The ONE exception is **predation** — `killBugsInSwarm` (`predation.go:339`)
  drops only `KillDrops`, **no carcass**. So your hypothesis "not generated on starvation/old-age" is **false**;
  they are generated.
- **Why you saw "barely any corpses" anyway — two real reasons:**
  1. **They were invisible.** The `dead_*` carcass sprites were missing in your playtest build, so carcasses
     spawned but drew nothing. **I fixed this earlier today (commit 9b61b95).** Re-test — they should now show.
  2. **They're eaten fast.** Carcasses are `food_value:10` (edible) with no rot timer, so decomposers
     (millipede/beetle) and flies consume them quickly → few exist at any instant. Expected food-web behavior.
- **Your "few wasps and carrion" case:** few wasps ⇒ little predation ⇒ flies were dying by starvation/old-age,
  which DO make carcasses — that you couldn't see them is reason (1). Consistent.
- **Design choice (ties to #20):** predation leaving NO corpse is intentional today, but #20 wants "the corpse
  appears + the predator feeds on it." Recommend: make predation kills ALSO `spawnCarcass` (then the feeding
  pause has something to feed on). Sim-touching → frontier-sync + determinism gate.
- **Certainty:** death→carcass mapping **95%** · "invisible + eaten = the scarcity" **80%** (re-test with the
  sprite fix confirms). **Needs your decision:** should predation drop a carcass too (for #20)? **Status:** `READY`.

## 1. Issue
> "investigate if wasps and flies are dying of starvation and old age and if so why … chart plummets but barely any corpses … are the corpses not getting generated when dying of starvation or old age?"

## 2. Death-cause → carcass map (verified)
| cause | path | carcass? |
|---|---|---|
| old age | `processNaturalDeath` (`match.go:2020/2044`) → `killBugsNaturally` | ✅ yes |
| starvation | `processStarvation` (`:2068/2090`) → `killBugsNaturally` | ✅ yes |
| director cull | `directorCull` (`ecology_director.go:141`) → `killBugsNaturally` | ✅ yes |
| **predation** | `applyPredationStrike` (`predation.go:339`) / combat (`handlers_combat.go:118`) → `killBugsInSwarm` → `spawnKillDrops` | ❌ **no carcass** |
`spawnCarcass` fires only when `species.CarcassItem != ""` — all 6 species set it (`dead_fly`/`dead_wasp`/…).

## 3. Recommendation
1. **Re-test with the sprite fix (commit 9b61b95)** — confirm carcasses are now visible after starvation/age
   deaths. Most of "barely any corpses" should resolve.
2. If you want predation to leave corpses (and it underpins #20's feeding pause): add a `spawnCarcass` to
   `killBugsInSwarm` (or a `carcass_on_predation` flag). This changes the decomposer food supply → run
   `tools/sim-determinism` + the sync-harness + re-check the ecology bands (`ecology-tuning`).
3. Optional telemetry: surface `Stats.recordDeath(cause)` (deaths-by-cause already tracked) in the chart so
   "what killed them" is visible — directly answers this class of question next time.
