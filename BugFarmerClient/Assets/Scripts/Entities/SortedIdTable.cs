using System;
using System.Collections;
using System.Collections.Generic;

namespace BugFarmer.Entities
{
    /// <summary>
    /// A dictionary that also keeps its keys sorted, so the bug simulation can walk the zone's groups and a group's bugs
    /// in order without sorting them again every tick (Stage 1.1, docs/plans/village-slice.md: those sorts and the lists
    /// they made ran every tick).
    ///
    /// <see cref="SortedKeys"/> is rebuilt as a NEW array after any change and never edited, so a loop that took the old
    /// array keeps the same snapshot an <c>OrderBy(id => id)</c> taken at the same moment gave it. The caller names the
    /// comparer: ordinal for the group ids (character by character, the same on every computer), the default for the
    /// integer bug ids. Keys are unique, so the comparer alone decides the order.
    /// Every change goes through this class (there is no other way to reach the dictionary), so none can be missed.
    /// </summary>
    public sealed class SortedIdTable<TKey, TValue> : IEnumerable<KeyValuePair<TKey, TValue>>
    {
        private readonly Dictionary<TKey, TValue> _map = new Dictionary<TKey, TValue>();
        private readonly IComparer<TKey> _comparer;
        private TKey[] _sorted = Array.Empty<TKey>();
        private bool _dirty;

        public SortedIdTable(IComparer<TKey> comparer)
        {
            _comparer = comparer;
        }

        public int Count => _map.Count;
        public Dictionary<TKey, TValue>.KeyCollection Keys => _map.Keys;
        public Dictionary<TKey, TValue>.ValueCollection Values => _map.Values;

        public TValue this[TKey key]
        {
            get => _map[key];
            set
            {
                if (!_map.ContainsKey(key)) _dirty = true;
                _map[key] = value;
            }
        }

        public bool TryGetValue(TKey key, out TValue value) => _map.TryGetValue(key, out value);
        public bool ContainsKey(TKey key) => _map.ContainsKey(key);

        public bool Remove(TKey key)
        {
            if (!_map.Remove(key)) return false;
            _dirty = true;
            return true;
        }

        public void Clear()
        {
            if (_map.Count == 0) return;
            _map.Clear();
            _dirty = true;
        }

        /// <summary>The keys in order; a new array after any change, never edited.</summary>
        public TKey[] SortedKeys
        {
            get
            {
                if (_dirty)
                {
                    var keys = new TKey[_map.Count];
                    _map.Keys.CopyTo(keys, 0);
                    Array.Sort(keys, _comparer);
                    _sorted = keys;
                    _dirty = false;
                }
                return _sorted;
            }
        }

        public Dictionary<TKey, TValue>.Enumerator GetEnumerator() => _map.GetEnumerator();
        IEnumerator<KeyValuePair<TKey, TValue>> IEnumerable<KeyValuePair<TKey, TValue>>.GetEnumerator() => _map.GetEnumerator();
        IEnumerator IEnumerable.GetEnumerator() => _map.GetEnumerator();
    }
}
