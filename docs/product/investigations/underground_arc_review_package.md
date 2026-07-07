# Underground Arc — Owner Review Package (P4, 2026-07-07)

Everything the plan promised for review, in one place. Decisions needed are marked ►.

## 1. The three zone designs (READY for your read)
- **[ant_tunnels_30.md](../zones/ant_tunnels_30.md)** — (3,0) EASY: lit surface strip
  continuing Bee Meadow's gradient, block-built tunnel mouths, scout territory, fungus
  terraces, the mining-camp burrow-seam contract, "files of ants hauling fruit down a
  sunlit shaft."
- **[ant_colony_40.md](../zones/ant_colony_40.md)** — (4,0) MEDIUM: the colony city —
  Great Trunk Tunnel, fungus-garden terraces (one blighted + quarantined), brood
  nurseries, granaries, the scripted Queen in a fungus-cathedral dome, the Royal Vault,
  the (4,1) raid seam.
- **[centipede_cavern_41.md](../zones/centipede_cavern_41.md)** — (4,1) MEDIUM: the
  beautiful dark — Dripstone Hall, Glowworm Grotto, the Matron den, the rail stub they
  ran from, spiders' webbed caverns, row-4 ore.
Each doc carries craft-brief + interest quotas (≥3 secrets, hooks on all 10 landmarks,
a surprise inversion) and authority labels (owner rulings/D-entries vs candidates).

► **Per-doc "Owner decisions needed" lists** (NPCs: Myrmecologist / Hermit; aphid
livestock; Matron mini-boss; glowworm as a real species; the two authored rule-bends;
difficulty label for (4,1); D18 vs the old formic/chitin drop ladders).

## 2. Ants — what is BUILT and PROVEN
- Two sim species (ant_worker, ant_scout) on the bee's verbatim forager loop; ant_brood
  nest anchor (structures are BLOCKS per your ruling — ant_mound deprecated); fungus
  pools on existing mushrooms (bounded, depleting); rotten-fruit wildcard for windfalls;
  attraction-scoped nest gates (a flower field can't feed an ant colony).
- Colony memory + scout breadcrumbs + march commitment + recruitment + traffic
  reinforcement + site coalescence — all server-only soft state (never hashed/saved/
  snapshotted; the persistence tripwire enforces it), zero new ledger events.
- **Gates green:** full docker go suite (14 ant/colony tests), sim-determinism, FRESH
  latejoin co-located AND spawn-apart both SYNC IDENTICAL.
- **The trail feel-bar is OPEN (not met, not relaxed):** 11 lab runs, each fixing a real
  mechanism bug (the full chain is in ecology_tuning_log.md). The loop fires end-to-end
  with log evidence; what's missing is RATE — two named bottlenecks (recruit-eligibility
  filter needs one instrumented run; scout coverage needs patrol bias). Recommendation:
  close them either (a) now with ~2 more instrumented runs, or (b) on ant_tunnels_30's
  REAL tunnel geometry, which changes the calculus in the trail's favor anyway.
► **Choose (a) finish the bar in the lab now, or (b) build (3,0) first and bar it there.**

## 3. Furniture sets (BUILT as data; sprites queued)
Floral (8 pieces) · Stone (5 + the existing trio) · Marble accents (3) — collections
registered, recipes tagged (floral_furniture / stone_works), placeholders render, all
verified. Sprite batch = reference-generation per set (art_needed.md).
► Set membership tweaks? (You said you'd check later.)

## 4. Reconciliation shipped with this arc
Stale underground docs fixed/superseded; lighting FULLY SPECCED + backlogged (your
Terraria rule captured verbatim); REAL cross-zone bug transfer backlogged (your ruling);
marble backlogged; 3 new interest lenses (Secret-Keeper / Surprise / Curiosity-Hook).

## 5. What starts after your review
The zone-BUILD plan: (3,0) → (4,0) → (4,1) through zone-craft (options-first, rendered
choices), with the ant system landing in (3,0) as its first production zone.
