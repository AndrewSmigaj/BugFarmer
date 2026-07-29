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

**Cut:** ~~straw~~ (too hard to integrate as a *set*), ~~diamond~~ (platinum is the top — diamond armour doesn't
make sense). Existing `items.json` ids reused: the full `leather_*` and `iron_*` sets, `copper_helmet`.

> **As-built note:** `straw_hat` ✅ still exists in `items.json` as a single **T0 starter head** piece (it
> predates the "straw set cut" decision). It isn't part of the leather→platinum ladder — **your call** whether to
> keep it as a one-off starter hat or remove the item. (Surfaced, not silently changed.)
>
> **Standalone head pieces (D26):** `reed_hat` ✅ — T0 woven sun-hat (head slot), recipe @ workbench (fiber),
> bought from the Fisherman; `straw_hat` deferred to a later zone. `gardener_gloves` ✅ — a **hands**-slot
> piece (a glove, not an accessory), recipe @ loom, sold at the General Store (harvest-bonus mechanic backlogged).

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
set), **Fire-Warden** (no firewarden). ~~**Swamp** has a vendor + waders; a dedicated swamp set is
optional/pending until the swamp is designed.~~ — **superseded 2026-07-29: the swamp set was built at the
owner's direction**, ahead of the swamp being designed. Recorded so the catalog doesn't silently disagree
with what exists on disk.

> **Sprite status (2026-07-29, second pass).** Walk-cycle sprites + matching gauntlets exist for
> **22 sets** under `tools/_generated/player/outfits/`. **Art only** — no `items.json` ids, no stats,
> no recipes, nothing loaded by the game.
>
> **The base ladder (A) is now COMPLETE — all 9 rungs have sprites:**
> `leather` `padded` `copper` `bronze` `iron` `steel` `silver` `gold` `platinum`.
> The four grey rungs separate by brightness rather than by shape, measured off the worn material in
> `front_1.png` — iron 66, steel 90, silver 113, platinum 157 — so a rung is legible at sprite size.
>
> Bonus concepts (B) with sprites: `ranger` `beekeeper` `entomologist` · `ant-carapace` `beetle-shell`
> (the Chitin/Carapace family).
>
> **Not in this catalog, built anyway:** `farmer` `wood` `swamp-gear` `fisherman` `wizard-robe`
> `hornet-stinger` `moth-wool` `glowworm` — **owner's call** whether each becomes a real set, a cosmetic,
> or is dropped. `beetle-shell`, `moth-wool` and `glowworm` were the assistant's proposals to fill the
> bug-derived gap; they are not owner-chosen and carry no weight until he says so.
>
> **Still unbuilt:** `Miner / Spelunker` and `Diver / Waders` from the concepts, plus `Silk`
> (pending late zones). Diver/Waders was the one deliberately skipped of the three remaining concepts —
> `swamp-gear` and `fisherman` already cover that visual ground.
>
> *Correction to the first pass of this note: it listed the unbuilt ladder rungs as padded/copper/steel
> and **omitted `iron`**, which had no sprite either (its ✅ above is an `items.json` id, not art). All
> four are built now.*

**Set-design rule (D10):** a new set must justify a *concept*, not just exist because a zone does. "Thorough"
= ~7 bonus-set concepts + 9 base sets — enough variety, not bloat.

### Owner decisions 2026-07-29 (from the ranger design sheet)

Three designs were drawn as options for one set; the owner kept **all three** and gave each a different home.
`tools/_generated/player/explore/ranger/REVIEW.png`.

| design | becomes | owner's words |
|---|---|---|
| 1 — hooded scout, ragged cloak | the **spidersilk stealth set** (the old `ranger` slot) | *"keep the first as ranger outfit (need a better naming), made from spidersilk and some other things, makes you stealthier"* |
| 2 — brimmed hat, leather jerkin | **Entomologist** — replaces the khaki pith-helmet version | *"the second one will be the preemptive etomologist outfit"* |
| 3 — leaf plates, antlered helm | **Forest armour** — a new set | *"the third is the forest armor"* |

- **NAMED `shadowsilk`** by the owner, 2026-07-29 — *"ranger's shadowsilk armor"*. It is spider-silk and
  stealth, which makes it the **Silk** concept in section B arriving earlier than T4–T5, not a new set. The
  old `ranger` set name retires; `forest` takes the woodland slot.
- **Signature stat is STEALTH / reduced aggro**, not the `dodge_chance / move_speed / crit` this table
  currently lists for Silk — *"makes you stealthier (backlog stealth bonuses, basically reduces aggro I guess)"*.
  The mechanic is **backlogged**, so the table row is left as-is until it is built rather than being rewritten
  to describe something that does not exist.
- **Design 3 is the legibility risk.** At real game size its gold linework turns to noise while designs 1 and 2
  stay readable. Its 12-frame sheet must be regenerated with the detail cut back, not scaled down from this.

---

## Reconciliation note
The 17 per-zone sheets in `../zones/` still describe their original per-zone sets; **this catalog is now the
canonical set list** (consolidated). When pruning the zone sheets, map each old set → its concept here
(e.g. `prospector`/`spelunker`/`deep_delver` → **Miner/Spelunker**; `marshwalker`/`boghunter`/`cavediver` →
**Diver/Waders**; `colonist`/`carapace_warden` → **Chitin**).

## Count
**9 base sets** (45 pieces) + **7 bonus-set concepts** (5 active + Silk pending). Down from the 28-set draft —
deliberately consolidated to "thorough, not excessive."
