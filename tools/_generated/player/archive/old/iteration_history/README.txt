THINGS TO LOOK AT  (open the .png files in this folder)

This folder is on your PC at:
  C:\Users\emily\BugFarmer\tools\_generated\previews\player\_REVIEW\

You picked CRISP. These show how it's going.

--------------------------------------------------------------------------
>>> MASKING? Read HOW_TO_MASK.txt in this folder. Suits to cut up:
    copper_FULL_SUIT_for_masking.png + silver_FULL_SUIT_for_masking.png.
    Save the cut pieces into the  pieces\  subfolder. <<<

23_crest_aware_height.png  <-- NEWEST. Fixes the "short" issue: OLD row measured height to
    the crest tip (squashed the body); NEW row measures to the top of the HEAD (bodies all
    match, crest sticks up extra). Baked into the height-lock; nothing changes in your masking.
22_silver_framed.png  a FAILED experiment (prompt framing zoomed in + cut the feet) -- ignore.

21_copper_silver_matched.png  base | copper v4 | silver v2, all locked to the
    SAME height + pixel size. This is the fix for "different pixel count/size": every suit is
    crisped to the base character's height, so gpt's per-gen scale drift no longer matters.
    copper_FULL_SUIT_for_masking.png is now copper v4 (uniform pixels). Both suits match -> mask + mix.

20_silver_uniform_pixels.png  v1 (uneven) | v2 (uniform-pixel prompt) |
    v2 crisped. v2 draws chunky consistent pixels + crisps almost losslessly. v2 is now
    the silver masking source (silver_FULL_SUIT_for_masking.png). Copper still needs this
    same treatment (redo pending).

18_fancy_silver.png  Fancy silver v1 (before the uniform-pixel fix). one-pass, chibi-locked, dead-on
    front): crest, gold trim, embossed chestplate, chainmail. Its masking source is
    silver_FULL_SUIT_for_masking.png. Mixes with copper.

17_copper_front_facing.png  char | v2 (slightly 3/4) | v3 (dead-on front).
    v3 faces straight at the camera now (symmetrical) -> it's the masking source. A touch
    less crisp than v2's roll; say the word for a few more tries if you want it sharper.
    (copper_FULL_SUIT_for_masking.png is now v3.)

16_full_copper_suit.png  Full copper suit generated in ONE pass:
    char | v1 (came out an ADULT knight - wrong) | v2 (chibi-locked - lines up). v2 is the
    keeper. FILES TO MASK FROM (this folder):
      copper_FULL_SUIT_for_masking.png   = the chibi copper suit, transparent, full-res
      bald_front_fullres_for_lineup.png  = the bald char, same full-res, to line up against

15_copper_armor.png  COPPER armor set on the bald front, piece-by-piece through the
    pipeline (green dummy -> copper -> auto-cut -> crisp -> composed). Full set, reads
    as copper. A bit dark/aged and the torso's slightly busy -- dial-able.

14_side_color_match.png  front | side before | side after a gentle skin
    colour-match toward the front. Clean (no speckle); closes most of the gap. A small
    muted-ness remains (the two gens differ slightly) -- minor at game size.

13_bald_side_from_front.png  BEST bald STANDING side, made by
    feeding the model the already-bald front and asking it to turn to the side (never
    mentioning "hair"). No black fringe, same character, same height. Minor: skin is
    a touch more muted than the front -- can palette-match. This is the standing-side
    walk base. (12_ was the older, black-fringed attempt.)

11_bald_running_sideways.png  First try at a BALD running-sideways pose
    next to the locked bald front. Good running motion, same character + size. This is
    ONE frame; a run animation needs several frames (a cycle).

LOCKED_bald_front.png    = the chosen bald front (run 1). This is THE bald front now.

10_bald_front_runs.png  The bald front generated 4 times, SAME prompt,
    so you can see run-to-run variation and pick one. Runs 1-3 have clean eyes;
    run 4's eyes have a small streak (my cut). Tell me which run to keep.

9_front_and_matching_side.png  Front + a side view that MATCHES it
    (same character, same height, crisp). The side is HAIRED on purpose -- you'll
    bald it by hand. It's left-facing (mirror it for the right side).
    crisp_side_matching.png = just the side sprite by itself, to edit.

7_crisp_steel_gpt2.png   Steel armor made with the STRONGER model
    (gpt-image-2). Chest/legs/boots look good + crisp. BUT there's a checkerboard
    block around the helmet -- gpt-image-2 can't do transparent backgrounds and
    drew a fake see-through pattern that leaked in. (Explained below.)

6_new_bald_vs_old.png    The bald character redone with gpt-image-2 (right) vs the
    old model (left). About the same -- the bald edit is too simple to show a
    difference. Both are the exact same SIZE as our character (good).

5_crisp_dressed_steel.png   The crisp character in steel armor (earlier model).
    Proves the armor comes out crisp too, not just the bare character.
    (Honest note: the black outlines around the armor are a bit heavy right
     now -- that's a cleanup pass I can do.)

0_crisp_base_all_4_directions.png
    The plain character, crisp, in all 4 facings (front / sides / back).
    NOTE: the sides look BIGGER than the front/back. That's because gpt
    drew the side pictures ~13% taller than the others -- an old gpt problem,
    not a crisp problem. Fixing it means re-drawing the 4 as one matched set.

1_pixelsnap_3way.png        the crisp-vs-blurry comparison you already saw.
2_pixelsnap_vs_current.png  new method vs old, bigger.
3_crisp_version_alone.png   the crisp character by itself.
4_detailed_version_alone.png  the softer/higher-res option (not chosen).

crisp_base_down/left/right/up.png = the raw crisp character pictures, one per
    facing (small files -- these are the actual pixels, not previews).

--------------------------------------------------------------------------
WHERE THINGS STAND
  - Crisp look: locked in, works for the character AND the armor.
  - To finish: (a) clean up the heavy armor outlines, (b) fix the side
    pictures being too big, (c) make this the normal way the tool works.
