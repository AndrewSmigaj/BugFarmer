I'll research boids/flocking thoroughly. Let me start by loading the web tools and firing off the canonical searches and fetches in parallel.

---

Let me fire off the searches and canonical fetches in parallel.

---

Now let me deep-read the strong technical pages: Van Hunter Adams (Cornell), Ben Eater, Nature of Code, and the games-focused pages (jdxdev RTS boids, Arnauld's spatial grid blog).

---

I have strong coverage. Let me fetch one more games/performance page for spatial-grid depth to solidify the performance section.

---

I fetched and deep-read 6 distinct pages plus one search-result synthesis. Here are the structured findings.

---

# BOIDS / FLOCKING — Research Findings

Sources actually fetched and read:
- **[A] red3d.com/cwr/boids/** — Craig Reynolds' own boids page (canonical origin)
- **[B] red3d.com/cwr/steer/** — Reynolds' "Steering Behaviors For Autonomous Characters"
- **[C] vanhunteradams.com/Pico/Animal_Movement/Boids-algorithm.html** — Van Hunter Adams (Cornell), the most algorithmically explicit page
- **[D] eater.net/boids** — Ben Eater's interactive boids page
- **[E] natureofcode.com/autonomous-agents/** — Daniel Shiffman, "Nature of Code," steering-force formulation
- **[F] jdxdev.com/blog/2021/03/19/boids-for-rts/** — boids adapted for RTS / goal-directed game units
- **[G] arnauld-alex.com/…spatial-grids-and-zero-copy-optimization** — performance engineering for boids at scale

---

## 1. THE THREE RULES (exact definitions + how each becomes a force)

Reynolds' canonical wording [A]:
- **Separation** — "steer to avoid crowding local flockmates."
- **Alignment** — "steer towards the average heading of local flockmates."
- **Cohesion** — "steer to move toward the average position of local flockmates."

These are three independent local rules; the global flock behavior is *emergent* — "complex global behavior arising from the interaction of simple local rules" [A]. No boid knows about the flock as a whole.

### Two flavors of the math

There are two equivalent ways games compute these, and it's worth knowing both because your codebase could use either:

**(i) The "velocity-nudge" formulation** (Van Hunter Adams, [C]) — simplest, no explicit steering-vector normalization. Each rule directly increments velocity by a small factor. Uses **two radii**: a small `protected range` (separation only) and a larger `visual range` (alignment + cohesion).

- **Separation** — sum displacement away from each too-close neighbor, scaled by `avoidfactor` (~0.05):
  ```
  close_dx += boid.x - other.x        (for each neighbor within PROTECTED range)
  close_dy += boid.y - other.y
  boid.vx  += close_dx * avoidfactor
  boid.vy  += close_dy * avoidfactor
  ```
  Note: NOT normalized/distance-weighted here — the accumulation of raw displacement naturally pushes harder when more/closer neighbors crowd in.

- **Alignment** — steer toward the average velocity of visual-range neighbors, scaled by `matchingfactor` (~0.05):
  ```
  xvel_avg = Σ(other.vx)/N ;  yvel_avg = Σ(other.vy)/N
  boid.vx += (xvel_avg - boid.vx) * matchingfactor
  boid.vy += (yvel_avg - boid.vy) * matchingfactor
  ```

- **Cohesion** — steer toward the average position (center of mass) of visual-range neighbors, scaled by `centeringfactor` (~0.0005 — deliberately much weaker):
  ```
  xpos_avg = Σ(other.x)/N ;  ypos_avg = Σ(other.y)/N
  boid.vx += (xpos_avg - boid.x) * centeringfactor
  boid.vy += (ypos_avg - boid.y) * centeringfactor
  ```
  The centering factor being ~100× smaller than the others is important: cohesion is a weak long-range pull; separation/alignment are strong short-range corrections. [C]

**(ii) The steering-force formulation** (Shiffman/Reynolds, [E][B]) — each rule produces a *desired velocity*, then `steer = desired − velocity` (see §2). Separation = average of the (away) flee vectors from close neighbors, set to max speed; Alignment = average neighbor velocity set to max speed; Cohesion = *seek* toward average neighbor position. Each is then limited to `maxforce`.

### Combining — weighted sum

Both formulations combine the three by **weighted sum of forces** [E]. Shiffman's defaults:
```
separate.mult(1.5);   // separation weighted highest
align.mult(1.0);
cohere.mult(1.0);
applyForce(separate); applyForce(align); applyForce(cohere);
```
Separation is typically weighted highest to prevent overlap. Weights are the primary tuning knob for the "feel" of the swarm. [E]

---

## 2. THE STEERING MODEL (Reynolds' general framework, [B][E])

Steering behaviors sit on top of a **simple vehicle model**: mass, max_force, max_speed. A behavior outputs a steering force; the physics integrates it. [B]

**The one core formula** [E][B]:
```
steering = desired_velocity − current_velocity
```
This is the "error" between where the agent wants to go and where it's actually going — steering corrects toward the desired vector rather than snapping to it, which is what produces smooth, life-like turns.

**Seek** (the atomic behavior) [E]:
```
desired = (target − position), setMag(maxspeed)   // full-speed straight at target
steer   = desired − velocity
steer.limit(maxforce)                             // TRUNCATE to max force
applyForce(steer)
```

**Force limiting / truncation** is essential [B][E]: the steering vector is clamped to `maxforce` (turning/acceleration authority), and after integration the velocity is clamped to `maxspeed`. Limited force = limited turn rate = agents can't instantly reverse, which is what makes motion read as physical.

**Integration loop** [E]:
```
velocity += acceleration
velocity.limit(maxspeed)
position += velocity
acceleration = 0            // forces reset each frame
```
(The nudge formulation [C] folds this together and clamps speed at the end with an explicit min AND max — see §speed below.)

Related behaviors in the same framework [B]: Flee, Pursue/Evade (predictive seek/flee), **Arrival** (seek that decelerates inside a slowing radius), Obstacle Avoidance, Wall/Path Following. Flocking is just separation+alignment+cohesion composed via the same machinery.

**Speed clamping** — the nudge version [C] enforces BOTH bounds (keeps boids perpetually moving, never frozen):
```
speed = sqrt(vx² + vy²)
if speed > maxspeed: v = v/speed * maxspeed
if speed < minspeed: v = v/speed * minspeed   // e.g. minspeed=3, maxspeed=6 px/frame
```
Adams notes the `sqrt` is the slow step and suggests the alpha-max-plus-beta-min approximation for fixed-point/embedded targets. [C]

---

## 3. NEIGHBORHOOD / LOCAL PERCEPTION

The neighborhood is the core scalability + realism device. Reynolds [A]: the neighborhood is "characterized by a **distance** (measured from the center of the boid) and an **angle**, measured from the boid's direction of flight," and "flockmates outside this local neighborhood are ignored."

- **Distance (perception radius):** only boids within range influence you. Adams [C] splits this into two radii — a small **protected range** (separation) and a larger **visual range** (alignment + cohesion). This lets a boid align with the broad group while still hard-avoiding immediate collisions.
- **Angle (field of view):** neighbors behind the boid (outside the view cone) are ignored — a boid doesn't react to what it can't "see." [A]
- **Why local matters:** Ben Eater [D] frames it biologically — "Real animals can't see the entire flock; they can only see the other animals around them." Locality is *why the emergent behavior looks alive* (waves ripple through the flock rather than the whole group turning as one unit), AND *why it's cheap* (each boid touches only O(neighbors), not O(all)).

---

## 4. PERFORMANCE

**Naive cost is O(n²)** [A][C][G]: every boid checks every other boid for all three rules. "Doubling your boids quadruples your cost" [G]. Reynolds himself notes the straightforward implementation "has an asymptotic complexity of O(n²)." [A]

**Spatial partitioning → near O(n)** [A][C][G]:
- Reynolds: spatial data structures reduce it "down to nearly O(n)," enabling large flocks in real time. [A]
- **Uniform grid / spatial hash:** divide space into cells, bucket each boid by position, and only test boids in the same cell + adjacent cells. [G][search]
- **Cell sizing rule:** set cell width ≈ the perception (search) radius. If cell width = the interaction radius, in 2D a boid only needs to scan its own cell plus 8 surrounding cells; with cell width = 2× the max search radius, only ~4 neighbor cells need checking. Sizing cells to the radius is what guarantees all real neighbors fall in the scanned cells. [search][G]
- **Flat hash index:** `cellY * gridWidth + cellX` gives constant-time cell lookup with no tree overhead. [G]

**Two more game-grade optimizations:**
- **Shared / zero-copy neighbor list** [G]: compute each boid's neighbor set ONCE per frame and reuse it across separation+alignment+cohesion instead of re-querying the grid three times; return array references, not copies, to kill GC pressure. Measured: `updateFlock` 8.70 ms → 3.52 ms average (~60% faster), worst-case spike 49.54 ms → 18.50 ms (>50% cut). [G]
- **Hard neighbor cap** [F]: cap the number of neighbors scanned per agent (e.g. jdxdev's "hard limit on the max target count to scan"), bounding worst-case cost in dense clusters regardless of local crowding.

Scale achieved with these techniques: interactive frame-rates for very large flocks (search synthesis cited up to ~1M boids with GPU/grid approaches).

---

## 5. WHY IT READS AS "ALIVE" — AND THE ENEMY-SWARM TRADEOFF

**Why it looks intelligent** [A][D]: no boid is scripted and no boid sees the whole flock; coordinated, organic motion *emerges* purely from three local rules. Because perception is local, disturbances propagate as waves through the flock (turning, splitting around obstacles, re-merging), which reads as collective intelligence rather than a rigid formation. Reynolds' model is the foundation used in film (Batman Returns bat/penguin swarms 1992, Lion King wildebeest stampede 1994) and countless games. [A]

**The key tradeoff for enemies/goal-directed swarms** — cohesion (and often alignment) fight goal-seeking. Pure flocking has no destination; cohesion pulls each unit toward the *group's* center of mass, which can drag the swarm AWAY from the player/target. The practical game pattern (from jdxdev's RTS work [F]) is:

- **Keep:** Seek (toward the goal/target) + Separation (or a lighter avoidance force) — this is the workhorse combo for enemies. Seek gives them purpose; separation stops them stacking into one sprite.
- **Drop or minimize cohesion** — it interferes with goal-directed movement by pulling units off-target during maneuvers. [F]
- **Alignment is optional/light** — useful for making a group move coherently, but not essential.
- jdxdev actually **replaced pure separation with a traditional avoidance force**, because separation forces from many surrounding neighbors *cancel out and trap units* (opposing push vectors sum to ~zero, killing the seek), and locked avoidance to a consistent side to stop left/right flickering. [F]
- For units crossing through each other, they **zero avoidance + cohesion, leaving only seek + alignment**, and lean on physics colliders sized ~1.5–2.5× a unit's hard radius for spacing. [F]
- They also **scale down the seek force** when it points at a close neighbor, and use grid-based spatial partitioning + a max-scan cap for performance. [F]

**Takeaway for a game swarm:** start from `seek(target) + separation`, add alignment only if you want the group to visibly flow together, and reach for cohesion only when you actually want them to clump as a group rather than converge on a target. Weight separation highest so they never overlap.

---

Sources:
- [Craig Reynolds — Boids](https://www.red3d.com/cwr/boids/)
- [Craig Reynolds — Steering Behaviors For Autonomous Characters](https://www.red3d.com/cwr/steer/)
- [Van Hunter Adams (Cornell) — Boids algorithm](https://vanhunteradams.com/Pico/Animal_Movement/Boids-algorithm.html)
- [Ben Eater — Boids](https://eater.net/boids)
- [Daniel Shiffman — Nature of Code, Autonomous Agents](https://natureofcode.com/autonomous-agents/)
- [jdxdev — Boids for RTS](https://www.jdxdev.com/blog/2021/03/19/boids-for-rts/)
- [Arnauld — Scaling Boids for Multiplayer Games (spatial grids)](https://arnauld-alex.com/scaling-boids-for-multiplayer-games-fast-flocking-with-spatial-grids-and-zero-copy-optimization)