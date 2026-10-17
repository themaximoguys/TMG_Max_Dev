"""Change manifests: the list of artifacts that make up one feature / ticket.

manifests/<NAME>.yaml
    name: WO-CUSTOMER-EMAIL
    description: Cross over customer email from SR to WO
    items:
      - domain: TMGPRIORITY            # type id: name (as in `maxdev ls`)
      - object: WORKORDER
      - autoscript: [WORKORDER.SAVE, SR.CUSTEMAIL.VALIDATE]
      - path: src/07-app-designer/WOTRACK.XML
    manual:                            # steps no API can do — printed, never skipped silently
      - Apply Configuration Changes for WORKORDER
"""
from __future__ import annotations

from pathlib import Path

import yaml

from . import engine
from .env import REPO


def load(name_or_path: str) -> dict:
    p = Path(name_or_path)
    if not p.exists():
        p = REPO / "manifests" / (name_or_path if name_or_path.endswith((".yaml", ".yml")) else name_or_path + ".yaml")
    m = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    m["_path"] = str(p)
    return m


def items(m: dict) -> list[tuple]:
    out = []
    for entry in m.get("items") or []:
        for k, v in entry.items():
            vals = v if isinstance(v, list) else [v]
            if k == "path":
                out += engine.resolve_files(None, None, [str(x) for x in vals])
            else:
                out += engine.resolve_files(k, [str(x) for x in vals], None)
    return _dedupe(out)


def _dedupe(items_):
    seen, out = set(), []
    for t, f in items_:
        if f not in seen:
            seen.add(f)
            out.append((t, f))
    order = {t.id: i for i, t in enumerate(engine.registry.ordered())}
    return sorted(out, key=lambda x: (x[0].layer, order[x[0].id], str(x[1])))
