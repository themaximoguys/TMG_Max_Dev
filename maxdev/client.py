"""HTTP client for the Maximo Manage JSON API (/maximo/api/...).

Every network call in this repo goes through MaximoClient, so the CLI and the
MCP server behave identically. Patterns here were proven against MAS 9 tenants
in the reference delivery repo:

  find     GET  /api/os/{OS}?lean=1&oslc.where=k="v"&oslc.select=k,href
  update   POST {href}?lean=1  + x-method-override: PATCH, patchtype: MERGE
  create   POST /api/os/{OS}?lean=1
  delete   POST {href}?lean=1  + x-method-override: DELETE
  script   POST /api/script/{NAME}   (automation-script REST handlers)
"""
from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from typing import Any, Iterable
from urllib.parse import quote

import requests

# Keys the API adds to every record; never stored in Git, never sent back.
META_KEYS = {"href", "localref", "_rowstamp", "_imagelibref", "rdf:about", "prefixes"}


class MaximoError(RuntimeError):
    def __init__(self, status: int, message: str, url: str = ""):
        super().__init__(f"HTTP {status} {url}: {message}")
        self.status = status
        self.message = message
        self.url = url


def strip_meta(node: Any) -> Any:
    """Remove API bookkeeping so a record diffs cleanly against Git."""
    if isinstance(node, list):
        return [strip_meta(x) for x in node]
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k in META_KEYS or k.startswith("_") or k.endswith("_collectionref") or k.endswith("_localref"):
                continue
            out[k] = strip_meta(v)
        return out
    return node


def where_clause(key: dict[str, Any]) -> str:
    parts = []
    for k, v in key.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            parts.append(f"{k}={v}")
        else:
            parts.append('%s="%s"' % (k, str(v).replace('"', '\\"')))
    return " and ".join(parts)


def resource_id(value: str) -> str:
    """Maximo resource ids are '_' + base64(key) with '=' padding written as '-'.
    Sending raw '==' resolves to a context that answers 204 and drops the write."""
    return "_" + base64.b64encode(value.encode()).decode().replace("=", "-")


@dataclass
class Target:
    name: str
    base_url: str               # e.g. https://host/maximo
    api_key: str = ""
    maxauth: str = ""           # base64(user:password), legacy/non-MAS only
    verify_tls: bool = True
    timeout: int = 180


class MaximoClient:
    def __init__(self, target: Target, session: requests.Session | None = None):
        if not target.base_url:
            raise ValueError(f"environment {target.name!r} has no MAXIMO_BASE_URL")
        if not (target.api_key or target.maxauth):
            raise ValueError(f"environment {target.name!r} has no MAXIMO_API_KEY (or MAXIMO_MAXAUTH)")
        self.t = target
        self.base = target.base_url.rstrip("/")
        self.s = session or requests.Session()
        self.s.headers.update({"Accept": "application/json", "Content-Type": "application/json; charset=utf-8"})
        if target.api_key:
            self.s.headers["apikey"] = target.api_key
        else:
            self.s.headers["maxauth"] = target.maxauth
        self.s.verify = target.verify_tls

    # ── low level ──────────────────────────────────────────────────────────
    def _url(self, path: str) -> str:
        return path if path.startswith("http") else f"{self.base}/{path.lstrip('/')}"

    def request(self, method: str, path: str, *, params: dict | None = None, body: Any = None,
                headers: dict | None = None, raw: bool = False, retries: int = 2):
        url = self._url(path)
        data = None
        if body is not None:
            data = body if isinstance(body, (bytes, str)) else json.dumps(body, ensure_ascii=False)
            if isinstance(data, str):
                data = data.encode("utf-8")      # never let the transport pick latin-1
        for attempt in range(retries + 1):
            r = self.s.request(method, url, params=params, data=data, headers=headers or {}, timeout=self.t.timeout)
            if r.status_code in (502, 503, 504) and attempt < retries:
                time.sleep(2 * (attempt + 1))
                continue
            break
        if r.status_code >= 400:
            msg = r.text[:800]
            try:
                err = r.json().get("Error", {})
                msg = f"{err.get('reasonCode', '')} {err.get('message', msg)}".strip()
            except Exception:
                pass
            raise MaximoError(r.status_code, msg, r.url)
        if raw:
            return r
        if not r.content:
            return {}
        try:
            return r.json()
        except ValueError:
            return r.text

    # ── identity / discovery ───────────────────────────────────────────────
    def whoami(self) -> dict:
        return self.request("GET", "api/whoami")

    def os_probe(self, os_name: str) -> str:
        """ok | unauthorized (BMXAA9301E) | missing (BMXAA4216E) | unusable (e.g. BMXAA1283E MIGRATIONMGR-only)"""
        try:
            self.request("GET", f"api/os/{os_name.lower()}", params={"lean": 1, "oslc.pageSize": 1, "oslc.select": "*"})
            return "ok"
        except MaximoError as e:
            if "BMXAA9301E" in e.message:
                return "unauthorized"
            if e.status == 404 and "BMXAA4216E" in e.message:
                return "missing"
            if e.status in (400, 404):
                return "unusable"
            raise

    def os_exists(self, os_name: str) -> bool:
        try:
            self.request("GET", f"api/os/{os_name.lower()}", params={"lean": 1, "oslc.pageSize": 1, "oslc.select": "*"})
            return True
        except MaximoError as e:
            if e.status in (400, 404):
                return False
            raise

    # ── read ───────────────────────────────────────────────────────────────
    def query(self, os_name: str, where: str = "", select: str = "*", page_size: int = 100,
              max_records: int | None = None, order_by: str = "") -> list[dict]:
        params = {"lean": 1, "oslc.pageSize": page_size, "oslc.select": select or "*"}
        if where:
            params["oslc.where"] = where
        if order_by:
            params["oslc.orderBy"] = order_by
        url, out = f"api/os/{os_name.lower()}", []
        while url:
            page = self.request("GET", url, params=params)
            params = None                       # nextPage already carries the query
            out.extend(page.get("member", []))
            if max_records and len(out) >= max_records:
                return out[:max_records]
            url = (page.get("responseInfo") or {}).get("nextPage", {}).get("href")
        return out

    def find(self, os_name: str, key: dict[str, Any], select: str = "") -> list[dict]:
        sel = select or ",".join(list(key) + ["href"])
        return self.query(os_name, where=where_clause(key), select=sel, page_size=50)

    def get_deep(self, href: str, depth: int = 0) -> dict:
        """lean GETs return children as *_collectionref links. Follow them so a
        captured record is complete (a CTRLGROUP without its conditions is empty)."""
        rec = self.request("GET", href, params={"lean": 1})
        if depth >= 3:
            return rec
        for k in [k for k in rec if k.endswith("_collectionref")]:
            child = k[: -len("_collectionref")]
            coll = self.request("GET", rec[k], params={"lean": 1})
            items = [self.get_deep(m["localref"], depth + 1) if m.get("localref") else m for m in coll.get("member", [])]
            if items:
                rec[child] = items
        return rec

    # ── write ──────────────────────────────────────────────────────────────
    def create(self, os_name: str, record: dict) -> dict:
        return self.request("POST", f"api/os/{os_name.lower()}", params={"lean": 1}, body=record,
                            headers={"properties": "*"})

    def merge(self, href: str, record: dict) -> dict:
        return self.request("POST", href, params={"lean": 1}, body=record,
                            headers={"x-method-override": "PATCH", "patchtype": "MERGE"})

    def delete(self, href: str) -> None:
        self.request("POST", href, params={"lean": 1}, headers={"x-method-override": "DELETE"})

    def upsert(self, os_name: str, key: dict[str, Any], record: dict) -> str:
        """Returns 'created' or 'updated'. Refuses to guess when the key is ambiguous."""
        hits = self.find(os_name, key)
        if len(hits) > 1:
            raise MaximoError(409, f"key {key} matched {len(hits)} records; refusing to guess", os_name)
        if hits:
            self.merge(hits[0]["href"], record)
            return "updated"
        self.create(os_name, record)
        return "created"

    def replace(self, os_name: str, key: dict[str, Any], record: dict) -> str:
        """Delete-then-create for types MERGE cannot update faithfully (attribute
        formulas, conditional-UI trees). Captures the old rows first and restores
        them if the create fails. Every outcome is confirmed by a read-back."""
        hits = self.find(os_name, key)
        captured = [strip_meta(self.get_deep(h["href"])) for h in hits]
        for h in hits:
            self.delete(h["href"])
        try:
            self.create(os_name, record)
            if not self.find(os_name, key):
                raise MaximoError(500, "create returned OK but the record is not there", os_name)
            return "replaced" if hits else "created"
        except Exception:
            for c in captured:
                try:
                    self.create(os_name, c)
                except Exception:
                    pass
            if captured and not self.find(os_name, key):
                raise MaximoError(500, f"REPLACE FAILED AND ROLLBACK FAILED for {key}; old rows: "
                                  + json.dumps(captured)[:2000], os_name)
            raise

    # ── automation-script handlers / actions ───────────────────────────────
    def call_script(self, name: str, params: dict | None = None, body: Any = None, method: str = "POST"):
        return self.request(method, f"api/script/{name}", params=params, body=body if body is not None else {})

    def wsmethod(self, href: str, method: str, body: dict | None = None):
        return self.request("POST", href, params={"action": f"wsmethod:{method}", "lean": 1}, body=body or {},
                            headers={"x-method-override": "PATCH"})

    def presentation_href(self, app: str) -> str:
        return f"{self.base}/api/os/mxapipresentation/{resource_id(app.upper())}"


def chunked(it: Iterable, n: int):
    buf = []
    for x in it:
        buf.append(x)
        if len(buf) == n:
            yield buf
            buf = []
    if buf:
        yield buf


__all__ = ["MaximoClient", "MaximoError", "Target", "strip_meta", "where_clause", "resource_id", "quote"]
