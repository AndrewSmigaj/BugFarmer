# Plan — overnight swing design + outfit build-out (2026-07-29)

**Recovered 2026-07-29 from the session transcript after a power cut.** This plan was approved in plan
mode and never written to a file, so it existed only in the conversation. Recorded here so it survives.

**Status: Phases 0-5 DONE. Phase 6 NOT STARTED** (up to 5 more outfits from `armor.md`).
Two owner amendments after approval, both verbatim:
- "you can switch to platinum" — diamond was replaced by platinum, so diamond was never built.
- "i already said to do the swamp one" — swamp set confirmed; noted in `armor.md` as owner-directed.
- "also as part of the plan we need to get the guide written on hwo to create and process these" —
  done: `.claude/skills/player-sprites/SKILL.md` (c920d99) + `docs/guides/art/CHARACTER_DESIGN_GUIDE.md`.

**Note:** the overnight run itself was lost — the turn was ended with "Ready when you are" instead of
executing after auto was engaged. All of Phases 0-5 were done in ~2.5 hours the following morning
(06:27-08:49), which is why Phase 6 was never reached.

---

## THE APPROVED PLAN, VERBATIM

# Plan — overnight: design the best tool/weapon swing, then build out outfits

## Context
The floating-hand approach works — walk and run read correctly, and one animator drives every tool so no
swing needs hand-animating. What hasn't been done properly is the **swing motion design**: so far I ported the
existing curves rather than asking what the best motion would be.

This run does that properly, then uses the day's proven sprite technique to build out the wardrobe.

The failure mode being guarded against is **me rushing** — half-glancing at research, collapsing five ideas
into one, and reporting success without looking. The countermeasures below are chosen to make that visible in
the morning rather than to police me in the moment.

## Anti-rush measures (agreed)
- **≥10 sources, from ≥5 distinct games or engines** — not ten articles about one game.
- **Every source leaves an evidence file**: URL, a real excerpt, and the specific technique it contributed.
  Counting evidence rather than links means the count can't be padded without doing the reading.
- **The five approaches are named in writing BEFORE iteration 1 runs**, each with a *different parent*
  (a specific game, animation-principle theory, a physical/procedural model, frame-data timing, etc). Left to
  myself I would drift into five tunings of whatever worked first; different origins can't quietly converge.
- **Predict before rendering.** Each report states what I expected *before* the gif existed, then what I
  actually observe in it, as separate sections. Today's failures were all "changed it, narrated success".
- The reports exist to make me **wrong in a way you can spot quickly**, not to claim success.

## Phase 0 — prerequisite fix
The swing hand is **1.5× too big**: walk sizes it off body height (17%), swing sizes it off the tool sprite
(25%). One constant, relative to body height, shared by walk/run/swing. Also archive the stray
`outfits/bronze-helmet/` duplicate folder.

## Phase 1 — research → `docs/product/investigations/swing-design/`
How good 2D games handle melee/tool swing feel: anticipation and follow-through, hit-stop, arcs and trails,
frame timing, recovery, weight differentiation between light and heavy tools, and how the hand/weapon is
composited. Sources saved to `sources/` one file each.

## Phase 2 — design
A design doc scoring **≥4 candidate approaches**, picking one, and naming **all five iteration approaches**
with their distinct parents. Written before any implementation.

## Phase 3 — five iterations
Each: predict → implement → render → observe → report.
- **Demo scene must show BOTH the side and the front-facing sprite** — both need to work.
- Framed so the character and the full arc fill the frame (the last attempt was a thumbnail in a green field).
- Four tools each: sword, axe, net, hoe — they exercise genuinely different motions.
- Output: `iteration-N.gif` + `iteration-N.md` (approach / prediction / what I see / one improvement).

## Phase 4 — gauntlets for the existing sets — **6 image calls**
`ant-carapace, beekeeper, farmer, gold, silver, wood` (bronze already has one). Same prompt shape as the
bronze gauntlet, referencing each outfit's own sheet so the material matches.

## Phase 5 — new outfits — **20 image calls** (10 sets × sheet + gauntlet)
Exactly the technique that worked today: gpt-image-2, no mask, the 12-frame 3×4 sheet template, both bases as
references, "the character has no arms" stated explicitly, headgear included.

Yours: **swamp gear, fisherman, leather, ranger, wizard's robe, hornet-stinger set** (design mine), plus
**diamond** *if you confirm* — see the flag below.
Mine, fitted to a bug-farming/crafting game: proposed in the design doc before building, not invented at 3am.

## Phase 6 — from the catalog — **up to 10 image calls**
`docs/product/economy/catalogs/armor.md` is the canonical list. Still unbuilt and genuinely planned:
padded/cloth, copper, steel, platinum (base ladder); Entomologist, Miner/Spelunker, Diver/Waders (concepts).
Up to 5 of these.

## ⚠ Needs your call before Phase 5
- **Diamond** is recorded as **cut** (`armor.md:25`) — "platinum is the top". Build it anyway, or skip?
- **Swamp set** is recorded as **optional/pending until the swamp is designed** (`armor.md:56`). Your ask
  overrides if you say so.

I'll build both unless you say otherwise, and note in the catalog that they were owner-directed rather than
letting the doc and the assets silently disagree.

## Cost
**~36 image calls** total (6 + 20 + 10). Flagging the number up front rather than discovering it later.

## Files
- `docs/product/investigations/swing-design/` — research, sources, design doc, 5 reports, 5 gifs.
- `tools/player_sprites/demo_swings.py` — hand scale, framing, the five approaches.
- `tools/player_sprites/gen.py` — all generation goes through it (records prompt + model + refs per run).
- `tools/_generated/player/outfits/<name>/` — one folder per outfit, gauntlet inside it. No new buckets.
- `docs/product/economy/catalogs/armor.md` — mark what got built.

Nothing under `BugFarmerClient/` is modified; this stays preview + art work.

## Verification
Ten evidence files from five-plus distinct games. Five reports whose approaches differ in origin, each with a
prediction written before its render. Five gifs, each showing side and front, arc fully in frame, hand
hand-sized and on the handle. Every outfit folder holds a 12-frame sheet, 12 cut frames and a matching
gauntlet.
