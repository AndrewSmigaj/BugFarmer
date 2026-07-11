# Deep research — 2026-07 (combat · bugs · station minigames · visuals)

Overnight research across four topics. **A process note up front (honest):** this run launched too many
research agents, which spawned their own sub-agents and burned the session limit before most agents wrote
their final docs. The **research itself survived** in the agent transcripts and was recovered; the clean docs
below were then rebuilt from it. See the `no-wide-agent-fanout` memory for the rule this violated. Raw
recovered research (permanent) lives in `_raw_recovered/`.

## The map

### 1. Combat / enemy AI — `combat/` — **COMPLETE (3 docs)**
- **`01_melee_enemy_ai.md`** — steering (seek/arrive/pursue) + FSM/BT/utility/GOAP compared; the **attack-token
  "stage manager" (Belgian AI)** as the deterministic-server sweet spot; anti-patterns; determinism landmines.
- **`02_swarm_group_ai.md`** — flow fields vs per-unit A\*; boids separation; sticky priority targeting;
  magic-box cohesion; mapped to our `SWARM_SET_TARGET` legs.
- **`03_challenge_and_effectiveness.md`** — L4D threat director, **bite-token pool**, WoW threat tables, enemy
  **roles/variety** (function-over-stats), telegraphing; all integer/deterministic; the "cozy but threatening" model.

### 2. Bugs (per-species behaviour) — `bugs/` — **PARTIAL (1 doc + index)**
- **`flying_pests_stingers.md`** — DONE. Flies/mosquitoes/wasps/**hornets** grounded in 14 biology sources;
  the marquee **giant-hornet hive-raid boss**, mosquito **cast-and-surge**, alarm-pheromone recruit + smoker counter.
- **`README.md`** — honest coverage: **scorpions/centipedes + spiders + pollinators survived only as raw/partial**
  recovered research (those agents died early). Flagged for a low-concurrency re-run; raw material is a head-start.

### 3. Station minigames — `station_minigames/` — **COMPLETE (2 docs)**
- **`01_minigame_taxonomy.md`** — the key genre signal (**processing = passive timers, not minigames**; forcing
  them → the "mobile-game timer" backlash); the two proven primitives (click-to-stop, catch-bar); the
  perfect=bonus/never-lose-input reward model.
- **`02_per_station_proposals.md`** — a proposal per station across 3 shared primitives; client-skill-check →
  server-tier netcode note.

### 4. Visuals (Unity URP-2D) — `visuals/` — **PARTIAL (1 doc + index)**
- **`01_unity_urp2d_lighting_and_rendering.md`** — DONE, project-grounded. The ranked lighting/render levers:
  **Falloff Strength fixes the hard lamps · Bloom is one flag away · warm/cool contrast · sprite-cookie lights ·
  emissive accents · (normal maps = the expensive lever).**
- **`README.md`** — art-direction reference + asset-pack survey survived as raw; synthesis owed. This is the
  owner's core "other games look more interesting" concern — the art-direction (not tech) angle.

### Cross-cutting
- **`SELF_CRITIQUE.md`** — what's missing per topic, other approaches we didn't cover, and how I'd go deeper
  (the requested self-review pass).
- **`_raw_recovered/`** — the permanent raw research the clean docs were built from.

## What's owed (for the low-concurrency re-run)
1. **Bugs:** clean per-type docs for **spiders** (wolf/jumping/orb/funnel/huntsman/tarantula/widow/cave),
   **scorpions**, and **gentle pollinators** — raw material exists, synthesis + more depth owed.
2. **Visuals:** the **art-direction** synthesis (palette cohesion, making AI-sprites cohere) + the **asset-pack** shortlist.
3. All re-runs at **≤2 self-contained agents that write incrementally** (`no-wide-agent-fanout`).
