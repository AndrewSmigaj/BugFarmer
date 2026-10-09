# darkness-check

The darkness overlay's maths against the overlay as it was before Stage 1.5 (`docs/plans/village-slice.md`).

- `../../BugFarmerClient/Assets/Scripts/World/Rendering/DarknessField.cs` is **linked**, not copied: the check always
  runs the client's own code.
- `OldOverlay.cs` is the overlay's maths at 246c217a (one 256 × 256 texture, nine-read blur, lamps stamped into the
  whole texture), with only the texture plumbing taken out. It is the reference: never edit it to match new code.
- `Program.cs` builds both on 12 random 256 zones (block masses, scattered blocks, roofed caves, cells outside the
  zone), compares 25 camera windows each (the whole zone, corners, anywhere) with lamps inside, outside and across the
  window's edges, and every cell's "underground darkness"; then six checks on a 512 zone.

```bash
~/.dotnet/dotnet run --project tools/darkness-check     # exit 0 = the same picture (one shade of 255 allowed)
```

Built copies of the game can't draw the overlay (its shader is missing from builds — BACKLOG), so this is the only
headless check of it. A planted fault (lamps skipping a window's last column) was caught on 2026-10-09.
