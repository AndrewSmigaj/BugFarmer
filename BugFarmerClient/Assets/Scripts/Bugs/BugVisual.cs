using UnityEngine;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// Pairs a BugAgent with its visual Transform for rendering.
    /// Handles position capture and interpolation for smooth 60fps display
    /// while simulation runs at 10Hz.
    /// </summary>
    public class BugVisual
    {
        /// <summary>
        /// The deterministic bug simulation agent.
        /// </summary>
        public BugAgent Agent;

        /// <summary>
        /// Transform of the visual GameObject (sprite).
        /// </summary>
        public Transform Transform;

        /// <summary>
        /// Cached SpriteRenderer for Y-sorting.
        /// </summary>
        public SpriteRenderer Renderer;

        /// <summary>
        /// Position at the start of current tick (for interpolation).
        /// </summary>
        public Vector2 PrevPos;

        /// <summary>
        /// Position at the end of current tick (for interpolation).
        /// </summary>
        public Vector2 CurrPos;

        public BugVisual(BugAgent agent, Transform transform)
        {
            Agent = agent;
            Transform = transform;
            Renderer = transform?.GetComponent<SpriteRenderer>();
            CurrPos = agent.Position.ToVector2();
            PrevPos = CurrPos;
        }

        /// <summary>
        /// Capture current position as previous before simulating next tick.
        /// Call this before SimulateTick(). CurrPos will be updated in Interpolate()
        /// after simulation has run.
        /// </summary>
        public void CapturePosition()
        {
            PrevPos = CurrPos;
            // Don't update CurrPos here - it will be updated in Interpolate()
            // after SimulateTick() has changed Agent.Position
        }

        /// <summary>
        /// Interpolate visual position between PrevPos and CurrPos.
        /// Updates CurrPos from Agent.Position (which was changed by SimulateTick).
        /// Also updates sorting order for Y-sorting (bugs in front of lower objects).
        /// </summary>
        /// <param name="t">Interpolation factor 0-1 (time within current tick)</param>
        public void Interpolate(float t)
        {
            // Update CurrPos from agent's current position (after SimulateTick)
            CurrPos = Agent.Position.ToVector2();

            if (Transform != null)
            {
                Vector2 pos = Vector2.Lerp(PrevPos, CurrPos, t);
                Transform.position = pos;

                // Y-sorting: lower Y = higher sorting order (appears in front)
                // Add small offset to appear slightly above ground-level occupants
                if (Renderer != null)
                {
                    Renderer.sortingOrder = -Mathf.FloorToInt(pos.y) + 1;
                }
            }
        }

        /// <summary>
        /// Sync visual position directly to agent position (no interpolation).
        /// Use when spawning or after catching up multiple ticks.
        /// </summary>
        public void SyncPosition()
        {
            CurrPos = Agent.Position.ToVector2();
            PrevPos = CurrPos;
            if (Transform != null)
            {
                Transform.position = CurrPos;

                // Update sorting order to match position
                if (Renderer != null)
                {
                    Renderer.sortingOrder = -Mathf.FloorToInt(CurrPos.y) + 1;
                }
            }
        }
    }
}
