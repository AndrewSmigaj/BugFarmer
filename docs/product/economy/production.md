# Production plan — how we build it all

Turning the design (`crafting.md`, `merchants.md`, `progression.md`) into real content **at volume**, in
bounded shippable waves. Key fact that makes this tractable: **~190 placeables already exist as entities+art**
— most "make decorations craftable" work is *writing recipe lines*, not creating items.

---

## 1. What's NEW (needs art) vs what only needs a recipe
**Only needs a recipe line** (entity + art already exist): the ~190 furniture / decoration / structure /
lighting / storage placeables, and the 4 existing extra stations with art (sawmill, loom, cauldron,
cooking_pot — already in `placeables.json`). These are pure data.

**Genuinely NEW (queue for `gen_sprites.py` / `recolor_sprites.py`):**
| Group | Items | Pipeline |
|---|---|---|
| Material ladder | plank, thread, cloth, glass, charcoal; bars copper/bronze/silver/gold/platinum | gen (icons) |
| New stations | keg, preserves_jar, jeweler, dye_vat, **electronics_bench**, rain_collector | gen (world sprites) |
| Tiered tools/armor | per-metal recolors of the wood/iron base art | **recolor_sprites.py** (already mints tier icons) |
| Utility outfits (~6) | bee suit, fisherman's vest, miner kit, gardener's apron, entomologist coat, explorer cloak | gen |
| Accessories (~12–15) | rings/charms/amulets | gen (icons) |
| Sprinklers (×3) | basic/iron/steel | gen |
| Consumables/dyes | potion/dye icons | gen |
| Bug-derived | chitin set, silk cloth, candles, mead, trophy cases | gen / recolor |

## 2. Authoring conventions (so volume stays consistent)
- **Recipe naming:** key = output id; grouped in `recipes.json` by station; tiered families as
  `{family}_{tier}` (e.g. `pickaxe_copper`). One canonical `unlock` value: `craft` / `buy@<shop>` / `find`.
- **Tier template (kills repetition):** for each metal tier, (1) `recolor_sprites.py --family <fam>` mints the
  icons from the base, (2) a small generator expands the bar→tool/armor recipes from `crafting.md §1`'s
  formula — so a tier is ~one command + one data block, not 15 hand-written rows.
- **Canonical data home:** edit `nakama/data/entities/*.json`, then `python3 tools/publish_entities.py`. Décor
  bonus VALUES are NOT authored until the §11.5 field ships — only the bonus TYPE tag.

## 3. Build waves (each bounded, shippable, verifiable)
| Wave | Content | New code? |
|---|---|---|
| **W1 — Village spine** | material ladder (planks/cloth/glass + copper/iron bars) · all basic stations craftable · wood→copper tools · General Store opening stock | data only |
| **W2 — Gear** | the ~5 metal tiers (recolor + generated recipes) · armor sets · ~6 utility outfits · ~12–15 accessories | data only |
| **W3 — Consumables, artisan & bug-derived** | cooking/cauldron/keg/preserves recipes · bug-drop crafts · **currency + Blacksmith/Carpenter MVP** | coins on `CharacterSave`, buy/sell RPC, shop UI |
| **W4 — Décor & structure fill** | recipes for the ~190 existing placeables, tagged craft/buy/find (~70/20/10) | data only |
| **W5 — Automation & late tech** | **sprinklers** (the new watering-aura mechanic) · fertilizer/bait/rain-collector · dyes · deeper-zone resource placement · electronics bench | sprinkler aura + power = code |

Recommended first build target: **W1** — it makes the village economy real and is pure data (no art blocked,
no engine work). Everything after layers on cleanly.

## 4. What needs engine work (flag early, not data)
- **Currency + buy/sell + shop UI** (W3) — the merchant system.
- **Sprinkler watering aura** + the optional power/electrification route (W5) — the only genuinely-new
  gameplay mechanics here; model the aura on the existing `compost_bin`/`autonet` station pattern.
- **Décor passive-bonus field** (§11.5) — when it ships, backfill the bonus VALUES we only tagged by TYPE.

Everything else is data + art through the existing pipelines.
