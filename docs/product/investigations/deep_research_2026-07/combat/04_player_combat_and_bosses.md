# Player-side combat, bosses & co-op — research findings

*Topic 4 of the 2026-07 combat research. The PLAYER half of the loop. `01_melee_enemy_ai.md` and
`03_challenge_and_effectiveness.md` research ENEMY AI (telegraphs, attack-token pacing, threat director);
but combat is two-sided and our player has almost no defensive kit, so those enemy tells have nothing to
counter WITH. This doc researches the player's defensive verbs, weapon movesets/feel, boss structure, co-op
combat, and the netcode note — for a deterministic, server-authoritative 2D top-down cozy game.
Deep-read sources in the table below; pairs with `03`'s "Reality check — our player-side combat kit".*

## Verified project state (do not re-derive)
- Player has weapon **primary/secondary** movesets: `MeleeController.TryHandleClick("primary"/"secondary")`
  + a `moves` block per weapon in `items.json` (every weapon has a `secondary`). Hits are **server-validated**.
  A procedural `PlayerToolAnimator` renders the swing (contact-frame animator + camera kick already exist).
- **NO dodge/roll/dash, NO block, NO parry, NO i-frames.** Movement is plain walking.
- 2D top-down MULTIPLAYER (Nakama), deterministic server-authoritative bug sim.

## TL;DR
The single highest-leverage add is a **dodge/roll with a brief startup i-frame window** — it's the verb the
whole "telegraph → sidestep → punish the recovery" loop from `01`/`03` needs to become fair. Model it on
**Enter the Gungeon** (i-frames on the *first half*, vulnerable + committed on the recovery half) so it stays
skill-expressive, not a spam-immunity button. Layer a **Zelda-style "perfect dodge" reward** (dodge on the
telegraph → a brief counter window) on top later for depth. Keep the existing primary/secondary as a
**light/heavy** pairing with **early-exit combo windows**, and lean into the **contact-frame hitstop + camera
kick we already have** (3–5 frame freeze, capped, scaled by hit weight). Bosses = the giant-hornet raid as a
**telegraph-dense, multi-phase, checkpointed arena fight**. Co-op = **shared threat table (no friendly fire),
a downed/revive state, and frequency-scaled (not stat-scaled) difficulty by player count**.

## Source table (deep-read)

| Source | Concrete technique / data | Relevance to us |
|---|---|---|
| **Enter the Gungeon Wiki — Dodge Roll** (enterthegungeon.wiki.gg) | Roll ≈ **0.7 s** total; **i-frames on the first half only**, vulnerable on the second half; **committed** (can't change direction mid-roll, 8-dir on kb / 360° on pad); roll deals 3 contact dmg; sliding a table gives faster recovery (shorter than a full roll) | The canonical fair dodge: invuln burst + a punishable recovery tail. The model to copy. |
| **Hades (Steam/community) — Dash** | i-frames near **startup into the middle** of the dash, **late part punishable**; using cast/attack mid-dash with most weapons **disables the i-frames for the rest of the dash**; the hold-to-*sprint* has **no** protection | Confirms the "invuln at the front, commitment at the back" shape; and that acting during the dodge should cost the invuln. |
| **Hyper Light Drifter (wiki/community)** | Dash **originally had NO i-frames** (pure spacing/skill), patch added them, later patch **reduced** them "for fairness while maintaining challenge"; **chain-dash** (3 dashes, then faster cadence — timed, not mashable); **can't attack while dashing** except a dash-stab | Shows i-frame count is a live fairness dial; and that a pure-spacing dodge is viable but harsh — i-frames make it cozy-fair. |
| **Sekiro Wiki — Deflection** (fextralife) | Parry window **12 frames (0.2 s)** by default; **shrinks to 4 or even 0** frames if you spam the button; success **negates all damage + builds enemy Posture + staggers** → counter window; **too early = a plain Guard** (chip, no reward); Posture damage **scales up in a flurry** | The parry archetype: highest skill ceiling, highest reward; "too early degrades to block" is a great fail-soft. Probably too spiky for our default cozy verb. |
| **Zelda: BotW — Perfect Dodging / Flurry Rush** (Game8, Zelda Wiki) | Backflip/side-hop **right before** the hit → time slows → a free multi-hit flurry; must dodge **perpendicular** to the attack's axis; too early/late = no bonus | A dodge that *reads the telegraph* and rewards it with offense — the cozy-friendly way to add a skill ceiling without a punishing parry. |
| **Playtank — "Building Systemic Melee"** (playtank.io) | Attack = **startup(telegraph) → active(e.g. frames 78–94, weapon "on") → recovery**; **combo string window** (e.g. frames 94–110 lets you chain a 2nd attack); weapon **weight** distinguishes quick vs "haymaker" heavies; knockback = "balance" damage that makes the enemy fall | The frame-window recipe for making our primary/secondary feel like a real light/heavy combo. |
| **Sakurai, "Thinking About Hitstop"** (Source Gaming translation) | On a hit **both parties freeze** to emphasize impact; duration **scales with damage but is capped**; **per-attack modifiers** (Marth's tip = more hitstop, rest of blade less); polish layered on: decaying vibration, imperceptibly-slow attacker drift | Directly tunes our existing contact-frame animator: cap the freeze, scale by hit weight, add a decaying shake. |
| **"The Juice Factor" / hitstop explainers** (hackread; Ahmad Mohammadnejad) | A sword hit freezes **3–5 frames** so the brain registers impact — "cutting through bone, not air"; **hitstop ≠ hitstun** (hitstun is the victim's reaction state) | Concrete numbers for our hitstop; separates the freeze (feel) from the enemy flinch (readability, see `01`). |
| **gamedesignskills / itch.io — Boss design** | Fairness via **telegraphing** (visual+audio+environment); **phases** for escalation, each **distinct**; the fight should **teach during it**, win = understanding not more potions; **arena/environment** forces spatial play; long fights **drag without variation**; presentation (music) is part of the boss | The giant-hornet raid blueprint: distinct telegraphed phases in a reactive arena. |
| **Co-op: Game Developer "Co-op Revive Mechanics"; designthegame Co-op vs PvP** | Revive = reach the downed ally + channel **in contact range**; "Second Wind" **costs the reviver's health**; generous revive = less frustration / strict = more tension; alternatives to the cross-map-revive chore: **teleport-to-ally, life-trade remote revive, consumable/self-revive with diminishing returns**; **friendly fire** = tactical caution vs frustration tradeoff; scale challenge by player count (**linear vs emergent**) | The downed/revive + friendly-fire + scaling decisions for our raid. |

## Minimal player kit to add FIRST

Combat is two-sided; the enemy telegraph→recovery loop only pays off if the player can *act on the read*.
The **load-bearing prerequisite** (from `03`) is one defensive verb. In priority order:

1. **Dodge/roll with startup i-frames** — THE prerequisite. A short committed burst; invulnerable on the
   first ~half, vulnerable + recovering on the tail (Gungeon shape). This is the thing every enemy tell in
   `01`/`03` is designed to be answered by. Build this first, alone if need be.
2. **Light/heavy feel on the existing primary/secondary** — no new verb, just tune the two moves we already
   have into a readable light (fast, small flinch) + heavy (committed, stagger/knockback) pair with an
   **early-exit combo window** (Playtank), and lean on the **hitstop we already have** (cap it, scale by weight).
3. **(Later, optional) a reactive reward** — a Zelda-style "perfect dodge → brief counter/flurry window", OR a
   Sekiro-style deflect on a chosen weapon, for players who want a skill ceiling. NOT needed for fairness;
   it's the depth layer once #1 exists.

Do **not** ship "harder enemies" before #1: without a dodge, "harder" can only mean more unavoidable damage —
the unfair path every source in `03` warns against.

## Scored candidates — the defensive verb

Axes (1–5, higher = better): **fairness-enabling** (does it make telegraphed threats answerable?) ·
**fits-cozy** (approachable, low-punish, not twitchy) · **dev/netcode cost** (higher = cheaper/easier in our
server-authoritative deterministic model) · **skill ceiling** (room to get better without being mandatory).

| Candidate | Fairness | Fits-cozy | Dev/netcode (cheap=high) | Skill ceiling | Verdict |
|---|:--:|:--:|:--:|:--:|---|
| **A. Dodge-roll w/ startup i-frames** (Gungeon: invuln first half, committed vulnerable tail) | 5 | 5 | 4 | 4 | **PICK.** Directly answers every telegraph; i-frames = cozy-forgiving; the committed tail keeps it skillful, not spam. One movement verb + one authored invuln tick-window = cheap & deterministic. |
| B. Dash (Hades: shorter burst, invuln front-loaded, hold-to-sprint no invuln) | 4 | 4 | 4 | 4 | Strong alt / a *variant* of A. Snappier and more offensive-flow (great feel), but a short dash reads as less "cozy generous" than a roll and is easier to whiff a read with. Essentially A with a shorter window — ship A, tune toward this if it feels sluggish. |
| C. Block / shield (hold to reduce/negate frontal damage) | 3 | 4 | 4 | 2 | Keep as a **secondary** later (a shield item), not the first verb. Passive holding doesn't teach the read the way a timed dodge does, adds a facing/stamina system, and low skill ceiling. Doesn't reposition you out of a swarm. |
| D. Parry / deflect (Sekiro: 12-frame window → negate + stagger + counter) | 5 | 2 | 3 | 5 | **REJECT as the default.** Highest ceiling & reward, but a 12-frame window is spiky/punishing — wrong first-impression for a cozy farmer, and the tightest netcode timing (server must adjudicate a 0.2 s window vs client latency). Great as an **opt-in advanced weapon move** (fail-soft to a block) once A exists. |
| E. Reactive "perfect dodge" (Zelda flurry: dodge on the telegraph → slow-mo counter) | 5 | 4 | 3 | 4 | **Adopt as a LAYER on A, not a standalone.** It IS dodge A plus a reward for dodging *on the tell* — so it costs A first. The cozy-friendly way to add a skill ceiling (forgiving base dodge; bonus for good reads). Slow-mo is a client cosmetic; the counter window is a short authored tick flag. |

**Why A wins for us:** a roll with front-loaded i-frames is the *minimum* thing that turns "telegraphed lunge"
(from `01`) into a fair exchange, it's the most cozy-forgiving option (generous invuln, no tight timing to
fail), and it's the cheapest to make deterministic — it's a movement leg plus one authored `invulnStartTick /
invulnEndTick` window the server checks damage against. Ship A; expose the window length + roll distance as
tuning dials; add E's perfect-dodge reward and D's opt-in deflect later as depth, not fairness.

**Concrete starting numbers (to tune, from the sources):** total roll ≈ **0.6–0.7 s**; **i-frames ≈ first
~40–50%** (~**12–18 frames @60**); **vulnerable + committed recovery tail** the rest; short cooldown so it
can't be chained infinitely (Gungeon has none, but a cozy game wants a small one so dodging isn't a walk
replacement); **acting (attack) during the roll cancels remaining i-frames** (Hades). Perfect-dodge bonus
window if the roll's i-frames overlap an enemy active-strike tick.

## Weapon movesets / combos — making a small moveset feel good

We already have exactly the two inputs the sources say you need — **primary (light) + secondary (heavy)** — so
the work is *tuning*, not new systems:
- **Phase every swing** as startup(telegraph) → **active window** (weapon "on" for hits, a handful of frames) →
  recovery (Playtank). Our `PlayerToolAnimator` already renders contact frames — formalize the active window.
- **Combo string via early-exit frames** (Playtank frames 94–110 example): let a primary → primary → primary
  chain if the next input lands inside a small late window of the current swing; a mistimed/late input just
  plays the full recovery. This is what makes a 2-button moveset feel deep.
- **Light vs heavy by commitment, not just damage:** primary = fast, small enemy **flinch**, cancelable;
  secondary/heavy = longer startup, **no/short early-exit** (commitment), **stagger + knockback** on hit
  (the "haymaker"). Per-weapon `moves` blocks already exist to carry these numbers.
- **Cancels:** allow **dodge-cancel** out of a swing's recovery (Hades-style flow) — this is the single biggest
  "feels good" lever and it ties the new dodge into offense. Attacking out of a dodge cancels i-frames.
- **Feedback per hit tier** (combo sources): light = small flinch + short hitstop; heavy = big flinch/knockdown
  + longer hitstop + bigger camera kick. Scale the feel with the hit.

## Hitstop / knockback / feedback feel (build on what we have)

We already have a **contact-frame animator + camera kick** — this is tuning, not new tech:
- **Hitstop:** on a landed hit, freeze both attacker and victim for **~3–5 frames** (light) up to more for
  heavies, **capped** so a huge hit doesn't stall play (Sakurai). Scale duration by hit weight; add **per-move
  modifiers** (a weapon's "sweet spot" hits harder-feeling). Hitstop is the difference between "cutting bone"
  and "cutting air."
- **Keep hitstop (feel) separate from enemy hitstun/flinch (readability):** the freeze sells impact; the
  enemy's flinch/stagger state is the reaction the player reads (ties to `01`'s three-phase enemy attacks).
- **Knockback** = a short impulse scaled by hit tier (heavy = real displacement/knockdown; light = a nudge).
  In our sim this is an authored outcome on the hit event, not client physics (keep it server-decided).
- **Layered juice** (Sakurai): decaying screen/sprite shake, a flash/particle-gather on the contact frame, a
  brief camera kick already present — layer them, don't rely on one. All cosmetic → client-only, no sim cost.

## Boss-fight structure — applied to the giant-hornet raid

The sources converge: a good (especially *first*) boss is **fair through telegraphing, escalates in distinct
phases, teaches during the fight, uses its arena, and never drags without variation.** Applied to the
giant-hornet raid:

- **Arena:** a defined space (a clearing / the hornet's nest approach) with **usable environment** — cover to
  break line-of-sight on the ranged phase, chokes, maybe destructible nest structures. Terrain is what makes
  positioning (and our new dodge) matter; a flat empty ring is the weakest option.
- **Phases (distinct, escalating):**
  1. **Phase 1 — teach the read:** the hornet does 1–2 heavily-telegraphed dive attacks (long wind-up, clear
     audio buzz — `01`'s three-phase attack with a generous anticipation). Goal: the player learns "buzz +
     rear-up = dodge sideways, then punish the recovery." Low telegraph *density* here.
  2. **Phase 2 — add a vector:** introduce a second attack (a ranged spit / a summoned escort of drones — the
     "Swarm/Sniper" roles from `03`) so the player must prioritize and use terrain. Higher telegraph density.
  3. **Phase 3 — pressure/enrage:** faster cadence, combined tells, maybe an arena hazard. Escalation, but
     **still all telegraphed** — difficulty from density + speed, never from removing the tell.
- **Fairness first-boss rules:** every attack telegraphed (visual + audio + a reserved "unblockable/dodge-only"
  colour tell per `03`); **HP-gate the phases** (phase changes at HP thresholds, not timers, so learning
  translates to progress); make the win come from *understanding the hornet*, not out-healing it.
- **Checkpoints / retry loop** (the sources under-cover this, so it's a design call): a first boss must be
  **cheap to retry** — respawn at the arena entrance, keep gear, short walk-back. A cozy game should lean
  **generous** (see co-op down-states below) so death is a lesson, not a punishment. This is an owner question.
- **Co-op scaling:** in the raid, scale **frequency/adds and add an attack that targets a specific player**
  (forcing spread), NOT flat HP/damage — consistent with `03`'s "vary frequency, not amplitude." See below.
- **Presentation:** the buzz/music is part of the boss (Undertale-Megalovania point) — the audio *is* the
  telegraph layer in a top-down view where the sprite is small.

## Co-op combat

Our game is Nakama multiplayer, so the raid must work with N players. Guidance from the co-op sources:
- **Shared threat table, no friendly fire (default).** Reuse `03`'s per-enemy integer threat table across all
  players: each player accrues threat; the hornet/bugs target the top-threat player; taunt-like lures peel it.
  This is the co-op version of `01`'s attack-token layer — the **attack-token pool is shared across players**
  so density stays scary but concurrent bites stay bounded regardless of party size. **Skip friendly fire:**
  the sources flag it as a frustration source, and it's wrong for a cozy game (nobody wants to net a friend).
- **Downed + revive state (generous).** Instead of instant death, a player who runs out of HP enters a
  **downed** state (can't act, bleeding a timer); a teammate revives by **channeling in contact range**. Keep
  it generous for cozy: no permadeath, a self-revive timer or a consumable so a solo-in-a-duo player isn't
  hard-stuck. The "Second Wind costs the reviver something" idea (a little health / a brief vulnerability) adds
  stakes without frustration. Offer an anti-chore option (teleport-to-ally or a remote life-trade) since our
  zones are large.
- **Difficulty scaling by player count = frequency, not stats.** Scale the **shared attack-token pool, add
  count, and reinforcement cadence** with N players, and add a **player-targeted attack** in the raid that
  forces the group to spread (so 4 players can't deathball one spot). Do **not** just multiply boss HP/damage
  (bullet-sponge anti-pattern from `03`). Scaling can be **linear (predictable)** or **emergent** (more players
  → new attack unlocks) — an owner taste call.
- **Everything stays server-authoritative:** threat, token grants, downed/revive transitions, and scaling are
  all server decisions relayed as events (same shape as the predation strike) — no client trusts another
  client for damage or state.

## Netcode / determinism note — dodge i-frames in a server-authoritative model

The dodge must feel instant locally yet have the **server own the damage window**, and must not break the
deterministic sim. Design:
- **Client-predicted movement, server-authoritative damage.** The dodge is a *movement* verb — predict it on
  the local client immediately (responsiveness), exactly as normal walking is presented; but **the server
  decides whether a hit lands**, and it does so by checking the player's **invulnerability window** at the
  relevant tick. The client never tells the server "I was invincible"; the server derives the window.
- **Model the invuln as authored integer tick counts on a dodge event**, mirroring `01`'s enemy attack legs:
  a `DODGE` action carries `startTick`, `invulnStartTick`, `invulnEndTick`, `recoveryEndTick`. When the sim
  resolves an enemy strike that would hit this player, it checks `invulnStart ≤ strikeTick ≤ invulnEnd` →
  no damage. Pure integer comparison → deterministic, replayable, resync-safe. This is the same pattern as the
  enemy telegraph (`windup/active/recovery` ticks) but on the player.
- **Determinism rules (from `01`/frontier-sync):** no per-frame RNG in the dodge; the invuln window is fixed
  integer ticks (or seeded from `(tick, playerId)` if anything varies); the dodge event rides the zone-wide
  ledger so late-joiners/resyncs reconstruct it; the *outcome* (hit / no-hit) is the authority's, relayed via
  the existing hit event — clients just render.
- **Latency reconciliation:** because the server owns the window, a laggy client's dodge is adjudicated on the
  server's tick timeline (optionally with a small input-buffer / lag-compensation grace). Cosmetic hitstop,
  camera kick, slow-mo (perfect-dodge) are **client-only** and never enter the sim. This keeps the
  "are all players in sync" guarantee intact: two clients replaying the same dodge + strike ledger events reach
  the same hit/no-hit result bit-for-bit.
- **Perfect-dodge / parry windows** are just tighter authored tick flags evaluated the same way — a parry's
  0.2 s window is a 12-tick server check, not a client claim (which is exactly why parry is the highest-cost
  netcode option in the scored table).

## Open questions (owner taste — not guessed)
1. **Dodge feel:** roll (Gungeon, generous/cozy) vs dash (Hades, snappy/offensive)? And how generous — i-frame
   length and whether there's a cooldown (a cooldown keeps it a *tool*; no cooldown makes it a movement style)?
2. **How much skill ceiling?** Ship just the forgiving base dodge, or also the perfect-dodge reward (E) and/or
   an opt-in weapon parry (D)? These raise the ceiling but push away from pure cozy.
3. **Is there a block/shield at all** (candidate C as a later secondary), or is dodge the only defensive verb?
4. **Boss retry generosity:** how punishing is a failed giant-hornet raid — full retry from the entrance with
   gear kept (cozy), or a real cost? Tied to the downed/revive generosity.
5. **Co-op difficulty scaling:** linear-and-predictable, or emergent (new attacks/adds unlock with more
   players)? And friendly fire — confirmed OFF, or a hard-mode opt-in?
6. **Downed/revive rules:** self-revive timer + teammate revive (generous), or teammate-only with a real cost
   (tense)? Where on the cozy↔tense axis (same dial as `03`'s Q1)?
7. **Does the raid want a player-targeted "spread" attack** (recommended for N-player fairness), i.e. are we
   committing to real co-op boss mechanics vs. just more bugs?
