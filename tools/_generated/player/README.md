# Player art — start here

Everything for the player character + wearables lives here. Four folders:

- **`current/`** — what's **LIVE in the game right now** (a preview + which attempt it came from). The real
  game files are in `BugFarmerClient/Assets/Resources/Player/layers/`; `current/` is the viewable snapshot.
- **`in-progress/`** — what you're **making**. One folder per item (e.g. `copper-armor/`), and inside it one
  folder per **attempt**, named by date: **`YYYY-MM-DD_HHMM_label/`**. The **newest date is the latest.** Each
  attempt has `suit.png` (the render you cut) + `pieces/` (the cut game pieces you export).
- **`references/`** — the `base` / `bald` / `mannequin` you mask against (one shared set for all attempts).
- **`old/`** — finished + abandoned stuff, out of the way. Ignore unless you're digging.
- **`HOW_TO_ASEPRITE.md`** — the masking tutorial.

## How to work
1. Open the item in `in-progress/<item>/<newest-date>/`.
2. Open its `suit.png` + `references/base.png` as layers in Aseprite; cut the pieces.
3. Save the cut pieces into that attempt's `pieces/`.
4. When you approve one, tell me — I publish its pieces to `Resources/Player/layers/` (the game updates),
   refresh `current/`, and log which attempt went live.

## Making a new thing
- New item → new folder `in-progress/<name>/` (e.g. `iron-helmet/`).
- New attempt at an existing item → a new **dated** folder `in-progress/<name>/YYYY-MM-DD_HHMM_label/`.
- **Never dump loose files** — always a dated attempt folder, so you can always tell attempts apart and find
  the latest one at a glance.

Governed by the `player-sprites` skill (`.claude/skills/player-sprites/SKILL.md`).
