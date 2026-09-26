# §21 · Art direction
<!-- gdd: id=21 status=draft updated=2026-09-26 -->

Not written yet. This section will gather the design from the sources below, run every idea through the
idea lenses, then go to the review page.

## Decided
- **All art is made with gpt-image-2 and pixel-snapped** — *"we will use gpt-image-2 for everything, just full outfits
  I guess as yours are really bad, so we were partway done with the outfits and we had planned regenerating all the
  world and item actual sprites with gpt-image-2 as it was a different pipeline and we did not use pixelsnap
  correctly like our new pipeline … (the only thing done correctly are the outfits)"* (2026-09-26). The model draws
  large visible pixel blocks and `pixelsnap` recovers them exactly — never a resize: *"I ALWAYS wanted the
  pixelsnapped same pixel density converted to pixels (ABSOLUTELY NOT DOWNSCALING)"* (2026-08-14).
- **The look stays** — *"same style as currently"* (2026-09-26): 32 art pixels per grid square, as today's
  objects are drawn.
- **When** — *"most outfits and other things will be made after signing off on the GDD … (and with test batches so
  we can ensure you are doing it right)"* (2026-09-26). The copper outfit is the approved first test batch; the world
  and item art is regenerated after the sign-off, test batch first, and only for content this document keeps.
- **Not code-drawn art** — tried on 2026-09-26 and rejected: *"they look terrible."*

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
