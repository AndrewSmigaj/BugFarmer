using System;
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
            if (!HasFlag("-synctest")) return;
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
            Log($"start: zone={zone} clientId={clientId} duration={duration}s");

            try
            {
                await NetworkManager.Instance.Session;            // device auth (distinct per -clientid)
                await NetworkManager.Instance.ConnectSocketAsync();
                Log("socket connected; entering world (ephemeral, no character)…");
                await WorldManager.Instance.EnterWorld(zone, null);
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
                Log($"world seed ready ({WorldSeedProvider.Instance.WorldSeed}); recording…");

                // Record per-tick state hashes exactly like DebugOverlay F1 (SetTraceCallback -> TickTraceBuffer).
                var buffer = new TickTraceBuffer();
                int maxBugs = 0;
                SwarmManager.Instance.SetTraceCallback((tick, hash, bugs, players) =>
                {
                    if (bugs != null && bugs.Count > maxBugs) maxBugs = bugs.Count;
                    buffer.RecordTick(tick, hash, bugs, players);
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
