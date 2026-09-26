# §08 · Gear: armour, clothing & accessories
<!-- gdd: id=08 status=draft updated=2026-09-26 -->

Not written yet. This section will gather the design from the sources below, run every idea through the
idea lenses, then go to the review page.

## Decided
- **Whole outfits, not separate armour pieces** — *"we are moving to a whole outfit system (no way I can mask all
  the individual things)"* (2026-08-05); on 2026-09-26: *"we will use gpt-image-2 for everything, just full outfits
  I guess as yours are really bad"*. One image set per outfit, each drawn with its own head, hair and helmet.
- **An armless character with floating hands** — decided 2026-07-28: the hands are separate fists moved by code, so
  a new weapon needs no new body poses. Every approved outfit is built this way.
- **How an outfit is made** — three designs in one image, you pick one, then a turnaround, one walk per direction and
  the five hands, and you approve the finished animations (the `player-sprites` skill). *"anything with CHOSEN has
  been picked, the others we still need to work through together"* (2026-09-26). Made: bronze, fire-ant,
  black-ant. Picked, not yet made: copper, iron, platinum, steel, leather, beetle-shell, gilded-steel, fancy.

## To settle (raw list — not yet checked against the idea lenses)
- **How big the player is on screen.** The finished outfits are 64–91 pixels tall (bronze to black-ant); the game
  still draws the old 16×32 farmer. To be decided by looking at a rendered scene, not in the abstract (backlog, 2026-07-29).
- **How outfits are worn.** The server checks 8 armour slots piece by piece and no item exists yet for the three
  finished outfits: one outfit slot, or an outfit plus some separate slots (accessories)? What drops, what shops
  sell, and how recipes and prices change (backlog: *Armour economy overhaul*).
- **A starter outfit** — what a new character wears.
- **Character choices** — today you pick a class, hair and skin (5 × 5 × 3, `CharacterSelectPanel.cs:28-30`). With
  whole outfits, which of these stay, and how?
- **Tool motions still missing** — the game animates 9 tools; the sword has approved motions in all three facings;
  axe, hoe, net and shovel only side-on; pickaxe, scythe, spear and watering can none.
- **Which extra sets become real sets, cosmetics, or get dropped** — farmer, wood, swamp-gear, fisherman,
  wizard-robe, hornet-stinger, moth-wool, glowworm (outside the armour catalog).
- How many accessory slots · set bonuses · a third legendary set; 4th tiers for fishing and beekeeping gear ·
  outfit names.

## Sources to gather
- `docs/product/design/brainstorm_armor.md`
- `docs/product/design/outfit_roster_scratchpad.md`
- `docs/brainstorms/armor/armor_clothing.md`
- `docs/product/economy/catalogs/armor.md, accessories.md`
- `docs/product/economy/stats_and_bonuses.md`
- `docs/product/economy/DECISIONS.md D10, D11`
- `docs/product/investigations/dye-station-design.md`
