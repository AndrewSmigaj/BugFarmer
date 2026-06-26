# Armor — the catalog (finalized 2026-06-25)

Two layers: a **base metal defense ladder** and a small set of **conceptual bonus sets** (not one-per-zone).
Per `DECISIONS.md` D10–D11. Stat vocab in `../stats_and_bonuses.md`; cost model in `../crafting.md §1`.
Design-only. Per-set DEFENSE numbers are tuned against zone enemy damage later → **backlog** (D11).

---

## (A) Base metal sets — the pure-defense ladder
**9 sets, leather → platinum** (5 pieces each: head/body/arms/legs/feet). Defense rises smoothly; the base set
always out-tanks a same-tier bonus set (bonus sets buy power in a *signature stat* instead).

| Set | Tier | Station | Source of material | Defense band |
|---|---|---|---|---|
| **leather** ✅(pieces) | T1 | bug-leather station + workbench | **bug-leather station**: dead bugs → leather (no skinning) | low |
| **padded (cloth)** | T1–T2 | loom | **cloth** — from **silk + cotton** (+ other fibers) | low |
| **copper** | T2 | anvil | copper_bar | low-mid |
| **bronze** | T2–T3 | forge | bronze_bar | mid |
| **iron** ✅ | T3 | anvil | iron_bar | mid |
| **steel** | T4 | forge | steel_bar | mid-high |
| **silver** | T4 | forge | silver_bar | high |
| **gold** | T5 | forge | gold_bar | high |
| **platinum** | T5 | forge | platinum_bar | **top** |

**Cut:** ~~straw~~ (too hard to integrate), ~~diamond~~ (platinum is the top — diamond armour doesn't make
sense). Existing `items.json` ids reused: the full `leather_*` and `iron_*` sets, `copper_helmet`.

**New stations/materials this implies:** a **bug-leather station** (dead bugs → `leather`), **cotton** as a
cloth source (D15).

---

## (B) Conceptual bonus sets (consolidated — D10)
Sets are *concepts*, not one per zone. Each = base-ish defense **+ a signature stat** + a set bonus. Far/late
ones are **designed but PENDING** until we reach those zones.

| Set | Concept / where | Tier band | Signature stat(s) | Status |
|---|---|---|---|---|
| **Ranger** | Wasp Thicket (east of village, half-woods, ranger station) — early exploration/woodland | T1–T2 | move_speed, light/stealth, woodland traversal | active (replaces *Forager* + *Thornweave*) |
| **Beekeeper** | the bee zones — a multi-tier line tied to the beekeeping system | T1–T3 | honey_yield_pct, sting_immunity, calm_radius, pollination | active (folds Hive-Keeper + Apiarist) |
| **Entomologist** | bug-CATCHING set (calm-spray, nets, `catch_*` boosts) | T2–T3 | catch_radius/arc/cap, calm_radius, rare_bug_luck | active (the "collector") |
| **Miner / Spelunker** | the mining line | T3–T4 | light_radius, mining_speed_pct, carry_weight, vein_sense, hazard_resist | active (folds Prospector + Spelunker + Deep-Delver) |
| **Diver / Waders** | aquatic line — **waders gate entry** to certain water/swamp areas | T2–T4 | water_walk, water_breath, hazard_resist | active (folds Marshwalker + Bog-Hunter + Cave-Diver) |
| **Chitin / Carapace** | bug-derived heavy armour (beetle/ant/spider chitin) | T3–T4 | defense, thorns, knockback | active (folds Carapace-Warden + Colonist) |
| **Silk** | light/agility spider-silk set; the **Widow** endgame variant folds in | T4–T5 | dodge_chance, move_speed_pct, crit | **pending** (late zones) |

**Cut sets:** Forager (→Ranger), Thornweave (→Ranger), **Swarm-Warden** (locust is an interesting *area*, no
set), **Fire-Warden** (no firewarden). **Swamp** has a vendor + waders; a dedicated swamp set is optional/pending
until the swamp is designed.

**Set-design rule (D10):** a new set must justify a *concept*, not just exist because a zone does. "Thorough"
= ~7 bonus-set concepts + 9 base sets — enough variety, not bloat.

---

## Reconciliation note
The 17 per-zone sheets in `../zones/` still describe their original per-zone sets; **this catalog is now the
canonical set list** (consolidated). When pruning the zone sheets, map each old set → its concept here
(e.g. `prospector`/`spelunker`/`deep_delver` → **Miner/Spelunker**; `marshwalker`/`boghunter`/`cavediver` →
**Diver/Waders**; `colonist`/`carapace_warden` → **Chitin**).

## Count
**9 base sets** (45 pieces) + **7 bonus-set concepts** (5 active + Silk pending). Down from the 28-set draft —
deliberately consolidated to "thorough, not excessive."
