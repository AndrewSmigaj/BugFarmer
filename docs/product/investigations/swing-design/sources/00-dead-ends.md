# Dead ends — searched, read, contributed nothing
Recorded so the same ground isn't covered twice, and so the source count isn't inflated by
things that yielded nothing. These are NOT counted toward the source quota.

## Terraria tool/weapon animation internals
terraria.wiki.gg + fandom wiki, 2026-07-29. The wikis document `use time` as a stat and note that
drills/chainsaws are "alternate animations" of pickaxes/axes, but carry no arc, rotation or frame data.
Mechanically Terraria is our closest cousin (same tool AND weapon set, rotating held sprite) so this is a
genuine loss, not a shrug — the information would need extracting from the game itself.

## Zelda: A Link to the Past sword frame data
zeldix.net/t1877, 2026-07-29. The thread is people asking for exactly this data and not having it.
ZoriaRPG: "I do not know how the movement works in-ROM"; "commented disassembly does not exist for this."
Getting it would mean tracing the ASM in a debugger. Not worth it for this run.

## Weapon-trail VFX search
Returned Unreal/Niagara marketplace material and stock art. We already have a TrailRenderer wired to the
swing, so there was nothing to gain.
