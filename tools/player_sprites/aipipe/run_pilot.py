"""Full-outfit pilot (front view): generate a leather set on the mannequin, extract each
piece with a shared palette, and stack them in draw order into a dressed character.
Validates the committed pipeline end-to-end + multi-item composition."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # tools/player_sprites
from aipipe import common as C
import numpy as np
from PIL import Image, ImageDraw

DIR = sys.argv[1] if len(sys.argv) > 1 else "down"
SETNAME = sys.argv[2] if len(sys.argv) > 2 else "leather"
REFS = "tools/_generated/player/references"   # base/bald/mannequin the owner masks against
OUT = f"tools/_generated/player/old/_pilot/{DIR}"   # validation-spike output; kept OUT of in-progress/
os.makedirs(OUT, exist_ok=True)

base = C.load_rgba(REFS + "/base.png")   # haired base (front); side views not produced yet
# the DUMMY we paint gear onto is BALD (if we have one for this dir) so head gear sits on a clean
# scalp; body/proportions are identical to the haired base, so gear still lands correctly.
baldp = REFS + "/bald.png"
man = C.make_mannequin(C.load_rgba(baldp) if os.path.exists(baldp) else base, "green")
manp = OUT + f"/mannequin_{DIR}.png"
C.save_rgba(man, manp)

# draw order (back->front) = legs, feet, torso, head — matches CharacterComposer.
SETS = {
    "leather": [
        ("legs",  "leather_leg_armor", "brown LEATHER leg armor — full-length leather leggings/trousers that "
                                       "cover the ENTIRE thighs, knees and shins with NO bare skin showing"),
        ("feet",  "leather_boots",  "brown LEATHER boots worn on the feet and lower legs"),
        ("torso", "leather_chest",  "a rugged brown LEATHER chest tunic with stitching, straps and buckles "
                                    "and small shoulder pads, worn on the torso"),
        ("head",  "leather_cap",    "a simple brown LEATHER cap sized to fit over the character's hair; keep "
                                    "the head the same size, do not shrink it"),
    ],
    "steel": [
        ("legs",  "steel_leg_armor", "STEEL PLATE leg armor — metallic grey steel greaves/leggings covering "
                                     "the ENTIRE thighs, knees and shins with NO bare skin showing"),
        ("feet",  "steel_boots",  "STEEL PLATE armored boots, metallic grey steel with a cuff"),
        ("torso", "steel_chest",  "a STEEL PLATE chestplate with rounded shoulder pauldrons and straps, "
                                  "polished metallic grey steel, worn on the torso"),
        ("head",  "steel_helmet", "a STEEL helmet that fits over the top of the character's head, metallic "
                                  "grey steel; keep the head the same size, do not shrink it"),
    ],
}
ITEMS = SETS[SETNAME]

y0, y1, x0, x1 = C.char_bbox(base)
def small(a):
    return np.asarray(Image.fromarray(a[y0:y1 + 1, x0:x1 + 1], "RGBA").resize((C.NATIVE_W, C.NATIVE_H), Image.BOX), np.uint8)
def opq(s):
    return s[..., :3].reshape(-1, 3)[s[..., 3].reshape(-1) >= 128]

# 1. generate + align every piece on the mannequin
renders = []
for slot, iid, noun in ITEMS:
    region = C.slot_region(base, slot)
    maskp = OUT + f"/{iid}_mask.png"
    C.region_mask_png(base.shape, region, maskp)
    prompt = (f"This is an edit that adds ONLY the {slot} gear and changes NOTHING else. {noun}, worn by the "
              f"green figure in the image. CRITICAL: keep the character's HEIGHT, body size, proportions, pose "
              f"and position EXACTLY identical — do NOT resize, shrink, enlarge or redraw the body. Everything "
              f"outside the {slot} stays exactly the same green figure. Paint ONLY inside the editable region. "
              f"{C.STYLE}")
    print(f"[gen] {iid}", flush=True)
    png = C.masked_edit(manp, maskp, prompt)
    editp = OUT + f"/{iid}_gen.png"
    open(editp, "wb").write(png)
    edit = C.load_rgba(editp)
    # robust scale+position correct onto the mannequin (== base coords); no second align needed.
    # head gear replaces the head's look, so anchor it on the TORSO (green in both); else the head.
    band = (0.34, 0.64) if slot == "head" else (0.0, 0.32)
    sedit, scale, dx, dy = C.normalize_align(man, edit, match_band=band)
    smask = region
    renders.append((slot, iid, sedit, smask))
    print(f"  [ok] scale={scale:.3f} dx={dx} dy={dy}", flush=True)

# 2. one SHARED palette (base + every render) so all layers agree on colour
pool = [opq(small(base))]
for _, _, sedit, smask in renders:
    comp = base.copy(); comp[smask] = sedit[smask]
    pool.append(opq(small(comp)))
pal = C._pc.build_palette(np.concatenate(pool, 0), 26)

# 3. extract each layer with the shared palette
layers = {}
bsn = ba = None
for slot, iid, sedit, smask in renders:
    layer, gear, (bsn, ba) = C.extract_layer(base, sedit, smask, "green", palette=pal)
    layers[slot] = layer
    C.save_rgba(layer, OUT + f"/layer_{slot}_{iid}.png")
    print(f"  [extract] {iid} px={int(gear.sum())}", flush=True)

# 4. compose in draw order
order = ["legs", "feet", "torso", "head"]
dressed = C.compose_layers(bsn, ba, [layers[s] for s in order if s in layers])
naked = np.dstack([bsn, ba]).astype(np.uint8)

# preview: naked base | dressed, x8
SC = 8
def big(arr):
    return Image.fromarray(arr, "RGBA").resize((C.NATIVE_W * SC, C.NATIVE_H * SC), Image.NEAREST)
GAP, HEAD = 20, 26
w = GAP + (C.NATIVE_W * SC + GAP) * 2
sheet = Image.new("RGBA", (w, HEAD + C.NATIVE_H * SC + GAP), (40, 40, 46, 255))
d = ImageDraw.Draw(sheet)
d.text((GAP + 2, 6), f"base ({C.NATIVE_W}x{C.NATIVE_H})", fill=(235, 235, 240, 255))
sheet.alpha_composite(big(naked), (GAP, HEAD))
x2 = GAP + C.NATIVE_W * SC + GAP
d.text((x2 + 2, 6), f"DRESSED ({SETNAME})", fill=(235, 235, 240, 255))
sheet.alpha_composite(big(dressed), (x2, HEAD))
sheet.convert("RGB").save(OUT + f"/_pilot_dressed_{SETNAME}.png")
print("[done]", OUT + "/_pilot_dressed.png", flush=True)
