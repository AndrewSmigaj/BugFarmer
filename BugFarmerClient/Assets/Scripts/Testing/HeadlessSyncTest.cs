using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using BugFarmer.Networking;
using BugFarmer.Entities;
using BugFarmer.Bugs;
using BugFarmer.Tracing;

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
    /// </summary>
    public static class HeadlessSyncTest
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Boot()
        {
            if (!HasFlag("-synctest") && !HasFlag("-ecology")) return;
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
        private async void Start()
        {
            string zone = HeadlessSyncTest.GetArg("-zone", "village_21_B");
            string clientId = HeadlessSyncTest.GetArg("-clientid", "A");
            if (!int.TryParse(HeadlessSyncTest.GetArg("-duration", "60"), out int duration)) duration = 60;

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
            Log($"start: zone={zone} clientId={clientId} duration={duration}s spawn={(entryX.HasValue ? $"{entryX},{entryY}" : "default")}");

            try
            {
                await NetworkManager.Instance.Session;            // device auth (distinct per -clientid)
                await NetworkManager.Instance.ConnectSocketAsync();
                Log("socket connected; entering world (ephemeral, no character)…");
                await WorldManager.Instance.EnterWorld(zone, null, entryX, entryY);
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

            float t0 = Time.realtimeSinceStartup;
            while (Time.realtimeSinceStartup - t0 < durationSeconds)
            {
                await Task.Delay(100);
                long tick = SwarmManager.Instance.SimulationTick;
                if (tick - lastSampledTick < 10) continue; // ~1 sample / game-second (SimRate=10 ticks/sim-sec)
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

            if (maxTotal == 0)
            {
                Log("WARNING: sampled 0 bugs the whole window — client saw no swarms; treating run as INVALID.");
                Quit(5);
                return;
            }
            Quit(0);
        }

        private static void Log(string m)
        {
            Debug.Log("[HeadlessSyncTest] " + m);
            BugFarmer.Util.DebugFileLogger.Log("[HeadlessSyncTest] " + m);
        }

        private static void Quit(int code)
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit(code);
#endif
        }
    }
}
