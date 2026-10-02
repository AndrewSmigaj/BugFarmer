# Real dishes for the food list

Research for Bug Farmer (2026-10-01). The food list is being designed again from real dishes that people actually
cook, made from what players grow, fish and farm. This page collects real dishes in six groups, checks each against
the game's ingredients, and ends with a shortlist.

Rulings this research must respect (restated, with dates):

- Only bugs, fish and people survive: no mammals, birds, reptiles or amphibians, so no milk, butter, cheese, cream,
  bird eggs, mammal or bird meat, lard or gelatin from animals (D32, 2026-09-28). Fish gelatin is still possible,
  since fish survive.
- A bug is an insect or another arthropod: spiders, scorpions, centipedes, millipedes, pill bugs, crayfish and crabs.
  No worms, no leeches, and no snails (D64, 2026-09-28). So snail and earthworm dishes are out.
- No hunger. A meal heals over a while and gives one boost at a time; a new meal replaces the last. Food doesn't spoil
  (D50, D54, 2026-09-27).
- No magic; the world runs on 2126 science (D65, 2026-09-28).
- The game passes on a little real biology, but plays as a game; realism is never required (D66, 2026-09-28).
- Dead bugs are processed into materials at the Bug Extractor, which is also used in cooking (D18). Ants lay eggs as
  a mechanic and don't drop them (D18); the nursery stations hold eggs, larvae and pupae as collectable output
  (`docs/product/architecture/architecture_nursery_stations.md`).

How to read the tables:

- **Game ingredients?** "yes" means the dish can be made from the game's planned ingredients plus salt, water, honey
  and a cooking oil (sunflower oil is not in the game yet - see section 6). "needs X" names what is missing. Where a
  dish has an easy, still-real version without the missing thing, the column says so.
- **Everyday or novelty** (bug dishes only): whether people eat it as ordinary food where it comes from, or mostly as a
  dare or tourist snack. The game shouldn't present a novelty as a staple.
- Every fact comes from a source in the source table at the end. "Unverified" marks anything I could not confirm in a
  source I opened.

Method: one researcher, no sub-agents (as asked), writing each section to this file as it was finished. The web
search tool's budget for the session was already used up when this research began, so pages were found by name and
through Wikipedia's own search box instead. 235 Wikipedia articles (English, plus the Spanish article on escamoles)
were fetched as full plain text through Wikipedia's API and searched for the relevant passages, and 14 game-wiki pages
(Stardew Valley, Dinkum, Core Keeper, Valheim, Coral Island) were read through those wikis' own API. One page (the
Necesse wiki) was read through a summarising web fetch and is marked as less checked. Wikipedia is the main source;
where a claim needed a better source and none could be opened, the row says UNVERIFIED. Before finishing, the rows
were checked again against the saved page text, and the corrections are already in.

Status: COMPLETE (research, 2026-10-01). Research only - nothing here is decided; the recommendations are a menu for
the owner.

---

## 1. Real insect and other bug dishes

People eat more than 2,000 insect species, and about two billion people eat insects (sources 47, 34). Almost every bug
planned for the game has at least one real dish somewhere in the world. The exceptions are centipedes and millipedes
(no everyday dish found) and mantises (eaten, but no named dish found).

"Game ingredients?" assumes the bug itself is in the game. The things most often missing are onion, garlic, chili,
lime or lemon, rice and soy sauce - see section 6.

Numbers in the last column point to the source table at the end.

### 1a. Grasshoppers, locusts and crickets

| Dish | What it is | Where it's from | Key ingredients and method | Game ingredients? | Everyday or novelty | Source |
|---|---|---|---|---|---|---|
| Chapulines | Toasted grasshoppers, eaten as a snack, a topping, or a filling (for example in a tlayuda, a big toasted tortilla) | Oaxaca and around Mexico City | Grasshoppers toasted on a comal (a flat griddle), seasoned with garlic, lime juice, chilies and/or salt. They are gathered from corn and alfalfa fields; the young ones taste sweeter and cost more | Yes with salt. Garlic, lime and chili are not in the game | Everyday: an important protein in the Oaxaca countryside and a delicacy in Oaxaca city | 1, 2 |
| Inago no tsukudani | Rice grasshoppers simmered in soy sauce and sugar | Inland and mountain Japan (Nagano, Fukushima) | Kept a night without food, boiled, dried in a hot pan, fried crisp in oil, then cooked in soy sauce and sugar | Grasshoppers yes. Needs soy sauce; honey can stand in for sugar | Traditional; once an important food in hard times, now seen as a luxury | 15, 11 |
| Boiled and dried locusts | Locusts boiled, dried and eaten whole except head, wings and legs | Yemen, Arabia, Morocco; Yemenite Jewish cooking | Dropped into boiling salted water for a few minutes, then dried in a hot oven or in the sun | Yes (locusts, salt, water, oven) | A well-established food of Yemen's Jews (some called it a delicacy, others food of the poor); eaten in Saudi Arabia and Yemen today; allowed under both Jewish and Islamic food law | 28, 27 |
| Fried crickets (ching rit) | Deep-fried crickets sold at markets and as drinking snacks | Thailand, mostly the north and north-east | Crickets, oil, salt. Dry-roasting is also common | Yes, once there is a cooking oil (section 6) | Everyday. The UN's food agency (FAO) estimates about 20,000 cricket farms in 53 of Thailand's 76 provinces | 8, 18 |
| Fried grasshoppers and crickets (kripik, rempeyek) | Grasshoppers and crickets lightly battered and deep-fried into a crispy snack | Java and Kalimantan, Indonesia | Insects, a light batter, palm oil | Yes with flour and an oil | Everyday snack | 34 |
| Nsenene | A seasonal bush cricket (katydid) | Central and south-western Uganda; also eaten by the Haya of Tanzania | Swarm in the wet seasons, around May and November. How they are cooked is not in the sources I could open (often described as fried - UNVERIFIED) | Yes (a grasshopper-type bug) | A much-awaited seasonal delicacy | 49, 50 |

### 1b. Ants

| Dish | What it is | Where it's from | Key ingredients and method | Game ingredients? | Everyday or novelty | Source |
|---|---|---|---|---|---|---|
| Escamoles | Ant larvae and pupae, nicknamed "insect caviar" or "Mexican caviar" | Central Mexico (Mexico City area, Hidalgo, Puebla, Tlaxcala, Guanajuato); eaten since before the Spanish came | Dug in March-April from nests at the foot of agave plants, in prickly-pear patches or by pepper trees; washed in clean water. Fried with butter and epazote (a Mexican herb), or with egg, in sauces, in tortillas. Taste described as buttery and nutty | Ant brood yes. Butter and egg are out (fry in oil instead - plausible); epazote no | Everyday in season in old Mexico; today a costly delicacy, because the ants are fierce and breed only once a year | 3, 57 |
| Hormigas culonas | Roasted leafcutter ant queens | Santander, Colombia (San Gil, Barichara) | Only the queens, caught during about nine weeks of the rainy season; legs and wings pulled off, soaked in salty water, roasted in clay pans | Yes (ant queens, salt) | Seasonal regional delicacy, given as wedding gifts and exported | 4 |
| Chicatanas, and salsa de chicatanas | Flying leafcutter ants, eaten as a snack, in tacos or ground into a sauce | Central and southern Mexico (Oaxaca, Chiapas, Veracruz, Guerrero and others) | Toasted on a comal or fried, with salt, lemon and hot sauce. The Mixtec sauce adds chili, onion and garlic and is spread on tortillas | Ants and salt yes. The sauce needs chili, onion and garlic | Seasonal, at the start of the rainy season | 5 |
| Kaeng khai mot daeng (ant egg soup) | A soup of weaver-ant eggs and pupae, whose taste is described as creamy, sour and lemony | Laos and north-east Thailand; also Hainan, China | The eggs go in near the end. Recipes may use stock, lemongrass, fish sauce, chilies, tamarind, shallot and spring onion | Ant brood yes. The other flavourings are not in the game; fish sauce can be made from fish and salt (section 6) | Traditional food of country farmers, "an emblem of rural life"; less popular with young people | 7, 6, 8, 10 |
| Red ant egg salad (koi or tam khai mot daeng) | A salad of ant eggs; their sourness is used in place of lemon juice or vinegar | Laos and north-east and northern Thailand | Ant eggs with roasted vegetables, long pepper and two kinds of mint | Ant brood and mint yes | Traditional | 6, 8 |
| Honeypot ants | Ants whose swollen bodies are full of nectar, eaten for the sweetness | Central Australia (Aboriginal peoples) | Dug out of vertical tunnels up to two metres deep | Would need a honeypot-type ant | An occasional traditional food | 32 |

### 1c. Wasps and bees

| Dish | What it is | Where it's from | Key ingredients and method | Game ingredients? | Everyday or novelty | Source |
|---|---|---|---|---|---|---|
| Hachinoko and hebo-gohan | Wasp larvae and pupae; hebo-gohan is rice cooked with them | The Chubu region of Japan (Nagano, Gifu, Aichi) | Cooked, fried or pickled and seasoned with soy sauce and sugar. In Gifu the wasp (hebo) is eaten only in November; people move small colonies into hives near their houses and even shelter them through the winter | Wasp brood yes. Needs rice and soy sauce | A regional delicacy for autumn festivals; one festival weighs the nests in a contest | 11, 12 |
| Goheimochi with wasp-larva sauce | Grilled rice cakes on skewers, coated in a sweet sauce; one of the sauces is made with wasp larvae, another with honey | Nagano, Gifu and Aichi | Rice cake, sauce | Needs rice | Regional | 13 |
| Jibachi senbei | Rice crackers with dried wasps baked in | Japan | Rice cracker, dried wasps | Wasps yes; rice no. A wheat cracker would be plausible, not a known dish | Listed as one senbei variety; how common it is was not checked | 14 |
| Bee brood | Honeybee eggs, larvae and pupae; the pupae have the most protein | Harvested by beekeepers in many countries. In Banyuwangi (Java), botok tawon is comb with larvae, spiced, mixed with grated coconut and steamed in a banana leaf. Thai markets sell bee larvae | Brood comb, spices | Needs bee brood as an item (the hives exist); coconut and banana leaf are not in the game | Regional | 35, 34, 8 |

### 1d. Moth and butterfly caterpillars and pupae

| Dish | What it is | Where it's from | Key ingredients and method | Game ingredients? | Everyday or novelty | Source |
|---|---|---|---|---|---|---|
| Beondegi | Boiled or steamed silkworm pupae served in paper cups; also a soup (beondegi-tang) with soy sauce, chili, garlic and green onion | South Korea | Pupae and water | Yes (moth pupae) | Everyday street snack and pub food; sold canned in supermarkets | 16 |
| Silkworm pupae, Assam style | Pupae boiled when the silk is taken off, then eaten with salt or fried with chili or herbs | Assam, India | Pupae, salt, herbs | Yes (moth pupae, salt, herbs) | Everyday; a by-product of silk making | 17 |
| Mopane worms | Big caterpillars of an emperor moth | Southern Africa (Zimbabwe, Botswana, South Africa, Zambia) | Squeezed clean, boiled with plenty of salt, then dried in the sun or smoked. Eaten dry as a crunchy snack, or soaked and fried, or stewed with onion, tomatoes and spices and served with maize porridge (pap or sadza). Also sold canned in tomato or chili sauce | Caterpillars, salt, tomato and corn yes; onion no | Everyday seasonal food and a big rural trade | 29, 30 |
| Rot duan (bamboo worms) | Deep-fried caterpillars of a bamboo-boring moth | Northern Thailand, Laos, Myanmar, Yunnan | Fried, sometimes with herbs, spices or sauces; now farmed | Yes (caterpillars, oil, herbs) | Everyday snack, growing in popularity | 19 |
| Gusanos de maguey (maguey worms) | Caterpillars that live in agave plants | Central Mexico | Deep-fried or braised, seasoned with salt, lime and a spicy sauce, served in a tortilla | Caterpillars and corn tortillas yes; lime and chili no | A delicacy | 45 |
| Witchetty grubs | Big white wood-eating larvae of moths (and some beetles) | Australia (Aboriginal peoples) | Eaten raw or lightly cooked in hot ashes. Raw, they taste of almonds; cooked, the skin goes crisp | Yes (beetle grubs or caterpillars, a fire) | Traditional staple: "the most important insect food of the desert" | 31 |

### 1e. Beetle grubs

| Dish | What it is | Where it's from | Key ingredients and method | Game ingredients? | Everyday or novelty | Source |
|---|---|---|---|---|---|---|
| Sago grubs (ulat sagu, duong dua) | Palm weevil larvae | Papua, Kalimantan and the Moluccas (Indonesia); Vietnam | In Papua eaten roasted or raw. In Vietnam eaten alive dipped in fish sauce, or toasted, fried or steamed, with sticky rice and salad, or cooked in rice porridge | Beetle grubs yes; rice no | A delicacy | 33, 34 |
| Mealworms | Larvae of a darkling beetle | Street food in South-East Asia; approved as food in Switzerland (2017) and the EU (2021) | Baked or fried as a snack; ground into burgers, pasta and bars | Yes (darkling-type larvae) | Everyday in parts of South-East Asia. In Europe mostly snacks and protein bars | 46, 47 |

### 1f. Water bugs, cicadas and stink bugs

| Dish | What it is | Where it's from | Key ingredients and method | Game ingredients? | Everyday or novelty | Source |
|---|---|---|---|---|---|---|
| Nam phrik maeng da | A thick chili dip made with roasted, pounded giant water bug | Thailand | Chilies, shallots, lime juice and fish or shrimp paste pounded with the bug (garlic is left out). Similar dips are made with mole crickets, wasps, grasshoppers or bee larvae | Water bug yes; chili, shallot and lime no | Everyday condiment; the bug has a strong, penetrating smell | 20, 8, 21 |
| Alukap (Philippines) | Giant water bug sauteed in oil with garlic, onions and tomatoes, or roasted, with wings and legs removed | Ilocos and the Visayas, Philippines | Bug, oil, garlic, onion, tomato | Water bug and tomato yes; garlic and onion no | Traditional; eaten with rice or as a snack with drinks | 21 |
| Cicadas | Adult cicadas and, more often, the nymphs | Ancient Greece; parts of modern China; Malaysia, Myanmar, central Africa, Pakistan's Balochistan | The sources don't give a recipe | Cicadas yes | Everyday in some regions; a delicacy for the Onondaga people. A novelty for most Americans (the periodic 13- and 17-year cicadas) | 43 |
| Jumiles salsa | Stink bugs mashed in a stone mortar with tomatoes, chilies and onions, eaten with corn tortillas | Taxco, Guerrero, Mexico | Bugs, tomato, chili, onion | Stink bugs are not in the game; the same bug-salsa method would work with game bugs (plausible, not a known dish) | Festive: the season opens with a fiesta on 1 November | 44 |

### 1g. Spiders, scorpions, centipedes, millipedes and mantises

| Dish | What it is | Where it's from | Key ingredients and method | Game ingredients? | Everyday or novelty | Source |
|---|---|---|---|---|---|---|
| A-ping (fried tarantula) | Palm-sized tarantulas tossed in sugar, salt and seasoning, then fried in oil with garlic | Skuon, Cambodia ("Spiderville") | Tarantula, sugar, salt, garlic, oil | Tarantula, salt and honey yes; garlic no | Mostly a snack for tourists. May have started during the Khmer Rouge famine; popular only since about the 1990s | 22, 23, 56, 54 |
| Fried scorpions | Scorpions roasted, fried or grilled with the sting left on (cooking makes the venom harmless) | Traditional in Shandong, China; sometimes street food in Thailand; scorpion wine in Vietnam | Scorpions, oil | Yes (scorpions, oil) | Traditional in Shandong. In tourist markets it is a dare: Beijing's Donghuamen night market sold fried scorpions, centipedes, crickets and silkworms until it closed in 2016. Durango, Mexico, sells scorpions in tacos, on skewers, as lollipops or drowned in mezcal | 24, 26, 25, 55 |
| Centipedes | Deep-fried at Beijing's Donghuamen night market | Beijing (closed 2016) | - | Centipedes yes | Novelty only; no everyday centipede dish found | 25 |
| Millipedes | No food use found; most millipedes defend themselves with chemicals released from pores along the body | - | - | - | Not food | 52 |
| Mantises | Listed among insects eaten in Thailand, but no named dish found | Thailand | - | - | No known dish | 53 |

### 1h. Crayfish and crabs

| Dish | What it is | Where it's from | Key ingredients and method | Game ingredients? | Everyday or novelty | Source |
|---|---|---|---|---|---|---|
| Crawfish boil | Crawfish boiled in a big pot with seasoning and vegetables, tipped onto a paper-covered table and eaten by hand | Louisiana (Cajun and Creole), in spring | Crawfish, corn on the cob, new potatoes, onions, whole garlic; cayenne, salt, lemons, bay leaf | Crayfish, corn and salt yes; potatoes, onions, garlic, lemons and cayenne no | Everyday and festive; cheap in season; held by churches and clubs as fundraisers | 36, 37 |
| Kraftskiva (crayfish party) | Crayfish boiled in salt water with lots of dill, left in the brine overnight and eaten cold | Sweden, Finland, Norway; every August | Crayfish, salt, sugar, ale, dill | Crayfish and salt yes; honey could stand in for sugar; dill no | Everyday festive tradition | 38, 39 |
| Russian boiled crayfish | Crayfish boiled live in salted water with carrots, onion, dill, parsley, bay leaf and peppercorns; eaten with beer | Russia, Ukraine | As listed | Crayfish, salt and carrots yes; the rest no | Traditional seasonal snack | 39 |
| Ma la xiao long xia (spicy crayfish) | Crayfish in a hot, spicy soup with cucumber and Sichuan pepper; also stir-fried with garlic, or simply steamed whole | China, now the world's largest grower and eater of crayfish | As listed | Steamed whole: yes. The spicy version needs chili, Sichuan pepper and cucumber | Everyday | 39 |
| Acocil (Mexican crayfish) | An important Aztec food; today boiled, or in soups and tacos | Central and southern Mexico | Crayfish, tortillas | Yes (crayfish, corn tortillas) | Everyday regional | 39 |
| Crawfish etouffee | Crawfish "smothered" in a thick sauce built on a roux (flour cooked in fat), served over rice | Louisiana | Crawfish, roux, the "trinity" of bell pepper, onion and celery, rice | Crayfish, flour and oil yes; rice, pepper, onion and celery no | Everyday | 40, 41, 37 |
| Chinese mitten crab (hairy crab) | A freshwater crab, an autumn delicacy prized for the female's roe | Shanghai and eastern China | Usually steamed with ginger and dipped in rice vinegar, sugar and ginger | Steaming: yes for the game's cave crabs; the dip needs vinegar (section 6); ginger no | Seasonal delicacy | 42, 184 |

### 1i. Flies

| Dish | What it is | Where it's from | Key ingredients and method | Game ingredients? | Everyday or novelty | Source |
|---|---|---|---|---|---|---|
| Kunga cake | A cake of densely pressed flies | East Africa | One line in the source; details not checked | Adult flies (not larvae) | Regional | 34 |
| Black soldier fly larvae | Bred at factory scale as feed for chickens, fish and pets; records of people eating them are hard to find | Worldwide | - | Fly larvae fit best as animal or bug feed, not people food | Feed, not food | 51 |

### What section 1 means for the game

- **Ant brood, wasp brood, moth pupae, caterpillars, grasshoppers, locusts, crickets, beetle grubs, the water bug,
  scorpions and crayfish all have everyday real dishes.** The simplest real methods use only salt, water, oil and a
  fire: toast on a griddle (chapulines), boil in salt water and dry (locusts, mopane worms), deep-fry (crickets, bamboo
  worms, scorpions), roast in hot ashes (witchetty grubs), boil (crayfish).
- **Tarantulas, centipedes and Beijing-style scorpion skewers are tourist dares in real life.** If the game has them,
  they shouldn't be presented as ordinary staples. Millipedes and mantises have no dish.
- **Real people farm these bugs for food the way the game imagines:** Thai cricket farms, weaver-ant nests kept on
  trees and fed sugar water, Japanese wasp colonies moved next to houses and sheltered over winter, farmed bamboo
  worms (sources 8, 6, 12, 19). This fits the game's idea of bugs raised like livestock.
- **Many bug dishes are eaten with corn** - tortillas in Mexico, maize porridge with mopane worms in southern Africa -
  so corn is the natural partner crop for bug protein in the game.
- **Weaver ants have long guarded citrus orchards:** farmers in China and South-East Asia have used them against pests
  since at least the year 400 (source 9). A real link the game could use between ants and its orange trees.

---

## 2. Real dishes from the game's crops, fruit, herbs and mushrooms

All of these are made without dairy, bird eggs or mammal meat - either as they really are, or (where marked
"plausible") with only the forbidden part left out. "Oil" means a pressed cooking oil, which the game doesn't have yet
(section 6); "lime" means the alkali used for corn (section 6), not the fruit.

### 2a. Corn

| Dish | What it is | Where it's from | Key ingredients | Game ingredients? | Source |
|---|---|---|---|---|---|
| Corn tortillas | Thin flatbreads cooked on a hot griddle (comal) | Mexico and Central America | Corn soaked and cooked in an alkali (lime or wood-ash lye), ground with salt and water. Plain cornmeal can't make a dough - the alkali step is what makes it hold together | Corn, salt, water yes; needs lime or wood ash (section 6) | 96, 95, 97 |
| Arepa | A thick flatbread of ground corn dough, often split and filled | Colombia, Venezuela | Ground corn (not alkali-treated), water, salt | Yes | 98, 96 |
| Johnnycake (hoecake, journey cake) | Unleavened cornbread baked on a board leaned before an open fire, or fried on a griddle; often eaten with honey | North America (Native origin), the Caribbean | Cornmeal, salt, water | Yes | 99 |
| Corn pone | A thick cornmeal dough, usually without egg or milk, cooked in an iron pan over a fire in fat or oil | Southern United States | Cornmeal, water, oil | Yes | 100 |
| Cornbread with sunflower seeds, apples or berries | Cherokee and Seneca cooks enrich the basic cornbread batter with sunflower seeds, apples or berries (or chestnuts). The earliest colonial cornbread was just cornmeal and water baked over a fire | Native North America | Cornmeal, water, sunflower seeds, apples or berries | Yes with a plain cornmeal-and-water batter (the source doesn't list the Cherokee batter) - every part is a game crop | 100 |
| Polenta / mamaliga | Cornmeal boiled into a porridge; it can be cooled, cut, then baked, fried or grilled | Northern Italy; Romania, Moldova and neighbours | Cornmeal, water, salt | Yes | 101, 102 |
| Ugali (sadza, nshima, pap) | Maize meal cooked in boiling water to a stiff dough, eaten by hand with a stew ("relish") of vegetables, fish or insects | Much of Africa; on UNESCO's cultural heritage list | Maize meal, water | Yes; the natural partner for a mopane-worm or fish stew | 103, 30, 29 |
| Grits / hominy | Porridge of coarsely ground corn or alkali-treated corn (hominy), cooked in salted water | United States (Native origin) | Corn, water, salt (lime or lye for hominy) | Yes; hominy needs lime or wood ash | 104, 105, 95 |
| Corn on the cob | Sweet corn picked young and steamed, boiled or grilled; it loses a quarter of its sweetness within a day of picking | Worldwide | Corn, salt (usually butter too) | Yes, without the butter | 106 |
| Popcorn | Kernels of a special popping corn that burst when heated | The Americas; one of the oldest snacks | Popping corn, salt or a sweetener | Needs a popping-corn variety; honey or salt yes | 107 |
| Pinole | Roasted ground corn, used for drinks and baking | Mexico, Central America; Nicaragua's national drink | Corn | Yes | 108 |
| Atole | A hot, thick drink of corn dough and water, sweetened and spiced; served with tamales | Mexico, Central America | Masa (alkali-treated corn dough), water, sweetener | Corn and honey yes; needs lime | 109 |
| Tamales | Corn dough with any filling, steamed in a corn husk | Mexico, Central America | Masa, filling, husk | Corn yes (husks come with the corn); needs lime; a bug or vegetable filling would be plausible | 110 |
| Pozole | A stew of hominy, usually with chicken or pork, topped with cabbage, chili and onion | Mexico | Hominy, meat, cabbage | Meat is out; a bug-meat pozole is plausible, not a known dish | 111 |

**Cornbread without eggs or milk is real:** johnnycake and corn pone are made without them, and the earliest colonial
cornbread was cornmeal and water; eggs, milk and baking powder were added later (the source dates them to the 18th and
19th centuries) (source 100).

### 2b. Wheat breads

| Dish | What it is | Where it's from | Key ingredients | Game ingredients? | Source |
|---|---|---|---|---|---|
| Sourdough bread | Bread raised by a starter: flour and water left somewhere warm for a week or two until wild yeasts take hold, then "fed" with more flour and water. Gold prospectors carried starter in a pouch | One of the oldest ways to raise bread (a loaf from 3700 BC survives); famous in San Francisco and the Klondike | Flour, water, salt, starter | Yes | 114 |
| Damper | A plain bread baked in the coals of a campfire | Australian settlers | Flour, salt, water (butter if there was any) | Yes - a campfire bread | 116 |
| Chapati | Flatbread cooked on an iron griddle and puffed over direct heat | South Asia, East Africa | Whole-wheat flour, water | Yes | 115 |
| Matzah | Unleavened flatbread, soft or crisp | Jewish (Passover) | Flour, water | Yes | 118 |
| Hardtack | A dense, dry cracker that keeps a long time if kept dry; a standard ship's and army ration from the 1600s to the early 1900s | Europe and America | Flour, water, a little salt | Yes - a travel food | 117 |
| Pain d'epices | Honey spice bread; in 1694 the French Academy defined it as rye flour, honey and spices | France | Rye flour, honey, spices | Honey yes; wheat instead of rye is plausible; the spices (e.g. anise, cinnamon) are not in the game | 119 |
| Lebkuchen | Honey-sweetened German Christmas cakes, similar to gingerbread (German gingerbread recipes often use potash to raise the dough) | Germany | Flour, honey, spices | Flour and honey yes; potash can come from wood ash (section 6); spices no | 120, 196 |
| Pa amb tomaquet | Bread rubbed with ripe tomato, then oil and salt | Catalonia | Bread, tomato, olive oil, salt | Yes, with sunflower oil for olive (plausible) | 121 |
| Bruschetta | Grilled bread with garlic, oil and salt, often topped with tomato | Italy | Bread, garlic, oil, salt, tomato | Needs garlic | 122 |
| Manakish with za'atar | Dough topped with za'atar (wild thyme-like herbs, sesame, sumac, salt) and oil | The Levant | Dough, za'atar, oil | Bread, thyme, oil yes; sesame and sumac no. A thyme-and-salt flatbread is plausible | 123, 124 |

### 2c. Vegetables, soups and ferments

| Dish | What it is | Where it's from | Key ingredients | Game ingredients? | Source |
|---|---|---|---|---|---|
| Sauerkraut | Finely shredded cabbage layered with salt and left to ferment; keeps for several months somewhere cool, with no refrigeration needed. Eastern European versions add shredded carrot, caraway or whole apples | Germany, Central and Eastern Europe; Roman writers describe salted cabbage | Cabbage, salt (carrot, apple) | Yes - all game ingredients | 125, 187 |
| Shchi | Russian cabbage soup, eaten with rye bread. The old recipe was cabbage, meat, mushrooms, flour and an onion-and-garlic seasoning; in fasting times fish replaced the meat; carrots were added later; "sour shchi" uses sauerkraut | Russia | Cabbage, mushrooms, flour, carrots, fish or meat | Cabbage, mushroom, flour, carrot, fish yes; onion and garlic no | 126 |
| Red cabbage with apples or vinegar | Red cabbage turns blue when cooked unless vinegar or a sour fruit goes in the pot | Germany and much of Europe | Red cabbage, vinegar or sour apples | Yes if cabbage can be red; vinegar is a new staple | 127 |
| Pumpkin soup | A thick soup of pureed pumpkin with broth. In Styria (Austria) a few drops of pumpkin seed oil go on top | Europe, North America, Asia, Australia | Pumpkin, broth (pumpkin seed oil) | Yes (a vegetable or fish broth) | 128, 129 |
| Tzimmes | Carrots and prunes stewed slowly with honey; eaten at the Jewish New Year, when sweet, honeyed dishes are the custom | Ashkenazi Jewish | Carrots, prunes, honey | Yes - carrot, dried plums, honey | 135 |
| Pickled eggplants of Almagro | Eggplants pickled with fennel stems | Almagro, Spain | Eggplant, fennel stems, a pickling liquid | Yes with vinegar or brine | 134, 187 |
| Eggplant escabeche | Eggplant marinated in a vinegar sauce (often fried first) | Argentina | Eggplant, oil, vinegar | Yes with oil and vinegar | 70 |
| Imam bayildi | Whole eggplant stuffed with onion, garlic and tomato, simmered in olive oil | Ottoman Turkey and its old lands | Eggplant, onion, garlic, tomato, oil | Eggplant, tomato, oil yes; onion and garlic no | 131 |
| Ratatouille | A stew of summer vegetables cooked in olive oil | Provence, France | Tomato, onion, garlic, courgette, eggplant, bell pepper, herbs (thyme, fennel) | Eggplant, tomato, thyme, fennel yes; onion, garlic, courgette, pepper no | 130 |
| Baba ghanoush | Fire-roasted eggplant mashed with oil, lemon and tahini (sesame paste) | The Levant | As listed | Eggplant and oil yes; lemon and tahini no | 132 |
| Caponata | Fried eggplant in a sweet-and-sour tomato sauce with celery, olives and capers | Sicily | As listed | Eggplant and tomato yes; celery, olives, capers no | 133 |
| Succotash | Sweet corn cooked with lima or other shell beans | North America (Narragansett name) | Corn, beans | Needs beans | 136 |
| Kimchi | Salted fermented cabbage with chili powder, garlic, ginger and salted seafood | Korea | As listed | Cabbage and salt yes; chili, garlic, ginger no. Sauerkraut is the game-ready cabbage ferment | 138 |
| Tabbouleh | Salad of parsley, cracked wheat (bulgur), tomato, mint and onion with oil and lemon | The Levant | As listed | Wheat, tomato, mint, oil yes; parsley, onion, lemon no | 139 |

The **Three Sisters** - corn, beans and squash grown together, with sunflowers as a "fourth sister" - were the core
crops of many Native peoples of North and Central America (source 137). Bug Farmer already grows corn, pumpkin and
sunflowers; beans would complete the set and unlock succotash.

### 2d. Mushrooms

| Dish | What it is | Where it's from | Key ingredients | Game ingredients? | Source |
|---|---|---|---|---|---|
| Sauteed chanterelles | Chanterelles fried in fat - their flavour dissolves in fat - or added to soups | Europe, North America | Chanterelles, oil | Yes | 140 |
| Dried chanterelle seasoning | Dried chanterelles crushed into a powder to season soups and sauces | Europe | Chanterelles | Yes | 140 |
| Marinated mushrooms | Wild or farmed mushrooms preserved in vinegar | Poland and elsewhere | Mushrooms, vinegar | Yes with vinegar | 143 |
| Mushroom shchi | See shchi above: mushrooms were part of the old recipe | Russia | Cabbage, mushrooms | Yes | 126 |
| Puffballs | Edible only while young and white inside; inedible once mature, and young deadly Amanitas look similar | Worldwide | - | Yes as a forage item; how they are cooked isn't in the source | 141 |
| Brown mushrooms (cremini, button) | One of the most widely eaten mushrooms; grows in rich soil and compost and is farmed in more than 70 countries | Worldwide | - | Yes; a real link to the game's compost bins | 142 |

### 2e. Fruit

| Dish | What it is | Where it's from | Key ingredients | Game ingredients? | Source |
|---|---|---|---|---|---|
| Apple butter | Apples cooked long and slowly with juice or water until their sugar caramelises into a dark spread; no dairy, and no added sugar needed | Belgian and Dutch Limburg and the Rhineland (medieval monasteries); colonial America, where families took turns stirring big copper kettles | Apples, water | Yes | 144 |
| Powidl (plum butter) | Plums cooked for hours into a thick spread with no added sweetener or setting agent; made in late autumn as a shared village job; used as a sweetener before sugar was cheap | Austria, Czechia, Poland | Late plums | Yes | 145 |
| Apple sauce | A puree of apples, sweetened or not | North America, Europe | Apples | Yes | 146 |
| Baked apples | Cored apples filled and baked until soft; honey is one of the usual sweeteners; baked in an oven or on top of a wood stove | Europe; German Christmas | Apples, honey (butter, spices, wine) | Yes, with honey | 147 |
| Fruit cooked with honey ("confit") | Fruit cooked with honey or sugar until it sets like jam | France and elsewhere | Fruit, honey | Yes. Apples, plums and oranges set well because they are rich in pectin; cherries and soft fruit such as strawberries are low in it, so cooks add a high-pectin fruit such as orange | 148, 149 |
| Orange marmalade | A sweet spread of oranges; one of the earliest English recipes ("Marmelet of Oranges") dates from 1677 | Britain (first made from quince in Portugal) | Oranges, sugar | Oranges yes; honey for sugar is plausible, not the classic recipe | 150 |
| Prunes and dried fruit | Fruit dried in the sun; prunes are dried plums of suitable varieties | Since about 4000 BC in Mesopotamia | Fruit | Yes (apples, plums, cherries, berries) | 151, 152 |
| Kompot | Fruit boiled in plenty of water and sweetened with honey or sugar, drunk hot or cold; a way to keep fruit for winter | Central and Eastern Europe, the Caucasus | Apples, plums, cherries, berries, honey | Yes | 153 |
| Kissel | Berry juice thickened to a jelly with potato or corn starch; old Polish and French versions were set with fish gelatin | Russia, Poland, Eastern Europe | Berries, starch | Berries yes; needs corn starch (section 6) or fish gelatin | 154 |
| Prickly pear jam (konfyt) | Southern African jam, made from fruits including prickly pears | South Africa | Fruit, sugar | Prickly pear yes; honey for sugar is plausible | 148 |
| Nopales | Prickly-pear pads, eaten as a vegetable; the fruit is eaten raw or cooked | Mexico | Pads, fruit | Only if the game's prickly pear yields pads | 156, 157 |
| Pastila | Apple or berry paste baked dry in a Russian oven for hours; the cheapest kind used honey instead of sugar | Russia | Apples or berries, honey, egg whites | Needs egg whites, so it is out as it stands; plain dried apple paste would be plausible | 158 |

**Honey instead of sugar is real and traditional.** Before sugar was cheap, honey and fruit butters such as powidl were
the sweeteners of Central Europe (source 145); fruit cooked with honey until it sets is a confit (148); the cheapest
Russian pastila used honey (158); kompot is sweetened with honey or sugar (153). Honey-glazed carrots as such were not
looked up; tzimmes is the real carrot-and-honey dish found.

### 2f. Seeds

| Dish | What it is | Where it's from | Key ingredients | Game ingredients? | Source |
|---|---|---|---|---|---|
| Roasted pumpkin seeds (pepitas) | Seeds roasted and salted as a snack; also ground into sauces (pipian) | Mexico; Greece ("pastime") | Pumpkin seeds, salt | Yes | 159 |
| Roasted sunflower seeds | Dried, roasted, salted seeds eaten as a snack | Worldwide; Russia and Ukraine grow half the world's crop | Sunflower seeds, salt | Yes | 160 |
| Sunflower halva | A dense sweet of roasted, ground sunflower seeds | Former Soviet Union, Bulgaria, Romania | Sunflower seeds, sugar or honey | Yes, with honey | 162 |
| Poppy seed and honey bars | Boiled poppy seeds mixed with honey and set into bars | The Balkans, Greece, the old Austro-Hungarian lands | Poppy seeds, honey | Yes | 163 |

### 2g. Teas and other drinks

| Dish | What it is | Where it's from | Key ingredients | Game ingredients? | Source |
|---|---|---|---|---|---|
| Herbal teas: chamomile, fennel, lavender, mint | Infusions of herbs in hot water (strictly "tisanes", since they contain no tea leaf) | Worldwide | Dried flowers or leaves, hot water | Yes | 165, 164, 134, 166 |
| Dandelion coffee | Roasted dandelion root brewed as a coffee substitute | Widely made | Dandelion root | Yes | 167, 168 |
| Dandelion greens | The leaves eaten in salads | Worldwide | Dandelion leaves | Yes | 168 |
| Mead | Honey and water fermented; with fruit it is a melomel, with spices a metheglin. Possibly the oldest alcoholic drink | Europe, Africa, Asia | Honey, water (fruit) | Yes (the keg) | 170 |
| Cider | Fermented apple juice | Britain and Ireland (the most per person), North America and elsewhere | Apples | Yes (a press and the keg) | 171 |
| Kvass | A sweet-sour, barely alcoholic drink of rye bread soaked in hot water and fermented | Russia, Ukraine, Poland, the Baltic | Rye bread, water, yeast, a sweetener | Wheat bread instead of rye is plausible | 172 |
| Dandelion wine | Wine made from dandelion petals, sugar and an acid such as lemon juice | Homemade in many countries | Petals, sugar, acid | Dandelion yes; honey for sugar and orange for lemon are plausible | 169 |
| Colonche | A sweet, fizzy red drink of prickly-pear juice, boiled two to three hours and left to ferment a few days | Northern-central Mexico | Prickly pear fruit | Yes (the keg) | 155 |
| Gruit ale | Beer flavoured with a herb mix instead of hops, before hops took over; today's gruit mixes often include yarrow | Netherlands, Belgium, north-west Germany (from the 10th century) | Malted grain, herbs | Needs malt (section 6); yarrow yes | 173 |
| Switchel ("haymaker's punch") | Water with vinegar, sweetened with molasses or honey and often flavoured with ginger | United States (for example Vermont) | Water, vinegar, honey | Yes once vinegar exists; ginger no | 174 |
| Oxymel | Honey mixed with vinegar, an old medicine and drink | Ancient Greece onward | Honey, vinegar | Yes once vinegar exists | 175, 185 |
| Shrub (drinking vinegar) | A sweet fruit-and-vinegar syrup mixed with water | Colonial America, England | Fruit, vinegar, honey or sugar | Yes once vinegar exists | 176 |
| Tejuino, pozol, chicha | Fermented corn drinks: tejuino (corn dough, lightly fermented, served with lime and salt), pozol (fermented corn dough drink), chicha de jora (Andean corn beer) | Mexico; southern Mexico; the Andes | Corn | Corn yes (tejuino and pozol use alkali-treated dough) | 112, 183, 113 |

Herbs in the game that turned out to be **medicine more than food:** yarrow (a wound herb since antiquity; no food
use in the source, apart from flavouring gruit ales) and aloe (its gel goes on the skin; the latex is toxic when
swallowed in quantity) (sources 181, 180, 173). Both fit potions and salves better than meals. Red clover flowers
and leaves are edible as a garnish (source 179); sage goes with pumpkin and with fish (source 177); thyme dries well and keeps its flavour (source 178).

What section 2 means for the game:

- **A real grown-food menu needs only a few staples the game hasn't got yet:** a cooking oil, vinegar, an alkali for
  corn (lime or wood ash), a bread starter, and for a few dishes corn starch. All of them can be made from things the
  game already has (section 6). Sugar isn't needed: honey stands in for it, and apple butter and powidl need no
  sweetener at all.
- **The best "everything is already in the game" dishes:** corn breads (johnnycake, corn pone, the Cherokee-style
  cornbread with sunflower seeds and berries), polenta, ugali, sourdough, damper, sauerkraut, tzimmes, apple butter,
  powidl, baked apples with honey, kompot, roasted seeds, sunflower halva, herbal teas, dandelion coffee, mead and
  cider.
- **Onion and garlic are the biggest gap.** They appear in almost every savoury dish across sections 1-3; adding them
  as crops would open dozens of real recipes (section 6).

---

## 3. Real freshwater fish dishes

The game's fish so far are perch and carp, with trout, catfish, pike and eel as likely additions. All six are real
food fish with real dishes. The simplest real methods again need only salt, fire, oil, flour or cornmeal.

| Dish | What it is | Where it's from | Key ingredients and method | Game ingredients? | Source |
|---|---|---|---|---|---|
| Salt-grilled fish on a skewer (ayu shioyaki) | A small whole fish bent into a "swimming" curve, skewered and grilled with salt over charcoal | Japan (ayu, a river fish) | Fish, salt, a skewer, a fire | Yes - a campfire dish for any small fish | 66 |
| Shore lunch | Cooking the catch on the shore where it was caught | Northern US and Canada | Whatever was caught, cooked outdoors | Yes - the idea behind a campfire fish meal | 64 |
| Fried or grilled perch | Perch has firm, white, flaky, well-flavoured flesh and is widely eaten in Europe, fried or grilled | Europe (Russia and Finland catch the most) | Perch, oil or a fire, salt | Yes | 76 |
| Fish with fennel or sage | Many fish dishes use fresh or dried fennel leaves; in Italy sage is a favourite with fish. No single named freshwater dish was found | Mediterranean Europe | Fish, fennel or sage | Yes | 134, 177 |
| Masgouf | Seasoned, grilled carp | Iraq, where it is often called the national dish | Carp, seasoning, fire. (The source gives no more detail.) | Yes (carp, salt, fire) | 58 |
| Fried carp for Christmas Eve | Carp breaded and fried, with a soup made from the head | Czechia, Slovakia, Poland, eastern Croatia, Austria, parts of Germany | Breading usually means egg and breadcrumbs; a flour or cornmeal coating avoids the egg (plausible). The Czech meal adds potato salad | Carp, flour or cornmeal, oil yes; egg and potato no | 61, 62 |
| Halaszle (Hungarian fisherman's soup) | A hot, red paprika soup of carp or mixed river fish (carp, catfish, perch, pike), cooked in a kettle over an open fire on the river bank and eaten with bread | Hungary and the Danube region; Christmas Eve | Onion fried in oil, paprika, water, then the fish; broth from heads and bones with onion, peppers and tomato | Fish, tomato, oil and bread yes; paprika, peppers and onion no | 59, 62 |
| Ukha | A clear soup of freshwater fish (bream, catfish, pike, ruffe; perch adds flavour) - some cooks say it can't be made well from sea fish | Russia, especially the Don region | Fish broth with root vegetables, leek, potato, bay leaf, dill, parsley, pepper and fennel seed. Fishermen add a dash of vodka, or dip a smouldering stick from the fire into the pot | Fish and fennel yes; carrot as the root vegetable (plausible); leek, potato, bay and dill no | 60 |
| Southern fish fry | Catfish or bream coated in cornmeal and deep-fried, served with hushpuppies (fried corn dumplings) and coleslaw | Southern United States, as an outdoor family or church gathering | Cornmeal and seasoning; the coating often uses milk or buttermilk too | Catfish, cornmeal, oil and cabbage yes; the milk is not needed for a plain cornmeal coating (plausible) | 63 |
| Friday fish fry | Battered or breaded fried fish - in Wisconsin often perch, walleye or bluegill in beer batter | Midwest and north-east United States, especially during Lent | Fish, beer batter, oil | Perch, flour and oil yes; the beer would come from the keg if beer is brewed | 63 |
| Fish tacos (tacos de pescado) | Fried or grilled fish on a corn or flour tortilla with cabbage, pico de gallo (fresh tomato salsa) and a creamy sauce | Baja California, Mexico | Fish, tortilla, cabbage, tomato; the sauce is sour cream or mayonnaise | Fish, corn tortilla, cabbage and tomato yes; the sauce has dairy or egg, so leave it out or use another sauce | 65 |
| Kabayaki | Eel split, boned, skewered and grilled with a sweet soy glaze, often served on rice. Catfish and loach are cooked the same way | Japan; eaten on a midsummer day "to gain stamina" | Eel, soy sauce glaze, grill | Eel yes; needs soy sauce and rice. A honey-and-salt glaze would be plausible, not the real dish | 67 |
| Jellied eels | Chopped eel boiled in water and vinegar with spices and left to cool; the eel's own collagen sets the stock to a jelly. Eaten cold with chili or malt vinegar | London's East End, since the 1700s | Eel, vinegar, water, nutmeg, lemon juice | Eel and vinegar yes; nutmeg and lemon no. A real fish jelly that mostly sets by itself (some cooks add gelatin) | 68 |
| Smoked fish | Fish salted, then smoked cold (not cooked) or hot (cooked). Fish salted and cold-smoked for two weeks or more could be stored a year or more | Worldwide; traditional smokehouses stood beside fishermen's cottages | Fish, salt, a smoker | Yes, but needs a smoker (a new station, or the campfire) | 69 |
| Vobla (dried roach) | Small fish soaked in brine for some days, then air-dried; eaten as a snack, often with beer | Russia and the Caspian region | Fish, salt, air | Yes | 71 |
| Escabeche | Fish fried, then marinated in a vinegar sauce with paprika, citrus and spices. Argentina makes it with eggplant | Spain, Portugal, Latin America, the Philippines | Fish or eggplant, oil, vinegar, citrus | Fish, eggplant, oil and orange yes; vinegar is a new staple (section 6); paprika no | 70 |
| Fish pilaki | Fish cooked in a sauce of onion, garlic, carrot, potato, tomato and oil, served cold | Turkey | As listed | Fish, carrot, tomato and oil yes; onion, garlic and potato no | 78 |
| Cured fish (gravlax) | Raw salmon cured with salt, sugar and dill, sliced thin | Nordic countries | Fish, salt, sugar, dill | Real gravlax is salmon. Trout cured the same way is plausible (trout flesh is close to salmon); honey for sugar; dill no | 74, 75 |
| Prahok (fermented fish paste) | Fish salted, sun-dried, pounded and left in jars about a month; the liquid that rises is skimmed off as fish sauce | Cambodia ("No prahok, no salt") | Freshwater fish, salt, sun | Yes - and it makes fish sauce as a by-product (section 6) | 72 |
| Pla ra (fermented fish) | Fish fermented with salt and rice bran or roasted rice for six months or more | Thailand, Laos | Fish, salt, rice bran | Needs rice; prahok is the version the game can make | 73 |

What section 3 means for the game:

- **Perch, carp, catfish, pike and eel are everyday food fish** (sources 76, 61, 80, 77, 81). Pike is famously bony
  but has a long history in European cooking; carp is a Christmas fish across Central Europe.
- **The early fish dishes need nothing but a fire and salt** (salt-grilled skewers, a shore lunch, masgouf). The middle
  tier adds flour or cornmeal and oil (fried carp, a southern fish fry). Soups and stews come with the wood stove
  (halaszle, ukha, pilaki). The keg and a smoker add the preserved fish: smoked, dried, cured and fermented.
- **Eel has a real "stamina" link** (Japan's midsummer eel day), which fits a bigger-stamina boost.
- **Fish make the game's missing seasonings:** fish and salt give fish paste and fish sauce, the savoury seasoning of
  South-East Asian cooking - and an answer to the missing soy sauce (section 6).

---

## 4. Combined dishes: bugs (and fish) with crops

Real dishes first, then plausible ones. "Plausible" means built from a real technique with game ingredients, but not a
dish anyone is known to make - it should be named plainly (for example "cricket flatbread"), not given a made-up
traditional name.

### 4a. Real combined dishes

| Dish | What it is | Where it's from | Key ingredients | Game ingredients? | Source |
|---|---|---|---|---|---|
| Chapulines in a tlayuda | Toasted grasshoppers as the filling of a big toasted tortilla | Oaxaca, Mexico | Grasshoppers, corn tortilla | Yes once corn tortillas exist (needs lime) | 1, 96 |
| Chicatana tacos and salsa de chicatanas | Fried flying ants in tacos; a sauce of toasted ants with chili, onion and garlic spread on tortillas | Central and southern Mexico | Ants, tortillas (chili, onion, garlic for the sauce) | Tacos yes; the sauce needs chili, onion, garlic | 5 |
| Escamoles in tortillas or gorditas | Fried ant brood folded into tortillas or thick corn cakes | Central Mexico | Ant brood, corn dough | Yes (fry in oil instead of butter - plausible) | 57 |
| Maguey-worm tacos | Fried or braised caterpillars in a tortilla with salt, lime and hot sauce | Central Mexico | Caterpillars, tortilla | Yes, without the lime and chili | 45 |
| Acocil (crayfish) tacos | Boiled crayfish in tacos or soups | Central and southern Mexico | Crayfish, tortillas | Yes | 39 |
| Mopane worms with tomato and maize porridge | Dried caterpillars soaked, then stewed with onion, tomatoes and spices, served with pap or sadza | Southern Africa | Caterpillars, tomato, maize meal (onion) | Yes except the onion | 29, 103 |
| Porridge with an insect "relish" | Ubwali (millet porridge) eaten with one stew at a time - of meat, fish, insects or vegetables; nshima (maize porridge) is served with relish and stews the same way | Zambia (Bemba people) | Porridge, insect or fish stew | Yes | 30 |
| Jumiles salsa with tortillas | Stink bugs mashed with tomatoes, chilies and onions, eaten with corn tortillas | Guerrero, Mexico | Bugs, tomato, tortilla (chili, onion) | Tomato and tortilla yes; the same method works with other game bugs (plausible) | 44 |
| Giant water bug with tomato | Sauteed in oil with garlic, onions and tomatoes | Philippines | Water bug, tomato, oil (garlic, onion) | Yes except garlic and onion | 21 |
| Crawfish boil with corn | Crawfish boiled with corn on the cob, potatoes, onions and garlic | Louisiana | Crayfish, corn (potato, onion, garlic) | Crayfish and corn yes | 36, 37 |
| Russian crayfish with carrots | Crayfish boiled with carrots, onion, dill and bay leaf | Russia, Ukraine | Crayfish, carrots (onion, dill, bay) | Crayfish and carrots yes | 39 |
| Ant egg salad with mint | Weaver-ant eggs with roasted vegetables, long pepper and mint | Laos, Thailand | Ant brood, vegetables, mint | Yes except long pepper | 6, 8 |
| Fried battered grasshoppers (kripik, rempeyek) | Grasshoppers or crickets in a light batter, deep-fried | Indonesia | Insects, flour batter, oil | Yes | 34 |
| Cricket bread (sirkkaleipa) | Bread with cricket flour baked in | Finland (a modern shop product) | Flour, cricket flour | Yes - modern, not traditional | 47 |
| Cricket-flour pasta, cookies and chips | Wheat products with cricket or mealworm flour mixed in | Europe, North America (modern products) | Flour, insect flour | Yes - modern | 47, 48 |
| Cricket parathas | Flatbreads made with ground roasted crickets | Vij's restaurant, Vancouver (by 2011) | Flour, cricket meal | Yes - one restaurant's dish, so a curiosity | 34 |
| Mealworm burgers | Patties made from mealworm or cricket flour and other ingredients | Europe (modern products) | Insect flour, other ingredients | Plausible in the game (the source doesn't list the other ingredients) | 47, 46 |
| Wasp-larva rice (hebo-gohan) | Rice cooked with seasoned wasp larvae, for autumn festivals | Central Japan | Wasp brood, rice, soy sauce | Needs rice and soy sauce | 11, 12 |
| Sago grubs with rice porridge | Palm weevil larvae cooked in porridge, or eaten with sticky rice and salad | Vietnam | Grubs, rice | Needs rice | 33 |
| Fish shchi | Cabbage soup with fish in place of meat in fasting times | Russia | Cabbage, fish, carrots, mushrooms | Yes except onion and garlic | 126 |
| Fish tacos | Fried fish, cabbage and fresh tomato salsa on a corn tortilla | Baja California | Fish, cabbage, tomato, tortilla | Yes | 65 |
| Southern fish fry with hushpuppies | Cornmeal-coated fried catfish with fried corn dumplings | Southern United States | Fish, cornmeal, oil | Yes | 63 |
| Crayfish paste | A fermented crayfish sauce, described by a French ambassador to Siam in 1687-88 (today's Thai kapi is a fermented shrimp paste) | Thailand (historic) | Crayfish, salt | Yes | 20, 73 |

### 4b. Plausible combined dishes (not known real dishes)

Each is built from a real technique in sections 1-3. Named plainly.

| Plausible dish | Built from (real technique) | Game ingredients | Source of the technique |
|---|---|---|---|
| Bug-meat stew with pumpkin, carrot and cabbage | Mopane-worm stew with tomato; Zambian insect relish with porridge | Bug meat, pumpkin, carrot, cabbage, salt | 29, 30 |
| Locust (or cricket) flatbread | Cricket bread and cricket parathas; chapati and damper | Flour, ground dried locusts, water, salt | 47, 34, 115, 116 |
| Ant-brood or grub tamales | Tamales with any filling | Masa, ant brood or grubs, corn husk | 110, 3 |
| Bug-meat pozole | Pozole (hominy stew) with bug meat instead of pork | Hominy, bug meat, cabbage | 111 |
| Honey-glazed grub skewers | Kabayaki (a sweet glaze on skewered eel); grilled skewers | Beetle grubs, honey, salt | 67 |
| Wasp larvae in honey and salt | Hachinoko seasoned with soy sauce and sugar | Wasp brood, honey, salt (fish sauce for the soy) | 12 |
| Cricket polenta | Polenta, plus toasted crickets as a topping (as chapulines are used) | Cornmeal, crickets | 101, 1 |
| Grasshopper and seed trail mix | Toasted grasshoppers as a snack; roasted seeds; dried fruit | Toasted grasshoppers, sunflower and pumpkin seeds, dried berries | 1, 159, 160, 151 |
| Bug salsa with tomato | Jumiles salsa | Any small bug, tomato, salt (chili if it is ever added) | 44 |
| Bug-and-fish sauce | Prahok and fish sauce; historic crayfish paste | Fish or crayfish, salt | 72, 79, 20 |

---

## 5. How farming and life-sim games design cooking

Read from each game's wiki (sources 82-94). Recipe counts are what each wiki lists today. "Copy" and "avoid" are my
judgement, not the wikis'.

| Game | Recipes | How recipes are learned | Boosts and how long | Stations and tiers | Copy this | Avoid this | Source |
|---|---|---|---|---|---|---|---|
| Stardew Valley | 81 | Every recipe but one (fried egg) must be learned: a TV cooking show teaches a new one each Sunday for the first two years (32 in all, with reruns on Wednesdays); villagers send recipes by letter as friendship grows; some are bought at the saloon and other shops; some come with skill levels | One food boost and one drink boost at a time; a new food replaces the old boost. Lengths roughly 3-17 minutes | A kitchen comes with the first house upgrade; its fridge counts as part of your bag when cooking; a cookout kit later lets you cook anywhere | Recipes as small rewards from people and a TV show; the one-food-plus-one-drink rule (the game already chose one meal boost at a time, D54) | Cooking starts only after a house upgrade, so it arrives late | 82, 83 |
| Dinkum | 31 at the cooking table | None to learn: every recipe is listed at the cooking table, which can be built on day 1; you only need the ingredients | Every dish gives a "full" state (6-60 minutes) plus health and stamina over time; some add defence, attack, speed, mining or foraging | Single items cook on a campfire or barbecue (raw food does less); the cooking table; a licensed advanced table that cooks from chests within a 12 x 12 area; drinks in a keg, billy can or kettle | A menu of real, recognisable national dishes (damper, lamington, pavlova, meat pie, fairy bread) - the same idea as Bug Farmer's real-dish list. The advanced station that pulls from nearby chests | With nothing to learn, a new recipe is never a reward | 84, 85, 86, 87 |
| Core Keeper | Any 2 of 74 ingredients: 2,775 possible dishes | Nothing to learn: put any two ingredients in a cooking pot and see | The dish combines both ingredients' effects; most last 5-10 minutes (for example +15% larger harvests, +15% chance of a double fish). Golden crops, grown with a farming skill, make stronger dishes. The game has hunger | The cooking pot | Farming skill makes better ingredients, which make better dishes | Names are generated from the ingredients ("Mushy Mushroom Soup"), not real dishes - the opposite of the real-dish direction | 88, 89, 90 |
| Valheim | 88 foods listed | (Not checked) | Three different foods at once; each raises maximum health and stamina (and magic), and the effect fades over 10-50 minutes. No starving | A grill (cooking station), an iron grill, a cauldron, an oven and a preparation table. The cauldron levels up to 6 when you build kitchen furniture next to it: a spice rack, a butcher's table, pots and pans, a mortar and pestle. Each new region brings a new tier of food | Upgrading a station by placing real kitchen furniture beside it; food tiers that follow exploration | Three fading boosts at once means constant upkeep; Bug Farmer already chose one boost at a time | 91, 92 |
| Coral Island | About 107 | Letters from townspeople at friendship levels (36), skill levels, a few others. An unknown recipe can be cooked by choosing the right utensils and ingredients and passing a short timing game - doing it teaches the recipe | Boosts named by activity: speed, farming, fishing, gathering, ranching, mining, catching, stamina, defence. Better ingredients give a longer boost | A kitchen through a house upgrade; utensils (pot, frying pan, grill, oven, skewer, seasoning set...) bought from a shop decide which dishes you can make | Flexible slots such as "any fish", "any honey", "any insect" - its bug jerky is "any insect" on the grill. Learning a recipe by experimenting | A timing game on every cook would get old (my view) | 93 |
| Necesse | (not counted) | (not checked) | Three qualities: simple food 4 minutes, fine 8, gourmet 20 | A cooking pot and a roasting station. Food spoils | Three clear quality tiers, with longer boosts for better food | Spoiling food; Bug Farmer already chose no spoilage (D54) | 94 |

What section 5 means for the game:

- **Mix two ways of learning.** Simple dishes known from the start, as in Dinkum, so cooking is useful on day one;
  better dishes learned as small rewards - from townspeople (Stardew, Coral Island), from experimenting (Coral Island,
  Core Keeper) or bought.
- **Use flexible slots** ("any fish", "any bug meat", "any grub") so a recipe doesn't need one exact fish or bug -
  Coral Island does this, and it suits a game with many bug species.
- **Tie the tiers to stations and progress:** campfire for single items, wood stove for soups and stews, oven for
  breads and bakes, keg for drinks and ferments; Valheim's furniture upgrades are a good model for growing a kitchen.
- **Boosts are mostly tied to activities** (farming, fishing, mining, gathering, speed, stamina) in Stardew, Dinkum,
  Core Keeper and Coral Island; Valheim instead raises health and stamina. Bug Farmer's planned boosts (more stamina,
  more from each harvest, a better catch) match the genre.

---

## 6. Staples the list needs that aren't in the game yet

Each of these is a real, old way of making the staple from things the game already has.

| Staple | Why the list needs it | Simplest real way to make it from game things | Game ingredients? | Source |
|---|---|---|---|---|
| Cooking oil | Frying bugs and fish, roasting, corn pone, dressings; many of the dishes above | Press sunflower seeds in a screw press. The oil comes out; the crushed seeds left behind (seed cake or meal) are rich in protein and used as animal feed, fertiliser or fuel. Pumpkin seeds give a strong, nutty oil when roasted and pressed (Styria, Austria). Poppy seeds are also an oilseed | Yes: sunflower or pumpkin seeds and a new **oil press**. The seed cake could feed bugs or go in the compost | 161, 160, 188, 129, 163 |
| Vinegar | Pickles, escabeche, marinated mushrooms, jellied eels, switchel and oxymel, red cabbage, crab dip | Let cider (or any fruit wine) sour in the air: bacteria turn the alcohol into vinegar. A film called "mother of vinegar" forms and is added to start the next batch. Fruit vinegars are made from apple, quince, tomato and others | Yes: apples (or other fruit) and the keg | 185, 186, 189 |
| Cornmeal and corn flour | All the corn breads and porridges | Grind dried corn at a mill, coarse or fine | Yes: corn and the existing mill | 190, 191 |
| Lime or wood ash (for corn) | Corn tortillas, masa, tamales, atole, hominy, grits - plain cornmeal won't hold together as a dough | Soak and cook the corn in water with slaked lime (burnt limestone with water added - one of the oldest chemical processes, at least 9,000 years old), or with lye from wood ash, as was done historically | Wood ash from fires yes; limestone if the game has it (a kiln burns it to quicklime) | 95, 192, 193 |
| Bread raising | Sourdough and other risen breads (bakers once got their yeast from brewers) | Three real ways: a **sourdough starter** (flour and water left warm for a week or two, then fed); **barm**, the yeasty foam skimmed off brewing beer; **pearl ash**, a purified potash made from wood ashes, used to raise quick breads in 18th-century America (German gingerbread recipes still often use potash) | Yes: flour and water; or the keg's foam; or wood ash | 114, 194, 195, 196, 203, 202 |
| Sweetener | Jams, cakes, drinks | Honey already exists: it is about as sweet as sugar and never spoils if kept properly. Apple butter and powidl need no sweetener at all. Malt (sprouted, dried grain) gives malt syrup | Yes | 182, 144, 145, 197 |
| Savoury seasoning (instead of soy sauce) | Many Asian bug dishes use soy sauce or fish sauce | Fish sauce: fish coated in salt and fermented (for up to two years); Cambodia's prahok ferments salted, dried, pounded fish for about a month and skims off the liquid as fish sauce. The Romans had a fermented fish sauce too (garum). Historic Siam made a paste from crayfish | Yes: fish or crayfish, salt, a jar or keg | 72, 79, 199, 20 |
| Salt | Everywhere | Rock salt is mined; it seasons and cures food such as fish | Already in the game | 198 |
| Gelatin and thickeners | Jellies, kissel, aspics | Fish gelatin and isinglass (from dried swim bladders) are real; eel stock sets on its own (jellied eels). The oldest kissels were simply fermented grain porridges (oats, rye or wheat), so no starch is needed; modern ones use potato or corn starch | Yes: fish, eel, wheat | 200, 201, 68, 154 |
| Malt | Kvass, gruit ale, malt vinegar | Soak grain until it sprouts, then dry it with hot air | Yes: wheat (or corn) | 197 |
| Pectin | Jams that set | Not needed as a separate item: apples, plums and oranges are naturally rich in pectin; add them to berries or cherries | Yes | 149, 148 |

### Crops whose absence costs the most real dishes

Not a recommendation to add them - just what the tables above show:

- **Onion and garlic**: in the real versions of chapulines, chicatana salsa, mopane-worm stew, the water-bug saute, the
  crawfish boil, ratatouille, imam bayildi, halaszle, pilaki, bruschetta, shchi's old seasoning and many more.
- **Chili**: in nam phrik, chicatana and jumiles salsas, kimchi, Chinese spicy crayfish, chapulines.
- **Rice**: in hebo-gohan, goheimochi, jibachi senbei, sago grubs with rice, etouffee, kabayaki.
- **Beans**: the third of the Three Sisters; succotash.
- **Potatoes**: in the crawfish boil, ukha, the Czech Christmas carp's potato salad, pilaki.
- **A citrus for juice (lemon or lime)**: in many bug dishes; the game's orange can stand in for some, and real
  ant eggs are used as the sour ingredient in place of lemon (source 6).
- **Dill**: in the Swedish crayfish party and gravlax.

---

## Recommendations

A shortlist of 40 dishes, balanced across grown food, fish, bugs and combined dishes, ordered from simple (one
ingredient on a campfire) to combined (several ingredients, later stations). The station column is only a suggestion
for tiering. "Everyday real dish" means people really cook it as described (with at most a small, noted swap);
"plausible" means a real technique with game ingredients, not a known dish. Which meal gives which boost is still to
be settled with the recipe list (D50), so boosts are not proposed here.

| # | Dish | Group | Suggested station | New staple needed? | Real or plausible | Sources |
|---|---|---|---|---|---|---|
| 1 | Corn on the cob | Grown | Campfire | - | Everyday real dish | 106 |
| 2 | Johnnycake (cornmeal, water, salt by the fire) | Grown | Campfire | Cornmeal (mill) | Everyday real dish | 99 |
| 3 | Damper (campfire bread) | Grown | Campfire | - | Everyday real dish | 116 |
| 4 | Roasted salted pumpkin or sunflower seeds | Grown | Campfire | - | Everyday real dish | 159, 160 |
| 5 | Herbal tea (chamomile, mint, fennel or lavender) | Grown | Campfire | - | Everyday real dish | 165, 164, 134, 166 |
| 6 | Toasted grasshoppers (chapulines) | Bug | Campfire | - | Everyday real dish | 1, 2 |
| 7 | Locusts boiled in salt water and dried | Bug | Campfire | - | Everyday real dish | 28, 27 |
| 8 | Grubs roasted in hot ashes (witchetty-style) | Bug | Campfire | - | Everyday real dish | 31 |
| 9 | Boiled moth pupae with salt (beondegi) | Bug | Campfire | - | Everyday real dish | 16, 17 |
| 10 | Crayfish boiled in salt water | Bug | Campfire | - | Everyday real dish | 38, 39 |
| 11 | Salt-grilled fish on a skewer | Fish | Campfire | - | Everyday real dish | 66, 64 |
| 12 | Grilled carp (masgouf) | Fish | Campfire | - | Everyday real dish | 58 |
| 13 | Polenta or ugali (maize porridge) | Grown | Wood stove | Cornmeal | Everyday real dish | 101, 103 |
| 14 | Pumpkin soup | Grown | Wood stove | - | Everyday real dish | 128 |
| 15 | Tzimmes (carrots and prunes with honey) | Grown | Wood stove | - | Everyday real dish | 135 |
| 16 | Sauteed chanterelles | Grown | Wood stove | Oil | Everyday real dish | 140 |
| 17 | Apple butter or powidl (plum butter) | Grown | Wood stove | - | Everyday real dish | 144, 145 |
| 18 | Fried crickets | Bug | Wood stove | Oil | Everyday real dish | 8, 18 |
| 19 | Ant egg soup (with mint and fish sauce instead of Thai herbs) | Bug | Wood stove | Fish sauce | Everyday real dish, simplified | 7, 6 |
| 20 | Fried scorpions (a regional dish; a dare for most players) | Bug | Wood stove | Oil | Everyday real dish (Shandong) | 24 |
| 21 | Wasp larvae cooked with honey and salt | Bug | Wood stove | - | Plausible (the real hachinoko uses soy sauce and sugar) | 12 |
| 22 | Fish fried in a cornmeal coat | Fish | Wood stove | Oil, cornmeal | Everyday real dish (milk left out) | 63 |
| 23 | Ukha (clear fish soup with carrot and fennel seed) | Fish | Wood stove | - | Everyday real dish, simplified (no potato or leek) | 60 |
| 24 | Jellied eels | Fish | Wood stove | Vinegar | Everyday real dish (historic London) | 68 |
| 25 | Caterpillar stew with tomato, served with maize porridge | Combined | Wood stove | - | Everyday real dish (onion left out) | 29, 103 |
| 26 | Crayfish boil with corn on the cob | Combined | Wood stove | - | Everyday real dish (potatoes, onion, garlic left out) | 36, 37 |
| 27 | Bug-meat stew with pumpkin, carrot and cabbage | Combined | Wood stove | - | Plausible | 29, 30 |
| 28 | Fish shchi (cabbage soup with fish, mushrooms and carrot) | Combined | Wood stove | - | Everyday real dish (onion and garlic left out) | 126 |
| 29 | Battered fried grasshoppers (rempeyek) | Combined | Wood stove | Oil | Everyday real dish | 34 |
| 30 | Honey-glazed grub skewers | Combined | Wood stove | - | Plausible | 67 |
| 31 | Sourdough bread | Grown | Oven | Starter | Everyday real dish | 114 |
| 32 | Cornbread with sunflower seeds and berries | Grown | Oven | Cornmeal | Everyday real dish (Cherokee and Seneca), with a plain batter | 100 |
| 33 | Baked apples with honey | Grown | Oven | - | Everyday real dish | 147 |
| 34 | Cricket bread (cricket flour in the dough) | Combined | Oven | Starter | Real (a modern product) | 47 |
| 35 | Corn tortillas with a filling: toasted grasshoppers (tlayuda), fried ant brood, or fish (fish tacos) | Combined | Wood stove | Lime or wood ash, oil | Everyday real dish | 1, 57, 65, 96 |
| 36 | Smoked fish | Fish | Smoker (new) or campfire | - | Everyday real dish | 69 |
| 37 | Sauerkraut (with carrot or apple) | Grown | Keg or crock | - | Everyday real dish | 125 |
| 38 | Mead | Grown (drink) | Keg | - | Everyday real dish | 170 |
| 39 | Cider (and from it, vinegar) | Grown (drink) | Keg | A press | Everyday real dish | 171, 186 |
| 40 | Fish sauce (prahok-style) | Fish (seasoning) | Keg or jar | - | Everyday real dish | 72, 79 |

Balance: 16 grown (including 2 drinks), 7 fish (including a seasoning), 9 bug, 8 combined. 35 are everyday real
dishes as described or simplified; 3 are plausible; 2 are real but specific (a modern cricket bread; fried scorpions,
which are traditional only in Shandong).

Other recommendations from the research:

1. **Add four staples before the full list:** an oil press (sunflower or pumpkin seeds give oil plus seed cake for bug
   feed or compost), vinegar from cider in the keg, wood ash (or lime) for corn dough, and a sourdough starter. Each is
   a real, old process and each unlocks several dishes (section 6).
2. **Use fish sauce as the game's savoury seasoning.** It is real, made from fish and salt, and replaces soy sauce in
   the Asian bug dishes without inventing anything.
3. **Keep the dares as dares.** Fried tarantulas and centipedes exist mainly for tourists; if they appear, present
   them as curiosities, not as everyday food. Millipedes and mantises have no dish, so they need none.
4. **Fly larvae belong in bug feed, not in meals** (black soldier fly larvae are bred for feed; human eating is
   rare). Adult-fly "kunga cake" is real but only lightly sourced here.
5. **The bug farming in the game has real parallels worth surfacing in item descriptions:** Thai cricket farms,
   weaver-ant nests kept on mango trees and fed sugar water, Japanese wasp colonies moved beside houses, ants guarding
   citrus orchards since about the year 400 (sources 8, 6, 12, 9).
6. **Onion and garlic would add the most real dishes** if new crops are ever considered; chili, rice and beans come
   next (section 6).

---

## Source table

Every page below was opened and read for this research (Wikipedia articles as full text through Wikipedia's API;
game wikis through their MediaWiki API, which returns the same page content). The numbers match the "Source"
columns above.

| # | Source | What it was used for |
|---|---|---|
| 1 | https://en.wikipedia.org/wiki/Chapulines | Chapulines: toasted grasshoppers, seasoning, Oaxaca, season, tlayuda filling, 2017 Mariners novelty |
| 2 | https://en.wikipedia.org/wiki/Oaxacan_cuisine | Oaxacan food: chapulines as rural protein, from corn and alfalfa fields, semi-domesticated; tejate drink |
| 3 | https://en.wikipedia.org/wiki/Escamol | Escamoles: Liometopum ant larvae and pupae, Mexico City area, since the Aztecs, buttery and nutty |
| 4 | https://en.wikipedia.org/wiki/Atta_laevigata | Hormigas culonas: leafcutter queens, rainy season, salted water, roasted in clay pans, Santander |
| 5 | https://en.wikipedia.org/wiki/Atta_mexicana | Chicatanas: toasted or fried, tacos, Mixtec salsa de chicatanas with chili, onion, garlic |
| 6 | https://en.wikipedia.org/wiki/Ant_eggs | Khai mot daeng: weaver ant eggs and pupae, sour, used instead of lemon or vinegar, salad, farmed on trees with sugar water |
| 7 | https://en.wikipedia.org/wiki/Ant_egg_soup | Ant egg soup: Lao and Thai, ingredients, harvesting into a bucket of water, emblem of rural life |
| 8 | https://en.wikipedia.org/wiki/Thai_cuisine | Thai insects: FAO ~20,000 cricket farms; market insects; nam phrik maeng da and variants; tam khai mot daeng; insects bland when fried |
| 9 | https://en.wikipedia.org/wiki/Weaver_ant | Weaver ants: prized food in NE Thailand (larvae twice the price of beef); husbandry; used in citrus orchards since 400 AD |
| 10 | https://en.wikipedia.org/wiki/Oecophylla_smaragdina | Weaver ant larvae and pupae eaten in Thailand and the Philippines; taste creamy, sour, lemony |
| 11 | https://en.wikipedia.org/wiki/Insects_in_Japanese_culture | Hachinoko and hebo in Gifu/Nagano; hebo-gohan; inago a luxury food; wartime and famine role |
| 12 | https://en.wikipedia.org/wiki/Vespula_flaviceps | Wasp eaten in central Japan; colonies moved into hives near homes and sheltered in winter; soy sauce and sugar; rice dish at autumn festivals |
| 13 | https://en.wikipedia.org/wiki/Goheimochi | Goheimochi sauces include honey and wasp larvae |
| 14 | https://en.wikipedia.org/wiki/Senbei | Senbei varieties include jibachi senbei (with dried wasps) |
| 15 | https://en.wikipedia.org/wiki/Inago_no_tsukudani | Inago no tsukudani: rice grasshoppers in soy sauce and sugar; Nagano, Fukushima; preparation steps |
| 16 | https://en.wikipedia.org/wiki/Beondegi | Beondegi: boiled or steamed silkworm pupae; soup; canned; history |
| 17 | https://en.wikipedia.org/wiki/Bombyx_mori | Silkworm pupae eaten after reeling; Assam: boiled with salt or fried with chili or herbs |
| 18 | https://en.wikipedia.org/wiki/House_cricket | House cricket farmed for food in SE Asia; dry-roasted or deep-fried; cricket flour; EU approval |
| 19 | https://en.wikipedia.org/wiki/Omphisa_fuscidentalis | Bamboo worm (rot duan): deep-fried; now farmed |
| 20 | https://en.wikipedia.org/wiki/Nam_phrik | Nam phrik: chili dip ingredients; nam phrik maeng da with giant water bug |
| 21 | https://en.wikipedia.org/wiki/Lethocerus_indicus | Giant water bug as food: Vietnam, Thailand, Philippines (sauteed with garlic, onion, tomato), NE India |
| 22 | https://en.wikipedia.org/wiki/Fried_spider | Fried tarantula in Skuon, Cambodia: recipe, tourist attraction, Khmer Rouge origin theory, popular since ~1990s |
| 23 | https://en.wikipedia.org/wiki/Cambodian_cuisine | Fried spiders a remnant of the Khmer Rouge famine, now sold to tourists; crabs and crayfish eaten |
| 24 | https://en.wikipedia.org/wiki/Scorpion | Fried scorpion traditional in Shandong; sting left on; Thailand street food; Vietnam scorpion wine |
| 25 | https://en.wikipedia.org/wiki/Donghuamen_Night_Market | Beijing night market sold fried crickets, centipedes, silkworms, scorpions; closed 2016 |
| 26 | https://en.wikipedia.org/wiki/Arachnids_as_food | About 15 spider species eaten; fried scorpion in Shandong |
| 27 | https://en.wikipedia.org/wiki/Locust | Locusts as food: delicacy in many African, Middle Eastern and Asian countries; fried, smoked or dried; Saudi Ramadan spike |
| 28 | https://en.wikipedia.org/wiki/Kosher_locust | Yemenite locust cooking: boiled in salt water, oven- or sun-dried, head, wings and legs removed |
| 29 | https://en.wikipedia.org/wiki/Gonimbrasia_belina | Mopane worms: cleaning, salt-boiling, drying or smoking; fried or stewed with onion and tomato; with pap or sadza; canned |
| 30 | https://en.wikipedia.org/wiki/Zambian_cuisine | Nshima (maize porridge) with relish; insects eaten incl. mopane worms |
| 31 | https://en.wikipedia.org/wiki/Witchetty_grub | Witchetty grubs: raw or cooked in hot ashes; most important insect food of the desert |
| 32 | https://en.wikipedia.org/wiki/Honeypot_ant | Honeypot ants eaten by Indigenous Australians; dug up to 2 m deep |
| 33 | https://en.wikipedia.org/wiki/Rhynchophorus_ferrugineus | Palm weevil larvae: delicacy in SE Asia; Vietnam preparations |
| 34 | https://en.wikipedia.org/wiki/Entomophagy_in_humans | Insect eating worldwide; Indonesian fried grasshopper/cricket snacks; botok tawon; sago grubs; Thai markets; kunga cake; Vij's cricket parathas |
| 35 | https://en.wikipedia.org/wiki/Bee_brood | Bee brood harvested as food in many countries; pupae highest in protein |
| 36 | https://en.wikipedia.org/wiki/Seafood_boil | Crawfish boil: Louisiana, spring, ingredients, method |
| 37 | https://en.wikipedia.org/wiki/Louisiana_Creole_cuisine | Crawfish boil with potatoes, onions, corn; crab-boil spice bags; etouffee |
| 38 | https://en.wikipedia.org/wiki/Crayfish_party | Swedish crayfish party: August, salt water and dill, served cold |
| 39 | https://en.wikipedia.org/wiki/Crayfish_as_food | Crayfish in China (ma la), France, Mexico (acocil), Nordics (salt, sugar, ale, dill), Russia (carrots, onion, dill, bay) |
| 40 | https://en.wikipedia.org/wiki/%C3%89touff%C3%A9e | Etouffee: smothered shellfish with a roux over rice |
| 41 | https://en.wikipedia.org/wiki/Cajun_cuisine | The Cajun "trinity" of bell pepper, onion and celery |
| 42 | https://en.wikipedia.org/wiki/Chinese_mitten_crab | Mitten crab an autumn delicacy in Shanghai, prized for roe |
| 43 | https://en.wikipedia.org/wiki/Cicada | Cicadas eaten in Ancient Greece, China (mostly nymphs), etc.; novelty in the US |
| 44 | https://en.wikipedia.org/wiki/Jumiles | Jumiles salsa with tomatoes, chilies and onions; with corn tortillas; Taxco fiesta |
| 45 | https://en.wikipedia.org/wiki/Maguey_worm | Maguey worms deep-fried or braised, salt, lime, spicy sauce, in a tortilla |
| 46 | https://en.wikipedia.org/wiki/Mealworm | Mealworms: SE Asian street food; EU approval 2021; mostly snacks and bars in the West; pest of stored grain |
| 47 | https://en.wikipedia.org/wiki/Insects_as_food | 2,000+ edible insect species; 2 billion eaters; EU approvals; insect bread (Sirkkalepa), pasta, burgers |
| 48 | https://en.wikipedia.org/wiki/Cricket_flour | Cricket flour: made from freeze-dried crickets; used in pasta, bread, cookies, chips |
| 49 | https://en.wikipedia.org/wiki/Nsenene | Nsenene: seasonal bush-cricket delicacy in Uganda; swarms around May and November |
| 50 | https://en.wikipedia.org/wiki/Ugandan_cuisine | Nsenene and nswaa (white ants) as seasonal foods |
| 51 | https://en.wikipedia.org/wiki/Hermetia_illucens | Black soldier fly larvae: feed for poultry, fish, pets; human eating records hard to find |
| 52 | https://en.wikipedia.org/wiki/Millipede | Millipedes: defensive chemicals; no food use mentioned |
| 53 | https://en.wikipedia.org/wiki/List_of_edible_insects_by_country | Species lists by country (mantises listed for Thailand) |
| 54 | https://en.wikipedia.org/wiki/Cyriopagopus_albostriatus | Tarantula sold fried on the streets of Cambodia |
| 55 | https://en.wikipedia.org/wiki/Mexican_cuisine | Insects in Mexican food; Durango scorpion novelties; tacos; honey drinks balche and xtabentun |
| 56 | https://en.wikipedia.org/wiki/Skuon | Skuon known as "Spiderville", famous with visitors for fried spiders |
| 57 | https://es.wikipedia.org/wiki/Escamol | Escamoles (Spanish Wikipedia): harvested March-April from nests by agave, prickly pear and pepper trees; fried with butter and epazote, with egg, in tortillas; costly |
| 58 | https://en.wikipedia.org/wiki/Masgouf | Masgouf: seasoned grilled carp, often called Iraq's national dish |
| 59 | https://en.wikipedia.org/wiki/Fisherman%27s_soup | Halaszle: Hungarian paprika fish soup of carp and river fish, cooked in kettles over open fire; Christmas Eve |
| 60 | https://en.wikipedia.org/wiki/Ukha | Ukha: clear Russian freshwater fish soup; root vegetables, bay, dill, fennel seed; firebrand custom |
| 61 | https://en.wikipedia.org/wiki/Carp | Carp as food: Christmas Eve fried carp (Slovakia, Poland, Czechia, Croatia); sweet-and-sour carp; koikoku |
| 62 | https://en.wikipedia.org/wiki/Common_carp | Carp farmed since Roman times; spread by monks; Central European Christmas Eve dinners |
| 63 | https://en.wikipedia.org/wiki/Fish_fry | US fish fries: Wisconsin Friday perch; Southern cornmeal-coated catfish with hushpuppies; Lent |
| 64 | https://en.wikipedia.org/wiki/Fried_fish | Fried fish worldwide; the "shore lunch" of cooking the catch where it was caught |
| 65 | https://en.wikipedia.org/wiki/Taco | Fish tacos from Baja California: fried or grilled fish, cabbage, pico de gallo, sauce, tortilla |
| 66 | https://en.wikipedia.org/wiki/Ayu_sweetfish | Ayu grilled on a skewer with salt over charcoal |
| 67 | https://en.wikipedia.org/wiki/Kabayaki | Kabayaki: split eel (or catfish, loach) grilled with sweet soy glaze; eaten in midsummer for stamina |
| 68 | https://en.wikipedia.org/wiki/Jellied_eels | Jellied eels: boiled in vinegar stock, set by their own collagen; London East End |
| 69 | https://en.wikipedia.org/wiki/Smoked_fish | Smoked fish: salt then cold or hot smoke; smokehouses beside fishermen's cottages; kept a year or more |
| 70 | https://en.wikipedia.org/wiki/Escabeche | Escabeche: fried fish (or eggplant) marinated in vinegar sauce with paprika and citrus |
| 71 | https://en.wikipedia.org/wiki/Caspian_roach | Vobla: dried salted roach, a popular snack |
| 72 | https://en.wikipedia.org/wiki/Prahok | Prahok: salted, dried, pounded and fermented fish paste; the liquid that rises is fish sauce |
| 73 | https://en.wikipedia.org/wiki/Pla_ra | Pla ra: fish fermented with salt and rice bran or roasted rice for 6+ months; 1687 account of crayfish paste |
| 74 | https://en.wikipedia.org/wiki/Gravlax | Gravlax: salmon cured with salt, sugar and dill |
| 75 | https://en.wikipedia.org/wiki/Trout | Trout flesh close to salmon; farmed and stocked |
| 76 | https://en.wikipedia.org/wiki/European_perch | Perch: good eating, white firm flesh; suited to frying and grilling |
| 77 | https://en.wikipedia.org/wiki/Northern_pike | Pike: bony (Y-bones) but a long history in European cooking |
| 78 | https://en.wikipedia.org/wiki/Pilaki | Pilaki: fish or beans cooked in onion, garlic, carrot, potato, tomato and oil, served cold |
| 79 | https://en.wikipedia.org/wiki/Fish_sauce | Fish sauce: fish coated in salt and fermented up to two years; staple in SE Asia; Roman garum |
| 80 | https://en.wikipedia.org/wiki/Catfish | Catfish farmed and eaten for thousands of years in Africa, Asia, Europe, North America |
| 81 | https://en.wikipedia.org/wiki/Eel_as_food | Eel: Japan eats over 70% of the world catch; eel blood is toxic until cooked |
| 82 | https://stardewvalleywiki.com/Cooking | Stardew: 81 recipes; kitchen with first house upgrade; cookout kit; each recipe must be learned; one food buff and one drink buff; buff durations about 3-17 min |
| 83 | https://stardewvalleywiki.com/The_Queen_of_Sauce | Stardew TV cooking show: new recipe each Sunday for two years, reruns Wednesdays, 32 recipes |
| 84 | https://dinkum.fandom.com/wiki/Cooking_Table | Dinkum: cooking table craftable from day 1; all recipes available; food worth its ingredients |
| 85 | https://dinkum.fandom.com/wiki/Template:CookingTableRecipes | Dinkum: the 31 cooking-table dishes with buffs (Full 6-60 min, health, stamina, defence, attack...) |
| 86 | https://dinkum.fandom.com/wiki/Advanced_Cooking_Table | Dinkum: licence-gated advanced table cooks from nearby storage (12x12) |
| 87 | https://dinkum.fandom.com/wiki/Consumables | Dinkum: raw food weaker, cooked on campfire/BBQ better; brewing in keg, billy can, kettle; buff types |
| 88 | https://corekeeper.fandom.com/wiki/Cooking | Core Keeper: combine two of 74 ingredients (2,775 combinations); names from ingredients; golden crops via Expert gardener |
| 89 | https://corekeeper.fandom.com/wiki/Food | Core Keeper: hunger bar; dish buffs mostly 5-10 min (e.g. larger harvests, double fish) |
| 90 | https://corekeeper.fandom.com/wiki/Cooking_Pot | Core Keeper cooking pot: "Combine two and see what happens!" |
| 91 | https://valheim.fandom.com/wiki/Food | Valheim: three foods at once; effects fade; 10-50 min; tiered by biome; stations |
| 92 | https://valheim.fandom.com/wiki/Cauldron | Valheim cauldron: upgrades to level 6 by building spice rack, butcher's table, pots and pans, mortar and pestle nearby |
| 93 | https://coralisland.fandom.com/wiki/Cooking | Coral Island: kitchen upgrade; utensils; recipes from hearts and skills; manual cooking teaches recipes; "any fish/insect" slots; bug jerky; quality lengthens buffs |
| 94 | https://necessewiki.com/Food | Necesse: simple 4 min, fine 8 min, gourmet 20 min buffs; cooking pot and roasting station; food spoils (read through a summarising web fetch) - UNVERIFIED in detail: read through a summarising web fetch, not line by line |
| 95 | https://en.wikipedia.org/wiki/Nixtamalization | Nixtamalization: corn soaked and cooked in limewater or wood-ash lye; plain cornmeal won't form a dough, nixtamalized meal makes masa |
| 96 | https://en.wikipedia.org/wiki/Corn_tortilla | Corn tortilla: ground hominy, salt and water on a comal; arepa uses unnixtamalized maize |
| 97 | https://en.wikipedia.org/wiki/Masa | Masa: dough of ground nixtamalized corn for tortillas and tamales |
| 98 | https://en.wikipedia.org/wiki/Arepa | Arepa: ground maize dough flatbread, Colombia and Venezuela |
| 99 | https://en.wikipedia.org/wiki/Johnnycake | Johnnycake/hoecake: cornmeal, salt and water, baked before a fire or on a griddle; served with honey |
| 100 | https://en.wikipedia.org/wiki/Cornbread | Cornbread: earliest just cornmeal and water; corn pone egg- and milk-free; Cherokee and Seneca add sunflower seeds, apples, berries |
| 101 | https://en.wikipedia.org/wiki/Polenta | Polenta: boiled cornmeal; can be cooled then baked, fried or grilled |
| 102 | https://en.wikipedia.org/wiki/M%C4%83m%C4%83lig%C4%83 | Mamaliga: maize porridge of Romania, Moldova and neighbours |
| 103 | https://en.wikipedia.org/wiki/Ugali | Ugali/sadza/nshima/pap: maize meal cooked in water to a stiff dough; across Africa |
| 104 | https://en.wikipedia.org/wiki/Grits | Grits: porridge of coarsely ground corn or hominy in salted water |
| 105 | https://en.wikipedia.org/wiki/Hominy | Hominy: corn kernels treated with alkali (lime or lye) |
| 106 | https://en.wikipedia.org/wiki/Corn_on_the_cob | Corn on the cob: sweet corn steamed, boiled or grilled; loses sweetness within a day |
| 107 | https://en.wikipedia.org/wiki/Popcorn | Popcorn: a special popping variety of flint corn; eaten salted or sweetened |
| 108 | https://en.wikipedia.org/wiki/Pinole | Pinole: roasted ground maize for drinks and baking; national drink of Nicaragua |
| 109 | https://en.wikipedia.org/wiki/Atole | Atole: hot masa drink, with tamales, Day of the Dead |
| 110 | https://en.wikipedia.org/wiki/Tamale | Tamale: masa steamed in a corn husk with any filling |
| 111 | https://en.wikipedia.org/wiki/Pozole | Pozole: hominy stew garnished with cabbage, chili, onion |
| 112 | https://en.wikipedia.org/wiki/Tejuino | Tejuino: lightly fermented corn-dough drink, served with lime and salt |
| 113 | https://en.wikipedia.org/wiki/Chicha | Chicha de jora: Andean corn beer |
| 114 | https://en.wikipedia.org/wiki/Sourdough | Sourdough: starter of flour and water left warm one to two weeks; prospectors carried it |
| 115 | https://en.wikipedia.org/wiki/Chapati | Chapati: whole-wheat flour and water, griddle then puffed over flame |
| 116 | https://en.wikipedia.org/wiki/Damper_(food) | Damper: flour, salt and water baked in campfire coals |
| 117 | https://en.wikipedia.org/wiki/Hardtack | Hardtack: flour, water, salt; long-keeping cracker for voyages |
| 118 | https://en.wikipedia.org/wiki/Matzah | Matzah: unleavened flatbread of Passover |
| 119 | https://en.wikipedia.org/wiki/Pain_d%27%C3%A9pices | Pain d'epices: rye flour, honey and spices (1694) |
| 120 | https://en.wikipedia.org/wiki/Lebkuchen | Lebkuchen: honey-sweetened German Christmas cakes |
| 121 | https://en.wikipedia.org/wiki/Pa_amb_tom%C3%A0quet | Pa amb tomaquet: bread rubbed with tomato, oil and salt |
| 122 | https://en.wikipedia.org/wiki/Bruschetta | Bruschetta: grilled bread with garlic, oil, salt, often tomatoes |
| 123 | https://en.wikipedia.org/wiki/Manakish | Manakish: Levantine dough topped with za'atar and oil |
| 124 | https://en.wikipedia.org/wiki/Za%27atar | Za'atar: wild thyme-like herbs, sesame, sumac and salt |
| 125 | https://en.wikipedia.org/wiki/Sauerkraut | Sauerkraut: shredded cabbage layered with salt and fermented; keeps months; carrots, caraway, apples added in Eastern Europe |
| 126 | https://en.wikipedia.org/wiki/Shchi | Shchi: Russian cabbage soup; historically cabbage, meat, mushrooms, flour, onion and garlic; fish in fasting times; carrots |
| 127 | https://en.wikipedia.org/wiki/Red_cabbage | Red cabbage keeps its colour when cooked with vinegar or acidic fruit |
| 128 | https://en.wikipedia.org/wiki/Pumpkin_soup | Pumpkin soup: pumpkin puree with broth |
| 129 | https://en.wikipedia.org/wiki/Pumpkin_seed_oil | Styrian pumpkin seed oil: pressed from roasted seeds; dressing with cider vinegar; drops on pumpkin soup |
| 130 | https://en.wikipedia.org/wiki/Ratatouille | Ratatouille: tomato, onion, garlic, courgette, eggplant, pepper, herbs incl. fennel and thyme |
| 131 | https://en.wikipedia.org/wiki/%C4%B0mam_bay%C4%B1ld%C4%B1 | Imam bayildi: eggplant stuffed with onion, garlic and tomato, simmered in oil |
| 132 | https://en.wikipedia.org/wiki/Baba_ghanoush | Baba ghanoush: roasted eggplant, oil, lemon, tahini |
| 133 | https://en.wikipedia.org/wiki/Caponata | Caponata: fried eggplant in sweet-sour tomato sauce with celery, olives, capers |
| 134 | https://en.wikipedia.org/wiki/Fennel | Fennel: bulb, leaves and seeds eaten; fennel tea; pickled eggplants of Almagro use fennel stems |
| 135 | https://en.wikipedia.org/wiki/Tzimmes | Tzimmes: carrots and prunes stewed slowly with honey; Rosh Hashanah |
| 136 | https://en.wikipedia.org/wiki/Succotash | Succotash: sweet corn with lima or shell beans |
| 137 | https://en.wikipedia.org/wiki/Three_Sisters_(agriculture) | Three Sisters: maize, beans and squash planted together; sunflowers a fourth sister |
| 138 | https://en.wikipedia.org/wiki/Kimchi | Kimchi: salted fermented cabbage with chili, garlic, ginger, salted seafood |
| 139 | https://en.wikipedia.org/wiki/Tabbouleh | Tabbouleh: parsley, bulgur, tomato, mint, onion, oil, lemon |
| 140 | https://en.wikipedia.org/wiki/Chanterelle | Chanterelles: flavour is fat-soluble, sauteed in oil; soups; dried and ground as seasoning |
| 141 | https://en.wikipedia.org/wiki/Puffball | Puffballs: edible only when young and white inside; deadly look-alikes |
| 142 | https://en.wikipedia.org/wiki/Agaricus_bisporus | Common brown or white mushroom; grows in rich soil and compost; widely cultivated |
| 143 | https://en.wikipedia.org/wiki/Marinated_mushrooms | Marinated mushrooms: preserved in vinegar; a Polish tradition |
| 144 | https://en.wikipedia.org/wiki/Apple_butter | Apple butter: apples cooked long and slow until caramelised; medieval monasteries; family kettle events |
| 145 | https://en.wikipedia.org/wiki/Powidl | Powidl: plum butter cooked for hours with no added sweetener; communal autumn event; a sweetener alongside honey |
| 146 | https://en.wikipedia.org/wiki/Apple_sauce | Apple sauce: puree of apples |
| 147 | https://en.wikipedia.org/wiki/Baked_apple | Baked apples: cored, filled, honey among the sweeteners; on a wood stove or in the oven; German Christmas |
| 148 | https://en.wikipedia.org/wiki/Fruit_preserves | Fruit preserves: confit = fruit cooked with honey or sugar until jam-like; low-pectin fruit helped by orange; konfyt includes prickly pear |
| 149 | https://en.wikipedia.org/wiki/Pectin | Pectin: high in apples, plums, quince, oranges; low in cherries, grapes, strawberries |
| 150 | https://en.wikipedia.org/wiki/Marmalade | Marmalade: first quince; early orange marmalade recipe 1677 |
| 151 | https://en.wikipedia.org/wiki/Dried_fruit | Dried fruit: sun drying; since the 4th millennium BC in Mesopotamia |
| 152 | https://en.wikipedia.org/wiki/Prune | Prune: dried plum of suitable varieties |
| 153 | https://en.wikipedia.org/wiki/Kompot | Kompot: fruit boiled in lots of water, sweetened with honey or sugar; preserves fruit for winter |
| 154 | https://en.wikipedia.org/wiki/Kissel | Kissel: berry or grain jelly thickened with starch; old versions set with fish gelatin |
| 155 | https://en.wikipedia.org/wiki/Colonche | Colonche: prickly pear juice boiled 2-3 hours then fermented a few days |
| 156 | https://en.wikipedia.org/wiki/Nopal | Nopal: prickly pear pads and fruit eaten raw or cooked |
| 157 | https://en.wikipedia.org/wiki/Opuntia_ficus-indica | Prickly pear: a domesticated fruit and vegetable crop of dry lands |
| 158 | https://en.wikipedia.org/wiki/Pastila | Pastila: apple or berry paste with honey or sugar and egg whites; honey version the cheapest |
| 159 | https://en.wikipedia.org/wiki/Pumpkin_seed | Pumpkin seeds roasted and salted as a snack; pipian; sikil pak |
| 160 | https://en.wikipedia.org/wiki/Sunflower_seed | Sunflower seeds: snack, dried, roasted, salted; oilseed types pressed for oil |
| 161 | https://en.wikipedia.org/wiki/Sunflower_oil | Sunflower oil: pressed from the seeds; a frying oil with a neutral taste |
| 162 | https://en.wikipedia.org/wiki/Halva | Sunflower halva: roasted ground sunflower seeds, sweetened; former USSR, Bulgaria, Romania |
| 163 | https://en.wikipedia.org/wiki/Poppy_seed | Poppy seeds: bars of boiled seeds with honey in the Balkans and Greece; poppy seed rolls |
| 164 | https://en.wikipedia.org/wiki/Chamomile | Chamomile tea from dried flowers and hot water |
| 165 | https://en.wikipedia.org/wiki/Herbal_tea | Herbal teas: infusions of any herb |
| 166 | https://en.wikipedia.org/wiki/Lavandula | Culinary lavender in desserts and teas; bees make lavender honey |
| 167 | https://en.wikipedia.org/wiki/Dandelion_coffee | Dandelion coffee: roasted root as coffee substitute |
| 168 | https://en.wikipedia.org/wiki/Taraxacum_officinale | Dandelion: flowers for wine, greens for salads, roots for coffee substitute |
| 169 | https://en.wikipedia.org/wiki/Fruit_wine | Fruit wines; dandelion wine from petals, sugar and an acid |
| 170 | https://en.wikipedia.org/wiki/Mead | Mead: honey and water fermented; melomel with fruit, metheglin with spices |
| 171 | https://en.wikipedia.org/wiki/Cider | Cider: fermented apple juice |
| 172 | https://en.wikipedia.org/wiki/Kvass | Kvass: fermented drink from rye bread soaked in hot water |
| 173 | https://en.wikipedia.org/wiki/Gruit | Gruit: herb mix incl. yarrow that flavoured beer before hops |
| 174 | https://en.wikipedia.org/wiki/Switchel | Switchel: water, vinegar, often ginger, sweetened with molasses or honey |
| 175 | https://en.wikipedia.org/wiki/Oxymel | Oxymel: honey and vinegar |
| 176 | https://en.wikipedia.org/wiki/Shrub_(drink) | Shrub: sweetened vinegar syrup with fruit, mixed with water |
| 177 | https://en.wikipedia.org/wiki/Salvia_officinalis | Sage: paired with pumpkin, fried as a garnish, favoured with fish in Italy |
| 178 | https://en.wikipedia.org/wiki/Thyme | Thyme: part of bouquet garni and herbes de Provence; dries well |
| 179 | https://en.wikipedia.org/wiki/Trifolium_pratense | Red clover flowers and leaves edible; can be ground into flour |
| 180 | https://en.wikipedia.org/wiki/Aloe_vera | Aloe: gel used on skin; ingested latex can be toxic |
| 181 | https://en.wikipedia.org/wiki/Achillea_millefolium | Yarrow: traditional wound herb; no food use in the article |
| 182 | https://en.wikipedia.org/wiki/Honey | Honey: does not spoil when properly stored; sweetness close to table sugar |
| 183 | https://en.wikipedia.org/wiki/Pozol | Pozol: fermented corn dough and drink, southern Mexico |
| 184 | https://en.wikipedia.org/wiki/Shanghai_cuisine | Shanghai hairy crab steamed with ginger, dipped in vinegar, sugar and ginger |
| 185 | https://en.wikipedia.org/wiki/Vinegar | Vinegar: double fermentation; fruit vinegars from fruit wines (apple, tomato...); oxymel and shrubs |
| 186 | https://en.wikipedia.org/wiki/Apple_cider_vinegar | Cider vinegar: apple juice fermented to cider, then to vinegar |
| 187 | https://en.wikipedia.org/wiki/Pickling | Pickling: in brine (fermentation) or vinegar; since ancient Mesopotamia |
| 188 | https://en.wikipedia.org/wiki/Expeller_pressing | Oil pressing: seeds squeezed in a screw press; leaves a press cake used in local dishes or animal feed |
| 189 | https://en.wikipedia.org/wiki/Mother_of_vinegar | Mother of vinegar: a film of bacteria and yeast that turns cider or wine into vinegar; added to start new batches |
| 190 | https://en.wikipedia.org/wiki/Cornmeal | Cornmeal: ground dried maize; nixtamalized meal is masa harina; boiled cornmeal is polenta |
| 191 | https://en.wikipedia.org/wiki/Gristmill | Gristmill: grinds grain into flour |
| 192 | https://en.wikipedia.org/wiki/Calcium_hydroxide | Slaked lime: quicklime plus water, from burnt limestone (since ~7000 BCE); used for nixtamalizing maize and pickling |
| 193 | https://en.wikipedia.org/wiki/Wood_ash | Wood ash: lye from ashes used for nixtamalization; ashes leached for potash; Sumerian bread baked under hot ash |
| 194 | https://en.wikipedia.org/wiki/Leavening_agent | Leavening: sourdough starter, beer barm, pearl ash (Amelia Simmons, 1796) |
| 195 | https://en.wikipedia.org/wiki/Barm | Barm: yeast foam from fermenting beer, used to raise bread |
| 196 | https://en.wikipedia.org/wiki/Potassium_carbonate | Pearl ash (refined potash) raised quick breads in 18th-century America; German gingerbread uses potassium carbonate |
| 197 | https://en.wikipedia.org/wiki/Malt | Malt: grain soaked to sprout, then dried with hot air; for beer, malt vinegar, malt syrup |
| 198 | https://en.wikipedia.org/wiki/Halite | Rock salt: mined; used to season and to cure foods such as fish |
| 199 | https://en.wikipedia.org/wiki/Garum | Garum: Roman fermented fish sauce |
| 200 | https://en.wikipedia.org/wiki/Isinglass | Isinglass: collagen from dried fish swim bladders; clears beer and wine |
| 201 | https://en.wikipedia.org/wiki/Gelatin | Gelatin can be made from fish; boiling bones or cartilage at home gives a stock that sets (aspic) |
| 202 | https://en.wikipedia.org/wiki/Baker%27s_yeast | Early bread yeast: wild yeast in flour and water; 19th-century bakers got yeast from brewers |
| 203 | https://en.wikipedia.org/wiki/Potash | Potash and pearl ash made from wood ashes; asheries |

Also opened while researching, but not cited above (nothing in them changed a row):

https://dinkum.fandom.com/wiki/Crafting_Recipes, https://en.wikipedia.org/wiki/African_Palm_Weevil, https://en.wikipedia.org/wiki/Asian_giant_hornet, https://en.wikipedia.org/wiki/Balch%C3%A9, https://en.wikipedia.org/wiki/Bannock, https://en.wikipedia.org/wiki/Bush_tucker, https://en.wikipedia.org/wiki/Cabbage_soup, https://en.wikipedia.org/wiki/Cooking_oil, https://en.wikipedia.org/wiki/Corn_oil, https://en.wikipedia.org/wiki/Cossidae, https://en.wikipedia.org/wiki/Cream_of_mushroom_soup, https://en.wikipedia.org/wiki/Desert_locust, https://en.wikipedia.org/wiki/Fish_amok, https://en.wikipedia.org/wiki/Fish_soup, https://en.wikipedia.org/wiki/Fish_stew, https://en.wikipedia.org/wiki/Gozinaki, https://en.wikipedia.org/wiki/Gryllus_bimaculatus, https://en.wikipedia.org/wiki/Hornet, https://en.wikipedia.org/wiki/Huhu_beetle, https://en.wikipedia.org/wiki/Isan, https://en.wikipedia.org/wiki/Japanese_cuisine, https://en.wikipedia.org/wiki/Lao_cuisine, https://en.wikipedia.org/wiki/Liometopum_apiculatum, https://en.wikipedia.org/wiki/List_of_fermented_foods, https://en.wikipedia.org/wiki/Lye, https://en.wikipedia.org/wiki/Mantis, https://en.wikipedia.org/wiki/Mezcal_worm, https://en.wikipedia.org/wiki/Migratory_locust, https://en.wikipedia.org/wiki/Mint_tea, https://en.wikipedia.org/wiki/Nagano_Prefecture, https://en.wikipedia.org/wiki/Olivierus_martensii, https://en.wikipedia.org/wiki/Pupa, https://en.wikipedia.org/wiki/Rhynchophorus, https://en.wikipedia.org/wiki/Scolopendra_subspinipes, https://en.wikipedia.org/wiki/Shandong_cuisine, https://en.wikipedia.org/wiki/Sphenarium_purpurascens, https://en.wikipedia.org/wiki/Swedish_cuisine, https://en.wikipedia.org/wiki/Thai_curry, https://en.wikipedia.org/wiki/Thai_salads, https://en.wikipedia.org/wiki/Tortilla, https://en.wikipedia.org/wiki/Tsukudani, https://en.wikipedia.org/wiki/Wangfujing, https://en.wikipedia.org/wiki/Xtabent%C3%BAn, https://en.wikipedia.org/wiki/Yellow_perch, https://en.wikipedia.org/wiki/Zimbabwe, https://en.wikipedia.org/wiki/Zophobas_atratus, https://valheim.fandom.com/wiki/Crafting, https://academic.oup.com/jee/article/113/5/2150/5892968 (nsenene: no cooking information)

Could not be opened (so nothing from them is used): https://www.atlasobscura.com/foods/nsenene-grasshopper-uganda
(blocked, HTTP 403), https://www.sciencedirect.com/science/article/pii/S0740002018305240 (HTTP 403),
https://www.npr.org/2011/10/10/141134793/somethings-fishy-about-chinese-hairy-crabs (timed out),
https://onyamarks.blogspot.com/2008/11/nsenene-chronicle.html (HTTP 404). The one claim they were meant to check -
how nsenene are cooked - is marked UNVERIFIED in section 1.

