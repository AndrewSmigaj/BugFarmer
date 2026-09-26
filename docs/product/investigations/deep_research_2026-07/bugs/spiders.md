# Bugs: spiders (the marquee arachnid enemy family)

*Topic of the 2026-07 bug research. Spiders were a **specifically requested** enemy family. One section
PER spider type, each grounded in real hunting biology, in how good games actually do it, and mapped to
our deterministic swarm sim. Builds on the already-approved spider system in
`docs/product/ecology/design_ants_spiders.md` (web-builder + jumping/wolf archetypes, reuse verified
against real code) and the shared enemy framework in `../combat/03_challenge_and_effectiveness.md`.
Recovered raw research was thin (the dedicated spider agents died at ~2 tool calls):
`../_raw_recovered/bugs/{ad3b80dd9865c378f,a5e43c1048681edb7,a2670bf6a75e6d5a0}.md` are mostly
ant/centipede/underground noise — the game research below is a fresh deep-read (see Source table).*

---

## 0. What we already have (recovered set + code)
- **Sprites exist, no data/sim yet:** wolf, jumping, orb-weaver, funnel, huntsman, tarantula, black
  widow, cave spider. (`nakama/data/bugs.json` / the `mining_caves` brainstorm roster.)
- **Nothing spider is built.** `cave_spider` is a design candidate ABSENT from `species.json`;
  `spider_web`/`web` ABSENT from entities.
- **D21 (owner decision):** small webbed spiders live only in the **lower/harder underground** (Centipede
  Cavern + deeper), NOT the first Mining Camp; `cave_spider` "drops from the ceiling on silk." BACKLOG:
  "Spiders & webs in the underground (don't forget!)".
- **`design_ants_spiders.md` (APPROVED, reuse verified against real code)** already maps two archetypes:
  - **(A) Web-builder ambush trapper** — web = server-placed occupant that **SLOWS** prey via a new
    `web_slow` field read **server-side** (rides the existing leg-speed field, reuses the already-hashed
    `OCCUPANT_BLOCKS_BUGS`); webs are **transient soft occupants** that decay, are never written to saved
    zone data, and never placed on edge/spawn/transition cells. Spider then pounces.
  - **(B) Jumping/wolf stalk-and-pounce hunter** — **pure reuse of the centipede `ActionState` machine**
    (`centipede.go:65`: windup→surge→recover, samples target velocity at windup). Pounce = the `surge`
    leg; kill = predation strike (`BUG_REMOVED`); windup = the readable telegraph.
  - Build phasing there: **spiders FIRST** (jumping spider = lowest-risk win), ants later.

## 0.1 The engine contract every spec below respects
- **Movement = `SWARM_SET_TARGET` legs** (fixed-point). Server AI moves swarm **centers only** — no per-bug
  positions server-side; clients deterministically scatter per-bug positions from
  `(worldSeed, swarmId, bugId, tick)`.
- **Strikes: detect-don't-remove.** The authority client detects a per-bug predation hit → server relays
  `BUG_REMOVED`. Damage-to-player rides the same authority-relay pattern.
- **Player interaction:** `PLAYER_CELL_ENTER` (flee / aggro trigger). A zone-wide `blocks_bugs` collision
  map exists (`OCCUPANT_BLOCKS_BUGS`).
- **The lever (from `design_ants_spiders.md`):** anything that only changes *which leg the server emits* is
  **server-only soft state** — no new ledger event, no hashing, no client code. Web-slow, stalk-vs-pounce
  speed, and aggro/leash accumulators all live here. Pounce/lunge always targets the prey **swarm center**;
  the authority client resolves the per-bug victim. **No view-scoped reads; fixed-point/integer only.**
- **Top-down adaptation is the crux for spiders.** We have no Z axis, so "wall-crawl," "ceiling," and
  "drop-from-above" all become **2D reinterpretations** (spelled out per type): a *drop* becomes a
  **telegraphed ambush spawn** (`SWARM_SPAWNED` at a marked cell with a landing shadow); *ceiling/wall*
  becomes a **web-cell / cave-wall cling state** the spider sits in until it commits.

---

## 1. Orb-weaver — the WEB TRAP (signature ambush; the "build a place dangerous" spider)

**(a) Real behavior.** Orb-weavers spin a wheel-shaped web across a flyway, have poor eyesight, and sit in
or beside the hub reading **web vibrations**; when a flying insect is snared they rush out and wrap/bite it.
They are *sit-and-wait* trappers, not chasers — the web does the catching. (Britannica / Australian Museum /
CSU Extension.)

**(b) How games do it.** *Grounded's* Orb Weaver patrols a small area and **periodically spins webs**;
it sleeps in its nesting area near Orb-Weaver Jr.s and Spiderlings and **wakes if a nearby web breaks or a
fellow spider takes damage** (a proximity alarm). Its attacks: a blockable lunge bite, a triple sidestep
bite, a **charged bite that roars first and tracks the player as it charges**, and — the signature — an
**unblockable web shot** that immobilizes ("drastically reducing movement speed until broken out of"); you
dodge the projectile or break free by hitting it. In *Grounded 2* it also holds a **defensive web stance**
(immune to light attacks from the front while it advances).

**(c) BEHAVIOR SPEC → our sim.** This is archetype (A), already approved.
- The orb-weaver **anchors a home range** and periodically emits a **web-placement** = server-places a
  `spider_web` occupant at a chosen cell (exactly like a nest split: `chunk.SetOccupant` +
  `broadcastWorldUpdate` + `OCCUPANT_BLOCKS_BUGS`). Cells chosen deterministically via `state.Rng` +
  `sortedStringKeys`; **never on edge/spawn/transition cells** (placement guard); webs **decay** on a
  lifetime/HP timer and are **not persisted** to saved zone data.
- **`web_slow` field, read server-side:** any prey swarm center (or the player, via `PLAYER_CELL_ENTER`)
  standing on a web cell gets `SpeedMult < 1` on its next leg. No per-bug client state, no new hash — it
  rides the existing leg-speed field.
- **Catch → pounce:** when a slowed prey center sits on the web, the orb-weaver runs an `ActionState`
  windup→`surge` onto it → strike (`BUG_REMOVED`).
- **Web shot (optional variant, matches Grounded's marquee attack):** a **telegraphed ranged event** — the
  spider rears (windup leg), then fires a fixed-velocity "web glob" computed at the fire tick toward the
  player cell (server-known). On hit it **applies `web_slow` to the player** (a slow debuff, integer
  timer), not damage. This is one small new authority-relayed event in the class of the hornet venom-spit
  (`flying_pests_stingers.md`); resolve authority-side, relay the observable. Player breaks free by moving /
  by an input, mirroring "hit it to break out."
- **Proximity alarm:** damaging a web or an ally within radius emits a **wake influence event** (reuse the
  nest-defender recall pattern) → nearby orb-weavers switch to aggressive. Integer radius.

**(d) Threat / role.** The **Sniper/Controller** of the roster (per the combat role grid): it makes
**terrain and positioning matter** — you can't just walk the flyway. In a bug-farming game its diegetic
menace is perfect: an orb-weaver web strung across your path **catches your own farmed bugs** (an ecology
disruptor and a reason to clear it). Memorable, screenshot-worthy, and the reason a *place* feels dangerous.

**(e) Telegraph + counterplay.** The **web itself is the telegraph** — a visible placed occupant you can see
and route around or burn/cut. The web shot has a rear-up windup (color tell on the spider, never over the
wind-up, per the top-down telegraph rule). Counterplay: destroy the web (frees the lane and any caught farm
bugs), dodge the glob, or bait the pounce and punish the recovery window. Fair because every threat is a
**visible, static, destructible object** before it's a hit.

---

## 2. Funnel-web — AMBUSH BURST from the tube (the trapdoor scare)

**(a) Real behavior.** Funnel-web / funnel-weaver spiders build a **sheet web with a narrow silk tube** at
one edge and **lie in wait at the tube mouth**; prey walking the sheet sends vibrations, and the spider
**bursts out explosively**, drags the prey back in, and retreats. Pure ambush — fast, short, then gone.
(Australian Museum; CSU/UMD Extension; "wolf spider vs funnel weaver.")

**(b) How games do it.** This is the classic **trapdoor/ambush enemy**: dormant and near-invisible until you
enter its trigger radius, then a single explosive burst. *Don't Starve* dens work this way at the cluster
level — **stepping on the sticky webbing makes spiders erupt from the den to investigate**, and attacking
one "signals the entire cluster to the den's defense." *Hollow Knight's* Deepnest leans on exactly this
dread: still, dark, then something lunges from a hole.

**(c) BEHAVIOR SPEC → our sim.**
- The funnel-web is a **stationary ambusher tied to a `funnel_web` occupant** (its tube). It idles hidden
  (no legs) until a player/prey enters its trigger radius (`PLAYER_CELL_ENTER` / a prey center on an
  adjacent cell).
- **Burst = one hard `ActionState`:** a very short windup → a **high-`SpeedMult` `surge` leg** out to the
  target → strike (`BUG_REMOVED` / player hit) → a fast **retreat leg back to the tube** (reuse the
  provisioning "homing" phase target = the occupant cell). Then it re-hides and goes on cooldown.
- The **sheet web around the tube can be `web_slow` cells** (reuse §1's field) so prey is pre-slowed in the
  kill zone — mechanically ties the ambush to the trap.
- Cluster alarm reuses the wake event (§1) so a nest of funnels erupts together (the Don't Starve feel).

**(d) Threat / role.** A **Grunt-with-a-gimmick / area-denial** enemy: individually low sustained threat
(it retreats), but it **punishes careless movement** and turns a corridor into a held breath. Cheap variety
— it teaches "watch the ground before you walk."

**(e) Telegraph + counterplay.** The tube occupant is a **visible tell in the environment** (a funnel of
silk); the burst has a short but distinct windup + audio. Because it **always retreats**, the counterplay is
to **bait the burst and punish the recovery/retreat window**, or destroy the tube to remove the ambush.
Fairness valve: a leash (it never chases past its home range) and the visible web zone.

---

## 3. Wolf spider — the ACTIVE HUNTER (relentless ground stalker)

**(a) Real behavior.** Wolf spiders **build no capture web**. They are fast, primarily **nocturnal**
ground hunters that patrol, rely on excellent eyesight + sensory leg hairs, **stalk, then pounce** on prey.
Fast runners. (CSU Extension; Pacific Horticulture; UMD Extension.)

**(b) How games do it.** *Grounded's* Wolf Spider is the marquee terror: **nocturnal** (sleeps by day with
an audible "snoring" tell), "**hostile… will produce snarling sounds and give chase upon spotting**" you,
and — the key AI — **even before it sees you it "will slowly approach the player's location if within range
of its territory."** A pre-sighting **stalk**. Long legs give "a deceptively fast stride." Four attacks:
basic bite, a 5-hit combo bite, a **charged lunge**, and a **jump/dive attack** ("massive damage," perfect-
blockable or avoided by running). Poison on most hits; **venom** (longer DoT) on the charged lunge.
Counterplay is one-handed-weapon + shield to learn its tells for perfect blocks.

**(c) BEHAVIOR SPEC → our sim.** This is archetype (B), already approved.
- **Stalk (server-only soft state):** when the player is within territory range (`PLAYER_CELL_ENTER` +
  an integer aggro radius) but not yet "engaged," the wolf spider emits **slow legs toward the player's last
  cell** — the pre-sighting creep. Aggro is an integer accumulator with a **leash** (out of range → decay →
  return to patrol). This is exactly Grounded's "approach the location before it sees you."
- **Pounce = `ActionState` windup→`surge`** (reuse centipede machine): a telegraphed lunge that samples the
  target's velocity at windup, targets the swarm center / player cell → strike (`BUG_REMOVED`).
- **Combo bite** = a short repeated-strike state (a few quick strikes on cooldown) once adjacent.
- **Venom** on the pounce = an integer DoT payload on the player (timer/accumulator), deterministic.
- **Day/night** activity = an integer time-of-day gate on aggro (cheap; ties to the night-danger theme).

**(d) Threat / role.** The **apex melee hunter** of the surface/night roster — a **Tank/Bruiser** that
*comes to you*. High memorability; the "there's a wolf spider out there at night" dread. Pairs with the
threat-director's night ramp (`03_challenge_and_effectiveness.md`).

**(e) Telegraph + counterplay.** Layered tells: the **snarl audio** on aggro, the **stalk creep** (you see
it coming before it commits), and a distinct **windup per attack** (rear-up before the pounce/dive). Counter:
break line/leash to disengage (fairness valve), dodge or block the telegraphed pounce, punish recovery.
Because damage is **frequency-gated by the bite-token pool**, its scary presence never becomes unfair DPS.

---

## 4. Jumping spider — STALK-then-LEAP (the precision pouncer; BUILD FIRST)

**(a) Real behavior.** Jumping spiders are **diurnal, big-eyed active hunters** that **stalk prey to within
~5–10 cm and then pounce**, jumping several body-lengths. No capture web (they trail a silk dragline). The
purest **stalk → single explosive leap** predator. (CSU Extension; Britannica.)

**(b) How games do it.** The stalk-then-committed-leap is the cleanest readable pounce in the genre — it's
the *Grounded* wolf-spider "charged lunge / jump attack" distilled to one move, and it's the pattern
`design_ants_spiders.md` calls the **safest, fastest win** (retarget the centipede lunge to prey/player).
The arc is the tell: a crouch/windup, then a fast fixed-distance leap.

**(c) BEHAVIOR SPEC → our sim.** Archetype (B), the **first thing to build**.
- **Stalk:** slow approach legs (low `SpeedMult`) toward the target center while in aggro range.
- **Leap = `ActionState` windup→`surge`** — the signature: a **short, fixed-distance, high-speed leg** (the
  "arc"). The leap distance is a constant so the range is learnable; overshoot on a dodge = a punish window.
- **Strike** on landing = `BUG_REMOVED` (prey) / player hit; then a recovery leg.
- Everything is pure reuse — no web, no new occupant, no new ledger event. `design_ants_spiders.md` scores
  its determinism/reuse fit ~90%.

**(d) Threat / role.** A **fast, low-HP "Swarm/skirmisher"** whose whole identity is the leap-gap. Great
first spider because it proves the pounce tech end-to-end at the lowest risk, and it reads instantly.

**(e) Telegraph + counterplay.** The **crouch/windup before the leap** is the tell (the classic anticipation
frame, ~15+ frames per `03`). Counter: **sidestep the fixed arc** — because leap distance is constant, a
timed dodge always beats it, and the recovery is the punish window. The fairest possible pounce.

---

## 5. Huntsman — the FAST WALL-CRAWLER (speed skirmisher; top-down reinterpret)

**(a) Real behavior.** Huntsman spiders build **no web** and **actively chase prey with speed** — flat,
crab-like, long angular legs that move **forward and sideways** very fast; among the fastest, most agile
spiders. They favor vertical surfaces (walls, bark) and dart. (Wikipedia; HowStuffWorks; spiderzoon.)

**(b) How games do it.** Wall-crawl in 2D is *Terraria's* **Wall Creeper**: it uses **"Spider AI" to climb
background walls** in Spider Nests and only **"reverts to acting like a fighter enemy when there are no
background walls,"** and it **drops onto** the player. Key constraint we can borrow: "**like all spiders,
cannot travel through a 2-tile-wide shaft**" — a spatial rule that makes tunnels a counter.

**(c) BEHAVIOR SPEC → our sim (the top-down wall-crawl adaptation).** We have no vertical walls, so:
- **Wall-cling state:** the huntsman prefers cells **adjacent to `blocks_bugs` cave-wall blocks** (it hugs
  the rock). While clinging it moves **very fast along the wall line** (high base leg speed) and is a low
  threat — it's *positioning*. This uses the existing collision map, no new data.
- **Dart:** when the player passes, it **breaks off the wall with a fast `surge` leg** across open ground to
  strike, then races back to a wall (retreat leg). Fast, twitchy, repeated — the "skirmisher."
- **Speed is its whole gimmick** — pure leg-speed values; reuses everything from the pounce tech. No web.
- Borrow Terraria's spatial counter: the huntsman **won't enter tight/blocked geometry** the same way,
  making narrow tunnels a safe pocket (a `blocks_bugs`-driven pathing preference).

**(d) Threat / role.** A **fast harasser / Swarm-role** that makes open cave galleries dangerous and
rewards using terrain (hug the tunnels). Distinct from the wolf spider by **speed + hit-and-run vs.
committed stalk** — different *rhythm*, real variety (per Harvey Smith's "function not stats").

**(e) Telegraph + counterplay.** The tell is **it's on the wall** (safe) → the **break-off dart** is the
commit (a brief windup as it leaves the wall). Counter: it's fast but fragile — catch it mid-dart, or hold a
tight-corridor pocket it avoids. Fairness: it always returns to the wall (a natural leash/rhythm).

---

## 6. Tarantula — the TANKY BURROWER (heavy ambush; the "don't melee it blind" wall)

**(a) Real behavior.** Tarantulas are **ambush predators that rely on burrows** — heavy, hairy, slow,
strong grip and high bite force; they wait at the burrow mouth and lunge at passing prey, then retreat.
Much greater body mass than the fast hunters. (spiderzoon; Quora comparisons; HowStuffWorks.) Many also
kick **urticating (irritant) hairs** as a defense.

**(b) How games do it.** The burrow-ambush tank is a staple: a **durable, slow enemy that emerges from a
den** (Don't Starve's higher-tier **Warrior Spider** that "emerges to defend its den when threatened"),
combining a trapdoor ambush (§2) with a **Tank** stat profile — you can't just facetank it, and its
death-state/defense punishes greedy attacks.

**(c) BEHAVIOR SPEC → our sim.**
- **`tarantula_burrow` occupant** = its den; the tarantula idles in/at it (no legs) until triggered
  (`PLAYER_CELL_ENTER` / prey adjacent).
- **Emerge → heavy lunge:** a **longer windup** `ActionState` (it's slow — a generous, very readable tell) →
  a short powerful `surge` → strike → slow retreat to the burrow. Higher HP than the other spiders (the
  Tank), slow legs.
- **Urticating-hair defense (optional death/on-hit state, per the combat "death states" layer):** attacking
  it in melee applies a brief **integer irritant DoT/slow to the player** — "don't just melee it," a
  reason to bring reach/ranged. Deterministic (timer payload).
- Because it's slow with a big leash, it's the roster's **positional wall**, not a chaser.

**(d) Threat / role.** The **Tank** — durable, slow, punishes greed, gates a space. In the deep underground
it's the "heavy" guarding a chamber. Low mobility keeps it fair; the payload is *toughness + on-hit
deterrent*, not speed.

**(e) Telegraph + counterplay.** The **long emerge/lunge windup** is a huge readable tell (fits the "big
moves stretch toward ~1 s" rule). Counter: **kite it** (it can't keep up), use **reach/ranged** to avoid the
urticating deterrent, and punish the long recovery. Fairness: slow speed + a hard leash to the burrow.

---

## 7. Black widow — the VENOMOUS LURKER (low threat presence, high consequence)

**(a) Real behavior.** Widows build a **messy tangle/cobweb** (not an orb), **prefer to save energy and
wait** in a retreat, rarely leaving; they subdue prey caught in the tangle with a **potent neurotoxin far
stronger than a tarantula's**. Shy — the danger is the **venom**, not aggression. (Quora/biology summaries;
CSU Extension on cobweb weavers.)

**(b) How games do it.** The "shy but deadly" lurker is the enemy whose **damage payload (a strong DoT
status), not its behavior, is the threat** — a natural fit for the combat framework's "**vary the payload,
not the aggression**." It sits in its web (like Grounded's Orb Weaver waking only when disturbed) and its
one bite matters because of the **venom stack**.

**(c) BEHAVIOR SPEC → our sim.**
- **Tangle-web lurker:** anchors a `tangle_web` cluster (reuse §1's `spider_web` occupant + `web_slow`, but
  irregular/messy placement). Mostly **stationary in a retreat cell**; low aggro; wakes when its web is
  disturbed or an ally is hit (the wake event).
- **Single venom strike:** a telegraphed `ActionState` bite from the web edge → strike applies a **strong
  `venom` DoT** (the biggest integer DoT payload in the set: high total, slow ticks — the "consequence"),
  then it retreats. It does **not** chase.
- Distinct from the orb-weaver: **orb-weaver = the web/lane threat + web-shot control; widow = the venom
  payload + a lurk.** Same `spider_web` tech, different role knobs (aggression low, DoT high).

**(d) Threat / role.** A **glass-cannon Sniper-by-payload / area guardian**: barely moves, but the venom
turns one careless step into a long, dangerous DoT you must play around (heal / retreat). Teaches **respect
the web, don't brute-force it.**

**(e) Telegraph + counterplay.** Tell: it's **visibly nested in a distinctive tangle web** (approach = your
choice), plus a clear bite windup. Counter: **clear the web from range** or bait the single bite and back
off; bring **antivenom/healing** (an item hook). Fairness: it never pursues — engaging is opt-in.

---

## 8. Cave spider — DROP-FROM-ABOVE PACK (the underground swarm; D21's mandate)

**(a) Real behavior.** (The in-game cave spider is a small, pale, cave-adapted swarm hunter; real
cave-associated spiders are small and drop on draglines.) Behaviorally we model the **small, fast, venomous,
pack drop-attack** the D21 decision + brainstorm roster already specify (`cave_spider`, `cave_spider_funnel`,
`cave_widow_pale`, `tunnel_weaver`).

**(b) How games do it.** *Minecraft's* Cave Spider is the template: **spawns from spawner "nests" in
mineshafts at light 0**, is **tiny (0.5-block tall, fits 1-block gaps)**, **applies Poison** (Normal/Hard),
is **neutral in light ≥12 / hostile in the dark**, and **swarms in numbers from the nest**. *Don't Starve's*
**Dangling Depth Dweller** nails the drop: it **"slides down from above on its silk"** and uses a **leap
attack** — a ceiling ambush. *Don't Starve* dens also give the pack behavior: **step on the webbing → the
whole cluster erupts**; **attack one → the cluster is signalled to defend.** *Terraria's* Wall Creeper
**drops onto** the player from the nest ceiling.

**(c) BEHAVIOR SPEC → our sim (the top-down "drop-from-above" adaptation).**
- **`cave_spider_nest` occupant on the cave ceiling/wall** (a lair). It is dormant until the player enters
  its trigger radius **in darkness** (`PLAYER_CELL_ENTER` + the existing light/dark gate — the D21
  full-dark underground) — Minecraft's light rule becomes our **darkness-gated aggro**.
- **Drop = a telegraphed ambush SPAWN:** on trigger, the nest emits `SWARM_SPAWNED` for a **pack** of small
  cave spiders at cells near the player, each preceded by a **landing-shadow telegraph** (a marked cell for
  ~0.5 s before the spider resolves) — this is how "drop from the ceiling" reads in top-down with no Z axis.
  Reuse Nest/Brood spawn plumbing.
- **Pack behavior:** small fast swarms with the **stalk→leap** pounce (§4 tech) and a shared **wake event**
  (§1) so the whole nest commits together (the Don't Starve cluster feel).
- **Venom:** each bite applies a **small `venom` DoT**; individually trivial, but the **pack stacks it** —
  the swarm's threat is *frequency* (many small bites), capped by the **bite-token pool** so it stays fair.
- **Light is the counter (diegetic):** carrying light / lighting the room **suppresses the darkness aggro**
  and stops the drop — ties directly to the glowworm/torch light economy of the underground zones.

**(d) Threat / role.** The **Swarm** role incarnate and the **underground headliner** — the reason the
Centipede Cavern + deeper is scary. Density is high, per-bite damage is low, the pack drop is a genuine
"oh no" moment. This is the "**spiders & webs in the underground (don't forget!)**" backlog item realized.

**(e) Telegraph + counterplay.** Tells: the **nest is a visible ceiling/wall lair**; the **landing shadows**
telegraph each drop (the top-down fairness fix — you always see where they'll land); the aggro is
**darkness-gated** so you're warned by the dark itself. Counter: **bring light** (suppresses the drop),
fight in a lit choke, or destroy the nest. Fairness: token-pooled DPS + landing shadows + a light counter =
scary density that never becomes an unreadable pile-on.

---

## Source table (deep-read → fact → mechanic hook)

| Source | Key fact mined | Mechanic hook for us |
|---|---|---|
| **Grounded — Wolf Spider** ([wiki.gg](https://grounded.wiki.gg/wiki/Wolf_Spider)) | Nocturnal; snarls + chases on sight; **approaches your location before it sees you** (pre-stalk); fast stride; bite / 5-combo / **charged lunge (venom)** / **jump-dive**; perfect-block counter | The active-hunter stalk→pounce (§3, §4); pre-sighting stalk = server-only slow legs; venom DoT; night gate |
| **Grounded — Orb Weaver** ([wiki.gg](https://grounded.wiki.gg/wiki/Orb_Weaver)) | Patrols + **periodically spins webs**; wakes if a web breaks / ally hurt; lunge / triple-bite / **charged bite that tracks** / **unblockable web-shot immobilize**; defensive web stance | Web-trap archetype (§1); web-shot = telegraphed slow projectile; ally/web proximity **wake event** |
| **Grounded — Arachnophobia slider** ([Game Rant](https://gamerant.com/grounded-how-to-use-arachnophobia-mode/), [Windows Central](https://www.windowscentral.com/grounded-arachnophobia-safe-mode)) | Accessibility-tab **0–5 slider**, live-adjustable, live preview; strips legs→body→textures→"two eyes + hitbox"; **does NOT change behavior/difficulty** | Our arachnophobia-safe toggle (below): purely a client render swap, zero sim effect |
| **Terraria — Wall Creeper** ([wiki.gg](https://terraria.wiki.gg/wiki/Wall_Creeper)) | **Climbs background walls (Spider AI)**, reverts to fighter AI off walls, **drops onto** player; **can't pass a 2-tile shaft**; Spider Nests marked by cobwebs | Top-down wall-cling (§5 huntsman); drop-from-nest (§8); tight-tunnel spatial counter |
| **Don't Starve — Spider / Spider Queen** ([wiki.gg](https://dontstarve.wiki.gg/wiki/Spider)) | Nocturnal, sleep by day; **step on webbing → cluster erupts**; **attack one → whole cluster defends den**; Queen spawns from Tier-3 den after 60–120 s proximity; Warrior defends den | Cluster **wake event** (§1,§2,§8); funnel/tarantula den-ambush; den = nest occupant |
| **Don't Starve — Spitter & Dangling Depth Dweller** ([Spitter wiki.gg](https://dontstarve.wiki.gg/wiki/Spitter), [DDD search]) | **Spitter = rapid ranged web-balls + snap when close**; **DDD slides down silk from above + leap attack** | Ranged web-shot (§1 variant); **drop-from-above** = telegraphed ambush spawn (§8) |
| **Hollow Knight — Nosk / Deepnest** ([hollowknight.wiki](https://hollowknight.wiki/w/Nosk)) | **Mimic lure** (looks like the Knight), **hangs prey from the ceiling**, ambushes on arena re-enter; **screech→charge across arena**, leaps, infection spew | The dread/lure ambush tone; charge = a long telegraphed traverse-lunge; ceiling-hang flavor |
| **Minecraft — Cave Spider** ([minecraft.wiki](https://minecraft.wiki/w/Cave_Spider)) | **Spawns from mineshaft spawners at light 0**; tiny, **fits 1-block gaps**; **Poison** (Normal/Hard); **neutral in light ≥12 / hostile in dark**; slow (0.3) but swarms | Cave-spider pack (§8): nest spawner, **darkness-gated aggro**, light = counter, venom DoT, swarm |
| **Spider hunting biology** ([CSU Ext.](https://extension.colostate.edu/resource/spiders-in-the-home/), [UMD Ext.](https://extension.umd.edu/resource/predatory-spiders), [Britannica](https://www.britannica.com/animal/spider-arachnid/Feeding-behavior), [Australian Museum](https://australian.museum/learn/animals/spiders/prey-capture-and-feeding/)) | Jumping = stalk to 5–10 cm then pounce (diurnal, big eyes); wolf = webless nocturnal active hunter; orb-weaver = wheel web, poor vision, feels vibration; funnel = sheet+tube, waits at mouth | Grounds the per-type *role* split — stalk-leap / active-hunt / web-trap / tube-ambush |
| **Huntsman / tarantula / widow biology** ([Wikipedia](https://en.wikipedia.org/wiki/Huntsman_spider), [HowStuffWorks](https://animals.howstuffworks.com/arachnids/huntsman-spider.htm), spiderzoon) | Huntsman = webless, **very fast, crab-like sideways legs, wall-favoring**; tarantula = **burrow ambush, slow, heavy, high bite force**; widow = **tangle web + potent neurotoxin, saves energy, waits** | Huntsman speed-skirmisher (§5); tarantula burrow-tank (§6); widow venom-lurker (§7) |

---

## Scored: which spiders to build FIRST

Axes (1–5, higher = better): **threat/memorability · fits-our-sim (reuse) · dev cost (5 = cheap) · variety
it adds**. Verdict from the totals + the phasing in `design_ants_spiders.md`.

| Spider | Threat/memory | Fits sim | Dev cost | Variety | Verdict |
|---|:--:|:--:|:--:|:--:|---|
| **Jumping — stalk-leap** | 3 | 5 | 5 | 3 | **PICK #1.** Pure `ActionState` reuse, no new data; the safest end-to-end proof of the pounce tech (`design_ants_spiders.md` agrees). |
| **Orb-weaver — web trap** | 5 | 4 | 3 | 5 | **PICK #2.** The signature, screenshot-worthy spider; proves the `spider_web`+`web_slow` occupant tech that 4 other types reuse. Highest variety. |
| **Cave spider — drop pack** | 5 | 4 | 3 | 4 | **PICK #3.** D21's mandate + the "don't forget underground spiders" backlog; proves the telegraphed ambush-spawn ("drop") + darkness-gated aggro; the underground headliner. |
| Wolf — active hunter | 5 | 5 | 4 | 3 | Strong, but **same core tech as jumping** (stalk→pounce) — build as a *tier-up variant* of #1, not a separate first effort. |
| Funnel — ambush burst | 3 | 5 | 4 | 3 | Cheap reuse (ActionState burst + retreat); good *second wave*, lower memorability alone. |
| Black widow — venom lurker | 4 | 4 | 4 | 3 | Reuses the web tech + a DoT knob; a **payload variant** of the orb-weaver — build after #2. |
| Huntsman — wall skirmisher | 3 | 4 | 3 | 4 | The top-down wall-cling needs a new pathing-preference pass; fun variety but not first. |
| Tarantula — burrow tank | 4 | 4 | 3 | 3 | The Tank; needs an HP/on-hit-deterrent layer; a later "heavy" for deep chambers. |

**PICK: Jumping spider → Orb-weaver → Cave spider.** In that order they (1) prove the pounce, (2) prove the
web occupant, (3) prove the ambush-spawn — the three primitives every other spider reuses. Wolf, funnel,
widow, huntsman, tarantula then fall out as **variants that recombine those three primitives** (cheap
variety, the "function not stats" way).

---

## Arachnophobia-safe toggle (ship it — it's cheap and it's the right call)

*Grounded's* model is the proven standard and it's **purely cosmetic**: an **accessibility-menu slider
(0–5), adjustable live with a preview**, that progressively strips spider-ness (8 legs → 4 → none → no
face → just eyes+hitbox) and **does not touch behavior or difficulty**.

**For us this is a client-only render swap — zero sim/determinism impact** (it changes nothing the server
emits, so it can't affect sync):
- A **setting** (0–3+) that, at the spider **sprite-load** step, substitutes an alternate sprite: e.g.
  L0 normal → L1 fewer/no legs → L2 a neutral "crawler blob" / rounded critter → L3 a plain marker
  (colored dot + eyes). Because the sim only knows the entity id + center legs, swapping the *sprite* is
  invisible to it.
- Keep **all telegraphs, shadows, and audio** — fairness/readability must not degrade (an accessibility
  option can't make the game unfair). Optionally offer a "less-skittery motion / reduced count visual"
  purely as a render/animation tweak, still sim-identical.
- Because our art is data-driven (`bugs.json` sprite keys), the alternate skins are just extra PNGs keyed
  off the setting — no code in the sim path.

---

## Owner questions (taste / scope — not guessed)
1. **How lethal is spider venom?** DoT stacks (cave-spider pack, widow) can get punishing. Cozy-light
   (short, small ticks) or genuinely dangerous at night/in the deep (Don't-Starve-tense)? This sets the
   whole family's damage dial.
2. **Do we want a true ranged attacker (orb-weaver web-shot / a spitter)?** It's the one place we'd add a
   small new authority-relayed event (a projectile), and it changes how the player closes distance. Worth
   it, or keep spiders melee-only for v1?
3. **How far into "drop-from-above"?** The telegraphed **landing-shadow ambush spawn** is our honest
   top-down answer to a ceiling drop — do you want that theatrical spawn, or should cave spiders just walk
   out of a wall nest (simpler, less "gotcha")?
4. **Webs as an ecology disruptor?** Should orb-weaver/tangle webs actually **catch the player's farmed
   bugs** (a real reason to clear them, ties spiders into the farming loop) or stay purely a player hazard?
5. **Arachnophobia default + granularity** — ship the 0–3 slider as above? And do we want a single global
   toggle plus the slider, defaulting to OFF (full spiders)?
6. **Surface wolf spiders?** D21 currently confines spiders to the deep underground. Do you want a
   **night-time surface wolf spider** (the Grounded terror) as a top-side threat, or keep spiders
   underground-only?

---
### Coverage note (honesty)
Game research is a fresh deep-read of 5 titles (Grounded, Don't Starve, Terraria, Hollow Knight, Minecraft)
across 10 sources + 4 biology sources; the sim mapping reuses the **already-code-verified** primitives in
`design_ants_spiders.md` (pounce = `centipede.go:65` ActionState; web = `spider_web` occupant + `web_slow`;
strikes = `BUG_REMOVED`; aggro/flee = `PLAYER_CELL_ENTER`). The **web-shot projectile** and the
**landing-shadow ambush spawn** are the two places this doc proposes *new* mechanics beyond the approved
design — both flagged as owner questions and both designed to stay authority-relayed / fixed-point. Real
cave-spider-specific biology is thin (in-game the "cave spider" is a game archetype); §8 leans on the D21
decision + the game templates rather than field biology, and says so.
