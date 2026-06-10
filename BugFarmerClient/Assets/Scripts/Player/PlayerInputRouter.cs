using UnityEngine;
using UnityEngine.EventSystems;
using BugFarmer.Data;
using BugFarmer.UI;

namespace BugFarmer.Player
{
    /// <summary>
    /// The single owner of the LEFT-CLICK. Exactly one controller handles any click, chosen
    /// by the equipped tool's type — replacing the old pattern of four controllers each
    /// polling Input and guessing (which is how "every click near a swarm hand-catches even
    /// with a pickaxe equipped" happened).
    ///
    /// Contract:
    ///  - UI always wins: clicks over UI reach nobody.
    ///  - The route is resolved ONCE on mouse-down and never re-dispatched mid-hold.
    ///  - If Breaking is the resolved owner, the hold is LATCHED to Breaking: its held path
    ///    runs every frame until release, then StopBreaking(). (Preserves hold-to-break;
    ///    prevents held-click machine-gunning of single-fire actions.)
    ///  - Right-click stays with PlacementController/StationController (interact/place is a
    ///    different verb family).
    /// </summary>
    public class PlayerInputRouter : MonoBehaviour
    {
        private CatchingController _catching;
        private ToolUseController _toolUse;
        private BreakingController _breaking;
        private MeleeController _melee; // lands with combat; router tolerates absence

        private bool _holdLatchedToBreaking;

        private void Start()
        {
            // Siblings on the player GameObject (prefab + scene-added components alike).
            _catching = GetComponent<CatchingController>();
            _toolUse = GetComponent<ToolUseController>();
            _breaking = GetComponent<BreakingController>();
            _melee = GetComponent<MeleeController>();
        }

        private void Update()
        {
            // An in-progress break owns the button until release.
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

            if (!Input.GetMouseButtonDown(0))
                return;

            // UI always wins.
            if (EventSystem.current != null && EventSystem.current.IsPointerOverGameObject())
                return;

            string toolId = InventoryManager.Instance?.GetEquippedToolId() ?? "";
            string toolType = EntityDatabase.Get(toolId)?.ToolType;

            switch (toolType)
            {
                case "sword":
                case "spear":
                    if (_melee != null)
                    {
                        _melee.TryHandleClick();
                        return;
                    }
                    LatchBreaking(); // until MeleeController exists
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

        private void LatchBreaking()
        {
            if (_breaking == null) return;
            _holdLatchedToBreaking = true;
            _breaking.HoldBreak();
        }
    }
}
