# docs/ — what each folder holds

The front page, [`../README.md`](../README.md), lists the current document for each topic. This page says what each
folder here is for and how much of it is current. Older documents are kept for the record; each says at its top when
it has been replaced.

| Folder | What it holds | Current? |
|---|---|---|
| [`gdd/`](gdd/README.md) | **The design document** — one file per section, reviewed by the owner one section at a time. Its README is the index and the review process; `item_table.jsonl` is the data behind the item review. | Current |
| [`product/`](product/) | The project's working documents: [`ROADMAP.md`](product/ROADMAP.md), [`BACKLOG.md`](product/BACKLOG.md), [`CHANGELOG.md`](product/CHANGELOG.md). | Current |
| [`product/architecture/`](product/architecture/ARCHITECTURE.md) | How the game is built, one system per document. `ARCHITECTURE.md` is the index. | Mostly current; outdated parts are marked |
| [`product/economy/`](product/economy/README.md) | The decision log for the whole game ([`DECISIONS.md`](product/economy/DECISIONS.md)), the item catalogs (`catalogs/`), and the economy designs. Its `zones/` folder holds the June 2026 zone content sheets. | The log and the catalogs marked as built are current; the rest is design |
| [`product/design/`](product/design/) | Older design documents: the January 2026 design, the December 2025 requirements, the armour brainstorm, the outfit roster. The design document (`gdd/`) is gathering them. | Older, being replaced |
| [`product/ecology/`](product/ecology/) | Bug ecology: tuning parameters, the tuning log, the control campaign, the ants-and-spiders design (not built). | Current |
| [`product/zones/`](product/zones/) | Design notes for the zones that exist. The starting village is `village_21_B`. | Mixed; outdated ones are marked |
| [`product/investigations/`](product/investigations/) | Research and root-cause write-ups, most dated. Working material behind decisions, not decisions. | Records |
| [`guides/`](guides/) | How-to guides: `art/` (how sprites look and are made), `authoring/` (how to build zones and scenes), `claudecode/` (an essay on working with Claude Code). | Current; outdated parts are marked |
| [`plans/`](plans/README.md) | Approved plans. **One active plan** ([`village-slice.md`](plans/village-slice.md)); its README groups the rest as reference, paused and archived (`plans/archive/`). | The active plan is current; the rest are records |
| [`brainstorms/`](brainstorms/) | June 2026 idea lists, raw material for the design document. Not decisions. | Older |
| [`archive/`](archive/) | Guides for the retired zone generator. | Retired |

`playerspritepipeline.md` and `scaffolding_scratchpad.md`, loose in this folder, are older notes; each says so at its
top.
