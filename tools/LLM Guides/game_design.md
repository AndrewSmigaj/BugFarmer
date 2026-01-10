BugFarmer — Consolidated Game Design Document (Final)
BUCKET 1: World Structure & Core Loop

High-level concept

Top-down multiplayer sandbox inspired by Terraria + Stardew Valley

Emergent gameplay; no scripted events

Systems interact naturally and spatially

Core player actions

Dig, build, place/remove blocks

Explore outward from a starting village

Catch, farm, fight, and sell bugs

World layout

World expands radially

Further zones = harder, richer, more dangerous

Cliffside horizontal digging

Mines carved into rock

Underground ant colonies, tunnels, ore

Rivers separate difficulty zones

Shallow crossings exist

All blocks are breakable

Nothing is truly impassable

Players can bridge, dig, or reroute

Navigation & discovery

Signpost / waypoint system

Move between zones

Set spawn points

Secrets

Hermit cabins

Special merchants

Hidden items / gear

Design intent

No forced progression

No scripted world events

The world creates problems; players decide whether and how to respond

BUCKET 2: Bugs, Swarms, and Networking Model

Scale

~50 bug species planned across biomes

Two bug representations
Swarm Bugs

Examples:

Flies

Mosquitoes

Butterflies

Bees

Server tracks (per swarm)

Swarm center

Wander radius / targeting

Count

Meters (calm / agitation)

Resource counters (nectar, food)

Reproduction readiness flags

Client-side

Renders individual virtual bugs

Handles local steering, visuals, hit interactions

Individual bugs are interaction proxies

Multiplayer rules

Players do not need to see the same individual bugs

Swarm count and state changes are authoritative enough

Catching removes from swarm; others see it shrink

Individual Bugs

Examples:

Spiders

Frogs

Wasps

Bosses / large bugs

Tracked individually for:

Combat

Danger

Boss-like encounters

Some bugs grow over time (e.g., millipede crossing danger thresholds)

BUCKET 3: Life Stages & Reproduction (Biology, Not Simulation)

Life stages

Eggs

Juvenile / larva

Adult

Purpose

Teach biology incidentally

Introduce delays and consequences

Enable emergent population dynamics

Scope

Population-level, not per-individual micromanagement

Visible as world objects where appropriate

Egg mechanics (example: flies)

Rotten fruit or suitable substrate → egg piles

Egg piles:

Consume the resource

Persist after resource is gone

Server tracks egg count

Hatching:

Joins nearby swarm OR

Spawns new swarm if none nearby

BUCKET 4: Tools & Capture Mechanics

Nets

Multiple sizes

Visible AoE indicator

Beginner nets catch easy bugs instantly

Throwable / cast nets

Area capture

Gamey and fun

Placeable ground nets

Used in automated farm setups

Attract bugs → collect at net

Smokers

Calm bees

General subdual mechanic

Capture rules

Some bugs require HP reduction

Some require calming

Wrong tool can agitate swarm

Design intent

Tools unlock behaviors and efficiency

Tools never replace player presence

BUCKET 5: Containment & Farming

Pens

Built entirely by players

Materials determine strength:

Wood → iron → steel → higher

Bug behavior

Some never break fences

Some slowly damage them

Some rapidly destroy weak materials (e.g., termites)

Escapes

Visible breaches

Gradual leakage

Swarm center shifts if enough escape

Rule

Any bug can be farmed if conditions and containment are met

BUCKET 6: Ecology Scenarios (Demo Focus)
Starting Village — Fly Dynamics

Core early gameplay: fly farming

Food sources:

Rotting fruit (natural + player-created)

Predators:

Small frogs

Small spiders

Wasps migrate from adjacent zone (right side)

Butterfly Zone (north of village)

Not a starting zone

Contains:

Butterflies

Milkweed

More valuable, harder-to-catch flies

Predators: frogs, small spiders

Milkweed pressure sources:

Grazers

Environmental nudges (rain/dry spells)

Player harvesting

If milkweed hits zero:

Butterflies become inert

No reproduction

Population ages out

Bees / Wasps

Wasps prey on bees

Wasp reproduction requires successful predation

Bees reproduce when:

Hive exists

Sufficiently fed

Pollination:

Heuristic

Triggered when swarm center passes near flowers

BUCKET 7: Private Plot vs Shared World
Shared World

Chaotic

Persistent

No ownership of pens

Good for exploration, risk, group farms

Private Plot

Fully separate scene

Shared world unloads

Owned by player

No chaos unless player introduces it

Used for:

Stable farming

Experiments

Ownership-based achievements

Expandable via City Hall

BUCKET 8: NPCs, Quests, and Learning
NPC Types

Ecologist

Miner / Delver

Builder / Foreman

Explorer / Scout

Traders / others

Ecologist (unique role)

Shows current knowledge of a zone

Gives quests based on real imbalances

Uses tracking stations to unlock info in adjacent zones

Explains ecology at high-school level

Hidden mini-lessons per quest

Never scripts events

Quests

Respond to world state

Never create problems

Optional

Multiple valid solutions

Ignoring is always allowed

BUCKET 9: Achievements

Track player actions only

Two categories:

Private plot

Shared world

No achievements for:

Passive waiting

Ambiguous ownership

Observing collapse

BUCKET 10: Magnifying Glass

Inspect unique instances

Repeated inspection does not count

Unlocks:

What bugs like

What they avoid

Breeding conditions

Educational tidbits

Supports curiosity, not progression gating

IDLE & AUTOMATION BUCKET (Private Plot Focus)

Design goal

Support optimization-focused idle play

Reward layout and long-term planning

Reduce tedium without replacing gameplay

Hard constraints

No purchasable pens

All containment is emergent

No automated catching

No automated combat

Private plot only

Hireable NPC Workers

Lumberjack

Miner (processor role only)

Bug Handler / Keeper

NPCs:

Are physical entities

Operate in limited areas

Accelerate but never replace loops

Specialized structures

Hives

Smokers

Extractors

Rotten fruit piles

Incubators
(All require player-built containment)

Passive comfort & nudges

Benches, lamps, rugs, gardens, water features

Shade, moisture, windbreaks, heat lamps

Time-based production

Compost bins

Honey extractors

Silk reels

Egg incubators

Idle risk

Slow

Visible

Local

Reversible

No offline catastrophes

RISK, EVENTS, & OFFLINE BEHAVIOR
Private Plot

No random invasions

No disasters

No offline damage

Production aggregated while offline

Shared World

Chaos and emergence

Migration

Predation

Environmental nudges

Player-caused events only

Events philosophy

No timers

No forced raids

No surprise punishments

Everything is spatial and visible

SWARM-LEVEL NETWORKING LOCK

Virtual insects are client-side interaction proxies; all meaningful progression state (counts, meters, resources, reproduction readiness) is tracked per-swarm server-side and updated via batched client deltas plus occasional discrete events (e.g., pollination).

FLIES: Egg Piles, Maggots, Hatching

(Entire fly reproduction system preserved exactly as specified)

Egg piles consume resources

Maggot stage is visual + optional gameplay

Hatching reinforces nearby swarms

Merging common, splitting rare

Anti-spam caps in place

BEEKEEPING (Structured System)

Hive-based farming

Environmental preparation

Agitation management

Smoker use

Visual feedback only

No sudden colony death

Stable idle-friendly progression

PLANT FARMING (Expanded)

Plants exist to support bugs

Watering tiers (manual → automated)

Pollination via swarm proximity

No plant death from neglect

Decoration has gameplay value

COMBAT & LARGE ARTHROPODS

Real-time, item-driven

No stamina, no XP

Control and positioning matter

Millipedes / Centipedes

Bezier-segmented bodies

Momentum-based attacks

Fast turning while idle

Committed lunges

Scorpions

Precision predators

Tail telegraphs

Burst damage

Bosses

Emerge naturally

No scripted telegraphs

Simply tougher, larger, scarier

ARMOR, UTILITY GEAR, ACCESSORIES

Armor always equipped

Utility overlays (bee suit, mining gear)

Accessories for expression

No forced tradeoffs

ITEMS, ACCESSORIES & RARITY

Small meaningful rolls

No reroll treadmill

Rarity = interesting, not mandatory

Active tools reward intention

WEATHER, DAY/NIGHT & ENVIRONMENT

Soft modifiers only

No disasters

No punishment

Supports ecology quietly

NPC VENDORS & TIERS

Most items buyable immediately

Money is primary gate

Tiers provide:

Discounts

Convenience

A few niche unlocks

Quests optional and grounded

BugFarmer Swarm Movement & Containment
Execution Model Lock (MANDATORY)

This guide exists to prevent incorrect assumptions about where computation happens.

BugFarmer — Combat & Catching Guide (Architecture-Locked, Implementation-Ready)
0) Non-Negotiables (Hard Locks)

Multiplayer cooperation must work. Multiple players can hit/catch the same bug and see consistent results.

Every bug has HP. Flies are just low-HP bugs. No special “flies have no HP” rule.

Swarms have shared meters/conditions (calm/agitation/etc.) that affect behavior and catchability.

We avoid bandwidth blowups. We do not stream positions for thousands of swarm members.

We do not care about anti-cheat. Player-hosted servers; moderation is “kick.”

Inactive chunks are aggregated only. No per-bug simulation when no one is nearby.

CRITICAL FIX: We do not track persistent alive/dead flags for bugs.
If a bug dies or is caught, it is removed from the swarm roster (deleted). No graveyard tables.

1) Definitions
Swarm

The core gameplay/network unit.

Has shared state: meters, reproduction readiness, etc.

Has a member roster for combat/catching (HP per member).

A “solo bug” is a swarm with count = 1.

Swarm Member

An individually addressable bug inside a swarm.

Address: (swarm_id, member_id)

Has HP on the server.

Has a movement style (see §3).

2) What Lives Where (Authoritative Ownership)
Server (authoritative for shared truth, cheap)

Per swarm:

swarm_id, species_id, zone_id/chunk_id

center (x,y), wander_radius (center movement is server-owned; see §3)

meters (calm/agitation/optional panic)

members: { member_id -> hp_current }

No “dead” members stored. If it dies/caught → remove the entry.

reproduction counters/flags (egg piles etc.)

split/merge results (roster reassignment)

Server does NOT simulate:

per-member pathfinding

per-member collision / targeting

per-frame movement

“where the scorpion is standing” as an authoritative physics truth (we only need consistent visuals + synchronized HP outcomes)

Clients (feel + local sim)

For swarms in active chunks:

render members

run movement visuals deterministically (see §3)

run local hit detection (fast feedback)

send hit/catch events to server

apply server deltas to reconcile truth (HP removals, meter changes)

3) Deterministic Positions Without Bandwidth (This is the Key)

We need: “everyone fights the same scorpion in the same place” without streaming positions for thousands of bugs.

So we use two movement profiles, per species (not “flies vs others”; it’s a species config choice):

A) Orbit (Stateless Deterministic Offsets) — Default for big swarms

Used when the swarm can be large (flies, mosquitoes, etc.) and we refuse bandwidth.

Core idea: A member’s position is a deterministic function of:

swarm_center

member_id

global_sim_tick (or time quantized to ticks)

species movement params

So a late joiner doesn’t need replay or snapshots. They only need:

current swarm_center

the current global_sim_tick

the roster (member_ids + hp)

Example (conceptual):

offset = OrbitOffset(member_id, tick, species_seed)

pos = swarm_center + offset

optional: tiny deterministic “noise jitter” derived from (member_id, tick)

Collision / barriers:
Members in Orbit mode do not individually collide with walls. Barriers are respected by swarm-center movement (server-owned). This is the scalable trade:

If the center is inside a pen, the whole swarm visually stays “in the pen.”

If the center can move through a gap, the whole swarm migrates through.

You do not do per-member wall physics for 10,000 bugs. Ever.

This is what keeps bandwidth and CPU sane.

B) Agent (Stateful Local Motion) — For small, high-value “positional truth” swarms

Used for things like “3 giant scorpions” where per-member distinct placement matters and N is small.

Here you can afford more state because N is small:

Each client simulates them in the same way (deterministic RNG + same tick base).

Optional: if you ever get drift, you can resync occasionally only for small-N Agent swarms.

Important: Even in Agent mode, we still avoid streaming constant positions for everything. Agent mode is for small-N only.

4) Ticks & Progression (Architectural Reminder)

Use three time granularities:

Render/Sim Tick (client): 30–60 Hz

smooth movement/animation

local hit detection

Server Swarm Logic Tick: ~5–10 Hz

apply queued Hit/Catch events

clamp/update meters

handle split/merge outcomes

update centers (migration intent)

Inactive Chunk Tick (server): every ~2–10 seconds

aggregated ecology only (counts, reproduction timers, etc.)

no per-member anything

Global tick source: server maintains global_sim_tick (monotonic).
Clients use it to keep deterministic motion aligned.

5) IDs & Roster Rules (No Dead Tables)
Member lifecycle

Spawn: server creates member_id and adds {member_id: hp} to roster.

Death: server removes member_id from roster immediately.

Catch: server removes member_id from roster immediately.

No alive=false. No historical storage.

Member_id format

Use something cheap and unique enough:

member_id can be a 32-bit integer generated from a per-swarm counter (or random).

When removed, it’s gone.

Do not reuse ids quickly (avoid confusing late packets). If you do reuse, do it with an epoch counter (but simplest: don’t reuse).

6) Combat (Member-Level HP, Server Truth)
6.1 Local hit detection (client)

Client computes “did I hit a bug?” by colliding attack shapes with deterministically computed member positions (Orbit/Agent).

On hit, client sends:

HitBug Event

swarm_id

member_id

damage

weapon_id/tool_id

source_player_id

optional client_seq (ordering)

6.2 Server hit resolution (authoritative, cheap)

On HitBug:

Look up swarm.

Check member_id exists in roster.

If not present: ignore (already dead/caught).

Apply damage to roster HP.

If HP <= 0:

remove member_id from roster

decrement count

spawn loot/corpse item(s) (separate entity rules)

optionally apply meter effects (agitation spike, etc.)

Broadcast minimal deltas:

MemberHPChanged (optional, if you display HP)

MemberRemoved with reason death

SwarmCountChanged (optional if implied)

SwarmMetersChanged if thresholds crossed

6.3 Client reconciliation

Clients show immediate VFX, then reconcile with server deltas:

if member removed → delete it locally

if HP differs → correct UI/feedback if you show it

rejected hits (member missing) do nothing beyond cosmetic feedback

7) Catching (Member-Level Action + Swarm-Level Conditions)

Catching targets a specific (swarm_id, member_id) and checks:

member is present

HP threshold (if required)

swarm meter thresholds (calm enough / not too agitated)

tool constraints (net type, trap type, smoke effect, etc.)

CatchAttempt Event (client → server)

swarm_id

member_id

tool_id

attempt_type (net / trap / hand / etc.)

source_player_id

Server catch resolution

Verify member exists in roster.

Verify tool rules.

Verify conditions:

HP threshold if needed

calm/agitation thresholds if needed

If success:

remove member_id from roster

decrement count

grant captured bug item to player inventory

broadcast MemberRemoved reason caught

If failure:

optionally raise agitation / lower calm

broadcast meter change if it crosses thresholds

Multiplayer guarantee

Because the server is the roster authority:

two players cannot both catch the same member

first processed wins; later attempts see “member missing” and fail cleanly

8) Swarm Meters / Shared Conditions (Calm / Agitation / Optional Panic)
What meters do

Meters affect:

catch success rules

client-side behavior mode (visual aggression vs calm)

optional scatter/split likelihood (if you want that coupling)

How meters change

Clients generate influences from micro interactions but batch them.

MeterDelta Event (client → server) sent every ~0.5–2s or per action burst:

swarm_id

calm_delta

agitation_delta

source_player_id (optional)

Server:

clamps meters

resolves state transitions (Calm/Neutral/Agitated/etc.)

broadcasts SwarmMeterStateChanged only on meaningful change

9) Movement vs Combat Truth (How we keep “same bug in same place”)
Orbit mode (large N)

Everyone computes the same positions because:

positions are a pure function of center + (member_id, tick, species params)

no snapshots required

late joiner receives:

swarm roster

center

current tick

species params
…and instantly renders identical positions

Agent mode (small N)

Everyone computes identical positions because:

deterministic sim uses:

same tick

same movement params

same starting seed derived from swarm_id + member_id

Optional drift handling for Agent mode only:

rare AgentResync snapshot (positions for 3–20 members is tiny)

not used for big swarms

10) Pens, Barriers, and “Flies Ignore Barriers”

We do not do per-member barrier physics for large swarms. That is how you die (CPU and complexity).

Instead, barriers matter because swarm-center movement is blocked.

The server moves the center and respects solid tiles.

Clients render members relative to center.

If the center is trapped, the swarm is trapped.

If a gap exists and the center can pass, the swarm migrates out.

This makes pens work without per-fly collision.

11) Inactive Chunks (Aggregated Only)

When no players are nearby:

no member rendering

no hit/catch events (nobody there)

server runs only aggregated ecology:

reproduction timers/counters

population nudges

migration intent / center stepping at coarse tick (optional)

When a chunk becomes active:

server sends swarm roster + HP + meters + center + tick

clients instantiate members deterministically (Orbit/Agent)

12) Minimal Server Data Structures

Per swarm:

swarm_id

species_id

zone_id/chunk_id

center_x, center_y

wander_radius

meters {calm, agitation, panic?}

members: Map<member_id, hp_current>

reproduction flags/counters

That’s it.

No:

member positions

dead tables

per-member AI state (unless Agent mode truly needs a tiny optional state, and only for small N)

13) Network Events (Only What You Need)

Client → Server:

HitBug(swarm_id, member_id, damage, weapon_id, source_player_id, seq?)

CatchAttempt(swarm_id, member_id, tool_id, attempt_type, source_player_id)

MeterDelta(swarm_id, calm_delta, agitation_delta)

optional SplitCandidate(...) (if you keep split reporting elsewhere)

Server → Clients:

MemberRemoved(swarm_id, member_id, reason=death|caught)

MemberHPChanged(swarm_id, member_id, new_hp) (only if you want it visible)

SwarmMetersChanged(swarm_id, meters/state)

SwarmUpdated(swarm_id, center, count) (count optional if implied by roster size)

14) Explicit Anti-Patterns (Reject These in Review)

❌ Persistent alive/dead flags
❌ “dead bug history tables” per swarm
❌ Server-side member positions for large swarms
❌ Streaming thousands of member positions each tick
❌ Fence raycasts / enclosure detection to “fix pens”
❌ Complexity introduced “for anti-cheat”

Locked Summary (One paragraph)

Combat and catching are synchronized at the member level using a server-owned swarm roster where each member_id has HP; on death/catch, the server removes the member from the roster (no persistent alive/dead tracking). Clients render and simulate member motion deterministically for scalability: large swarms use stateless Orbit mode (positions derived from center + member_id + global tick), while small high-value groups may use Agent mode with optional rare resync. The server owns shared swarm meters (calm/agitation) updated via batched deltas, and owns swarm center movement (blocking against terrain), making pens work without per-member barrier physics. Inactive chunks remain aggregated only.

Orbit function — literal orbit or just deterministic offset?

Short answer:
It is not a literal circular orbit unless you want it to be.
“Orbit” means deterministic, stateless offset from the swarm center.

What “Orbit mode” really means (implementation truth)

Each member’s position is a pure function:

position = swarm_center + f(member_id, global_tick, species_params)


There is:

❌ no per-member state

❌ no memory of past positions

❌ no replay or syncing

Late joiners reconstruct positions instantly from the same inputs.

What f(…) should look like (recommended)

Use cheap, bounded, pseudo-random motion, not perfect circles.

Good options (pick one, keep it simple):

✅ Option A: Low-frequency noise offset (recommended default)

Use a hash / noise function seeded by member_id

Sample it at tick * speed

Clamp to a radius

Example (conceptual, not language-specific):

angle = hash(member_id) * 2π + tick * angular_speed
radius = base_radius + noise(member_id, tick) * jitter
offset = (cos(angle), sin(angle)) * radius


This:

looks organic

is deterministic

does not require storing phase

avoids obvious “orbiting bees” visuals

✅ Option B: Lissajous-style motion (fine, but optional)

Only if you want prettier motion:

x = sin(a*t + φ1)
y = sin(b*t + φ2)


Seed φ1, φ2 from member_id.

❌ What NOT to do

❌ True Brownian motion with accumulated deltas (needs state → breaks determinism)

❌ RNG calls without fixed inputs

❌ Anything that depends on previous frame results

Design rule to lock in

Orbit mode means stateless deterministic offsets, not “they must move in circles.”

If you document that sentence, Claude / future-you won’t screw this up.

2. Species config for movement mode

Yes — explicitly add this. This is the cleanest way to prevent overengineering.

Recommended species config fields
{
  "species_id": "giant_scorpion",
  "movement_mode": "agent",
  "max_hp": 120,
  "swarm_defaults": {
    "wander_radius": 6
  }
}

{
  "species_id": "house_fly",
  "movement_mode": "orbit",
  "max_hp": 3,
  "orbit_params": {
    "base_radius": 2.5,
    "jitter": 1.0,
    "angular_speed": 0.4
  }
}

Why this matters

Prevents accidental “agent simulation” for flies

Makes performance characteristics explicit

Lets you tune visuals per species without touching networking

Keeps your codebase readable

Hard rule to document

movement_mode = "orbit" must be stateless and reconstructible from (member_id, tick, swarm_center) alone.

If someone violates this, they’re breaking the architecture.

3. MaxHP source & HP bars

You are thinking about this correctly.

Server-side truth

Species config defines max_hp

Swarm roster stores only current HP

On spawn:

member.hp = species.max_hp

How clients know max HP

Clients already know species data (they must, to render bugs).

So:

HP bar max = species.max_hp

HP bar current = server-synced hp_current

No extra syncing required.

Do NOT do this

❌ Don’t store max_hp per member (wasteful, redundant)

❌ Don’t sync HP percentages (harder to reconcile)

❌ Don’t store dead members “for reference”

HP bar visibility (design note)

You can choose:

No HP bars (read behavior only)

HP bars only for:

solo / agent-mode enemies

bosses

captured-in-progress bugs

That’s a presentation choice, not an architecture issue.

One-paragraph “lock statement” you should add to the doc

You can paste this verbatim:

Orbit movement is a stateless, deterministic position offset from the swarm center, computed from (member_id, global_tick, species parameters) and requiring no per-member state or replay. Species explicitly declare movement_mode = orbit | agent. Member HP is initialized from species max_hp; the server stores only current HP, removing members entirely on death or capture. Clients derive max HP from species data for display.

If this paragraph is in your design doc, this entire class of confusion disappears.

If you want next steps, good follow-ups would be:

“How do agent-mode enemies handle wall collisions deterministically?”

“Do we ever need partial resync for agent-mode drift?”

“How do bosses differ from agent swarms of size >1?”

But you’re now on solid, sane ground with these three points.

well why dont we address those questions then?  (bosses are just the max level of bugs, limited by a cap of bosses per level so others just stay at the adult stage)  they arise when enough resources have been obtained by the bug

Good — these are exactly the right next questions, and your clarification about bosses helps a lot. I’ll go one by one, keep it implementable, and avoid re-introducing bandwidth or replay problems.

I’ll also explicitly separate what must be deterministic vs what is allowed to diverge slightly client-to-client, because that’s the real axis here.

1. Agent-mode enemies: wall collisions & determinism
First: what level of determinism do we actually need?

We need shared combat reality, not bit-perfect animation sync.

That means:

Everyone must be hitting the same bug

HP changes must apply to the same entity

The bug must be in roughly the same place, not pixel-perfect

We do not need:

Identical footstep paths

Identical idle jitter

Identical micro-corrections against walls

This is critical, because perfect determinism + collision resolution = replay hell.

So we choose a hybrid determinism model.

Recommended model: “Authoritative intent, client-resolved motion”

For agent-mode bugs (scorpions, frogs, millipedes, bosses):

Server owns:

swarm_id

member_id

HP

alive / removed

high-level intent (optional, coarse)

Examples of intent:

target position

target player

idle / chase / flee state

cooldown timers

Client owns:

exact pathfinding

collision resolution

animation

short-term steering

This is the same model used by:

Terraria

Valheim

Minecraft mobs (to a degree)

Collision handling (the important part)

Clients resolve collisions locally using normal physics:

walls

terrain

obstacles

If two clients resolve slightly differently:

That’s fine

HP events still apply to the same member_id

The illusion holds because:

Bugs are moving entities, not grid-aligned chess pieces

Combat tolerates small discrepancies

Key constraint

A bug’s identity and HP must be consistent, not its exact x/y every frame.

Periodic coarse correction (optional, cheap)

If you want to reduce long-term drift without replay:

Every few seconds (e.g. 1–3s), server may broadcast:

member_id
approx_center_position


Clients softly nudge toward it (lerp, no snap).

This is:

optional

low bandwidth

not per tick

not replay

You can even skip this initially.

2. Do we need resyncs? When and how?
Orbit-mode (flies, bees)

Never.
They reconstruct instantly from:

swarm_center

tick

member_id

Late joiners get perfect positions automatically.

Agent-mode (scorpions, bosses)
Late join scenario

Player joins while others are fighting a scorpion.

What happens:

Server sends:

swarm_id

member_ids

HP values

current intent (e.g. “chasing player X”)

approximate position

Client spawns agent locally

Simulation continues forward

No replay.
No per-frame sync.
No asking another client for state.

The joining player might see:

the scorpion a tiny bit offset
That’s acceptable.

Hard rule

We never request “exact bug positions from another client.”

That’s the bandwidth trap you were trying to avoid originally.

3. Bosses (your clarification, locked in)

Your rule is actually very clean. Let’s formalize it so it’s implementable.

Boss definition (final)

A boss is:

a normal bug species

that has crossed a resource / growth threshold

and has entered its boss stage

There is no separate boss entity type.

Boss emergence rules

Each species has:

boss_threshold_resources
boss_cap_per_zone


When an adult bug accumulates enough resources:

If boss_cap not reached:
→ it upgrades to boss stage

Else:
→ it stays adult forever

No telegraph required.
No cutscene.
No announcement.
It just gets bigger, tougher, scarier.

What changes when a bug becomes a boss?

All of these are just multipliers, not new systems:

max_hp ↑

damage ↑

size ↑

maybe movement speed ↓

maybe aggression radius ↑

Networking-wise:

still a member_id

still HP-based

still agent-mode

This is important: bosses do not add architectural complexity.

4. Multiple players fighting the same boss (critical)

This now works cleanly with what you already decided.

Why it works

There is one member_id

All hit events reference that ID

HP is server-owned

Removal happens once

Even if:

one client sees it slightly left

another sees it slightly right

They are still interacting with the same entity.

Visual mismatch risk (acceptable)

Yes, one player might swing and “miss” visually while HP goes down.

But:

this already happens in Terraria-style games

tight hitboxes + forgiving weapons mitigate it

the alternative (full sync) is worse

You can also:

make hit volumes generous

bias melee arcs forward

5. Drift, splitting, and bosses

Bosses should never split.

So:

split_enabled = false for boss-stage members

they are always “swarm of one”

Regular agent swarms (e.g. scorpions in groups):

can split via your existing outlier logic

bosses are exempt

This keeps:

logic simple

behavior intuitive

6. Inactive chunks & bosses

Inactive chunk rules still apply cleanly:

When no players nearby:

no movement

no combat

no HP changes

Boss state persists as:

member exists

HP value

stage = boss

When a player returns:

client spawns boss

resumes agent simulation

No replay.
No catch-up simulation.
No weirdness.

7. Final architectural stance (this is the “don’t screw this up” version)

You can drop this straight into your doc:

Orbit-mode species use stateless, deterministic motion reconstructed from swarm center and tick and never require synchronization. Agent-mode species (including bosses) are simulated locally per client for movement and collisions, while identity, HP, and life/death are synchronized via member-level events. Exact positions are not authoritative; shared combat reality is achieved through consistent member IDs and server-owned HP. Bosses are not special entities, but adult bugs that exceed a resource threshold and upgrade in place, limited by a per-zone boss cap.

Bottom line

Your bandwidth goal is preserved

Multiplayer combat works

Bosses are just “grown-up bugs”

No replay system

No client-to-client state copying

No per-bug server simulation

This is sane, scalable, and matches Terraria-like expectations

