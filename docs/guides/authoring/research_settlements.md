# Research: how settlements read as real in 2D overhead games (2026-07)

Digest of a web-research sweep on vernacular settlement morphology (why real hamlets
have the shapes they have) and how cozy 2D games (Stardew, Animal Crossing) turn that
logic into readable tile maps. Every rule below is checkable on a rendered zone preview.

## 1. Settlement shape follows its reason

Geography's canonical forms are each CAUSED by something visible on the map:
**nucleated** — houses cluster around one focal asset (church/green/square), fields
OUTSIDE the cluster; **linear** — "a single street with houses on either side," ONE
PLOT DEEP along a road/river/shore, with "no obvious centre"; **crossroads** — trade
at the junction; **dispersed** — lone farmsteads. A fishing village is nucleation
around "a small natural harbour which provides a safe haven for a village fleet."
The design translation (2minutetabletop): pick the reason FIRST — "how a town might
have grown from" what the location gives (Gullwash Landing: the inlet is the reason).

**Rules we adopt**
- Every settlement names its REASON (cove, ford, spring, crossroads, field edge) in
  the zone intent doc, and that reason is a visible feature ON the map, not lore.
- Form matches reason: harbor/green → nucleated cluster; road → linear one-plot-deep
  row; junction → shops AT the crossing; farmland → dispersed farmsteads.
- Buildings orient to the reason (doors face the water/green/lane — the existing
  CONTEXT rule), so the layout still reads with the paths hidden.
- Work land sits OUTSIDE the cluster (crop beds/orchards ring a hamlet, never fill its
  middle); a linear hamlet stays one building deep per side.

**Counterexample**: a "fishing village" ringing an inland plaza, shore empty — a stage set.

Sources: en.wikipedia.org Nucleated_village · Linear_settlement · Fishing_village ·
2minutetabletop.com/how-to-design-a-town.

## 2. The commons: one shared space carries the community read

The village green was "a common open area... placed in the centre of a settlement" —
cattle pond, meeting place, market, festivals: a WORKING reason to gather, with houses
fronting onto it. Cozy games rediscover this: ACNH guides converge on "a centralized
gathering spot for villagers" plus shops near homes ("random encounters that make the
island feel truly alive"); Pelican Town's square is the hub its river and shops hang
off. The commons scales down — a hamlet's is a well, fire, or quay (Gullwash's docks).

**Rules we adopt**
- ONE primary commons per settlement, scaled to it: hamlet = well / fire ring / quay
  with 2-3 seats; village = green or fountain plaza. Two rivals split the read.
- The commons contains water, fire, or trade (well, pond, campfire, market board,
  dock) — never bare paving; something must justify standing there.
- Doors and shop frontages within a screen of the commons FACE it.
- Main paths pass THROUGH the commons, not beside it; from the zone entry, the commons
  or its landmark appears within about one screen of walking the main path.

**Counterexample**: a fountain plaza on a four-house hamlet — commons scale must match settlement.

Sources: en.wikipedia.org Village_green · gamesradar.com + screenrant.com ACNH guides ·
stardewvalleywiki.com Pelican_Town · mygamerank.com SDV map guide.

## 3. Work visible: the livelihood grammar

Real villages are legible economies. Fishing villages need "a safe way of landing fish
and securing boats," plus processing and repair — quays, net sheds, drying racks,
smokehouses (Walraversijde, c. 1465); a farmstead is a house PLUS working buildings.
Trades self-sort: "fishing docks away from housing due to smell, mills outside town
centers, farms on borders." The Level Design Book's check — "Who made this place? Who
lives here now?" — is answered with props: "tools, signage, wear-and-tear... make the
world feel lived-in and purposeful." Our working props are exactly this vocabulary.

**Rules we adopt**
- Every home answers "how does this household eat?" with ≥2 yard props of ONE trade
  (nets + drying rack; hives + honey crates; anvil + ore sacks; coop + feed bin).
- Work props sit BETWEEN the door and the work source — nets on the water side,
  woodpile on the forest side. The chore has a geography.
- Smelly/noisy trades sit at the cluster's edge, never inside a cottage row; every
  production prop has its evidence nearby (hives → flowers in reach).
- One in-progress vignette per settlement (laundry mid-line, half-loaded wagon, fish
  on half the rack) — frozen mid-task, not museum-arranged.

**Counterexample**: five cottages with identical crate+barrel yards — decoration, not livelihood.

Sources: en.wikipedia.org Fishing_village · 2minutetabletop.com · book.leveldesignbook.com
worldbuilding · gamedeveloper.com + toxigon.com environmental storytelling.

## 4. Density, variety and the poor→nice range

History licenses ROWS — planned medieval villages used burgage plots, "equal-sized
house plots arranged in regular rows" — but within the row no two households are
equal. The storytelling literature is blunt: "a pristine environment feels artificial;
grime, scuff marks and peeling paint make the world feel lived-in," and wear
concentrates where use does (GT4's guardrail scuffs "where everyone kept hitting the
same spot"). ACNH's lived-in trick is spill-over: "items at the exterior of houses or
on street corners." Variety needs a budget, not dice (research_procgen §3's landmark
rule): mostly simple rects, 1-2 showpieces.

**Rules we adopt**
- No two homes in one settlement share all three of footprint, yard style, and
  interior collection — vary at least two; check side-by-side in the region crops.
- A readable wealth gradient: ≥1 visibly poorer home (weathered fence, patchy yard)
  and ≥1 nicer one (flower beds, lamp, porch) per settlement.
- Wear tracks use: dirt scuffs and path-widening at doors, gates, the well, the dock
  steps — never sprinkled at random.
- Spill-over at the seams: a prop or two OUTSIDE the fence line (bucket by the gate);
  density thins from commons to field edge — the gradient IS the boundary.

**Counterexample**: Sułoszowa's 9 km of identical roadside farms is REAL yet reads procedural on tiles.

Sources: en.wikipedia.org Nucleated_village (burgage plots) · Linear_settlement
(Sułoszowa) · toxigon.com + brushsauceacademy.com (wear) · research_procgen.md §3.

## 5. Wayfinding and names: the approach is part of the settlement

The navigation literature's core finding: distinctive landmarks AT DECISION POINTS
make spaces learnable — reference points that "indicate when and where actions should
be taken." Pelican Town applies it: compact but maze-like, yet the river + bridges
give structure and every public building has a unique silhouette and a name; theme
parks add the "weenie," one tall magnet pulling you down the approach. Our approach is
authorable — zone edge → work land → first yard → commons — with per-placement sign
text naming lanes and shops Stardew-style.

**Rules we adopt**
- One landmark per approach axis: the tallest/widest distinct silhouette (hall,
  lighthouse, great tree) visible on the main path in, before the houses.
- Signs at decisions, not decoration: signposts at junctions, one named sign per
  PUBLIC building; homes named only where a lane branches.
- Public buildings never reuse a cottage shell unchanged — distinct footprint, sign
  width, or frontage per function (shop_building's wide sign is the pattern).
- Every lane ends at something (door, dock, shrine, field gate); the first screen
  entering the zone shows the settlement's identity (its §1 reason or its landmark).

**Counterexample**: a sign on every fencepost reads as UI, not place — wayfinding is scarcity.

Sources: arxiv.org/pdf/cs/0304001 (landmark guidelines) · mygamerank.com SDV map guide ·
stardewvalleywiki.com · 2minutetabletop.com (districts & naming).
