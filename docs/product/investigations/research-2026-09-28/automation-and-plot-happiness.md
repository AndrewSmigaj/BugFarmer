# Research: farm automation (sprinklers and beyond) and a plot happiness panel

Date: 2026-09-28. Status: RESEARCH (evidence + a recommendation). Nothing here is decided; every number
below is a starting suggestion to be tuned, not a design value.

Two questions:

- **A.** How should sprinklers and farm automation grow over the game — from the watering can, to bought
  sprinklers, to fuel-fed and then powered machines — without making early farming pointless?
- **B.** What should a private plot's "happiness / decoration" panel look like, so the player can see how
  furniture and decorative outfits add to the plot, and understand that duplicates add less and that there
  is a cap?

Our constraints (restated from `docs/gdd/overview.md` §4, §7, §15, §16 and `docs/product/design/game_design.md`
§11.4–11.6): manual farming first (hoe, watering can, rain); crops grow when watered and never wilt; no
seasons; a 14-minute day; small sprinklers sold in the starting village but priced so the player saves up,
bigger ones in the western town of the Locust Farmland; automation grows manual → fuel-fed → electric
(wind turbines, solar, a power unit that powers a radius); no hired NPC workers; machines take chores off
the player but never play the game for them; the slow, capacity-capped autonet is the only automatic
catcher; Modern Wares in the village sells powered appliances the player can't power yet (except inside the
Mayor's small powered area). Private plots are bought through City Hall and are invite-only; decorations
and decorative outfits give small bonuses that shrink with each duplicate of the same item, under an
overall cap; the plot needs a panel that shows its happiness and related values.

The search angles used are named at the start of each question's findings (§3).

**In short (details and reasons in §3):**

- **A — automation ladder (for proposal P22).** Four rungs, each taking away a *different* chore: (0) watering
  can, rain and straw mulch; (1) a **small sprinkler sold in the village**, priced as a savings goal, watering the
  3×3 around it at dawn from its own small tank that rain refills; (2) in the **western town**, a **large 5×5
  sprinkler** fed by a **water tower** that serves every sprinkler within a radius, filled by a **fuel pump** that
  needs feeding every few days; (3) an **electric pump** inside a powered area — no fuel, never runs dry, and power
  acts as pressure so every sprinkler reaches one ring further. Planting and **harvesting stay manual at every
  rung**. Water and electricity then share one picture — a source serving a radius, shown while placing.
- **B — plot happiness panel (for proposal P26).** A layered panel: a headline (face, band word, a bar whose end
  is the cap, and the effect in plain words), a breakdown folded by category that shows **every copy's value side
  by side** ("Sofa ×3 +8 +4 +2"), a short "try next" hint, and an on-demand view on the plot that outlines each
  decoration by what it adds (full / less / nothing) — plus a floating "+8" or "+2 (3rd sofa)" while holding a
  decoration. It opens from a small on-screen plot badge, the plot's entrance sign, and an inventory button.
  Suggested duplicate rule to go with it: each copy counts half the one before, and the fourth adds nothing.

## 1. Source table

| # | Source (URL) | Concrete technique / numbers | Fits our constraints? |
|---|---|---|---|
| A1 | Stardew Valley wiki — Sprinkler, Quality Sprinkler, Iridium Sprinkler (https://stardewvalleywiki.com/Sprinkler, https://stardewvalleywiki.com/Quality_Sprinkler, https://stardewvalleywiki.com/Iridium_Sprinkler) — deep-read | Three tiers, all water once every morning, only tilled soil. Sprinkler: the 4 tiles above/below/left/right, recipe at Farming level 2 (1 copper bar + 1 iron bar). Quality: the 8 tiles around it (3×3), Farming level 6 (iron bar + gold bar + refined quartz), sell 450g; also sold at random by the Traveling Cart for 1,350–2,250g and given as bundle/festival/prize rewards. Iridium: the 24 tiles around it (5×5), Farming level 9 (gold bar + iridium bar + battery pack), sell 1,000g; Krobus sells one each Friday for 10,000g. Can't sit on sand; a torch can sit on top (1.6). | Strong fit for the *shape* of a ladder (3 tiers, each a clear jump in area, costed in the next metal). Our twist: we sell the first tier in a shop rather than locking it behind a skill level (we have no skill levels). The daily "morning" pulse matches our day-transition design in `architecture_farming.md`. |
| A2 | Stardew wiki — Pressure Nozzle (https://stardewvalleywiki.com/Pressure_Nozzle) and Enricher (https://stardewvalleywiki.com/Enricher) — deep-read | Late add-ons (added in 1.5), one per sprinkler, and a sprinkler takes one or the other, never both. Nozzle grows each tier by one ring (Sprinkler → 3×3, Quality → 5×5, Iridium → 7×7). Enricher is loaded with fertiliser and spends one unit per tile when seeds are planted in range. Both bought from Qi's Walnut Room for 20 Qi Gems (the wiki's wording suggests a set of 4 per purchase — see section 4). | Good fit: "upgrade what you already own, choose one of two add-ons" keeps old sprinklers useful and adds a small choice instead of a new item that replaces the old one. Fertiliser is already decided for our game (compost is a source), so an enricher-like add-on has something to spend. |
| A3 | Stardew wiki — Junimo Hut (https://stardewvalleywiki.com/Junimo_Hut) — deep-read | Bought from the Wizard for 20,000g + 200 stone, 9 starfruit, 100 fibre, after a quest chain. Three helpers harvest ripe crops in a 17×17 square around the door, drop them in a bag of 36 slots, stop at 7:10pm, don't work in rain or winter, give no farming experience. | Mostly *doesn't* fit: it is the "harvest for you" step, i.e. hired hands in a costume. Our rule (machines ease chores but never play for the player) and "no hired workers" argue against automatic harvesting. Useful as the boundary marker: watering is the chore, harvesting is the reward. |
| A4 | Stardew wiki — Auto-Grabber (https://stardewvalleywiki.com/Auto-Grabber) and Auto-Petter (https://stardewvalleywiki.com/Auto-Petter) — deep-read | Auto-Grabber: Farming level 10, 25,000g from Marnie, collects animal products into a 36-slot box, but gives no experience and loses the +5 friendship of collecting by hand. Auto-Petter: 50,000g on the Joja route; gives about 8 friendship a day versus 15 for petting by hand, and stops the daily loss. | The best-fitting pattern in the whole study: **the machine does roughly half the job and the hand still does it better.** It lifts the floor (nothing is lost while you're away) without taking the ceiling (the player who tends by hand still gets more). This is exactly "ease chores, never play." |
| A4b | Stardew wiki — Hopper (https://stardewvalleywiki.com/Hopper) — deep-read | Added in 1.5, late (Qi's Walnut Room: 10 Qi Gems, or the recipe for 50 — 10 hardwood, 1 iridium bar, 1 radioactive bar). It loads items into the machine in front of it, but **"items produced this way will still have to be manually removed from the machine"**, and it won't start the next batch until the output is taken. | Another clean "the machine loads, you collect" line — the same boundary as our rule, applied to stations: automation may feed a machine, the player still takes the result. |
| A5 | Core Keeper — BisectHosting automation guide (https://www.bisecthosting.com/blog/core-keeper-automation-automate-farming-ore-collection-mining-requirements-layouts) and Core Keeper DB sprinkler entry (https://www.corekeeperdb.com/resources/sprinkler) — deep-read (the official wiki pages returned 403/402 to the fetcher) | Automation Table (5 copper + 8 tin bars) crafts conveyor belts, drills, robot arms and the sprinkler (now 8 iron + 8 scarlet bars — a mid-game metal). The sprinkler waters a 5×5 square and needs **no power or wiring**; robot arms, drills and the robot farm arm need an electricity generator (copper) plus wire, and power weakens with wire length. Automated farming and mining **give no skill experience.** | Partial fit. The split "watering needs nothing; moving/harvesting needs power" is the useful idea. The conveyor-and-robot-arm harvest line goes further than our rule allows (it plants and harvests for you). |
| A6 | Terraria wiki — Planter Box (https://terraria.wiki.gg/wiki/Planter_Box) — deep-read | No watering and no sprinklers at all. Herbs grow in planter boxes (1 silver each from the Dryad, available from the start since 1.4.5). Harvesting a blooming herb with the Staff of Regrowth (or while holding its seed) **replants it automatically**. | Useful counter-example: Terraria "automates" farming by folding two actions into one (harvest + replant), not by removing the player. A replant-on-harvest tool is a cheap, rule-safe convenience we could borrow. |
| A7 | Dinkum wiki (fandom, read through its MediaWiki API): Sprinkler, Advanced Sprinkler, Water Tank, Windmill, Solar Panel, Licences, Farming (https://dinkum.fandom.com/wiki/Sprinkler, …/Advanced_Sprinkler, …/Water_Tank, …/Windmill, …/Solar_Panel, …/Licences, …/Farming) — deep-read | Sprinklers **do nothing without a Water Tank** in range: Sprinkler 3×3 (8 tiles), Advanced 5×5 (24 tiles), both run only 7–9am. The Water Tank (2×2) feeds every sprinkler within a 22×22 square (one tank can feed 24 advanced sprinklers = a 25×25 field) and refills watering cans. Unlock: Irrigation Licence level 1 (1,000 permit points, after Farming Licence 3) → sprinkler + tank; level 2 (4,000 points) → advanced sprinkler. Windmill: speeds up furnaces, grinders, BBQs etc. **within 14 tiles of each side (30×30), halves their time, doesn't stack, doesn't work indoors.** Solar panel: 18×18 range, commissioned for 400,000 Dinks + parts. A **Tape Measure** tool shows the range of any range-based object. | Very strong fit for our "a power unit powers a radius" plan: Dinkum already ships the *source → consumers within a square* model twice (water tank → sprinklers; windmill/solar → machines), with a tool that draws the range. The "doesn't stack" rule keeps overlapping sources from being a trap. |
| A8 | Coral Island wiki (fandom, via API): Sprinklers & attachments, Sprinkler I/II/III, Auto harvest, Auto SFH (https://coralisland.fandom.com/wiki/Sprinklers_%26_attachments, …/Sprinkler_I, …/Sprinkler_II, …/Sprinkler_III, …/Auto_harvest, …/Auto_SFH) — deep-read | Sprinkler I: 3×3, Farming mastery 2, and **one is mailed to the player as a gift after a farming quest** ("you can craft as many of these as you need"). Sprinkler II: 5×5, mastery 6. Sprinkler III: 9×9 (80 tiles), mastery 9, needs a battery. One attachment per sprinkler: auto-fertiliser, auto-seed, auto-harvest (20 crop slots), or "Auto SFH" which **plants, fertilises and harvests** — developed at a Laboratory, needs a battery. Sprinkler watering earns no farming points; harvesting through the attachment does. | Two lessons. (1) The free first sprinkler is a good way to show the player what they are saving for. (2) Coral Island's attachment chain ends with a sprinkler that farms the plot on its own — the exact line our rule forbids. We should copy the attachment idea only for chores (water, fertilise), never for planting and harvesting. |
| A9 | Sun Haven wiki (fandom, via API): Farming, Watering Can Totem, Sunite Watering Can (https://sun-haven.fandom.com/wiki/Farming, …/Watering_Can_Totem, …/Sunite_Watering_Can) and the official wiki FAQ (https://sunhaven.wiki.gg/wiki/Frequently_Asked_Questions) — deep-read | **No sprinklers at all** (the FAQ says so plainly). Watering relief comes from: bigger watering cans (the Sunite can holds 70 pours, needs Farming skill 40 and 10 sunite bars), a Rain Cloud spell (5 tiles wide, travels 10 tiles), water fertiliser, and a Watering Can Totem that gives crops in a 5-tile radius (max 120 crops) **a 20% chance to stay watered overnight.** A missed watering delays the harvest by a day (crops don't die). | Shows a second, softer ladder: better *tools* and *partial* relief instead of a machine that removes the chore. Its weakness (players keep asking for sprinklers on the Steam forums) tells us people expect a real sprinkler in this genre. Its "missed day = one day late, no death" rule matches our never-wilt crops. |
| A10 | Factorio wiki — Burner mining drill and Electric mining drill (https://wiki.factorio.com/Burner_mining_drill, https://wiki.factorio.com/Electric_mining_drill) — deep-read | The textbook fuel-fed → electric step. Burner drill: burns wood/coal at 150 kW, mines 0.25 items/s over 2×2 tiles, heavy pollution, needs no electricity (two can even refuel each other on coal). Electric drill: 90 kW from the grid, 0.5 items/s over 5×5 tiles, needs research and circuits. | Strong fit for our manual → fuel → electric ladder: the fuel tier works anywhere but needs feeding and is small; the electric tier is bigger and hands-off but only works inside infrastructure. Each step removes a *different* chore (hauling water → feeding fuel → nothing), which is a clean way to make every tier feel new. |
| A11 | The Escapist — "Fae Farm Fails at the Routine That Makes Farming Sims Great" (https://www.escapistmagazine.com/fae-farm-routine-pointless/) — deep-read | Argues repetition in farming games exists mainly for pacing and structure, and that an upgrade only feels meaningful "because you've done the same thing before" (the horse is exciting because you were slow). Automation (sprinklers, helpers) should free stamina for new activities; by the end game farming is "mostly automated, leaving you to pick up your crops". Fae Farm's failure: after about 8 hours upgrades become only "more stamina, water more crops at once". | Fits and sharpens our plan: the manual watering period is *needed* (it is what makes the first sprinkler feel good), but each automation step must also open something new to do, not just shave numbers. The end state it describes (you still pick up your crops) is our line too. |
| A12 | Fields of Mistria — fan wiki "Sprinklers: Unlock, Range & Layout" (https://fieldsofmistria.run/farming/sprinklers) — deep-read; the design reason from search results of the game's Steam forum (https://steamcommunity.com/app/2142790/discussions/0/510701289425923969/) | Its sprinklers ("Water Sprite Statues") come **late** (Woodcrafting 20 plus a treasure box behind a late-game seal; the large one at Woodcrafting 30). Standard: 5×5 (24 crop tiles); large: 7×7 (48). **They run on fuel**: an Essence Stone lasts 1 day (tiny), 5 (small), 10 (medium), 20 (large) or 40 days (giant); no charge is used on rainy days. They **don't trigger the perks that reward watering by hand**, so the fan guide recommends automating big fields and still hand-watering a small bed. Players complain that early watering eats their energy before the day starts. | The most direct precedent for our "fuel-fed" tier: a sprinkler that needs feeding every so many days, with rain saving fuel. It also repeats the Auto-Petter lesson (A4): keep a small, real reason to do the chore by hand. Its very late unlock is the pitfall on the other side — players felt the manual phase ran too long. |
| A13 | Steam — Stardew Valley forum thread on watering cans and sprinklers (https://steamcommunity.com/app/413150/discussions/0/357284767251485949) — deep-read; plus search-level results from related Stardew threads | Stardew's first "automation" is a *tool*: upgraded cans water 3, 5, 3×3 or 3×6 tiles by holding the button. Players say the copper/iron cans come first "since you'll get those before you have gold available for the sprinklers", and that quality sprinklers make the can nearly useless by summer. Related threads (search-level): farms of 50+ plants use the whole energy bar and half the day; players bank bars to craft 10–15 sprinklers the moment they can. | Confirms the order players experience: bigger can → first sprinklers → the "I don't water any more" moment. Our watering cans are capacity-only by decision (D12: small and large, no metal tiers), so the first sprinkler carries more weight for us than in Stardew and should arrive a bit earlier. |
| B1 | Necesse wiki — Settlements (https://necessewiki.com/Settlements) — deep-read | Settler happiness is a sum of capped parts: food quality (+10/+20/+35%), food variety (0–1 foods 0%, 2–4 +10%, 5–7 +20%, 8–11 +30%, 12+ +40%), room size (up to +20% at 60+ tiles), **furniture variety by number of UNIQUE types: 1 = +4%, 2 = +7%, 3 = +10%, 4 = +13%, 5 = +15%, 6 = +17%, 7+ = +20% (cap)**, settlement size, bed-sharing penalty (−20% for 2 … −50% for 5+), −10% each for no floor / no light. Overall cap 100%. Named bands ("Somewhat Happy" at 50%+ … "Extremely Happy" at 90%+). Happy settlers give better prices and take shorter breaks; below 50% they may strike. Settlers also farm, replant and fertilise (they are Necesse's automation). | The furniture-variety table is almost exactly our "variety pays, with a cap" rule, already tuned in a shipped game. Their settlers-as-workers are what we *don't* have — noted, not copied. |
| B2 | "Necesse 1.3 Settlement Changes" guide, deilru.com (https://deilru.com/necesse-settlement-1-3-update-guide/) — deep-read (a fan guide, secondary) | How Necesse *shows* happiness: a coloured badge per settler (green = 80+ and rising, yellow = 50–79 steady, red = below 50 and falling) with a hover tooltip; a "How are you doing?" screen with three bars (happiness, hunger, recreation) and a **"Thoughts:" list of every modifier with its number**. Leisure activities lose effect when the same kind is repeated, **down to 5% of normal.** | Direct evidence for the "summary badge + one-click breakdown list" pattern, and a second shipped example of repeat-use decay being shown to players as numbers. |
| B3 | Terraria wiki — Happiness (https://terraria.wiki.gg/wiki/Happiness) — deep-read (two passes) | Happiness only changes shop prices: buying 75%–150% of base, selling 67%–133%, rounded to 1%. Factors **multiply**: loved biome 88% (buy) / liked 94% / disliked 106% / hated 112%, and the same four steps per loved/liked/disliked/hated neighbour within 25 tiles; solitude bonus 95% if no more than 2 other NPCs within 25 tiles and no more than 3 between 25–120 tiles; each NPC beyond three within 25 tiles adds a 105% crowding step. Most vendors sell pylons when another NPC is nearby. **The in-game "Happiness" button shows dialogue only, no numbers**, and the NPC says what affects them *now*, not what would help; preferences are otherwise learned from the Bestiary portrait background or by trial and error. | Lesson by failure: charming but opaque. The biome/neighbour idea is a nice flavour, but a dialogue-only readout does not let a player plan. See B4. |
| B4 | Fan-made Terraria happiness calculators (search results: https://github.com/Machine-Maker/terraria-happiness-planner, https://synchromic.github.io/terraria-npc-happiness/, https://mcjmzn.github.io/TerrariaHappinessCalculator/, https://xgamingserver.com/tools/terraria/npc-happiness, https://hawk.bar/TerrariaHapinessCalculator/, https://terrariadb.com/) — search-level evidence, not deep-read | At least six separate community tools exist just to compute what the game won't show. | Evidence that hiding the numbers pushes players out of the game to a spreadsheet. Our panel should show the numbers the player needs to plan. |
| B5 | RimWorld wiki — Room stats (https://rimworldwiki.com/wiki/Room_stats), read through the wiki's MediaWiki API — deep-read | A room's **Impressiveness** comes from four stats (wealth, beauty, space, cleanliness). Each is scaled to "natural units" (wealth ÷ 1500, beauty ÷ 3, space ÷ 125, 1 + cleanliness ÷ 2.5), then anything above 1 is curved with **1 + ln(x)** (a log curve = diminishing returns), then combined as 65 × average + 35 × the **lowest** stat — so the weakest stat counts for about half. The number is shown as a named band ("dull" 20–29, "decent" 40–49, … "wondrously impressive" 240+), and the **band**, not the exact number, sets the mood effect (+2 … +8 for bedrooms). The room-stats readout is toggled from a button at the lower right (hotkey G) and Alt shows more. The wiki's own advice: "there are sharply diminishing returns … it is not worth putting a lot of resources into any of the stats beyond a point." | Strong fit for the *maths*: a log curve per source and a "weakest area drags you down" rule both push players toward variety without a hard rule. The four-stat formula is too intricate to copy as-is (the wiki itself says it's impractical to predict in play), which argues for showing a simple band plus a breakdown. |
| B6 | RimWorld wiki — Beauty (https://rimworldwiki.com/wiki/Beauty), via API — deep-read | Every tile has a beauty value (sum of the objects on it; dirt and filth are negative). A pawn perceives the average over an 8-tile radius in line of sight. A **toolbar toggle shows the environmental and perceived beauty of the tile under the cursor**, Alt shows beauty numbers of nearby tiles, and the result appears as a mood line such as "Pretty environment +5" (need 35–65% = neutral; beauty 6+ drives it to 100% = +15). | The per-tile overlay is the precedent for an in-world "what does this spot add" view. RimWorld pairs it with a plain named result line (the thought), which is the part a casual player actually reads. |
| B7 | Nookipedia — Happy Home Academy (https://nookipedia.com/wiki/Happy_Home_Academy), via API — deep-read (all generations; New Horizons section in full) | Animal Crossing scores a house by items placed and **sends a letter** with the score and tips (weekly, Sunday, in New Horizons). NH ranks B/A/S per house size (e.g. first house: S at 15,000+, basement stage: S at 90,000+). NH bonuses are **goals to hit**: 6/10/15/20 furniture in a room (+1,000 each), 4+ items of one series (1,000 × items), a complete set (800 × items), 3+ of one category (500 × items), 70% / 90% one colour (200 / 600 × items), feng shui (+500), lucky items (777 each), wall items (400 each, **limit three**). Deductions: cockroaches (−2,500 each), trash (−500), items facing a wall (−300). Older games counted colour and lucky-item bonuses **only per unique item**. | The HHA is the model for a **goals checklist** ("a complete set", "three of a kind", "a colour theme") and for per-bonus limits ("wall items, max three"). It rewards *coherence* (sets, colours), which is the opposite pull from "every different item adds a bit" — worth offering both kinds of goal. Its weakness for us: feedback comes days later in a letter, so the player can't see cause and effect while decorating. |
| B8 | The Sims wiki — Environment (https://sims.fandom.com/wiki/Environment), via API — deep-read | The Sims 1 "Room" / Sims 2 "Environment" need; in The Sims 3 and 4 objects carry an environment rating and a room gives a named moodlet ("Decorated", "Nicely Decorated", "Beautifully Decorated"). Sims 3 rule: a room needs at least 3 objects with 1+ point before it counts; in small rooms (under 5×5) **the first 5 objects count the most and the 6th onward count much less**, with extra measures to stop filling a room with 1-point items; in large rooms (over 15×15) the best 15 count, each at 60%; outdoors the best 10 count, within 10 squares. Mess costs points (puddle −8, broken object −10, no light and no window −5, bare floor or walls −15). | "Only your best N count fully" is another clean diminishing-returns rule, and "named moodlet as the result" is again the readout players actually see. The Sims hides all of the numbers; the wiki had to reverse-engineer them. |
| B9 | Valheim wiki — Comfort, Resting Effect, Rested (https://valheim.fandom.com/wiki/Comfort, …/Resting_Effect, …/Rested), via API — deep-read; plus game8's comfort guide (https://game8.co/games/Valheim/archives/320726) for the on-screen number (search-level) | Furniture is sorted into **categories** (fire, bed, chair, table, rug, banner, garland, lantern, pot, stand, hot tub); **only the best item in each category counts, and "no item stacks with itself".** Items must be within 10 m. Comfort sets the Rested buff: 7 minutes + 1 per comfort level (22 = 29 minutes). The wiki lists the **maximum comfort reachable per biome** (Meadows 5, Black Forest 11, … Ashlands 22), so comfort grows with progress. The Resting icon shows the current comfort level as a number next to it. | The closest shipped example to our plot rule in a survival-crafting game: variety across categories is the only way up, duplicates give nothing, and the reward is a small, non-essential buff. Valheim's "duplicates give zero" is harsher than our "duplicates give less"; the per-biome table is a neat way to show that new zones bring new décor. |
| B10 | Two Point Hospital Steam threads — "Suggestion: Improving the prestige system" (https://steamcommunity.com/app/535930/discussions/0/1737715419900279890/) and "Spamming Prestige" (https://steamcommunity.com/app/535930/discussions/0/1742220359680134789/) — deep-read | Room prestige is roughly a sum of per-item prestige (values hidden from the player) plus a room-size term, converted to levels capped at 5. Players fill rooms with the best value-per-space item — chairs, gold awards, "20 medicine cabinets and all gold award behind them" — which "looks ridiculous". One experienced player says duplicate diminishing returns exist but are "really small". Proposed fixes from players: −40% per extra copy, or 2^(−0.5x) (100% → 71% → 50% → 35% … → about 4% by the 10th copy), and showing the hidden values. | The clearest evidence for our rule and for its *strength*: weak diminishing returns still produce spam. The second copy has to be clearly worse than a *different* item, and the values must be visible. |
| B11 | Game Developer — "Game Design Principle: Transparency" (https://www.gamedeveloper.com/design/game-design-principle-transparency) — deep-read | Information only helps a plan if it can be "grasped almost immediately". Techniques: keep numbers small and in discrete steps, use visual metaphors instead of bare numbers, and offer an optional expert layer (Diablo 3's "advanced tooltips") so casual players aren't swamped. | Supports a layered panel: a simple headline for everyone, exact numbers one click (or hover) deeper. |
| B12 | Parkitect devlog 166 (https://themeparkitect.tumblr.com/post/166476645512/devlog-update-166) — deep-read; decoration-view behaviour from search results (Parkitect guide/forum snippets, e.g. https://steamcommunity.com/app/453090/discussions/1/1741104717711618659/) | Guests have an "Immersion" stat from what they can see (scenery raises it; visible staff paths, haulers, trash lower it); it slows happiness decay; guests leave a scenery rating that feeds the park rating. Visibility is recomputed in the background only where scenery changed. The decoration view paints areas **green (well decorated) or red (guests see something ugly)** and marks the offending objects **pink**, updating live as you cover them. | Precedent for the in-world overlay option: colour the ground by effect and mark the *culprits*, live. Its cost is a full-screen mode; best used as an on-demand view, not always on. |
| B13 | Palia wiki — Gardening (https://palia.wiki.gg/wiki/Gardening) — deep-read | A multiplayer cozy game with private housing plots. Crops don't wither if unwatered, they just wait. No sprinklers; watering-can tiers (four). Some crops (tomato, potato, napa cabbage) give "Water Retain" to crops directly next to them, **but only to *other* crop types**, and buffs don't stack with fertiliser. **Visitors may water and till on someone else's plot but cannot harvest.** | Two multiplayer rules we can borrow: visitors can *help* with chores but can't *take*; and a variety rule in the garden itself (a buff that only works on a different neighbour) — the same "variety pays" idea as our décor. |
| B14 | Stardew wiki — Farm Computer (https://stardewvalleywiki.com/Farm_Computer) — deep-read | A placed device that, when used, lists farm totals: pieces of hay, total crops, crops ready, **unwatered crops**, crops ready in greenhouse, open tilled soil, forage items, **machines ready**, farm-cave status. Late-game recipe (dwarf gadget + battery pack + 10 refined quartz). | A diegetic, pixel-art-friendly way to open a plot summary — and "unwatered crops" / "machines ready" is exactly the automation status our plot panel could show alongside happiness. |
| B15 | Oxygen Not Included wiki — Decor (https://oxygennotincluded.fandom.com/wiki/Decor), via API — deep-read | Every object has a decor value and a radius; a tile's decor is the sum of everything reaching it. **The Decor overlay (F8) tints tiles green (positive) or red (negative); hovering a tile shows its decor and a detailed report of everything contributing, and each contributor lights up.** **At 120 the readout adds "(Maximum Decor)"** — the value can go higher, but 120 is the most that earns a morale bonus. Morale bands from last cycle's average: Poor +0, Mediocre +1 (≥0), Average +3 (≥30), Nice +6 (≥60), Charming +9 (≥90), Gorgeous +12 (≥120). The shown value eases toward the real one (a sudden change doesn't hit at once). | The best example found of **showing a cap in the interface** in plain words right where the number is. Also a model for hover-to-explain on the overlay, and for named bands with small, even steps. |

## 2. Codebase study

Two open-source codebases were read at their current `HEAD` (shallow sparse clones into the session scratchpad,
not into this repo).

### 2.1 OpenRCT2 — guest happiness and the park rating (C++)

Repository https://github.com/OpenRCT2/OpenRCT2, commit `75ffdd23a10e6d132457b12685c570a98d8cf10c`
(2026-09-27). OpenRCT2 is the open-source re-implementation of RollerCoaster Tycoon 2, so these rules are the
original game's (the `rct2: 0x…` comments mark the original addresses they were recovered from).

**(a) The park rating is a sum of capped parts, each of which starts as a penalty that the player earns back.**
`src/openrct2/world/Park.cpp`, `CalculateParkRating` (line 376 onward;
https://github.com/OpenRCT2/OpenRCT2/blob/develop/src/openrct2/world/Park.cpp):

```cpp
int32_t result = 1150;
...
// -150 to +3 based on a range of guests from 0 to 2000
result -= 150 - (std::min<int32_t>(2000, park.numGuestsInPark) / 13);
...
// Peep happiness -500 to +0
result -= 500;
if (park.numGuestsInPark > 0)
{
    result += 2 * std::min(250u, (happyGuestCount * 300) / park.numGuestsInPark);
}

// Up to 25 guests can be lost without affecting the park rating.
if (lostGuestCount > 25)
{
    result -= (lostGuestCount - 25) * 7;
}
...
// Litter
...
result -= 600 - (4 * (150 - std::min<int32_t>(150, litterCount)));
...
result -= park.ratingCasualtyPenalty;
result = std::clamp(result, 0, 999);
```

What this teaches: every contributor has its **own ceiling** (`std::min(250u, …)` means the happiness part is
full once about 83% of guests are happy; litter stops costing more after 150 pieces), and then the total is
clamped. Ride excitement and intensity are scored against a **sweet spot** (46 and 65 after scaling), so
"more" is not always better. A capped sum is easy to explain in a breakdown: each line shows "x of max y".

**(b) Scenery helps a guest by a threshold, not by a count — and one good thing at a time.**
`src/openrct2/entity/Guest.cpp`, `GuestAssessSurroundings` (line 2870 onward):

```cpp
// TODO: Refactor this to step as tiles, 160 units is 5 tiles.
...
        case TileElementType::largeScenery:
        case TileElementType::smallScenery:
            num_scenery++;
            break;
...
if (num_fountains >= 5 && num_rubbish < 20)
    return PeepThoughtType::fountains;

if (num_scenery >= 40 && num_rubbish < 8)
    return PeepThoughtType::scenery;

if (nearby_music == 1 && num_rubbish < 20)
    return PeepThoughtType::music;

if (num_rubbish < 2 && !getGameState().cheats.disableLittering)
    return PeepThoughtType::veryClean;
```

and the caller (line ~900), every 18 updates while a guest walks or sits:

```cpp
PeepThoughtType thought_type = GuestAssessSurroundings(x & 0xFFE0, y & 0xFFE0, z);

if (thought_type != PeepThoughtType::none)
{
    insertNewThought(thought_type);
    happinessTarget = std::min(kPeepMaxHappiness, happinessTarget + 45);
}
```

What this teaches: RCT's scenery bonus is **binary** — 40 scenery pieces within 5 tiles (and little litter)
earn a fixed +45, and 400 pieces earn the same. Only the first satisfied reason in priority order counts, so
fountains, scenery and music do not stack. It is simple and cannot be exploited, but it gives **no reason to
vary** (40 identical trees pass) and nothing between 0 and 40 is rewarded, so it is a poor model for our
"each different decoration adds a bit" rule. It does show one thing worth considering: **litter vetoes the
bonus** (a mess cancels the nice things) — the basis of the optional "mess lowers plot happiness" question in
B.4.

**(c) A decoration with a hard ceiling on its effect.** Same file, line ~1135, in the queuing state:

```cpp
/* Queue line TV monitors make the peeps waiting in the queue
 * slowly happier, up to a certain level. */
if (happinessTarget < 90)
    happinessTarget = 90;

// This is +2 as UpdateMotivesIdle (that is called later in the function)
// will -1. We want to gradually increase happiness to 165
if (happinessTarget < 165)
    happinessTarget += 2;
```

A queue TV can lift a waiting guest only to 165 of 255 (about 65%) — an item-level cap, the same idea as our
"overall cap", applied per item type.

**(d) The shown value eases toward the real value.** `Guest.cpp` line ~790: `happiness` moves toward
`happinessTarget` by at most 4 per update (`newHappiness = std::max(newHappiness - 4, 0)` / `+ 4`), so the
number the player sees never jumps. Idle guests also drift back toward the middle (`updateMotivesIdle`: "Idle
peep happiness tends towards 127 (50%)").

**(e) How RCT shows it: a face, a thoughts list, and a summary grouped by reason.** The face sprite is chosen in
`GetFaceSpriteOffset` (line ~7380):

```cpp
// ANGRY
if (peep->angriness > 0)
    return PEEP_FACE_OFFSET_ANGRY;
// VERY_VERY_SICK
if (peep->nausea > 200)
    return PEEP_FACE_OFFSET_VERY_VERY_SICK;
...
int32_t offset = PEEP_FACE_OFFSET_VERY_VERY_UNHAPPY;
// There are 7 different happiness based faces
for (int32_t i = 37; peep->happiness >= i; i += 37)
{
    offset++;
}
```

Seven faces split the 0–255 scale into steps of 37, and the **most urgent problem overrides the mood face**
(angry, sick, tired). The guest list's "Summarised" tab
(`src/openrct2-ui/windows/GuestList.cpp`, `RefreshGroups`, line ~820) groups every guest by their current
thought, draws a few faces per group and **sorts the groups by how many guests share that thought**:

```cpp
auto& group = FindOrAddGroup(GetArgumentsFromPeep(*peep, _selectedView));
...
group.NumGuests++;
...
// Sort groups by number of guests
std::sort(_groups.begin(), _groups.end(), [](const GuestGroup& a, const GuestGroup& b) {
    return a.NumGuests > b.NumGuests;
});
```

and the park window's Rating tab (`src/openrct2-ui/windows/Park.cpp`, `onPrepareDrawRating`, line ~658) shows
the current rating over a history graph fixed to 0–1000. So RCT's answer to "why is my score what it is?" is a
**ranked list of reasons with counts**, next to one number and its trend — never a formula.

### 2.2 Data Layers (a Stardew Valley mod) — showing sprinkler coverage (C#)

Repository https://github.com/Pathoschild/StardewMods, commit `76565e83ede4bc8b3c293f1c659032ba9c39c213`
(2026-03-28), folder `DataLayers/`. Data Layers is a long-running Stardew mod by the author of the SMAPI mod
loader (its popularity was not measured here); it exists because players want to *see* coverage.

`DataLayers/Layers/Coverage/SprinklerLayer.cs` (https://github.com/Pathoschild/StardewMods/blob/develop/DataLayers/Layers/Coverage/SprinklerLayer.cs):

```csharp
this.Legend = [
    this.Wet = new LegendEntry(I18n.Keys.Sprinklers_Covered, colors.Get(layerId, "Covered", Color.Green)),
    this.Dry = new LegendEntry(I18n.Keys.Sprinklers_DryCrops, colors.Get(layerId, "NotCovered", Color.Red))
];
...
groups.Add(new TileGroup(tiles, outerBorderColor: sprinkler.TileLocation == cursorTile ? this.SelectedColor : this.Wet.Color));
...
// yield dry crops
var dryCrops = this
    .GetDryCrops(location, visibleTiles, covered)
    .Select(pos => new TileData(pos, this.Dry));
...
// yield sprinkler being placed
SObject heldObj = Game1.player.ActiveObject;
if (this.IsSprinkler(heldObj, legacyCustomCoverageBySprinklerId))
{
    var tiles = this
        .GetCoverage(heldObj, cursorTile, legacyCustomCoverageBySprinklerId, isHeld: true, visibleTiles)
        .Select(pos => new TileData(pos, this.Wet, this.Wet.Color * 0.75f));
    groups.Add(new TileGroup(tiles, outerBorderColor: this.SelectedColor, shouldExport: false));
}
```

and `DataLayers/Layers/AutoLayer.cs`: "A data layer which chooses an overlay automatically based on context like
the held item." — the sprinkler, scarecrow and bee-house layers implement `IAutoItemLayer`, so the overlay turns
itself on when the player holds one of those items.

What this teaches, in four rules we can copy directly: (1) covered cells in one colour; (2) **only the crops that
are NOT covered** in a warning colour — the overlay points at the problem, not at everything; (3) the source under
the cursor gets its own border; (4) **holding the item shows a ghost of its coverage at the cursor before
placing**, automatically. The same four rules serve a power unit's radius and a decoration's reach. This
matches the existing requirement in `docs/product/design/game_design.md` §11.6 ("highlight the covered cells so
the player can see exactly what is energized before committing").

## 3. Findings

### Question A — sprinklers and farm automation

**Search angles used (named):** (1) by technique — sprinkler coverage shapes, "water source + radius",
fuel-fed versus electric machines, tool upgrades as the first automation; (2) by game — Stardew Valley, Core
Keeper, Terraria, Dinkum, Coral Island, Sun Haven, Fields of Mistria, Palia, Factorio (Necesse noted under B1: its
automation is settlers, which we don't have); (3) by code — the Data Layers mod's sprinkler overlay (§2.2); (4) by
problem — "automation removes the fun", "watering is exhausting", "why doesn't this game have sprinklers"
(Sun Haven and Fields of Mistria forums), routine design (The Escapist). Two further angles were checked for
our own facts: the repo's design docs and the Go server's watering code.

#### A.1 What the games show

1. **Each step should take away a *different* chore.** Stardew goes can → sprinkler → bigger sprinkler → an
   add-on you choose (A1, A2, A13); Dinkum goes can → sprinkler plus tank → advanced sprinkler (A7); Factorio goes
   "feed it fuel" → "feed it nothing, but build a grid" (A10). A step that only makes a number bigger feels flat —
   Fae Farm's upgrades are criticised as just "water more crops at once" (A11).
2. **The manual phase has a job, and a time limit.** Hand-watering is what makes the first sprinkler feel good
   (A11). When it runs too long, players complain: Fields of Mistria's sprinklers arrive very late and players say
   watering eats their energy before the day starts (A12); Sun Haven has none and players keep asking (A9).
3. **Show one, then sell many.** Coral Island mails the player a free first sprinkler after a farming quest (A8).
4. **The hand keeps a small edge.** Stardew's Auto-Petter gives about half the friendship of petting by hand (A4);
   Fields of Mistria's statues skip the bonuses tied to watering by hand (A12); Core Keeper and Coral Island give no
   skill points for automated farming (A5, A8). This is how a game says "the machine takes the chore, not your
   place".
5. **Automate upkeep, never the harvest.** Where games let machines harvest (Junimo huts, Coral Island's auto-harvest
   and "Auto SFH", Core Keeper's robot arms) the plot starts farming itself (A3, A5, A8). Terraria instead folds
   harvest and replant into one swing (A6) — fewer clicks, same player.
6. **A source that serves a radius is readable, and it is our power model already.** Dinkum ships it twice (tank →
   sprinklers, windmill/solar → machines, overlaps don't stack, a tape measure shows range — A7). Our design already
   says a power unit powers every square within a radius and shows it while placing (`docs/gdd/overview.md` §16;
   `docs/product/design/game_design.md` §11.6).
7. **Fuel works in a cozy game when a load lasts days and weather helps.** Fields of Mistria's fuel stones last 1–40
   days and aren't used on rainy days (A12). Factorio's constant refuelling (A10) suits a factory game, not ours.
8. **Show coverage before placing.** Data Layers draws a ghost of the coverage when the sprinkler is held, colours
   covered tiles, and flags only the crops left dry (§2.2).

#### A.2 Facts about our own game that change the answer (checked in the repo)

- **Our watering cans only differ in capacity** — no bigger watering pattern, no metal tiers (decision D12,
  `docs/product/economy/catalogs/tools.md`; prototype data `nakama/data/entities/items.json`: small can 40 pours,
  large can 80). So the first sprinkler is our *first* real relief; it should come a little earlier than
  Stardew's big moment, not later.
- **Crops can take two waterings a day in the prototype** (`max_daily_waterings: 2` on all seven crops in
  `nakama/data/entities/crops.json`, enforced in `nakama/modules/world/handlers_farming.go:571` and in the rain pass
  `handlers_env.go:356`), and growth counts waterings (`waterings_per_stage` 2–4). A sprinkler that waters once at
  dawn therefore grows crops at half the speed of a player who waters twice. That is either the "hand keeps an
  edge" rule (pattern 4) or a sprinkler that feels like a downgrade. This is a prototype rule, not a decision —
  see question 2 below.
- **Rain already does what a sprinkler does, for every crop.** `rainWaterAll` (`handlers_env.go`) adds one watering
  within the daily cap, swaps the ground to `garden_plot_wet` and broadcasts it; the day rollover
  (`nakama/modules/world/match.go`, around line 1516) resets the daily counts. A sprinkler pass is the same code
  limited to covered cells, run at dawn. Farming lives in the server's match loop, **outside the bug simulation**:
  a search for `garden_plot_wet` finds only the farming and weather handlers, a test, and the client's placement
  controller. So sprinklers carry no bug-sync risk — unless a later idea lets wet ground affect bugs (say,
  mosquitoes breeding in standing water); that would make it a bug-simulation input and need the `frontier-sync`
  recipe.
- **One world clock; the world only stops when nobody is online; empty zones stay frozen and catch up on the
  first visit** (`docs/gdd/overview.md` §17: the clock and night rules decided 2026-09-28, the frozen-zone rule
  2026-09-26). So a plot's sprinklers keep watering while its owner is away as long as its zone is running, and
  when the zone has been frozen **the catch-up on the next visit must apply the missed dawns too** (spending tank
  water and pump fuel the same way), or sprinklers would silently do nothing while the zone slept. Crops never
  wilt, so they simply wait ripe. That eases a chore without playing for anyone, but it is worth stating in the
  plot rules.
- **Everything in the shared world must run the same for every player** (decided 2026-09-28). Coverage and power
  must depend only on the machine and where it stands — never on who owns it or who is nearby.
- **Straw mulch that keeps a plot wet longer is already proposed** (proposal P11 in `docs/gdd/overview.md`, the
  uses of cut straw — a proposal, not yet decided), and **fertiliser raises yield** (decided 2026-09-27). Both give
  a ladder something to hang on.

#### A.3 Candidate ladders, scored

Scores are 1 (poor) to 5 (strong) on the five axes asked for.

| Candidate | Keeps farming fun | Pacing | Eases chores, never plays | Fits a shared multiplayer world | Readability | Total |
|---|---|---|---|---|---|---|
| **L1 Stardew-style.** Three sprinkler sizes (small 3×3 in the village, large 5×5 in the western town, a powered 7×7), bought, no upkeep, no water source. | 4 | 3 | 4 | 4 | 5 | 20 |
| **L2 Dinkum-style.** Cheap sprinklers that only work near a water source: a rain barrel (village) → a pumped water tower (western town) → an electric pump (power). | 4 | 4 | 5 | 4 | 3 | 20 |
| **L3 Soft relief only.** No sprinklers: mulch, water-holding companion plants, rain barrels by the beds, better cans. | 3 | 2 | 5 | 5 | 4 | 19 |
| **L4 Full automation line.** Sprinklers with plant / fertilise / harvest attachments, conveyors to chests, all under power. | 2 | 3 | 1 | 3 | 3 | 12 |
| **L5 Hybrid (PICK).** Village sprinkler with its own small tank that rain refills → western-town large sprinkler fed by a water tower that a fuel pump fills → power adds pressure (one ring more) and never runs dry. Harvest always by hand. | 5 | 4 | 5 | 5 | 4 | 23 |

Why the scores:

- **L1** is the proven, most readable ladder (A1). It loses on pacing because it has no middle step: once a
  sprinkler is down, that bed never needs anything again, so the fuel-fed rung our design calls for has nothing to
  do with water, and the powered tier becomes "the same thing, bigger" — the Fae Farm trap (A11).
- **L2** is the tidiest fit to our power model (pattern 6) and every rung removes a different chore. It loses on
  readability early: two objects (sprinkler + source) before the player's first relief, and a first sprinkler
  that does nothing on its own is a confusing purchase.
- **L3** keeps farming hands-on and is very multiplayer-safe, but it contradicts a decision already made (small
  sprinklers are sold in the village) and the genre evidence says players expect sprinklers (A9, A12). Rejected as
  a ladder; its best part (mulch) is kept as rung 0.
- **L4** is what our rule forbids: the plot farms itself (A8's Auto SFH, A5's robot arms). Its only keepable part
  is a fertiliser doser, which is upkeep, not harvest. Rejected.
- **L5** takes L1's readable first sprinkler, L2's source-and-radius model from the second rung on (so water and
  electricity teach the same idea), Fields of Mistria's "fuel that lasts days, rain saves it" (A12), Stardew's
  pressure nozzle turned into the reward for power (A2), and keeps harvest manual (pattern 5).

#### A.4 Recommendation — ladder L5, concretely

All sizes, durations and radii below are **starting suggestions to tune in play**, not design values.

| Rung | What | Where it comes from | What runs it | Covers (suggested) | Chore it removes | Chore that stays |
|---|---|---|---|---|---|---|
| 0 | Watering can (small, large), rain, **straw mulch** | Village general store; mulch made from cut straw (proposal P11) | The player | One tile per pour; mulch keeps a bed wet about 2 days | — | Watering every bed |
| 1 | **Small sprinkler** — a brass impact sprinkler on a stake, with a small tank | **Village general store, priced as a savings goal** (decided); optionally *one* given as a thank-you after the first harvest sale, as Coral Island does | Its own tank: enough for **3 dawns**; **rain refills it**; one pour of the watering can tops it up | **3×3** (the 8 tiles around it), once at dawn | 8 pours a day → 1 pour every 3 dry days | Refilling in a dry spell; planting; harvesting |
| 2 | **Large sprinkler + water tower + pump** | **The western town in the Locust Farmland** (decided: larger ones come from other places, such as the western town) | The tower feeds every sprinkler within about **10 tiles** (small ones too); a **fuel pump** standing on a pond or well fills the tower — one load of fuel (wood, charcoal) lasts several days; rain also fills the tower | Large sprinkler **5×5** (24 tiles) | Refilling each sprinkler → feeding one pump every few days | Feeding the pump; planting; harvesting |
| 3 | **Electric pump**, plus one optional add-on per sprinkler: a **fertiliser doser** (fills new seedlings in range from a hopper, like Stardew's Enricher) | Bought, never player-made (electronics rule D1/D26): the western town, and Modern Wares as a teaser the player can't power yet | Must stand inside a powered area (windmill, solar, generator); no fuel; never runs dry | **Power is pressure: inside a powered area every sprinkler reaches one ring further** (small 5×5, large 7×7) — the pressure nozzle, earned instead of bought | Feeding the pump; fertilising by hand | Planting; **harvesting — never automated** |

**What stays manual on purpose, at every rung:** choosing and planting crops, harvesting, picking fruit, catching
bugs (the autonet stays the only automatic catcher), and dealing with pests through the ecology. If the owner keeps
two waterings a day, a second watering by hand still speeds a crop — the Auto-Petter rule (A4).

**Why this ladder:**

- Each rung removes a different chore and adds one new idea — a tank you tend, then one source serving many plus
  fuel, then power as pressure — instead of only bigger numbers (patterns 1 and 7; A11).
- From rung 2 on, water and electricity use **the same picture**: a thing that serves every square within a
  radius, shown while you place it. The power rung teaches nothing new; it just removes the fuel.
- Weather matters to the farm: rain refills tanks and the tower, and droughts (decided 2026-09-28 to be part of
  the game, like rain) empty them. That ties farming to the living world instead of switching it off.
- It keeps both decided fixed points (small village sprinklers the player saves for; larger ones in the western
  town) and fills in the rest, which is what the owner left to design (proposal P22).
- The harvest — the reward — never leaves the player's hands (pattern 5).

**Smaller rules worth keeping from the sources:**
- **Squares, not a plus.** Stardew's first sprinkler waters only the 4 tiles beside it — a deliberate layout
  puzzle, but stingy for an item the player saved up for (A1). Squares (3×3, 5×5, 7×7) are easier to read and to
  tile; recommended.
- **A rainy dawn costs nothing.** On a rainy day a sprinkler doesn't spend its tank (Fields of Mistria's rule,
  A12) — rain waters the crops anyway.
- **Tools don't knock sprinklers out by accident.** Stardew had to fix exactly this in 1.5 ("hoes no longer remove
  sprinklers", A1); our hoe and shovel should skip a placed sprinkler.
- **Stations follow the same line as fields.** A hopper-style feeder may load a station, but the player takes the
  output (Stardew's Hopper, A4b) — consistent with the autonet's slow, capped design.

**Readability rules to build with it** (from §2.2, A7 and `game_design.md` §11.6): holding a sprinkler shows a
ghost of its coverage at the cursor; a placed sprinkler shows its coverage on hover; the sprite shows its tank
level in three steps (full, half, empty) and an "empty" drop icon (the game already uses a droplet over trees);
the tower and every power unit show their radius the same way; while the player holds a watering tool, crops that
nothing covers get a small dry marker — only those, so the overlay points at the problem; and the plot panel
(Question B) gets one farm line: "sprinklers empty: 2, pump fuel: 3 days".

**Multiplayer:** the dawn pass runs where farming already runs (the server match loop, like rain), so every player
sees the same wet ground and a late joiner gets it from the saved crop and tile state. On an invite-only plot a
visitor may refill a tank or fuel the pump but may not harvest (Palia's rule, B13). Out in the lawless world a
sprinkler or pump can be taken like anything else, so expensive automation naturally belongs on the safe private
plot — which supports the plot design rather than fighting it.

**Optional flavour, not lens-checked yet:** the pump could also burn *bug oil*. Rendering fat from fly larvae into
biodiesel is real research (black soldier fly larvae; e.g. the 2025 review in the International Journal of Energy
Research, https://onlinelibrary.wiley.com/doi/full/10.1155/er/8032373, search-level only). It would tie farm
automation to bug farming. It must go through the idea lenses before the owner sees it as a proposal.

**Questions for the owner (taste, not research):**

1. The small village sprinkler: (a) has a small tank that rain refills and the can tops up — recommended, because
   it gives rung 1 a job and makes weather matter; (b) runs forever with no upkeep, like Stardew.
2. Crops take two waterings a day in the prototype. Sprinklers should give (a) one watering at dawn, and a second
   by hand still speeds the crop — recommended, the hand keeps a small edge; (b) two (dawn and dusk), a full
   replacement; (c) crops change to one watering a day, as in Stardew.
3. The first sprinkler: (a) one is given after the first harvest sale so the player sees what they are saving for;
   (b) none is given.
4. Power: (a) power adds one ring of reach to every sprinkler in a powered area — recommended, no extra items;
   (b) separate "powered sprinkler" items sold at Modern Wares.

### Question B — the plot happiness / decoration panel

**Search angles used (named):** (1) by technique — duplicate diminishing returns, variety rules, caps, named
bands, overlays, breakdown lists; (2) by game — Terraria, Necesse, RimWorld, Animal Crossing, The Sims, Valheim,
Oxygen Not Included, Two Point Hospital, Parkitect, Palia, Stardew (Farm Computer); (3) by code — OpenRCT2's park
rating, guest thoughts and summary list (§2.1), and the existence of open-source Terraria happiness calculators
(B4); (4) by problem — "players spam one item for prestige" (Two Point Hospital), "happiness is opaque → players
build calculators" (Terraria), "how much to show" (Game Developer's transparency article). Our own facts came from
`docs/gdd/overview.md`, `docs/product/design/game_design.md` §11.5, `docs/product/economy/stats_and_bonuses.md`
and the existing station panel `BugFarmerClient/Assets/Scripts/UI/CraftingPanel.cs`.

#### B.1 What the games show

1. **Hidden numbers push players out of the game.** Terraria's Happiness button speaks in dialogue only (B3), and at
   least six fan calculators exist (B4). Two Point Hospital hides item prestige and players spam the best item
   (B10). The Sims hides the environment maths; the wiki reverse-engineered it (B8).
2. **The number players actually read is a named band.** RimWorld ("somewhat impressive"), Oxygen Not Included
   ("Charming"), Necesse ("Very Happy"), The Sims ("Nicely Decorated"), Animal Crossing (B/A/S). The exact
   formula can sit one layer down (B2, B5, B7, B8, B15).
3. **"Why" is shown as a list of reasons with numbers.** Necesse's "Thoughts:" list (B2), RimWorld's mood lines
   ("Pretty environment +5", B6), OpenRCT2's summarised thoughts sorted by how many guests share them (§2.1), and
   Oxygen Not Included's hover report of every contributor (B15).
4. **A cap is shown where the number is.** Oxygen Not Included prints "(Maximum Decor)" next to the value (B15).
   OpenRCT2 caps each part of the park rating separately (§2.1). RimWorld's log curve makes a soft cap and its wiki
   has to warn players not to overspend (B5).
5. **Variety is enforced by the rule, then made visible.** Valheim: only the best item per category counts, and no
   item stacks with itself (B9). Necesse: furniture happiness counts *unique* types, 1 = +4% … 7+ = +20% (B1), and
   repeated leisure falls to 5% of normal (B2). The Sims 3: only the best few objects count fully (B8). Animal
   Crossing's old games counted colour and lucky-item bonuses per *unique* item (B7). **Two Point Hospital shows
   what happens when the rule is too weak: spam** (B10).
6. **Spatial problems are best shown in the world.** Parkitect's green/red decoration view with pink culprits (B12),
   RimWorld's beauty toggle (B6), Oxygen Not Included's decor overlay (B15), Data Layers' coverage overlay (§2.2).
   All are on-demand modes, not always on.
7. **Goals give direction.** Animal Crossing turns decorating into targets — a full set, three of a category, a
   colour theme, limits like "wall items, max three" — and sends tips with the score (B7). Its weakness: the
   feedback comes days later in a letter.
8. **Smooth the shown value.** OpenRCT2 moves the shown happiness toward the real value a few points per update
   (§2.1d); Oxygen Not Included does the same (B15). A panel that jumps on every placement feels twitchy.

#### B.2 The rule the panel has to explain (a suggestion — the panel can only be as clear as the rule)

The plot rule is decided in principle (January 2026, reconfirmed 2026-09-28): small production bonuses from
decorations, less for each duplicate of the same item, up to an overall cap; duplicates are keyed on the item `id`,
and `category` is available as a coarser grouping (`game_design.md` §11.5; `architecture_items.md`). The exact
curve is open. Four ways to write "less for each duplicate", judged by how well a panel can show them:

| Duplicate rule | Example | Panel clarity | Pushes variety | Matches "a second sofa adds less" |
|---|---|---|---|---|
| **D1 Halve each copy; the 4th and later add nothing (PICK)** | Sofa worth 8: +8, +4, +2, then 0 | High — whole numbers if item values are multiples of 4; "copies can never add more than 1¾ of one item" is one sentence | Strong: a second copy is always worth less than a *new* item of the same value | Yes |
| D2 Smooth decline (each copy × 0.7, as proposed by Two Point Hospital players) | +8, +5.6, +3.9, +2.7 … | Medium — decimals, never quite zero | Strong | Yes |
| D3 Only the best item per category counts (Valheim) | a second sofa adds 0 | High | Strongest | **No** — it adds nothing, not less |
| D4 Count unique types per category (Necesse) | 1 type +4, 2 types +7, 3 types +10 … | Medium — per-item values disappear | Strong | Partly |

D1 is the pick: it is the literal reading of the rule, it keeps the numbers small and whole (the transparency
article's "discrete, small numbers", B11), and its steepness sits where Two Point Hospital's players asked for,
well past the weak version that let them spam (B10). The overall cap stays a single number for the whole plot.
All values here are placeholders for tuning.

#### B.3 Candidate panels, scored

Scores are 1 (poor) to 5 (strong) on the four axes asked for.

| Candidate | Clarity | Fits pixel-art 2D UI | Encourages variety | Low clutter | Total |
|---|---|---|---|---|---|
| **P1 Single meter** — one bar or face and a band name, nothing else (RCT's face, Necesse's badge) | 2 | 5 | 1 | 5 | 13 |
| **P2 Full breakdown list** — every placed item with its contribution, duplicates shown smaller, the cap line (Necesse "Thoughts", ONI hover report) | 5 | 3 | 4 | 2 | 14 |
| **P3 In-world overlay** — each decoration outlined by what it adds: full, reduced, nothing (Parkitect, ONI, RimWorld) | 3 | 4 | 4 | 4 | 15 |
| **P4 Variety checklist** — goals such as "a light", "a rug", "a plant in every corner", sets (Animal Crossing) | 2 | 5 | 5 | 4 | 16 |
| **P5 Layered (PICK)** — P1's meter and band as the headline, P2's list grouped by category and folded, P3's overlay on demand and while holding a decoration, P4 reduced to a short "try next" line | 5 | 4 | 5 | 4 | 18 |

Why the scores:

- **P1** is clean and fits pixel art perfectly (a face is a 16×16 sprite), but it says *what* and never *why*;
  that is exactly Terraria's gap (B3, B4). Players can't see that their fourth sofa adds nothing.
- **P2** answers every question, but a plot with 60 items becomes a wall of small pixel text — the reason
  Necesse and RCT group or summarise (B2, §2.1e).
- **P3** makes duplicates obvious *in place* (grey outline on the fourth stool) and is the best teacher while
  decorating, but it shows no total, no cap and no effect — it needs a panel beside it.
- **P4** pushes variety hardest and reads well as icons with ticks, but it hides the numbers and the cap, and a
  long checklist turns a cozy plot into homework.
- **P5** keeps each layer where it is strongest: one glance for the headline, one click for "why", and the world
  itself for "which one". It borrows the proven parts only.

#### B.4 Recommendation — the layered plot panel (P5), concretely

**Where it opens**
- **A small plot badge** on screen while the player stands on a plot they own or are visiting: the face and the
  band word (the pattern of RCT's face and Necesse's badge). Clicking it opens the panel.
- **The plot's sign at its entrance** — a sign post that would come with a bought plot (to be designed with the
  plots themselves, which aren't built). Using it opens the same panel, the way Stardew's Farm Computer reports
  farm totals (B14). Visitors can open it read-only, so a plot can be shown off
  (Animal Crossing's score is a social thing, B7).
- **A "Plot" button in the inventory screen** once the player owns a plot, so it can be checked from anywhere.

**What it shows** — a narrow column in the style of the existing station panels (`CraftingPanel.cs`: a header
plaque with one flavour line, bars always paired with a number, distinct colours). Example with made-up numbers:

```
+--------------------------------------------+
|  ROSE'S PLOT                          [x]  |
|  "A quiet patch at the meadow's edge."     |
+--------------------------------------------+
|  (face)  PLEASANT                          |
|  [#################.........|]  62 / 100   |
|  Crops and stations on this plot: +6%      |
+--------------------------------------------+
|  v Seating                           21    |
|      Sofa x3          +8  +4  +2           |
|      Stool x4         +4  +2  +1   0       |
|        (a 4th stool adds nothing)          |
|  > Lighting                          10    |
|  > Plants                            12    |
|  > Art and trophies                  10    |
|  > Textiles                           4    |
|  > Outfits on mannequins              5    |
+--------------------------------------------+
|  Try next: no rug yet · no clock yet       |
|  [ Show on plot ]            [ Farm > ]    |
+--------------------------------------------+
```

1. **Headline:** the face (five faces are enough for a small panel), the band word, the bar with the **cap as its
   right end** and the number "62 / 100", and **the effect in plain words** ("Crops and stations on this plot:
   +6%"). At the cap the number reads "100 / 100 — at the cap" and the effect line adds "more decorations won't
   raise this; they still look nice" (the Oxygen Not Included "(Maximum Decor)" pattern, B15). The shown number
   eases toward the real one instead of jumping (§2.1d).
2. **Breakdown by category, folded by default:** one line per category with its subtotal. (Today's `category`
   field in `nakama/data/entities/placeables.json` is too coarse for this — 79 `furniture`, 86 `decoration`, 8
   `lighting`, 78 `structure` among 286 entries — so a finer display group such as seating / lighting / plants /
   art / textiles would be added *with* the bonus system, together with each item's bonus value, following the
   house rule "don't add gameplay fields to the schema ahead of the feature", `docs/scaffolding_scratchpad.md`.)
   Unfolding a category lists each item with **every copy's value side by
   side** — "Sofa ×3 +8 +4 +2" — reduced copies in a dimmer colour and copies that add nothing shown as a grey 0,
   with a one-line note the first time it happens ("a 4th stool adds nothing"). This is how the panel *teaches*
   the duplicate rule without a tutorial: the halving is visible in the row.
3. **"Try next":** at most two or three short hints naming categories or common items the plot doesn't have yet.
   It is the checklist idea (P4) as a gentle nudge, not a list of chores.
4. **"Show on plot":** turns on the in-world view (below). **"Farm":** a second small tab with the farm status from
   Question A — "sprinklers empty: 2 · pump fuel: 3 days · crops ready: 14" — the Farm Computer's job (B14).

**The in-world view (P3's part)**
- With "Show on plot" on, every decoration that counts gets an outline: **gold** = counts in full, **silver** =
  counts less (a duplicate), **grey** = adds nothing (a 4th copy, or the plot is at the cap). Hovering one shows a
  one-line tooltip: "Sofa — 2nd of 3: +4 (the first gives +8)".
- **While the player holds a decoration to place**, a small number floats by the cursor: "+8", "+2 (3rd sofa)" or
  "+0 (plot at cap)". This is the Data Layers "held item shows its effect before you place it" rule (§2.2) applied
  to value — the moment where the player actually decides between another sofa and something new. The floating
  number is immediate even though the headline bar eases (B.1 point 8), so feedback never feels delayed.
- **Not colour alone:** each outline also carries a tiny mark (a full pip, a half pip, a dash) so the three states
  read for colour-blind players, and the outlines are drawn on the interface layer so night-time lighting can't
  hide them.

**What the player learns from it**
- how happy the plot is and what that does for them (the band and the effect line);
- which items count in full, which count less because they are duplicates, and which add nothing;
- how far they are from the cap, and when extra decorating is purely for looks;
- which kinds of things the plot is missing — so variety is the obvious next step.

**How it fits the rest of the game**
- The plot's score is a pure function of what is on the plot (placed items by `id`, and outfits on its
  mannequins), recalculated when the plot changes, kept in whole numbers, and sent to players; the panel only
  reads it. Every player sees the same number, and nothing in the shared world changes speed for one player —
  the bonus belongs to the plot (decided 2026-09-28: the shared world runs the same for everyone).
- It reuses what the client already has: the narrow station-panel column and its bar helper in `CraftingPanel.cs`,
  `TooltipUI.cs` for hovers, and the placement preview in `PlacementController.cs` for the held-item number.
- Folded rows suit a controller too (up and down to move, confirm to unfold); controller support is still an open
  question in the interface section of the design document.

**Questions for the owner (taste, not research):**

1. **Whose happiness is it?** (a) the plot's own score, which raises the plot's production — recommended, it
   matches `stats_and_bonuses.md` ("comfort … feeds a farm/production multiplier"); (b) the player's, as a
   Valheim-style rest bonus while at home; (c) the penned bugs', as welfare that raises their yield.
2. **What is it called?** (a) happiness; (b) comfort; (c) cosiness. The band words (for example Bare, Plain,
   Pleasant, Cosy, Delightful) follow from this.
3. **The duplicate rule:** (a) halve each copy, the 4th adds nothing (D1, recommended); (b) a smooth decline (D2);
   (c) only the best per category (D3).
4. **Decorative outfits count when:** (a) shown on a mannequin on the plot, like furniture — recommended, it is
   stable and needs no new rule; (b) worn by the owner while on the plot; (c) worn by anyone on the plot.
5. **Should mess lower it?** Rotting fruit, carcasses or broken things on the plot could take points off, the way
   litter cancels scenery in RollerCoaster Tycoon (§2.1b), filth in RimWorld (B6) and cockroaches in Animal
   Crossing (B7). (a) yes, a small penalty shown as its own line; (b) no.

## 4. Claims I am NOT sure about

**About other games (secondary sources, fetcher summaries, or search-level only):**

1. **Stardew's Pressure Nozzle and Enricher prices.** The wiki pages as summarised said "20 Qi Gems", once "for 4".
   I could not confirm whether 20 gems buys one or four.
2. **When Stardew players typically reach Farming 2, 6 and 9.** Not researched; I avoided putting a day on it.
   The "no more watering" feeling rests on forum threads (one deep-read, the rest search-level), not a survey.
3. **Core Keeper details.** The official wiki blocked the fetcher (403/402). The sprinkler recipe (8 iron + 8
   scarlet bars) and "needs no power" come from a database site and a hosting company's guide; guides disagree on
   the recipe (older ones say tin) and on how far power carries (a "25-tile radius" versus "18 wire tiles, then
   5 of fall-off"). Treat Core Keeper numbers as approximate.
4. **Dinkum, Coral Island, Sun Haven, Valheim, Oxygen Not Included and Parkitect numbers** come from
   community wikis. Several Coral Island pages are marked as stubs; Valheim's page says it is not fully updated
   for 1.0; Dinkum's windmill range picture is marked "outdated". Parkitect's green/red/pink decoration view is
   from search results, not a deep read.
5. **Valheim shows the comfort number next to the Resting icon** — from a guide's search snippet (game8), not
   checked in the game.
6. **Necesse's interface** (the coloured badge, the "How are you doing?" screen and its "Thoughts:" list) is from a
   fan guide to version 1.3, not checked in the game; the wiki's happiness numbers may predate 1.3 (the guide says
   1.3 changed the room-sharing penalty to −20 per extra settler, up to −100).
7. **Two Point Hospital's duplicate rule.** One forum player says weak diminishing returns exist; another thread
   assumes none. Neither is developer data. What is solid is the behaviour: players spam the best-value item.
8. **Fields of Mistria** is still in early access; its unlock route and fuel durations may change. The design
   reason ("sprinklers would ruin perks tied to watering by hand") is a forum player's explanation, not a
   developer statement.
9. **Animal Crossing: New Horizons HHA bonuses** are community-datamined, and Nookipedia's per-item points
   section for New Horizons is a stub.
10. **Terraria fan calculators** were counted from search results, not opened.
11. **Insect-fat biodiesel** is search-level (paper abstracts and a review), offered only as optional flavour.

**About our own game (checked, but with limits):**

12. **"Sprinklers can't affect the bug simulation"** rests on a search for the wet-ground tile id
    (`garden_plot_wet`); it found only farming and weather handlers, a test and the client's placement controller.
    I did not audit every path by which crop state might reach the bug simulation. Crop pests (aphids and the like)
    are designed but not built; when they are, check again.
13. **Two waterings a day** is prototype data (`crops.json`), not a design decision; the recommendation's
    question 2 depends on the owner's answer.
14. **The one world clock, droughts, "the shared world runs the same for every player", and the plot panel as
    proposal P26** were read from the uncommitted working copy of `docs/gdd/overview.md` and
    `docs/product/BACKLOG.md` dated 2026-09-28; they may still be edited. How private plots relate to zones
    (their own zone, or an area inside one) is still open, so the "frozen zone catches up" note in A.2 may apply
    to the plot's zone or to the zone around it.
15. **Line numbers** quoted from OpenRCT2 and Data Layers are for the commits named in §2 and will drift.

**How this was checked, and what wasn't done:** the research skill's cold-critic step normally uses a fresh agent;
this task forbade sub-agents, so I ran the adversarial pass myself. It caught and fixed: straw mulch was described
as designed when it is only proposed (P11); the panel's category groups assumed a data field that is far coarser
today (`category`: furniture / decoration / lighting / structure); the two-waterings-a-day rule makes a once-a-dawn
sprinkler half as fast as careful hand-watering (now a question for the owner); colour-only outlines would fail
colour-blind players; Stardew's hopper (asked about) had not been read; and the frozen-zone rule means a plot's
sprinklers need the zone catch-up to apply missed dawns. A fresh critic may still find more —
especially on the scores, which are my judgement against the stated axes, not measurements.
