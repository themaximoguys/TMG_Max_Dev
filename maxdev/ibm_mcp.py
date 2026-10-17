"""Client for the IBM Maximo MCP server shipped with MAS 9.2 (early / partial feature set).

IBM docs (developing > Maximo MCP server overview): runs as the <instance>-mcp
deployment, JSON-RPC 2.0 over HTTP POST, responses may be SSE, auth by apikey
header or JWT, tool list is driven from Manage (AI config tools in MAXAICFGTOOL,
object structures, automation scripts, workflows, API routes).

The route URL is tenant-specific, so it is configured, not guessed:
    MAXIMO_MCP_URL=https://<instance>-mcp.<domain>/mcp     (in environments/.env.<name>)
    MAXIMO_MCP_AUTH=apikey | bearer                         (default apikey, reuses MAXIMO_API_KEY)
    MAXIMO_MCP_TOKEN=<jwt>                                  (only for bearer)

    maxdev ibm-mcp tools                 list the tools Manage exposes
    maxdev ibm-mcp call NAME --args '{}' call one (read tools only unless --apply)

Everything here is status=verify: IBM's server is new and the exact path,
session handling and tool names must be confirmed on your 9.2 tenant.
"""
from __future__ import annotations

import itertools
import json

import requests

PROTOCOL = "2025-03-26"


class IbmMcpError(RuntimeError):
    pass


class IbmMcpClient:
    def __init__(self, url: str, api_key: str = "", token: str = "", auth: str = "apikey",
                 verify_tls: bool = True, timeout: int = 600):
        if not url:
            raise ValueError("MAXIMO_MCP_URL is not set for this environment")
        self.url = url
        self.timeout = timeout
        self.s = requests.Session()
        self.s.verify = verify_tls
        self.s.headers.update({"Content-Type": "application/json",
                               "Accept": "application/json, text/event-stream"})
        if auth == "bearer":
            if not token:
                raise ValueError("MAXIMO_MCP_AUTH=bearer needs MAXIMO_MCP_TOKEN")
            self.s.headers["Authorization"] = f"Bearer {token}"
        else:
            if not api_key:
                raise ValueError("MAXIMO_API_KEY is required for apikey auth")
            self.s.headers["apikey"] = api_key
        self._ids = itertools.count(1)
        self.server_info: dict = {}
        self._initialized = False

    @classmethod
    def from_session(cls, s) -> "IbmMcpClient":
        v = s.vals
        return cls(v.get("MAXIMO_MCP_URL", ""), api_key=s.target.api_key, token=v.get("MAXIMO_MCP_TOKEN", ""),
                   auth=v.get("MAXIMO_MCP_AUTH", "apikey").lower(), verify_tls=s.target.verify_tls)

    # ── transport ──────────────────────────────────────────────────────────
    @staticmethod
    def _parse(resp: requests.Response, want_id):
        ctype = resp.headers.get("Content-Type", "")
        if "text/event-stream" in ctype:
            msgs = []
            for line in resp.text.splitlines():
                if line.startswith("data:"):
                    payload = line[5:].strip()
                    if payload:
                        try:
                            msgs.append(json.loads(payload))
                        except ValueError:
                            pass
            for m in msgs:
                if m.get("id") == want_id:
                    return m
            if msgs:
                return msgs[-1]
            raise IbmMcpError(f"empty SSE response: {resp.text[:300]}")
        if not resp.content:
            return {}
        return resp.json()

    def _rpc(self, method: str, params: dict | None = None, notify: bool = False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        mid = None
        if not notify:
            mid = next(self._ids)
            msg["id"] = mid
        r = self.s.post(self.url, data=json.dumps(msg), timeout=self.timeout)
        if r.status_code >= 400:
            raise IbmMcpError(f"HTTP {r.status_code} from {self.url}: {r.text[:500]}")
        sid = r.headers.get("Mcp-Session-Id")
        if sid:
            self.s.headers["Mcp-Session-Id"] = sid
        if notify:
            return None
        out = self._parse(r, mid)
        if "error" in out:
            raise IbmMcpError(f"{method}: {out['error']}")
        return out.get("result", out)

    def initialize(self) -> dict:
        if not self._initialized:
            self.server_info = self._rpc("initialize", {
                "protocolVersion": PROTOCOL, "capabilities": {},
                "clientInfo": {"name": "tmg-maxdev", "version": "0.1.0"}})
            try:
                self._rpc("notifications/initialized", notify=True)
            except IbmMcpError:
                pass   # some servers do not accept the notification; not fatal
            self._initialized = True
        return self.server_info

    # ── MCP operations ─────────────────────────────────────────────────────
    def list_tools(self) -> list[dict]:
        self.initialize()
        tools, cursor = [], None
        while True:
            res = self._rpc("tools/list", {"cursor": cursor} if cursor else {})
            tools += res.get("tools", [])
            cursor = res.get("nextCursor")
            if not cursor:
                return tools

    def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        self.initialize()
        return self._rpc("tools/call", {"name": name, "arguments": arguments or {}})


def is_read_only(tool: dict) -> bool:
    """Honour MCP tool annotations; fall back to name heuristics."""
    ann = tool.get("annotations") or {}
    if "readOnlyHint" in ann:
        return bool(ann["readOnlyHint"])
    n = tool.get("name", "").lower()
    return n.startswith(("get", "list", "query", "search", "read", "describe", "find"))
