# 2026-08-03 — the walk/run hands, and two backwards outfits

## The mistake

Every animation was built on the **cut gauntlet views** (`gauntlet/front|back|side.png`) instead of the
hands that were already agreed. `APPROVED/DECISIONS.md` says in writing that those cuts

> "are a re-cut made on 08-01 and were never approved... anything unapproved living here is how the wrong
> sprite gets picked later."

Which is exactly what happened. Bronze's walk used a discarded sprite, and the swing used the tool-grip
hand — a hand meant for holding a handle — while the agreed hands sat unused in `APPROVED/hands/`.

## The hands, settled. Do not substitute.

| sprite | used by |
|---|---|
| `APPROVED/hands/h1.png` | knuckles / back of hand — walk + run, the **near** hand |
| `APPROVED/hands/h2.png` | palm — walk + run, the **far** hand (dimmed, drawn behind the body) |
| `APPROVED/hands/h3.png` | profile — walking **toward or away** from the camera |
| `bronze/hands/grip_*.png` | **swings only** |

These are bronze's, and **every other outfit's gauntlet was generated from them**, so a non-bronze outfit
uses its own gauntlet in the same three roles: `front`→h1, `back`→h2, `side`→h3.

`1_APPROVED_vs_NOW.png` — top row is the approved reference, bottom is the current render. The hands now
match.

## Also fixed: copper and farmer faced left

Everything downstream assumes the side row faces right — the near hand swings to `+x`, every swing arcs
toward `+x` — so those two walked and swung backwards. Mirrored with `flip_side.py`. They were the only
two of 22; see `2_facing_audit_all_22.png` and `3_facing_heads_zoomed.png` (the face, visor slit or hat
brim points the way they face).

**Do not automate the facing check.** A centroid heuristic agreed with a careful visual read on only 6 of
8 outfits, and a detector wrong a quarter of the time would mirror sprites the wrong way, silently.
