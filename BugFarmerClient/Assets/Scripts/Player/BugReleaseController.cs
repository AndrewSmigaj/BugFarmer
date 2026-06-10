using UnityEngine;
using UnityEngine.EventSystems;
using BugFarmer.Networking;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// Release caught bugs into the world: while the DRAG CURSOR holds a BUG stack and the
    /// mouse is over the world, LEFT-click releases the WHOLE stack at the click and
    /// RIGHT-click releases ONE (mirroring the slot deposit verbs). The server grows a
    /// nearby same-species swarm or spawns a new one there.
    ///
    /// Affordance: a faint circle follows the mouse over the world while the bug cursor is
    /// active, green/red by the same ≤4 reach the server validates — so "the world is
    /// clickable" is visible and an out-of-reach click is legible, not a silent no-op.
    ///
    /// No optimistic anything: the swarm appears via SwarmUpdate / SWARM_REPRODUCED within
    /// a tick, and the cursor count updates through the existing BugSlotUpdate echo
    /// interception (count==0 clears the cursor).
    /// </summary>
    public class BugReleaseController : MonoBehaviour
    {
        [SerializeField] private float releaseReach = 4f; // server validates 4.5 (+slack)
        [SerializeField] private float indicatorRadius = 0.6f;
        [SerializeField] private Color inReachColor = new Color(0.4f, 1f, 0.4f, 0.35f);
        [SerializeField] private Color outOfReachColor = new Color(1f, 0.3f, 0.3f, 0.35f);

        private Camera _mainCamera;
        private LineRenderer _indicator;

        private void Start()
        {
            _mainCamera = Camera.main;

            // Release-point indicator (the CatchIndicator LineRenderer pattern)
            var obj = new GameObject("BugReleaseIndicator");
            obj.transform.SetParent(null);
            _indicator = obj.AddComponent<LineRenderer>();
            _indicator.useWorldSpace = true;
            _indicator.loop = true;
            _indicator.startWidth = 0.05f;
            _indicator.endWidth = 0.05f;
            _indicator.sortingLayerName = "Occupants";
            _indicator.sortingOrder = 500;
            _indicator.material = new Material(Shader.Find("Sprites/Default"));
            _indicator.positionCount = 24;
            _indicator.enabled = false;
        }

        private void OnDestroy()
        {
            if (_indicator != null)
                Destroy(_indicator.gameObject);
        }

        private bool BugCursorActive =>
            DragDropController.Instance != null &&
            DragDropController.Instance.HasCursorItem &&
            DragDropController.Instance.CursorSourceType == SlotType.Bug;

        private void Update()
        {
            if (_indicator == null) return;

            bool overUI = EventSystem.current != null && EventSystem.current.IsPointerOverGameObject();
            if (!BugCursorActive || overUI || _mainCamera == null)
            {
                _indicator.enabled = false;
                return;
            }

            Vector2 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            bool inReach = (mouseWorld - (Vector2)transform.position).sqrMagnitude
                           <= releaseReach * releaseReach;
            var color = inReach ? inReachColor : outOfReachColor;
            _indicator.startColor = color;
            _indicator.endColor = color;
            for (int i = 0; i < _indicator.positionCount; i++)
            {
                float a = (float)i / _indicator.positionCount * Mathf.PI * 2f;
                _indicator.SetPosition(i, new Vector3(
                    mouseWorld.x + Mathf.Cos(a) * indicatorRadius,
                    mouseWorld.y + Mathf.Sin(a) * indicatorRadius, 0f));
            }
            _indicator.enabled = true;
        }

        /// <summary>
        /// Handle a routed world click while the bug cursor is active. ALWAYS consumes when
        /// active (mode-based, the red-ghost rule) — an out-of-reach click eats the click
        /// (the red circle is the feedback) rather than falling through to a tool.
        /// </summary>
        public bool TryHandleClick(bool releaseAll)
        {
            if (!BugCursorActive) return false;

            var world = WorldManager.Instance;
            var socket = NetworkManager.Instance?.Socket;
            if (world?.CurrentMatch == null || socket == null || !socket.IsConnected)
                return true; // still the cursor's verb — consume

            if (_mainCamera == null)
            {
                _mainCamera = Camera.main;
                if (_mainCamera == null) return true;
            }

            Vector2 clickPos = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            if ((clickPos - (Vector2)transform.position).sqrMagnitude > releaseReach * releaseReach)
                return true; // out of reach: consumed; the red circle already said why

            var drag = DragDropController.Instance;
            var msg = new ReleaseBugsMessage
            {
                slot_index = drag.CursorSourceIndex,
                // Whole-stack = the CURSOR count, never -1: after a half-pickup the slot's
                // remainder belongs to the slot, not the release.
                count = releaseAll ? drag.CursorCount : 1,
                x = clickPos.x,
                y = clickPos.y
            };
            _ = socket.SendMatchStateAsync(world.CurrentMatch.Id, OpCodes.ReleaseBugs,
                                           JsonUtility.ToJson(msg));
            return true;
        }
    }
}
