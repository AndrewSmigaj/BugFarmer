# Grass overhaul — research (how 2D top-down games do grass)

> **Done (noted 2026-10-01):** the grass overhaul shipped on 2026-07-26; the "pending" marks below are from
> before then. As built: `docs/product/architecture/architecture_world.md` §0.

Working research for the grass overhaul (roadmap: `docs/plans/grass-overhaul.md`). Goal: understand exactly how
polished top-down farming/crafting games render grass, so we can design the best overhaul for our game — not the
cheapest or quickest.

## What we're studying
**Games** (≥5, target 10): Stardew Valley, Terraria, Core Keeper, Necesse, Rune Factory, Dinkum, Fields of
Mistria, Roots of Pacha, Sun Haven, Forager, Moonlighter, Graveyard Keeper, Don't Starve (+ others as found).
**Per game:** base tile art vs autotiling/Wang tiles · tufts/overlay decals · wind sway / animation (shader vs
frames) · color/hue/value variation · transitions/edge blending to dirt/path/water · layering & depth ·
density/scatter · biome/seasonal variation · palette + pixel detail.
**General techniques:** autotiling (blob/Wang/marching-squares), scatter decals, wind-sway shaders, dithered
transitions, hue variation / anti-tiling (breaking repetition), sub-pixel detail, edge treatment, depth/parallax.

## Method (thorough-research quotas)
Each research doc: ≥15 deep-read sources (WebFetch full articles/talks/dev-blogs/teardowns, not snippets) +
study real implementations where available; a **source table** (source → technique → cost/perf → fits us?);
≥4 search angles per topic; adversarial cold-critic loop until it returns nothing material; verify load-bearing
claims against the real source.

## Doc layout (this folder)
- `README.md` — this index + status.
- `games_*.md` — per-cluster game teardowns (source tables + techniques).
- `techniques_*.md` — general-technique deep-dives.
- `synthesis.md` — distilled techniques → what applies to OUR game (the input to the plan).

## Status
| doc | scope | status |
|-----|-------|--------|
| games_farming_sims.md | Stardew · Rune Factory · Fields of Mistria · Dinkum · Roots of Pacha · Sun Haven | pending |
| games_sandbox_survival.md | Terraria · Core Keeper · Necesse · Don't Starve · Forager · Moonlighter | pending |
| techniques_autotiling_transitions.md | autotiling, Wang tiles, edge blending, anti-tiling | pending |
| techniques_wind_color_depth.md | wind sway shaders, color variation, tufts/decals, depth | pending |
| synthesis.md | distilled → our game | pending |
