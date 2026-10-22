"""Dashboard builder: one YAML spec -> every record behind an operations dashboard.

Two Manage front ends share the same building blocks:
  Operational Dashboard (OPDASHBOARD)  cards read KPIs and work queues; layout lives in VIEWMANAGER
  start center (classic home page)     portlets read saved queries and KPIs; layout in SCTEMPLATE

  catalog/dashboards/<NAME>.yaml           the spec (see maintenance_supervisor.yaml)
    -> src/02-security/groups/             optional dedicated security group
    -> src/02-security/app-rights/         OPDASHBOARD rights + READ on the object structures cards use
    -> src/07-app-designer/_queries/       saved queries for result sets and work queues
    -> src/19-kpi/                         KPI definitions (KPI value / trend / comparison cards, KPI portlets)
    -> src/07-app-designer/_workqueues/    work queues (work queue, map and table cards; result-set style lists)
    -> src/07-app-designer/_views/         the Operational Dashboard view (VIEWMANAGER row)
    -> src/07-app-designer/_startcenters/  the start center template (presentation XML)
    -> manifests/<NAME>.yaml               deploy order + the manual steps no API covers

Card definitions inside an Operational Dashboard view are the app's own JSON, which IBM does not
document. Build cards once in the app, `maxdev extract view`, and point `opdashboard.cards_from` at
that file; the builder then carries those cards into every rebuild and environment.

Nothing here talks to Maximo. Deploy the manifest the usual way:
`maxdev deploy --manifest NAME` (dry run), then `--apply` after a yes.
"""
from __future__ import annotations

import json
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
# Operational Dashboard rights (OPDASHBOARD sig options on MAS 9) and what each needs on MXAPIVIEWMANAGER.
# Cards read through these object structures, so a group without READ on them sees empty cards (BMXAA0024E).
# Granted through MXAPIGROUP maxapps (`apprights`): APPLICATIONAUTH via TMGMXAPIGRANT rejects these app
# types with BMXAA4191E (seen on demo).
DASH_RIGHTS = {"READ": [], "INSERT_PRIVATE": ["SAVE", "INSERT"], "INSERT_PUBLIC": ["SAVE", "INSERT"],
               "MANAGE_PRIVATE": ["SAVE"], "HIDE_PUBLIC": ["SAVE"], "DELETE_PUBLIC": ["DELETE"]}
CARD_SOURCES = ["MXAPIVIEWMANAGER", "MXAPIWORKQUEUE", "MXAPIWFASSIGNMENT", "MXAPIPERSON", "MXAPIKPIMAIN"]
OPD_COMPONENT = "NX_PV"     # componentid of every OPDASHBOARD view on MAS 9 (OOTB and user-made)


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
        errs.append("name: required, UPPER_CASE letters/digits/underscore (start center contentuid, manifest name)")
    if not spec.get("description"):
        errs.append("description: required (dashboard title)")
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
        for a in w.get("actions") or []:
            if not (a.get("action") if isinstance(a, dict) else a):
                errs.append(f"workqueues[{n}]: each action needs an action name (an Actions app record)")
    errs += _validate_opdashboard(spec, kpis, {w.get("name") for w in spec.get("workqueues") or []})
    sec = spec.get("security") or {}
    bad = [r for r in sec.get("dashboard_rights") or [] if r not in DASH_RIGHTS]
    if bad:
        errs.append(f"security.dashboard_rights: {bad} not in {sorted(DASH_RIGHTS)}")
    if sec.get("create_group") and not sec.get("groups"):
        errs.append("security.create_group: needs security.groups (the first one is created)")
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
    if not spec.get("portlets") and not spec.get("opdashboard"):
        errs.append("portlets or opdashboard: build at least one front end")
    return errs


def _validate_opdashboard(spec: dict, kpis: set, queues: set) -> list[str]:
    o = spec.get("opdashboard")
    if not o:
        return []
    errs = []
    vid = str(o.get("id") or "")
    if not vid or not vid.replace("_", "").isalnum() or not vid.isupper():
        errs.append("opdashboard.id: required, UPPER_CASE (VIEWMANAGER viewid)")
    if not o.get("title"):
        errs.append("opdashboard.title: required (dashboard tab name)")
    if o.get("cards_from"):
        try:
            _cards_from(o["cards_from"])
        except (OSError, ValueError, KeyError) as e:
            errs.append(f"opdashboard.cards_from: {e}")
    for k in o.get("kpis") or []:
        if k not in kpis:
            errs.append(f"opdashboard.kpis: {k!r} is not in kpis:")
    for q in o.get("workqueues") or []:
        if q not in queues:
            errs.append(f"opdashboard.workqueues: {q!r} is not in workqueues:")
    return errs


def _cards_from(path: str) -> dict:
    """The delta (cards + layouts) of a view extracted with `maxdev extract view`."""
    p = Path(path) if Path(path).is_absolute() else REPO / path
    rec = json.loads(p.read_text(encoding="utf-8"))
    if (rec.get("app") or "").upper() != "OPDASHBOARD":
        raise ValueError(f"{path} is not an OPDASHBOARD view")
    delta = json.loads(rec["content"]).get("delta") or {}
    return {"cards": delta.get("cards") or [], "layouts": delta.get("layouts") or {}}


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
    acts = []
    for i, a in enumerate(w.get("actions") or []):     # "WO COMP" or {action, label, completes}
        a = a if isinstance(a, dict) else {"action": a}
        row = {"action": a["action"], "actionlabel": a.get("label") or a["action"], "actionorder": i + 1}
        if a.get("completes"):
            row["completes"] = True     # the record leaves the queue once this action runs
        acts.append(row)
    return {"queuename": w["name"].upper(), "description": w.get("description") or w["name"],
            "app": q["app"].upper(), "owner": q.get("owner", owner).upper(), "queuetype": "RESULTSET",
            "clausename": f"{q['app'].upper()}:{q['name']}",   # queues name their query APP:CLAUSENAME
            "intobjectname": w["object_structure"].upper(),
            "uniquecolumnname": w["unique_column"].upper(), "isactive": bool(w.get("active", True)), "langcode": "EN",
            "workqueuecols": sorted(cols, key=lambda c: c["attributename"]),
            "workqueueactions": sorted(acts, key=lambda a: a["action"])}


def view_record(spec: dict) -> dict:
    """Operational Dashboard view, in the exact shape demo's OOTB OPDASHBOARD rows use."""
    o = spec["opdashboard"]
    delta = _cards_from(o["cards_from"]) if o.get("cards_from") else {"cards": [], "layouts": {}}
    desc = o.get("description") or spec["description"]
    content = {"delta": delta, "viewName": o["title"], "isDefault": bool(o.get("default", False)),
               "isPublic": bool(o.get("public", True)), "description": desc}
    return {"app": "OPDASHBOARD", "componentid": OPD_COMPONENT, "viewid": o["id"], "viewname": o["title"],
            "description": desc, "viewtype": "DASHBOARD", "userid": str(o.get("owner", spec.get("owner", "MAXADMIN"))).upper(),
            "ispublic": content["isPublic"], "isdefault": content["isDefault"],
            "content": json.dumps(content, separators=(",", ":"), ensure_ascii=False)}


def dashboard_rights(rights: list[str]) -> dict[str, list[str]]:
    """app -> sig options a group needs to use the dashboard (SAVE before INSERT, as Maximo requires)."""
    out = {"OPDASHBOARD": list(rights), "MXAPIVIEWMANAGER": ["READ"]}
    for r in rights:
        out["MXAPIVIEWMANAGER"] += [o for o in DASH_RIGHTS[r] if o not in out["MXAPIVIEWMANAGER"]]
    for app in CARD_SOURCES[1:]:
        out[app] = ["READ"]
    return out


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

    sec = spec.get("security") or {}
    groups = [g.upper() for g in sec.get("groups") or []]
    if sec.get("create_group"):
        save("securitygroup", {"groupname": groups[0], "description": sec.get("group_description") or spec["description"],
                               "independent": True})
    if spec.get("opdashboard"):
        t = registry.get("apprights")
        for g in groups:
            f = t.dir / f"{store.filename(t, {'groupname': g})}.json"
            rights = store.load_json(f)["rights"] if f.exists() else {}   # grant-only: keep what is there
            for app, opts in dashboard_rights(sec.get("dashboard_rights") or ["READ"]).items():
                rights[app] = rights.get(app, []) + [o for o in opts if o not in rights.get(app, [])]
            save("apprights", {"groupname": g, "rights": rights})
    db = spec.get("database")
    for q in queries.values():
        save("query", query_record(q, owner, db))
    for k in spec.get("kpis") or []:
        save("kpi", kpi_record(k, db))
    for w in spec.get("workqueues") or []:
        save("workqueue", workqueue_record(w, queries[w["query"]], owner))
    if spec.get("opdashboard"):
        save("view", view_record(spec))
    if spec.get("portlets"):
        save("startcenter", {"contentuid": spec["name"], "description": spec["description"],
                             "presentation": presentation(spec, queries, owner)})

    out = {"spec": spec["_path"], "files": [{"type": t, "file": _rel(p), "changed": c} for t, p, c in written]}
    if write_manifest:
        out["manifest"] = _rel(_write_manifest(spec, written))
    return out


def manual_steps(spec: dict) -> list[str]:
    """What no REST call can do: both assignments below store generated ids (sctemplateid, viewmanagerid)."""
    sec = spec.get("security") or {}
    groups = [g.upper() for g in sec.get("groups") or []] or ["<each group that needs it>"]
    o = spec.get("opdashboard")
    steps = []
    for g in groups:
        if o:
            steps.append(f"Security Groups > {g} > Operational Dashboard tab > Select Dashboards: add '{o['title']}' "
                         f"(viewid {o['id']}); this writes DASHBOARDAUTH")
        if spec.get("portlets"):
            steps.append(f"Security Groups > {g}: set Start Center Template to '{spec['description']}' "
                         f"(contentuid {spec['name']}); users get it at next login or Update Start Center")
    if sec.get("create_group"):
        steps.append(f"Security Groups > {groups[0]}: add the users (or include it in their existing groups)")
    apps = sorted({q["app"].upper() for q in spec.get("queries") or []})
    if apps:
        steps.append(f"Check those groups can read {', '.join(apps)}; queues and result sets show nothing without app access")
    if spec.get("workqueues"):
        steps.append("Work Queue Manager: add person-group members to restricted queues (members have no REST "
                     "structure); public queues need nothing")
    if o and not o.get("cards_from"):
        cards = [f"KPI {k}" for k in o.get("kpis") or []] + [f"work queue {q}" for q in o.get("workqueues") or []]
        steps.append(f"Operational Dashboard > '{o['title']}' > Edit > Card gallery: add cards for "
                     f"{', '.join(cards) or 'the KPIs and work queues above'}; then `maxdev extract view --where "
                     f"'app=\"OPDASHBOARD\" and viewid=\"{o['id']}\"'`, set opdashboard.cards_from to that file and rebuild")
    if o and o.get("data_source_cards"):
        steps.append("Value / Table / Gauge cards need a data source defined in the OPDASHBOARD app (MAF Configuration, "
                     "src/18-mobile/maf-apps); work queue cards need none")
    if any(not k.get("realtime", True) or k.get("trend") for k in spec.get("kpis") or []):
        steps.append("KPI trend cards and non-realtime KPIs: Cron Task Setup > KPICronTask > KPINONREALTIME: set a "
                     "schedule and activate it, so KPIHISTORY gets at least two points")
    return steps


def _write_manifest(spec: dict, written) -> Path:
    manual = manual_steps(spec)
    m = {"name": spec["name"], "description": f"Dashboard: {spec['description']}",
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
