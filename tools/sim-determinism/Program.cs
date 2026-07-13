// Headless determinism harness for the bug simulation.
//
// WHAT IT PROVES: the per-bug client sim (the code every player runs to place individual bugs around a
// synced swarm center) is DETERMINISTIC — same seed + same swarm-center path => byte-identical bug
// positions every time. That is the success criterion for "all players stay in sync" (the server only
// syncs swarm CENTERS; each client computes the individual bugs, so they must compute them identically).
//
// HOW: it links the REAL client sim source (see the .csproj) and drives every species for N ticks along a
// fixed center path, hashing all bug positions+velocities each tick (the same FNV-1a the client's
// ComputeStateHash uses). It runs the whole thing TWICE and asserts the per-tick hash streams are identical
// — which catches the real desync causes (wall-clock, unordered collections, shared static state, float
// nondeterminism). It also asserts bugs actually MOVED (no vacuous pass).
//
// SCOPE (honest): this covers the per-bug MOVEMENT sim, the fragile deterministic core. It does NOT
// replay server merge/split/spawn events (that needs the SwarmManager orchestration) and does NOT prove
// two *different machines* agree (that needs real clients / the server drift detector). See the
// test-changes skill for the full ladder; this is the fast, committed, no-Unity-needed first gate.
//
//   ~/.dotnet/dotnet run --project tools/sim-determinism      (exit 0 = deterministic, 1 = DIVERGED)

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using BugFarmer.Bugs;

namespace SimDeterminism
{
    public static class Program
    {
        public static string RepoRoot;

        const long WorldSeed = 1337;          // pinned (production uses random; the test pins for repeatability)
        const int BugsPerSpecies = 25;
        const int Ticks = 600;                // ~60s at 10Hz — long enough for behavior cycles (alert windows, intent changes)
        static readonly string[] Species =
        {
            "fly_common", "butterfly_meadow", "wasp_common",
            "centipede_garden", "millipede", "beetle_carrion",
        };

        // #20: focused geometry test for BugCollision.LineBlocked (the predator line-of-sight). Run with
        // --los-test. Proves the integer Bresenham tests cells STRICTLY BETWEEN the endpoints (skipping
        // both) — a deterministically-WRONG walk would still pass the 2-client sync gate but fails here.
        // Drives the delegate core with a stubbed blocked-set, so no Unity/TilemapManager is needed.
        static int RunLosTest()
        {
            int failures = 0;
            void Check(string name, bool got, bool want)
            {
                if (got != want) { Console.WriteLine($"LOS-TEST: ❌ {name}: got {got}, want {want}"); failures++; }
                else Console.WriteLine($"LOS-TEST: ✅ {name}");
            }
            FixedPoint2 Pt(float x, float y) => new FixedPoint2(FixedPoint.FromFloat(x), FixedPoint.FromFloat(y));
            System.Func<UnityEngine.Vector2Int, bool> Blocked(params (int x, int y)[] cells) =>
                cell => cells.Any(c => c.x == cell.x && c.y == cell.y);

            // Cell (n) center is world (n+0.5); GetCellCoords floors → cell n.
            Check("clear horizontal", BugCollision.LineBlocked(Pt(5.5f, 5.5f), Pt(8.5f, 5.5f), _ => false), false);
            Check("blocker between (6,5)", BugCollision.LineBlocked(Pt(5.5f, 5.5f), Pt(8.5f, 5.5f), Blocked((6, 5))), true);
            Check("victim-cell (8,5) skipped", BugCollision.LineBlocked(Pt(5.5f, 5.5f), Pt(8.5f, 5.5f), Blocked((8, 5))), false);
            Check("predator-cell (5,5) skipped", BugCollision.LineBlocked(Pt(5.5f, 5.5f), Pt(8.5f, 5.5f), Blocked((5, 5))), false);
            Check("adjacent: no cell between", BugCollision.LineBlocked(Pt(5.5f, 5.5f), Pt(6.5f, 5.5f), Blocked((5, 5), (6, 5))), false);
            Check("same cell", BugCollision.LineBlocked(Pt(5.5f, 5.5f), Pt(5.5f, 5.5f), _ => true), false);
            Check("blocker vertical (5,7)", BugCollision.LineBlocked(Pt(5.5f, 5.5f), Pt(5.5f, 9.5f), Blocked((5, 7))), true);
            Check("blocker on diagonal (7,7)", BugCollision.LineBlocked(Pt(5.5f, 5.5f), Pt(9.5f, 9.5f), Blocked((7, 7))), true);
            Check("clear diagonal", BugCollision.LineBlocked(Pt(5.5f, 5.5f), Pt(9.5f, 9.5f), _ => false), false);

            Console.WriteLine(failures == 0
                ? "LOS-TEST: ✅ PASS — LineBlocked geometry correct (endpoints skipped, between-cells tested)."
                : $"LOS-TEST: ❌ FAIL — {failures} case(s) wrong.");
            return failures == 0 ? 0 : 1;
        }

        public static int Main(string[] args)
        {
            RepoRoot = FindRepoRoot();
            if (args.Contains("--los-test"))
                return RunLosTest();
            bool selftest = args.Contains("--selftest");
            bool attackTest = args.Contains("--attack-test");
            Console.WriteLine($"[sim-determinism] repo={RepoRoot}");
            Console.WriteLine($"[sim-determinism] {Species.Length} species x {BugsPerSpecies} bugs x {Ticks} ticks, seed={WorldSeed}"
                              + (selftest ? "  [SELFTEST: run B is deliberately perturbed]" : "")
                              + (attackTest ? "  [ATTACK-TEST: a deterministic moving player drives attack/flee/curious]" : ""));

            // --selftest proves this harness can actually SEE divergence (so a normal PASS isn't vacuous):
            // run B is perturbed with wall-clock, so the two runs MUST differ; we assert we detect it.
            long[] runA = RunSim(perturb: false, withPlayer: attackTest);
            long[] runB = RunSim(perturb: selftest, withPlayer: attackTest);

            int firstDiff = -1;
            for (int t = 0; t < Ticks; t++)
                if (runA[t] != runB[t]) { firstDiff = t; break; }

            bool moved = runA[Ticks - 1] != runA[0];   // sanity: the sim actually advanced (not a frozen no-op)

            Console.WriteLine($"[sim-determinism] final hash A={runA[Ticks - 1]:X16}  B={runB[Ticks - 1]:X16}");
            Console.WriteLine($"[sim-determinism] bugs moved over the run: {moved}");

            if (selftest)
            {
                // The harness PASSES self-test iff it DETECTED the injected divergence.
                if (firstDiff >= 0)
                {
                    Console.WriteLine($"SELFTEST: ✅ PASS — harness detected the injected nondeterminism at tick {firstDiff} " +
                                      "(so a normal PASS is meaningful, not vacuous).");
                    return 0;
                }
                Console.WriteLine("SELFTEST: ❌ FAIL — harness did NOT detect injected nondeterminism. The check is blind; fix it.");
                return 1;
            }

            if (!moved)
            {
                Console.WriteLine("DETERMINISM: INCONCLUSIVE — bugs never moved (sim frozen); check the harness, not the game.");
                return 2;
            }
            if (firstDiff >= 0)
            {
                Console.WriteLine($"DETERMINISM: ❌ FAIL — two identical runs DIVERGED at tick {firstDiff} " +
                                  $"(A={runA[firstDiff]:X16} B={runB[firstDiff]:X16}). The per-bug sim is NONDETERMINISTIC " +
                                  "=> players WILL desync. Suspect: wall-clock, Dictionary/HashSet iteration, shared static, or float math.");
                return 1;
            }
            Console.WriteLine($"DETERMINISM: ✅ PASS — {Ticks} ticks, all {Species.Length} species, two runs byte-identical. " +
                              "The per-bug movement sim is deterministic.");
            return 0;
        }

        // One full simulation pass: build swarms, advance every tick, return the per-tick state hash.
        // perturb=true injects wall-clock into the center path (SELFTEST ONLY) so the run is nondeterministic.
        // withPlayer=true feeds a deterministic MOVING player each tick, exercising the player-reactive paths
        // (wasp attack orbit-and-dive, fly flee, butterfly curious) — the --attack-test gate.
        static long[] RunSim(bool perturb, bool withPlayer = false)
        {
            // SortedDictionary(Ordinal) => deterministic swarm iteration, mirroring the client's OrderBy(id).
            var swarms = new SortedDictionary<string, List<BugAgent>>(StringComparer.Ordinal);
            foreach (var sp in Species)
            {
                string swarmId = "swarm_" + sp;
                var bugs = new List<BugAgent>(BugsPerSpecies);
                for (int i = 0; i < BugsPerSpecies; i++)
                {
                    // deterministic ring of start positions around (100,100)
                    double ang = i * 2.0 * Math.PI / BugsPerSpecies;
                    var start = new FixedPoint2(
                        FixedPoint.FromFloat(100f + 3f * (float)Math.Cos(ang)),
                        FixedPoint.FromFloat(100f + 3f * (float)Math.Sin(ang)));
                    bugs.Add(new BugAgent(WorldSeed, swarmId, sp, i, start));
                }
                swarms[swarmId] = bugs;
            }

            var players = new List<PlayerTarget>();   // default: no players (wander-only drift check)
            var hashes = new long[Ticks];

            for (int t = 0; t < Ticks; t++)
            {
                if (withPlayer)                        // deterministic moving player → exercises attack/flee/curious
                {
                    players.Clear();
                    players.Add(new PlayerTarget { PlayerId = "p1", Position = PlayerAt(t) });
                }
                foreach (var kv in swarms)            // sorted by swarmId
                {
                    FixedPoint2 center = CenterAt(kv.Key, t);
                    if (perturb && t == 50)           // SELFTEST: nudge one tick by wall-clock => nondeterministic
                        center = new FixedPoint2(FixedPoint.FromInt((int)(DateTime.Now.Ticks % 7) + 100), center.Y);
                    foreach (var bug in kv.Value.OrderBy(b => b.BugId))   // sorted by bugId, like SwarmVisual.SimulateTick
                        bug.SimulateTick(center, players, t);
                }
                hashes[t] = HashState(swarms);
            }
            return hashes;
        }

        // A deterministic moving player (a slow circle near the swarms at 100,100), standing in for the
        // synced player CELL. Pure function of tick → identical across runs, so it gates the attack-movement
        // reproducibility (the wasp orbit-and-dive) exactly like CenterAt gates the wander sim.
        static FixedPoint2 PlayerAt(int tick)
        {
            float ang = tick * 0.03f;
            return new FixedPoint2(
                FixedPoint.FromFloat(100f + 8f * (float)Math.Cos(ang)),
                FixedPoint.FromFloat(100f + 8f * (float)Math.Sin(ang)));
        }

        // A deterministic moving swarm center (a slow circle), standing in for the server's SWARM_SET_TARGET
        // legs. Pure function of (swarmId, tick) — identical across runs.
        static FixedPoint2 CenterAt(string swarmId, int tick)
        {
            int h = 17;
            foreach (char c in swarmId) h = h * 31 + c;
            float baseAng = (float)((h % 360) * Math.PI / 180.0);
            float ang = baseAng + tick * 0.02f;
            float cx = 100f + 20f * (float)Math.Cos(ang);
            float cy = 100f + 20f * (float)Math.Sin(ang);
            return new FixedPoint2(FixedPoint.FromFloat(cx), FixedPoint.FromFloat(cy));
        }

        // FNV-1a over every bug's fixed-point position + velocity, in (swarmId, bugId) order — the same
        // construction as the client's SwarmManager.ComputeStateHash.
        static long HashState(SortedDictionary<string, List<BugAgent>> swarms)
        {
            unchecked
            {
                ulong hash = 14695981039346656037UL;
                const ulong prime = 1099511628211UL;
                foreach (var kv in swarms)
                {
                    foreach (var bug in kv.Value.OrderBy(b => b.BugId))
                    {
                        hash ^= (ulong)(long)bug.Position.X.Value; hash *= prime;
                        hash ^= (ulong)(long)bug.Position.Y.Value; hash *= prime;
                        hash ^= (ulong)(long)bug.Velocity.X.Value; hash *= prime;
                        hash ^= (ulong)(long)bug.Velocity.Y.Value; hash *= prime;
                    }
                }
                return (long)hash;
            }
        }

        static string FindRepoRoot()
        {
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            while (dir != null)
            {
                if (File.Exists(Path.Combine(dir.FullName, "nakama", "data", "species.json")))
                    return dir.FullName;
                dir = dir.Parent;
            }
            throw new Exception("could not find repo root (nakama/data/species.json) above " + AppContext.BaseDirectory);
        }
    }
}
