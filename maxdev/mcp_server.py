"""MCP server: the same engine as the CLI, exposed to any MCP client.

Run:   python -m maxdev.mcp_server          (stdio)
Client setup and registrations are described in docs/AGENT_SETUP.md.

Safety model for tools exposed by this server:
  * every write tool takes apply=False by default and returns a dry-run plan
  * environments with MAXIMO_PROTECTED=true refuse writes inside the engine
  * deploy resolves artifacts from registered source folders — the agent edits
    files, a human reviews the diff, then deploy applies them
"""
from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from . import admin, builder, dashboard, data, engine, ibm_mcp, license, manifest, registry, scaffold, store
from .env import REPO, list_envs

mcp = FastMCP("tmg-maximo-dev")
_sessions: dict[str, engine.Session] = {}


def _s(env: str | None) -> engine.Session:
    key = env or "default"
    if key not in _sessions:
        _sessions[key] = engine.Session(env)
    return _sessions[key]


def _ok(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


@mcp.tool()
def list_environments() -> str:
    """Environments configured in environments/.env.<name>."""
    return _ok(list_envs())


@mcp.tool()
def license_status() -> str:
    """maxdev licence: licensee, expiry, licensed Maximo hosts. Maximo tools need a valid licence."""
    return _ok(license.status())


@mcp.tool()
def ping(env: str | None = None) -> str:
    """Check connectivity and identity (GET /api/whoami)."""
    s = _s(env)
    who = s.client.whoami()
    return _ok({"env": s.env, "base_url": s.target.base_url, "protected": s.protected,
                "user": who.get("userName") or who.get("personid")})


@mcp.tool()
def doctor(env: str | None = None) -> str:
    """For every artifact type, report which object structure exists on the tenant."""
    return _ok(engine.doctor(_s(env)))


@mcp.tool()
def list_artifact_types() -> str:
    """Every Maximo development area this repo manages: layer, handler, object structure, folder, gotchas."""
    return _ok([{"id": t.id, "label": t.label, "layer": t.layer, "handler": t.handler, "os": t.os,
                 "key": t.key, "folder": f"src/{t.folder}", "status": t.status, "note": t.note}
                for t in registry.ordered()])


@mcp.tool()
def list_local(type_id: str | None = None) -> str:
    """Artifacts currently in the repo (optionally one type)."""
    ts = [registry.get(type_id)] if type_id else registry.ordered()
    return _ok({t.id: [str(f.relative_to(REPO)) for f in store.local_files(t)] for t in ts if store.local_files(t)})


@mcp.tool()
def extract(type_id: str, names: list[str] | None = None, like: str | None = None,
            where: str | None = None, limit: int | None = None, env: str | None = None) -> str:
    """Pull artifacts from Maximo into src/ (one file per record). Give names, a prefix (like='TMG')
    or an oslc.where clause — whole-type extracts of OOTB data are refused."""
    return _ok(engine.extract(_s(env), type_id, names, like, where, limit))


@mcp.tool()
def diff(type_id: str | None = None, names: list[str] | None = None, paths: list[str] | None = None,
         env: str | None = None) -> str:
    """Compare repo files with the live environment (unified diff per record)."""
    return _ok(engine.diff(_s(env), engine.resolve_files(type_id, names, paths)))


@mcp.tool()
def deploy(type_id: str | None = None, names: list[str] | None = None, paths: list[str] | None = None,
           manifest_name: str | None = None, apply: bool = False, force_replace: bool = False,
           env: str | None = None) -> str:
    """Deploy repo artifacts in dependency order. DRY RUN unless apply=True.
    App Designer XML is merged additively onto the live screen unless force_replace=True."""
    items = manifest.items(manifest.load(manifest_name)) if manifest_name else engine.resolve_files(type_id, names, paths)
    return _ok(engine.deploy(_s(env), items, apply=apply, force_replace=force_replace))


@mcp.tool()
def query(object_structure: str, where: str = "", select: str = "*", limit: int = 20, env: str | None = None) -> str:
    """Read records from any object structure (oslc.where / oslc.select syntax)."""
    return _ok(_s(env).client.query(object_structure, where=where, select=select, max_records=limit))


@mcp.tool()
def schema(object_structure: str, env: str | None = None) -> str:
    """JSON schema of an object structure (GET /api/jsonschema/<os>) — use before writing a new artifact file."""
    return _ok(_s(env).client.request("GET", f"api/jsonschema/{object_structure.lower()}", params={"oslc.select": "*"}))


@mcp.tool()
def call_script(name: str, params: dict | None = None, body: dict | None = None, method: str = "POST",
                apply: bool = False, env: str | None = None) -> str:
    """Invoke an automation-script REST handler (/api/script/<name>). Scripts can write, so apply=True is required."""
    s = _s(env)
    if not apply:
        return _ok({"mode": "DRY-RUN", "would_call": f"{method} api/script/{name}", "params": params, "body": body})
    s.guard_write()
    return _ok(s.client.call_script(name, params=params, body=body, method=method))


@mcp.tool()
def dbconfig_status(env: str | None = None) -> str:
    """Database Configuration objects with unapplied changes (MAXOBJECTCFG.CHANGED != N)."""
    return _ok(admin.dbconfig_pending(_s(env)))


@mcp.tool()
def dbconfig_apply(admin_mode: bool = False, apply: bool = False, env: str | None = None) -> str:
    """Apply pending Database Configuration changes through the configured apply script.
    admin_mode=True wraps it in Admin Mode on/off (structural changes). DRY RUN unless apply=True."""
    s = _s(env)
    if not apply:
        return _ok({"mode": "DRY-RUN", **admin.dbconfig_pending(s), "admin_mode": admin_mode})
    return _ok(admin.dbconfig_apply(s, admin=admin_mode))


@mcp.tool()
def new_autoscript(name: str, launch_point: str = "library", object_name: str | None = None,
                   attribute: str | None = None, javascript: bool = False) -> str:
    """Create a new automation-script file in repo format (source + scriptConfig). Does not deploy."""
    path = scaffold.autoscript(name, launch_point, object_name, attribute, js=javascript)
    return _ok({"created": str(path.relative_to(REPO)), "content": path.read_text(encoding="utf-8")})


@mcp.tool()
def list_script_templates() -> str:
    """TMG automation-script templates (kind, logging style, name pattern). Read the standards in
    docs/standards/TMG_AUTOSCRIPT_STANDARDS.md before filling one."""
    return _ok(builder.list_templates())


@mcp.tool()
def build_script(kind: str, object_name: str = "", attribute: str = "", name: str = "", channel: str = "",
                 service_name: str = "", exit_type: str = "USEREXIT", logging: str = "mxlogger",
                 description: str = "", java_class: str = "") -> str:
    """Create a script in src/09-automation-scripts/ from a TMG template. Mechanical placeholders are
    filled; business placeholders ({PURPOSE_DESCRIPTION}, {BUSINESS_RULE_1}...) remain for you to write.
    Returns the file content and lint result. Does not deploy."""
    path, issues = builder.build(kind, object_name=object_name, field=attribute, name=name, channel=channel,
                                 service_name=service_name, exit_type=exit_type, logging=logging,
                                 description=description, java_class=java_class)
    return _ok({"file": str(path.relative_to(REPO)), "lint": issues, "content": path.read_text(encoding="utf-8")})


@mcp.tool()
def lint_script(path: str) -> str:
    """Check a script against the TMG hard rules (Jython 2.7, SqlFormat, MboSet close, one logging style,
    Java 17 APIs, unfilled placeholders). Deploy refuses scripts with errors."""
    p = (REPO / path)
    return _ok(builder.lint_text(p.read_text(encoding="utf-8"), p.name))


@mcp.tool()
def analyze_java(path: str) -> str:
    """Classify a Maximo Java customisation (MBO, field class, cron, action, exit, bean) and map its
    methods to the TMG script template to convert it into. Then use the convert-java-to-script skill."""
    return _ok(builder.analyze_java(Path(path) if Path(path).is_absolute() else REPO / path))


@mcp.tool()
def write_artifact(type_id: str, record: dict) -> str:
    """Write/overwrite one JSON artifact file in src/ from a record (normalised naming + formatting). Does not deploy."""
    t = registry.get(type_id)
    if t.handler not in ("json", "replace"):
        raise ValueError(f"{type_id} uses handler {t.handler}; edit the file directly or use new_autoscript")
    store.key_of(t, record)
    path, changed = store.save_json(t, record)
    return _ok({"file": str(path.relative_to(REPO)), "changed": changed})


@mcp.tool()
def build_dashboard(spec: str, write_manifest: bool = True) -> str:
    """Build an operational dashboard from a YAML spec (catalog/dashboards/<name>.yaml or a path): writes the
    saved queries, KPIs, work queues and start center template into src/ plus manifests/<NAME>.yaml.
    Offline; deploy it with deploy(manifest_name=NAME) as a dry run first."""
    return _ok(dashboard.build(spec, write_manifest=write_manifest))


@mcp.tool()
def data_load(object_structure: str, file: str, key: list[str], apply: bool = False, env: str | None = None) -> str:
    """Bulk add/update records from a JSON or CSV file (x-method-override: BULK). DRY RUN unless apply=True."""
    return _ok(data.load(_s(env), object_structure, (REPO / file), key, apply=apply))


@mcp.tool()
def data_export(object_structure: str, where: str, out_file: str, select: str = "*", limit: int | None = None,
                env: str | None = None) -> str:
    """Export records to a JSON file under the repo (e.g. src/91-data/...)."""
    return _ok(data.export(_s(env), object_structure, where, select, REPO / out_file, limit))


@mcp.tool()
def ibm_mcp_tools(env: str | None = None) -> str:
    """List tools exposed by IBM's MAS 9.2 Maximo MCP server (needs MAXIMO_MCP_URL in the env file)."""
    c = ibm_mcp.IbmMcpClient.from_session(_s(env))
    return _ok({"server": c.initialize(),
                "tools": [{"name": t["name"], "read_only": ibm_mcp.is_read_only(t),
                           "description": t.get("description"), "inputSchema": t.get("inputSchema")}
                          for t in c.list_tools()]})


@mcp.tool()
def ibm_mcp_call(name: str, arguments: dict | None = None, apply: bool = False, env: str | None = None) -> str:
    """Call one tool on IBM's MAS 9.2 MCP server. Tools not annotated read-only need apply=True
    and are refused on protected environments."""
    s = _s(env)
    c = ibm_mcp.IbmMcpClient.from_session(s)
    tool = next((t for t in c.list_tools() if t["name"] == name), None)
    if tool is None:
        raise ValueError(f"IBM MCP server has no tool {name!r}")
    if not ibm_mcp.is_read_only(tool):
        if not apply:
            return _ok({"mode": "DRY-RUN", "tool": name, "arguments": arguments,
                        "reason": "tool is not annotated read-only; pass apply=True"})
        s.guard_write()
    return _ok(c.call_tool(name, arguments))


def main():
    mcp.run()


if __name__ == "__main__":
    main()
