"""On-disk format for every artifact type.

json types    src/<folder>/<NAME>.json   sorted keys, 2-space indent, LF, API meta stripped
autoscript    src/09-automation-scripts/<lp-type>/<NAME>.py|.js
              real source + a trailing scriptConfig block holding everything else
appxml        src/07-app-designer/<APP>.xml   raw presentation XML

Stable serialisation matters: extract -> deploy -> re-extract must be byte-identical
so `maxdev diff` only ever shows real change.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import scriptconfig as sc
from .client import strip_meta
from .registry import ArtifactType

SAFE = re.compile(r'[\\/:*?"<>|\s]+')
CFG_MARK = "# ── maxdev scriptConfig (managed: edit values, keep the block last) ──"
JS_MARK = "// ── maxdev scriptConfig (managed: edit values, keep the block last) ──"
PY_CFG = re.compile(r'\n?' + re.escape(CFG_MARK) + r'\s*\nscriptConfig\s*=\s*"""(.*?)"""\s*$', re.S)
JS_CFG = re.compile(r'\n?' + re.escape(JS_MARK) + r'\s*\nvar\s+scriptConfig\s*=\s*(\{.*\});?\s*$', re.S)
# Also accept a plain sharptree-style block so hand-written scripts deploy too.
LOOSE_PY = re.compile(r'\nscriptConfig\s*=\s*"""(.*?)"""\s*$', re.S)
LOOSE_JS = re.compile(r'\n(?:var|let|const)\s+scriptConfig\s*=\s*(\{.*\});?\s*$', re.S)
# TMG house format: a trailing Jython dict literal (optionally after a comment line).
TMG_DICT = re.compile(r'\n(?:#[^\n]*\n)*scriptConfig\s*=\s*(\{.*\})\s*$', re.S)
TMG_MARK = "# Script Configuration (maxdev reads this block on deploy; keep it last)"

LP_FOLDERS = {"OBJECT": "object", "ATTRIBUTE": "attribute", "ACTION": "action",
              "CUSTOMCONDITION": "condition", "CRONTASK": "crontask"}
INTEGRATION_HINT = re.compile(r"^(PUBLISH|SYNC|INVOKE|OS|ENDPOINT|EXTEXIT|USEREXIT|SMTP)\.", re.I)


def dumps(rec: Any) -> str:
    return json.dumps(rec, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def filename(t: ArtifactType, rec: dict) -> str:
    parts = []
    for f in t.name_fields:
        v = rec.get(f)
        if v in (None, ""):
            raise ValueError(f"{t.id}: record missing name field {f!r}")
        parts.append(SAFE.sub("_", str(v)))
    return "__".join(parts)


def key_of(t: ArtifactType, rec: dict) -> dict:
    missing = [k for k in t.key if rec.get(k) in (None, "")]
    if missing:
        raise ValueError(f"{t.id}: record missing key field(s) {missing}")
    return {k: rec[k] for k in t.key}


def write_text(path: Path, text: str) -> bool:
    """Write with LF endings; returns True if content changed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == text:
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return True


# ── JSON types ─────────────────────────────────────────────────────────────
def save_json(t: ArtifactType, rec: dict) -> tuple[Path, bool]:
    rec = strip_meta(rec)
    path = t.dir / f"{filename(t, rec)}.json"
    return path, write_text(path, dumps(rec))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ── automation scripts ─────────────────────────────────────────────────────
def script_ext(rec: dict) -> str:
    lang = (rec.get("scriptlanguage") or "python").lower()
    return ".js" if lang in ("javascript", "js", "nashorn", "ecmascript") else ".py"


def script_folder(rec: dict) -> str:
    lps = rec.get("scriptlaunchpoint") or []
    if lps:
        return LP_FOLDERS.get((lps[0].get("launchpointtype") or "").upper(), "other")
    if INTEGRATION_HINT.match(rec.get("autoscript", "")):
        return "integration"
    return "library"


def render_script(rec: dict, fmt: str = "tmg") -> str:
    """fmt='tmg': Jython dict with camelCase keys (TMG standard, default).
    fmt='json': JSON-in-string block (lossless for any field, sharptree-like)."""
    meta = rec.get("_tmg_meta") or {}
    rec = strip_meta(dict(rec))
    source = (rec.pop("source", "") or "").replace("\r\n", "\n").rstrip("\n")
    source = strip_script_config(source).rstrip("\n")
    if script_ext(rec) == ".js":
        cfg = json.dumps(rec, indent=2, sort_keys=True, ensure_ascii=False)
        return f"{source}\n\n{JS_MARK}\nvar scriptConfig = {cfg};\n"
    if fmt == "tmg":
        cfg = sc.record_to_tmg(rec)
        cfg.update(meta)
        return f"{source}\n\n{TMG_MARK}\nscriptConfig = {sc.render_dict(cfg)}\n"
    cfg = json.dumps(rec, indent=2, sort_keys=True, ensure_ascii=False)
    return f'{source}\n\n{CFG_MARK}\nscriptConfig = """{cfg}"""\n'


def strip_script_config(text: str) -> str:
    for rx in (PY_CFG, JS_CFG, LOOSE_PY, LOOSE_JS, TMG_DICT):
        text = rx.sub("", text)
    return text


def _tmg_meta(path: Path) -> dict:
    """TMG documentation keys (cronSetup, integrationBinding...) survive re-extract."""
    m = TMG_DICT.search(path.read_text(encoding="utf-8"))
    if not m:
        return {}
    try:
        cfg = sc.parse_dict(m.group(1))
    except ValueError:
        return {}
    return {k: v for k, v in cfg.items() if k in sc.TMG_META}


def script_format(path: Path) -> str:
    if not path.exists():
        return "tmg"
    text = path.read_text(encoding="utf-8")
    return "json" if (PY_CFG.search(text) or LOOSE_PY.search(text)) else "tmg"


def parse_script(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    notes: list[str] = []
    m = None
    for rx in (PY_CFG, JS_CFG, LOOSE_PY, LOOSE_JS):
        m = rx.search(text)
        if m:
            cfg = json.loads(m.group(1))
            break
    if not m:
        m = TMG_DICT.search(text)
        if not m:
            raise ValueError(f"{path.name}: no scriptConfig block — run `maxdev new autoscript` for the template")
        cfg, notes = sc.tmg_to_record(sc.parse_dict(m.group(1)))
    if not cfg.get("autoscript"):
        cfg["autoscript"] = path.stem
    cfg["autoscript"] = str(cfg["autoscript"]).upper()
    # Deploy the source only; the managed block is repo metadata, not runtime code.
    cfg["source"] = text[: m.start()].rstrip("\n") + "\n"
    cfg.setdefault("scriptlanguage", "javascript" if path.suffix == ".js" else "python")
    if notes:
        cfg["_notes"] = notes
    return cfg


def save_script(t: ArtifactType, rec: dict, fmt: str | None = None) -> tuple[Path, bool]:
    name = SAFE.sub("_", rec["autoscript"])
    existing = [p for p in t.dir.rglob(f"{name}.*") if p.suffix in (".py", ".js")] if t.dir.exists() else []
    path = t.dir / script_folder(rec) / f"{name}{script_ext(rec)}"
    # keep whatever format (and folder) the developer already uses for this script
    fmt = fmt or (script_format(existing[0]) if existing else "tmg")
    if fmt == "tmg" and existing:
        rec = dict(rec)
        rec["_tmg_meta"] = _tmg_meta(existing[0])
    if existing and existing[0].parent.name in ("integration",) and script_folder(rec) == "library":
        path = existing[0]
    for old in existing:
        if old != path:
            old.unlink()
    return path, write_text(path, render_script(rec, fmt))


# ── App Designer ───────────────────────────────────────────────────────────
def save_appxml(t: ArtifactType, app: str, xml: str) -> tuple[Path, bool]:
    from . import appxml as ax
    path = t.dir / f"{SAFE.sub('_', app.upper())}.xml"
    return path, write_text(path, ax.pretty(xml.replace("\r\n", "\n")))


# ── discovery ──────────────────────────────────────────────────────────────
def local_files(t: ArtifactType) -> list[Path]:
    if not t.dir.exists():
        return []
    if t.handler == "autoscript":
        pats = ("*.py", "*.js")
    elif t.handler == "appxml":
        pats = ("*.xml",)
    else:
        pats = ("*.json",)
    out = []
    for p in pats:
        # only this type's own folder tree, not a nested folder owned by another type
        for f in t.dir.rglob(p):
            if f.name.startswith(("_", ".")):
                continue
            rel = f.relative_to(t.dir).parts
            if t.handler != "autoscript" and len(rel) > 1:
                continue
            out.append(f)
    return sorted(out)


def load_record(t: ArtifactType, path: Path) -> dict:
    if t.handler == "autoscript":
        return parse_script(path)
    if t.handler == "appxml":
        return {"app": path.stem.upper(), "presentation": path.read_text(encoding="utf-8")}
    return load_json(path)


def find_local(t: ArtifactType, name: str) -> Path | None:
    want = SAFE.sub("_", name).lower()
    for f in local_files(t):
        if f.stem.lower() == want:
            return f
    return None
