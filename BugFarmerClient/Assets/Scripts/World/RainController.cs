using System.Collections.Generic;
using UnityEngine;
using BugFarmer.Audio;

namespace BugFarmer.World
{
    /// <summary>
    /// Rain visuals, driven by DayNightController.Weather (WorldEnv OpCode 91 — applied on receipt;
    /// until-tick is the missed-stop fallback). DayNightController creates this at runtime (no scene
    /// setup) and reads <see cref="Raining"/> for the ambient overcast dim.
    ///
    /// Built to be a real effect, not a flat sheet:
    ///   - PARALLAX streak layers (data-driven <see cref="LayerSpec"/> presets, depth via per-layer
    ///     size/speed/sort): Light = one gentle layer; Heavy = an intense base + a darker-drops layer.
    ///   - A SPLASH layer: short ripples scattered across the visible ground (drops landing).
    ///   - GUSTING wind: the streak drift breathes over time instead of a constant.
    ///   - LIGHTNING (Heavy only): an over-bright flash on the single global light + delayed thunder.
    ///
    /// <see cref="Intensity"/> picks the preset — a CLIENT toggle today (F8), a clean seam for the
    /// multi-zone system to drive per-zone later. Fog/dust (BACKLOG) will be SEPARATE self-activating
    /// components reading the same weather state, not branches here (their shapes differ too much to
    /// share a base until 2-3 exist).
    /// </summary>
    public class RainController : MonoBehaviour
    {
        /// <summary>True while rain visuals should show (weather + fallback evaluated).</summary>
        public static bool Raining { get; private set; }

        public enum RainIntensity { Light, Heavy }
        /// <summary>Which preset the "rain" state renders. Default Light ("normal" rain). Set by the
        /// F8 debug toggle now; intended to be server/zone-driven later.</summary>
        public static RainIntensity Intensity = RainIntensity.Light;

        /// <summary>One stretched-streak layer's tunables (data, not code paths).</summary>
        private struct LayerSpec
        {
            public float lifetime, sizeMin, sizeMax, emission, velYMin, velYMax, velScale;
            public Color color;
            public int sortOrder;
        }

        // Light / "normal" rain — one gentle layer: short, thin, dim, slow.
        private static readonly LayerSpec[] LightLayers =
        {
            new LayerSpec { lifetime = 0.7f, sizeMin = 0.04f, sizeMax = 0.05f, emission = 200f,
                velYMin = -15f, velYMax = -12f, velScale = 0.045f,
                color = new Color(0.74f, 0.84f, 1f, 0.34f), sortOrder = 900 },
        };

        // Heavy rain — an intense base PLUS a darker-drops layer on top for depth.
        private static readonly LayerSpec[] HeavyLayers =
        {
            new LayerSpec { lifetime = 0.95f, sizeMin = 0.05f, sizeMax = 0.09f, emission = 520f,
                velYMin = -22f, velYMax = -16f, velScale = 0.07f,
                color = new Color(0.74f, 0.84f, 1f, 0.5f), sortOrder = 900 },
            new LayerSpec { lifetime = 0.9f, sizeMin = 0.05f, sizeMax = 0.08f, emission = 300f,
                velYMin = -24f, velYMax = -18f, velScale = 0.075f,
                color = new Color(0.40f, 0.48f, 0.62f, 0.5f), sortOrder = 901 },
        };

        private static RainController _inst;

        private readonly List<ParticleSystem> _streaks = new();
        private ParticleSystem _splash;
        private Camera _cam;
        private RainIntensity _builtIntensity;
        private float _nextStrike;

        private void Awake() => _inst = this;

        private void Start()
        {
            AudioFx.Ensure();           // thunder needs the synth pool alive
            _cam = Camera.main;
            BuildLayers();
        }

        // ---- layer construction ----

        private void BuildLayers()
        {
            foreach (var s in _streaks)
                if (s != null) Destroy(s.gameObject);
            _streaks.Clear();
            if (_splash != null) Destroy(_splash.gameObject);

            var specs = Intensity == RainIntensity.Heavy ? HeavyLayers : LightLayers;
            for (int i = 0; i < specs.Length; i++)
                _streaks.Add(BuildStreak($"RainStreak{i}", specs[i]));

            // Sparse splashes for light, dense for heavy.
            _splash = BuildSplash(Intensity == RainIntensity.Heavy ? 130f : 45f);
            _builtIntensity = Intensity;
        }

        private ParticleSystem BuildStreak(string name, LayerSpec s)
        {
            var ps = NewSystem(name);
            var main = ps.main;
            main.loop = true;
            main.startLifetime = s.lifetime;
            main.startSpeed = 0f;                 // motion from velocityOverLifetime
            main.startSize = new ParticleSystem.MinMaxCurve(s.sizeMin, s.sizeMax);
            main.startColor = s.color;
            main.maxParticles = 1400;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.playOnAwake = false;

            var emission = ps.emission;
            emission.rateOverTime = s.emission;
            emission.enabled = false;

            var shape = ps.shape;                 // wide thin band above the camera top edge
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(30f, 1.5f, 1f);

            // ALL three velocity curves MUST share a mode (TwoConstants) or Unity throws "Particle
            // Velocity curves must all be in the same mode" and emits nothing (the bug that hid rain).
            var vel = ps.velocityOverLifetime;
            vel.enabled = true;
            vel.space = ParticleSystemSimulationSpace.World;
            vel.x = new ParticleSystem.MinMaxCurve(0.8f, 1.6f); // gusted each frame in Update
            vel.y = new ParticleSystem.MinMaxCurve(s.velYMin, s.velYMax);
            vel.z = new ParticleSystem.MinMaxCurve(0f, 0f);

            var r = ps.GetComponent<ParticleSystemRenderer>();
            r.renderMode = ParticleSystemRenderMode.Stretch;
            r.velocityScale = s.velScale;
            r.material = new Material(Shader.Find("Sprites/Default")); // unlit; stretch + lit is flaky
            r.sortingLayerName = "Occupants";
            r.sortingOrder = s.sortOrder;
            return ps;
        }

        private ParticleSystem BuildSplash(float emission)
        {
            var ps = NewSystem("RainSplash");
            var main = ps.main;
            main.loop = true;
            main.startLifetime = 0.35f;
            main.startSpeed = 0f;                 // splashes pop in place and fade
            main.startSize = new ParticleSystem.MinMaxCurve(0.05f, 0.11f);
            main.startColor = new Color(0.85f, 0.9f, 1f, 0.5f);
            main.maxParticles = 700;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.playOnAwake = false;

            var em = ps.emission;
            em.rateOverTime = emission;
            em.enabled = false;

            var shape = ps.shape;                 // a flat box over the whole camera view
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(32f, 20f, 1f);

            // Ripple: grow a little, then the alpha fades to nothing.
            var sol = ps.sizeOverLifetime;
            sol.enabled = true;
            sol.size = new ParticleSystem.MinMaxCurve(1f,
                new AnimationCurve(new Keyframe(0f, 0.3f), new Keyframe(1f, 1.4f)));

            var col = ps.colorOverLifetime;
            col.enabled = true;
            var grad = new Gradient();
            grad.SetKeys(
                new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                new[] { new GradientAlphaKey(1f, 0f), new GradientAlphaKey(0f, 1f) });
            col.color = new ParticleSystem.MinMaxGradient(grad);

            var r = ps.GetComponent<ParticleSystemRenderer>();
            r.renderMode = ParticleSystemRenderMode.Billboard;
            r.material = new Material(Shader.Find("Sprites/Default"));
            r.sortingLayerName = "Occupants";
            r.sortingOrder = 895;                 // under the falling streaks
            return ps;
        }

        private ParticleSystem NewSystem(string name)
        {
            var go = new GameObject(name);
            go.transform.SetParent(transform, false);
            return go.AddComponent<ParticleSystem>();
        }

        // ---- per-frame ----

        private void Update()
        {
            if (_builtIntensity != Intensity)
                BuildLayers();

            bool raining = DayNightController.Weather == "rain";
            if (raining && DayNightController.WeatherUntilTick > 0)
            {
                long tick = Entities.SwarmManager.Instance != null
                    ? Entities.SwarmManager.Instance.SimulationTick : 0;
                if (tick > DayNightController.WeatherUntilTick)
                    raining = false;            // missed-stop fallback
            }
            Raining = raining;

            ToggleEmission(_streaks, raining);
            ToggleEmission(_splash, raining);

            if (!raining || _cam == null && (_cam = Camera.main) == null)
                return;

            // Gusting wind: a breathing horizontal drift shared by every streak layer.
            float wind = 1.1f + 0.9f * Mathf.Sin(Time.time * 0.6f)
                       + (Mathf.PerlinNoise(Time.time * 0.35f, 0f) - 0.5f) * 1.2f;
            foreach (var ps in _streaks)
            {
                if (ps == null) continue;
                var vel = ps.velocityOverLifetime;
                vel.x = new ParticleSystem.MinMaxCurve(wind - 0.4f, wind + 0.4f);
            }

            // Position: streak band just above the visible top edge; splashes over the whole view.
            var cp = _cam.transform.position;
            float top = cp.y + _cam.orthographicSize + 1.5f;
            foreach (var ps in _streaks)
                if (ps != null) ps.transform.position = new Vector3(cp.x - 1f, top, 0f);
            if (_splash != null)
                _splash.transform.position = new Vector3(cp.x, cp.y, 0f);

            // Heavy storms flash. Random intervals; first strike a few seconds in.
            if (Intensity == RainIntensity.Heavy)
            {
                if (_nextStrike <= 0f) _nextStrike = Time.time + Random.Range(4f, 10f);
                if (Time.time >= _nextStrike)
                {
                    Strike();
                    _nextStrike = Time.time + Random.Range(7f, 18f);
                }
            }
        }

        private static void ToggleEmission(ParticleSystem ps, bool on)
        {
            if (ps == null) return;
            var em = ps.emission;
            if (em.enabled != on)
            {
                em.enabled = on;
                if (on) ps.Play();
            }
        }

        private static void ToggleEmission(List<ParticleSystem> list, bool on)
        {
            foreach (var ps in list) ToggleEmission(ps, on);
        }

        // ---- lightning ----

        /// <summary>F8 "Strike lightning" button hook.</summary>
        public static void RequestStrike() { if (_inst != null) _inst.Strike(); }

        private void Strike()
        {
            DayNightController.LightningFlash = Random.Range(1.0f, 1.5f);
            Invoke(nameof(SecondFlicker), 0.07f);                  // characteristic double flash
            Invoke(nameof(PlayThunder), Random.Range(0.3f, 1.6f)); // sound lags light = distance
        }

        private void SecondFlicker() =>
            DayNightController.LightningFlash = Mathf.Max(DayNightController.LightningFlash, 0.6f);

        private void PlayThunder() => AudioFx.Thunder();
    }
}
