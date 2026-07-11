# Crafting/gathering station minigames — taxonomy & the big design signal

*Topic 3 of the 2026-07 research. Synthesized from deep-read sources (5 full pages fetched + corroborating
search). Raw transcript: `../_raw_recovered/minigames/a551e666a97947f00.md`.*

## The single most important finding (read this before proposing anything)
> **In nearly every farming/processing sim, the crafting/processing stations are PASSIVE TIMERS, not minigames.**
> The real skill-check minigames are concentrated in **fishing** (a catch-bar or click-to-stop) and in
> **occasional cooking contests** — almost never in machine processing (kegs, furnaces, looms).

Players actively **resent forced per-item interaction** on processing: the mod ecosystems prove it —
Coral Island *"Instant Processing,"* Sun Haven *"No Time For Fishing,"* and My Time at Portia's most-cited
thread is literally *"Why does everything have a timer? Feels like a mobile game."* **If we add a mandatory
minigame to every processing action, we should expect that backlash.** The genre's answer is the opposite:
routine processing stays passive/automatic; the skill minigame is an **opt-in, occasional, bonus-bearing**
layer.

## Source table (URLs actually fetched → mechanic → fields)

| Source (fetched) | Game / feature | Verb | Input | Loop | Reward | Skippable? | Player gripes |
|---|---|---|---|---|---|---|---|
| carlsguides.com/stardewvalley/fishing | **Stardew — fishing bar** | reel / keep-in-box | **feathered hold** of one button (hold→green bar rises, release→falls); keep the moving box over the fish | a few sec/fish; catch-meter fills while in-box, drains while out | catch + **"Perfect!"** quality/score flag; higher level enlarges the box | not auto-skippable (level/tackle only *ease* it) | fish move erratically, bounce & trick you |
| carlsguides (kegs/looms) + forum | **Stardew — kegs/casks/jars/looms** | insert → wait | **none (passive)** | days-long timer | deterministic quality/value uplift; no perfect, no skill | fully passive; "skill" = scheduling | tedium is *quantity management*, not the machine |
| sunhaven.wiki.gg/wiki/Fishing | **Sun Haven — fishing** | click-to-stop | **single click** when a moving marker hits the zone; inner **sweet spot** = perfect | one short timing check/fish | **Perfect = +30% XP**; zone shrinks with rarity; miss = still catch | not auto (a "No Time For Fishing" mod exists *because* it's forced) | — (cheapest, least-fatiguing primitive) |
| thecookbooktest / steam guides | **Dave the Diver — normal cooking** | plate & serve | **automatic** (staff cook) | real-time service | money from menu/pricing, not cooking skill | cooking itself isn't a skill gate | focus is management |
| steamcommunity cook-off threads | **Dave the Diver — cook-off contests** | chop / coat / stir / mix / rotate | on-screen prompts; **circular mouse motion**, drag-to-cover | multiple tight timed tasks/dish | **score-based, partial credit** (92 despite a fumbled step) | occasional event, retry to pass | "artificial difficulty spike," "poorly implemented," rotation finicky on controller |
| *(search, med-confidence)* | **Graveyard Keeper** | hold-F at station | passive + **star/probability** (ingredient quality + tech) | wait | RNG quality tiers, not dexterity | one-at-a-time for high tiers | sitting & waiting per item |
| *(search, med-confidence)* | **Portia / Sandrock / Coral Island** | feed materials → wait | passive fueled timers; Sandrock/Coral add **auto-assemble/Auto-Chest** | timers | deterministic | **auto at high tier** | "feels like a mobile game" (the timer backlash) |

## The two proven, low-fatigue primitives (the ones to reuse)
1. **Catch-bar / keep-in-zone** (Stardew fishing): one-button **feathered hold**, a continuous meter that
   fills while a moving target stays inside a moving box, drains while out. Difficulty via **erratic target
   motion**; mastery via a **growing tolerance zone**. Reward = success + a "Perfect" flag. *More engaging,
   slightly more effort to build, ~a few seconds — too long to repeat 100×/day if mandatory.*
2. **Click-to-stop timing gate** (Sun Haven): a single well-timed **click** on a moving marker, with nested
   **good / perfect** zones; rarity/quality shrinks the zone. Reward = a flat **perfect bonus (+30%)**, miss =
   still succeed. **Cheapest to build, least fatiguing per rep — the best fit for a short check that repeats
   often.** This is the recommended default primitive.

## The reward model that works (critical)
Every successful design gives a **bonus on perfect and NO real penalty on "just okay," and never destroys the
input.** Sun Haven +30% XP for the sweet spot (miss → still catch); Dave the Diver contests give **partial
credit**; Stardew "Perfect" is a quality/score flag. **Lesson for a processing minigame: perfect =
speed/quality/yield bonus; average = normal result; you never lose the ingredients.**

## ≥4 scored minigame families (which to reuse)
Axes: **fun-per-second · low-fatigue on repetition · dev cost/simplicity · fits crafting flow + multiplayer** (1–5).

| Family | Fun/sec | Low-fatigue | Dev cost | Flow/MP fit | Verdict |
|---|:--:|:--:|:--:|:--:|---|
| **Click-to-stop timing gate** (Sun Haven) | 3 | 5 | 5 | 5 | **PICK #1 — the default.** One click, bonus-not-gate, trivially client-side, near-zero fatigue. |
| **Feathered-hold catch-bar** (Stardew) | 4 | 3 | 3 | 4 | **PICK #2 — for "special"/hero crafts only.** More engaging but too long to force every rep. |
| **Balance/temperature gauge** (keep a needle in a band while it drifts) | 3 | 3 | 4 | 4 | Keep as a *themed variant* of #1 for forge/cook; don't build a third input scheme if #1 covers it. |
| Multi-step prompt sequence / rotation (Dave the Diver cook-off) | 4 | 1 | 2 | 2 | REJECT for routine use — the single most-criticized one (finicky, controller-hostile). Reserve for a rare *contest event*. |
| Mash / QTE spam | 1 | 1 | 5 | 3 | REJECT — fatiguing and unloved. |

## Anti-fatigue design rules (non-negotiable)
- **Routine processing stays passive/automatic; the minigame is opt-in and bonus-bearing**, not a per-item tax.
- **Perfect = bonus (speed/quality/yield); average = normal; failure never loses the input.**
- **Keep it ≤ a couple seconds** and one simple input (avoid circular-rotation-on-controller).
- **Build the skip/automation path from day one** (every game here auto-completes at high tier or has a de-minigame mod).
- **Novelty caution:** pan/mash/thread/spin as *active* checks are **absent from the genre's processing** — building them is genuinely novel, but the evidence says frame them as *perfect-bonus* checks, not mandatory taxes.

## Open questions (owner taste — not guessed)
1. **Reward axis — quality is ruled out by the data.** Verified 2026-07-11: our economy has **no quality/tier
   axis** on items or recipe outputs (only `process_ticks` speed + fixed I/O). So "perfect = quality" can't
   land without a new economy feature; the free options are **+speed or +yield**. Which do you want — or is a
   quality system worth building?
2. **Mandatory or opt-in?** Given the strong genre signal, my recommendation is opt-in-for-bonus. Do you agree, or do you want at least *some* stations to require the minigame for flavour?
3. **How often will a player hit each station?** High-frequency stations (furnace, workbench) argue hardest for the cheap click-to-stop or full automation; low-frequency "hero" crafts can afford the richer catch-bar.
