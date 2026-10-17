"""Database Configuration, Admin Mode and Migration Manager over REST.

What IBM documents (REST API guide, migrationmanager/api):
  POST adminmode/on {"numsessions":5,"logoutmin":1}   GET adminmode/state (0 off, 1 on, 2 pending)
  POST adminmode/off
  POST dm/create  {"pkgdefname","readme"}   POST dm/distribute   GET dm/download
  POST dm/upload?filename=   POST dm/deploy   POST dm/completedeploy

What IBM does NOT document: a REST "Apply Configuration Changes". Non-structural
changes apply live; structural ones need Admin Mode + configdb. This module
therefore applies through an automation script you install (MAXIMO_DBCONFIG_SCRIPT,
default TMG.CONFIGDB.APPLY) and always reports what is still pending, read from
MAXOBJECTCFG.CHANGED, so nothing is assumed.

The base path of these services differs between releases (reports of /dm/* not
found on MAS 9). Prefix is MAXIMO_SERVICE_PREFIX (default "api"); `maxdev doctor`
probes it. Treat every call here as status=verify until proven on your tenant.
"""
from __future__ import annotations

from .client import MaximoError


def _prefix(s) -> str:
    return s.vals.get("MAXIMO_SERVICE_PREFIX", "api").strip("/")


def dbconfig_pending(s) -> dict:
    rows = s.client.query("MXOBJECTCFG", where='changed!="N"', select="objectname,changed,description",
                          page_size=200)
    return {"env": s.env, "pending": [{"objectname": r.get("objectname"), "changed": r.get("changed")} for r in rows],
            "count": len(rows),
            "hint": "CHANGED values: I=new object, Y=structural change pending, N=applied"}


def adminmode_state(s) -> dict:
    r = s.client.request("GET", f"{_prefix(s)}/adminmode/state")
    return {"env": s.env, "state": r}


def adminmode(s, on: bool, sessions: int = 5, logout_min: int = 1) -> dict:
    s.guard_write()
    path = f"{_prefix(s)}/adminmode/{'on' if on else 'off'}"
    body = {"numsessions": sessions, "logoutmin": logout_min} if on else {}
    return {"env": s.env, "result": s.client.request("POST", path, body=body)}


def dbconfig_apply(s, admin: bool = False) -> dict:
    """Runs the configured apply script, optionally wrapped in Admin Mode."""
    s.guard_write()
    script = s.vals.get("MAXIMO_DBCONFIG_SCRIPT", "TMG.CONFIGDB.APPLY")
    before = dbconfig_pending(s)["count"]
    out = {"env": s.env, "script": script, "pending_before": before}
    if before == 0:
        out["result"] = "nothing pending"
        return out
    if admin:
        out["adminmode_on"] = adminmode(s, True)["result"]
    try:
        out["result"] = s.client.call_script(script, body={"admin": admin})
    except MaximoError as e:
        out["error"] = (f"{e}. Install bootstrap/autoscripts/{script}.py (maxdev bootstrap) "
                        "or apply in Database Configuration > Apply Configuration Changes.")
    finally:
        if admin:
            try:
                out["adminmode_off"] = adminmode(s, False)["result"]
            except MaximoError as e:
                out["adminmode_off_error"] = str(e) + "  <-- TURN ADMIN MODE OFF MANUALLY"
    out["pending_after"] = dbconfig_pending(s)["count"]
    return out


# ── Migration Manager ──────────────────────────────────────────────────────
def dm_create(s, pkgdef: str, readme: str = "") -> dict:
    s.guard_write()
    return s.client.request("POST", f"{_prefix(s)}/dm/create", body={"pkgdefname": pkgdef, "readme": readme})


def dm_download(s, pkgdef: str, package_id, out_path) -> str:
    r = s.client.request("GET", f"{_prefix(s)}/dm/download",
                         params={"dmpackagedef": pkgdef, "dmpackageid": package_id}, raw=True)
    with open(out_path, "wb") as fh:
        fh.write(r.content)
    return str(out_path)


def dm_upload(s, zip_path) -> dict:
    s.guard_write()
    from pathlib import Path
    p = Path(zip_path)
    return s.client.request("POST", f"{_prefix(s)}/dm/upload", params={"filename": p.name}, body=p.read_bytes(),
                            headers={"Content-Type": "application/octet-stream"})


def dm_deploy(s, complete: bool = False) -> dict:
    s.guard_write()
    return s.client.request("POST", f"{_prefix(s)}/dm/{'completedeploy' if complete else 'deploy'}", body={})
