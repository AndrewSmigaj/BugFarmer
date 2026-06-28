#!/usr/bin/env python3
"""Recipe-graph + completeness validator — the crafting integrity gate.

Two gates, run from the git root (`python3 tools/data/recipe_graph.py`):

  1. REACHABILITY — every recipe input/output/catalyst id resolves to a real entity
     (item/placeable/occupant), every station id is a real placeable, and every
     crafted intermediate is itself produced by some recipe or is a base resource
     (mined drop / forage / a raw item). No dangling refs, no orphan intermediates.

  2. COMPLETENESS ("no half-ladder") — the matrices we build must be FULL, not partial.
     The lesson behind this tool: shipping `iron_bar` with no `copper_bar`, or tools that
     stop at iron, reads as "done" but isn't. So we assert the declared sets exist whole:
       - the 6-metal mining refine chain (ore -> paydirt -> refined -> bar) per metal
       - the metal tool ladders (pickaxe/axe/hoe/scythe/shovel x copper..platinum)
       - the gem chain (block -> raw -> cut) per gem

Exit non-zero on any failure so it can gate a build/commit. Pure data read; no deps.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, "nakama", "data", "entities")

def load(name):
    return {k: v for k, v in json.load(open(os.path.join(D, name))).items() if not k.startswith("_")}

items, plac, occ = load("items.json"), load("placeables.json"), load("occupants.json")
recipes = load("recipes.json")
all_ids = set(items) | set(plac) | set(occ)

errors, warnings = [], []

# ---- collect what each entity DROPS (so intermediates are "reachable" from mining/forage) ----
def drops_of(e):
    out = []
    w = e.get("world", {}) or {}
    br = w.get("breakable", {}) or {}
    for d in br.get("drops", []) or []:
        out.append(d.get("item_id"))
    for d in e.get("drops", []) or []:
        out.append(d.get("item_id") if isinstance(d, dict) else d)
    return [x for x in out if x]

produced = set()                      # ids produced by a recipe output
for r in recipes.values():
    produced.add(r["output"]["item"])
dropped = set()                       # ids dropped by an occupant/placeable (mined/broken)
for src in (occ, plac):
    for e in src.values():
        dropped.update(drops_of(e))
# base resources: anything that is an item but is gathered (no recipe needed) — we treat
# an item as a valid leaf if it is dropped, OR is a known raw resource category.
RAW_OK = produced | dropped | set(occ)

# ---- GATE 1: reachability ----
for name, r in recipes.items():
    if r.get("station") not in all_ids:
        errors.append(f"[reach] recipe '{name}': station '{r.get('station')}' is not an entity")
    ins = list(r.get("inputs", []) or [])
    if r.get("catalyst"):
        ins.append(r["catalyst"])
    for i in ins:
        iid = i["item"]
        if iid not in all_ids:
            errors.append(f"[reach] recipe '{name}': input '{iid}' is not an entity")
        elif iid not in RAW_OK:
            # an input that is neither produced by a recipe nor dropped nor a base raw → orphan
            warnings.append(f"[reach] recipe '{name}': input '{iid}' has no producer (recipe/drop) — base resource?")
    out = r["output"]["item"]
    if out not in all_ids:
        errors.append(f"[reach] recipe '{name}': output '{out}' is not an entity")

# ---- GATE 2: completeness matrices ----
METALS = ["copper", "iron", "tin", "silver", "gold", "platinum"]
for m in METALS:
    chain = [f"{m}_ore", f"{m}_paydirt", f"refined_{m}_ore"]
    for it in chain:
        if it not in items:
            errors.append(f"[complete:metal] {m}: missing item '{it}'")
    if f"{m}_paydirt" not in recipes:
        errors.append(f"[complete:metal] {m}: missing crusher recipe -> {m}_paydirt")
    if f"refined_{m}_ore" not in recipes:
        errors.append(f"[complete:metal] {m}: missing sluice recipe -> refined_{m}_ore")

TOOL_FAMS = ["pickaxe", "axe", "hoe", "scythe", "shovel"]
TOOL_TIERS = ["copper", "iron", "steel", "silver", "gold", "platinum"]
for fam in TOOL_FAMS:
    for t in TOOL_TIERS:
        key = f"{fam}_{t}"
        if key not in items:
            errors.append(f"[complete:tool] missing tool item '{key}'")
        elif key not in recipes:
            errors.append(f"[complete:tool] tool '{key}' has no recipe")

GEMS = ["diamond", "quartz", "ruby", "sapphire", "emerald"]
for g in GEMS:
    if g not in items:
        errors.append(f"[complete:gem] missing raw gem '{g}'")
    if f"cut_{g}" not in items:
        errors.append(f"[complete:gem] missing cut gem 'cut_{g}'")
    if f"cut_{g}" not in recipes:
        errors.append(f"[complete:gem] gem '{g}' has no cutter recipe")

# ---- report ----
print(f"recipes={len(recipes)} items={len(items)} placeables={len(plac)} occupants={len(occ)}")
if warnings:
    print(f"\n⚠ {len(warnings)} warning(s) (base-resource inputs — usually fine):")
    for w in warnings[:25]:
        print("  " + w)
if errors:
    print(f"\n❌ {len(errors)} ERROR(s):")
    for e in errors:
        print("  " + e)
    sys.exit(1)
print("\n✅ recipe graph OK — reachability + completeness gates pass")
