"""Operational dashboard builder: one YAML spec -> the Maximo records behind a start center.

  catalog/dashboards/<NAME>.yaml           the spec (see maintenance_supervisor.yaml)
    -> src/07-app-designer/_queries/       saved queries the result-set portlets and work queues read
    -> src/19-kpi/                         KPI definitions for KPI list / graph portlets
    -> src/07-app-designer/_workqueues/    work queues built on those queries
    -> src/07-app-designer/_startcenters/  the start center template (presentation XML)
    -> manifests/<NAME>.yaml               deploy order + the manual steps no API covers

Nothing here talks to Maximo. Deploy the manifest the usual way:
`maxdev deploy --manifest NAME` (dry run), then `--apply` after a yes.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

from . import registry, store
from .env import REPO

CATALOG = REPO / "catalog" / "dashboards"
MANIFESTS = REPO / "manifests"

# spec portlet type -> (XML element, portletid) as Maximo stores them in SCTEMPLATE.PRESENTATION
PORTLETS = {
    "resultset": ("resultset", "RSCONFIG"),
    "kpilist": ("kpilist", "KPILCONFIG"),
    "kpigraph": ("kpigraph", "KPIGCONFIG"),
    "favorites": ("favoriteapplications", "FACONFIG"),
    "quickinsert": ("quickinsert", "ACTIONSCFG"),
    "inbox": ("inbox", "INBXCONFIG"),
    "bulletin": ("bulletinboard", "BBOARD"),
}
CHARTS = {"BAR", "PIE", "LINE"}
FORMATS = {"DECIMAL", "PERCENT", "CURRENCY"}
# {now} in spec SQL -> the tenant database's current-timestamp function. Maximo has no bind for it
# that works in saved queries: :sysdate fails with HTTP 500 on MAS 9 (verified on demo).
NOW = {"sqlserver": "GETDATE()", "oracle": "SYSDATE", "db2": "CURRENT TIMESTAMP"}


def load_spec(name_or_path: str) -> dict:
    p = Path(name_or_path)
    if not p.exists():
        p = CATALOG / (name_or_path if name_or_path.endswith((".yaml", ".yml")) else name_or_path + ".yaml")
    spec = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    spec["_path"] = str(p)
    return spec


def validate(spec: dict) -> list[str]:
    """Every problem in the spec, so the author fixes them in one pass."""
    errs = []
    name = str(spec.get("name") or "")
    if not name or not name.replace("_", "").isalnum() or not name.isupper():
        errs.append("name: required, UPPER_CASE letters/digits/underscore (it becomes the start center contentuid)")
    if not spec.get("description"):
        errs.append("description: required (start center title)")
    sql = [q.get("where") or "" for q in spec.get("queries") or []]
    sql += [(k.get("select") or "") + (k.get("where") or "") for k in spec.get("kpis") or []]
    if any("{now}" in x for x in sql) and spec.get("database") not in NOW:
        errs.append(f"database: required when SQL uses {{now}}; one of {sorted(NOW)}")
    if any(":sysdate" in x.lower() for x in sql):
        errs.append("SQL uses :sysdate, which Maximo does not bind; use {now} and set database:")
    queries = {q.get("name"): q for q in spec.get("queries") or []}
    for q in spec.get("queries") or []:
        for f in ("name", "app", "where"):
            if not q.get(f):
                errs.append(f"queries[{q.get('name', '?')}]: missing {f}")
    kpis = {k.get("name") for k in spec.get("kpis") or []}
    for k in spec.get("kpis") or []:
        n = k.get("name", "?")
        if not k.get("name") or not str(k["name"]).isupper():
            errs.append(f"kpis[{n}]: name required, UPPER case")
        if not k.get("select"):
            errs.append(f"kpis[{n}]: missing select (e.g. 'select count(*) from workorder')")
        if str(k.get("format", "DECIMAL")).upper() not in FORMATS:
            errs.append(f"kpis[{n}]: format must be one of {sorted(FORMATS)}")
        if len(k.get("caution") or [0, 0]) != 2:
            errs.append(f"kpis[{n}]: caution must be [min, max]")
    for w in spec.get("workqueues") or []:
        n = w.get("name", "?")
        for f in ("name", "query", "object_structure", "unique_column"):
            if not w.get(f):
                errs.append(f"workqueues[{n}]: missing {f}")
        if w.get("query") and w["query"] not in queries:
            errs.append(f"workqueues[{n}]: query {w['query']!r} is not in queries:")
    for i, p in enumerate(spec.get("portlets") or []):
        where = f"portlets[{i}] ({p.get('type', '?')})"
        if p.get("type") not in PORTLETS:
            errs.append(f"{where}: type must be one of {sorted(PORTLETS)}")
            continue
        if p.get("chart") and str(p.get("charttype", "BAR")).upper() not in CHARTS:
            errs.append(f"{where}: charttype must be one of {sorted(CHARTS)}")
        if p["type"] == "resultset":
            if p.get("query") not in queries:
                errs.append(f"{where}: query {p.get('query')!r} is not in queries:")
            if not p.get("columns"):
                errs.append(f"{where}: columns required")
            if p.get("chart") and p["chart"] not in (p.get("columns") or []):
                errs.append(f"{where}: chart column {p['chart']!r} must be one of its columns")
            for rule in p.get("highlight") or []:
                if rule.get("column") not in (p.get("columns") or []) or not rule.get("color") or "value" not in rule:
                    errs.append(f"{where}: highlight needs column (one of its columns), color and value")
        if p["type"] in ("kpilist", "kpigraph"):
            missing = [k for k in p.get("kpis") or [] if k not in kpis]
            if not p.get("kpis"):
                errs.append(f"{where}: kpis required")
            elif missing:
                errs.append(f"{where}: kpis {missing} are not in kpis:")
    if not spec.get("portlets"):
        errs.append("portlets: at least one portlet required")
    return errs


def _sql(text: str, database: str | None) -> str:
    return text.strip().replace("{now}", NOW.get(database or "", "{now}"))


def query_record(q: dict, owner: str, database: str | None = None) -> dict:
    return {"app": q["app"].upper(), "clausename": q["name"], "owner": q.get("owner", owner).upper(),
            "description": q.get("description") or q["name"], "clause": _sql(q["where"], database),
            "ispublic": bool(q.get("public", True)), "isuserlist": False, "langcode": "EN"}


def kpi_record(k: dict, database: str | None = None) -> dict:
    lo, hi = k.get("caution") or [0, 0]
    rec = {"kpiname": k["name"], "description": k.get("description") or k["name"],
           "selectstmt": _sql(k["select"], database), "format": str(k.get("format", "DECIMAL")).upper(),
           "target": float(k.get("target", 0)), "cautionmin": float(lo), "cautionmax": float(hi),
           "realtime": bool(k.get("realtime", True)), "trendenabled": bool(k.get("trend", False)),
           "ispublic": True}   # no langcode: MXAPIKPIMAIN defaults it and never returns it
    if k.get("where"):
        rec["clause"] = _sql(k["where"], database)
    return rec


def workqueue_record(w: dict, q: dict, owner: str) -> dict:
    # Children sorted the way Maximo returns them, so a deployed queue re-diffs `same`.
    cols = [{"attributename": c.upper(), "columnorder": i + 1} for i, c in enumerate(w.get("columns") or [])]
    acts = [{"action": a, "actionlabel": a, "actionorder": i + 1} for i, a in enumerate(w.get("actions") or [])]
    return {"queuename": w["name"].upper(), "description": w.get("description") or w["name"],
            "app": q["app"].upper(), "owner": q.get("owner", owner).upper(), "queuetype": "RESULTSET",
            "clausename": f"{q['app'].upper()}:{q['name']}",   # queues name their query APP:CLAUSENAME
            "intobjectname": w["object_structure"].upper(),
            "uniquecolumnname": w["unique_column"].upper(), "isactive": True, "langcode": "EN",
            "workqueuecols": sorted(cols, key=lambda c: c["attributename"]),
            "workqueueactions": sorted(acts, key=lambda a: a["action"])}


def presentation(spec: dict, queries: dict, owner: str) -> str:
    """Start center XML in the shape Maximo itself stores (attributes as in the OOTB templates)."""
    uid = spec["name"]
    root = ET.Element("startcenter", contentuid=uid, description=spec["description"],
                      layout=spec.get("layout", "NW"))
    order = {0: 0, 1: 0}
    for i, p in enumerate(spec["portlets"], 1):
        tag, pid = PORTLETS[p["type"]]
        col = int(p.get("column", 0))
        order[col] = order.get(col, 0) + 1
        puid = f"{uid}P{i}"
        el = ET.SubElement(root, tag, charttype=str(p.get("charttype", "BAR")).upper(), columnnum=str(col),
                           contentuid=puid, description=p.get("title") or tag, minormax="1",
                           ordernum=str(order[col]), portletid=pid, showchart="1" if p.get("chart") else "0")
        if p["type"] == "resultset":
            q = queries[p["query"]]
            el.set("queryapp", q["app"].upper())
            el.set("queryclausename", q["name"])
            el.set("queryowner", q.get("owner", owner).upper())
            flagged = {str(r["column"]).upper() for r in p.get("highlight") or []}
            for c in p["columns"]:
                c = c.upper()
                ET.SubElement(el, "attribute", columnorder="", contentuid=f"{puid}{c}", description=c, display="1",
                              isconditionset="1" if c in flagged else "0",
                              isgraphon="1" if c == str(p.get("chart", "")).upper() else "0", querycolumn=c)
            for rule in p.get("highlight") or []:   # Maximo colours rows where the flagged column matches
                ET.SubElement(el, "portletdisplay", color=rule["color"], expression=rule.get("expression", "="),
                              expvalue=str(rule["value"]))
        elif p["type"] in ("kpilist", "kpigraph"):
            for k in p["kpis"]:
                ET.SubElement(el, "kpi", kpiname=k)
        elif p["type"] == "favorites":
            for n, app in enumerate(p.get("apps") or [], 1):
                ET.SubElement(el, "application", app=app.upper(), ordernum=str(n))
        elif p["type"] == "quickinsert":
            for n, a in enumerate(p.get("apps") or [], 1):
                app = (a["app"] if isinstance(a, dict) else a).upper()
                label = a.get("label") if isinstance(a, dict) else None
                ET.SubElement(el, "action", app=app, contentuid=f"{puid}{app}INSERT",
                              description=label or f"New {app.title()}", optionname="INSERT", ordernum=str(n))
    ET.indent(root, "  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")   # Maximo trims a trailing newline


def build(name_or_path: str, write_manifest: bool = True) -> dict:
    """Write every record the spec describes into src/ plus manifests/<NAME>.yaml. Returns the file list."""
    spec = load_spec(name_or_path)
    errs = validate(spec)
    if errs:
        raise ValueError("dashboard spec has errors:\n  " + "\n  ".join(errs))
    owner = str(spec.get("owner", "MAXADMIN"))
    queries = {q["name"]: q for q in spec.get("queries") or []}
    written: list[tuple[str, Path, bool]] = []

    def save(type_id, rec):
        path, changed = store.save_json(registry.get(type_id), rec)
        written.append((type_id, path, changed))

    db = spec.get("database")
    for q in queries.values():
        save("query", query_record(q, owner, db))
    for k in spec.get("kpis") or []:
        save("kpi", kpi_record(k, db))
    for w in spec.get("workqueues") or []:
        save("workqueue", workqueue_record(w, queries[w["query"]], owner))
    save("startcenter", {"contentuid": spec["name"], "description": spec["description"],
                         "presentation": presentation(spec, queries, owner)})

    out = {"spec": spec["_path"], "files": [{"type": t, "file": _rel(p), "changed": c} for t, p, c in written]}
    if write_manifest:
        out["manifest"] = _rel(_write_manifest(spec, written))
    return out


def _write_manifest(spec: dict, written) -> Path:
    groups = spec.get("groups") or []
    manual = [f"Security Groups > {g}: set Start Center Template to '{spec['description']}' "
              f"(contentuid {spec['name']}); users get it at next login or Update Start Center" for g in groups]
    if not groups:
        manual.append(f"Security Groups: assign Start Center Template '{spec['description']}' to the groups that need it")
    apps = sorted({q["app"].upper() for q in spec.get("queries") or []})
    if apps:
        manual.append(f"Check those groups can read {', '.join(apps)}; result sets show nothing without app access")
    if any(not k.get("realtime", True) for k in spec.get("kpis") or []):
        manual.append("Non-realtime KPIs: confirm the KPI cron task (KPICronTask) is active")
    m = {"name": spec["name"], "description": f"Operational dashboard: {spec['description']}",
         "items": [{"path": [_rel(p) for _, p, _ in written]}], "manual": manual}
    path = MANIFESTS / f"{spec['name']}.yaml"
    header = f"# Generated by `maxdev dashboard build {Path(spec['_path']).stem}` — edit the spec, not this file.\n"
    store.write_text(path, header + yaml.safe_dump(m, sort_keys=False, allow_unicode=True, width=110))
    return path


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(p)
