# Research: how coasts, streams & surface geology deposit terrain (2026-07)

Digest of a coastal + fluvial + surface-geology sweep, translated to our 256²
strict-overhead zones (no elevation render — relief is implied by material + form).
Builds PAST shipped rules (wrack line, harbor connectivity, caves.md ore doctrine).

## 1. Coastline anatomy — points are rock, bays are sand

Coves alternate with points because resistant rock stands as headlands while weak
bands erode into bays; wave refraction CONCENTRATES energy on headlands (rocky
shores, offshore stacks) while sheltered bays collect sand — convex = attack,
concave = collection. Tile-legible depositional forms: **spit** (drift-grown sand
finger from a sharp coast turn, hooked tip, calm water behind), spit sealing a bay
= **baymouth bar** + **lagoon**, near-shore island tied by a **tombolo**.

**Rules we adopt**
- Material follows convexity: every convex point gets rock (`rock_mass` crown or
  boulders); sand bands appear ONLY inside concave cove bites.
- Alternation rhythm: a discernible rocky point between any two coves — never
  adjacent bites separated by plain grass coast.
- Islands sit off HEADLANDS on the point's axis (stack logic), never centered in
  bays; an island within ~6 cells of shore may earn a 1-2-cell sand tombolo.
- Max one spit per zone: rooted at a sharp coast turn, 2-3 cells wide, recurved
  hook; mud/reeds dress the water behind it, sand the seaward face.
- Bar-sheltered harbors keep a provable inlet gap (water.md rule) — a bar may narrow the mouth, never close it.

**Counterexample**: a sandy beach wrapped around a headland tip — sand painted on the highest-energy shore.

Sources: en.wikipedia.org Headland + Spit_(landform) · PMC10784308 (embayed-beach
wave sheltering) · PMC7663187 (Sopot tombolo).

## 2. Streams — meanders, banks, confluences, mouths

Meander wavelength ≈ 10-14 channel widths (Leopold): our width-2 streams complete
a full S every ~20-30 cells, varied in amplitude, never sinusoidal. Bends are
asymmetric — steep bare **cut bank** outside, low sand/gravel **point-bar**
crescent inside. Pools (deep) sit at outer bends, riffles (shallow coarse gravel)
at the crossings between bends, ~5-7 widths apart. Rivers only JOIN (acute
downstream Y) and only widen; the sole split is a **delta** at the mouth, where
dying current drops a bar that forks the flow. Skip braiding/levees/terraces; an
oxbow pond beside a bend is the one relic worth faking.

**Rules we adopt**
- A bend every ~20-30 cells at width 2; no natural straight run > ~15 cells.
- Bank asymmetry at every marked bend: sand/pebble crescent INSIDE, bare/rocky
  OUTSIDE — never the same treatment on both banks.
- Confluences are acute downstream Ys, downstream width ≥ each parent; no inland
  fork ever reaches the sea twice.
- Fake the riffle-pool pulse: `water_deep` at outer bends, pebble-speckled shallow
  on the straights between them, alternating down the channel.
- Mouths deposit: an estuary flare or a one-island delta fork — never a constant-width pipe butting the sea.

**Counterexample**: a river that forks mid-zone and reaches the sea twice.

Sources: en.wikipedia.org Riffle-pool_sequence + River_delta · PMC9299336 ·
PMC10374638 (riffle-pool dataset) · kmalexander.com rivers · redraggedfiend.com.

## 3. Where rock shows — cuts, points, and rises

Bedrock is exposed wherever erosion strips cover faster than soil re-forms: cut
sides of stream bends, gorge walls, headland tips, crowns of rises where resistant
rock stands proud (differential erosion) — rock marks where water actively cuts,
which is how an overhead map implies relief. Freeze-thaw sheds angular fragments
that pile below a face as a **scree apron**, densest at the foot, fining outward;
detached boulders lie near their parent mass, decaying with distance.

**Rules we adopt**
- Rock appears where something CUTS: outer stream bends, cove-flank points, gorge
  walls, or the core of a rise — never freestanding mid-meadow with no story.
- Every `rock_mass` gets a scree apron: rubble/pebbles densest within 1-2 cells of
  the foot, gone by 4 — the apron IS the implied slope.
- Stray boulders cluster within ~5 cells of a parent mass; no boulder salt-and-pepper.
- Cut banks may run 2-4 cells of exposed rock on the OUTER bend only — the cheapest "cutting" signal.
- Mineable promise honored: dirt-looking AREAS are `dirt_block` masses (shovel
  shell, stone/ore core); ore rides the vein tables, never hand lines (owner rule).

**Counterexample**: boulders confettied evenly across a meadow with no mass, cut, or rise to shed them.

Sources: en.wikipedia.org Scree · frontiersin.org 2022 talus formation · wooster.edu
weathering notes · PMC10651117 (rock strength vs river form) · caves.md (internal).

## 4. Wetlands & transitions — the water-to-land gradient

Natural shores step through an ORDERED banded sequence — deep → shallow → bare
mud/sand flat → emergent reeds → wet grass — each band a flooding tolerance. Reeds
are emergent: they stand IN water ≲10 cm deep and at the waterline; lily pads need
still sheltered shallows. Mud is a shelter signal: fines settle only where water
stops — lagoons, estuaries, the lee of spits, backwaters — never on exposed shore.

**Rules we adopt**
- Bands stay ordered (deep → shallow → mud/sand → reeds → grass), 1-3 cells each,
  parallel to the composite shoreline (adjacency-derived, as `shore_dress` does),
  broken with gaps — bands, not rings.
- Reeds streak along SHELTERED concave banks and backwaters, feet in shallow water
  or the waterline cell; never on an exposed sandy point.
- Lily pads only on still water (lake bays, lagoons) — never in a flowing channel.
- Mud flats only where the map shows shelter: behind a spit/bar, inside a lagoon,
  in an estuary funnel or confluence backwater.
- Marsh edges are ragged: broken reed belts + pockets of open shallow + mud specks, never a solid rim.

**Counterexample**: a reed ring circling 100 % of a lake at constant thickness.

Sources: en.wikipedia.org Mudflat · PMC5441591 (reed depth optimum) · PMC4838329
(flooding-gradient zonation) · madelinejameswrites.com river-and-wetlands.

## 5. Deposition grammar — energy sorts the material

The one law: moving water carries, slowing water drops coarse-first, still water
drops fines. Hence pebbles/gravel where flow is fast (riffles, bar heads, point
tips), sand where it slackens (cove bites, bar crescents, spit bodies), mud where
it stops (lagoons, backwaters). Floating debris obeys the same law: wood and wrack
strand where transport ends — the high-tide line, stream mouths (which DELIVER the
wood), and snag points such as confluences and outer-bend obstructions.

**Rules we adopt**
- Sort every scatter by local energy: pebbles on points/riffles/bar noses, sand in
  bays and bar tails, mud in still water — one material family per energy zone.
- Stream mouths are deposition fans: sand/gravel spread + a driftwood cluster —
  the second debris hotspot after the wrack line (extends the shipped rule).
- Point bars grade internally: pebbles on the upstream nose, sand on the tail.
- Wood snags in 2-4-piece clusters at obstructions — confluences, outer bends, spit roots/hooks.
- Cut faces stay clean: nothing deposits on outer-bend banks or wave-facing
  headland fronts; those cells read rock/bare only.

**Counterexample**: shells + pebbles + driftwood sprayed uniformly across a whole beach — energy-blind confetti.

Sources: en.wikipedia.org Driftwood + River_delta (mouth bars) + Riffle-pool
(gravel sorting) · PMC9302618 / arXiv 2207.11190 (meander deposition) · water.md
wrack rule (internal, built past).
