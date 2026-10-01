---
name: run-backend
description: Use when launching, restarting, stopping, rebuilding, or checking the Bug Farmer server (the Nakama + Postgres + Go-plugin Docker stack). Covers verifying the Go module loaded, picking the right restart for code vs data changes, reading logs, and shutting down cleanly without leaving orphaned containers. Also documents how the Unity client connects.
---

# Run the backend

The server is a three-container Docker Compose stack defined in `docker-compose.yml`:

| Container | Role | Notes |
|-----------|------|-------|
| `bugfarmer-postgres` | Database (player accounts, saves) | Healthchecked; data in the `pgdata` volume. |
| `bugfarmer-builder` | One-shot: compiles `nakama/modules/**` Go into `backend.so` | Runs, copies the `.so` into the `modules` volume, then **exits 0**. An exited builder is normal, not a crash. |
| `bugfarmer-nakama` | Game server | Loads `backend.so` from the `modules` volume. Ports 7349 (gRPC) / 7350 (client API) / 7351 (console). |

Startup order is enforced by Compose: Postgres must be healthy and the builder must exit 0 before Nakama starts.

**No `sudo` needed in this environment.** (Older docs say `sudo docker compose`; it isn't required here — try without first.)

## Launch

```bash
docker compose up -d
```

Then **always verify** — "up" only means the containers started, not that the module loaded:

```bash
docker compose ps                                   # postgres + nakama should be (healthy); builder Exited (0)
docker compose logs nakama | grep -iE "module loaded successfully|Registered .* RPC|Match creation|error|panic"
```

A healthy launch shows `Bug Farmer module loaded successfully`, the registered RPCs (`world_create`, `world_join`, `world_list`), and the `world` match handler. If Nakama is unhealthy, check the builder first: `docker inspect bugfarmer-builder --format '{{.State.ExitCode}}'` (must be 0) and `docker compose logs builder`.

## Restart — pick by what you changed

- **Go server code (`nakama/modules/**`)** — the compiled `backend.so` lives in the `modules` volume, so you MUST recompile. A plain restart will run the *old* binary:
  ```bash
  docker compose build builder && docker compose up -d
  ```
  Compose recreates the builder (fresh image → recompiles → copies new `.so`) and then recreates Nakama. If you want to be certain Nakama picks up the new `.so`, add `--force-recreate nakama`.
- **Entity/zone data (`nakama/data/**`, bind-mounted, read at startup)** — no recompile; just bounce Nakama:
  ```bash
  docker compose restart nakama
  ```
- **Config (`nakama/data/local.yml`)** — same as data: `docker compose restart nakama`.

## Stop — clean shutdown, no hanging processes

```bash
docker compose down            # stops + removes containers and the network; KEEPS volumes (DB + compiled module)
```

This is the safe default — it leaves no orphaned containers and preserves player data and the built plugin.

**A clean stop saves the world (since 2026-09-30).** `stop`, `down`, `restart` and `up --force-recreate` send the
server a polite stop; it gives every zone up to 15 s (`shutdown_grace_sec` in `nakama/data/local.yml`) to write its
final save — the world and every character still in it, in one write — and Docker waits up to 30 s
(`stop_grace_period` in `docker-compose.yml`) before forcing it. `docker kill`, a crash, or switching off the PC/WSL
skips that save. After changing `stop_grace_period`, recreate the container once (`docker compose up -d
--force-recreate nakama`) — Compose applies it only when creating the container. Check: `docker inspect -f
'{{.Config.StopTimeout}}' bugfarmer-nakama` → `30`. Confirm nothing is left:

```bash
docker compose ps
docker ps -a | grep bugfarmer   # expect no leftover bugfarmer-* containers after `down`
```

**Destructive — only when deliberately resetting:**

```bash
docker compose down -v          # ALSO deletes pgdata + modules volumes: wipes the database and the compiled plugin
```

Never run `down -v` to "fix" a problem unless you intend to lose all server-side data. Confirm with the user first.

## Backups — every zone and every character, kept automatically (since 2026-09-30)
The server backs up every zone's save and every character, at one moment, to
`C:/Users/emily/BugFarmer_backups/world/world-<UTC time>.json` — at every start, then every 30 minutes if anything
was saved since; a copy identical to the newest isn't written. Kept: the newest 10, plus the newest of each of the 7
most recent days and of the 4 most recent weeks that have one; older ones are pruned only after a new backup has read
back intact, and only files named `world-<time>.json`. Each one is logged: `docker compose logs nakama | grep Backup`.
Settings: `BF_BACKUP_DIR` (the folder inside the container, `/nakama/backups`) and `BF_BACKUP_MINUTES` in
`nakama/data/local.yml` runtime.env; the folder mount in `docker-compose.yml` (`BF_BACKUP_HOST_DIR` moves it). A
changed mount needs `docker compose up -d --force-recreate nakama`. How it works: `architecture_persistence.md` →
"Backups". The whole-database dump taken before the saves work began is
`C:/Users/emily/BugFarmer_backups/db-before-saves-2026-09-30.dump`.

**Restore one** (puts every zone and character back as in the backup; anything made since is removed):
```bash
python3 tools/saves/restore_backup.py --list                      # the backups, newest first, with counts
python3 tools/saves/restore_backup.py world-<time>.json           # asks, then restarts the server and reports
python3 tools/saves/restore_backup.py pre-restore-<time>.json     # undo a restore: its safety copy
```
The server applies it at its next start, before anyone can join, after writing a safety copy of the current state
to `world/pre-restore/` (never pruned) — all of it in one database transaction, or none. The file ends up in
`world/restore/done/` (or `failed/`, with the reason in the log: `docker compose logs nakama | grep -i restore`).
Accounts and the world list are not part of a backup. Test it with `bash tools/harness_restore_test.sh` (it restores
the whole database and back — run it when no one is playing).

## Logs

```bash
docker compose logs -f nakama                       # follow live
docker compose logs nakama | grep -iE "error|panic" # scan for failures
```

## Console & connection facts

- **Nakama console:** http://localhost:7351 — login `admin` / `password`.
- **Client API:** http://127.0.0.1:7350, server key `defaultkey`.

## Frontend (Unity client)

The client lives in `BugFarmerClient/` and connects via `Assets/Scripts/Networking/NetworkManager.cs` (`new Client("http", "127.0.0.1", 7350, "defaultkey")`). It must match the running server's host/port/key above.

**Playing it:** the owner opens the project in the Unity Editor and presses Play. Claude can't drive the Editor's
window, but it CAN run the real game client headless: the sync-test player build (`SyncTestBuild.Build` in Unity
batchmode, Editor closed) driven by `HeadlessSyncTest` — the two-player sync gates (`tools/run_sync_latejoin.sh`) and
the zone-crossing test with a character (`tools/run_crosstest.sh`). The test-changes skill lists what each covers;
look there before handing an in-game check to the owner.

## Gotchas

- An **Exited (0)** builder is success, not failure — it's a one-shot copy job.
- After Go changes, a plain `up -d`/`restart` keeps the **old** `backend.so`; you must `build builder` first.
- **Rebuilding while someone plays no longer crashes the server (fixed 2026-09-30).** The builder used to copy the
  new `backend.so` straight over the file the running server had open — the match goroutine panicked (SIGSEGV at
  pc=0x0) and clients were left bound to a dead match. It now copies to `backend.so.new` and renames it into place,
  so the running server keeps its old file (`nakama/modules/Dockerfile.build`). The new code still loads only when
  nakama restarts (`up -d` after a build does that): a clean stop — every zone saves, players are disconnected and
  rejoin.
- **Reset one zone's save** (start it from the authored zone again): stop the server FIRST, or its final save writes
  the zone straight back — `docker compose stop nakama`, then
  `docker compose exec -T postgres psql -U postgres -d nakama -c "delete from storage where collection='zone_state'
  and left(key, length('<zone>:')) = '<zone>:';"`, then `docker compose start nakama`. Match the exact `<zone>:`
  prefix: with `like '<zone>%'`, `_` is a wildcard and `village_21%` also deletes `village_21_B` and `village_21_lab`.
- Don't `down -v` unless you mean to wipe the database.
- If Nakama won't go healthy, the cause is almost always the builder (compile error) — read `docker compose logs builder` before touching Nakama.
