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
decided is asked again.

**The review page:** a private page on claude.ai, generated from these files by `python3 tools/gdd/build_page.py`
(so it can't drift from them). Link: **https://claude.ai/artifact/CRtGxrNmWdXPVAVyNnwWW1** (private to the owner).
Answers are stored in the page's own database, one document per section (`answers/<§>`); read them back with the
`ArtifactData` tool (`list`, collection `answers`). Republish from another session by passing that URL.

## Sections, in review order
Status: **review** = ready for your answers · **rework** = being redone · **draft** = not written yet · **final** = reviewed and settled.

| order | § | section | status | file |
|---|---|---|---|---|
| 1 | 00 | Premise, pillars & what belongs in the world | rework | [00_premise.md](00_premise.md) |
| 2 | 19 | Multiplayer & hosting | rework | [19_multiplayer.md](19_multiplayer.md) |
| 3 | 01 | World & zones | rework | [01_world.md](01_world.md) |
| 4 | 02 | Progression & tiers | draft | [02_progression.md](02_progression.md) |
| 5 | 03 | Bestiary & tiers | draft | [03_bestiary.md](03_bestiary.md) |
| 6 | 04 | Ecology, the Ecologist & the Ecology tab | draft | [04_ecology.md](04_ecology.md) |
| 7 | 05 | Bug farming, catching & storage | draft | [05_bug_farming.md](05_bug_farming.md) |
| 8 | 06 | Farming & gardening | draft | [06_farming.md](06_farming.md) |
| 9 | 07 | Combat, enemies & bosses | draft | [07_combat.md](07_combat.md) |
| 10 | 08 | Gear: armour, clothing & accessories | draft | [08_gear.md](08_gear.md) |
| 11 | 09 | Tools & weapons | draft | [09_tools_weapons.md](09_tools_weapons.md) |
| 12 | 10 | Crafting, stations & materials | draft | [10_crafting.md](10_crafting.md) |
| 13 | 11 | Food, cooking & potions | draft | [11_food.md](11_food.md) |
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
## Current design        what the design documents already say
## As built              what exists in the game today (file references)
## How it will work      (optional) engineering the owner should see but not answer
## Proposals             ### P1. Title — body — a paragraph starting **Lenses:**
## Questions             ### Q1. Question? — context — options "- **A.** …" — "**Recommendation: A.** why"
## Sources
```
