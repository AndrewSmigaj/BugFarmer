# Swing while running — PICKED: half pump

Owner, 2026-08-14, verbatim: **"half pump is the one"**

Chosen from three renders of the off (far) hand while the sword arm swings and the legs keep running:
`bronze_ALL_THREE.gif` — keeps its full run pump / **half pump** / held forward.

## The numbers behind it

From `tools/player_sprites/run_swing_lab.py`, variant `B_half_pump`:

- the FAR fist (`hands["back"]`, dimmed, drawn behind the body) swings at **half** the approved RUN
  amplitude — `amp * 0.5`. Nothing else about the run changes: `ay`, `rot`, `tilt`, `waist`, `ratio` and
  the phase array are the approved values, read from `official.py`'s `GAITS["RUN"]`.
- the NEAR fist becomes `grip_back` on the swing arc — no decision there, it is holding the weapon.
- the body is sampled by time off the run cycle (90ms beats) across the 320ms stroke, so the legs run
  through the swing and come out mid-stride.

## Not built

This is a lab render only. Nothing in the game or in `build.py` swings while running yet — owner,
2026-08-14: *"None of this has actually been implemented so we will need to implement this later."*
Wiring it in means a new animation kind, since today a gait and a swing are separate rows in
`official.ANIMATIONS` that never overlap.

Known from the render, for whoever builds it: the off fist sits low and mostly behind the torso, so at
game size it is a few dark pixels; and the first five frames are identical across all three variants,
because the anticipation and the start of the strike fall inside a single 90ms run beat.
