# Zone persistence — the WorldSave document and the save queue

> System of record for HOW ZONES AND CHARACTERS SURVIVE A CRASH OR A RESTART (Terraria-style hosting: a player runs
> the server; everything persists). The WorldSave document shipped 2026-07-05 (§P); the save queue, one live copy
> per zone, saving characters with their zone and rolling backups on 2026-09-30 (D73). Code: `nakama/modules/world/world_save.go`
> (the document) + `persist_classes.go` (the enforcement) + `zone_persist.go` (the dying legacy importer) +
> `persistence.go` / `save_writer.go` / `save_batch.go` (the save queue) + `zone_lease.go` (one live copy per zone) +
> `char_registry.go` (one zone at a time per character) + `backup.go` (rolling backups).
> Characters are user-owned documents (`character_persist.go`), saved only together with the zone they are in.

## The principle
**The world saves as-is and time continues.** One `WorldSave` JSON document per zone (storage key
`<zone>:world`), marshaled whole, restored whole, and the WORLD CLOCK (`Tick`) persists with it —
so every tick-stamp anywhere in the state (tree gates, rehatch timers, smoke stamps, action
cooldowns) stays valid across the restart with **no clamps, no relinking, no lossy rebuilds**.
Those compensations existed only because the old system reset the clock and re-minted swarm
identities; both roots are gone.

## What's in the document
`Tick` (+ `LastRolloverDay`), the sky (`DayOffsetTicks`, weather kind/until/rain-at/drought),
`GroundItemSeq` (id counter — a reset counter silently overwrote restored items), `CellEdits`
(the global-coordinate SEMANTIC DIFF of every loaded chunk vs the authored zone — authored-zone
updates stay compatible with old saves), the `Gnaw` map (half-chewed fences stay half-chewed),
**full-fidelity `Swarms`** (whole `SwarmState` structs — json tags ARE the save format; identities
kept, so `NestState.ResidentSwarmID` stays valid), and every sidecar registry (crops, trees,
stations, containers, craft stations, nests, forage pools, host plants, broods, ground items).
Two swarm fields are refreshed from the live species def at load (`Radius`, `WanderRad` — a
rebalance must reach saved swarms); the player-ref field `DefendTargetID` holds a stable userID and
self-heals (`WindupTargetID` was removed with the centipede combat-brain move to the client, 2026-07-18).

## Restore (eager, at MatchInit, before any client joins)
One order, one function (`restoreWorldSave`): **(1)** the clock + scalars, **(2)** the registries, **(3)** the swarms
(+ `SwarmsBySpecies` rebuild), **(4)** every chunk referenced by a CellEdit: `LoadChunk` → apply
edits → the five init scans (all skip-if-present; tree randomness is position-hashed, so
load-order-independent). Untouched chunks keep lazy-loading on subscribe, where the same scans
start them from scratch. The zone-wide collision map sees saved fences because edited chunks are
already in memory (`chunkForCollision` is in-memory-first).

## Write: one save queue (D73, 2026-09-30)
**The rule everything rests on: stored data is always the result of writing, in order, the first N jobs of one
queue.** Each zone save is a **batch** (`save_batch.go`): the zone's document plus the character of every player
in it — and of the players leaving with it — captured at one tick on the match goroutine as bytes (frozen: later
changes can't leak in; KnownRecipes sorted, so an unchanged character encodes to the same bytes). The one queue
goroutine (`save_writer.go`) writes each batch in **one** `StorageWrite` — one transaction: all of it lands or none
does. So a crash, a restart or a backup always finds each zone and the characters in it from the same moment.

**When a zone saves:**
- **every minute while occupied** (`defaultAutosaveInterval`; runtime.env `BF_AUTOSAVE_SECONDS` for the server, a test
  zone's `autosave_seconds` for that zone) — checked by `saveIfDue` at the START of every occupied MatchLoop, on the
  state the previous call left, so a panic later in a tick can never stop saves;
- **whenever someone leaves**: MatchLeave captures each departing character before removing it, then queues ONE batch
  with the zone and everyone still in it (this replaced the per-player background save and the empty-zone save);
- **after a sleep in a bed**: `SaveRequested`, picked up by `saveIfDue` (at most one sleep save per 5 s) — never the
  character on its own;
- **at a clean stop**: see "The clean stop" below.

**The queue's rules:**
- the zone's document is written against the version the queue last wrote, or MatchInit loaded (`*` = create only,
  before the zone's first save); characters with `""` (each is live in one zone only);
- a database error never skips a batch: the same batch is retried, with growing pauses (100 ms → 5 s), until it lands,
  with a warning every 30 s;
- a refused version means something other than this queue changed the zone's save: saving **stops** (an error every
  30 s); storage keeps its last consistent state, and the next start of the server loads it;
- characters whose account was deleted are left out (storage refuses rows for a missing account);
- autosave and sleep batches are coalesced (while one waits for a zone, another is skipped); departures and final saves
  always queue; more than 100 waiting jobs is logged;
- barriers (`barrier`) and tasks (`runTask`) run in queue order: a barrier tells its caller everything queued before it
  is written; the old-format records' one-time clean-up runs in the zone's first write job.

`EphemeralSwarms` test zones skip ONLY the population (swarms + ground items) both ways; `tools/ecology/run_config.py`
WIPES the zone's storage before every tuning run so runs stay comparable — with the server STOPPED (stop → wipe →
start), since a clean stop saves the zone.

**Save cost (2026-09-30).** The document is built on the match goroutine, so it must stay cheap now that zones save
every minute. Building it diffs every loaded chunk against its authored file: `occCellEqual` first compares the
cells' bytes (a chunk loaded from its file keeps each cell's exact bytes, so an untouched cell matches without
decoding — the old path ran ~65,000 JSON decodes per save of a 64-chunk zone), and the authored files are read once
per match and kept (`WorldState.BaseChunks` via `baseChunk`, per-run, read-only). Measured on a fully loaded
village_21_B with 251 edits (`world_save_cost_test.go`): ~110 ms per save before, ~1.1 ms after — except the first
save after a zone starts, which fills the cache (~110 ms once). The byte fast path agreed with the full comparison on
all 140,600 cell pairs tested.

**The clean stop (2026-09-30).** `MatchTerminate` → `finalSave` queues the zone's last batch — the world and everyone
still in it — and waits until it is written (every batch queued before it, e.g. an earlier departure, lands first),
no longer than the grace period less a second (`terminateSaveTimeout`). It then returns **nil**: Nakama stops the
match at once, whereas a live state would keep the match running unsaved through the grace period (Nakama 3.35
`match_handler.go` `QueueTerminate`). The server's shutdown hook (`saveSystem.Shutdown`, `RegisterShutdown` in
`main.go`) stops new zone entries, then waits for the queue to drain within the grace period; Nakama runs it
alongside the zones' MatchTerminate and waits for both. **This needs shutdown time:** `nakama/data/local.yml` `shutdown_grace_sec: 15` (Nakama's
default, 0, halts every match with no MatchTerminate — so before this date no zone was ever saved on shutdown)
and `docker-compose.yml` `stop_grace_period: 30s`, which applies when the container is (re)created; check it with
`docker inspect -f '{{.Config.StopTimeout}}' bugfarmer-nakama` → 30. A crash (or turning off the PC / WSL)
still skips this save.

## One live copy per zone (D73, 2026-09-30)
A zone's save is per zone, not per world, so two matches running one zone would load and write the same save (the
roadmap's known fault 2: two players arriving at once started two copies; the debug panel's `world_create` could start
a second copy of a running zone under a new world id). `zone_lease.go`:

| Situation | What happens |
|---|---|
| A request needs the zone (`world_enter`, `world_create`, `world_join` → `ZoneMatch`) | Takes the zone's lock (a 1-slot channel, so the wait can time out). All the request's waits share one 8 s budget (`zoneEntryBudget`, rpc): Nakama cuts a request off at 10 s with no reply. |
| The zone's live copy is running (`nk.MatchGet` ≠ nil) | Reused. `world_create` / `world_join` refuse instead (`ZONE_RUNNING`): a different world must not run a second copy. |
| No live copy, or its match is gone | 1. **Retire** the old copy: from now on nothing it queues is accepted. 2. In the same critical section, queue a barrier and wait for it: everything the old copy queued before is written. 3. Reserve the next epoch. 4. `MatchCreate` with `zone_epoch`; **MatchInit binds** its match id (`RUNTIME_CTX_MATCH_ID`) to that epoch at its very end, once it has loaded — a stale epoch is refused. 5. A failed start frees the zone (`abort`). |
| A batch is queued (`queueSave`) | Admitted only if its match is the zone's bound, unretired copy — refused **at the door**, never dropped from inside the queue ("fencing"). Nakama can stop a match while one of its callbacks still runs; that callback can't write over the new copy. |

The model check behind this design (two zones, a character carrying two items, crashes anywhere, a copy stopped with a
late callback) found that a takeover WITHOUT retiring first lets the dead copy's late save land after the new copy
loaded — so retiring comes before waiting (investigation record: the D73 plan's Part 3).

## One zone at a time — the character registry (D73, 2026-09-30)
A character is loaded from storage when it enters a zone and saved with that zone. If it entered the next zone before
the last one's save of it was written, the next zone would load an older copy (the zone-crossing duplication: Nakama
acknowledges "left" before MatchLeave runs). So a character may enter a zone only once its departure is written
(`char_registry.go`):

| State | Entered by | Left by |
|---|---|---|
| free | — | `world_enter` (with `char_id`) reserves it for one match and returns an **entry pass** |
| reserved (match, pass, time) | `world_enter` | MatchJoinAttempt checks the pass (this account, this character, this match), loads the character once, stages it **by session**, and re-checks that the pass is at most **8 s** old as its LAST step → joining. A pass not used in time counts as free; a failed load cancels it. |
| joining (match, session) | MatchJoinAttempt | MatchJoin, for that session → active, using the staged character (no second read). A late MatchJoin for a pass that ran out (15 s) is kicked. |
| active (match, session) | MatchJoin | MatchLeave for that session → its departure batch is queued → releasing |
| releasing (match) | MatchLeave | the save queue writes the departure (`onWritten`) → free |

`world_enter` waits for "free" on its own RPC goroutine, within the request's 8 s budget (then `CHARACTER_BUSY`; the game
retries behind its fade): active in the SAME zone under another session (a second copy of the game) → that session is
kicked through the match (`MatchSignal` "kick" → `dispatcher.MatchKick` → an ordinary MatchLeave, which saves it) — the
newer copy takes over; another character of the same account in the zone → sent out the same way first (one player per
account per zone); its zone's match gone → that match is retired, its queued saves awaited; active in another zone →
wait (a second copy elsewhere is refused). **Why the 8 s pass:** Nakama gives a join 10 s and then tells the client
"rejected", but still runs the join if the zone gets to it — a ghost holding the character. A pass is issued before the
client starts joining, so refusing any attempt that finishes more than 8 s after the pass means the client always gets
the answer. Character deletion (`DeleteCharacter`) is refused while a character is in play and otherwise runs as a task
on the save queue, after every save already queued. A join without a character (test harness, debug) bypasses all this.

**The game's side** (`WorldManager.cs`, `CrossZoneController.cs`). `EnterWorld` sends `char_id` to `world_enter` and
carries the reply's pass in the join metadata (`char_id`, `pass`, and `entry_x`/`entry_y` on a crossing). A refusal
throws a `WorldEnterException` with a code: the reply's own (`{error, code}` with HTTP 200 — `CHARACTER_BUSY`,
`ZONE_BUSY`, `UNKNOWN_ZONE`, `SERVER_STOPPING`, …), or `JOIN_REJECTED` when the zone turns the join away (nakama-dotnet
raises the server's reason as a `WebSocketException` message: `pass_expired`, `pass_refused`, `already_in_zone`, …).
Any failure clears the half-made join (the pre-join buffer). `EnterWorldWithRetry` retries the refusals that clear by
themselves — busy, and a join turned away for its pass or for the account's other session still leaving — every 0.5 s
for up to 15 s; the menu's Play and every crossing use it. A crossing does this behind the fade; if the next zone still
can't be entered, the player goes back to the zone they left — pulled back out of the edge band, so they don't walk
straight into it again — and a short message says so (the fix the ROADMAP gave its latent bug 6). If the zone they left
can't be entered either — the server stopping, say — they're left in no zone; that narrower case stays open. Deleting
a character in play shows the server's refusal on the select screen.

## Backups (D73, 2026-09-30)
Every zone's save and every character at ONE moment, in one file (`backup.go`):
- **What:** every `zone_state` record except the pre-upgrade copies (`<zone>:world:v<N>`) — so zones still in the old
  format are included — and every character of every account (all accounts' records, 100 at a time). Not the
  accounts, the world list (`worlds`) or `character_backup`.
- **One moment:** the listing runs as a task on the save queue, so it sees exactly what the jobs before it wrote — each
  zone and the characters in it from the same moment, as a crash at that point would leave them.
- **When:** at start-up — queued by `StartSaveSystem` before any zone can save, so it keeps the state from before an
  update — then every `BF_BACKUP_MINUTES` (30) if the queue has changed storage since (a batch written, a character
  deleted). A backup with the same content hash as the newest isn't written, so idle restarts add nothing.
- **The file:** `world-<UTC time>.json` in `BF_BACKUP_DIR` (`/nakama/backups` in the container; on this PC
  `C:/Users/emily/BugFarmer_backups/world`, mounted by `docker-compose.yml`): `format`, `kind`, `created_at`,
  `content_hash`, then `zone_state` and `characters`, each record with its key, account (characters only),
  read/write permissions and value — sorted by key, then account, so equal storage gives an equal file. It is written
  under a temporary name, synced, renamed, then **read back and checked against its hash**: only a backup that reads
  back counts (the folder is on Windows, where a sync isn't guaranteed to reach the disk), and a damaged one is
  removed. Temporary files left by a stop mid-write are removed at start-up.
- **Kept:** the newest 10, the newest of each of the 7 most recent days that have one, and the newest of each of the 4
  most recent ISO weeks that have one — at most 21. Pruned only after a new backup reads back, and only files named
  like ours.
- **Failures** are warnings: the game carries on, and the next interval tries again. With `BF_BACKUP_DIR` unset there
  are no backups (a warning at start-up).

First live run (2026-09-30): 64 zone records and 27 characters, 479 KB — identical to the database record by record
(values and permissions); a restart with nothing changed wrote none; after a scripted player made a character and
placed fences, the next start wrote a new one.

## Save formats — upgrade old, refuse newer, never overwrite what can't be read (2026-09-26)
Every stored document carries `version` — the format of the build that wrote it (`worldSaveVersion`,
`characterSaveVersion`). `save_versions.go` (`upgradeSaveJSON`) decides on load:
- **same format** → read as-is (byte-identical);
- **older** → upgraded one step at a time on the raw JSON (`worldSaveSteps` / `characterSaveSteps`: step `v`
  turns a version-v document into v+1, so a step can reshape fields today's structs no longer know). The
  untouched original is kept first — a zone at `<zone>:world:v<N>` in `zone_state`, a character at
  `<charID>:v<N>` in `character_backup` (a separate collection so it never appears on the select screen). The
  first backup of a version is never replaced. If the backup can't be written, the zone does not start;
- **newer** (a downgrade), **unreadable**, or **storage unreachable** → the zone does NOT start (`MatchInit`
  returns no state → `world_enter` answers `MATCH_CREATE_FAILED`; the log says why) and the document is left
  untouched; `writeWorldSave` also refuses to write over a newer or unreadable document. A character that
  can't be used refuses the join (`character load failed`) and is left off the select screen.

This replaced "any other version = treat the save as missing", where the zone then started empty and the next
autosave wrote over the player's world; a storage read error at start-up did the same. **Changing a save
shape:** bump the version and add the step for the OLD version; never edit an existing step.

## The enforcement — persist_classes.go
Every `WorldState` field is classified exactly once: **WORLD-STATE** (in the document, note says
which field) | **PER-RUN** (presences, the sync ledger — per-run BY the sync architecture —, RNG,
caches, telemetry) | **CONFIG** (reloaded from data files). A reflection test
(`TestPersistClassificationComplete`) fails BY NAME on any unclassified new field — "forgot to
persist X" cannot happen silently. The table doubles as the field-by-field documentation.

## Determinism boundary
Nothing here enters the bug-sim hash. The ledger/epoch/seq are PER-RUN by design (determinism is
within-run); a restart starts a fresh sync epoch over the restored world, exactly like a fresh
boot over an authored zone. Restore happens entirely before the first join.

## Migration (dying code)
Old multi-record saves (`:meta` + `:<cx>_<cy>` + `:swarms`) are imported ONCE at boot when no
document exists (`importLegacySave` — the OLD clamps live only inside it, because legacy stamps
were written against a clock that reset), and the legacy records are DELETED on the first
successful document write. New-doc-wins forever after. The importer dies a release later.

## Gates that hold it
`world_save_test.go`: classification completeness, full round-trip deep-equality, resume-clock,
GroundItemSeq no-collision, ephemeral skip, generation guard, legacy decode+clamps, SwarmState
json tags. `storage_fake_test.go`: `memStorage`, the faithful in-memory stand-in for Nakama storage the save tests run
on (Nakama 3.35's version rules, all-or-nothing batches, all-users listing in pages, deleted accounts refused,
injected failures), with tests pinning each rule. `save_versions_test.go`: the upgrade chain, refusing newer /
unreadable saves at start-up and on write, upgrading an older save with its original backed up once, and
the same for characters. `save_writer_test.go`: the queue writes each batch in one write and in order, against the stored version (a changed
save stops saving), retries a database error until the batch lands, leaves out deleted accounts, coalesces autosaves
but never departures, runs barriers and tasks in order, frees departures only once written, cleans up old-format
records once. `char_registry_test.go` (through the real join / leave / signal callbacks): a crossing waits for the departure and
loads the newest character; the newer copy in the same zone takes over (the old session kicked, the live bag kept); a
dead zone retired before its character moves (its late save refused); another character of the account sent out
first; pass rules (missing, expired, fresh); a late MatchJoin after expiry kicked; a busy character refused within the
budget; deletion refused while in play, then queued after saves. `zone_lease_test.go`: one copy started and reused; ten simultaneous requests start one copy; a dead copy
is retired before a new one loads its last save, and its late save is refused; a live zone reported for create; a
stale start refused; a failed start frees the zone; no start while stopping; the 8 s budget gives up with "busy".
`backup_test.go`: a backup is one moment of the queue (a batch queued after its listing isn't in it); the start-up
listing runs before any save; zone records and characters in, pre-upgrade copies and other collections out; every
account across pages, sorted; damage and newer formats refused on reading; unchanged copies skipped, also across a
restart; the retention (10 / 7 days / 4 weeks, reaching back past idle weeks); no pruning unless the new file reads
back; files not ours left alone; a backup only when something was saved, none once the server is stopping. Each of
three deliberate breaks (prune before the read-back, keep the pre-upgrade copies, list outside the queue) fails its
test. `world_save_cost_test.go`: the byte fast path agrees with the full cell comparison on every real village_21_B cell,
and the save-build timing (run with -v). `final_save_test.go`: the clean stop queues the world and the present characters as ONE
batch, waits for it, and returns nil; over a save changed by something else it writes nothing and stops saving. End-to-end: `tools/harness_persist_test.sh`
(stop → wipe → start; build a farm headless → clean stop → start → assert restored; a direct Postgres inspection of
the stored document; and proof the clean stop itself wrote the save — its `saved_at` is at or after the stop),
plus a seeded legacy-format migration run (imported → carried → legacy rows deleted). **The saves crash test,**
`tools/harness_crash_test.sh`: a scripted player with a real character in the test zones `persist_a` ↔ `persist_b`,
checking fences in the world + in the bag = 50 through a clean stop, a `docker kill`, a zone crossing (with
`persist_a`'s `debug_leave_delay_ms` holding back the departure save so the race happens every time) and a reconnect.
Recorded on 2026-09-30, before the save queue and the character registry: graceful PASS (50); crash FAIL — 45, five
fences lost (the world last saved on leaving, the character on sleeping); cross FAIL — the bag arrived with 50 after
leaving with 45 (duplicated); reconnect FAIL — a second copy of the game saw the stored 50, not the live 48. With the
save queue (same day): crash PASS — 10 in the world + 40 in the bag after the kill. With the character registry (same
day): **all four PASS** — cross arrived with the 45 it left with; reconnect saw the live 48. **The crossing test in the
game client,** `tools/run_crosstest.sh` (the headless Unity player, `HeadlessSyncTest -crosstest`): a new character
enters `persist_a`, places 2 fences and crosses three times through the game's own `CrossZoneController` — into a zone
that can't be entered (it must come back), into `persist_b` (the server waits for `persist_a`'s held-back save), and
back (`persist_b` holds its save 10 s, past the server's 8 s wait, so the game is told "busy" and must retry) —
checking each time that the bag the server sends on arrival is the bag that left. First run (2026-09-30): PASS — back
from the unknown zone in 3.6 s, into `persist_b` in 3.5 s, back into `persist_a` in 10.9 s after one "busy" refusal;
48 fences every time. The late-join gate also runs with client B entering as a character (`CHAR_B`).
