"""Open a ticket: work/<TICKET>.md from the ticket template, plus a manifest stub.

  python3 tools/new_work.py TICKET --type feature|enhancement|bug [--env NAME] [--force] [--dry-run]

Never overwrites without --force; never contacts Maximo.
"""
from datetime import date
from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills" / "maximo-dev-engine" / "TICKET_TEMPLATE.md"
MANIFEST = """# Ticket {ticket}: items mirror the Artifacts table in work/{ticket}.md.
#   python3 -m maxdev --env NAME deploy --manifest {ticket}          (dry run)
name: {ticket}
description: "[[PLACEHOLDER: one line]]"
items: []
manual: []
"""


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticket")
    p.add_argument("--type", required=True, choices=["feature", "enhancement", "bug"])
    p.add_argument("--env", default=None, help="target environment named by the user")
    p.add_argument("--force", action="store_true", help="overwrite an existing ticket file")
    p.add_argument("--dry-run", action="store_true", help="list what would be written")
    a = p.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", a.ticket):
        p.error("ticket must be letters, digits, '.', '_' or '-'")
    values = {"TICKET": a.ticket, "TYPE": a.type, "DATE": date.today().isoformat(),
              "ENV": a.env or "[[PLACEHOLDER: environment named by the user]]"}
    targets = [(ROOT / "work" / f"{a.ticket}.md", None), (ROOT / "manifests" / f"{a.ticket}.yaml", "manifest")]
    for path, kind in targets:
        rel = path.relative_to(ROOT)
        if path.exists() and not (a.force and kind is None):
            print(f"  exists   {rel}")
            continue
        print(f"  {'would write' if a.dry_run else 'write':8} {rel}")
        if a.dry_run:
            continue
        if kind == "manifest":
            text = MANIFEST.format(ticket=a.ticket)
        else:
            text = TEMPLATE.read_text(encoding="utf-8")
            for k, v in values.items():
                text = text.replace("{{%s}}" % k, v)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
