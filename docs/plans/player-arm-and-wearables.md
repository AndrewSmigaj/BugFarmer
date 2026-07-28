# Player character: swinging arm + a wearables pipeline that registers

**Status: PLAN (2026-07-28).** Supersedes the arm section of `player-sprite-and-wearable-creation.md`.

## The problem
A weapon swing needs the arm to move, so the arm must be its own sprite with a shoulder pivot. Everything
else follows from that one requirement, and the failures so far all come from ignoring it:

- Cutting an arm out of a finished armour render gives ragged, fragmented pieces (proven — the copper arm
  trailed loose plate pixels when rotated) and leaves a hole in the torso.
- Free-form AI edits move the shoulder between renders, so a fixed pivot is impossible.

**The fix is ordering: split the BASE first, then generate armour onto the split pieces.** Armour painted
onto a body-without-arm is automatically a body-without-arm. Armour painted onto an arm mannequin is
automatically a clean arm. Registration stops being something we hope for and becomes structural.

Rotation itself is already proven viable at our working size: at 36×71 the arm is 8px wide and reads
clearly when rotated 30/60/90° (`tools/_generated/player/arm_swing_feasibility.png`). Shoulder pivot
measured at (25, 34) on the front base.

---

## 1. The sprite contract
Every character asset — base or armoured — is **two pieces per direction**:

| piece | contains | notes |
|---|---|---|
| **body** | torso, head, legs, feet, and the OFF arm | the weapon-arm socket is **filled in** (a shoulder cap), so no hole appears when the arm swings away |
| **arm** | the weapon arm only: shoulder → hand | drawn hanging straight down; **pivot at the shoulder end**, a fixed pixel per direction |

Directions: **down, side(right), up**. Left = mirrored right, never authored.
Walk frames stay derived mechanically (leg shifts + head bob), as today.

## 2. One-time foundation: split the base — **DONE for `down` (2026-07-28)**
`tools/player_sprites/split_base_arm.py`. Two things the build corrected about this plan:

- **There is no socket to paint.** The plan assumed the arm had to be cut out and the hole filled by hand.
  It doesn't: below the shoulder the character's own art already separates arm from torso by a 1px gap, so
  taking the connected blob on the weapon side leaves the body whole. Verified `body+arm == original exactly`,
  0 overlap, 0 lost pixels.
- **The arm carries a 3-row shoulder cap COPIED from the body, not cut from it.** Rotating about the armpit
  visibly detaches the arm by 50°; the copied cap moves the hinge to the shoulder joint, and because the body
  keeps its own shoulder the overlap can't open a seam. Cap size was chosen by looking at
  `arm_cap_comparison_down.png` (0 = detaches, 2 = notches, 3 = right, 4 = rides into the chest).
- **Gotcha:** the split needs **4-connectivity**. The gap column steps sideways by one pixel partway down,
  which under 8-connectivity is a diagonal touch that bridges it and swallows the whole lower body.

Front result: arm cols 25-31 rows 34-47 (72px), body 1029px, **pivot (26, 34)**, recorded in `pivots.json`.
Each direction also writes a layered `split.aseprite` (body / arm / hidden original) for hand tidying.

Inputs we already have: front `base.png`, side base (`pair_2`'s bare figure). **Missing: the up/back view** —
one generation, then split the same way. Side is expected to be harder: the arm overlaps the torso in profile
rather than sitting beside it, so there may be no gap to find and the split may need hand work after all.

Output: `references/{down,side,up}/{body,arm}.png` + `pivots.json`.

## 3. Mannequins
`make_mannequin()` recolours each piece green (luminance preserved). Six mannequins: body + arm × three
directions. These are the only surfaces armour is ever painted on.

## 4. Per-armour-set generation (repeatable, ~6 calls per set)
For each direction: **two masked generations** — body armour, and arm armour — using
`region_mask_png()` + `masked_edit()` so the model can only paint inside the piece and the silhouette
cannot drift. Then:
- **extract by colour** (`extract_layer`: keep everything that is not mannequin-green), shared palette;
- **convert with `pixelsnap`** (true grid recovery, never an area downscale);
- **split the body armour into slots by fixed row bands** (helmet / chest / legs / boots). Deterministic, so
  every set's slots line up. A hand-mask override stays available for a set the bands don't suit — the
  exception, not the method.

## 5. Game code
- **`CharacterComposer`** returns **two** sprites per (direction, frame): body composite and arm composite.
  Same layer stack and cache; the arm slot leaves the body composite.
- **`PlayerArmAnimator`** (new, mirrors `PlayerToolAnimator`'s shape): `ArmPivot` at the shoulder pixel,
  child arm renderer; rest angle idle, swings through the tool profile's arc.
- **The tool re-parents to the hand end of the arm**, so the weapon follows the arm instead of orbiting the
  player centre. `PlayerToolAnimator` keeps its profiles/timing and drives the arm.
- **Sort order per facing:** arm in front for down/side, behind for up.

## 6. OPEN — the published size (needs an owner decision)
Our art is **36×71**; the game's paperdoll is **16×32** at 16 PPU (1×2 cells). Publishing the new art means
either downscaling to 16×32 — which throws away most of what the new pipeline buys — or making the character
larger in world terms. This is a look/scale judgement, not a technical one, and it blocks step 5's publish
(not the art work). **Recommendation: decide it against a rendered scene** (character beside a tree and the
new grass at both sizes) rather than in the abstract.

## Order
1. Split the front base (body + arm + socket) — the smallest complete test of the contract.
2. Prove it: rotate the split arm, confirm no hole and a clean limb.
3. Up/back view generated + split; side split.
4. Mannequins.
5. Copper set through the masked pipeline, all three directions.
6. Game code (composer split, arm animator, tool re-parent).
7. Size decision → publish.

## Verification
- **Art:** each direction's body+arm composes back to the original silhouette with no hole and no stray
  pixels; the arm rotates through 0-100° cleanly.
- **Pipeline:** a second armour set (silver) runs through with no hand-masking.
- **Code:** headless Unity batchmode compile, 0 CS errors, symbols in `Assembly-CSharp.dll`; in-engine swing
  in all four facings.
- Client-visual + input only: no server, sim, or determinism surface.
