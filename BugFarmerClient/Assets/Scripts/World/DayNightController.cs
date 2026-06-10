using UnityEngine;
using UnityEngine.Rendering.Universal;
using BugFarmer.Entities;

namespace BugFarmer.World
{
    /// <summary>
    /// Day/night cycle driven by the AUTHORITATIVE TICK — the tick is already synced to every
    /// client (ZoneTickBroadcast, 10Hz), so time-of-day needs zero extra netcode:
    ///   timeOfDay = (SimulationTick % 8400) / 8400      (one day = 14 minutes)
    /// A match starts at tick 0 = MORNING (fresh zones are lit). Creates a Global Light2D at
    /// runtime and drives its intensity/color through dawn/day/dusk/night; exposes
    /// Daylight (0..1) for lamp lights (LampLight) and the player's night light.
    /// Attach to the same systems GameObject as DebugOverlay. Fully programmatic — no scene
    /// or prefab setup needed (URP 2D pipeline is active project-wide).
    /// </summary>
    public class DayNightController : MonoBehaviour
    {
        public const long DayTicks = 8400; // must match server DayLengthTicks

        [Header("Ambient")]
        [SerializeField] private float nightIntensity = 0.22f;
        [SerializeField] private Color nightColor = new Color(0.35f, 0.42f, 0.75f); // moonlit blue
        [SerializeField] private Color dawnDuskColor = new Color(1.0f, 0.80f, 0.58f); // warm amber

        /// <summary>Current daylight level 0 (deep night) .. 1 (full day). Lamps read this.</summary>
        public static float Daylight { get; private set; } = 1f;

        /// <summary>Current day number (1-based) for the clock UI.</summary>
        public static int DayNumber { get; private set; } = 1;

        private Light2D _globalLight;
        private PlayerNightLight _playerLight;

        // F7 debug: instantly preview the cycle without waiting for the shared clock.
        // -1 = live tick; otherwise an override of timeOfDay (visual only, this client).
        private static readonly float[] _previewStops = { -1f, 0.50f, 0.70f, 0.95f }; // live, dusk, night, dawn
        private static readonly string[] _previewNames = { "live", "DUSK (preview)", "NIGHT (preview)", "DAWN (preview)" };
        private int _previewIndex;

        private void Start()
        {
            var go = new GameObject("GlobalLight2D");
            go.transform.SetParent(transform);
            _globalLight = go.AddComponent<Light2D>();
            _globalLight.lightType = Light2D.LightType.Global;
            _globalLight.intensity = 1f;
            _globalLight.color = Color.white;
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.F7))
                _previewIndex = (_previewIndex + 1) % _previewStops.Length;

            long tick = SwarmManager.Instance != null ? SwarmManager.Instance.SimulationTick : 0;
            float t = (tick % DayTicks) / (float)DayTicks; // 0 = morning
            if (_previewStops[_previewIndex] >= 0f)
                t = _previewStops[_previewIndex]; // F7 visual preview (this client only)
            DayNumber = (int)(tick / DayTicks) + 1;

            Daylight = DaylightAt(t);

            if (_globalLight != null)
            {
                _globalLight.intensity = Mathf.Lerp(nightIntensity, 1f, Daylight);
                // Near the transitions, tint warm (dawn/dusk); at night go moonlit blue.
                float transition = TransitionAmount(t);
                var dayCol = Color.Lerp(Color.white, dawnDuskColor, transition);
                _globalLight.color = Color.Lerp(nightColor, dayCol, Daylight);
            }

            EnsurePlayerLight();
        }

        /// <summary>
        /// Daylight curve over the day (t=0 is morning):
        ///   0.00-0.45 day -> 0.45-0.55 dusk -> 0.55-0.90 night -> 0.90-1.00 dawn.
        /// </summary>
        private static float DaylightAt(float t)
        {
            if (t < 0.45f) return 1f;
            if (t < 0.55f) return 1f - (t - 0.45f) / 0.10f; // dusk fade
            if (t < 0.90f) return 0f;
            return (t - 0.90f) / 0.10f; // dawn ramp
        }

        /// <summary>1 in the middle of a dawn/dusk transition, 0 elsewhere (for the warm tint).</summary>
        private static float TransitionAmount(float t)
        {
            if (t >= 0.45f && t < 0.55f) return 1f - Mathf.Abs((t - 0.50f) / 0.05f);
            if (t >= 0.90f) return 1f - Mathf.Abs((t - 0.95f) / 0.05f);
            return 0f;
        }

        /// <summary>
        /// Attach the personal night light to the local player once it exists, and switch the
        /// player's sprite renderers (body + gear children) to the lit material.
        /// </summary>
        private void EnsurePlayerLight()
        {
            if (_playerLight != null) return;
            var player = FindObjectOfType<BugFarmer.Player.PlayerController>();
            if (player == null) return;
            _playerLight = player.gameObject.AddComponent<PlayerNightLight>();
            foreach (var sr in player.GetComponentsInChildren<SpriteRenderer>(true))
                LitMaterials.Apply(sr);
        }

        private void OnGUI()
        {
            // Tiny clock: day number + phase glyph + HH:MM of the in-game day (F7 = preview)
            long tick = SwarmManager.Instance != null ? SwarmManager.Instance.SimulationTick : 0;
            float t = (tick % DayTicks) / (float)DayTicks;
            string suffix = "";
            if (_previewStops[_previewIndex] >= 0f)
            {
                t = _previewStops[_previewIndex];
                suffix = $"  [{_previewNames[_previewIndex]} - F7]";
            }
            int mins = (int)(t * 24f * 60f);
            string glyph = Daylight > 0.5f ? "☀" : "☽"; // sun / moon
            GUI.Label(new Rect(Screen.width / 2f - 60, 8, 320, 22),
                $"{glyph} Day {DayNumber}  {(6 + mins / 60) % 24:D2}:{mins % 60:D2}{suffix}");
        }
    }
}
