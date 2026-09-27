# §21 · Art direction
<!-- gdd: id=21 status=draft updated=2026-09-26 -->

Not written yet. This section will gather the design from the sources below, run every idea through the
idea lenses, then go to the review page.

## Decided
- **All art is made with gpt-image-2 and pixel-snapped** (2026-09-26) — the outfits are the only art made the right
  way so far; all the world and item art will be regenerated on the same pipeline, because the older route didn't
  convert its pixels properly. The model draws large visible pixel blocks and `pixelsnap` recovers them exactly; art
  is never shrunk to size (2026-08-14).
- **The look stays** (2026-09-26) — the same style as today: 32 art pixels per grid square, as today's objects are
  drawn.
- **When** (2026-09-26) — most outfits and other art are made after this document is signed off, starting with test
  batches that check the work is being done right. The copper outfit was the first test batch (approved); the world
  and item art is regenerated after the sign-off, test batch first, and only for content this document keeps.
- **Not code-drawn art** — tried on 2026-09-26 and rejected.

## To settle (raw list — not yet checked against the idea lenses)
- **One sizing rule** for everything whose on-screen size comes from its image's pixel count rather than the data —
  items (0 of 209 have a size), held tools, ground drops, strike effects, grass tufts, bugs — so sharper art does
  not change how big things look.
- **Keeping one look across hundreds of separate images** — today's 431 object sprites use 8,226 colours between
  them; judge on the first test batches whether that shows.
- **The grass** — shipped 2026-07-26 at 16 pixels per square, half the density of everything else.
- The player's size on screen (see §08).

## Sources to gather
- `docs/guides/art/*.md` (the pipeline guides; `object_pipeline.md` first)
- `tools/art/style.json` + `tools/art/catalog/*.json` (the approved per-family prompts)
- `.claude/skills/player-sprites/SKILL.md` + `tools/_generated/player/APPROVED/DECISIONS.md` (the outfit procedure
  and every pick)
- `docs/product/BACKLOG.md` — *Now — all art on gpt-image-2 + pixelsnap*
- `docs/product/art_needed.md` (superseded missing-sprite queue)
