Consistent AI Pixel-Art Character + Equipment Pipeline (Final)
Goal: one animated player sprite plus hundreds of armor/clothing items that (a) match the gpt-image-1.5 style used by the rest of the game, (b) layer correctly over the body as a paperdoll, and (c) slice into body parts that drive your existing procedural animation rig.

Style-agnostic: fill every {BRACES} placeholder yourself. Engine-agnostic: Section 9 adapts output to the part format your game already consumes.


0. The two ideas everything depends on
Idea 1 — Consistency comes from constraint, not prompting. You author the character once, then force every item to be painted onto that same locked base, inside a masked region, and normalize the output with code. You never ask the model to "match the style" from scratch — you never give it the chance to drift.

Idea 2 — Never trust the model to preserve pixels. Enforce it in code. gpt-image-1/1.5 re-renders the entire canvas on every edit call. The mask is a strong instruction about where to paint, not a guarantee that unmasked pixels survive. Even "unchanged" areas come back slightly different. So:

Composite-in-post rule: after every edit call, programmatically paste the base's pixels back everywhere OUTSIDE the mask. Accept generated pixels only INSIDE the mask.

After compositing, "outside the mask is identical to base" is true by your code, which is the only guarantee that holds. The whole extraction pipeline rests on this, not on API behavior.


1. Lock the fixed spec (author once)
1.1 Style — {STYLE}. One reusable paragraph pasted into every prompt. Specify: palette (or named palette), outline (1px black / colored / none), shading (flat / cel / dithered), perspective ({VIEWS}), and detail density. Since the rest of your game is gpt-image-1.5 output, derive {STYLE} by describing your existing game art precisely — same vocabulary every time.

1.2 Native resolution + author scale. Pick the sprite's native size, e.g. 64 px tall character. Pick an integer author scale so the API canvas is an exact multiple — e.g. native 64×64 cell grid × 16 = 1024×1024 API canvas. All real assets live at NATIVE resolution; the API only ever sees nearest-neighbor ×16 upscales. This matters because the model outputs "fake" pixel art whose blocks aren't grid-aligned — the modal downsample in Step 5 recovers a true grid, and feeding the API a grid-perfect upscaled base encourages it to keep the grid.

1.3 Canvas + background. Fixed API size (1024×1024 or the model's supported sizes). Request transparent background (gpt-image-1.5 supports it; 2.0 doesn't yet). If alpha edges come back fuzzy, fallback: generate on solid magenta and chroma-key in post.

1.4 Rig pose + baseline. See Section 1A. Feet on a fixed baseline row; character centered. This anchor is shared by every sprite and item forever.

1.5 Views/frames — {VIEWS}. Each direction is an independent base: base_{view}.png. (With cut-out animation you need one rig pose per view, not per animation frame — the engine makes the frames.)

1.6 palette.png. The exact allowed colors. Every asset gets snapped to it.

1.7 Slots — {SLOT}. e.g. head, torso, legs, hands, back, feet, plus hair as its own layer with a reduced "hat hair" variant, so helmets/hats can swap or shrink it (base head is bald/short under it).


1A. The rig pose — what you cut from (critical)
Cut every part from ONE neutral rig pose per view — never an action pose. Procedural animation rotates rigid pieces around joints; it does not redraw them. A running frame has the bend baked into the art and cannot be un-bent. One neutral pose per view feeds all animations.

Requirements ("A-pose built for cut-out rigging"):

Limbs separated from the torso (arms ~15–30° out), legs slightly apart — pieces must be sliceable.
Each segment straight along its bone; elbows/knees straight or barely bent.
Hands relaxed, nothing crossing or touching another part, head straight.

Joint overlap (or rotation tears gaps): each piece gets extra material and a rounded end at the joint, so adjacent pieces overlap; the pivot sits inside the overlap. Encode this in the parts mask. Never butt-joint.

Honest limits: rigid gear (plate, boots, helmets) rotates believably — that's how armor moves. Flowing cloth (capes, robes, skirts) is stiff under rigid rotation: cut cloth into 2–3 stacked flaps on their own bones, use mesh deform (Spine/Unity 2D), or accept stiffness. 2D rotation isn't 3D foreshortening — keep swings moderate within each view; that's what per-view art is for.


2. Author the masks (once, at NATIVE resolution)
For each view:

Slot masks slot_{SLOT}_{view}.png — white where that slot's item may be painted, with a generous margin beyond the body for silhouette-changing gear (pauldrons, crests, capes). Too tight clips items; too loose invites wandering art.
Parts mask parts_mask_{view}.png — flat ID color per body part (head, torso, upper_arm_L, forearm_L, thigh_L, shin_L, foot_L, R-side, …), with joint overlap (1A), extended into slot-mask margins so overflow armor can be assigned to a part.

Author at native res (easy, unambiguous). Nearest-neighbor upscale ×16 whenever a mask is sent to the API.


3. Build the base character (once per view)
Generate with:

Full-body character sprite of {CHAR}, {VIEW} view, standing A-pose with arms

slightly away from the body, entire body visible head to feet, centered on the

canvas, feet on a consistent ground line, transparent background. {STYLE}

Modal-downsample to native res (Step 5 mechanics), palette-snap.
Hand-clean at native res in a pixel editor until it's exactly right. Every one of hundreds of items inherits this file's quality — this is the one place manual polish is mandatory.
Freeze as canonical base_{view}.png (native). Its ×16 upscale is the input for all item edits.

Keep the base bald/short-haired; generate your default hair as the first "item" in the hair slot.


4. Generate items (masked edit + composite + reference chaining)
Front view of each item — edit call: image = base_front ×16, mask = slot mask ×16, prompt:

Add {ITEM}, worn on the {SLOT}. Keep the character's pose, body, size, and

position identical. Paint only inside the editable region. {STYLE}

Other views — chain the reference. API calls are independent; "batching" does nothing for consistency. What works: pass the finished front-view result as an additional input image when editing the side/back bases:

Add the same {ITEM} shown in the reference image, worn on the {SLOT}, drawn

from the {VIEW} view. Keep the character's pose, body, size, and position

identical. Paint only inside the editable region. {STYLE}

This is the mechanism that keeps one item recognizable across its views. (Verify the current parameter names for multi-image edit + mask in the API docs before wiring the batch runner.)

Immediately composite-in-post (Idea 2): paste base pixels back outside the mask. Store the composited result as raw_{ITEM}_{view}.png.

Prompt style tip that pays off later: ask for armor "with visible segment seams at shoulder, elbow, hip, and knee joints" — part-cut boundaries then read as intentional armor articulation instead of slicing artifacts.


5. Normalize, then extract (order matters)
Per raw item image:

Re-grid: modal-downsample ×16 → native. Each native pixel = the modal (most frequent) color of its 16×16 cell; alpha = modal opaque/transparent. This absorbs the model's off-grid noise and fringe.
Palette-snap to palette.png (nearest color; no invented colors).
Diff-extract: item pixels = pixels inside the slot mask where snapped_raw != snapped_base — exact palette-index comparison, because both sides were snapped first. (Diffing before snapping false-positives on every slightly re-rendered skin/shirt pixel inside the mask margin.)
De-speckle: drop isolated 1–2 px orphans.
Save aligned item_{ITEM}_{view}.png, transparent elsewhere.


6. Slice into parts (script, slot-aware)
Apply parts_mask_{view} to the base and to every item layer:

Pixel inside a part region → that part.
Overflow pixel (margin, beyond the body) → assign slot-aware, not nearest-anything: helmet overflow → head; torso-slot overflow near the shoulder → upper arm or torso per your rig's pauldron convention; cape → its own back part. Encode these defaults per slot; nearest-region only as final fallback.

Output body_{part}_{view}.png, item_{ITEM}_{part}_{view}.png — every item cut on the same boundaries as the body, so your existing rig moves body and gear together.


7. Layer / draw order (author once, per view)
e.g. front: [back, body_*, feet, legs, torso, hands, head, hair|hat]; side views typically differ (far arm behind torso, near arm in front). Store as config your engine reads. Decide pauldron attachment (torso vs upper arm) here and keep Section 6's overflow rule consistent with it.


8. QA loop + the pilot gate
Automated flags per item:

Ignored: changed-pixel count ≈ 0 → regenerate.
Clipped: item pixels form a hard edge along the slot-mask boundary → the mask cut the item off → widen mask or regenerate. (After compositing, "spill" can't exist — clipping is the failure mode to watch.)
Style drift: pre-snap color count or average snap distance abnormally high → inspect; usually a prompt problem.
Cross-view identity: flag items whose per-view layers differ wildly in palette usage or pixel count → re-chain from the front reference.

Human pass: spot-check a random sample; hand-fix outliers at native res (a few minutes each — you author the base once, you touch up items).

Pilot gate: run ~20 varied items end-to-end before mass production. Measure the rejection/hand-fix rate. If it's low, scale up. If it's high, move generation to a local ControlNet pipeline (Section 11) and keep everything else (masks, extract, slice, pack) unchanged — the pipeline is generator-agnostic.


9. Pack + manifest (adapt to your engine)
Emit whatever atlas/file layout your existing system consumes, plus a manifest:

item_id: {

  slot, views: [...],

  parts: { part: filepath },

  anchor: [x, y],            # shared feet-baseline anchor

  layer_order_ref,

  provenance: { prompt, model, date, reference_chain }   # no seeds exposed —

}                                                        # this is your repro trail


9A. Change management — what's cheap vs expensive to change
Treat the isolated item layers (post-extract, pre-slice: item_{ITEM}_{view}.png) as the canonical archived assets. Per-part files are derived artifacts — slicing is a free, re-runnable script.

Cheap to change later (re-run scripts, no regeneration): parts mask / part boundaries, joint overlaps, draw order, packing format, palette (re-snap), animation timing/angles.
Expensive to change later (invalidates generation — hundreds of API calls): the rig pose, the base sprites, slot mask shapes, native resolution, {STYLE}.

So: freeze pose/bases/slot masks/style before mass production (the pilot gate); iterate freely on everything in the cheap list afterward. Since the in-game animation system may still evolve, this split is what makes that safe.

Golden set: keep ~10 fixed items with locked prompts. Re-run them after any prompt-template, mask, or pipeline change and diff against their last outputs — regression testing for the art pipeline.
10. Animation notes (affects how parts are authored)
Rotation jaggies: rotating pixel art at arbitrary angles breaks the grid and looks mushy — the classic reason Stardew-likes hand-draw frames. Since your rig already works, mitigate per frame: quantize bone angles to coarse steps, or rotate each part at high res (×16) and re-pixelate to the grid. Pick one before authoring; it influences how much joint overlap you need.
Cloth: flap-bones or mesh deform (see 1A limits).
Hats: draw order hair|hat + the hat-hair variant handles most cases without per-hat hair work.


11. Costs + alternatives
Cost reality: items × views × retries = thousands of edit calls at scale. At typical gpt-image per-image pricing this lands in the tens to a few hundred dollars — check current pricing and multiply before committing; the pilot gate exists partly for this.
Local ControlNet/img2img (ComfyUI + pixel-art model, conditioned on the base's silhouette/lineart): pixel-locked consistency, near-zero marginal cost, real setup effort. The drop-in replacement for Section 4 if gpt-image QA rates disappoint. Note: its style won't automatically match your gpt-image game art — you'd tune toward it; this is the main trade-off, since style match is why you chose gpt-image-1.5.
Universal LPC Spritesheet Generator (free, hand-drawn, modular, animated) — only if your style can flex to it; otherwise ignore.


Appendix A — Script inventory
Script
Input
Output
batch_gen
item list, bases ×16, slot masks ×16, prompts
raw API results
composite
API result, base ×16, slot mask ×16
composited raw (outside mask = base)
regrid
composited raw (×16)
native-res image (modal per cell)
snap
native image, palette.png
palette-exact image
extract
snapped item, snapped base, slot mask
isolated aligned item layer
slice
layer, parts mask, slot-overflow config
per-part PNGs
qa
layers, masks, palette
pass/flag report
pack
part layers, layer-order config
engine atlas + manifest.json


All pure Pillow/numpy except batch_gen (API wrapper). No art judgment required anywhere except hand-cleaning the base and QA spot-checks.
Appendix B — Order of operations
Freeze: style, native res + author scale, rig pose, views, palette, slots.
Generate → re-grid → snap → hand-clean base per view. Freeze bases.
Author slot masks (margin) + parts mask (joint overlap), native res.
Pilot ~20 items: masked edit (front, then reference-chained views) → composite → re-grid → snap → diff → de-speckle → slice → QA.
Decision gate: scale with gpt-image, or swap generator to ControlNet.
Mass-produce; QA flags; hand-fix outliers. Archive isolated item layers as canonical (9A); establish the golden set.
Pack + manifest → engine.

