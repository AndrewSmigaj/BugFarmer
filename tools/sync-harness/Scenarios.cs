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
}
