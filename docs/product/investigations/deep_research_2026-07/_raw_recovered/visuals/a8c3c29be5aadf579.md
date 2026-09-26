I'll research this directly using web search and fetch tools. Let me load them first.

---

Let me fire off multiple parallel searches across the required angles.

---

Good coverage on the first angles. Now let me deep-read the key mechanics pages and search the remaining games in parallel.

---

Necesse Lighting page was just an object catalog, and the RimWorld wiki blocked the fetch. Let me route around those and pull the deeper mechanics pages.

---

Strong RimWorld and Don't Starve detail now. Let me nail down RimWorld's per-tile roof generation and Core Keeper's default-dark model, and fill the Graveyard Keeper angle.

---

I have solid material. Let me hit the deep-read quota with two more full fetches (RimWorld's actual save-file roof data model, and the Core Keeper default-dark thread) plus confirm RimWorld's sunlight/glow interaction and Core Keeper's surface.

---

The Core Keeper "roof light / ceiling hole" mechanic is a key find. Let me deep-read it plus the actual Ludeon dev blog on RimWorld's sun/lighting.

---

Both mirrors blocked. Let me get the Core Keeper biome-lighting/day-night detail from the Steam discussion instead, which is directly on point.

---

I have enough from shipped-game breakdowns to synthesize. Two mirror pages blocked me (rimworldwiki.com and ludeon.com both bot-block WebFetch, Core Keeper Fandom rate-limited), but I recovered every load-bearing fact through Steam threads, the Necesse/Don't Starve wikis, search snippets, and — most valuably — the RimWorld roof-editor tool's actual save-file data model. Here is the report.

---

# How shipped top-down games make caves dark with an organic surface↔underground boundary

## Source table

| # | Game | Source (type) | URL | Depth |
|---|------|---------------|-----|-------|
| 1 | RimWorld | Roof-editor tool README — **actual per-cell roof data model** (concrete impl) | https://github.com/thearn/Rimworld_roof_editor | Deep-read in full |
| 2 | RimWorld | Steam "Think I misunderstand roof collapse" (mechanics thread) | https://steamcommunity.com/app/294100/discussions/0/3823048658582532830/ | Deep-read in full |
| 3 | RimWorld | Wiki *Roof* + *Environment* + *Sun lamp* (mechanics pages) | https://rimworldwiki.com/wiki/Roof , /wiki/Environment | Search-extracted (site 403s the fetcher) |
| 4 | RimWorld | Ludeon dev blog "Sun shadows" (primary devblog) | https://ludeon.com/blog/2013/08/sun-shadows/ | Attempted (403); glow-grid detail via Environment page |
| 5 | Core Keeper | Steam "always dark?" (default-dark design thread) | https://steamcommunity.com/app/1621690/discussions/0/7098294290806458126/ | Deep-read in full |
| 6 | Core Keeper | Wiki *Roof light* / *Biomes* + Steam "replicate Meadow lighting" | https://core-keeper.fandom.com/wiki/Roof_light | Search-extracted (Fandom 402s the fetcher) + thread read |
| 7 | Necesse | Wiki *Caves* + *Lighting* (mechanics pages) | https://necessewiki.com/Caves | Deep-read in full |
| 8 | Don't Starve | Wiki *Caves* (wiki.gg, mechanics page) | https://dontstarve.wiki.gg/wiki/Caves | Deep-read in full |
| 9 | Stardew Valley | Wiki *Darkness* / *Glow Ring* / *Torch* | https://stardew.wiki/darkness/ | Search-extracted |
| 10 | Graveyard Keeper | Wiki *Lantern* / *Torch* | https://graveyardkeeper.fandom.com/wiki/Lantern | Search-extracted |

Search angles covered: (1) RimWorld roof system, (2) Core Keeper cave darkness, (3) generic top-down cave/roof lighting, (4) Necesse, (5) Don't Starve, (6) Stardew mines, (7) Graveyard Keeper. Seven angles, five sources deep-read in full.

The headline: shipped top-down games solve your exact problem with **an explicit per-cell "roof / sky-exposure" layer that is separate from the wall and floor layers**. Nobody infers "roofed" from a straight depth line or from "is there a wall here." RimWorld is the canonical, directly-applicable implementation.

---

## RimWorld — the one to copy (explicit per-tile roof grid)

**The mechanism: a dedicated per-cell roof grid, orthogonal to walls/floors.** The roof-editor tool confirms the concrete data model from the save file: roof is a flat per-cell array, one value per map tile, encoded as 2 bytes per cell, with exactly four roof types:

- `0x00 0x00` = **no roof** (open sky)
- `0x2b 0x1a` = **thin rock roof**
- `0x0d 0x14` = **constructed roof** (player-built)
- `0x44 0x2a` = **overhead mountain** (thick natural rock roof)

That is the crux for you: **"is this open cell roofed?" is answered by a separate one-value-per-cell grid, not by geometry and not by the wall layer.** The tool even renders the grid as a 1-pixel-per-cell grayscale bitmap (tones 0/85/170/255) — literally a second tilemap layer whose only job is roof state.

**How it decides roofed vs open sky.** At map generation, natural rock is grown as organic blobs, and every cell over natural rock gets a rock/overhead-mountain roof stamped into the roof grid. Player-constructed roofs are filled in via a "build roof" zone and must sit within ~6 tiles of a support (wall/pillar/rock). Sunlight is applied **only to no-roof cells**; the wiki's Environment page is explicit: "Light in roofed areas is provided by appliances rather than natural daylight… natural light [is] the light generated on unroofed tiles." So a roofed cell simply never samples the sun.

**Why the boundary reads organic.** Because the roof grid is an independent layer that follows the map-gen rock outline, the surface↔mountain boundary is whatever shape the rock blob is. There's no straight line anywhere — the "dark region" is exactly the union of roofed cells, which traces the organic rock edge. A single map freely mixes open (no-roof, sunlit) and mountain-interior (overhead-mountain, dark) cells; adjacent cells can differ, so a cave stays dark while the beach one tile away stays lit — no global per-map flag involved.

**Digging updates darkness — and this is the key subtlety.** Roof is stored independently of the wall, so when you mine a rock wall the wall is removed but **the overhead-mountain roof bit above it stays**. Overhead mountain / thick rock roof "does not collapse regardless of span" (confirmed in the collapse thread and wiki). Result: a freshly-dug tunnel deep in a mountain is open floor you can walk on, but it is still roofed → still zero sunlight → still dark. That's precisely the "digging into a mountain turns those cells dark" behavior — and it's automatic because the roof layer was already there; mining just exposes floor under a pre-existing roof. (Constructed roofs, by contrast, are the ones that collapse when the last support within ~6 tiles is removed.)

**Day/night.** No-roof cells run the full sun model — the wiki gives the actual formula (angle between latitude and sun-position vectors, minus a latitude offset, cosine, ÷0.7; varies by latitude/season/time). Roofed cells ignore all of that and sit at 0% natural light. Point lights (torches, lamps, sun lamps) are layered on top via a **glow grid**: light propagates by Dijkstra path-distance so it spills around corners, attenuating with mixed linear+quadratic falloff, and roofing doesn't matter for those — they're purely additive.

RimWorld is your scenario almost exactly: one map, mixed surface + mountain interior, organic boundary, dig-reveals-dark, sun ignored indoors.

---

## Core Keeper — the inverse encoding (default-dark + authored "ceiling holes")

Core Keeper is one giant cave, so it flips RimWorld's default: **every cell is dark/roofed by default; light is purely additive.** There is no "is this roofed?" question because the answer is always yes. Ambient light ≈ 0 everywhere; the only illumination is torches, placed lamps, the carried lamp-slot bubble, and pet glow (Embertail). Darkness is a gameplay input, not just cosmetic: enemies spawn on unlit tiles, so lighting a tile suppresses spawns.

The interesting part for you is how they get **naturally-lit patches inside an underground world**: **"roof lights" (a.k.a. ceiling holes)** — a *natural per-tile feature generated in the ceiling of certain biomes* (Azeos' Wilderness, Sunken Sea, Desert of Beginnings) that admits daylight. And players can "punch the ceiling" with a late-game tool to create light-admitting holes. So Core Keeper authors lit regions as **per-tile sky-holes stamped into the terrain at generation**, exactly the RimWorld roof bit but inverted (mark the *lit* cells instead of the *dark* ones). Even the late-game "above ground" area (Azeos' Wilderness, reached by tearing down the Great Wall) is still built from abundant roof-lights rather than a true open sky. Takeaway: when underground dominates, mark the *sky-exposed* cells; when surface dominates (RimWorld), mark the *roofed* cells. Same one-bit-per-cell layer, opposite default.

---

## Necesse / Don't Starve / Stardew — the "separate level" shortcut (why it doesn't fit you)

These three sidestep the hard question by **never mixing surface and underground on one map**:

- **Necesse:** caves are a **discrete underground level** reached by placing a Cave Ladder; "Caves" then "Deep Caves" are separate maps. Underground levels are dark by default (surface uses day/night); the level identity itself is the "no sky" signal — a single per-level flag, not per-tile.
- **Don't Starve:** caves are "generated as whole new maps upon entering" — a separate **shard**. Caves are "perpetually in darkness"; sanity drains and Charlie attacks in full dark. Notably, "some natural light may leak in from the surface… but only while it is daytime in the world above," and cave time stays synced to surface time. That's an authored per-spot light source gated by the surface clock — conceptually the same as a Core Keeper roof light.
- **Stardew Valley:** the Mines are separate indoor "locations," dark by default (deeper floors darker), lit only by a held Torch (~3-tile radius), placed torches, or the Glow/Glowstone Ring. The overworld is a separate location that follows day/night. Again a per-location flag, not per-tile.

Lesson for you: if a region were *entirely* underground you could get away with a single per-zone "no sky" boolean. But your zones are **mixed** (coast + underground in one zone with an organic boundary), so a per-zone flag is insufficient — you need the per-cell layer that RimWorld/Core Keeper use.

**Graveyard Keeper** is the least relevant: no true underground darkness system: lanterns/torches auto-ignite at dusk and extinguish at dawn purely to let you see at night on the surface. It confirms the generic pattern (place-based light sources that follow the clock) but has no roof/sky concept.

---

## The pattern across all of them

Everyone who mixes lit and dark on the same map represents the answer as **a separate per-cell "does this cell see the sky?" layer, authored at generation time, decoupled from walls and floors**:

- RimWorld: mark **roofed** cells (default = sunlit). Boundary = organic rock outline. Mining leaves the roof bit → dug cells stay dark.
- Core Keeper: mark **sky-hole** cells (default = dark). Boundary = wherever ceiling holes are stamped.
- Nobody derives it from a straight depth line, and nobody derives it from "is there a wall on this tile" — because you need open, walkable floor cells to still count as roofed. The roof/sky state has to be its own value.

Sun is ignored indoors trivially: **roofed/no-sky cells never sample the day-night ambient curve**; only sky cells do. Point lights are a separate additive pass (RimWorld's Dijkstra glow grid) that runs the same everywhere.

---

## Recommendation for your build: the cleanest signal to emit

Your situation maps 1:1 onto RimWorld, and you have the advantage RimWorld's map-gen has: **your zonegen builder already knows which cells it carved as cave/tunnel.** So author the signal directly rather than inferring it.

**Emit one per-cell "sky exposure" bit as its own grid layer, parallel to your collision/tile grids.**

- Call it `roofed` (equivalently `noSky` / `underground`). One bit — or one byte if you want headroom — per cell.
- **Semantics:** `roofed = true` → client treats the cell as indoor/underground: ambient = 0 (or a low floor), day-night sun curve ignored, only additive point lights (torches/lamps) illuminate it. `roofed = false` → client samples the zone's day-night sky ambient normally.
- **Builder authoring:** every cell your generator carves as cave/tunnel interior → stamp `roofed = true`. Everything the generator leaves as open surface → `roofed = false` (the default). Because you stamp exactly the carved outline, the surface↔underground boundary is automatically the organic shape you carved — no straight-line assumption, and a cave cell can sit one tile from a lit beach cell in the same zone.
- **Critical convention (RimWorld's lesson):** store `roofed` **independently of walls**. Do *not* set it from "is there a rock wall here." An open, walkable tunnel floor deep in the rock must carry `roofed = true` on its own. That's what makes a dug-out interior stay dark. If you ever support runtime digging: opening rock into a formerly-solid interior cell should leave `roofed = true` (dig sideways into a mountain → new tunnel is dark, like overhead mountain persisting); only breaking through to the *outside/ceiling* (a "skylight"/Core-Keeper ceiling-hole action) should flip a cell to `roofed = false`. Since your darkness is cosmetic/client-side, this flip is a pure client re-evaluation with no sim impact.

**Optional second value (only if you want lit patches inside caves):** add a `skylight` state (Core Keeper roof light / Don't Starve leak-in). A `skylight` cell is underground but samples the day-night ambient locally — bright by day, dark by night — so you can author sun-shafts, cave mouths, or collapsed-ceiling clearings. Minimally you don't need it; the single `roofed` bit covers your stated requirement.

**Transport:** ship the `roofed` grid to the client the same way you ship the tile/collision grids (same run-length or bitmask encoding — it compresses extremely well since it's large contiguous regions). The client then does two cheap passes: (1) base ambient per cell = `roofed ? 0 : sunCurve(timeOfDay)`; (2) additive point-light propagation (a BFS/Dijkstra falloff like RimWorld's glow grid) for torches/lamps, independent of `roofed`.

Net: copy RimWorld's model — an explicit per-cell roof/sky bit, authored by the generator that already knows what it carved, carried to the client as a lightweight parallel grid, with sun sampled only on non-roofed cells and point lights added on top. That is exactly how shipped top-down games get an organic, mixed surface/underground boundary that stays dark where you dug and lit where the sky is open.