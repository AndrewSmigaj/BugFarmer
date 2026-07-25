# Grass rendering in top-down farming / life-sim games

Deep-read research for the grass overhaul. Focus games: **Stardew Valley, Rune Factory (3/4/5),
Fields of Mistria, Dinkum, Roots of Pacha, Sun Haven.**

Per game we want: tile size + grid; base tile vs autotile vs base-color-plus-decals; grass detail
tufts/blades/flowers as scattered decals (density, random placement/rotation/variant); color
variation (variants / hue jitter / seasonal / gradients); transitions to dirt/path/water/sand;
animation (sway — frames vs shader — and player reaction); depth/layering (shadow, overlap with
player); and THE key question — what specifically makes the grass read as lush/polished rather than
a flat repeating tile.

**CONFIRMED** = stated by a cited source. **INFERENCE** = my reading of screenshots/rips/mechanics
(flagged). Uncertainty is called out explicitly.

---

## Source table (URL → concrete technique → cost/complexity → fits our Unity tile-PNG + shader game?)

| # | Source (URL) | Game | Concrete technique it reveals | Cost / complexity | Fits us? |
|---|--------------|------|-------------------------------|-------------------|----------|
| _(filled in as sources are deep-read below)_ |

---

<!-- Sections appended per game as research proceeds -->
