# Zone-craft corrections ledger — the owner's taste, indexed

The single place every world-building correction is FINDABLE, so a builder meets all of them —
not just the ones in guides they happened to open. **The contract:** a new correction lands
INLINE in its topical guide first (a dated owner quote, the water.md:16 / house.md:194 style),
then gets ONE line here pointing at it. Cross-cutting corrections with no topical home carry
their own two-line why here. Read this file at the START of any zone or scene work (the
zone-craft skill's Step 0), and walk it at review (Step 5): each applicable line is either
HONORED or DELIBERATELY BENT with a stated reason — never silently ignored.

Entry shape: `**C<n> — <the principle>.** (owner, date) → <guide>§<section>`

---

- **C1 — Doors face CONTEXT, not compass south.** (owner, 2026-07-05: "not all houses have to
  have doors on the bottom, it is awkward") → house.md §composer (+ the COT_N north-door plan).
- **C2 — "Dirt areas" means DIRT-BLOCK MASSES, not painted ground.** (owner, 2026-07-06)
  → caves.md §4. Diggable-looking terrain must actually be diggable.
- **C3 — Ore is ONLY veins per the doctrine — never hand-set, even rares.** (owner, 2026-07-06:
  "you don't need to spread them out in such a linear fashion") → caves.md §4 (veins 3-6,
  jittered seeding, commons shallow / rares few+deep, MEASURE with the density probe).
- **C4 — A harbor CONNECTS to the sea.** (owner, 2026-07-05: "the little lake with the fishing
  buildings does not connect to the ocean") → water.md §coasts. Verify water continuity IN TEXT.
- **C5 — Beach debris follows the WRACK LINE, never even spray.** (2026-07-05, bee_meadow pass 1)
  → water.md §coasts. Structure debris the way the world deposits it.
- **C6 — ROWS for human-made things, CLUMPS for wild ones** — and the border between them is
  the story (planted beds beside the wild meadow; kept boxes vs the wild hive outside the
  fence). → vegetation.md (clumping) + authoring/README.md "THE ROWS RULE".
- **C7 — CLEARINGS, not hilltops.** (owner, 2026-07-05: "we cant really show a hilltop with
  overhead but we can make clearings") → forest.md §rules #6. Absence-in-density is the
  overhead focal-point tool; keep traveller corridors open through forest bands.
- **C8 — Docks boardwalk the land gap and STOP MID-WATER.** (2026-07-05: a pier decked clean
  across the inlet) → water.md §docks. A pier that reaches the far shore is a bridge.
- **C9 — Blandness = GROUND VARIETY first.** (owner, 2026-07-05: "the area is rather bland" →
  fixed with terrain, not props). Cross-cutting: before adding objects to a dead region, vary
  what it's MADE of — ground materials, block masses, transitions. Object scatter only fixes
  close-ups; ground reads at every zoom.
- **C10 — Regeneration tools CLOBBER newer committed art.** (2026-07-05: three incidents in one
  session — player sprites, a bare pixelclean pass, stale plot paths). Cross-cutting: after any
  bulk regen, diff MODIFIED (not new) files against HEAD before committing; run cleaners
  targeted; exit 0 is not success. (Also in the add-object skill + agent memory.)
- **C11 — Guides are GUIDELINES; sameness reads worse than any rule-break.** (owner, 2026-07-06:
  "these guides should be guidelines I want to see you have some creativity here and make
  things appropriate") → house.md §composer. Every zone names ONE deliberate rule-bend and why
  (the zone-craft brief makes this structural).
- **C12 — A neighbor-zone transition is a terrain GRADIENT, not the neighbor's content.**
  (owner, 2026-07-06: "the ant colony is in the zone to the south, there is no ant colony in
  the zone... I just didn't want immediate boundaries so wanted it to start getting dirty and
  rocky on a gradient not suddenly having the dirt wall.") Cross-cutting: foreshadow a
  neighbor by bleeding its MATERIALS toward the shared edge on a density gradient (clean →
  speckled → dirty → rocky), so crossing the zone line lands mid-gradient — never a hard
  material wall at the boundary, and never the neighbor's inhabitants/set-pieces built early
  in this zone. (The in-zone "ANT COUNTRY / OLD DIG" narrative was the builder's invention
  from one owner sentence — the owner's design had NO ants here at all.)
- **C13 — Feature blobs stamped N times read as polka dots; transitions are knife edges
  without falloff.** (owner, 2026-07-06: "everything looks aweful, just sudden changes no
  gradients, unatural geometry (lines, etc)"). Cross-cutting, pairs with C9/C12: same-size
  round masses at even spacing, row-banded block fills, and dead flat ground between features
  are the stamp tells. Vary size ~5:1, cluster and overlap masses, jitter fills, and give
  every feature a falloff ring — the village_21_B renders are the in-repo quality bar to
  compare crops against.
