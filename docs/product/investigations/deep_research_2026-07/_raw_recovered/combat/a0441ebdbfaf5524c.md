Fandom returned 402 (blocked). The L4D PDF was saved locally. Let me extract it with Python and fetch alternate sources for threat and Arkham.

---

PDF extraction produced nothing (no pdf lib). Let me fetch a proper L4D article, the numbers-rich GitHub threat wiki, and try the Booth PDF another way.

---

fitz/pypdf are available. Let me extract the Booth L4D PDF text locally.

---

I have the L4D deck. Let me read the pacing-specific portion (the Dramatic Pacing section).

---

Strong L4D primary source captured. Let me deep-read one solid Arkham technical source to firm up that row.

---

API Error: Server is temporarily limiting requests (not your usage limit) · Rate limited

---

Let me grab the authoritative Game Developer Arkham analysis to firm up that row, then emit the report.

---

I have four solid deep-read sources plus corroborating Arkham numbers. Let me send the report to the peer that requested it, then emit my final report.

---

The peer address isn't reachable, so I'll deliver the report as my final message (which the requesting session reads directly).

---

# Enemy Aggression Pacing & Threat Management — Deep-Read Source Table

4 sources fetched full-text. Fandom wiki pages (Wowpedia Threat, Arkham Freeflow) returned HTTP 402 and are excluded from deep-read rows; where I lean on a search snippet I flag it explicitly.

## ROW 1 — Left 4 Dead "AI Director" (PRIMARY, full 95-slide deck deep-read)
**URL:** https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf ("The AI Systems of Left 4 Dead", Michael Booth, Valve — extracted full text locally)

**Technique:** Adaptive Dramatic Pacing. The Director tracks a per-Survivor "emotional intensity" scalar and modulates the *population* of enemies (not their strength) through a 4-phase cycle.

**Concrete numbers / verbatim rules:**
- Intensity RISES: when injured (∝ damage taken), on incapacitation, when pulled/pushed off a ledge, and when a nearby Infected dies (∝ inverse distance).
- Intensity DECAYS toward zero over time — but does NOT decay while Infected are actively engaging the Survivor.
- Director tracks the MAX intensity across all 4 Survivors.
- Cycle: **Build Up** (full threat pop until intensity crosses peak threshold) → **Sustain Peak** (hold full pop **3–5 seconds** after peak; guarantees a minimum build-up) → **Peak Fade** (drop to minimal pop, wait for a natural lull) → **Relax** (minimal pop for **30–45 seconds**, or until Survivors travel far enough toward the next safe room, then resume Build Up).
- Relax pop = "No Wanderers until team is calm, No Mobs, No Special Infected (existing Specials may still attack)."
- **75% of mobs spawn BEHIND** the team (at/behind the team's "flow" distance).
- Thesis, verbatim: "Algorithm adjusts pacing, not difficulty — **Amplitude (difficulty) is not changed, frequency (pacing) is.**" "Constant unchanging combat is fatiguing; long periods of inactivity are boring."
- Boss encounters are exempt from adaptive pacing (they intentionally break the rhythm).

**Map to bug swarm:** Give each player/zone a deterministic intensity accumulator (rises with bites taken + nearby bug deaths, decays only when no bug is engaging). Run a Build-Up → Sustain(3–5s) → Fade → Relax(30–45s) valve on the swarm director: at peak pressure, STOP committing new bugs to the attack and let the current cluster resolve — never make bugs stronger. Keep per-bite damage fixed; vary frequency. Bring reinforcements in from off-screen edges so pressure is directional, not a teleport pile-on. Decay-only-when-disengaged blocks cheesing yet guarantees a breather after every real fight.

## ROW 2 — "Attack token" enemy-AI convention (Ask a Game Dev, full post deep-read)
**URL:** https://askagamedev.tumblr.com/post/620010728353595392/when-designing-non-boss-enemy-ai-ie-ai-for

**Technique:** Only an AI holding an "attack token" may attack; after finishing it passes the token to another. Tokenless enemies still crowd, wander, and make scary noises to look threatening but cannot deal damage.

**Numbers:** No hard counts given, but token COUNT is the difficulty knob — 1 token = one attacker at a time; "in more challenging battles we might want more than one active attack token." Intent, verbatim: "This keeps the relative threat to the player at any given time controlled, **rather than constantly scaling with the number of enemies.**"

**Map to bug swarm:** The single most transferable mechanic. Give the swarm a small deterministic pool of "bite tokens" per player (e.g. 1–2, scaled by a fairness setting). Only token-holders may execute a damaging lunge; the other 30 bugs still swarm/crawl/menace (the scary part) but can't all bite at once. Token passes on a fixed cooldown after each bite. This decouples visible density (cozy-scary) from actual DPS (fair, capped) — the core of "threatening but not an unavoidable pile-on." Integer pool + fixed cooldowns = deterministic/sync-safe.

## ROW 3 — WoW threat/aggro tables (magey/classic-warrior wiki, full deep-read; corroborated by Wowhead/Warcraft Tavern search)
**URL:** https://github.com/magey/classic-warrior/wiki/Threat-Mechanics

**Technique:** Per-NPC threat TABLE — every action adds threat points; the NPC attacks whoever tops its table, with positional hysteresis to prevent flip-flopping.

**Numbers / verbatim:**
- **1 damage = 1 threat; 1 healing = 0.5 threat.**
- Steal aggro by exceeding the current target's threat by **10% at MELEE range, 30% at RANGED range** (the hysteresis band — "once someone has aggro it's easier to keep it").
- Stance multipliers: Battle/Berserker **0.8×**, Defensive Stance **1.3×**, +Defiance talent **1.15×** (multiplicative ≈ **1.495×**). Example ability threat values: Shield Slam R4 = 254, Revenge R6 = 270 (2.25× mult), Cleave = 100 bonus/target.
- Taunt = set your threat equal to the current top target's (forces swap). Aggro lost by leaving leash range, dying, or a drop-combat ability (feign death).
- (Search snippet only, NOT in a fetched primary: tank passive threat grew to ~5× by Cataclysm — flagged unverified.)

**Map to bug swarm:** A threat table gives cheap, fair, deterministic TARGET ARBITRATION: which bugs pick the player vs. a crop / lure / scarecrow / torch. Model aggro as an integer accumulator per (bug, target); movement/damage/light add threat; use the 10%/30% hysteresis so a placed LURE (a threat magnet = the "taunt"/"tank" of a cozy game) peels part of the swarm off the player without instant flip-flopping. Aggro radius + leash range = bugs only wake within R cells and give up past a leash distance, so retreating is always a valid escape (the fairness valve). Turns a blind pile-on into a system the player out-plays with placement. All integer accumulators → sync-safe.

## ROW 4 — Batman: Arkham free-flow combat / combat ring (Fandom 402'd; pieced from fetchable analyses + search)
**URLs read:** https://medium.com/@paple124/the-batman-arkham-combat-problem-7a95b90b5857 (full) and https://www.gamedeveloper.com/design/batman-arkham-design-analysis-part-1- (full). Simultaneous-attacker cap is search-snippet corroboration only.

**Technique:** Enemies surround Batman in a ring but only a limited number strike at once; every incoming attack is telegraphed and answered with a single-button counter (a "dance-like rhythm"). Damaging animations are protected so the player isn't robbed mid-flourish.

**Numbers / specifics:**
- "No more than 3 enemies attack at the same time" — **search-snippet only, could not confirm in a fetched primary; treat as ~2–3, directional.**
- Each attacker shows a visual telegraph (blue crackle/indicator above the head on normal; **removed on Hard** to raise the skill ceiling — search, not primary).
- You tap counter once PER simultaneous attacker.
- **Verified in the Game Developer analysis:** instant-takedown animations grant invulnerability ("other enemies will not attack you during the animation") to avoid the bad feel of losing an earned takedown; but ground takedowns are interruptible ("the closest enemy will always go to hit you and cancel the takedown") — a deliberate risk/reward asymmetry.

**Map to bug swarm:** (1) TELEGRAPH every commit-to-bite — a token-holding bug winding up to lunge flashes a clear tell (rear-up / antenna flare / tint) with a fixed few-frame windup, so a swarm bite is always dodgeable/parryable; a net or spear sweep in that window is the "counter." This is what makes it FAIR vs. a random-damage cloud. (2) Protect the player's committed actions — while mid-swing or mid-net-throw, bites are blocked or queued so the player is never stunlocked out of their own attack. Cap concurrent *winding-up* bugs (the Row 2 token pool IS this cap) to ~1–3 so tells stay readable.

---

## Synthesis — keeping a deterministic bug swarm threatening but FAIR
All four sources converge on one principle: **decouple how dangerous a swarm LOOKS from how much it can actually HURT per unit time, and vary FREQUENCY not damage.**

1. **Bite-token pool (Row 2)** — a small counted integer pool caps simultaneous damaging bugs regardless of on-screen density. Scary density, bounded DPS. Integer + cooldowns → deterministic.
2. **Telegraphed, counterable bites (Row 4)** — every lunge has a fixed windup tell (always avoidable with correct play); protect the player's own attack animations from stunlock.
3. **Intensity population valve (Row 1)** — per-player intensity rises with bites/nearby deaths, decays only when disengaged; Build-Up/Sustain(3–5s)/Fade/Relax(30–45s) eases the swarm off after every real fight. Change frequency, keep per-bite damage fixed.
4. **Threat-table arbitration + aggro radius/leash (Row 3)** — deterministic per-target aggro with 10%/30% hysteresis lets lures/torches peel the swarm (the cozy "taunt"); a leash/aggro radius guarantees the player can always retreat. Integer accumulators → sync-safe.

Every mechanic is integer/counter/timer based, so all four fit a deterministic ledger sim with no floats.

**Could-not-verify (search snippets only, Fandom pages 402'd):** WoW "~5× tank multiplier by Cataclysm"; Arkham "max 3 simultaneous attackers" and "indicator removed on Hard"; the exact token counts in Row 2 (the author gave none). Everything from the L4D Booth PDF and the classic-warrior threat wiki is fully deep-read primary text.