# Challenge & enemy effectiveness — research findings

*Topic 1 of the 2026-07 combat research. How to make enemies threatening, fair, and satisfying —
and add real threat to a currently-toothless cozy game — WITHOUT breaking the cozy tone or the
deterministic sim. Pairs with `01_melee_enemy_ai.md` (the how-to-move/attack layer). Raw transcripts:
`../_raw_recovered/combat/`.*

## The one principle everything converges on
> **Decouple how dangerous a swarm LOOKS from how much it can HURT per unit time, and vary FREQUENCY, not damage.**

Scary density can be huge; actual damage-per-second is a small bounded number. Every source below is a
different mechanism for that split, and every one is integer/counter/timer based → deterministic-safe.

## Source table (deep-read)

### 1. Left 4 Dead "AI Director" — adaptive dramatic pacing (Michael Booth, Valve, full deck)
- Tracks a per-Survivor **emotional intensity** scalar; modulates the **population** of enemies (not their strength) through a 4-phase cycle.
- Intensity **RISES** with damage taken, incapacitation, being pulled/pushed off a ledge, and a nearby infected death (∝ inverse distance). **DECAYS** toward zero over time — **but not while infected are actively engaging**. Director tracks the **MAX** across the team.
- Cycle: **Build Up** (full threat until intensity crosses a peak) → **Sustain Peak** (hold full pop **3–5 s** after peak) → **Peak Fade** (drop to minimal pop, wait for a lull) → **Relax** (minimal pop **30–45 s** or until the team travels far enough, then resume).
- Verbatim thesis: *"Algorithm adjusts pacing, not difficulty — **amplitude (difficulty) is not changed, frequency (pacing) is.**"* "Constant unchanging combat is fatiguing; long periods of inactivity are boring."
- **75 % of mobs spawn BEHIND** the team (at/behind its "flow" distance). Bosses are exempt from adaptive pacing (they intentionally break rhythm).

### 2. "Attack token" convention (Ask a Game Dev, full post)
- Only an AI holding an **attack token** may attack; on finishing it passes the token on. Tokenless enemies still crowd, wander, and menace (the scary part) but can't damage.
- Token **count** is the difficulty knob (1 = one attacker at a time; more for harder fights). Verbatim intent: keep threat controlled "**rather than constantly scaling with the number of enemies.**"

### 3. WoW threat / aggro tables (classic-warrior wiki, corroborated)
- Per-NPC **threat table**: every action adds threat; the NPC attacks whoever tops it. **1 damage = 1 threat; 1 healing = 0.5 threat.**
- Steal aggro by exceeding the current target by **10 % at melee / 30 % at ranged** — a **hysteresis band** that stops flip-flopping ("easier to keep it once you have it").
- **Taunt** = set your threat equal to the top target's (forces a swap). Aggro lost by leaving **leash** range, dying, or a drop-combat ability.

### 4. Batman: Arkham free-flow / combat ring (pieced from fetchable analyses)
- Enemies surround the player in a ring but only a limited number strike at once (~2–3, directional — *search-only, unconfirmed in a primary*); every incoming attack is **telegraphed** and answered with a counter.
- **Verified:** takedown animations grant invulnerability ("other enemies will not attack you during the animation") so you're never robbed of an earned move — but ground takedowns are interruptible (a deliberate risk/reward asymmetry).

### 5. Enemy variety & role composition (5 sources)
- **Harvey Smith, "Designing enemies with distinct functions":** differentiate by **function/counter, not stats**. "Reverse-engineer" — decide the role first, then the creature. Two enemies with different speed/dmg/HP but the same *response* are fake variety.
- **The Level Design Book (cites Mike Stout):** 6 archetypes — **Grunt** (easy melee), **Squad** (coordinated mid-range), **Leader** (survivable buffer), **Tank** (durable/slow/big), **Swarm** (fast/low-HP/many), **Sniper** (weak/long-range). "Melee enemies by themselves are usually pretty boring"; **ranged/"Far" enemies are what make terrain & positioning matter.** Each archetype teaches ONE idea; mixing them forces target-prioritization = emergent difficulty without stat-scaling.
- **Jason de Heras, "Enemy design layers in Hollow Knight":** 6 layers (foreshadowing, spawn, projectiles, timing/rhythm, death states, on-hit responses); every enemy needs a clear **tell** (visual OR audio — Mosscreep long wind-up; Fool Eater a shaking *sound*; Mosskin zero-startup plays on knowledge). Vary **attack rhythm** across species so one dodge-timing can't clear a mixed group. Death states as flavour+risk (explodes on death → don't melee it).
- **Deliberate Game Design categorization:** by role-relative-to-player — **Smashers** (trivial, power-fantasy), **Emphasizers** (reward a mechanic, don't require it — should be MOST of the roster), **Enforcers** (demand a specific mechanic — use sparingly), **Challengers** (boss-tier). Audit on a role×tier grid to find redundant clusters and gaps; every enemy's gimmick fits in one sentence.
- **L4D Special Infected** as the model roster: Boomer (bile → summons a horde = support/debuff), Tank (bruiser), Jockey (clings/steers the player = controller). Out-of-combat **demeanor** telegraphs the threat before the fight.

## Telegraphing & fairness (numbers) — shared with `01`
- Human reaction ≈ **250 ms**; a reactable wind-up ≥ ~**15 frames @60 fps**; big/unblockable moves stretch toward **~1 s**. Every attack = **anticipation → active → recovery**; recovery length is the punish-window dial. (GDKeys "Anatomy of an Attack"; frame-data explainers.)
- Reserve a **consistent colour tell** (Sekiro red-kanji) for "default defence won't work — sidestep/net it," placed **ON the enemy, never covering its wind-up** (critical in top-down).
- **Layer** tells multi-sensorially (motion + rising buzz/hum + particle-gather + release flash) so they stay legible when the swarm is small on-screen (Game Developer telegraphing article).

## ≥4 scored candidates for "add meaningful challenge to a cozy deterministic game"
Axes: **challenge gained · keeps cozy tone · determinism/perf fit · dev cost** (1–5).

| Candidate | Challenge | Cozy-safe | Determinism | Dev cost | Verdict |
|---|:--:|:--:|:--:|:--:|---|
| **A. Bite-token pool + telegraphed lunges** (cap concurrent attackers; every bite has a wind-up) | 4 | 5 | 5 | 3 | **PICK #1.** Scary density, bounded fair DPS; integer pool + tick timers. |
| **B. Deterministic "threat director"** (per-player intensity valve: Build-Up/Sustain 3–5 s/Fade/Relax 30–45 s; vary frequency not damage; reinforce from off-screen edges) | 4 | 5 | 4 | 4 | **PICK #2.** Guarantees a breather after every real fight → threat that never becomes fatigue. |
| **C. Threat-table target arbitration + aggro radius/leash** (lures/torches/scarecrows peel the swarm; 10 %/30 % hysteresis; leash = retreat always works) | 4 | 5 | 5 | 3 | **PICK #3.** Turns a blind pile-on into a placement puzzle the player out-plays. The cozy "taunt." |
| D. Just raise bug HP / damage / count | 2 | 2 | 5 | 1 | REJECT — spongey + unfair; the anti-pattern every source warns against. |
| E. Global difficulty slider only | 2 | 4 | 5 | 1 | Keep as a *wrapper* over A–C's dials, not a substitute. |

## The proposal in one picture (for BugFarmer)
1. **Roles, not stats** — give the bug roster distinct *functions* mapped to player *tools*: Grunt (common crawler, any tool), Swarm (gnat cloud → **net** fodder), Sniper/Squad (a **spitter** that pelts from range → makes terrain matter, forces closing), Leader/Buffer (a **broodmother** that spawns/enrages nearby bugs → **kill-first** target), Tank (armoured beetle → kite/avoid), Controller (a **latcher** that slows/steers the player → peel it off). A swarm of only crawlers is a blob; add one spitter + one broodmother and the player *must* prioritize. Most species are "Emphasizers"; a *few* "Enforcers" (only the net catches the flyer; only the spear pierces the shell) teach the kit.
2. **Bite-token pool per player** (default 1–2, difficulty-scaled) caps damaging bugs; the rest menace.
3. **Every damaging lunge telegraphs** (integer wind-up leg, distinct per species, + rising-buzz audio + particle-gather); protect the player's own swing/net animation from being stun-locked.
4. **Threat director valve** per player: intensity rises with bites/nearby deaths, decays only when disengaged; Build-Up → Sustain(3–5 s) → Fade → Relax(30–45 s); reinforcements arrive from off-screen edges (directional pressure, not a teleport pile-on).
5. **Threat table + aggro radius + leash:** lures/torches/scarecrows are threat magnets that peel part of the swarm; a leash guarantees retreat is always a valid escape (the fairness valve).

Every mechanic above is integer/counter/timer based — no floats — so all five ride the deterministic ledger the same way the predation strike already does (authority decides, relays the observable via events).

## Reality check — our player-side combat kit (verified 2026-07-11)
Combat is two-sided, so the enemy telegraph→recovery loop only pays off if the player has counters. What we
actually have in the code today:
- **Weapon movesets exist** — `MeleeController.TryHandleClick("primary"/"secondary")` + a `moves` block per
  weapon in `items.json` (every weapon has a `secondary`); hits are server-validated; the procedural
  `PlayerToolAnimator` renders the swing.
- **No defensive kit at all** — there is **no dodge / roll / dash, no block, no parry, no i-frames**
  (no such controller in `Assets/Scripts/Player/`; `MeleeController` has no invuln logic). Movement is plain
  walking.
**Implication:** the research's fair-threat model (telegraph → sidestep/counter → punish the recovery) has
**nothing to sidestep *with*** today. Before (or alongside) smarter enemies, the player needs a minimal
defensive verb — at least a **dodge/dash with brief i-frames** (the single highest-leverage add), and possibly
a **block/parry** if we lean into tell-reading. Without it, "raise the challenge" can only mean "take more
unavoidable damage," which is the unfair path every source warns against. **This is the load-bearing
prerequisite for the whole combat direction** and is called out further in `../SELF_CRITIQUE.md`.

## Anti-patterns
- Scaling **stats** (HP/damage/count) to make things "harder" → bullet-sponges + unfair pile-ons (universal warning).
- No **leash / aggro radius** → the player can never disengage → cozy game becomes stressful/unfair.
- One dodge-timing clears everything → give species **different attack rhythms**.
- Five redundant crawlers → audit on a role×tier grid; every species passes the one-sentence-gimmick test.
- Decaying intensity **while still being attacked** → lets the player cheese the breather; decay only when disengaged.

## Open questions (owner taste — not guessed)
1. **How cozy vs. how threatening?** The whole system is dialable (token pool, telegraph length, director amplitude). Where on the cozy↔tense axis should the *default* sit — Stardew-mines-light, or genuinely dangerous at night/in caves?
2. **Is threat opt-in?** Should danger be zoned/time-gated (safe farm by day, dangerous wilds/caves/night) so players choose their challenge, à la Don't Starve seasons?
3. **Which roles do we actually want?** The roster (spitter / broodmother / latcher / armoured tank) implies new species + new player counters — how far do you want to expand the bestiary for combat vs. keep bugs mostly ambient?
4. **Difficulty settings?** One global slider over these dials, or per-axis (separate "how many bugs" vs "how hard they hit")?
