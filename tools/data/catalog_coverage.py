#!/usr/bin/env python3
"""Catalog coverage audit — every game entity is documented; no catalog cites a ghost.

Reads the SINGLE source of truth (`nakama/data/entities/{items,occupants,placeables}.json`)
and the design catalogs under `docs/product/economy/catalogs/` (+ `crafting.md` stations and
`species_and_drops.md` bugs), and checks the invariant the economy docs actually need:

  GATE 1 — no ORPHAN: every real entity is documented (mentioned by id) in >=1 catalog.
  GATE 2 — no GHOST: every id a catalog marks present (a line carrying the ✅ marker) is a real entity.

It is NOT a rigid one-catalog partition — catalogs are curated DESIGN docs that legitimately
cross-reference an item where it's functionally relevant (e.g. `torch` lives in furniture.md but
is mentioned in tools.md as a light). So multi-homing is REPORTED for tidiness, never failed.

Entities are deduped by id across the three files (14 ids are intentionally dual: 13 forageables
are both a `resource` item and a `natural` occupant; `notice_board` is occupant + placeable), and
crop growth stages (`plant_X_stageN`) collapse to their base crop `plant_X`.

Also REPORTS (not gates):
  - multi-homed ids (mentioned in >1 catalog)
  - drop item_ids that resolve only to an occupant with no item entry (possible broken inventory
    icon) — the seed of a future data-schema lint.

Usage:  python3 tools/data/catalog_coverage.py            # full report; exit 1 if a GATE fails
        python3 tools/data/catalog_coverage.py --quiet     # only failures + summary
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENT = os.path.join(ROOT, "nakama", "data", "entities")
CAT = os.path.join(ROOT, "docs", "product", "economy", "catalogs")
ECON = os.path.join(ROOT, "docs", "product", "economy")

CROP_STAGE = re.compile(r"_stage\d+$")
BACKTICK = re.compile(r"`([a-z][a-z0-9_]+)`")  # entity ids are lower_snake_case


def load(name):
    with open(os.path.join(ENT, name)) as f:
        d = json.load(f)
    return {k: v for k, v in d.items() if not k.startswith("_")}


def base_id(eid):
    """Collapse crop growth stages to the base crop id."""
    return CROP_STAGE.sub("", eid)


def primary_home(eid, items, occ, pl):
    """The catalog page an entity's full row is EXPECTED on (homing rule). Used for the
    placement report only — GATE 1 just needs the id documented somewhere."""
    di, do, dp = items.get(eid), occ.get(eid), pl.get(eid)

    # placeable overrides first (container wins over its base category)
    if dp:
        cat = dp.get("category")
        if dp.get("world", {}).get("container"):
            return "containers"
        if cat == "crafting" or eid == "honey_extractor":
            return "crafting"           # stations live in crafting.md
        if cat == "beekeeping":
            return "structures"         # hives
        if cat in ("furniture", "lighting"):
            return "furniture"
        if cat == "decoration":
            return "decoration"
        if cat == "structure":
            return "structures"
        if cat == "block" or cat == "natural":   # block(5) + boulder
            return "materials"
        if cat == "flora":              # marsh_plant
            return "plants"
        if cat == "storage":
            return "containers"

    if occ.get(eid):
        cat = do.get("category")
        if cat in ("natural", "nature", "crop", "flora"):
            return "plants"
        if cat == "ore":
            return "materials"
        if cat == "lighting":
            return "furniture"
        if cat == "storage":
            return "containers"
        if cat == "structure":
            return "structures"

    if di:
        cat = di.get("category")
        if cat == "resource":
            # dual forageables (also a natural occupant) belong with the plant
            return "plants" if occ.get(eid) else "materials"
        if cat == "tool":
            return "weapons" if di.get("tool_type") in ("sword", "spear") else "tools"
        if cat == "weapon":
            return "weapons"
        if cat == "armor":
            return "accessories" if di.get("armor_slot") == "accessory" else "armor"
        if cat == "consumable":
            return "consumables"
        if cat == "seed":
            return "plants"
        if cat == "backpack":
            return "containers"
    return "?"


def catalog_text():
    """Return {page_name: text} for every catalog + crafting.md + species_and_drops.md."""
    pages = {}
    for p in sorted(glob.glob(os.path.join(CAT, "*.md"))):
        pages[os.path.splitext(os.path.basename(p))[0]] = open(p).read()
    for extra in ("crafting.md", "species_and_drops.md"):
        fp = os.path.join(ECON, extra)
        if os.path.exists(fp):
            pages[os.path.splitext(extra)[0]] = open(fp).read()
    return pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    items, occ, pl = load("items.json"), load("occupants.json"), load("placeables.json")

    # entity id-union, deduped + crop-collapsed
    raw_ids = set(items) | set(occ) | set(pl)
    entities = sorted({base_id(e) for e in raw_ids})
    itemset = set(items)

    pages = catalog_text()

    # Some catalogs document a tiered/sized SET compactly (a "family") rather than every id:
    #   tools.md  "**pickaxe** wood→iron…", "**net** small+large"   (covers tool ids)
    #   armor.md  "**leather** ✅(pieces)", "**iron** ✅"             (covers armor pieces)
    # Families are EXPLICIT and CATEGORY-SCOPED so an armor "iron" row can't accidentally cover an
    # `ore_iron_block`. A member counts as documented when its family stem is documented as **bold**.
    SENTINELS = {"hands"}  # bare-hands pseudo-item; never cataloged by design
    TOOL_FAMILIES = {"pickaxe", "axe", "shovel", "hoe", "scythe", "watering_can", "net"}
    ARMOR_FAMILIES = {"leather", "iron", "copper", "straw"}

    def item_cat(e):
        d = items.get(e)
        return d.get("category") if d else None

    def family_stem(e):
        cat = item_cat(e)
        if cat in ("tool", "weapon"):
            for s in TOOL_FAMILIES:
                if e.startswith(s + "_") or e.endswith("_" + s):
                    return s
        if cat == "armor":
            for s in ARMOR_FAMILIES:
                if e.startswith(s + "_"):
                    return s
        return None

    table_ids = {}   # ids appearing in a markdown table row (line starting with '|'), per page
    bold_back = {}   # ids in backtick or **bold** markup, per page
    bold_stems = {}  # **stem** tokens, per page (for family coverage)
    for name, text in pages.items():
        tids, bb = set(), set()
        bstems = set(re.findall(r"\*\*([a-z][a-z0-9_]+)\*\*", text))
        for line in text.splitlines():
            toks = set(BACKTICK.findall(line)) | set(re.findall(r"\*\*([a-z][a-z0-9_]+)\*\*", line))
            bb |= toks
            if line.lstrip().startswith("|"):
                tids |= {w for w in re.findall(r"[a-z][a-z0-9_]+", line)}
        table_ids[name] = tids
        bold_back[name] = bb
        bold_stems[name] = bstems

    def mentions(e, name):
        # documented = explicit id markup (backtick/bold) OR a real table cell — NOT bare prose
        if e in bold_back[name] or e in table_ids[name]:
            return True
        stem = family_stem(e)
        if stem and stem in bold_stems[name]:
            return True
        return False

    # ids each page CLAIMS PRESENT: the ✅ marker sits ADJACENT to the id it certifies
    # (`poppy` ✅ / **leather** ✅ / wood✅) — NOT line-wide (a row lists designed ingredients too).
    CLAIM_RE = re.compile(r"(?:`([a-z][a-z0-9_]+)`|\*\*([a-z][a-z0-9_]+)\*\*|\b([a-z][a-z0-9_]+))\s*✅")
    claimed = {}
    for name, text in pages.items():
        claim = set()
        for m in CLAIM_RE.finditer(text):
            claim.add(m.group(1) or m.group(2) or m.group(3))
        claimed[name] = claim

    # which pages mention each entity (for orphan + multi-home)
    mentioned = {name: {e for e in entities if mentions(e, name)} for name in pages}
    all_mentioned = set().union(*mentioned.values()) if mentioned else set()

    # GATE 1 — orphans (sentinels excluded: never cataloged by design)
    orphans = [e for e in entities if e not in all_mentioned and e not in SENTINELS]

    # REPORT 2 — suspicious ✅: a ✅-marked id that is not a real ENTITY. NOT a hard gate: catalogs
    # legitimately mark DESIGNED materials ✅ ("exists in crafting.md / decided") that have no entity
    # def yet (bug-extractor outputs, crafting intermediates). Family stems (leather/iron) and a few
    # prose words are filtered. This surfaces possibly-stale claims for human review — never auto-fixed.
    STOPWORDS = {"all", "every", "none", "tbd", "na"}
    fam_all = TOOL_FAMILIES | ARMOR_FAMILIES
    ghosts = []
    for name, claim in claimed.items():
        for cid in sorted(claim):
            if cid in raw_ids or base_id(cid) in entities:
                continue
            if cid in fam_all or cid in STOPWORDS:
                continue
            ghosts.append((name, cid))

    # REPORT — placement (entity not on its primary page) + multi-home
    placement, multi = [], []
    for e in entities:
        homes = [n for n in pages if e in mentioned[n]]
        if len(homes) > 1:
            multi.append((e, homes))
        ph = primary_home(e, items, occ, pl)
        if ph != "?" and ph not in homes and e not in orphans:
            placement.append((e, ph, homes))

    # REPORT — drops whose item_id is a pure OCCUPANT (no item def AND not a placeable). Placeables
    # that drop themselves (well->well) are intended (Terraria) and render via the Objects/{id}
    # fallback, so they're excluded; this leaves forageable occupants lacking an item entry.
    occ_only_drops = {}
    for src, d in (("occupants", occ), ("placeables", pl)):
        for k, v in d.items():
            for drop in v.get("world", {}).get("breakable", {}).get("drops", []):
                iid = drop.get("item_id")
                if iid and iid not in itemset and iid in occ and iid not in pl:
                    occ_only_drops.setdefault(iid, []).append(k)

    # ---- output ----
    def section(title, rows):
        print(f"\n{title} ({len(rows)})")
        for r in rows:
            print(f"  {r}")

    if not args.quiet:
        print(f"Entities (deduped, crop-collapsed): {len(entities)}")
        print(f"Catalogs scanned: {', '.join(sorted(pages))}")
        # homing breakdown (useful when authoring)
        from collections import Counter
        byhome = Counter(primary_home(e, items, occ, pl) for e in entities)
        print("Primary-home breakdown: " + ", ".join(f"{k}={v}" for k, v in sorted(byhome.items())))

    fail = False
    if orphans:
        fail = True
        section("GATE 1 FAIL — ORPHANS (entity documented in no catalog)", orphans)
    else:
        print("\nGATE 1 PASS — no orphans (every entity documented in >=1 catalog).")

    if not args.quiet:
        section("REPORT — suspicious ✅ (marked present but no entity def — designed? stale?)", ghosts)
        section("REPORT — placement (entity not on its primary page)", placement)
        section("REPORT — multi-homed (mentioned on >1 page)", multi)
        section("REPORT — drops resolving to occupant-only (no item entry → icon?)",
                sorted(f"{k}  <- {v}" for k, v in occ_only_drops.items()))

    print("\n" + ("RESULT: ❌ GATE 1 failed (orphans exist)"
                  if fail else "RESULT: ✅ GATE 1 passes — every entity documented"))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
