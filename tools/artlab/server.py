#!/usr/bin/env python3
"""Art Lab — local dev server to see art variants in real scenes and pick which to use.

  python3 tools/artlab/server.py        # then open http://localhost:8765

Lazy: a scene renders on first view (cached); the variant you select is overlaid live (back-to-front).
**Apply** promotes the chosen variants to the live game sprites (+.meta) and re-renders the scenes that
contain them. Selection persists in variants/selection.json and is loaded on open (remembered).

Pieces it ties together (each its own concern):
  zonegen/registry.py — the scene catalog (scene -> zone + canonical scale); renders
                        previews/<zone>/<scene>.png. Owned by the authoring system; we consume it.
  library.py          — variant library (variants/<key>/), selection, promote-to-live
"""
import http.server
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # tools/artlab
TOOLS = os.path.dirname(HERE)                              # tools
for p in (HERE, os.path.join(TOOLS, "zonegen")):
    if p not in sys.path:
        sys.path.insert(0, p)
import registry as scenes                                  # the scene catalog (authoring system)  # noqa: E402
import library                                             # noqa: E402

PORT = 8765
APP = os.path.join(HERE, "app")
_cache = {}                                                # scene name -> rendered state (rects, size)


def _record_keys():
    return set(library.library()) & library.tile_keys()    # tile keys we have variants for (record floor cells)


def scene_state(name, force=False):
    if force or name not in _cache:
        r = scenes.render_one(name, record_tiles=_record_keys())
        lib = library.library()
        draw = [{"key": rc["key"], "x": rc["x"], "y": rc["y"], "w": rc["w"], "h": rc["h"]}
                for rc in r["block_rects"] if rc["key"] in lib]
        zone = scenes.zone_of(name)
        _cache[name] = {"name": name, "zone": zone, "file": f"{zone}/{name}.png",
                        "w": r["w"], "h": r["h"], "draw": draw,
                        "keys": list(dict.fromkeys(d["key"] for d in draw))}
    return _cache[name]


def state():
    zones = {}
    for n in scenes.REGISTRY:
        zones.setdefault(scenes.zone_of(n), []).append(n)
    return {"zones": zones, "variants": library.library(), "selection": library.load_selection()}


def apply(sel):
    applied = [k for k, fn in sel.items() if library.promote(k, fn)]
    library.save_selection(sel)
    for name, sc in list(_cache.items()):                  # re-render only cached scenes that use a changed key
        if set(sc["keys"]) & set(applied):
            scene_state(name, force=True)
    return applied


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
        with open(path, "rb") as f:
            self._send(200, f.read(), _CT.get(os.path.splitext(path)[1], "application/octet-stream"))

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/", "/index.html"):
            return self._file(os.path.join(APP, "index.html"))
        if p == "/api/state":
            return self._send(200, json.dumps(state()))
        if p.startswith("/api/scene/"):
            name = p[len("/api/scene/"):]
            if name not in scenes.REGISTRY:
                return self._send(404, "unknown scene", "text/plain")
            return self._send(200, json.dumps(scene_state(name)))
        if p.startswith("/scene/"):
            rel = p[len("/scene/"):]
            return self._safe(scenes.PREVIEWS, rel)
        if p.startswith("/variant/"):
            rel = p[len("/variant/"):]
            return self._safe(library.VARIANTS, rel)
        if p.startswith("/app/"):
            return self._file(os.path.join(APP, os.path.basename(p)))
        return self._send(404, "not found", "text/plain")

    def _safe(self, root, rel):
        if ".." in rel:
            return self._send(403, "no", "text/plain")
        return self._file(os.path.join(root, rel))

    def do_POST(self):
        p = self.path.split("?")[0]
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0) or b"{}")
        if p == "/api/apply":
            applied = apply(body.get("selection", {}))
            return self._send(200, json.dumps({"applied": applied}))
        return self._send(404, "not found", "text/plain")

    def log_message(self, *a):
        pass


def main():
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Art Lab ready -> http://localhost:{PORT}   (Ctrl-C to stop)")
    print(f"  scenes: {len(scenes.REGISTRY)} | variant keys: {list(library.library())}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
