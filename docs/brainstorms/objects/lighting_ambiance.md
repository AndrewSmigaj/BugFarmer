# Lighting & Ambiance Objects — Brainstorm

Lights and mood objects across poor→fancy, indoor & outdoor — including the glow-bug jar bug-farming
crossover. Design only.

Read alongside:
- `docs/product/design/game_design.md` §16 (day/night), §11.5 (furniture idle boosts), §11.6 (fuel/power).
- Existing ids: `torch`, `candle`, `candelabra`, `lantern`, `lamp_floor`, `lamp_floor_fancy`,
  `lamp_table`, `lamp_post`, `fireplace`.
- Bug crossover inputs from `bug_farming.md` (glow-bugs) and `cooking_food.md`/beekeeping (beeswax).

## Rules this file follows
- Light is **fuel vs power vs passive**: candles/torches burn (consumable/fuel feel), some lamps are
  electric (§11.6) once that ships, magical/bug lights are passive. Tag intent, don't add a schema
  flag ahead of the feature.
- Variety poor→fancy, indoor & outdoor. Many of these double as **idle-boost decor** (§11.5).
- Some lights tie to night gameplay (light traps in `bug_farming.md` §1.7, night fishing).

---

## 1. CANDLES & SMALL FLAMES (poor, indoor)

| id | one-line | tier | notes |
|----|----------|------|-------|
| `candle` *(exists)* | a single lit candle on a dish | poor | tiny warm glow |
| `candle_pair` | two candles in a small holder | poor | slightly more light |
| `candlestick` | a tall single candlestick | poor | classic table light |
| `candelabra` *(exists)* | branched multi-candle stand | mid | elegant, more light |
| `beeswax_candle` | a honey-scented beeswax candle | poor/mid | bug crossover (beeswax from hives); calm ambiance |
| `votive_cluster` | a tray of small votive candles | poor | cozy grouped glow |
| `tea_light_row` | a row of floating tea lights | poor | decorative water/edge accent |

## 2. LAMPS (indoor, poor→fancy; many electric-capable)

| id | one-line | tier | notes |
|----|----------|------|-------|
| `lamp_table` *(exists)* | a small table lamp | common | desk/side-table light |
| `lamp_floor` *(exists)* | a standing floor lamp | common | room light |
| `lamp_floor_fancy` *(exists)* | brass fringed floor lamp | fancy | richer room light |
| `oil_lamp` | a glass-chimney oil lamp | poor | fuel (oil); warm pool of light |
| `desk_lamp` | a hooded adjustable desk lamp | common | task light (electric-capable) |
| `lamp_banker` | a green-shade banker's lamp | mid | study ambiance |
| `lamp_tiffany` | a stained-glass shade lamp | fancy | colorful prestige light |
| `sconce_wall` | a wall-mounted candle/lamp sconce | common | wall light, saves floor |
| `sconce_gas` | an ornate wall gas-lamp sconce | mid | hallway/manor light |

## 3. LANTERNS (indoor/outdoor, portable feel)

| id | one-line | tier | notes |
|----|----------|------|-------|
| `lantern` *(exists)* | a framed glass hand lantern | common | carry/hang, warm flame |
| `lantern_paper` | a soft paper lantern | poor | gentle diffuse glow, decorative |
| `lantern_iron` | a heavy iron storm lantern | mid | rugged outdoor light |
| `lantern_hanging` | a chained hanging lantern | mid | hang from a beam/post |
| `lantern_railroad` | a red-glass signal lantern | mid | rustic/mining flavor (cf. cave/mine set) |

## 4. TORCHES & BRAZIERS (outdoor, fire)

| id | one-line | tier | notes |
|----|----------|------|-------|
| `torch` *(exists)* | a wall/ground torch | poor | basic outdoor/cave light, burns |
| `torch_tiki` | a bamboo tiki torch | poor | yard/party flame |
| `wall_torch_iron` | an iron wall-bracket torch | poor | mounted flame, dungeon/manor |
| `brazier` | an iron fire bowl on legs | mid | bright outdoor area light + warmth |
| `brazier_stone` | a carved stone fire bowl | mid | grand courtyard light |
| `fire_pit` | a ringed-stone ground fire pit | mid | gathering light + warmth (cf. `campfire`) |
| `bonfire_stack` | a tall log bonfire | mid | big outdoor event light |

## 5. GRAND / CEILING LIGHTS (fancy, indoor)

| id | one-line | tier | notes |
|----|----------|------|-------|
| `chandelier_iron` | a wrought-iron candle chandelier | mid | hall centerpiece |
| `chandelier_crystal` | a sparkling crystal chandelier | fancy | manor showpiece, big light |
| `chandelier_antler` | a rustic antler chandelier | mid | lodge/cabin flavor |
| `pendant_lamp` | a single hanging pendant lamp | common | over a table/island |
| `lantern_chandelier` | a ring of hanging lanterns | mid | tavern/kitchen feel |

## 6. STRING & FAIRY LIGHTS (outdoor/indoor, festive)

| id | one-line | tier | notes |
|----|----------|------|-------|
| `string_lights` | a strand of warm bulb string lights | common | drape across posts; party/yard |
| `fairy_lights` | a fine strand of tiny twinkle lights | common | delicate decor glow |
| `paper_lantern_string` | a strand of colored paper lanterns | common | festival ambiance |
| `lantern_garland` | a garland of small hanging lanterns | mid | pretty path/eave light |
| `globe_string_lights` | round frosted-globe string lights | mid | patio/cafe feel |

## 7. OUTDOOR POSTS & PATH LIGHTS

| id | one-line | tier | notes |
|----|----------|------|-------|
| `lamp_post` *(exists)* | a street/garden lamp post | mid | tall outdoor light |
| `lamp_post_double` | a twin-globe lamp post | fancy | grand avenue light |
| `path_light` | a short staked path light | poor | line a walkway |
| `bollard_light` | a low glowing bollard | mid | modern path edge |
| `gate_lantern` | a lantern mounted on a gatepost | common | entrance light |

## 8. FIREPLACES & HEARTHS (indoor, ambiance + light)

| id | one-line | tier | notes |
|----|----------|------|-------|
| `fireplace` *(exists)* | a stone fireplace with flames | mid | room centerpiece, warmth + light |
| `fireplace_brick` | a brick hearth with mantel | mid | cozier cottage variant |
| `fireplace_grand` | a grand carved-marble fireplace | fancy | manor showpiece |
| `wood_stove_glow` (cf. `stove_wood`) | a glowing pot-belly stove | mid | heat + soft light, cabin flavor |
| `hearth_open` | a rustic open cooking hearth | poor | cottage hearth (cooking crossover) |

## 9. BUG-FARMING CROSSOVER LIGHTS (the signature ones)

Living/bug-derived lights — pay off the bug-farming loop as ambiance.
| id | one-line | tier | notes |
|----|----------|------|-------|
| `glowbug_jar` | a mason jar of captive glowing bugs | poor/mid | passive soft glow; needs farmed glow-bugs (no fuel) |
| `glowbug_lantern` | an ornate lantern housing glow-bugs | mid | brighter, prettier living light |
| `firefly_globe` | a glass globe swarming with fireflies | mid | magical pulsing glow; bug-farm prize |
| `glowbug_chandelier` | a hanging cluster of glow-bug jars | fancy | living chandelier; showpiece |
| `glowworm_string` | a strand seeded with glowworms | mid | living "fairy lights" |
| `glow_mushroom_lamp` | a lamp grown over glowing mushrooms | mid | flora crossover; eerie green glow |
| `glowbug_path_jars` | staked jars of glow-bugs lining a path | poor | living path lights |

---

## Notes / follow-ups
- Light "brightness/radius" + day-night interaction values belong in the lighting/render + ecology
  work, not here. Many lights should also count as §11.5 idle-boost decor (flag when catalogued).
- Glow-bug lights consume a **living input** that can dim/expire if the bugs aren't kept — a nice
  soft maintenance hook tying decor back to the bug-farm loop.
- Electric lamps get the §11.6 power flag *when that system ships*.
