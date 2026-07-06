# Feature guide: lakes, shores & water (surface)

How to author WATER that reads natural — lakes, shorelines, docks. Supersedes the
lake half of the old `trees-and-ponds.md` (its checklists live on here, now backed by
real primitives; its forest half merged into the forest guidance). Module:
`tools/zonegen/features/terrain.py`. Test card: `scene_shore_arcs`.

## `lake()` — the shape rule (multi-blob, NEVER the star)
```python
from features.terrain import lake, shore_dress
info = lake(b, cx, cy, radius, seed=3, shore="sand", reeds=12)
```
- A real lake is a UNION of 2-4 elongated, offset blobs strung along a random long
  axis — a long body with bays and a bowed shoreline. The first version used radius
  harmonics from one center and produced symmetric 5-7-point STARS (2026-06
  correction: "I really don't like the shapes of all the lakes"). High-frequency
  radial bumps always read as geometry; offset-blob unions read as water.
- Structure: deep core → shallow rim → a `shore` ring (sand/mud) with gaps → reeds
  clumped on the banks. Water is reserved; lakes FLOW INTO existing water (skip
  reserved), so overlapping calls merge into one body.
- Returns `{"center", "radius", "reeds"}` — feed it to `shore_dress`.

## `shore_dress()` — no two banks alike
```python
shore_dress(b, info, [(225, 315, "sand"),     # S beach
                      (315, 30, "reeds"),     # E reed bank
                      (135, 225, "forest")],  # W forested bank
            seed=1)
```
- Arc treatments: `sand | mud | reeds | forest | rocks`. **Angles are math-convention
  with +y NORTH: 0°=E shore, 90°=N, 180°=W, 270°=S** (read that twice). Arcs may wrap.
- The shoreline is RE-DERIVED by adjacency scan, so it follows the COMPOSITE bank
  after merges — never dressed from one call's cells.
- Leave one arc plain where a built feature (dock, boat store) owns the bank.

## Docks (the walkable-water trick)
Player walkability comes from the GROUND TILE (a hardcoded id switch both sides), so
a dock is simply **`bridge_wood` tiles replacing water cells** — walkable everywhere
with zero engine work. `scene_lakeside.place_boat_store` is the worked example: the
building sits ON the shore (hug it — a dock that stops at the waterline was a real
defect), the 2-wide deck runs out over the water, mooring posts/lantern/boat are
deliberately water-anchored occupants (their `validate()` notes are expected).
- **Docks BOARDWALK-ramp the land gap and STOP MID-WATER** (2026-07-05, bee_meadow_20:
  a max_len-12 pier decked clean across the whole inlet — a pier that reaches the far
  shore is a bridge, not a dock; and a deck starting at the waterline floats detached
  when the shoreline wanders). `scene_fishing_docks._dock` is the hardened version:
  pre-scans for water (refuses to build into grass), decks the land cells as the ramp,
  ends mid-channel.

## Coasts, harbors & tidelines (learned building bee_meadow_20)
- **A harbor CONNECTS to the sea** (owner correction 2026-07-05: "the little lake with
  the fishing buildings does not connect to the ocean"). Water that boats and fishing
  imply must be PROVABLY continuous open water to the sea — verify IN TEXT (walk a
  water-only line across the map), never by eyeball. A landlocked "bay" is a bug.
- **Beach debris follows the WRACK LINE, never even spray**: flotsam (shells, driftwood,
  starfish, the odd bottle) concentrates in the 2-3 sand cells nearest the water — the
  way tides deposit — with only stray pieces above, and dune grass breaking the
  sand→grass seam. `scene_beach_cove.dress_beach` is the primitive; even scatter reads
  as confetti.

## Placement & the "used lake" rule (kept from trees-and-ponds)
- 2-5 lakes/ponds per zone; vary radius, seed, shore material, AND treatment arcs.
- At least half the lakes get one "used" feature: an approach lane, a clearing, a
  fishing spot, a beached rowboat — water nobody visits reads as paint.
- Bridges + rivers: deferred to the river-zone slice (a stream is a hard player
  barrier — plan crossings deliberately; see BACKLOG).

## Checklist
- [ ] No lake reads as a star/circle; long axis visible, bays present.
- [ ] Deep + shallow + broken shore ring, reeds in streaks not singles.
- [ ] Each bank arc differs from its neighbors; one arc owned by a built feature
      where the design wants one.
- [ ] Docks actually cross onto water; `validate()` water-anchored notes are only
      the deliberate dock furniture.
