"""Check one ticket file for consistency with src/, the manifest, git and the deploy record.

  python3 tools/validate_work.py TICKET [--json]

  T-01  Requirement IDs unique; each has acceptance criteria
  T-02  Each requirement has a design row with a valid ladder; right of CONFIGURATION says why
  T-03  Non-OOB design rows name artifacts that exist in the Artifacts table, and vice versa
  T-04  Each artifact file exists and sits in the folder of its registry type
  T-05  The manifest resolves exactly the artifact files (both directions)
  T-06  Each artifact file is staged in git and the working copy matches the index
  T-07  Script artifacts pass maxdev lint with 0 errors
  T-08  Each APPLY has an earlier DRY-RUN, the user's quoted approval, a receipt, and a later RE-DIFF that says `same`
  T-09  Bug tickets record a reproduction, a root cause and a regression test
  T-10  Status `done`: every requirement has a PASS test with evidence; no [[PLACEHOLDER left

Offline. PASS / FAIL / SKIP (nothing to check yet). Exit 1 on any FAIL.
"""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

LADDER = ["OOB", "CONFIGURATION", "AUTOMATION SCRIPT", "INTEGRATION", "CUSTOM JAVA"]
CHANGES = {"NEW", "MODIFY", "RETIRE"}
ID = re.compile(r"\b[A-Z]+-\d+\b")


def sections(text: str) -> dict[str, list[dict]]:
    """First Markdown table under each `## Heading`, as row dicts keyed by header; blank rows dropped."""
    out, current, header = {}, None, None
    for line in text.splitlines():
        if line.startswith("## "):
            current, header = line[3:].strip(), None
            out[current] = []
            continue
        s = line.strip()
        if current is None or not s.startswith("|"):
            continue
        cells = [c.strip().strip("`").strip() for c in s.strip("|").split("|")]
        if header is None:
            header = cells
        elif set("".join(cells)) <= set("-: "):
            continue
        elif any(cells):
            out[current].append(dict(zip(header, cells + [""] * (len(header) - len(cells)))))
    return out


def field(text: str, name: str) -> str:
    m = re.search(r"^- \*\*%s:\*\*\s*(.*)$" % re.escape(name), text, re.M)
    return m.group(1).strip() if m else ""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}  # safe inside git hooks
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, env=env)


def validate(ticket: str, root: Path = ROOT) -> list[dict]:
    from maxdev import builder, manifest, registry

    path = root / "work" / f"{ticket}.md"
    if not path.is_file():
        raise FileNotFoundError(f"work/{ticket}.md not found; run tools/new_work.py {ticket} --type ...")
    text = path.read_text(encoding="utf-8")
    sec = sections(text)
    reqs, design, arts = sec.get("Requirements", []), sec.get("Design", []), sec.get("Artifacts", [])
    log, tests, state = sec.get("Deploy log", []), sec.get("Tests", []), sec.get("Current state", [])
    req_ids = [r.get("ID", "") for r in reqs]
    art_ids = {a.get("Art", "") for a in arts}
    out = []

    def result(vid, checked, problems):
        out.append({"id": vid, "status": "SKIP" if not checked else ("FAIL" if problems else "PASS"),
                    "problems": problems if checked else []})

    p = [f"{i or '(blank)'}: duplicate ID" for i in sorted(set(req_ids)) if req_ids.count(i) > 1]
    p += [f"{r.get('ID') or '(blank)'}: no acceptance criteria" for r in reqs if not r.get("Acceptance")]
    result("T-01", reqs, p)

    designed = {d.get("Req") for d in design}
    p = [f"{i}: no design row" for i in req_ids if i not in designed]
    for d in design:
        lad = d.get("Ladder", "")
        if lad not in LADDER:
            p.append(f"{d.get('Req')}: ladder {lad!r} not one of {', '.join(LADDER)}")
        elif LADDER.index(lad) > 1 and not d.get("Why not further left"):
            p.append(f"{d.get('Req')}: {lad} needs 'Why not further left'")
    result("T-02", reqs, p)

    p, named = [], set()
    for d in design:
        if d.get("Ladder") == "OOB":
            continue
        ids = ID.findall(d.get("Artifacts", ""))
        named |= set(ids)
        if not ids:
            p.append(f"{d.get('Req')}: non-OOB design names no artifact")
        p += [f"{d.get('Req')}: artifact {i} not in Artifacts table" for i in ids if i not in art_ids]
    p += [f"{a}: not referenced by any design row" for a in sorted(art_ids - named)]
    result("T-03", design, p)

    files, p = {}, []
    for a in arts:
        aid, typ = a.get("Art", ""), a.get("Type", "")
        if a.get("Change") not in CHANGES:
            p.append(f"{aid}: change {a.get('Change')!r} not one of {', '.join(sorted(CHANGES))}")
        f = root / a.get("File", "")
        if not a.get("File") or not f.is_file():
            p.append(f"{aid}: file {a.get('File') or '(blank)'} not found")
            continue
        files[f.resolve()] = aid
        t = registry.type_for_path(f)
        if not t or t.id != typ:
            p.append(f"{aid}: {a['File']} is a {t.id if t else 'unregistered'} file, row says {typ!r}")
    result("T-04", arts, p)

    mpath = root / "manifests" / f"{ticket}.yaml"
    p, resolved = [], set()
    if mpath.is_file():
        try:
            resolved = {Path(f).resolve() for _, f in manifest.items(manifest.load(str(mpath)))}
        except Exception as exc:  # a manifest that does not resolve is itself the finding
            p.append(f"manifests/{ticket}.yaml does not resolve: {exc}")
    elif arts:
        p.append(f"manifests/{ticket}.yaml missing")
    for a in arts:  # rows, not existing files, so an empty manifest cannot pass
        if a.get("File") and (root / a["File"]).resolve() not in resolved:
            p.append(f"{a.get('Art')}: {a['File']} not in manifest")
    p += [f"{f.relative_to(root)}: in manifest but not in Artifacts" for f in sorted(resolved) if f not in files]
    result("T-05", arts, p)

    p, checked = [], files
    if files:
        rels = {str(f.relative_to(root)): aid for f, aid in files.items()}
        ls = _git(root, "ls-files", "--", *rels)
        if ls.returncode:
            checked = {}  # not a git work tree
        else:
            tracked = set(ls.stdout.split())
            dirty = set(_git(root, "diff", "--name-only", "--", *rels).stdout.split())
            for rel, aid in rels.items():
                if rel not in tracked:
                    p.append(f"{aid}: {rel} not staged; run tools/track_work.py {ticket}")
                elif rel in dirty:
                    p.append(f"{aid}: {rel} changed after staging; re-run tools/track_work.py {ticket}")
    result("T-06", checked, p)

    p, scripts = [], []
    for f, aid in files.items():
        t = registry.type_for_path(f)
        if t and t.handler == "autoscript":
            scripts.append(f)
            p += [f"{aid}: {i['rule']} line {i['line']}"
                  for i in builder.lint_text(f.read_text(encoding="utf-8"), f.name) if i["level"] == "error"]
    result("T-07", scripts, p)

    p, applies = [], [(i, s) for i, s in enumerate(log) if s.get("Mode") == "APPLY"]
    for i, s in applies:
        env, step = s.get("Env", ""), s.get("Step") or i + 1
        if not any(x.get("Mode") == "DRY-RUN" and x.get("Env") == env for x in log[:i]):
            p.append(f"step {step}: APPLY on {env} without an earlier DRY-RUN")
        if not s.get("Approval (quote)") or not s.get("Date"):
            p.append(f"step {step}: APPLY without the user's quoted approval and date")
        rc = s.get("Receipt", "")
        if not rc or f"receipts/{env}/" not in rc or not (root / rc).is_file():
            p.append(f"step {step}: receipt {rc or '(blank)'} not found under .maxdev/receipts/{env}/")
        later = [x for x in log[i + 1:] if x.get("Mode") == "RE-DIFF" and x.get("Env") == env]
        res = later[-1].get("Result", "") if later else ""
        if not later:
            p.append(f"step {step}: no RE-DIFF after APPLY on {env}")
        elif not re.search(r"\bsame\b", res) or re.search(r"\bchanged\b|missing", res):
            p.append(f"step {step}: last RE-DIFF on {env} is not `same`: {res[:80]}")
    result("T-08", applies, p)

    bug = field(text, "Type").lower() == "bug"
    p = []
    if bug:
        if not state:
            p.append("bug ticket has no reproduction in Current state")
        if not re.search(r"\*\*Root cause \(bug only\):\*\*[ \t]*\S", text):
            p.append("bug ticket has no root cause")
        if not any("regression" in (t.get("Test", "") + " " + t.get("Command / steps", "")).lower() for t in tests):
            p.append("bug ticket has no regression test")
    result("T-09", [1] if bug else [], p)

    done = field(text, "Status").lower() == "done"
    p = []
    if done:
        passing = {r for t in tests if t.get("Result") == "PASS" and t.get("Evidence") for r in ID.findall(t.get("Req", ""))}
        p += [f"{i}: no PASS test with evidence" for i in req_ids if i not in passing]
        if "[[PLACEHOLDER" in text:
            p.append("unresolved [[PLACEHOLDER in the ticket")
    result("T-10", [1] if done else [], p)
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticket")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        res = validate(a.ticket)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        for r in res:
            print(f"{r['id']}  {r['status']}")
            for problem in r["problems"]:
                print(f"       - {problem}")
        n = {s: sum(r["status"] == s for r in res) for s in ("PASS", "FAIL", "SKIP")}
        print(f"{a.ticket}: {n['PASS']} PASS, {n['FAIL']} FAIL, {n['SKIP']} SKIP")
    return 1 if any(r["status"] == "FAIL" for r in res) else 0


if __name__ == "__main__":
    sys.exit(main())
