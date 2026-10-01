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

**The client is currently human-run:** the user opens the project in the Unity Editor and presses Play to test in-game. Claude cannot drive the Unity GUI, so after a backend change, verify what you can from server logs and the console, then hand off to the user for in-game checks. (Agent-driven Play-mode testing is a future goal, not yet wired up.)

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
