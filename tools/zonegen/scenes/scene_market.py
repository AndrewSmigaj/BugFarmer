#!/usr/bin/env python3
"""Building piece — the MARKET (general store). A SHOP main room (shelving, the merchant behind the
counter, produce crates + barrels) over a back STOREROOM (stock: crates, barrels, chests, produce),
connected by an internal door, with a 3-wide market sign + produce stalls out front, in a fenced yard.

`place_market(b, ox, oy)` drops it into any builder; run directly to preview standalone ->
tools/_generated/previews/tests/scene_market.png.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ZG = os.path.dirname(HERE)
sys.path.insert(0, ZG)
from zonebuilder import ZoneBuilder                                   # noqa: E402
from render import render_builder                                     # noqa: E402
from features.tilemap import stamp, dump                              # noqa: E402
from features.yard import property_yard                               # noqa: E402

# 12 wide x 14 tall: STOREROOM (north) over the SHOP (south, with the front door). Merchant 2 cells
# behind the counter; shelving split around the central aisle (cols stay clear under both doors).
MARKET = """
WWWWWWWWWWWW
Wc.b.h.b.c.W
W..........W
Wp..c.b..p.W
WWWWWDWWWWWW
W..........W
WS.S..S.S..W
W..........W
W....M.....W
W..........W
W....C.....W
Wp.b....b.pW
W.c......c.W
WWWWWDWWWWWW
"""
LEG = {"W": ("occ", "wall_wood"), "D": ("occ", "door_square"), "c": ("occ", "crate"),
       "b": ("occ", "barrel"), "h": ("occ", "chest_wood"), "p": ("occ", "produce_crate"),
       "S": ("occ", "shop_shelving"), "M": ("npc", "merchant_down"), "C": ("occ", "counter"),
       ".": ("floor",)}

BW, BH, DOORX = 12, 14, 5


def place_market(b, ox, oy):
    """Drop the market (SW corner ox,oy). Open-fronted (no fence) — building, a 3-wide sign, and produce
    stalls out front. Door faces south at ox+DOORX. Returns the building rect."""
    stamp(b, MARKET, LEG, ox=ox, oy=oy)
    b.place_occupant("sign_market_board", ox + 1, oy - 1, surface="grass")   # 3-wide sign, left of the door
    # the produce STALL LINE: one straight row under the frontage (rows discipline —
    # market goods sit in a line, not sprinkled)
    for (oid, x, y) in [("produce_crate", ox + DOORX + 2, oy - 1), ("produce_crate", ox + DOORX + 3, oy - 1),
                        ("produce_crate", ox + DOORX + 4, oy - 1), ("barrel", ox + DOORX + 5, oy - 1)]:
        fw, fh = b.footprint(oid)
        if all(b.in_bounds(x + dx, y + dy) and b.is_free(x + dx, y + dy)
               for dx in range(fw) for dy in range(fh)):
            b.place_occupant(oid, x, y, surface="grass")
    return (ox, oy, ox + BW - 1, oy + BH - 1)


def build():
    b = ZoneBuilder("scene_market", BW + 8, BH + 12, base_tile="grass", name="Market")
    place_market(b, 4, 7)
    b.spawn = [4 + DOORX, 1]
    return b


if __name__ == "__main__":
    b = build()
    out = os.path.abspath(os.path.join(ZG, "..", "_generated", "previews", "tests", "scene_market.png"))
    render_builder(b, out, scale=10)
    print(dump(b, 4, 7, 15, 20))
    print("LINT:", b.lint() or "0 defects", "| warnings:", len(b.warnings), "| missing_art:", b.missing_art())
    print("rendered ->", out)
