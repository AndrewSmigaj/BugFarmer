# Bugs: gentle pollinators & ambient fliers (butterfly, bee, firefly, dragonfly, mayfly, cicada, moth)

*Topic 2 of the 2026-07 bug-behaviour research — the CALM half of the roster. How to make the game's
beautiful flying insects feel ALIVE (flight noise, flower-hopping, light-attraction, glow, mating dances)
and how the one aerial PREDATOR here (the dragonfly) hunts, grounded in real biology + how good 2D games
do it, mapped to our deterministic swarm sim. Pairs with `flying_pests_stingers.md` (aerial threats),
`scorpions_centipedes.md` (ground ambush), and `../combat/03_challenge_and_effectiveness.md` (shared
framework). Raw (thin — the pollinator agent died early): `../_raw_recovered/bugs/a1c61bc0ef1c7d5f9.md`,
`ab9f15ce2fe9e961b.md`, `abf6d6b1bbdc1ec5e.md` — those held mostly bee-zone AUTHORING material, not
behaviour, so the behaviour below is fresh web research.*

## The core takeaways (the readable wins)
1. **These bugs sell the world's LIVELINESS, not its threat.** Their whole job is ambient beauty +
   being catchable. Function-over-stats still applies (§03): each one teaches a different *motion* and a
   different *reason to be somewhere* (butterfly = flowers by day; firefly = stream at dusk; dragonfly =
   over water hawking wasps; moth = around your lamp at night), so a zone reads as a living food web, not a
   sprite scatter.
2. **Flight FEEL = per-species wander noise, not per-species AI.** Real "aliveness" comes from the *texture*
   of the path — a butterfly's random flutter vs. a dragonfly's straight-line dart vs. a firefly's slow
   drift. Our sim already exposes exactly the knobs: `movement_style` (client render class),
   `wander_radius`, `wander_change_rate`, `base_speed`, plus a client-side vertical BOB. That's the whole
   trick and it's cheap.
3. **Light-attraction (moths, fireflies) is a target-selection rule, not new physics.** "Moth to a flame"
   = the same forage/attraction machinery we already run for flowers, pointed at LAMP occupants at night.
   Fireflies gathering along the stream at dusk = a day/night spawn/behaviour gate on the tick clock.
4. **Firefly glow is our emissive-visuals hook.** Fireflies should pulse a warm light at night (client
   LampLight-style emissive), and it should be a *rhythmic pulse*, not a static tint. This is display-only
   and rides the deterministic day/night tick — no sim change.
5. **The dragonfly is the one PREDATOR here and it's already built** — `dragonfly_blue` hawks
   `wasp_common` out of the air via the existing `predation` block (strike radius, hunt speed, cooldown).
   It's the "beautiful thing that is quietly lethal to pests" — a helpful predator the player *wants*
   around. Its behaviour spec is mostly a tuning + visuals pass, not new code.
6. **Mayfly + cicada are the "event" bugs** — a mayfly mating-swarm dance (huge, brief, spectacular,
   short lifespan) and the cicada's summer drone (audio-first, perch-on-trees). They cost almost nothing in
   the sim but give the world seasonal/temporal punctuation.

---

## Engine facts this doc builds on (verified against code, 2026-07-11)
- **Movement = legs.** All bug motion is `SWARM_SET_TARGET` "legs" (origin → target → speed, fixed-point),
  emitted by the authority and replayed identically on every client. `wander_radius` /
  `wander_change_rate` / `base_speed` shape the wander legs; nothing view-scoped feeds the sim.
- **`movement_style` is a CLIENT RENDER CLASS, not sim.** `modules/entities/species.go:111-113`:
  *"Client movement class key (`brownian`, `gliding`, `darting`, `crawling`)."* The server does not branch
  on it — it only rides along in the snapshot so the client can pick a flutter/dart/drift animation +
  bob. **So per-species flight FEEL is a client cosmetic keyed off one string** → free to make gorgeous,
  zero determinism cost. (Today: butterfly/firefly = `gliding`, bee = `brownian`, dragonfly = `darting`.)
- **Forage / attraction is target selection.** `attractions_by_phase.{feeding,reproducing}` lists the
  occupant ids a swarm is drawn to; `forage_chance`, `attraction_strength`, `vision_range`, `feed_amount`
  drive flower-hopping. Butterfly `reproducing` phase points at `milkweed` (host plant) — a real
  two-target state machine already exists (feed at flowers → breed at host).
- **Day/night is a FREE deterministic clock.** `match.go:47-51`: one day = `DayLengthTicks = 8400` ticks
  (14 min @10Hz); the phase is a pure function of `tick % DayLengthTicks`, so *"the day/night cycle needs
  no extra netcode."* Any night-active behaviour (firefly glow, moth-to-lamp, cicada day-drone) gates on
  this integer — bit-identical on every client. `setTimeOfDay` (`handlers_env.go:95`) can force a phase for
  testing.
- **Predation already works for the dragonfly.** `dragonfly_blue.predation`: `prey:["wasp_common"]`,
  `strike_radius:3.0`, `strike_cooldown_ticks:120`, `kills_per_strike:1`, `feed_per_kill:50`,
  `hunt_speed_mult:1.4`, `hunt_satiation_threshold:40`. The authority runs the strike; the observable is
  relayed (`BUG_REMOVED`-class), clients never decide a kill (`match.go:1131,1321`). `base_speed:2.8`,
  `movement_style:"darting"`, `flies_over_fences:true`, `max_swarm_size:3`.
- **Flee/reaction.** `player_reaction` (`curious`/`ignore`) + `reaction_radius` + `flee_speed_mult` +
  `predator_flee_radius`; flee is `PLAYER_CELL_ENTER`-driven. Butterfly = `curious` (drifts near you);
  bee/firefly/dragonfly = `ignore`.
- **Catch / calm.** `net_size`, `catch_condition` (`always` for butterfly/firefly/dragonfly; `calm` for
  the honeybee — subdue with smoke first), `condition_tools:{calm:…}`. Per-bug `max_hp` is display-only.
- **Lifespan is a species field** — `lifespan_secs` + `lifespan_spread_secs` (butterfly ~3360s, firefly
  ~6000s, dragonfly ~9000s). A mayfly's famously short life = a very small `lifespan_secs`.
- **What EXISTS as species (has AI):** `butterfly_meadow`, `bee_honey`, `dragonfly_blue`, `firefly`.
  **Sprites-only (no `species.json`, no AI → won't spawn):** the rest — `bee_carpenter`, `bumblebee`,
  `butterfly_{monarch,swallowtail,emperor,fields}`, `firefly_{blue,great}`, `dragonfly_{emperor,hawker}`,
  `mayfly_{common,giant}`, `cicada_{annual,periodical}`, `moth_{common,luna,atlas,brown}`. These need a
  `species.json` entry to come alive (a `bugs.json` id without a species spec silently fails to spawn).
- **NO glow/emissive field exists on species yet** (`grep glow|emissive|light_radius` → nothing). Firefly
  glow is a GAP to add — client-side, reusing the existing `LampLight.cs` / `DarknessOverlay.cs` emissive
  path, gated on the day/night tick.

---

# Per-species specs
*Each: **(a) real behaviour · (b) how games do it (cited) · (c) BEHAVIOR SPEC on our sim · (d) role ·
(e) visual/animation note.***

## 1. Butterfly (`butterfly_meadow`; sprites monarch/swallowtail/emperor/fields)

**(a) Real.** Butterflies fly in an erratic, twisting zig-zag — an evolved *predator-evasion* tactic: the
unpredictable path makes it hard for a bird to anticipate where they'll be (the hindwings exist mainly to
enable this maneuverability, not lift) [B-fly-flight]. Toxic/aposematic species that don't *need* to dodge
fly notably STRAIGHTER — a lovely built-in variety hook. They nectar with **flower constancy**: learn which
flower colours/shapes pay best and return to them repeatedly, using colour + UV + scent to find them
[B-fly-nectar].

**(b) Games.** Stardew's butterflies are *decorative*: they "wander within a broad area of their spawn site"
and are a deliberate aesthetic touch ConcernedApe added "to make the game more lively," spawning in the air
and around flowers by day [SDV-critters]. Animal Crossing butterflies "spawn in the air and around flowers
during daylight hours" and are "skittish fliers" that scatter if you run — you must **hold to creep slowly**
[ACNH-bugs]. The common/yellow butterflies are the easy-catch tutorial bugs.

**(c) Spec (BUILT — a tuning + variety pass).** Keep the existing `butterfly_meadow`: `movement_style:
"gliding"`, `base_speed:1.2`, `wander_radius:12`, `wander_change_rate:0.05`, `player_reaction:"curious"`,
two-phase forage (`feeding`→`flower_*`, `reproducing`→`milkweed`). To sell the erratic flutter, RAISE
`wander_change_rate` and shorten the wander legs so the leg-path itself kinks frequently (the server half of
the flight model, §candidates B), and let the client `gliding` renderer add the flutter + vertical bob (§C).
- **Flower-hop = the existing forage state:** on reaching a flower it PAUSES (a short zero-length "perch"
  leg while `feed_amount` ticks), then picks the next attracted flower — this IS the flower-hopping state
  machine, already in the forage/attraction code; just make the pause visible.
- **Variety for free (biology-true):** give `butterfly_monarch` (aposematic/toxic) a *straighter* path —
  lower `wander_change_rate`, longer legs — vs. the twitchy common; swallowtail/emperor as mid. One data
  dial, real distinctness.
- **`curious`** already makes it drift toward a still player and flee only if you rush — the AC "creep
  slowly" catch loop falls out of `reaction_radius` + `flee_speed_mult`.

**(d) Role.** Pure ambient beauty + the beginner catch (net, `catch_condition:"always"`, `net_size:small`).
The daytime meadow's signature motion.

**(e) Visual.** `gliding` = asymmetric wing-flap flutter + a gentle vertical bob (sine), path visibly
kinking. Monarch reads "confident/straight"; common reads "drunken flutter." Perch-with-wings-folded on the
flower during the feed pause.

## 2. Bee (`bee_honey` honeybee; sprites bumblebee/carpenter)

**(a) Real.** A gentle central-place forager: works flowers for nectar, flies it home to the hive, only
stings to defend the colony. Tight, buzzy, businesslike flight between flower and hive (not a wanderer).

**(b) Games.** Bees read as *purposeful* — Stardew/AC bees orbit flowers and hives; the fantasy is "busy,
useful, mostly harmless unless provoked." (Our own hornet doc, `flying_pests_stingers.md`, covers the
*aggressive* stinger side; the honeybee is its calm cousin — the smoker that pacifies hornets is the same
diegetic tool that lets you harvest a hive.)

**(c) Spec (BUILT — the most complete already).** `bee_honey` has a real forage→deposit LOOP via its
`predation` block repurposed as **central-place foraging**: `nest_occupant:"bee_hive_wild"` (+ `beehive_*`
stations), `deposit_satiation:80`, `hunt_satiation_threshold:45` — i.e. forage flowers until full, fly to
the hive, deposit (→ honey economy), repeat. `movement_style:"brownian"`, `base_speed:1.8`,
`wander_change_rate:0.25` (tighter/busier than the butterfly), `player_reaction:"ignore"`,
`stings_only_defending:true`, `attack_is_sting:true`, `catch_condition:"calm"` (smoke first),
`flies_over_fences:true`, small tight swarms (`max_swarm_size:12`, `swarm_radius:1.5`).
- **Keep it as-is;** the one gap is the *defensive* sting escalation (recruit-on-disturb) — that's the
  hornet doc's alarm-pheromone system; a honeybee hive can reuse a gentler version (smoke suppresses it).
- **Bumblebee/carpenter** = data variants: bumblebee slower/rounder path (lower speed, bigger bob), carpenter
  a loner (min_swarm_size 1). Same forage loop.

**(d) Role.** Ambient + the farm's productive engine (nectar→honey), NOT a threat unless you swat its hive.
The player *wants* bees.

**(e) Visual.** `brownian` = fast small jitter with a tight hover-bob over each flower; a visible pollen
dab; a straight beeline back to the hive (contrast the wanderers). Bumblebee = heavier, lower bob.

## 3. Firefly (`firefly`; sprites blue/great) — the night glow (our emissive hook)

**(a) Real.** Fireflies rest on foliage by day and begin their glow ritual **around dusk** [FF-bio]. The
light is *cold* bioluminescence (luciferin + luciferase); flashes are **orderly, species-specific patterns**
(spirals, J-loops) at roughly **~1-second intervals**, males flying higher and flashing brightest while
females answer from vegetation [FF-bio]. Some Southeast-Asian species (*Pteroptyx*) **synchronize** — whole
trees pulse in unison [FF-bio].

**(b) Games.** Stardew fireflies "glow and enhance the night ambiance," appear in summer, and are purely
decorative (non-interactive) — a canonical "make the night feel alive" flourish [SDV-critters]. AC fireflies
appear **near water at night** (June) with "characteristic glowing behaviour" [ACNH-bugs][NL-bugs].

**(c) Spec (BUILT motion; GLOW is the gap).** `firefly` exists: `movement_style:"gliding"`, slow
`base_speed:0.9`, `wander_radius:10`, small drifty swarms (3–10), `player_reaction:"ignore"`,
`catch_condition:"always"`. Description already reads *"loveliest at dusk along the stream."* Add:
- **Night gate (deterministic):** gate spawn/visibility/behaviour on `tick % DayLengthTicks` (dusk→night
  window). Free and bit-identical (`match.go:47-51`) — no netcode.
- **THE GLOW (client emissive — new, cross-ref visuals):** there is **no glow field on species today**
  (verified). Add a client-side pulsing emissive (reuse `LampLight.cs` / `DarknessOverlay.cs`) — a warm
  amber point light that **pulses on a ~1s rhythm** (biology-true), not a static tint. Because the pulse
  phase is derived from the **deterministic tick + the swarm's stable id**, every client shows the same
  blink WITHOUT any sim/ledger change (display-only). Optional gorgeous upgrade: a **swarm-synchronized
  pulse** (all fireflies in a swarm blink together, *Pteroptyx*-style) — trivially deterministic since it's
  one tick-derived phase per swarm.
- **Blue/great** = colour + brightness variants (blue = cooler light, rarer; great = larger, brighter,
  slower pulse).

**(d) Role.** The night's headline ambient beauty; a catchable "jar of light" trophy. The single strongest
tie-in to the emissive/lighting work.

**(e) Visual.** Slow drifting `gliding` path low over water/grass at night; the emissive **pulse** is the
star — soft bloom, ~1s cadence, brief off-beats; catching one in a net = a little light going out. Day =
resting on foliage, unlit, not spawned.

## 4. Dragonfly (`dragonfly_blue`; sprites emperor/hawker) — the aerial hunter (the one predator)

**(a) Real.** The apex aerial hunter — an **~95% capture rate** (lions ~25%, sharks ~50%) achieved by
**predictive interception**, not a tail-chase: it computes a *future collision course* from the prey's speed
and heading (target-selective descending neurons), aided by forward-facing binocular eyes. Fast, darting,
territorial over water; capture success DROPS as prey gets bigger [DF-hunt].

**(b) Games.** AC dragonflies are "found near water bodies with notably fast movement patterns" [ACNH-bugs];
their darting speed makes them a harder, more prized catch than the drifting ambient bugs. They read as
"the fast jewel over the pond."

**(c) Spec (BUILT — a lead/telegraph polish).** `dragonfly_blue` already hunts: `predation.prey:
["wasp_common"]`, `strike_radius:3.0`, `strike_cooldown_ticks:120`, `kills_per_strike:1`,
`feed_per_kill:50`, `hunt_speed_mult:1.4`, `hunt_satiation_threshold:40`; `base_speed:2.8`,
`movement_style:"darting"`, small territorial groups (1–3), `flies_over_fences:true`, `net_size:"medium"`.
The authority runs the strike; the kill is relayed (`BUG_REMOVED`-class, `match.go:1131,1321`) — determinism
already handled by the built predation path (see `flying_pests_stingers.md`'s dragonfly note, and the sim
facts above).
- **Polish 1 — interception, not a chase:** when hunting, aim the surge leg at a **lead point** (prey pos +
  prey velocity × time-to-close) rather than the prey's current cell — biology-true and it *reads* as
  skill. Pure integer/fixed-point leg math → deterministic. This is the one behavioural add.
- **Polish 2 — perch-and-sally:** dragonflies perch on a reed/post, then dart out to hunt and return — a
  perch idle (zero-length leg on a `reed`/`mooring_post` occupant) between hunts, reusing the forage-pause
  mechanic. Gives the pond a still-then-explosive rhythm.
- **emperor/hawker** = faster/larger variants; `dragonfly_emperor` could add `prey:["wasp_common",
  "mosquito"]` if mosquitoes ship (a stronger pest-control ally).

**(d) Role.** The beautiful, *useful* predator — free pest control the player wants near the farm; also the
prize daytime catch (higher `sell_price:12`, medium net). Function-over-stats: it's the only ambient flier
that *removes a threat*.

**(e) Visual.** `darting` = long straight fast dashes with abrupt ~90° saccade turns (fly-like, real), near-
zero bob, hovering pauses; a bright strike flash on the intercept. Perch with wings held out on a reed tip.

## 5. Mayfly (sprites `mayfly_common`/`giant`) — the mating-swarm event (NEEDS species)

**(a) Real.** Adults **cannot feed** (vestigial mouthparts) and live **hours to a day** — the origin of
"ephemeral." They **mass-emerge synchronously** (predator satiation: overwhelm predators by all appearing at
once) and males form **vertical "dancing" swarms over a visual marker** (a tree, rock, bridge, the water) at
**late afternoon→dusk**; females fly in to mate, drop eggs on the water, and die [MF-bio].

**(b) Games.** The mass-emergence is inherently a *spectacle event* — the design analogue is Stardew's
seasonal critter flourishes and AC's time-gated rare bugs [SDV-critters][ACNH-bugs]: a brief, striking,
place-specific display that punctuates the calendar rather than a persistent ambient bug.

**(c) Spec (NEW species — cheap; leans entirely on existing knobs).** Add `mayfly_common` as a
`category:"swarm"` flier over water/stream, `movement_style:"gliding"`, `player_reaction:"ignore"`.
- **The dance = an amplified VERTICAL bob over a marker.** Reuse the swarm cohesion around a center
  (`swarm_radius`) but render a strong up-and-down bob (client, §C) so a dense cluster **bobs vertically in
  place** over a reed/rock/bridge — the readable mayfly signature. Server side it's a tight-radius wander
  swarm; the "vertical" is a client bob amplitude, display-only.
- **Ephemeral lifespan:** set `lifespan_secs` VERY low (minutes, not the firefly's 6000s) so they visibly
  live-fast-die — the built lifespan field already despawns them.
- **Emergence event (optional, deterministic):** gate a big synchronized spawn on the day/night tick
  (dusk) and/or season, so a stream periodically erupts in a swarm that lasts a short window then dies off —
  "predator satiation" as a scheduled spectacle. Tick-gated = free determinism.
- **`giant`** = larger, sparser, slower variant for the marquee shot.

**(d) Role.** Ambient *event* (time/place spectacle) + easy catch during the window. Zero threat; adds
temporal texture to a waterside zone.

**(e) Visual.** A shimmering column of gliding bugs **bobbing vertically** over the water at dusk, thinning
as the window closes; low golden light through the wings. The whole swarm winks out as lifespans expire.

## 6. Cicada (sprites `cicada_annual`/`periodical`) — the summer drone (NEEDS species)

**(a) Real.** Nymphs live **years underground** on tree-root sap; adults climb trunks, emerge, and males
**"sing"** a >90 dB chorus from the trees to attract females, living only 3–4 weeks. Periodical broods
emerge on **13- or 17-year** cycles en masse; annual cicadas appear every summer [CIC-bio].

**(b) Games.** AC cicadas sit **on tree trunks** in summer daytime, are **loud** (audio-first), and **flee
fast** if you approach carelessly — one of the "be slow or it's gone" catches [ACNH-bugs][NL-bugs]. They're
defined more by SOUND and PERCH than by flight.

**(c) Spec (NEW species — a PERCH-and-sing bug, barely any motion).** Add `cicada_annual` as a mostly-
**stationary perched** occupant-adjacent flier: `player_reaction:"curious"`/skittish, tiny `wander_radius`,
`catch_condition:"always"` but a high `catch_difficulty` / fast `flee_speed_mult` (the AC "creep or it
bolts" loop).
- **Perch verb:** parks on a tree occupant (zero-length leg on a `tree_*`), the dominant state — reuse the
  forage/perch pause. It only makes a short buzzing *flight* when startled, then re-perches.
- **The drone (client audio, gated day + summer):** the signature is a positional **buzzing SFX** that
  swells in the day heat and fades at dusk — gated on the day/night tick (day-active, the firefly's inverse)
  and optionally a summer season flag. Audio is display-only; no sim change.
- **`periodical`** = a rare **event brood**: a tick/season-gated mass emergence (the 17-year drama
  compressed to an in-game rare event), otherwise absent — the counterpart to the annual's every-summer
  presence.

**(d) Role.** Ambient *atmosphere* (the sound of summer) + a skittish daytime tree catch. Teaches "slow
down." Near-zero sim cost.

**(e) Visual.** Clinging to a trunk, wings folded, an occasional wing-buzz; a heat-shimmer + a swelling
drone SFX localized to wooded areas by day. Startle = a clumsy short buzz-flight to the next trunk.

## 7. Moth (sprites `moth_common`/`luna`/`atlas`/`brown`) — the lamp-drawn nocturne (NEEDS species)

**(a) Real.** Moths navigate by **transverse orientation** — holding a fixed angle to a *distant* light (the
moon). A nearby lamp breaks the trick: they can't hold the angle, so they **spiral inward in endless loops**
and tend to **dip down** as they close on the light (keeping the lit sky above) — a "catastrophic
navigational failure," not desire [MOTH-light]. Nocturnal; the spiral drains their energy.

**(b) Games.** AC moths are "active at night, attracted to artificial light sources like lamps"
[ACNH-bugs][NL-bugs] — the light-lure IS the spawn/find rule (place a lamp, moths come). The moth-to-lamp
image is one of the most legible ambient-bug behaviours in games.

**(c) Spec (NEW species — the light-lure is our forage machinery pointed at lamps at night).** Add
`moth_common` as a `category:"swarm"` nocturnal flier, `movement_style:"gliding"`, `player_reaction:
"ignore"`, `catch_condition:"always"`.
- **Moth-to-light = attraction, retargeted (deterministic, reuses built code):** put lamp/lantern occupant
  ids in `attractions_by_phase.feeding` and **gate the attraction to night** (tick). The swarm is drawn to
  the nearest lit lamp exactly as the butterfly is drawn to a flower — same `vision_range`/
  `attraction_strength`/leg machinery, no new sim system.
- **The spiral (client render, §C):** once "foraging" a lamp, the client renders an **inward spiral / endless
  loop around the lamp cell, dipping toward it** — display-only over the authoritative "sit near the lamp"
  legs. This is the marquee visual and costs no determinism.
- **Night gate + lamp dependency** make moths a *reason to place lamps* (and a firefly counterpart on the
  same night-tick): lamps become ambient-life magnets. `luna`/`atlas` = big showpiece rare variants (pale
  green luna, giant atlas), `brown` = the common drab one.

**(d) Role.** Nocturnal ambient beauty tied to player-placed light; a night catch. Pairs with fireflies to
make night worth being out in. Gives lamps a living purpose beyond illumination.

**(e) Visual.** `gliding` bumbling flutter that **spirals into any lit lamp** at night and loops there,
dipping; big soft wings (luna's tails, atlas's size) catch the lamp glow. Absent by day. Contrast the
firefly (self-lit, drifting) with the moth (unlit, chasing others' light).

---

# ≥4 SCORED candidates — flight-motion model
*How to make each species' flight FEEL alive on our leg-based sim. Axes (1–5): **aliveness ·
species-distinctness · determinism/perf (5 = safe/cheap) · dev cost (5 = cheap)**.*

| # | Model | Alive | Distinct | Det/perf | Dev cost | Verdict |
|---|---|:--:|:--:|:--:|:--:|---|
| **A** | **`movement_style` render class + client vertical BOB** — server emits ordinary wander legs; the client picks a flutter/dart/drift animation and a sine bob keyed off the existing `movement_style` string (`gliding`/`brownian`/`darting`). | 4 | 4 | 5 | 5 | **PICK (base).** Already the as-built hook (`species.go:111-113` — server never branches on it). Free, zero determinism cost, instantly per-species. |
| **B** | **Per-species SERVER wander params** — tune `base_speed`/`wander_radius`/`wander_change_rate` + leg length so the LEG PATH itself differs (butterfly = short frequent kinks; dragonfly = long straight dashes; bee = tight busy jitter; firefly/mayfly = slow drift). | 4 | 5 | 5 | 4 | **PICK (server half).** Integer legs → deterministic; makes paths genuinely distinct (not just the animation). Pure data tuning. |
| **C** | **Client display-only STEERING/noise overlay** — between authoritative leg waypoints the client adds a Reynolds-style smoothed wander / saccades / vertical bob / **moth spiral-to-lamp** / **firefly glow pulse**, never fed back to the sim. | 5 | 5 | 5 | 3 | **PICK (polish layer).** Where the beauty lives; because it's cosmetic it's determinism-FREE. Reynolds "constrained random walk" (retain heading + small displacements) is the recipe for smooth-not-twitchy [STEER]. |
| D | **Authoritative per-tick steering in the sim** — server runs full steering behaviors each tick per bug. | 5 | 5 | 3 | 2 | REJECT. Fixed-point steering is a determinism minefield and ×N per-tick cost, for a look C delivers client-side for free. |
| E | **Scripted spline / keyframed flight paths** (hand-authored). | 3 | 3 | 4 | 1 | REJECT. Doesn't scale to a living swarm; reads as canned/looping — the opposite of "alive." |

**PICK: A + B + C layered.** The server emits per-species-tuned wander legs (**B**) tagged with a
`movement_style` (**A**); the client renders them through a display-only steering/noise/bob overlay (**C**)
that adds the flutter, dart, drift, vertical bob, moth-spiral, and firefly pulse. **All sim state stays the
existing legs; every "alive" flourish is cosmetic → no new determinism surface.** D and E are rejected:
D pays determinism + perf for what C gets free; E doesn't scale. This matches the codebase exactly —
`movement_style` is *already* a client-only render key, and legs are *already* the only thing the sim
shares.

**Specials, mapped onto the pick:**
- **Moth-to-light / firefly-at-dusk / cicada-by-day** → attraction retargeting + a `tick % DayLengthTicks`
  gate (server, deterministic, reuses forage code + the free day/night clock).
- **Firefly glow** → client emissive pulse, phase from `tick`+swarm-id (display-only; the emissive/lighting
  cross-ref).
- **Moth spiral, mayfly vertical dance, dragonfly saccade** → client overlay (**C**), display-only.
- **Dragonfly interception lead** → the ONE server behavioural add (aim the surge at prey-lead point);
  integer leg math, deterministic.

# SOURCE TABLE
*Only sources actually read this session (WebFetch = full deep-read; WebSearch = multi-source synthesis).*

| Tag | Source | Read via | Key facts used | Confidence |
|---|---|---|---|---|
| **STEER** | Reynolds, *Steering Behaviors for Autonomous Characters* (red3d.com/cwr/steer/gdc99) | WebFetch (full) | Wander = retain heading + small random displacements constrained to a sphere ("constrained random walk"), NOT per-frame noise (twitchy); Seek/Arrival/Flocking/Path-Following defs. The recipe for smooth organic flight. | High |
| **ACNH-bugs** | Nintendo Life — *ACNH Bugs complete guide* | WebFetch (full) | Most bugs flee if you run → hold to creep slowly; wasps/scorpions chase instead; butterflies spawn in air + around flowers by day; cicadas on trees (summer day); moths at night on lamps; dragonflies near water, fast; fireflies near water at night, glowing. | High |
| **MOTH-light** | ZME Science — *Like a moth to the flame* | WebFetch (full) | Transverse orientation (fixed angle to a distant light); near lamp → **inward spiral / endless loops**; moths **dip down** closing on light; target the dark region beside the lamp; energy drain. | High |
| **SDV-critters** | Blog/Steam/forum + modding-wiki synthesis (Stardew critters) | WebSearch synthesis | Fireflies glow to enhance night ambiance (summer, non-interactive); butterflies decorative, wander a broad area around spawn near flowers by day; ConcernedApe added them "to make the game more lively." | Med-High |
| **FF-bio** | Science News Today / Schlitz Audubon / Nature (Aquatica) / Piedmont MG synthesis | WebSearch synthesis | Rest by day on foliage, glow at dusk; cold bioluminescence; species-specific patterns (spirals/J-loops) at ~1s intervals; males fly higher/brightest, females answer; *Pteroptyx* trees synchronize. | High |
| **DF-hunt** | onenaturalist / UC Davis Biology / Oxford ICB / NHM / Forbes synthesis | WebSearch synthesis | ~95% capture (vs lion 25%, shark 50%); **predictive interception** (computes future collision course via TSDN neurons), binocular eyes; success drops with prey size. | High |
| **MF-bio** | Malheur Friends / A-Z Animals / PestWhisperer / Animals Around The Globe synthesis | WebSearch synthesis | Adults can't feed, live hours-to-a-day; synchronized mass emergence (predator satiation); males form **vertical dancing swarms over a marker** at dusk; females enter to mate, drop eggs on water, die. | High |
| **CIC-bio** | Smithsonian / Britannica / Wikipedia / Nature.org synthesis | WebSearch synthesis | Years underground on root sap; climb trunks to emerge; males sing >90 dB chorus from trees; adults live 3–4 weeks; periodical 13/17-yr mass broods vs annual. | High |
| **B-fly-flight** | ResearchGate defense review / BBC Science Focus / ScienceABC / PMC hindwing study synthesis | WebSearch synthesis | Erratic zig-zag = predator evasion (unpredictable path); hindwings enable evasive maneuverability; toxic species fly straighter. | High |
| **B-fly-nectar** | AMNH / rcannon992 / Northern Woodlands synthesis | WebSearch synthesis | Flower constancy (learn + return to rewarding flowers); use colour/UV/scent to find flowers; nectar fuels flight. | Med-High |
| **NL-bugs** | GameSpot/Nintendo Life ACNH bug lists (cross-check) | WebSearch synthesis | Corroborates location/time gates: fireflies water+night, cicadas trees+summer-day, moths lamps+night, dragonflies water+fast. | Med-High |

*Marked lower-confidence:* the Stardew and biology-synthesis rows are WebSearch aggregations (not a single
primary deep-read); none is load-bearing beyond corroborating the three full WebFetch reads (STEER,
ACNH-bugs, MOTH-light). The two 403'd pages (entomologist.net Stardew guide; Nookipedia bug-catching) were
covered by the Nintendo Life full read + Stardew synthesis instead.

# Determinism notes
- **The whole flight model is determinism-neutral by construction.** Sim state = the existing
  `SWARM_SET_TARGET` legs (fixed-point). `movement_style` is client-only (`species.go:111-113`); the bob,
  flutter, saccade, moth-spiral, and firefly pulse are the client display overlay (candidate C) and touch
  nothing the sim reads. **No `frontier-sync` wiring needed for motion or glow.**
- **Day/night gates are FREE and deterministic.** Firefly-glow, moth-to-lamp, cicada-drone, and the mayfly
  emergence all gate on `tick % DayLengthTicks` (`match.go:47-51` — "the day/night cycle needs no extra
  netcode"). Same tick on every client → same gate. Use `setTimeOfDay` (`handlers_env.go:95`) to test.
- **Light-attraction reuses the built forage path.** Pointing `attractions_by_phase.feeding` at lamp
  occupants (moth) or host flowers (butterfly) is ordinary target selection — already deterministic; no new
  event. The night restriction is the only added condition.
- **Firefly glow phase must derive from shared inputs only.** Pulse phase = f(`tick`, stable swarm id) —
  both identical on every client → identical blink with ZERO ledger/snapshot cost. Do NOT seed it from a
  client-local RNG or wall-clock (that desyncs the *look*, though not the sim). A swarm-synchronized pulse
  is one phase per swarm; still free.
- **The dragonfly interception lead is the one sim-touching add** and must be integer/fixed-point (prey pos
  + prey velocity × ticks-to-close, all fixed-point) so the surge leg is bit-identical. The strike itself
  already rides the built, sync-safe predation path (`match.go:1131,1321`). Wire any change through
  `frontier-sync` + the `sim-determinism` gate.
- **New species (moth/mayfly/cicada) need `species.json` entries** to spawn at all (a `bugs.json` id
  without a species spec silently fails). Adding them is data + sprite (they already have sprites) via the
  `add-object` path; the AI is entirely reused knobs above — no new Go behaviour except the dragonfly lead.

# OWNER QUESTIONS (taste / scope — not guessable)
1. **Which "sprites-only" species do we actually promote to live bugs?** All of moth/mayfly/cicada +
   the butterfly/firefly/dragonfly/bee VARIANTS (monarch, luna, hawker, bumblebee…), or a curated subset?
   Each needs a `species.json` entry; the roster size is a content/scope call.
2. **Firefly glow — how much visual investment?** Minimum = a pulsing amber point light (reuse `LampLight`).
   Full = swarm-synchronized pulses + species colours (blue/great) + a soft bloom + "light goes out when
   caught." How far toward the *Pteroptyx* spectacle do we go, and is this bundled with the emissive/lighting
   work or a follow-up?
3. **Do moths REQUIRE a placed lamp, or also spawn ambiently at night?** Lamp-only makes lamps meaningful
   ("place light → life arrives") but means no moths until the player builds lighting; ambient-plus-lamp is
   softer. Which reads better for our night?
4. **Mayfly/periodical-cicada as scheduled EVENTS or always-ambient?** A dusk mayfly emergence and a rare
   17-year cicada brood are spectacle if gated to a window/season; always-on dilutes them. Do we have (or
   want) a seasonal calendar to hang these on, or keep everything day/night-only for now?
5. **Cicada = audio-first ambience — is positional bug SFX in scope?** The cicada's whole charm is the
   summer DRONE. Are we willing to add localized ambient SFX (also enables the firefly-quiet-night and the
   bee buzz), or should these ship silent for now?
6. **Dragonfly as pest control — how strong an ally?** Keep it to `wasp_common`, or let
   `dragonfly_emperor` also hunt mosquitoes/flies (a real farm-defense creature the player cultivates)?
   This nudges the farm toward an ecology the player *manages*.
7. **Catch difficulty curve.** Butterfly = trivial tutorial catch; should cicada/dragonfly be the
   "creep slowly or it bolts" skill catches (higher `flee_speed_mult` / `catch_difficulty`), giving the
   gentle roster its own mini progression? Or keep all ambient bugs easy and reserve difficulty for threats?
