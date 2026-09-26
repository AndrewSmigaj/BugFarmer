using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json.Linq;

namespace BugFarmer.Data
{
    /// <summary>
    /// Client mirror of the server's ground_recipes.json (the shovel tile-placement costs). Loads
    /// Data/entities/ground_recipes (published from the canonical JSON) into material-id -> ingredients, and
    /// resolves a composite id's FULL cost — the union (summed) of BOTH its materials' recipes — the client
    /// counterpart of the server's groundRecipeIngredients. Lets the builder panel show live have/need.
    /// Uses the same JObject approach + RecipeIO-style shape as RecipeDatabase/EntityDatabase.
    /// </summary>
    public static class GroundRecipeDatabase
    {
        public struct Ing { public string item; public int count; }

        private static Dictionary<string, List<Ing>> _byMaterial;

        public static void EnsureLoaded()
        {
            if (_byMaterial != null) return;
            _byMaterial = new Dictionary<string, List<Ing>>();
            var ta = Resources.Load<TextAsset>("Data/entities/ground_recipes");
            if (ta == null)
            {
                Debug.LogWarning("[GroundRecipeDatabase] Data/entities/ground_recipes.json not found in Resources");
                return;
            }
            try
            {
                var root = JObject.Parse(ta.text);
                foreach (var prop in root.Properties())
                {
                    if (prop.Name.StartsWith("_")) continue; // skip the _comment
                    var list = new List<Ing>();
                    foreach (var e in (JArray)prop.Value)
                        list.Add(new Ing { item = (string)e["item"], count = (int)e["count"] });
                    _byMaterial[prop.Name] = list;
                }
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[GroundRecipeDatabase] parse failed: {ex.Message}");
            }
        }

        // The material(s) a ground id is made of: [matA, matB] for a composite, [id] for a solid.
        private static List<string> MaterialsOf(string id)
        {
            if (!string.IsNullOrEmpty(id) && id.Contains("~"))
            {
                var parts = id.Split('~');
                if (parts.Length == 3)
                    return new List<string> { parts[0], parts[1] };
            }
            return new List<string> { id };
        }

        /// <summary>Ingredients to place `id`: the union (summed by item) of every material's recipe.
        /// Empty when the id has no recipe (not shovel-placeable).</summary>
        public static List<Ing> Ingredients(string id)
        {
            EnsureLoaded();
            var merged = new Dictionary<string, int>();
            var order = new List<string>();
            foreach (var mat in MaterialsOf(id))
            {
                if (!_byMaterial.TryGetValue(mat, out var list)) continue;
                foreach (var ing in list)
                {
                    if (!merged.ContainsKey(ing.item)) order.Add(ing.item);
                    merged[ing.item] = (merged.TryGetValue(ing.item, out var c) ? c : 0) + ing.count;
                }
            }
            var outList = new List<Ing>();
            foreach (var it in order)
                outList.Add(new Ing { item = it, count = merged[it] });
            return outList;
        }
    }
}
