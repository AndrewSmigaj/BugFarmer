# Bugs: flying pests & stingers (flies, mosquitoes, wasps, HORNETS)

*Topic 2 of the 2026-07 research. How to implement the game's real aerial THREATS, grounded in real
biology (14 deep-read sources) mapped to readable, fair mechanics for our deterministic swarm sim.
Hornet was a specifically requested enemy — it gets a marquee design. Raw transcript:
`../_raw_recovered/bugs/a6e6cea1898d67583.md`.*

## The five readable wins (the core takeaways)
1. **Mosquito "cast-and-surge" = a telegraphed wavy approach.** Real mosquitoes surge upwind while in a CO₂
   plume and cast side-to-side in 30–60° arcs (~2–3 s) when they lose it. In-game: the mosquito approaches in
   a **visible zig-zag hunting the scent**, not a straight line — the player *sees* it hunting and dodges by
   breaking the line. The single most readable enemy motion in the set.
2. **Alarm pheromone = a "recruit more attackers" system.** Disturb a nest → escalating waves. **Swatting/
   crushing ADDS attackers** (releases pheromone). Yellowjackets even **mark** the player for the whole colony.
3. **The smoker is the canonical counter** — it **masks the alarm pheromone** (breaks the recruit loop) and
   **pacifies via a gorging/evacuation instinct**. A perfect diegetic beekeeper item (we already have a smoker).
4. **Concrete, tunable aggro triggers** (quantified by a real color study): **dark/black target = high aggro**
   (black drew ~26 attackers for 82 s; light colors ~0), **vibration/running = trigger**, **standing still +
   light-coloured + quiet = safe**, **sound doesn't matter**, nests safest to clear **at night**, and aggro has
   a **leash range** (a few hundred feet) so escape always works. This is a ready-made fair aggro table.
5. **Distinct archetypes fall out of biology for free** — slow homing mosquito (heat/CO₂) vs. fast daytime
   horsefly (movement/dark) vs. un-swattable housefly (evasion gimmick) vs. crop-ruining spotted-wing vs. the
   giant-hornet **hive-raid boss** vs. the botfly **parasite-via-carrier**.

## Source table (deep-read → fact → mechanic hook)
| Species | Key real facts | Mechanic hook |
|---|---|---|
| **European hornet** | carnivore(spring)→scavenger(fall); night-active, light-drawn; "alarm dance" (buzz, dart in/out) before defending; stings when grabbed/stepped on | Telegraphed **alarm-dance wind-up** before the swarm commits; seasonal AI mode-switch; light lures it at night |
| **Asian giant hornet** | **slaughter phase**: 1 hornet = up to **40 bees/min**; **<50 wipe a 10,000-hive in hours**; a **scout** lays a trail to recruit a raiding party; 40 km/h, 100 km/day | **Hive-raid BOSS** that wrecks the player's apiary/bug-farm; a **scout** that, if it escapes, returns with a raid party; counter = trap-and-overwhelm (the bees' 46 °C "heat-ball") |
| **Bald-faced hornet** | big aerial paper nest (≤58 cm); **repeatedly stings**; can **spray venom into eyes → temporary blindness** | A **ranged "venom spit"** variant → screen-blur/blind debuff; distinct from melee stingers |
| **Yellowjacket** | ground OR aerial nests; **sting repeatedly**; **mark aggressors & pursue**; crushed body summons nestmates; late-summer → aggressive sugar/fruit scavenging | **"Marked" status** (whole nest prioritizes you); **late-season difficulty ramp** (calm early → aggressive fall) |
| **Paper wasp** | least aggressive; **3-stage tell**: raise wings → patrol nest → fly out & sting; hunts caterpillars | The cheap **warning-grammar teacher** — a low-threat enemy whose visible escalation trains the player to read tells |
| **Mosquito** | CO₂ plume (>500–600 ppm) + heat + dark/high-contrast visuals; **cast-and-surge** wavy flight ~0.5–2 km/h; only females bite; crepuscular (Aedes/tiger by day) | Slow **telegraphed homing** pursuer; dark clothing = more aggro; break the scent line to dodge; day vs dusk variants; disease = status payload |
| **Horsefly** | only females bite (slice flesh); home on **polarized light off dark, MOVING objects**; **very fast** (≤145 km/h); daytime only | **Fast daytime melee chaser** keyed to movement + dark; escape via **shade / breaking sight**, not outrunning |
| **Housefly** | **sees ~7× faster than humans** → dodges slow swats; erratic looping; lays 75–150 eggs on rot; contaminates | **Un-swattable nuisance** (reaction-time gimmick); clouds around compost/rot; spreads contamination to crops |
| **Spotted-wing drosophila** | **serrated ovipositor lays eggs in RIPE, undamaged fruit**; 300 eggs, 13 gen/season | The true **crop antagonist** — ruins *ripening* harvest → a harvest-before-infestation race with real stakes |
| **Botfly** | **phoresy** — glues eggs to a captured mosquito/fly; host heat hatches them; larva burrows | **Two-stage parasite**: hijacks a carrier bug as delivery; kill the carrier or take a lingering debuff |

## MARQUEE DESIGN — the Hornet (requested)
A tiered hornet family that reads clearly and escalates:
- **Common hornet (patrol threat).** Patrols near its nest; **alarm-dance wind-up** (buzz + dart in/out, a
  clear ~0.5 s tell) before a committed **dive-sting**, then retreats (sting-and-retreat, not a persistent
  cloud). Aggro from the trigger table (dark gear / running / nest proximity); leash range lets you flee.
- **Nest defense = the recruit loop.** Hitting/approaching the nest emits an **alarm influence event** that
  recruits N more defenders in escalating waves; **swatting a hornet adds one** (pheromone). The **smoker**
  suppresses the alarm event (no recruitment) and pacifies — the intended counter, using our existing item.
- **Giant hornet (mini-boss raid).** A **scout** appears near the player's apiary; if it isn't killed before it
  leaves, it **returns with a raiding party** that will **wreck beehives/bug-farms fast** (the "slaughter
  phase"). Counter mirrors the bees' heat-ball: funnel + overwhelm (e.g. lure into a trap, or a defended
  choke). This is the marquee threat with real stakes to the farm.
- **Bald-faced variant (ranged).** A **venom-spit** that applies a brief screen-blur — a distinct attack that
  makes the player close differently.

All of it fits our sim as **influence events**: the alarm/recruit is one authority-emitted zone-wide event
(like nest defenders already recall); the dive-sting is a telegraphed leg + an authority-relayed hit
(`BUG_REMOVED`-class); aggro/leash are integer accumulators; the smoker toggles a server flag. Nothing here
reads view-scoped data into the sim.

## ≥4 scored candidate "aerial-attacker attack patterns"
Axes: **threat · fairness/readability · determinism fit · dev cost** (1–5).

| Pattern | Threat | Readable/fair | Determinism | Dev cost | Verdict |
|---|:--:|:--:|:--:|:--:|---|
| **A. Telegraphed dive-sting-and-retreat** (alarm-dance wind-up → dive → retreat) | 4 | 5 | 5 | 3 | **PICK.** Fair (clear tell), dodgeable, integer legs; the hornet/wasp default. |
| **B. Cast-and-surge homing** (mosquito zig-zag) | 3 | 5 | 4 | 3 | **PICK for mosquitoes.** Most readable motion; break line-of-scent to dodge. |
| C. Persistent harass cloud (always on you) | 3 | 2 | 4 | 2 | REJECT for damage — unfair/unreadable; fine for the *non-damaging* housefly nuisance. |
| D. Ranged venom-spit (blind debuff) | 4 | 4 | 5 | 3 | Keep as a **variant** (bald-faced) — needs a clear tell + short range to stay fair. |
| E. Instant un-telegraphed sting | 5 | 1 | 5 | 1 | REJECT — the "impossible flying attacker" anti-pattern. |

## Anti-patterns
- **Un-telegraphed flying attacker** you can't react to (the classic "impossible to hit / unfair sting").
- **Persistent damage cloud** with no counterplay — use it only for the non-damaging housefly.
- **Swatting reduces the threat** — invert it (crushing releases pheromone → *more* attackers) so the smoker/
  running-away counters are the intended play.
- **No leash** → can't escape → cozy game becomes stressful.

## Open questions (owner taste — not guessed)
1. **How lethal is the giant-hornet raid?** Should it be able to actually destroy hives/kill bug stock (real
   stakes, Don't-Starve-tense) or just steal/damage (softer)?
2. **Do we want the aggro trigger table wired to real player choices** (dark gear = more aggro, standing still =
   safe), or keep aggro simple?
3. **Disease/parasite payloads** (mosquito, botfly) — do we want status effects in a cozy game, or is that too
   punishing?
4. **Day/night + seasonal aggression ramps** — worth the systems, or keep bugs season-agnostic?

---
### Coverage note (honesty)
The flying-pests/hornet biology survived in full (this doc). The **spiders, scorpions, and gentle-pollinator**
research agents mostly died early on the session limit — that per-species research is thin/incomplete in the
recovered set and should be re-run at low concurrency (see `no-wide-agent-fanout`). `../bugs/README.md` tracks
which families are solid vs. owed.
