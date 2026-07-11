# Per-station minigame proposals

*Topic 3 of the 2026-07 research. Applies the two proven primitives from `01_minigame_taxonomy.md` to
BugFarmer's 15 stations. Grounded in the taxonomy's hard rules: **routine processing stays passive; the
minigame is opt-in and bonus-bearing; perfect = bonus, average = normal, you never lose the input; ≤3
shared primitives; build a skip/automation path.** Additional raw research: `../_raw_recovered/minigames/`.*

## Design frame (before the per-station list)
- **The genre signal is real** — do NOT gate every craft behind a dexterity check (the "mobile-game timer"
  backlash). Recommendation: a craft **auto-completes passively as today**, and pressing the action button
  at the right moment during the (short) craft grants a **bonus tier**. Ignore it → you still get the item.
- **One reward axis, chosen by the owner:** perfect → **+quality**, **+speed** (finish now), or **+yield**
  (bonus output). **VERIFIED against our data (2026-07-11):** there is **no quality/tier/grade axis** on items
  or recipe outputs today — `recipes.json` outputs are fixed I/O with only `process_ticks` (a speed knob);
  `tool_tier` is a *gating* tier, not output quality. **So "perfect = quality" has nowhere to land right now.**
  Default the reward to **+speed (reduce `process_ticks`) or +yield (bonus output count)** — both fit the
  existing economy with zero new systems. A quality axis is possible but is a *separate, larger* economy
  feature (new item field + everywhere that reads/sells items), not a minigame prerequisite.
- **Three shared primitives only**, reused across all 15 stations (never 15 bespoke systems):
  - **P1 — Click-to-stop** (Sun Haven): one click on a moving marker; nested good/perfect zones; rarity/tier
    shrinks the zone. *Default for most stations. Cheapest, least fatiguing.*
  - **P2 — Balance band** (keep a drifting needle inside a moving band for ~2 s via taps/hold): themed as
    heat/spin/stir. *For the "sustained process" stations (forge, cook, honey).*
  - **P3 — Feathered-hold catch-bar** (Stardew): the richer ~few-second bar. *Hero/rare crafts ONLY* — too
    long to repeat every rep.
- **Netcode:** the minigame is a **client-side skill check**; its *result* (a bonus tier 0–2) is sent with the
  craft request. Crafting output stays **server-authoritative** — the server runs the craft and applies the
  tier (clamped to a legal range so a hacked client can't send "always perfect" beyond the cap). The minigame
  never touches the deterministic bug sim; it's cosmetic-to-sim, like the shovel's client swing.

## The stations

### Smelting & metal — **forge, furnace** → P2 balance band ("heat")
- **Verb:** manage the heat. A temperature needle drifts; tap to pump the bellows and keep it in the glowing
  band for the smelt. Perfect = the whole smelt stayed in-band.
- **Reward:** faster smelt (−`process_ticks`) or bonus bars (+yield); **never a quality tier** (no quality axis
  — see 01). **Skip path:** an upgraded furnace auto-holds heat.
- **See the richer, genre-grounded version below** → *"Blacksmith-genre deep-dive (anvil + forge)."*

### **anvil** → P1 click-to-stop ("strike") — the classic blacksmith beat
- **Verb:** the hammer sweeps over the anvil; click when it's over the glowing sweet spot. 2–3 strikes per item.
- **Reward:** perfect strikes → faster finish (−`process_ticks`) or a bonus part (+yield); **not "quality"**
  (no quality axis). **Skip:** power hammer upgrade auto-strikes.
- **See the richer, genre-grounded version below** → *"Blacksmith-genre deep-dive (anvil + forge)."*

### Blacksmith-genre deep-dive (anvil + forge)
*Supplement — the farming-sim taxonomy (01) under-covered the dedicated smithing genre, whose whole loop is
exactly our forge=heat + anvil=strike pair. Deep-read 2026-07-11 (6 full sources). It confirms our two
primitives are the right ones and hands us concrete tuning + a fatigue trap to avoid — but every one of these
games rewards **quality/durability/stat tiers**, which we don't have, so we translate that reward to
**+speed / +yield** throughout (per 01's verified constraint).*

**Source table (all fetched & read):**

| Game (source) | Verb | Input | Loop | Reward (theirs → ours) | Gripes / lessons |
|---|---|---|---|---|---|
| **Kynseed** — Steam guide 2940467589 + wiki | heat-then-hammer | LMB to pull metal at the **green (+15) / yellow (+10) marker** on a moving scale; then LMB to **cover a target**, hits = your **Strength** stat, **Perfect+10/Good+5/OK+2/MISS=penalty** | 2 phases/item: time the pull, then N strikes | durability tiers → **our +speed/+yield** | zones shrink & scales oscillate with better ore; **Strength-paradox: extra swings AFTER the goal waste time or *lose* durability on a miss** → *end the check at the goal, never force extra reps*; higher ore = harder for same reward (perverse) → *reward must scale WITH the difficulty tier*; timer never pauses |
| **The Forge** — forge.wiki guide | pump → pour → hammer | **bellows**: quick up/down to fill; **pour**: keep white indicator in a **moving yellow zone**; **hammer**: click when **outer ring overlaps inner ring = "Perfect"** | 3 short phases, rhythm-driven | Broken→Masterwork **(+20–30% stats)** → **our +speed/+yield** | clean split: pour = **our P2 balance-band**, hammer = **our P1 click-to-stop**; "focus on rhythm; visual/audio cues" |
| **Fantasy Blacksmith** — gameslushpile review | strike the ingot | timed hammer taps (not mash); **thermometer**; metal **cools and must be reheated** mid-forge; "hammer till done, **not too much or it goes bad**" | reheat↔strike cycle/item, then sell | reputation/gold → n/a (we don't sell-craft) | *"the repetition sets in"*; *"would have worked better as a mini game in another game than as a game in itself"* → **great as a garnish, fatal as the whole loop** — vindicates opt-in |
| **Wartales** — Steam disc. 6222…790 | strike on cue | **click the instant the plate turns white** — near **frame-perfect**; even perfect ≈ only 20% at max | repeat per item | armor-stat odds → n/a | *"has to be like a single frame,"* *"I don't play games in this genre to have my twitch reflexes tested,"* save-scumming, stutter ruins it → **avoid a punishing single-frame window; use generous nested good/perfect zones; never make failure destroy the input (kills save-scum incentive)** |
| **Blacksmith Simulator** — Impulse Gamer review | full physical sim | smelt→heat→**hammer to shape**→quench→fit guard/handle/pommel→sharpen | many manual steps/item | quality → n/a | mostly-negative; paywalled forge upgrades + soft-lock bugs; **too many mandatory steps per item** → *don't chain a 5-step tax onto every bar* |
| **My Time at Sandrock** — wiki/forums | (none) | Forging Machine is a **passive automated station** — no forge minigame at all | queue → wait | — | the biggest modern crafting sim keeps smithing **passive** → reinforces 01's "processing is a timer" default; a minigame here is strictly the opt-in bonus layer |

**Richer forge (heat management) — P2 balance band, refined by the genre:**
- **Verb:** while a bar smelts, a **heat needle drifts** on a vertical gauge; **tap to pump the bellows** (nudges
  it up; it cools between taps). Keep it inside the **glowing work-band** (nested **good / perfect** sub-bands, à la
  The Forge's pour + Kynseed's green/yellow). A short **~2 s** check, not the whole smelt.
- **Both edges are live** (the genre's real texture): drift **too cold** *or* **overheat past the band** both leave
  the band — but per 01, leaving it just yields the **normal** result, it never scorches/destroys the bar.
- **Difficulty (opt-in, cosmetic-to-sim):** rarer ore → **narrower band + faster drift** (Kynseed/The Forge). It only
  changes how much bonus is on offer, never the base output.
- **Reward:** all-in-band smelt → **−`process_ticks` (finish sooner)** or **+1 bar (yield)** — owner picks the axis
  (01 Q1). **Skip path:** an upgraded/automated furnace **auto-holds heat** (Sandrock-style passive).

**Richer anvil (strike timing) — P1 click-to-stop, refined by the genre:**
- **Verb:** a **short chain of 2–3 strikes**. Each strike a marker sweeps the anvil face; **click on the glowing
  sweet spot** (nested good/perfect), the classic beat that Kynseed, The Forge and Wartales all use.
- **Anti-Wartales rule (load-bearing):** the perfect zone is **generous and clearly telegraphed**, *not* a single
  frame — Wartales' frame-perfect window is the #1 gripe of the genre and turns a garnish into a chore.
- **Anti-Kynseed rule (load-bearing):** the strike chain is **fixed-length and ends at the goal** — never bolt on
  "extra swings" that waste time or (their bug) *subtract* on a late miss. A missed strike in ours = **that strike
  just doesn't earn the bonus**; you still get the item.
- **Reward:** all strikes perfect → **−`process_ticks`** or **+yield** (a bonus part). Partial credit like Dave-the-
  Diver: 2/3 perfect = 2/3 of the bonus, **input never lost**. **Skip:** power-hammer upgrade auto-strikes.

**Optional forge→anvil chaining (owner call, below):** the dedicated genre runs these as *one* loop — heat the bar
at the forge, then strike it at the anvil while it's hot — which is why they feel iconic together. We *can* wire the
forge's heat result as a small **carry-over bonus** into an immediately-following anvil strike (hot metal = wider
strike window), or keep the two stations fully independent. Both fit the primitives; it's a feel choice (Q5).

**Owner questions this genre surfaces (add to 01/02's list):**
5. **Chain the two, or keep them independent?** Dedicated smithing games make forge→anvil one continuous
   heat-then-strike loop (their signature feel). Do you want that linkage (forge heat carries a bonus into the anvil
   strike) — richer but couples two stations — or two independent opt-in checks that are simpler and reusable?
6. **Strike count: 1 or 2–3?** A single strike is the cheapest, least-fatiguing rep (01's default); a 2–3 strike
   chain reads far more like real smithing (Kynseed/The Forge) at some added time-per-craft. Which cadence do you
   want on the anvil specifically (it can differ from the other P1 stations)?

### Wood — **sawmill** → P1 click-to-stop ("cut on the line")
- **Verb:** stop the moving saw on the marked cut line. Off = normal plank; perfect = an extra plank or a
  cleaner grade. **Skip:** automated mill.

### Textiles — **spinning_wheel, loom, sewing_machine** → P1 click-to-stop ("rhythm"), P3 for hero garments
- **Verb:** a repeating rhythm marker (spin → thread → weave); a couple of well-timed clicks keep the rhythm.
  Chain of 3 quick clicks feels like a loom's cadence without being a QTE spam.
- **Reward:** perfect rhythm → finer cloth / bonus length. **Hero garments** (rare recipes) use **P3** for a
  more involved make. **Skip:** motorized loom.

### **dye_vat** → P1 click-to-stop ("match the shade")
- **Verb:** a hue slider sweeps a gradient; stop it on the target-colour band. Great fit because dyeing is
  literally about hitting a colour. Perfect = truer/richer dye. **Skip:** measured-recipe upgrade.

### **gem_cutter** → P1 click-to-stop ("precision facet"), tightest zone
- **Verb:** the classic precision check — a fast marker on a **small** zone that **shrinks with gem rarity**.
  This is where a skill check feels *earned* (cutting a gem should be delicate).
- **Reward:** perfect cut → higher gem grade/value; a botch is still a cut gem (never lose the rough). **Skip:**
  laser cutter upgrade.

### Stone & ore — **stonecutter, rock_crusher, ore_sluice**
- **stonecutter** → **P1** "stop on the score line" (like the sawmill, for stone).
- **rock_crusher** → **P1** "time the crush" — one strike at peak.
- **ore_sluice** → **P2/pan variant:** a "pan" sweet-spot slides across the sluice; keep the pan over it to
  catch more flecks. This is the one genuinely novel verb (panning) and it *fits* sluicing. Perfect = bonus ore.
- **Skip:** upgraded machinery auto-processes.

### **honey_extractor** → P2 balance band ("keep the spin")
- **Verb:** crank/keep the centrifuge speed in the band for the spin. Perfect = more honey / less wax waste.
  **Skip:** motorized extractor.

### **bug_extractor** → P1 click-to-stop ("extraction")
- **Verb:** a precision stop as you extract essence/materials from a caught bug; rarer bugs → tighter zone.
  Perfect = bonus essence. **Skip:** auto-extractor.

### **workbench** → mostly PASSIVE + optional quick P1
- **Verb:** the highest-frequency station — do NOT tax it. Default passive/instant; an *optional* single
  click-to-stop grants a small speed bonus for players who want to engage. **Skip:** already effectively skippable.

### Cooking — **cauldron, cooking_pot** → P2 balance band ("stir/heat"), occasional P3 "feast" contest
- **Verb:** keep the heat/stir in the band while cooking (a gentle balance). For special **feast/festival**
  dishes, an occasional **P3** cook-off-style contest (kept simple — the Dave-the-Diver rotation was the
  most-criticized input, so avoid circular motion). Perfect = tastier food (better buff/value).
- **Skip:** recipe mastery auto-cooks staples.

## Shared-primitive summary (the whole system is 3 things)
| Primitive | Stations | Why |
|---|---|---|
| **P1 Click-to-stop** | anvil, sawmill, textiles(routine), dye_vat, gem_cutter, stonecutter, rock_crusher, bug_extractor, workbench(opt) | Cheapest, least fatiguing, one input; the default. |
| **P2 Balance band** | forge, furnace, honey_extractor, cauldron/cooking_pot, ore_sluice(pan) | For "sustained process" stations where holding a state reads right. |
| **P3 Catch-bar** | hero textile garments, feast cooking | Rich but long — rare crafts only. |

## ≥4 scored candidates for the SHARED-PRIMITIVE set
Axes: **fun/sec · anti-fatigue · dev cost · multiplayer-safe** (1–5).

| Option | Fun | Anti-fatigue | Dev | MP-safe | Verdict |
|---|:--:|:--:|:--:|:--:|---|
| **P1 + P2 + P3 (this proposal)** | 4 | 4 | 4 | 5 | **PICK.** Three reusable primitives cover all 15 stations; client-side result → server tier. |
| P1 only (one primitive everywhere) | 3 | 5 | 5 | 5 | Safe fallback if we want minimum build; loses per-station flavour. |
| Bespoke minigame per station | 5 | 2 | 1 | 3 | REJECT — 15 systems to build + balance; fatigue + maintenance nightmare. |
| No minigames, pure passive (status quo) | 2 | 5 | 5 | 5 | The genre norm; valid — but the owner asked for engagement, so P1-as-opt-in-bonus is the low-risk step up. |

## Open questions (owner taste — not guessed)
1. **What does "perfect" reward?** Now narrowed by the data check: **quality doesn't exist in our economy**, so
   it's **+speed vs +yield** (both drop in for free) — OR you decide to invest in a new **quality axis** (bigger
   scope). Which of the three? This is the load-bearing decision.
2. **Opt-in bonus vs. mandatory?** Recommendation (from the taxonomy evidence): opt-in-for-bonus, never mandatory. Confirm.
3. **Which stations deserve the effort first?** Suggest starting with the ones where a skill check feels *earned* and iconic — **anvil (strike)**, **gem_cutter (precision)**, **dye_vat (match shade)** — rather than all 15 at once.
4. **Multiplayer griefing/AFK:** should a co-op partner be able to do the minigame for your craft? (Client-result model allows it; just decide the rule.)
