using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Attached to occupant GameObjects to store metadata for click detection.
    /// When Physics2D raycast hits an occupant, this component provides
    /// the anchor cell position and occupant ID for breaking/interaction.
    /// </summary>
    public class OccupantClickTarget : MonoBehaviour
    {
        /// <summary>
        /// The anchor cell position (bottom-left of footprint) in global grid coordinates.
        /// </summary>
        public Vector2Int AnchorCell { get; private set; }

        /// <summary>
        /// The occupant ID from occupants.json (e.g., "tree_oak", "rock_small").
        /// </summary>
        public string OccupantId { get; private set; }

        /// <summary>
        /// Whether this occupant is breakable.
        /// </summary>
        public bool IsBreakable { get; private set; }

        /// <summary>
        /// Initialize the click target with occupant data.
        /// Called by TilemapManager when rendering the occupant.
        /// </summary>
        public void Initialize(Vector2Int anchorCell, string occupantId, bool isBreakable)
        {
            AnchorCell = anchorCell;
            OccupantId = occupantId;
            IsBreakable = isBreakable;
        }

        /// <summary>
        /// Reset for object pooling.
        /// </summary>
        public void Reset()
        {
            AnchorCell = Vector2Int.zero;
            OccupantId = null;
            IsBreakable = false;
        }
    }
}
