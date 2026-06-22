using UnityEngine;
using UnityEngine.Rendering.Universal;
using BugFarmer.Entities;

namespace BugFarmer.World
{
    /// <summary>
    /// Day/night cycle driven by the AUTHORITATIVE TICK — the tick is already synced to every
    /// client (ZoneTickBroadcast, 10Hz), so time-of-day needs almost zero extra netcode:
    ///   timeOfDay = ((SimulationTick + DayOffsetTicks) % 8400) / 8400   (one day = 14 min)
    /// DayOffsetTicks arrives via WorldEnv (OpCode 91, on change + per-joiner) — the debug
    /// set-time shifts the APPARENT time on every client identically; the tick never jumps.
    /// A match starts at tick 0 = MORNING (fresh zones are lit). Creates a Global Light2D at
    /// runtime and drives its intensity/color through dawn/day/dusk/night; exposes
    /// Daylight (0..1) for lamp lights (LampLight) and the player's night light.
    /// Attach to the same systems GameObject as DebugOverlay. Fully programmatic — no scene
    /// or prefab setup needed (URP 2D pipeline is active project-wide).
    /// </summary>
    public class DayNightController : MonoBehaviour
    {
        public const long DayTicks = 8400; // must match server DayLengthTicks

        // === World environment (OpCode 91) — shared display state ===
        /// <summary>Debug set-time offset; added to the tick for the apparent time of day.</summary>
        public static long DayOffsetTicks { get; private set; }
        /// <summary>"" or "rain" — applied on receipt; until-tick is the missed-stop fallback.</summary>
        public static string Weather { get; private set; } = "";
        public static long WeatherUntilTick { get; private set; }

        /// <summary>Apparent time within the day, 0..1 (0 = morning). The shared clock.</summary>
        public static float TimeOfDay { get; private set; }

        /// <summary>Current apparent day index (the server's rollover epoch).</summary>
        public static long CurrentDayIndex { get; private set; }

        /// <summary>Debug-only live override for the night-floor intensity (F8 slider).
        /// When non-null it wins over the serialized <see cref="nightIntensity"/>; remove with the
        /// debug overlay before ship.</summary>
        public static float? DebugNightIntensityOverride;

        /// <summary>Additive over-bright on the global light for a lightning strike (0 = none).
        /// Set by RainController on a strike; decayed here each frame. Reuses the single global
        /// light, so the whole screen flashes blue-white for a beat.</summary>
        public static float LightningFlash;

        [Header("Ambient")]
        [SerializeField] private float nightIntensity = 0.20f; // DEEP night — you can't see past light radii
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
            // EXACTLY ONE global light. URP 2D accumulates all global lights into the
            // Multiply blend texture, so a stray scene global at full intensity pins the
            // world bright and defeats the night ramp (the long-standing "night isn't
            // dark" bug — SampleScene shipped a static Global Light 2D at intensity 1).
            // Adopt the first existing global and DISABLE the rest; create one only if
            // none exist. Never leave zero enabled — lit sprites with no global render black.
            foreach (var l in FindObjectsByType<Light2D>(FindObjectsSortMode.None))
            {
                if (l.lightType != Light2D.LightType.Global) continue;
                if (_globalLight == null) _globalLight = l;
                else l.enabled = false;
            }
            if (_globalLight == null)
            {
                var go = new GameObject("GlobalLight2D");
                go.transform.SetParent(transform);
                _globalLight = go.AddComponent<Light2D>();
                _globalLight.lightType = Light2D.LightType.Global;
            }
            _globalLight.enabled = true;
            _globalLight.intensity = 1f;
            _globalLight.color = Color.white;

            if (BugFarmer.Networking.WorldManager.Instance != null)
                BugFarmer.Networking.WorldManager.Instance.OnMatchData += HandleMatchData;

            // Rain visuals live on a sibling component (programmatic, no scene setup)
            if (GetComponent<RainController>() == null)
                gameObject.AddComponent<RainController>();
        }

        private void OnDestroy()
        {
            if (BugFarmer.Networking.WorldManager.Instance != null)
                BugFarmer.Networking.WorldManager.Instance.OnMatchData -= HandleMatchData;
        }

        private void HandleMatchData(Nakama.IMatchState state)
        {
            if (state.OpCode != BugFarmer.Networking.OpCodes.WorldEnv) return;
            var json = System.Text.Encoding.UTF8.GetString(state.State);
            var msg = JsonUtility.FromJson<BugFarmer.Networking.WorldEnvMessage>(json);
            if (msg == null) return;
            DayOffsetTicks = msg.day_offset_ticks;
            Weather = msg.weather ?? "";
            WeatherUntilTick = msg.weather_until_tick;
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.F7))
                _previewIndex = (_previewIndex + 1) % _previewStops.Length;

            long tick = SwarmManager.Instance != null ? SwarmManager.Instance.SimulationTick : 0;
            long apparent = tick + DayOffsetTicks;
            float t = (apparent % DayTicks) / (float)DayTicks; // 0 = morning
            if (_previewStops[_previewIndex] >= 0f)
                t = _previewStops[_previewIndex]; // F7 visual preview (this client only)
            CurrentDayIndex = apparent / DayTicks;
            DayNumber = (int)CurrentDayIndex + 1;
            TimeOfDay = t;

            Daylight = DaylightAt(t);

            if (_globalLight != null)
            {
                float nightFloor = DebugNightIntensityOverride ?? nightIntensity;
                float intensity = Mathf.Lerp(nightFloor, 1f, Daylight);
                if (RainController.Raining)
                    intensity *= 0.85f; // overcast dim while it rains
                else if (Weather == "drought")
                    intensity *= 1.08f; // parched: harsh, glaring sun (a Director drought)
                intensity += LightningFlash; // additive over-bright on a strike
                _globalLight.intensity = intensity;
                // Near the transitions, tint warm (dawn/dusk); at night go moonlit blue.
                float transition = TransitionAmount(t);
                var dayCol = Color.Lerp(Color.white, dawnDuskColor, transition);
                var col = Color.Lerp(nightColor, dayCol, Daylight);
                if (RainController.Raining) // overcast: cooler, desaturated
                    col = Color.Lerp(col, new Color(0.62f, 0.66f, 0.72f), 0.32f);
                else if (Weather == "drought") // parched: warm, washed-out, dusty
                    col = Color.Lerp(col, new Color(1.0f, 0.90f, 0.66f), 0.34f);
                if (LightningFlash > 0f) // strikes are blue-white
                    col = Color.Lerp(col, Color.white, Mathf.Min(1f, LightningFlash));
                _globalLight.color = col;
                // Snappy decay: a ~1.0 flash fades in ~0.2s.
                LightningFlash = Mathf.MoveTowards(LightningFlash, 0f, Time.deltaTime * 5f);
            }

            EnsurePlayerLight();
        }

        /// <summary>
        /// Daylight curve over the day (t=0 is morning):
        ///   0.00-0.42 day -> 0.42-0.58 golden dusk (smoothstep — the fruit-fall evening
        ///   window t∈[0.40,0.62) lives inside it) -> 0.58-0.88 deep night -> 0.88-1.00
        ///   smoothstep dawn. Smoothstep replaces the old abrupt linear ramps.
        /// </summary>
        private static float DaylightAt(float t)
        {
            if (t < 0.42f) return 1f;
            if (t < 0.58f) return 1f - Mathf.SmoothStep(0f, 1f, (t - 0.42f) / 0.16f); // dusk
            if (t < 0.88f) return 0f;
            return Mathf.SmoothStep(0f, 1f, (t - 0.88f) / 0.12f); // dawn
        }

        /// <summary>1 in the middle of a dawn/dusk transition, 0 elsewhere (for the warm tint).</summary>
        private static float TransitionAmount(float t)
        {
            if (t >= 0.42f && t < 0.58f) return 1f - Mathf.Abs((t - 0.50f) / 0.08f);
            if (t >= 0.88f) return 1f - Mathf.Abs((t - 0.94f) / 0.06f);
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
            float t = ((tick + DayOffsetTicks) % DayTicks) / (float)DayTicks;
            string suffix = "";
            if (_previewStops[_previewIndex] >= 0f)
            {
                t = _previewStops[_previewIndex];
                suffix = $"  [{_previewNames[_previewIndex]} - F7]";
            }
            int mins = (int)(t * 24f * 60f);
            string glyph = Daylight > 0.5f ? "☀" : "☽"; // sun / moon
            if (Weather == "rain") glyph = "☔";        // weather wins the glyph slot
            GUI.Label(new Rect(Screen.width / 2f - 60, 8, 320, 22),
                $"{glyph} Day {DayNumber}  {(6 + mins / 60) % 24:D2}:{mins % 60:D2}{suffix}");
        }
    }
}
