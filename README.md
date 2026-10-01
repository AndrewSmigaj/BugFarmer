# Bug Farmer

A 2D multiplayer sandbox set in 2126. A plague killed nearly every mammal, and people bred bugs big enough to eat. You
arrive on the frontier with almost nothing and make a life as a bug farmer: most players start a fly farm and grow
from there, but you can ranch ants, roam the wilds as a hunter, or anything between. You can grow your bugs' food or
buy it; fish, mine, craft and build; trade with the townspeople; and push out from the village into wilder land where
the bugs are more dangerous. The world is a living food web that answers what you do. With friends it becomes a
shared frontier.

**Status: a playable prototype.** The design is being settled one section at a time (the design document below), so
much of what is in the game today is a stand-in.

Built with Unity 6 (the client), a Go game server on [Nakama](https://heroiclabs.com/nakama/), PostgreSQL, and
Python tools for art, zones and testing.

## Start here

| If you want to… | Read |
|---|---|
| Understand the game | [`docs/gdd/README.md`](docs/gdd/README.md), then its [overview](docs/gdd/overview.md) — the design document, reviewed section by section |
| See what has been decided | [`docs/product/economy/DECISIONS.md`](docs/product/economy/DECISIONS.md) — every decision, dated (it covers the whole game, despite its folder) |
| See the plan and what's next | [`ROADMAP.md`](docs/product/ROADMAP.md) · [`BACKLOG.md`](docs/product/BACKLOG.md) · [`CHANGELOG.md`](docs/product/CHANGELOG.md) |
| Understand how it is built | [`ARCHITECTURE.md`](docs/product/architecture/ARCHITECTURE.md) (the stack and an index), then the `architecture_*.md` documents beside it |
| Understand multiplayer sync | [`architecture_swarm_sync.md`](docs/product/architecture/architecture_swarm_sync.md) §0 — how every player's game stays identical |
| Build zones and scenes | [`docs/guides/authoring/README.md`](docs/guides/authoring/README.md) |
| Make art | [`docs/guides/art/object_pipeline.md`](docs/guides/art/object_pipeline.md) (world art) and the [`player-sprites`](.claude/skills/player-sprites/SKILL.md) skill (outfits) |
| Run the tests | the [`test-changes`](.claude/skills/test-changes/SKILL.md) skill — every test and sync check |
| Work on it with Claude Code | [`CLAUDE.md`](CLAUDE.md) (the map for AI agents) and the skills in [`.claude/skills/`](.claude/skills/) |

## What's where

| Folder | What it holds |
|---|---|
| [`BugFarmerClient/`](BugFarmerClient/) | The Unity 6 game client (C#). The art the game loads is under `Assets/Resources/`. |
| [`nakama/`](nakama/) | The game server (Go modules on Nakama) and the game's data: items, species, zones (`nakama/data/`). |
| [`tools/`](tools/) | Python tools — the sprite pipeline, the zone builder, test harnesses. [`tools/README.md`](tools/README.md) maps them. |
| [`docs/`](docs/) | Design, architecture and guides. [`docs/README.md`](docs/README.md) says what each folder holds and what is current. |
| [`.claude/`](.claude/) | Skills, hooks and review checklists used when working with Claude Code. |

## The current document for each topic

Older documents are kept for the record; each now says at its top when it has been replaced.

| Topic | Current | Older (kept for the record) |
|---|---|---|
| The game's design | [`docs/gdd/`](docs/gdd/README.md) | `docs/product/design/game_design.md` (January 2026), `requirements.md` (December 2025), `docs/brainstorms/` |
| Decisions | [`DECISIONS.md`](docs/product/economy/DECISIONS.md) | decisions noted inside older documents |
| Items | the item review, [`docs/gdd/item_table.jsonl`](docs/gdd/item_table.jsonl), and [`docs/product/economy/catalogs/`](docs/product/economy/catalogs/) | `economy/item_catalog.md`, `design/item_database.md` |
| The world map and zones | [`docs/gdd/01_world.md`](docs/gdd/01_world.md) and [`architecture_world.md`](docs/product/architecture/architecture_world.md) | `docs/product/zones/demo_slice.md`, the June zone sheets in `docs/product/economy/zones/` |
| Bugs | [`architecture_bugs.md`](docs/product/architecture/architecture_bugs.md) and [`architecture_swarm_sync.md`](docs/product/architecture/architecture_swarm_sync.md) | `docs/guides/art/bugs_new.md` |
| Player art | the [`player-sprites`](.claude/skills/player-sprites/SKILL.md) skill and [`CHARACTER_DESIGN_GUIDE.md`](docs/guides/art/CHARACTER_DESIGN_GUIDE.md) (its 2026-07-28 section) | `docs/playerspritepipeline.md`, the two superseded player plans in `docs/plans/` |
| World art | [`object_pipeline.md`](docs/guides/art/object_pipeline.md), with the art decision in the [ROADMAP](docs/product/ROADMAP.md) | `docs/product/art_needed.md` |
| Saving and backups | [`architecture_persistence.md`](docs/product/architecture/architecture_persistence.md) | — |
| Building zones | [`docs/guides/authoring/`](docs/guides/authoring/README.md) | `docs/archive/` |

## Running it locally

**The server** runs in Docker (Docker Compose, from the repository root):

```bash
docker compose up -d                                   # start PostgreSQL, the Go module builder and Nakama
docker compose build builder && docker compose up -d   # after changing Go code under nakama/modules/
docker compose logs nakama --tail 50                   # check it loaded ("Bug Farmer module loaded successfully")
docker compose down                                    # stop (keeps the database)
```

Ports: 7350 is the client API, 7351 the Nakama console (`admin` / `password`), 5432 PostgreSQL. More, including
wiping the database and restoring a backup, is in the [`run-backend`](.claude/skills/run-backend/SKILL.md) skill.

**The client:** open `BugFarmerClient/` in Unity 6 (6000.2.9f1) and press Play; it connects to the server at
`127.0.0.1:7350`.
