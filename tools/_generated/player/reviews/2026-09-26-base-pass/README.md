# 2026-09-26 — A cleanup pass on the player base

> **VERDICT (2026-09-26): rejected.** The bases in `tools/_generated/player/bases/` are unchanged and stay as they
> are. The decision that followed: all art is made with gpt-image-2, with whole outfits. Kept as a record only.

Folder: `C:\Users\emily\BugFarmer\tools\_generated\player\reviews\2026-09-26-base-pass\`

The two base sprites — `tools/_generated/player/bases/armless_front.png` and `armless_side.png` — redrawn by
Claude in code. **Same character, same 36×71 canvas, same pixel size, same outline**: every edge pixel is where
it was, so anything lined up to the base (hands, outfits) still lines up. Nothing in `bases/` was changed; the
new versions are only here until you decide.

## Open these
1. **`01_today_vs_new.png`** — today's base and the new one, both views, enlarged and at game size on grass.
2. **`02_side_by_side_8x.png`** — the four enlarged side by side.
3. `sprites/armless_front.png`, `sprites/armless_side.png` — the new sprites at actual size (the `.txt` beside
   each is the same sprite as a grid of letters, one per pixel, so a single pixel can be changed by hand).

## What changed
- **The eyes (front).** Both pupils sat on the inner side of the eyes, so he looked slightly cross-eyed. Now
  each eye is dark with a small highlight on the same side, so he looks at you.
- **The eye (side).** It had no pupil — and two pixels inside it were see-through, so on grass the eye showed
  green. Now it has a pupil and a white in front of it.
- **The hair (both views).** Redrawn by hand inside the same outline: separate locks with dark gaps between
  them, a highlight across the top, the fringe ending in points. The locks beside the face are darker than the
  face, so the face keeps its width instead of blending into the hair.
- **Clean edges.** The front had 571 half-see-through pixels around the edge (a soft blur); now every pixel is
  either solid or empty.
- **One set of colours.** 805 colours (front) and 619 (side) became 25, in proper light-to-dark steps for hair,
  skin, top and shorts — the same colours as before, tidied.
- **Side view:** the shoulder strap is a clean band instead of a dotted line, and there is a dark line where
  the far leg meets the near one, so the two legs read apart.
- **Front view:** the tank top's left (lit) side has one outline instead of two dark stripes.

## What did not change
The design — hair, face, tank top, shorts, bare feet, no arms — and the outline, size and pixel scale. The walk
frames and every outfit are separate images and are untouched.

## The numbers (checked by script)
| | front today → new | side today → new |
|---|---|---|
| colours | 805 → 25 | 619 → 25 |
| half-see-through pixels | 571 → 0 | 0 → 0 |
| outline pixels moved | 0 | 2 added (the see-through eye pixels, now filled) |

## What I need from you
Is this better? If yes, I'll make these the bases (the old ones kept in the archive). If some parts are better
and some aren't (for example you prefer the old eyes), say which and I'll keep those from today's version.

Rebuild this folder: `python3 tools/sprites/drawn/base_pass.py` (the hand-drawn parts are in that file:
`FRONT_HAIR`, `SIDE_HAIR`, `SIDE_HEAD`, `face_front`).
