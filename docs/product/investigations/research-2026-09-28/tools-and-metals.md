# Research: tool tiers and the metal ladder (2026-09-28)

Status: COMPLETE (research, 2026-09-28). Research only; nothing here is decided — the recommendations are for
the owner. The owner's rulings this research must respect (dated): tools never wear out (2026-09-27); no gold or diamond tools (2026-09-27); no magic
and no fantasy metals, the world is 2126 science (GDD P2).

Two questions:
1. Tool-tier progression — is "each new tool roughly halves the effort of the gather it unlocks" what Terraria does?
   What do real games change between tool tiers, by how much?
2. The metal ladder — which metals make sense as tools, where silver, gold and platinum go instead, and whether real
   bug biology (metal-reinforced mandibles and stings) supports a top tier made from giant-bug parts.

## 0. What the game does today (read from the code, 2026-09-28)

- The "halves the effort" line is in `docs/product/economy/progression.md:79` ("a new tool roughly halves the
  effort of the gather it unlocks") and is repeated in `docs/gdd/overview.md:588`.
- Pickaxes in `nakama/data/entities/items.json`: wood, stone, copper, iron, steel, silver, gold, platinum =
  `tool_tier` 1–8, with `mining_speed` 1.0, 1.3, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6 and a `durability` 50 → 880.
- **`mining_speed` is never used.** It is parsed (`nakama/modules/world/entities.go:33`,
  `BugFarmerClient/Assets/Scripts/Data/EntityDatabase.cs:467`) but no code reads it. The server break handler
  (`nakama/modules/world/handlers_world.go`, the `progress.CurrentHP--` line) takes exactly **1 HP per hit, whatever
  the tool**. So in the prototype a better pickaxe changes nothing about speed; tiers only gate.
- Gating is `required_tool_tier` on each breakable (`nakama/data/entities/occupants.json`): coal hp 4 / tier 1,
  copper hp 5 / tier 1, iron hp 6 / tier 2, silver hp 7 / tier 2, gold hp 8 / tier 3, platinum hp 10 / tier 4,
  diamond hp 12 / tier 5; oak tree hp 5 / axe tier 1. Check is `toolTier >= b.RequiredToolTier`
  (`nakama/modules/world/entities.go:263`). Across all entity data the highest pickaxe requirement is 5 and the
  highest axe requirement is 2, so pickaxe tiers 6–8 (silver, gold, platinum) and axe tiers 3–8 gate nothing today.
- If the unused `mining_speed` were switched on, consecutive tiers would be 1.30×, 1.23×, 1.25×, 1.20×, 1.17×,
  1.14×, 1.13× faster — a gentle ramp, nowhere near halving (halving = 2.00× per tier).


## 1. Sources

| # | Source (URL) | What it says (concrete numbers / technique) | Fits our constraints? |
|---|---|---|---|
| S1 | https://terraria.wiki.gg/wiki/Pickaxes (deep-read) | Per-pickaxe power and mining speed (ticks between hits, 60 ticks = 1 s; lower = faster). Copper 35% / 15, Tin 35% / 14, Iron 40% / 13, Lead 43% / 12, Silver 45% / 11, Tungsten 50% / 19, Gold 55% / 17, Platinum 59% / 15, Nightmare 65% / 15, Deathbringer 70% / 14, Molten 100% / 18, Cobalt 110% / 13, Palladium 130% / 12, Mythril 150% / 10, Orichalcum 165% / 9, Adamantite 180% / 8, Titanium 190% / 7, Chlorophyte 200% / 7, Picksaw 210% / 6, Luminite (Solar/Vortex/Nebula/Stardust) 225% / 6. The wiki: "Higher pickaxe power causes a pickaxe to deal more 'damage' to blocks per hit, and lower mining speed values mean that the pickaxe hits blocks more frequently"; "use time" is only the swing animation. | Yes as a reference shape. Terraria's durability-free tools match our "tools never wear out". |
| S2 | https://terraria.wiki.gg/wiki/Pickaxe_power (deep-read, fetched twice to confirm) | A tile breaks when accumulated damage reaches 100. Damage per hit = pickaxe power × a block factor: soft blocks (dirt, sand, clay) ×2; stone and most ores ×1; ebonstone, crimstone, pearlstone, hellstone, cobalt/palladium ore, dungeon brick ÷2; mythril/orichalcum ÷3; adamantite/titanium/lihzahrd ÷4; chlorophyte ÷5; damage 0 if power is below the block's minimum. Minimums: all eight basic pre-hardmode ores (copper … platinum) 0 (any pick); meteorite 50%; demonite/crimtane 55%; obsidian 55%; hellstone/ebonstone/crimstone/pearlstone 65%; dungeon brick 100%; cobalt/palladium 100%; mythril/orichalcum 110%; adamantite/titanium 150%; chlorophyte 200%; lihzahrd brick 210%. | Yes. The "hardness divisor" (harder ores take a fraction of your power) is a clean, readable technique we can copy. |
| S3 | https://terraria.wiki.gg/wiki/Axes and https://terraria.wiki.gg/wiki/Axe_power (deep-read) | Tree tiles have 100 HP; damage per hit = floor(axe power × 24) (Lead axe 50% → 12 → 9 hits; Molten Hamaxe 150% → 36 → 3 hits). Axe power / tool speed (ticks): Copper 35% / 21, Iron 45% / 19, Silver 50% / 18, Gold 55% / 18, Platinum 60% / 17, Molten Hamaxe 150% / 16. No tree needs a minimum axe power. | Yes. Axes in Terraria are pure speed (no gating), unlike pickaxes. |
| S4 | https://stardewvalleywiki.com/Tools (deep-read) | Upgrades at the blacksmith: Copper 2,000g + 5 copper bars, Steel 5,000g + 5 iron bars, Gold 10,000g + 5 gold bars, Iridium 25,000g + 5 iridium bars; each takes two days, during which you have no tool. Hoe and watering can: charged area 1 → 3 in a line → 5 in a line → 3×3 (9) → 6×3 (18); watering can holds 40 → 55 → 70 → 85 → 100. At skill 0 a pickaxe, axe or hoe use costs 2 energy; each skill level cuts 0.1. | Partly. The *area* idea fits farming tools; the two-day wait fits a single-player game, not a shared world where the tool is needed now. |
| S5 | https://stardewvalleywiki.com/Axe (deep-read) | Hits to fell a grown tree: basic 10, copper 8, steel 6, gold 4, iridium 2; small stump 5, 4, 3, 2, 1. Copper is needed for large stumps, steel for large logs. | Yes. A hit count that drops by a fixed step is very readable. |
| S6 | https://stardewvalleywiki.com/Pickaxe (deep-read) | Basic: mine rocks on floors 1–39 in 2 hits, copper nodes in 3. Copper: floors 1–39 in 1 hit, 40–79 in 2, copper nodes in 2. Steel: needed for farm boulders (4 hits), floors 40–79 in 1, copper nodes 1, iron 2, gold 3, iridium 6. Gold: breaks meteorites; floors 80–120 in 1; gold nodes 2, iridium 4. Iridium: quarry and Skull Cavern rocks in 1 hit; diamond nodes 2. Ore is gated by mine *depth*, not by pickaxe — even the basic pick can hit an iridium node, only slowly. | Yes. Shows "fewer hits" plus a few named obstacles (boulder, meteorite) as the gates. |
| S7 | https://stardewvalleywiki.com/Hoe (deep-read) | Hold to charge an upgraded hoe, release to till the area; the area can be steered while charging. Areas as S4. | Yes, a charge-for-area action suits farming, not mining. |
| S8 | https://minecraft.wiki/w/Breaking (deep-read, fetched twice) | "The base time in seconds is the block's hardness multiplied by: 1.5 if the player can harvest the block with the current tool; 5 if the player cannot", divided by the tool's speed; rounded up to whole ticks (1/20 s). Speeds: hand 1, wood 2, stone 4, copper 5, iron 6, diamond 8, netherite 9, gold 12. Stone (hardness 1.5): hand 7.5 s, wood 1.15, stone 0.6, iron 0.4, diamond 0.3, netherite 0.25, gold 0.2. Obsidian (hardness 50): diamond 9.4 s, netherite 8.35 s. With the wrong tier the block drops nothing and takes the ×5 time. | Yes as a formula. Its gold (fastest but weakest) only makes sense because Minecraft tools wear out — gold's catch is 32 uses. With no wear, a fast gold tool would simply be best, which is one more reason the owner's no-gold-tools ruling is sound. |
| S9 | https://minecraft.wiki/w/Tiers and https://minecraft.wiki/w/Pickaxe (deep-read) | Durability: gold 32, wood 59, stone 131, copper 190 (the Tiers table says 191), iron 250, diamond 1561, netherite 2031. Mining levels: "a block with the tag `minecraft:needs_stone_tool` requires a mining level of 1 or higher, … `needs_iron_tool` … 2 or higher, … `needs_diamond_tool` … 3 or higher"; wood and gold are level 0, stone and copper 1, iron 2, diamond 3, netherite 4. The Pickaxe page: "gold ore must be mined with an iron pickaxe, diamond pickaxe, or netherite pickaxe, or else the player harvests no item". Cobblestone: wood 1.5 s, stone 0.75, copper 0.6, iron 0.5, diamond 0.4, netherite 0.35, gold 0.25. Copper tools arrived in Java 1.21.9 (snapshot 25w31a). | Yes. Netherite shows a top tier that is a small speed step (×1.125) and mostly a status/durability step. |
| S10 | Core Keeper wiki: https://core-keeper.fandom.com/wiki/Pickaxes and https://core-keeper.fandom.com/wiki/Blocks (deep-read through the wiki's own API, `api.php?action=parse&prop=text`, because the normal page returned HTTP 402) | Base mining damage per pickaxe: Wood 15, Copper 42, Tin 83, Iron 180, Scarlet 289, (Ancient 385), Octarine 417, Galaxite 576, Solarite 735. Every wall block has health and a *damage reduction*: "If the player's mining damage is equal to or less than the wall's damage reduction, they will deal no damage to it, instead stating 'I need higher mining damage'". Dirt 135 HP / reduction 1; Clay 179 / 22; Stone 300 / 55; Grass 550 / 135; Beach 700 / 242; Desert 850 / 355; Crystal 950 / 535; Fossil 1415 / 1600. Since patch 0.6 walls take zero (not one) damage when your number is too low. Tools have durability 200–800 (not relevant to us). | Yes — the strongest technique found. One number both gates and speeds; see the worked table in §3. |
| S11 | Valheim wiki: https://valheim.fandom.com/wiki/Pickaxes, …/wiki/Axes, …/wiki/Trees, …/wiki/Copper_deposit, …/wiki/Silver_vein (deep-read via the wiki API) | Pickaxe damage: Antler 18, Bronze 25, Iron 33, Black metal 49 (×1.39, ×1.32, ×1.48). Antler and bronze mine stone, copper, tin, scrap; iron adds obsidian and silver; black metal adds black marble, soft tissue, flametal. Deposits have a per-node durability and a tool tier: copper node 50 HP, tier "Any"; silver node 40 HP, tier "Iron". Axe chop damage: Stone 20, Flint 30 (both "up to Pine"), Bronze 40, Iron 50 ("up to Birch and Oak"), Black metal 60 ("up to Yggdrasil shoots"). Trees: beech 80 HP (stone tier), birch 80 and oak 200 (bronze tier). "Metal deposits do not respawn." | Yes. Gates by named resource plus modest damage steps (×1.2–1.5); the big jumps come from new *places*, not from the tool. Non-respawning deposits in a shared world is a real design choice we must make too. |
| S12 | https://necessewiki.com/Tools and https://necessewiki.com/Tungsten_Pickaxe (deep-read); older numbers in https://scalacube.com/blog/necesse/a-guide-to-tools-in-necesse | Tool damage rises by a flat +15 per pickaxe: Wood 50, Copper 65, Iron 80, Gold 95, Frost 110, Demonic 125, Runic 140, Ivy 155, Quartz 170, Tungsten 185, Glacial 200, Dryad 215, Mycelium 230, Ancient Fossil 245. Almost every pickaxe's note is a key to the next place: Frost "Can mine walls in the Void Dungeon", Demonic "Can mine Runestone in plains caves", Quartz "Can mine Tungsten in deep forest caves", Tungsten "Can mine Obsidian and Glacial ore in deep snow caves" (tungsten needs 16 tungsten bars at a tungsten anvil). The ScalaCube guide (older game version, fossil pick at 195) says most pickaxes were "tier 0" and only Tungsten (2), Glacial (3) and Ancient Fossil (5) had higher tiers. | Yes. A flat +15 means the speed ratio shrinks every tier (×1.30 at first, ×1.07 at the end): the pickaxe is mostly a *key*. The version drift shows these numbers get re-tuned often. |
| S13 | https://docs.tmodloader.net/docs/stable/class_mod_tile.html (tModLoader, the Terraria modding API; deep-read) | Two numbers per block: `MinPick` — "The minimum pickaxe power required for pickaxes to mine this block" (default 0; meteorite uses 50); `MineResist` — "A multiplier describing how much this block resists harvesting. Higher values will make it take longer to harvest" (default 1; pearlstone 2 ≈ twice the hits, sand 0.5 ≈ half). | Yes. This is the engine-level shape of Terraria's system: a gate number and a toughness number per block, one power number per tool. It maps directly onto our `required_tool_tier` + `hp`. |
| S14 | Schofield et al. 2021, "The homogenous alternative to biomineralization: Zn- and Mn-rich materials enable sharp organismal 'tools' that reduce force requirements", *Scientific Reports* 11:17481 — https://www.nature.com/articles/s41598-021-91795-y ; full text read from Europe PMC (PMC8410824): https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8410824/fullTextXML (deep-read) | Measured fangs, stings and mandibles of a leafcutter ant (*Atta cephalotes*), spider (*Araneus diadematus*), scorpion (*Hadrurus arizonensis*) and a nereid worm. "Heavy element biomaterials" hold "zinc, manganese, bromine, and copper, in concentrations between about 1 and 25% of dry mass", found "in many insect orders, in spiders and most other arachnids, in many centipedes, crustaceans, marine worms". Zinc sits as single atoms bound to protein (no mineral grains), which allows nanometre-sharp edges. In every case the Zn/Mn material was harder and stiffer than the plain cuticle next to it; Zn harder than Mn in the same animal; four of six metal-rich materials were up to 3× more abrasion-resistant than their comparison regions (the ant mandible and spider fang did not differ significantly). Absolute level: "at least a factor of 2 harder than the hardest of the tested plastics (PMMA), with a hardness slightly greater than aluminum, but about 1/3 that of the 430 stainless steel and 1/10 of that of the fused silica". The authors *hypothesise*, from contact mechanics and simplified models, "a roughly 2/3 reduction in the force, energy, and muscle mass required to initiate puncture of stiff materials". Metal is up to "about 20% by mass" of the tooth. | Yes, strongly — real biology the examine text can quote. **But** it does not support "bug part harder than steel": the material is about aluminium-hard, a third of a common stainless steel. Its real strengths are sharpness, abrasion resistance and damage tolerance. |
| S15 | Schofield, Nesson & Richardson 2002, "Tooth hardness increases with zinc-content in mandibles of young adult leaf-cutter ants", *Naturwissenschaften* 89:579–583, doi:10.1007/s00114-002-0381-4 (abstract read via Europe PMC, PMID 12536282: https://europepmc.org/article/MED/12536282) | Zinc enters the mandible teeth of leaf-cutter ants in early adult life, "reaching concentrations of about 16% of dry mass"; "the hardness of the mandibular teeth increases nearly three-fold as the adults age and that hardness correlates with Zn content (r=0.91)"; "young adults rarely cut leaves partly because their mandibles are not yet rich in Zn". Also: "measured Zn concentrations reach 25% of dry mass in scorpion stings". | Yes — a lovely, true hook: a bug's jaw "cures" harder after it hatches. |
| S16 | Schofield et al. 2003, "Zinc is incorporated into cuticular 'tools' after ecdysis…", *J. Insect Physiology* 49:31–44, doi:10.1016/s0022-1910(02)00224-x (abstract via Europe PMC, PMID 12770014) | In the ant *Tapinoma sessile* zinc, manganese, calcium and chlorine build up in the mandible teeth after the moult, zinc peaking at 16% of dry mass; in the scorpion *Vaejovis spinigeris* the same happens in pedipalp teeth, leg claws, cheliceral teeth and the sting; zinc "may be deposited" through nanometre canals found only in the metal-bearing cuticle; the evidence suggests this "heavy metal-halogen fortification evolved before these groups diverged". | Yes — scorpions, ants, spiders all do it; it is general arthropod biology, not a one-species quirk. |
| S17 | Cribb et al. 2008, "Insect mandibles — comparative mechanical properties and links with metal incorporation", *Naturwissenschaften* 95:17–23, doi:10.1007/s00114-007-0288-1 (abstract via Europe PMC, PMID 17646951) | Six termite species compared by nanoindentation: "termite mandibles lacking metals when fully developed have lower values for hardness and elastic modulus. Zinc is linked to a relative 20% increase in hardness when compared with mandibles devoid of metals." Minor manganese showed no significant gain. | Yes — and it is a caution: the measured gain can be +20% (termites) as well as ~3× (young vs mature ant). Not every metal-rich jaw is super-hard. |
| S18 | Lichtenegger et al. 2002, "High abrasion resistance with sparse mineralization: copper biomineral in worm jaws", *Science* 298:389–392, doi:10.1126/science.1075433 (abstract via Europe PMC, PMID 12376695) | Bloodworm (*Glycera*) jaws hold the copper mineral atacamite; it "enhances hardness and stiffness"; the jaws show "an extraordinary resistance to abrasion, significantly exceeding that of vertebrate dentin and approaching that of tooth enamel". | Partly — a worm, not a bug (worms are allowed in the premise), but it shows copper as a real biological hardener. |
| S19 | Politi et al. 2012, "A Spider's Fang: How to Design an Injection Needle Using Chitin-Based Composite Material", *Advanced Functional Materials* 22:2519–2528 — https://advanced.onlinelibrary.wiley.com/doi/10.1002/adfm.201200063 ; press summary deep-read at https://phys.org/news/2012-05-incisive-solution-spider-venomous-fang.html | Wandering spider (*Cupiennius salei*) fang: "Zinc and chloride are found in the outer layer of the fang, the calcium occurs in its interior"; histidine rises toward the tip, where metal ions cross-link the proteins, making it "particularly hard and stiff"; the protein matrix spreads the stress so the fang does not snap; the authors suggest it as a model for special materials and hypodermic needles. | Yes — a real "graded" design (hard tip, tough base) that an engineered bug-tool could copy. |
| S20 | Wikipedia, "Hardnesses of the elements (data page)" — https://en.wikipedia.org/wiki/Hardnesses_of_the_elements_(data_page) (deep-read through the MediaWiki API; the page carries a "needs more citations" banner) | Pure, annealed elements. Mohs / Vickers (MPa) / Brinell (MPa): gold 2.5 / 188–216 / 188–245; silver 2.5 / 250 / 245–250; platinum 3.5 / 400–549 / 310–500; copper 3.0 / 343–369 / 235–878; tin 1.5 / — / 51–75; lead 1.5 / — / 38–50; zinc 2.5 / — / 327–412; iron 4.0 / 608 / 200–1180; nickel 4.0 / 638; cobalt 5.0 / 1043; titanium 6.0 / 830–3420; chromium 8.5 / 1060; tungsten 7.5 / 3430–4600; aluminium 2.75 / 160–350. (Divide MPa by ~9.8 for the usual HV number: gold ≈ 20 HV, silver ≈ 25 HV, platinum ≈ 40–55 HV, copper ≈ 35 HV, iron ≈ 60 HV.) | Yes. Gold and silver are the softest useful metals here — softer than pure copper; platinum is copper-soft; tin and lead are softer still. As *pure* metals, none of the eight is a tool material; tools come from alloys and heat treatment. |
| S21 | Wikipedia, "Tool steel" — https://en.wikipedia.org/wiki/Tool_steel and "High-speed steel" — https://en.wikipedia.org/wiki/High-speed_steel (deep-read via API) | Water-hardening tool steels "can attain high hardness (above 66 Rockwell C)"; O1 "can be hardened to 66 Rockwell C (HRC), though it is typically used at 61-63 HRC"; shock-resisting S grades 58–60 HRC with "very high impact toughness and relatively low abrasion resistance"; D2 "very wear resistant but not as tough". Tool steels suit tools because of "their distinctive hardness, resistance to abrasion and deformation, and their ability to hold a cutting edge at elevated temperatures". HSS: "hardness of 63 to 65 Rockwell C", keeps its temper at cutting heat; "The addition of cobalt … can give a hardness up to 70 Rockwell C"; history: Mushet steel 1868, Taylor & White 1899–1900. | Yes. Real steels trade hardness against toughness (hard D2 vs tough S grades) — a good, true source of *sidegrades*, not only upgrades. |
| S22 | Wikipedia, "Stellite" — https://en.wikipedia.org/wiki/Stellite and "Tungsten carbide" — https://en.wikipedia.org/wiki/Tungsten_carbide (deep-read via API) | Stellite: cobalt–chromium alloys (chromium up to 33%, tungsten up to 18%) "designed for wear resistance"; "outstanding hardness and toughness"; used for "saw teeth, hardfacing", and early lathe tools that beat "early carbon steel tools and even some high-speed steel tools". Tungsten carbide: "about 9.0–9.5 on the Mohs scale, and with a Vickers number of around 2600"; ~3× as stiff as steel; made by sintering WC powder with a cobalt binder; "used extensively in mining in top hammer rock drill bits … generally utilised as a button insert, mounted in a surrounding matrix of steel"; brittle — "can occasionally be shattered"; "roughly 10 times harder than 18 k gold". | Yes. Carbide *tips* in a steel body is exactly how real rock drills and picks are made today — a credible top mining tier that is not fantasy. |
| S23 | Wikipedia, "Ti-6Al-4V" — https://en.wikipedia.org/wiki/Ti-6Al-4V and "Chromium–vanadium steel" — https://en.wikipedia.org/wiki/Chrome-vanadium_steel (deep-read via API) | Ti-6Al-4V: "high specific strength and excellent corrosion resistance"; hardness "36 Rockwell C (Typical)"; "the poor shear strength and wear resistance of titanium alloys have limited their biomedical use". Cr-V steel: carbon 0.50%, chromium 0.80–1.10%, vanadium 0.18%; "Chromium and vanadium both make the steel more suitable for hardening. Chromium also helps resist abrasion, oxidation, and corrosion." | Titanium: light and rust-proof but *softer and less wear-resistant* than tool steel — a poor cutting-edge tier, a good light-armour or light-tool material. Cr-V: a real, everyday hand-tool steel — plausible, but it reads as "a kind of steel", not a new tier. |
| S24 | Wikipedia, "Bronze" — https://en.wikipedia.org/wiki/Bronze and "Arsenical bronze" — https://en.wikipedia.org/wiki/Arsenical_bronze (deep-read via API) | "Though bronze, whose Vickers hardness is 60–258, is generally harder than wrought iron, with a hardness of 30–80, the Bronze Age gave way to the Iron Age after a serious disruption of the tin trade". Bronze tools "were harder and more durable than their stone and copper … predecessors". Bronze does not spark, so it is used for "hammers, mallets, wrenches and other durable tools to be used in explosive atmospheres". Arsenical copper: "as little as 0.5 to 2 wt% As, giving a 10-to-30% improvement in hardness and tensile strength"; axe edges were "work-hardened by beating the working edge with a hammer". | Yes, and it corrects a common assumption: **plain (wrought) iron is not harder than good bronze**; iron won on cost and supply, and only steel (iron + carbon, quenched) is clearly better. Our tool ladder's copper → iron step should really be copper → bronze → steel, or iron must be understood as "iron and early steel". |
| S25 | Wikipedia, "Silver" — https://en.wikipedia.org/wiki/Silver , "Gold" — https://en.wikipedia.org/wiki/Gold , "Platinum" — https://en.wikipedia.org/wiki/Platinum (deep-read via API) | Silver: "exhibits the highest electrical conductivity, thermal conductivity and reflectivity of any metal"; "used in photovoltaics, electrical contacts and conductors, printed electronics, brazing alloys, catalysis, specialised mirrors … and antimicrobial materials"; "the lowest contact resistance of any m[etal]". Gold: "continued use in corrosion-resistant electrical connectors in all types of computerized devices (its chief industrial use)"; new gold goes "about 50% in jewelry, 40% in investments, and 10% in industry". Platinum: "a key component in catalytic converters, laboratory equipment, electrical contacts and electrodes, platinum resistance thermometers, dentistry equipment, and jewelry"; "As a fuel cell catalyst, platinum enables hydrogen and oxygen reactions"; used in green-hydrogen electrolysers. | Yes — all three have obvious, true jobs in an electric 2126: silver for solar panels, wiring contacts and anti-germ coatings; gold for corrosion-proof connectors and jewelry; platinum for catalysts, fuel cells, lab gear and sensors. None of those jobs is "pickaxe head". |
| S26 | Starbound wiki: https://starbounder.org/Tier and https://starbounder.org/Gold_Bar (deep-read) | Gear tiers: 1 Iron, 2 Tungsten, 3 Titanium, 4 Durasteel, 5 Aegisalt / Ferozium / Violium (three parallel materials with different stat leanings), 6 Solarium. Copper, silver, gold and platinum are *not* tiers; the gold bar goes into a battery, a cave detector, a pixel compressor, a sprinkler, fossil displays and gold blocks. | Yes — a shipped precedent for the direction this research was asked to test: precious metals feed electronics, utility and décor while tools and armour climb a separate hard-metal ladder. Its tier 5 (three parallel metals) shows a way to end a ladder in *choice* rather than one "best". |
| S27 | Wikipedia, "Titanium nitride" — https://en.wikipedia.org/wiki/Titanium_nitride and "Iridium" — https://en.wikipedia.org/wiki/Iridium (deep-read via API) | TiN: "an extremely hard ceramic material, often used as a physical vapor deposition (PVD) coating"; "Vickers hardness of 1800–2100"; "appears gold when applied as a coating"; used on "drill bits and milling cutters, often improving their lifetime by a factor of three or more". Iridium: Mohs 6.5, Vickers 1760–2200 MPa (≈ 180–225 HV), "very hard, brittle", second-densest metal (22.56 g/cm³); used in spark plugs, crucibles, chlorine electrodes, and historically fountain-pen nib points; "The Vickers hardness of pure platinum is 56 HV, whereas an alloy of 50 % platinum and iridium can reach over 500 HV". | TiN: yes — a real, *gold-coloured* top coating for tools, so the game can have a golden-looking top tool without a gold tool. Iridium: a platinum-group metal that is hard but brittle and ~3× as dense as steel — a tip material, not a tool body; platinum alloys can be hard, but never tool-steel hard and ruinously heavy. |
| S28 | "About iron & steel", Fur Trade Axes & Tomahawks — https://www.furtradetomahawks.com/about-iron-and-steel---25.html (deep-read; a specialist maker/collector page, not peer-reviewed) | "steel was expensive to produce in the 19th C. and earlier so iron was used for the body of most axes with a smaller piece of steel added to the iron." | Yes as flavour and as the honest meaning of an "iron" tool rung: an iron head with a steel edge welded in. |
| S29 | Wikipedia, "Scheelite" — https://en.wikipedia.org/wiki/Scheelite , "Erythrite" — https://en.wikipedia.org/wiki/Erythrite , and the cobalt section of "High-speed steel" (S21) (deep-read via API) | Scheelite (CaWO₄) is "an important ore of tungsten"; "Scheelite fluoresces under shortwave ultraviolet light, the mineral glows a bright sky-blue", and geologists use that glow when prospecting. Erythrite is crimson-to-pink "cobalt bloom" on cobalt arsenide minerals; "the prospector may use it as a guide to associated cobalt and native silver". HSS: "M35 … with 5% cobalt added … is also known as Cobalt Steel"; M42 (8% cobalt) has "superior red-hardness". | Yes — real, *visible* prospecting hooks for a pitch-dark underground: a UV lamp makes tungsten ore glow blue; pink bloom marks cobalt (and silver). "Cobalt steel" is a real, sold tool steel with a gamer-familiar name. |
| S30 | Wikipedia, "Mangalloy" (manganese / Hadfield steel) — https://en.wikipedia.org/wiki/Mangalloy (deep-read via API) | Steel with 11–15% manganese; "known for its high impact strength and resistance to abrasion once in its work-hardened state"; "will achieve up to three times its surface hardness during conditions of impact, without any increase in brittleness"; normally ~200 HB; "used in the mining industry, cement mixers, rock crushers, railway switches and crossings"; "generally considered to mark the birth of alloy steels" (Hadfield, 1882); nearly impossible to machine. | Yes — the real steel of rock-breaking equipment, and it hardens as it is struck. Manganese is also one of the two metals bugs use to harden stings and jaws (S14, S16): a true echo between the bug biology and the metal ladder. |

## 2. Codebase study (quoted code)

### 2a. Luanti (formerly Minetest) — engine + Minetest Game

Files read in full or in the relevant part, downloaded 2026-09-28:
- Engine: `src/tool.cpp` — https://github.com/luanti-org/luanti/blob/master/src/tool.cpp (function `getDigParams`, lines 367–420 at the time of reading)
- Engine docs: `doc/lua_api.md` — https://github.com/luanti-org/luanti/blob/master/doc/lua_api.md (sections "Digging time calculation specifics", "Tool Capabilities", lines ~2670–2830)
- Game: `mods/default/tools.lua` and `mods/default/nodes.lua` — https://github.com/luanti-org/minetest_game/blob/master/mods/default/tools.lua and …/nodes.lua

How a tool is described. Each tool lists, per material group (`cracky` = stone-like, `choppy` = wood, `crumbly` = soil),
a table of dig times by the block's rating (1 = toughest, 3 = easiest), how many uses it has, and the highest block
`level` it can touch (`mods/default/tools.lua`, lines 26–108):

```lua
minetest.register_tool("default:pick_wood", {
	tool_capabilities = {
		full_punch_interval = 1.2,
		max_drop_level=0,
		groupcaps={
			cracky = {times={[3]=1.60}, uses=10, maxlevel=1},
		},
…
minetest.register_tool("default:pick_stone", {
			cracky = {times={[2]=2.0, [3]=1.00}, uses=20, maxlevel=1},
…
minetest.register_tool("default:pick_bronze", {
			cracky = {times={[1]=4.50, [2]=1.80, [3]=0.90}, uses=20, maxlevel=2},
…
minetest.register_tool("default:pick_steel", {
			cracky = {times={[1]=4.00, [2]=1.60, [3]=0.80}, uses=20, maxlevel=2},
…
minetest.register_tool("default:pick_mese", {
			cracky = {times={[1]=2.4, [2]=1.2, [3]=0.60}, uses=20, maxlevel=3},
…
minetest.register_tool("default:pick_diamond", {
			cracky = {times={[1]=2.0, [2]=1.0, [3]=0.50}, uses=30, maxlevel=3},
```

Blocks carry the matching group (`mods/default/nodes.lua`): stone and coal ore `cracky = 3`; iron, copper, tin and
gold ore `cracky = 2`; mese and diamond ore `cracky = 1`; obsidian `{cracky = 1, level = 2}`; tree trunk `choppy = 2`;
dirt `crumbly = 3`.

The engine combines them (`src/tool.cpp`, `getDigParams`):

```cpp
	int level = itemgroup_get(groups, "level");
	for (const auto &groupcap : tp->groupcaps) {
		const ToolGroupCap &cap = groupcap.second;

		int leveldiff = cap.maxlevel - level;
		if (leveldiff < 0)
			continue;
…
		const auto time_o = cap.getTime(rating);
		if (!time_o.has_value())
			continue;
		float time = *time_o;

		if (leveldiff > 1)
			time /= leveldiff;
…
			const u32 real_uses = std::min<f64>(cap.uses * pow(3.0, leveldiff), U16_MAX);
```

And the docs state the gate in words (`doc/lua_api.md`, "Digging times"): "`times={[2]=2.00, [3]=0.70}` … would
result in the item to be able to dig nodes that have a rating of `2` or `3` for this group, and unable to dig the
rating `1`, which is the toughest." And: "`max_drop_level` … This value is not used in the engine; it is the
responsibility of the game/mod code to implement this."

**What this means — two separate gates plus a speed table.** (1) A tool with no time entry for a rating cannot dig it
at all (the wooden pick has only `[3]`, so it cannot touch any ore but coal). (2) A block with a `level` above the
tool's `maxlevel` is out of reach (obsidian needs `maxlevel` 2+). (3) Tools far above a block's level dig it faster
(`time /= leveldiff`), so old easy blocks keep getting quicker without anyone tuning them.

Dig times that result (computed from the code above; seconds; × = speed-up over the previous pick):

| Block | wood | stone | bronze | steel | mese | diamond |
|---|---|---|---|---|---|---|
| stone / coal (cracky 3) | 1.60 | 1.00 (×1.60) | 0.45 (×2.22) | 0.40 (×1.12) | 0.20 (×2.00) | 0.17 (×1.20) |
| iron, copper, tin, gold ore (cracky 2) | cannot | 2.00 | 0.90 (×2.22) | 0.80 (×1.12) | 0.40 (×2.00) | 0.33 (×1.20) |
| mese, diamond ore (cracky 1) | cannot | cannot | 2.25 | 2.00 (×1.12) | 0.80 (×2.50) | 0.67 (×1.20) |
| obsidian (cracky 1, level 2) | cannot | cannot | 4.50 | 4.00 (×1.12) | 2.40 (×1.67) | 2.00 (×1.20) |

The pattern: Minetest Game moves in **pairs** — a big step (stone→bronze ×2.2, steel→mese ×2.0) that also opens a
new ore class, then a small "side-grade" step (bronze→steel ×1.12, mese→diamond ×1.20) that opens nothing new. Only
the big steps come close to "halving". Wear (`uses`) is irrelevant for us (tools never wear out).

### 2b. VoxeLibre (a Minecraft-like game on Luanti) — the Minecraft formula in open code

Files: `mods/ITEMS/mcl_tools/init.lua` and `mods/CORE/_mcl_autogroup/init.lua` —
https://git.minetest.land/VoxeLibre/VoxeLibre/src/branch/master/mods/ITEMS/mcl_tools/init.lua and
https://git.minetest.land/VoxeLibre/VoxeLibre/src/branch/master/mods/CORE/_mcl_autogroup/init.lua (downloaded 2026-09-28).

Per-pickaxe speed multiplier and level (`mcl_tools/init.lua`, lines 56–160):

```lua
		pickaxey = { speed = 2, level = 1, uses = 60 }      -- pick_wood
		pickaxey = { speed = 4, level = 3, uses = 132 }     -- pick_stone
		pickaxey = { speed = 6, level = 4, uses = 251 }     -- pick_iron
		pickaxey = { speed = 12, level = 2, uses = 33 }     -- pick_gold
		pickaxey = { speed = 8, level = 5, uses = 1562 }    -- pick_diamond
		pickaxey = { speed = 9.5, level = 6, uses = 2031 }  -- pick_netherite
```

Dig time from block hardness (`_mcl_autogroup/init.lua`, `get_digtimes`, lines 130–156):

```lua
	for _, hardness in pairs(hardness_values[group]) do
		local digtime = (hardness or 0) / speed
		if can_harvest then
			digtime = digtime * 1.5
		else
			digtime = digtime * 5
		end

		if digtime <= 0.05 then
			digtime = 0
		else
			digtime = math.ceil(digtime * 20) / 20
		end
```

**What this means.** Speed is one number per material; every block's time is hardness ÷ speed, so the ratio between
two tiers is the same on every block (stone→iron is always ×1.5). The only gate is the level. Note VoxeLibre ranks
gold *above* wood (level 2 of 6) but still gives it only 33 uses — the "fast but flimsy" gold only balances because
tools break. VoxeLibre also uses 9.5 for netherite where Minecraft uses 9: clones drift, so read the source, not the
wiki, when exact numbers matter.


## 3. Question 1 — tool-tier progression

Search angles used: **by game** (Terraria, Stardew Valley, Minecraft, Core Keeper, Valheim, Necesse wikis); **by
engine/library feature** (Luanti `tool_capabilities` / `getDigParams`, VoxeLibre `_mcl_diggroups`, tModLoader
`MinPick` / `MineResist`); **by technique** ("tool damage vs block health", "damage reduction threshold", "speed
multiplier per material"); **by problem** ("is it worth upgrading / skipping pickaxe tiers", "upgrades that feel
meaningful" — https://terraria.guide/guides/early-game/ore-progression/ and
https://www.gamedeveloper.com/design/how-to-power-up-players-with-upgrades).

### 3.1 Short answer: is "each tool halves the effort" what Terraria does?

**No.** Terraria's pickaxes barely speed up between neighbouring tiers. On ordinary stone (and on every one of the
eight basic pre-hardmode ores, which take the same damage as stone) the effort per block is:

| Pickaxe | Power | Ticks between hits | Hits on stone | Effort (ticks) | vs previous |
|---|---|---|---|---|---|
| Copper | 35% | 15 | 3 | 45 | — |
| Tin | 35% | 14 | 3 | 42 | ×1.07 |
| Iron | 40% | 13 | 3 | 39 | ×1.08 |
| Lead | 43% | 12 | 3 | 36 | ×1.08 |
| Silver | 45% | 11 | 3 | 33 | ×1.09 |
| Tungsten | 50% | 19 | 2 | 38 | ×0.87 (slower) |
| Gold | 55% | 17 | 2 | 34 | ×1.12 |
| Platinum | 59% | 15 | 2 | 30 | ×1.13 |
| Deathbringer | 70% | 14 | 2 | 28 | ×1.07 |
| Molten | 100% | 18 | 1 | 18 | ×1.56 |
| Cobalt → Luminite | 110–225% | 13 → 6 | 1 | 13 → 6 | ×1.0–1.4 each |

(Computed from S1 + S2: a block breaks at 100 damage; a hit deals the pickaxe power; effort = hits × ticks between
hits.) Copper to platinum — eight pickaxes — is only **1.5× faster in total**. Axes do a little more: copper → iron →
silver → gold → platinum fell a tree in 273 → 190 → 162 → 144 → 136 ticks (×1.44, ×1.17, ×1.12, ×1.06; **2.0× over
the whole early ladder**), and the Molten Hamaxe is ×2.8 over platinum (S3).

What Terraria's tiers mainly change is **what you can mine**, and even that only at a few thresholds: meteorite
(50%), demonite / crimtane / obsidian (55%), hellstone (65%), dungeon brick and cobalt/palladium (100%),
mythril/orichalcum (110%), adamantite/titanium (150%), chlorophyte (200%), lihzahrd (210%) (S2). The basic ores need
nothing, so most early pickaxes open nothing new — and players skip them: a player guide advises "Skip Copper/Tin
armor entirely. Craft a Copper/Tin Pickaxe if needed, then head straight to Iron/Lead or deeper"
(https://terraria.guide/guides/early-game/ore-progression/).

The hard ores also resist: hellstone, cobalt and palladium take ½ the power, mythril ⅓, adamantite ¼, chlorophyte ⅕.
So the pickaxe that first reaches an ore is slow on it, and later picks speed it up. On adamantite ore, for
example: Mythril pick 30 ticks → Orichalcum 27 → Adamantite 24 → Titanium 21 → Chlorophyte 14 — again steps of
×1.1, with one ×1.5 jump when the hit count drops from 3 to 2.

### 3.2 What a tier improves in each game

| Game | What a tier improves | Ratio between consecutive tiers (measured) | How access is gated |
|---|---|---|---|
| Terraria — pickaxes | Power (damage per hit) and hit rate | ×0.87–1.13 across the 8 early tiers (1.5× total); ×1.56 at Molten; ×1.0–1.4 in hardmode | Minimum power per block (50/55/65/100/110/150/200/210%); hard ores take ½ … ⅕ of the power |
| Terraria — axes | Axe power (hits per tree) and hit rate | ×1.44, 1.17, 1.12, 1.06 (2.0× total); ×2.8 to Molten Hamaxe | None — every axe fells every tree |
| Stardew Valley — axe / pickaxe | Fewer hits | Tree hits 10 → 8 → 6 → 4 → 2 (×1.25, 1.33, 1.5, 2.0) | A few named obstacles: large stump (copper axe), large log (steel axe), farm boulder (steel pick), meteorite (gold pick). Ore itself is gated by mine depth, not by the pick |
| Stardew Valley — hoe / watering can | Area of a charged use | 1 → 3 → 5 → 9 → 18 tiles (×3.0, 1.67, 1.8, 2.0) | None; cost 2k/5k/10k/25k gold + 5 bars, two days without the tool |
| Minecraft | One speed multiplier per material | Wood→stone ×2.0, stone→iron ×1.5, iron→diamond ×1.33, diamond→netherite ×1.125 (copper, new in 2025, sits ×1.25 above stone) | Mining level: stone tool for iron ore, iron tool for gold/diamond ore, diamond tool for obsidian; below it, no drop |
| Luanti — Minetest Game | A dig-time table per block rating, divided by level difference | Alternating big and small steps: ×1.6, ×2.22, ×1.12, ×2.0, ×1.2 | A tool lacking a time for a rating cannot dig it; block `level` above the tool's `maxlevel` cannot be dug |
| Core Keeper | Mining damage vs the block's health and damage reduction | Damage ×2.8, 1.98, 2.17, 1.61, 1.44, 1.38, 1.28 — but the *felt* change on a block is ×3–5 (see 3.3) | Damage must exceed the block's damage reduction, else zero damage and "I need higher mining damage" |
| Valheim | Pickaxe / chop damage | Pick 18 → 25 → 33 → 49 (×1.39, 1.32, 1.48); axe 20 → 30 → 40 → 50 → 60 | Tool tier per deposit and per tree type (oak/birch need bronze, Yggdrasil needs black metal); big progress comes from new biomes |
| Necesse | Tool damage, +15 per tier | ×1.30 falling to ×1.07 (50 → 245 over 14 picks) | Nearly every pick is the key to the next place's ore |
| Bug Farmer prototype | Nothing yet (`mining_speed` 1.0 → 3.6 is never read; 1 HP per hit) | (would be ×1.30 falling to ×1.13) | `required_tool_tier`; pickaxe tiers 6–8 and axe tiers 3–8 gate nothing |

**Pattern.** No game halves the effort at every tier. Halving happens in three places: the very first step
(Minecraft wood→stone ×2.0), the "big" steps of a big/small pair (Luanti ×2.0–2.2 every other tier), and — most
usefully — **on the previous frontier when the next tool arrives** (Core Keeper, and to a lesser degree Terraria's
hard ores). Everywhere, the thing that changes most between tiers is *what you can reach*; speed is the secondary
reward. Where speed is the only reward (Terraria's early picks, Necesse's late ones) players treat tiers as skippable.

### 3.3 The best technique found: a toughness threshold (Core Keeper)

Core Keeper gives each block a health and a *damage reduction*; a pickaxe deals (roughly) its mining damage minus
that reduction, and nothing at all if it does not exceed it (S10). Computed hits per block (lowest damage roll of
each pickaxe):

| Block (health / reduction) | Wood 15 | Copper 42 | Tin 83 | Iron 180 | Scarlet 289 | Octarine 417 | Galaxite 576 | Solarite 735 |
|---|---|---|---|---|---|---|---|---|
| Dirt (135 / 1) | 10 | 4 | 2 | 1 | 1 | 1 | 1 | 1 |
| Clay (179 / 22) | cannot | 9 | 3 | 2 | 1 | 1 | 1 | 1 |
| Stone (300 / 55) | cannot | cannot | 11 | 3 | 2 | 1 | 1 | 1 |
| Grass (550 / 135) | cannot | cannot | cannot | 13 | 4 | 2 | 2 | 1 |
| Beach (700 / 242) | cannot | cannot | cannot | cannot | 15 | 4 | 3 | 2 |
| Desert (850 / 355) | cannot | cannot | cannot | cannot | cannot | 14 | 4 | 3 |
| Crystal (950 / 535) | cannot | cannot | cannot | cannot | cannot | cannot | 24 | 5 |

Read along a row: the first pickaxe that can touch a biome's wall needs **9–24 hits** ("I can barely dent it"); the
next pickaxe needs **3–5** (×3–5 faster); two tiers on it is 1–2 hits. Read down a column: a player always has one
slow frontier material and everything older is quick. One number per tool does both jobs — gate and speed — and it
cannot run away: the newest material is always slow with the tool that first reaches it, however many tiers there
are. This is the old design line's "halving" in an accurate form: **each new tool roughly halves (or better) the
effort on what the previous tool had only just unlocked.**

### 3.4 Candidate rules for Bug Farmer (scored 1–5; higher is better)

| | Rule | Feel of progress | Pacing over 8 tiers | Readability | Shared-world fit | Total | Keep / reject |
|---|---|---|---|---|---|---|---|
| A | Halve the effort every tier | 5 | 1 — 2⁷ = 128× by tier 8; with our 4–12 HP blocks every block is one hit by tier 4–5 | 4 | 2 — a veteran strips shared ore and trees ~100× faster than a newcomer | 12 | Reject: no surveyed game does it; it trivialises mining (a main loop, D13) |
| B | Terraria-style: tiers mainly gate, modest speed (×1.1–1.25) | 3 — gate moments are great, the tiers between feel flat and get skipped | 5 | 4 | 5 | 17 | Keep the *gate*, reject the flat speed |
| C | Stardew-style: fewer hits by a fixed step, bigger area | 4 | 3 — hits reach the floor of 1 within ~5 tiers | 5 — hit counts and tile areas are visible | 3 — the blacksmith wait suits single-player only | 15 | Keep **area** for the few farm-tool steps only |
| D | Minecraft-style: one speed multiplier per material + harvest level | 4 early, 2 late (×1.125 at the top) | 3 | 3 — you feel it, you never see it | 4 | 14 | Reject as the main rule; its gold only works with wear, which we removed |
| E | Core Keeper-style toughness threshold: damage per hit = tool power − material toughness; ≤ 0 = "Need a better tool" | 5 — "barely dent it" then "now it's easy" | 5 — self-limiting: the newest material always starts slow | 4 — one power number per tool; hit counts visible | 4 — equal gates for everyone; a veteran is at most ~10× faster, and only on old materials | 18 | **Pick** (with F's parts) |
| F | Hybrid: E for pickaxe, axe and shovel; C's area idea for the few farm-tool steps (D12 keeps the watering can at small + large); every tier must open something named | 5 | 5 | 4 | 4 | 18 | **Recommended** (E is its core) |

### 3.5 Recommendation (numbers are a shape, not tuning)

**Rule F, built on the toughness threshold.**
1. **Gathering tools (pickaxe, axe, shovel):** each tool has one *power* number; each material has a *toughness*
   and a *health*. A hit deals power − toughness; if that is zero or less the game says "Need a better tool" (the
   message already exists). Keep the swing speed the same at every tier — the change the player sees is the hit
   count, which the break-progress crack overlay already shows per hit (`BreakingVisual.SetProgress`, driven by
   the server's BreakProgress message).
2. **Shape:** power grows about **×1.3 per tier** (8 tiers ≈ 6× from wood to top). A material first reachable at
   tier *k* gets toughness ≈ **0.8 × the power of tier *k*** (so tier *k*−1 cannot dent it) and health such that tier
   *k* needs **about 8–10 hits** (the prototype's ores already take 4–12 hits at 1 HP per hit; Core Keeper's frontier
   takes 9–24, Terraria's 3–4). That gives, on any material, by tiers above the one that unlocks it:
   **10 → 4–5 → 3 → 2 → 1** hits. (Checked numerically: power ×1.25–1.3 with toughness 0.8–0.85 of the unlocking
   power all give 10 → 4–5 → 3 → 2 → 1–2.) An equivalent, even simpler way to build it is a small table of hits by
   "tool tier minus material tier" (0 → 10, 1 → 4–5, 2 → 3, 3 → 2, 4+ → 1, below 0 → cannot).
3. **Every tier opens something named** — an ore, a tougher stone, a hard wood, a zone's walls — so no tier is
   skippable filler. Today tiers 6–8 open nothing (§0); whatever the final ladder is, each rung needs its own key
   material.
4. **Farm tools stay light on tiers.** The watering can is already settled at small + large only, with farming
   not gated behind fancy metals (D12 in `docs/product/economy/DECISIONS.md`). Where a farm tool does improve (the
   large can, the hoe, the scythe's sweep), make the improvement *area*, not speed — Stardew's 1 → 3 → 5 → 9 → 18
   tiles is a shape that reads well. How many hoe and scythe steps there are is the owner's call.
5. **Axes gate sparingly** (Valheim gates oak and Yggdrasil; Terraria gates no tree): most trees open to any axe;
   a few big, tough trees need more. This matches D12's saw — a wood tool a tier above the axes for larger,
   tougher trees, with better axes returning above it.
6. **Replace the doc line.** Restate "a new tool roughly halves the effort of the gather it unlocks" as: "the first
   tool that can take a new material takes it slowly (about eight to ten hits); each tier after that roughly halves the hits
   on it, down to one." That keeps the intent and matches how the good games actually behave.

What the code would need (for whoever builds it, not decided here): the server's break handler takes 1 HP per hit
(`handlers_world.go`, `progress.CurrentHP--`); this rule needs a per-hit damage from the tool's power and the
material's toughness. The unused `mining_speed` field is the natural slot for *power*. A shared-world detail found on
the way: today a second player's hit on the same block restarts its progress under that player (the same handler:
`if !exists || progress.PlayerID != userID` creates fresh progress at full HP), so two players cannot dig one block
together. If co-op digging should add up, that is a separate small change.


## 4. Question 2 — the metal ladder

Search angles used: **by material science** (hardness tables, tool steels, carbides, coatings); **by history /
problem** (why bronze gave way to iron, why iron axes got steel edges); **by industrial use** (what silver, gold and
platinum actually do in modern technology); **by biology** (heavy-element biomaterials in arthropod mandibles,
stings and fangs — Europe PMC full-text and abstract searches); **by game** (tier names and order in Terraria,
Minecraft, Stardew Valley, Core Keeper, Valheim, Necesse, Starbound).

### 4.1 What makes a metal good for a tool

A pick point or axe edge needs, at the same time, **hardness** (it does not dent or wear down), **toughness** (it
does not chip or snap on impact) and the ability to be **heat-treated** so it holds an edge. Pure metals are soft;
almost every real tool is an alloy that has been hardened. Hard and tough pull against each other (S21: the hard,
wear-resistant D2 steel is "not as tough"; the shock-resisting S steels are tough but less wear-resistant).

| Material | Hardness (source) | What it means | As a tool |
|---|---|---|---|
| Lead | Brinell 38–50 MPa, Mohs 1.5 (S20) | softest here | never |
| Tin (alone) | Brinell 51–75 MPa, Mohs 1.5 (S20) | too soft; its job is making bronze | never alone |
| Gold | Vickers ≈ 190–220 MPa (≈ 20 HV), Mohs 2.5; density 19.3 g/cm³ (S20, S25) | softer than pure copper and ~2.5× as heavy as steel | no — agrees with the owner's ruling |
| Silver | ≈ 25 HV, Mohs 2.5 (S20) | softer than pure copper | no |
| Platinum | ≈ 40–56 HV, Mohs 3.5; density 21.5 g/cm³ (S20, S25, S27) | about copper-soft, ~2.7× as heavy as steel | no |
| Copper (pure) | ≈ 35 HV, Mohs 3.0 (S20) | the first metal tools; hammering the edge hardens it | early rung |
| Arsenical copper | +10–30% hardness over copper (S24) | what "copper" tools really were | the honest meaning of a copper rung |
| Bronze (copper + tin) | 60–258 HV (S24) | harder than wrought iron | a real rung |
| Wrought iron | 30–80 HV (S24) | *softer* than good bronze; won on supply, not hardness; axes got a steel edge welded in (S28) | a rung only as "iron with a steel edge" |
| Hardened tool steel | 58–66 HRC (S21) (≈ 650–860 HV, my conversion) | the modern baseline for edges | a rung |
| Cobalt high-speed steel | 63–65 HRC, up to 70 with cobalt; stays hard when hot; sold as "Cobalt Steel" (M35/M42) (S21, S29) | today's premium drill-bit steel | a rung |
| Cobalt–chrome ("Stellite") | "outstanding hardness and toughness"; saw teeth, hardfacing (S22) | a trademark; generic name is cobalt-chrome | a possible rung |
| Manganese (Hadfield) steel | ~200 HB, rising up to 3× at the surface under impact, "without any increase in brittleness" (S30) | the steel of rock crushers and mining gear; a poor cutting edge (cannot be quench-hardened or easily ground) | a possible rung for picks and shovels |
| Titanium alloy (Ti-6Al-4V) | 36 HRC; "poor shear strength and wear resistance" (S23) | light and rust-proof, a weak edge | light armour / light gear, **not** a tool rung |
| Tungsten carbide | ~2600 HV, Mohs 9–9.5; brittle, "can occasionally be shattered"; set as tips in steel bodies of rock drills and mining picks (S22) | among the hardest practical tool materials — only abrasives such as cubic boron nitride and diamond can polish it (S22) | the top **mining** rung (tips only; too brittle for swords) |
| Titanium nitride coating | 1800–2100 HV; **gold-coloured**; ×3 tool life on drill bits (S27) | a finish, not a body | a real way to make the top tool *look* golden |
| Platinum–iridium 50/50 | > 500 HV (S27) | hard for a precious alloy, still below tool steel, ~3× steel's weight, extremely rare | no |
| Zinc-rich bug cuticle | slightly harder than aluminium, ≈ ⅓ of 430 stainless (S14) | very sharp, abrasion-resistant, tough, light | blades, stings, sickles — **not** picks |

**So:** gold, silver and platinum are wrong as tools for the same reason — they are *softer than copper* and much
heavier than steel. Dropping gold but keeping silver and platinum would contradict the reason gold was dropped.
Tin and lead are softer still. The strong tool materials beyond steel are real and nameable: cobalt steel, cobalt-
chrome, tungsten carbide, with a titanium-nitride finish.

### 4.2 Real jobs for the precious metals in an electric 2126

| Metal | Real modern use (source) | Possible Bug Farmer job (ideas for the owner, not decided) |
|---|---|---|
| Copper | best-value electrical conductor ("the high electrical conductivity of pure copper", S24) | early tools *and* later the wire and power-line metal |
| Silver | "highest electrical conductivity, thermal conductivity and reflectivity of any metal"; photovoltaics, electrical contacts, printed electronics, brazing, mirrors, antimicrobial coatings (S25) | solar panels and contacts for the power system; mirrors/reflectors; brazing for pipes and sprinklers; silverware and jewelry |
| Gold | "corrosion-resistant electrical connectors in all types of computerized devices (its chief industrial use)"; ~50% of new gold goes to jewelry (S25) | connectors for powered stations and automation; gilding (the gilded-steel outfit, crowns, trophies, frames); jewelry; trade value |
| Platinum | "catalytic converters, laboratory equipment, electrical contacts and electrodes, platinum resistance thermometers"; fuel-cell and green-hydrogen catalyst (S25) | a chemistry/fertiliser station's catalyst; fuel cells or electrolysers to store wind and solar power; a precise thermometer for a bug incubator; lab gear for the bug extractor; jewelry |

One constraint to respect: the overview records that "the electronics are bought, never player-made (D1, D26)".
D1 itself says complex stations such as the electronics bench are bought from a merchant. So if electronics stay
bought, precious metals can still feed them as **trade goods** or **commission materials** (bring silver, the
engineer builds your panel) — that choice is the owner's.

### 4.3 The biology: do real bugs support a top tier made from giant-bug parts?

**What the papers show (S14–S19):**
- Metal-hardened "tools" are general arthropod biology, not a curiosity: zinc, manganese, bromine and copper at
  about 1–25% of dry mass, in "many insect orders, in spiders and most other arachnids, in many centipedes,
  crustaceans, marine worms" (S14). Ants, scorpions, spiders, termites and centipedes all do it (S14, S16, S17).
- Leaf-cutter ant mandible teeth reach ~16% zinc by dry mass and get **nearly three times harder** as the young adult
  matures and the zinc arrives; hardness tracks zinc (r = 0.91); young ants rarely cut leaves (S15). Zinc goes in
  *after* the moult, probably through nanometre canals (S16). Scorpion stings reach 25% zinc (S15).
- The size of the gain varies: termites show about **+20%** hardness with zinc (S17).
- Absolute level: the zinc/manganese material is "slightly greater than aluminum" in hardness, "about 1/3 that of
  the 430 stainless steel" (S14). Its real advantages are **sharpness** (zinc is bound atom by atom, so edges can be
  nanometre-sharp), **abrasion resistance** (four of the six metal-rich materials tested were up to 3× more
  abrasion-resistant than plain cuticle; the ant mandible and spider fang were not significantly different) and
  **damage tolerance**. From contact mechanics and simplified models the authors *hypothesise* "a roughly 2/3
  reduction in the force … required to initiate puncture of stiff materials" compared with plain cuticle (S14).
- Spider fangs are graded: zinc and chlorine on the outer skin, calcium inside, histidine and metal cross-links
  rising toward a "particularly hard and stiff" tip (S19). A bloodworm's jaw uses a copper mineral and resists
  abrasion nearly as well as tooth enamel (S18).

**Verdict.** The science **supports** giant-bug parts as a real, excellent material for **cutting and piercing**
— blades, spear tips, sickles, shears: light, very sharp, never rusting, slow to wear. It **does not support** a
bug-part tool *harder than steel*: the best measured bug material is roughly aluminium-hard, a third of an ordinary
stainless steel. Breeding a bug giant makes the part bigger, not harder (hardness is a property of the material, not
of its size — my reasoning, see §5). So a mandible **pickaxe** above steel would need the examine text to lie; a
mandible **sickle** or a sting **spear** would not.

A real hook the game could use (owner's taste): a mandible from a **mature** ant is the harder material, because the
zinc arrives after the ant hatches (S15, S16) — a bug-farming reason to raise ants to adulthood before harvesting.

### 4.4 How other games name and order their top tiers

| Game | Ladder, low → high | What the top is made of | Where the precious metals sit |
|---|---|---|---|
| Terraria (S1, S2) | copper/tin, iron/lead, silver/tungsten, gold/platinum, (demonite/crimtane, molten), cobalt/palladium, mythril/orichalcum, adamantite/titanium, chlorophyte, luminite | invented (mythril, orichalcum, adamantite, chlorophyte, luminite) mixed with real names (cobalt, palladium, titanium) | early pickaxe tiers |
| Minecraft (S8, S9) | wood, stone, copper, iron, diamond, netherite (+ gold) | a gem and an invented alloy | gold is a fast-but-fragile oddity that only works because tools wear out |
| Stardew Valley (S4) | basic, copper, steel, gold, iridium | real metals; iridium on top | gold is a tool tier |
| Core Keeper (S10; ore list: https://xgamingserver.com/blog/core-keeper-mining-ores-guide/) | wood, copper, tin, iron, scarlet, (ancient), octarine, galaxite, solarite | invented | gold is an ore, not a pickaxe tier |
| Valheim (S11) | antler, bronze, iron, black metal (silver needs the iron pick) | invented (black metal, flametal) | silver is a mined metal |
| Necesse (S12) | wood, copper, iron, gold, frost, demonic, runic, ivy, quartz, tungsten, glacial, dryad, mycelium, ancient fossil | mostly invented, some real (quartz, tungsten) | gold is an early pick tier |
| Starbound (S26) | iron, tungsten, titanium, durasteel, aegisalt / ferozium / violium, solarium | real middle, invented top, and a three-way split at tier 5 | copper, silver, gold, platinum feed batteries, detectors, sprinklers, décor — not tiers |

**Pattern.** Every game keeps real metals low and *invents* its top. Bug Farmer cannot invent (no fantasy metals),
so its top has to come from real engineering or real biology. Real top names already read well to players:
tungsten (Terraria, Necesse, Starbound), cobalt and titanium (Terraria, Starbound). Starbound is the one shipped
precedent for taking precious metals out of the gear ladder and putting them into technology — the direction this
research was asked to test.

### 4.5 Candidate ladders (scored 1–5; higher is better)

| | Ladder | Science (2126, no magic) | Readable progression | Bug-farming theme | Tier count (8 today) | What happens to silver / gold / platinum | Total | Keep / reject |
|---|---|---|---|---|---|---|---|---|
| A | Today minus gold: wood, stone, copper, iron, steel, silver, platinum (weapons also bronze) | 1 — silver and platinum are softer than copper | 4 — familiar from Terraria | 2 | 4 (7) | 1 — silver and platinum stay stuck in tools for no reason; gold orphaned | 12 | Reject: contradicts the reason gold went |
| B | Science line: wood, stone, copper, bronze, iron, steel, cobalt steel, tungsten carbide — for tools *and* weapons (weapons stop at cobalt steel) | 5 | 4 — every name is real and most are known from games | 2 — nothing of the bugs | 5 (8) | 5 — freed for power, automation, jewelry, gilding | 21 | Keep as the spine |
| C | Metals to steel, then two bug-part tiers on top of the *pick* line (e.g. "zinc mandible", "sting alloy") | 2 — a bug pick harder than steel is not supported (≈ aluminium-hard) | 3 — players will ask why a jaw beats steel on rock | 5 | 5 (8) | 4 | 19 | Reject as the top of the pick line; keep the bug parts as a branch |
| D | Short ladder of about five, one per chapter: stone, copper/bronze, iron/steel, cobalt steel, tungsten carbide | 5 | 5 — few, very clear steps | 2 | 2 — cuts three rungs; D4 says tuning changes numbers, never deletes content | 5 | 19 | Reject for now; revisit only if the owner wants fewer, bigger steps |
| E | **Two tracks + a bug branch:** B's hard-metal line for gathering tools and weapons; a bug-part branch for cutting and piercing (mandible sickle and blade, sting spear, fang dagger) as sidegrades from the iron–steel stage; precious metals move to power, automation, jewelry, décor and gilding; the top tool wears a gold-coloured titanium-nitride finish | 5 | 4 | 4 — bug parts where biology backs them, plus real prospecting hooks | 5 (8) | 5 | **23** | **Pick** |
| F | Starbound-style ending in a choice: steel, then three parallel top materials (cobalt steel, tungsten carbide, bug composite) | 4 | 3 — a choice at the top needs explaining | 4 | 4 | 5 | 20 | Keep in mind for *weapons and armour* (each role has its own best set, 2026-08-06); gathering tools need one line for gating |

### 4.6 Recommendation: ladder E

**One hard-metal line, shared by tools and weapons (8 rungs):**

| Rung | Name | What it honestly is | Example of what it opens (shape only — zones decide) |
|---|---|---|---|
| 1 | Wood | a hardwood digging stick, mallet, hatchet | dirt, sand, clay, small trees |
| 2 | Stone | a flint or stone head | stone, coal, copper ore |
| 3 | Copper | arsenical copper, edge hammered hard (S24) | tin ore, harder stone |
| 4 | Bronze | copper + tin, harder than wrought iron (S24) — this also gives tools the bronze rung the weapons already have (§02's "one ladder" question) | iron ore |
| 5 | Iron | an iron head with a steel edge welded in (S28) — the milestone rung | silver ore |
| 6 | Steel | quenched carbon steel, the workhorse (S21) | cobalt ore, marked by pink "cobalt bloom", which real prospectors also read as a sign of silver (S29) |
| 7 | Cobalt steel | steel alloyed with cobalt and tungsten, sold today as "Cobalt Steel" (S21, S29) | tungsten ore, which glows sky-blue under a UV lamp and in real geology can point to gold (S29); gold |
| 8 | Tungsten carbide | carbide tips set in a steel head, with a gold-coloured titanium-nitride finish (S22, S27) — the golden-looking top tool, with no gold in it | the hardest deep rock: gem pockets and the richest platinum |

The ore order above follows real mineral associations where they exist (cobalt with silver, tungsten with gold), but
real geology does not rank ores by tool hardness — native gold and silver are soft. The gate is a game abstraction
("this vein sits in harder rock"), as in every game surveyed.

**One honest nuance about rung 7.** Real impact tools are deliberately tougher and softer than cutting tools: a
cobalt high-speed steel (63–70 HRC) is a drill-bit and cutter steel and would chip as a pick head. The real steel of
rock-breaking gear is **manganese (Hadfield) steel**, which hardens up to 3× under impact (S30) — and manganese is
one of the two metals bugs use to harden their stings (S14). Two honest options, the owner's taste: (a) keep one name,
"cobalt steel", for the whole rung (readable, and one ladder for tools and weapons as §02 asks); or (b) name the rung
by use — manganese steel for picks and shovels, cobalt steel for axes and blades — more authentic, one more thing to
explain.

- **Weapons** use rungs 2–7. Carbide is too brittle for blades (S22), so the top weapon metal is cobalt steel; the
  bug branch supplies the other top weapons.
- **Bug-part branch** (cutting and piercing only): mandible sickle, scythe blade and sword; sting spear; fang
  dagger. Sidegrades that appear around rungs 5–6 and need bred, *mature* bugs (the zinc-curing hook, §4.3). They
  are never pickaxes.
- **Silver, gold and platinum leave the tool and weapon ladders** and become the late-game money and technology
  metals (§4.2): silver for solar panels, contacts and mirrors; gold for connectors and gilding; platinum for
  catalysts, fuel cells and lab gear; all three for jewelry. Their ores stay in the world as deep rewards that the
  better picks open.
- **New ores this needs:** cobalt and tungsten (both need art and data). Diamond stays out of tools, per the owner.
- **Armour (for §08, the owner's call):** the science says gold, silver and platinum are poor protection too (soft
  and heavy); showpiece armour in history was usually gilded or etched *steel* (general knowledge, not fetched here),
  which matches the gilded-steel outfit already picked. Titanium — strong for its weight and rust-proof (S23) — is the
  credible light-armour metal. Whether the picked platinum outfit becomes a prestige outfit rather than a
  protection rung is a question for the owner, not something this research decides.

**Why E beats the others.** It is the only ladder that scores top marks on science *and* keeps eight rungs *and*
gives the precious metals a real job. Its names are real and mostly already familiar from other games (bronze,
iron, steel, cobalt, tungsten). It brings in the bugs exactly where biology supports them (sharp, light cutting
tools) instead of where it does not (a jaw that beats steel on rock).


## 5. Claims I am NOT sure about

Game numbers
1. **Terraria mining speeds** (S1) came from a summarised read of the wiki's pickaxe table; I cross-checked the
   mechanics page twice but not every item page. Tungsten 19 / Gold 17 / Platinum 15 look odd (slower than silver)
   and should be spot-checked. The conclusion (early picks are ~1.1× apart, 1.5× in total) does not depend on them:
   the hit counts, set by power thresholds, dominate.
2. **Effort = hits × ticks between hits** is a proxy for continuous mining; it ignores that the first hit lands at
   once and any targeting delay.
3. **Terraria axe tool speeds** were read only for copper, iron, silver, gold, platinum and the Molten Hamaxe.
4. **Stardew energy for a charged hoe or can** (I believe 2 × (charge level + 1), less skill) is not stated on the
   pages I read.
5. **Minecraft mining levels**: the summarised wiki tables gave contradictory values for gold (a cell read "32",
   clearly its durability) and for copper (0 vs 1). I relied on the Pickaxe page: gold is level 0, copper sits with
   stone at level 1. Copper's durability is 190 on one page and 191 on another.
6. **Core Keeper's formula**: the wiki says a wall takes no damage when mining damage ≤ its damage reduction; that
   each hit deals exactly *(mining damage − reduction)* is my inference, which the table in §3.3 assumes. The table
   uses each pickaxe's lowest roll and ignores skill and upgrades. A third-party guide (farminggames.help) gave
   different numbers and no octarine tier; I discarded it as unreliable.
7. **Necesse numbers change between versions** (the fossil pick was 195 in an older guide, 245 on the current wiki),
   and the older "tool tier" system (most picks tier 0; tungsten 2, glacial 3, fossil 5) may no longer exist.
8. **Valheim**: per-node HP and tool tier come from two deposit pages; the pickaxe skill also raises damage.

Material science
9. **HRC → HV conversions** (58 HRC ≈ 650 HV, 66 HRC ≈ 860 HV) are from standard conversion tables I know, not
   fetched.
10. **The Wikipedia hardness data page** carries a "needs more citations" banner, and its values are for pure,
    annealed metals; alloying and hammering change them a lot.
11. **Wrought iron 30–80 HV** (from the Bronze article) looks low next to figures I remember (~100 HB). The direction
    — good bronze is at least as hard as wrought iron — is well supported; the exact range is not.
12. **Steel's density (~7.8 g/cm³)** is inferred from "tungsten carbide … twice as dense as steel" (15.6 g/cm³).
13. **The medieval steel-edge-on-iron-axe practice** rests on one specialist web page (S28) and search summaries —
    widely repeated, but not from a scholarly source.
14. **Platinum–iridium over 500 HV** is Wikipedia's statement; I did not check its citation.
15. **Chromium–vanadium steel as the everyday wrench and socket steel** is common knowledge; the Wikipedia article
    I read gives only its composition, so the doc does not lean on it.
16. **Why the Bronze Age ended** is debated among historians; Wikipedia's tin-trade explanation is one view.
17. **"Showpiece armour was gilded or etched steel"** is general knowledge, not fetched.

Biology
18. **"Hardness does not grow with size"** is my reasoning from basic materials science (hardness is a property of
    the material, not of the object): a bigger mandible is stronger as a *structure* but not harder. The game's
    premise says the bugs were bred bigger, not re-engineered, so the same material is assumed.
19. **The "⅓ of 430 stainless steel" comparison** (S14) is against a fairly soft, annealed stainless; hardened tool
    steel is several times harder again, so the gap to tool steel is larger than "⅓" suggests. I did not verify the
    hardness of the 430 sample.
20. **The ~2/3 force reduction** is the authors' model-based hypothesis, and it compares metal-rich cuticle with
    *plain cuticle*, not with steel.
21. **Politi et al. 2012** (spider fang) was read through a press summary; the paper itself is paywalled.

Design
22. **The recommended shapes are computed, not played**: ×1.3 power, toughness 0.8, 8–10 hits on the frontier.
    Eight to ten hits on every new material for eight tiers may feel slow; tune in play.
23. **The ore-per-rung chain** in §4.6 is an example. Real geology does not rank ores by tool hardness.
24. **D1/D26 and precious metals**: the overview says electronics are "bought, never player-made"; D1 itself only says
    complex stations such as the electronics bench are bought. Whether silver, gold and platinum may be crafting
    inputs for player-made power parts is the owner's call.
25. **Starbound's gold-bar uses** (battery, cave detector, pixel compressor, sprinkler, décor) come from a summarised
    read of one wiki page; I did not check each recipe.

Process
26. The brief forbade sub-agents, so the thorough-research skill's independent cold-critic pass was **not** run. I
    did an adversarial self-review instead (it added the manganese-steel nuance, the co-op digging finding, the
    D12 farm-tool constraint and several hedges in the biology), but a fresh critic may still find gaps.
