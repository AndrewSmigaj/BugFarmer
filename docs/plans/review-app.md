# Plan — The review app: one page for zones, bugs, items and the design document

> One web page where the owner reviews everything with feedback beside what it's about. It is published over the
> items page so every mark carries over, and only after a rehearsal. Part A of
> [`finish-bugs-zones-items.md`](finish-bugs-zones-items.md).

## PROGRESS (newest last; the resume pointer)
- 2026-10-04: plan written (Part 0). Nothing built yet.
- 2026-10-04 (overnight, on auto):
  - **Built:** the registries and stable keys (`8341f16e`); the builder, the page and the screenshot check
    (`af9d5451`); the saving stress test (`65a34e77`): 11 scenarios with reloads, all passing, and planted faults
    caught.
  - **Found and fixed by the two-device scenario:** when another device's older answer lands after ours, storage
    kept it and the page never re-sent its newer one. The page now checks storage and re-sends, so the newest answer
    wins in the end.
  - **Added:** diagrams on explanation pages (```svg blocks, checked for scripts); two explanation pages
    (`docs/gdd/explain/`); `test_build_app.py` (a planted fault per builder check); `marks_diff.py` (manifest, diff,
    orphans) and `marks_restore.py` (a restore plan that never deletes).
  - **Dry-run export of the real marks** (read only) to `BugFarmer_backups/2026-10-04_review-app/dryrun-1/`:
    374 documents (373 marks in 7 kinds, plus the GDD page's one answer document); the old `item_marks` store and every
    new note and approval collection are empty; 35 filled marks sit on rows the item table no longer has, so the
    app's "Older notes" must list 35.
  - **Not done:** the rehearsal on a throwaway page and the publish (it waits for the owner's pause).

## Context / why
The owner reviews the design and can't do it in a terminal: they had to scroll back and forth to see what they were
answering (2026-10-03). Today there are two review pages, each with its own storage:
- **the GDD page** (https://claude.ai/artifact/CRtGxrNmWdXPVAVyNnwWW1), which holds one test answer;
- **the items page** (https://claude.ai/artifact/L9ftJfjRfcFD3yAB66qenD), which holds every mark.

A bug has four unconnected ids, there is no zone registry, and only 4 of 20 zones have map data. Settled cuts clutter
every list.

## Requirements (the owner's, restated and dated)
- **One app** holding zones (description, a map drawn in code, every bug that lives there), bugs, items with settled
  cuts archived, and the design sections. Feedback sits beside what it's about (2026-10-03).
- **A zone's high-level map is approved before any detail** (2026-10-03).
- **Bugs live in many zones.** Each zone lists what spawns there and what comes in from neighbours (2026-10-03; D53).
- **Explanations live in the app too**, as plain pages with diagrams (2026-10-03).
- **Sign-offs:** one per zone (map plus bug list), one per behaviour system, items by kind (2026-10-04).
- **The owner's words never go in the public repo.** Exports of the marks go to `C:/Users/emily/BugFarmer_backups/`.

## Acceptance criteria (each with how it's verified)
- [ ] **Every earlier mark is intact.** *Verified by:* `tools/gdd/marks_diff.py`, an exact field-by-field diff of the
  exports taken before and after the publish.
- [ ] **Nothing the owner wrote vanishes.** *Verified by:* the "Older notes" count equals the export's count of marks
  on removed ids.
- [ ] **The accounting is complete:** every lineup row, kept bug-list row, species and §03 sheet is placed exactly once.
  *Verified by:* `tools/gdd/_build/review_app_report.txt`, plus `test_build_app.py`.
- [ ] **The builder refuses bad data**, each planted fault with its own message. *Verified by:*
  `tools/gdd/tests/test_build_app.py`.
- [ ] **Saving survives misbehaving storage:** a stored mark is never replaced by an older one, writes go only to the
  right path, orphans show, and a note never changes a sign-off. *Verified by:* `tools/gdd/tests/save_stress.mjs`.
- [ ] **It works on every screen:** 1440 and 400 px, light and dark, no sideways scrolling, no text under 16 px, the
  map's north-up probe correct, no console errors. *Verified by:* `tools/gdd/tests/screens.mjs`.
- [ ] **The rehearsal passes:** the exact publish over a throwaway page holding seeded marks changes nothing.
  *Verified by:* exports E0 = E1, and the checklist ticked.
- [ ] **The owner reviews a zone, a bug, an item and a design question without the terminal.** *Verified by:* their
  test note, read back.

## Design (checked against the code on 2026-10-04)
**Facts the design rests on:**
- **The "applied" rule:** a mark counts as applied when the row has `decided` and the mark's `on` ≠ `decided`
  (`tools/gdd/items_page.template.html:196`).
- **Hidden marks:** today's page skips stored marks whose id is no longer in the data (`:422`). 227 item ids have
  been removed over 10 versions of the table.
- **Comment lines:** `parse_section` drops every line starting with `<!--` (`tools/gdd/build_page.py:222`).
- **Storage limits** (contract `db.d.ts`): 64 live subscriptions per view, 256 KB per document, 25,000 documents.
- **Storage belongs to the page's address** and survives a republish. Omitting capabilities on a redeploy keeps them.
- **Mark groups:** `GROUPS` (`tools/gdd/build_items_page.py:31-40`).

**One file**, about 1.5 MB: GDD ≈ 453 KB, items and bugs ≈ 450 KB, maps ≈ 193 KB as plain run-length text, the code
≈ 150 KB. It builds into the git-ignored `tools/gdd/_build/review_app.html`, with `review_app_report.txt` beside it.

**Data** (`docs/gdd/data/`, seeded once by `tools/gdd/seed_registry.py`, then edited by hand):
- **`zones.jsonl`:** exactly 20 rows. Fields: `id, name, aliases, row, col, layer, ring, danger, built, neighbours,
  purpose, sheets, layout`.
- **`bugs.jsonl`:** exactly 58 rows.
  - Fields: `id` (the lineup id without `lineup_`; also the storage doc id), `name, names, latin, family, lineup,
    bug_table[], species[], sheet` (a stable `bug.<id>` key, not a P-number), `hand{}`, and
    `zones[{zone, how: spawns|comes_in, from[], note, proposed}]`.
  - Every seeded zone link is `proposed` until its zone is signed off.
  - A bug may have `zones: []` with a note "kept for its zone's design (D79)".
  - The 12 hand-made links (`lineup_killer_bee` → its sheet, plus 11 bug-list ids) carry their reasons in `hand`.
- **`phrases.jsonl`:** document wording → ids ("both Swamps", "bees"). The build fails on any wording it can't place.
- **Built-zone maps** are generated from `nakama/data/zones/<built>/chunk_*.json` at build time and never committed.
  - Format: ground and object palettes with run-length rows, y-up, spawn areas mapped to bug ids, edges, and a probe.
  - The built world is found by walking neighbours from `village_21_B`, not by listing folders.

**The builder:** `tools/gdd/build_app.py`, with `app.template.html` and the inlined `app_save.js`, `app_views.js`
and `app_maps.js`.
- **It reuses:**
  - from `build_page.py`: `inline, table, blocks, plain, split_h3, parse_proposal, parse_question, parse_section` (with
    the key change), `review_order, Malformed`;
  - from `build_items_page.py`: `GROUPS, ITEM_VERDICTS, BUG_VERDICTS, WHERE, BUG_WHERE, load, read`;
  - from `tools/viewer/build_sprites_page.py`: `load` (entity categories);
  - from `tools/world/view_world.py`: `GROUND_COLORS`, with the diagonal path tiles coloured by prefix.
- **New functions:** `load_registry, auto_crosswalk, check_accounting, compare_where, resolve_phrase, encode_zone_map,
  decode_check, world_from, placements, content_ver`.
- **It fails loudly** (exit 1, listing every problem) on:
  - malformed data, or unknown or duplicate ids;
  - not exactly 20 zones;
  - neighbours that aren't adjacent or don't link both ways;
  - a built id whose row or column doesn't match;
  - accounting gaps;
  - an unresolved phrase;
  - a GDD `Malformed` section, or a missing or duplicate key;
  - an unmapped tile or object, or a map round trip that doesn't match;
  - the orientation probe: the village's deep water must lie south-west;
  - `GROUPS` missing a stored group;
  - an `approved` or `signed_off` field in the data;
  - page-format rules: `<title>` in the first 8 KB, no html/head/body tags, scripts only from the allowed CDNs;
  - more than 15 MB (warning above 3 MB).

**One source of truth for where bugs live:** the registry. `compare_where` reports where §03 headers, §04's table
and the game as built disagree, and never picks one. The app shows each disagreement in amber. After a zone is signed
off, §03 and §04's lists for it are generated from the registry.

**Feedback storage** (every path has the same 4-segment shape, so one saving engine handles all of it):
- `marks/<group>/items/<id>`: unchanged, with the browser key `bf-items-v2`, the import of old marks and the applied
  rule kept exactly.
- `notes/<zone|bug|gdd|section|system>/items/<id>`: shaped `{id,kind,mark,note,at,ver,page}`.
- `signoff/<kind>/items/<id>`: shaped `{id,kind,level,at,ver,page}`, with `ver` a fingerprint of what was approved.
- Design proposals and questions get stable `<!-- key: <sid>.<slug> -->` lines, added once by
  `tools/gdd/assign_keys.py`. `parse_section` keeps them; the old page ignores them.
- All 23 mark groups are read (31 subscriptions in all, under the cap of 64). Docs are matched to rows by id; writes go
  to the row's current group; marks on removed ids appear under "Older notes".

**Views:**
- **Zones:** a 5×4 grid, north up. Each zone page has the map, the description, its bugs in two lists ("spawns and
  breeds here" and "comes in from"), the items placed there, and feedback and approval for the map and for the
  details.
- **Bugs:** by family. Each bug page shows "in the game?" (the same mark as the items list), its sheet, its zones,
  disagreements, feedback and approval.
- **Items:** as today, plus "placed: Village ×161 · show on map", and an **Archive** view filter. Archived means cut,
  and either decided or agreed by the owner. Archiving never moves a row or its storage.
- **Design:** proposals and questions answered in place.
- **Status:** approvals only from `signoff/*`; Older notes; mark tallies.
- **Explain:** plain pages with diagrams and real numbers.
- **Also:** "changed since you last looked", links to any page by bare anchor (`#z-village`), 20 px text with an A−/A+
  control, light and dark themes, phone width.

**Maps:** a canvas for ground and objects, with an SVG layer drawn on the same coordinates for spawn circles, edge
names, the compass, highlights and (later) schematic layouts. Unbuilt zones show the outline and edges with "layout
not drawn yet".

## Deferred decisions
- **Mine:** the archive rule's edge cases, found in the rehearsal; the map's colours.
- **The owner's:** the look, after the first publish; whether to show the older zone sheets (folded away by default).

## Out of scope
- The Systems view's content (it waits for the behaviour audit).
- Schematic layouts for unbuilt zones (their format comes from the zone-design work).
- Item pictures.
- Happiness sub-kinds for decorations.
- Retiring the old builders (only after the owner accepts the app).

## Test plan (and the publishing procedure)
- **Tests** (`tools/gdd/tests/`, made-up data only):
  - `mock_db.js`, the misbehaving fake storage brought out of the git-ignored `_build/test_save.html`;
  - `save_stress.mjs` (Playwright): stress, failures, recovery, leftover, moved_group, orphan, legacy_import,
    applied_mark, two_devices, note_vs_signoff and archive_flip, with reloads;
  - `test_build_app.py`, with a planted fault per check;
  - `screens.mjs`.
  Playwright is found through `PLAYWRIGHT_DIR` or `~/.npm/_npx/*/node_modules/playwright`.
- **Publishing.** If any step fails: stop, roll back, tell the owner.
  1. The tests pass and the local screenshots are taken.
  2. The owner confirms nothing is waiting to save on every device, and pauses marking.
  3. **Export** every `marks/<group>/items` collection, plus `item_marks`, `notes/*` and `signoff/*` (expected empty),
     and the GDD page's `answers`, to `C:/Users/emily/BugFarmer_backups/<date>_review-app/`, with a `MANIFEST.json` of
     counts and sha256. List twice and compare. Also save the current `_build/item_pass.html` as the rollback copy.
  4. **The rehearsal, on a throwaway artifact:**
     - publish today's items page there and seed made-up marks covering every case;
     - export E0, publish the app over it with the same call as step 5, export E1; E1 must equal E0;
     - check every case on screen;
     - test `marks_restore.py`;
     - delete the throwaway.
  5. **Publish** over the items address with the `url` and without `capabilities`. Confirm the result kept `db` and
     made no new address.
  6. **Re-export and diff** with `marks_diff.py`; the result must be identical. After the owner opens it, only newer
     `at` values are allowed.
  7. **A test doc** at `selftest/run/items/<stamp>`: set, get, delete. Then the owner's zone note, read back.
  8. **Retire the GDD page** with a "moved" notice (no capabilities change). Update `docs/gdd/README.md`,
     `tools/README.md` and CLAUDE.md's list of sanctioned pages.

---
## Conformance table (filled at done-time)
| Acceptance criterion | Evidence (file:line / command output) | Test / gate |
|---|---|---|
| … | … | … |
