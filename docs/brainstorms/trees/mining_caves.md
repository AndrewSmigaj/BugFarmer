# Brainstorm — Mining Caves "trees"

The honest answer: **there are no trees underground.** No light, no canopy. So this is the shortest of the
zone docs. But "tree-scale vertical features" still matter for composition — the cave needs a few **big,
trunk-like landmarks** to break up flat floors and ceilings, the way trees punctuate a surface scene. These
are tree-*adjacent*: giant roots from the world above, fossilized/petrified wood, and one rare living
giant fungus that *acts* like a tree.

(Where these are stone/mineral they'd use the **mineral** art family per `caves.md`; the living
fungus-tree and roots are organic.)

---

## 1. Roots from above (the "tree" is overhead — we see only its reach)
- `giant_root_column` — a massive woody root descending floor-to-ceiling like a trunk; the surface tree it
  belongs to is unseen above. The closest thing to an underground "tree." Landmark-scale. uncommon.
- `root_arch` — two great roots that have fused/crossed into a natural archway you can walk under. rare.
- `hanging_root_chandelier` — a knot of thick roots dangling from a high ceiling crack, dripping. uncommon.
- `buttress_root_wall` — a fan of flattened buttress roots splaying against one cavern wall. uncommon.

## 2. Petrified & fossil wood (trees turned to stone — long dead, mineralized)
- `petrified_log` — a fallen log fully turned to banded agate/stone; minable for **petrified wood** material. mineral family. uncommon.
- `petrified_stump` — a stone stump rooted in the floor, growth rings now quartz veins. uncommon.
- `fossil_log_embedded` — a fossil tree-trunk half-buried in a wall, ferns/bark texture preserved. rare; flavor/collectible.
- `coal_seam_trunk` — a recognizable tree shape inside a coal seam (coal = ancient forest). Mining lore beat. rare.
- `petrified_forest_cluster` — a small grove of several petrified stumps in one chamber — a landmark room. rare. (overlaps landmarks doc)

## 3. The living giant cave-fungus (rare "tree" of the deep — a real biome anchor)
A single, mythic, **tree-sized fungus** — the underground answer to the great oak. Worth one showpiece.
- `great_fungus_tree` — towering mushroom with a thick fibrous "trunk" and a broad glowing cap-canopy that
  lights a whole chamber. Glow, landmark. very rare (one per deep zone, signposts a special grotto).
- `fungus_tree_sapling` — a knee-high young version; hints the big one can grow/be cultivated. rare.
- `shelf_fungus_tower` — a stack of giant brackets climbing a wall into a stepped "tree" of shelves; harvestable. uncommon.
- `mycelium_pillar` — a dense vertical column of fused mycelium and small fruiting bodies, faintly glowing. uncommon.

---

## Notes
- **Purpose is vertical composition + landmarks**, not a tree-farming loop. Treat `great_fungus_tree` and
  `petrified_forest_cluster` as *destination features* (see landmarks doc), not common scatter.
- **Material payoff:** petrified wood (decor/craft material), the coal_seam_trunk as a lore-rich coal find,
  giant fungus caps as glow-decor / large food harvest.
- **No** surface `tree_oak`/`tree_pine`/`tree_apple` underground — if one appears it's a dead, fallen, or
  petrified intrusion via a sinkhole, never a living canopy.
