---
name: player-sprites
description: Use when creating, regenerating, or processing the PLAYER character sprite or any player WEARABLE — clothing, armor, hats/helmets, hair, boots, held gear — including the AI generation, the mask/extract pipeline, aligning + pixelizing, and where the work lives on disk. Covers tools/player_sprites/** (the aipipe pipeline) and the player paperdoll. Does NOT cover world objects / occupants / tiles / items (that is the add-object skill, Pipeline A) — the player is its OWN pipeline (B) with its own base, mannequin, and layer format.
---

# Player sprites & wearables

The player is a **paperdoll**: a locked base character plus coverage layers (helmet, chest, legs, boots,
hair, …) that `CharacterComposer` stacks in draw order. This skill makes hundreds of those layers
**consistent** with each other and with the game's look, and keeps the work **findable** so a request like
"make a new hat" has one obvious home. Read the `_generated` MAP (`tools/_generated/README.md`) and the
as-built format doc (`docs/guides/art/CHARACTER_DESIGN_GUIDE.md`) alongside this.

## The one idea everything depends on — consistency comes from CONSTRAINT, not prompting
You never ask the model to "match the style" from scratch — that's where drift comes from. Instead you author
the character **once**, then force every wearable to be painted **onto that same locked base, inside a masked
region**, and you **normalize the output with code**. The model only ever fills a hole on a figure it was
handed. That is why the pipeline below exists and why shortcuts around it (free-form "draw a knight") fail.

## Where the work lives (read this before making a folder — the anti-mess rule)
All player art work lives under **`tools/_generated/player/`** (gitignored except the structure docs). Layout:
- **`current/`** — a preview (`character.png`) of what's LIVE in the game. The real files are
  `Resources/Player/layers/{slot}/{id}_{dir}{_w1|_w3}.png` — that is what the game loads and the single source
  of "current." **To polish a live sprite, edit THAT file directly** (each layer PNG is an isolated true-pixel
  piece — never keep a second copy, it just drifts).
- **`in-progress/<item>/<YYYY-MM-DD_HHMM_label>/`** — active work, **per item, per DATED attempt.** Each attempt
  holds `suit.png` (the render to cut) + `pieces/` (the cut pieces). **The newest-dated folder is the latest.**
  "Make a new hat" → `in-progress/<name>/<today>_label/`. **NEVER dump loose files — always a dated attempt**
  (so near-identical attempts stay distinguishable and the latest is obvious).
- **`references/`** — the ONE shared `base`/`bald`/`mannequin` you mask against (not copied per attempt).
- **`old/`** — finished + abandoned stuff, out of the way.
- **On approve:** publish the chosen attempt's `pieces/` to `Resources/Player/layers/…`, refresh `current/`, and
  log which attempt is live in `current/README.md`. If you think you need a new top-level folder, you almost
  certainly don't — see the MAP `tools/_generated/README.md` and `docs/guides/authoring/ORGANIZATION.md`.

## The pipeline (Pipeline B — hand-authored base + AI wearables), as built in `tools/player_sprites/aipipe/`
`aipipe/common.py` is the tested toolbox; `aipipe/run_pilot.py` is the worked end-to-end example (a full set,
front view). Native working resolution is **64×128** (`NATIVE_W/NATIVE_H`, owner-chosen for detail); the model
is **`gpt-image-1.5`**, canvas `1024x1536`, quality `high`.

1. **Base + mannequin.** The locked base is the haired character gear composites onto. Build the dummy with
   `make_mannequin(base, "green")` — it recolours the base to a shaded chroma dummy *preserving luminance* so
   the model still drapes gear correctly. Paint HEAD gear on the **bald** base so a helmet sits on a clean
   scalp. `"green"` is default; `"magenta"` is the fallback chroma when the gear itself is green (extraction =
   "keep everything that isn't the dummy colour", so the dummy colour must be one no gear uses).
2. **Mask the slot.** `slot_region(base, slot)` → a generous paint-here region → `region_mask_png(...)`
   (transparent = editable, opaque = protected). The mask is a soft hint; the precise cut happens in extract.
3. **Generate.** `masked_edit(mannequin_path, mask_path, prompt, ref_path=None)` — a gpt-image edit. It sends
   `input_fidelity=high` + `background=transparent` on gpt-image-1/1.5 (keeps the figure faithful); it OMITS
   both on gpt-image-2 (which rejects them — see FAILED below). An optional second `image[]` (`ref_path`) is a
   finished view for cross-view consistency; the mask applies to the FIRST image only.
4. **Normalize with code.** `normalize_align(mannequin, render, match_band=…)` corrects gpt's scale drift AND
   position in one step by matching an anchor band (SSD on a downscaled grayscale) across scale 0.70–1.40. Use
   `match_band=(0.0,0.32)` (the HEAD) for body gear; use a TORSO band `(0.34,0.64)` for HEAD gear (a helmet
   replaces the head's look, so anchor where the figure is still green in both images).
5. **Extract as a coverage layer.** Build ONE shared palette across the base + every render (`_pc.build_palette`,
   k≈26) so all layers agree on colour, then `extract_layer(base, aligned_render, region, palette=…)` cuts the
   gear (inside region AND not-the-dummy-colour AND opaque; despeckled). Pass `hand_mask=` to use an
   owner-drawn silhouette instead of the colour test (supports "hand-modify the mask" in Aseprite).
6. **Compose / preview.** `compose_layers(base_rgb, base_alpha, [layers in draw order])` stacks onto the base,
   mirroring `CharacterComposer`'s order (legs → feet → torso → head).

### Pixelize FIRST, always (`aipipe/pixelsnap.py`)
gpt draws each logical pixel as an anti-aliased ~N×N block on a non-integer grid. **Recover the true low-res
grid immediately — never surface a raw render for editing** (the owner edits pixels, not drawings-of-pixels).
`python pixelsnap.py in.png out.png --auto [--width 64 --height 128] [--palette 24] [--debug]` finds the pitch
(largest on-grid-energy pitch = the fundamental; square grid from both axes) + corner and samples the **median
of the inner 50%** of each cell (ignores AA borders). When crisping to a fixed height, be **crest-aware**:
normalize by feet-to-top-of-**head** (first head-wide row), so a helmet crest is extra rows, not a squashed body.

## Prompting rules (hard-won — each was a real failure)
- **Negations BACKFIRE.** Never say "no hair" / "without hair" — naming "hair" primes the model to draw it.
  Describe positively ("bare shaved scalp"), or better, FEED the bald base and ask only for a view change.
- **Feed the finished thing + ask for a small delta.** "Here is the bald character; make it stand from the
  side, keep everything else identical" beats "remove the hair and turn it".
- **UNIFORM PIXEL GRID.** Say: big chunky SQUARE pixels, ALL the same size, same density everywhere, no detail /
  filigree / chainmail / anti-aliasing smaller than one pixel; keep the "fancy" in BOLD shapes + a little trim.
  This is what fixes inconsistent pixelization between renders.
- **A one-pass full suit must be LOCKED to the chibi silhouette.** A loose box mask → the model draws a
  realistic ADULT knight. State: stocky CHIBI, BIG head, SHORT body, dead-on symmetric FRONT, keep pose/position.
- **Keep the body identical.** Every gear prompt ends with "keep HEIGHT, body size, proportions, pose and
  position EXACTLY identical; paint ONLY inside the editable region; everything else stays the same figure."

## FAILED / rejected approaches (don't re-try these)
- **gpt-image-2 — rejected.** It refuses `input_fidelity` and `transparent` background and paints a fake
  checkerboard where it wants transparency. Stay on **gpt-image-1.5**. There is no "reasoning/thinking" param
  for image models.
- **Prompt-driven framing/height** ("fill the frame, ~60px tall") — over-zooms and distorts. Control size with
  the METHOD (mannequin = recolor = same size) + `normalize_align`, not words.
- **Hand-resizing sprites** — never. The runtime NEAREST-scales; `pixelsnap`/`pixelclean` are the only intended
  resizers.

## Publish + verify
- **Publish** the extracted, pixelized layers to `Resources/Player/layers/{slot}/{id}_{dir}{_w1|_w3}.png` (the
  9 slots `CharacterComposer` reads: arms, body, chest, feet, hair, helmet, legs, pants, shirt). The game format
  is **16×32 today**; the crisp native-size bump (64×128 → a larger published size) is a **separate,
  owner-gated integration**, not something to slip in silently.
- **Client C# is unverified until a Unity batchmode compile** — a Go/determinism gate never compiles
  `CharacterComposer.cs`. If you touch client code, say so and run the headless compile (see `test-changes`).
- **Spend freely on the image API when the owner has authorized it** — generate fresh assets and the good
  version; don't reuse old art or defer to dodge cost.

## Pointers
- `tools/_generated/README.md` — the MAP (where every generated thing lives).
- `docs/guides/art/CHARACTER_DESIGN_GUIDE.md` — the as-built paperdoll format + `CharacterComposer`.
- `docs/guides/art/object_pipeline.md` — the sibling Pipeline-A (world art) doc; `add-object` owns it.
- `docs/guides/authoring/ORGANIZATION.md` — the repo folder rule (why we don't invent buckets).
