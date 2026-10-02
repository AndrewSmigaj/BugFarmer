# The character sheet and perks: how other games show and balance stats

Research for the item system, 2026-10-02. Status: **complete**. Nothing here is decided: it is evidence and
recommendations for the owner to judge. The game is a prototype; numbers below are examples unless marked.

## What is being designed

Bug Farmer is a 2D top-down multiplayer sandbox set in 2126, where people have bred bugs giant. Players
farm, raise bugs like livestock, fish, mine, craft, build and explore zones that get more dangerous the
further out they go. The item system is being built on a character sheet, accepted as a starting point:

- **Six meters shown as dots**: Health, Stamina, Armor, Strength, Speed, Stealth (how close a bug gets
  before it notices you). You start partway up each; items add or remove dots; each is capped at ten.
- **Three protections** as percentages: Sting, Venom, Acid.
- **Standalone perks** in standard sizes (night vision, +30% planks at the sawmill, +1 net reach,
  faster dragging...).

Each kind of item has a job: one outfit worn whole (armor, protections, small meter shifts, 1-3 perks);
two accessory slots (perks only, the tools of a trade); one meal at a time (raises Health and Stamina,
better food more, often plus a boost); one timed potion at a time (a strong short change); tools (their
metal is their power); weapons (damage, speed, reach, one trait). These are guidelines: an item may
break the pattern when it makes sense.

This document answers: how should the sheet show meters, protections and perks; how should an item's
tooltip show what would change; how should timed effects show; how should stacking and caps work and
how is a cap shown; what standard perk sizes to use; and how to keep the sheet readable as the game grows.

Related earlier research (what items do, not how the sheet shows them):
`../research-2026-10-01/accessories-in-games.md` and `../research-2026-10-01/potions-and-sets-in-games.md`.

## Method

Sources were read in full, not taken from search snippets: wiki pages were fetched as raw page text through
each wiki's own interface; forum threads, developer announcements and documentation were read as whole pages;
open-source code was read from the projects' own repositories; interface screenshots were viewed at full size.
Each source's notes (the appendix, "Reading notes") say what was read and when.

Four search angles were used: **by technique** (pips versus numbers, stat breakdowns, comparison tooltips, caps
and diminishing returns, stacking rules), **by game** (16 games), **by interface write-up** (developer patch
notes, Blizzard's itemization post, a screenshot library, accessibility guidelines) and **by player complaint**
(Steam forum threads for Core Keeper and Grounded, and wiki notes about hidden numbers). Three open-source
projects (Veloren, Cataclysm: Dark Days Ahead, Luanti) show how stats, effects and stacking are stored.
Limits are listed in section 4.

Game terms are explained the first time they appear. Player quotes are from public forums; no one connected
with Bug Farmer is quoted.

**Words used in this document.** A **buff** is a temporary boost and a **debuff** a temporary drawback (both are
also called *effects*). A **pip** is one dot in a row of dots. A **tooltip** is the small box that appears when you
point at something. The **always-on display** (often called the HUD, "heads-up display") is what sits over the game
world while you play; the **sheet** is the character screen you open. A **cap** is the most a value can reach; to
**stack** is for two sources of the same bonus to add up. A **set bonus** is an extra effect for wearing every piece
of a matching armor set. A **modifier** is one stored bonus or penalty. A **crit** (critical hit) is an extra-strong
hit, and **affinity** is Monster Hunter's word for the chance of one. The **hotbar** is the row of quick-use slots.

## Summary: the five recommendations that matter most

1. **Meters: ten pips in a row, four pip states.** A plain pip for your starting amount, a filled pip in a
   second colour for bonus from worn gear, a ringed pip for bonus that will run out (meal or potion), an empty
   pip with a slash for a pip an item takes away. The exact number, what it means in the game ("bugs notice
   you at 6 tiles") and where each pip comes from are one hover away. (§2.1-2.3)
2. **Show the change before it happens.** Pointing at an outfit, accessory, meal or potion previews the
   result on the sheet itself (pips that would be gained or lost, perk lines marked + or −), and the item's
   tooltip lists only what changes. A meal or potion says what it would replace and how long that has left.
   (§2.8)
3. **Timed effects get two fixed sockets.** One for the meal, one for the potion, beside Health and Stamina:
   the item's icon, a ring that drains, minutes left, a small slow blink near the end, a faint outline when
   empty. Everything else goes in one short row whose frame shape says where it came from. (§2.9)
4. **Perks come in two kinds and standard sizes.** Either a yes-or-no "unlock" (night vision, "wasps ignore
   you") or a sized perk with exactly three published sizes. One sentence plus one exact number each, never
   vague words; the smallest size must be big enough to notice. (§2.6-2.7)
5. **One rule for stacking, one look for caps, and a frozen frame.** Each slot holds one item and the slots
   add up; meters stop at ten, protections stop at a visible cap below 100%, and any waste is shown
   ("+1 over"). The six meters and three protections never grow; new content adds perks; anything at its
   normal value is hidden; every line of text is generated from the same data that computes the value.
   (§2.5, §2.10, §2.11)

## 1. Source table

Source numbers (S1-S60) point to the reading notes at the end of this document. "Fit" is fit for Bug Farmer's
accepted sheet (six meters as dots capped at ten, three protections as percentages, standalone perks in standard
sizes, one outfit, two accessories, one meal, one potion).

| # | Source | Concrete technique | What it does for readability or balance | Fit for Bug Farmer |
|---|---|---|---|---|
| S1 | Minecraft wiki, *Health* | Ten heart icons with half steps; extra hearts from an effect drawn in yellow after the red ones; hearts shake when low, bounce while regenerating | Amount, bonus amount, danger and an active effect read without one number | **High** — the model for pip meters with a bonus colour |
| S2 | Minecraft wiki, *Armor* | Armor row drawn above health only while armor is worn; 4% per point, capped at 80%; a second value (toughness) has no indicator at all | A meter that appears only when it matters; a hard cap prevents immunity; the hidden value sends players to the wiki | **High** for contextual display and the cap; avoid hidden values |
| S3, S6 | Minecraft wiki, *Effect*, *Heads-up display* | Effect icons top-right, sooner-ending further left, flashing before they end; good effects top row, bad bottom; effects from a placed block outlined blue | Urgency and source at a glance | **High** |
| S3 | Minecraft wiki, *Effect* | The same effect never stacks with itself: higher level replaces lower, longer replaces shorter | Simple and exploit-proof | **High** for meals and potions |
| S4 | Minecraft wiki, *Attribute* | Every bonus is a named modifier (id, attribute, operation, amount); add, then add-percent-of-base, then multiply; clamp to min and max | Predictable maths; taking an item off removes exactly its bonus | **High** (data shape) |
| S5 | Minecraft wiki, *Tooltip* | "When on Head: +2 Armor"; good lines blue, bad red; "Slowness IV (0:20)" for timed effects | One grammar for every item line | **Medium-high** |
| S7 | Terraria wiki, *Defense* | Defense number inside a shield icon; hover says "Reduces hit damage by 10"; the shield's border colour shows the difficulty | Turns an abstract number into what it does | **High** |
| S8 | Terraria wiki, *Buffs* | Icons under the hotbar with time left under each; right-click cancels; one key drinks all buff potions; 44-effect limit | Timers always visible; a chore removed | **Medium** (Bug Farmer allows one potion) |
| S9 | Terraria wiki, *Accessories* | No duplicate accessories; accessories combine at a workbench into one item; random accessory bonuses are never negative | Slot count stays meaningful as items multiply | **Medium** |
| S10 | Terraria wiki, *Informational Accessories* | Readout gadgets (depth, fish finder, radar) work from the backpack, combine into one, grey out when not relevant, and share their readout with teammates within 50 tiles | Information as equipment; co-op sharing | **Medium-high** (trade gadgets) |
| S11 | Terraria wiki, *Armor* | "Set Bonus" line appears in the tooltip while the whole set is worn; job sets (mining set +20% + 10%) | Clear role sets; mixed sets are where depth and confusion live | **High** (whole outfits avoid the mixing) |
| S12 | Terraria wiki, *Well Fed* | Three food buffs change the same seven stats in fixed steps; only one active, the newest wins | Standard sizes; a stacking rule anyone can say in one sentence | **High** |
| S13 | Stardew wiki, *Buffs* | One food buff and one drink buff at a time; icon blinks before expiry; food tooltip shows duration; two display bugs fixed | Slot rule easy to learn; shows why text must come from data | **High** |
| S14, S15 | Stardew wiki, *Rings*, *Forge* | Two ring slots; some rings add up (listed ring by ring); a forge merges two rings into one (at most four effects in two slots; undoable) | A controlled ceiling on stacking | **Medium** |
| S16 | Valheim wiki, *Food* | Three food slots raise maximum health and stamina; the bonus fades on a curve; icon flashes when the slot can be refilled; a coloured fork on each food icon shows which meter it feeds | A meal's job is readable from its icon | **High** (fork colour for meals) |
| S17 | Valheim wiki, *Status effects* | Whole-set effects sit in the status row with no timer, "only while entire set is equipped"; sets carry drawbacks too | Worn effects visible alongside timed ones | **High** |
| S18 | Valheim wiki, *Resistance* | Resistances as named steps (Weak … Very resistant, Immune); sources do not add: the strongest wins | No arithmetic; one rule | **Medium** (considered for protections) |
| S19 | Valheim wiki, *Damage mechanics*, *Rested* | Armor "diminishing return" is fair in hits-to-death; Rested's +50% skill gain is missing from its description | Explains the "my armor does less" feeling; hidden effects get found and resented | **Medium** |
| S20 | Grounded wiki, *Armor* | Defense shown as a segmented bar, resistance as a percentage, minimum guaranteed damage hidden; light/medium/heavy trade damage reduction for stamina | Three display kinds in one game; a visible trade-off | **High** relevance: copy the bar and the trade-off, avoid the hidden rule |
| S21 | Grounded wiki, *Status Effects* | Named effect icons reused at many sizes (+Damage Resist 2% … 50%); vague in-game wording | Size cannot be read from the icon; players need the wiki | **Avoid** |
| S21 | Grounded wiki, *Status Effects* | Species perks: red ants treat you as one of them, aphids ignore you, wasps turn neutral but bees turn hostile | Big, readable yes-or-no perks with built-in costs | **Very high** (Stealth's natural companion) |
| S22 | Grounded wiki, *Mutations* | Perks earned by doing things, 2 → 5 slots, three phases in fixed steps, four saved loadouts | Steps are learnable; loadouts end swap chores | **Medium** |
| S23 | Grounded wiki, *Trinkets* | One trinket (accessory) slot only | Few slots keep perks scarce and readable | **Medium** |
| S25 | Grounded wiki, *Damage Types* | A dozen damage types and many matching resistances | Depth for combat fans, a lot to learn for everyone else | **Avoid** — three protections are enough |
| S24 | Grounded wiki, *Consumables* | Meal tiers: 12/16/20 minutes, ×1/×1.5/×2 regeneration, 1/1/2 effects | A food size table in one glance | **High** |
| G2a, G2b | Grounded 2 wiki, *Armor (Grounded 2)*, *Buggies* | Armor archetypes with a passive; bulky-or-sleek choice when upgrading; riding a buggy makes its species neutral; buggy skills cost stamina bars | Role identity; ranching meets stealth | **High** (closest premise) |
| S26-S29 | Core Keeper wiki + Steam forums | Per-piece stat lists with decimals; players unsure how food buffs stack four years on; movement speed missing from the stat screen; no compare until 2026 | Evidence of what goes wrong | **Avoid the gaps** |
| S28 | Core Keeper wiki, *Cooking* | Ingredient effects "are not shown in-game" | Wiki dependence | **Avoid** |
| S30-S32 | RimWorld wiki + Ludeon's translation files | Hover breakdown: Base value, Relevant gear, Health, multipliers, Final value; fixed order (add, multiply, clamp); stats hidden while at default | Every number explains itself; hundreds of stats stay readable | **Very high** |
| S33 | Necesse wiki, *Food* tiers | Simple / Fine / Gourmet, sub-tiers shown by the item name's colour | Named quality bands | **High** |
| S34 | Necesse wiki, *Buffs* | A scaling bonus's icon changes colour by size band (blue < 10%, green, purple, orange 40%+) | Strength at a glance | **Medium** |
| S35 | Necesse wiki, *Armor* | Late upgrades bring old sets to similar defense so the set bonus decides | Role outfits stay relevant | **Medium-high** |
| S36 | Don't Starve wiki, *Health*, *Hunger*, *Sanity* | Meters as pictures; an arrow over Sanity shows rising or falling, sized by speed; low sanity changes the world | Rate and danger are felt | **High** (rate arrow) |
| S37 | Don't Starve wiki, *Armor*, *Winter Hat* | Clothing with one job and visible drawbacks (95% armor but −30% speed); armors multiply; which piece wears first is hidden | Clear trade-offs; one hidden rule | **Medium** |
| S38, S39 | Hades wiki, *Boons*, *Pom of Power* | One perk per action slot; four rarities scale the same numbers; level scaling "currently unsolved" | Slots organise perks; opaque scaling frustrates planning | **Medium-high** (slots); **avoid** opaque scaling |
| S40-S42 | Slay the Spire wiki | Relics: one exact sentence each; counters on icons; every buff declares how it stacks (power, turns, uses); bold keywords; final damage shown before you act | Exactness and previews | **Very high** |
| S43 | Blizzard, *Season 4: Loot Reborn* | Affixes cut to 2-3 per item and made stronger; conditional lines removed; fewer drops; improved lines recoloured | "Is this an upgrade?" answerable at a glance | **Very high** (the counterexample and its fix) |
| S44-S46 | Monster Hunter wiki | Skill list with levels to a per-skill maximum; written steps per level; set bonuses by piece count; "Secret" skills raise a cap; the old points-threshold model | A perk list you can read; caps as rewards | **High** |
| S47, S48 | Elden Ring wiki | Icon frame shape by source (square = permanent, diamond = temporary, none = situational); one temporary buff per category; buffs multiply | Source at a glance; category stacking | **High** |
| S49 | Veloren source (`buff.rs`) | Each buff stores source, category tags, strength, end time; same kind keeps only the strongest active; identical re-application refreshes; food queues; potion sickness weakens back-to-back potions | A proven data shape for timed effects | **High** |
| S50 | Cataclysm: DDA docs (`EFFECTS_JSON.md`) | Effects as data: intensity names, how repeats add time or intensity, good/bad rating, descriptions generated from the data | Text can never disagree with the effect | **High** |
| S51 | Luanti `player_monoids` | Every change has a name; each stat declares how changes combine (multiply, strongest); value always recomputed | Removes "permanent speed boost" exploits | **High** |
| S52 | Grounded patch notes | Effect tooltips and HUD icons added later; a line on the bars marks the base 100; per-piece values normalised; a 10% effect raised to 50% | What to build from day one | **High** |
| S53 | Core Keeper patch notes | Stat window kept gaining missing lines and fixes; gear comparison added in 2026 | Same | **High** |
| S54 | Valheim patch notes | Totals tooltip had to start including timed effects | Totals must include meals and potions | **High** |
| S55 | Necesse patch notes | Armor tiers made "more clear"; buff icons moved beside the health bar | Small layout lessons | **Medium** |
| S56 | Path of Exile wiki, *Resistance* | Capped value with the uncapped total in brackets; caps raisable by rare items | Shows spare beyond the cap | **High** |
| S57 | League of Legends wiki, *Armor* | 100 / (100 + armor): no hard cap, each point adds the same effective health; editors had to defend the page against "diminishing returns" edits | Explains why percentages confuse | **Medium** |
| S58 | Grounded Steam forums | Vague set-bonus text; no totals screen; a player used a memory scanner to find durability; a real debate about numbers in survival games | A layered display satisfies both camps | **High** |
| S59 | interfaceingame.com screenshots | Hades: one sentence + one number per perk, empty slots as silhouettes, a "+3" counter beside the column; Monster Hunter: skill pips, set-bonus piece counts, Compare; Elden Ring: "110 + 15", Simple view; Diablo IV: "(+34)" delta and a scrolling tooltip; Slay the Spire: relic row, intent, recoloured numbers | Concrete, proven layouts | **High** |
| S60 | Game Accessibility Guidelines | Never colour alone; minimum text size; flashing limits | The sheet works for colour-blind players | **High** |

## 2. Recommendations for Bug Farmer's sheet

**How to read the scores.** Each hard choice lists at least four candidates scored 1-5 on four axes:
**Readability** (can a new player read it at a glance?), **Depth** (does it carry enough information for
players who plan?), **Fit** (does it suit the accepted sheet and a farming-and-ranching sandbox?) and
**Build cost** (5 = cheapest to build and maintain). The total is out of 20. The pick is reasoned, not just
the highest total; combinations are named when the best answer uses two candidates together.

### 2.0 Two layers, not one

Most of the games read here split information between the always-on display and the sheet, and the clearest
ones put **only what changes minute to minute** on screen: Minecraft shows health and hunger always,
armor only while worn, effects as small icons (S1-S3, S6); Grounded shows its coziness level only "if it is at
least 1" (S52). For Bug Farmer this suggests:

- **Always on screen:** current Health and Stamina; the meal socket and the potion socket (§2.9); a short row
  of other active effects. Armor could appear as a thin row of pips only while something can hurt you, as in
  Minecraft. Stealth could appear only while sneaking or when a bug is near. (These two are suggestions for the
  owner, not research findings.)
- **On the sheet:** all six meters, the three protections, the active perks, and every hover breakdown.

### 2.1 Meters: how to draw them

| Candidate | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. Ten pips in a row, a small meter icon at the start | 5 | 3 | 5 | 5 | **18** | Minecraft hearts and armor (S1, S2); Grounded's segmented defense bar (S20); Monster Hunter skill pips (S59) |
| b. A number per meter ("Speed 6") | 3 | 3 | 2 | 5 | 13 | Elden Ring, Core Keeper stat screens (S47, S26) |
| c. A smooth bar with a mark at the starting value | 4 | 3 | 3 | 4 | 14 | Grounded's "100" line on its bars (S52) |
| d. Repeated themed icons (hearts, boots, eyes) | 4 | 3 | 4 | 3 | 14 | Minecraft hearts (S1); Don't Starve gauges (S36) |
| e. A six-sided "spider" chart of all meters | 2 | 3 | 2 | 3 | 10 | — |

**Pick: (a), with the number one hover away.** Ten identical pips can be counted at a glance and read the same
way for all six meters, so a player learns one grammar once. They are exactly the accepted "dots capped at ten".
The number and its meaning live in the hover (§2.3) — the layered answer to the Grounded forum debate, where one
camp wanted no "math and numbers in your face" and the other could not find totals at all (S58). Use whole pips
only: items move meters by whole dots, and Minecraft needs half hearts only because one heart stands for two points.

### 2.2 Starting amount, bonus, loss — and colour by source

| Candidate | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. One colour, total only | 4 | 1 | 2 | 5 | 12 | — |
| b. Starting pips plain, bonus pips in a second colour, lost pips empty with a slash | 5 | 4 | 5 | 4 | **18** | Minecraft's yellow extra hearts (S1); Elden Ring's "110 + 15" (S59); Grounded's base line (S52) |
| c. A different colour for each item source (outfit, accessory, meal, potion) | 2 | 5 | 3 | 3 | 13 | None of the games read here colours a meter by item |
| d. Colour by how long it lasts: worn bonus vs timed bonus | 4 | 4 | 5 | 4 | 17 | Elden Ring's square vs diamond frames (S48); Minecraft's outlined beacon effects (S3) |
| e. A starting-value mark only | 4 | 2 | 3 | 5 | 14 | Grounded (S52) |

**Pick: (b) and (d) together, as four pip states with four shapes:**

| Pip state | Look | Means |
|---|---|---|
| Starting | plain solid pip | what you have with nothing worn or eaten |
| Worn bonus | solid pip in the gear colour | from the outfit or an accessory; stays while worn |
| Timed bonus | pip with a ring (or a small clock notch) in the timed colour | from the meal or potion; will vanish when its timer ends |
| Lost | empty pip with a slash | taken away by an item |

Why: at a glance a player needs three facts — how much, how much is extra, and what will vanish when a timer
ends. Which exact item gave which pip is a hover question (§2.3, RimWorld-style, S30-S32). Four item colours (c)
would fail colour-blind players and would not survive two accessories in similar colours; the shapes keep the
four states readable without colour (S60).

### 2.3 Every meter says what it means (a rule, not a choice)

Terraria's defense hover reads "Reduces hit damage by 10" (S7); Elden Ring writes "30.8 / 49.8 — Med. Load"
(S59); Slay the Spire prints the final damage on the card before you play it (S42). Hovering a Bug Farmer meter
should show, in this order: the number ("Stealth 6 of 10"); **what that does in game units**; what one more pip
would do; and the breakdown by source with the cap last. Format example (the numbers are illustrative only):

> **Stealth 6 / 10** — most bugs notice you at 5 tiles; wasps at 7.
> One more pip: 4 tiles.
> Starting 4 · Outfit +2 · Potion +1 (2:10 left) · Accessory −1 → 6

Two cautions from the sources: a percentage that grows more slowly than players expect gets called "diminishing
returns" even when every point is worth the same (S57, S19), so state the game effect, not only the number; and a
hover is only trustworthy if it is computed by the same code that computes the value (Stardew and RimWorld both
shipped text that disagreed with the effect, S13, S30).

### 2.4 Protections (Sting, Venom, Acid): how to show them

| Candidate | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. An icon and a percentage ("Venom 40%"), the cap shown beside it | 4 | 4 | 5 | 5 | **18** | Grounded resistance % (S20); Path of Exile (S56) |
| b. Named steps (Weak … Resistant … Immune) | 5 | 3 | 3 | 5 | 16 | Valheim (S18) |
| c. Ten pips, each worth 10% | 4 | 3 | 3 | 5 | 15 | — |
| d. Signed whole numbers (+3, −2) | 3 | 4 | 2 | 5 | 14 | Monster Hunter (S59) |
| e. A shield icon partly filled, number on hover | 4 | 3 | 4 | 4 | 15 | — |

**Pick: (a).** Keep the accepted percentages, but in **standard steps of 10%**, each protection with its own icon
(a stinger, a drop, a splash). Show the cap next to the value ("Venom 40% · max 80%"). Allow a negative value for
outfits with a weakness, drawn with a minus sign and a cracked icon (Valheim's Bear set and Don't Starve's night
armor show that a drawback on a strong item is a feature, S17, S37). The hover converts the percentage into a
real case: "A wasp sting: 3 hearts → 2"; "Venom lasts 6 s instead of 10 s". Keeping protections as percentages
and meters as pips also keeps the two kinds of number visibly different. Named steps (b) read best of all but
would replace an accepted decision; they remain a good fallback if percentages prove confusing in testing.

### 2.5 Stacking and caps

**Decision A — how sources combine.**

| Candidate | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. Everything adds, then clamp | 4 | 5 | 3 | 5 | 17 | Terraria accessory bonuses (S9); Path of Exile (S56) |
| b. One item per slot; the slots add; then clamp | 5 | 4 | 5 | 5 | **19** | Stardew's one food + one drink (S13); Elden Ring's one-per-category (S48); Terraria's food (S12) |
| c. The strongest single source wins | 4 | 2 | 3 | 5 | 14 | Valheim resistances (S18); Veloren (S49) |
| d. Multiply what gets through ((1 − a) × (1 − b)) | 2 | 4 | 3 | 5 | 14 | Don't Starve armor (S37) |
| e. A points-to-percent curve | 2 | 4 | 2 | 4 | 12 | League of Legends (S57) |

**Pick: (b).** Bug Farmer's item jobs already are slots — one outfit, two accessories, one meal, one potion — so
"each slot holds one thing, and the slots add up" is a rule the player can say in one sentence, and it limits how
many items can ever touch a meter to five (effects from the world, such as venom, come on top). Details:

- **Meters** add across slots and are clamped to 0-10.
- **Protections** add across slots and are clamped to a visible cap below 100% (Minecraft stops armor at 80%;
  Path of Exile's commonly cited default is 75%; the exact number is a balance call). 100% ("immune") only from
  deliberate exceptions — the "an item may break the pattern" rule.
- **Sized perks of the same family** (two sources of "more planks") add up to that family's cap and show as one
  merged line; a duplicate yes-or-no perk does nothing and its item says so ("you already have this").
- **Meals and potions:** the same item again refreshes its time; a different one replaces it (Minecraft, Terraria,
  Stardew and Valheim all do one of these, S3, S12, S13, S16). Say the rule where it applies — in the tooltip of
  the meal you are about to eat (§2.8). Core Keeper's players were still arguing about its rule four years after
  release (S29).
- **Never write a meter directly.** Every pip comes from a named entry that is removed by name (§2.11); Luanti's
  library exists because direct writes caused "permanent speed boost" exploits (S51).

**Decision B — how a cap shows.**

| Candidate | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. Silent clamp; extra is simply lost | 3 | 3 | 4 | 5 | 15 | Minecraft's armor row above 20 (S2) |
| b. Clamp, show the overflow ("+1 over") and warn before equipping | 5 | 4 | 5 | 4 | **18** | Path of Exile's uncapped value in brackets (S56) |
| c. Soft cap: pips past 8 cost double | 2 | 4 | 2 | 3 | 11 | — |
| d. Gear can reach 8; only timed items reach 10 | 3 | 5 | 4 | 4 | 16 | (a balance lever) |
| e. Rare items raise a cap past ten | 4 | 5 | 3 | 3 | 15 | Monster Hunter's "Secret" skills (S44); Path of Exile max resistances (S56) |

**Pick: (b).** A full meter gets a small cap mark on its tenth pip; wasted pips appear as a dimmed "+1" after the
row; the item's tooltip warns before you equip ("Speed +1 — wasted, Speed is already 10"). Keep (d) and (e) in
reserve as balance levers for the owner — Monster Hunter makes lifting a cap a top-tier reward, but it breaks the
clean "out of ten" frame, so it should be rare if used at all.

### 2.6 Perks: how to show them

| Candidate | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. A text list grouped by activity, active perks only | 5 | 4 | 5 | 5 | **19** | RimWorld's hide-at-default (S30); Monster Hunter's skill list (S44) |
| b. An icon grid with text on hover | 3 | 4 | 4 | 3 | 14 | Slay the Spire relic row, Hades column (S59) |
| c. Each row: family icon + one sentence with the number highlighted + size pips + a small source mark | 5 | 5 | 5 | 3 | **18** | Hades boon card (S59); Monster Hunter skill pips (S59) |
| d. Only inside item tooltips | 1 | 3 | 1 | 5 | 10 | Early Grounded (S52, S58) |
| e. Empty accessory slots drawn as silhouettes | 4 | 3 | 4 | 4 | 15 | Hades action slots (S59) |

**Pick: (c) rows inside (a)'s layout, plus (e).** The sheet's perk panel lists only active perks, grouped by
activity (farming, ranching, fishing, mining, crafting, building, moving, fighting), each row reading like a
Hades card: icon, one sentence, one number in the highlight colour, three size pips, and a tiny mark for its
source (outfit, accessory, meal, potion). Empty accessory slots show a faint silhouette, so a player sees there is
room for a trade tool. Perks do not need to be on the always-on display unless timed.

The slot structure keeps this list short by itself: an outfit carries 1-3 perks, two accessories carry a few
more, a meal and a potion add one each — around **nine lines at most**, however large the item catalogue grows.

### 2.7 Perks: standard sizes

| Candidate | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. Any number per item | 2 | 4 | 1 | 5 | 12 | Grounded (S21) |
| b. Three sizes per perk family (Small, Medium, Large) from one published table | 5 | 4 | 5 | 5 | **19** | Monster Hunter levels (S44); Terraria food tiers (S12); Grounded mutation phases and meal tiers (S22, S24) |
| c. Rarity tiers that scale every number | 3 | 4 | 3 | 4 | 14 | Hades (S38) |
| d. Yes-or-no "unlock" perks only | 5 | 3 | 4 | 5 | 17 | Slay the Spire relics (S40); Monster Hunter's "activates skill effect" (S44); Grounded's species perks (S21) |
| e. Points that switch a perk on at thresholds | 1 | 4 | 1 | 4 | 10 | Older Monster Hunter (S46) |

**Pick: (b) and (d) together — two kinds of perk.**

1. **Unlocks** (yes or no): for example night vision, or "one kind of bug ignores you". These change
   what you can do, read instantly, and are the perks players remember (Grounded's HumAnt and Waspoid, S21).
2. **Sized perks**: exactly three sizes per family, from one published table, written on the item as a number.

Rules drawn from the sources:
- **The smallest size must be felt.** Grounded raised one trinket effect from 10% to 50% damage resistance in a
  patch (S52) — a sign the small size was not worth a slot; Blizzard cut Diablo IV's item lines and made the rest
  "more effective" (S43); a Core Keeper thread complains that pieces with small percentages are "quickly
  overshadowed by other options with bigger numbers" (S29). For counted outputs, a Small perk should give at least
  one extra item in a normal batch.
- **Never vague words in place of numbers** ("increased efficiency" made Grounded players open the wiki, S58).
- **No conditional mini-perks** ("+5% against slowed targets") — one of the things Blizzard removed (S43).
- **One family, one direction**: output, speed of an action, reach, duration, carrying, notice distance.
- **Write perks in the activity's own units where possible** — "+1 plank per 3 logs" is clearer than "+33%" (my
  suggestion; Terraria's defense hover does the same kind of translation, S7).

A **starting table for the owner to judge** (a proposal, not a decision; the sheet's own examples are +30% planks
at the sawmill and +1 net reach):

| Family kind | Small | Medium | Large | Notes |
|---|---|---|---|---|
| More output (planks, honey, fish) | +15% | +30% | +50% | "+30% planks" lands as Medium |
| Faster action (dragging, chopping, reeling) | −15% time | −30% time | −45% time | shown as "faster", never as negative |
| Reach or range in whole tiles | +1 | +2 | +3 | "+1 net reach" is Small |
| Meter pips (outfit or accessory) | +1 | +2 | +3 | added to the meter |
| Meal: Health and Stamina pips | +1 | +2 | +3 | better food, more pips, longer (Grounded 12/16/20 min, S24) |
| Potion: one strong change | +3 pips or +30% protection | — | — | potions are "strong and short"; one size may be enough |

### 2.8 Item tooltips: what would change if you wear or eat it

| Candidate | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. The item's own lines only | 3 | 2 | 3 | 5 | 13 | Minecraft (S5) |
| b. Change lines against what it replaces (+/−, better/worse) | 4 | 4 | 5 | 4 | 17 | Diablo IV "(+34)" (S59); Monster Hunter's highlighted values (S59) |
| c. A side-by-side compare panel on a key | 4 | 5 | 4 | 3 | 16 | Diablo IV, Monster Hunter "Compare" (S59); Core Keeper, added 2026 (S53) |
| d. Live preview on the sheet: pips and perk lines change while you point | 5 | 5 | 5 | 3 | **18** | Elden Ring and Monster Hunter status columns (S59); Slay the Spire's damage preview (S42) |
| e. Full breakdown on demand | 3 | 5 | 3 | 4 | 15 | RimWorld (S30-S32) |

**Pick: (d) with (b) in the tooltip; (e) on any meter's hover.**
- **Outfits and accessories:** while you point at one, the sheet shows the result — pips that would be gained
  drawn as outlined pips that gently pulse, pips that would be lost slashed, perk rows that would appear marked
  "+" and rows that would go marked "−". The tooltip lists **only the changes**, best first: "Speed ●●●●●○ (+1)",
  "Gains: wasps ignore you", "Loses: +1 net reach". Because an outfit is worn whole, there is only ever one
  outfit to compare against — far simpler than the three- and four-piece armor of Terraria, Grounded and Minecraft.
- **Meals and potions:** "Health +2 pips for 16 min — replaces your current meal (+1, 3 min left)". If the new item is
  weaker than the current one, say so. If eating would waste pips at the cap, say so.
- **Accessories when both slots are full:** ask which slot it replaces, and preview both.
- A **compare key** (c) is a later extra; the live preview covers most of its use.

### 2.9 Timed effects: icons with time left

| Candidate | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. Icon row with minutes:seconds under each | 4 | 3 | 4 | 5 | 16 | Terraria (S8); Minecraft's inventory list (S3) |
| b. Icon with a draining ring and a blink near the end | 5 | 3 | 5 | 4 | 17 | Minecraft flashing (S6); Stardew blinking (S13); Valheim flashing a food when it can be refilled (S16) |
| c. A text list of names and timers | 3 | 4 | 2 | 5 | 14 | — |
| d. On the sheet only | 2 | 3 | 2 | 5 | 12 | — |
| e. Two fixed sockets (meal, potion) plus a short row for other effects, frame shape by source | 5 | 4 | 5 | 4 | **18** | Elden Ring frames (S48); Hades slots (S59); Grounded HUD icons (S52) |

**Pick: (e) drawn with (b).**
- **Meal socket and potion socket** beside Health and Stamina: the item's own icon, a ring that drains, minutes
  left as a small number, a slow blink in the last ten seconds (small and slow, within the flashing guideline,
  S60), and a faint outline when empty — a quiet reminder that you could eat. Because Bug Farmer allows one of
  each, this area never grows.
- **Other effects** (poisoned, wet, cosy at home, night vision from a hat) in one short row: **round frame =
  timed, square frame = from worn gear, no frame = from a place** (Elden Ring's grammar, S48); good or bad by frame
  colour **plus** an up or down arrow (S60); ordered soonest-ending first (Minecraft, S6); anything that ticks
  (venom, hunger) gets Don't Starve's small arrow sized by speed (S36).
- **Hover:** name, one sentence, the exact numbers, time left, and the source.
- On the sheet, timed pips are the ringed pips of §2.2, so the sheet and the sockets tell the same story.

### 2.10 Keeping the sheet readable as the game grows

| Candidate rule | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. Freeze the frame: six meters and three protections never grow; new content adds perks from approved families | 5 | 4 | 5 | 5 | **19** | Blizzard's affix cut (S43); Grounded's dozen damage types as the warning (S25) |
| b. Hide anything at its normal value | 5 | 4 | 5 | 5 | **19** | RimWorld (S30); Grounded's coziness "if at least 1" (S52) |
| c. Group perks by activity, collapsible | 4 | 4 | 5 | 4 | 17 | Monster Hunter skill groups (S45) |
| d. A simple / detailed toggle | 4 | 5 | 4 | 3 | 16 | Elden Ring "Simple view" (S59) |
| e. Bold game terms, each with its own explanation | 4 | 4 | 4 | 4 | 16 | Slay the Spire keywords (S42); Hades (S59) |
| f. Every line generated from the same data that computes it | 4 | 4 | 5 | 3 | 16 | Cataclysm: DDA (S50); mismatch bugs in Stardew, RimWorld, Core Keeper (S13, S30, S53) |

**Pick: (a), (b) and (f) as rules from day one; (c) and (e) as layout tools; (d) only if the sheet gets dense.**
Add three house rules: **a perk budget per item kind** (outfit 1-3, accessory 1-2, meal one boost, potion one
change); **a size table** (§2.7) that new items must use; and **before adding a meter or protection, first try the
idea as a perk** — most "new stats" are really perks.

### 2.11 The data under the sheet

| Candidate | Readability | Depth | Fit | Build cost | Total | Seen in |
|---|---|---|---|---|---|---|
| a. Change the meter directly when an item is equipped or eaten | 2 | 2 | 1 | 5 | 10 | Luanti before its library (S51) — leads to stuck or permanent boosts |
| b. A list of named modifiers (id, target, operation, amount), applied in a fixed order, then clamped | 4 | 4 | 5 | 4 | 17 | Minecraft (S4); RimWorld (S30) |
| c. Per-target combine rules over named entries (add, strongest, multiply) | 4 | 5 | 5 | 4 | **18** | Luanti monoids (S51); Veloren (S49) |
| d. Effects as pure data with stacking fields, text generated from the data | 4 | 5 | 5 | 3 | 17 | Cataclysm: DDA (S50) |

**Pick: (b) + (c) + (d).** Each bonus is an entry with: a unique id; its source slot (outfit, accessory 1 or 2,
meal, potion, place); its target (a meter, a protection or a perk family); its amount or size; and its end time
if timed. Each target declares how entries combine (meters and protections: add, then clamp; sized perks: add up
to the family cap; unlocks: any). Each timed kind declares refresh-or-replace. The sheet, the tooltips and the
breakdowns are all generated from these entries, and the **uncapped** total is kept so the overflow can be shown.
In a multiplayer game where the server is the authority, a value that is always recomputed from named entries is
also easy to check and to send to other players. These would be new fields on the item entries in the canonical
entity data.

### 2.12 What is the owner's call, not research

These are taste or balance questions; the research above informs them but cannot answer them:
- The protection cap (75%, 80%?) and whether any item may give 100% against one danger.
- Whether any rare item may lift a meter past ten.
- The numbers in the size table (§2.7).
- Whether a meal raises **maximum** Health and Stamina (Valheim) or refills them (Minecraft), and how meal pips
  look on the always-on display.
- The pip colours, the frame shapes and the icons (art direction).
- Whether Armor and Stealth appear on the always-on display, and whether hovering Stealth draws a notice-distance
  ring in the world (Don't Starve shows how a meter can be felt in the world, S36).

## 3. Grounded: what to copy and what to avoid

Grounded (early access 2020, full release 2022, patched into 2025) and Grounded 2 (early access since 2025) are the
closest premise: people among giant bugs, armor made from bug parts, resistances to dangers such as poison and gas,
and — in Grounded 2 — bugs you hatch, raise and ride. Sources: S20-S25, the Grounded 2 pages, S52 and S58.

**Copy**

1. **Perks about how a species treats you.** The red ant set makes red ants treat you as one of them; aphid
   slippers make aphids ignore you; the bard hat makes wasps neutral **but bees hostile**; riding a soldier-ant
   buggy makes that species neutral (S21, Grounded 2 *Buggies*). These are among the clearest perks in the
   game: yes-or-no, visible in play, often with a built-in cost. For Bug Farmer they are the natural companion to the
   Stealth meter — Stealth is "how close bugs get before noticing you", a species perk is "this kind of bug does not
   mind you" — and they fit a game where bugs are raised like livestock.
2. **A visible trade-off by weight class.** Light, medium and heavy armor give 10/20/30% less damage but cost
   5/15/25% more stamina per action (S21). Bug Farmer's outfits can carry the same honest drawback, shown as lost pips.
3. **A meal table with fixed sizes.** Tier 1/2/3 meals last 12/16/20 minutes, give 1×/1.5×/2× regeneration and
   1/1/2 extra effects (S24). One table, learnable in a minute.
4. **A mark for the starting amount.** Grounded added a line on the health and stamina bars "to help show how much
   growth your health and stamina get from… upgrades or status effects" (S52) — the same job as Bug Farmer's
   starting-pip versus bonus-pip states.
5. **Effect icons with tooltips, on screen and in the inventory**, and enemy effects shown under the enemy's health
   bar (S52) — so venom on a bug you hit is visible.
6. **Comfort from building a home**, shown only when it is at least level 1, with duplicates of the same furniture
   counting less (S52) — a gentle, readable link between building and the sheet.
7. **Saved loadouts** (four mutation loadouts, S22) — worth considering for quick swaps between trade accessories.
8. **Normalising values** — Grounded tidied per-piece values into equal ones in update 1.3 (S52); Bug Farmer can start
   with the size table instead of tidying later.

**Avoid**

1. **Vague in-game text.** "Reflects some damage back at attacker" was 100%; "your body recycles energy with increased
   efficiency" meant faster stamina regeneration (S21, S58). Players went to the wiki, and one used a memory scanner to
   find a shield's durability (S58). Every Bug Farmer perk line carries its number.
2. **One effect name at many sizes.** "+Damage Resist" ranges from 2% to 50% depending on the source (S21), so the icon
   tells you nothing about size. In Bug Farmer, one perk family has one size table.
3. **Effects too small to feel** (5% thirst, 5% stamina delay, 5% against early creatures, S21), and a trinket effect that
   had to be raised from 10% to 50% (S52).
4. **No totals and hidden rules.** Players could see each piece's defense but nowhere the total (S58), and a minimum
   damage rule is "not visible in-game" (S20). Bug Farmer's sheet shows totals and every rule that changes a number.
5. **Set bonuses nobody can find.** Players did not know set bonuses existed until reading about them (S58). Bug
   Farmer's outfits are worn whole, so their perks must be on the outfit's tooltip **before** you wear it.
6. **A dozen damage types and resistances** (acid, burning, busting, chopping, explosive, shock, slashing, stabbing,
   fresh, spicy, salty, sour… S25). Three protections are enough for a farming sandbox.
7. **Perks scattered across separate systems** (armor effects, trinkets, mutations, meals, pets). Grounded had to add
   mutation icons next to the other effect icons in 2023 (S52). If Bug Farmer ever grants a perk from outside items,
   it belongs in the same perk list with a source mark.

## 4. Claims I could not verify

- **Vanilla Minecraft has no "compare with what you wear" tooltip.** Believed (mods exist for it), not confirmed from a
  source.
- **Grounded's internal size words.** The wiki's effect ids include Tiny / Small / Medium (`CriticalHitTiny`,
  `MaxHealthSmall`, `SwimSpeedMedium`). That the developers use them as standard sizes is my inference.
- **Grounded 2's archetype passives and its stat screen.** The Grounded 2 wiki pages were thin (early access); the
  archetype names and the bulky/sleek choice are confirmed, the passives' numbers and any new stat display are not.
- **Elden Ring's buff categories in game.** The wiki lists the categories (Armament, Body, Aura, Health Regen); whether
  the game itself names them anywhere was not checked.
- **Don't Starve's exact numbers on screen.** Whether and when the meters show numbers (hover, settings) was not checked.
- **Hades' "+3" counter.** Seen in a screenshot beside the boon column; that it stands for further boons not drawn in
  the column is my reading of the picture. The full pause-screen boon list was not seen.
- **Core Keeper's new gear comparison.** Only the patch line ("Introduced the ability to compare gear", 21 Sept 2026) was
  read; how it works was not.
- **Monster Hunter: levels beyond a skill's maximum do nothing.** Strongly implied (each skill lists a fixed number of
  levels, and "Secret" skills exist to raise the maximum), not stated in the text read.
- **Path of Exile's default 75% cap.** The page read gives the 90% hard cap and uses 75% in its example; the default is
  the commonly cited value.
- **Stardew's buff icon position and hover text**, **Necesse's rule for eating two foods of different quality**, and
  **Valheim's in-game display of the fork colours' meaning** were not checked.
- **The Game UI Database** (gameuidatabase.com) refused automated access (HTTP 403); a different screenshot library was used
  instead (S59). **GDC talks** were available only as abstracts; none were used as evidence.
- **Reddit** refused automated access, so player-complaint evidence comes from Steam forums and wiki notes only.
- **The 28-pixel text guideline** comes from television viewing distance; how it maps to a PC pixel-art game was not
  checked.
- **Search method limit.** This session's web-search allowance was already used up, so sources were found through the
  wikis' own search, Steam's forum search and news feed, GitHub and GitLab, and known addresses. Breadth is good (16
  games, 3 open-source projects, 60 numbered sources), but a general web search might have found developer blog posts
  that this method missed.

---

## Appendix: reading notes, source by source

### S1-S6. Minecraft (Mojang) — minecraft.wiki pages S1 *Health*, S2 *Armor*, S3 *Effect*, S4 *Attribute*, S5 *Tooltip*, S6 *Heads-up display* (read 2026-10-02 as raw page text)

**Meters as icons, not numbers.** Health is a row of 10 heart icons; each heart has two halves, so 10 icons
show 20 points. Armor is a second row of 10 chestplate icons drawn **directly above the health row, and only
when armor is worn**. The armor row shows at most 20 points; the real cap is 30, so anything above 20 is
invisible on screen (S2: "The armor bar does not show armor points above 20"). A second armor value,
*toughness* (it makes armor hold up better against big hits), **has no visual indicator at all** — the wiki
says so in those words. This is the classic "hidden number" that players have to look up.

**Colour shows the source or condition.** Hearts change texture by condition: green when poisoned, black
when withering, cyan when freezing, and **extra hearts granted by the Absorption effect are drawn yellow**
and added after the red ones (S1). Low health (4 points or fewer) makes the hearts shake; the Regeneration
effect makes them bounce in a wave. So the one row of icons carries: amount, bonus amount (different
colour), danger (shake) and an active effect (motion), without a single number.

**How armor maths stays bounded.** Each armor point is worth 4% damage reduction, capped at 80% (20 points);
armor gets weaker against bigger hits, but never below one fifth of its full value (S2 formula). A hard cap
(80%) plus a soft fall-off is how Minecraft keeps full armor from making a player immune.

**Timed effects (S3, S6).** Every active effect shows as an icon in the top-right corner of the screen.
Effects that run out sooner sit further left; an effect about to run out **flashes**; good effects sit on the
top row, neutral and bad on the bottom row; effects from a beacon (a placed block that buffs everyone near
it) get a **blue outline** so you can tell "from the world" apart from "from a potion". The inventory screen
lists each effect with its level and time left. Potion tooltips read like "Slowness IV (0:20)": name, level
in Roman numerals, time in minutes:seconds; good effects in blue text, bad in red (S5).

**Stacking rule (S3).** Different effects all apply at once, even opposites (Strength and Weakness), but
**the same effect never stacks with itself**: a higher level replaces a lower one, and a longer time
replaces a shorter one at the same level. In the Java edition, for non-player creatures, a weaker but longer
effect hides under the stronger one and comes back when the stronger one ends.

**Item tooltips (S5).** Worn items show a "When on Head:" line, then each bonus such as "+2 Armor" in blue
(negative in red). There is no built-in "compared with what you are wearing" view in the base game
(see the unverified list).

**Data shape (S4).** Every bonus is a *modifier*: an id, one attribute it changes, an operation and an
amount. Three operations, always applied in this order: (1) add a flat amount; (2) add a percentage of the
base, where percentages from different items are **added together first** (+20% and +30% = +50%);
(3) multiply the running total, where each one **compounds**. The result is then clamped to the attribute's
minimum and maximum. Because each item's modifier has its own id, taking the item off removes exactly that
modifier, and the same item can never be counted twice.

**What Bug Farmer takes from it:** a row of ten icons that can show half-steps, an extra-colour for bonus
amounts, a meter that only appears when relevant, and the warning that any value with no indicator becomes a
wiki question. The three-operation modifier model is a ready-made, well-tested data shape.

### S7-S12. Terraria (Re-Logic) — terraria.wiki.gg pages S7 *Defense*, S8 *Buffs*, S9 *Accessories*, S10 *Informational Accessories*, S11 *Armor*, S12 *Tooltips* + *Well Fed* (read 2026-10-02 as raw page text)

**Defense is one number with a plain-language hover.** Terraria's defense is a flat amount taken off each
hit (half the defense value in the normal difficulty). The inventory shows it as a shield icon with the number
inside; hovering it reads "20 Defense / Reduces hit damage by 10" (the in-game text, expanded from the wiki's
game-text template). This is the important trick: **the abstract number is translated into what it does for
you, right where you see it.** The shield's border colour also tells you the world difficulty (rainbow for
Expert, red for Master), so one icon carries a second fact.

**Set bonuses (S11).** A full matching set adds a "Set Bonus" line that appears in the tooltip only while
the whole set is worn. Sets are often built for a job: the Mining armor gives +20% mining speed spread across
its pieces, and the full set adds another +10% (+30% total) plus a light on the helmet. The wiki's own tips
spend a whole section on **mixed sets** (one piece from each of several sets), which is where Terraria's depth
lives — and also where newcomers get lost.

**Accessories (S9, S10).** Five accessory slots (six or seven on harder difficulties). **The same accessory
cannot be worn twice.** Accessories that would crowd the slots can be **combined at a workbench into one item
that keeps all their effects** (Hermes Boots + Rocket Boots → Spectre Boots and so on), which is how Terraria
lets the list of effects grow without adding slots. Accessories can roll a small random bonus ("modifier",
+1 to +4 defense or +1% to +4% of a stat) but **never a penalty**; the wiki notes that an accessory and its own
ingredients worn together "will not necessarily combine" — the stacking rule is per item, and you have to look
it up.

**Information as equipment (S10).** "Informational accessories" (watch, depth meter, compass, radar, fish
finder, weather radio, DPS meter...) each add one line of readout beside the minimap. Since version 1.3 they
**work from the backpack** rather than taking an accessory slot, they combine into one gadget (the PDA, later
the Shellphone), and **their readouts are shared with teammates within 50 tiles** in multiplayer. In 1.4.4 a
readout greys out or shows "N/A" when it does not apply right now.

**Timed effects (S8).** Active buffs show as icons **below the hotbar with their time left under each icon**;
hovering shows a tooltip; right-click cancels most buffs. One key ("B" by default) drinks every buff potion you
carry that is not already active — a convenience that exists because buff management became a chore. The cap
is 44 active buffs and debuffs at once (when full, the leftmost one is dropped).

**Food in tiers (Well Fed page).** Food gives one of three buffs: *Well Fed*, *Plenty Satisfied*,
*Exquisitely Stuffed*. All three change **the same seven stats, in fixed steps** (for example defense +2/+3/+4,
movement speed +20%/+30%/+40%); better food gives the higher tier and longer time (1 to 48 minutes). **Only one
of the three can be active; the most recent meal wins.** This is a clean model of "one meal at a time, better
food is a bigger standard size".

**Tooltip colours (S12).** Stats first, then the set bonus (when worn), then random modifier lines at the
bottom, **green for good, red for bad**.

**What Bug Farmer takes from it:** plain-language hover on every number; food as fixed tiers of the same
boost; "one of each, most recent wins"; combine-able trade gadgets instead of more slots; readouts that work
from the backpack and are shared with nearby friends; and the warning that per-item stacking rules that you
must look up are a cost.

### S13-S15. Stardew Valley (ConcernedApe) — stardewvalleywiki.com pages S13 *Buffs*, S14 *Rings*, S15 *Forge* (read 2026-10-02 as raw page text)

**One food and one drink (S13).** Buffs ("buff" = a temporary boost, a "debuff" is a temporary drawback) from
**exactly one food and one drink** can be active at once. Eating a new buff food wipes the old food's buffs
but leaves the drink's; a new drink replaces the old drink. Food that only restores health and energy can be
eaten freely without touching buffs. Only three stats (Luck, Speed, Max Energy) come from both food and drink,
so only those can add up (coffee's +1 Speed plus a meal's +1 Speed). Bad effects and a few special effects are
handled separately: one of each, a repeat just resets its timer. All buffs end when you sleep.

**Display details (S13 history).** Version 1.5 made a buff's icon **blink before it runs out**; version 1.6
made a food's inventory tooltip **show the buff's duration** before you eat it, and fixed two display bugs worth
learning from: a meal whose good and bad effects summed to zero was silently discarded, and negative custom
buffs printed as "--2 speed". (Both are the sort of mistake a generated tooltip makes when the display is not
built from the same data as the effect.)

**Rings (S14, S15).** Two ring slots. Some rings add up with themselves (two light rings make more light; two
magnet rings pull from further), and the wiki has to say, ring by ring, which ones do. A late-game forge
**combines two different rings into one** that keeps both effects; a combined ring cannot be combined again, and
it can be split back. So two slots become at most four effects — a controlled ceiling on stacking, reached by
effort, and undoable.

**What Bug Farmer takes from it:** the one-food-plus-one-drink split matches "one meal at a time, one potion at
a time" almost exactly and shows it is easy to understand; show a meal's duration in its tooltip before eating;
blink before expiry; and if two worn items may add up, say so on the item rather than leaving it to a wiki.

### S16-S19. Valheim (Iron Gate) — valheim.fandom.com pages S16 *Food*, S17 *Armor* + *Status effects*, S18 *Resistance*, S19 *Damage mechanics* + *Rested* (read 2026-10-02 through the wiki's API)

**Three food slots (S16).** Food does not fill a hunger meter; each meal **raises your maximum health and
stamina** (and eitr, the magic meter) for a while. You can have **three different foods** active; the same
food cannot be eaten again until the first is partly digested, which is shown by **its icon flashing** in the
status panel; re-eating it refreshes it. The bonus fades along a curve: slowly at first, then quickly just
before it ends (92% left at three-quarters time, 50% left with a tenth of the time left). Every food icon has a
small **fork symbol coloured by the meter it mostly feeds: red for health, yellow for stamina, blue for eitr,
white for balanced** — you can read a food's job off its inventory icon without opening a tooltip. The wiki's
"max combinations" section shows the decision this creates: three health foods, three stamina foods, or a
balanced mix, chosen for the trip ahead.

**Resistances are words, and the strongest one wins (S18).** Valheim shows damage-type protection not as a
percentage but as a **named step**: Very weak (200% damage taken), Weak (150%), Slightly weak (125%), Neutral,
Slightly resistant (75%), Resistant (50%), Very resistant (25%), Immune (0%). **Sources do not add up and do not
cancel out: the single strongest resistance wins** (a frost-resistance drink plus a frost-resistant cape is
still just "Resistant"), and any resistance beats any weakness. The wiki lists nine worked examples, which is a
hint that the rule needed explaining. (One oddity in the code order: "Slightly resistant" outranks "Immune".)

**Armor maths (S19).** Damage minus armor while armor is under half the hit; above that, damage shrinks along a
curve. The wiki makes the point that this "diminishing return" is still fair when you count **hits until death**:
each point of armor adds the same number of survivable hits as the one before. (This is the usual answer to
"why do my extra armor points seem to do less?")

**Set effects as status icons (S17).** Wearing a whole set adds a named status effect — the Bear set gives
*Berserk* (+30% health regeneration, +10% slash damage, but 25% more damage taken from blunt, slash and pierce),
the Fenris set gives *Fenris blessing*. These sit in **the same icon row as timed effects, without a timer**, "only
while entire set is equipped". A set can carry a drawback as well as a benefit.

**Hidden effects get noticed (S19 *Rested*).** The *Rested* effect (from sleeping or sitting by a fire in a
comfortable house) raises regeneration; the wiki notes it also gives +50% skill experience, "not mentioned in its
description". Its duration grows by one minute per comfort level, so building a nicer home is rewarded on the
sheet — a nice link between building and stats.

**What Bug Farmer takes from it:** colour a food's icon by the meter it feeds; flash the icon when it is about to
end; named steps for protections are a strong alternative to percentages; "strongest single source wins" is the
simplest stacking rule there is; a whole-outfit effect can live in the status row with no timer; never leave an
effect out of the description.

### S20-S25. Grounded (Obsidian) — grounded.fandom.com pages S20 *Armor*, S21 *Status Effects* (+ its positive, negative and set-bonus tables), S22 *Mutations*, S23 *Trinkets*, S24 *Consumables*, S25 *Damage Types*; plus the *Armor (Grounded 2)*, *Buggies* and *Grounded 2* pages (read 2026-10-02 through the wiki's API)

Grounded is the closest premise: shrunken teenagers surviving in a backyard among giant bugs, with armor
crafted from bug parts. Grounded 2 (early access since 2025) adds rideable, hatch-and-raise bugs ("buggies").

**How armor numbers show (S20).** Armor protection comes from three numbers applied in order: *Defense*, a flat
amount taken off each hit, **"shown as a segmented bar"**; *Resistance*, a percentage cut set by the armor's weight
class (light 10%, medium 20%, heavy 30%), **"shown as a percentage number"**; and *Minimum Guaranteed Damage*
(25% of every hit always gets through), **"not visible in-game"**. So Grounded already mixes a segmented bar,
a percentage and a hidden rule — the same three display kinds Bug Farmer is choosing between. The weight class is
also a trade: light/medium/heavy armor costs 5%/15%/25% more stamina per action (S21).

**Effects are named icons — one name, many sizes (S21).** Every bonus is a named effect with an icon: *+Damage
Resist*, *+The Quickness* (movement speed), *+Poison Resist*, *Trickle Regen* and so on. The same named effect is
reused by many sources at **very different sizes**: *+Damage Resist* is 2% from one burger, 10% from a food, 35% from
a badge and 50% from a pet; *+The Quickness* is 10%, 15%, 20% or 20-50% depending on the source. The icon alone
does not tell you how big it is. Several effects are tiny enough to be hard to feel (+5% thirst drain, a 5%
shorter stamina delay, 5% damage against early creatures).

**In-game wording hides the numbers (S21 set-bonus table).** The wiki prints two columns, "Details" (worked out by
players) and "In-Game Description", and the gap is large: the Black Ant set says "Reflects some damage back at
attacker" (the wiki: 100% of damage taken); the Ladybug set says "Occasionally heal after blocking attacks" (50%
chance, 1 health every 2 seconds for 20 seconds); the Antlion set says "Faster reload speed while in combat" (40%
for 3 seconds). The size of most set bonuses is only knowable from the wiki.

**Bug-specific perks — the strongest idea for Bug Farmer (S21).** Several of Grounded's most distinctive effects are
about **how a species treats you**: the Red Ant set's *HumAnt* ("Red ants see you as one of them": soldiers ignore
you unless you attack an ant or steal an egg); the Aphid Slippers' *Aphkid* (aphids ignore you); the Bard hat's
*Waspoid* (wasps turn neutral, **but bees turn hostile** — a perk with a built-in cost). These are standalone,
yes-or-no perks, easy to read, and they change play more than a +5% ever does.

**Perks as a separate, slot-limited system (S22).** *Mutations* are Grounded's perks: earned by doing things (kill
40/100/200 creatures with an axe to reach phase 1/2/3), **start with 2 slots, raised to 5** with a rare currency,
41 in all, and **up to 4 saved loadouts** to swap sets quickly. Phases give standard steps (e.g. poison resistance
25%/50%/75%, movement 20%/35%/50%). Mutations bought from the game's robot are "unlocked for all players in the
world" — a shared, multiplayer-friendly unlock.

**Accessories and food (S23, S24).** Only **one trinket** slot. Meals come in three tiers with fixed sizes:
tier 1 = 12 minutes, normal regeneration, 1 meal effect; tier 2 = 16 minutes, 1.5x, 1 effect; tier 3 = 20 minutes,
double, 2 effects — a clean "better food is bigger and longer" table. The *Well Fed* effect is the same idea
(1 / 1.5 / 2 health every 2 seconds by meal tier).

**Damage types (S25).** Grounded has many damage types for weapons and creatures (acid, burning, busting, chopping,
explosive, generic, shock, slashing, stabbing, plus fresh/spicy/salty/sour "augments") and many matching
resistances (poison, gas, burn, sizzle, explosive, smashing, stabbing...). The list is large; for a farming game
three protections (Sting, Venom, Acid) is far easier to learn.

**Grounded 2 (S20 G2 tab, Buggies, Grounded 2 page).** The Grounded 2 wiki pages are thin (early access; the armor
page was last updated 10/03/2025 and warns that information may be wrong). Confirmed from the store text quoted on
the wiki: "unique archetypes, each offering distinct abilities" and buggies you "hatch, raise, and ride", which can
fight and gather. A buggy is obtained by hatching an egg (red soldier ant, orb weaver, ladybug).

**G2a. Grounded 2 armor data (grounded.wiki.gg, *Armor (Grounded 2)* page and its set template, read 2026-10-02).** Most
Grounded 2 armor belongs to an *archetype* — Fighter, Ranger, Mage or Rogue — and "each of these archetypes have a
unique passive buff that is applied to the player when worn, as well as guiding players as to which armor will fit
their playstyle". Armor upgrades to level 5; at level 3 the player picks **bulky** (more defense) or **sleek**
(slightly less defense plus a unique effect). The wiki's data template stores each set as: tier, class, defense per
piece (chest worth double), resistance % per piece, one piece effect id, one set-bonus id, one sleek effect id. The
effect ids carry **size words** — `MaxHealthSmall`, `StaminaBlockTiny`, `CriticalHitTiny`, `SwimSpeedMedium`,
`DamageResistAllShort` — which suggests the developers think in standard sizes (tiny / small / medium) even though
the in-game text never shows the size (see the unverified list).

**G2b. Buggies (grounded.wiki.gg *Buggies*, read 2026-10-02).** Rideable bugs are hatched in a Hatchery (24 in-game hours), one active
at a time, each with two unique skills that **cost stamina bars** ("This skill costs 2 stamina bars to use"), their
own health per tier, resistances and weaknesses, and a shared 30-slot inventory. Riding a red soldier ant buggy
**makes that species of soldier ant neutral** — the "how a species treats you" perk again, this time from a mount.

### S26-S29. Core Keeper (Pugstorm) — core-keeper.fandom.com *Character*, *Armor* (+ *Octarine armor*, *Scarlet armor*), *Cooking*, *Foods* (read 2026-10-02 through the wiki's API); four Steam forum threads (read 2026-10-02 in full)

**Stat lists with decimals (S26).** Core Keeper gear shows a list of effects per piece: Octarine Helm at level 15
reads "+36 max health (+7) / +18 armor (+3) / +7% mining speed (+1%)", where the brackets show what upgrading added.
A full set adds lines such as "+6.4-9.3% range attack speed" and set bonuses like "Attack speed is increased by 0.2%
for every percentage of missing health". Every piece has 9-11 upgrade levels, each nudging several decimals.
There is a character stat screen that lists totals.

**Hidden cooking numbers (S28).** "Each ingredient has hidden effects used to determine the final result. These
effects are different from the ingredient's effects when eaten individually, and **are not shown in-game**." Players
learn cooking from the wiki.

**What players say (S29, Steam forums):**
- *"Gear Comparison"* (Sept 2025): a player asks for a way to compare a worn item with one in the backpack; the
  answer is that there is no side-by-side comparison, so put the items next to each other or use the wiki.
- *"way to check movement speed bonus?"* (Apr 2023): "The other bonuses are listed in the character stat screen" —
  movement speed was not, so the player could not tell what their gear did.
- *"Is there a limit how many food buffs you can have? Or how do they stack?"* (Feb-Mar 2026, four years after
  release): one player says the **last** food eaten wins, another says the **strongest** wins, a third says that with
  many buffs "some buffs will not appear in your buffs list and in your stats screen". Players still disagree about
  the stacking rule — the rule is not shown anywhere in the game.
- *"The Armor system is pretentious"* (Mar 2026, 29 replies): the armor number "doesn't feel like an option"; a
  reply says many armor pieces "offer mediocre %dmg stats or low amounts of %crit… quickly overshadowed by other
  options with bigger numbers". Small percentages lose to big ones; defense as a stat gets ignored.
- *"Scarlet Armor Set - Bug"* (2022): the set says "+3% critical chance" per kill, but the player's **stat sheet**
  showed attack speed rising instead — a stat sheet computed from the real numbers let a player catch a bug.

**What Bug Farmer takes from it:** show the stacking rule on screen; never hide a number the player needs to plan;
give a side-by-side "what changes" view (players ask for it even when stat lists exist); keep every meter on the
sheet (a missing one becomes a forum thread); prefer fewer, chunkier effects to many small percentages.

### S30-S32. RimWorld (Ludeon) — rimworldwiki.com *Stat* (order of operations) and *Move Speed* (read 2026-10-02 through the wiki's API); Ludeon's official translation repository on GitHub, file `Core/Keyed/Dialog_StatsReports.xml`, which carries the English originals of the stat-breakdown labels (read 2026-10-02)

**The breakdown tooltip.** RimWorld's info window explains every stat as a ledger. The label set (English
originals, S32) shows its shape: **"Base value"**, then sections such as **"Relevant traits"**, **"Relevant
gear"**, **"Relevant health conditions"**, **"Skills"**, **"Health"**, then multipliers ("Multiplier for light {0}",
"Multiplier for difficulty {0}", "Quality multiplier"), and finally **"Final value"** (and "Max value" where a cap
applies). For compound numbers it even prints the formula: "DPS = Melee damage * Melee hit chance / Cooldown in
seconds". This is the gold-standard answer to "where does this number come from?" — every source is named with
its contribution, and the total is shown last.

**Fixed order: adds, then multiplies, then curve, then clamp (S30).** The wiki reproduces the game's order:
start from the base value; add all flat offsets (traits, health conditions, gear, genes...); then multiply by all
factors; then apply "stat parts" (situational rules such as light level); then a post-process curve; then
rounding; then **clamp to the minimum and maximum**. The *Move Speed* page (S31) shows why order matters: a
flak vest's -0.12 cells/second becomes -0.18 for a pawn with bionic legs, because the offset is applied before
the bionic multiplier. Fixed order makes the result predictable; the breakdown makes it visible.

**Hide what is at default (S30).** "Certain stats like Sleep Fall Rate are **hidden from the stat view until they
are actively being modified away from default values**." RimWorld has hundreds of stats and stays readable by only
listing the ones that are not at their normal value.

**A warning from the same wiki.** The *Reprocessor stomach* page notes that "contrary to what is displayed on the
item info card" the effect is applied differently in code (found through the wiki's text search). A breakdown is
only trustworthy if it is generated from the same code path that computes the value.

**What Bug Farmer takes from it:** a one-glance sheet backed by a hover breakdown ("Base 4 · Beekeeper's outfit +2 ·
Honey cake +1 · Cap 10 → 7"); a fixed order of operations; only show a perk or stat line when it is not at its
normal value; generate the breakdown from the same function that computes the number.

### S33-S35. Necesse (Fair Games) — necessewiki.com *Food*, *Simple Food*, *Fine Food*, *Gourmet Food*, *Hunger* (S33), *Buffs* (S34), *Armor* + *Trinkets* (S35) (read 2026-10-02 as raw page text)

**Food as named quality bands (S33).** Food comes in three named qualities — *Simple*, *Fine*, *Gourmet* — and
each has sub-tiers that the game shows **by the colour of the item's name** (for Gourmet: blue = 12-minute buff,
yellow = 16 minutes, purple = 20 minutes; Fine: white = 4 minutes, green = 8 minutes). The quality also sets how
happy the food makes a settler who eats it (+10% / +20% / +35%). The hunger meter is optional at world creation; at
5% you get *Hungry* (no health regeneration), at 0% *Starving* (slow, losing health).

**Colour bands for a growing bonus (S34).** The *Amethyst* armor set's bonus scales with a stat, and its buff icon
**changes colour by size band** — blue under 10%, green 10-19%, purple 20-39%, orange 40% and over — each with a
joking tooltip ("Pfft, weak" … "Please don't hit me!"). One glance tells you roughly how strong it is right now.
Stacking buffs show their stack count (*Barkskin*: "+10 Armor per stack, but lose a stack when hit").

**Armor and trinkets (S35).** Each armor point removes 0.5 damage per hit. Sets have a set bonus and lean towards a
class (melee, ranged, magic, summoner). Once the late-game "incursions" unlock, **every armor piece can be upgraded
to a similar defense level, so an early set stays useful for its set bonus** — the set's identity outlives its
numbers. Trinkets (accessories): 4 slots plus 1 "ability" slot at the start, raised to 8 by boss rewards.

**What Bug Farmer takes from it:** named food quality bands with a colour per band are easy to learn; colour bands
for "how big is it right now" work well for any scaling effect; letting old outfits be upgraded keeps a role
outfit's perks relevant when its armor would otherwise be outgrown.

### S36-S37. Don't Starve / Don't Starve Together (Klei) — dontstarve.wiki.gg pages (read 2026-10-02 as raw page text)

Pages read: *Health*, *Hunger*, *Sanity* (S36), *Armor/DS*, *Winter Hat* (S37).

**Three meters as pictures (S36).** Health is a heart-shaped gauge that "shrivels and empties"; Hunger is a stomach
that shrivels; Sanity is a brain. The picture does most of the work (whether and when the exact number shows was not
checked; see the unverified list). **A small
animated arrow over the Sanity icon shows whether it is rising or falling, and the arrow's size shows how fast**
— a rate indicator, so you can see that your hat is slowly helping, or that the dark is slowly hurting. Low sanity
also changes the world itself (the screen shakes, colours drain, shadow creatures appear at fixed thresholds such
as 75%, 50% and 15%), so the meter is felt, not just read.

**Clothing has one job each (S37).** A Winter Hat restores 1.33 sanity per minute and is "tier 2 warm clothing"
(insulation 120), wearing out over 10 days. Armor is a single percentage of damage absorbed (grass suit 60%, log
suit 80%, marble suit 95%) plus durability, and **many pieces carry a clear trade-off**: the marble suit gives 95%
but -30% movement speed; night armor gives 95% but drains sanity. Some armor changes how a creature treats you
(cactus armor: elephant cacti ignore the player). Two armors multiply: damage × (1 − first) × (1 − second); the
wiki notes that which piece counts as "first" is "difficult to tell without getting hit first or using a mod" — a
hidden rule that only affects which item wears out.

**What Bug Farmer takes from it:** pictures for meters; a rising/falling arrow (sized by rate) for anything
draining or filling; outfits whose drawback is as visible as their benefit; perks that change how a creature
treats you.

### S38-S39. Hades (Supergiant) — hades.fandom.com *Boons* (S38) and *Pom of Power* (S39) (read 2026-10-02 through the wiki's API)

*Boons* are the run-long perks the gods give. Two things matter for Bug Farmer:

**Slots by job (S38).** Five boons attach to a named action — Attack, Special, Cast, Dash, Call — and **each action
holds exactly one** ("you cannot have both Cast from Aphrodite and Dionysus"). Another god may offer to *replace* the
one in that slot. Every other boon is a passive with no slot limit. Slotting by job is what keeps a growing pile of
perks understandable: you always know which perk changes your dash.

**Fixed size steps, by name (S38, S39).** Boons come in four rarities — Common, Rare, Epic, Heroic — each "more
powerful… the same numbers get bigger", and a separate level raised by an item (Pom of Power). Levels give most of
their value in the first two or three and then fall off to a floor; **"the exact formula is currently unsolved"**
for how rarity and level combine, and pom scaling is "not entirely consistent" between boons. Players read the
rarity colour and level instead of a formula, which works for a run-based game but would frustrate in a game where
you plan a whole outfit.

### S40-S42. Slay the Spire (Mega Crit) — slay-the-spire.fandom.com *Relics* (S40), *Buffs* (S41), *Strength*, *Pen Nib*, *Happy Flower*, *Keywords* (S42) (read 2026-10-02 through the wiki's API)

**Relics are one-line, exact, permanent perks (S40).** Each relic is an icon with a single sentence that contains
the exact number: "At the end of combat, heal 6 HP." "Start each combat with 10 Block." "Every 3 turns, gain 1
Energy." No hidden values, no ranges. Rarity (common/uncommon/rare/boss) sets how strong a relic may be.

**Counters on the icon (S42).** Relics that count show the count beside the icon: Happy Flower's number "shows how
many turns have passed since last activation". A patch note shows the cost of a long relic row: counters were drawn
in the wrong place "when the player has too many relics".

**The stacking type is a named rule (S41).** Every buff declares how it stacks: by **intensity** (the number is the
power: Strength 3 = +3 damage), by **duration** (the number is turns left), as a **counter** (the number counts down
uses: Artifact 2 = blocks the next 2 debuffs), or **not at all**. The icon always shows that one number. Learning
three stacking words is enough to read every buff in the game.

**Result previews and keywords (S42).** The game shows the final damage on a card *before* you play it, with all
modifiers already applied (Pen Nib: "correctly shown in the tooltip before confirming your Attack"). Game terms
appear **in bold** in every description and have their own explanation — "Keywords" — so a perk's text can stay
short. Strength is capped at 999 / -999, and some sources cap themselves (Girya: "up to 3 times per run").

### S43. Diablo IV (Blizzard) — the counterexample: Blizzard's own announcement *Galvanize your Legend in Season 4: Loot Reborn* (news.blizzard.com, 30 April 2024), read in full 2026-10-02, cross-checked with diablo.fandom.com *Season of Loot Reborn*

Diablo-style loot is the classic "too many stats" case, and Blizzard's own post explains why they cut it back:
"One of our several goals for the Itemization changes is to make it easier to understand which items are upgrades
when they drop. We reduced the number of affixes on items (down to 3 on Legendary items, 2 on Rare items) and made
these affixes more effective. Instead of seeing an affix that relies on conditional values (+10% damage on
non-injured Elites), you'll see affixes such as base increases to your Movement Speed, Max life, or single ranks of
a Core Skill." ("Affix" = one random stat line on an item.) They also dropped fewer items so players spend "less
time sorting through the many items that drop", and moved the depth into crafting (Tempering adds a chosen line;
Masterworking boosts lines, **recolouring a boosted line blue, then yellow, then orange**).

**Lessons for Bug Farmer:** fewer, bigger, unconditional lines beat many small, conditional ones; "is this an
upgrade?" must be answerable at a glance; put choice in crafting (deliberate) rather than in random rolls; colour can
mark "this line has been improved".

### S44-S46. Monster Hunter (Capcom) — monsterhunter.fandom.com *MHW: Skill List*, *MHWI: Skill List* (S44), *MHWilds: Skills* (S45), and the in-game help file *Activating Skills* from Monster Hunter Freedom 2 (S46) (read 2026-10-02 through the wiki's API)

Monster Hunter's armor *skills* are the closest thing in games to Bug Farmer's standalone perks.

**A skill list with levels, in fixed steps (S44, S45).** Every armor piece carries a few named skills at a level
(1-3 per piece). The game adds up the levels across all worn pieces and decorations, **up to each skill's own
maximum** (1, 3, 5 or 7). Each level is a fixed, written step: Critical Eye is "Affinity +4% / +8% / +12% / +16% /
+20%"; Attack Boost "+3 / +5 / +7 …". Some skills use words for the steps instead ("Slightly extends range / Extends
range / Greatly extends range"). Many skills are simple yes-or-no unlocks ("Activates skill effect", "Lets you use
blast coating") — perks that change what you can do, not just how much. The Wilds page also lists *Group Skills* /
*Set Bonus* skills that switch on when enough pieces of one family are worn.

**Raising a cap is itself a reward (S44).** In *World: Iceborne*, "Secret" skills on top-end sets **"raise the maximum
level"** of another skill (Agitator Secret takes Agitator from level 5 to 7). The cap is visible, and lifting it is
something you earn.

**The older threshold model (S46).** In earlier games skills were *points*: "Once you exceed 10 Skill Points, you will
activate a skill… 20 or more points will activate more potent skills, though you could also activate a skill with a
negative impact if your Skill Points hit -10." Players had to do arithmetic across five pieces to know which skills
were on; the newer level-and-cap model replaced it with a list you can read.

**What Bug Farmer takes from it:** perks in named steps with the number written on each step; a visible cap per
perk; yes-or-no "unlock" perks alongside size perks; a rare item that lifts a cap is an exciting top-tier reward
(Bug Farmer's "items may break the pattern" case). Avoid the old point-threshold model — it is arithmetic, not play.

### S47-S48. Elden Ring (FromSoftware) — eldenring.wiki.fextralife.com *Stats* (S47), *Status Effects* and *Buffs and Debuffs* (S48) (read 2026-10-02 as whole pages)

**Icon border shape tells you the source (S48).** Effects show as icons under the health bar. "Icons with **square
borders** represent permanent effects or effects which come from a permanent source such as a Talisman"; "Icons with
**diamond borders** represent temporary effects"; "Icons with **no border** represent effects which seem to be
reactive with the world or have contextual requirements". One glance separates "my gear does this" from "my drink
does this, and it will run out".

**Stacking by category (S48).** "Persistent Buffs, their effects denoted by square borders, can be freely stacked"
(weapons, armor and talismans with special effects). "Temporary Buffs, denoted by diamond borders, fall into
categories, **only one of each can be active at a time**": Armament, Body, Aura, Health Regen. Buffs "often stack
multiplicatively (e.g. … +20% Damage and … +20% Physical Damage would result in +44% Physical Damage)". This is the
same "one of each kind" model as Bug Farmer's one-meal / one-potion rule, generalised to named categories.

**The status screen reflects gear (S47).** "Within the Status Menu, you can check your level, attributes, base stats,
and more. The information shown here also reflects changes to your attack, defense, and resistances bestowed by
armaments and armor that you have equipped."

**What Bug Farmer takes from it:** use icon **shape** for source (worn = square, timed = round, place-based = no
frame), so colour stays free for good/bad; "one per category" is a proven, explainable stacking rule — but the
categories must be *named in the game*, not only on a wiki (see the unverified list).

### S49-S51. Open-source code: how stats, buffs and stacking are stored

**S49. Veloren (open-source voxel RPG, Rust) — `common/src/comp/buff.rs` on GitLab (master, read 2026-10-02).**
Data shape of one buff:
`Buff { kind, data: BuffData { strength, duration (optional), delay, secondary_duration, misc_data }, cat_ids: [BuffCategory],
start_time, end_time, effects: [BuffEffect], source: BuffSource }`.
- *Source is recorded on every buff*: `BuffSource` is one of Character (who, with which tool), World ("like a
  poisonous fumes from a swamp"), Command, Item, Buff (an after-effect), Block, Unknown. That is exactly the field a
  UI needs to colour or frame an effect by where it came from.
- *Stacking is a per-kind rule in code*: by default several buffs of the same kind are kept, **sorted strongest
  first, and only the strongest is active** ("Checks if multiple instances of the buff should be processed, instead of
  only the strongest" — only PotionSickness and Resilience add up). Weaker copies wait underneath and take over when the
  strongest ends. Re-applying an identical buff (same strength, categories and source) just **refreshes its end time**.
- *Food queues*: `Saturation` (eating) "queues" — a second meal waits until the first finishes instead of replacing it.
- *Drinking potions back-to-back is limited by a debuff*: `PotionSickness` "Results from drinking a potion. Decreases
  the health gained from subsequent potions." — a soft alternative to a hard one-potion rule.
- *Categories as tags*: `PersistOnDeath`, `RemoveOnAttack`, `RemoveOnLoadoutChange`, `SelfBuff` ("Ensures only 1 buff
  with this category can be present"), `WeaponCoating` (also only one). Effects declare `Additive` or `Multiplicative`.
- *UI hint in code*: for stacking kinds the HUD iterates "in reverse order to show the timer of the soonest one to
  expire".

**S50. Cataclysm: Dark Days Ahead (open-source survival roguelike) — `doc/JSON/EFFECTS_JSON.md` (GitHub master, read
2026-10-02).** Effects are pure data (`"type": "effect_type"`). Stacking behaviour is a set of fields:
`max_intensity`, `max_effective_intensity`, `int_add_val` (how much a repeat application raises intensity),
`int_decay_step`/`int_decay_tick` (fading), `max_duration`, `dur_add_perc` (a repeat adds this % of its duration — 100
by default, can be less, even negative). **Each intensity can have its own name** (the example: "Tipsy", "Drunk",
"Trashed", "Wasted"); `rating` is good / neutral / bad / mixed and drives colour; `show_intensity` toggles "Weakness
[142]" vs "Weakness". The descriptions are short on purpose: "**Stats and effects do not need to be included, and will
be automatically generated from the other effect data**." Stat changes are `base_mods` plus `scaling_mods` (per
intensity), with optional min/max values a single effect may push a stat to.

**S51. Luanti (formerly Minetest) — the `player_monoids` library README (GitHub minetest-mods, read 2026-10-02).**
The problem it solves is a real stacking exploit: "a player could be under a speed boost effect… and then sleep in a
bed. If the bed mod resets the player's speed, it might remove the boost entirely… potentially leading to exploits
such as **permanent speed boosts**." The fix: never write a stat directly. Each stat is a *monoid* — a declared
`combine` rule (multiply, or `max` for "strongest wins"), an `identity` (the "no change" value) and an `apply` step.
Every change is added with **a named id** (`add_change(player, 2, "mymod:zoom")`) and removed by the same id, and the
value is always recomputed from the list. "Nested" monoids let one group of changes use "strongest boost only" and
another "worst drawback only" before feeding the main stat.

**What Bug Farmer takes from it (all three agree):** store each bonus as a named entry with a source and an optional
end time; recompute every meter from base + entries by a declared rule, then clamp; declare per effect kind whether it
stacks, takes the strongest, refreshes or queues; generate the tooltip text from the same data. (In a multiplayer game where the server is the authority, a value that is always recomputed from a list of named
entries is also easier to check and to send to other players.)

### S52-S55. Developer patch notes (official announcements on each game's Steam news feed, fetched through Steam's public news API and read in full, 2026-10-02)

These show what developers had to *add later* because players needed it — the strongest evidence of what a sheet
must have from day one.

**S52. Grounded (Obsidian):**
- *Into the Wood update* (1 Feb 2022): "Status Effects are now displayed with tooltips on the Backpack and Status
  screens. Active Status Effects will also be displayed on the HUD" — effect tooltips and HUD icons arrived after
  launch into early access.
- *Home Stretch update* (25 Aug 2022): "A line will show up on your SCA.B Health and Stamina bars to indicate where
  '100' health or stamina is at. **This is to help show how much growth your health and stamina get from Molar upgrades
  or status effects.**" — a base marker on the bar, so bonus amount is visible.
- *Super Duper update* (25 Apr 2023): enemy status effects shown "beneath the enemy health bar"; "Active Mutation
  status effects display in the UI next to your other status effect icons"; coziness: "one bed will provide lots of
  coziness, but a second bed of the same type will only give you a little more" (duplicates give less), and "your
  current coziness level will show on your HUD **if it is at least 1**" (hide at zero).
- *Update 1.3* (13 Nov 2023): "Black Widow armor status effect values **normalized so they're all equal instead of being
  different per piece**" — tidying sizes into a standard.
- *Patch 1.4.1* (29 Apr 2024): the trinket effect "+Damage Resist" raised "from 10% to 50%" — a size that was too small
  to matter.

**S53. Core Keeper (Pugstorm):** the character stats window kept growing and needed fixes: "Added missing description for
the burn damage in player stat window" (0.5.0, Nov 2022); "Fixed an error in the calculation of the damage value shown in
the stats window" (0.7.3, Jan 2024); "Added boss damage bonus to character stat window" (1.0.1, Oct 2024); "Hovering Titan
Breath's buff icon now displays the correct percentage" (1.2.1.3, May 2026); and, answering the 2025 forum request, version
1.3.0.1 (21 Sept 2026) "**Introduced the ability to compare gear**." A gear comparison arrived four years after early access.

**S54. Valheim (Iron Gate):** "Tooltips showing total currently equipped special stats now include those from status
effects" (0.218.14, May 2024) — a totals tooltip that had to learn to include timed effects.

**S55. Necesse (Fair Games):** "Rebalanced armor values, **making the different tiers more clear**" (0.20, 2020); "Buff icons
are now placed on the right side of your health bar instead of under it" (0.22, Aug 2023).

**What Bug Farmer takes from it:** build in from the start what these games bolted on: effect tooltips, base markers on
meters, a compare view, totals that include timed effects, and sizes normalised into clear tiers.

### S56-S57. Two technique sources on caps and percentages

**S56. Path of Exile (Grinding Gear Games) — pathofexile.fandom.com *Resistance* (read 2026-10-02 through the wiki's
API).** The game most often named for having too many stats still has one very good display trick for caps: resistances
are capped (the page gives a hard cap of 90%; its worked example uses 75%, the commonly cited default), and the
character panel shows the capped value with **the
uncapped total in parentheses** — "Uncapped resistances are shown in parentheses". Players can see both "I am at the cap"
and "how much spare I have" (spare matters because enemy curses can lower it). The cap itself can be raised by rare
items and passives. The game also deliberately lowers resistances as the story advances (-30% after part one, -60%
after part two), so gear that was enough stops being enough.

**S57. League of Legends (Riot) — wiki.leagueoflegends.com *Armor* (read 2026-10-02 as raw page text).** Armor
reduces damage by the factor 100 / (100 + armor), so it never reaches 100% and needs no hard cap. The page's key point:
"Every 1 point of armor adds 1% to the effective health pool" — "By definition, armor does not give diminishing returns
of effective health." The page carries an editors' note asking people *not* to edit it to say armor has diminishing
returns, which shows how often players misread a percentage that grows more slowly (60 armor = 37.5% less damage, 120 =
54.5%) as "worth less".

**What Bug Farmer takes from it:** if a protection is shown as a percentage, show the cap and any spare beyond it; pick
one stacking formula and teach it once; a "points to percent" curve avoids a hard cap but invites "diminishing returns"
confusion — showing what the protection *does* ("a wasp sting takes 2 hearts instead of 3") avoids the argument.

### S58. Grounded players on its stat display — Steam forum threads, read in full 2026-10-02

Found with the Steam forum search for "set bonus description", "stats screen", "description numbers", "vague":
- *"Spider Armor Set Bonus"* (Oct 2022): the set bonus text reads "your body recycles energy with increased efficiency";
  the player guesses it means slower stamina drain and asks why the game does not just say so. Replies point to the wiki
  ("Increases Stamina regeneration rate"); others answer that the game should put this on "an actual character sheet
  instead of being so vague and cryptic" and that one "shouldn't really have to refer to a wiki".
- *"Overall Stats?"* (Oct 2022, 13 replies): a player can see each armor piece's defense and resistance but nowhere the
  **total**; they suggest a small "total defence" and "total resistance" bar or value beside the armor slots. The thread
  then becomes **the real debate**: one side says survival games should not put "math and numbers… in-your-face" and
  that "RPGs these days have turned into spreadsheet simulators"; the other says a single summary place does not clutter
  anything and saves re-doing sums after every gear change.
- *"Shield Durability"* (Jan 2023): "the developers seem to hate the idea of giving us any kind of actual exact numbers";
  one reply argues exact numbers are "a relic from the past" for games like this, and that they would make the HUD less
  readable "(though the buff description could definitely be better)". The asker then **used a memory-scanning cheat
  tool** to measure both shields' durability (500 hits each).
- *"What do the armor set bonuses do?"* (Aug 2020) and *"Armor Set Bonuses"*: set-bonus names "are not very descriptive";
  one player did not know set bonuses existed until reading about them online.
- *"Just Started..."*: armor lists status effects by name "but no description on what these effects are".

**Reading of the debate:** both camps are right about different layers. Nobody objects to a clean at-a-glance display;
the anger is about information that exists in the game but cannot be found at all. A glanceable sheet (dots, icons)
with exact numbers one hover away satisfies both.

### S59. UI breakdowns from screenshots — interfaceingame.com (a public library of game-interface screenshots), full-size images viewed 2026-10-02

(The Game UI Database refused automated access — HTTP 403 — so this library stood in for it; see the unverified list.)

- **Hades — boon choice screen.** Each offer is a card: a diamond icon in the god's colour, the boon's name, **one
  sentence with game terms in bold** ("Your **Cast** is a wide, short-range blast that inflicts **Weak**."), then **exactly
  one stat line with its number in green**: "▸ Cast Damage: 90", "▸ Weak Duration: +5 Sec.", "▸ Weak Damage Reduction:
  +10%". The sentence says what it does; the single number says how much.
- **Hades — the in-run HUD.** A vertical column of diamond slots down the left edge, one per action (attack, special,
  cast, dash, call). **Empty slots show a grey silhouette of the action**, so you can see what you have not filled yet;
  filled slots show the boon's icon. A counter ("+3") sits beside the column — by my reading, the boons not drawn there. The keepsake sits
  at the bottom with its rank as stars (★★★). Health is a bar plus "56 / 125".
- **Monster Hunter: World — forge screen.** The armor piece panel shows defense, decoration slots, five elemental
  resistances as **signed whole numbers** (Vs. Fire 3, Vs. Water -2, Vs. Ice -3…), then **"Skills: Weakness Exploit — Level
  1" with a small pip bar** (one of three pips filled), then **"Set Bonus Skills"** with icons for each piece and the
  piece counts that unlock each bonus ("2 ▸ Agitator Secret", "4 ▸ Artillery Secret"), and a **"Compare"** button.
- **Monster Hunter: World — change equipment.** A status column (attack, affinity, element, defense, the five
  resistances) with a value shown in a highlight colour when the selection changes it, and a "Skill Info" tab for the
  summed skill list.
- **Elden Ring — equipment screen.** Three columns: the item grid, the selected item's numbers, and the full
  **Character Status**. Upgrade bonuses are shown **next to the base, not merged**: "Physical 110 + 15". Equip load reads
  "30.8 / 49.8 — Med. Load" (number plus its meaning). A "Passive Effects" box lists effects, with dashes when empty.
  The button bar offers **"Simple view"**, a toggle between a short and a detailed layout.
- **Diablo IV (beta, French build) — weapon tooltip.** "81 damage per second (**+34**)" with the difference from the worn
  weapon in green; then six small percentage lines, four of them conditional (damage against close / crowd-controlled /
  slowed targets), then a long legendary paragraph — and **the tooltip has to scroll** ("Faire défiler vers le bas").
  This is the picture of the problem the Season 4 rework (S43) fixed. "Shift: Compare" opens a side-by-side view.
- **Slay the Spire — combat.** Top bar: health "39/96" with a heart, gold, potion slots, floor. Directly under it, **the
  relic row**: one icon per relic, a small counter on those that count. Under the player's health bar, buff icons each with
  **one number** (stacks or turns). Enemy health bar with its own debuff icons and numbers; above the enemy, its **intent**
  ("18" with an attack icon). On cards, numbers changed by buffs are recoloured (a boosted "20" damage shows in green).

**What Bug Farmer takes from it:** one sentence plus one number per perk; empty slots shown as silhouettes; a "+N" overflow
counter; base and bonus side by side ("4 + 2"); a simple/detailed toggle; a compare button; numbers that change colour when
something is modifying them; and a warning picture of what happens when lines multiply (a scrolling tooltip).

### S60. Game Accessibility Guidelines (gameaccessibilityguidelines.com) — *Ensure no essential information is conveyed by a fixed colour alone*, *Use an easily readable default font size*, *Avoid flickering images and repetitive patterns* (read 2026-10-02)

- Colour: difficulty telling red from green affects "around 8-10% of males"; "Wherever you can, use colour as a
  back-up for another means of communicating the information, such as text or a symbol, pattern or shape."
- Text size: it cites a 10-foot (TV) guideline of 28 px minimum on a 1080p screen, "as a minimum rather than a target",
  and recommends letting players choose the font size.
- Flashing: avoid more than three flashes a second over 25% or more of the screen — a small icon blinking before it
  expires is within the guideline, a full-screen pulse is not.

**What Bug Farmer takes from it:** every colour code on the sheet (base / bonus / timed / lost; good / bad) needs a second
cue — fill, outline, shape or a symbol — so the sheet still reads in red-green colour blindness; keep expiry blinks
small and slow; make the sheet's text size adjustable.

