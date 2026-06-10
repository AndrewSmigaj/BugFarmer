using UnityEngine;
using UnityEngine.EventSystems;
using BugFarmer.Data;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// The single owner of BOTH mouse buttons' world clicks. Exactly one controller handles
    /// any click — replacing the old pattern of controllers each polling Input and guessing
    /// (which is how "every click near a swarm hand-catches even with a pickaxe equipped"
    /// and the Placement+Station right-click double-fire happened).
    ///
    /// LEFT-CLICK (resolved ONCE on mouse-down by equipped tool_type; never re-dispatched
    /// mid-hold):
    ///  - UI always wins: clicks over UI reach nobody.
    ///  - If Breaking is the resolved owner, the hold is LATCHED to Breaking: its held path
    ///    runs every frame until release, then StopBreaking(). (Preserves hold-to-break;
    ///    prevents held-click machine-gunning of single-fire actions.)
    /// RIGHT-CLICK (priority chain — the verb depends on world context, not just the tool):
    ///  UI guard → Station (a station under the cursor wins; CLOSING an open menu also
    ///  CONSUMES the click) → Placement (mode-based: consumes whenever placing mode is
    ///  active, even on a red ghost) → weapon "secondary" move (sword jab, axe combat
    ///  swing, spear sweep).
    /// </summary>
    public class PlayerInputRouter : MonoBehaviour
    {
        private CatchingController _catching;
        private ToolUseController _toolUse;
        private BreakingController _breaking;
        private MeleeController _melee;
        private PlacementController _placement;
        private StationController _station;
        private Camera _mainCamera;

        private bool _holdLatchedToBreaking;

        private void Start()
        {
            // Siblings on the player GameObject (prefab + scene-added components alike).
            _catching = GetComponent<CatchingController>();
            _toolUse = GetComponent<ToolUseController>();
            _breaking = GetComponent<BreakingController>();
            _melee = GetComponent<MeleeController>();
            _placement = GetComponent<PlacementController>();
            _station = GetComponent<StationController>();
            _mainCamera = Camera.main;
        }

        private void Update()
        {
            // An in-progress break owns the left button until release.
            if (_holdLatchedToBreaking)
            {
                if (Input.GetMouseButton(0))
                {
                    _breaking?.HoldBreak();
                }
                else
                {
                    _breaking?.StopBreaking();
                    _holdLatchedToBreaking = false;
                }
                return;
            }

            if (Input.GetMouseButtonDown(0))
                RouteLeftClick();
            else if (Input.GetMouseButtonDown(1))
                RouteRightClick();
        }

        private void RouteLeftClick()
        {
            // UI always wins.
            if (EventSystem.current != null && EventSystem.current.IsPointerOverGameObject())
                return;

            string toolId = InventoryManager.Instance?.GetEquippedToolId() ?? "";
            string toolType = EntityDatabase.Get(toolId)?.ToolType;

            switch (toolType)
            {
                case "sword":
                case "spear":
                    _melee?.TryHandleClick("primary");
                    return;

                case "net":
                    _catching?.TryHandleClick(netMode: true);
                    return;

                case "hoe":
                case "watering_can":
                case "scythe":
                    _toolUse?.TryHandleClick();
                    return;

                default:
                    // Bare hand (or a non-tool item): try to grab a bug first; if no bug was
                    // under the cursor, the click falls through to breaking. This ordered
                    // fallthrough replaces BreakingController's old bug-priority probe.
                    if (toolType == null && _catching != null && _catching.TryHandleClick(netMode: false))
                        return;
                    LatchBreaking();
                    return;
            }
        }

        private void RouteRightClick()
        {
            // UI always wins.
            if (EventSystem.current != null && EventSystem.current.IsPointerOverGameObject())
                return;

            if (_mainCamera == null)
            {
                _mainCamera = Camera.main;
                if (_mainCamera == null) return;
            }
            Vector3 mouseWorld = _mainCamera.ScreenToWorldPoint(Input.mousePosition);
            mouseWorld.z = 0;

            // 1. Stations: interact beats attack/place; closing an open menu consumes too.
            if (_station != null && _station.TryHandleRightClick(mouseWorld))
                return;

            // 2. Placement (equipped placeable, or the cursor-place mode): mode-based
            //    consume — a misclicked red-ghost placement must never fall through to a jab.
            if (_placement != null && _placement.TryHandleRightClick())
                return;

            // 3. Weapon secondary move (sword jab, axe combat swing, spear sweep).
            string toolId = InventoryManager.Instance?.GetEquippedToolId() ?? "";
            if (EntityDatabase.Get(toolId)?.GetMove("secondary") != null)
                _melee?.TryHandleClick("secondary");
        }

        private void LatchBreaking()
        {
            if (_breaking == null) return;
            _holdLatchedToBreaking = true;
            _breaking.HoldBreak();
        }
    }
}
