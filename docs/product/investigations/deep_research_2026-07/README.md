# Deep research — 2026-07 (combat · bugs · station minigames · visuals)

Overnight research across four topics. **A process note up front (honest):** this run launched too many
research agents, which spawned their own sub-agents and burned the session limit before most agents wrote
their final docs. The **research itself survived** in the agent transcripts and was recovered; the clean docs
below were then rebuilt from it. See the `no-wide-agent-fanout` memory for the rule this violated. Raw
recovered research (permanent) lives in `_raw_recovered/`.

## The map

### 1. Combat / enemy AI — `combat/` — **COMPLETE (4 docs)**
- **`01_melee_enemy_ai.md`** — steering (seek/arrive/pursue) + FSM/BT/utility/GOAP compared; the **attack-token
  "stage manager" (Belgian AI)** as the deterministic-server sweet spot; anti-patterns; determinism landmines.
- **`02_swarm_group_ai.md`** — flow fields vs per-unit A\*; boids separation; sticky priority targeting;
  magic-box cohesion; mapped to our `SWARM_SET_TARGET` legs.
- **`03_challenge_and_effectiveness.md`** — L4D threat director, **bite-token pool**, WoW threat tables, enemy
  **roles/variety** (function-over-stats), telegraphing; all integer/deterministic; the "cozy but threatening"
  model. *(+ verified reality-check: we have movesets but no defensive kit.)*
- **`04_player_combat_and_bosses.md`** — the PLAYER side: **dodge+i-frames** as the load-bearing prerequisite
  (Gungeon-shape, server-owned invuln-tick window), weapon combos, hitstop, the **giant-hornet raid** boss
  blueprint, and **co-op** (shared threat, no friendly-fire, downed/revive, frequency-not-stat scaling).

### 2. Bugs (per-species behaviour) — `bugs/` — **COMPLETE for all requested families (4 docs + index)**
- **`flying_pests_stingers.md`** — flies/mosquitoes/wasps/**hornets**; the marquee **giant-hornet hive-raid boss**,
  mosquito **cast-and-surge**, alarm-pheromone recruit + smoker counter.
- **`spiders.md`** — all 8 types; built on our approved `design_ants_spiders.md` + Grounded/Don't-Starve
  research; build order **jumping → orb-weaver → cave**; client-only arachnophobia toggle.
- **`scorpions_centipedes.md`** — burrow-ambush scorpions (pincer/venom variant split) + segmented centipede
  (cosmetic path-sampled body); verified against our `centipede.go`.
- **`pollinators_gentle_fliers.md`** — butterfly/bee/firefly/dragonfly/mayfly/cicada/moth; alive-but-cosmetic
  flight overlay (no new determinism surface); firefly-glow flagged as the emissive gap.
- **`README.md`** — index. Remaining (never launched): the minor families **beetles/ladybugs, orthoptera,
  aquatic, ants** (ant material is largely prior-session colony work).

### 3. Station minigames — `station_minigames/` — **COMPLETE (2 docs)**
- **`01_minigame_taxonomy.md`** — the key genre signal (**processing = passive timers, not minigames**; forcing
  them → the "mobile-game timer" backlash); the two proven primitives (click-to-stop, catch-bar); the
  perfect=bonus/never-lose-input reward model.
- **`02_per_station_proposals.md`** — a proposal per station across 3 shared primitives; client-skill-check →
  server-tier netcode note.

### 4. Visuals (Unity URP-2D) — `visuals/` — **COMPLETE (2 docs + index)**
- **`01_unity_urp2d_lighting_and_rendering.md`** — project-grounded lighting/render levers:
  **Falloff Strength fixes the hard lamps · Bloom is one flag away (a `DefaultVolumeProfile` already exists) ·
  warm/cool contrast · sprite-cookie lights · emissive accents · (normal maps = the expensive lever) · no LUT
  exists yet = the cohesion gap.**
- **`02_art_direction_and_cohesion.md`** — the owner's core "other games look more interesting" concern. Why
  great 2D games look rich; the **AI-sprite cohesion pipeline** (master palette → global LUT → prompt-anchoring
  → post-gen palette clamp → one light direction → gradient-map rescue); tile variety; motion-density budget;
  **look-target = Stardew**; a verified **asset-pack shortlist**; pick order **LUT → palette-lock → tile-variety+motion**.
- **`README.md`** — index. Remaining (deeper, lower-priority): a broader **asset-pack survey** + **other-URP
  techniques** (VFX Graph, custom passes) still sit as raw recovered files.

### Cross-cutting
- **`SELF_CRITIQUE.md`** — what's missing per topic, other approaches we didn't cover, and how I'd go deeper
  (the requested self-review pass).
- **`_raw_recovered/`** — the permanent raw research the clean docs were built from.

## Status: all four topics + the emphasized gaps are DONE
The supplemental thorough pass (2026-07-11) filled every gap the self-critique found: player-side combat (04),
spiders, scorpions/centipedes, pollinators, art-direction/cohesion, the forge/blacksmith deep-dive, and the
verified economy/kit/Volume checks. 16 clean docs.

### What genuinely remains (lower-priority — do at ≤2 self-contained agents per `no-wide-agent-fanout`)
1. **Bugs — the minor families** not yet researched: beetles/ladybugs, orthoptera (grasshopper/cricket/locust),
   aquatic (diving beetles/striders/backswimmer). Ants exist mostly as prior colony work.
2. **Visuals — deeper slices:** a broader **asset-pack survey** and **other-URP techniques** (VFX Graph, custom
   full-screen passes) beyond the lighting + art-direction docs.

### The real next step is NOT more research — it's in-engine spikes (per `SELF_CRITIQUE.md`)
- **Visuals:** a one-day **LUT + palette-lock** cohesion spike with a before/after zone render (likely the
  single biggest look uplift — prove it before building more effects).
- **Combat:** prototype the **dodge+i-frames** verb + ONE telegraphed enemy in the `feel_test` zone and playtest.
- **Minigames:** build the **click-to-stop** primitive as a reusable component; A/B it on the anvil.
