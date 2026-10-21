"""Instantiate the MaximoDev engine's registers for one work package.

  python3 tools/new_work.py TICKET [--env NAME] [--force] [--dry-run]

Writes engine/templates/*.md to work/<TICKET>/ (filling {{TICKET}}, {{DATE}}, {{ENV}}) and a
manifests/<TICKET>.yaml stub. Never overwrites without --force; never deletes; never contacts Maximo.
"""
from datetime import date
from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "engine" / "templates"
MANIFEST = """# Work package {ticket}. Owned by release-manager; items mirror work/{ticket}/ARTIFACT_REGISTER.md.
#   python3 -m maxdev --env NAME deploy --manifest {ticket}          (dry run)
name: {ticket}
description: "[[PLACEHOLDER: one line | work-package-manager]]"
items: []
manual: []
"""


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticket")
    p.add_argument("--env", default=None, help="target environment named by the user")
    p.add_argument("--force", action="store_true", help="overwrite existing register files")
    p.add_argument("--dry-run", action="store_true", help="list what would be written")
    a = p.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", a.ticket):
        p.error("ticket must be letters, digits, '.', '_' or '-'")

    values = {"TICKET": a.ticket, "DATE": date.today().isoformat(),
              "ENV": a.env or "[[PLACEHOLDER: environment named by the user | work-package-manager]]"}
    out_dir = ROOT / "work" / a.ticket
    plan = [(t, out_dir / t.name) for t in sorted(TEMPLATES.glob("*.md"))]
    manifest = ROOT / "manifests" / f"{a.ticket}.yaml"
    written = skipped = 0
    for src, dst in plan:
        if dst.exists() and not a.force:
            print(f"  exists   {dst.relative_to(ROOT)}")
            skipped += 1
            continue
        print(f"  {'would write' if a.dry_run else 'write':8} {dst.relative_to(ROOT)}")
        if not a.dry_run:
            text = src.read_text(encoding="utf-8")
            for k, v in values.items():
                text = text.replace("{{%s}}" % k, v)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(text, encoding="utf-8")
        written += 1
    if manifest.exists():
        print(f"  exists   {manifest.relative_to(ROOT)}")
    else:
        print(f"  {'would write' if a.dry_run else 'write':8} {manifest.relative_to(ROOT)}")
        if not a.dry_run:
            manifest.write_text(MANIFEST.format(ticket=a.ticket), encoding="utf-8")
    print(f"{a.ticket}: {written} register(s) {'planned' if a.dry_run else 'written'}, {skipped} kept")
    return 0


if __name__ == "__main__":
    sys.exit(main())
