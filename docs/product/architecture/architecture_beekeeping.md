# Beekeeping + the condition/subdual system

> System of record for the BEE LOOP (forage → honey → harvest → extract → craft) and the GENERAL
> calming mechanic it debuts (GDD §7.2/§7.3 — "calm bees AND OTHER INSECTS"). Shipped 2026-07-05.
> Code: `nakama/modules/world/{condition.go, nests.go, predation.go, handlers_hive.go,
> handlers_farming.go}`; data: `species.json` + `entities/{occupants,placeables,items,recipes}.json`.
> The zone that showcases it: `docs/product/zones/bee_meadow_20.md`.

## The player loop
Wild colonies live in tree hives; bees forage NECTAR from flowers (the existing depletable
`ForagePools` — flower density IS the honey economy), fly home, and deposit: brood grows the
colony and **every deposit also makes honey** (`honeyPerDeposit` × the hive's `world.hive.
honey_mult`, capped at its `honey_cap` — tiers: wild 3 / basic 4 / medium 6 / large 8 / deluxe 10,
deluxe accrues ×1.5). The player right-clicks a hive to hand-harvest whole honeycombs (OpCode
107/108, the tree-pick pattern) — which **RECALLS THE COLONY'S DEFENDERS onto them** unless the
hive was freshly smoked; the bee suit negates the STINGS, not the anger. Honeycomb spins into
honey ×2 OR beeswax ×1 at the honey_extractor (single-output recipes — each comb is allocated);
beeswax feeds candles (re-themed: beeswax + fiber). Maren the Beekeeper (bee_meadow_20) sells
beehive_basic / smoker / bee_suit / calm_spray and buys honey / honeycomb / beeswax.

## The bee, on the wasp-nest chassis
`bee_honey` is a NEST species with an EMPTY prey list. The one sim branch: a hungry prey-less
nest forager **DECLINES predationThink ownership** (the centipede carrion-first pattern) so the
SHARED forage block dines on nectar; at ≥90 satiation the provision block carries the load home
(brood + honey). The decline **normalizes Phase ""/idle → "feeding"** — nest species skip the
standard phase machine, and attractions are looked up BY PHASE; without the normalization a fresh
resident starves beside a full flower field (found by the bug_lab bee arena, run 1). Gentle-until-
provoked: `stings_only_defending` (checkBugAttacks skips unless Phase == "defending");
`flies_over_fences: true` (a fenced apiary must not trap residents); wasps prey on bees (GDD 9.2)
and dragonflies hunt the wasps.

**Player-placed hive boxes register DORMANT** (no free bees); a thriving colony (full patrol +
full brood bank) CLAIMS an empty box in range (`findClaimableBox`) — that's how an apiary comes
alive — else it founds a wild hive beside the richest flower field (`findNestSiteWithNectar`).
Recovery and founding are NECTAR-GATED (`nestCanFeedNearby`: hunters need live prey, foragers a
live ForagePool above the graze floor, both within home range).

## The condition/subdual system (§C — general, NOT bee-only)
`SwarmState.ConditionValue` (0-100) is the subdual meter, on the schema that was waiting for it:
- **Apply:** `ConditionValue = max(current, condition_tools[effect] × item effect_power)` — no key
  = that species is IMMUNE to that effect (opt-in map; every current species carries an explicit
  `condition_tools.calm` fill: bee 95, centipede 90, wasp 85, harmless 80). Decays
  `condition_decay`/s (default 2).
- **ONE threshold** (`condition_threshold`, default 40) means "subdued at/above" for BOTH behavior
  AND catching — never placid-but-uncatchable. Playable windows: bee ≈27s, centipede ≈25s.
- **All three aggression funnels honor it** (+ a belt in `applyBugAttackToPlayer`, the single
  damage funnel): (1) the ambient contact sting; (2) the centipede machine — no windup start,
  mid-windup/surge aborts to recover, no gnaw start, and an ALREADY-gnawing centipede stops
  (damage kept, no cooldown) — the GDD's "smoke it and walk past it", complete; (3) nest defense
  via ONE precedence rule at all three entries (passive proximity, recallNestDefenders, exit
  hysteresis): *defense is suppressed while (the resident is subdued) OR (the nest is smoked)*.
  `NestState.SmokedUntilTick` is the hive-local lingering smoke — the meter alone can't express
  smoke at the entrance while residents forage afield.
- **Catching:** `catch_condition: "calm"` (the bee debuts it) rejects agitated swarms in
  handleCatchBug right after the net-tier gate; all pre-bee species stay `"always"`.
- **Delivery — one network verb:** the smoker tool AND consumables (calm_spray, effect "calm",
  finally consumed) both ride ToolUse (OpCode 7). `handleSmoker` fills every calmable swarm in
  reach 4 + stamps hives; `handleConsumableUse` applies the item's effect in its `reach`,
  possession-checked, and a miss costs nothing. `EntityDef.EffectPower` is the tool-tier knob.

## Determinism boundary
Honey, ConditionValue, SmokedUntilTick, brood — all SERVER-ONLY soft state (persisted via the
WorldSave document, never hashed). Their observable outputs — the ABSENCE of stings/surges/defend
legs, spawns/removals — ride the existing ledger vocabulary (`SWARM_SET_TARGET` /
`SWARM_REPRODUCED` / `SWARM_SPAWNED` / `BUG_REMOVED`). **Zero new ledger events.** Gated by the
FRESH 2-client latejoin run, both halves SYNC IDENTICAL.

## The suit
`bee_suit` (body armor, `sting_immune`) is the game's first armor damage hook: in
applyBugAttackToPlayer, a sting-class attack (`attack_is_sting` — bees AND wasps) against a
sting-immune body piece deals 0; a centipede BITE lands regardless. Worn overlay layer-set exists
(pipeline B) but runtime composition is pinned off since the vector-Scout trial
(`ComposedOutfitsEnabled=false`) — immunity works now, the look lands with the wearables re-anchor.

## Backlogged (deliberate, not forgotten)
Smoker tiers via `effect_power` data · smoke_bomb/chill_canister/stun_rod · the "weakened"
catch_condition + the centipede subdue/drag/revive capture loop · SwarmMeterUpdate broadcast
(client meter UI) · mead/keg (D26) · the 4-piece suit set · the wasp nest-economy fix (their
starve square-wave predates all of this — see the ecology tuning log).
