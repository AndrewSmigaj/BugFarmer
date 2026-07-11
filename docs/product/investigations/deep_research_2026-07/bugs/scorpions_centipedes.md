# Bugs: scorpions & centipedes (ambush burrowers + segmented crawlers)

*Topic 2 of the 2026-07 bug-behaviour research. How to build the game's ground-dwelling AMBUSH and
SEGMENTED predators — scorpion (burrow-ambush, pincer-grab → tail-sting, venom DoT) and centipede /
giant_centipede (serpentine hunter, extended into a true segmented "follow-the-leader" body) — grounded in
real biology and how good 2D games do it, mapped to our deterministic swarm sim. Pairs with
`flying_pests_stingers.md` (aerial threats) and `../combat/03_challenge_and_effectiveness.md` (the shared
challenge framework).*

> **Provenance note (honesty).** The three raw files nominally tagged "scorpion" in
> `../_raw_recovered/bugs/` (`a2f63515…`, `a5e43c10…`, `abeb6d47…`) are actually the calm/subdual research,
> the centipede-cavern zone digest, and a persistence review — the dedicated scorpion biology agent died
> early (see `README.md`). Those raw files gave the deep **centipede sim + calm/subdual** grounding used
> below; **all scorpion behaviour here is fresh web research**, cited inline and in the source table.

## The core takeaways (the readable wins)
1. **Scorpion = the game's sit-and-wait AMBUSHER.** Real scorpions bury themselves, sense ground vibrations,
   and stay motionless until prey enters the kill zone — then *turn, dash, seize*. That "the ground itself is
   the threat" fantasy is a distinct enemy category we don't have yet (everything else patrols or wanders).
   Grounded builds exactly this: scorpions "submerge themselves in dirt… with only parts of their heads
   visible, then leap out to ambush." The **resurface** is the telegraph.
2. **Grab → sting is a two-stage COMBO, not one hit.** Biology: the scorpion seizes prey with pincers and
   *only stings if the prey is large/struggling* — otherwise it just holds and eats. ARK's Pulmonoscorpius
   grab "locks lone survivors in place and makes them vulnerable to its stinger." Map this to a **pincer-grab
   that roots/slows the player (stage 1) → a telegraphed tail-sting that lands venom (stage 2)** — the sting
   is escapable if you break the grab. Fair, readable, and it makes the scorpion a *controller* archetype
   (§03's "latcher"), not another crawler.
3. **Pincer size is INVERSELY tied to venom — and it maps 1:1 onto our three sprites.** "The bigger the claws
   the less toxic the sting; the smaller the claws the more toxic." Emperor scorpions have the largest
   pedipalps of any scorpion and an almost-harmless sting — "they prefer to use their pincers to crush and
   dismember prey" and *as adults don't sting to defend at all*. Bark scorpions have thin pincers and North
   America's deadliest venom. So `scorpion_emperor` = **crush/grab tank, weak venom**; `scorpion_bark` =
   **fragile, potent venom glass-cannon**; `scorpion_desert` (desert hairy) = the middle. That's
   function-over-stats variety for free, biologically true.
4. **Venom = a telegraphed damage-over-time BUILDUP, not burst.** Grounded's scorpion venom is a buildup
   meter; the two venom attacks "should be taken into high priority… without the antidote this can prove
   quickly lethal," countered by a **Scorpidote** brew. A DoT that you *cure/prevent with a consumable* fits
   our cozy tone (the danger is a resource drain, not a one-shot) and gives the alchemy/consumable economy a
   real customer.
5. **A true segmented body is a rendering trick, not new sim.** Terraria's worm bodies are pure
   "follow-the-leader": once the head passes a point, every segment must follow the same path. Our centipede
   head *already* emits a deterministic leg trail every client shares — so the visible body can be
   **reconstructed from that trail at fixed offsets with ZERO new sim state and perfect sync**. The
   expensive version (independent hittable/splitting segments) is reserved for a boss.

---

## Engine facts this doc builds on (verified against code, 2026-07-11)
- **Movement = legs.** All bug motion is `SWARM_SET_TARGET` "legs" (origin → target → speed, fixed-point),
  emitted by the authority and replayed identically on every client. Nothing view-scoped feeds the sim.
- **Strikes = detect-don't-remove.** The authority runs the hit test and relays the observable via a
  `BUG_REMOVED`-class event / `applyBugAttackToPlayer` (`handlers_player.go`); clients never decide a hit.
- **Flee/aggro = `PLAYER_CELL_ENTER`** + per-tick range checks (`nearestPlayer`).
- **Collision = zone-wide `blocks_bugs` map.** `state.IsBlockedForSpecies(x,y,species)` + `RaycastClamp`/
  `RaycastClampWithBlock` clamp every leg at fences/water/stone. Centipedes are ground-bound
  (`flies_over_fences:false`).
- **The centipede already exists** as `centipede_garden` (`species.json`): `category:"individual"` = a
  "swarm-of-one" ground crawler with a per-tick **ActionState machine** that runs BEFORE the think gate
  (`world/centipede.go`):
  `windup (8t / 0.8s telegraph freeze — a zero-length leg + a "windup" telegraph broadcast) → surge (≤25t,
  base_speed ×4.8 ≈ 7.7 u/s, OVERSHOOTS 3.5 cells past the aim) → bite (dmg 2, range 1.6, per-tick with a
  line-of-sight ray so it can't bite through a fence) → recover (20t straight backoff, 5s cooldown) :
  turnaround (banked arc of ≤3 chained short legs, re-press on a 1.5s cooldown)`. Plus a **gnaw** state that
  chews wooden fences (16s each; stone stops it) and a serpentine **wander** (heading-constrained ±60° short
  4–7-cell legs with a dead-end escape hatch). `net_size:"trap_only"` (no net catches it → subdue-and-trap).
  Base speed 1.9, max_hp 6, wander_radius 20.
- **The centipede is already calmable** — `condition_tools:{"calm":90}`; `swarmSubdued(swarm,species)` aborts
  windup/surge/gnaw-start and stops a mid-gnaw (the smoke-and-walk-past loop from the §C subdual design).
  **Reuse this identical hook for the scorpion.**
- **IMPORTANT — segments are art, not sim.** The sprites `centipede_head/body/tail_a/b` EXIST but the sim
  renders the centipede as a SINGLE moving center. True segmented follow-the-leader body movement is **not
  built** — it is the main new design here (§ segmented-body candidates).
- **Scorpion: sprites only, NO species yet.** `bugs.json`: `scorpion` (14×14, speed 0.7, catch_diff 4,
  value 80, zone `scorpion_rocks`), `scorpion_bark` (16×16, tier easy, catch_diff 1), `scorpion_desert`
  (16×16, medium, catch_diff 2), `scorpion_emperor` (16×16, elite, catch_diff 4). No `species.json` entry,
  no AI. Everything scorpion below is a from-scratch spec.

---

# Per-species specs

Each spec: **(a) real behaviour · (b) how games do it (cited) · (c) BEHAVIOR SPEC mapped to our sim ·
(d) threat/role · (e) fair telegraph + counterplay.**

## 1. Centipede (`centipede_garden`) — the serpentine hunter, given a real body

**(a) Real.** Centipedes are fast, many-legged ground/pole crawlers; the body writhes as an S-curve as the
head leads. Predatory, venomous forcipules, prefers dark/damp.

**(b) Games.** *Terraria* worm family = "follow-the-leader": "once the head passes a given point, every body
segment must follow," so the player can stand beside the body and hit each segment as it passes; destroying a
mid-segment splits the worm. *Rain World* centipedes are segmented crawlers that "outpace most creatures…
and climb background walls," with a signature **alternating-vision** quirk — each of the two heads sees on
alternate frames, so a player moving at a steady pace catches them "in a consistent loop of starting and
stopping" (an exploitable, readable tell); big ones grab prey and deliver an electric shock, small ones are
passive. Behaviour scales with size.

**(c) Spec (mostly BUILT — the extension is the visible body).** Keep the entire existing ActionState
machine. Add a **cosmetic segmented body** derived from the head's leg trail (see the segmented-body PICK):
the client samples the head's recent deterministic path at fixed arc-length offsets and draws
`centipede_body_*` / `centipede_tail_*` there. No new sim state, no ledger event, bit-identical on every
client because every client already holds the same leg history. Optional data field
`segment_count` (default e.g. 4) on the species so `giant_centipede` can be longer. The serpentine wander +
surge already produce exactly the S-curve trail this needs — the body "just" renders onto it.
- *Rain-World alternating-vision homage (optional, cheap):* the existing 0.8s windup freeze already gives the
  "start-stop" readability tell; no extra work needed to echo it.

**(d) Role.** Grunt/Bruiser hybrid — the mid-cave melee threat that also *destroys the player's fences*
(unique pressure). trap_only makes it the tutorial for the subdue-and-trap loop.

**(e) Telegraph/counterplay (built).** 0.8s hiss/windup freeze before every surge; overshoot means a
direction-change dodges it; **stone walls stop it, wood gets gnawed** (the "build in stone" lesson); smoke
calms it (walk past). Fair today.

## 2. `giant_centipede` — the flanker boss (segmented, envenomed)

**(a/b) Real/games.** The Rain-World "Overgrown Centipede" (13–17 segments, ~4× the protagonist) is the model
— a genuinely dangerous predator that grabs and shocks; Terraria's long worms let you attack the body but
punish standing in the path. Bigger = scarier density, same bounded DPS (§03).

**(c) Spec (NEW, boss-tier — reuse the centipede machine, turn three dials).**
1. **Longer body:** `segment_count` ~8–12 via the same cosmetic path-sampling → reads as a giant.
2. **Envenomed bite:** its `bite` applies the shared **venom DoT** status (same event the scorpion uses) on
   top of contact damage — the one centipede that leaves a lingering cost, so you *want* to avoid the pass,
   not tank it.
3. **Faster flanker:** higher `centSurgeSpeedMult` / shorter cooldown so it presses harder; the turnaround
   arc makes it circle rather than retreat.
4. *(Optional escalation — hittable/splitting segments):* promote the body from cosmetic to authoritative
   (segmented-body candidate **B**) so a spear can sever segments and a cut mid-body splits it into two
   shorter centipedes (Terraria-style). Big feature; gate behind "do we want a real boss fight."

**(d) Role.** Mini-boss / Enforcer — the Centipede Cavern's apex; teaches venom-management and reach weapons.

**(e) Telegraph/counterplay.** Same windup freeze (longer, more legible at boss scale); venom telegraphed by
a distinct bite flash + the buildup meter; countered by antidote consumable, stone chokepoints, and reach
weapons that hit the head without entering bite range.

## 3. Scorpion — generic (`scorpion`) — the burrow ambusher

**(a) Real.** Sit-and-wait nocturnal ambush predator; buries in a burrow by day, senses ground vibration and
prey distance/direction, then "turns, runs to the prey, and seizes it," stinging *only* if the prey is large
or struggling — otherwise just holding it in the pedipalps. Defensive posture = raised claws + arched tail;
fluoresces blue-green under UV.

**(b) Games.** *Grounded* Northern Scorpion: submerges in dirt with only the head showing, emerges when a
player gets "extremely close"; a **Burrow Strike** follows the player underground (shown by dirt particles)
then surfaces into a tail sting; attacks are a claw combo capped by a **stinger strike that adds Venom
buildup**; classified "Angry / aggressive on sight," short detection range. *ARK* Pulmonoscorpius: a
**grab attack locks a lone target in place**, then the stinger delivers a paralytic (torpor) — the grab-then-
sting combo.

**(c) Spec (NEW species; `category:"individual"`, reuse the centipede ActionState scaffold + add states).**
- **State `burrowed` (default/idle):** the scorpion parks in place, sets a server flag `Burrowed=true`,
  broadcast as a telegraph so clients render only a dirt-mound / head-nub. While burrowed it emits **no
  legs** and is **not catchable / not a bite hazard** (it's "underground"). This uses only a server flag +
  a cosmetic broadcast — deterministic, no collision change needed. (We do NOT need to edit `blocks_bugs`:
  burrow is a *visibility/armed* state, not a walkable-terrain change.)
- **Trigger → `emerge` (telegraph):** when `nearestPlayer` within `scorpTriggerRange` (~4) — the resurface.
  A ~0.6–0.8s emerge freeze (zero-length leg + "emerge" telegraph broadcast, exactly like the centipede
  windup). This is the fair tell: you see the ground erupt before it can hit you.
- **`pincer_grab` (stage 1):** a short fast lunge leg (like a shortened centipede surge, overshoot small) →
  on contact `applyBugAttackToPlayer` for light damage AND applies a brief **GRAB status** to the player
  (root or heavy-slow for ~0.8–1.2s, authority-applied + relayed — same class as an attack effect, so it
  syncs). No venom yet.
- **`tail_sting` (stage 2, the combo):** immediately after a landed grab, a telegraphed sting windup (~0.5s,
  a distinct "sting" telegraph) → sting → applies the **venom DoT buildup**. If the player breaks the grab
  (see counterplay) before the windup completes, the sting whiffs. Sting-on-grab only (biology: sting the
  thing that struggles).
- **`burrow_strike` (reposition/pursuit):** after a completed combo, or if the player flees past
  `scorpDeAggroRange`, the scorpion re-enters `burrowed` and **repositions underground** toward the player
  over a couple of hidden legs (Grounded's underground follow — rendered as travelling dirt particles, the
  scorpion sprite hidden), then re-emerges. Determinism: the "underground" legs are ordinary authority legs
  with the sprite hidden by the `Burrowed` flag; the dirt-particle trail is cosmetic-from-legs.
- **Venom DoT — the shared status.** Authority applies a `venom` buildup meter to the player; at/over
  threshold it **ticks integer damage on a fixed cadence** (e.g. 1 dmg every N ticks for M ticks) and decays.
  Because the authority owns the tick schedule and relays it as a player-status event (NOT per-client
  arithmetic), it is deterministic and sync-safe — it rides the ledger like any relayed strike. This is the
  same status `giant_centipede` reuses.
- **Calmable:** give it `condition_tools:{"calm":…}` so `swarmSubdued` no-ops `emerge`/grab/sting (smoke a
  scorpion nest and harvest safely) — free reuse of the built subdual hook.

**(d) Role.** Controller / Ambusher (§03 "latcher") — the first enemy that *holds* you and punishes standing
in the open near disturbed ground. Distinct rhythm (long dormant, sudden burst) breaks up a mixed swarm's
dodge-timing.

**(e) Telegraph/counterplay.** The **resurface emerge freeze** is the primary tell (you always get warning
before the first grab); the sting has its own windup; venom is a visible buildup meter countered by an
antidote consumable (Scorpidote-style) and by *not* lingering on disturbed dirt. **Grab counterplay:** a
mash/dodge to break free, or the grab auto-releases after its short duration — never an inescapable lock
(the §03 fairness rule: retreat/escape must always exist). Bark's fast surface variant (below) trades the
burrow for a shorter, more frequent telegraph.

## 4. `scorpion_bark` — the glass-cannon (thin pincers, potent venom)

**(a/b) Real/games.** Arizona bark scorpion — thin pincers, North America's deadliest venom; small claws are
"a warning sign a scorpion relies on its venom more than crushing." Fast, climbs, less reliant on ambush.

**(c) Spec.** Small (16×16), fragile (low max_hp, catch_diff 1 = easy net-catch when subdued), **surface
patroller** rather than a burrower (skip/shorten the `burrowed` state → cheaper "attack pattern D"): a
centipede-like telegraphed sting-lunge with **no pincer-grab** but **high venom DoT** on the sting. Weak
direct damage, dangerous poison. Fast base_speed.

**(d) Role.** Emphasizer/Swarm-adjacent — comes in small numbers, teaches venom-management; the antidote's
main customer. Cheap to build (a centipede-machine reskin minus burrow/grab, plus venom).

**(e) Telegraph/counterplay.** Short sting windup + a bright venom tell; kill it fast (low HP) or catch it
(easy net once calmed); antidote negates the poison. Its *speed* is the threat, not its bite.

## 5. `scorpion_desert` (desert hairy) — the balanced burrower

**(a/b) Real/games.** Large desert-hairy scorpion — stout pincers, moderate venom, classic desert
burrow-by-day ambusher (the A-Z/biology "desert scorpions dig burrows to escape heat, hunt at night").

**(c) Spec.** The **canonical burrow-ambusher** (the full generic §3 pattern), middle stats: medium grab,
medium venom, medium HP, catch_diff 2. The "default" scorpion players learn the archetype on.

**(d) Role.** Bruiser/Controller — the standard desert-zone threat.

**(e)** As §3: emerge-freeze tell, grab→sting combo with escapable grab, moderate venom curable by antidote.

## 6. `scorpion_emperor` — the crush tank (huge pincers, mild venom)

**(a/b) Real/games.** Emperor scorpion — the largest pedipalps of any scorpion, "crush and dismember prey…
as adults don't use the sting to defend at all," almost-harmless venom, docile, burrows deep (termite
mounds up to 6 ft), fluoresces under UV. The pincer-vs-venom inverse taken to its extreme.

**(c) Spec (attack pattern B — grab/crush-focused).** Elite (catch_diff 4), high max_hp = the **tank**. Its
attack is **pincer-grab → CRUSH** (a heavy melee slam that does real burst damage), NOT a venom combo — the
grab is stronger/longer and the sting is minimal-to-absent. Slow, deliberate, high threat when it connects.
A defensive **claws-up blocking posture** (Grounded's scorpion "shields its face with its claws, immune to
light frontal attacks; charged attacks interrupt") maps cleanly to a **frontal-armor state**: light hits
bounce, only a heavy/charged weapon or a flank hit lands — a reach/positioning puzzle, not a stat sponge.

**(d) Role.** Tank / Enforcer — demands the heavy weapon or flanking; the elite catch (value trophy).

**(e) Telegraph/counterplay.** Big slow grab windup (very legible); the block-posture teaches "hit it from
behind / charge the attack"; low venom means the danger is the *slam*, dodgeable on its long tell. UV-glow
in dark caves as an ambient pre-telegraph (you see it before it sees you).

---

# ≥4 SCORED candidates — segmented-body movement model
*The visible centipede/worm body. Axes (1–5): **looks-right · determinism/perf · dev cost (5 = cheap) ·
fits our leg system**.*

| # | Model | Looks | Determinism/perf | Dev cost | Fits legs | Verdict |
|---|---|:--:|:--:|:--:|:--:|---|
| **A** | **Cosmetic path-sampled body** — client reconstructs `body/tail` sprites by sampling the HEAD's existing deterministic leg trail at fixed arc-length offsets. Zero sim state, zero new ledger event. | 5 | 5 | 5 | 5 | **PICK (base centipede + giant).** The body rides the trail the client already renders; identical on every client because the leg history is identical; adds nothing to sim cost. |
| B | **Authoritative distance-constraint chain** — each segment is a sim entity that chases the one ahead at fixed spacing; server emits a leg per segment; segments are hittable and a mid-cut splits the worm (Terraria). | 5 | 3 | 2 | 4 | **PICK for a BOSS only.** The only way to get hittable/splitting segments, but ×N legs per centipede, ×N collision, and real determinism surface. Reserve for `giant_centipede`/matron if we want a true segmented boss. |
| C | **Authoritative breadcrumb buffer** — head records a position-history ring buffer each tick; segment *i* reads `history[i·lag]`; buffer persisted + synced. | 4 | 3 | 3 | 3 | Reject vs A: same look as A but pays sim state, persistence, and late-join snapshot cost for a purely visual result. A gets the identical look for free client-side. |
| D | **Loose multi-swarm "knot"** — N independent swarm-of-one centipedes tethered near one center (reuse existing knot/merge). | 2 | 4 | 4 | 5 | Reject as a *body*: reads as a clump of separate bugs, not one segmented animal. Fine as the existing "knot of centipedes" flavour, not as segments. |
| E | **Verlet/rope physics chain** (spring-coupled segments). | 5 | 1 | 2 | 2 | Reject. Best-looking writhe but floating-point springs are a determinism minefield and don't ride legs at all. |

**PICK: A for all normal centipedes and the giant's visual body; B is the opt-in escalation only if we
decide `giant_centipede` should have severable, splitting, individually-hittable segments (a real boss
feature).** Rationale: A delivers the Terraria "follow-the-leader" look with *zero* determinism/perf/persist
cost because our head already emits the shared trail; segments become gameplay objects only when the design
actually needs to hit them, and only then do we pay B's price — on exactly one species.

# ≥4 SCORED candidates — scorpion attack patterns
*Axes (1–5): **threat · fairness/readability · determinism fit · dev cost (5 = cheap)**.*

| # | Pattern | Threat | Fair/readable | Determinism | Dev cost | Verdict |
|---|---|:--:|:--:|:--:|:--:|---|
| **A** | **Burrow-ambush → resurface → pincer-grab → tail-sting (venom) combo** — the full fantasy (generic/desert). | 5 | 4 | 4 | 3 | **PICK (marquee, desert/generic).** Distinct ambush rhythm; the resurface + grab + sting each telegraph; grab is escapable; all events are authority-relayed (legs + strike + a venom-status event). |
| **B** | **Grab → CRUSH slam + block-posture, minimal sting** — big-pincer tank (emperor). | 4 | 5 | 5 | 3 | **PICK (emperor variant).** Biology-true (huge pincers, no venom); the frontal-block posture is a positioning puzzle, not a sponge; pure melee = trivially deterministic. |
| **D** | **Surface telegraphed sting-lunge, high venom, no grab/burrow** — fast glass-cannon (bark). | 3 | 5 | 5 | 4 | **PICK (bark variant).** Cheapest (a centipede-machine reskin + venom); its speed + poison are the threat; very readable. |
| C | **Ranged venom-spit / blind debuff.** | 4 | 3 | 5 | 3 | Reject for scorpion — that's the bald-faced-hornet niche (`flying_pests_stingers.md`); a spitting scorpion isn't the fantasy and would blur the two enemies. |
| E | **Instant grab+sting, no telegraph.** | 5 | 1 | 5 | 5 | Reject — the "impossible ambush" anti-pattern; an unseen one-shot from the ground is unfair, not scary. |

**PICK: A (desert/generic marquee) + B (emperor tank) + D (bark cannon)** — three biologically-grounded
patterns that give the four sprites genuine functional variety (controller / tank / cannon) off one shared
scaffold (the centipede ActionState machine + a shared venom-DoT status + the burrow flag).

---

# SOURCE TABLE (only sources actually read)

| # | Source | Read via | Key facts used | Confidence |
|---|---|---|---|---|
| 1 | Grounded Wiki — *Northern Scorpion* | WebFetch (full) | Submerge-in-dirt ambush (head visible); emerge on proximity; Burrow Strike = underground follow (dirt particles) → tail sting; claw combo + stinger add **Venom buildup**; block-posture immune to light frontal hits, charged attacks interrupt; "Angry / aggressive on sight," short detection. | High |
| 2 | GamesRadar / PCGamesN — *Grounded 2 Northern Scorpion strategy* | WebSearch synthesis | Venom attacks = high priority, "quickly lethal" without antidote; burrow strike has little telegraph; parry/stun counterplay; **Scorpidote** cure brew. | Med-High |
| 3 | ARK Wiki — *Pulmonoscorpius* | WebSearch synthesis (page itself 402'd) | Grab attack **locks a lone target in place** → stinger; paralytic neurotoxin (torpor); venom sacs in pincers. | Med (page not directly fetched — mark grab-lock detail corroborated by ARK community, unverified in primary) |
| 4 | A-Z Animals / biology synthesis — *Scorpion* | WebSearch synthesis | Sit-and-wait nocturnal ambush; sense ground vibration + prey distance/direction; turn-run-seize; **sting only large/struggling prey**, else hold in pedipalps; desert burrow by day. | High (multi-source agreement) |
| 5 | Wikipedia — *Emperor scorpion* | WebFetch (full) | Largest pedipalps of any scorpion; mild sting; adults "don't use the sting to defend… prefer pincers to crush and dismember"; burrows deep; **UV fluoresce**; vibration-sensing hairs. | High |
| 6 | A-Z Animals blog + Quora synthesis — *pincer-vs-venom inverse* | WebSearch synthesis | "Bigger claws → less toxic sting; smaller claws → more toxic"; bark scorpion thin pincers + deadliest NA venom; emperor mild. | Med-High (popular-science framing of a real ecological trade-off) |
| 7 | Terraria Wiki — *Worm AI* / *Eater of Worlds* | WebFetch + WebSearch | Follow-the-leader: once head passes a point every segment follows; segments hittable; mid-segment death **splits** the worm; variable segment count. (Wiki does NOT document the internal follow algorithm — implementation inferred.) | High for behaviour; **impl details unverified** |
| 8 | Rain World Wiki — *Centipedes* | WebSearch synthesis (miraheze 403/402'd) | Segmented, fast crawler + wall-climb; **alternating-vision** start-stop exploit; grab + electric shock; behaviour scales with size (small passive → large predator; Overgrown 13–17 segments). | Med (page not directly fetched; wiki-summary) |
| 9 | GameMaker/Unity dev-community threads — *worm boss segments* | WebSearch synthesis | Two canonical follow methods: **each segment chases the one ahead at fixed spacing** vs **breadcrumb position-history**; trail-particle tutorials differ from body-follow. | Med (informal but consistent across threads) |

**Marked unverified:** ARK grab-lock specifics (#3, page paywalled), Terraria's internal segment algorithm
(#7, not in wiki), Rain World details (#8, not directly fetched). None is load-bearing for our PICKs — the
segmented-body PICK (A) derives from our own leg system, and the scorpion combo is corroborated across
Grounded (#1/#2) + biology (#4/#5).

# Determinism notes (segmented movement + scorpion, specifically)
- **Segmented body (PICK A) is display-only → trivially deterministic.** It reads the head's already-shared
  leg trail; it writes nothing to the sim, emits no ledger event, and needs no late-join snapshot field. Two
  clients draw identical segments because they hold identical leg histories. **No `frontier-sync` wiring
  needed for the base body.**
- **If we ever adopt PICK B (hittable/splitting boss segments):** each segment becomes authoritative sim
  state and MUST go through `frontier-sync` — segment positions/HP in the late-join snapshot, splits as a
  spawn/split ledger event, and every segment leg fixed-point. This is a real determinism surface; keep it
  to one boss species and test with the sync-harness + `sim-determinism` gate.
- **Scorpion burrow = a server flag, not a collision edit.** `Burrowed` is authoritative boolean state
  broadcast as a telegraph; the sprite-hide + dirt particles are cosmetic-from-flag. Do NOT mutate the
  zone-wide `blocks_bugs` map for burrow (that would be a shared-collision change other bugs read → a
  determinism and gameplay hazard). The scorpion's underground repositioning uses ordinary authority legs.
- **Venom DoT must be authority-scheduled, not per-client.** The buildup meter, the integer per-tick damage
  cadence, and decay all live on the server and relay as a player-status event (like `applyBugAttackToPlayer`
  relays a strike). No client computes venom damage locally — that would desync. Fixed-point / integer ticks
  only. This IS a new sim input → wire it via `frontier-sync` (one new relayed status event, reused by both
  the giant centipede and every venomous scorpion).
- **Grab/root is the same class as an existing attack effect** — authority applies + relays it; the
  client-side break (mash/dodge) sends an intent the authority resolves. Never let the client decide the
  release locally.

---

# OWNER QUESTIONS (taste / scope — not guessable)
1. **Do we want a true segmented BOSS (PICK B), or is the cosmetic body (PICK A) enough?** A gives every
   centipede a great-looking follow-the-leader body for free. B adds hittable/severable/splitting segments —
   a whole boss feature (and a determinism surface) — for exactly one creature (`giant_centipede`/matron).
   Ship A now; is B a "later" boss goal or out of scope?
2. **How lethal is venom in a cozy game?** A DoT-buildup that's a *resource drain you cure with an antidote*
   (Grounded's Scorpidote model) vs. a mild scary-but-survivable tick. Where on the cozy↔tense axis? (This
   also decides whether the antidote/alchemy line is a required counter or a convenience.)
3. **Is the pincer/venom variant split good?** Proposed: emperor = crush tank / weak venom; bark = fast
   glass-cannon / potent venom; desert = balanced burrower; generic = the archetype. Biologically true and
   gives real functional variety — but it means three distinct AI behaviours, not one reskin. Approve, or
   collapse to one scorpion pattern with stat tweaks?
4. **Grab-lock: hard root or heavy slow?** ARK-style *can't-move-until-you-break-free* is tense but risks
   feeling unfair in a cozy game. A heavy slow + a quick escape mash is gentler. Which?
5. **Where do scorpions live and when?** Only `scorpion_rocks`/desert zones, or also deep caves alongside
   centipedes? Nocturnal-only (day = burrowed/safe) à la real behaviour + our day/night, or always-on?
6. **Do we build a scorpion NEST / ambush field** (several burrowed scorpions the smoker calms for a safe
   harvest, reusing the nest+smoker loop), or are they lone ambushers scattered in the terrain?
