# Masahiro Sakurai — "Thinking About Hitstop", Famitsu column vol. 490-1
https://sourcegaming.info/2015/11/11/thoughts-on-hitstop-sakurais-famitsu-column-vol-490-1/
Read: 2026-07-29 · director of Super Smash Bros / Kirby

## What it contributes
Hitstop as a SCALED quantity with a cap, from the designer who made it a genre standard.

## Verbatim
- "When you strike the opponent, both parties momentarily freeze, emphasizing the power of impact."
- "In general, the more damage an attack inflicts, the longer the hitstop period."
- "the hitstop period is determined not only by the amount of damage, but by certain factors exclusive to each
  individual attack."
- Marth's sword TIP gets increased hitstop to emphasise its strength; the blade edge gets reduced hitstop.
- Restrained in free-for-alls: "When you and the opponent are frozen in hitstop, that creates a chance for a
  third player to move in and strike."
- He caps maximum freeze frames regardless of attack power, so heavy weapons (Hammer) do not stall the game.

## Techniques, checkable
1. **Hitstop duration scales with damage** — it is a function of the hit, not a constant per weapon.
2. **Plus a per-attack override**, so a signature move can feel special beyond its damage number.
3. **Sweet-spot differentiation**: the same weapon gives MORE hitstop on its strong part and LESS on its weak
   part. That is hitstop used to teach a mechanic, not just to feel good.
4. **A hard cap** regardless of power — otherwise the game stalls.
5. **Multiplayer caution**: freezing both parties creates an exploit window. Relevant to us — this is a
   multiplayer game, and freezing the local player during a swing while other players keep moving is a
   desync-adjacent design question, not merely cosmetic.

## Fit with our constraints
Scaling hitstop by damage is directly available: MeleeController already passes item move data (arc, swing
time) and fires onContact.

The multiplayer note is the important caution. Our hitstop must be a LOCAL VISUAL freeze of the tool/hand
only. It must never pause the sim or the player's position, or clients diverge. That constrains the design in
a way none of the single-player sources would have told us.
