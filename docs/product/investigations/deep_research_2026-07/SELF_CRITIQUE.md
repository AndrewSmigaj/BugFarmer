# Self-critique — what I missed, other approaches, and how I'd do it

*The requested cross-cutting pass: for each topic, "was there anything else I could look into that I missed?
Other interesting approaches? How would I do it?" Written after the docs, deliberately adversarial toward my
own work.*

## UPDATE 2026-07-11 — most of this critique has since been ADDRESSED
A supplemental thorough pass acted on the gaps below (≤2 self-contained write-to-disk agents, the fixed way):
- **Combat player-side** → now `combat/04_player_combat_and_bosses.md` (dodge+i-frames prereq, hornet-raid boss
  structure, co-op, netcode). ✅
- **Bugs: spiders / scorpions / pollinators** → now `bugs/spiders.md`, `bugs/scorpions_centipedes.md`,
  `bugs/pollinators_gentle_fliers.md`. ✅
- **Minigames: forge-genre depth + the economy-quality check** → forge deep-dive added to
  `station_minigames/02`; verified our economy has **no quality axis** (reward = speed/yield). ✅
- **Visuals: art-direction/cohesion + LUT + asset packs** → now `visuals/02_art_direction_and_cohesion.md`;
  verified the `DefaultVolumeProfile`/no-LUT state and added the cohesion note to `visuals/01`. ✅
**Still open (lower priority):** minor bug families (beetles/orthoptera/aquatic/ants); deeper visuals slices
(broad asset-pack survey, VFX Graph / custom passes). And the *real* next move below stands: **in-engine spikes,
not more reading.** The original critique text is kept intact below as the record.

## Meta (the biggest miss was the process itself)
The overnight run over-parallelized agents and burned the session limit — the research survived and was
recovered, but this should never have happened and cost real time/money. The rule is now in memory
(`no-wide-agent-fanout`): **≤2 self-contained agents that write incrementally, paced across time.** Every
"owed" re-run below must follow it. Beyond that, the topic-level gaps:

## 1. Combat — what I missed
The docs nail the **enemy** side (movement, attack-token pacing, threat director, telegraphs). Real gaps:
- **The PLAYER side is barely researched.** Combat is two-sided — dodge/roll + i-frames, weapon movesets &
  cancels, block/parry, stamina, hitstop/knockback feel. Our telegraph/recovery math is meaningless without a
  matching player-counter vocabulary. **Missed entirely.**
- **No boss-fight structure.** The giant-hornet raid is sketched as a threat, not as a *fight* (phases, arena,
  tells, checkpoints). Cozy games that add bosses (Stardew, Cult of the Lamb) have a specific structure I didn't cover.
- **Integration with the cozy loop is unanswered** — *when/where* does the player fight? Zone-gated? Night-only?
  Optional? This is the load-bearing design question and it's only an open-question, not researched.
- **Co-op combat** (our multiplayer) — shared aggro/threat across players, friendly-fire, revive/down states,
  scaling to N players. The threat-director research is single-player-shaped.
- **Reward/loot** — why fight at all in a farming game? Drops, essences, unlocks. Unresearched.
- **Audio + accessibility** — telegraph *sound* design and assist modes (the sources flagged audio tells but I didn't go deep).

**How I'd do it:** stop researching and **prototype** — build the attack-token pool + ONE telegraphed enemy in
the existing `feel_test` zone, playtest the actual feel, and let that drive the player-counter design. Feel
questions resolve in-engine, not on paper. Then a focused doc on player-side combat verbs + co-op threat.

## 2. Bugs — what I missed
- **The emphasized species (spiders, scorpions) only survived as raw** — the clean per-type docs the owner
  asked for aren't written. That's the headline gap.
- **Whole families untouched:** beetles/ladybugs, orthoptera (grasshopper/cricket/locust), aquatic
  (diving beetles/striders/backswimmer), and the gentle pollinators only partly.
- **The tie to our existing ECOLOGY sim is unexplored.** We *already* have deterministic predator-prey
  (centipede hunts, wasp nests). New "combat bugs" must reconcile with that — is a hornet an ecology actor, a
  scripted threat, or both? I researched them as enemies in isolation, not as members of the living food web.
- **Per-species animation** — the sprites exist but behavior-driven animation (a spider's pounce arc, a
  scorpion's tail-strike) wasn't specced.
- **Determinism/perf at scale** — adding rich per-bug behavior to a swarm sim that must stay bit-identical is a
  real constraint I flagged but didn't stress-test.

**How I'd do it:** one tight doc per marquee — **spider archetypes** (web-trap vs hunter vs ambush) and
**scorpion** — each with a concrete behavior spec expressed as our influence events + a determinism review,
cross-referenced against the `ecology-tuning` and `frontier-sync` skills so combat bugs and ecology bugs share
one model rather than fighting.

## 3. Station minigames — what I missed
- **Blacksmith/forge-genre depth.** The taxonomy leaned on farming-sims (where processing is passive). I did
  *not* deep-read the dedicated smithing games (Blacksmith games, SteamWorld, Shining Force forge, Under the
  Sea) where the strike/heat minigame is the whole point — the anvil proposal could be much richer.
- **Didn't validate against OUR economy** — the entire "perfect = quality bonus" model assumes a quality axis
  that may not exist. That's an open question, but I should have *checked the entity data* for a quality field
  before proposing the reward model. (Research-answerable; I punted it to the owner. Fixable.)
- **Accessibility & fatigue math** — no timing-assist / one-button mode; no estimate of how many times/day a
  player hits each station (which decides "minigame vs automate").
- **Multiplayer** — can a co-op partner do your craft's minigame? Flagged, not resolved.

**How I'd do it:** first **read our economy data** to answer the quality question myself (it's in the repo, not
a taste call). Then build the **click-to-stop** primitive as one reusable Unity component and A/B it on the
anvil in a playtest — the fatigue question only answers in the hand.

## 4. Visuals — what I missed (this is the owner's actual concern, and the weakest topic)
The lighting doc is strong and actionable, but the owner's real complaint — *"other games look more
interesting"* — is an **art-direction** problem, and that's exactly the part that survived only as raw:
- **Making AI-generated sprites COHERE** — our specific risk. Palette unification, gradient-map recolor to a
  master ramp, one consistent light direction across all sprites, a unifying color-grade/LUT post-pass. This is
  probably the single biggest lever for "looks like a game, not a pile of assets," and it's unsynthesized.
- **Tile variety / anti-repetition** — the #1 cause of "flat and samey" ground; not covered here (the prior
  research touched ground variety, but not the auto-variant/scatter techniques).
- **"1000 tiny motions"** — idle micro-animation on everything (grass tufts, water sparkle, hanging signs,
  chimney smoke, critters). Density of small motion is what makes Stardew/Spiritfarer feel *alive*; I have it
  as a principle, not a budget/plan.
- **A concrete look target** — we never picked a reference game to measure against. "Better" is unfalsifiable
  without one.
- **URP techniques beyond lighting** — a color-grading LUT (huge cohesion lever), full-screen custom passes,
  screen-space AO-between-sprites, decals, VFX Graph for ambient life. Only lighting got synthesized.
- **Asset packs** — the survey died; no shortlist (Feel/DOTween for juice, All-In-1 Sprite Shader, a
  post-processing/LUT pack) — all owed.

**How I'd do it (and I think this is the real answer to "higher visual quality"):**
1. **Pick ONE reference screenshot** (e.g. a Stardew or Spiritfarer frame) and break it down — palette count,
   value structure, light direction, motion density — as the concrete bar.
2. **Do a cohesion spike:** run our AI sprites through a **gradient-map palette-unification post-pass** + a
   single global **color-grade LUT**, and compare a before/after zone render. I strongly suspect *cohesion*
   (not more effects) is what's missing — disparate AI sprites read as "AI-generated" precisely because their
   palettes/light don't agree. This is testable in an afternoon and would tell us more than more research.
3. **Then** the config wins from the lighting doc (Falloff Strength, Bloom, warm/cool) which are near-free.
4. **Then** a motion-density pass (idle micro-animations everywhere) — the grass pass is the first of many.

## The one-line version
Combat and minigames are in good shape and research-complete; **bugs (spiders/scorpions) and visuals
(art-direction/cohesion) are the real remaining work**, and for visuals specifically I'd bet the biggest uplift
is **palette/light cohesion of our AI sprites + a LUT**, not another effect — and I'd prove it with a one-day
spike rather than more reading.
