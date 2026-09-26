I'll explore the BugFarmer repo to verify this persistence design. Let me start with parallel searches across the key files.

---

Let me look at the entities package, swarm struct, and MatchInit in parallel.

---

Let me read the core files: swarm struct, zone_persist, state init, and MatchInit.

---

Let me examine state init, seed/epoch machinery, and swarm ID minting.

---

Let me look at MatchInit, the ZoneState/epoch machinery, and swarm ID minting.

---

Let me look at ZoneState struct, the late-join snapshot path, and how the client learns the tick.

---

Let me read the WorldInit/seed-baseline broadcast path and the rest of MatchInit.

---

Let me read handlers_env.go (day/night + weather), the seed-baseline builder, and grep for cadence/drift math.

---

Let me find cadence math, drift-check windows, autosave, and the relinkNestResident calls.

---

Let me read the relink logic, the match-loop cadences/drift sampling, and the client tick init.

---

Let me check the client tick handling and the drift-sampling window.

---

Let me check the client's authority/WorldInit bootstrap and the drift margin constant.

---

Let me verify LastZoneSaveTick init, tick fields in other restored entities, and any tests touching MatchInit/restoreSwarms.

---

Let me quickly verify crop growth timing and what the flagged tests actually exercise.

---

Let me do a final check for any storage size limits/guards documented, and confirm no independent epoch for swarm stamps.

---

I have everything needed. Here is my verification report.

---

# Verdict: "Resume TickCount + full-fidelity swarms" is SAFE

No real breakers found. Every tick-stamp in the codebase is anchored to `state.TickCount` (pattern `state.TickCount + delta`), never to an independent epoch or wall clock. The client learns the tick as an opaque `long` from the server. Preserving swarm IDs eliminates the only cross-entity reference that dangles today. The clamps and the relink exist *solely* to paper over the `TickCount→0` reset and the fresh-ID rebuild; both disappear under this design.

The one thing to also carry over (see §1) is `state.LastRolloverDay` — it is already written to `:meta` but not currently re-read; without it the first tick after resume fires one idempotent day-rollover. Not a breaker, but restore it for cleanliness.

---

## 1. TickCount init + absolute-time assumptions

**Init:** `nakama/modules/world/state.go:382` — `TickCount: 0` in `NewWorldState`. The only writer in the loop is `nakama/modules/world/match.go:829` — `worldState.TickCount++`. MatchInit never sets it to anything but the `NewWorldState` zero. So the *only* change needed is: after `prefetchZoneState`, set `state.TickCount = meta.SavedTick` (a new field on `ZoneMeta`).

**Every tick consumer, and why each survives a large starting tick:**

- **Day/night modulo** — `handlers_env.go:98` `state.TickCount % DayLengthTicks`; `:117` `(state.TickCount + state.DayOffsetTicks) % DayLengthTicks`; client `DayNightController.cs:10` `((SimulationTick + DayOffsetTicks) % 8400)`. Modulo is phase-correct at any magnitude. `DayLengthTicks = 8400` (`match.go:51`).
- **Day rollover is epoch-compare, NOT modulo** — `handlers_env.go:86-92` `AdvanceDayIfNeeded`: `currentDay := (s.TickCount + s.DayOffsetTicks) / DayLengthTicks; if s.TickCount > 0 && currentDay != s.LastRolloverDay`. With a large resumed tick and a *stale* `LastRolloverDay=0`, this fires once on the first tick — and the comment at `:84` guarantees "the resets it guards are all idempotent-safe." Restoring `LastRolloverDay` from `:meta` (already persisted, `zone_persist.go:440`) removes even that one-shot.
- **Cadence gates** (`match.go`): `%100` (:1442,:1447,:1543,:1547,:1568), `%300` drift (:1520), `%30` (:1169), `% DirectorIntervalTicks` (:1439), `handlers_player.go:142` `%regenIntervalTick`, `craft_stations.go:429` `Progress%20`. All periodic `== 0` tests — a large start only shifts *which* absolute ticks are phase-0, never correctness.
- **Autosave is a delta, not modulo** — `match.go:836` `worldState.TickCount - worldState.LastZoneSaveTick >= zoneAutosaveTicks` (`LastZoneSaveTick` inits 0, `state.go:211`). Resuming large → fires one early save on the first eligible tick. Harmless.
- **Drift sampling window** — `match.go:3012` `sampleTick := state.TickCount - driftSampleMargin` (`driftSampleMargin = 20`, :2999); guarded `if sampleTick < 0 { return }`. Large start passes the guard immediately; `LastSampleTick`/`DriftChecks` maps init empty and are keyed relative. Fine.
- **Weather until-ticks** — `handlers_env.go:217,225,276` all `state.TickCount + …`; compared `TickCount >= X` (:252,:257,:263). Weather is *not* persisted (resets to none/`0` on restart, `zone_persist.go:251-252`), and none/0 is valid at any tick.
- **No wall-clock comparison of TickCount anywhere.** `CreatedAt`/`SavedAt` use `time.Now().Unix()` but are never compared against `TickCount`; the sim is a pure function of `(seed, ticks)` (`state.go:73-75`).

**Client:** the tick flows through as opaque. `match.go:567` ZoneAuthority `AuthoritativeTick: worldState.TickCount` → `SwarmManager.cs:1848-1849` `_authoritativeTick = authoritativeTick; _simulationTick = authoritativeTick`. Late-join: `SwarmManager.cs:1496-1497` `_simulationTick = msg.snapshot_tick`. `WorldInit` (`match.go:499-504`) carries seed + tick. Client `%50` uses (`:407,:562`) are log-only. A 5,000,000 start simply becomes the client's starting `_simulationTick`. **Nothing client-side assumes ticks start near 0.**

## 2. SwarmState field inventory (`entities/swarm.go:10-117`)

Legend: **V** = persistable value · **T** = derived/transient (safe to drop) · **R** = reference. All tick-stamps are `TickCount`-relative (no independent epoch) → **valid as-is under resume**.

| Field | line | Class | Note |
|---|---|---|---|
| ID | 11 | **V (identity)** | the map key; **must** be preserved to kill the relink |
| SpeciesID | 12 | V | |
| Position | 13 | V | server-authoritative; client re-derives from seed/legs |
| Radius / WanderRad | 14,19 | V | derivable from species (`SwarmRadius`/`WanderRadius`) |
| Count | 15 | V | |
| Facing / Velocity | 16,17 | T | recomputed every `Move` (`:270,:297`) |
| HomePos | 18 | V | tether point (nest pos for members) |
| ReproduceCooldown | 21 | V | seconds, not ticks |
| ConditionValue / CurrentHP | 24,25 | V | |
| Phase | 28 | V | already in lossy save |
| Satiation / ReproductionMeter | 29,30 | V | already in lossy save |
| CompostCooldown / StarveTimer | 31,32 | V | seconds |
| **DeathTick** map[int]int64 | 36 | V (tick-stamps) | per-bug absolute-tick; **JSON-serializable** (Go marshals int keys as strings); valid under resume |
| TargetX/Y / HasTarget | 39-41 | T | regenerated by `Think` |
| **NextThinkTick** | 44 | V (stamp) | `TickCount`-relative |
| RelocateReadyTick | 45 | V (stamp) | |
| TargetFoodID/X/Y/Depletable | 49-52 | T | Think cache, re-validated vs registry |
| ForageMode / ModeUntilTick | 56,57 | V / stamp | |
| SpeedMult | 67 | T | per-leg; 0=unset |
| TargetPreyID | 73 | R/T | prey swarm id — transient hunt cache, safe to clear |
| HuntStartTick/LastStrikeTick/FeedUntilTick/LastAttackTick | 74-80 | V (stamps) | `FeedUntilTick` comment (:76-78) already says drop-on-restart is fine either way |
| **NestKey** | 85 | **R** | `"gx,gy"` — **position-keyed, not id-keyed → survives restart intrinsically** |
| CarryingBrood | 86 | V | |
| HomingStartTick / DefendUntilTick | 87,88 | V (stamps) | |
| DefendTargetID | 89 | R/T | player id — clear (sessions change) |
| ActionState + ActionUntilTick/SurgeCooldownUntil/GnawNextTick/GnawCooldownUntil | 95-106 | T + stamps | centipede FSM; stamps `TickCount`-relative |
| WindupTargetID / GnawKey | 98,104 | R/T | player id / fence cell-key |
| WindupStartX/Y / WanderHeading / ClampedLegStreak / TurnLegsLeft | 99-103 | V | |
| **RemovedBugIDs** map[int]bool | 109 | V | comment says "not serialized" but it **is** serializable; already shipped over the wire as a slice via `GetRemovedIDs()` (`:202`) in the seed baseline |
| **NextBugID** | 110 | V | per-swarm counter — **must persist** for id continuity |
| **BugHP** map[int]int | 116 | V | sparse per-bug HP; JSON-serializable |

**Client-derived vs server-learned:** the client derives **per-bug positions** independently from `(worldSeed, swarmId, bugId)` seeded at the swarm centre (`match.go:2714-2721`) and marches them along `SWARM_SET_TARGET` legs. It **learns from the server**: swarm centre/leg, `Count`, `Phase`, `Facing`, `NextBugID`, `RemovedIDs` (via `SwarmData`, `match.go:2736-2748` / `:1489-1501`). None of the server-only fields (Satiation, meters, DeathTick, BugHP, action FSM) are client-visible, so persisting them at full fidelity is invisible to the client.

**Confirmed:** no swarm tick-stamp references an epoch that resets independently of `TickCount` — every write is `state.TickCount + const` (e.g. `centipede.go:113,133,193,272,295,319`; `nests.go:656,657`; `handlers_player.go:58,59`).

## 3. Restart → client boundary

Server-restart flow for the first client is entirely tick-and-id-opaque:
- `match.go:498-504` `WorldInitMessage{WorldSeed, Tick: worldState.TickCount}`.
- `match.go:564-575` ZoneAuthority with `AuthoritativeTick: worldState.TickCount`, `LastEventSeq: -1`, and `Swarms: buildSwarmSeedBaseline(...)`.
- `buildSwarmSeedBaseline` (`match.go:2722-2766`) copies `swarm.ID` **verbatim** into `SwarmData.ID` (:2737) plus `NextBugID`/`RemovedIDs`. Preserved string IDs + a large `TickCount` pass straight through — the client treats them as opaque (§1). The hydrated "live leg" is read from `zone.InfluenceLog`, which is **empty** after restart, so restored swarms get their first leg from their first live event (:2749-2750) — identical behavior to today.

**Ledger/frontier is fully fresh per match run and untouched by persistence:**
- `NextSeq` + `InfluenceLog` live on `ZoneState` (`state.go:256-257`), which is created fresh by `GetOrCreateZone` — never persisted.
- On zone-empty, `match.go:729-740` resets `NextSeq = 0`, `InfluenceLog`, `LatestSnapshot*`, authority, `PendingInfluence`.
- The "epoch" in this codebase is only the day-rollover epoch (`LastRolloverDay`, `state.go:124`), not a ledger/resync epoch. So nothing about persistence touches the frontier machinery.

## 4. Current save/restore machinery to be simplified (`zone_persist.go`)

- **`:meta` record shape** — `ZoneMeta` (`:168-174`): `Version, ZoneID, LastRolloverDay, ModifiedChunks[], SavedAt`. **This is the natural home for `SavedTick int64`** (add one field; it's already built at `:438-441` where `LastRolloverDay` is captured).
- **Lossy save** — `SwarmSave` (`:87-95`): only `SpeciesID, WorldX, WorldY, Count, Phase, Satiation, Repro`. The doc comment at `:83-86` explicitly states it drops combat/think/action + bug-id tracking to "sidestep the TickCount-reset + not-serialized-RemovedBugIDs landmines" — i.e. **the lossiness exists only because of the two things this design removes.** `buildSwarmSave` (`:106-121`) / `ZoneSwarmSave` (`:99-103`).
- **`restoreSwarms` + id-minting** — `:127-164` calls `spawnSwarmAt` (`handlers_bugs.go:91-127`) per saved swarm, which **mints a brand-new ID: `fmt.Sprintf("swarm_%s", id.String()[:8])`** (`handlers_bugs.go:102`; the split path is identical, `match.go:2309`). This fresh-ID rebuild is exactly why the relink exists.

## (c) id-counter collision answer

**There is no integer swarm-id counter — so there is nothing to collide with.** Swarm IDs are UUID-prefixed (`swarm_<8 hex of uuid.NewV4()>`, `handlers_bugs.go:102` and `match.go:2309`). New swarms spawned after a restore get fresh random UUIDs; restoring preserved string IDs cannot collide with them (32-bit random suffix, a handful of swarms → negligible birthday risk). The only counter, `NextBugID`, is **per-swarm** (`swarm.go:110`), already carried in `SwarmData`, and would be persisted per-swarm — no global counter, no cross-swarm collision.

## (d) Exact deletions the simplification enables

1. **FruitTree tick-stamp clamp** — `zone_persist.go:515-517`:
   ```go
   t.LastFallTick = 0    // tick stamps are stale after a TickCount reset — clamp the gate anchors
   t.LastHarvestTick = 0
   ```
   (Retired: with resume, `handlers_farming.go:823` `state.TickCount - tree.LastFallTick >= treeFallSpacingTicks` is valid as-saved.)
2. **Nest tick-stamp clamps + id clear + relink call** — `zone_persist.go:531-542`:
   ```go
   n.RehatchAtTick = 0
   n.SmokedUntilTick = 0
   n.ResidentSwarmID = ""            // ← id clear becomes unnecessary (preserved swarm ids)
   ...
   m.relinkNestResident(state, n)    // ← the whole relink call
   ```
3. **`relinkNestResident`** — the entire function `nests.go:598-639` (proximity re-adoption) becomes dead code, because `NestState.ResidentSwarmID` still points at a live restored swarm and `SwarmState.NestKey` is position-keyed. (`ChunkSave` comment `:69-70` about the dangle also goes away.)
4. **The lossy `SwarmSave` → full `SwarmState`** — replace `SwarmSave`/`buildSwarmSave`/the `spawnSwarmAt` rebuild loop in `restoreSwarms` (`:150-161`) with a direct marshal/unmarshal of `*entities.SwarmState` (add `omitempty`/`json` tags; the maps round-trip). The landmine comments at `:83-86` and `:531-534` are deleted.

## (e) Storage size / practicality

- **No size guard or chunking anywhere** — `writeZoneRecords` (`:456-470`) and `writeZoneRecord` (`:178-192`) batch straight into `nk.StorageWrite`; no Nakama per-object size limit is referenced in the code (worth confirming against Nakama's configured `max_request_size_bytes` / storage object limit before shipping). The whole bug population is one `:swarms` object.
- **Full-fidelity size delta** is dominated by the three per-bug maps. `DeathTick`/`BugHP`/`RemovedBugIDs` scale with bug count and swarm age. `RemovedBugIDs` grows **monotonically** (added in `RemoveBugs`, `swarm.go:162`, never pruned; bounded by `NextBugID`), so a long-lived, heavily-churned swarm's set is the main bloat vector — consider a compaction/prune, though the same data already ships every `SwarmsDirty` broadcast (`match.go:1500`), so it is not new to the system. `BugHP` is sparse (damaged bugs only). Rough order: a 200-bug swarm ≈ a few KB JSON; dozens of swarms ≈ low hundreds of KB — fine for one storage object but the item to size-check.

## 5. Test-state assumptions

- `swarm_population_test.go:39` `TickCount: 1000` in `newTestState` — a nonzero base for *relative*-tick assertions (e.g. `combat_test.go:463` "T+5 since the stamp", `centipede_test.go:209` `SurgeCooldownUntil - state.TickCount`). None assert an *absolute* tick tied to init.
- `death_test.go:103` explicitly comments `newTestState(20) // TickCount = 1000`.
- `fruit_tree_test.go`, `world_env_test.go`, `ecology_director_test.go` set `TickCount` directly and iterate — all self-contained, none go through `MatchInit`.
- `initial_spawn_test.go` and `nest_test.go` build `WorldState` directly and call `spawnInitialSwarms`/nest handlers, **not** the storage-backed `MatchInit`/`restoreSwarms`. **No test asserts an absolute post-MatchInit tick.** The resume change touches only `MatchInit`'s read of `meta.SavedTick`, so existing unit tests are unaffected; a new test would cover the resume path itself.