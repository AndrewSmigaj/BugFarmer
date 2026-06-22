// Minimal stand-ins for the handful of Unity / Unity-singleton types the linked client sim touches.
// The sim core is deliberately Unity-independent (fixed-point math + counter RNG); these shims only cover
// the render-helper Vector2 and the two singletons the sim NULL-CHECKS (so headless => no food, no walls,
// which is fully deterministic). EntityDatabase here reads the real species.json so per-species movement
// (brownian/gliding/darting/crawling, player_reaction, flies_over_fences) matches what ships.

using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace UnityEngine
{
    public struct Vector2
    {
        public float x, y;
        public Vector2(float x, float y) { this.x = x; this.y = y; }
    }

    public struct Vector2Int
    {
        public int x, y;
        public Vector2Int(int x, int y) { this.x = x; this.y = y; }
    }

    // Logging is a no-op headless (the sim's diagnostics don't affect state).
    public static class Debug
    {
        public static void Log(object _) { }
        public static void LogWarning(object _) { }
        public static void LogError(object _) { }
    }

    // Only the members the linked sim could reference. All pure functions (deterministic).
    public static class Mathf
    {
        public const float PI = 3.14159265358979f;
        public static float Clamp(float v, float a, float b) => v < a ? a : (v > b ? b : v);
        public static int Clamp(int v, int a, int b) => v < a ? a : (v > b ? b : v);
        public static float Clamp01(float v) => v < 0f ? 0f : (v > 1f ? 1f : v);
        public static float Abs(float v) => v < 0 ? -v : v;
        public static int Abs(int v) => v < 0 ? -v : v;
        public static float Min(float a, float b) => a < b ? a : b;
        public static float Max(float a, float b) => a > b ? a : b;
        public static float Sqrt(float v) => (float)Math.Sqrt(v);
        public static int FloorToInt(float v) => (int)Math.Floor(v);
        public static int RoundToInt(float v) => (int)Math.Round(v);
        public static float Sin(float v) => (float)Math.Sin(v);
        public static float Cos(float v) => (float)Math.Cos(v);
        public static float Atan2(float y, float x) => (float)Math.Atan2(y, x);
    }
}

namespace BugFarmer.World
{
    // Headless: no tilemap loaded => Instance is null => BugCollision treats every cell as walkable.
    public class TilemapManager
    {
        public static TilemapManager Instance => null;
        public bool IsCellBlockedForBugs(UnityEngine.Vector2Int cell, bool ignoreOccupants = false) => false;
    }
}

namespace BugFarmer.Util
{
    public static class DebugFileLogger
    {
        public static void Log(string _) { }
    }
}

namespace BugFarmer.Bugs
{
    // The food registry is fed from server/chunk state on a live client. Headless: Instance is null =>
    // BugAgent.TryFeedAtFood returns false (bugs wander, never "land on food"). Deterministic. The method
    // body never runs (Instance is null); it exists only so the linked BugAgent compiles.
    public class InfluenceManager
    {
        public static InfluenceManager Instance => null;
        public bool TryGetNearestFood(FixedPoint2 center, float radius, out FixedPoint2 food)
        {
            food = FixedPoint2.Zero;
            return false;
        }
    }
}

namespace BugFarmer.Data
{
    // Reads the real nakama/data/species.json so the linked MovementFactory picks each species' true
    // movement_style + player_reaction (the data that feeds the deterministic per-bug sim).
    public static class EntityDatabase
    {
        public class SpeciesInfo
        {
            public string MovementStyle = "";
            public string PlayerReaction = "ignore";
            public float ReactionRadius;
            public bool FliesOverFences;
        }

        private static Dictionary<string, SpeciesInfo> _cache;

        public static SpeciesInfo GetSpecies(string speciesId)
        {
            if (_cache == null) Load();
            return _cache.TryGetValue(speciesId, out var s) ? s : null;
        }

        private static void Load()
        {
            _cache = new Dictionary<string, SpeciesInfo>();
            var path = Path.Combine(SimDeterminism.Program.RepoRoot, "nakama", "data", "species.json");
            using var doc = JsonDocument.Parse(File.ReadAllText(path));
            foreach (var prop in doc.RootElement.EnumerateObject())
            {
                var o = prop.Value;
                _cache[prop.Name] = new SpeciesInfo
                {
                    MovementStyle = o.TryGetProperty("movement_style", out var ms) ? (ms.GetString() ?? "") : "",
                    PlayerReaction = o.TryGetProperty("player_reaction", out var pr) ? (pr.GetString() ?? "ignore") : "ignore",
                    ReactionRadius = o.TryGetProperty("reaction_radius", out var rr) ? (float)rr.GetDouble() : 0f,
                    FliesOverFences = o.TryGetProperty("flies_over_fences", out var ff) && ff.ValueKind == JsonValueKind.True,
                };
            }
        }
    }
}
