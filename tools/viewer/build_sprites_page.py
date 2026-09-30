#!/usr/bin/env python3
"""build_sprites_page.py — build "Bug Farmer Sprites": every sprite and animation the game uses, on one page.

    python3 tools/viewer/build_sprites_page.py

Writes tools/_generated/viewer/sprites/index.html (git-ignored, like all generated output) plus a copy of each
approved outfit animation under tools/_generated/viewer/sprites/outfits/<outfit>/<animation>.gif. The page is
published to claude.ai (link in tools/viewer/README.md); republish index.html after rebuilding. To look at it on
this PC instead, open preview.html in the same folder (the same page with the few lines claude.ai adds).

WHAT IS ON IT — everything the game draws, found the way the game finds it:
  items          the inventory icon, by the game's own lookup (EntityDatabase.GetItemSprite: Objects/{icon_from},
                 Objects/{id}, Items/{id}_icon, Items/{id}, then the bug sprite)
  objects        placeables + occupants: the world sprite Objects/{id}, drawn at its in-game size (sprite_w x
                 sprite_h game pixels, 16 to a cell) — the townspeople are occupants too
  crops          each crop's growth stages Objects/plant_<crop>_stage<n> (TilemapManager.cs:714-717)
  bugs           each species' flap frames Bugs/{sprite_id}_0.._11 (SwarmVisual.cs:121-130) at the game's flap rate
                 (BugVisual.FlapFps 11, flies 20), its eggs/larvae (the nursery panel's pictures) and, for
                 centipedes and millipedes, the segment sprites (CentipedeTrail.cs:66-76)
  ground tiles   Tiles/{id} for every tile type in nakama/data/tiles.json, the grass variants and the grass tufts
  player         the paper-doll layers the game composes (CharacterComposer.cs: order, walk cycle, 7 fps from
                 PlayerController.WalkFps) and the baked class sprites
  outfits        the approved whole outfits and their animations, from official.py — NOT in the game yet
  effects + UI   the breaking stages and the interface sprites

Nothing is hand-listed except the game's rules above, so a new sprite or entity shows up on the next rebuild.
Requested by the owner on 2026-09-30: one page showing every sprite and animation the game uses. It is generated,
never edited by hand, and is not dead code.
"""
import base64
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

# The repo root, found by walking up (works wherever this file sits).
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "nakama").is_dir() and (p / "tools").is_dir())
RES = ROOT / "BugFarmerClient" / "Assets" / "Resources"
DATA = ROOT / "nakama" / "data"
PLAYER_ART = ROOT / "tools" / "_generated" / "player"
TEMPLATE = Path(__file__).with_name("sprites_page.template.html")
OUT_ROOT = ROOT / "tools" / "_generated" / "viewer"
OUT = OUT_ROOT / "sprites"

sys.path.insert(0, str(ROOT / "tools" / "player_sprites"))
import official  # noqa: E402  — the approved outfits + animations (the same list gallery.py shows)

# The game's own constants, with where they live (checked 2026-09-30).
WALK_FPS = 7            # PlayerController.WalkFps
FLAP_FPS = 11           # BugVisual.FlapFps (default)
BUZZ_FPS = 20           # SwarmVisual: flies buzz ("fly" in the sprite id, not "butterfly")
PLAYER_DIRS = ["down", "left", "right", "up"]            # CharacterComposer.DirNames
WALK_SUFFIX = ["_w1", "", "_w3", ""]                     # CharacterComposer.FrameSuffix
LAYER_ORDER = ["body", "pants", "legs", "feet", "shirt", "chest", "arms", "hair", "helmet"]  # LayerPaths
HIDES_HAIR = ["iron_helmet"]                             # CharacterComposer.HidesHair
CELL = 16               # game pixels per cell (16 PPU)

SPRITES = {}            # "Objects/tree_oak" -> {"w", "h", "src"}; each PNG embedded once


def sprite(key):
    """Register Resources/<key>.png if it exists; return the key, or None when the game has no such file."""
    if key in SPRITES:
        return key
    p = RES / (key + ".png")
    if not p.is_file():
        return None
    with Image.open(p) as im:
        w, h = im.size
    SPRITES[key] = {"w": w, "h": h, "src": "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()}
    return key


def load(name):
    d = json.loads((DATA / "entities" / name).read_text(encoding="utf-8"))
    return {k: v for k, v in d.items() if not k.startswith("_") and isinstance(v, dict)}


def facts(d, keys):
    """The scalar data fields worth showing, in a fixed order, skipping empties."""
    out = []
    for k in keys:
        v = d.get(k)
        if v in (None, "", [], {}):
            continue
        if isinstance(v, bool):
            v = "yes" if v else "no"
        if isinstance(v, (list, dict)):
            v = json.dumps(v, ensure_ascii=False)
        out.append([k.replace("_", " "), str(v)])
    return out


ITEM_FACTS = ["category", "description", "sell_price", "buy_price", "stackable", "max_stack", "tool_type",
              "tool_tier", "reach", "durability", "mining_speed", "cooldown_ticks", "armor_slot", "overlay",
              "food_value", "places_crop", "icon_from", "effect", "effect_power"]
WORLD_FACTS = ["category", "description", "sprite_w", "sprite_h", "sell_price", "stackable", "max_stack"]
SPECIES_FACTS = ["category", "description", "max_hp", "sell_price", "movement_style", "base_speed",
                 "attack_damage", "carcass_item", "net_size", "lifespan_secs", "larva_name", "brood_label"]


def item_icon(eid, d, species_sprite):
    """EntityDatabase.GetItemSprite, in order (EntityDatabase.cs:775-787)."""
    cands = []
    if d.get("icon_from"):
        cands.append(f"Objects/{d['icon_from']}")
    cands += [f"Objects/{eid}", f"Items/{eid}_icon", f"Items/{eid}", f"Bugs/{species_sprite.get(eid, eid)}"]
    for c in cands:
        if sprite(c):
            return c
    return None


def world_extras(d):
    """A few facts from an object's world block: footprint, what it does, what breaks it, what it drops."""
    w = d.get("world") or {}
    out = []
    if w.get("footprint"):
        out.append(["footprint", " x ".join(str(x) for x in w["footprint"]) + " cells"])
    if w.get("interaction_type"):
        out.append(["interaction", w["interaction_type"]])
    br = w.get("breakable") or {}
    if br:
        tool = br.get("required_tool_type")
        out.append(["breaks with", (tool or "hand") + (f" (tier {br['required_tool_tier']})" if br.get("required_tool_tier") else "")])
        drops = [x.get("item_id") for x in (br.get("drops") or []) if isinstance(x, dict) and x.get("item_id")]
        if drops:
            out.append(["drops", ", ".join(drops)])
    shop = w.get("shop") or {}
    if shop.get("sells"):
        out.append(["sells", ", ".join(s["id"] for s in shop["sells"])])
    return out


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return ""


def build():
    items, occ, pl = load("items.json"), load("occupants.json"), load("placeables.json")
    species = {k: v for k, v in json.loads((DATA / "species.json").read_text(encoding="utf-8")).items()
               if isinstance(v, dict)}
    tiles = {k: v for k, v in json.loads((DATA / "tiles.json").read_text(encoding="utf-8")).items()
             if isinstance(v, dict)}
    species_sprite = {k: v.get("sprite_id") for k, v in species.items() if v.get("sprite_id")}
    stage_re = re.compile(r"^(.*)_stage(\d+)$")
    missing = []

    # ---- items ----------------------------------------------------------------------------------------
    sec_items = []
    for eid, d in sorted(items.items(), key=lambda kv: (kv[1].get("category", ""), kv[1].get("name", kv[0]))):
        key = item_icon(eid, d, species_sprite)
        if not key:
            missing.append(eid)
        sec_items.append({"id": eid, "name": d.get("name", eid), "group": d.get("category") or "other",
                          "frames": [key] if key else [], "facts": facts(d, ITEM_FACTS),
                          "note": "inventory icon"})

    # ---- objects (placeables + occupants, crop stages live under crops) --------------------------------
    sec_objects = []
    townsfolk = set()
    for src, table in (("placeable", pl), ("occupant", occ)):
        for eid, d in table.items():
            if stage_re.match(eid):
                continue
            w = d.get("world") or {}
            group = d.get("category") or "other"
            if w.get("shop") or w.get("interaction_type") == "npc":
                group = "townspeople"
                townsfolk.add(eid)
            key = sprite(f"Objects/{eid}")
            if not key:
                missing.append(eid)
            gw, gh = d.get("sprite_w"), d.get("sprite_h")
            sec_objects.append({"id": eid, "name": d.get("name", eid), "group": group, "kind": src,
                                "frames": [key] if key else [], "game": [gw, gh] if gw and gh else None,
                                "facts": facts(d, WORLD_FACTS) + world_extras(d)})
    sec_objects.sort(key=lambda e: (e["group"], e["name"].lower()))

    # ---- crops: growth stages ---------------------------------------------------------------------------
    stages = {}
    for table in (occ, pl):
        for eid, d in table.items():
            m = stage_re.match(eid)
            if m:
                stages.setdefault(m.group(1), []).append((int(m.group(2)), eid, d))
    crops = json.loads((DATA / "entities" / "crops.json").read_text(encoding="utf-8"))
    sec_crops = []
    for base, sts in sorted(stages.items()):
        sts.sort()
        frames, sizes = [], []
        for _, eid, d in sts:
            k = sprite(f"Objects/{eid}")
            if k:
                frames.append(k)
                sizes.append([d.get("sprite_w"), d.get("sprite_h")])
            else:
                missing.append(eid)
        crop = base[len("plant_"):] if base.startswith("plant_") else base
        cd = crops.get(crop, {})
        harvest = cd.get("harvest_item")
        sec_crops.append({"id": base, "name": crop.replace("_", " ").title(), "group": "crops",
                          "frames": frames, "sizes": sizes, "fps": 1.5, "anim": "growth",
                          "harvest": item_icon(harvest, items.get(harvest, {}), species_sprite) if harvest else None,
                          "facts": facts(cd, ["growth_stages", "waterings_per_stage", "harvest_item",
                                              "harvest_count_min", "harvest_count_max", "multi_harvest",
                                              "max_harvests"]),
                          "stage_ids": [eid for _, eid, _ in sts]})

    # ---- bugs ---------------------------------------------------------------------------------------------
    sec_bugs = []
    for sid, d in species.items():
        spr = d.get("sprite_id") or sid
        frames = []
        for i in range(12):                        # contiguous from _0, as SwarmVisual loads them
            k = sprite(f"Bugs/{spr}_{i}")
            if not k:
                break
            frames.append(k)
        if len(frames) < 2:
            one = sprite(f"Bugs/{spr}")
            frames = [one] if one else frames[:1]
        buzzer = "fly" in spr and "butterfly" not in spr
        brood = []
        for label, field in (("eggs", "egg_sprite_id"), (d.get("larva_name") or "larvae", "larva_sprite_id"),
                             ("pupae", "pupa_sprite_id")):
            bid = d.get(field)
            if bid:
                k = item_icon(bid, {}, species_sprite)
                brood.append({"label": label, "id": bid, "frames": [k] if k else []})
        segs = []
        if d.get("movement_style") == "centipede" or "millipede" in sid:
            milli = "millipede" in sid
            fam = d.get("sprite_family") or ("millipede" if milli else "centipede")
            v = "a" if milli else "b"
            for part, key in (("head", f"Bugs/{spr}"), ("body", f"Bugs/{fam}_body_{v}"), ("tail", f"Bugs/{fam}_tail_{v}")):
                k = sprite(key)
                if k:
                    segs.append({"label": part, "frames": [k]})
        drops = [x.get("item_id") if isinstance(x, dict) else x for x in (d.get("kill_drops") or [])]
        sec_bugs.append({"id": sid, "name": d.get("name", sid), "group": d.get("category") or "bug",
                         "frames": frames, "fps": BUZZ_FPS if buzzer else FLAP_FPS,
                         "anim": "flap" if len(frames) > 1 else None, "brood": brood, "segments": segs,
                         "facts": facts(d, SPECIES_FACTS) + ([["kill drops", ", ".join(x for x in drops if x)]] if any(drops) else [])})
    sec_bugs.sort(key=lambda e: e["name"].lower())

    # ---- ground tiles -------------------------------------------------------------------------------------
    sec_tiles = []
    for tid, d in sorted(tiles.items()):
        frames = [k for k in [sprite(f"Tiles/{tid}")] if k]
        variants = [k for k in (sprite(f"Tiles/{tid}_v{n}") for n in range(2, 6)) if k]
        if not frames:
            missing.append(tid)
        sec_tiles.append({"id": tid, "name": tid.replace("_", " "), "group": "tiles", "frames": frames,
                          "variants": variants, "game": [CELL, CELL],
                          "facts": facts(d, ["movement_mult", "blocks_players", "blocks_bugs", "accepts_furniture",
                                             "accepts_structure", "accepts_plant", "tool_actions"])})
    tufts = [k for k in (sprite(f"Objects/grass_tuft_{n}") for n in range(1, 5)) if k]

    # ---- player: paper-doll layers + baked class sprites --------------------------------------------------
    layers_dir = RES / "Player" / "layers"
    slots = {}
    for slot_dir in sorted(p for p in layers_dir.iterdir() if p.is_dir()):
        styles = sorted({re.sub(r"_(down|left|right|up)(_w[13])?$", "", f.stem) for f in slot_dir.glob("*.png")})
        slots[slot_dir.name] = styles
        for st in styles:
            for dr in PLAYER_DIRS:
                for suf in ("", "_w1", "_w3"):
                    sprite(f"Player/layers/{slot_dir.name}/{st}_{dr}{suf}")
    classes = sorted({re.sub(r"_(down|left|right|up)(_w[13])?$", "", f.stem) for f in (RES / "Player").glob("*.png")})
    for c in classes:
        for dr in PLAYER_DIRS:
            for suf in ("", "_w1", "_w3"):
                sprite(f"Player/{c}_{dr}{suf}")

    # ---- approved outfits (not in the game yet) ------------------------------------------------------------
    outfits = []
    for oid, od in official.OUTFITS.items():
        anims = []
        for a in official.ANIMATIONS:
            src = PLAYER_ART / official.path(oid, "anim") / f"{a}.gif"
            if src.is_file():
                with Image.open(src) as im:
                    size = list(im.size)
                anims.append({"id": a, "file": f"outfits/{oid}/{a}.gif", "src": str(src), "size": size})
        outfits.append({"id": oid, "name": oid.replace("fireant", "fire ant").replace("blackant", "black ant").title(),
                        "approved": od.get("approved", ""), "anims": anims})

    # ---- effects + interface ------------------------------------------------------------------------------
    sec_effects = [{"id": "break_stages", "name": "Breaking", "group": "effects", "anim": "stages", "fps": 3,
                    "frames": [k for k in (sprite(f"Effects/break_stage_{n}") for n in range(1, 5)) if k],
                    "facts": [["shown", "over a block or object while it is being broken, one stage per step of damage"]]}]
    sec_ui = [{"id": f.stem, "name": f.stem.replace("_", " "), "group": "interface", "frames": [sprite(f"UI/{f.stem}")]}
              for f in sorted((RES / "UI").glob("*.png"))]

    commit = git("rev-parse", "--short", "HEAD")
    dirty = bool(git("status", "--porcelain", "--", "BugFarmerClient/Assets/Resources", "nakama/data"))
    data = {
        "built": {"date": datetime.date.today().isoformat(), "commit": commit, "dirty": dirty},
        "counts": {"sprites": len(SPRITES), "missing": sorted(set(missing))},
        "sprites": SPRITES,
        "items": sec_items, "objects": sec_objects, "crops": sec_crops, "bugs": sec_bugs,
        "tiles": sec_tiles, "tufts": tufts, "effects": sec_effects, "ui": sec_ui,
        "player": {"slots": slots, "classes": classes, "dirs": PLAYER_DIRS, "walk": WALK_SUFFIX,
                   "walkFps": WALK_FPS, "order": LAYER_ORDER, "hidesHair": HIDES_HAIR},
        "outfits": [{k: v for k, v in o.items()} for o in outfits],
        "townsfolk": sorted(townsfolk),
    }

    # ---- write ------------------------------------------------------------------------------------------
    out = OUT.resolve()
    assert out.parent == OUT_ROOT.resolve() and out.name == "sprites", out     # only ever wipe our own folder
    if out.exists():
        shutil.rmtree(out)
    (out / "outfits").mkdir(parents=True)
    for o in outfits:
        for a in o["anims"]:
            dst = out / a["file"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(a.pop("src"), dst)
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    assert html.count("/*__DATA__*/null") == 1, "template data marker missing"
    page = html.replace("/*__DATA__*/null", blob)
    (out / "index.html").write_text(page, encoding="utf-8")        # what gets published (claude.ai adds the skeleton)
    (out / "preview.html").write_text(                                 # the same page, openable from disk
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>'
        + page + "</body></html>", encoding="utf-8")

    # ---- self-check -------------------------------------------------------------------------------------
    problems = []
    def check(entries, where):
        for e in entries:
            for k in e.get("frames", []) + e.get("variants", []):
                if k not in SPRITES:
                    problems.append(f"{where}/{e['id']}: frame {k} not embedded")
    for name in ("items", "objects", "crops", "bugs", "tiles", "effects", "ui"):
        check(data[name], name)
    gifs = sum(len(o["anims"]) for o in outfits)
    expected_gifs = len(official.OUTFITS) * len(official.ANIMATIONS)
    if gifs != expected_gifs:
        problems.append(f"outfit animations: {gifs} found, {expected_gifs} expected")
    mb = (out / "index.html").stat().st_size / 1e6
    if mb > 15:
        problems.append(f"page is {mb:.1f} MB — over claude.ai's 16 MB page limit soon")
    print(f"wrote {out / 'index.html'}  ({mb:.2f} MB, {len(SPRITES)} sprites embedded)")
    print(f"  items {len(sec_items)} · objects {len(sec_objects)} (townspeople {len(townsfolk)}) · crops {len(sec_crops)} · "
          f"bugs {len(sec_bugs)} · tile types {len(sec_tiles)} · tufts {len(tufts)} · player layer slots {len(slots)} · "
          f"classes {len(classes)} · outfit animations {gifs} · effects {len(sec_effects)} · interface {len(sec_ui)}")
    print(f"  things the game has no picture for: {len(set(missing))}")
    if problems:
        print("PROBLEMS:\n  " + "\n  ".join(problems))
        sys.exit(1)
    print("self-check OK")


if __name__ == "__main__":
    build()
