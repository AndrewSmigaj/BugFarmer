#!/usr/bin/env python3
"""placeholder_sprites — Pipeline-B (manual, NO API) placeholder art.

Emits a flat colored square PNG + a Unity Single-mode .meta for ids that don't
have real art yet, so new items/placeables/occupants are fully functional in
engine while their real sprites are tracked in `docs/product/art_needed.md` and
generated later (gpt-image-1 for world art, generate_player_sprites for NPCs).

The colour is a deterministic hash of the id (so the same id is always the same
hue) with a dark rim and a 2–3 char label for at-a-glance identification. This
is intentionally ugly — placeholders should read as "not final art".

Usage:
  python3 tools/sprites/placeholder_sprites.py --folder Items  --suffix _icon --size 16   id1 id2 ...
  python3 tools/sprites/placeholder_sprites.py --folder Objects --size 16x16              id1 id2 ...
  # or feed a file of ids (one per line):
  python3 tools/sprites/placeholder_sprites.py --folder Items --suffix _icon --ids-file /tmp/ids.txt

Writes under BugFarmerClient/Assets/Resources/<folder>/. Never overwrites an
existing NON-placeholder PNG unless --force (a placeholder is recognised by a
marker chunk in its .meta userData).
"""
import argparse
import colorsys
import hashlib
import os
import uuid

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(REPO, "BugFarmerClient", "Assets", "Resources")
PLACEHOLDER_MARKER = "placeholder_sprite"  # written into .meta userData

META_TMPL = """fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 12
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
  isReadable: 0
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: 16
  alphaIsTransparency: 1
  textureType: 8
  textureShape: 1
  textureSettings:
    serializedVersion: 2
    filterMode: 0
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
  nPOTScale: 0
  spriteGenerateFallbackPhysicsShape: 1
  userData: {marker}
  assetBundleName:
  assetBundleVariant:
"""


def _hue(id_str):
    h = int(hashlib.md5(id_str.encode()).hexdigest(), 16)
    hue = (h % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.85)
    return int(r * 255), int(g * 255), int(b * 255)


def _label(id_str):
    parts = id_str.replace("-", "_").split("_")
    if len(parts) >= 2:
        return (parts[0][:1] + parts[1][:1]).upper()
    return id_str[:2].upper()


def make_placeholder(id_str, folder, suffix, w, h, force=False):
    out_dir = os.path.join(RES, folder)
    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, f"{id_str}{suffix}.png")
    meta = png + ".meta"
    if os.path.exists(png) and not force:
        # only refuse to clobber REAL art (a placeholder meta carries the marker)
        is_ph = os.path.exists(meta) and PLACEHOLDER_MARKER in open(meta).read()
        if not is_ph:
            return f"skip (real art exists): {png}"

    r, g, b = _hue(id_str)
    im = Image.new("RGBA", (w, h), (r, g, b, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(24, 20, 24, 255))  # dark rim
    label = _label(id_str)
    try:
        d.text((2, h // 2 - 4), label, fill=(24, 20, 24, 255))
    except Exception:
        pass
    im.save(png)
    with open(meta, "w") as f:
        f.write(META_TMPL.format(guid=uuid.uuid4().hex, marker=PLACEHOLDER_MARKER))
    return f"wrote {png} ({w}x{h}, {label})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True, help="Resources subfolder (Items|Objects|Bugs|Effects)")
    ap.add_argument("--suffix", default="", help="filename suffix (e.g. _icon for item icons)")
    ap.add_argument("--size", default="16", help="WxH or single N for square")
    ap.add_argument("--ids-file", help="file with one id per line")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("ids", nargs="*")
    a = ap.parse_args()

    if "x" in a.size:
        w, h = (int(x) for x in a.size.lower().split("x"))
    else:
        w = h = int(a.size)

    ids = list(a.ids)
    if a.ids_file:
        ids += [ln.strip() for ln in open(a.ids_file) if ln.strip() and not ln.startswith("#")]
    if not ids:
        ap.error("no ids given")

    for i in ids:
        print(make_placeholder(i, a.folder, a.suffix, w, h, a.force))


if __name__ == "__main__":
    main()
