# Ground-tile R&D — candidates + what we learned (2026-07-25)

**Look at `previews/_GRID_COMPARE.png` first** — every candidate rendered as a repeating field, which is
the only view that shows seams and repetition. `previews/_ALL_CANDIDATES.png` is the same set bigger, with
each tile shown on its own next to its field.

Nothing here has been published to the game. `raw/` = the 1024px API output (kept — it cost money),
`candidates/` = the 32×32 results, `previews/` = the comparison sheets.
Measure/preview anything with `python3 tools/sprites/tile_lab.py grid|sheet|one <png>`.

## The headline finding: it's the SCALE of the detail, not the prompt
Our shipped `grass.png` is flat speckle, and **A1 proves why.** A1 is our existing prompt run on
gpt-image-1.5: at 1024px it's a *lovely* grass texture — but its blade marks are only ~5-10px, so shrinking
1024→32 averages many marks into every output pixel and they vanish into mush.
**For a 32×32 tile the marks must be ~25-32px in the 1024 render (≈ one output pixel each).** Every good
candidate below obeys that; every bad one doesn't. Measured: our current tiles have 20 near-identical greens
with **no dominant base** (base_share 0.11) vs the Stardew reference's **0.48**.

## What each approach did
| # | approach | result |
|---|----------|--------|
| **A1** | our existing tile prompt on 1.5 | Beautiful at 1024, **mush at 32** — the detail-scale trap. Too saturated/lime. |
| **A2** | "draw exactly 32×32 chunky blocks" | **Backfired**: the model drew a literal grid with visible cell borders — reads as checkered floor. Don't ask for blocks this way. |
| **A3** | render a big field, crop the interior | **Works well.** Asking for a *field* (not "a tile") avoids tile-framing/vignette artefacts; marks came out at a good size. |
| **A4** | offset 50% + mask-repaint the seam cross | **Works.** Clean seams (seam 23/13), texture preserved. A solid way to make any candidate wrap. |
| **A5** | reference-fed edit (input_fidelity=high) | Mediocre here — picked up checkering from its source. Reference-feeding is still the right tool for *palette matching* (see tufts). |
| **SH** | **4 tiles on ONE sheet** | **The standout.** Four good, distinct tiles that share palette/style *by construction* (one image), plus a nice checkered base + light/dark blade fans + tan specks. `q4` measures seam (0,0). This was the owner's idea — one he expected probably would not work — and it worked best. |
| **M1** | AI texture → grid-sample → code seam-heal | Good: AI look, guaranteed wrap, no extra API call. |
| **M2** | AI texture → patch quilting | Tiles fine but the quilt repeats visibly — patch size needs work. |
| **M3** | palette extracted from AI → procedural stamping | Good, calm, guaranteed seamless; the most controllable. |
| **H1-H3** | hand-authored pixel grids (no API) | All seamless **by construction**. H1 reads as a quiet, plausible grass base; H2/H3 are mottled alternatives. |
| **OV** | grass drawn taller than the cell | **Did not work as a tile** (as predicted): the model drew a *scene* — a wall of tall grass behind ground — not a repeatable overhang. The blades themselves are good pixel art, so this render is a decent source for separate **tuft sprites** instead. |

## V — the recipe applied (one extra call, after the experiments)
`V1_recipe_*` combines the two winners in ONE call: big-field framing + a 2×2 sheet + an explicit
**mark-scale** instruction ("smallest mark ≈ 1/32 of the square, ~30 across, not hundreds of specks"), then
code-side seam healing (the `_wrapped` versions) so no extra calls are spent per variant.
- **The mark scale worked** — the marks survive the downscale, exactly as the headline finding predicts, and
  the four variants are style-matched.
- **But the palette drifted bright/lime**, away from our muted look, because the prompt specified *structure*
  without anchoring *colour*. **Fix next time: state the palette explicitly, or feed an existing tile as a
  colour reference (`--ref`).** Also learned: when slicing a sheet, **auto-trim the divider lines** — a fixed
  inset left black pixels in the crop and the `edge_delta` metric caught it (39 → 7 after the fix).

## My honest picks (for the owner to choose from)
- **Best overall: `SH1_sheet_q4` / `q1` / `q3`** — muted natural green, readable blade marks, no visible
  repeat, *and* a matched variant set from a single call.
- **Best single AI tile:** `A3_bigfield_crop` (or `A4_offset_healed` for a guaranteed-wrap version).
- **Best guaranteed-seamless:** `M1_mine_seamheal`, `M3_mine_palette_stamp`, `H1_handauthored` (calm/quiet).
- **`V1_recipe_*`:** right structure, wrong colour (too bright/lime for us) — worth one re-run with the
  palette pinned; it would likely become the best of the lot.
- **Not usable:** `A2_gridlocked` (literal grid), `OV*` (a scene, not a tile).

## Recipe that follows from this (draft — to confirm with more runs)
1. Ask for a **large flat field** of the material, "seen from directly above, even coverage, no centre subject,
   no border, no vignette, flat lighting", crisp pixel art, ~5 colours — **not** "a tile", **not** "N×N blocks".
2. Make sure the **marks are big enough** to survive the downscale (~1 output pixel each).
3. Get variants from a **2×2 sheet in one call** (style-matched by construction), or by re-cropping the field.
4. Convert by **grid-sampling** (median of each cell's inner 50%) + palette snap, not area-averaging.
5. Make it wrap by **offset + mask-repaint** (A4) or **offset + code blend** (M1) — the model will not wrap on its own.
6. Verify with `tile_lab` (seam percentile ≈ 50, base_share ≈ 0.5, no vignette) **and** by looking at the field.

## Still open
Dirt (the real test of whether this generalises to a structured texture), tuft sprites, and folding the
winning recipe into the sprite pipeline + a proper tiles guide.
