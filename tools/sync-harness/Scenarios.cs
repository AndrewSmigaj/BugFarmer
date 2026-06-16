using System;
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
