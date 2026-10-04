#!/usr/bin/env python3
"""build_app.py — build the review app: one page for zones, bugs, items and the design document.

The plan is docs/plans/review-app.md. The page is published over the items page's address
(https://claude.ai/artifact/L9ftJfjRfcFD3yAB66qenD) so every stored mark carries over; never publish it without the
procedure in that plan (export, rehearse, compare).

  python3 tools/gdd/build_app.py              # -> tools/gdd/_build/review_app.html + review_app_report.txt
  python3 tools/gdd/build_app.py --test-mock  # same page with the misbehaving fake storage (tools/gdd/tests/)

Inputs: docs/gdd/data/{zones,bugs,phrases}.jsonl (the registries), docs/gdd/*.md (the design sections, parsed by
build_page.py), docs/gdd/{item_table,bug_table,bug_lineups}.jsonl (the rows the owner marks, read by
build_items_page.py), the saved built zones in nakama/data/zones/, the entity data (object categories), and
docs/gdd/explain/*.md (explanation pages). The builder refuses to write the page when the data is inconsistent
(every problem listed); differences between the documents about where bugs live are NOT failures — they are shown
to the owner in the app.

Storage (unchanged for marks): marks/<group>/items/<row id>; new: notes/<kind>/items/<id>, signoff/<kind>/items/<id>.
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GDD = ROOT / "docs/gdd"
REG = GDD / "data"
APP = ROOT / "tools/gdd/app"
OUT_DIR = ROOT / "tools/gdd/_build"
ZONES_DIR = ROOT / "nakama/data/zones"
sys.path.insert(0, str(ROOT / "tools/gdd"))
import build_page as bp  # noqa: E402
import build_items_page as bi  # noqa: E402

# The mark groups the page has ever stored under. Marks live at marks/<group>/items/<id>; dropping a group from the
# page would hide its stored marks, so the builder fails if GROUPS ever loses one of these.
STORED_GROUPS = ["bugs", "bug_ideas", "tools", "weapons", "armour", "accessories", "potions", "meals", "seeds_crops",
                 "plants", "materials", "ores", "stations", "furniture", "decoration", "lighting", "storage",
                 "structures", "blocks", "beekeeping", "natural", "npcs", "other"]
NOTE_KINDS = ["zone", "bug", "gdd", "section", "system"]
SIGNOFF_KINDS = ["zone", "bug", "section", "system"]
RINGS = ["home", "middle", "far", "edge"]
FAMILY_ORDER = ["flies", "bees", "wasps and hornets", "ants", "butterflies and moths", "centipedes", "millipedes",
                "spiders and harvestmen", "beetles", "dragonflies", "scorpions", "mantises", "crickets and locusts",
                "fireflies and glowworms", "mosquitoes", "water life"]
DOC_ID = re.compile(r"^[A-Za-z0-9_.~:@+-]{1,200}$")

# Map colours (light theme; the page derives dark ones). Ground from tools/world/view_world.py GROUND_COLORS.
GROUND = {"grass": "#aad28c", "dirt": "#8b7765", "stone_path": "#a9a9a9", "water_shallow": "#87cefa",
          "water_deep": "#4169e1", "mud": "#654321", "sand": "#eed6af", "wood_floor": "#a0785a",
          "stone_floor": "#808080", "cave_floor": "#3c3c3c", "garden_plot": "#593c1f", "bridge_wood": "#8a5a2b"}
CATEGORY = {"natural": "#3f6b2a", "flora": "#5c8a3a", "crop": "#9bbf3a", "structure": "#5a4636", "block": "#6e5a48",
            "ore": "#c9a227", "decoration": "#b5527a", "furniture": "#8e5b3b", "crafting": "#7a4fa3",
            "lighting": "#f2c94c", "storage": "#a86b32", "beekeeping": "#e0a020", "other": "#d04ad0"}


class Problems:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def jsonl(path, P):
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            P.err(f"{path.name} line {n}: not JSON ({e})")
    return rows


def ver(obj):
    """A short fingerprint of what the owner sees for one thing: an approval stores it, so the app can say
    'approved, but changed since'."""
    return hashlib.sha1(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:8]


def norm(s):
    s = s.lower().replace("’", "'").replace("'s", "s").replace("'", "")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return " ".join(s.split())


def plural_forms(name):
    out = {name}
    if name.endswith("fly"):
        out.add(name[:-1] + "ies")
    elif name.endswith("y") and not name.endswith("ey"):
        out.add(name[:-1] + "ies")
    elif name.endswith(("s", "x", "sh", "ch")):
        out.add(name + "es")
    else:
        out.add(name + "s")
    return out


# ------------------------------------------------------------------ registries

def load_registry(P, sections):
    zones = jsonl(REG / "zones.jsonl", P)
    bugs = jsonl(REG / "bugs.jsonl", P)
    phrases = jsonl(REG / "phrases.jsonl", P) if (REG / "phrases.jsonl").exists() else []
    zid = {z["id"]: z for z in zones}
    if len(zones) != 20:
        P.err(f"zones.jsonl: {len(zones)} zones, expected 20")
    if len(zid) != len(zones):
        P.err("zones.jsonl: duplicate zone ids")
    seen_sq = {}
    for z in zones:
        for f in ("id", "name", "row", "col", "ring", "neighbours", "purpose"):
            if f not in z:
                P.err(f"zone {z.get('id')}: missing {f}")
        if not DOC_ID.match(z.get("id", "")):
            P.err(f"zone id {z.get('id')!r} can't be a storage key")
        sq = (z.get("row"), z.get("col"))
        if sq in seen_sq:
            P.err(f"zones {seen_sq[sq]} and {z['id']} share grid square {sq}")
        seen_sq[sq] = z["id"]
        if z.get("ring") not in RINGS:
            P.err(f"zone {z['id']}: ring {z.get('ring')!r}")
    opposite = {"north": "south", "south": "north", "east": "west", "west": "east"}
    step = {"north": (-1, 0), "south": (1, 0), "west": (0, -1), "east": (0, 1)}
    for z in zones:
        for d, n in (z.get("neighbours") or {}).items():
            if n is None:
                continue
            if n not in zid:
                P.err(f"zone {z['id']}: {d} neighbour {n!r} unknown")
                continue
            o = zid[n]
            if (o["row"], o["col"]) != (z["row"] + step[d][0], z["col"] + step[d][1]):
                P.err(f"zone {z['id']}: {d} neighbour {n} is not next door")
            if (o.get("neighbours") or {}).get(opposite[d]) != z["id"]:
                P.err(f"zone {z['id']} -> {n}: the link isn't returned ({opposite[d]})")
        if z.get("built"):
            zj = ZONES_DIR / z["built"] / "zone.json"
            if not zj.exists():
                P.err(f"zone {z['id']}: built zone {z['built']} has no zone.json")
            else:
                b = json.loads(zj.read_text())
                if (b.get("row"), b.get("col")) != (z["row"], z["col"]):
                    P.err(f"zone {z['id']}: built {z['built']} sits at {(b.get('row'), b.get('col'))}, registry says {(z['row'], z['col'])}")

    lineups = {r["id"]: r for r in jsonl(GDD / "bug_lineups.jsonl", P)}
    bug_table = {r["id"]: r for r in jsonl(GDD / "bug_table.jsonl", P)}
    species = json.loads((ROOT / "nakama/data/species.json").read_text())
    sheet_keys = {p.get("key"): p for s in sections if s["id"] == "03" for p in s["proposals"]
                  if (p.get("key") or "").startswith("bug.")}
    bid = {}
    for b in bugs:
        if b["id"] in bid:
            P.err(f"bugs.jsonl: duplicate id {b['id']}")
        bid[b["id"]] = b
        if not DOC_ID.match(b["id"]):
            P.err(f"bug id {b['id']!r} can't be a storage key")
        if b.get("approved") is not None or b.get("signed_off") is not None:
            P.err(f"bug {b['id']}: approvals live in the app's storage, never in the data")
        if b.get("family") not in FAMILY_ORDER:
            P.err(f"bug {b['id']}: family {b.get('family')!r} not in the family order")
        if b.get("lineup") not in lineups:
            P.err(f"bug {b['id']}: lineup row {b.get('lineup')!r} unknown")
        elif lineups[b["lineup"]]["verdict"] == "cut":
            P.err(f"bug {b['id']}: its lineup row is cut")
        for t in b.get("bug_table", []):
            if t not in bug_table:
                P.err(f"bug {b['id']}: bug-list row {t!r} unknown")
        for s in b.get("species", []):
            if s not in species:
                P.err(f"bug {b['id']}: species {s!r} not in species.json")
        if b.get("sheet") not in sheet_keys:
            P.err(f"bug {b['id']}: §03 has no sheet keyed {b.get('sheet')!r}")
        if not b.get("zones") and not b.get("zones_note"):
            P.err(f"bug {b['id']}: no zone, and no note saying it waits for its zone's design")
        zs = set()
        for e in b.get("zones", []):
            if e.get("zone") not in zid:
                P.err(f"bug {b['id']}: unknown zone {e.get('zone')!r}")
                continue
            if e["zone"] in zs:
                P.err(f"bug {b['id']}: zone {e['zone']} listed twice")
            zs.add(e["zone"])
            if e.get("how") not in ("spawns", "comes_in"):
                P.err(f"bug {b['id']} in {e['zone']}: how {e.get('how')!r}")
            if e.get("how") == "comes_in":
                nb = set((zid[e["zone"]].get("neighbours") or {}).values())
                for f in e.get("from", []):
                    if f not in nb:
                        P.err(f"bug {b['id']} comes into {e['zone']} from {f}, which isn't a neighbour")
                if not e.get("from"):
                    P.err(f"bug {b['id']} comes into {e['zone']} from nowhere")
        if b.get("zones") and not any(e.get("how") == "spawns" for e in b["zones"]):
            P.err(f"bug {b['id']}: it spawns nowhere (D53: every bug spawns in its own areas somewhere)")
    # accounting: every roster row, kept bug-list row, species and §03 bug sheet is placed
    roster = [k for k, r in lineups.items() if r["verdict"] != "cut"]
    used = Counter(b.get("lineup") for b in bugs)
    for k in roster:
        if used[k] != 1:
            P.err(f"accounting: lineup row {k} is used by {used[k]} bugs (expected exactly 1)")
    used_bt = Counter(t for b in bugs for t in b.get("bug_table", []))
    for k, r in bug_table.items():
        if r["verdict"] != "cut" and not used_bt[k]:
            P.err(f"accounting: kept bug-list row {k} belongs to no bug")
    used_sp = Counter(s for b in bugs for s in b.get("species", []))
    for k in species:
        if used_sp[k] != 1:
            P.err(f"accounting: species {k} belongs to {used_sp[k]} bugs (expected exactly 1)")
    used_sh = Counter(b.get("sheet") for b in bugs)
    for k in sheet_keys:
        if used_sh[k] != 1:
            P.err(f"accounting: §03 sheet {k} belongs to {used_sh[k]} bugs (expected exactly 1)")
    acct = {"lineup rows (roster)": len(roster), "kept bug-list rows": sum(1 for r in bug_table.values() if r["verdict"] != "cut"),
            "game species": len(species), "§03 bug sheets": len(sheet_keys), "bugs": len(bugs), "zones": len(zones)}
    return zones, bugs, phrases, lineups, bug_table, species, sheet_keys, acct


# ------------------------------------------------------------------ built zones -> maps

def entity_categories():
    cats = {}
    for f in ("occupants", "placeables", "items", "crops"):
        p = ROOT / f"nakama/data/entities/{f}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        for k, v in (d.items() if isinstance(d, dict) else []):
            if isinstance(v, dict) and k not in cats:
                cats[k] = v.get("category") or ("crop" if f == "crops" else "other")
    return cats


def ground_color(tile):
    if tile in GROUND:
        return GROUND[tile]
    base = re.sub(r"_d_(ne|nw|se|sw)$", "", tile)
    if base in GROUND:
        return GROUND[base]
    if tile.startswith("dirt_path"):
        return GROUND["dirt"]
    return None


def rle(row):
    out, prev, n = [], None, 0
    for v in row:
        if v == prev:
            n += 1
        else:
            if prev is not None:
                out.append(f"{prev}*{n}" if n > 1 else str(prev))
            prev, n = v, 1
    if prev is not None:
        out.append(f"{prev}*{n}" if n > 1 else str(prev))
    return ",".join(out)


def unrle(s):
    out = []
    for part in s.split(","):
        if "*" in part:
            v, n = part.split("*")
            out += [int(v)] * int(n)
        else:
            out.append(int(part))
    return out


def built_world(P):
    """The built zones, found by walking neighbours from the real village (not by listing folders, which also holds
    labs, tests and bench copies)."""
    seen, todo = [], ["village_21_B"]
    while todo:
        z = todo.pop(0)
        if z in seen:
            continue
        zj = ZONES_DIR / z / "zone.json"
        if not zj.exists():
            P.err(f"built world: {z} has no zone.json")
            continue
        seen.append(z)
        todo += [n for n in (json.loads(zj.read_text()).get("neighbors") or {}).values() if n]
    return seen


def encode_zone_map(built, cats, item_ids, P, placements):
    zj = json.loads((ZONES_DIR / built / "zone.json").read_text())
    w, h = int(zj.get("width", 256)), int(zj.get("height", 256))
    ground = [[None] * w for _ in range(h)]
    things = [[None] * w for _ in range(h)]
    anchors = Counter()
    for cf in sorted((ZONES_DIR / built).glob("chunk_*.json")):
        c = json.loads(cf.read_text())
        cx, cy = c["chunk_x"], c["chunk_y"]
        for ly, row in enumerate(c["ground"]):
            for lx, t in enumerate(row):
                x, y = cx * 32 + lx, cy * 32 + ly
                if 0 <= x < w and 0 <= y < h:
                    ground[y][x] = t
        for ly, row in enumerate(c.get("occupants") or []):
            for lx, o in enumerate(row):
                if not o:
                    continue
                x, y = cx * 32 + lx, cy * 32 + ly
                if 0 <= x < w and 0 <= y < h:
                    things[y][x] = o["id"]
                    if o.get("anchor"):
                        anchors[o["id"]] += 1
    missing = sum(1 for y in range(h) for x in range(w) if ground[y][x] is None)
    if missing:
        P.err(f"map {built}: {missing} cells have no ground (missing chunks?)")
    gpal = sorted({t for r in ground for t in r if t})
    tpal = [None] + sorted({t for r in things for t in r if t})
    for t in gpal:
        if not ground_color(t):
            P.err(f"map {built}: ground tile {t!r} has no colour")
    thing_info = {}
    for t in tpal[1:]:
        cat = cats.get(t)
        if cat is None:
            P.err(f"map {built}: placed object {t!r} isn't in the entity data")
            cat = "other"
        if t not in item_ids:
            P.warn(f"map {built}: placed object {t!r} has no item row")
        thing_info[t] = {"cat": cat if cat in CATEGORY else "other"}
    gi = {t: i for i, t in enumerate(gpal)}
    ti = {t: i for i, t in enumerate(tpal)}
    g_rows = [rle([gi[t] for t in ground[y]]) for y in range(h)]
    t_rows = [rle([ti[t] for t in things[y]]) for y in range(h)]
    # round trip: decode and compare
    for y in range(h):
        if [gpal[i] for i in unrle(g_rows[y])] != ground[y] or [tpal[i] for i in unrle(t_rows[y])] != things[y]:
            P.err(f"map {built}: run-length round trip differs on row {y}")
            break
    for t, n in anchors.items():
        placements[t][built] += n
    areas = []
    for a in (zj.get("bug_spawning") or {}).get("spawn_areas", []):
        if a.get("type", "circle") == "circle":
            areas.append({"id": a.get("id", ""), "species": a.get("species", []), "x": a.get("cx"), "y": a.get("cy"),
                          "r": a.get("radius")})
            if not (0 <= a.get("cx", -1) < w and 0 <= a.get("cy", -1) < h):
                P.err(f"map {built}: spawn area {a.get('id')} lies outside the zone")
    return {"built": built, "w": w, "h": h, "y_up": True, "ground_palette": gpal,
            "ground_colors": [ground_color(t) for t in gpal], "ground_rle": g_rows,
            "thing_palette": tpal, "thing_rle": t_rows, "things": thing_info,
            "spawn_areas": areas, "spawn_point": zj.get("spawn_point"), "caps": sorted((zj.get("bug_spawning") or {}).get("species_caps", {}))}


def north_up_probe(m, P):
    """The village's big lake must lie in the south-west quarter (high y = north; CLAUDE.md's sanity check)."""
    deep = m["ground_palette"].index("water_deep") if "water_deep" in m["ground_palette"] else None
    if deep is None:
        P.err("north-up probe: the village has no deep water")
        return None
    xs, ys, n = 0, 0, 0
    for y, r in enumerate(m["ground_rle"]):
        for x, v in enumerate(unrle(r)):
            if v == deep:
                xs, ys, n = xs + x, ys + y, n + 1
    cx, cy = xs / n, ys / n
    if not (cx < m["w"] / 2 and cy < m["h"] / 2):
        P.err(f"north-up probe: the village's deep water centres at ({cx:.0f},{cy:.0f}), not in the south-west")
    return {"x": round(cx), "y": round(cy), "tile": "water_deep", "expect": "south-west"}


# ------------------------------------------------------------------ where bugs live: the documents compared

def split_top(s):
    """Split on commas/semicolons that aren't inside brackets."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch in ",;" and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]


def name_index(bugs, lineups):
    idx = {}
    for b in bugs:
        names = set(b.get("names") or [])
        nm = b["name"]
        names.add(re.sub(r"\s*\(.*?\)\s*", " ", nm).strip())
        for p in re.findall(r"\(([^)]*)\)", nm):
            names.add(re.sub(r"^the ", "", p.strip()))
        for n in list(names):
            for f in plural_forms(norm(n)):
                if f:
                    idx.setdefault(f, set()).add(b["id"])
    return idx


def match_phrase(text, idx, phrases):
    t = norm(re.sub(r"\(.*?\)", " ", text))
    found = set()
    rest = f" {t} "
    for key in sorted(idx, key=len, reverse=True):
        if f" {key} " in rest:
            found |= idx[key]
            rest = rest.replace(f" {key} ", " ")
    for p in phrases:
        k = norm(p["phrase"])
        if k and f" {k} " in rest:
            found |= set(p.get("ids", []))
            rest = rest.replace(f" {k} ", " ")
    return found, " ".join(rest.split())


def compare_where(zones, bugs, lineups, phrases, maps, species_to_bug, P):
    zid = {z["id"]: z for z in zones}
    zname = {}
    for z in zones:
        for n in [z["name"]] + z.get("aliases", []):
            zname[norm(n)] = z["id"]
    idx = name_index(bugs, lineups)
    s04 = defaultdict(set)
    unmatched = []
    text = (GDD / "04_ecology.md").read_text(encoding="utf-8")
    m = re.search(r"\n\| Ring \| Zone \|[^\n]*\n\|[-| ]+\|\n((?:\|[^\n]*\n)+)", text)
    if not m:
        P.warn("§04: zone table not found; documents not compared")
    else:
        for line in m.group(1).strip().split("\n"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 5:
                continue
            z = zname.get(norm(cells[1]))
            if not z:
                P.warn(f"§04 table: zone {cells[1]!r} not in the registry")
                continue
            for cell in (cells[2], cells[4]):
                for part in split_top(cell):
                    if norm(part) in ("", "-"):
                        continue
                    ids, rest = match_phrase(part, idx, phrases)
                    s04[z] |= ids
                    if not ids:
                        unmatched.append(f"§04 {cells[1]}: {part}")
    built_has = defaultdict(set)
    built_ids = {z["built"]: z["id"] for z in zones if z.get("built")}
    for b, mp in maps.items():
        z = built_ids.get(b)
        if not z:
            continue
        for sp in mp["caps"]:
            if sp in species_to_bug:
                built_has[z].add(species_to_bug[sp])
    reg = {(e["zone"], b["id"]): e["how"] for b in bugs for e in b.get("zones", [])}
    diffs = []
    for z in zones:
        all_bugs = {b for (zz, b) in reg if zz == z["id"]} | s04[z["id"]] | built_has[z["id"]]
        for bgid in sorted(all_bugs):
            r = reg.get((z["id"], bgid), "absent")
            in04 = bgid in s04[z["id"]]
            built = ("spawns" if bgid in built_has[z["id"]] else "absent") if z.get("built") else "n/a"
            # A difference: the registry lacks a bug another source has here, or §04 doesn't mention a bug the
            # registry lists. (A planned bug not yet in the built game isn't a difference: most bugs aren't built.)
            if r == "absent" or not in04:
                diffs.append({"zone": z["id"], "bug": bgid, "registry": r, "s04": in04, "built": built})
    return diffs, unmatched


# ------------------------------------------------------------------ page

def explain_pages(P):
    out = []
    d = GDD / "explain"
    for f in sorted(d.glob("*.md")) if d.exists() else []:
        lines = f.read_text(encoding="utf-8").split("\n")
        if not lines or not lines[0].startswith("# "):
            P.err(f"explain/{f.name}: needs a '# Title' first line")
            continue
        out.append({"slug": f.stem, "title": bp.inline(lines[0][2:].strip()), "plain": bp.plain(lines[0][2:]),
                    "html": bp.blocks(lines[1:])})
    return out


def build(test_mock=False):
    P = Problems()
    names = bp.review_order()
    sections = []
    for name in names:
        try:
            sections.append(bp.parse_section(GDD / name))
        except bp.Malformed as e:
            P.err(f"GDD: {e}")
    keys = Counter()
    for s in sections:
        for it in s["proposals"] + s["questions"]:
            if not it.get("key"):
                P.err(f"GDD {s['file']} {it['id']}: no stable key (run tools/gdd/assign_keys.py)")
            else:
                keys[it["key"]] += 1
                if not DOC_ID.match(it["key"]):
                    P.err(f"GDD key {it['key']!r} can't be a storage key")
    for k, n in keys.items():
        if n > 1:
            P.err(f"GDD key {k} is used {n} times")

    items, item_problems = bi.load()
    for p in item_problems:
        P.err(f"items: {p}")
    groups = [g for g in bi.GROUPS]
    for g in STORED_GROUPS:
        if g not in dict(groups):
            P.err(f"items: GROUPS lost {g!r}, which holds stored marks")
    item_ids = {it["id"] for it in items}

    zones, bugs, phrases, lineups, bug_table, species, sheet_keys, acct = load_registry(P, sections)
    species_to_bug = {s: b["id"] for b in bugs for s in b.get("species", [])}

    cats = entity_categories()
    placements = defaultdict(Counter)
    maps, probe = {}, None
    world = built_world(P)
    built_reg = {z["built"] for z in zones if z.get("built")}
    if set(world) != built_reg:
        P.err(f"the built world {sorted(world)} differs from the registry's built zones {sorted(built_reg)}")
    for b in world:
        maps[b] = encode_zone_map(b, cats, item_ids, P, placements)
        zj = json.loads((ZONES_DIR / b / "zone.json").read_text())
        reg_z = next((z for z in zones if z.get("built") == b), None)
        for d, n in (zj.get("neighbors") or {}).items():
            other = next((z for z in zones if z.get("built") == n), None)
            if reg_z and other and (reg_z.get("neighbours") or {}).get(d) != other["id"]:
                P.err(f"built {b}: its {d} link to {n} disagrees with the registry")
    if "village_21_B" in maps:
        probe = north_up_probe(maps["village_21_B"], P)
        maps["village_21_B"]["probe"] = probe

    diffs, unmatched = compare_where(zones, bugs, lineups, phrases, maps, species_to_bug, P)
    short = {b["id"]: re.sub(r"\s*\(.*?\)", "", b["name"]).strip() for b in bugs}
    for mp in maps.values():
        for a in mp["spawn_areas"]:
            a["bugs"] = sorted({short[species_to_bug[s]] for s in a["species"] if s in species_to_bug})

    # ---------------- page data
    built_to_zone = {z["built"]: z["id"] for z in zones if z.get("built")}
    zone_out = []
    for z in zones:
        spawn = [{"id": b["id"], "note": e.get("note", ""), "proposed": e.get("proposed", False)}
                 for b in bugs for e in b.get("zones", []) if e["zone"] == z["id"] and e["how"] == "spawns"]
        come = [{"id": b["id"], "from": e.get("from", []), "note": e.get("note", ""), "proposed": e.get("proposed", False)}
                for b in bugs for e in b.get("zones", []) if e["zone"] == z["id"] and e["how"] == "comes_in"]
        placed = []
        if z.get("built"):
            for t, per in placements.items():
                if per.get(z["built"]):
                    placed.append({"id": t, "n": per[z["built"]], "cat": cats.get(t, "other")})
            placed.sort(key=lambda p: (p["cat"], -p["n"], p["id"]))
        zo = {k: z.get(k) for k in ("id", "name", "aliases", "row", "col", "layer", "ring", "danger", "built",
                                     "neighbours", "purpose", "sheets", "layout")}
        zo.update({"spawn": spawn, "comes": come, "placed": placed,
                   "diffs": [d for d in diffs if d["zone"] == z["id"]]})
        zo["ver_map"] = ver({"map": z.get("built") and maps[z["built"]]["ground_rle"][::32], "layout": z.get("layout")})
        zo["ver_plan"] = ver({"purpose": z.get("purpose"), "spawn": spawn, "comes": come})
        zone_out.append(zo)
    bug_out = []
    for b in bugs:
        sh = sheet_keys.get(b["sheet"], {})
        bo = {k: b.get(k) for k in ("id", "name", "latin", "family", "lineup", "bug_table", "species", "zones", "hand")}
        bo["sheet"] = {"key": b["sheet"], "p": sh.get("id"), "title": sh.get("title", ""), "html": sh.get("html", ""),
                       "lenses": sh.get("lenses", "")}
        bo["diffs"] = [d for d in diffs if d["bug"] == b["id"]]
        bo["ver"] = ver({"sheet": sh.get("html", ""), "zones": b.get("zones")})
        bug_out.append(bo)
    for it in items:
        per = placements.get(it["id"])
        if per:
            it["placed"] = {built_to_zone[k]: v for k, v in per.items() if k in built_to_zone}
    sec_out = []
    for s in sections:
        so = dict(s)
        so["ver"] = ver({"p": [(p.get("key"), p["html"]) for p in s["proposals"]],
                         "q": [(q.get("key"), q["context"]) for q in s["questions"]], "decided": s["decided"]})
        sec_out.append(so)
    data = {
        "version": date.today().isoformat(), "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "groups": groups, "stored_groups": STORED_GROUPS, "note_kinds": NOTE_KINDS, "signoff_kinds": SIGNOFF_KINDS,
        "items": items, "zones": zone_out, "bugs": bug_out, "families": FAMILY_ORDER, "rings": RINGS,
        "sections": sec_out, "explain": explain_pages(P), "maps": {built_to_zone[b]: m for b, m in maps.items()},
        "colors": {"category": CATEGORY}, "unmatched": unmatched, "accounting": acct,
    }

    # ---------------- page assembly and output checks
    shell = (APP / "shell.html").read_text(encoding="utf-8")
    parts = {"/*__CSS__*/": (APP / "app.css").read_text(encoding="utf-8"),
             "/*__SAVE__*/": (APP / "save.js").read_text(encoding="utf-8"),
             "/*__MAPS__*/": (APP / "maps.js").read_text(encoding="utf-8"),
             "/*__VIEWS__*/": (APP / "views.js").read_text(encoding="utf-8"),
             "/*__MOCK__*/": (ROOT / "tools/gdd/tests/mock_db.js").read_text(encoding="utf-8") if test_mock else ""}
    for slot, code in parts.items():
        if slot not in shell:
            P.err(f"shell.html has no {slot} slot")
        shell = shell.replace(slot, code)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    if "/*__DATA__*/null" not in shell:
        P.err("shell.html has no data slot")
    html = shell.replace("/*__DATA__*/null", payload)
    head = html[:8192]
    if "<title>" not in head:
        P.err("the <title> must be in the first 8 KB")
    for tag in ("<html", "<head", "<body"):
        if re.search(tag + r"[\s>]", html[:20000], re.I):
            P.err(f"the page must not contain its own {tag}> (the viewer adds the skeleton)")
    for src in re.findall(r"<script[^>]+src=\"([^\"]+)\"", html):
        if not src.startswith(("https://cdnjs.cloudflare.com/", "https://cdn.jsdelivr.net/npm/", "https://unpkg.com/")):
            P.err(f"script from a host the viewer blocks: {src}")
    size = len(html.encode("utf-8"))
    if size > 15 * 1024 * 1024:
        P.err(f"page is {size // 1024} KB, over the 15 MB limit")
    elif size > 3 * 1024 * 1024:
        P.warn(f"page is {size // 1024} KB (over 3 MB)")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / ("review_app_test.html" if test_mock else "review_app.html")
    report = OUT_DIR / "review_app_report.txt"
    lines = [f"review app build {data['built_at']} -> {out.name} ({size // 1024} KB)", "", "ACCOUNTING"]
    lines += [f"  {k}: {v}" for k, v in acct.items()]
    lines += ["", f"WHERE BUGS LIVE: {len(diffs)} differences between the registry, §04 and the game as built"]
    lines += [f"  {d['zone']:24} {d['bug']:20} registry={d['registry']:9} §04={'yes' if d['s04'] else 'no ':3} built={d['built']}" for d in diffs]
    lines += ["", f"WORDS IN §04 THE BUILDER COULDN'T PLACE: {len(unmatched)}"] + [f"  {u}" for u in unmatched]
    lines += ["", f"WARNINGS: {len(P.warnings)}"] + [f"  {w}" for w in P.warnings]
    lines += ["", f"ERRORS: {len(P.errors)}"] + [f"  {e}" for e in P.errors]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if P.errors:
        print(f"REFUSED: {len(P.errors)} problem(s) — see {report}")
        for e in P.errors[:30]:
            print("  " + e)
        return 1
    out.write_text(html, encoding="utf-8")
    print(f"built {out} ({size // 1024} KB): {len(zones)} zones, {len(bugs)} bugs, {len(items)} rows, "
          f"{len(sections)} sections, {len(maps)} maps, {len(diffs)} where-differences, {len(unmatched)} unplaced words, "
          f"{len(P.warnings)} warnings")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-mock", action="store_true")
    a = ap.parse_args()
    return build(a.test_mock)


if __name__ == "__main__":
    sys.exit(main())
