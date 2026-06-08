# Demo Slice — the vertical N–S corridor

The first playable demo is a **vertical slice** through the map, centered on the starting village. Four
zones, descending in difficulty/depth, each with real **landmarks and little features** (not flat maps).
The rest of the 24-zone world (`architecture_world.md`) stays world-doc-only until after the demo.

```
        ┌───────────────────────┐
        │   BUTTERFLY MEADOW     │  north · medium
        │   milkweed · flutter   │  pollinators + first wasps, edge millipedes/centipedes
        └───────────┬───────────┘
                    │ road north
        ┌───────────┴───────────┐
        │      VILLAGE (2,1)     │  START · easy — the TOWN
        │  shops · docks · farms │  town hall, market, store, carpenter, smith, boat/fishing (SW lake)
        └───────────┬───────────┘
                    │ descend (cave mouth, south)
        ┌───────────┴───────────┐
        │     MINING CAVES       │  underground · ores & stone
        │  veins · pools · camp  │  copper→iron→silver…, the existing cave/mining-camp scenes
        └───────────┬───────────┘
                    │ deeper
        ┌───────────┴───────────┐
        │      ANT COLONY        │  deep underground · HARDER
        │  tunnels · chambers    │  branching nest, egg chambers, queen, soldier ants
        └───────────────────────┘
```

| Zone | `zone_id` | Role / difficulty | Key species | Landmark hooks | Status |
|------|-----------|-------------------|-------------|----------------|--------|
| Butterfly Meadow | `butterfly_meadow_11` | North · Medium | milkweed; 2–3 butterflies; 2 wasps (easy + harder); edge millipede/centipede | a giant milkweed stand, a flower-clock glade, a broken fence line | **new** (doc + scenes) |
| Village | `village_21` | Start · Easy | flies/fruit ecology; villagers | civic square + well, the SW lake & docks, the orchard | **expand** to a town |
| Mining Caves | `underground_passages_31` | Underground · Med→Hard | cave bugs; ore veins | rail tunnel, glow-pool cavern, miner's camp | **extend** existing |
| Ant Colony | `ant_colony` *(grid TBD)* | Deep · Hard | worker/soldier ants, queen, aphid "livestock" | egg chamber, the queen's hall, fungus garden | **new** (doc + scenes) |

**This pass produces (DATA / placeholders only — no art generation):**
- Per-zone design docs (this folder), brainstorm docs (`docs/brainstorms/`), an ecology proposal.
- 2+ first-pass scene scripts per zone (placeholders for any new entities).
- The village built out as a town scene with NPC houses + decorations.

**To confirm with the user:** the exact grid cell for the Ant Colony (the world doc places "Deadly Ants" in
col 3; the demo wants it directly *below* the mining zone). Tracked in the plan.
