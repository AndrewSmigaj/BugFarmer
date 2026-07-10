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
            if (!Input.GetKeyDown(KeyCode.G))
                return;

            var tm = TilemapManager.Instance;
            var cam = Camera.main;
            if (tm == null || cam == null)
                return;

            // Camera tracks the player, so its XY is the player's location.
            Vector2Int origin = tm.WorldToCell(new Vector3(cam.transform.position.x, cam.transform.position.y, 0f));

            // A 2x2 grid of 3x3 blocks, one block per diagonal shape, offset a couple cells east of the player
            // so the player sprite doesn't cover it. Plus a reference column of solid grass / dirt.
            string[] shapes = { "diagNE", "diagNW", "diagSE", "diagSW" };
            for (int b = 0; b < 4; b++)
            {
                int bx = (b % 2) * 3;
                int by = (b / 2) * 3;
                string id = $"grass~dirt~{shapes[b]}";
                for (int dy = 0; dy < 3; dy++)
                    for (int dx = 0; dx < 3; dx++)
                        tm.StampGroundDebug(new Vector2Int(origin.x + 2 + bx + dx, origin.y - 3 + by + dy), id);
            }
            // Reference column: pure grass then pure dirt, just east of the composited blocks.
            for (int dy = 0; dy < 3; dy++)
            {
                tm.StampGroundDebug(new Vector2Int(origin.x + 9, origin.y - 3 + dy), "grass");
                tm.StampGroundDebug(new Vector2Int(origin.x + 9, origin.y + dy), "dirt");
            }

            Debug.Log("[ShapedGroundSpike] Stamped grass~dirt~diag{NE,NW,SE,SW} blocks + solid grass/dirt refs " +
                      $"near {origin}. Composite render spike (M0).");
        }
    }
}
