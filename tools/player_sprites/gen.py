"""gen.py — the ONLY way a player sprite gets generated.

Everything that made an image is written next to the image. Nothing about a run lives in my head or in the
chat, because that is exactly what kept getting lost: the prompt, which model, which references, when. Each
run creates one timestamped folder holding the result, the exact references that were sent, and a plain-text
record you can read without asking me. One line per run is appended to RUNS.txt so there is a single file
that says what exists and where.

Layout (fixed — do not invent another one). There is ONE player folder and four things in it:
    tools/_generated/player/bases/        the current official sprites, nothing else
    tools/_generated/player/<dest>/          e.g. outfits/bronze, hands
        result.png        what came back
        RECORD.txt        prompt, model, references, timestamp
        ref_1_<name>.png  every reference exactly as sent
    tools/_generated/player/current/      what is live in the game
    tools/_generated/player/old/          archive
    tools/_generated/player/RUNS.txt      one line per run, newest last

  python3 tools/player_sprites/gen.py --dest hands --prompt "..." \
      --ref tools/_generated/player/bases/armless_front.png

Folders are named for WHAT IS IN THEM, not for how they were made — looking for the bronze armour should mean
knowing it is called bronze, not knowing which run produced it.
"""
import argparse
import datetime
import json
import os
import shutil
import base64
import urllib.request

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites"))
import gen_sprites as _gen                                   # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.join(REPO, "tools", "_generated", "player")
RUNS = os.path.join(ROOT, "RUNS.txt")
BASES = os.path.join(ROOT, "bases")

# The model lives HERE and nowhere else, so it cannot drift between calls. Every RECORD.txt states which
# model actually ran, so a change is visible after the fact too.
MODEL = "gpt-image-2"
SIZE = "1024x1536"
QUALITY = "high"


def call(prompt, refs, model, size, quality):
    """gpt-image edit with NO mask. A mask is what turned earlier runs into black boxes."""
    b = "----bf-gen"
    parts = []

    def field(k, v):
        parts.append((f"--{b}\r\nContent-Disposition: form-data; "
                      f"name=\"{k}\"\r\n\r\n{v}\r\n").encode())

    for k, v in [("model", model), ("prompt", prompt), ("size", size),
                 ("quality", quality), ("n", "1")]:
        field(k, v)
    for i, p in enumerate(refs):
        parts.append((f"--{b}\r\nContent-Disposition: form-data; name=\"image[]\"; "
                      f"filename=\"ref{i}.png\"\r\nContent-Type: image/png\r\n\r\n").encode()
                     + open(p, "rb").read() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(
        _gen.EDIT_URL, data=b"".join(parts),
        headers={"Authorization": f"Bearer {_gen.resolve_api_key()}",
                 "Content-Type": f"multipart/form-data; boundary={b}"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as r:
        return base64.b64decode(json.loads(r.read())["data"][0]["b64_json"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True,
                    help="where it goes, relative to tools/_generated/player — e.g. 'outfits/bronze', 'hands'")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--ref", action="append", default=[], help="reference image; repeatable, order matters")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--size", default=SIZE)
    ap.add_argument("--quality", default=QUALITY)
    ap.add_argument("--scale", type=int, default=14,
                    help="nearest-neighbour upscale applied to every reference before sending; the bases "
                         "are game-size sprites and the model needs a bigger image to read them")
    ap.add_argument("--dry-run", action="store_true", help="write the folder + RECORD, spend nothing")
    a = ap.parse_args()

    now = datetime.datetime.now()
    out = os.path.join(ROOT, a.dest)
    os.makedirs(out, exist_ok=True)

    # Upscale each reference and send THAT, so what is recorded is exactly what the model saw.
    from PIL import Image
    kept, how = [], []
    for i, p in enumerate(a.ref, 1):
        if not os.path.exists(p):
            raise SystemExit(f"reference not found: {p}")
        dst = os.path.join(out, f"ref_{i}_{os.path.basename(p)}")
        im = Image.open(p).convert("RGBA")
        # Only tiny references get upscaled — a sprite needs it so the model can see the shapes; an
        # already-large sheet does not, and blowing one up to 30+ megapixels would be rejected.
        if a.scale > 1 and max(im.size) < 400:
            im = im.resize((im.width * a.scale, im.height * a.scale), Image.NEAREST)
            how.append(f"upscaled x{a.scale} -> {im.width}x{im.height}")
        else:
            how.append(f"sent as-is at {im.width}x{im.height}")
        im.save(dst)
        kept.append(dst)

    with open(os.path.join(out, "RECORD.txt"), "w") as f:
        f.write(f"when      : {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"model     : {a.model}\nsize      : {a.size}\nquality   : {a.quality}\nmask      : NONE\n")
        f.write(f"dest      : {a.dest}\n")
        f.write("references (in the order sent):\n")
        # Record what ACTUALLY happened to each reference, not the flag. This line used to say
        # "sent upscaled x14" unconditionally, including when the size guard skipped the upscale —
        # a record that states an intention rather than a fact is worse than no record.
        for i, (p, note) in enumerate(zip(a.ref, how), 1):
            f.write(f"  {i}. {os.path.relpath(p, REPO)}  ({note})\n")
        f.write(f"\nPROMPT:\n{a.prompt}\n")

    if a.dry_run:
        print("DRY RUN — nothing spent")
    else:
        # WRITE ATOMICALLY: fetch fully into memory, write a temp file, then rename.
        #
        # This used to be `open(dest,"wb").write(call(...))`. Python evaluates `open()` FIRST, so the
        # destination was created and truncated to zero BEFORE the paid call was even made — and if the
        # call then raised, or the process was interrupted mid-flight, what survived was a 0-byte
        # `result.png` that looks like a generated file. That has happened twice (ant-carapace-black,
        # and fireant on 2026-08-06), and in both cases it was impossible to tell afterwards whether the
        # money had been spent. Now: no bytes, no file.
        data = call(a.prompt, kept, a.model, a.size, a.quality)
        if not data:
            raise SystemExit("the API returned no image data — nothing written")
        dest = os.path.join(out, "result.png")
        tmp = dest + ".part"
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, dest)
        print(f"  received {len(data) / 1024:.0f} KB")

    os.makedirs(ROOT, exist_ok=True)
    with open(RUNS, "a") as f:
        f.write(f"{now.strftime('%Y-%m-%d %H:%M')}  {a.model:14} {a.dest:28} "
                f"{'(dry-run)' if a.dry_run else os.path.relpath(out, REPO)}\n")

    print(f"\nFOLDER : {out.replace('/mnt/c/', 'C:/')}")
    print(f"RESULT : {os.path.join(out, 'result.png').replace('/mnt/c/', 'C:/')}")
    print(f"RECORD : RECORD.txt in that folder has the prompt, model and references")
    print(f"LOG    : {RUNS.replace('/mnt/c/', 'C:/')}")


if __name__ == "__main__":
    main()
