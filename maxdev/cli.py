"""maxdev — Maximo development from the command line.

  maxdev envs                                 list configured environments
  maxdev ping     [--env dev]                 who am I, is the API reachable
  maxdev doctor   [--env dev]                 which object structures exist for every type
  maxdev types                                registry: every Maximo area and how it is handled
  maxdev ls       [TYPE]                      artifacts in the repo
  maxdev extract  TYPE [NAME ...] [--like TMG] [--where ...] [--limit N]
  maxdev diff     TYPE [NAME ...] | --path P  repo vs live
  maxdev deploy   TYPE [NAME ...] | --path P | --manifest M   [--apply] [--force-replace]
  maxdev dbconfig status | apply [--admin] [--apply]
  maxdev adminmode state | on | off [--apply]
  maxdev query    OS [--where W] [--select S] [--limit N]
  maxdev schema   OS                          JSON schema of an object structure
  maxdev script   NAME [--param k=v] [--body JSON] [--apply]   plan/call a script handler
  maxdev data     export OS --where W --out F | load OS FILE --key k1,k2 [--apply]
  maxdev dm       create PKGDEF | download PKGDEF ID OUT | upload ZIP | deploy [--complete]  (writes need --apply)
  maxdev templates                            TMG script templates (catalog/templates)
  maxdev build    KIND --object O [--attr A] [--name N] [--logging service]   new script from a TMG template
  maxdev lint     [PATH ...]                  TMG standards check (default: all scripts in src/)
  maxdev java     analyze FILE.java [...]     which template / launch point a Java class converts to
  maxdev new      autoscript NAME --type object|attribute|action|library|... (minimal skeleton)
  maxdev bootstrap [authapps|generate] [--apply]  1) authapps: set auth app on IBM MX* structures
                                              2) deploy TMG structures only where none is REST-usable
  maxdev ibm-mcp  info | tools | call NAME [--args JSON] [--apply]   IBM MAS 9.2 MCP server

Writes are dry runs unless --apply is given. Environments marked
MAXIMO_PROTECTED=true refuse every write.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import admin, bootstrap_gen, builder, data, engine, ibm_mcp, manifest, registry, scaffold, store
from .env import REPO, list_envs


def _print(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def _items(a):
    if getattr(a, "manifest", None):
        m = manifest.load(a.manifest)
        for step in m.get("manual") or []:
            print(f"  [MANUAL] {step}", file=sys.stderr)
        return manifest.items(m)
    return engine.resolve_files(a.type, a.names or None, a.path or None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="maxdev", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--env", default=None, help="environment name (environments/.env.<name>); default MAXIMO_ENV or dev")
    sub = p.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--env", default=argparse.SUPPRESS, help="environment name")
    _add = sub.add_parser
    sub.add_parser = lambda *a_, **k: _add(*a_, parents=[common], **k)

    sub.add_parser("envs")
    sub.add_parser("ping")
    sub.add_parser("doctor")
    sub.add_parser("types")
    x = sub.add_parser("ls"); x.add_argument("type", nargs="?")

    x = sub.add_parser("extract")
    x.add_argument("type"); x.add_argument("names", nargs="*")
    x.add_argument("--like"); x.add_argument("--where"); x.add_argument("--limit", type=int)

    for name in ("diff", "deploy"):
        x = sub.add_parser(name)
        x.add_argument("type", nargs="?"); x.add_argument("names", nargs="*")
        x.add_argument("--path", action="append"); x.add_argument("--manifest")
        if name == "deploy":
            x.add_argument("--apply", action="store_true", help="really write (default: dry run)")
            x.add_argument("--force-replace", action="store_true", help="appxml: overwrite instead of additive merge")
            x.add_argument("--keep-going", action="store_true", help="do not stop at the first failure")
        else:
            x.add_argument("--full", action="store_true", help="compare every live field, not just those in the repo file")

    x = sub.add_parser("dbconfig"); x.add_argument("action", choices=["status", "apply"]); x.add_argument("--admin", action="store_true")
    x.add_argument("--apply", action="store_true", help="execute configuration changes (default: dry run)")
    x = sub.add_parser("adminmode"); x.add_argument("action", choices=["state", "on", "off"])
    x.add_argument("--apply", action="store_true", help="change Admin Mode (default: dry run)")

    x = sub.add_parser("query"); x.add_argument("os"); x.add_argument("--where", default="")
    x.add_argument("--select", default="*"); x.add_argument("--limit", type=int, default=20)
    x = sub.add_parser("schema"); x.add_argument("os")
    x = sub.add_parser("script"); x.add_argument("name"); x.add_argument("--param", action="append", default=[])
    x.add_argument("--body"); x.add_argument("--get", action="store_true")
    x.add_argument("--apply", action="store_true", help="invoke the script, including GET handlers (default: dry run)")

    x = sub.add_parser("data"); ds = x.add_subparsers(dest="dcmd", required=True)
    y = ds.add_parser("export"); y.add_argument("os"); y.add_argument("--where", default=""); y.add_argument("--select", default="*")
    y.add_argument("--out", required=True); y.add_argument("--limit", type=int)
    y = ds.add_parser("load"); y.add_argument("os"); y.add_argument("file"); y.add_argument("--key", default="")
    y.add_argument("--apply", action="store_true"); y.add_argument("--all-or-nothing", action="store_true")

    x = sub.add_parser("dm"); dm = x.add_subparsers(dest="dcmd", required=True)
    y = dm.add_parser("create"); y.add_argument("pkgdef"); y.add_argument("--readme", default="")
    y.add_argument("--apply", action="store_true")
    y = dm.add_parser("download"); y.add_argument("pkgdef"); y.add_argument("id"); y.add_argument("out")
    y = dm.add_parser("upload"); y.add_argument("zip")
    y.add_argument("--apply", action="store_true")
    y = dm.add_parser("deploy"); y.add_argument("--complete", action="store_true")
    y.add_argument("--apply", action="store_true")

    x = sub.add_parser("new"); x.add_argument("kind", choices=["autoscript"]); x.add_argument("name")
    x.add_argument("--type", default="library", choices=sorted(scaffold.LP_TYPES))
    x.add_argument("--object"); x.add_argument("--attr"); x.add_argument("--js", action="store_true")

    x = sub.add_parser("bootstrap"); x.add_argument("action", nargs="?", default="deploy", choices=["deploy", "generate", "authapps"])
    x.add_argument("--apply", action="store_true"); x.add_argument("--only", nargs="*")
    sub.add_parser("templates")
    x = sub.add_parser("build"); x.add_argument("kind", choices=sorted(builder.KINDS))
    for o in ("object", "attr", "name", "channel", "service", "author", "description", "java_class", "autoscript"):
        x.add_argument("--" + o.replace("_", "-"), default="")
    x.add_argument("--exit-type", default="USEREXIT"); x.add_argument("--logging", default="mxlogger", choices=["mxlogger", "service"])
    x = sub.add_parser("lint"); x.add_argument("paths", nargs="*")
    x = sub.add_parser("java"); x.add_argument("action", choices=["analyze"]); x.add_argument("files", nargs="+")
    x = sub.add_parser("ibm-mcp"); x.add_argument("action", choices=["info", "tools", "call"])
    x.add_argument("name", nargs="?"); x.add_argument("--args", default="{}")
    x.add_argument("--apply", action="store_true", help="allow tools not annotated read-only")

    a = p.parse_args(argv)

    try:
        if a.cmd == "envs":
            _print(list_envs()); return 0
        if a.cmd == "types":
            layers, _ = registry.load()
            for t in registry.ordered():
                os_ = " | ".join(t.os) or "-"
                print(f"L{t.layer:<3}{t.id:<18}{t.handler:<11}{t.status:<7}{os_:<38}src/{t.folder}")
            return 0
        if a.cmd == "ls":
            for t in ([registry.get(a.type)] if a.type else registry.ordered()):
                for f in store.local_files(t):
                    print(f"{t.id:<18}{f.relative_to(REPO)}")
            return 0
        if a.cmd == "templates":
            for t in builder.list_templates():
                print(f"  {t['kind']:<20}{t['logging']:<10}{t['name_pattern']:<38}{t['file']}")
            return 0
        if a.cmd == "build":
            path, issues = builder.build(a.kind, object_name=a.object, field=a.attr, name=a.name, channel=a.channel,
                                         service_name=a.service, exit_type=a.exit_type, logging=a.logging,
                                         author=a.author, description=a.description, java_class=a.java_class,
                                         autoscript=a.autoscript)
            print(f"created {path.relative_to(REPO)}")
            for i in issues:
                print(f"  [{i['level']}] {i['rule']}: {i['msg']}")
            return 0
        if a.cmd == "lint":
            files = [Path(p) for p in a.paths] or sorted(list((REPO / "src/09-automation-scripts").rglob("*.py")))
            bad = 0
            for f in files:
                for i in builder.lint_text(f.read_text(encoding="utf-8"), f.name):
                    bad += i["level"] == "error"
                    print(f"{f}:{i['line']}: [{i['level']}] {i['rule']}: {i['msg']}")
            print(f"{len(files)} file(s), {bad} error(s)")
            return 1 if bad else 0
        if a.cmd == "java":
            for f in a.files:
                _print(builder.analyze_java(Path(f)))
            return 0
        if a.cmd == "new":
            path = scaffold.autoscript(a.name, a.type, a.object, a.attr, js=a.js)
            print(f"created {path.relative_to(REPO)}"); return 0

        s = engine.Session(a.env)
        # Match MCP's dry-run contract for every imperative write command.
        # GET script handlers can mutate too; the HTTP verb is not a safety signal.
        writes = (a.cmd == "script" or
                  (a.cmd == "dbconfig" and a.action == "apply") or
                  (a.cmd == "adminmode" and a.action != "state") or
                  (a.cmd == "dm" and a.dcmd != "download"))
        if writes:
            if not a.apply:
                _print({"mode": "DRY-RUN", "env": s.env,
                        "command": {k: v for k, v in vars(a).items() if k != "apply"}})
                return 0
            s.guard_write()
        if a.cmd == "ping":
            who = s.client.whoami()
            _print({"env": s.env, "base_url": s.target.base_url, "protected": s.protected,
                    "user": who.get("userName") or who.get("personid"), "insertSite": who.get("insertSite")})
        elif a.cmd == "doctor":
            r = engine.doctor(s)
            print(f"env={r['env']} user={r['user']} protected={r['protected']}")
            for row in r["types"]:
                print(f"  {row['type']:<18}{row['status']:<9}{row['os']}")
            print(f"  bootstrap TMG_EXPORT_PRES: {'installed' if r['bootstrap']['TMG_EXPORT_PRES'] else 'missing (maxdev bootstrap)'}")
        elif a.cmd == "extract":
            _print(engine.extract(s, a.type, a.names or None, a.like, a.where, a.limit))
        elif a.cmd == "diff":
            r = engine.diff(s, _items(a), full=a.full)
            for row in r["results"]:
                print(f"[{row['status']}] {row['file']}")
                if row.get("diff"):
                    print(row["diff"])
                if row.get("error"):
                    print("   ", row["error"])
            print(r["summary"])
        elif a.cmd == "deploy":
            items = _items(a)
            if not items:
                print("nothing to deploy"); return 1
            r = engine.deploy(s, items, apply=a.apply, force_replace=a.force_replace, stop_on_fail=not a.keep_going)
            for row in r["results"]:
                extra = row.get("error") or (row.get("compare") or {}).get("verdict", "")
                print(f"  {row['action']:<15}{row['type']:<16}{row['file']}  {extra}")
            print(f"{r['mode']} {r['env']}: {r['summary']}")
            if r["dbconfig_pending"]:
                print("  ! Database Configuration rows changed — run `maxdev dbconfig status` then apply.")
            if r.get("receipt"):
                print(f"  receipt: {r['receipt']}")
            return 1 if r["summary"].get("FAILED") else 0
        elif a.cmd == "dbconfig":
            _print(admin.dbconfig_pending(s) if a.action == "status" else admin.dbconfig_apply(s, admin=a.admin))
        elif a.cmd == "adminmode":
            _print(admin.adminmode_state(s) if a.action == "state" else admin.adminmode(s, a.action == "on"))
        elif a.cmd == "query":
            _print(s.client.query(a.os, where=a.where, select=a.select, max_records=a.limit))
        elif a.cmd == "schema":
            _print(s.client.request("GET", f"api/jsonschema/{a.os.lower()}", params={"oslc.select": "*"}))
        elif a.cmd == "script":
            params = dict(kv.split("=", 1) for kv in a.param)
            body = json.loads(a.body) if a.body else None
            _print(s.client.call_script(a.name, params=params, body=body, method="GET" if a.get else "POST"))
        elif a.cmd == "data":
            if a.dcmd == "export":
                _print(data.export(s, a.os, a.where, a.select, Path(a.out), a.limit))
            else:
                key = [k for k in a.key.split(",") if k]
                _print(data.load(s, a.os, Path(a.file), key, apply=a.apply, all_or_nothing=a.all_or_nothing))
        elif a.cmd == "dm":
            if a.dcmd == "create":
                _print(admin.dm_create(s, a.pkgdef, a.readme))
            elif a.dcmd == "download":
                print(admin.dm_download(s, a.pkgdef, a.id, a.out))
            elif a.dcmd == "upload":
                _print(admin.dm_upload(s, a.zip))
            else:
                _print(admin.dm_deploy(s, complete=a.complete))
        elif a.cmd == "ibm-mcp":
            c = ibm_mcp.IbmMcpClient.from_session(s)
            if a.action == "info":
                _print(c.initialize())
            elif a.action == "tools":
                for t in c.list_tools():
                    ro = "read " if ibm_mcp.is_read_only(t) else "WRITE"
                    print(f"  [{ro}] {t['name']:<40}{(t.get('description') or '').splitlines()[0][:90] if t.get('description') else ''}")
            else:
                if not a.name:
                    raise ValueError("ibm-mcp call needs a tool NAME")
                tool = next((t for t in c.list_tools() if t["name"] == a.name), None)
                if tool is None:
                    raise ValueError(f"IBM MCP server has no tool {a.name!r}")
                if not ibm_mcp.is_read_only(tool):
                    if not a.apply:
                        raise PermissionError(f"{a.name} may write; re-run with --apply")
                    s.guard_write()
                _print(c.call_tool(a.name, json.loads(a.args)))
        elif a.cmd == "bootstrap" and a.action == "authapps":
            for r in bootstrap_gen.authapps(s, apply=a.apply):
                print(f"  {r['action']:<15}{r['os']:<16}{r.get('authapp', '')}  {r.get('probe', '')}")
        elif a.cmd == "bootstrap" and a.action == "generate":
            defs = bootstrap_gen.build(s.client, a.only)
            for f in bootstrap_gen.write(defs):
                print(f"  wrote {f}")
            for d in defs:
                if "_error" in d:
                    print(f"  [SKIP] {d['intobjectname']}: {d['_error']}")
        elif a.cmd == "bootstrap":
            items = engine.resolve_files(None, None, ["src/00_predeployment"])
            r = engine.deploy(s, items, apply=a.apply)
            for row in r["results"]:
                print(f"  {row['action']:<15}{row['file']}  {row.get('error', '')}")
            print(r["summary"])
            return 1 if r["summary"].get("FAILED") else 0
        return 0
    except (KeyError, ValueError, FileNotFoundError, PermissionError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
