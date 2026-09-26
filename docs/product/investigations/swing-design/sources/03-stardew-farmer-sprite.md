# Stardew Valley — Modding: Farmer sprite (swing frame data)
https://stardewvalleywiki.com/Modding:Farmer_sprite
Read: 2026-07-29 · the closest shipped comparable — top-down farming game, tools AND weapons

## What it contributes
Actual per-frame timings from the genre's benchmark, and the fact that it is FRAME-BASED, not curve-based.

## Verbatim (frame index @ duration, in ms)
- Swing DOWN:      24@55, 25@45, 26@25, 27@25, 28@25, 29@swipeSpeed
- Swing LEFT/RIGHT: 30@55, 31@45, 32@25, 33@25, 34@25, 35@swipeSpeed
- Swing UP:        36@55, 37@45, 38@25, 39@25, 40@25, 41@swipeSpeed
- sword swipeSpeed = 6.5 x (10 - (weapon speed + farmer added speed)) x (1 - farmer weapon speed modifier)
- club  swipeSpeed = 10.4 x (...)   <- clubs 1.6x slower than swords by the same formula

## Techniques, checkable
1. **Six frames per swing, per direction.** Not a smooth curve — six discrete poses.
2. **Front-loaded timing: 55, 45, 25, 25, 25, variable.** The first two frames are the slow wind-up
   (100ms of the ~200ms total), then four fast frames. So roughly HALF the swing is anticipation.
   Ours gives anticipation only 15% (Swing) / 22% (Chop). This is a big divergence and worth testing.
3. **The last frame's duration is the weapon's stat** — recovery length IS the weapon speed stat. Weapon
   differentiation lives in the RECOVERY, not the wind-up.
4. **Club = 1.6x sword** via the same formula, one coefficient. Heavy vs light is a single multiplier.
5. Per-direction frame sets: down / left-right / up are separate art, not one arc reused.

## Fit with our constraints
We are procedural (rotate a sprite) where Stardew is frame-based (draw six poses). We cannot copy the poses,
but we CAN copy the timing distribution: front-load the anticipation far more heavily than we do, and make
recovery the per-tool knob.

The 1.6x heavy multiplier is a cleaner model than our per-tool duration table: one coefficient rather than
four hand-set numbers.
