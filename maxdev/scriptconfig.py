"""TMG house scriptConfig  <->  MXAPIAUTOSCRIPT record.

TMG scripts (catalog/templates, catalog/samples, TMG_MAX_CODE) end with a Jython dict:

    scriptConfig = {
        "autoscript": "WORKORDER.OBJ.SAVE.BEFORE", "description": "...", "version": "1.0.0",
        "active": True, "logLevel": "ERROR",
        "scriptLaunchPoints": [{"launchPointName": "...", "launchPointType": "OBJECT",
                                "objectName": "WORKORDER", "events": {"save": True, "beforesave": True}}]
    }

The dict is valid Jython (harmless at runtime), readable, and what the TMG standards
mandate, so it is the default format for new and extracted scripts.

Launch point events are sent through SCRIPTLAUNCHPOINT's helper flags (addaction,
saveaction, deleteaction, initaction, beforesave / validate, initializevalue, action,
listfilter). That is the route the reference repo deployed live on MAS 9; the raw
OBJECTEVENT bitmask (init 1, add 2, update 4, save 6 seen on tenants) is kept verbatim
when a record arrives without flags. aftersave/aftercommit flag names are status=verify.

Integration exits (PUBLISH/SYNC/INVOKE...) and CRONTASK "launch points" are not
SCRIPTLAUNCHPOINT rows in Maximo: integration scripts bind by name
(PUBLISH.<CHANNEL>.<EXIT>...), cron scripts run from a ScriptCrontask instance with the
SCRIPTNAME parameter. Those entries are kept in the file for documentation but not sent.
"""
from __future__ import annotations

import ast
import json

TOP = {"logLevel": "loglevel", "scriptLanguage": "scriptlanguage", "scriptLaunchPoints": "scriptlaunchpoint",
       "autoscriptVars": "autoscriptvars", "interface": "interface"}
LP = {"launchPointName": "launchpointname", "launchPointType": "launchpointtype", "objectName": "objectname",
      "attributeName": "attributename", "actionName": "actionname", "condition": "condition",
      "launchPointVars": "launchpointvars"}
OBJ_EVENTS = {"init": ["initaction"], "initialize": ["initaction"], "add": ["addaction"],
              "update": ["saveaction"], "save": ["addaction", "saveaction"], "delete": ["deleteaction"],
              "beforesave": [], "beforeSave": [], "aftersave": [], "afterSave": [],
              "aftercommit": [], "afterCommit": []}
ATTR_EVENTS = {"validate": "validate", "init": "initializevalue", "initValue": "initializevalue",
               "initializevalue": "initializevalue", "initialize": "initializevalue",
               "action": "action", "runAction": "action", "list": "listfilter", "listfilter": "listfilter"}
NOT_LAUNCH_POINTS = {"CRONTASK", "PUBLISH", "ENTERPRISE", "INVOCATION", "INVOKE", "SYNC", "OS",
                     "OBJECTSTRUCTURE", "ENDPOINT", "INTEGRATION", "ESCALATION"}
# TMG documentation-only keys: kept in the file, never sent to MXAPIAUTOSCRIPT.
TMG_META = {"cronSetup", "integrationBinding", "escalationSetup", "workflowSetup", "dependencies", "notes"}
API_TOP = {"autoscript", "description", "version", "active", "loglevel", "scriptlanguage", "scriptlaunchpoint",
           "autoscriptvars", "interface", "status", "category", "owner", "userdefined", "comments"}
_r_TOP = {v: k for k, v in TOP.items()}
_r_LP = {v: k for k, v in LP.items()}


def _object_flags(events: dict) -> tuple[dict, list[str]]:
    low = {k.lower(): bool(v) for k, v in events.items()}
    notes, out = [], {}
    unknown = [k for k in events if k.lower() not in {e.lower() for e in OBJ_EVENTS}]
    if unknown:
        notes.append(f"unknown object events {unknown} ignored")
    if low.get("init") or low.get("initialize"):
        out["initaction"] = True
    if "add" in low or "update" in low:          # explicit flags beat the generic 'save'
        add, upd = low.get("add", False), low.get("update", False)
    else:
        add = upd = low.get("save", False)
    if add:
        out["addaction"] = True
    if upd:
        out["saveaction"] = True
    if low.get("delete"):
        out["deleteaction"] = True
    if low.get("aftercommit"):
        out.update(beforesave=False, aftercommit=True)
        notes.append("aftercommit flag name is status=verify — confirm with `maxdev diff` after deploy")
    elif low.get("aftersave"):
        out.update(beforesave=False, aftersave=True)
        notes.append("aftersave flag name is status=verify — confirm with `maxdev diff` after deploy")
    elif add or upd or out.get("deleteaction"):
        out["beforesave"] = True
    return out, notes


def tmg_to_record(cfg: dict) -> tuple[dict, list[str]]:
    notes: list[str] = []
    rec = {}
    for k, v in cfg.items():
        if k == "scriptLaunchPoints":
            continue
        api = TOP.get(k, k)
        if k in TMG_META:
            continue
        if api not in API_TOP:
            notes.append(f"scriptConfig key {k!r} is not an MXAPIAUTOSCRIPT field — kept in file, not sent")
            continue
        rec[api] = v
    lps = []
    for lp in cfg.get("scriptLaunchPoints") or cfg.get("scriptlaunchpoint") or []:
        lptype = str(lp.get("launchPointType") or lp.get("launchpointtype") or "").upper()
        if lptype in NOT_LAUNCH_POINTS:
            notes.append(f"{lp.get('launchPointName')}: {lptype} is bound by name/cron instance, not a launch point — not sent")
            continue
        out, events = {}, {}
        obj_keys = {e.lower() for e in OBJ_EVENTS}
        for k, v in lp.items():
            if k == "events" and isinstance(v, dict):
                events.update(v)
            elif isinstance(v, bool) and lptype == "OBJECT" and k.lower() in obj_keys:
                events[k] = v
            elif isinstance(v, bool) and lptype == "ATTRIBUTE" and k in ATTR_EVENTS:
                events[k] = v
            else:
                out[LP.get(k, k)] = v
        if lptype == "OBJECT" and events:
            flags, n = _object_flags(events)
            out.update(flags)
            notes += [f"{out.get('launchpointname')}: {x}" for x in n]
        elif lptype == "ATTRIBUTE" and events:
            for ev, on in events.items():
                if on:
                    out[ATTR_EVENTS[ev]] = True
        lps.append(out)
    if lps or "scriptLaunchPoints" in cfg:
        rec["scriptlaunchpoint"] = lps
    rec.setdefault("scriptlanguage", "python")
    return rec, notes


def record_to_tmg(rec: dict) -> dict:
    cfg = {}
    order = ["autoscript", "description", "version", "active", "loglevel", "scriptlanguage"]
    for k in order + sorted(k for k in rec if k not in order and k not in ("source", "scriptlaunchpoint")):
        if k in rec:
            cfg[_r_TOP.get(k, "logLevel" if k == "loglevel" else k)] = rec[k]
    lps = []
    for lp in rec.get("scriptlaunchpoint") or []:
        lp = dict(lp)
        t = str(lp.get("launchpointtype", "")).upper()
        out, events = {}, {}
        if t == "OBJECT" and any(k in lp for k in ("addaction", "saveaction", "deleteaction", "initaction")):
            if lp.pop("initaction", False):
                events["init"] = True
            add, upd = lp.pop("addaction", False), lp.pop("saveaction", False)
            if add and upd:
                events["save"] = True
            elif add:
                events["add"] = True
            elif upd:
                events["update"] = True
            if lp.pop("deleteaction", False):
                events["delete"] = True
            bs, as_, ac = lp.pop("beforesave", None), lp.pop("aftersave", None), lp.pop("aftercommit", None)
            if ac:
                events["afterCommit"] = True
            elif as_ or bs is False:
                events["afterSave"] = True
            elif bs:
                events["beforesave"] = True
            lp.pop("objectevent", None)      # flags are authoritative when present
        if t == "ATTRIBUTE":
            for api in ("validate", "initializevalue", "action", "listfilter"):
                if lp.get(api) is True:
                    events[{"initializevalue": "initValue", "listfilter": "list"}.get(api, api)] = True
                    lp.pop(api)
        for k in ("launchpointname", "launchpointtype", "active", "objectname", "attributename", "actionname"):
            if k in lp:
                out[_r_LP.get(k, k)] = lp.pop(k)
        if events:
            out["events"] = events
        for k in sorted(lp):
            out[_r_LP.get(k, k)] = lp[k]
        lps.append(out)
    cfg["scriptLaunchPoints"] = lps
    return cfg


def parse_dict(text: str) -> dict:
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"scriptConfig is not a literal dict: {e}") from e


def render_dict(obj, indent: int = 0) -> str:
    """Jython-literal rendering: double-quoted strings, True/False/None, 4-space indent."""
    pad, inner = " " * indent, " " * (indent + 4)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = [f"{inner}{json.dumps(k)}: {render_dict(v, indent + 4)}" for k, v in obj.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(obj, list):
        if not obj:
            return "[]"
        return "[\n" + ",\n".join(inner + render_dict(v, indent + 4) for v in obj) + "\n" + pad + "]"
    if obj is True:
        return "True"
    if obj is False:
        return "False"
    if obj is None:
        return "None"
    return json.dumps(obj, ensure_ascii=False)
