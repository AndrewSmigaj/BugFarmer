using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using Nakama;
using UnityEngine;
using BugFarmer.Networking;
using BugFarmer.Entities;
using BugFarmer.Bugs;
using BugFarmer.Player;
using BugFarmer.Tracing;
using BugFarmer.UI;
using BugFarmer.Util;

namespace BugFarmer.Testing
{
    /// <summary>
    /// Headless cross-client SYNC TEST bootstrap — the real Unity client, driven with no UI.
    ///
    /// Activated by the <c>-synctest</c> command-line flag (tools/run_sync_test.sh sets it). This player
    /// authenticates as a distinct account (NetworkManager reads <c>-clientid</c>), enters a zone with NO
    /// character (ephemeral), records its per-tick bug-state hash via the same TickTraceBuffer the F1/F2
    /// debug overlay uses, then quits after <c>-duration</c> seconds.
    ///
    /// Run TWO instances (different -clientid) into the same zone and diff their trace files: identical
    /// <c># TICK n HASH …</c> streams ⇒ both players computed the SAME bugs ⇒ the frontier-gated
    /// deterministic sync holds. This is the FULL system (real client + real server, merge/split/spawn all
    /// live) — not a reimplementation. Built players don't take the Unity project lock, so N instances run
    /// alongside an open Editor. See tools/run_sync_test.sh and the test-changes skill §3.
    ///
    /// <c>-character &lt;name&gt;</c> enters WITH that character (found by name, or created) — the way a player enters
    /// from the menu: world_enter reserves it and the join carries its entry pass (D73).
    /// <c>-crosstest</c> (needs <c>-character</c>) is the zone-crossing test in the real client, in the linked test
    /// zones persist_a and persist_b — see <see cref="HeadlessSyncTestRunner.RunCrossTest"/> and
    /// tools/run_crosstest.sh.
    /// </summary>
    public static class HeadlessSyncTest
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Boot()
        {
            if (!HasFlag("-synctest") && !HasFlag("-ecology") && !HasFlag("-crosstest")) return;
            var go = new GameObject("/[HeadlessSyncTest]");
            UnityEngine.Object.DontDestroyOnLoad(go);
            go.AddComponent<HeadlessSyncTestRunner>();
        }

        public static bool HasFlag(string flag)
        {
            foreach (var a in Environment.GetCommandLineArgs())
                if (a == flag) return true;
            return false;
        }

        public static string GetArg(string flag, string fallback)
        {
            var args = Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++)
                if (args[i] == flag) return args[i + 1];
            return fallback;
        }
    }

    public class HeadlessSyncTestRunner : MonoBehaviour
    {
        // Stage 1.0b test rig flags (docs/plans/village-slice.md): -perfmode clean|breakdown (cost probe; clean = the
        // per-part timers off), -behaviour (behaviour tally), -hashlog (fingerprint log), -shadowreports (a computer
        // not in charge logs the reports it would send), -reportlog (log the reports sent), -route <file> (walk a
        // route), -vsyncoff, -screenshot <s>[,<s>...] (a windowed run saves the game's own picture that many seconds
        // after the rig starts). Outputs go to persistentDataPath with the client id in the name.
        private string _perfMode;
        private string _fileId;

        private async void Start()
        {
            string zone = HeadlessSyncTest.GetArg("-zone", "village_21_B");
            string clientId = HeadlessSyncTest.GetArg("-clientid", "A");
            if (!int.TryParse(HeadlessSyncTest.GetArg("-duration", "60"), out int duration)) duration = 60;

            // -timescale N: run this client's clock N times faster, to keep pace with a fast-forwarded test zone
            // (call_rate 60 = 6x). The bug sim steps by Time.deltaTime, so without it a client in a 6x zone simulates
            // at a sixth of the server's pace and falls ever further behind (every real-client ecology run did,
            // 2026-07-18 to 2026-10-04). -duration stays in real seconds.
            if (float.TryParse(HeadlessSyncTest.GetArg("-timescale", "1"), System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out float timeScale) && timeScale > 0f)
                Time.timeScale = timeScale;

            // Phase 1b proof: -spawn gx,gy places this client at a chosen cell so two instances load DIFFERENT
            // chunk sets (one near a fly-farm fence, one far away). Collision is now zone-wide, so fence-adjacent
            // bugs must stay bit-identical even on the client that never loaded the fence. Omitted = default spawn.
            float? entryX = null, entryY = null;
            string spawn = HeadlessSyncTest.GetArg("-spawn", null);
            if (!string.IsNullOrEmpty(spawn))
            {
                var parts = spawn.Split(',');
                if (parts.Length == 2
                    && float.TryParse(parts[0], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float sx)
                    && float.TryParse(parts[1], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float sy))
                {
                    entryX = sx + 0.5f; // cell centre
                    entryY = sy + 0.5f;
                }
                else Log($"WARNING: could not parse -spawn '{spawn}' (want gx,gy); using default spawn");
            }
            string charName = HeadlessSyncTest.GetArg("-character", null);
            Log($"start: zone={zone} clientId={clientId} duration={duration}s timescale={Time.timeScale} spawn={(entryX.HasValue ? $"{entryX},{entryY}" : "default")} character={charName ?? "none"}");

            try
            {
                await NetworkManager.Instance.Session;            // device auth (distinct per -clientid)
                await NetworkManager.Instance.ConnectSocketAsync();
                string charId = null;
                if (!string.IsNullOrEmpty(charName))
                {
                    charId = await EnsureCharacter(charName);
                    CharacterSession.SelectedCharID = charId;     // what a zone crossing re-enters with
                    CharacterSession.SelectedCharName = charName;
                    Log($"character '{charName}' = {charId}");
                }
                if (HeadlessSyncTest.HasFlag("-crosstest"))
                {
                    if (charId == null) { Log("ERROR: -crosstest needs -character"); Quit(2); return; }
                    Quit(await RunCrossTest(charId) ? 0 : 7);
                    return;
                }
                // Logs that must see the join itself (the replay and the first live tick) open before entering.
                string pdir = Application.persistentDataPath;
                // -runtag <t>: a suffix for this process's files, so the same player rejoining (same -clientid, same
                // account) doesn't overwrite its first session's files.
                string fileId = clientId + (HeadlessSyncTest.GetArg("-runtag", null) is string rt ? "_" + rt : "");
                _fileId = fileId;
                if (HeadlessSyncTest.HasFlag("-hashlog")) HashLog.Open(Path.Combine(pdir, $"hashlog_{fileId}.csv"));
                if (HeadlessSyncTest.HasFlag("-shadowreports") || HeadlessSyncTest.HasFlag("-reportlog"))
                    ReportLog.Open(Path.Combine(pdir, $"reports_{fileId}.csv"));
                ReportLog.Shadow = HeadlessSyncTest.HasFlag("-shadowreports");

                Log(charId == null ? "socket connected; entering world (ephemeral, no character)…"
                                   : $"socket connected; entering world as '{charName}'…");
                // As the menu does: a refusal that clears by itself (the character still being saved) is retried.
                await WorldManager.Instance.EnterWorldWithRetry(zone, charId, entryX, entryY);
                Log($"entered '{zone}'; waiting for the bug sim…");

                float t0 = Time.realtimeSinceStartup;
                while (SwarmManager.Instance == null && Time.realtimeSinceStartup - t0 < 20f)
                    await Task.Yield();
                if (SwarmManager.Instance == null) { Log("ERROR: SwarmManager never appeared"); Quit(2); return; }

                // FAIL FAST on a broken harness: the bug sim can only run once the world seed (OpCode 68
                // WorldInit) has arrived. If it never does, the client caches swarm rosters forever and shows
                // 0 swarms — that is a DEAD client, not determinism data, and must not be silently recorded.
                // (This was the real bug: the one-shot WorldInit was dropped during join; the WorldManager
                // pre-join buffer fixes it. We keep this guard so a regression can never masquerade as a run.)
                float ts0 = Time.realtimeSinceStartup;
                while (WorldSeedProvider.Instance?.IsInitialized != true && Time.realtimeSinceStartup - ts0 < 10f)
                    await Task.Yield();
                if (WorldSeedProvider.Instance?.IsInitialized != true)
                {
                    Log("ERROR: WorldSeed never initialized (no WorldInit) — client would show 0 swarms. Aborting as INVALID.");
                    Quit(4);
                    return;
                }
                bool ecology = HeadlessSyncTest.HasFlag("-ecology");
                Log($"world seed ready ({WorldSeedProvider.Instance.WorldSeed}); {(ecology ? "sampling population" : "recording")}…");
                StartRig(_fileId ?? clientId);

                // ECOLOGY MODE: just live in the zone (authority → predation runs) while the SERVER logs ECOSTATS;
                // sample the client's ground-truth population and write fly_counts.csv. No hash trace (that's the
                // sync-test job) — keeps the run light.
                if (ecology)
                {
                    await RunEcologySampling(duration);
                    return;
                }

                // DRIFT-NET SELF-TEST (`-desyncafter N`): deliberately perturb one bug N recorded ticks in, so
                // THIS client diverges — the zone drift round + authority tie-referee must then DETECT it and
                // RESYNC us (watch the server log for "tie broken by AUTHORITY"). Inert without the flag.
                int desyncAfter = 0;
                int.TryParse(HeadlessSyncTest.GetArg("-desyncafter", "0"), out desyncAfter);
                int recordedTicks = 0; bool chaosInjected = false;

                // Record per-tick state hashes exactly like DebugOverlay F1 (SetTraceCallback -> TickTraceBuffer).
                var buffer = new TickTraceBuffer();
                int maxBugs = 0;
                SwarmManager.Instance.SetTraceCallback((tick, hash, bugs, players) =>
                {
                    if (bugs != null && bugs.Count > maxBugs) maxBugs = bugs.Count;
                    recordedTicks++;
                    if (desyncAfter > 0 && !chaosInjected && recordedTicks >= desyncAfter)
                    {
                        chaosInjected = true;
                        Log($"CHAOS: injecting 1-bug perturbation at tick {tick} (drift-net self-test)");
                        SwarmManager.Instance.DebugPerturbOneBug();
                    }
                    // DIAGNOSTIC: also capture per-swarm leg+center each tick (leg/center divergence pin).
                    var legs = SwarmManager.Instance.CollectSwarmLegTraces();
                    buffer.RecordTick(tick, hash, bugs, players, legs);
                });
                Log($"recording {duration}s of tick hashes…");
                await Task.Delay(duration * 1000);

                SwarmManager.Instance.SetTraceCallback(null);
                buffer.DumpToFile(clientId);                       // -> persistentDataPath/trace_<clientId>_*.csv
                Log($"DONE: dumped {buffer.Count} ticks for client {clientId} (max bugs seen: {maxBugs})");
                if (maxBugs == 0)
                {
                    Log("WARNING: recorded 0 bugs the whole window — client saw no swarms; treating run as INVALID.");
                    Quit(5);
                    return;
                }
                Quit(0);
            }
            catch (Exception e)
            {
                Log("EXCEPTION: " + e);
                Quit(3);
            }
        }

        /// <summary>ECOLOGY MODE: live in the zone as authority (predation runs) while the SERVER logs ECOSTATS,
        /// and sample the client's GROUND-TRUTH per-species counts ~once per game-second (speed-independent) into
        /// fly_counts.csv — the same format the .NET harness produced, now more accurate (real swarm counts, not a
        /// ledger reconstruction). Written to persistentDataPath so run_config reads it from PDATA. No hash trace.</summary>
        private async Task RunEcologySampling(int durationSeconds)
        {
            var samples = new List<(long tick, Dictionary<string, int> bySpecies)>();
            var speciesSeen = new SortedSet<string>(StringComparer.Ordinal);
            long lastSampledTick = long.MinValue;
            int maxTotal = 0;

            // COST WINDOWS (the scaling study, docs/product/investigations/scaling-2026-10-04/): every ~5 s of real
            // time, the CPU this client spent per game tick at the bug count it carried -> client_perf.csv. Pure
            // observation: PerfProfiler only times existing work, never the hashed sim state.
            PerfProfiler.Enabled = _perfMode != "clean"; // -perfmode clean: the per-part timers stay off (their own cost skews timings)
            PerfProfiler.ResetTotals();
            var perf = new StringBuilder("real_s,tick,swarms,bugs,ticks,frames,cpu_ms,sim_ms,gc0,managed_mb,food_ms,food_calls,tick_ms\n");
            var proc = System.Diagnostics.Process.GetCurrentProcess();
            double CpuMs() { try { proc.Refresh(); return proc.TotalProcessorTime.TotalMilliseconds; } catch { return -1; } }
            double SimMs() => PerfProfiler.Totals.TryGetValue("Sim.SwarmTick", out var st) ? st.ms : 0;
            double TickMs() => PerfProfiler.Totals.TryGetValue("Sim.Tick", out var tt) ? tt.ms : 0; // the whole tick
            (double ms, int calls) Food() => PerfProfiler.Totals.TryGetValue("Sim.FoodLookup", out var ft) ? (ft.ms, ft.calls) : (0, 0);
            float wStart = Time.realtimeSinceStartup;
            long wTick = SwarmManager.Instance.SimulationTick;
            int wFrames = Time.frameCount, wGc = GC.CollectionCount(0), windows = 0;
            double wCpu = CpuMs(), wSim = SimMs(), wTickMs = TickMs();
            var wFood = Food();

            float t0 = Time.realtimeSinceStartup;
            while (Time.realtimeSinceStartup - t0 < durationSeconds)
            {
                await Task.Delay(100);
                long tick = SwarmManager.Instance.SimulationTick;
                float now = Time.realtimeSinceStartup;
                if (now - wStart >= 5f)
                {
                    double cpu = CpuMs(), sim = SimMs(), tickMs = TickMs();
                    var food = Food();
                    int gc = GC.CollectionCount(0);
                    perf.Append(FormattableString.Invariant(
                        $"{now - t0:F1},{tick},{SwarmManager.Instance.SwarmCount},{SwarmManager.Instance.TotalBugCount},{tick - wTick},{Time.frameCount - wFrames},{cpu - wCpu:F1},{sim - wSim:F2},{gc - wGc},{GC.GetTotalMemory(false) / 1048576.0:F1},{food.ms - wFood.ms:F2},{food.calls - wFood.calls},{tickMs - wTickMs:F2}\n"));
                    windows++;
                    wStart = now; wTick = tick; wFrames = Time.frameCount; wGc = gc; wCpu = cpu; wSim = sim; wFood = food; wTickMs = tickMs;
                }
                // ~1 sample / game-second (SimRate=10 ticks/sim-sec). The first pass always samples: `tick - long.MinValue`
                // overflows to a negative number, which kept every ecology run since 2026-07-18 at 0 samples.
                if (lastSampledTick != long.MinValue && tick - lastSampledTick < 10) continue;
                lastSampledTick = tick;
                var counts = SwarmManager.Instance.BugCountBySpecies();
                foreach (var k in counts.Keys) speciesSeen.Add(k);
                int total = SwarmManager.Instance.TotalBugCount;
                if (total > maxTotal) maxTotal = total;
                samples.Add((tick, counts));
            }

            var cols = new List<string>(speciesSeen);
            var sb = new StringBuilder("tick,").Append(string.Join(",", cols)).Append(",total_bugs\n");
            foreach (var (tick, bySpecies) in samples)
            {
                sb.Append(tick);
                int total = 0;
                foreach (var c in cols) { int v = bySpecies.TryGetValue(c, out var vv) ? vv : 0; total += v; sb.Append(',').Append(v); }
                sb.Append(',').Append(total).Append('\n');
            }
            string path = Path.Combine(Application.persistentDataPath, "fly_counts.csv");
            File.WriteAllText(path, sb.ToString());
            Log($"ECOLOGY: {samples.Count} population samples, {cols.Count} species, max total {maxTotal} -> {path}");
            string perfPath = Path.Combine(Application.persistentDataPath, "client_perf.csv");
            File.WriteAllText(perfPath, perf.ToString());
            // Every timed part of the client over the whole run (ms and calls per scope), for the per-tick breakdown.
            var totals = new StringBuilder("scope,ms,calls\n");
            foreach (var kv in PerfProfiler.Totals)
                totals.Append(FormattableString.Invariant($"{kv.Key},{kv.Value.ms:F2},{kv.Value.calls}\n"));
            File.WriteAllText(Path.Combine(Application.persistentDataPath, "client_perf_totals.csv"), totals.ToString());
            Log($"PERF: {windows} cost windows -> {perfPath}");

            if (maxTotal == 0)
            {
                Log("WARNING: sampled 0 bugs the whole window — client saw no swarms; treating run as INVALID.");
                Quit(5);
                return;
            }
            Quit(0);
        }

        // ---- the zone-crossing test (-crosstest) ----

        // The linked test zones (tools/world/make_test_zone.py): 64x64 each, persist_a west of persist_b. Each holds
        // back its departure saves (debug_leave_delay_ms): persist_a 3 s — the next zone is asked for before the save
        // lands, so the server must wait for it; persist_b 10 s — longer than the server waits (8 s), so the client is
        // told "busy" and must retry behind the fade.
        private const string ZoneA = "persist_a", ZoneB = "persist_b", Fence = "fence_wood";
        private const int FenceRow = 44, FenceFirstX = 36;
        private int _fullSyncs;          // full inventory syncs received (one per join)
        private int _syncedFences = -1;  // fences in the bag in the latest full sync
        private int _failures;

        /// <summary>
        /// The zone-crossing test in the real client (D73). Enter persist_a with the character and place 2 fences;
        /// then three crossings through CrossZoneController, each checked against the bag that left:
        ///   1. into a zone that can't be entered — the player must come back to persist_a;
        ///   2. into persist_b — the server waits for persist_a's held-back save before letting the character in;
        ///   3. back into persist_a — persist_b's save is held back past the server's wait, so the entry is refused
        ///      as busy and must be retried behind the fade.
        /// Every bag is read from the server's full inventory sync on arrival — a stale saved copy shows as 50.
        /// </summary>
        public async Task<bool> RunCrossTest(string charId)
        {
            var wm = WorldManager.Instance;
            wm.OnMatchData += CountFullSyncs;

            int syncs = _fullSyncs;
            await wm.EnterWorldWithRetry(ZoneA, charId);
            Check(await WaitUntil(() => _fullSyncs > syncs, 10f), $"entered {ZoneA} and received the character's bag");
            Log($"CROSSTEST entered {ZoneA} with BAG {Fence}={_syncedFences}");

            int placed = await PlaceFences(2);
            int left = CountItem(InventoryManager.Instance.ItemSlots, Fence);
            Check(placed == 2, $"placed 2 fences [placed {placed}]");
            Log($"CROSSTEST placed {placed}; BAG {Fence}={left}");

            var cross = FindObjectOfType<CrossZoneController>();
            if (cross == null) { Log("CROSSTEST ERROR: no CrossZoneController (no local player)"); return false; }

            await Crossing(cross, "no_such_zone", 2.5f, FenceRow + 0.5f, ZoneA, left,
                           "a crossing into a zone that can't be entered comes back");
            await Crossing(cross, ZoneB, 2.5f, FenceRow + 0.5f, ZoneB, left,
                           "the crossing waits for the zone left behind to save the character");
            int retries = wm.EnterRetries;
            await Crossing(cross, ZoneA, 61.5f, FenceRow + 0.5f, ZoneA, left,
                           "a crossing refused as busy is retried behind the fade");
            Check(wm.EnterRetries > retries, $"the way back was refused as busy and retried [retries {wm.EnterRetries - retries}]");

            wm.OnMatchData -= CountFullSyncs;
            Log(_failures == 0 ? "CROSSTEST PASS" : $"CROSSTEST FAIL ({_failures} check(s) failed)");
            return _failures == 0;
        }

        // One crossing: walk into `target` at (ex, ey); check the player ends up in `expectZone` with `bag` fences.
        private async Task Crossing(CrossZoneController cross, string target, float ex, float ey, string expectZone,
                                    int bag, string what)
        {
            int syncs = _fullSyncs;
            float t0 = Time.realtimeSinceStartup;
            await cross.CrossTo(target, ex, ey);
            var wm = WorldManager.Instance;
            bool arrived = wm.CurrentMatch != null && wm.CurrentZoneId == expectZone &&
                           await WaitUntil(() => _fullSyncs > syncs, 10f);
            Log($"CROSSTEST crossing to {target}: now in {wm.CurrentZoneId ?? "no zone"} after " +
                $"{Time.realtimeSinceStartup - t0:F1}s with BAG {Fence}={_syncedFences}");
            Check(arrived, $"{what}: in {expectZone} with a fresh bag");
            Check(_syncedFences == bag, $"{what}: the bag that arrived is the bag that left — {bag} fences [got {_syncedFences}]");
        }

        // Place up to `count` fences along the test row; a placement counts once the server takes it out of the bag.
        private async Task<int> PlaceFences(int count)
        {
            var inv = InventoryManager.Instance;
            int placed = 0;
            for (int x = FenceFirstX; placed < count && x < FenceFirstX + 24; x++)
            {
                int before = CountItem(inv.ItemSlots, Fence);
                var json = JsonUtility.ToJson(new TilePlaceMessage { grid_x = x, grid_y = FenceRow, occupant_id = Fence, direction = 0 });
                await NetworkManager.Instance.Socket.SendMatchStateAsync(WorldManager.Instance.CurrentMatch.Id, OpCodes.TilePlace, json);
                if (await WaitUntil(() => CountItem(inv.ItemSlots, Fence) == before - 1, 3f)) placed++;
            }
            return placed;
        }

        private void CountFullSyncs(IMatchState state)
        {
            if (state.OpCode != OpCodes.FullInventorySync) return;
            var msg = JsonUtility.FromJson<FullInventorySyncMessage>(Encoding.UTF8.GetString(state.State));
            _syncedFences = CountItem(msg?.item_slots, Fence);
            _fullSyncs++;
        }

        private void Check(bool ok, string what)
        {
            if (!ok) _failures++;
            Log($"CROSSTEST CHECK {(ok ? "ok" : "FAILED")}: {what}");
        }

        private static int CountItem(InventorySlot[] slots, string itemId)
        {
            int n = 0;
            if (slots != null)
                foreach (var s in slots)
                    if (s != null && s.item_id == itemId) n += s.count;
            return n;
        }

        private static async Task<bool> WaitUntil(Func<bool> done, float seconds)
        {
            float t0 = Time.realtimeSinceStartup;
            while (!done())
            {
                if (Time.realtimeSinceStartup - t0 > seconds) return false;
                await Task.Yield();
            }
            return true;
        }

        /// <summary>The account's character with this name (as the select screen lists it), created if missing.</summary>
        private static async Task<string> EnsureCharacter(string name)
        {
            var session = await NetworkManager.Instance.Session;
            var client = NetworkManager.Instance.Client;
            var list = JsonUtility.FromJson<CharacterListResponse>((await client.RpcAsync(session, "character_list", "{}")).Payload);
            if (list?.characters != null)
                foreach (var c in list.characters)
                    if (string.Equals(c.name, name, StringComparison.OrdinalIgnoreCase)) return c.char_id;
            var result = await client.RpcAsync(session, "character_create", JsonUtility.ToJson(new CharacterCreateRequest { name = name }));
            var created = JsonUtility.FromJson<CharacterCreateResponse>(result.Payload);
            if (created?.character == null || string.IsNullOrEmpty(created.character.char_id))
                throw new InvalidOperationException($"character_create '{name}' refused: {JsonUtility.FromJson<ErrorResponse>(result.Payload)?.error}");
            return created.character.char_id;
        }

        private static void Log(string m)
        {
            Debug.Log("[HeadlessSyncTest] " + m);
            BugFarmer.Util.DebugFileLogger.Log("[HeadlessSyncTest] " + m);
        }

        /// <summary>Starts the Stage 1.0b probes the command line asks for (the flags are listed above _perfMode).</summary>
        private void StartRig(string clientId)
        {
            _perfMode = HeadlessSyncTest.GetArg("-perfmode", null);
            bool cost = _perfMode != null;
            if (cost)
            {
                CostProbe.Start();
                gameObject.AddComponent<CostProbeFrame>();
                Log($"cost probe on (perfmode={_perfMode}; per-thread allocations {(CostProbe.ThreadAllocSupported ? "" : "NOT ")}counted, " +
                    $"per-frame allocations {(CostProbe.FrameAllocSupported ? "" : "NOT ")}counted)");
            }
            bool behaviour = HeadlessSyncTest.HasFlag("-behaviour");
            if (behaviour) BehaviourTally.Start();
            if (HeadlessSyncTest.HasFlag("-vsyncoff")) { QualitySettings.vSyncCount = 0; Application.targetFrameRate = -1; }
            // The test enters the world directly, so the character-select overlay (built at scene load, hidden only when
            // a player picks a character) would stay drawn over the game in a windowed run (found 2026-10-06).
            if (CharacterSelectPanel.Instance != null) CharacterSelectPanel.Instance.gameObject.SetActive(false);
            string shots = HeadlessSyncTest.GetArg("-screenshot", null);
            if (!string.IsNullOrEmpty(shots))
                gameObject.AddComponent<TestScreenshots>().Begin(Application.persistentDataPath, clientId, shots);
            RouteFollower route = null;
            string routeFile = HeadlessSyncTest.GetArg("-route", null);
            if (!string.IsNullOrEmpty(routeFile))
            {
                route = gameObject.AddComponent<RouteFollower>();
                Log(route.Load(routeFile) ? $"route loaded: {routeFile}" : $"WARNING: route file missing or empty: {routeFile}");
            }
            if (cost || behaviour || route != null || HashLog.Enabled || ReportLog.Active)
                gameObject.AddComponent<ProbeWriter>().Begin(Application.persistentDataPath, clientId, _perfMode, cost, behaviour, route);
        }

        private static void Quit(int code)
        {
            ProbeWriter.Instance?.Finish(); // write the probes' files before the player exits
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit(code);
#endif
        }
    }
}
