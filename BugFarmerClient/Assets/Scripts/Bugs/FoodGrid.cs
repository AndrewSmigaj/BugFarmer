using System.Collections.Generic;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// The deterministic food registry (food id -> world position and level) with a cell index, so "the nearest food
    /// within r of a point" checks only the cells the search square touches instead of every food in the zone
    /// (Stage 1.1 of docs/plans/village-slice.md: the full scan was up to 91% of the client's bug-simulation time).
    ///
    /// Same answer as checking every entry: the nearest by fixed-point squared distance, ties to the lower id (ordinal).
    /// That is a total order, so only the SET of candidates in range decides the result, never the order they are
    /// visited in; the cells searched cover the whole range plus a margin, so every candidate in range is seen.
    ///
    /// The last answer is kept per (registry version, point, radius): the bugs of one group all ask with the group's
    /// centre in the same tick, and the registry only changes between ticks (events), so the group shares one lookup.
    /// The id -> entry dictionary is written in the same order as the old one, so anything that lists the food (the
    /// authority's snapshot export) sees the same order as before. No Unity types: the sim-determinism harness tests it
    /// against the full scan (--food-index-test).
    /// </summary>
    public sealed class FoodGrid
    {
        /// <summary>Cell size in fixed-point units (×1000): 4 world cells.</summary>
        public const int CellSize = 4000;

        private readonly Dictionary<string, (FixedPoint2 pos, int level)> _entries = new Dictionary<string, (FixedPoint2, int)>();
        private readonly Dictionary<long, List<string>> _cells = new Dictionary<long, List<string>>();
        private int _version;

        // The last nearest-food answer (TryGetNearestCached).
        private int _memoVersion = -1;
        private FixedPoint2 _memoFrom;
        private int _memoMaxSqr;
        private bool _memoFound;
        private FixedPoint2 _memoPos;

        public int Count => _entries.Count;
        public IEnumerable<KeyValuePair<string, (FixedPoint2 pos, int level)>> Entries => _entries;
        public bool Contains(string id) => _entries.ContainsKey(id);
        public bool TryGet(string id, out (FixedPoint2 pos, int level) entry) => _entries.TryGetValue(id, out entry);

        /// <summary>Add or overwrite an entry (an overwrite may move it to another cell).</summary>
        public void Set(string id, FixedPoint2 pos, int level)
        {
            long key = CellKey(pos);
            if (_entries.TryGetValue(id, out var old))
            {
                long oldKey = CellKey(old.pos);
                if (oldKey != key)
                {
                    RemoveFromCell(oldKey, id);
                    AddToCell(key, id);
                }
            }
            else
            {
                AddToCell(key, id);
            }
            _entries[id] = (pos, level);
            _version++;
        }

        public bool Remove(string id)
        {
            if (!_entries.TryGetValue(id, out var old)) return false;
            RemoveFromCell(CellKey(old.pos), id);
            _entries.Remove(id);
            _version++;
            return true;
        }

        public void Clear()
        {
            _entries.Clear();
            _cells.Clear();
            _version++;
        }

        /// <summary>The nearest food within maxDist of from (its position only), reusing the last answer when the
        /// registry, the point and the radius are all unchanged.</summary>
        public bool TryGetNearestCached(FixedPoint2 from, float maxDist, out FixedPoint2 pos)
        {
            int maxSqr = MaxSqr(maxDist, out _);
            if (_memoVersion == _version && _memoMaxSqr == maxSqr && _memoFrom == from)
            {
                pos = _memoPos;
                return _memoFound;
            }
            _memoFound = TryGetNearest(from, maxDist, out _, out _memoPos);
            _memoVersion = _version;
            _memoFrom = from;
            _memoMaxSqr = maxSqr;
            pos = _memoPos;
            return _memoFound;
        }

        /// <summary>The nearest food within maxDist of from: nearest by fixed-point squared distance, ties to the lower
        /// id (ordinal). Checks only the cells the search square touches.</summary>
        public bool TryGetNearest(FixedPoint2 from, float maxDist, out string foodId, out FixedPoint2 pos)
        {
            foodId = null;
            pos = default;
            if (_entries.Count == 0) return false;
            int maxSqr = MaxSqr(maxDist, out int reach);
            // One world cell of margin past the radius: fixed-point rounding can only shorten a distance by a hair.
            int span = reach + 1000;
            long x0 = FloorDiv(from.X.Value - span), x1 = FloorDiv(from.X.Value + span);
            long y0 = FloorDiv(from.Y.Value - span), y1 = FloorDiv(from.Y.Value + span);
            int bestSqr = int.MaxValue;
            for (long cx = x0; cx <= x1; cx++)
            {
                for (long cy = y0; cy <= y1; cy++)
                {
                    if (!_cells.TryGetValue(Key(cx, cy), out var ids)) continue;
                    for (int i = 0; i < ids.Count; i++)
                    {
                        string id = ids[i];
                        var e = _entries[id];
                        int sqr = e.pos.SqrDistanceTo(from).Value;
                        if (sqr > maxSqr) continue;
                        if (sqr < bestSqr || (sqr == bestSqr && string.CompareOrdinal(id, foodId) < 0))
                        {
                            bestSqr = sqr;
                            foodId = id;
                            pos = e.pos;
                        }
                    }
                }
            }
            return foodId != null;
        }

        /// <summary>The same question answered by checking every entry — the old way; the tests compare against it.</summary>
        public bool TryGetNearestByFullScan(FixedPoint2 from, float maxDist, out string foodId, out FixedPoint2 pos)
        {
            foodId = null;
            pos = default;
            int bestSqr = int.MaxValue;
            int maxSqr = MaxSqr(maxDist, out _);
            foreach (var kv in _entries)
            {
                int sqr = kv.Value.pos.SqrDistanceTo(from).Value;
                if (sqr > maxSqr) continue;
                if (sqr < bestSqr || (sqr == bestSqr && string.CompareOrdinal(kv.Key, foodId) < 0))
                {
                    bestSqr = sqr;
                    foodId = kv.Key;
                    pos = kv.Value.pos;
                }
            }
            return foodId != null;
        }

        /// <summary>The squared range exactly as the old lookups computed it (FromFloat, then a fixed-point multiply).</summary>
        private static int MaxSqr(float maxDist, out int reach)
        {
            var maxFixed = FixedPoint.FromFloat(maxDist);
            reach = maxFixed.Value < 0 ? -maxFixed.Value : maxFixed.Value;
            return (maxFixed * maxFixed).Value;
        }

        private static long FloorDiv(int v) => v >= 0 ? v / CellSize : -((-(long)v + CellSize - 1) / CellSize);

        private static long Key(long cx, long cy) => (cx << 32) ^ (cy & 0xffffffffL);

        private static long CellKey(FixedPoint2 p) => Key(FloorDiv(p.X.Value), FloorDiv(p.Y.Value));

        private void AddToCell(long key, string id)
        {
            if (!_cells.TryGetValue(key, out var ids))
            {
                ids = new List<string>(4);
                _cells[key] = ids;
            }
            ids.Add(id);
        }

        private void RemoveFromCell(long key, string id)
        {
            if (!_cells.TryGetValue(key, out var ids)) return;
            ids.Remove(id);
            if (ids.Count == 0) _cells.Remove(key);
        }
    }
}
