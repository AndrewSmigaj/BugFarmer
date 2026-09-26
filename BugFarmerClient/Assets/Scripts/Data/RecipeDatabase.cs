using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json.Linq;

namespace BugFarmer.Data
{
    /// <summary>
    /// Loads crafting recipes from Resources/Data/entities/recipes.json (published from the
    /// canonical nakama/data/entities/recipes.json). Read-only client mirror — the SERVER is the
    /// authority for all consume/produce; the client uses this only to render the panel (the recipe
    /// list per station, inputs have/need, output preview). Lazy-loaded on first access.
    /// </summary>
    public static class RecipeDatabase
    {
        public class RecipeIO
        {
            public string item;
            public int count;
        }

        public class Recipe
        {
            public string id;
            public string station;
            public List<RecipeIO> inputs = new List<RecipeIO>();
            public RecipeIO output;
            public int processTicks;
            public RecipeIO catalyst; // null when none
            public string unlock;
            public string collection; // "recipe book" group (a book grants the whole set); "" = standalone
        }

        private static Dictionary<string, Recipe> _byId;
        private static Dictionary<string, List<Recipe>> _byStation;

        public static void EnsureLoaded()
        {
            if (_byId != null) return;
            _byId = new Dictionary<string, Recipe>();
            _byStation = new Dictionary<string, List<Recipe>>();

            var ta = Resources.Load<TextAsset>("Data/entities/recipes");
            if (ta == null)
            {
                Debug.LogWarning("[RecipeDatabase] recipes.json not found under Resources/Data/entities/");
                return;
            }

            JObject root;
            try { root = JObject.Parse(ta.text); }
            catch (System.Exception e)
            {
                Debug.LogError($"[RecipeDatabase] failed to parse recipes.json: {e.Message}");
                return;
            }

            foreach (var prop in root)
            {
                if (prop.Key == "_comment") continue;
                if (!(prop.Value is JObject o)) continue;

                var r = new Recipe
                {
                    id = prop.Key,
                    station = o["station"]?.Value<string>() ?? "",
                    output = ParseIO(o["output"] as JObject),
                    processTicks = o["process_ticks"]?.Value<int>() ?? 0,
                    catalyst = ParseIO(o["catalyst"] as JObject),
                    unlock = o["unlock"]?.Value<string>() ?? "",
                    collection = o["collection"]?.Value<string>() ?? ""
                };
                if (o["inputs"] is JArray ins)
                {
                    foreach (var it in ins)
                    {
                        var io = ParseIO(it as JObject);
                        if (io != null) r.inputs.Add(io);
                    }
                }
                if (r.output == null) r.output = new RecipeIO { item = r.id, count = 1 };

                _byId[r.id] = r;
                if (!_byStation.TryGetValue(r.station, out var list))
                {
                    list = new List<Recipe>();
                    _byStation[r.station] = list;
                }
                list.Add(r);
            }
            Debug.Log($"[RecipeDatabase] loaded {_byId.Count} recipes across {_byStation.Count} stations");
        }

        private static RecipeIO ParseIO(JObject o)
        {
            if (o == null) return null;
            return new RecipeIO
            {
                item = o["item"]?.Value<string>() ?? "",
                count = o["count"]?.Value<int>() ?? 1
            };
        }

        public static Recipe Get(string id)
        {
            EnsureLoaded();
            return _byId.TryGetValue(id, out var r) ? r : null;
        }

        /// <summary>Every recipe craftable at the given station entity id (empty list if none).</summary>
        public static List<Recipe> ForStation(string stationId)
        {
            EnsureLoaded();
            return _byStation.TryGetValue(stationId, out var l) ? l : new List<Recipe>();
        }

        /// <summary>Does this placeable have any recipes (i.e. is it a craft station)?</summary>
        public static bool IsCraftStation(string stationId)
        {
            EnsureLoaded();
            return _byStation.TryGetValue(stationId, out var l) && l.Count > 0;
        }
    }
}
