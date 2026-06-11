using UnityEngine;
using BugFarmer.World;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// Deterministic collision resolution for individual bug movement.
    /// Uses fixed-point math and consistent axis resolution order (X then Y).
    /// </summary>
    public static class BugCollision
    {
        /// <summary>
        /// Resolve collision for proposed movement. Returns valid position.
        /// Deterministic: always resolves X-axis first, then Y-axis.
        /// This allows bugs to slide along walls instead of getting stuck.
        /// </summary>
        public static FixedPoint2 Resolve(FixedPoint2 current, FixedPoint2 proposed)
        {
            return Resolve(current, proposed, false);
        }

        /// <summary>
        /// Species-aware resolve (§14, the client half of flies_over_fences):
        /// ignoreOccupants skips ONLY the occupant blocking branch — water/impassable
        /// ground still blocks fliers, mirroring the server rule exactly.
        /// </summary>
        public static FixedPoint2 Resolve(FixedPoint2 current, FixedPoint2 proposed, bool ignoreOccupants)
        {
            // 1. Try full move - if not blocked, return proposed
            if (!IsBlocked(proposed, ignoreOccupants))
                return proposed;

            // 2. Try X-only move (slide horizontally along wall)
            var xOnly = new FixedPoint2(proposed.X, current.Y);
            if (!IsBlocked(xOnly, ignoreOccupants))
                return xOnly;

            // 3. Try Y-only move (slide vertically along wall)
            var yOnly = new FixedPoint2(current.X, proposed.Y);
            if (!IsBlocked(yOnly, ignoreOccupants))
                return yOnly;

            // 4. Fully blocked - stay in place
            return current;
        }

        /// <summary>
        /// Check if a fixed-point position is blocked.
        /// </summary>
        public static bool IsBlocked(FixedPoint2 pos, bool ignoreOccupants = false)
        {
            var cellPos = GetCellCoords(pos);
            return TilemapManager.Instance?.IsCellBlockedForBugs(cellPos, ignoreOccupants) ?? false;
        }

        /// <summary>
        /// Convert fixed-point position to cell coordinates.
        /// Uses floor division to handle negative coordinates correctly.
        /// </summary>
        public static Vector2Int GetCellCoords(FixedPoint2 pos)
        {
            int cellX = FloorDiv(pos.X.Value, FixedPoint.Scale);
            int cellY = FloorDiv(pos.Y.Value, FixedPoint.Scale);
            return new Vector2Int(cellX, cellY);
        }

        /// <summary>
        /// Floor division toward negative infinity.
        /// C# integer division truncates toward zero, which is wrong for negative coords.
        /// </summary>
        private static int FloorDiv(int a, int b)
        {
            if (a >= 0)
                return a / b;
            return (a - b + 1) / b;
        }
    }
}
