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

        public static int Main(string[] args)
        {
            RepoRoot = FindRepoRoot();
            bool selftest = args.Contains("--selftest");
            Console.WriteLine($"[sim-determinism] repo={RepoRoot}");
            Console.WriteLine($"[sim-determinism] {Species.Length} species x {BugsPerSpecies} bugs x {Ticks} ticks, seed={WorldSeed}"
                              + (selftest ? "  [SELFTEST: run B is deliberately perturbed]" : ""));

            // --selftest proves this harness can actually SEE divergence (so a normal PASS isn't vacuous):
            // run B is perturbed with wall-clock, so the two runs MUST differ; we assert we detect it.
            long[] runA = RunSim(perturb: false);
            long[] runB = RunSim(perturb: selftest);

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
        static long[] RunSim(bool perturb)
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

            var players = new List<PlayerTarget>();   // no players (drift checks run without player interaction too)
            var hashes = new long[Ticks];

            for (int t = 0; t < Ticks; t++)
            {
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
