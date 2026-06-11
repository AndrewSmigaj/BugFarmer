using UnityEngine;

namespace BugFarmer.World
{
    /// <summary>
    /// Rain visuals: a camera-following band of stretched streak particles, driven entirely
    /// by DayNightController.Weather (WorldEnv OpCode 91 — applied on receipt; the until-tick
    /// is the missed-stop fallback). DayNightController creates this at runtime (no scene
    /// setup) and also reads <see cref="Raining"/> for the ambient dim while it rains.
    /// </summary>
    public class RainController : MonoBehaviour
    {
        /// <summary>True while rain visuals should show (weather + fallback evaluated).</summary>
        public static bool Raining { get; private set; }

        [SerializeField] private float emissionRate = 240f;
        [SerializeField] private Color rainColor = new Color(0.72f, 0.82f, 1f, 0.45f);

        private ParticleSystem _ps;
        private Camera _cam;

        private void Start()
        {
            _cam = Camera.main;

            var go = new GameObject("RainParticles");
            go.transform.SetParent(transform, false);
            _ps = go.AddComponent<ParticleSystem>();

            var main = _ps.main;
            main.loop = true;
            main.startLifetime = 0.7f;
            main.startSpeed = 0f;
            main.startSize = 0.06f;
            main.startColor = rainColor;
            main.maxParticles = 800;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.playOnAwake = false;

            var emission = _ps.emission;
            emission.rateOverTime = emissionRate;
            emission.enabled = false;

            // A wide, thin band hovering above the camera's top edge (positioned in Update)
            var shape = _ps.shape;
            shape.enabled = true;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(26f, 1.5f, 1f);

            // Slanted fall — the streak look comes from stretch-mode rendering
            var vel = _ps.velocityOverLifetime;
            vel.enabled = true;
            vel.space = ParticleSystemSimulationSpace.World;
            vel.x = new ParticleSystem.MinMaxCurve(1.2f, 2.0f);
            vel.y = new ParticleSystem.MinMaxCurve(-17f, -14f);
            vel.z = 0f;

            var renderer = _ps.GetComponent<ParticleSystemRenderer>();
            renderer.renderMode = ParticleSystemRenderMode.Stretch;
            renderer.velocityScale = 0.045f;
            // Deliberately UNLIT (Sprites/Default): a lit sprite shader on a stretch-mode
            // particle renderer is unreliable, and faint glowing streaks read fine at night.
            renderer.material = new Material(Shader.Find("Sprites/Default"));
            renderer.sortingLayerName = "Occupants";
            renderer.sortingOrder = 900; // above world objects, below screen UI
        }

        private void Update()
        {
            bool raining = DayNightController.Weather == "rain";

            // Missed-stop fallback: until-tick shares the SimulationTick domain
            if (raining && DayNightController.WeatherUntilTick > 0)
            {
                long tick = Entities.SwarmManager.Instance != null
                    ? Entities.SwarmManager.Instance.SimulationTick : 0;
                if (tick > DayNightController.WeatherUntilTick)
                    raining = false;
            }

            Raining = raining;
            if (_ps == null) return;

            var emission = _ps.emission;
            if (emission.enabled != raining)
            {
                emission.enabled = raining;
                if (raining) _ps.Play();
            }

            // Follow the camera: keep the emitter band just above the visible top edge
            if (raining)
            {
                if (_cam == null) _cam = Camera.main;
                if (_cam != null)
                {
                    var p = _cam.transform.position;
                    _ps.transform.position = new Vector3(p.x - 1f, p.y + _cam.orthographicSize + 1.5f, 0f);
                }
            }
        }
    }
}
