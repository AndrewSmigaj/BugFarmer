# Bug Farmer — the Game Design Document (GDD)

The one place the game's design lives. It gathers what is scattered across ~50 older documents (the January 2026
GDD, the December 2025 requirements, `economy/DECISIONS.md`, the brainstorms, the zone docs, backlog notes) into
one section per topic, and every section is reviewed by the owner before it is final.

**The plan for building it all:** [`docs/product/ROADMAP.md`](../product/ROADMAP.md).

## How a section is reviewed
1. I write the section from its sources: what you have already **decided** (restated in my words and dated — never
   quoted — so you can check I understood it), the
   **current design**, what is **built**, then my **proposals** (each checked against the idea lenses in
   `.claude/lenses.md` and by a separate reviewer) and the few **questions** that are genuinely yours to answer.
2. You open the review page, pick the section, and answer: each proposal gets **Keep / Cut / Change**, each question
   gets an option (or your own answer). Answers save as you go.
3. I read your answers back, write the results into the section (under "Decided", in my words and dated) and into
   `docs/product/economy/DECISIONS.md`, mark the section **final**, and republish the page.
4. Old documents are kept, with a one-line note at the top saying which section now holds their content.

Research-answerable calls are made by me and shown as proposals, never asked as questions. Nothing you have already
decided is asked again. Each proposal sits beside the part it belongs to — named at the end of that part and tagged
with it — so it can be answered while the part is being read (the overview showed its proposals only at the end,
2026-09-28).

**The review page:** a private page on claude.ai, generated from these files by `python3 tools/gdd/build_page.py`
(so it can't drift from them). Link: **https://claude.ai/artifact/CRtGxrNmWdXPVAVyNnwWW1** (private to the owner).
Answers are stored in the page's own database, one document per section (`answers/<§>`); read them back with the
`ArtifactData` tool (`list`, collection `answers`). Republish from another session by passing that URL.

## The item pass
Every item in the game and in the old designs — 1,204 rows — with a recommendation (keep, change, cut or add) and a
one-line reason (the owner's request of 2026-09-28, D55). The data is `item_table.jsonl`; the review page is built
from it by `python3 tools/gdd/build_items_page.py` and published at
**https://claude.ai/artifact/L9ftJfjRfcFD3yAB66qenD** (private to the owner). His marks — agree, disagree and a note
per row — are stored in that page's database, one document per item (`marks/<group>/items/<id>`, holding `{mark, note,
at}`); read them back with the `ArtifactData` tool, one kind at a time. The first version of the page
(https://claude.ai/artifact/3Sxunf4HDezB1fgAKFRZG1, 2026-09-28) stored a whole kind of item as one document and lost
the owner's first batch of marks when an older copy overwrote a newer one; it was replaced on 2026-09-29 and its
storage is not used.

**Where it stands (2026-10-02).**
- **Settled:** batch 1, the tool families and the pickaxes, axes and shovels, 34 rows (D69). Rows that are settled
  carry `"decided"` in the table and show a Decided label on the page.
- **Settled:** batch 3, the Armour (22 rows, D75): the metal sets are armour, the start is the Farmer's Outfit, gilded
  steel is cut and Fancy Armor replaces the platinum plate.
- **Marked, waiting for the last answers:** batch 2, the rest of Tools and the Weapons (110 rows). All but two of its
  questions are answered and recorded in D75 (still open: the harvest sickle, and the tools that bring a bug in
  alive); its rows are updated once those two are in.
- **Redone from scratch:** on 2026-10-01 the owner dropped every old accessory and potion and asked for new sets. They
  replace the old rows: 32 accessories and 3 kits, 12 potions and remedies, each kind with a row of rules first. The
  outfit roster (31 outfits and three family rows, with a rules row) and two powerful weapons were added for marking
  too. Rows for things already in the game stay: the flashlight, the bee charm, the lucky clover and the calm spray.
  The research behind them is in `docs/product/investigations/research-2026-10-01/`. His marks on the accessories are
  recorded in D75: twelve kept (station accessories at 30%, the figure he gave for most), the rest cut, a Drag Harness
  proposed in place of the running insoles, and jewelry (five pieces and a stand) added so a plot's happiness can come
  from things on display.
- **Batch 4, the potions (D74, D75):** marked and settled; the Night Vision Potion and the Venom Resistance Potion
  follow his answers, and one timed potion works at a time. Seven new potions from his list of effects wait for his
  marks.
- **Foods redone from scratch (D74), then around giant bugs as livestock (D75, D76):** 51 rows wait for the owner's
  marks: two rules rows, 8 staples, 38 dishes and three drinks, built on the research in
  `docs/product/investigations/research-2026-10-01/foods-real-dishes.md`. A meal raises Health and Stamina and many
  dishes add a boost; the stove takes the bugs themselves (the four cuts proposed in D75 went in D76). New dyes,
  cotton cloth and the plant rows were updated in D74 so every plant has a use.
- **The item system as a whole (D76):** a character sheet of six meters, three protections and standalone perks, with
  a job for each kind of item, accepted as a start. Rules first, rows second: the design sections are on the review
  page — §08 (gear and the character sheet) and §11 (food, cooking and potions) — and the rows are rewritten against
  them in one pass once they're answered.
- **How cooking plays (D77):** from recipes, with no experimenting and no Palia-style chains of preparing steps;
  recipes come singly and in books, found and bought; each recipe names its station, and the spit is back as one. The
  rules row, the station rows and a new recipe-books row follow the answer; §11 proposes the details (P9–P11) and asks
  which stations can cook which dishes (Q2).
- **Next:** the owner's answers on §08 and the rest of §11; the rare dishes and each dish's station, drafted as rows
  and past a reviewer first; the owner's marks on the foods, the jewelry, the new potions, the outfit roster and the
  two powerful weapons; batch 2's last two answers; then the other kinds in page order.

**How a batch goes.**
1. The owner marks rows on the page.
2. Read his marks with `ArtifactData` (`list`, one `marks/<group>/items` collection per kind of item) and line them
   up with the rows. Read every kind, not only the one he names, and compare each mark's time with the last batch:
   on 2026-10-01 his accessory marks were missed because only the potions were read.
3. Answer each note, checked against the decisions and the code; new ideas go past a reviewer before he sees them.
4. When he answers, record the outcome as a new D-entry in `docs/product/economy/DECISIONS.md`, in our own words.
5. Update the rows: settled rows get `"decided": "<date>"`, and item ids never change, because his marks are keyed by
   id.
6. Rebuild with `python3 tools/gdd/build_items_page.py`, republish `tools/gdd/_build/item_pass.html` to the same link,
   and commit.

## Sections, in review order
**Start with the overview** ([overview.md](overview.md)): the whole game as every design document describes it,
activity by activity — what is decided, in the prototype, designed and still open — written after reading all of them
(2026-09-26). The sections below are rebuilt from it once it has been checked.

Status: **review** = ready for your answers · **rework** = being redone · **draft** = not written yet · **final** = reviewed and settled.

| order | § | section | status | file |
|---|---|---|---|---|
| 0 | OV | **Start here:** the game as the documents describe it | final | [overview.md](overview.md) |
| 1 | 00 | Premise, pillars & what belongs in the world | final | [00_premise.md](00_premise.md) |
| 2 | 19 | Multiplayer & hosting | review | [19_multiplayer.md](19_multiplayer.md) |
| 3 | 01 | World & zones | rework | [01_world.md](01_world.md) |
| 4 | 02 | Progression & tiers | draft | [02_progression.md](02_progression.md) |
| 5 | 03 | Bestiary & tiers | draft | [03_bestiary.md](03_bestiary.md) |
| 6 | 04 | Ecology, the Ecologist & the Ecology tab | draft | [04_ecology.md](04_ecology.md) |
| 7 | 05 | Bug farming, catching & storage | draft | [05_bug_farming.md](05_bug_farming.md) |
| 8 | 06 | Farming & gardening | draft | [06_farming.md](06_farming.md) |
| 9 | 07 | Combat, enemies & bosses | draft | [07_combat.md](07_combat.md) |
| 10 | 08 | Gear, accessories & the character sheet | review | [08_gear.md](08_gear.md) |
| 11 | 09 | Tools & weapons | draft | [09_tools_weapons.md](09_tools_weapons.md) |
| 12 | 10 | Crafting, stations & materials | draft | [10_crafting.md](10_crafting.md) |
| 13 | 11 | Food, cooking & potions | review | [11_food.md](11_food.md) |
| 14 | 12 | Electricity & automation | draft | [12_electricity.md](12_electricity.md) |
| 15 | 13 | Fishing & water | draft | [13_fishing.md](13_fishing.md) |
| 16 | 14 | Mining & the underground | draft | [14_mining.md](14_mining.md) |
| 17 | 15 | Building, housing, private plots & City Hall | draft | [15_building.md](15_building.md) |
| 18 | 16 | NPCs, towns & the economy | draft | [16_npcs.md](16_npcs.md) |
| 19 | 17 | Exploration, secrets & loot | draft | [17_exploration.md](17_exploration.md) |
| 20 | 18 | Time, weather & light | draft | [18_time_weather.md](18_time_weather.md) |
| 21 | 20 | UI, onboarding & tutorials | draft | [20_ui.md](20_ui.md) |
| 22 | 21 | Art direction | draft | [21_art.md](21_art.md) |
| 23 | 22 | Audio & music | draft | [22_audio.md](22_audio.md) |

After these: one design bible per zone, under `zones/`.

## The shape of a section file (the page generator reads it)
```
# §NN · Title
<!-- gdd: id=NN status=review|draft|final updated=YYYY-MM-DD -->
## The experience        one paragraph: what it feels like to play
## Decided               the owner's decisions, restated in my words and dated (never quoted)
## The game, activity by activity   (the overview only) one ### heading per activity
## Current design        what the design documents already say
## As built              what exists in the game today (file references)
## How it will work      (optional) engineering the owner should see but not answer
## Proposals             ### P1. Title — body — a paragraph starting **Lenses:**
## Questions             ### Q1. Question? — context — options "- **A.** …" — "**Recommendation: A.** why"
## Sources
```
