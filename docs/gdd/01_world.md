# §01 · World & zones
<!-- gdd: id=01 status=review updated=2026-09-26 -->

## The experience
You start in the village, on the southern edge of the surface. The world is twenty hand-made zones laid out like a
chessboard four wide and five deep: three rows of surface above and, below a long cliff wall, two rows of
underground. Going north or east on the surface, and down or east underground, the zones get more dangerous and
richer. Nothing is locked behind a door or a level — a few water areas need waders or a hook — but the next zones
will hurt you until your gear is ready for them. Far to the north-west, in the locust farmland, is a second town.
The bugs don't respect the borders — ants forage out of their tunnels into the meadow, swarms spill out of the
farmland — and a zone nobody has visited for a while has moved on when you come back.

## Decided
- **The grid** — recorded in the June review (`economy/DECISIONS.md`, 2026-06-25): the world is **rows 0–4**, four
  columns; the deepest row (row 5) is dropped *"for now"*, to be re-added later, and *"its rare ores (silver→diamond)
  compress up into row 4, gated by the harder east columns"* (D2). Underground, the **west column is the ants** —
  easy ants above, medium ants below with a **Queen** — by *"user direction"* (D3).
- **All twenty, ring by ring** — the roadmap approved on 2026-09-26 builds every zone on the map: the five around home
  first (Village, Bee Meadow, Ant Tunnels, Mining Camp, Ant Colony and its Queen), then the middle ring, then the far
  rows.
- **One village** — the June review: *"Zone 1 = `village_21_B` … NOT the plain `village_21` demo"* (D19) — the
  rebuilt village ("Village B" on the dev menu), not the old one.
- **A second town, in the locust farmland** — the far north-west zone is *"a little western-style town"*, and the
  village's windmill can't be bought or built until you reach it (2026-06-27, `BACKLOG.md`): *"I will know what it
  means when we get there."* The approved roadmap builds it with the farmland and electricity.
- **The ants' country** — *"they will have their colony in the sw ant zone"* (2026-07-06); *"make half of the easy ant
  zone outside so ants can form trails to food sources"* (2026-07-07); *"there should be a natural boundary like with
  the beginning mining zone all along the ant area and the rocky area"* (2026-07-07 — the rock between the Ant Tunnels
  and the Mining Camp).
- **The Bee Meadow's borders** — *"there is no ant colony in the zone"* and *"the ants will be coming from the south,
  they mostly collect dead bugs and food"* (2026-07-06); *"the river should flow to the sea not a little pond next to
  the sea"* (2026-07-06); *"removing the strip at the bottom of the bee zone… more spread out forest"* (2026-07-07).
- **Where bugs cross borders, already settled:** ants into the Bee Meadow (above); ants *"CROSS OVER"* into the Mining
  Camp through the dirt tunnels (D21); the Deadly Ants forage up into the Shallow Swamp above them (D3, D9).
- **Bugs really cross zone borders** — *"it will be real bug transfer"* (2026-07-06); and on 2026-09-26: *"finish the
  mechanics and zones (including cross zone bug transfer when they get to an edge which will need care with our
  deterministic lockstep system)"*. How they cross was left to me: *"you decide based on what will be better design
  and more efficient"* (2026-09-26) — the design is under "How it will work".
- **Zones nobody is in** — *"as already designed frozen with aggregation upon first access with random border
  crossing events"* (2026-09-26).
- **Progress is gated by cost, not locks** — *"things are gated by costs and such so you have to work on your char
  before going to certain zones"* (2026-09-26).
- **No rule forced on every zone** — *"we dont want mechanics forcing rules on zones"* (2026-09-26).
- **New bugs, not new zones** — on adding bugs: *"as long as it doesnt mess up the balance and require completely new
  zones"* (2026-09-26).
- **A secret place** — the Queens' set is *"locked in a chest in a little underground fortress"* (2026-08-06,
  `brainstorm_armor.md`); it isn't on the map yet (where secrets go is §17).
- **The village's to-do list** — *"NPCs and NPC behavior, Building and zone overhauls to make it look better and more
  coherent, just general improvement and polish passes, village secrets"* (2026-09-26).
- **The zones' contents are still open** — *"We haven't fully fleshed out what is in the zones, all the interesting
  items and weapons/clothes in various zones"* (2026-09-26). They get one design document per zone after this
  document is signed off.

## Current design
**The map** (`architecture_world.md`), north at the top, west on the left. Danger in brackets.

| | west | | | east |
|---|---|---|---|---|
| **surface, far north** | Locust Farmland + the western town (hard) | Millipede Forest (hard) | Spider Vale West (extra hard) | Spider Vale East (the hardest surface zone) |
| **surface** | Hilltop Meadow (medium) | Butterfly Fields (medium) | Scorpion Rocks (hard) | Deep Swamp (extra hard) |
| **surface, south** | Bee Meadow (easy) | **Village** (easy — start) | Wasp Thicket (medium) | Shallow Swamp (hard) |
| **underground** | Ant Tunnels (easy) | Mining Camp (easy) | Underground River (medium) | Deadly Ants outpost (hard) |
| **deep underground** | Ant Colony + Queen (medium) | Centipede Cavern (medium) | Underground River, deep (hard) | Deadly Ants core (extra hard) |

The armour notes record your view of the hardest places: the upper surface and the lower underground are roughly
even; the swamp, the underground river and the lake are about equal; Spider Vale is the hardest surface zone and the
fire-ant domain the hardest underground one.

**What each zone is for** (from its design sheet in `economy/zones/`):
- **Village** — home: shops, the Ecologist, your farm.
- **Bee Meadow** — beekeeping; the fishing hamlet of Gullwash Landing is on its coast. **Hilltop Meadow** — advanced
  beekeeping, and wasps kept as pest control.
- **Butterfly Fields** — rare catches, night and glowing bugs, silk. **Wasp Thicket** — the first real fights:
  venom and swarms.
- **Scorpion Rocks** — mining in daylight, deadly venom, heat. **Millipede Forest** — logging and chitin armour.
- **Locust Farmland** — ruined farmland where you hold a line against locust swarms, around the western town.
  **Spider Vales** — silk, agility, rare metals; the east vale finishes the surface.
- **Shallow Swamp** — the water gear. **Deep Swamp** — diving, disease and poison, an apex predator.
- **Ant Tunnels** — half outdoors: ant trails, the first tunnels. **Ant Colony** — the Colony Queen.
- **Mining Camp** (Underground Passages) — mining with light, tools and ore. **Centipede Cavern** — glowworm light,
  fast venom, crystals. **Underground River** — cave fishing, pearls, a sunken ruin.
- **Deadly Ants** — endgame ant warfare; fire resistance is the key; the War Queen in the core.

**How danger rises:** on the surface, north and east; underground, down and east, with the rare ores in the deepest
row and the hardest of it in the east (D2). Which metal belongs to which ring beyond that is §02 (the gear ladder)
and §14 (mining).

**How zones connect:** roads branch out from the village to each surface zone; underground zones are entered
through openings in the cliff wall (`architecture_world.md`). The map draws a river down the middle between the
medium zones and the hard ones, with shallow crossings. Waders open certain water and swamp areas, and a grappling
hook crosses deep-water gaps later. Most zone designs put a camp with a trader near the way in; the Ant Colony and the
Deadly Ants core have none.

**Where the documents disagree** (settled when each zone gets its design document; the map above wins, except where a
later ruling changed things — water is Q1):
- The January GDD's world *"expands radially from a starting village"*; the map puts the village on the southern edge
  of the surface, west of centre. The December requirements describe the regions as one continuous world that
  players and bugs cross freely.
- The Mining Camp is *easy* on the map, *medium to hard* on its sheet; the Centipede Cavern is *medium* on the map,
  *hard* on its sheet. The Mining Camp's bugs also differ between its sheet and the June review (D21), and one sheet
  still puts the Deadly Ants in the west column.
- The Wasp Thicket's camp is an abandoned shack on the map, a trapper on its sheet, and a ranger station in the June
  review (D10) — while the map puts the ranger station in the Millipede Forest. The armour notes (2026-08-06) want the
  ranger armour found in a zone with a small outpost full of wasps and hornets, not designed yet.
- Three sheets swap directions (for example Spider Vale East, top right of the map, is called "the western edge").
- Some sheets still have frogs (rejected, D31), and bugs dropping parts of themselves — since D18 a bug drops only its
  body, and the Bug Extractor turns bodies into materials (formic acid comes from dead ants that way).

## As built
- **Four zones are built and linked in a loop:** Village ↔ Bee Meadow ↔ Ant Tunnels ↔ Mining Camp ↔ Village. Each
  zone is 256 × 256 squares. The Bee Meadow's west edge is the sea; the Ant Tunnels' west edge is the edge of the world.
- **The one built river** runs from the sea through the Bee Meadow's gorge toward the village; in the saved zones it
  stops just short of the border. The map's big river down the middle isn't built.
- **Started, not finished:** the Ant Colony (a half-built layout, never saved), the Butterfly Fields (two preview
  scenes), the Centipede Cavern (a design document only).
- **Two villages exist.** The dev menu's default ("Normal") is still the old village, which has no shops; walk south
  from it and back north and you arrive in the rebuilt village ("Village B"), the real one (`WorldMenu.cs`,
  `zone_links_test.go`).
- **The rebuilt village** has the windmill you asked for and the Weaver's clothing racks (display pieces, D27) — and
  231 wheat plants, although the June review moved wheat out of the village (D19).
- **Rare ore sits outside the deep row:** silver and gold in the Bee Meadow and the Ant Tunnels; silver, gold,
  platinum and diamond in the Mining Camp — against the June rule (D2).
- **Crossing a border:** walk to any point on an edge that has a neighbour; the screen fades and you appear four
  squares inside the next zone, at the same point along the edge (`CrossZoneController.cs`). Only the player crosses.
  The server keeps each swarm inside its zone; single bugs on screen can drift past the line.
- **88 crossing points land on a solid square**, and 35 of those are boxed in on all four sides — worst between the
  Ant Tunnels and the Mining Camp, where the openings on the two sides of the rock don't line up. The game doesn't
  check where you land (`match.go`).
- **Water today:** it stops people, and no bug — every bug crosses it (your playtest rule of 2026-06-11).
- **Zones nobody is in:** a zone saves when its last player leaves and then stops completely — bugs, fruit trees,
  machines, and the weather: no rain falls there, so no crops get watered. Nothing catches up when you return, and each
  zone keeps its own clock, so two neighbouring zones can show different times of day.
- **If you faint,** you wake at the zone's starting point, or in your bed if you've slept in one there.
- **Found while writing this** (by reading the code; not yet reproduced): crossing into a zone that fails to start
  leaves the player in no zone at all — the game leaves the old zone before it has joined the new one (roadmap,
  known bug 6).

## How it will work
- **One village.** New games start in the rebuilt village; the old one becomes a test zone.
- **Bugs crossing borders.** A swarm stays inside its zone unless it is *migrating*: overcrowded, hungry, fleeing, or
  on one of the random crossing events. A migrating swarm — or a small group split off from one, even a single bug —
  walks out, and once it is past the line it is handed to the next zone whole, exactly once. Nothing vanishes in front
  of you, and nothing is left half on each side.
- **Zones nobody is in** stay frozen. When someone arrives, the bugs first catch up on the time they missed — they
  eat, breed and die over it, worked out on the server — and only then does the zone show itself. The weather, the
  fruit and the machines are P6 below.
- **One world clock**, so every zone shows the same time of day.
- **Crossing never strands you:** if you would land on a solid square, you land on the nearest open square you can
  reach from that edge; if the next zone can't start, you stay where you were. The real fix is a check that each
  zone's openings line up on both sides of every shared border.

## Proposals
### P1. The dropped deepest row stays out of 1.0
Row 5 stays out of 1.0 and can come back in an update. Nothing waits on it: the Queen already moved up to the Ant
Colony (D3) and the rare ores up into row 4 (D2).

**Lenses:** Scope — twenty zones is already the biggest job in the plan. Built on what's decided — D2 said *"for
now"*; this says *"for 1.0"*.

### P2. Gated by cost and danger — never by locked doors
Any zone can be walked into at any time; a few water areas need waders or a grappling hook (June review). What stops
you is what lives there, and each danger has an answer you can make or buy:

| ring | zones | what stops you |
|---|---|---|
| home | Village, Bee Meadow, Ant Tunnels, Mining Camp, Ant Colony | the dark underground; the Colony Queen |
| middle | Wasp Thicket, Butterfly Fields, Hilltop Meadow, Centipede Cavern, Underground River | stings and swarms; venom; dark water |
| far | Scorpion Rocks, Shallow Swamp, Millipede Forest, Locust Farmland, Deadly Ants outpost, the deep river | deadly venom and heat; deep water; locust swarms; fire |
| edge | Deep Swamp, Spider Vale West, Spider Vale East, Deadly Ants core | disease and poison; webs; the War Queen |

**Lenses:** Your *"gated by costs … work on your char before going to certain zones"*. Curiosity — nothing is
walled off, so you can always look ahead. Meaningful choices — several zones open at once in each ring. Picture the
moment — you walk into the Wasp Thicket with copper tools, get stung twice, and go home to make an antidote.

### P3. Where danger changes, the land changes
Every border between two danger levels shows it on the ground: a river with bridges and shallow crossings you can
walk, the cliff wall, a forest edge, the swamp's open water. Borders between zones of the same danger are drawn for
their own two zones — open meadow, or the rock you asked for between the Ant Tunnels and the Mining Camp. Each zone's
design document shows its borders, and a check keeps both sides of a shared border matching.

**Lenses:** Readable state — the land tells you, not a warning sign. Built on what's designed — the river and the
cliff wall are on the map. Zone freedom — each border is drawn for its own two zones.

### P4. The edge of the world is land, not an invisible wall
The outer rim is natural and can't be crossed: the sea to the west (built — the Bee Meadow's coast), mountains to the
north, open water beyond the swamps to the east, and bedrock beneath the deepest zones. Walking up to it shows why you
can't go on.

**Lenses:** Picture the moment — the Bee Meadow's beach already does this. Premise — a frontier has an edge you can
see. Cost — border art in the outer zones, not a new system.

### P5. More places where bugs cross — written into the zones they touch
Beyond the crossings already settled (the ants, the Deadly Ants), three more from the designs:
- **giant centipedes** raid across from the Centipede Cavern into the Ant Colony (the Ant Colony's design);
- **locust** swarms spill out of the farmland into the zones around it (its design);
- **wasps** spread in from the zones next door (the January GDD: *"Wasps migrate from adjacent zones"*).

Crossings belong to the borders they cross, never a rule for every zone. When a frozen zone wakes, some of what
happened while it slept comes from these neighbours: a new ant trail, a swarm that arrived from next door.

**Lenses:** Your *"random border crossing events"*. Zone freedom — only these borders. Surprise — you come back and
something has moved in. Bestiary — all three are bugs already designed.

### P6. A frozen zone catches up on its weather, orchard and machines too
When a zone wakes, it catches up on everything the time would have brought, not only its bugs: the showers that would
have watered its crops (today three days in ten get one), the fruit that would have ripened, and the batches its
machines would have finished.

**Lenses:** Your *"frozen with aggregation upon first access"* — the catching up covers the whole zone. Fair to your
time (§00, proposed pillar 8). Cost — showers, fruit and machines already run on the game's clock, so catching them
up means giving them the time they missed.

## Questions
### Q1. Should water stop crawling bugs?
Your playtest rule of 2026-06-11: water stops people only, because flies were getting stuck at shorelines — and that
is how the game works now: every bug crosses every river. The June 25 review later wrote the older rule back into its
notes: shallow water *"blocks insects"* (D7). The map was drawn with the river as a barrier. Whichever rule holds
decides whether a river — or a moat around your farm — keeps any bug out.
- **A.** As now: water stops people only; every bug crosses it.
- **B.** Water stops bugs that walk, not bugs that fly. Ants, centipedes, millipedes and beetles stop at the water's
  edge; flies, bees, wasps, butterflies and locusts fly over — so no flier gets stuck at a shore. Rivers and moats
  keep crawling pests out.
- **C.** Shallow water stops every bug, as the June 25 note says — and the flies-stuck-at-the-shore problem comes back.

**Recommendation: B.** It keeps your playtest fix — nothing that flies gets stuck — and gives rivers and moats a job:
real ants can't cross a river on foot, and a moat against crawling pests is the kind of trick a bug farmer should be
able to pull. Cost: bugs already have a setting for whether they fly over fences, so a water setting is the same kind
of change, made carefully because every player's game must move the bugs identically.

## Sources
- `docs/product/architecture/architecture_world.md` — the map (§1), connections, roads and hubs (§2)
- `docs/product/zones/*.md` — the built zones and their rulings (`ant_tunnels_30.md`, `ant_colony_40.md`,
  `bee_meadow_20.md`, `village_21_B.md`, `underground_passages_31.md`, `centipede_cavern_41.md`)
- `docs/product/economy/zones/*.md` — one design sheet per zone
- `docs/product/economy/DECISIONS.md` — D2, D3, D7, D9, D10, D18, D19, D21, D27, D31
- `docs/product/BACKLOG.md` — the western town and the windmill (2026-06-27); real bug transfer (2026-07-06)
- `docs/product/design/brainstorm_armor.md` — the difficulty view, the ranger outpost, the underground fortress
- `docs/product/design/game_design.md` §3, §9.3 (January 2026) · `docs/product/design/requirements.md` §4 (December 2025)
- `docs/product/ROADMAP.md` — the rings, and the designs for migration, frozen zones, the world clock and blocked entry
- The water rule: commit `d99ddbaf` (2026-06-11), `CHANGELOG.md`, `architecture/architecture_swarm_sync.md`
- As built: `nakama/data/zones/*/zone.json` and chunks, `nakama/modules/world/zone_links_test.go`, `match.go`,
  `handlers_player.go`, `handlers_env.go`, `BugFarmerClient/…/CrossZoneController.cs`, `WorldMenu.cs`
