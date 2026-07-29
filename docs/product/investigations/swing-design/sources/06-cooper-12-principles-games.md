# Jonathan Cooper — The 12 Principles of Animation (In Video Games)
https://www.gameanim.com/2019/05/15/the-12-principles-of-animation-in-video-games/
Read: 2026-07-29 · animation director, Assassin's Creed / Uncharted / The Last of Us

## What it contributes
The responsiveness-vs-weight tension stated explicitly, and the resolution: put the weight in the RECOVERY.
This directly contradicts the Stardew timing and is the most important finding so far.

## Verbatim
- Anticipation: "Too little and the desired move will have little weight to it... Too long and the move will
  feel unresponsive, removing agency from the player."
- "A sword that swings immediately might look light, so it is the game animator's task to add that weight at
  the end in the follow-through."
- "To maintain responsiveness, the animator should be able to control when the player is able to perform a
  follow-up action by specifying a frame where the player regains control."
- Exaggeration for games: "poses accentuated and held a little longer than in reality" — because games need
  360-degree readability, unlike film's fixed camera.
- On arcs: game animators deliberately BREAK arcs; "much of the cleanup of making motion-capture work within a
  game is removing egregious breaks from arcs", yet selective breaking (head snapping after the body stops)
  reads as authentic.

## Techniques, checkable
1. **Player-initiated attacks should have MINIMAL anticipation; NPC attacks should have LONG anticipation.**
   Two opposite rules for the same motion, split by who pressed the button. Our player swing currently spends
   15-22% winding up before anything happens — that is input lag the player feels.
2. **Weight belongs in the follow-through, not the wind-up.** Fast-in, slow-out. Stardew does the opposite
   (55+45ms of its ~200ms swing is wind-up). Both ship successfully — so this is a genuine design fork, and a
   good axis for two distinct iterations.
3. **A separate "regains control" frame** decoupled from the animation end: the swing can keep playing
   visually after the player may act again. We have no such concept — IsPlaying gates the whole duration.
4. Held poses, slightly longer than natural, for readability.

## Fit with our constraints
Points 1 and 2 give a fully-formed alternative approach: strike on frame 1 with no wind-up, and spend the
whole budget on an exaggerated follow-through. That is testable against the current implementation directly.

Point 3 is a real gameplay improvement independent of look: recovery could stop blocking input before the
visual finishes.
