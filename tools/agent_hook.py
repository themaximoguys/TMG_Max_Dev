"""Claude Code hooks for this repo (wired in .claude/settings.json).

  session  SessionStart: run the offline checks and report whether git hooks are enabled
  guard    PreToolUse: refuse touching environment secrets or writing to Maximo around maxdev
  lint     PostToolUse: TMG standards lint on any edited script under src/

Exit code 2 blocks the tool call (guard) or feeds the lint errors back to the agent (lint).
"""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENV_DIR = (ROOT / "environments").resolve()
SECRET = re.compile(r"environments[\\/]+\.env\.(?!example\b)[\w.-]+")
RAW_WRITE = re.compile(r"\b(curl|wget|http|Invoke-RestMethod|Invoke-WebRequest)\b.*?/maximo/.*?"
                       r"(-X\s*(POST|PUT|PATCH|DELETE)|--data|\s-d\s|-Method\s+(Post|Put|Patch|Delete))",
                       re.IGNORECASE | re.DOTALL)


def _run(*args):
    p = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def _path(event):
    raw = (event.get("tool_input") or {}).get("file_path") or (event.get("tool_input") or {}).get("notebook_path")
    if not raw:
        return None
    p = Path(raw)
    return (p if p.is_absolute() else Path(event.get("cwd") or ROOT) / p).resolve()


def session(_event):
    lines = []
    for script in ("tools/check_agent_setup.py", "tools/check_components.py"):
        rc, out = _run(script)
        lines.append(out if rc == 0 else f"FAILED {script}:\n{out}")
    hooks = subprocess.run(["git", "config", "core.hooksPath"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if hooks != ".githooks":
        lines.append("Git hooks are not enabled for this clone; ask the user before running "
                     "`git config core.hooksPath .githooks`.")
    print("\n".join(lines))
    return 0


def guard(event):
    tool = event.get("tool_name", "")
    if tool == "Bash":
        cmd = (event.get("tool_input") or {}).get("command", "")
        if SECRET.search(cmd):
            print("Blocked: environment files hold credentials and are managed by the user (AGENTS.md). "
                  "Use `python3 -m maxdev envs` / `ping --env NAME` instead.", file=sys.stderr)
            return 2
        if RAW_WRITE.search(cmd):
            print("Blocked: write to Maximo outside maxdev. Use `python3 -m maxdev ... --env NAME` "
                  "(dry run, then --apply after approval) so protection and receipts apply.", file=sys.stderr)
            return 2
        return 0
    path = _path(event)
    if path and path.parent == ENV_DIR and path.name.startswith(".env.") and path.name != ".env.example":
        print(f"Blocked: {path.name} is user-managed (credentials, MAXIMO_PROTECTED). "
              "Ask the user to change it.", file=sys.stderr)
        return 2
    return 0


def lint(event):
    path = _path(event)
    src = (ROOT / "src").resolve()
    if not path or src not in path.parents or path.suffix not in (".py", ".js") or not path.is_file():
        return 0
    rc, out = _run("-m", "maxdev", "lint", str(path))
    if rc:
        print(f"TMG lint errors in {path.relative_to(ROOT)} (fix before deploy):\n{out}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        event = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except ValueError:
        event = {}
    handler = {"session": session, "guard": guard, "lint": lint}.get(mode)
    if handler is None:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    sys.exit(handler(event))
