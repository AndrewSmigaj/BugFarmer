using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Ambient dust motes — a subtle, always-on atmosphere layer (owner: the world reads flat vs. good
    /// indie games). A single World-space <see cref="ParticleSystem"/> of ~15-20 tiny slow motes that
    /// follows the camera, built the same way as <see cref="RainController"/> (World sim space,
    /// camera-follow reposition, rebuild on zoom). Sorted on "Occupants" so the darkness overlay (on the
    /// "Player" layer) multiplies over it → motes dim underground for free; brightness also scales with
    /// <see cref="DayNightController.Daylight"/> so the unlit motes fade at night instead of glowing.
    ///
    /// Created by DayNightController at runtime as a sibling of RainController (no scene setup).
    /// Cosmetic, client-local, zero sim/determinism surface — like the lighting overlay.
    /// </summary>
    public class DustController : MonoBehaviour
    {
        // Warm motes; alpha is the day/night-scaled ceiling (see Update).
        private static readonly Color BaseColor = new Color(1f, 0.97f, 0.88f, 0.3f);

        private ParticleSystem _ps;
        private Camera _cam;
        private float _builtOrtho = -1f;

        private void Start()
        {
            _cam = Camera.main;
            Build();
        }

        private void Build()
        {
            if (_ps != null) Destroy(_ps.gameObject);
            if (_cam == null) _cam = Camera.main;
            float ortho = _cam != null ? _cam.orthographicSize : 5f;
            float aspect = _cam != null ? _cam.aspect : 16f / 9f;
            float viewW = 2f * ortho * aspect;
            float viewH = 2f * ortho;

            var go = new GameObject("DustMotes");
            go.transform.SetParent(transform, false);
            _ps = go.AddComponent<ParticleSystem>();

            var main = _ps.main;
            main.loop = true;
            main.startLifetime = new ParticleSystem.MinMaxCurve(6f, 12f); // long-lived, slow
            main.startSpeed = new ParticleSystem.MinMaxCurve(0.05f, 0.25f);
            main.startSize = new ParticleSystem.MinMaxCurve(0.04f, 0.09f); // fine motes (owner: prev too big)
            main.startColor = BaseColor;
            main.gravityModifier = 0f;              // near-zero gravity — floaty
            main.maxParticles = 80;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.playOnAwake = false;

            var emission = _ps.emission;
            emission.rateOverTime = 4f;             // ~4/s × ~9s life ≈ 36 in the box, ~20 in view

            var shape = _ps.shape;                  // fill a box a little larger than the view
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(viewW + 4f, viewH + 4f, 1f);

            // Gentle non-linear drift (curl-ish) so motes wander instead of sliding in a line.
            var noise = _ps.noise;
            noise.enabled = true;
            noise.strength = 0.12f;
            noise.frequency = 0.2f;
            noise.scrollSpeed = 0.1f;
            noise.damping = true;

            // Twinkle: fade in then out over life so motes shimmer instead of hard-popping.
            var col = _ps.colorOverLifetime;
            col.enabled = true;
            var grad = new Gradient();
            grad.SetKeys(
                new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                new[]
                {
                    new GradientAlphaKey(0f, 0f),
                    new GradientAlphaKey(1f, 0.5f),
                    new GradientAlphaKey(0f, 1f),
                });
            col.color = new ParticleSystem.MinMaxGradient(grad);

            var r = _ps.GetComponent<ParticleSystemRenderer>();
            r.renderMode = ParticleSystemRenderMode.Billboard;
            r.material = new Material(Shader.Find("Sprites/Default")); // unlit; day/night via alpha scale below
            r.sortingLayerName = "Occupants";
            r.sortingOrder = 850;                   // above occupant sprites, below rain (900) + the darkness overlay
            _ps.Play();
            _builtOrtho = ortho;
            Debug.Log($"[DustController] built (ortho {ortho:0.0}, motes rate {emission.rateOverTime.constant})");
        }

        /// <summary>Debug toggle (F5) — lets a playtester rule dust in/out as the source of an artifact.</summary>
        public static bool Enabled = true;

        private void Update()
        {
            if (_cam == null && (_cam = Camera.main) == null) return;
            // Rebuild on zoom — the box + spawn count are sized to the live view (same as rain).
            if (Mathf.Abs(_cam.orthographicSize - _builtOrtho) > 0.5f) Build();
            if (_ps == null) return;

            if (Input.GetKeyDown(KeyCode.F5)) Enabled = !Enabled;
            var em = _ps.emission;
            if (em.enabled != Enabled)
            {
                em.enabled = Enabled;
                if (!Enabled) _ps.Clear(); // drop existing motes immediately so the toggle is unambiguous
            }
            if (!Enabled) return;

            // Follow the camera so motes always fill the view.
            var cp = _cam.transform.position;
            _ps.transform.position = new Vector3(cp.x, cp.y, 0f);

            // Fade with daylight so the unlit motes don't glow at night (keep a faint trace).
            float day = Mathf.Clamp01(DayNightController.Daylight);
            var main = _ps.main;
            var c = BaseColor;
            c.a = BaseColor.a * (0.15f + 0.85f * day);
            main.startColor = c;
        }
    }
}
