using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// One-shot particle bursts for hit feedback — a little poof of leaves (chopping a tree) or wood
    /// chips (hitting a structure) at the strike point. A single shared World-space ParticleSystem that
    /// we Emit into (moved to the hit position first; a Circle shape gives an outward in-plane spray),
    /// so there's no GameObject churn per hit. Cosmetic, client-local, zero sim/determinism surface.
    /// </summary>
    public class HitBurst : MonoBehaviour
    {
        public enum Kind { Leaf, Chip, Generic }

        private static HitBurst _inst;
        private ParticleSystem _ps;
        private static Texture2D _leafTex;

        // A small, SOLID football/leaf shape = a filled narrow ellipse (~2:1) that fills most of the quad, so
        // it reads clearly at particle size. Soft-edged. Tinted per kind at emit; rotated per particle.
        private static Texture2D LeafTex()
        {
            if (_leafTex != null) return _leafTex;
            const int N = 32;
            var tex = new Texture2D(N, N, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp };
            var px = new Color32[N * N];
            float half = (N - 1) * 0.5f;
            float a = 0.82f * half, b = 0.42f * half;  // long axis (x) : short axis (y) ≈ football
            for (int y = 0; y < N; y++)
                for (int x = 0; x < N; x++)
                {
                    float nx = (x - half) / a, ny = (y - half) / b;
                    float e = nx * nx + ny * ny;                 // <=1 inside the ellipse
                    float alpha = Mathf.Clamp01((1f - e) / 0.18f); // solid interior, ~soft edge
                    px[y * N + x] = new Color32(255, 255, 255, (byte)(alpha * 255f));
                }
            tex.SetPixels32(px);
            tex.Apply();
            _leafTex = tex;
            return _leafTex;
        }

        private static HitBurst Instance()
        {
            if (_inst != null) return _inst;
            var go = new GameObject("HitBurst");
            _inst = go.AddComponent<HitBurst>();
            _inst.Build();
            return _inst;
        }

        private void Build()
        {
            _ps = gameObject.AddComponent<ParticleSystem>();

            var main = _ps.main;
            main.loop = false;
            main.playOnAwake = false;
            main.startLifetime = new ParticleSystem.MinMaxCurve(0.4f, 0.8f);
            main.startSpeed = new ParticleSystem.MinMaxCurve(1.4f, 3.4f);
            main.startSize = new ParticleSystem.MinMaxCurve(0.12f, 0.24f); // bigger = clearly visible
            main.startRotation = new ParticleSystem.MinMaxCurve(0f, 6.28f);
            main.gravityModifier = 1.3f;             // chips/leaves fall after the pop
            main.maxParticles = 400;
            main.simulationSpace = ParticleSystemSimulationSpace.World;

            var emission = _ps.emission;
            emission.enabled = false;                // manual Emit only

            var shape = _ps.shape;                   // outward in-plane spray
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = 0.1f;
            shape.arc = 360f;

            var col = _ps.colorOverLifetime;         // hold then fade
            col.enabled = true;
            var grad = new Gradient();
            grad.SetKeys(
                new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                new[]
                {
                    new GradientAlphaKey(1f, 0f),
                    new GradientAlphaKey(1f, 0.6f),
                    new GradientAlphaKey(0f, 1f),
                });
            col.color = new ParticleSystem.MinMaxGradient(grad);

            var rot = _ps.rotationOverLifetime;      // gentle flutter (owner: "rotate a little", not spin)
            rot.enabled = true;
            rot.z = new ParticleSystem.MinMaxCurve(-1.2f, 1.2f);

            var r = _ps.GetComponent<ParticleSystemRenderer>();
            r.renderMode = ParticleSystemRenderMode.Billboard;
            r.material = new Material(Shader.Find("Sprites/Default")) { mainTexture = LeafTex() }; // unlit leaf shape
            r.sortingLayerName = "Occupants";
            r.sortingOrder = 800;                    // in front of occupant sprites
        }

        /// <summary>
        /// Emit a burst at a world position. <paramref name="sizeScale"/> (0..1, from the struck object's
        /// size) contains it on small plants: fewer particles, shorter range — so a little plant gets a few
        /// flecks, a tree gets the full pop.
        /// </summary>
        public static void Play(Vector3 worldPos, Kind kind, float sizeScale = 1f)
        {
            var inst = Instance();
            inst.transform.position = worldPos;      // World sim space: particles live independently after emit
            sizeScale = Mathf.Clamp(sizeScale, 0.25f, 1f);

            var main = inst._ps.main;
            main.startColor = kind switch
            {
                Kind.Leaf => new Color(0.36f, 0.60f, 0.22f), // leaf green
                Kind.Chip => new Color(0.55f, 0.40f, 0.24f), // wood brown
                _ => new Color(0.72f, 0.72f, 0.72f),         // neutral
            };
            // Contain the RANGE on small objects (shorter fly-out) but keep them clearly visible — softened
            // from a too-tight version that made small-plant bursts hard to see.
            float spd = 0.45f + 0.55f * sizeScale;   // plant ≈0.63x range, tree 1x
            main.startSpeed = new ParticleSystem.MinMaxCurve(1.4f * spd, 3.4f * spd);
            float sz = 0.7f + 0.3f * sizeScale;      // barely shrink small ones
            main.startSize = new ParticleSystem.MinMaxCurve(0.12f * sz, 0.24f * sz);
            int count = Mathf.Max(4, Mathf.RoundToInt(8f * sizeScale));
            Debug.Log($"[HitBurst] {kind} x{count} scale {sizeScale:0.00} @ {worldPos}");
            inst._ps.Emit(count);
        }
    }
}
