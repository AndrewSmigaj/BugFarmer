"""AI player-sprite pipeline (mannequin-based, gpt-image-1.5).

Generates the player body + gear as style-matched pixel-art coverage layers that the
runtime paper-doll (CharacterComposer.cs) already consumes. Separate from the
hand-authored Pipeline-B modules in the parent package (pixkit/body_frames/wearables).

Flow per gear item (all stages proven in the refart_spike experiments):
  generate on the GREEN MANNEQUIN (rough reusable slot region)
    -> auto-align the render to the base (head-match)
    -> extract "not the mannequin colour" (+ optional owner hand-mask override)
    -> palette-snap (authored neutral palette) -> downscale to 32x64 coverage layer
  then derive the 4 walk frames and pack into Resources/Player/layers/ + a manifest.

Client-cosmetic art only: nothing here touches the deterministic sim.
"""
