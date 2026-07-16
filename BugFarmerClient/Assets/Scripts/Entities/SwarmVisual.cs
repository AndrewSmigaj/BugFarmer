using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using BugFarmer.Bugs;
using BugFarmer.Networking;
using BugFarmer.Util;

namespace BugFarmer.Entities
{
    /// <summary>
    /// Visual representation of a swarm - a PASSIVE RENDERER that never owns time.
    /// SwarmManager owns THE ONE simulation tick and calls:
    /// - SimulateTick(tick, players) to advance bug simulation
    /// - Interpolate(t) to smooth visuals between ticks
    ///
    /// This class manages Dictionary of bugs keyed by ID for O(1) lookup.
    /// FIX #2: All bug iteration uses OrderBy(bugId) for determinism.
    ///
    /// Species differentiation is automatic via BugAgent constructor:
    /// - fly → BrownianMovement (erratic, flee from players)
    /// - butterfly → GlidingMovement (graceful arcs, curious toward players)
    /// </summary>
    public class SwarmVisual : MonoBehaviour
    {
        // Bugs keyed by ID for O(1) lookup and deterministic removal
        private readonly Dictionary<int, BugVisual> _bugs = new();
        private static readonly Stack<Transform> _spritePool = new();

        // Species sprite loaded from Resources/Bugs/{species_id}
        private Sprite _bugSprite;
        // Cosmetic flap-animation frames (Bugs/{spriteId}_0.png, _1.png, ...). null = static sprite.
        // DISPLAY-ONLY: the shown frame is never hashed, so animation is free to differ per client.
        private Sprite[] _bugFrames;
        private bool _isBuzzer;     // fly-type → fast continuous wing buzz (no glide)

        // Bug ID tracking (matches server)
        private int _nextBugId;
        private HashSet<int> _removedIds = new();

        // Swarm center interpolation (server-driven)
        private Vector2 _previousCenter;
        private Vector2 _targetCenter;
        private float _centerInterpProgress = 1f;
        private const float CenterInterpDuration = 0.15f;

        // NOTE: SwarmManager owns THE ONE simulation tick.
        // SwarmVisual NEVER advances time on its own.
        // _localTick and _tickAccumulator have been REMOVED.

        // Late joiner sync - don't simulate until snapshot received
        private bool _waitingForSnapshot;

        // Deterministic swarm center, derived each SimulateTick from the swarm's current
        // movement leg (InfluenceManager.TryComputeSwarmCenter). This is the value bug AI reads.
        // It is NEVER written from the rendered transform - that would be non-deterministic (#1 fix).
        private FixedPoint2 _simCenter;
        // Initial/fallback center (from SwarmData x,y) used until the first SWARM_SET_TARGET leg.
        private FixedPoint2 _fallbackCenter;
        private float _radius;

        public string SwarmId { get; private set; }
        public string SpeciesId { get; private set; }
        public int Count => _bugs.Count;

        // DIAGNOSTIC (leg/center trace): the center bug AI used this tick, and the metadata fallback center.
        public FixedPoint2 SimCenter => _simCenter;
        public FixedPoint2 FallbackCenter => _fallbackCenter;
        public float Radius => _radius;
        public bool IsWaitingForSnapshot => _waitingForSnapshot;

        /// <summary>
        /// Mark this swarm as waiting for snapshot (late joiner).
        /// Simulation is paused until ApplySnapshot is called.
        /// </summary>
        public void SetWaitingForSnapshot()
        {
            _waitingForSnapshot = true;
            Debug.Log($"[SwarmVisual] {SwarmId} waiting for snapshot - simulation paused");
        }

        /// <summary>
        /// Initialize the swarm visual with server data.
        /// Handles late joiner sync via next_bug_id and removed_ids.
        /// </summary>
        /// <summary>
        /// Initialize swarm from server data.
        /// </summary>
        /// <param name="data">Swarm data from server</param>
        /// <param name="serverTick">The server tick from the SwarmUpdate message - MUST use this for determinism</param>
        public void Initialize(SwarmData data, long serverTick)
        {
            SwarmId = data.id;
            SpeciesId = data.species_id;

            // Load sprite from Resources using sprite_id from server. SWARM_SPAWNED-born swarms
            // arrive with an EMPTY sprite_id (the later SwarmUpdate carries the real one) — resolve
            // it from the species def so we never fall back to the raw species id, which has no
            // Bugs/ sprite (e.g. butterfly_meadow -> butterfly_common). Display-only, never hashed.
            var spriteId = data.sprite_id;
            if (string.IsNullOrEmpty(spriteId))
            {
                var spInfo = Data.EntityDatabase.GetSpecies(data.species_id);
                spriteId = !string.IsNullOrEmpty(spInfo?.SpriteId) ? spInfo.SpriteId : data.species_id;
            }
            // Flies buzz continuously (fast, no glide); butterflies keep the graceful flap-glide default.
            _isBuzzer = !string.IsNullOrEmpty(spriteId) &&
                        spriteId.Contains("fly") && !spriteId.Contains("butterfly");
            // Animation frames: Bugs/{spriteId}_0, _1, ... (contiguous). >=2 => animated (cosmetic flap).
            var frames = new System.Collections.Generic.List<Sprite>();
            for (int i = 0; i < 12; i++)
            {
                var f = Resources.Load<Sprite>($"Bugs/{spriteId}_{i}");
                if (f == null) break;
                frames.Add(f);
            }
            _bugFrames = frames.Count >= 2 ? frames.ToArray() : null;
            _bugSprite = _bugFrames != null ? _bugFrames[0] : Resources.Load<Sprite>($"Bugs/{spriteId}");
            if (_bugSprite == null)
            {
                Debug.LogWarning($"[SwarmVisual] No sprite found at Resources/Bugs/{spriteId}");
            }

            _previousCenter = new Vector2(data.x, data.y);
            _targetCenter = _previousCenter;
            _fallbackCenter = FixedPoint2.FromVector2(_previousCenter);
            _simCenter = _fallbackCenter;
            transform.position = _previousCenter;
            _radius = data.radius;

            // Setup bug ID tracking for late joiner sync
            _nextBugId = data.next_bug_id > 0 ? data.next_bug_id : data.count;
            _removedIds.Clear();
            if (data.removed_ids != null)
            {
                foreach (int id in data.removed_ids)
                {
                    _removedIds.Add(id);
                }
            }

            // NOTE: SwarmManager owns the tick. serverTick is used only for logging/debugging.
            // The actual tick for simulation comes from SwarmManager.AdvanceOneTick().

            // Spawn bugs with deterministic positions
            SpawnInitialBugs(data.count, data.radius);
        }

        /// <summary>
        /// Spawn initial bugs deterministically. For late joiners, spawns bugs 0 to _nextBugId-1
        /// skipping any in _removedIds, resulting in exactly data.count bugs.
        /// </summary>
        private void SpawnInitialBugs(int targetCount, float radius)
        {
            if (!WorldSeedProvider.Instance?.IsInitialized ?? true)
            {
                Debug.LogError($"[SwarmVisual] WorldSeed not initialized! This should not happen - SwarmManager should wait for seed.");
                return; // Don't spawn bugs without proper seed
            }

            long worldSeed = WorldSeedProvider.Instance.WorldSeed;

            var spawnMsg = $"[SwarmVisual] Spawning {targetCount} bugs for swarm {SwarmId} with seed {worldSeed}, nextBugId={_nextBugId}";
            Debug.Log(spawnMsg);
            DebugFileLogger.Log(spawnMsg);

            // Spawn bugs 0 to _nextBugId-1, skipping removed IDs
            for (int bugId = 0; bugId < _nextBugId && _bugs.Count < targetCount; bugId++)
            {
                if (_removedIds.Contains(bugId))
                    continue;

                SpawnBug(worldSeed, bugId, radius);
            }

            var completeMsg = $"[SwarmVisual] Spawn complete for {SwarmId}: {_bugs.Count} bugs created (target was {targetCount}, nextBugId={_nextBugId})";
            Debug.Log(completeMsg);
            DebugFileLogger.Log(completeMsg);
        }

        /// <summary>
        /// Spawn a single bug with deterministic initial position.
        /// BugAgent constructor automatically gets correct movement for species:
        /// - fly → BrownianMovement
        /// - butterfly → GlidingMovement
        /// </summary>
        private void SpawnBug(long worldSeed, int bugId, float radius)
        {
            // Phase B: spawn every bug AT the swarm center; they spread outward by seeded per-bug wander
            // (there is no separation force). Deterministic — all clients place each bug at the same center.
            // (`radius` is retained in the signature but no longer scatters the spawn.)
            var startPos = _simCenter;

            // Create agent - MovementFactory.CreateMovement(SpeciesId) is called internally
            // fly → BrownianMovement, butterfly → GlidingMovement, etc.
            var agent = new BugAgent(worldSeed, SwarmId, SpeciesId, bugId, startPos);
            // DIAGNOSTIC (re-root investigation): stamp when/how this client first created the bug.
            var sm = SwarmManager.Instance;
            agent.SpawnTick = sm != null ? sm.CurrentSimTick : -1;
            agent.SpawnSource = sm != null ? sm.SpawnSourceTag : "?";

            // Get or create visual
            var visual = GetSpriteFromPool();
            if (visual == null)
            {
                var obj = new GameObject($"Bug_{bugId}");
                var sr = obj.AddComponent<SpriteRenderer>();
                sr.sprite = _bugSprite;
                sr.sortingLayerName = "Occupants";
                World.LitMaterials.Apply(sr); // bugs receive day/night lighting
                visual = obj.transform;
            }
            else
            {
                // Update pooled sprite in case species changed
                var sr = visual.GetComponent<SpriteRenderer>();
                if (sr != null)
                {
                    sr.sprite = _bugSprite;
                    sr.sortingLayerName = "Occupants";
                }
            }

            visual.gameObject.SetActive(true);
            visual.SetParent(transform);
            visual.position = startPos.ToVector2();

            // FLYING TELL (display-only): species that ignore fences get a drop shadow
            // offset below the sprite — the universal "airborne" read. Without it, a
            // wasp crossing your fence looks like broken collision. Pooled visuals may
            // carry a stale shadow from another species — sync its presence.
            var behavior = Bugs.MovementFactory.GetBehavior(SpeciesId);
            var shadow = visual.Find("Shadow");
            if (behavior.FliesOverFences && shadow == null)
            {
                var shadowGo = new GameObject("Shadow");
                shadowGo.transform.SetParent(visual, false);
                shadowGo.transform.localPosition = new Vector3(0.06f, -0.22f, 0f);
                shadowGo.transform.localScale = new Vector3(0.8f, 0.45f, 1f);
                var ssr = shadowGo.AddComponent<SpriteRenderer>();
                ssr.sprite = _bugSprite;
                ssr.color = new Color(0f, 0f, 0f, 0.35f);
                ssr.sortingLayerName = "Occupants";
                ssr.sortingOrder = -1000; // always under the bug
            }
            else if (!behavior.FliesOverFences && shadow != null)
            {
                Object.Destroy(shadow.gameObject);
            }

            // FIREFLY GLOW (display-only): each firefly carries a tiny warm LampLight —
            // invisible at noon, full amber at night (LampLight self-ramps by daylight,
            // the lamp/torch pattern). Pooled visuals may carry a stale glow from another
            // species — sync its presence exactly like the shadow above.
            bool glows = SpeciesId == "firefly";
            var glow = visual.Find("Glow");
            if (glows && glow == null)
            {
                var glowGo = new GameObject("Glow");
                glowGo.transform.SetParent(visual, false);
                glowGo.transform.localPosition = Vector3.zero;
                glowGo.AddComponent<World.LampLight>()
                      .Configure(1.6f, new Color(1f, 0.82f, 0.35f), 0.9f);
            }
            else if (!glows && glow != null)
            {
                Object.Destroy(glow.gameObject);
            }

            var bugVisual = new BugVisual(agent, visual);
            bugVisual.Frames = _bugFrames; // cosmetic flap frames (null = static)

            if (_isBuzzer)
            {
                // Fast, continuous wing buzz with a quick jittery hover — no butterfly glide.
                bugVisual.FlapFps = 20f;
                bugVisual.GlideSecs = 0f;
                bugVisual.FlapsPerBurst = 1;
                bugVisual.BobAmp = 0.03f;
                bugVisual.BobHz = 3.6f;
            }
            _bugs[bugId] = bugVisual;

            // INDIVIDUALS (centipede knots, §14.3): EVERY member drags its own
            // pure-display segment trail (a child GO so its segments die with it);
            // segment positions also feed the melee sector query (a body that's
            // unhittable on 6/8ths of its length reads as broken). The head sprite is
            // 2.0 world units raw — scale it down to match the trail parts. Pooled
            // visuals may arrive from a non-crawling species (or go back to one), so
            // BOTH branches set scale/rotation explicitly.
            var info = Data.EntityDatabase.GetSpecies(SpeciesId);
            bool crawling = info != null && info.MovementStyle == "crawling";
            // Only the SEGMENTED crawlers (centipede/millipede) render the multi-part body trail.
            // Single-body crawlers (e.g. beetle_carrion) fall through to the single-sprite path —
            // without this they'd be drawn with the hardcoded centipede trail (CentipedeTrail.cs).
            bool segmented = crawling &&
                             (SpeciesId.Contains("centipede") || SpeciesId.Contains("millipede"));
            if (segmented)
            {
                // Head scale matches its trail segments — per species (millipede = 2x centipede).
                float headScale = Bugs.CentipedeTrail.PartScaleFor(SpeciesId);
                visual.localScale = new Vector3(headScale, headScale, 1f);
                if (!_trails.ContainsKey(bugId))
                {
                    var trailGo = new GameObject($"trail_{bugId}");
                    trailGo.transform.SetParent(transform, false);
                    var trail = trailGo.AddComponent<Bugs.CentipedeTrail>();
                    trail.Initialize(visual, SpeciesId);
                    _trails[bugId] = trail;
                }
            }
            else
            {
                // Flies & butterflies read a touch large at 1:1 next to the player and the other
                // bugs — render them at HALF scale (user feedback). Wasps stay full size UNLESS the
                // species sets render_scale (e.g. wasp_soldier = 0.5 — its sprite reads too big). This
                // is DISPLAY-ONLY (localScale is never in the sim hash), so it's free to differ per
                // client, exactly like the crawler head scale above.
                float s = FlyerRenderScale(SpeciesId) * (info != null && info.RenderScale > 0f ? info.RenderScale : 1f);
                visual.localScale = new Vector3(s, s, 1f);
                visual.rotation = Quaternion.identity;
            }
        }

        /// <summary>Cosmetic render scale for NON-crawling bugs. Flies AND butterflies render at
        /// half size (they read large at 1:1); wasps/anything else stay unscaled. "butterfly_*"
        /// contains "fly", so one Contains("fly") covers both. Display-only — never hashed.</summary>
        private static float FlyerRenderScale(string speciesId) =>
            (!string.IsNullOrEmpty(speciesId) && speciesId.Contains("fly")) ? 0.5f : 1f;

        // One segment trail per crawling bug, keyed by bug id (1-3 per knot).
        private readonly Dictionary<int, Bugs.CentipedeTrail> _trails = new();

        /// <summary>Destroy a bug's trail (its segment GOs die with the child GO).</summary>
        private void DestroyTrail(int bugId)
        {
            if (_trails.TryGetValue(bugId, out var trail))
            {
                if (trail != null)
                    Destroy(trail.gameObject);
                _trails.Remove(bugId);
            }
        }

        /// <summary>
        /// Update from server data. SwarmUpdate is now event-driven (spawn/despawn/merge/split/
        /// count/phase change), NOT a per-tick center firehose. The center itself is derived
        /// deterministically from SWARM_SET_TARGET legs; data.x/y only updates the pre-leg fallback.
        /// </summary>
        public void UpdateFromServer(SwarmData data)
        {
            // data.x/y is the initial/fallback center, used only until the first leg event.
            _fallbackCenter = FixedPoint2.FromVector2(new Vector2(data.x, data.y));

            // Update cached state
            _radius = data.radius;

            // Sync bug ID state if server provides it
            if (data.next_bug_id > _nextBugId)
            {
                _nextBugId = data.next_bug_id;
            }
        }

        private void Update()
        {
            // ONLY do center interpolation - SwarmManager owns tick advancement
            UpdateCenterInterpolation();

            // DO NOT advance ticks here - SwarmManager.AdvanceOneTick() handles that
            // DO NOT call SimulateTick() here
            // Interpolation is called by SwarmManager.InterpolateAllSwarms()
        }

        private void UpdateCenterInterpolation()
        {
            // COSMETIC ONLY. Lerps the rendered transform toward the deterministic _simCenter.
            // It MUST NOT write any value the simulation reads (that was the #1 determinism bug).
            if (_centerInterpProgress < 1f)
            {
                _centerInterpProgress += Time.deltaTime / CenterInterpDuration;
                if (_centerInterpProgress > 1f)
                    _centerInterpProgress = 1f;

                transform.position = Vector2.Lerp(_previousCenter, _targetCenter, _centerInterpProgress);
            }
        }

        /// <summary>
        /// Simulate one tick. Called by SwarmManager (which owns SimulationTick).
        /// SwarmVisual NEVER advances time on its own.
        /// FIX #2: Bugs MUST be iterated in deterministic order (sorted by bugId).
        /// </summary>
        /// <param name="tick">The current simulation tick from SwarmManager</param>
        /// <param name="players">Player targets from InfluenceManager (deterministic, sorted by playerId)</param>
        public void SimulateTick(long tick, List<PlayerTarget> players,
                                 IReadOnlyList<(int bugId, FixedPoint2 pos)> preyBugs = null)
        {
            using var _perf = PerfProfiler.Sample("Sim.SwarmTick");
            if (!WorldSeedProvider.Instance?.IsInitialized ?? true)
                return;

            // Derive the deterministic swarm center for THIS tick from the current movement leg.
            // Stateless closed-form march - identical on every client, in live and replay.
            // Falls back to the initial/metadata center until the first leg event arrives.
            FixedPoint2 newCenter = (InfluenceManager.Instance != null &&
                                     InfluenceManager.Instance.TryComputeSwarmCenter(SwarmId, tick, out var c))
                ? c
                : _fallbackCenter;

            if (newCenter != _simCenter)
            {
                // Drive cosmetic interpolation from the rendered position toward the new sim center.
                _previousCenter = transform.position;
                _targetCenter = newCenter.ToVector2();
                _centerInterpProgress = 0f;
            }
            _simCenter = newCenter;

            // FIX #2: MUST iterate bugs in deterministic order (sorted by bugId)
            var sortedBugIds = _bugs.Keys.OrderBy(id => id).ToList();

            // Debug: warn if no bugs exist (key diagnostic)
            if (_bugs.Count == 0 && tick % 100 == 0)
            {
                var warnMsg = $"[SwarmVisual] {SwarmId} tick {tick}: NO BUGS! nextBugId={_nextBugId}";
                Debug.LogWarning(warnMsg);
                DebugFileLogger.Log("WARNING: " + warnMsg);
            }

            // 1. Capture previous positions for interpolation FIRST
            foreach (var bugId in sortedBugIds)
            {
                _bugs[bugId].CapturePosition();
            }

            // 2. Simulate each bug in deterministic order
            foreach (var bugId in sortedBugIds)
            {
                _bugs[bugId].Agent.SimulateTick(_simCenter, players, tick, preyBugs);
            }

            // Debug: log first bug's state every 100 ticks (sample one swarm)
            if (sortedBugIds.Count > 0 && tick % 100 == 0 && SwarmId.GetHashCode() % 50 == 0)
            {
                var firstBug = _bugs[sortedBugIds[0]];
                var agent = firstBug.Agent;
                var bugMsg = $"[SwarmVisual] {SwarmId} bug0 @ tick {tick}: pos=({agent.Position.X.Value},{agent.Position.Y.Value}) vel=({agent.Velocity.X.Value},{agent.Velocity.Y.Value}) behavior={agent.CurrentBehavior}";
                DebugFileLogger.Log(bugMsg);
            }
        }

        /// <summary>
        /// Interpolate all bugs between captured positions.
        /// Called by SwarmManager.InterpolateAllSwarms() after time accumulation.
        /// FIX #2: Iterate deterministically even for visuals (cheap insurance).
        /// INVARIANT: This is READ-ONLY visual lerp. MUST NOT mutate simulation state.
        /// </summary>
        /// <param name="t">Interpolation factor (0 to 1)</param>
        public void Interpolate(float t)
        {
            foreach (var bugId in _bugs.Keys.OrderBy(id => id))
            {
                _bugs[bugId].Interpolate(t);
            }
        }

        // NOTE: GetPlayerTargets() REMOVED - SwarmManager provides deterministic player targets
        // from InfluenceManager.GetPlayerCells() via the SimulateTick(tick, players) parameter.
        // This ensures all clients have identical inputs for bug behavior.

        /// <summary>
        /// Get bug IDs within radius of a world position.
        /// Used by catching system to determine which bugs were clicked.
        /// Returns IDs for deterministic removal across all clients.
        /// </summary>
        public int[] GetBugsInRadius(Vector2 worldPos, float radius)
        {
            float radiusSq = radius * radius;
            var result = new List<int>();

            foreach (var kvp in _bugs)
            {
                Vector2 bugPos = kvp.Value.Agent.Position.ToVector2();
                if ((bugPos - worldPos).sqrMagnitude <= radiusSq)
                {
                    result.Add(kvp.Key);
                }
            }

            return result.ToArray();
        }

        /// <summary>
        /// Get bug IDs inside a swept SECTOR (the melee/net hit area: |angle to bug −
        /// aim| ≤ arc/2 within reach of origin). Queries RENDER positions (the
        /// interpolated transform — what the player actually sees mid-lerp), a deliberate
        /// divergence from GetBugsInRadius's sim positions: hit detection is feel, and the
        /// IDs-are-trusted protocol (server validates alive-ids) makes both safe.
        /// </summary>
        public int[] GetBugsInSector(Vector2 origin, float aimDegrees, float arcDegrees, float reach)
        {
            float reachSq = reach * reach;
            float halfArc = arcDegrees / 2f;
            var result = new List<int>();

            foreach (var kvp in _bugs)
            {
                Vector2 bugPos = kvp.Value.Transform != null
                    ? (Vector2)kvp.Value.Transform.position
                    : kvp.Value.CurrPos;
                Vector2 delta = bugPos - origin;
                if (delta.sqrMagnitude > reachSq)
                    continue;
                float bugAngle = Mathf.Atan2(delta.y, delta.x) * Mathf.Rad2Deg;
                if (Mathf.Abs(Mathf.DeltaAngle(aimDegrees, bugAngle)) <= halfArc)
                    result.Add(kvp.Key);
            }

            // INDIVIDUALS: the segment trails are hittable too — a segment inside the
            // sector maps to ITS OWN bug id (knots are 1-3 centipedes, each with a
            // trail). Without this, 6/8ths of every body whiffs. The server validates
            // click-vs-PLAYER reach only (it holds no per-bug positions), so no server
            // change is needed — the rule is "stand within reach of whichever body
            // part you slash".
            foreach (var kvp in _trails)
            {
                int bugId = kvp.Key;
                if (kvp.Value == null || result.Contains(bugId) || !_bugs.ContainsKey(bugId))
                    continue;
                foreach (var seg in kvp.Value.SegmentPositions())
                {
                    Vector2 delta = seg - origin;
                    if (delta.sqrMagnitude > reachSq)
                        continue;
                    float segAngle = Mathf.Atan2(delta.y, delta.x) * Mathf.Rad2Deg;
                    if (Mathf.Abs(Mathf.DeltaAngle(aimDegrees, segAngle)) <= halfArc)
                    {
                        result.Add(bugId);
                        break;
                    }
                }
            }

            return result.ToArray();
        }

        /// <summary>
        /// Set a bug's DISPLAY-ONLY HP (fed by MeleeResultMessage / the late-join seed)
        /// and play the hit flash. Never touches the deterministic sim.
        /// </summary>
        public void SetDisplayHP(int bugId, int hp, bool flash)
        {
            if (!_bugs.TryGetValue(bugId, out var bug)) return;
            bug.DisplayHP = hp;
            if (flash)
                bug.FlashUntil = Time.time + 0.15f;
        }

        /// <summary>Cosmetic hit flash only (e.g. a killed bug, pre-ledger-removal).</summary>
        public void FlashBug(int bugId)
        {
            if (_bugs.TryGetValue(bugId, out var bug))
                bug.FlashUntil = Time.time + 0.15f;
        }

        /// <summary>Flash ONLY the member nearest a world position — one bug snatching its own prey,
        /// so a strike reads as an individual lunge, not the whole swarm flashing at once. Display-only.</summary>
        public void FlashNearest(Vector2 worldPos)
        {
            BugVisual best = null; float bestSqr = float.MaxValue;
            foreach (var bug in _bugs.Values)
            {
                if (bug.Transform == null) continue;
                float d = ((Vector2)bug.Transform.position - worldPos).sqrMagnitude;
                if (d < bestSqr) { bestSqr = d; best = bug; }
            }
            if (best != null)
                best.FlashUntil = Time.time + 0.15f;
        }

        /// <summary>#20: flash AND lunge the member nearest a victim — a committed jab toward the kill so
        /// the strike reads as an individual lunge, not just a flash. Display-only (no sim/hash effect).</summary>
        public void LungeNearest(Vector2 worldPos) => LungeNearest(worldPos, 0.35f, 0.18f);

        /// <summary>Flash + dart the member nearest a world point toward it, with a tunable reach/duration.
        /// The wasp dive uses a BIGGER reach (~1.1 cells) so the peel-off reads as a swoop, not the 0.35 jab
        /// the predation strike uses. Out-and-back (sin envelope in BugVisual.Interpolate); purely cosmetic —
        /// LungeVec never touches Agent.Position or the hash, so all clients keep identical sim positions.</summary>
        public void LungeNearest(Vector2 worldPos, float reach, float secs)
        {
            BugVisual best = null; float bestSqr = float.MaxValue;
            foreach (var bug in _bugs.Values)
            {
                if (bug.Transform == null) continue;
                float d = ((Vector2)bug.Transform.position - worldPos).sqrMagnitude;
                if (d < bestSqr) { bestSqr = d; best = bug; }
            }
            if (best == null) return;
            best.FlashUntil = Time.time + 0.15f;
            Vector2 from = best.Transform.position;
            Vector2 dir = worldPos - from;
            float dist = dir.magnitude;
            // dart toward the victim, but never overshoot past it (cap at 0.6× the gap for a near target).
            best.LungeVec = dist > 0.001f ? dir / dist * Mathf.Min(reach, dist * 0.6f) : Vector2.zero;
            best.LungeStart = Time.time;
            best.LungeDur = secs > 0f ? secs : 0.18f;
        }

        /// <summary>Flash the whole swarm (predator telegraphs — strike snatch, windup).</summary>
        public void FlashAllBugs()
        {
            foreach (var bug in _bugs.Values)
                bug.FlashUntil = Time.time + 0.15f;
        }

        /// <summary>
        /// Remove bugs by ID (deterministic removal).
        /// All clients call this with the same IDs from server broadcast,
        /// ensuring everyone sees the exact same bugs disappear.
        /// </summary>
        public void RemoveBugsById(int[] bugIds)
        {
            if (bugIds == null) return;

            foreach (int id in bugIds)
            {
                if (_bugs.TryGetValue(id, out var bug))
                {
                    DestroyTrail(id); // resets the pooled head's rotation on destroy
                    ReturnSpriteToPool(bug.Transform);
                    _bugs.Remove(id);
                    _removedIds.Add(id);
                }
            }
        }

        // === Split/Merge move machinery (SWARM_SPLIT / SWARM_MERGE influence events) ===
        // Bugs are MOVED between swarms with their position/velocity/motion-state intact —
        // never re-spawned (hard requirement: no visual resets). Safe because rendering is
        // world-space per frame from Agent.Position (BugVisual.Interpolate), and the sim RNG
        // keys live on (SwarmId, BugId), so reassignment only re-keys FUTURE wander.

        /// <summary>
        /// Extract the n highest-id bugs WITHOUT pooling their sprites — they are being moved
        /// to another swarm. Returned in ascending old-id order (deterministic new-id mapping).
        /// The extracted ids are marked removed here, mirroring the server's RemovedBugIDs.
        /// </summary>
        public List<KeyValuePair<int, BugVisual>> ExtractHighestBugs(int n)
        {
            var picked = _bugs.Keys.OrderByDescending(id => id).Take(n).OrderBy(id => id).ToList();
            var result = new List<KeyValuePair<int, BugVisual>>(picked.Count);
            foreach (int id in picked)
            {
                // Defensive: individuals never split/merge (category guards), but if a
                // trailed bug ever moved swarms its trail must not dangle here.
                DestroyTrail(id);
                result.Add(new KeyValuePair<int, BugVisual>(id, _bugs[id]));
                _bugs.Remove(id);
                _removedIds.Add(id);
            }
            return result;
        }

        /// <summary>
        /// Extract ALL bugs (ascending id order) without pooling — used when this swarm is
        /// absorbed by a merge and its bugs move to the survivor before this visual is destroyed.
        /// </summary>
        public List<KeyValuePair<int, BugVisual>> ExtractAllBugs()
        {
            var result = _bugs.OrderBy(kv => kv.Key).ToList();
            _bugs.Clear();
            return result;
        }

        /// <summary>
        /// Insert a moved bug under a new id in THIS swarm: reassigns the agent's identity
        /// (re-keys its counter-RNG for future ticks only), re-parents the visual, and pins the
        /// world position (no jump — rendering is world-space).
        /// </summary>
        public void InsertBug(int newId, BugVisual bug)
        {
            bug.Agent.SwarmId = SwarmId;
            bug.Agent.BugId = newId;
            if (bug.Transform != null)
                bug.Transform.SetParent(transform);
            _bugs[newId] = bug;
            if (newId >= _nextBugId)
                _nextBugId = newId + 1;
            bug.SyncPosition();
        }

        /// <summary>
        /// Remove + pool every current bug (defensive idempotency: clears bugs that were
        /// early-created by an on-receipt SwarmUpdate before the split event applied).
        /// </summary>
        public void ClearBugs()
        {
            foreach (var kvp in _bugs)
                ReturnSpriteToPool(kvp.Value.Transform);
            _bugs.Clear();
        }

        /// <summary>
        /// Spawn one bug at the swarm centre under an explicit id. Deficit-fill for the
        /// late-join window (the bugs to move don't exist locally). No-op if the id exists.
        /// </summary>
        public void SpawnBugAt(int bugId)
        {
            if (_bugs.ContainsKey(bugId)) return;
            if (!(WorldSeedProvider.Instance?.IsInitialized ?? false)) return;
            _removedIds.Remove(bugId); // the id is (re)alive in this swarm
            SpawnBug(WorldSeedProvider.Instance.WorldSeed, bugId, _radius);
            if (bugId >= _nextBugId)
                _nextBugId = bugId + 1;
        }

        /// <summary>
        /// Show catch animation for other players (local player has their own).
        /// </summary>
        public void ShowCatchAnimation(Vector2 catchPos, string catcherID)
        {
            var localUserId = WorldManager.Instance?.Self?.UserId;
            if (catcherID == localUserId)
                return;

            // Visual effect can be added here
            Debug.Log($"[SwarmVisual] Player {catcherID} caught bugs at {catchPos}");
        }

        // === Bug Sync (Late Joiner + Drift Detection) ===

        /// <summary>
        /// Get positions for specific bugs (used for sample request response).
        /// Returns full state including position, velocity, RNG, behavior, and movement state.
        /// </summary>
        public BugSampleData[] GetBugPositions(int[] bugIds)
        {
            var result = new List<BugSampleData>();
            foreach (int id in bugIds)
            {
                if (_bugs.TryGetValue(id, out var bug))
                {
                    result.Add(CreateBugSampleData(bug, id));
                }
            }
            return result.ToArray();
        }

        /// <summary>
        /// Create full state snapshot for a single bug.
        /// </summary>
        private BugSampleData CreateBugSampleData(BugVisual bug, int bugId)
        {
            var agent = bug.Agent;
            var movementState = agent.Movement.GetState();

            return new BugSampleData
            {
                swarm_id = SwarmId,
                bug_id = bugId,
                // Core state
                x = agent.Position.X.Value,
                y = agent.Position.Y.Value,
                vx = agent.Velocity.X.Value,
                vy = agent.Velocity.Y.Value,
                rng_state = agent.Rng.State,
                // Behavior state
                behavior = agent.CurrentBehavior ?? "wander",
                target_id = agent.TargetPlayerId ?? "",
                is_alerted = agent.IsAlerted,
                alert_cooldown = agent.AlertCheckCooldown,
                // Movement state
                ticks_until_change = movementState.TicksUntilChange,
                intent_dir_x = movementState.IntentDirX,
                intent_dir_y = movementState.IntentDirY,
                intent_target_x = movementState.IntentTargetX,
                intent_target_y = movementState.IntentTargetY,
                current_dir_x = movementState.CurrentDirX,
                current_dir_y = movementState.CurrentDirY,
                land_ticks = agent.LandTicks, // feed land/hold timer (history-dependent — must ride snapshot)
                hunt_target = agent.HuntTargetBugId, // committed prey bug id (history-dependent — rides snapshot)
                feed_until = agent.FeedUntilTick,    // corpse-eating timer (history-dependent — rides snapshot)
                feed_corpse_id = agent.FeedCorpseId, // the corpse being eaten (history-dependent — rides snapshot)
                // DIAGNOSTIC (re-root investigation)
                spawn_tick = agent.SpawnTick,
                spawn_source = agent.SpawnSource
            };
        }

        /// <summary>
        /// Get positions for all bugs (used for full snapshot response).
        /// </summary>
        public BugSampleData[] GetAllBugPositions()
        {
            var result = new List<BugSampleData>();
            foreach (var kvp in _bugs)
            {
                result.Add(CreateBugSampleData(kvp.Value, kvp.Key));
            }
            return result.ToArray();
        }

        /// <summary>
        /// Phase 2 predation strike: iterate ALIVE bugs as (bugId, fixed-point position) in ASCENDING
        /// bug-id order — deterministic so any client (e.g. a new authority after handoff) selects the
        /// same victim. _bugs is alive-only (RemoveBugsById deletes from it).
        /// </summary>
        public IEnumerable<(int bugId, FixedPoint2 pos)> GetAllBugsAliveSorted()
        {
            foreach (var bugId in _bugs.Keys.OrderBy(id => id))
                yield return (bugId, _bugs[bugId].Agent.Position);
        }

        /// <summary>S2 (authority): collect + CLEAR each bug's pending corpse-consume (a completed feed that rolled
        /// CONSUME). Returns the food ids to report so the server removes those corpses; the roll is deterministic
        /// (every client agrees) but only the authority reports (dedup). null if none this tick.</summary>
        public List<string> DrainCorpseConsumes()
        {
            List<string> ids = null;
            foreach (var bug in _bugs.Values)
            {
                var a = bug.Agent;
                if (!string.IsNullOrEmpty(a.WantsConsumeCorpse))
                {
                    (ids ??= new List<string>()).Add(a.WantsConsumeCorpse);
                    a.WantsConsumeCorpse = "";
                }
            }
            return ids;
        }

        /// <summary>
        /// Like GetAllBugsAliveSorted but yields each bug's RENDERED (on-screen) position — the interpolated
        /// transform, not the deterministic Agent.Position. Player-attack detection tests against THIS so the
        /// hit matches the sprite you see: for a fast surging centipede the rendered sprite lags the sim by
        /// ~1.4 cells, and testing the sim pos fired the "hit" that far off-screen (the phantom). This read is
        /// AUTHORITY-ONLY + sim-inert (feeds only server-bound strike reports; HP is display-only), so a
        /// rendered (non-deterministic) value here can NEVER enter the hash. Falls back to CurrPos if the
        /// transform is missing.
        /// </summary>
        public IEnumerable<(int bugId, FixedPoint2 pos)> GetAllBugsRenderedSorted()
        {
            foreach (var bugId in _bugs.Keys.OrderBy(id => id))
            {
                var b = _bugs[bugId];
                Vector2 v = b.Transform != null ? (Vector2)b.Transform.position : b.CurrPos;
                yield return (bugId, new FixedPoint2 { X = FixedPoint.FromFloat(v.x), Y = FixedPoint.FromFloat(v.y) });
            }
        }


        /// <summary>
        /// Apply snapshot from another client (late joiner or drift correction).
        /// Sets full state including position, velocity, RNG, behavior, and movement state.
        /// NOTE: SwarmManager owns ticks - this method only sets bug state.
        /// </summary>
        /// <param name="positions">Bug state data from snapshot</param>
        public void ApplySnapshot(BugSampleData[] positions)
        {
            int applied = 0;
            int notFound = 0;
            foreach (var data in positions)
            {
                if (_bugs.TryGetValue(data.bug_id, out var bug))
                {
                    var agent = bug.Agent;

                    // Core state
                    agent.Position = new FixedPoint2
                    {
                        X = new FixedPoint { Value = data.x },
                        Y = new FixedPoint { Value = data.y }
                    };
                    agent.Velocity = new FixedPoint2
                    {
                        X = new FixedPoint { Value = data.vx },
                        Y = new FixedPoint { Value = data.vy }
                    };
                    agent.Rng.State = data.rng_state;
                    agent.LandTicks = data.land_ticks; // restore feed land/hold timer (else feeding bugs desync)
                    agent.HuntTargetBugId = data.hunt_target; // restore the committed chase (else hunters desync)
                    agent.FeedUntilTick = data.feed_until;    // restore the corpse-eat timer (else feeders desync)
                    agent.FeedCorpseId = data.feed_corpse_id;
                    agent.SpawnSource = "snapshotApply"; // DIAGNOSTIC: got authoritative per-bug state

                    // Behavior state
                    agent.CurrentBehavior = string.IsNullOrEmpty(data.behavior) ? "wander" : data.behavior;
                    agent.TargetPlayerId = string.IsNullOrEmpty(data.target_id) ? null : data.target_id;
                    agent.IsAlerted = data.is_alerted;
                    agent.AlertCheckCooldown = data.alert_cooldown;

                    // Movement state
                    agent.Movement.SetState(new MovementState
                    {
                        TicksUntilChange = data.ticks_until_change,
                        IntentDirX = data.intent_dir_x,
                        IntentDirY = data.intent_dir_y,
                        IntentTargetX = data.intent_target_x,
                        IntentTargetY = data.intent_target_y,
                        CurrentDirX = data.current_dir_x,
                        CurrentDirY = data.current_dir_y
                    });

                    // Sync visual to new position (also resets interpolation state)
                    bug.SyncPosition();
                    applied++;
                }
                else
                {
                    notFound++;
                }
            }

            // Clear waiting flag - simulation can now proceed
            if (_waitingForSnapshot)
            {
                _waitingForSnapshot = false;
                Debug.Log($"[SwarmVisual] {SwarmId} snapshot received - simulation resumed");
            }

            Debug.Log($"[SwarmVisual] ApplySnapshot to {SwarmId}: {applied} applied, {notFound} not found, _bugs.Count={_bugs.Count}");
        }

        // NOTE: CatchUpTicks() REMOVED - SwarmManager.ReplayToTick() handles catch-up
        // by calling AdvanceOneTick() which calls swarm.SimulateTick(tick, players).

        // NOTE: SimulateSingleTick() REMOVED - superseded by SimulateTick(tick, players)
        // which is called by SwarmManager.AdvanceOneTick().

        /// <summary>
        /// Snap all bug visuals to current agent positions.
        /// Call after replay completes to update visuals to final state.
        /// </summary>
        public void SyncAllBugPositions()
        {
            foreach (var kvp in _bugs)
            {
                kvp.Value.SyncPosition();
            }
        }

        // === Sprite Pooling ===

        private static Transform GetSpriteFromPool()
        {
            while (_spritePool.Count > 0)
            {
                var sprite = _spritePool.Pop();
                if (sprite != null)
                    return sprite;
            }
            return null;
        }

        private static void ReturnSpriteToPool(Transform sprite)
        {
            if (sprite != null)
            {
                sprite.gameObject.SetActive(false);
                sprite.SetParent(null);
                _spritePool.Push(sprite);
            }
        }

        /// <summary>
        /// Clean up when swarm is destroyed.
        /// </summary>
        public void Cleanup()
        {
            foreach (var kvp in _trails)
            {
                if (kvp.Value != null)
                    Destroy(kvp.Value.gameObject); // resets pooled head rotations
            }
            _trails.Clear();
            foreach (var kvp in _bugs)
            {
                ReturnSpriteToPool(kvp.Value.Transform);
            }
            _bugs.Clear();
            _removedIds.Clear();
        }

        private void OnDestroy()
        {
            Cleanup();
        }
    }
}
