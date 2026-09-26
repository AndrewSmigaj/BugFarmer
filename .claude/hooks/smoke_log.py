#!/usr/bin/env python3
"""P0 smoke-test hook — logs WHICH hook event fired, to prove the new events
(UserPromptSubmit, Stop, and PreToolUse matched on the ExitPlanMode tool) actually
fire in our Claude Code before P2/P3/P4 build real logic on them.

TEMPORARY: this script and its settings.json wiring are REMOVED once P0 confirms
the events fire (see the P0 phase in the plan). Fail-open by construction: any error
exits 0 with no output, so it can never disrupt a tool call or a turn.

stdin (official Claude Code hook contract) includes at least:
  { "session_id": "...", "hook_event_name": "...", "tool_name": "<for PreToolUse>", ... }
Appends one tab-separated line per firing to _smoke.log next to this script.
"""
import sys
import os
import json
from datetime import datetime


def main() -> None:
    data = json.load(sys.stdin)
    event = data.get("hook_event_name", "UNKNOWN")
    tool = data.get("tool_name", "")
    session = (data.get("session_id", "nosession") or "nosession")[:8]
    logpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_smoke.log")
    line = f"{datetime.now().isoformat(timespec='seconds')}\tevent={event}\ttool={tool}\tsession={session}\n"
    with open(logpath, "a") as f:
        f.write(line)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open: never disrupt a tool call or turn
    sys.exit(0)
