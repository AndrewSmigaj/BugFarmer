using System.Collections.Generic;
using UnityEngine;

namespace BugFarmer.UI
{
    /// <summary>
    /// ScriptableObject database mapping item IDs to inventory icons.
    /// Create via Assets > Create > BugFarmer > ItemDatabase.
    /// Place the asset in a Resources folder for auto-loading.
    /// </summary>
    [CreateAssetMenu(fileName = "ItemDatabase", menuName = "BugFarmer/ItemDatabase")]
    public class ItemDatabase : ScriptableObject
    {
        private static ItemDatabase _instance;

        [System.Serializable]
        public class ItemEntry
        {
            public string itemId;
            public Sprite icon;
            public string displayName;
        }

        [SerializeField] private ItemEntry[] items;

        private Dictionary<string, ItemEntry> _lookup;

        public static ItemDatabase Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = Resources.Load<ItemDatabase>("ItemDatabase");
                    if (_instance == null)
                    {
                        Debug.LogWarning("[ItemDatabase] Not found in Resources. Create via Assets > Create > BugFarmer > ItemDatabase");
                    }
                    else
                    {
                        _instance.BuildLookup();
                    }
                }
                return _instance;
            }
        }

        private void BuildLookup()
        {
            _lookup = new Dictionary<string, ItemEntry>();
            if (items == null) return;

            foreach (var entry in items)
            {
                if (!string.IsNullOrEmpty(entry.itemId))
                {
                    _lookup[entry.itemId] = entry;
                }
            }
        }

        public static Sprite GetSprite(string itemId)
        {
            if (string.IsNullOrEmpty(itemId))
                return null;

            // Try manual lookup first
            if (Instance != null)
            {
                if (Instance._lookup == null)
                    Instance.BuildLookup();

                if (Instance._lookup.TryGetValue(itemId, out var entry) && entry.icon != null)
                    return entry.icon;
            }

            // Fallback: load by convention from Resources/Items/
            return Resources.Load<Sprite>($"Items/{itemId}");
        }

        public static string GetDisplayName(string itemId)
        {
            if (string.IsNullOrEmpty(itemId) || Instance == null)
                return itemId;

            if (Instance._lookup == null)
                Instance.BuildLookup();

            if (Instance._lookup.TryGetValue(itemId, out var entry) && !string.IsNullOrEmpty(entry.displayName))
                return entry.displayName;

            return itemId;
        }
    }
}
