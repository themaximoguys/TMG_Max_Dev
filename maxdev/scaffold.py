"""Templates for new artifacts, so new work starts in the repo format."""
from __future__ import annotations

from pathlib import Path

from . import registry, store

LP_TYPES = {"object", "attribute", "action", "condition", "crontask", "library", "integration"}

PY_BODY = {
    "object": '''from psdi.server import MXServer

# Implicit: mbo, app, user, onadd, onupdate, ondelete, service
if onadd or onupdate:
    pass
''',
    "attribute": '''# Implicit: mbo, mboValue, mbovalue, app, user, service
value = mbo.getString("{attr}")
if value and len(value) > 0:
    pass
    # service.error("tmg", "invalid{attr}")
''',
    "action": '''# Implicit: mbo, app, user, service (run from an action / escalation / workflow)
pass
''',
    "condition": '''# Implicit: mbo, evalresult (set True/False)
evalresult = False
''',
    "crontask": '''# Implicit: runAsUserInfo, arg (cron task parameter)
from psdi.server import MXServer
mx = MXServer.getMXServer()
''',
    "library": '''# Library script: call with service.invokeScript("{name}", ctx) or import via scriptlib
def run(ctx):
    return ctx
''',
    "integration": '''# Integration script. Implicit vars depend on the point (irData, erData, userExit...)
pass
''',
}


def autoscript(name: str, kind: str, obj: str | None = None, attr: str | None = None, js: bool = False) -> Path:
    if kind not in LP_TYPES:
        raise ValueError(f"--type must be one of {sorted(LP_TYPES)}")
    if kind in ("object", "attribute") and not obj:
        raise ValueError(f"--object is required for a {kind} launch point")
    if kind == "attribute" and not attr:
        raise ValueError("--attr is required for an attribute launch point")
    t = registry.get("autoscript")
    lp_name = name.replace(".", "_")[:30]
    rec: dict = {
        "autoscript": name.upper(),
        "description": f"TODO: describe {name}",
        "scriptlanguage": "javascript" if js else "python",
        "loglevel": "ERROR",
        "active": True,
        "source": "",
    }
    lp_type = {"object": "OBJECT", "attribute": "ATTRIBUTE", "action": "ACTION",
               "condition": "CUSTOMCONDITION", "crontask": "CRONTASK"}.get(kind)
    if lp_type:
        lp = {"launchpointname": lp_name.upper(), "launchpointtype": lp_type, "active": True,
              "description": rec["description"]}
        if obj:
            lp["objectname"] = obj.upper()
        if kind == "object":
            lp.update({"objectevent": 1, "addaction": True, "saveaction": True, "beforesave": True})
        if kind == "attribute":
            lp.update({"attributename": attr.upper(), "attributeevent": 0})   # 0 = validate
        rec["scriptlaunchpoint"] = [lp]
    body = PY_BODY[kind].format(attr=(attr or "").upper(), name=name.upper())
    if js:
        body = "// " + body.replace("\n", "\n// ") + "\n"
    rec["source"] = body
    if kind == "integration":
        rec["autoscript"] = rec["autoscript"]
    path, _ = store.save_script(t, rec)
    if kind == "integration" and path.parent.name != "integration":
        target = t.dir / "integration" / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        path.rename(target)
        path = target
    return path
