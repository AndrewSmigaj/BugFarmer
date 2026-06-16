using System;
using System.Collections.Generic;
using System.Text.Json;

namespace BugFarmer.SyncHarness
{
    // The harness's view of the world, built from the S->C farm/inventory messages it now parses
    // (the observer ignored these). Scenarios act, then assert against this model. Updated on the socket
    // callback thread + read by the scenario thread, so every access is under _gate.
    internal static class WorldModel
    {
        // S->C opcodes (verified in nakama/modules/world/messages.go).
        private const long OpEntityUpdate = 11;
        private const long OpSwarmUpdate = 20;
        private const long OpItemSlotUpdate = 37;
        private const long OpFullInventorySync = 38;
        private const long OpErrorMessage = 40;
        private const long OpChunkData = 44;
        private const long OpWorldUpdate = 46;
        private const long OpGroundItemSpawn = 47;
        private const long OpGroundItemRemove = 48;
        private const long OpCropUpdate = 50;
        private const long OpPlayerSpawn = 102;

        private static readonly object _gate = new object();

        private static readonly Dictionary<(int, int), string> _ground = new();      // (gx,gy) -> tile id
        private static readonly Dictionary<(int, int), string> _occupants = new();   // (gx,gy) -> occupant id
        private static readonly Dictionary<(int, int), (int stage, int hp, int water)> _crops = new();
        private static readonly Dictionary<string, (string type, int count)> _groundItems = new();
        private static readonly Dictionary<int, (string id, int count)> _itemSlots = new();
        private static readonly HashSet<string> _swarmIds = new();
        private static int _swarmBugTotal;
        private static double _myX, _myY;

        // 0 = all asserts passed; set to 1 by a failing Assert (drives the process exit code).
        public static int ExitCode = 0;

        public static void ResetAsserts() { lock (_gate) { ExitCode = 0; } }

        public static void Apply(long op, string json)
        {
            try
            {
                switch (op)
                {
                    case OpChunkData: ApplyChunkData(json); break;
                    case OpWorldUpdate: ApplyWorldUpdate(json); break;
                    case OpCropUpdate: ApplyCropUpdate(json); break;
                    case OpGroundItemSpawn: ApplyGroundItemSpawn(json); break;
                    case OpGroundItemRemove: ApplyGroundItemRemove(json); break;
                    case OpFullInventorySync: ApplyInventory(json); break;
                    case OpItemSlotUpdate: ApplySlotUpdate(json); break;
                    case OpEntityUpdate: ApplyEntityUpdate(json); break;
                    case OpPlayerSpawn: ApplyPlayerSpawn(json); break;
                    case OpSwarmUpdate: ApplySwarmUpdate(json); break;
                    case OpErrorMessage: ApplyError(json); break;
                }
            }
            catch (Exception ex) { Console.WriteLine($"[wm] parse err op{op}: {ex.Message}"); }
        }

        private static void ApplyChunkData(string json)
        {
            using var doc = JsonDocument.Parse(json);
            var r = doc.RootElement;
            int cx = r.GetProperty("chunk_x").GetInt32();
            int cy = r.GetProperty("chunk_y").GetInt32();
            lock (_gate)
            {
                if (r.TryGetProperty("ground", out var g) && g.ValueKind == JsonValueKind.Array)
                {
                    int ly = 0;
                    foreach (var row in g.EnumerateArray())
                    {
                        int lx = 0;
                        foreach (var tile in row.EnumerateArray())
                        {
                            _ground[(cx * 32 + lx, cy * 32 + ly)] = tile.GetString();
                            lx++;
                        }
                        ly++;
                    }
                }
                if (r.TryGetProperty("occupants", out var occ) && occ.ValueKind == JsonValueKind.Array)
                {
                    int ly = 0;
                    foreach (var row in occ.EnumerateArray())
                    {
                        int lx = 0;
                        foreach (var cell in row.EnumerateArray())
                        {
                            var key = (cx * 32 + lx, cy * 32 + ly);
                            if (cell.ValueKind == JsonValueKind.Object && cell.TryGetProperty("id", out var idp))
                                _occupants[key] = idp.GetString();
                            else
                                _occupants.Remove(key);
                            lx++;
                        }
                        ly++;
                    }
                }
            }
        }

        private static void ApplyWorldUpdate(string json)
        {
            using var doc = JsonDocument.Parse(json);
            var r = doc.RootElement;
            int gx = r.GetProperty("grid_x").GetInt32();
            int gy = r.GetProperty("grid_y").GetInt32();
            lock (_gate)
            {
                if (r.TryGetProperty("ground", out var g) && g.ValueKind == JsonValueKind.String && g.GetString().Length > 0)
                    _ground[(gx, gy)] = g.GetString();
                if (r.TryGetProperty("occupant", out var o))
                {
                    if (o.ValueKind == JsonValueKind.Object && o.TryGetProperty("id", out var idp))
                        _occupants[(gx, gy)] = idp.GetString();
                    else if (o.ValueKind == JsonValueKind.Null)
                        _occupants.Remove((gx, gy));
                }
            }
        }

        private static void ApplyCropUpdate(string json)
        {
            using var doc = JsonDocument.Parse(json);
            var r = doc.RootElement;
            int gx = r.GetProperty("grid_x").GetInt32();
            int gy = r.GetProperty("grid_y").GetInt32();
            int stage = r.TryGetProperty("stage", out var s) ? s.GetInt32() : 0;
            int hp = r.TryGetProperty("hp", out var h) ? h.GetInt32() : 0;
            int water = r.TryGetProperty("water", out var w) ? w.GetInt32() : 0;
            lock (_gate) _crops[(gx, gy)] = (stage, hp, water);
        }

        private static void ApplyGroundItemSpawn(string json)
        {
            using var doc = JsonDocument.Parse(json);
            var r = doc.RootElement;
            string id = r.GetProperty("id").GetString();
            string type = r.TryGetProperty("item_type", out var t) ? t.GetString() : "";
            int count = r.TryGetProperty("count", out var c) ? c.GetInt32() : 1;
            lock (_gate) _groundItems[id] = (type, count);
        }

        private static void ApplyGroundItemRemove(string json)
        {
            using var doc = JsonDocument.Parse(json);
            if (doc.RootElement.TryGetProperty("id", out var idp))
                lock (_gate) _groundItems.Remove(idp.GetString());
        }

        private static void ApplyInventory(string json)
        {
            using var doc = JsonDocument.Parse(json);
            if (doc.RootElement.TryGetProperty("item_slots", out var slots) && slots.ValueKind == JsonValueKind.Array)
            {
                lock (_gate)
                {
                    int i = 0;
                    foreach (var s in slots.EnumerateArray())
                    {
                        string id = s.TryGetProperty("item_id", out var ip) ? ip.GetString() : "";
                        int cnt = s.TryGetProperty("count", out var cp) ? cp.GetInt32() : 0;
                        _itemSlots[i] = (id, cnt);
                        i++;
                    }
                }
            }
        }

        private static void ApplySlotUpdate(string json)
        {
            using var doc = JsonDocument.Parse(json);
            var r = doc.RootElement;
            if (!r.TryGetProperty("slot_index", out var si)) return;
            int idx = si.GetInt32();
            string id = r.TryGetProperty("item_id", out var ip) ? ip.GetString() : "";
            int cnt = r.TryGetProperty("count", out var cp) ? cp.GetInt32() : 0;
            lock (_gate) _itemSlots[idx] = (id, cnt);
        }

        private static void ApplyEntityUpdate(string json)
        {
            using var doc = JsonDocument.Parse(json);
            if (!doc.RootElement.TryGetProperty("entities", out var ents) || ents.ValueKind != JsonValueKind.Array) return;
            foreach (var e in ents.EnumerateArray())
            {
                if (!e.TryGetProperty("id", out var idp)) continue;
                if (idp.GetString() == "player_" + Program.MyUserId)
                {
                    lock (_gate)
                    {
                        _myX = e.TryGetProperty("x", out var xp) ? xp.GetDouble() : _myX;
                        _myY = e.TryGetProperty("y", out var yp) ? yp.GetDouble() : _myY;
                    }
                }
            }
        }

        private static void ApplyPlayerSpawn(string json)
        {
            using var doc = JsonDocument.Parse(json);
            var r = doc.RootElement;
            lock (_gate)
            {
                _myX = r.TryGetProperty("x", out var xp) ? xp.GetDouble() : _myX;
                _myY = r.TryGetProperty("y", out var yp) ? yp.GetDouble() : _myY;
            }
        }

        private static void ApplySwarmUpdate(string json)
        {
            using var doc = JsonDocument.Parse(json);
            if (!doc.RootElement.TryGetProperty("swarms", out var sw) || sw.ValueKind != JsonValueKind.Array) return;
            lock (_gate)
            {
                int total = 0;
                foreach (var s in sw.EnumerateArray())
                {
                    if (s.TryGetProperty("id", out var idp)) _swarmIds.Add(idp.GetString());
                    if (s.TryGetProperty("count", out var cp)) total += cp.GetInt32();
                }
                if (total > _swarmBugTotal) _swarmBugTotal = total; // peak seen this session
            }
        }

        private static void ApplyError(string json)
        {
            using var doc = JsonDocument.Parse(json);
            if (doc.RootElement.TryGetProperty("error", out var ep))
                Console.WriteLine($"[wm] WorldError: {ep.GetString()}");
        }

        // ---- read accessors (locked) ----
        public static string OccupantAt(int gx, int gy) { lock (_gate) return _occupants.TryGetValue((gx, gy), out var v) ? v : null; }
        public static string GroundAt(int gx, int gy) { lock (_gate) return _ground.TryGetValue((gx, gy), out var v) ? v : null; }
        public static bool HasCrop(int gx, int gy) { lock (_gate) return _crops.ContainsKey((gx, gy)); }
        public static int SwarmCount() { lock (_gate) return _swarmIds.Count; }
        public static int SwarmBugTotal() { lock (_gate) return _swarmBugTotal; }

        // ---- assertions (set ExitCode=1 on failure) ----
        public static void Assert(bool cond, string msg)
        {
            if (cond) Console.WriteLine($"[assert] PASS: {msg}");
            else { Console.WriteLine($"[assert] FAIL: {msg}"); lock (_gate) ExitCode = 1; }
        }

        public static void AssertOccupantAt(int gx, int gy, string id)
            => Assert(OccupantAt(gx, gy) == id, $"occupant '{id}' at ({gx},{gy}) [got '{OccupantAt(gx, gy) ?? "none"}']");

        public static void AssertGroundAt(int gx, int gy, string tile)
            => Assert(GroundAt(gx, gy) == tile, $"ground '{tile}' at ({gx},{gy}) [got '{GroundAt(gx, gy) ?? "none"}']");

        public static void AssertCropAt(int gx, int gy)
            => Assert(HasCrop(gx, gy), $"crop present at ({gx},{gy})");

        public static void AssertSwarmsAtLeast(int n)
            => Assert(SwarmCount() >= n, $"swarm count >= {n} [got {SwarmCount()}]");
    }
}
