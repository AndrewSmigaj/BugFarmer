using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using Nakama;

namespace BugFarmer.SyncHarness
{
    // The SEND side: the exact client->server messages a Unity player sends (OpCodes + JSON verified in
    // nakama/modules/world/messages.go + handlers). A scenario calls these, then waits for the server echo
    // (WorldModel updates from the S->C broadcast) before asserting.
    internal static class Actions
    {
        private const long OpMovement = 1;
        private const long OpChunkSubscribe = 3;
        private const long OpTilePlace = 5;     // place occupant (seeds route to planting via PlacesCrop)
        private const long OpTileBreak = 6;
        private const long OpToolUse = 7;       // hoe/water/scythe — server reads EquippedTool
        private const long OpCatchBug = 24;
        private const long OpEquipTool = 27;
        private const long OpPlantInteract = 55;
        private const long OpStationDeposit = 85;
        private const long OpContainer = 98;
        private const long OpSetHome = 100;

        private static Task Send(ISocket s, string matchId, long op, object payload)
            => s.SendMatchStateAsync(matchId, op, JsonSerializer.Serialize(payload));

        public static Task SubscribeChunk(ISocket s, string m, int cx, int cy)
            => Send(s, m, OpChunkSubscribe, new Dictionary<string, object> { ["chunk_x"] = cx, ["chunk_y"] = cy });

        public static Task Move(ISocket s, string m, double x, double y, int facing = 0)
            => Send(s, m, OpMovement, new Dictionary<string, object> { ["x"] = x, ["y"] = y, ["facing"] = facing });

        public static Task EquipTool(ISocket s, string m, string toolId)
            => Send(s, m, OpEquipTool, new Dictionary<string, object> { ["tool_id"] = toolId });

        public static Task Place(ISocket s, string m, int gx, int gy, string occupantId, int dir = 0)
            => Send(s, m, OpTilePlace, new Dictionary<string, object>
            { ["grid_x"] = gx, ["grid_y"] = gy, ["occupant_id"] = occupantId, ["direction"] = dir });

        // Planting IS a place of a seed occupant (the server routes to handleSeedPlanting via PlacesCrop).
        public static Task Plant(ISocket s, string m, int gx, int gy, string seedId)
            => Place(s, m, gx, gy, seedId);

        public static Task Break(ISocket s, string m, int gx, int gy)
            => Send(s, m, OpTileBreak, new Dictionary<string, object> { ["grid_x"] = gx, ["grid_y"] = gy });

        // ToolUse uses whatever tool is equipped (EquipTool first). Hoe on grass -> garden_plot.
        public static Task ToolUse(ISocket s, string m, int gx, int gy)
            => Send(s, m, OpToolUse, new Dictionary<string, object> { ["grid_x"] = gx, ["grid_y"] = gy });

        public static Task Harvest(ISocket s, string m, int gx, int gy)
            => Send(s, m, OpPlantInteract, new Dictionary<string, object> { ["grid_x"] = gx, ["grid_y"] = gy, ["destroy_intent"] = false });

        public static Task Deposit(ISocket s, string m, int gx, int gy, string itemId)
            => Send(s, m, OpStationDeposit, new Dictionary<string, object> { ["gx"] = gx, ["gy"] = gy, ["item_id"] = itemId });

        public static Task SetHome(ISocket s, string m, int gx, int gy)
            => Send(s, m, OpSetHome, new Dictionary<string, object> { ["gx"] = gx, ["gy"] = gy });

        public static Task Catch(ISocket s, string m, double x, double y, string swarmId, int[] bugIds)
            => Send(s, m, OpCatchBug, new Dictionary<string, object>
            { ["click_x"] = x, ["click_y"] = y, ["swarm_id"] = swarmId, ["bug_ids"] = bugIds });

        // ---- wait helpers (poll the world-model for the server echo) ----
        public static async Task<bool> WaitFor(Func<bool> cond, int timeoutMs = 4000)
        {
            int waited = 0;
            while (waited < timeoutMs)
            {
                if (cond()) return true;
                await Task.Delay(100);
                waited += 100;
            }
            return cond();
        }

        public static Task<bool> WaitForOccupant(int gx, int gy, string id, int timeoutMs = 4000)
            => WaitFor(() => WorldModel.OccupantAt(gx, gy) == id, timeoutMs);

        public static Task<bool> WaitForGround(int gx, int gy, string tile, int timeoutMs = 4000)
            => WaitFor(() => WorldModel.GroundAt(gx, gy) == tile, timeoutMs);
    }
}
