using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using Nakama;

namespace BugFarmer.SyncHarness
{
    // A scripted scenario: act (via Actions) then assert (via WorldModel). Selected with --scenario.
    // Add a test = add a class here + register it in Get(). The process exit code is WorldModel.ExitCode.
    internal interface IScenario
    {
        Task RunAsync(ISocket socket, string matchId);
    }

    internal static class Scenarios
    {
        public static IScenario Get(string name)
        {
            switch (name)
            {
                case "farm-build": return new FarmBuildScenario();
                case "farm-verify": return new FarmVerifyScenario();
                case "crosszone": return new CrossZoneScenario();
                // The village↔Bee Meadow edge pair (road contract y=124). Run WEST with
                // --zone village_21_B, EAST with --zone bee_meadow_20.
                case "crosszone-west": return new CrossZoneHopScenario("bee_meadow_20", 253f, 124f);
                case "crosszone-east": return new CrossZoneHopScenario("village_21_B", 2f, 124f);
                // The saves crash test (tools/harness_crash_test.sh), in persist_a / persist_b, with --char.
                case "fences-place": return new FencesPlaceScenario();
                case "fences-count": return new FencesCountScenario();
                case "cross-fences": return new CrossFencesScenario();
                case "bag-count": return new BagCountScenario();
                default: return null;
            }
        }
    }

    // Shared fixed cells for the farm-persistence test. sim_test spawn = (48,48); the whole zone is empty
    // grass, so these are valid + deterministic, and BOTH scenarios use the same constants (no state file).
    internal static class FarmCells
    {
        public const int CropX = 48, CropY = 48;   // hoe + plant
        public const int BenchX = 52, BenchY = 48; // place bench
        public const int FenceX = 56, FenceY = 48; // place fence
        public const int SpawnChunkX = 1, SpawnChunkY = 1;
    }

    // Build a small farm: till + plant a tomato, place a bench + a fence. Then disconnect (Main closes the
    // socket → MatchLeave → on-empty save; the wrapper's restart also fires the MatchTerminate save).
    internal sealed class FarmBuildScenario : IScenario
    {
        public async Task RunAsync(ISocket s, string m)
        {
            Console.WriteLine("[scenario] farm-build");
            await Task.Delay(900); // settle: FullInventorySync + initial ChunkData

            await Actions.EquipTool(s, m, "hoe_wood");
            await Task.Delay(400);

            await Actions.ToolUse(s, m, FarmCells.CropX, FarmCells.CropY); // hoe grass -> garden_plot
            await Actions.WaitForGround(FarmCells.CropX, FarmCells.CropY, "garden_plot", 4000);

            await Actions.Plant(s, m, FarmCells.CropX, FarmCells.CropY, "seed_tomato");
            await Actions.WaitFor(() => WorldModel.HasCrop(FarmCells.CropX, FarmCells.CropY)
                                       || WorldModel.OccupantAt(FarmCells.CropX, FarmCells.CropY) != null, 4000);

            await Actions.Place(s, m, FarmCells.BenchX, FarmCells.BenchY, "bench");
            await Actions.WaitForOccupant(FarmCells.BenchX, FarmCells.BenchY, "bench", 4000);

            await Actions.Place(s, m, FarmCells.FenceX, FarmCells.FenceY, "fence_wood");
            await Actions.WaitForOccupant(FarmCells.FenceX, FarmCells.FenceY, "fence_wood", 4000);

            Console.WriteLine($"[scenario] build local view: ground@crop={WorldModel.GroundAt(FarmCells.CropX, FarmCells.CropY)} " +
                              $"crop={WorldModel.HasCrop(FarmCells.CropX, FarmCells.CropY)} " +
                              $"bench={WorldModel.OccupantAt(FarmCells.BenchX, FarmCells.BenchY)} " +
                              $"fence={WorldModel.OccupantAt(FarmCells.FenceX, FarmCells.FenceY)}");
            await Task.Delay(1200); // let final echoes settle before the socket closes
        }
    }

    // CROSS-ZONE: enter village_21 (via Program.Enter), then leave + enter the south neighbor
    // (underground_passages_31) with an entry position on its NORTH edge, and assert the server placed
    // us there (PlayerSpawn 102) instead of the zone spawn_point. Proves the entry-override end to end.
    internal sealed class CrossZoneScenario : IScenario
    {
        private const string Neighbor = "underground_passages_31";
        private const float EntryX = 128f, EntryY = 253f; // north edge (y=255) inset 2

        public async Task RunAsync(ISocket s, string m)
        {
            Console.WriteLine("[scenario] crosszone: village_21 -> underground (south neighbor) at its north edge");
            await Task.Delay(700); // village PlayerSpawn arrives first

            await s.LeaveMatchAsync(m);          // leave village
            await Task.Delay(400);
            WorldModel.ResetSpawn();             // ignore village's spawn; capture the neighbor's

            var enter = JsonSerializer.Serialize(new Dictionary<string, object> { ["zone_id"] = Neighbor });
            var rpc = await Program.Client.RpcAsync(Program.Session, "world_enter", enter);
            string m2; using (var d = JsonDocument.Parse(rpc.Payload)) m2 = d.RootElement.GetProperty("match_id").GetString();

            var meta = new Dictionary<string, string>
            {
                ["entry_x"] = EntryX.ToString("F1", System.Globalization.CultureInfo.InvariantCulture),
                ["entry_y"] = EntryY.ToString("F1", System.Globalization.CultureInfo.InvariantCulture),
            };
            await s.JoinMatchAsync(m2, meta);
            Console.WriteLine($"[scenario] joined {Neighbor} with entry ({EntryX},{EntryY})");

            bool got = await Actions.WaitFor(() => WorldModel.SpawnSeen(), 6000);
            WorldModel.Assert(got, "received PlayerSpawn in the neighbor zone");
            if (got)
            {
                var (sx, sy) = WorldModel.LastSpawn();
                Console.WriteLine($"[scenario] neighbor PlayerSpawn = ({sx:F1},{sy:F1})");
                WorldModel.Assert(Math.Abs(sx - EntryX) < 1.5 && Math.Abs(sy - EntryY) < 1.5,
                    $"spawned at the cross-zone entry ({EntryX},{EntryY}) [got ({sx:F1},{sy:F1})]");
            }
            await Task.Delay(1500); // let a few ticks confirm no sync gap on the join
        }
    }

    // CROSS-ZONE HOP (parameterized): leave the --zone match, enter `neighbor` with an entry
    // position, and assert the server spawned us AT the entry (PlayerSpawn 102) — the same
    // proof CrossZoneScenario gives for the village→underground edge, reused for any pair.
    internal sealed class CrossZoneHopScenario : IScenario
    {
        private readonly string _neighbor;
        private readonly float _ex, _ey;
        public CrossZoneHopScenario(string neighbor, float ex, float ey)
        { _neighbor = neighbor; _ex = ex; _ey = ey; }

        public async Task RunAsync(ISocket s, string m)
        {
            Console.WriteLine($"[scenario] crosszone hop -> {_neighbor} at ({_ex},{_ey})");
            await Task.Delay(700);

            await s.LeaveMatchAsync(m);
            await Task.Delay(400);
            WorldModel.ResetSpawn();

            var enter = JsonSerializer.Serialize(new Dictionary<string, object> { ["zone_id"] = _neighbor });
            var rpc = await Program.Client.RpcAsync(Program.Session, "world_enter", enter);
            string m2; using (var d = JsonDocument.Parse(rpc.Payload)) m2 = d.RootElement.GetProperty("match_id").GetString();

            var meta = new Dictionary<string, string>
            {
                ["entry_x"] = _ex.ToString("F1", System.Globalization.CultureInfo.InvariantCulture),
                ["entry_y"] = _ey.ToString("F1", System.Globalization.CultureInfo.InvariantCulture),
            };
            await s.JoinMatchAsync(m2, meta);

            bool got = await Actions.WaitFor(() => WorldModel.SpawnSeen(), 6000);
            WorldModel.Assert(got, $"received PlayerSpawn in {_neighbor}");
            if (got)
            {
                var (sx, sy) = WorldModel.LastSpawn();
                Console.WriteLine($"[scenario] {_neighbor} PlayerSpawn = ({sx:F1},{sy:F1})");
                WorldModel.Assert(Math.Abs(sx - _ex) < 1.5 && Math.Abs(sy - _ey) < 1.5,
                    $"spawned at the cross-zone entry ({_ex},{_ey}) [got ({sx:F1},{sy:F1})]");
            }
            await Task.Delay(1500);
        }
    }

    // Rejoin AFTER a server restart and assert the farm + bug population came back from storage.
    internal sealed class FarmVerifyScenario : IScenario
    {
        public async Task RunAsync(ISocket s, string m)
        {
            Console.WriteLine("[scenario] farm-verify (post-restart)");
            // Enter() already subscribed chunks → ChunkData + CropUpdate are streaming in; wait for our cells.
            await Actions.WaitForOccupant(FarmCells.BenchX, FarmCells.BenchY, "bench", 6000);
            await Actions.WaitForOccupant(FarmCells.FenceX, FarmCells.FenceY, "fence_wood", 6000);
            await Actions.WaitFor(() => WorldModel.HasCrop(FarmCells.CropX, FarmCells.CropY), 6000);
            await Task.Delay(2000); // let swarm updates arrive

            Console.WriteLine("[scenario] asserting restored farm:");
            WorldModel.AssertOccupantAt(FarmCells.BenchX, FarmCells.BenchY, "bench");
            WorldModel.AssertOccupantAt(FarmCells.FenceX, FarmCells.FenceY, "fence_wood");
            WorldModel.AssertGroundAt(FarmCells.CropX, FarmCells.CropY, "garden_plot"); // tilled soil persisted
            WorldModel.AssertCropAt(FarmCells.CropX, FarmCells.CropY);
            WorldModel.AssertSwarmsAtLeast(1); // bug population restored
        }
    }

    // ---- The saves crash test (tools/harness_crash_test.sh) ----
    // Fences are the counted item: a new character carries 50 (the starting kit). Whatever happens — a crash, a clean
    // stop, a zone crossing, a reconnect — the fences in the world plus the fences in the bag must stay 50.
    internal static class FenceCells
    {
        public const int Row = 44, FirstX = 36;    // fences go in a row at y=44: x = 36, 37, …
        public const int BedX = 48, BedY = 50;     // persist_a's bed (make_test_zone --occupant bed_basic@48,50)
        public const string Neighbor = "persist_b"; // persist_a's east neighbour
        public const double EntryX = 2, EntryY = 44; // persist_b's west edge, where a crossing from persist_a lands
    }

    internal static class Fences
    {
        // The join's full inventory, and the zone's chunks, before anything is read or placed.
        public static async Task Settle()
        {
            await Actions.WaitFor(() => WorldModel.InventorySyncCount() > 0, 6000);
            await Task.Delay(900);
        }

        // Place `count` fences in the next free cells of the row; returns how many the server confirmed.
        public static async Task<int> Place(ISocket s, string m, int count)
        {
            int before = WorldModel.ItemCount("fence_wood"), placed = 0;
            for (int x = FenceCells.FirstX; placed < count && x < FenceCells.FirstX + 24; x++)
            {
                if (WorldModel.OccupantAt(x, FenceCells.Row) != null) continue;
                await Actions.Place(s, m, x, FenceCells.Row, "fence_wood");
                if (await Actions.WaitForOccupant(x, FenceCells.Row, "fence_wood", 4000)) placed++;
            }
            await Actions.WaitFor(() => WorldModel.ItemCount("fence_wood") == before - placed, 3000);
            return placed;
        }
    }

    // fences-place: place --count fences; with --sleep, sleep in persist_a's bed (it saves the character); then stay
    // connected for --hold seconds — the crash test stops or kills the server meanwhile — and leave.
    internal sealed class FencesPlaceScenario : IScenario
    {
        public async Task RunAsync(ISocket s, string m)
        {
            var o = Program.Opt;
            await Fences.Settle();
            int placed = await Fences.Place(s, m, o.Count);
            Console.WriteLine($"[scenario] PLACED {placed} fence(s); BAG fence_wood={WorldModel.ItemCount("fence_wood")}");
            if (o.Sleep)
            {
                await Actions.SetHome(s, m, FenceCells.BedX, FenceCells.BedY);
                await Task.Delay(1500);
                Console.WriteLine("[scenario] SLEPT in the bed");
            }
            if (o.Hold > 0)
            {
                Console.WriteLine($"[scenario] HOLDING {o.Hold}s");
                await Task.Delay(o.Hold * 1000);
            }
            await Task.Delay(800);
        }
    }

    // fences-count: after a restart, count the fences in the zone and in the bag. --expect N asserts the total.
    internal sealed class FencesCountScenario : IScenario
    {
        public async Task RunAsync(ISocket s, string m)
        {
            await Fences.Settle();
            await Task.Delay(1500); // every subscribed chunk's data
            int world = WorldModel.OccupantCount("fence_wood"), bag = WorldModel.ItemCount("fence_wood");
            Console.WriteLine($"[scenario] COUNT world={world} bag={bag} total={world + bag}");
            if (Program.Opt.Expect >= 0)
                WorldModel.Assert(world + bag == Program.Opt.Expect,
                    $"fences in the world + in the bag = {Program.Opt.Expect} [got {world} + {bag} = {world + bag}]");
        }
    }

    // cross-fences: place --count fences in persist_a, walk into persist_b (leave, then enter at its west edge), and
    // check the bag there is the bag that left — not an older saved copy. persist_a holds back its departure save
    // (debug_leave_delay_ms), so the next zone always loads before that save lands: the crossing race, every time.
    internal sealed class CrossFencesScenario : IScenario
    {
        public async Task RunAsync(ISocket s, string m)
        {
            var o = Program.Opt;
            await Fences.Settle();
            int placed = await Fences.Place(s, m, o.Count);
            int left = WorldModel.ItemCount("fence_wood");
            Console.WriteLine($"[scenario] PLACED {placed}; leaving with BAG fence_wood={left}");

            int syncs = WorldModel.InventorySyncCount();
            await s.LeaveMatchAsync(m); // Nakama acknowledges this before the zone has run its leave
            string m2 = await Program.EnterZone(s, FenceCells.Neighbor, FenceCells.EntryX, FenceCells.EntryY);
            bool synced = await Actions.WaitFor(() => WorldModel.InventorySyncCount() > syncs, 8000);
            WorldModel.Assert(synced, $"entered {FenceCells.Neighbor} and received the character's inventory");
            int arrived = WorldModel.ItemCount("fence_wood");
            Console.WriteLine($"[scenario] arrived in {FenceCells.Neighbor} with BAG fence_wood={arrived}");
            WorldModel.Assert(arrived == left,
                $"the bag that arrived is the bag that left: {left} fences [got {arrived}]");
            await Task.Delay(1200);
        }
    }

    // bag-count: join and report the bag (the crash test's reconnect case runs it as a second copy of the game while
    // the first is still connected). --expect N asserts it.
    internal sealed class BagCountScenario : IScenario
    {
        public async Task RunAsync(ISocket s, string m)
        {
            await Fences.Settle();
            int bag = WorldModel.ItemCount("fence_wood");
            Console.WriteLine($"[scenario] BAG fence_wood={bag}");
            if (Program.Opt.Expect >= 0)
                WorldModel.Assert(bag == Program.Opt.Expect, $"the bag holds {Program.Opt.Expect} fences [got {bag}]");
        }
    }
}
