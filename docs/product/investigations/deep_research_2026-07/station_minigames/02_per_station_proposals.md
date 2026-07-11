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
  (bonus output). (Open question — see below. The proposals assume a generic "bonus tier".)
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
- **Reward:** faster smelt or a "refined" bar tier. **Skip path:** an upgraded furnace auto-holds heat.

### **anvil** → P1 click-to-stop ("strike") — the classic blacksmith beat
- **Verb:** the hammer sweeps over the anvil; click when it's over the glowing sweet spot. 2–3 strikes per item.
- **Reward:** perfect strikes → higher-quality tool/part. **Skip:** power hammer upgrade auto-strikes.

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
1. **What does "perfect" reward — quality, speed, or yield?** Needs an answer before building (the economy may not even have a quality axis yet). This is the load-bearing decision.
2. **Opt-in bonus vs. mandatory?** Recommendation (from the taxonomy evidence): opt-in-for-bonus, never mandatory. Confirm.
3. **Which stations deserve the effort first?** Suggest starting with the ones where a skill check feels *earned* and iconic — **anvil (strike)**, **gem_cutter (precision)**, **dye_vat (match shade)** — rather than all 15 at once.
4. **Multiplayer griefing/AFK:** should a co-op partner be able to do the minigame for your craft? (Client-result model allows it; just decide the rule.)
