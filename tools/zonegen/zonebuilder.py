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
        # Test/observation-zone flags (default off → no effect on normal zones). peaceful: bugs ignore
        # the player (ZoneConfig.Peaceful, zone.go). ephemeral_swarms: re-seed the initial population each
        # load instead of restoring the save (a reproducible sandbox). Both are additive in save().
        self.peaceful = False
        self.ephemeral_swarms = False
        # World-map identity, written by save() (retires the old post-save zone.json patching):
        # grid = (row, col) in the world grid; neighbors = {"north"/"south"/"east"/"west": zone_id}
        # zone links (walking off an edge enters that neighbor). Defaults match the old save().
        self.grid = (0, 0)
        self.neighbors = None  # dict or None
        self.meta = _load_entity_meta()
        self.warnings = []
        self.ground = [[base_tile] * width for _ in range(height)]
        self.occ = {}  # (x,y) -> {"id","dir","anchor"?}
        self.surface = [["grass"] * width for _ in range(height)]
        self.reserved = [[False] * width for _ in range(height)]
        # Per-cell "roofed" flag (True = underground / no sun) for the lighting darkness system.
        # Authored over the WHOLE underground region interior (solid AND open) so a runtime-dug cell
        # stays dark. Persisted per-chunk in save() (only when a chunk has any roofed cell). Independent
        # of walls/blocks. See docs/product/architecture/architecture_lighting.md.
        self.roof = [[False] * width for _ in range(height)]
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

    # ---- roof (lighting darkness) -------------------------------------------
    def set_roof(self, x, y, val=True):
        """Mark one cell roofed (underground / no sun) for the lighting darkness system."""
        if self.in_bounds(x, y):
            self.roof[y][x] = val

    def mark_roof_region(self, cells):
        """Mark every (x,y) in `cells` roofed. Author roof over the WHOLE underground region
        interior (solid AND open cells) so a runtime-dug cell inside stays dark — NOT just the
        carved tunnels (architecture_lighting.md HC2 / design-critic Finding 2)."""
        for (x, y) in cells:
            self.set_roof(x, y, True)

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
    def place_occupant(self, oid, x, y, direction=0, surface="building", reserve=True, text=None):
        """Place an occupant with its anchor at (x,y). Writes the anchor cell plus the
        entity's footprint cells (to the right/down). Refuses (and warns) if any covered
        cell is out of bounds or already reserved — no silent overwrite.
        `text` = optional per-placement authored text (signs: shown on right-click)."""
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
        # Place-time road check (the lint can't see this later: we overwrite the
        # surface mask below, destroying the 'path' evidence — roads also aren't
        # reserved, so the clash check above never fires for them).
        if surface == "building":
            on_road = [c for c in cells if self.surface[c[1]][c[0]] == "path"]
            if on_road:
                self.warn(f"{oid} @({x},{y}) placed over road cells {on_road} "
                          f"(the road will run visibly through it)")
        anchor = {"id": oid, "dir": direction, "anchor": True}
        if text:
            anchor["text"] = text
        self.occ[(x, y)] = anchor
        for (cx, cy) in cells:
            if (cx, cy) != (x, y):
                self.occ[(cx, cy)] = {"id": oid, "dir": direction}
            if reserve:
                self.reserved[cy][cx] = True
            if surface:
                self.surface[cy][cx] = surface
        return True

    # ---- composition ---------------------------------------------------------
    def blit(self, src, ox, oy, *, transparent=False, on_conflict="skip"):
        """Copy another builder's content into this one at offset (ox,oy) — the
        scene→zone composition API. Ground/surface/reserved copy per cell (out-of-
        bounds cells clip with one summary warn). Occupants copy ANCHOR-GROUPED
        through place_occupant (occ body cells carry no anchor back-pointer, so a
        per-cell copy could shear a footprint in half): a conflicting occupant is
        skipped whole with the usual loud warn (`on_conflict="raise"` raises
        instead, for strict scenes). `transparent=True` skips src cells that are
        untouched base tile — the dst terrain shows through, so a vignette drops in
        without stamping a rectangle. Render-only dressing (players/bugs/decor)
        offsets along. Does NOT merge spawn/bug_spawning — zone config stays the
        caller's. Returns the number of skipped occupants."""
        clipped = 0
        for y in range(src.H):
            for x in range(src.W):
                dx, dy = ox + x, oy + y
                if not self.in_bounds(dx, dy):
                    clipped += 1
                    continue
                occ_cell = (x, y) in src.occ
                if transparent and not occ_cell and not src.reserved[y][x] \
                        and src.ground[y][x] == src.base_tile:
                    continue
                self.ground[dy][dx] = src.ground[y][x]
                self.surface[dy][dx] = src.surface[y][x]
                # Occupant cells re-reserve via place_occupant below, so a SKIPPED
                # occupant doesn't leave phantom reservations behind.
                if src.reserved[y][x] and not occ_cell:
                    self.reserved[dy][dx] = True
        if clipped:
            self.warn(f"blit {src.zone_id} @({ox},{oy}): {clipped} cells clipped out of bounds")

        skipped = 0
        for (x, y), c in sorted(src.occ.items()):  # sorted: deterministic order
            if not c.get("anchor"):
                continue
            ok = self.place_occupant(c["id"], ox + x, oy + y, direction=c.get("dir", 0),
                                     surface=src.surface[y][x])
            if not ok:
                skipped += 1
                if on_conflict == "raise":
                    raise ValueError(f"blit conflict: {c['id']} @({ox + x},{oy + y})")

        for (sid, px, py) in src.players:
            self.players.append((sid, px + ox, py + oy))
        for tup in src.bugs:
            self.bugs.append((tup[0], tup[1] + ox, tup[2] + oy) + tuple(tup[3:]))
        for (did, fx, fy, mult) in src.decor:
            self.decor.append((did, fx + ox, fy + oy, mult))
        return skipped

    # ---- scene dressing (render-only; not persisted to chunks) --------------
    def place_player(self, sprite_id, x, y):
        """A character sprite (from Resources/Player) for scene previews only."""
        self.players.append((sprite_id, x, y))

    def place_bug(self, sprite_id, x, y, scale=1.0, flip=False):
        """A bug sprite (from Resources/Bugs) for scene previews only — sub-grid floats, scaled,
        no reserve. `flip=True` mirrors the sprite horizontally so bugs can face either way."""
        self.bugs.append((sprite_id, x, y, scale, flip))

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

    def lint(self):
        """Programmatic SPATIAL QA — returns human-readable defect strings (text I can actually reason
        about, vs eyeballing a render). Catches: blocked/oversized doors, walls on roads/water,
        wall!=door!=window heights, checkered roads."""
        m = self.meta
        out = []

        def world(o): return (m.get(o, {}) or {}).get("world", {}) or {}
        def is_door(o): return world(o).get("interaction_type") == "door" or o.startswith("door")
        def is_wall(o): return bool(o) and (o.startswith("wall") or (m.get(o, {}) or {}).get("category") == "block")
        def oid(x, y):
            c = self.occ.get((x, y)); return c["id"] if c else None
        def passable(x, y):  # doors and gates are openings you walk through
            o = oid(x, y); return bool(o) and (is_door(o) or o.startswith("gate"))
        def blocked(x, y):  # a cell you can't stand in (off-grid, or reserved by something solid)
            if not self.in_bounds(x, y):
                return True
            if not self.reserved[y][x] or passable(x, y):
                return False
            # Reserved-but-EMPTY interior floor is walkable: interiors reserve at
            # place-time so later passes can't paint/place inside a finished
            # building (the living-room road) — that's authoring, not collision.
            return bool(self.occ.get((x, y))) or self.surface[y][x] != "building"

        # doors: must be 1-wide and have a clear cell on BOTH sides (inside + outside the wall)
        for (x, y), c in self.occ.items():
            if not c.get("anchor") or not is_door(c["id"]):
                continue
            d = c["id"]
            if self.footprint(d)[0] != 1:
                out.append(f"DOOR {d} @({x},{y}) is {self.footprint(d)[0]}-wide — doors must be 1 wide")
            horiz = is_wall(oid(x - 1, y)) or is_wall(oid(x + 1, y))   # wall runs L-R → door faces N/S
            vert = is_wall(oid(x, y - 1)) or is_wall(oid(x, y + 1))
            perp = [(x, y - 1), (x, y + 1)] if horiz else [(x - 1, y), (x + 1, y)] if vert else []
            jammed = [p for p in perp if blocked(*p)]
            if jammed:
                out.append(f"DOOR {d} @({x},{y}) blocked in the doorway at {jammed} "
                           f"(occupant/wall where you'd walk through)")

        # walls/fences/gates sitting on a road/plaza/water tile
        for (x, y), c in self.occ.items():
            # gates excluded: a gate sits over its approach path by design
            if c.get("anchor") and c["id"].startswith(("wall", "fence")) \
                    and self.surface[y][x] in ("path", "water"):
                out.append(f"{c['id']} @({x},{y}) sits on '{self.surface[y][x]}' (road/plaza/water under a wall)")

        # wall / door / window heights must match
        placed = {c["id"] for c in self.occ.values()}
        def heights(pred): return sorted({(m.get(o, {}) or {}).get("sprite_h") for o in placed if pred(o)} - {None})
        wh, dh, nh = heights(lambda o: o.startswith("wall")), heights(lambda o: o.startswith("door")), heights(lambda o: o.startswith("window"))
        allh = set(wh) | set(dh) | set(nh)
        if len(allh) > 1:
            out.append(f"HEIGHT mismatch — walls{wh} doors{dh} windows{nh} (px); should all match")

        # checkered roads: dirt POTHOLES inside stone roads (a dirt path cell mostly
        # surrounded by stone path = checkering). LOCAL, not a global ratio — a zone
        # legitimately mixes stone roads with all-dirt lanes (the road hierarchy), and
        # edge_tile fraying puts dirt on shoulders (≤1 stone neighbor), so only
        # interior specks (≥3 stone path neighbors) count.
        stone_cells = potholes = 0
        for y in range(self.H):
            for x in range(self.W):
                if self.surface[y][x] != "path":
                    continue
                g = self.ground[y][x]
                if g.startswith("stone_path"):
                    stone_cells += 1
                elif g == "dirt":
                    stony = sum(1 for (nx, ny) in ((x+1, y), (x-1, y), (x, y+1), (x, y-1))
                                if self.in_bounds(nx, ny) and self.surface[ny][nx] == "path"
                                and self.ground[ny][nx].startswith("stone_path"))
                    if stony >= 3:
                        potholes += 1
        if stone_cells and potholes * 20 > stone_cells:  # >5% potholes
            out.append(f"ROADS checkered: {potholes} dirt potholes inside {stone_cells} "
                       f"stone road cells — muddy, not a clean road")

        # walls/fences standing on a road TILE — the safety net behind the place-time
        # warn (place_occupant overwrites the surface mask, so this reads the GROUND,
        # which buildings never touch). Gates/doors are excluded: a path running
        # through an opening is correct. Plain "dirt" is excluded too (forest floors
        # use it without being roads).
        road_tiles = {"stone_path", "dirt_path", "cobblestone"}
        for (x, y), c in self.occ.items():
            if not c.get("anchor") or not c["id"].startswith(("wall", "fence")):
                continue
            fw, fh = self.footprint(c["id"])
            on_road = [(x + dx, y + dy) for dy in range(fh) for dx in range(fw)
                       if self.in_bounds(x + dx, y + dy)
                       and self.ground[y + dy][x + dx] in road_tiles]
            if on_road:
                out.append(f"{c['id']} @({x},{y}) stands on road tiles {on_road} "
                           f"(wall/fence over a road)")

        # ROAD THROUGH A BUILDING (2026-06, the living-room road): a path cell
        # with building WALLS on both OPPOSITE sides means a road threaded a
        # building's interior (path() skip-paints reserved cells but marches
        # on). place_house/shop_building now reserve interiors and path()
        # warns on crossings; this is the net behind both.
        # (constructed walls only — a tunnel path between cave ROCK blocks is
        # correct, so category=="block" must not count here)
        def is_built_wall(o): return bool(o) and o.startswith("wall")
        for y in range(self.H):
            for x in range(self.W):
                if self.surface[y][x] != "path":
                    continue
                if (is_built_wall(oid(x - 1, y)) and is_built_wall(oid(x + 1, y))) or \
                        (is_built_wall(oid(x, y - 1)) and is_built_wall(oid(x, y + 1))):
                    out.append(f"road at ({x},{y}) runs THROUGH a building "
                               f"(walls on both sides)")

        # TALL-SPRITE OVERHANG: a tree directly SOUTH of a road cell draws its
        # ~2-cell-tall canopy OVER the roadway (the visual-clipping class that
        # on-tile checks miss). clear_road_margins() removes these; this is the net.
        for (x, y), c in self.occ.items():
            if c.get("anchor") and c["id"].startswith("tree") and self.in_bounds(x, y + 1) \
                    and self.surface[y + 1][x] == "path":
                out.append(f"{c['id']} @({x},{y}) overhangs the road north of it "
                           f"(tall sprite over the roadway)")

        # spawn circles mostly over water (the lakeside forest-patch lesson, 2026-06:
        # a circle's content must be REACHABLE habitat). bug_spawning is set on the
        # builder before lint in the standard flow; scenes without it no-op.
        for area in (self.bug_spawning or {}).get("spawn_areas", []):
            if area.get("type") != "circle":
                continue
            acx, acy, r = area.get("cx", 0), area.get("cy", 0), area.get("radius", 0)
            cells = wet = 0
            for yy in range(max(0, int(acy - r)), min(self.H, int(acy + r) + 1)):
                for xx in range(max(0, int(acx - r)), min(self.W, int(acx + r) + 1)):
                    if (xx - acx) ** 2 + (yy - acy) ** 2 <= r * r:
                        cells += 1
                        if self.surface[yy][xx] == "water":
                            wet += 1
            if cells and wet * 2 > cells:
                out.append(f"SPAWN AREA '{area.get('id', '?')}' circle ({acx},{acy} r{r}) "
                           f"is {100 * wet // cells}% water — bugs spawn over a lake")
        return out

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
            "zone_id": self.zone_id, "name": self.name,
            "row": self.grid[0], "col": self.grid[1],
            "width": self.W, "height": self.H, "spawn_point": list(self.spawn),
            "biome_type": self.biome, "seed": self.seed,
        }
        if self.neighbors:
            cfg["neighbors"] = dict(self.neighbors)
        if self.bug_spawning is not None:
            cfg["bug_spawning"] = self.bug_spawning
        if self.peaceful:
            cfg["peaceful"] = True
        if self.ephemeral_swarms:
            cfg["ephemeral_swarms"] = True
        with open(os.path.join(out, "zone.json"), "w") as f:
            json.dump(cfg, f, indent=2)
        cw, ch = self._chunk_counts()
        for cy in range(ch):
            for cx in range(cw):
                ground = [[self.ground[cy * CHUNK + ly][cx * CHUNK + lx] for lx in range(CHUNK)]
                          for ly in range(CHUNK)]
                occ = [[self.occ.get((cx * CHUNK + lx, cy * CHUNK + ly)) for lx in range(CHUNK)]
                       for ly in range(CHUNK)]
                chunk_obj = {"chunk_x": cx, "chunk_y": cy, "ground": ground, "occupants": occ}
                # Roof: only emit for chunks that actually have roofed cells (json:"roof,omitempty"
                # on the Go side treats a missing array as all-lit — so surface zones stay unbloated).
                roof = [[self.roof[cy * CHUNK + ly][cx * CHUNK + lx] for lx in range(CHUNK)]
                        for ly in range(CHUNK)]
                if any(any(row) for row in roof):
                    chunk_obj["roof"] = roof
                with open(os.path.join(out, f"chunk_{cx}_{cy}.json"), "w") as f:
                    json.dump(chunk_obj, f)
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
        b.peaceful = bool(cfg.get("peaceful", False))
        b.ephemeral_swarms = bool(cfg.get("ephemeral_swarms", False))
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
