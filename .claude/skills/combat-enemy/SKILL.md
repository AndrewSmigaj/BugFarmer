---
name: combat-enemy
description: Use when adding or tuning a COMBAT enemy (a bug that threatens the player) — a new species tier, a difficulty dial, a nocturnal night-hunter, or debugging why an enemy does/doesn't sting. Covers the species combat fields, the M1 per-individual telegraphed-sting foundation, the difficulty knobs, the nocturnal gate, and the arena test loop. For the ART pipeline see add-object; for ecology/spawn balance see ecology-tuning.
---

# Add / tune a combat enemy

The combat foundation is BUILT and everything reuses it — most new enemies are **pure data** (a `species.json`
entry + a sprite + a carcass item), **no new code**. Read the as-built first:
[`architecture_combat.md`](../../../docs/product/architecture/architecture_combat.md) §§ "Milestone 1" and
"Milestones 2–3". Runs inside the deterministic swarm sim — see `architecture_swarm_sync.md` §0.

## The foundation you're building on (don't rebuild it)
- **Per-individual telegraphed sting** (M1): the authority client detects which INDIVIDUAL bug is in
  `stingRange` (1.5) + line-of-sight of a player and reports it (`SwarmManager.RunBugPlayerStrikes` →
  `BUG_PLAYER_STRIKE`); the server **arms a two-beat wind-up** (`handleBugPlayerStrike` flashes a `"windup"`
  telegraph + schedules the hit `stingTelegraphTicks` later) and `processPendingStings` lands it, re-gated so a
  **dodge or step-out negates it**. Fires for **any** species with `attack_damage > 0`. You do NOT touch this.
- **Player HP is SIM-INERT** — damage/attack timers are server-only, never in the client hash. So a new enemy's
  combat needs **no ledger/snapshot/hash wiring** (unlike a movement mechanic). This is why tiers are just data.
- **Three ways an enemy engages the player** (a known overlap, tracked for a future consolidation): (a) the
  **centipede surge** (`centTriggerRange`→windup→lunge, its own ActionState) — used by every `individual`+predation
  crawler; (b) **wasp nest-defence** (`predationThink` "defending"); (c) **generic aggro** (`aggroPlayerThink`) —
  any attack-capable NON-centipede swarm chases a player within ~8 cells (capped by its vision). So a new swarm
  attacker WILL now pursue you; a new centipede tier pursues via the surge.

## Add an enemy tier (the common case — data only)
1. **`nakama/data/species.json`** — the combat spec. Clone the nearest existing species and dial the knobs.
   - **`category`** decides the AI: **`swarm`** = a cloud (+ a `predation` block → nest-predator hunt/defend, like
     wasps); **`individual`** = a single big crawler. ⚠️ `individual` + a `predation` block invokes the
     **centipede surge/lunge ActionState** (`match.go` gate `Predation != nil && Category == "individual"`) — this
     is how a **centipede tier** attacks (clone `centipede_garden`). A `swarm` attacker uses the ambient
     per-individual sting + generic aggro instead.
   - **Difficulty knobs** (no new code): `attack_damage` (per-hit) · `attack_cooldown` (frequency — but the **1 s
     shared invuln floors real damage at ≤1 hit/s**, so cd < 1.0 buys nothing) · `base_speed` (+ `predation.
     hunt_speed_mult`) for escape pressure · `vision_range` / `predation.home_range` for the aggro net · `max_hp`
     (hits-to-kill by the player's weapon) · `min/max_swarm_size` (cloud size).
   - **`nocturnal: true`** → lies low by day, full threat at night (server-gates the sting + hunt/defend; see below).
   - **`attack_is_sting`**: `true` = a sting the bee-suit (`sting_immune` body armor) negates; `false` = a
     bite/spines it does not. `sprite_id` → `Resources/Bugs/<sprite_id>.png`. `carcass_item` → a real `items.json` id.
2. **`nakama/data/bugs.json`** — the art-source row (`sprite_path`, `sprite_w/h`, `category`) that `gen_sprites
   --source bugs` reads.
3. **Carcass item** — if it's a new `dead_<x>`, add it to `nakama/data/entities/items.json` (+ a
   `tools/art/catalog/items.json` `look` row, `family: icon`) so the drop isn't a placeholder. Wasps can reuse
   `dead_wasp`.
4. **Sprite** — a `tools/art/catalog/bugs.json` `look` row (top-down, `family: creature`; SHAPE + key parts in
   CAPS + color + what it must NOT be mistaken for), then generate (see **add-object**; default is
   gpt-image-1.5 / medium): `python3 tools/sprites/gen_sprites.py --source bugs --keys <id>`. **Acceptance-check
   the full-res raw** in `tools/_generated/raw/<id>.png` — clear top-down silhouette, reads as the intended
   creature, correctly tiered menace.
5. **Publish + verify:** `python3 tools/data/publish_entities.py` (copies `species.json` + entities to the client),
   then confirm the new ids landed in `BugFarmerClient/Assets/Resources/Data/species.json`.

## Nocturnal (a night hunter)
Set `nocturnal: true`. The gate is server-side + deterministic (`isNightForHunting(state)` in `handlers_env.go`,
active window **[0.55, 0.90)** — tracks the client's VISUAL night, so the F8 "Night" button (t≈0.70) is night and
"Evening"/"Noon"/"Morning" are day). It gates the STING (`handleBugPlayerStrike` won't arm by day), the generic
AGGRO, and predator hunt/nest-defend — all output only legs / server HP, so no determinism surface. **Only flag a
genuinely night-active real species** (a moth, some beetles) — NOT a diurnal one (wasps/hornets read as wrong).

## Test loop (the arena)
- **In-game:** join the **Arena** zone (world menu) → **F8** debug panel → `<`/`>` pick the species, `-`/`+` count,
  "Spawn at player". Nest predators need a `wasp_nest` present to show DEFENDING pursuit; otherwise they
  ambient-sting when you enter the cloud. Test night behavior via the debug time control
  (`DebugWorldMessage.set_time_ticks`).
- **Gates (test-changes skill):** `bash tools/run_go_tests.sh` (add a `bug_player_strike_test.go`-style case if you
  touched a server gate) + the headless `sim-determinism` gate (a data-only tier that reuses an existing
  `movement_style` stays deterministic — but RUN it). A `nocturnal`/gate code change also wants the 2-client
  `run_sync_latejoin` regression once the plugin is deployed.

## Tuning an existing enemy
Same knobs, edit `species.json`, `publish_entities.py`, re-test in the arena. For POPULATION / spawn balance (how
many appear in a real zone), that's a different job — use **ecology-tuning** (caps, spawn circles, the Director),
not this skill. This skill owns the per-enemy COMBAT feel; ecology owns how many exist.

## Segmented crawler tiers (centipede / millipede)
A crawler renders as a head + trailing body/tail chain (`CentipedeTrail.cs`). To give a new tier its OWN segmented
look (not the shared green centipede body):
- `sprite_id` = the **head** sprite (`Resources/Bugs/<sprite_id>.png`); id must contain `"centipede"` so the
  segmented render + surge gates fire.
- `sprite_family` (species field) = the body/tail set → `CentipedeTrail` loads `<sprite_family>_body_b` +
  `<sprite_family>_tail_b`. Omit → the legacy centipede/millipede fallback.
- `render_scale` (species field, default 1.0) = a size multiplier (a giant tier ~1.4).
- Generate the 3 segment sprites (`_head`, `_body_b`, `_tail_b`) with **FLAT top/bottom edges** so they chain
  (per the `centipede_head_b`/`body_b`/`tail_b` catalog looks). Reuse `dead_centipede` as the carcass.

## Known gaps (tracked, don't re-derive)
- **No per-species token pool yet** — the sting token pool (≤2 individuals commit at once) is a global const;
  "higher tiers bite more at once" needs a small `attack_tokens` field wired into `RunBugPlayerStrikes` first.
- **Two damage-detection paths + 3 aggro triggers** — the centipede surge vs the wasp per-individual telegraph both
  feed the ONE funnel (`applyBugAttackToPlayer`); aggro is surge-trigger / nest-defence / `aggroPlayerThink`.
  Unifying them is a deliberate FUTURE refactor (the deferred "M4 regroup" + threat-table), not something to bolt
  onto — reuse the existing model when adding a tier.
