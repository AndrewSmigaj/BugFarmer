#!/usr/bin/env python3
"""BugFarmer design lab — a small local dev server for picking art variants inside real scenes.

  python3 tools/lab_server.py        # then open http://localhost:8765

ONE set of scenes: it renders the actual scene scripts to tools/_generated/previews/ (the same folder we
already use), recording each swappable block/tile's exact draw-rect. The web app overlays your chosen
variant on those previews (instant flip). **Apply** promotes the chosen variants to the live game sprites
(+ .meta) AND re-renders the previews, so the previews always reflect the current selection. The selection
persists in tools/_generated/blocklab/selection.json and is loaded on open (remembered).

Designed to grow: add more "labs" (item-icon design, zone layout) as new /api routes + app pages later.
This file stays the single, organized entry point.
"""
import http.server
import io
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "zonegen"))
sys.path.insert(0, os.path.join(HERE, "zonegen", "scenes"))
from render import render_builder        # noqa: E402
import gen_sprites as g                   # noqa: E402

REPO = g.REPO
LAB = os.path.join(HERE, "_generated", "blocklab")
PREVIEWS = os.path.join(HERE, "_generated", "previews")
SEL_PATH = os.path.join(LAB, "selection.json")
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")
APP = os.path.join(HERE, "lab")

APPROACHES = ["01_described", "02_explicit_dimensions", "03_grid_check"]
# (display name -> scene module, render scale). The SAME scene scripts that produce the previews.
SCENES = {
    "cavern": ("scene_underground_caverns", 2),
    "mining_camp": ("scene_underground_mining_camp", 2),
    "underground_house": ("scene_underground_house", 3),
    "cliff": ("scene_block_mine", 4),
    "houses": ("scene_block_house", 5),
    "desert": ("scene_desert", 2),
}
PORT = 8765

_STATE = {}   # cached: {"scenes":..., "variants":..., "selection":...}


# ----- variant library + selection -------------------------------------------------------------
def variant_library():
    lib = {}
    for ap in APPROACHES:
        d = os.path.join(LAB, ap)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".png"):
                    lib.setdefault(f.rsplit("_", 1)[0], {}).setdefault(ap, []).append(f"{ap}/{f}")
    tdir = os.path.join(LAB, "tiles")
    if os.path.isdir(tdir):
        for f in sorted(os.listdir(tdir)):
            if f.endswith(".png"):
                lib.setdefault(f.rsplit("_", 1)[0], {}).setdefault("tile", []).append(f"tiles/{f}")
    return lib


def load_selection():
    if os.path.exists(SEL_PATH):
        try:
            return json.load(open(SEL_PATH))
        except Exception:
            pass
    return {}


def save_selection(sel):
    os.makedirs(LAB, exist_ok=True)
    json.dump(sel, open(SEL_PATH, "w"), indent=2)


def is_tile_variant(relpath):
    return relpath.startswith("tiles/")


def live_path(key, relpath):
    sub = "Tiles" if is_tile_variant(relpath) else "Objects"
    return os.path.join(RES, sub, f"{key}.png")


# ----- render the scenes (the one preview set) + capture rects ----------------------------------
def render_scenes(swappable_keys, tile_keys):
    os.makedirs(PREVIEWS, exist_ok=True)
    scenes = {}
    for name, (mod_name, scale) in SCENES.items():
        try:
            mod = __import__(mod_name)
            b = mod.build()
            out = os.path.join(PREVIEWS, f"{mod_name}.png")        # the real preview filename
            r = render_builder(b, out, scale=scale, record_tiles=tile_keys)
        except Exception as e:
            print(f"  SKIP scene {name}: {str(e)[:140]}")
            continue
        draw = [{"key": rc["key"], "x": rc["x"], "y": rc["y"], "w": rc["w"], "h": rc["h"]}
                for rc in r["block_rects"] if rc["key"] in swappable_keys]
        keys = list(dict.fromkeys(d["key"] for d in draw))
        scenes[name] = {"file": f"{mod_name}.png", "w": r["w"], "h": r["h"], "draw": draw, "keys": keys}
        print(f"  {name}: {len(draw)} swappable cells {keys}")
    return scenes


def build_state(rerender=True):
    lib = variant_library()
    tile_keys = {k for k, aps in lib.items() if "tile" in aps}
    if rerender or "scenes" not in _STATE:
        print("rendering scenes -> previews/ ...")
        _STATE["scenes"] = render_scenes(set(lib), tile_keys)
    _STATE["variants"] = lib
    _STATE["approaches"] = APPROACHES
    _STATE["selection"] = load_selection()
    return _STATE


# ----- apply: promote selected variants to live sprites, persist, re-render ---------------------
def apply_selection(sel):
    applied = []
    for key, relpath in sel.items():
        src = os.path.join(LAB, relpath)
        if not os.path.exists(src):
            continue
        dst = live_path(key, relpath)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        meta = g.patch_meta(dst)
        if "new" in str(meta):                                     # brand-new sprite: clone a sibling .meta
            _ensure_meta(dst)
        applied.append(key)
    save_selection(sel)
    build_state(rerender=True)                                     # previews now reflect the selection
    return applied


def _ensure_meta(dst):
    """If a new sprite has no .meta, clone one from a sibling in the same folder with a fresh guid."""
    import re
    import uuid
    folder = os.path.dirname(dst)
    sibling = next((os.path.join(folder, f) for f in os.listdir(folder)
                    if f.endswith(".png.meta") and f != os.path.basename(dst) + ".meta"), None)
    if sibling:
        m = re.sub(r"guid: [0-9a-f]{32}", "guid: " + uuid.uuid4().hex, open(sibling).read(), count=1)
        open(dst + ".meta", "w").write(m)


# ----- HTTP -------------------------------------------------------------------------------------
_CT = {".html": "text/html", ".js": "application/javascript", ".css": "text/css", ".png": "image/png"}


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path):
        if not os.path.isfile(path):
            return self._send(404, "not found", "text/plain")
        ext = os.path.splitext(path)[1]
        with open(path, "rb") as f:
            self._send(200, f.read(), _CT.get(ext, "application/octet-stream"))

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/", "/index.html"):
            return self._file(os.path.join(APP, "index.html"))
        if p == "/api/state":
            return self._send(200, json.dumps(build_state(rerender=False)))
        if p.startswith("/scene/"):
            return self._file(os.path.join(PREVIEWS, os.path.basename(p)))
        if p.startswith("/variant/"):
            rel = p[len("/variant/"):]
            if ".." in rel:
                return self._send(403, "no", "text/plain")
            return self._file(os.path.join(LAB, rel))
        if p.startswith("/app/"):
            return self._file(os.path.join(APP, os.path.basename(p)))
        return self._send(404, "not found", "text/plain")

    def do_POST(self):
        p = self.path.split("?")[0]
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if p == "/api/apply":
            applied = apply_selection(body.get("selection", {}))
            return self._send(200, json.dumps({"applied": applied, "state": _STATE}))
        return self._send(404, "not found", "text/plain")

    def log_message(self, *a):
        pass   # quiet


def main():
    print("Design lab — building initial state (rendering scenes once)…")
    build_state(rerender=True)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"\n  ✔ ready → open  http://localhost:{PORT}\n  (Ctrl-C to stop)\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
