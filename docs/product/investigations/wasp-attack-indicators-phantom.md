# Investigation+Design: #20 phantom wasp attack + attack/feeding indicators
_status: BUILT 2026-06-30 (#20 shipped) — see AS-BUILT below · investigated 2026-06-28_

> **AS-BUILT (2026-06-30 — differs from the design below; the design is kept for the record):**
> (1) **LOS is CLIENT-side**, not server — the authority's `RunPredationStrikes` narrow-phase skips prey occluded by
> the zone-wide collision map via an integer-Bresenham `BugCollision.LineBlocked`. Chosen for per-individual precision
> (the server holds only swarm CENTRES, so a server LOS could only be centre-approximate). Predators now strike
> *around* a bin instead of whiffing.
> (2) **The corpse is a CLIENT VISUAL** (`StrikeVfx`, *consumed*: pops in → holds for the feed → fades), NOT a server
> `spawnCarcass` ground item — so it adds **no** carrion/ecology load (ecology-neutral, per the user's "Consumed" choice).
> (3) **The feeding pause IS the determinism change** — `FeedUntilTick` + a per-species `feed_pause_ticks` (wasp 50t,
> centipede 30t ≤ each one's strike cooldown → rate-neutral). The predator parks via a zero-length hold-leg on the
> *existing* `SWARM_SET_TARGET` event (no new event type). Gated: Go feed-pause tests + sim-determinism + the
> 2-client sync gate. (The lunge + corpse-pop + THWACK cover the attack-indicator ask; the predator→victim dart was
> deferred as optional.)

## Debrief (read me first)
- **Phantom attack — cause:** `applyPredationStrike` selects/strikes prey by **distance only — no
  line-of-sight check** (the snippet has range + satiation + telegraph, no `isBlocked`/LOS). So a predator
  within `strike_radius` but **behind a blocking occupant (the compost bin you placed)** still kills the fly;
  the strike telegraph (display-only flash/THWACK) plays AT the dead fly, while the attacker sits occluded /
  "stuck" on the far side → you see a death with no visible attacker. Matches your guess exactly.
- **Why attacks "barely show":** the kill is instant — `predator.Satiation += FeedPerKill` on the same tick
  (`:27`), then the predator immediately hunts again; the only tell is the lunge + a telegraph flash. No
  feeding beat, no corpse (predation skips `spawnCarcass`, see #22).
- **Design (what you asked to plan):** (A) a real **attack indicator** (lunge + impact + connecting dart) —
  display-only; (B) **corpse-on-kill + a feeding pause** — the predator parks on the spawned corpse and feeds
  over N ticks before hunting again (visible + prevents instant re-hunt) — this is a **sim/determinism change**
  (`frontier-sync` + the determinism gate).
- **Certainty:** phantom mechanism **80%** (LOS absence verified; "is it what you hit" needs a live repro) ·
  design is a proposal. **Needs your decision:** approve the feeding-pause sim change + LOS check? **Status:** `READY`.

## 1. Issue
> "phantom wasp attack … saw wasps but not the attacking one … one wasp stuck … maybe behind a compost bin within attack range. … wasps … just kinda move forward a little, there needs to be … indicators … when they kill a fly the corpse appears while the hornet feeds on it over a short amount of time … same with other bugs. plan that out."

## 2. What's there now (verified)
- Strike: `predation.go applyPredationStrike` — sets `LastStrikeTick`, `Satiation += FeedPerKill` (instant),
  broadcasts `broadcastBugStrikeTelegraph` (display-only flash/THWACK at victim positions). No LOS, no feeding
  state, no carcass on predation (`killBugsInSwarm` → `spawnKillDrops` only).
- Client: `SwarmManager.RunPredationStrikes` (authority) picks nearest prey within `strike_radius`; the visual
  is the small lunge + the telegraph flash.

## 3. Design

### A. Attack indicator (display-only — NO determinism)
On a strike telegraph: (1) a committed **lunge** of the predator individual toward the victim (bigger than the
current "move forward a little"), (2) an **impact** flash/pop at the victim cell, (3) optionally a short
**dart/streak** from predator→victim so the attacker is identifiable even at the screen edge. Enrich
`broadcastBugStrikeTelegraph` (already carries victim positions) + the client `RunPredationStrikes`/telegraph
handler. Free of sim impact.

### B. Corpse + feeding pause (SIM change → frontier-sync + determinism gate)
1. **Corpse on kill:** add `spawnCarcass` to the predation kill (`killBugsInSwarm`) — the fly corpse appears at
   the kill (ties #22). Carcass already rides the ground-item ledger.
2. **Feeding state:** give the predator a `Feeding{untilTick, corpseRef}` state — on a kill it enters Feeding
   for N ticks (e.g. 2–4s): it parks on/near the corpse, does NOT hunt, and satiation rises over the duration
   (replace the instant `+= FeedPerKill` with a per-tick drain-of-corpse). After `untilTick`, resume hunting.
   This (a) makes the attacker park visibly at the corpse (also fixes the phantom — the predator is now ON the
   visible corpse), (b) paces predation, (c) reads as "feeding."
3. **LOS for the strike (the phantom proper):** add a blocks-bugs line-of-sight check to strike selection so a
   predator can't kill through a wall/compost bin. (Or accept it and rely on the feeding-park to make the
   attacker visible — decide.)
4. **Generalize** to all predators (wasp/hornet/centipede) via species params (`feed_secs`, `requires_los`).
- **Determinism:** B changes hunt timing + which strikes land + the carcass food supply → all sim inputs.
  Wire via `frontier-sync` (the strike is already authority/ledger), then `tools/sim-determinism` + the
  sync-harness + an `ecology-tuning` band re-check (slower predation + more carrion shifts the food web).

## 4. Recommendation
Do **A** now (cheap, high readability win, no risk). Schedule **B** as a small `frontier-sync` feature
(corpse + feeding-pause + optional LOS) — it simultaneously fixes the phantom (predator parks on the visible
corpse), gives the feeding beat you want, and feeds the decomposer loop. Gate B with determinism + ecology.
