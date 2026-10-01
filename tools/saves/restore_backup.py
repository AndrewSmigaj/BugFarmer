#!/usr/bin/env python3
"""Restore a backup of every zone and character (D73) — or list the backups there are.

The server backs up every zone's save and every character, at one moment, to C:/Users/emily/BugFarmer_backups/world
(docs/product/architecture/architecture_persistence.md → "Backups"). This tool puts one back:

  python3 tools/saves/restore_backup.py --list                       # the backups, newest first
  python3 tools/saves/restore_backup.py world-20261001T040634Z.json  # restore that one (asks first)
  python3 tools/saves/restore_backup.py pre-restore-....json --yes   # undo a restore: put back its safety copy

Restoring puts every zone and every character back as they were in the backup and removes anything made since.
The server does it at its next start, before anyone can join: it first keeps a copy of the current state in
world/pre-restore/ (so a restore can itself be undone), then writes everything in one step — all of it or none.
This tool copies the file into world/restore/, restarts the server (zones save first, players are disconnected),
waits for it and prints the server's own report. Exit 0 = restored.

The folder is BF_BACKUP_HOST_DIR if set (as in docker-compose.yml), else ../BugFarmer_backups/world beside the repo.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FOLDER = os.environ.get("BF_BACKUP_HOST_DIR") or os.path.join(os.path.dirname(REPO), "BugFarmer_backups", "world")
INBOX = os.path.join(FOLDER, "restore")
PRE = os.path.join(FOLDER, "pre-restore")


def read_backup(path):
    """The backup's header and counts, or raise ValueError if it isn't a backup this tool understands."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        raise ValueError(f"{os.path.basename(path)} is not a readable backup: {e}")
    if not isinstance(data, dict) or data.get("format") != 1:
        raise ValueError(f"{os.path.basename(path)} is not a backup this game version reads (format {data.get('format')!r})")
    return {
        "kind": data.get("kind", "?"),
        "created_at": data.get("created_at", ""),
        "zones": len(data.get("zone_state") or []),
        "characters": len(data.get("characters") or []),
    }


def local_time(stamp):
    """A backup's created_at (RFC 3339, nanoseconds, UTC) as this PC's local time."""
    m = re.match(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(\.\d+)?(Z|[+-]\d\d:\d\d)$", stamp or "")
    if not m:
        return stamp
    zone = "+00:00" if m.group(3) == "Z" else m.group(3)
    micros = (m.group(2) or ".")[1:7].ljust(6, "0")  # Go writes up to nanoseconds; Python 3.10 reads exactly 6 digits
    t = dt.datetime.fromisoformat(f"{m.group(1)}.{micros}{zone}")
    return t.astimezone().strftime("%Y-%m-%d %H:%M")


def backups():
    """(folder label, file name, path) of every backup, newest first within each folder."""
    out = []
    for label, folder, prefix in (("rolling", FOLDER, "world-"), ("safety copy", PRE, "pre-restore-")):
        if os.path.isdir(folder):
            names = sorted((n for n in os.listdir(folder) if n.startswith(prefix) and n.endswith(".json")), reverse=True)
            out += [(label, n, os.path.join(folder, n)) for n in names]
    return out


def list_backups():
    found = backups()
    if not found:
        print(f"No backups in {FOLDER}")
        return 0
    print(f"Backups in {FOLDER} (times are this PC's):")
    for label, name, path in found:
        try:
            h = read_backup(path)
            size = os.path.getsize(path) // 1024
            print(f"  {local_time(h['created_at'])}  {name:48} {h['zones']:3} zone records  {h['characters']:3} characters"
                  f"  {size:5} KB  ({label})")
        except ValueError as e:
            print(f"  {name:66} UNREADABLE: {e}")
    waiting = [n for n in os.listdir(INBOX)] if os.path.isdir(INBOX) else []
    waiting = [n for n in waiting if os.path.isfile(os.path.join(INBOX, n)) and not n.startswith(".")]
    if waiting:
        print(f"Waiting to be restored at the next start: {', '.join(waiting)}")
    return 0


def resolve(name):
    if os.path.isfile(name):
        return os.path.abspath(name)
    for folder in (FOLDER, PRE):
        p = os.path.join(folder, name)
        if os.path.isfile(p):
            return p
    raise SystemExit(f"No backup called {name} in {FOLDER} or its pre-restore/ folder (see --list)")


def compose(*args, check=True):
    return subprocess.run(["docker", "compose", *args], cwd=REPO, capture_output=True, text=True, check=check)


def wait_healthy(timeout=180):
    end = time.time() + timeout
    while time.time() < end:
        ps = compose("ps", "--format", "{{.Name}} {{.Status}}", check=False).stdout
        if any("nakama" in line and "(healthy)" in line for line in ps.splitlines()):
            return True
        time.sleep(2)
    return False


def server_report(since):
    """The restore lines the server logged since `since` (RFC 3339)."""
    logs = compose("logs", "--since", since, "nakama", check=False).stdout
    lines = []
    for line in logs.splitlines():
        brace = line.find("{")
        if brace < 0:
            continue
        try:
            msg = json.loads(line[brace:]).get("msg", "")
        except json.JSONDecodeError:
            continue
        if msg.startswith("RESTORE") or msg.startswith("Restore"):
            lines.append(msg)
    return lines


def restore(name, yes):
    path = resolve(name)
    try:
        h = read_backup(path)
    except ValueError as e:
        raise SystemExit(str(e))
    os.makedirs(INBOX, exist_ok=True)
    waiting = [n for n in os.listdir(INBOX) if os.path.isfile(os.path.join(INBOX, n)) and not n.startswith(".")]
    if waiting:
        raise SystemExit(f"A restore is already waiting in {INBOX}: {', '.join(waiting)} — move it away first")
    print(f"This puts every zone and every character back as they were at {local_time(h['created_at'])}\n"
          f"({h['zones']} zone records, {h['characters']} characters, from {os.path.basename(path)}).\n"
          f"Anything made since is removed. A copy of the current state is kept first, in {PRE},\n"
          f"so this can be undone. The server restarts: zones save first, and anyone playing is disconnected.")
    if not yes and input("Type yes to restore: ").strip().lower() != "yes":
        print("Not restored.")
        return 1
    shutil.copyfile(path, os.path.join(INBOX, os.path.basename(path)))  # a fresh copy: a new restore request
    since = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print("Restarting the server…")
    compose("restart", "nakama")
    if not wait_healthy():
        print("The server didn't come back within 3 minutes — see: docker compose logs nakama")
        return 1
    report = server_report(since)
    for line in report:
        print("  server: " + line)
    if any(line.startswith("RESTORED") for line in report):
        return 0
    if not report:
        print("The server didn't report a restore — see: docker compose logs nakama | grep -i restore")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("backup", nargs="?", help="the backup's file name (from --list), or a path to one")
    ap.add_argument("--list", action="store_true", help="list the backups, newest first")
    ap.add_argument("--yes", action="store_true", help="don't ask before restoring")
    a = ap.parse_args()
    if a.list or not a.backup:
        return list_backups()
    return restore(a.backup, a.yes)


if __name__ == "__main__":
    sys.exit(main())
