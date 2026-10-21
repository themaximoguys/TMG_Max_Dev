"""Track a work package's src/ artifacts in git despite the src/** extract rule in .gitignore.

  python3 tools/track_work.py TICKET [--dry-run]

Stages every file manifests/<TICKET>.yaml resolves, plus work/<TICKET>/ and the manifest itself.
Git keeps tracking a file once it is added, so the ignore rule still keeps unrelated
environment extracts out. Stages only; never commits.
"""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def files_for(ticket: str, root: Path = ROOT) -> list[Path]:
    from maxdev import manifest
    path = root / "manifests" / f"{ticket}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"manifests/{ticket}.yaml not found")
    return sorted({Path(f).resolve() for _, f in manifest.items(manifest.load(str(path)))})


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticket")
    p.add_argument("--dry-run", action="store_true", help="list what would be staged")
    a = p.parse_args(argv)
    try:
        artifacts = files_for(a.ticket)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rel = [str(f.relative_to(ROOT)) for f in artifacts]
    extra = [x for x in (f"work/{a.ticket}", f"manifests/{a.ticket}.yaml") if (ROOT / x).exists()]
    for x in rel + extra:
        print(f"  {'would stage' if a.dry_run else 'stage':11} {x}")
    if a.dry_run:
        return 0
    if rel:
        subprocess.run(["git", "add", "-f", "--", *rel], cwd=ROOT, check=True)
    if extra:
        subprocess.run(["git", "add", "--", *extra], cwd=ROOT, check=True)
    print(f"{a.ticket}: {len(rel)} artifact(s) staged; review with `git diff --cached` before committing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
