#!/usr/bin/env python3
"""ZoneBuilder — the core of the zone-authoring builder library.

Holds a zone's two on-disk grids (ground tiles + occupants) PLUS two semantic masks
that feature primitives coordinate through, so features don't need to know about each
other:
  * surface[y][x]  in {water, path, building, farm, forest, grass}  -- what's logically here
  * reserved[y][x] (bool)                                           -- claimed by a hard feature

Primitives query reserved/surface BEFORE placing and refuse/clip LOUDLY on conflict
(never a silent overwrite), then update the masks. place_occupant writes the anchor cell
plus the entity's footprint cells, exactly like the game expects. save()/load() use the
same zone.json + chunk_X_Y.json format the server loads (and make_test_zone.py writes).

This is a low-level skeleton; feature primitives (pond/road/building/farm/scatter) live in
tools/zonegen/features/ and build on it.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENT_DIR = os.path.join(ROOT, "nakama", "data", "entities")
ZONES_DIR = os.path.join(ROOT, "nakama", "data", "zones")
OBJS_DIR = os.path.join(ROOT, "BugFarmerClient", "Assets", "Resources", "Objects")
CHUNK = 32  # cells per chunk side (must match world.ChunkSize)

SURFACES = {"water", "path", "building", "farm", "forest", "grass"}


def _load_entity_meta():
    meta = {}
    for fn in ("occupants.json", "placeables.json", "crops.json"):
        p = os.path.join(ENT_DIR, fn)
        if not os.path.exists(p):
            continue
        for k, v in json.load(open(p)).items():
            if isinstance(v, dict) and ("sprite_w" in v or "world" in v):
                meta[k] = v
    return meta


# Tile-id -> surface classification, for deriving masks when LOADING an existing zone.
def _tile_surface(tile_id):
    t = (tile_id or "").lower()
    if "water" in t or "pond" in t:
        return "water"
    if "path" in t or "road" in t or "cobble" in t:
        return "path"
    return "grass"


class ZoneBuilder:
    def __init__(self, zone_id, width, height, base_tile="grass", seed=0, name=None, biome="meadow"):
        # Render-only scene vignettes can be any size; only save() (which chunks the grid)
        # requires multiples of CHUNK.
        self.zone_id = zone_id
        self.W, self.H = width, height
        self.base_tile = base_tile
        self.seed = seed
        self.name = name or zone_id
        self.biome = biome
        self.spawn = [width // 2, height // 2]
        self.bug_spawning = None
        self.meta = _load_entity_meta()
        self.warnings = []
        self.ground = [[base_tile] * width for _ in range(height)]
        self.occ = {}  # (x,y) -> {"id","dir","anchor"?}
        self.surface = [["grass"] * width for _ in range(height)]
        self.reserved = [[False] * width for _ in range(height)]
        self.players = []  # [(sprite_id, x, y)] scene-dressing characters (render-only)
        self.bugs = []     # [(sprite_id, x, y)] scene-dressing bugs (render-only)
        self.decor = []    # [(id, x, y, mult)] free-floating ground decor (fruit) — render-only

    # ---- queries ------------------------------------------------------------
    def in_bounds(self, x, y):
        return 0 <= x < self.W and 0 <= y < self.H

    def footprint(self, oid):
        fp = (self.meta.get(oid, {}).get("world", {}) or {}).get("footprint")
        if isinstance(fp, (list, tuple)) and len(fp) >= 2:
            return int(fp[0]) or 1, int(fp[1]) or 1
        return 1, 1

    def is_free(self, x, y):
        return self.in_bounds(x, y) and not self.reserved[y][x]

    def warn(self, msg):
        self.warnings.append(msg)
        print(f"[zonebuilder:{self.zone_id}] WARN: {msg}")

    # ---- ground -------------------------------------------------------------
    def set_ground(self, x, y, tile, surface=None):
        if not self.in_bounds(x, y):
            return False
        self.ground[y][x] = tile
        if surface:
            self.surface[y][x] = surface
        return True

    def fill_ground(self, x0, y0, x1, y1, tile, surface=None):
        for y in range(max(0, y0), min(self.H, y1 + 1)):
            for x in range(max(0, x0), min(self.W, x1 + 1)):
                self.ground[y][x] = tile
                if surface:
                    self.surface[y][x] = surface

    def reserve(self, x, y, surface=None):
        if not self.in_bounds(x, y):
            return
        self.reserved[y][x] = True
        if surface:
            self.surface[y][x] = surface

    # ---- occupants ----------------------------------------------------------
    def place_occupant(self, oid, x, y, direction=0, surface="building", reserve=True):
        """Place an occupant with its anchor at (x,y). Writes the anchor cell plus the
        entity's footprint cells (to the right/down). Refuses (and warns) if any covered
        cell is out of bounds or already reserved — no silent overwrite."""
        fw, fh = self.footprint(oid)
        cells = [(x + dx, y + dy) for dy in range(fh) for dx in range(fw)]
        bad = [c for c in cells if not self.in_bounds(*c)]
        if bad:
            self.warn(f"place {oid} @({x},{y}) footprint {fw}x{fh} out of bounds: {bad}")
            return False
        clash = [c for c in cells if self.reserved[c[1]][c[0]]]
        if clash:
            self.warn(f"place {oid} @({x},{y}) overlaps reserved cells: {clash}")
            return False
        self.occ[(x, y)] = {"id": oid, "dir": direction, "anchor": True}
        for (cx, cy) in cells:
            if (cx, cy) != (x, y):
                self.occ[(cx, cy)] = {"id": oid, "dir": direction}
            if reserve:
                self.reserved[cy][cx] = True
            if surface:
                self.surface[cy][cx] = surface
        return True

    # ---- scene dressing (render-only; not persisted to chunks) --------------
    def place_player(self, sprite_id, x, y):
        """A character sprite (from Resources/Player) for scene previews only."""
        self.players.append((sprite_id, x, y))

    def place_bug(self, sprite_id, x, y, scale=1.0):
        """A bug sprite (from Resources/Bugs) for scene previews only — sub-grid floats, scaled,
        no reserve."""
        self.bugs.append((sprite_id, x, y, scale))

    def place_decor(self, oid, x, y, scale=1.0):
        """Free-floating ground decor (fruit) — sub-grid (x,y may be floats), scaled by `scale`,
        NOT an occupant (no footprint, no reserve, doesn't line up with cells)."""
        self.decor.append((oid, x, y, scale))

    # ---- art tracking -------------------------------------------------------
    def missing_art(self):
        """Placed occupant ids whose world sprite PNG doesn't exist yet (need art)."""
        ids = {c["id"] for c in self.occ.values()}
        return sorted(i for i in ids if not os.path.exists(os.path.join(OBJS_DIR, f"{i}.png")))

    # ---- validation ---------------------------------------------------------
    def validate(self):
        issues = []
        for (x, y), c in self.occ.items():
            if not self.in_bounds(x, y):
                issues.append(f"occupant {c['id']} out of bounds at ({x},{y})")
            if c.get("anchor") and self.surface[y][x] == "water":
                issues.append(f"occupant {c['id']} anchored on water at ({x},{y})")
        sx, sy = self.spawn
        if not self.in_bounds(sx, sy):
            issues.append(f"spawn point {self.spawn} out of bounds")
        elif self.reserved[sy][sx] or self.surface[sy][sx] in ("water", "building"):
            issues.append(f"spawn point {self.spawn} is on a reserved/{self.surface[sy][sx]} cell")
        return issues

    # ---- persistence --------------------------------------------------------
    def _chunk_counts(self):
        return self.W // CHUNK, self.H // CHUNK

    def save(self, zones_dir=ZONES_DIR):
        if self.W % CHUNK or self.H % CHUNK:
            raise ValueError(f"save() needs width/height as multiples of {CHUNK} "
                             f"(got {self.W}x{self.H}); pad the zone or build at a chunk-aligned size")
        out = os.path.join(zones_dir, self.zone_id)
        os.makedirs(out, exist_ok=True)
        cfg = {
            "zone_id": self.zone_id, "name": self.name, "row": 0, "col": 0,
            "width": self.W, "height": self.H, "spawn_point": list(self.spawn),
            "biome_type": self.biome, "seed": self.seed,
        }
        if self.bug_spawning is not None:
            cfg["bug_spawning"] = self.bug_spawning
        with open(os.path.join(out, "zone.json"), "w") as f:
            json.dump(cfg, f, indent=2)
        cw, ch = self._chunk_counts()
        for cy in range(ch):
            for cx in range(cw):
                ground = [[self.ground[cy * CHUNK + ly][cx * CHUNK + lx] for lx in range(CHUNK)]
                          for ly in range(CHUNK)]
                occ = [[self.occ.get((cx * CHUNK + lx, cy * CHUNK + ly)) for lx in range(CHUNK)]
                       for ly in range(CHUNK)]
                with open(os.path.join(out, f"chunk_{cx}_{cy}.json"), "w") as f:
                    json.dump({"chunk_x": cx, "chunk_y": cy, "ground": ground, "occupants": occ}, f)
        return out

    @classmethod
    def load(cls, zone_id, zones_dir=ZONES_DIR):
        zdir = zone_id if os.path.isdir(zone_id) else os.path.join(zones_dir, zone_id)
        cfg = json.load(open(os.path.join(zdir, "zone.json")))
        b = cls(cfg.get("zone_id", os.path.basename(zdir.rstrip("/"))),
                cfg.get("width") or 256, cfg.get("height") or 256,
                seed=cfg.get("seed", 0), name=cfg.get("name"), biome=cfg.get("biome_type", "meadow"))
        b.spawn = list(cfg.get("spawn_point", b.spawn))
        b.bug_spawning = cfg.get("bug_spawning")
        cw, ch = b._chunk_counts()
        for cy in range(ch):
            for cx in range(cw):
                cf = os.path.join(zdir, f"chunk_{cx}_{cy}.json")
                if not os.path.exists(cf):
                    continue
                chunk = json.load(open(cf))
                for ly in range(CHUNK):
                    for lx in range(CHUNK):
                        gx, gy = cx * CHUNK + lx, cy * CHUNK + ly
                        tile = chunk["ground"][ly][lx]
                        b.ground[gy][gx] = tile
                        b.surface[gy][gx] = _tile_surface(tile)
                        occ = chunk["occupants"][ly][lx]
                        if isinstance(occ, dict):
                            b.occ[(gx, gy)] = occ
                            b.reserved[gy][gx] = True
                            if b.surface[gy][gx] == "grass":
                                b.surface[gy][gx] = "building"
        return b
