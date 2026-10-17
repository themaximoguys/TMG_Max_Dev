"""Generate the TMG helper object structures from the tenant's own definitions.

Why: on MAS 9 with mxe.int.enableosauth=1, REST can only use an object structure
that has an authorisation app. Many config tables have no REST-usable structure
OOTB — they exist only as Migration Manager (DM*, usewith=MIGRATIONMGR, refused
by REST with BMXAA1283E) or as MX* integration structures with no authapp
(BMXAA9301E even for MAXADMIN).

Rule: a TMG clone is made ONLY when no REST-usable structure exists for the area.
Where IBM ships a working MXAPI* (MXAPIAUTOSCRIPT, MXAPIACTION, MXAPIWFPROCESS ...)
the registry uses it directly and nothing is cloned.

Fix without touching IBM's structures: clone the tenant's definition into a TMG*
INTEGRATION structure with an authapp. Reading the definitions is read-only;
`maxdev bootstrap --apply` creates them (needs MAXIMO_PROTECTED=false).
"""
from __future__ import annotations

import json

from .env import REPO
from .store import dumps

OUT = REPO / "bootstrap" / "15-integration" / "object-structures"

# new name: (source structure on tenant, authorisation app, purpose)
PLAN = {
    "TMGMXOBJECTCFG":       ("MXOBJECTCFG",       "CONFIGUR",   "Database Configuration objects/attributes"),
    "TMGMXAPIRELATIONSHIP": ("DMMAXRELATIONSHIP", "CONFIGUR",   "Relationships"),
    "TMGMXLOOKUPMAP":       ("DMMAXLOOKUPMAP",    "CONFIGUR",   "Lookup maps"),
    "TMGMXAPICONDITION":    ("DMCONDITION",       "CONDEXPMGR", "Conditional expressions"),
    "TMGMXAPICONDPROP":     ("DMCTRLGROUP",       "CONDEXPMGR", "Conditional UI (CTRLGROUP tree)"),
    "TMGMXAPISIGOPTION":    ("DMSIGOPTION",       "DESIGNER",   "Signature options"),
    "TMGMXAPIPRESENTATION": (None,                "DESIGNER",   "App Designer presentation XML (MAXPRESENTATION)"),
    "TMGMXAPIROLE":         ("DMROLE",            "ROLE",       "Workflow / escalation roles (MAXROLE)"),
    "TMGMXAPIESCALATION":   ("DMESCALATION",      "ESCALATION", "Escalations + ref points + notifications"),
    "TMGMXSCTEMPLATE":      ("DMSCTEMPLATE",      "STARTCNTR",  "Start center templates"),
    "TMGMXIFACEOUT":        ("MXIFACEOUT",        "PUBLISH",    "Publish channels"),
    "TMGMXIFACEIN":         ("DMMAXIFACEIN",      "INTSRV",     "Enterprise services"),
    "TMGMXIFACEINVOKE":     ("MXIFACEINVOKE",     "INVOKE",     "Invocation channels"),
    "TMGMXEXTSYSTEM":       ("MXEXTSYSTEM",       "EXTSYSTEM",  "External systems"),
    "TMGMXIFACECONTROL":    ("MXIFACECONTROL",    "EXTSYSTEM",  "Integration controls"),
    "TMGMXJSONMAPPING":     ("MXJSONMAPPING",     "JSONMAP",    "JSON mappings"),
}

DETAIL_DROP = {"maxintobjdetailid", "intobjectname", "href", "localref", "_rowstamp",
               "changeby", "changedate", "objectid", "parentobjid", "userdefined"}


def _clean_detail(d: dict) -> dict:
    return {k: v for k, v in d.items() if k not in DETAIL_DROP and not k.endswith(("_collectionref", "_description"))
            and not k.startswith("_") and not isinstance(v, (list, dict))}


def build(client, names: list[str] | None = None) -> list[dict]:
    want = {n: PLAN[n] for n in (names or PLAN)}
    sources = sorted({s for s, _, _ in want.values() if s})
    rows = client.query("MXINTOBJECT", where="intobjectname in [%s]" % ",".join('"%s"' % s for s in sources),
                        select="intobjectname,description,maxintobjdetail{*}", page_size=50)
    by = {r["intobjectname"]: r for r in rows}
    out = []
    for name, (src, app, purpose) in want.items():
        if src is None:
            details = [{"objectname": "MAXPRESENTATION", "hierarchypath": "MAXPRESENTATION",
                        "objectorder": 1, "processorder": 1}]
        else:
            if src not in by:
                out.append({"intobjectname": name, "_error": f"source {src} not on tenant"})
                continue
            details = [_clean_detail(d) for d in by[src].get("maxintobjdetail") or []]
            details.sort(key=lambda d: (str(d.get("hierarchypath", "")).count("/"), d.get("processorder") or 0))
        out.append({
            "intobjectname": name,
            "description": f"TMG REST transport: {purpose} (cloned from {src or 'MAXPRESENTATION'})"[:100],
            "usewith": "INTEGRATION",
            "authapp": app,
            "configurable": True,
            "queryonly": False,
            "maxintobjdetail": details,
        })
    return out


def write(defs: list[dict]) -> list[str]:
    OUT.mkdir(parents=True, exist_ok=True)
    files = []
    for d in defs:
        if "_error" in d:
            continue
        p = OUT / f"{d['intobjectname']}.json"
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dumps(d))
        files.append(str(p.relative_to(REPO)))
    return files


def summary(defs: list[dict]) -> str:
    return json.dumps([{"os": d["intobjectname"], "authapp": d.get("authapp"),
                        "objects": [x.get("hierarchypath") for x in d.get("maxintobjdetail", [])],
                        "error": d.get("_error")} for d in defs], indent=1)
