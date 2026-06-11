using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// "Can drink today" indicator: a small bobbing water-drop drawn above a fruit tree
    /// whose tank isn't full and that hasn't been manually watered this apparent day
    /// (TilemapManager.RefreshDroplet owns the rule). Clones the BreakingVisual pattern — a child
    /// SpriteRenderer on the occupant GameObject, "Occupants" layer, high sortingOrder.
    /// The droplet sprite is GENERATED AT RUNTIME (a 9x12 teardrop) so there is no
    /// art-pipeline or PPU-meta dependency.
    /// </summary>
    public class WaterDroplet : MonoBehaviour
    {
        private static Sprite _dropletSprite; // shared, generated once

        private SpriteRenderer _renderer;
        private float _baseY;
        private float _bobPhase;

        private void Awake()
        {
            _renderer = gameObject.AddComponent<SpriteRenderer>();
            _renderer.sprite = GetDropletSprite();
            _renderer.sortingLayerName = "Occupants";
            _renderer.sortingOrder = 1000; // always on top of occupants
            _bobPhase = Random.Range(0f, Mathf.PI * 2f);
        }

        /// <summary>Position the droplet above an occupant whose sprite is `heightCells` tall.</summary>
        public void AttachAbove(Vector3 occupantTop)
        {
            transform.position = occupantTop;
            _baseY = occupantTop.y;
        }

        private void Update()
        {
            // Gentle bob so it reads as "alive"/needs attention
            var p = transform.position;
            p.y = _baseY + Mathf.Sin(Time.time * 2.5f + _bobPhase) * 0.08f;
            transform.position = p;
        }

        /// <summary>
        /// Build the shared teardrop sprite: a 9x12 blue drop with a lighter core and a
        /// white glint, PPU 16 (≈0.6 x 0.75 cells on screen).
        /// </summary>
        private static Sprite GetDropletSprite()
        {
            if (_dropletSprite != null) return _dropletSprite;

            const int W = 9, H = 12;
            var tex = new Texture2D(W, H, TextureFormat.RGBA32, false);
            tex.filterMode = FilterMode.Point;
            var clear = new Color(0, 0, 0, 0);
            var outline = new Color(0.10f, 0.25f, 0.55f);
            var body = new Color(0.25f, 0.55f, 0.95f);
            var core = new Color(0.45f, 0.75f, 1f);

            // Teardrop: widths per row, bottom (round) to top (point)
            int[] widths = { 3, 5, 7, 9, 9, 9, 7, 7, 5, 3, 3, 1 };
            for (int y = 0; y < H; y++)
            {
                int w = widths[y];
                int x0 = (W - w) / 2;
                for (int x = 0; x < W; x++)
                {
                    if (x < x0 || x >= x0 + w) { tex.SetPixel(x, y, clear); continue; }
                    bool edge = x == x0 || x == x0 + w - 1 || y == 0 || y == H - 1 || w <= 1;
                    tex.SetPixel(x, y, edge ? outline : body);
                }
            }
            // Lighter core + glint
            for (int y = 2; y <= 5; y++)
                for (int x = 3; x <= 5; x++)
                    tex.SetPixel(x, y, core);
            tex.SetPixel(3, 4, Color.white);
            tex.Apply();

            _dropletSprite = Sprite.Create(tex, new Rect(0, 0, W, H), new Vector2(0.5f, 0f), 16f);
            return _dropletSprite;
        }
    }
}
