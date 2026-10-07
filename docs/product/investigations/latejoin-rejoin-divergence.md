# Investigation: a joining player out of step from its first live tick
_status: DRAFT (reproduction pending) · investigated 2026-10-06 · investigate-only (no fix applied)_

## Debrief (read me first)
*Written last, once the reproduction is in.*

## 1. Issue, repro & evidence
> Found 2026-10-06 by the Stage 1.0e player tests (`docs/plans/village-slice.md`); the owner asked for a full
> investigation the same evening, with a recommended fix and no change to the game until he approves one.

- **Symptom.** In `REJOIN_AT=100 tools/run_players.sh 3 bench_village 300` (P1 in charge and standing still; P2 and P3
  join 8 and 16 s later and walk a route; P2 quits after 100 s and rejoins at once as the same account), P2 was out of
  step with the others **from its first live tick in both sessions** (tick 96, and tick 1,087 after rejoining), with
  the same bug count as the others every tick, until the server's drift check resynced it (ticks 280 and 1,180:
  "Drift detected: client 50d304dc… != majority … resyncing"). P1 and P3 stayed identical (2,557 ticks).
- **Expected.** Every computer identical from its first live tick (the late-join design, `architecture_swarm_sync.md`
  §0); the drift check is a safety net, not a routine path.
- **Repro conditions.** Bench village as authored (normal speed, natural ecology), world seed 1704694170488522611
  (random per run), the base test build (`Build/SyncTest_base`, 2026-10-06), a fresh server (the script wipes and
  restarts). The same scenario without the rejoin, and with the computer in charge leaving, stayed identical in two
  other runs today (seeds 540831579781988151 and 5517314492318818892).
- **Evidence.** `tools/_generated/players/2026-10-07T010130Z_3p_bench_village/` (git-ignored): `hashlog_P*.csv`,
  `player_P*.log`, `nakama.log`; comparisons `…005207Z_2p…` and `…005629Z_3p…`.
- **Acceptance test.** The same scenario, repeated, with every player identical from its first live tick and no
  drift resync; plus a regression test for each cause found.

## 2. Root cause (the chain) — in progress
Two candidate causes so far, one for each session; the first is evidenced, the second is not yet explained.

**A. The rejoin (P2's second session): a departed player's position is removed outside the ordered event stream,
and a same-account rejoin brings the old position back.** Each step read in the code:
1. The bug simulation's player inputs are the cells in `InfluenceManager._playerCells`
   (`SwarmManager.cs:1002-1023`, `GetDeterministicPlayerTargets`, sorted by player id).
2. When a player leaves, the server deletes its cell and emits `PLAYER_CELL_LEAVE` (`match.go:762-775`) — but the
   client **ignores** that event on purpose ("keep last known position", `InfluenceManager.cs:240-244`).
3. The only removal on the clients is `SwarmManager.HandlePlayerLeft` (`SwarmManager.cs:259-263`), on **receipt** of
   the presence-leave message — not at an event tick. Each client drops the cell at whatever tick it happens to be
   on: a sim input outside the frontier-gated ledger (the invariant in `nakama/modules/world/CLAUDE.md`).
4. A joiner's snapshot carries the authority's player cells at the snapshot tick, filtered to the zone's current
   members (`match.go:3057-3069`; the comment there names "a known ~4s micro-gap"). A player who left and rejoined
   as the same account is a member again, so its **old** cell passes the filter.
5. P2's second session hydrated **3** player cells at its join (`player_P2_r2.log`), from the authority's snapshot at
   tick 1,067 — while only P1 and P3 were in the zone. The third can only be P2's own cell from before it left. For
   ticks 1,067–1,086 its replay had bugs reacting to a player at P2's old spot, while P1 and P3 (which had dropped
   the cell on receipt) had none there.
*Not yet proven:* which bugs differed (needs per-bug traces of the join window); that the third cell is P2's old
position (inferred from the count and the member filter).

**B. The first session (not a rejoin): not yet explained.** P2's first join used the tick-3 snapshot with one player
cell (P1) and 92 ticks of replay — exactly like P2's identical joins in the other two runs.

## 3. How the system actually works (late join)
`HandleLateJoinSnapshot` (`SwarmManager.cs:1840` on) replaces the whole state: player cells cleared then hydrated
from the snapshot; swarm legs cleared and re-set from metadata; the food registry, hunt assignments and subdued set
hydrated from the snapshot; swarms not in the snapshot pruned; swarms created from metadata with exactly the
snapshot's bug ids; then the influence log replays from the snapshot tick to the end tick, and the client goes live.
Live events are applied at their own tick in seq order (`ProcessEventsForTick`, `SwarmManager.cs:961-991`); an event
for a tick already passed is a protocol violation that requests a resync (none happened here).

## 4. Ruled out (not the cause)
- **A saved spawn position** (a character returning where it left): every player joined without a character, at the
  default spawn (`spawn=default character=none` in every player log).
- **The joiner's own exact position fed to the sim:** the per-tick player list comes only from the ledgered cells
  (`SwarmManager.cs:1002-1023`).
- **A join-side on-receipt write:** nothing adds a cell on presence join; only the leave handler writes outside the
  ledger (every `SetPlayerCell` / `RemovePlayerCell` / `OnPlayerJoined` call site listed).
- **The duplicate event at going live:** P2 logged `DUPLICATE EVENT BEFORE APPLY` for the last event of its join
  package (seq 956; and 9,675 after rejoining), but run 2's identical joiner had one too (seq 965), and the duplicate
  is dropped, not applied twice (`SwarmManager.cs:494-497`). A protocol oddity (the package's last event is sent again
  live), recorded, not this fault.
- **A late event / protocol violation:** none logged by any player.
- **The world:** P3 joined the same world 81 ticks later and was identical.

## 5. Next: the reproduction (after the windowed tour, 2026-10-06 evening)
1. The same scenario on run 3's world (the bench zone's seed set to 1704694170488522611 on the throwaway bench copy,
   rebuilt afterwards), twice: does it repeat?
2. Short versions so every player's 500-tick trace (`TickTraceBuffer`) covers the join window, then
   `tools/netcode/sync_diff.py` bug by bug, with each bug's behaviour (fleeing, curious, attacking) and the per-tick
   player count, for: a plain late join (session 1's class) and a quick same-account rejoin (session 2's class).
