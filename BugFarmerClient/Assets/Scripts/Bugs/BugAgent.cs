using System.Collections.Generic;

namespace BugFarmer.Bugs
{
    /// <summary>
    /// Player position data for deterministic targeting.
    /// </summary>
    public struct PlayerTarget
    {
        public string PlayerId;
        public FixedPoint2 Position;
    }

    /// <summary>
    /// Per-bug agent with deterministic simulation.
    /// Each bug has its own RNG, position, velocity, and movement behavior.
    /// Velocity is in units per tick (fixed timestep).
    ///
    /// RNG RULES:
    /// - Spawn-time initialization uses stateful Rng (runs once, no branching issues)
    /// - Simulation logic uses counter-based RNG via RandomInt/RandomFloat helpers
    /// - Counter-based RNG prevents desync from conditional RNG consumption
    /// </summary>
    public class BugAgent
    {
        public int BugId;
        public string SwarmId;
        public string SpeciesId;

        // DIAGNOSTIC ONLY (never hashed): provenance for the determinism re-root investigation —
        // which global tick this client first created/positioned the bug, and via which path.
        public long SpawnTick = -1;
        public string SpawnSource = "?";

        // Spawn-time RNG (stateful, OK because runs once per bug)
        public DeterministicRandom Rng;

        // Counter-based RNG context (set each tick)
        private long _worldSeed;
        private long _currentTick;

        public FixedPoint2 Position;
        public FixedPoint2 Velocity;
        public IBugMovement Movement;

        // Behavior state
        public string CurrentBehavior; // "wander", "flee", "attack", "curious"
        public string TargetPlayerId;

        // Individual predation (S1): the committed prey bug id this predator is pursuing (-1 = none). Deterministic
        // per-bug state — the prey SWARM is the swarm's TargetPreyID; only the individual prey bug id lives here.
        // Rides the snapshot (like TargetPlayerId) so late-joiners keep the same chase.
        public int HuntTargetBugId = -1;
        private const int HuntWindowTicks = 30; // per-bug hunt-entry roll re-rolls every 3s → a rolling subset pursues

        // Individual predation FEED (S2): after killing its prey a predator PAUSES at the fresh corpse and eats it
        // for FeedTicks, then a counter-RNG roll CONSUMES it (WantsConsumeCorpse → the authority reports the
        // removal) or LEAVES it (rots naturally). FeedUntilTick/FeedCorpseId ride the snapshot (like HuntTargetBugId).
        public long FeedUntilTick;             // > currentTick = currently eating a corpse (absolute tick, like _currentTick)
        public string FeedCorpseId;            // the corpse (food id) being eaten
        public string WantsConsumeCorpse = ""; // TRANSIENT (not snapshot): set the tick a feed ends with a CONSUME
                                               // roll; SwarmManager (authority) reads it that tick → reports → removes.
        private const int FeedTicks = 25;      // ~2.5s pause-and-eat at the corpse
        private const float CorpseEatRange = 2.0f; // must be ~on the fresh kill to start eating it

        // CENTIPEDE LUNGE (surge) — client per-bug combat, active when _behavior.AttackStyle == "lunge".
        // Deterministic (fixed-point, no RNG); the position-determining fields ride the snapshot + hash so a
        // late-joiner reconstructs a mid-lunge. Phase: 0 idle | 1 windup (freeze + telegraph) | 2 surge
        // (ballistic charge past the aim) | 3 recover (back off, then cooldown).
        public int SurgePhase;
        public long SurgeUntilTick;            // the current phase ends at this tick
        public long SurgeCooldownUntil;        // no new windup before this tick
        public int WindupCellX, WindupCellY;   // player cell at windup START (the velocity-lead sample; FixedPoint.Value)
        public int SurgeHeadingX, SurgeHeadingY; // locked unit heading during the charge (FixedPoint.Value)
        public int SurgeDistLeft;              // FixedPoint.Value: charge distance remaining (aim dist + overshoot)
        public string SurgeTargetId;           // player locked at windup (snapshot, NOT hashed — like FeedCorpseId)

        // Cached lunge params (from the attack.lunge profile; set in the ctor only for a "lunge" species).
        private int _windupTicks, _surgeCooldownTicks, _surgeMaxTicks;
        private const int SurgeRecoverTicks = 20;
        private FixedPoint _triggerRangeSqr;
        private FixedPoint _surgeSpeed;
        private FixedPoint _overshoot;
        private FixedPoint _lead;
        // The client has no per-species base_speed (movement speeds are hardcoded per style), so the surge uses a
        // uniform centipede base × the parsed surge_speed_mult. All tiers land < 1 cell/tick; ResolveSwept covers any excess.
        private static readonly FixedPoint CentBaseSpeed = FixedPoint.FromFloat(0.19f);
        private static readonly FixedPoint SurgeRecoverSpeed = FixedPoint.FromFloat(0.16f);

        // Alert state (stochastic reaction)
        private bool _isAlerted;
        private int _alertCheckCooldown;

        // Public accessors for sync
        public bool IsAlerted { get => _isAlerted; set => _isAlerted = value; }
        public int AlertCheckCooldown { get => _alertCheckCooldown; set => _alertCheckCooldown = value; }

        // Cached species behavior
        private SpeciesBehavior _behavior;
        private FixedPoint _reactionRadiusSqr;
        private FixedPoint _wanderRadiusSqr;

        // ATTACK-movement (player_reaction "attack") — the orbit-and-dive. Cached from _behavior with defaults.
        // Deterministic by construction: the swoop is a pure function of tick + bug-id (no RNG, no extra state),
        // the target is the deterministic player CELL, and the motion is fixed-point — so all clients agree.
        private FixedPoint _attackHoverRadiusSqr; // standoff² the hovering (non-diving) cloud keeps off the player
        private int _divePeriodTicks;             // each bug's swoop cycle length
        private int _diveTicks;                   // how long a swoop lasts, at the front of the cycle
        private const int DivePhaseStep = 13;     // per-bug phase offset (staggers who's diving; ~coprime w/ period)
        // The swoop travels this much faster than the twitchy hover dash, so a dive reads as a COMMITTED attack
        // (faster than the player's walk of 5 c/s) rather than a slow drift. Fixed-point → deterministic.
        private static readonly FixedPoint DiveSpeedMult = FixedPoint.FromFloat(2.0f);

        // Alert chance per check (3/10 = 30%). Integer ratio to keep the roll float-free.
        private const int AlertChanceNumerator = 3;
        private const int AlertChanceDenominator = 10;

        public BugAgent(long worldSeed, string swarmId, string speciesId, int bugId, FixedPoint2 startPosition)
        {
            BugId = bugId;
            SwarmId = swarmId;
            SpeciesId = speciesId;

            // Store world seed for counter-based RNG during simulation
            _worldSeed = worldSeed;
            _currentTick = 0;

            // Stateful RNG for spawn-time initialization only
            Rng = DeterministicRandom.ForBug(worldSeed, swarmId, bugId);
            Position = startPosition;
            Velocity = FixedPoint2.Zero;
            Movement = MovementFactory.CreateMovement(speciesId);

            CurrentBehavior = "wander";
            TargetPlayerId = null;

            _isAlerted = false;
            _alertCheckCooldown = Rng.RangeInt(1, 10); // Stagger initial checks (spawn-time, stateful OK)

            _behavior = MovementFactory.GetBehavior(speciesId);
            _reactionRadiusSqr = FixedPoint.FromFloat(_behavior.ReactionRadius * _behavior.ReactionRadius);
            _wanderRadiusSqr = FixedPoint.FromFloat(_behavior.WanderRadius * _behavior.WanderRadius);

            // Attack-movement params (defaults when unset): standoff 2.5 cells, a 5.5s dive cycle, 1.2s swoops.
            float standoff = _behavior.Standoff > 0f ? _behavior.Standoff : 2.5f;
            _attackHoverRadiusSqr = FixedPoint.FromFloat(standoff * standoff);
            _divePeriodTicks = _behavior.DivePeriodTicks > 0 ? _behavior.DivePeriodTicks : 55;
            _diveTicks = _behavior.DiveTicks > 0 ? _behavior.DiveTicks : 12;
            if (_diveTicks >= _divePeriodTicks) _diveTicks = _divePeriodTicks - 1; // always leave a hover phase

            // Cache the LUNGE (surge) params for a "lunge" species (centipedes) — read once here, like the dive knobs.
            var lungeAtk = Data.EntityDatabase.GetSpecies(speciesId)?.Attack;
            if (lungeAtk != null && lungeAtk.Style == "lunge")
            {
                _windupTicks = lungeAtk.TelegraphSecs > 0f ? (int)(lungeAtk.TelegraphSecs * 10f) : 8;
                _surgeCooldownTicks = lungeAtk.CooldownSecs > 0f ? (int)(lungeAtk.CooldownSecs * 10f) : 50;
                _surgeMaxTicks = lungeAtk.SurgeMaxTicks > 0 ? lungeAtk.SurgeMaxTicks : 25;
                float trig = lungeAtk.TriggerRange > 0f ? lungeAtk.TriggerRange : 5f;
                _triggerRangeSqr = FixedPoint.FromFloat(trig * trig);
                _surgeSpeed = CentBaseSpeed * FixedPoint.FromFloat(lungeAtk.SurgeSpeedMult > 0f ? lungeAtk.SurgeSpeedMult : 4.8f);
                _overshoot = FixedPoint.FromFloat(lungeAtk.Overshoot > 0f ? lungeAtk.Overshoot : 3.5f);
                _lead = FixedPoint.FromFloat(lungeAtk.Lead > 0f ? lungeAtk.Lead : 0.8f);
            }
        }

        /// <summary>
        /// Counter-based random int for simulation logic.
        /// Same inputs always produce same output - prevents desync from conditional branches.
        /// </summary>
        public int RandomInt(int purposeId, int min, int max)
        {
            return CounterRng.RangeInt(_worldSeed, SwarmId, BugId, _currentTick, purposeId, min, max);
        }


        /// <summary>
        /// Counter-based random float [0,1) for simulation logic.
        /// Same inputs always produce same output - prevents desync from conditional branches.
        /// </summary>
        public float RandomFloat(int purposeId)
        {
            return CounterRng.Float(_worldSeed, SwarmId, BugId, _currentTick, purposeId);
        }

        // === Feed-at-food visual (deterministic) ===
        private int _landTicks; // >0 = landed (paused) on a food source
        // Per-bug feed land/hold timer. History-dependent, so it MUST ride the snapshot (BugSampleData.land_ticks)
        // or a bug mid-landing at snapshot re-roots with 0 and desyncs. See architecture_swarm_sync.md.
        public int LandTicks { get => _landTicks; set => _landTicks = value; }

        private const float FeedVisualRadius = 2.5f; // centre within this of food => bugs engage
        private static readonly int LandDistSqr =
            (FixedPoint.FromFloat(0.35f) * FixedPoint.FromFloat(0.35f)).Value;

        // Per-bug feeding participation re-rolls every 8s window, so bugs drift in and out of
        // feeding INDIVIDUALLY — the swarm never flips between modes as one block.
        private const long ParticipationWindowTicks = 80;
        private static readonly FixedPoint ApproachRadiusSqr =
            FixedPoint.FromFloat(0.4f * 0.4f);
        // Non-landing bugs HOVER in a tight halo around the food (instead of the ±8-cell
        // swarm wander) — this is what makes "buzzing around the fruit/bin" visible.
        private static readonly FixedPoint HoverRadiusSqr =
            FixedPoint.FromFloat(1.2f * 1.2f);

        /// <summary>
        /// If the swarm centre is at a food source (deterministic event-driven registry),
        /// SOME bugs (per-bug per-window roll) approach it with their normal buzzy Brownian
        /// motion pulled toward a personal landing point, land for a few ticks, and resume;
        /// the rest keep wandering. Returns true when feeding owns this tick's movement.
        /// </summary>
        private bool TryFeedAtFood(FixedPoint2 swarmCenter)
        {
            var im = InfluenceManager.Instance;
            if (im == null) return false;

            if (!im.TryGetNearestFood(swarmCenter, FeedVisualRadius, out var foodPos))
            {
                _landTicks = 0;
                return false;
            }

            // INDIVIDUAL participation: each bug rolls per 8s window (counter-RNG on the
            // window index — deterministic on every client). ~60% LAND in any window; the
            // others don't land but HOVER in a tight halo around the food — the whole swarm
            // visibly condenses onto the fruit/bin ("buzzing"), staggered and alive.
            long window = _currentTick / ParticipationWindowTicks;
            bool joining = CounterRng.Chance(_worldSeed, SwarmId, BugId, window, RngPurpose.Participate, 3, 5);
            if (!joining)
            {
                _landTicks = 0;
                Movement.UpdateMovement(this, foodPos, HoverRadiusSqr);
                return true;
            }

            if (_landTicks > 0)
            {
                _landTicks--;
                Velocity = default; // landed: hold position
                return true;
            }

            // Per-bug landing point: a stable ring offset derived from BugId (no RNG burn) —
            // bugs encircle the fruit/bin instead of stacking on one pixel.
            var dir = FixedPointMath.DirectionFromIndex((BugId * 37) & (FixedPointMath.TableSize - 1));
            var ring = FixedPoint.FromFloat(0.3f);
            var target = new FixedPoint2(foodPos.X + dir.X * ring, foodPos.Y + dir.Y * ring);

            if (Position.SqrDistanceTo(target).Value <= LandDistSqr)
            {
                _landTicks = RandomInt(RngPurpose.Land, 10, 31); // land 1-3 seconds
                Velocity = default;
            }
            else
            {
                // BUZZY approach: the bug's normal Brownian movement with its "home" set to
                // the landing point and a tiny radius — identical visual character to regular
                // wandering (random jinks + gentle pull), just drifting onto the fruit,
                // instead of a robotic straight-line glide.
                Movement.UpdateMovement(this, target, ApproachRadiusSqr);
            }
            return true;
        }

        /// <summary>
        /// Simulate one tick of bug behavior and movement.
        /// </summary>
        /// <param name="swarmCenter">Current swarm center position</param>
        /// <param name="players">Player positions (from InfluenceManager)</param>
        /// <param name="currentTick">Current simulation tick for counter-based RNG</param>
        /// <param name="preyBugs">When this bug's swarm is hunting, the target prey swarm's (bugId, position) as of
        /// last tick — deterministic on every client. null = not hunting. Drives the individual HUNT pursuit.</param>
        public void SimulateTick(FixedPoint2 swarmCenter, List<PlayerTarget> players, long currentTick,
                                 IReadOnlyList<(int bugId, FixedPoint2 pos)> preyBugs = null)
        {
            // Store tick for counter-based RNG calls
            _currentTick = currentTick;

            // 1. Update behavior based on nearby players (stochastic alert). SKIP the re-eval while a centipede
            //    LUNGE is committed (SurgePhase != 0): the surge owns the tick, so CurrentBehavior stays "attack"
            //    and the switch below routes back into the surge — a player leaving range mid-surge can't abandon it.
            if (!(_behavior.AttackStyle == "lunge" && SurgePhase != 0))
                UpdateBehavior(players);

            // 2. Apply movement based on current behavior
            switch (CurrentBehavior)
            {
                case "attack":
                    // Lungers (centipedes) run the per-bug surge machine; contact attackers keep the orbit-and-dive.
                    if (_behavior.AttackStyle == "lunge")
                        CentipedeSurge(players);
                    else if (TargetPlayerId != null)
                    {
                        var targetPos = GetPlayerPosition(players, TargetPlayerId);
                        if (targetPos.HasValue)
                            AttackMove(targetPos.Value);
                        else
                            Movement.UpdateMovement(this, swarmCenter, _wanderRadiusSqr);
                    }
                    break;

                case "flee":
                    if (TargetPlayerId != null)
                    {
                        var fleeFrom = GetPlayerPosition(players, TargetPlayerId);
                        if (fleeFrom.HasValue)
                            Movement.MoveAwayFrom(this, fleeFrom.Value);
                        else
                            Movement.UpdateMovement(this, swarmCenter, _wanderRadiusSqr);
                    }
                    break;

                case "curious":
                    if (TargetPlayerId != null)
                    {
                        var curiousPos = GetPlayerPosition(players, TargetPlayerId);
                        if (curiousPos.HasValue)
                            Movement.MoveTowardSlow(this, curiousPos.Value);
                        else
                            Movement.UpdateMovement(this, swarmCenter, _wanderRadiusSqr);
                    }
                    break;

                default: // "wander" or "ignore"
                    // INDIVIDUAL PREDATION FEED (S2): if I'm eating a fresh kill's corpse, PAUSE on it and eat —
                    // priority over re-hunting so the kill→eat beat reads on screen; ends with a consume-or-leave roll.
                    if (!_behavior.SkipCollision && FeedUntilTick > 0 && HandleFeed())
                        break;
                    // INDIVIDUAL PREDATION (S1): when this swarm is hunting (preyBugs present) and this bug is
                    // committed to a chase OR its per-window stagger roll says go, PURSUE a specific prey bug —
                    // deterministic, so every client sees the SAME wasp chase the SAME fly. Center-riding crawlers
                    // (SkipCollision, e.g. centipedes) keep their own server-driven surge; fliers/walkers pursue.
                    if (!_behavior.SkipCollision && preyBugs != null && preyBugs.Count > 0
                        && (HuntTargetBugId >= 0 || ShouldHunt()) && TryHuntMove(preyBugs))
                        break;
                    // FEEDING VISUAL: when the swarm centre is at a registered food source,
                    // bugs approach it, LAND (pause), then resume — driven purely by
                    // deterministic inputs (event-driven food registry + derived centre +
                    // counter-RNG + a per-bug-id ring offset), so all clients stay identical.
                    // Crawling individuals skip the fly hover-land feed dance — the
                    // centipede head must ride the center verbatim (it still EATS via
                    // the server meters; this is display only).
                    if (_behavior.SkipCollision || !TryFeedAtFood(swarmCenter))
                        Movement.UpdateMovement(this, swarmCenter, _wanderRadiusSqr);
                    break;
            }

            // 3. Apply velocity, resolving collision against blocks_bugs cells so individual bugs can't
            //    pass through walls/fences. Deterministic: integer cell lookups + slide X-then-Y.
            //    All clients run this identically, so the per-tick state-hash stays in agreement.
            //    SPECIES-AWARE (§14, both collision sites): flies_over_fences skips the
            //    occupant branch (ground never blocks bugs — water stops people only);
            //    crawling individuals skip Resolve entirely (the head rides the
            //    server-clamped center verbatim).
            var proposed = new FixedPoint2(
                Position.X + Velocity.X,
                Position.Y + Velocity.Y
            );
            Position = _behavior.SkipCollision
                ? proposed
                : (SurgePhase == 2
                    // The fast charge sub-steps its collision so it clamps at a fence instead of tunneling.
                    ? BugCollision.ResolveSwept(Position, proposed, _behavior.FliesOverFences)
                    : BugCollision.Resolve(Position, proposed, _behavior.FliesOverFences));
        }

        /// <summary>
        /// ATTACK movement — "solo divers within a bigger swarm." Most of the cycle the bug HOVERS in a menacing
        /// cloud a standoff distance off the player (its natural darting hover, pulled toward the player instead of
        /// the swarm centre); during its own slice of a repeating cycle it SWOOPS straight in at dash speed, then
        /// the cycle returns it to the hover (which peels it back out). The dive slice is phase-offset per bug-id,
        /// so ~1-2 of the swarm dive at any instant — staggered, never a lockstep pile-on.
        ///
        /// DETERMINISM: the swoop/hover choice is a pure function of (currentTick, bugId) — no RNG, no per-bug
        /// state beyond Position (already synced) — the target is the deterministic player CELL, and MoveToward/
        /// UpdateMovement are the existing fixed-point + counter-RNG primitives. So every client computes the
        /// identical Agent.Position, exactly like the flee/curious behaviours that already ship.
        /// </summary>
        private void AttackMove(FixedPoint2 target)
        {
            long phase = (_currentTick + (long)BugId * DivePhaseStep) % _divePeriodTicks;
            if (phase < _diveTicks)
            {
                Movement.MoveToward(this, target);                     // SWOOP straight in...
                Velocity = new FixedPoint2(Velocity.X * DiveSpeedMult, // ...but faster than the hover — a committed
                                           Velocity.Y * DiveSpeedMult); //    dive (beats the player's walk speed)
            }
            else
                Movement.UpdateMovement(this, target, _attackHoverRadiusSqr); // HOVER around the player at standoff
        }

        /// <summary>
        /// CENTIPEDE LUNGE state machine (client-authority, deterministic — fixed-point, no RNG). Aims at the
        /// deterministic player CELL (the quantized GetDeterministicPlayerTargets). Owns the tick while active. The
        /// DAMAGE is detected separately by SwarmManager.RunLungeConnect against the rendered sprite; this only
        /// drives the motion. Phase: 0 idle (approach + trigger) | 1 windup (freeze + telegraph) | 2 surge (charge
        /// past the aim) | 3 recover (back off, then arm the cooldown).
        /// </summary>
        private void CentipedeSurge(List<PlayerTarget> players)
        {
            switch (SurgePhase)
            {
                case 1: // windup: FREEZE (the telegraph); at the end, launch
                    Velocity = FixedPoint2.Zero;
                    if (_currentTick >= SurgeUntilTick)
                        LaunchSurge(players);
                    return;

                case 2: // surge: ballistic charge along the locked heading until the overshoot distance is spent
                {
                    var heading = new FixedPoint2(new FixedPoint { Value = SurgeHeadingX }, new FixedPoint { Value = SurgeHeadingY });
                    Velocity = new FixedPoint2(heading.X * _surgeSpeed, heading.Y * _surgeSpeed);
                    SurgeDistLeft -= _surgeSpeed.Value;
                    if (SurgeDistLeft <= 0 || _currentTick >= SurgeUntilTick) // dist spent (or the safety cap)
                    {
                        SurgePhase = 3;
                        SurgeUntilTick = _currentTick + SurgeRecoverTicks;
                    }
                    return;
                }

                case 3: // recover: back off along the reverse heading, then idle on the cooldown
                {
                    var heading = new FixedPoint2(new FixedPoint { Value = SurgeHeadingX }, new FixedPoint { Value = SurgeHeadingY });
                    Velocity = new FixedPoint2(-(heading.X * SurgeRecoverSpeed), -(heading.Y * SurgeRecoverSpeed));
                    if (_currentTick >= SurgeUntilTick)
                    {
                        SurgePhase = 0;
                        SurgeCooldownUntil = _currentTick + _surgeCooldownTicks;
                    }
                    return;
                }

                default: // 0 idle: approach the player; at trigger range + off cooldown, begin the windup
                {
                    var target = GetPlayerPosition(players, TargetPlayerId);
                    if (!target.HasValue) { Velocity = FixedPoint2.Zero; return; }
                    var toPlayer = target.Value - Position;
                    if (_currentTick >= SurgeCooldownUntil && toPlayer.SqrMagnitude() <= _triggerRangeSqr)
                    {
                        SurgePhase = 1;
                        SurgeUntilTick = _currentTick + _windupTicks;
                        SurgeTargetId = TargetPlayerId;
                        WindupCellX = target.Value.X.Value;   // sample the player cell for the launch-time velocity lead
                        WindupCellY = target.Value.Y.Value;
                        Velocity = FixedPoint2.Zero;
                    }
                    else
                    {
                        Movement.MoveToward(this, target.Value); // close in at chase speed until in trigger range
                    }
                    return;
                }
            }
        }

        /// <summary>Windup → surge: aim at the player's cell plus a velocity lead sampled over the windup, lock a
        /// unit heading, set the charge distance (aim + overshoot). Target gone during windup → flinch into recover.
        /// Pure fixed-point (Normalize/Sqrt — no Atan2), so every client computes the identical charge.</summary>
        private void LaunchSurge(List<PlayerTarget> players)
        {
            var t = GetPlayerPosition(players, SurgeTargetId);
            if (!t.HasValue)
            {
                SurgePhase = 3;
                SurgeUntilTick = _currentTick + SurgeRecoverTicks;
                Velocity = FixedPoint2.Zero;
                return;
            }
            var launch = t.Value;
            var windupCell = new FixedPoint2(new FixedPoint { Value = WindupCellX }, new FixedPoint { Value = WindupCellY });
            // Player velocity over the windup (cells/tick) → lead by flight-time × the lead fraction.
            var vel = (launch - windupCell) / FixedPoint.FromInt(_windupTicks);
            var flight = FixedPointMath.Sqrt((launch - Position).SqrMagnitude()) / _surgeSpeed; // ticks
            var aim = launch + vel * (flight * _lead);
            var toAim = aim - Position;
            var heading = FixedPointMath.Normalize(toAim);
            SurgeHeadingX = heading.X.Value;
            SurgeHeadingY = heading.Y.Value;
            SurgeDistLeft = FixedPointMath.Sqrt(toAim.SqrMagnitude()).Value + _overshoot.Value;
            SurgePhase = 2;
            SurgeUntilTick = _currentTick + _surgeMaxTicks; // safety cap
        }

        /// <summary>Per-bug hunt-ENTRY stagger: ~1/3 of the swarm rolls in per window (re-rolls every
        /// HuntWindowTicks → a rolling subset pursues, not the whole cloud). Deterministic (counter-RNG on the
        /// window). A committed hunter (HuntTargetBugId set) keeps going regardless — this only gates entry.</summary>
        private bool ShouldHunt()
        {
            long window = _currentTick / HuntWindowTicks;
            return CounterRng.Chance(_worldSeed, SwarmId, BugId, window, RngPurpose.Hunt, 1, 3);
        }

        /// <summary>Individual pursuit: steer toward the COMMITTED prey bug (resolve its current position from
        /// preyBugs) — or, on a fresh entry, commit the NEAREST prey bug and steer to it. Returns false if the
        /// committed target is gone (drop the chase → caller wanders; re-entry re-gated next tick) or no prey
        /// exists. Deterministic: fixed-point distances + ascending-bug-id tie-break, so every client's wasp
        /// chases the same fly. Steers at the movement's dash speed (MoveToward) so it out-paces a wandering fly.</summary>
        private bool TryHuntMove(IReadOnlyList<(int bugId, FixedPoint2 pos)> preyBugs)
        {
            // 1. Committed target still alive? Pursue it.
            if (HuntTargetBugId >= 0)
            {
                for (int i = 0; i < preyBugs.Count; i++)
                    if (preyBugs[i].bugId == HuntTargetBugId) { Movement.MoveToward(this, preyBugs[i].pos); return true; }
                HuntTargetBugId = -1; // target died/gone — drop the chase (re-entry re-gated by ShouldHunt)
                // S2: if it was KILLED, a fresh corpse dropped right where I am — start eating it (pause + feed).
                var im = InfluenceManager.Instance;
                if (im != null && im.TryGetNearestFoodId(Position, CorpseEatRange, out var cid, out var cpos))
                {
                    FeedCorpseId = cid;
                    FeedUntilTick = _currentTick + FeedTicks;
                    Movement.MoveTowardSlow(this, cpos); // head onto the corpse
                    return true;
                }
                return false; // it fled (no corpse) → wander / re-hunt
            }
            // 2. Fresh entry (ShouldHunt already rolled true): commit the NEAREST prey bug.
            int best = -1; long bestSqr = long.MaxValue; FixedPoint2 bestPos = default;
            for (int i = 0; i < preyBugs.Count; i++)
            {
                long d = Position.SqrDistanceTo(preyBugs[i].pos).Value;
                int bid = preyBugs[i].bugId;
                if (d < bestSqr || (d == bestSqr && (best < 0 || bid < best)))
                { bestSqr = d; best = bid; bestPos = preyBugs[i].pos; }
            }
            if (best < 0) return false;
            HuntTargetBugId = best;
            Movement.MoveToward(this, bestPos);
            return true;
        }

        /// <summary>S2 — eat the fresh kill's corpse: HOLD on it for FeedTicks, then a counter-RNG roll CONSUMES it
        /// (WantsConsumeCorpse → the authority reports the removal so it vanishes) or LEAVES it (rots naturally).
        /// Returns true while eating (owns movement). Deterministic (counter-RNG on the tick); if the corpse
        /// vanishes mid-feed (consumed/rotted) the feed ends cleanly.</summary>
        private bool HandleFeed()
        {
            var im = InfluenceManager.Instance;
            if (_currentTick < FeedUntilTick)
            {
                if (im != null && im.TryGetFoodPos(FeedCorpseId, out var pos)) { Movement.MoveTowardSlow(this, pos); return true; }
                FeedUntilTick = 0; FeedCorpseId = null; return false; // corpse gone → stop
            }
            // feed ENDED this tick: consume-or-leave roll (~1/4 LEAVE).
            FeedUntilTick = 0;
            bool leave = CounterRng.Chance(_worldSeed, SwarmId, BugId, _currentTick, RngPurpose.LeaveCorpse, 1, 4);
            if (!leave) WantsConsumeCorpse = FeedCorpseId; // the AUTHORITY reports this → server removes the corpse
            FeedCorpseId = null;
            return false; // done → fall through to hunt/wander (moves off the corpse)
        }

        /// <summary>
        /// Update behavior with stochastic alert system.
        /// Bugs don't all react instantly - they notice players over time.
        /// </summary>
        private void UpdateBehavior(List<PlayerTarget> players)
        {
            // Peaceful OBSERVATION zone (from WorldInit): suppress the cosmetic attack/flee reaction entirely
            // so bugs fully ignore the player (paired with the server peace gates). All clients read the same
            // flag from WorldInit → deterministic. (Instance null in the headless harness → normal behavior.)
            if (_behavior.PlayerReaction == "ignore" || _behavior.ReactionRadius <= 0
                || (WorldSeedProvider.Instance != null && WorldSeedProvider.Instance.Peaceful))
            {
                CurrentBehavior = "wander";
                TargetPlayerId = null;
                return;
            }

            _alertCheckCooldown--;

            // If alerted and not time to re-check, keep current behavior
            if (_alertCheckCooldown > 0 && _isAlerted && TargetPlayerId != null)
            {
                // Verify target still in range
                var targetPos = GetPlayerPosition(players, TargetPlayerId);
                if (targetPos.HasValue)
                {
                    var distSqr = Position.SqrDistanceTo(targetPos.Value);
                    if (distSqr <= _reactionRadiusSqr)
                        return; // Still tracking target
                }
                // Target left range - become un-alerted
                _isAlerted = false;
                TargetPlayerId = null;
                CurrentBehavior = "wander";
                return;
            }

            // Time to check for players
            if (_alertCheckCooldown <= 0)
            {
                // Counter-based RNG for cooldown - always evaluates regardless of branch
                _alertCheckCooldown = RandomInt(RngPurpose.Cooldown, 5, 15);

                // Find nearest player in range
                string nearestId = null;
                FixedPoint nearestDistSqr = _reactionRadiusSqr;

                foreach (var player in players)
                {
                    var distSqr = Position.SqrDistanceTo(player.Position);
                    if (distSqr < nearestDistSqr)
                    {
                        nearestDistSqr = distSqr;
                        nearestId = player.PlayerId;
                    }
                    else if (distSqr == nearestDistSqr && nearestId != null)
                    {
                        // Tie-breaker: lexicographically smaller ID
                        if (string.CompareOrdinal(player.PlayerId, nearestId) < 0)
                            nearestId = player.PlayerId;
                    }
                }

                // Integer counter-based roll for alert - ALWAYS compute, use conditionally.
                // This prevents desync: same hash regardless of whether we're in the "if (!_isAlerted)"
                // branch, and the integer comparison is bit-identical across platforms.
                bool alertNotice = CounterRng.Chance(_worldSeed, SwarmId, BugId, _currentTick,
                    RngPurpose.Alert, AlertChanceNumerator, AlertChanceDenominator);

                if (nearestId != null)
                {
                    // Player in range - roll chance to notice
                    if (!_isAlerted)
                    {
                        if (alertNotice)
                        {
                            _isAlerted = true;
                            TargetPlayerId = nearestId;
                            CurrentBehavior = _behavior.PlayerReaction;
                        }
                        // else: didn't notice yet, keep wandering
                    }
                    else
                    {
                        // Already alerted - update target to nearest
                        TargetPlayerId = nearestId;
                        CurrentBehavior = _behavior.PlayerReaction;
                    }
                }
                else
                {
                    // No player in range - become un-alerted
                    _isAlerted = false;
                    TargetPlayerId = null;
                    CurrentBehavior = "wander";
                }
            }
        }

        private static FixedPoint2? GetPlayerPosition(List<PlayerTarget> players, string playerId)
        {
            foreach (var player in players)
            {
                if (player.PlayerId == playerId)
                    return player.Position;
            }
            return null;
        }

        /// <summary>
        /// Get world position as Vector2 for rendering.
        /// </summary>
        public UnityEngine.Vector2 WorldPosition => Position.ToVector2();
    }
}
