"""In-memory stand-in for the Manage JSON API, enough to exercise the engine end to end.

Implements: GET /api/os/<os> (oslc.where with =, "X%", in [..], and),
POST create, POST {href} with x-method-override PATCH(MERGE)/DELETE, BULK,
GET {href}, /api/whoami, /api/script/<name>.
"""
from __future__ import annotations

import json
import re
from urllib.parse import urlparse


class Resp:
    def __init__(self, status=200, body=None, url="", headers=None):
        self.status_code = status
        self.url = url
        self.headers = headers or {"Content-Type": "application/json"}
        self.text = body if isinstance(body, str) else (json.dumps(body) if body is not None else "")
        self.content = self.text.encode()

    def json(self):
        return json.loads(self.text)


def _match(rec, where):
    if not where:
        return True
    for clause in re.split(r"\s+and\s+", where):
        m = re.match(r'(\w+)\s+in\s+\[(.*)\]$', clause.strip())
        if m:
            vals = [v.strip().strip('"') for v in m.group(2).split(",")]
            if str(rec.get(m.group(1))) not in vals:
                return False
            continue
        m = re.match(r'(\w+)\s*(!=|=)\s*"?(.*?)"?$', clause.strip())
        if not m:
            raise AssertionError(f"fake cannot parse where {clause!r}")
        k, op, v = m.groups()
        cur = str(rec.get(k, ""))
        hit = (cur.startswith(v[:-1]) if v.endswith("%") else cur == v)
        if (op == "=") != hit:
            return False
    return True


class FakeMaximo:
    base = "https://fake/maximo"

    def __init__(self, structures=("MXAPIDOMAIN",)):
        self.db: dict[str, list[dict]] = {s.lower(): [] for s in structures}
        self.headers = {}
        self.verify = True
        self.calls = []
        self.scripts = {}
        self.fail_create = set()          # os names whose create should fail
        self.drop_writes = set()          # os names that 204 and discard (presentation bug)
        self._n = 0

    def seed(self, os_name, *recs):
        for r in recs:
            self._n += 1
            r = dict(r)
            r["href"] = f"{self.base}/api/os/{os_name.lower()}/_{self._n}"
            self.db[os_name.lower()].append(r)

    def _find_href(self, href):
        for os_name, rows in self.db.items():
            for r in rows:
                if r["href"] == href.split("?")[0]:
                    return os_name, r
        return None, None

    def request(self, method, url, params=None, data=None, headers=None, timeout=None):
        headers = {**self.headers, **(headers or {})}
        params = params or {}
        self.calls.append((method, url, headers.get("x-method-override"), params))
        path = urlparse(url).path.replace("/maximo/", "")
        body = json.loads(data) if data else None
        if path == "api/whoami":
            return Resp(200, {"userName": "TMGDEV"}, url)
        if path.startswith("api/script/"):
            name = path.split("/")[-1]
            if name not in self.scripts:
                return Resp(404, {"Error": {"message": "BMXAA script not found"}}, url)
            return Resp(200, self.scripts[name](params, body), url, {"Content-Type": "text/plain"})
        override = headers.get("x-method-override")
        os_name, rec = self._find_href(url)
        if rec is not None:
            if override == "DELETE":
                self.db[os_name].remove(rec)
                return Resp(204, None, url)
            if override == "PATCH":
                if os_name in self.drop_writes:
                    return Resp(204, None, url)
                for k, v in body.items():
                    if isinstance(v, list) and isinstance(rec.get(k), list) and headers.get("patchtype") == "MERGE":
                        rec[k] = rec[k] + [x for x in v if x not in rec[k]]
                    else:
                        rec[k] = v
                return Resp(204, None, url)
            return Resp(200, rec, url)
        m = re.match(r"api/os/(\w+)(?:/(_[\w-]+))?$", path)
        if not m:
            return Resp(404, {"Error": {"message": f"no route {path}"}}, url)
        os_name = m.group(1)
        if m.group(2):          # resource-id URL for a record (e.g. presentation by app)
            import base64
            key = base64.b64decode(m.group(2)[1:].replace("-", "=")).decode()
            rows = [r for r in self.db.get(os_name, []) if r.get("app") == key]
            if not rows:
                return Resp(404, {"Error": {"message": "not found"}}, url)
            return self.request(method, rows[0]["href"], params, data, headers)
        if os_name not in self.db:
            return Resp(404, {"Error": {"reasonCode": "BMXAA9301E", "message": "object structure not found"}}, url)
        if method == "GET":
            rows = [dict(r) for r in self.db[os_name] if _match(r, params.get("oslc.where", ""))]
            sel = params.get("oslc.select", "*")
            if sel and sel != "*" and "{" not in sel:
                keep = set(sel.split(",")) | {"href"}
                rows = [{k: v for k, v in r.items() if k in keep} for r in rows]
            return Resp(200, {"member": rows, "responseInfo": {}}, url)
        if override == "BULK":
            out = []
            for item in body:
                act = item.pop("_action")
                if act == "Update":
                    self.request("POST", item.pop("href"), data=json.dumps(item),
                                 headers={"x-method-override": "PATCH", "patchtype": "MERGE"})
                else:
                    self.seed(os_name, item)
                out.append({"_responsemeta": {"status": "201" if act == "Add" else "204"}})
            return Resp(200, out, url)
        if method == "POST":
            if os_name in self.fail_create:
                return Resp(400, {"Error": {"reasonCode": "BMXAA0024E", "message": "create refused"}}, url)
            self.seed(os_name, body)
            return Resp(201, None, url)
        return Resp(405, {"Error": {"message": "method"}}, url)
