"""Extract / deploy / diff for every registered artifact type.

Shared by the CLI and the MCP server. Every function returns plain dicts so the
same result can be printed, written as a receipt, or returned to an AI agent.
Writes are dry-run unless apply=True, and are refused on protected environments.
"""
from __future__ import annotations

import datetime as dt
import difflib
import json
from pathlib import Path

from . import appxml as ax
from . import registry, store
from .client import MaximoClient, MaximoError, strip_meta
from .env import REPO, is_protected, load_env

STATE = REPO / ".maxdev"            # git-ignored: backups and receipts


class Session:
    """One environment: client + resolved settings."""

    def __init__(self, env: str | None = None, client: MaximoClient | None = None):
        self.target, self.vals = load_env(env)
        self.env = self.target.name
        self.client = client or MaximoClient(self.target)
        self.protected = is_protected(self.vals)

    def os_for(self, t: registry.ArtifactType) -> str:
        return t.resolve_os(self.client, self.vals)

    def guard_write(self):
        if self.protected:
            raise PermissionError(f"environment {self.env!r} is MAXIMO_PROTECTED — writes are refused")


def _rel(p: Path) -> str:
    p = p.resolve()
    return str(p.relative_to(REPO)) if REPO in p.parents else str(p)


def _stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


# ── extract ────────────────────────────────────────────────────────────────
def build_where(t: registry.ArtifactType, names: list[str] | None, like: str | None, where: str | None) -> str:
    if where:
        return where
    primary = t.key[0] if t.handler != "autoscript" else "autoscript"
    if names:
        vals = ",".join('"%s"' % n for n in names)
        return f"{primary} in [{vals}]"
    if like:
        return f'{primary}="{like if "%" in like else like + "%"}"'
    return ""


def extract(s: Session, type_id: str, names: list[str] | None = None, like: str | None = None,
            where: str | None = None, limit: int | None = None) -> dict:
    t = registry.get(type_id)
    if not t.os:
        return {"type": t.id, "skipped": f"handler={t.handler}: {t.note}"}
    os_name = s.os_for(t)
    w = build_where(t, names, like, where)
    if not w and not limit:
        raise ValueError(f"refusing to extract every {t.label} (thousands of OOTB rows). "
                         "Pass names, --like PREFIX, --where or --limit.")
    if t.handler == "appxml":
        return _extract_appxml(s, t, os_name, w, limit)
    recs = s.client.query(os_name, where=w, select=t.select, page_size=min(100, limit or 100), max_records=limit)
    written, unchanged, files = 0, 0, []
    for rec in recs:
        rec = strip_meta(rec)
        if t.handler == "autoscript":
            path, changed = store.save_script(t, rec)
        else:
            path, changed = store.save_json(t, rec)
        files.append(_rel(path))
        written += changed
        unchanged += not changed
    return {"type": t.id, "os": os_name, "where": w, "records": len(recs),
            "written": written, "unchanged": unchanged, "files": files}


def _live_presentation(s: Session, os_name: str, app: str) -> str | None:
    rows = s.client.query(os_name, where=f'app="{app.upper()}"', select="app,presentation", page_size=1)
    if rows and rows[0].get("presentation"):
        return rows[0]["presentation"]
    # Some tenants expose MAXPRESENTATION without the CLOB; fall back to the bootstrap script.
    try:
        txt = s.client.call_script("TMG_EXPORT_PRES", params={"app": app.upper()}, method="GET")
        if isinstance(txt, str) and txt.lstrip().startswith("<"):
            return txt
    except MaximoError:
        pass
    return None


def _extract_appxml(s, t, os_name, where, limit):
    apps = [r["app"] for r in s.client.query(os_name, where=where, select="app", max_records=limit)]
    files, written = [], 0
    for app in apps:
        xml = _live_presentation(s, os_name, app)
        if not xml:
            continue
        path, changed = store.save_appxml(t, app, xml)
        files.append(_rel(path))
        written += changed
    return {"type": t.id, "os": os_name, "records": len(apps), "written": written, "files": files}


# ── resolve local files ───────────────────────────────────────────────────
def resolve_files(type_id: str | None, names: list[str] | None, paths: list[str] | None) -> list[tuple]:
    """Returns [(ArtifactType, Path)] in deploy order."""
    out = []
    for p in paths or []:
        path = (REPO / p).resolve() if not Path(p).is_absolute() else Path(p)
        if path.is_dir():
            for f in sorted(path.rglob("*")):
                if f.is_file() and not f.name.startswith((".", "_")) and f.suffix in (".json", ".py", ".js", ".xml"):
                    t = registry.type_for_path(f)
                    if t:
                        out.append((t, f))
            continue
        t = registry.type_for_path(path)
        if not t:
            raise ValueError(f"{p}: not under any registered src/ folder")
        out.append((t, path))
    if type_id:
        t = registry.get(type_id)
        if names:
            for n in names:
                f = store.find_local(t, n)
                if not f:
                    raise FileNotFoundError(f"{t.id} {n!r} not found under {_rel(t.dir)}")
                out.append((t, f))
        elif not paths:
            out += [(t, f) for f in store.local_files(t)]
    seen, uniq = set(), []
    for t, f in out:
        if f.resolve() not in seen:
            seen.add(f.resolve())
            uniq.append((t, f))
    order = {t.id: i for i, t in enumerate(registry.ordered())}

    def sort_key(item):
        t, f = item
        sub = 0
        if t.id == "action":          # single actions before the groups that reference them
            try:
                sub = 1 if (store.load_json(f).get("type") or "").upper() == "GROUP" else 0
            except Exception:
                pass
        return (t.layer, order[t.id], sub, str(f))
    return sorted(uniq, key=sort_key)


# ── deploy ─────────────────────────────────────────────────────────────────
def deploy(s: Session, items: list[tuple], apply: bool = False, force_replace: bool = False,
           stop_on_fail: bool = True) -> dict:
    if apply:
        s.guard_write()
    stamp = _stamp()
    results, needs_dbconfig = [], False
    for t, path in items:
        res = {"type": t.id, "file": _rel(path)}
        try:
            if not t.deployable:
                res.update(action="skipped", reason=f"handler={t.handler}: {t.note}")
            else:
                rec = store.load_record(t, path)
                if rec.pop("_notes", None):
                    res["notes"] = store.parse_script(path).get("_notes")
                if t.handler == "autoscript":
                    from . import builder
                    issues = builder.lint_text(path.read_text(encoding="utf-8"), path.name)
                    errors = [i for i in issues if i["level"] == "error"]
                    if errors:
                        raise ValueError("lint errors (fix or see `maxdev lint`): " +
                                         "; ".join(f"L{i['line']} {i['rule']}" for i in errors[:8]))
                res["key"] = store.key_of(t, rec) if t.handler != "autoscript" else {"autoscript": rec["autoscript"]}
                os_name = s.os_for(t)
                res["os"] = os_name
                if t.handler == "appxml":
                    res.update(_deploy_appxml(s, os_name, rec, apply, force_replace, stamp))
                elif not apply:
                    hits = s.client.find(os_name, res["key"])
                    res["action"] = ("would-" + ("replace" if t.handler == "replace" else "update")) if hits else "would-create"
                elif t.handler == "replace":
                    res["action"] = s.client.replace(os_name, res["key"], rec)
                else:
                    res["action"] = s.client.upsert(os_name, res["key"], rec)
                if t.post == "apply-dbconfig" and res.get("action", "").startswith(("created", "updated", "would")):
                    needs_dbconfig = True
        except Exception as e:  # noqa: BLE001 — every failure is reported, never swallowed
            res.update(action="FAILED", error=str(e))
        results.append(res)
        if res["action"] == "FAILED" and stop_on_fail and apply:
            # Config changes are not a transaction: stop, report exactly what landed.
            results += [{"type": tt.id, "file": _rel(pp), "action": "not-attempted"}
                        for tt, pp in items[len(results):]]
            break
    summary = {}
    for r in results:
        summary[r["action"]] = summary.get(r["action"], 0) + 1
    receipt = {"env": s.env, "base_url": s.target.base_url, "mode": "APPLY" if apply else "DRY-RUN",
               "at": stamp, "summary": summary, "results": results,
               "dbconfig_pending": needs_dbconfig}
    if apply:
        d = STATE / "receipts" / s.env
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{stamp}.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        receipt["receipt"] = _rel(d / f"{stamp}.json")
    return receipt


def _deploy_appxml(s, os_name, rec, apply, force_replace, stamp) -> dict:
    app, repo_xml = rec["app"], rec["presentation"]
    live = _live_presentation(s, os_name, app)
    if live is None:
        cmp = {"verdict": "NEW", "loss": 0}
        payload = repo_xml
    else:
        cmp = ax.compare(live, repo_xml)
        payload = repo_xml
        if cmp["loss"] and not force_replace:
            payload, stats = ax.merge(live, repo_xml)
            cmp["merge"] = stats
    out = {"compare": cmp}
    if not apply:
        out["action"] = ("would-create" if live is None else
                         "would-merge" if payload is not repo_xml else "would-update")
        return out
    if live is not None:
        bdir = STATE / "backups" / s.env / stamp
        bdir.mkdir(parents=True, exist_ok=True)
        (bdir / f"{app}.xml").write_text(live, encoding="utf-8")
        out["backup"] = _rel(bdir / f"{app}.xml")
    body = {"app": app, "presentation": payload}
    if live is None:
        s.client.create(os_name, body)
    else:
        s.client.merge(s.client.presentation_href(app), body)
    after = _live_presentation(s, os_name, app)
    if ax.fingerprints(after) != ax.fingerprints(payload):
        raise MaximoError(500, f"{app}: read-back does not match what was sent (write silently dropped?)", os_name)
    out["action"] = "created" if live is None else ("merged" if payload is not repo_xml else "updated")
    return out


# ── diff / drift ───────────────────────────────────────────────────────────
def _drop_empty(node):
    """null, [] and {} mean the same thing to Maximo; never report them as a change."""
    if isinstance(node, dict):
        return {k: _drop_empty(v) for k, v in node.items() if v not in (None, [], {})}
    if isinstance(node, list):
        return [_drop_empty(x) for x in node]
    return node


def _canon(t, rec: dict) -> str:
    rec = _drop_empty(strip_meta(rec))
    if t.handler == "autoscript":
        rec = dict(rec)
        rec["source"] = store.strip_script_config((rec.get("source") or "").replace("\r\n", "\n")).rstrip("\n") + "\n"
    return store.dumps(rec)


def _subset(local, live):
    """Compare only the fields the repo declares: live rows carry many defaulted
    attributes a hand-written file never states."""
    if isinstance(local, dict) and isinstance(live, dict):
        return {k: _subset(v, live.get(k)) for k, v in local.items()}
    if isinstance(local, list) and isinstance(live, list) and len(local) == len(live):
        return [_subset(a, b) for a, b in zip(local, live)]
    return live


def diff(s: Session, items: list[tuple], full: bool = False) -> dict:
    out = []
    for t, path in items:
        rel = _rel(path)
        try:
            rec = store.load_record(t, path)
            os_name = s.os_for(t)
            if t.handler == "appxml":
                live = _live_presentation(s, os_name, rec["app"])
                out.append({"file": rel, "status": "missing-live" if live is None else
                            ("same" if ax.fingerprints(live) == ax.fingerprints(rec["presentation"]) else "changed"),
                            "compare": ax.compare(live, rec["presentation"]) if live else None})
                continue
            key = store.key_of(t, rec) if t.handler != "autoscript" else {"autoscript": rec["autoscript"]}
            hits = s.client.find(os_name, key, select=t.select if t.select != "*" else "*")
            if not hits:
                out.append({"file": rel, "status": "missing-live"})
                continue
            live = strip_meta(hits[0])
            if not full:
                live = _subset(rec, live)
            a, b = _canon(t, live).splitlines(), _canon(t, rec).splitlines()
            d = list(difflib.unified_diff(a, b, f"live:{s.env}", f"repo:{rel}", lineterm="", n=2))
            out.append({"file": rel, "status": "same" if not d else "changed", "diff": "\n".join(d[:400])})
        except Exception as e:  # noqa: BLE001
            out.append({"file": rel, "status": "error", "error": str(e)})
    return {"env": s.env, "results": out,
            "summary": {k: sum(1 for r in out if r["status"] == k) for k in {r["status"] for r in out}}}


# ── doctor ─────────────────────────────────────────────────────────────────
def doctor(s: Session) -> dict:
    who = s.client.whoami()
    rows = []
    for t in registry.ordered():
        if not t.os:
            rows.append({"type": t.id, "os": "-", "status": t.handler})
            continue
        probes = {o: s.client.os_probe(o) for o in t.os}
        ok = [o for o, v in probes.items() if v == "ok"]
        if ok:
            rows.append({"type": t.id, "os": ok[0], "status": "ok", "registry_status": t.status})
        else:
            unauth = [o for o, v in probes.items() if v == "unauthorized"]
            rows.append({"type": t.id, "os": " | ".join(f"{o}:{v}" for o, v in probes.items()),
                         "status": "NO-AUTH" if unauth else "MISSING", "registry_status": t.status})
    script = False
    try:
        s.client.call_script("TMG_EXPORT_PRES", params={"app": "STARTCNTR"}, method="GET")
        script = True
    except MaximoError:
        pass
    return {"env": s.env, "user": who.get("userName") or who.get("personid"), "protected": s.protected,
            "types": rows, "bootstrap": {"TMG_EXPORT_PRES": script}}
