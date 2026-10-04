"""seed_registry.py — write the first versions of the zone and bug registries for the review app.

Run ONCE (2026-10-04): `python3 tools/gdd/seed_registry.py`. It writes docs/gdd/data/zones.jsonl and bugs.jsonl and
refuses to overwrite them unless --force: after seeding, those two files are edited by hand and are the source of
truth for which zones exist and which bugs live where (docs/plans/review-app.md).

Where the content comes from:
- ZONES: GDD §01 (the 5 x 4 grid, rings, dangers, what each zone is for) and the built zones' zone.json.
- BUG_ZONES: the assistant's reading of each §03 sheet's "where it lives" line and §04's zone table (2026-10-03).
  Every zone link is "proposed": nothing here is the owner's decision until a zone is signed off in the app.
- Links: lineup rows (docs/gdd/bug_lineups.jsonl, verdict != cut) are the roster; bug-list rows
  (bug_table.jsonl) and game species (nakama/data/species.json) are joined to them by name, by Latin name, or by
  the hand-made links below, each with its reason.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs/gdd/data"

# id, name, aliases, row, col, ring, danger, built zone id, purpose, older sheets
ZONES = [
    ("locust_farmland", "Locust Farmland", ["the western town", "western town", "Locust Farmland + town"], 0, 0, "far", "hard", None,
     "Ruined farmland where you hold a line against locust swarms, around the western town (electricity starts here).",
     ["docs/product/economy/zones/locust_farmland.md"]),
    ("millipede_forest", "Millipede Forest", [], 0, 1, "far", "hard", None,
     "Logging and chitin armour.", ["docs/product/economy/zones/millipede_forest.md"]),
    ("spider_vale_west", "Spider Vale West", [], 0, 2, "edge", "extra hard", None,
     "Silk, agility, rare metals.", ["docs/product/economy/zones/spider_vale_west.md"]),
    ("spider_vale_east", "Spider Vale East", [], 0, 3, "edge", "hardest surface", None,
     "Silk, agility, rare metals; it finishes the surface.", ["docs/product/economy/zones/spider_vale_east.md"]),
    ("hilltop_meadow", "Hilltop Meadow", ["Meadow"], 1, 0, "middle", "medium", None,
     "Advanced beekeeping, and wasps kept as pest control.", ["docs/product/economy/zones/meadow.md"]),
    ("butterfly_fields", "Butterfly Fields", ["Butterfly Meadow", "butterfly_meadow_11", "butterfly_fields_11"], 1, 1, "middle", "medium", None,
     "Rare catches, night and glowing bugs, silk.",
     ["docs/product/economy/zones/butterfly_fields.md", "docs/product/zones/butterfly_meadow_11.md"]),
    ("scorpion_rocks", "Scorpion Rocks", [], 1, 2, "far", "hard", None,
     "Mining in daylight, deadly venom, heat.", ["docs/product/economy/zones/scorpion_rocks.md"]),
    ("deep_swamp", "Deep Swamp", [], 1, 3, "edge", "extra hard", None,
     "Diving, disease and poison, an apex predator.", ["docs/product/economy/zones/deep_swamp.md"]),
    ("bee_meadow", "Bee Meadow", [], 2, 0, "home", "easy", "bee_meadow_20",
     "Beekeeping; the fishing hamlet of Gullwash Landing is on its coast.",
     ["docs/product/economy/zones/bee_meadow.md", "docs/product/zones/bee_meadow_20.md"]),
    ("village", "Village", ["Starting Village", "Starting Village B", "the player's farm"], 2, 1, "home", "easy (start)", "village_21_B",
     "Home: shops, the Ecologist, your farm.",
     ["docs/product/economy/zones/village.md", "docs/product/zones/village_21_B.md"]),
    ("wasp_thicket", "Wasp Thicket", [], 2, 2, "middle", "medium", None,
     "The first real fights: venom and swarms.", ["docs/product/economy/zones/wasp_thicket.md"]),
    ("shallow_swamp", "Shallow Swamp", [], 2, 3, "far", "hard", None,
     "The water gear.", ["docs/product/economy/zones/shallow_swamp.md"]),
    ("ant_tunnels", "Ant Tunnels", ["Ant Colony – intro"], 3, 0, "home", "easy", "ant_tunnels_30",
     "Half outdoors: ant trails, the first tunnels.", ["docs/product/zones/ant_tunnels_30.md"]),
    ("mining_camp", "Mining Camp", ["Underground Passages", "the mine"], 3, 1, "home", "easy", "underground_passages_31",
     "Mining with light, tools and ore.",
     ["docs/product/economy/zones/underground_passages.md", "docs/product/zones/underground_passages_31.md"]),
    ("underground_river", "Underground River", [], 3, 2, "middle", "medium", None,
     "Cave fishing, pearls, a sunken ruin.", ["docs/product/economy/zones/underground_river.md"]),
    ("deadly_ants_outpost", "Deadly Ants outpost", [], 3, 3, "far", "hard", None,
     "Endgame ant warfare begins; fire resistance is the key.", ["docs/product/economy/zones/deadly_ants.md"]),
    ("ant_colony", "Ant Colony + Queen", ["Ant Colony"], 4, 0, "home", "medium", None,
     "The Colony Queen.", ["docs/product/economy/zones/ant_colony.md", "docs/product/zones/ant_colony_40.md"]),
    ("centipede_cavern", "Centipede Cavern", [], 4, 1, "middle", "medium", None,
     "Glowworm light, fast venom, crystals.",
     ["docs/product/economy/zones/centipede_cavern.md", "docs/product/zones/centipede_cavern_41.md"]),
    ("underground_river_deep", "Underground River, deep", ["the deep river", "deep river"], 4, 2, "far", "hard", None,
     "The deep river below the Underground River.", ["docs/product/economy/zones/underground_river.md"]),
    ("deadly_ants_core", "Deadly Ants core", [], 4, 3, "edge", "extra hard (hardest underground)", None,
     "Endgame ant warfare; the War Queen.", ["docs/product/economy/zones/deadly_ants.md"]),
]
LAYER = {0: "surface", 1: "surface", 2: "surface", 3: "underground", 4: "deep underground"}

# Bug family per roster id (lineup id without "lineup_").
FAMILY = {
    "house_fly": "flies", "horse_fly": "flies", "cave_fly": "flies", "decapitating_fly": "flies",
    "paper_wasp": "wasps and hornets", "yellowjacket": "wasps and hornets", "european_hornet": "wasps and hornets",
    "giant_hornet": "wasps and hornets", "tarantula_hawk": "wasps and hornets",
    "bumblebee": "bees", "honeybee": "bees", "killer_bee": "bees", "asian_honey_bee": "bees",
    "black_ants": "ants", "fire_ants": "ants",
    "stone_centipede": "centipedes", "tiger_centipede": "centipedes", "giant_centipede": "centipedes",
    "garden_millipede": "millipedes", "african_millipede": "millipedes", "dragon_millipede": "millipedes",
    "forest_scorpion": "scorpions", "fat_tailed_scorpion": "scorpions",
    "blue_dasher": "dragonflies", "emperor_dragonfly": "dragonflies", "dragonhunter": "dragonflies",
    "meadow_butterfly": "butterflies and moths", "monarch": "butterflies and moths",
    "purple_emperor": "butterflies and moths", "luna_moth": "butterflies and moths",
    "deaths_head": "butterflies and moths", "silk_moth": "butterflies and moths",
    "burying_beetle": "beetles", "cave_beetle": "beetles", "hercules_beetle": "beetles", "stag_beetle": "beetles",
    "colorado_beetle": "beetles", "bombardier": "beetles",
    "cave_spider": "spiders and harvestmen", "daddy_longlegs": "spiders and harvestmen",
    "wolf_spider": "spiders and harvestmen", "jumping_spider": "spiders and harvestmen",
    "wandering_spider": "spiders and harvestmen", "black_widow": "spiders and harvestmen",
    "goliath": "spiders and harvestmen", "huntsman": "spiders and harvestmen",
    "house_mosquito": "mosquitoes", "malaria_mosquito": "mosquitoes",
    "water_strider": "water life", "crayfish": "water life", "river_crab": "water life",
    "mantis": "mantises", "orchid_mantis": "mantises",
    "house_cricket": "crickets and locusts", "field_cricket": "crickets and locusts", "locust": "crickets and locusts",
    "firefly": "fireflies and glowworms", "glowworm": "fireflies and glowworms",
}


def S(zone, note=""):
    """Spawns and breeds in this zone (D53: its own spawn areas there)."""
    return {"zone": zone, "how": "spawns", "note": note}


def C(zone, frm, note=""):
    """Comes in from a neighbouring zone."""
    return {"zone": zone, "how": "comes_in", "from": frm, "note": note}


# The assistant's reading of §03's "where it lives" lines and §04's zone table (2026-10-03). All proposed.
BUG_ZONES = {
    "house_fly": [S("village", "anywhere with rot"), S("bee_meadow"), S("ant_tunnels", "proposed in §04 as prey"), S("wasp_thicket")],
    "horse_fly": [S("shallow_swamp", "the edges"), S("deep_swamp")],
    "cave_fly": [S("ant_colony", "the food stores and refuse heaps"), S("mining_camp"), S("centipede_cavern"), S("underground_river")],
    "decapitating_fly": [S("shallow_swamp", "over the fire ants' columns")],
    "paper_wasp": [S("village"), S("bee_meadow", "the edges"), S("hilltop_meadow", "kept as pest control")],
    "yellowjacket": [S("wasp_thicket")],
    "european_hornet": [S("wasp_thicket", "the ranger outpost's lights"), S("hilltop_meadow", "its top threat")],
    "giant_hornet": [S("millipede_forest")],
    "tarantula_hawk": [S("spider_vale_east")],
    "bumblebee": [S("bee_meadow"), S("hilltop_meadow")],
    "honeybee": [S("village", "hives"), S("bee_meadow", "wild hives and Maren's farm"), S("hilltop_meadow"),
                 C("butterfly_fields", ["village", "hilltop_meadow"], "wild bees foraging")],
    "killer_bee": [S("locust_farmland"), S("scorpion_rocks")],
    "asian_honey_bee": [S("millipede_forest", "the third hive bee (D83); also kept in players' hives")],
    "black_ants": [S("ant_tunnels"), S("ant_colony", "the queen; the colony spans both zones"),
                   C("bee_meadow", ["ant_tunnels"], "foraging"), C("mining_camp", ["ant_tunnels"], "foraging through the dirt tunnels (D21)")],
    "fire_ants": [S("deadly_ants_outpost", "the galleries"), S("deadly_ants_core", "the queens"),
                  C("shallow_swamp", ["deadly_ants_outpost"], "the foraging front breaks the surface: mounds, rafts, mating flights (D3, D9)")],
    "stone_centipede": [S("village", "the north-east woods' logs and stones"), S("ant_tunnels", "built there today"),
                        S("spider_vale_east", "proposed in §04: damp litter, as prey")],
    "tiger_centipede": [S("mining_camp", "D21's cave centipede"), S("ant_colony", "the seam"), S("centipede_cavern", "the upper halls")],
    "giant_centipede": [S("centipede_cavern", "the depths"), S("millipede_forest"), S("spider_vale_west")],
    "garden_millipede": [S("village", "the woods"), S("bee_meadow", "built there today"),
                         S("spider_vale_east", "proposed in §04: damp litter")],
    "african_millipede": [S("mining_camp", "D21's tougher cave millipede"), S("millipede_forest"), S("centipede_cavern"),
                          S("spider_vale_east", "proposed in §04, as prey")],
    "dragon_millipede": [S("millipede_forest", "deep in it"), S("centipede_cavern", "proposed in §04: D21's venomous millipede")],
    "forest_scorpion": [S("wasp_thicket", "under logs in the damp woods")],
    "fat_tailed_scorpion": [S("scorpion_rocks")],
    "blue_dasher": [S("village", "the west side's water"), S("bee_meadow", "the river"),
                    S("shallow_swamp", "proposed in §04"), S("deep_swamp", "proposed in §04")],
    "emperor_dragonfly": [S("butterfly_fields"), S("shallow_swamp"), S("deep_swamp"),
                          S("millipede_forest", "along its river (§04)")],
    "dragonhunter": [S("millipede_forest", "along its river"),
                     C("butterfly_fields", ["millipede_forest"], "ranging down the river")],
    "meadow_butterfly": [S("village", "the meadows"), S("bee_meadow"), S("butterfly_fields")],
    "monarch": [S("butterfly_fields"), S("shallow_swamp", "proposed in §04: swamp milkweed"),
                S("deep_swamp", "proposed in §04: swamp milkweed")],
    "purple_emperor": [S("wasp_thicket", "high in the oaks")],
    "luna_moth": [S("wasp_thicket"), S("butterfly_fields"), S("millipede_forest", "proposed in §04")],
    "deaths_head": [S("bee_meadow")],
    "silk_moth": [S("village", "kept on the player's farm, on a mulberry tree")],
    "burying_beetle": [S("village", "anywhere carcasses fall"), S("bee_meadow"), S("ant_tunnels")],
    "cave_beetle": [S("mining_camp"), S("centipede_cavern"), S("underground_river"), S("underground_river_deep")],
    "hercules_beetle": [S("millipede_forest", "its boss form")],
    "stag_beetle": [S("wasp_thicket", "the woods")],
    "colorado_beetle": [S("locust_farmland")],
    "bombardier": [S("hilltop_meadow", "under stones")],
    "cave_spider": [S("centipede_cavern", "and deeper (D21: not the Mining Camp); which deeper zones is open")],
    "daddy_longlegs": [S("mining_camp", "the caves"), S("centipede_cavern"), S("spider_vale_west"), S("spider_vale_east")],
    "wolf_spider": [S("spider_vale_west")],
    "jumping_spider": [S("butterfly_fields"), S("spider_vale_west")],
    "wandering_spider": [S("spider_vale_west")],
    "black_widow": [S("spider_vale_east")],
    "goliath": [S("spider_vale_east", "deep burrows in damp ground")],
    "huntsman": [S("spider_vale_east", "the caves")],
    "house_mosquito": [S("shallow_swamp")],
    "malaria_mosquito": [S("deep_swamp")],
    "water_strider": [S("village", "the lake"), S("shallow_swamp"), S("deep_swamp")],
    "crayfish": [S("village", "the lake"), S("shallow_swamp"), S("deep_swamp")],
    "river_crab": [S("underground_river"), S("underground_river_deep")],
    "mantis": [S("wasp_thicket", "the edges"), S("locust_farmland")],
    "orchid_mantis": [S("butterfly_fields")],
    "house_cricket": [S("village", "farmed on the player's farm"), S("locust_farmland", "the western town's farm store")],
    "field_cricket": [S("bee_meadow", "dry, sunny, short grass"), S("hilltop_meadow"),
                      S("scorpion_rocks", "proposed in §04, as prey"), S("spider_vale_west", "proposed in §04, as prey")],
    "firefly": [S("village", "the meadows at dusk"), S("bee_meadow", "built there today"), S("butterfly_fields", "at night")],
    "glowworm": [S("mining_camp", "D21, with the glowing mushrooms"), S("centipede_cavern"),
                 S("underground_river", "over the water"), S("underground_river_deep")],
    "locust": [S("locust_farmland", "swarms carry on into a neighbouring zone (which one is open)")],
}

# Bug-list rows (bug_table.jsonl) the automatic join can't place, linked by hand with the reason.
HAND_BUG_TABLE = {
    "bug_bee_honey": (["honeybee"], "its text also names the killer bee's species; it is the honeybee"),
    "bug_warrior_ant": (["black_ants", "fire_ants"], "the warrior caste of both ant species (D39, D79)"),
    "bug_mosquito": (["house_mosquito", "malaria_mosquito"], "now two species (the lineups)"),
    "bug_raid_centipede": (["tiger_centipede"], "renamed: now the tiger centipede"),
    "bug_scorpion": (["forest_scorpion", "fat_tailed_scorpion"], "now two species"),
    "bug_hornet_second": (["european_hornet"], "renamed: now the European hornet"),
    "bug_cricket": (["house_cricket", "field_cricket"], "now two species"),
    "bug_mantis": (["mantis", "orchid_mantis"], "now two species"),
    "bug_forest_centipede": (["giant_centipede"], "renamed: now the giant centipede"),
    "bug_armored_centipede": (["giant_centipede"], "renamed: now the giant centipede"),
    "bug_dragonflies_extra": (["emperor_dragonfly", "dragonhunter"], "the medium and deadly dragonflies"),
}
# §03 sheets the Latin-name join can't place by itself.
HAND_SHEET = {"killer_bee": "its text also names Apis mellifera (the honeybee's sheet); matched by hand"}
# Game species ids (species.json) -> roster ids.
SPECIES = {
    "fly_common": "house_fly", "butterfly_meadow": "meadow_butterfly", "wasp_common": "paper_wasp",
    "centipede_garden": "stone_centipede", "millipede": "garden_millipede", "beetle_carrion": "burying_beetle",
    "bee_honey": "honeybee", "dragonfly_blue": "blue_dasher", "firefly": "firefly", "ant_worker": "black_ants",
    "ant_scout": "black_ants", "wasp_soldier": "yellowjacket", "hornet_giant": "european_hornet",
    "centipede_tiger": "tiger_centipede", "centipede_giant": "giant_centipede",
}

BINOM = re.compile(r"\b([A-Z][a-z]+ [a-z]{3,})\b")


def jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def neighbours(row, col, grid):
    out = {}
    for d, (dr, dc) in {"north": (-1, 0), "south": (1, 0), "west": (0, -1), "east": (0, 1)}.items():
        out[d] = grid.get((row + dr, col + dc))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="overwrite existing registry files")
    a = ap.parse_args()
    zpath, bpath = DATA / "zones.jsonl", DATA / "bugs.jsonl"
    if (zpath.exists() or bpath.exists()) and not a.force:
        sys.exit("registry files exist; they are hand-edited now. Use --force only to deliberately re-seed.")

    grid = {(z[3], z[4]): z[0] for z in ZONES}
    zone_ids = {z[0] for z in ZONES}
    zrows = []
    for zid, name, aliases, row, col, ring, danger, built, purpose, sheets in ZONES:
        zrows.append({"id": zid, "name": name, "aliases": aliases, "row": row, "col": col, "layer": LAYER[row],
                      "ring": ring, "danger": danger, "built": built, "neighbours": neighbours(row, col, grid),
                      "purpose": purpose, "sheets": sheets, "layout": None})

    lineups = [r for r in jsonl(ROOT / "docs/gdd/bug_lineups.jsonl") if r["verdict"] != "cut"]
    bug_table = [r for r in jsonl(ROOT / "docs/gdd/bug_table.jsonl") if r["verdict"] != "cut"]
    sys.path.insert(0, str(ROOT / "tools/gdd"))
    import build_page
    sec = build_page.parse_section(build_page.GDD / "03_bestiary.md")
    sheets = [p for p in sec["proposals"] if int(p["id"][1:]) >= 9]

    problems = []
    brows = []
    by_id = {}
    for r in lineups:
        bid = r["id"].removeprefix("lineup_")
        latin_txt = r["change"].split("Real species")[-1] if "Real species" in r["change"] else r["change"]
        bs = set(BINOM.findall(latin_txt))
        hits = [p for p in sheets if bs & set(BINOM.findall(p["plain"]))]
        if bid == "killer_bee":
            hits = [p for p in sheets if p["plain"].startswith("Killer bee")]
        if len(hits) != 1:
            problems.append(f"{bid}: sheet match {[p['id'] for p in hits]}")
        m = re.search(r"Real species[^:]*: ([^.;]+)", r["change"])
        latin = sorted(bs)[0] if bs else ""
        row = {"id": bid, "name": r["name"], "names": [], "latin": latin, "species_text": m.group(1).strip() if m else "",
               "family": FAMILY.get(bid, ""), "lineup": r["id"], "bug_table": [],
               "species": sorted(k for k, v in SPECIES.items() if v == bid),
               "sheet": f"bug.{bid}", "sheet_p_now": hits[0]["id"] if len(hits) == 1 else None,
               "hand": ({"sheet": HAND_SHEET[bid]} if bid in HAND_SHEET else {}),
               "zones": [dict(z, proposed=True) for z in BUG_ZONES.get(bid, [])]}
        if not row["family"]:
            problems.append(f"{bid}: no family")
        if bid not in BUG_ZONES:
            problems.append(f"{bid}: no zones")
        for z in row["zones"]:
            if z["zone"] not in zone_ids:
                problems.append(f"{bid}: unknown zone {z['zone']}")
            for f in z.get("from", []):
                if f not in zone_ids:
                    problems.append(f"{bid}: unknown from-zone {f}")
        brows.append(row)
        by_id[bid] = row

    # Bug-list rows: join by Latin name or by the game species they name; else the hand table.
    for r in bug_table:
        targets, why = None, None
        if r["id"] in HAND_BUG_TABLE:
            targets, why = HAND_BUG_TABLE[r["id"]]
        else:
            bs = set(BINOM.findall(r["change"]))
            hits = [b for b in brows if b["species_text"] and bs & set(BINOM.findall(b["species_text"]))]
            gm = re.search(r"In the game \(([a-z_]+)\)", r["change"])
            if gm and gm.group(1) in SPECIES:
                hits = [by_id[SPECIES[gm.group(1)]]]
            if len(hits) == 1:
                targets = [hits[0]["id"]]
        if not targets:
            problems.append(f"bug_table {r['id']} ({r['name']}): not placed")
            continue
        for t in targets:
            by_id[t]["bug_table"].append(r["id"])
            if why:
                by_id[t]["hand"].setdefault("bug_table", []).append(f"{r['id']}: {why}")

    for b in brows:
        b.pop("species_text")
    if problems:
        print("PROBLEMS:\n  " + "\n  ".join(problems))
        sys.exit(1)
    DATA.mkdir(parents=True, exist_ok=True)
    with open(zpath, "w", encoding="utf-8") as f:
        for z in zrows:
            f.write(json.dumps(z, ensure_ascii=False) + "\n")
    with open(bpath, "w", encoding="utf-8") as f:
        for b in brows:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")
    print(f"wrote {len(zrows)} zones, {len(brows)} bugs; bug-list rows placed: {sum(len(b['bug_table']) for b in brows)}")


if __name__ == "__main__":
    main()
