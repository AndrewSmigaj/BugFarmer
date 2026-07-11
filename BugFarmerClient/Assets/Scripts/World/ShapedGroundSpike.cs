using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// M0 shaped-ground render spike — DEBUG/temporary. Press <b>G</b> in Play to stamp a patch of
    /// runtime-composited tiles (four diagonal halves of <c>grass~dirt</c>, plus solid grass/dirt for
    /// reference) around the player, so the owner can eyeball whether the mask-composite reads cleanly.
    /// Client-only, local, no server / no persistence — this is the M0 taste checkpoint, replaced by the
    /// real builder at M4. Self-bootstraps so no scene edit is needed.
    /// </summary>
    public class ShapedGroundSpike : MonoBehaviour
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Boot()
        {
            var go = new GameObject("ShapedGroundSpike");
            Object.DontDestroyOnLoad(go);
            go.AddComponent<ShapedGroundSpike>();
        }

        private void Update()
        {
            // Builder input while a shovel is equipped (HotbarUI yields the wheel then). The WHEEL now
            // cycles the SHAPE ONLY — the old Shift/Ctrl-wheel material scheme was confusing (owner) and is
            // gone; material choice moves to a proper "Set Materials" panel (S2). Until that panel exists,
            // temporary dev keys keep composite placement testable: M = next material A, N = next material B.
            if (ShovelEquipped())
            {
                float scroll = Input.GetAxis("Mouse ScrollWheel");
                if (Mathf.Abs(scroll) > 0.01f)
                {
                    ShovelSelection.CycleShape(scroll > 0f ? 1 : -1);
                    LogSel();
                }
                if (Input.GetKeyDown(KeyCode.RightBracket)) { ShovelSelection.CycleShape(1); LogSel(); }
                if (Input.GetKeyDown(KeyCode.LeftBracket)) { ShovelSelection.CycleShape(-1); LogSel(); }
                if (Input.GetKeyDown(KeyCode.M)) { ShovelSelection.CycleMatA(1); LogSel(); } // temp: until Set-Materials panel
                if (Input.GetKeyDown(KeyCode.N)) { ShovelSelection.CycleMatB(1); LogSel(); } // temp: until Set-Materials panel
            }

            if (!Input.GetKeyDown(KeyCode.G))
                return;

            var tm = TilemapManager.Instance;
            var cam = Camera.main;
            if (tm == null || cam == null)
                return;

            // Camera tracks the player, so its XY is the player's location.
            Vector2Int origin = tm.WorldToCell(new Vector3(cam.transform.position.x, cam.transform.position.y, 0f));

            // One 2x2 block per shape in the full vocabulary, laid out in a grid with 1-tile dirt gaps so each
            // shape reads on its own (not the dense quilt). East of the player so the sprite doesn't cover it.
            var shapes = TileCompositor.Shapes;
            const int cols = 5, block = 2, pitch = block + 1;
            for (int s = 0; s < shapes.Length; s++)
            {
                int col = s % cols;
                int row = s / cols;
                int ox = origin.x + 2 + col * pitch;
                int oy = origin.y + 6 - row * pitch;   // north-up: first row highest
                string id = $"grass~dirt~{shapes[s]}";
                for (int dy = 0; dy < block; dy++)
                    for (int dx = 0; dx < block; dx++)
                        tm.StampGroundDebug(new Vector2Int(ox + dx, oy + dy), id);
            }

            Debug.Log($"[ShapedGroundSpike] Stamped {shapes.Length} grass~dirt shapes (one 2x2 block each) " +
                      $"near {origin}. Shaped-ground M1 shape set.");
        }

        private static void LogSel()
        {
            Debug.Log($"[Shovel] A:{ShovelSelection.MatA} B:{ShovelSelection.MatB} " +
                      $"shape:{ShovelSelection.Shape} -> '{ShovelSelection.CurrentGroundId}'");
        }

        // Functional builder readout (dev-grade HUD; the polished panel is the owner's M4 taste pass).
        private GUIStyle _hud;

        private void OnGUI()
        {
            if (!ShovelEquipped())
                return;
            if (_hud == null)
                _hud = new GUIStyle(GUI.skin.box)
                {
                    alignment = TextAnchor.UpperLeft,
                    fontSize = 13,
                    padding = new RectOffset(10, 10, 8, 8),
                };

            string txt =
                "SHOVEL BUILDER (functional v1)\n" +
                $"A: {ShovelSelection.MatA}    B: {ShovelSelection.MatB}    shape: {ShovelSelection.Shape}\n" +
                $"places: {ShovelSelection.CurrentGroundId}\n" +
                "wheel / [ ] = shape       (temp) M = material A    N = material B\n" +
                "LMB = place    Shift+LMB = dig";
            GUI.Box(new Rect(12, 12, 560, 112), txt, _hud);
        }

        private static bool ShovelEquipped()
        {
            var id = BugFarmer.UI.InventoryManager.Instance?.GetEquippedToolId();
            if (string.IsNullOrEmpty(id))
                return false;
            return BugFarmer.Data.EntityDatabase.Get(id)?.ToolType == "shovel";
        }
    }
}
