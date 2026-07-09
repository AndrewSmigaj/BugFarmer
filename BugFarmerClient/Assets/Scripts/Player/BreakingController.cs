using UnityEngine;
using BugFarmer.Data;
using BugFarmer.Networking;
using BugFarmer.World;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// Handles player breaking/mining of world objects (hold left-click on a breakable
    /// occupant). Input arrives via PlayerInputRouter, which latches the held click to this
    /// controller — routing by equipped tool type lives in the router, not here.
    /// Server validates tool requirements and tracks breaking progress.
    /// </summary>
    public class BreakingController : MonoBehaviour
    {
        [Header("Settings")]
        [Tooltip("Time between break messages sent to server")]
        [SerializeField] private float breakClickInterval = 0.25f;

        [Tooltip("Maximum distance from player to break an object (Terraria-style reach)")]
        [SerializeField] private float maxBreakDistance = 8f;

        private Vector2Int? _breakingCell;
        private float _lastBreakTime;
        private bool _isBreaking;
        private Camera _mainCamera;
        private PlayerToolAnimator _animator;

        private void Start()
        {
            _mainCamera = Camera.main;
            _animator = GetComponent<PlayerToolAnimator>();
        }

        /// <summary>
        /// Run one held frame of breaking (called by PlayerInputRouter while the latched
        /// left-click is held). The router guarantees tool routing and the UI guard.
        /// </summary>
        private float _lastSwingTime;

        public void HoldBreak()
        {
            if (_mainCamera == null)
                return;

            // Get world position under mouse
            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            mouseWorld.z = 0;

            // SWING ON EVERY ATTEMPT, target or not (Terraria: holding swings at air) —
            // without this, clicking with an axe at nothing shows NOTHING and the tool
            // reads as broken. Throttled at the break cadence; phase-offset vs the break
            // timer (which resets per target for instant first hits) is a sub-interval
            // cosmetic, accepted.
            if (Time.time - _lastSwingTime >= breakClickInterval)
            {
                var swingDef = EntityDatabase.Get(InventoryManager.Instance?.GetEquippedToolId() ?? "");
                if (_animator != null && swingDef?.ToolType != null)
                {
                    Vector2 aim = (Vector2)(mouseWorld - transform.position);
                    _animator.Play(swingDef.ToolType, EntityDatabase.GetItemSprite(swingDef.Id), aim);
                    _lastSwingTime = Time.time;
                }
            }

            // Front-most breakable occupant under the cursor (shared resolver; a bare OverlapPoint
            // returns an arbitrary overlapping collider — a tree overlapping the target could steal it).
            var clickTarget = InteractionResolver.TopmostInteractable(mouseWorld);
            if (clickTarget == null || !clickTarget.IsBreakable)
            {
                if (Input.GetMouseButtonDown(0))
                {
                    Debug.Log($"[BreakingController] No breakable occupant at {mouseWorld}");
                }
                StopBreaking();
                return;
            }

            // Use anchor cell from click target (bottom-left of footprint)
            Vector2Int anchorCell = clickTarget.AnchorCell;

            // Check distance from player to anchor cell
            if (TilemapManager.Instance != null)
            {
                Vector3 cellWorld = TilemapManager.Instance.CellToWorld(anchorCell);
                if (Vector3.Distance(transform.position, cellWorld) > maxBreakDistance)
                {
                    StopBreaking();
                    return;
                }
            }

            // Check if we have a tool equipped (not a placeable item)
            // Server will validate tool requirements - wrong tool = no action
            string equippedItem = InventoryManager.Instance?.GetEquippedToolId() ?? "";

            // Skip if holding a placeable item (placement uses different input)
            if (!string.IsNullOrEmpty(equippedItem) && EntityDatabase.IsPlaceable(equippedItem))
            {
                StopBreaking();
                return;
            }

            // Check if target changed
            if (_breakingCell != anchorCell)
            {
                _breakingCell = anchorCell;
                _lastBreakTime = 0; // Reset timer for new target
            }

            _isBreaking = true;

            // Send break message at interval (the swing already played above)
            if (Time.time - _lastBreakTime >= breakClickInterval)
            {
                SendBreakRequest(anchorCell);
                _lastBreakTime = Time.time;
                PlayHitFeedback(clickTarget);   // flash + shake + leaf/chip burst on each connecting hit
            }
        }

        /// <summary>Client-only juice on a connecting hit: flash the target, a tiny camera kick, and a
        /// leaf (tree) / wood-chip (structure) burst at the strike point. No sim/determinism surface.</summary>
        private void PlayHitFeedback(OccupantClickTarget target)
        {
            if (target == null) return;

            var sr = target.GetComponent<SpriteRenderer>();
            if (sr != null) World.HitFlash.Play(sr, 0.4f);   // gentle flash (was 0.9 — too extreme)

            CameraFollow.AddShake(0.22f);                     // small kick (was 0.5 — too extreme)

            string cat = EntityDatabase.Get(target.OccupantId)?.Category;
            var kind = cat == "natural" ? World.HitBurst.Kind.Leaf
                     : cat == "structure" ? World.HitBurst.Kind.Chip
                     : World.HitBurst.Kind.Generic;
            Vector3 at = sr != null ? sr.bounds.center : target.transform.position;
            World.HitBurst.Play(at, kind);
        }

        /// <summary>Clear breaking state (called by the router on click release/cancel).</summary>
        public void StopBreaking()
        {
            _isBreaking = false;
            _breakingCell = null;
        }

        private void SendBreakRequest(Vector2Int cellPos)
        {
            var socket = NetworkManager.Instance?.Socket;
            var match = WorldManager.Instance?.CurrentMatch;
            if (socket == null || !socket.IsConnected || match == null)
            {
                Debug.LogWarning("[BreakingController] Socket not connected");
                return;
            }

            var msg = new TileBreakMessage
            {
                grid_x = cellPos.x,
                grid_y = cellPos.y
            };
            var json = JsonUtility.ToJson(msg);
            _ = socket.SendMatchStateAsync(match.Id, OpCodes.TileBreak, json);
        }

        /// <summary>
        /// Check if currently breaking something.
        /// </summary>
        public bool IsBreaking => _isBreaking;

        /// <summary>
        /// Get the cell currently being broken, or null if not breaking.
        /// </summary>
        public Vector2Int? BreakingCell => _breakingCell;
    }
}
