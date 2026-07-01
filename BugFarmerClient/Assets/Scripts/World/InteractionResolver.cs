using UnityEngine;
using BugFarmer.Data;

namespace BugFarmer.World
{
    /// <summary>
    /// Resolves which occupant a world click targets.
    ///
    /// Every occupant's <see cref="BoxCollider2D"/> is sized to its FULL sprite bounds
    /// (TilemapManager), so tall/large sprites (trees, 2x4 beds, NPCs at storefronts) overlap
    /// neighbouring cells. A single <c>Physics2D.OverlapPoint</c> returns ONE ARBITRARY collider
    /// among all that overlap the point, so an occupant that merely overlaps can steal the click
    /// from the one the player actually sees on top — the click-steal defect behind #18 and the
    /// "clicked and nothing happened" flakiness.
    ///
    /// This picks the FRONT-MOST INTERACTABLE occupant deterministically instead:
    ///  - Front-most = lowest <see cref="OccupantClickTarget.AnchorCell"/>.y. Occupants render with
    ///    <c>sortingOrder = -cellY</c> and the click target is initialised with that same cell
    ///    (TilemapManager: <c>sr.sortingOrder = -cellPos.y</c>; <c>clickTarget.Initialize(cellPos,…)</c>),
    ///    so the smallest anchor-y is the occupant drawn on top.
    ///  - "Interactable" = breakable OR has an <c>interaction_type</c>, so a purely decorative
    ///    occupant on top doesn't produce a dead click (it's skipped and the interactable behind it wins).
    ///
    /// Each right/left-click handler resolves ONE occupant via this and applies its own type check,
    /// which composes with PlayerInputRouter's ordered stop-on-first chain WITHOUT reach-through
    /// (a handler can't grab a same-type occupant hidden behind a different front occupant).
    /// Client-only interaction target selection — no determinism/sim surface.
    /// </summary>
    public static class InteractionResolver
    {
        /// <summary>
        /// The front-most interactable occupant under <paramref name="worldPoint"/>, or null when
        /// nothing interactable is there. Only occupant GameObjects carry a Collider2D, so every hit
        /// maps to an <see cref="OccupantClickTarget"/>.
        /// </summary>
        public static OccupantClickTarget TopmostInteractable(Vector2 worldPoint)
        {
            var cols = Physics2D.OverlapPointAll(worldPoint);
            if (cols == null || cols.Length == 0) return null;

            OccupantClickTarget best = null;
            foreach (var c in cols)
            {
                if (c == null) continue;
                var t = c.GetComponent<OccupantClickTarget>();
                if (t == null || !IsInteractable(t)) continue;
                if (best == null || IsInFrontOf(t, best))
                    best = t;
            }
            return best;
        }

        /// <summary>
        /// True iff <paramref name="t"/> is drawn in front of <paramref name="other"/>: a lower anchor
        /// cell (smaller y = higher sortingOrder). Exact ties resolve by instance id so the pick is
        /// deterministic and never flickers between frames.
        /// </summary>
        private static bool IsInFrontOf(OccupantClickTarget t, OccupantClickTarget other)
        {
            if (t.AnchorCell.y != other.AnchorCell.y)
                return t.AnchorCell.y < other.AnchorCell.y;
            return t.GetInstanceID() < other.GetInstanceID();
        }

        /// <summary>Breakable, or carries an interaction_type (shop/station/craft/storage/sleep/sign/mannequin/fruit_tree/…).</summary>
        private static bool IsInteractable(OccupantClickTarget t)
        {
            if (t.IsBreakable) return true;
            var def = EntityDatabase.Get(t.OccupantId);
            return def?.World != null && !string.IsNullOrEmpty(def.World.InteractionType);
        }
    }
}
