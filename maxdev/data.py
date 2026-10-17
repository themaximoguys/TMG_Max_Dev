"""Seed / reference data: export any object structure to JSON, load JSON/CSV back.

Load uses the documented BULK call: POST /api/os/<os> with x-method-override: BULK
and a JSON array. Each item is committed on its own and the HTTP status is always
200, so the per-item _responsemeta.status is what decides success. allornothing=1
makes the whole batch atomic.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from .client import chunked, strip_meta


def read_rows(path: Path) -> list[dict]:
    if path.suffix.lower() == ".csv":
        with open(path, newline="", encoding="utf-8-sig") as fh:
            return [{k: v for k, v in r.items() if v != ""} for r in csv.DictReader(fh)]
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else data.get("member", [data])


def export(s, os_name: str, where: str, select: str, out: Path, limit: int | None = None) -> dict:
    rows = [strip_meta(r) for r in s.client.query(os_name, where=where, select=select, max_records=limit)]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"os": os_name, "records": len(rows), "file": str(out)}


def load(s, os_name: str, path: Path, key: list[str], apply: bool = False, batch: int = 100,
         all_or_nothing: bool = False) -> dict:
    rows = read_rows(path)
    if not apply:
        return {"os": os_name, "mode": "DRY-RUN", "rows": len(rows), "sample": rows[:3]}
    s.guard_write()
    ok, failed, errors = 0, 0, []
    for chunk in chunked(rows, batch):
        items = []
        for r in chunk:
            hits = s.client.find(os_name, {k: r[k] for k in key}) if key else []
            item = dict(r)
            if hits:
                item.update({"_action": "Update", "href": hits[0]["href"]})
            else:
                item["_action"] = "Add"
            items.append(item)
        hdr = {"x-method-override": "BULK", "patchtype": "MERGE"}
        if all_or_nothing:
            hdr["allornothing"] = "1"
        resp = s.client.request("POST", f"api/os/{os_name.lower()}", params={"lean": 1}, body=items, headers=hdr)
        for src, res in zip(chunk, resp if isinstance(resp, list) else []):
            status = int((res.get("_responsemeta") or {}).get("status", 0) or 0)
            if 200 <= status < 300:
                ok += 1
            else:
                failed += 1
                errors.append({"row": {k: src.get(k) for k in key}, "status": status,
                               "error": (res.get("_responsedata") or {}).get("Error", {}).get("message")})
    return {"os": os_name, "mode": "APPLY", "rows": len(rows), "ok": ok, "failed": failed, "errors": errors[:50]}
