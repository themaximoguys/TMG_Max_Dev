"""Run the MaximoDev engine's computed validators (engine/04_VALIDATORS.md) for one work package.

  python3 tools/validate_work.py TICKET [--json]

Offline: reads work/<TICKET>/*.md, manifests/<TICKET>.yaml, src/, engine/roster.yaml and
maxdev/registry.yaml. Exit 1 if any validator FAILs. SKIP means the register has no rows yet.
"""
from pathlib import Path
import argparse
import json
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PREFIXES = {"FUN", "TEC", "UI", "WF", "INT", "GIS", "AI", "SEC", "DAT", "MOB", "RPT", "SVC", "CNV", "ENV"}
LADDER = ["OOB", "CONFIGURATION", "AUTOMATION SCRIPT", "INTEGRATION", "CUSTOM JAVA"]
CHANGES = {"NEW", "MODIFY", "RETIRE", "NO-CHANGE"}
DISPOSITIONS = {"RETAIN", "RECONFIGURE", "REPLACE WITH OOB", "REPLACE WITH AUTOMATION SCRIPT",
                "REWRITE", "RETIRE", "REQUIRES INVESTIGATION"}
RESULTS = {"PASS", "FAIL", "NOT RUN", "BLOCKED"}
SPECIALIST = {"INT": "INTEGRATION_REGISTER.md", "GIS": "GIS_REGISTER.md", "AI": "AI_AGENT_REGISTER.md",
              "DAT": "DATA_LOAD_REGISTER.md", "SEC": "SECURITY_REGISTER.md"}
REQ_ID = re.compile(r"\b([A-Z]{2,3})-\d{3,}\b")


def table(path: Path) -> list[dict]:
    """Rows of the first Markdown table in a register, keyed by header; blank rows dropped."""
    if not path.is_file():
        return []
    header, rows = None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            if header is not None:
                break
            continue
        cells = [c.strip().strip("`") for c in s.strip("|").split("|")]
        if header is None:
            header = cells
        elif set("".join(cells)) <= set("-: "):
            continue
        elif any(cells):
            rows.append(dict(zip(header, cells + [""] * (len(header) - len(cells)))))
    return rows


def ids(cell: str) -> list[str]:
    return [m.group(0) for m in REQ_ID.finditer(cell or "")]


def split(cell: str) -> list[str]:
    return [x.strip() for x in re.split(r"[,;\s]+", cell or "") if x.strip()]


def validate(ticket: str, root: Path = ROOT) -> list[dict]:
    from maxdev import builder, manifest, registry

    wp = root / "work" / ticket
    if not wp.is_dir():
        raise FileNotFoundError(f"work/{ticket} not found; run tools/new_work.py {ticket}")
    reg = lambda name: table(wp / name)  # noqa: E731
    reqs, cls, arts = reg("REQUIREMENT_REGISTER.md"), reg("SOLUTION_CLASSIFICATION.md"), reg("ARTIFACT_REGISTER.md")
    tests, plan, finds = reg("TEST_REGISTER.md"), reg("DEPLOYMENT_PLAN.md"), reg("FINDINGS_LOG.md")
    roster = yaml.safe_load((root / "engine/roster.yaml").read_text(encoding="utf-8"))["agents"]
    type_owner = {t: name for name, a in roster.items() for t in a.get("types") or []}
    req_ids = [r["Req ID"] for r in reqs]
    art_ids = {a["Art ID"] for a in arts}
    active = [r for r in reqs if r.get("Status") not in ("DEFERRED", "REJECTED")]
    out = []

    def result(vid, rows, problems):
        status = "SKIP" if not rows else ("FAIL" if problems else "PASS")
        out.append({"id": vid, "status": status, "problems": problems if rows else []})

    # W-01..W-05 traceability
    p = []
    for r in reqs:
        rid = r["Req ID"]
        if not re.fullmatch(r"[A-Z]{2,3}-\d{3,}", rid) or rid.split("-")[0] not in PREFIXES:
            p.append(f"{rid or '(blank)'}: ID must be PREFIX-NNN with a taxonomy §1 prefix")
        if req_ids.count(rid) > 1:
            p.append(f"{rid}: duplicate ID")
        if not r.get("Acceptance criteria"):
            p.append(f"{rid}: no acceptance criteria")
    result("W-01", reqs, sorted(set(p)))
    classified = {r["Req ID"] for r in cls}
    result("W-02", active, [f"{r['Req ID']}: no classification row" for r in active if r["Req ID"] not in classified])
    p = []
    for r in cls:
        pos = r.get("Ladder position", "")
        if pos not in LADDER:
            p.append(f"{r['Req ID']}: ladder position {pos!r} not in taxonomy §2")
        elif LADDER.index(pos) > 1 and not r.get("Departure reason"):
            p.append(f"{r['Req ID']}: {pos} needs a departure reason")
    result("W-03", cls, p)
    p = []
    for r in cls:
        if r.get("Ladder position") == "OOB":
            continue
        named = split(r.get("Artifact IDs"))
        if not named:
            p.append(f"{r['Req ID']}: non-OOB row names no artifact")
        p += [f"{r['Req ID']}: artifact {a} not in ARTIFACT_REGISTER" for a in named if a not in art_ids]
    result("W-04", cls, p)
    p = []
    for a in arts:
        named = ids(a.get("Req IDs"))
        if not named:
            p.append(f"{a['Art ID']}: traces to no requirement")
        p += [f"{a['Art ID']}: requirement {r} does not exist" for r in named if r not in req_ids]
    result("W-05", arts, p)

    # W-10..W-16 repository consistency
    deployable = [a for a in arts if a.get("Change") != "NO-CHANGE"]
    files = {}
    p10, p11, p12, p15, p16 = [], [], [], [], []
    for a in arts:
        aid, typ, change = a["Art ID"], a.get("Type", ""), a.get("Change", "")
        if change not in CHANGES:
            p16.append(f"{aid}: change {change!r} not in taxonomy §3")
        if change == "RETIRE" and "approv" not in json.dumps(a).lower():
            p16.append(f"{aid}: RETIRE needs the user's approval cited")
        if typ not in type_owner:
            p12.append(f"{aid}: type {typ!r} is not a registry type owned in roster.yaml")
        elif a.get("Owner") != type_owner[typ]:
            p12.append(f"{aid}: owner {a.get('Owner')!r}, roster owner of {typ} is {type_owner[typ]}")
        if change == "NO-CHANGE":
            continue
        f = root / a.get("File", "")
        if not a.get("File") or not f.is_file():
            p10.append(f"{aid}: file {a.get('File') or '(blank)'} not found")
            continue
        files[f.resolve()] = aid
        t = registry.type_for_path(f)
        if not t or t.id != typ:
            p11.append(f"{aid}: {a['File']} is a {t.id if t else 'unregistered'} file, row says {typ}")
        if f.suffix in (".py", ".js") and t and t.handler == "autoscript":
            errs = [i for i in builder.lint_text(f.read_text(encoding="utf-8"), f.name) if i["level"] == "error"]
            p15 += [f"{aid}: {i['rule']} line {i['line']}" for i in errs]
    result("W-10", deployable, p10)
    result("W-11", deployable, p11)
    result("W-12", arts, p12)
    mpath = root / "manifests" / f"{ticket}.yaml"
    resolved = set()
    p13 = []
    if mpath.is_file():
        try:
            resolved = {Path(f).resolve() for _, f in manifest.items(manifest.load(str(mpath)))}
        except Exception as exc:  # a broken manifest is itself the finding
            p13.append(f"manifests/{ticket}.yaml does not resolve: {exc}")
    elif deployable:
        p13.append(f"manifests/{ticket}.yaml missing")
    p13 += [f"{aid}: {f.relative_to(root)} not in manifest" for f, aid in files.items() if f not in resolved]
    result("W-13", deployable, p13)
    result("W-14", resolved, [f"{f.relative_to(root)}: deployed by manifest but not in ARTIFACT_REGISTER"
                               for f in sorted(resolved) if f not in files])
    result("W-15", [a for a in deployable if a.get("Type") == "autoscript"], p15)
    result("W-16", arts, p16)

    # W-20..W-28 delivery evidence
    p20, p21, p22 = [], [], []
    for i, s in enumerate(plan):
        if s.get("Mode") != "APPLY":
            continue
        env = s.get("Env", "")
        if not any(x.get("Mode") == "DRY-RUN" and x.get("Env") == env for x in plan[:i]):
            p20.append(f"step {s.get('Step')}: APPLY on {env} without an earlier DRY-RUN")
        if not s.get("Approval (quote)") or not s.get("Date"):
            p21.append(f"step {s.get('Step')}: APPLY without quoted approval and date")
        rc = s.get("Receipt", "")
        if not rc or not (root / rc).is_file() or f"receipts/{env}/" not in rc:
            p22.append(f"step {s.get('Step')}: receipt {rc or '(blank)'} not found under .maxdev/receipts/{env}/")
    applies = [s for s in plan if s.get("Mode") == "APPLY"]
    result("W-20", applies, p20)
    result("W-21", applies, p21)
    result("W-22", applies, p22)
    verified = [r for r in reqs if r.get("Status") == "VERIFIED"]
    passing = {rid for t in tests if t.get("Result") == "PASS" and t.get("Evidence") for rid in ids(t.get("Req IDs"))}
    result("W-23", verified, [f"{r['Req ID']}: VERIFIED without a PASS test with evidence"
                              for r in verified if r["Req ID"] not in passing])
    p = []
    for t in tests:
        if t.get("Result") not in RESULTS:
            p.append(f"{t.get('Test ID')}: result {t.get('Result')!r} not in taxonomy §5")
        named = ids(t.get("Req IDs"))
        if not named:
            p.append(f"{t.get('Test ID')}: references no requirement")
        p += [f"{t.get('Test ID')}: requirement {r} does not exist" for r in named if r not in req_ids]
    result("W-24", tests, p)
    result("W-25", finds, [f"{f.get('F ID')}: OPEN BLOCKER - {f.get('Finding')}" for f in finds
                           if f.get("Severity") == "BLOCKER" and f.get("Status") == "OPEN"])
    conv = reg("CONVERSION_REGISTER.md")
    cnv = [r for r in active if r["Req ID"].startswith("CNV-")]
    p = [f"{c.get('Item ID')}: disposition {c.get('Disposition')!r} not in taxonomy §4"
         for c in conv if c.get("Disposition") not in DISPOSITIONS]
    covered = {rid for c in conv for rid in ids(c.get("Req IDs"))}
    p += [f"{r['Req ID']}: no conversion register row" for r in cnv if r["Req ID"] not in covered]
    result("W-26", cnv or conv, p)
    p, spec_rows = [], []
    for r in active:
        name = SPECIALIST.get(r["Req ID"].split("-")[0])
        if name:
            spec_rows.append(r)
            if r["Req ID"] not in {x for row in reg(name) for x in ids(row.get("Req IDs"))}:
                p.append(f"{r['Req ID']}: no row in {name}")
    result("W-27", spec_rows, p)
    docs = [wp / n for n in ("DESIGN_DOC.md", "HANDOFF.md") if (wp / n).is_file()]
    check = (wp / "WORK_CHECKLIST.md").is_file() and re.search(
        r"\|\s*D10[^|]*\|\s*✅", (wp / "WORK_CHECKLIST.md").read_text(encoding="utf-8"))
    result("W-28", docs if check else [], [f"{d.name}: unresolved [[PLACEHOLDER" for d in docs
                                           if "[[PLACEHOLDER" in d.read_text(encoding="utf-8")])
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
        counts = {s: sum(r["status"] == s for r in res) for s in ("PASS", "FAIL", "SKIP")}
        print(f"{a.ticket}: {counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['SKIP']} SKIP")
    return 1 if any(r["status"] == "FAIL" for r in res) else 0


if __name__ == "__main__":
    sys.exit(main())
