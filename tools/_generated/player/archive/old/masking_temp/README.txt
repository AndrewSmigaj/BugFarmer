MASKING TEMP FOLDER  (throwaway staging — we'll set up a real workflow later)
Windows path:  C:\Users\emily\BugFarmer\tools\_generated\previews\player\_MASKING_TEMP

WHAT THIS IS
  A clean, curated copy of exactly the images you'd hand-mask, pulled out of the ~20 scratch
  folders so you don't have to guess what's latest. These are FULL-SIZE renders (1024 x 1536) —
  draw your masks at this size. Nothing here is committed; it's all experimental.

  Quick look: open  _CONTACT_SHEET.png  to see every gear piece at a glance with its filename.

THE FOLDERS
  1_mannequins/   The plain green "dummy" — this is what is NOT gear. Use it to see which pixels
                  in a gear render are the dummy vs. the actual armor.
                    - mannequin_FRONT_bald.png .... the front dummy, BALD (what gear is painted on now)
                    - mannequin_SIDE_left_haired.png / _right_haired.png .... side dummies
                      (still HAIRED — only the front has a bald version so far)

  2_bases/        The real character (with hair + skin), for reference — front, both sides, back.

  3_gear_to_mask/ The pieces that came out well and are worth masking:
                    steel_helmet.png ............... full helmet (made on the haired dummy)
                    steel_helmet_ALT_on_bald_dummy.png  a 2nd helmet made on the bald dummy (about
                                                        the same quality — pick whichever you like)
                    steel_chest.png / steel_legs.png / steel_boots.png
                    leather_chest.png / leather_legs.png / leather_boots.png

  4_experimental/ Stuff that did NOT come out well yet — here only so you can see it:
                    leather_cap_v1 / v2 .... caps look bad on top of the big hair; they're on hold
                                             until hair becomes its own layer (backlogged).
                    hairstyle_*  ............ two test hairstyles (hair itself is backlogged).

HOW MASKING WORKS (short version)
  A mask just outlines the GEAR only (the metal / leather), leaving out the green dummy and the
  background. The pipeline then cuts the gear out along your outline and drops it onto the real
  character. So: paint over just the armor piece, ignore everything green.

NOTES
  - "steel_boots" came out thin (more of an ankle cuff) — fine to mask, or say the word and I'll
    re-roll a chunkier pair.
  - Green = dummy, magenta/grey = background — neither is gear.
