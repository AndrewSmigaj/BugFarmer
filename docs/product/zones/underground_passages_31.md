# Zone Design: Underground Passages (3,1)

## Overview

The first underground zone. This is a cliff face that players mine into. The zone is **mostly solid blocks** (Terraria-style) with a pre-dug mine entrance and scattered natural caverns to discover.

**Zone ID:** `underground_passages_31`
**Grid Position:** Row 3, Col 1
**Biome:** Underground / Cave
**Difficulty:** Easy (entry-level mining)

---

## Core Concept

- **90% solid blocks** - players mine to create tunnels
- **10% pre-carved spaces** - mine entrance, tunnel, natural caverns
- Ground layer is `cave_floor` (revealed when blocks mined)
- Occupant layer is mostly blocks with ores embedded

---

## Pre-Carved Areas

### Mine Entrance (north edge)

- Opening where road from village arrives
- Leads into the pre-dug mine tunnel

### Mine Tunnel

- Pre-carved tunnel going south into the cliff
- Goes roughly 1/4 to 1/3 into the zone
- Shows players what mining produces
- Some ore visible in surrounding walls
- Maybe one or two branches

### Miner's Camp (small area inside mine)

A small cleared room along the mine tunnel:
- `stone_floor` ground
- Miner NPC (sells picks)
- Workbench
- Torches
- Signpost
- Maybe a chest

### Natural Caverns (3-5 scattered)

Hidden in the solid rock, rewards for exploration:
- Small chambers with `cave_floor`
- Mushrooms (regular and glow)
- Crystals (small, occasionally large)
- Stalagmites
- Bone piles
- Some have small water pools
- Not connected to each other

---

## Block Types

### Rock Blocks

| Block | Frequency | Notes |
|-------|-----------|-------|
| `dirt_block` | Common near north | Easy to mine |
| `stone_block` | Very common | Standard rock |
| `clay_block` | Uncommon | Useful material |
| `hard_stone_block` | Rare, more common south | Needs better pick |

### Ore Blocks

| Ore | Frequency | Location |
|-----|-----------|----------|
| `ore_coal_block` | Common | Throughout |
| `ore_copper_block` | Common | Throughout |
| `ore_iron_block` | Uncommon | Mid to south |
| `ore_silver_block` | Rare | Far south only |

---

## Bugs

Found in natural caverns, not solid rock:
- Cave spiders (small)
- Blind beetles
- Mole crickets
- Springtails

---

## Connections
*(corrected 2026-07-06 to the D2/D3/D9 restructure — the old table predated it and put
the Centipede Cavern at (3,0); ants own col 0 now, the cavern moved to (4,1).)*

| Edge | To | Access |
|------|-----|--------|
| North | Village (2,1) | Mine entrance |
| South | **Centipede Cavern (4,1)** | Mine through |
| East | Underground River (3,2) | Mine through |
| West | **Ant Tunnels (3,0)** | The SW dirt seam — the ants' territory bleeds in from col 0 |

---

## Generation Approach

1. Fill ground layer with `cave_floor`
2. Fill occupant layer with `stone_block` (solid)
3. Scatter ore blocks throughout
4. Carve mine entrance and tunnel (remove blocks)
5. Place miner's camp objects in cleared area
6. Carve natural caverns, place cave objects inside
