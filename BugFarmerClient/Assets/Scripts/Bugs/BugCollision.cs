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
        /// ignoreOccupants skips the occupant blocking branch. Ground never blocks
        /// bugs (water stops people only) — mirroring the server rule exactly.
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
        /// #20 predator line-of-sight: true if any cell STRICTLY BETWEEN a and b is blocked for bugs
        /// (an occupant/wall occludes the shot). Integer Bresenham over the cell grid — PURE INTEGER, so
        /// every client computes the same result and an authority handoff stays bit-identical (this runs
        /// only on the authority's strike selection; the kill rides BUG_REMOVED). Endpoints are skipped:
        /// the predator stands on a walkable cell, and a flier prey may legitimately hover over a blocked
        /// cell. Reuses the ZONE-WIDE blocks_bugs map (ignoreOccupants:false) so the bin blocks the shot.
        /// </summary>
        public static bool LineBlocked(FixedPoint2 a, FixedPoint2 b)
        {
            return LineBlocked(a, b, cell =>
                TilemapManager.Instance != null && TilemapManager.Instance.IsCellBlockedForBugs(cell, false));
        }

        /// <summary>
        /// Testable core: the same integer walk, but the per-cell test is injected — mirrors the server's
        /// RaycastClampWithBlock(...func) shape so a unit test can drive it against a stubbed blocked set
        /// without a live TilemapManager.
        /// </summary>
        public static bool LineBlocked(FixedPoint2 a, FixedPoint2 b, System.Func<Vector2Int, bool> isBlocked)
        {
            Vector2Int c0 = GetCellCoords(a);
            Vector2Int c1 = GetCellCoords(b);
            int x = c0.x, y = c0.y;
            int x1 = c1.x, y1 = c1.y;
            if (x == x1 && y == y1)
                return false; // same cell: nothing between them

            int dx = Mathf.Abs(x1 - x), dy = Mathf.Abs(y1 - y);
            int sx = x < x1 ? 1 : -1;
            int sy = y < y1 ? 1 : -1;
            int err = dx - dy;

            // Step BEFORE testing so the start cell is never tested; stop AT the end cell so it isn't
            // either → only the cells strictly between are checked.
            while (true)
            {
                int e2 = 2 * err;
                if (e2 > -dy) { err -= dy; x += sx; }
                if (e2 < dx) { err += dx; y += sy; }
                if (x == x1 && y == y1)
                    return false; // reached the victim's cell with no blocker in between
                if (isBlocked(new Vector2Int(x, y)))
                    return true;
            }
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
