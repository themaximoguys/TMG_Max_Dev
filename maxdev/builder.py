"""Automation-script builder: TMG templates, standards lint, Java-class analysis.

Templates come from catalog/templates/{mxlogger,service}/TEMPLATE_<kind>[_service].py
(TMG_MAX_CODE, MIT). The builder fills the mechanical placeholders (object, field,
names, author, date) and leaves the business placeholders ({PURPOSE_DESCRIPTION},
{BUSINESS_RULE_1}...) for the developer or Claude. `maxdev lint` reports any left;
deploy refuses scripts with lint errors.
"""
from __future__ import annotations

import datetime as dt
import os
import re
from pathlib import Path

from .env import REPO

CATALOG = REPO / "catalog"
TEMPLATES = CATALOG / "templates"

# kind -> (template stem, autoscript name pattern, repo subfolder)
KINDS = {
    "field_validate":   ("field_validator_validate",   "{OBJECT}.{FIELD}.VALIDATE", "attribute"),
    "field_init":       ("field_validator_init",       "{OBJECT}.{FIELD}.INIT", "attribute"),
    "field_action":     ("field_validator_action",     "{OBJECT}.{FIELD}.ACTION", "attribute"),
    "field_listfilter": ("field_validator_listfilter", "{OBJECT}.{FIELD}.LISTFILTER", "attribute"),
    "object_init":      ("object_script_init",         "{OBJECT}.OBJ.INIT", "object"),
    "object_add":       ("object_script_add",          "{OBJECT}.OBJ.ADD", "object"),
    "object_save_before": ("object_script_save_before", "{OBJECT}.OBJ.SAVE.BEFORE", "object"),
    "object_save_after":  ("object_script_save_after",  "{OBJECT}.OBJ.SAVE.AFTER", "object"),
    "status_handler":   ("status_handler",             "{OBJECT}.STATUS.HANDLER", "object"),
    "workflow_action":  ("workflow_action",            "{OBJECT}.ACTION.{NAME}", "action"),
    "escalation_action": ("escalation_action",         "{OBJECT}.ACTION.{NAME}", "action"),
    "cron_task":        ("cron_task",                  "TMG_{NAME}.CRON.ACTION", "crontask"),
    "publish_channel":  ("integration_publish_channel", "PUBLISH.{CHANNEL}.{EXITTYPE}.OUT", "integration"),
    "enterprise_service": ("integration_enterprise_service", "SYNC.{SERVICE}.{EXITTYPE}.IN", "integration"),
}


def template_path(kind: str, logging: str = "mxlogger") -> Path:
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind!r}; one of {sorted(KINDS)}")
    stem = KINDS[kind][0]
    p = TEMPLATES / logging / (f"TEMPLATE_{stem}.py" if logging == "mxlogger" else f"TEMPLATE_{stem}_service.py")
    if not p.exists():
        raise FileNotFoundError(f"no template {p.relative_to(REPO)}")
    return p


def list_templates() -> list[dict]:
    out = []
    for kind, (stem, name, folder) in KINDS.items():
        for logging in ("mxlogger", "service"):
            try:
                p = template_path(kind, logging)
            except FileNotFoundError:
                continue
            out.append({"kind": kind, "logging": logging, "file": str(p.relative_to(REPO)),
                        "name_pattern": name, "folder": folder})
    return out


def build(kind: str, *, object_name: str = "", field: str = "", name: str = "", channel: str = "",
          service_name: str = "", exit_type: str = "USEREXIT", logging: str = "mxlogger",
          author: str = "", description: str = "", java_class: str = "", autoscript: str = "") -> tuple[Path, list[dict]]:
    """Write a new script into src/09-automation-scripts/<folder>/ from a template."""
    tpl = template_path(kind, logging).read_text(encoding="utf-8")
    O, F, N = object_name.upper(), field.upper(), name.upper()
    needs = {"OBJECT": O, "FIELD": F, "NAME": N, "CHANNEL": channel.upper(), "SERVICE": service_name.upper()}
    pattern = KINDS[kind][1]
    for k, v in needs.items():
        if "{" + k + "}" in pattern and not v:
            raise ValueError(f"{kind} needs --{ {'OBJECT': 'object', 'FIELD': 'attr', 'NAME': 'name', 'CHANNEL': 'channel', 'SERVICE': 'service'}[k] }")
    values = {
        "OBJECT": O, "object": O.lower(), "FIELD": F, "field": F.lower(), "NAME": N, "name": N.lower(),
        "CHANNEL": channel.upper(), "SERVICE": service_name.upper(), "EXITTYPE": exit_type.upper(),
        "ACTIONNAME": N, "actionname": N.lower(), "ACTION_NAME": N,
        "AUTHOR": author or os.environ.get("MAXDEV_AUTHOR", "TMG"), "DATE": dt.date.today().isoformat(),
        "OBJECT_DESC": O.title(), "SCRIPT_DESCRIPTION": description or "{SCRIPT_DESCRIPTION}",
        "LP_DESCRIPTION": description or "{LP_DESCRIPTION}", "JAVA_CLASS": java_class or "{JAVA_CLASS}",
    }
    text = re.sub(r"\{([A-Za-z_0-9]+)\}", lambda m: values.get(m.group(1)) or m.group(0), tpl)
    # TMG naming: the template's own scriptConfig name, placeholders filled. --autoscript overrides.
    m = re.search(r'"autoscript"\s*:\s*"([^"]*)"', text)
    script_name = (autoscript or (m.group(1) if m else "")).upper()
    if not script_name or "{" in script_name:
        script_name = pattern.format(**{k: v or k for k, v in {**needs, "EXITTYPE": exit_type.upper()}.items()}).upper()
    if m:
        text = text[: m.start(1)] + script_name + text[m.end(1):]
    folder = KINDS[kind][2]
    path = REPO / "src" / "09-automation-scripts" / folder / f"{script_name}.py"
    if path.exists():
        raise FileExistsError(f"{path.relative_to(REPO)} already exists — add the rule to it instead of a second script (TMG consolidation rule)")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path, lint_text(text, path.name)


# ── lint: TMG_AUTOSCRIPT_STANDARDS hard rules ─────────────────────────────
RULES = [
    ("error", "no-fstring", re.compile(r'(?<![\w])[fF][rR]?["\']'), "f-strings are not Jython 2.7"),
    ("error", "no-print", re.compile(r"^\s*print\s*\("), "use the logger, not print()"),
    ("error", "no-system-out", re.compile(r"System\.(out|err)\."), "use the logger"),
    ("error", "java17-sun-misc", re.compile(r"sun\.misc\."), "removed on Java 17: use java.util.Base64"),
    ("error", "java17-javax-xml-bind", re.compile(r"javax\.xml\.bind"), "use jakarta.xml.bind on MAS 9"),
    ("error", "no-commit", re.compile(r"\.commit\(\)"), "Maximo manages the transaction"),
    ("error", "no-threads", re.compile(r"^\s*(import|from)\s+(threading|subprocess|multiprocessing)\b"), "not allowed in scripts"),
    ("error", "no-async", re.compile(r"^\s*async\s+def\b|\bawait\b"), "not Jython 2.7"),
    ("error", "sql-concat", re.compile(r"setWhere\([^)]*[\"']\s*\+|setWhere\([^)]*\+\s*[\"']"), "build SQL with SqlFormat, never string concatenation"),
    ("error", "no-python-stdlib", re.compile(r"^\s*(import|from)\s+(re|json|os|datetime|string|collections|urllib\w*|base64|csv|random|functools|traceback|logging)\b"),
     "Maximo's Jython has no Python stdlib (ImportError at runtime) — use the java.* equivalent"),
    ("warn", "bare-except", re.compile(r"^\s*except\s*:"), "catch Exception and log + re-raise"),
]


def _code_lines(text: str):
    """Yield (lineno, line) for code, skipping comments and the trailing scriptConfig."""
    cut = text.rfind("\nscriptConfig")
    body = text if cut < 0 else text[:cut]
    in_doc = False
    for i, line in enumerate(body.splitlines(), 1):
        st = line.strip()
        if st.startswith(('"""', "'''")):
            if not (len(st) > 3 and st.endswith(st[:3])):
                in_doc = not in_doc
            continue
        if in_doc or st.startswith("#"):
            continue
        yield i, line


def lint_text(text: str, name: str = "") -> list[dict]:
    issues = []
    code = list(_code_lines(text))
    for i, line in code:
        for level, rule, rx, msg in RULES:
            if rx.search(line):
                issues.append({"level": level, "rule": rule, "line": i, "msg": msg, "text": line.strip()[:120]})
    src = "\n".join(l for _, l in code)
    if "MXLoggerFactory" in src and re.search(r"\bservice\.log", src):
        issues.append({"level": "error", "rule": "one-logging-style", "line": 0,
                       "msg": "mixes MXLoggerFactory and service.log — pick one"})
    opened = len(re.findall(r"\.getMboSet\(", src))
    closed = len(re.findall(r"\.close\(\)", src))
    if opened and closed < opened:
        issues.append({"level": "warn", "rule": "mboset-close", "line": 0,
                       "msg": f"{opened} getMboSet() vs {closed} close() — close sets in finally"})
    if re.search(r"\.INIT\b", name.upper()) and re.search(r"\.setValue\(", src):
        guarded = "toBeAdded()" in src
        issues.append({"level": "warn" if guarded else "error", "rule": "no-setvalue-in-init", "line": 0,
                       "msg": "setValue() in INIT" + (" (guarded by toBeAdded — new records only, OK per standard)" if guarded
                              else " dirties every existing record on load; guard with mbo.toBeAdded() or move to OBJ.ADD")})
    left = sorted(set(re.findall(r"\{([A-Z][A-Z_0-9]+)\}", text)))
    if left:
        code_left = sorted({p for p in left if "{" + p + "}" in src})
        issues.append({"level": "error" if code_left else "warn", "rule": "unfilled-placeholder", "line": 0,
                       "msg": "template placeholders left: " + ", ".join(left[:20])
                              + (f" (in code: {', '.join(code_left)})" if code_left else " (comments/config only)")})
    if "scriptConfig" not in text:
        issues.append({"level": "error", "rule": "missing-scriptconfig", "line": 0, "msg": "no scriptConfig block"})
    try:
        compile(re.sub(r"\bexcept\s+([\w.]+)\s*,\s*(\w+)\s*:", r"except \1 as \2:", text), name or "<script>", "exec")
    except SyntaxError as e:
        if "print" not in str(e.text or ""):
            issues.append({"level": "error", "rule": "syntax", "line": e.lineno or 0, "msg": str(e.msg)})
    return issues


# ── Java customisation analysis ───────────────────────────────────────────
JAVA_HINTS = [
    (re.compile(r"extends\s+(MAX|MboValueAdapter|MAXTableDomain|MAXString|MboValue\w*|Fld\w+)"), "field",
     "Field class (MboValueAdapter) → ATTRIBUTE launch point: validate()→field_validate, init()→field_init, action()→field_action, getList()→field_listfilter"),
    (re.compile(r"extends\s+(CronTaskAdapter|SimpleCronTask)"), "cron_task",
     "Cron task class → SCRIPTCRONTASK instance with SCRIPTNAME param (cron_task template)"),
    (re.compile(r"implements\s+ActionCustomClass|extends\s+\w*Action\b"), "workflow_action",
     "ActionCustomClass → ACTION launch point bound to an action (workflow_action / escalation_action)"),
    (re.compile(r"extends\s+(MaximoIfaceExit|MicUserExit|ExternalExit|UserExit|\w*Exit)\b"), "publish_channel",
     "Integration exit class → name-bound integration script (publish_channel / enterprise_service)"),
    (re.compile(r"extends\s+\w*(AppBean|DataBean)\b"), "bean",
     "UI bean → no script equivalent: use conditional UI, sig options or an ACTION script on a button; MAF for role-based apps"),
    (re.compile(r"extends\s+(Mbo|StatefulMbo|\w+Mbo|Asset|WO|WorkOrder|PO|PR|Ticket|SR)\b"), "object",
     "MBO class → OBJECT launch point: init()→object_init, add()→object_add, save()/appValidate()→object_save_before, changeStatus/canChangeStatus→status_handler"),
]
METHOD_MAP = {
    "validate": "field_validate", "init": "field_init or object_init", "initValue": "field_init",
    "action": "field_action", "getList": "field_listfilter", "add": "object_add",
    "save": "object_save_before", "appValidate": "object_save_before", "canDelete": "object_save_before (delete)",
    "changeStatus": "status_handler", "canChangeStatus": "status_handler", "cronAction": "cron_task",
    "applyCustomAction": "workflow_action", "setDataIn": "enterprise_service", "setDataOut": "publish_channel",
}


def analyze_java(path: Path) -> dict:
    src = path.read_text(encoding="utf-8", errors="replace")
    cls = re.search(r"\bclass\s+(\w+)\s+(extends\s+[\w.]+)?\s*(implements\s+[\w.,\s]+)?", src)
    header = cls.group(0) if cls else ""
    family, advice = "unknown", "No known Maximo base class — review manually"
    for rx, fam, adv in JAVA_HINTS:
        if rx.search(header):
            family, advice = fam, adv
            break
    methods = sorted(set(re.findall(r"public\s+(?:[\w<>\[\]]+\s+)+(\w+)\s*\(", src)))
    mapped = {m: METHOD_MAP[m] for m in methods if m in METHOD_MAP}
    blockers = []
    for rx, why in [(r"\bThread\b|ExecutorService", "threads"), (r"java\.sql\.(Connection|Statement)", "direct JDBC — use MboSets"),
                    (r"\bjavax\.xml\.bind|sun\.misc", "Java 17 removed APIs"), (r"RMI|Naming\.lookup", "RMI not supported in MAS"),
                    (r"extends\s+\w*(AppBean|DataBean)", "UI bean")]:
        if re.search(rx, src):
            blockers.append(why)
    imports = sorted(set(re.findall(r"^import\s+([\w.]+);", src, re.M)))
    return {"file": str(path), "class": cls.group(1) if cls else None, "declaration": header.strip(),
            "family": family, "advice": advice, "methods": methods, "method_to_template": mapped,
            "blockers": blockers, "imports": imports, "lines": src.count("\n") + 1,
            "convertible": family not in ("unknown", "bean") and not {"threads", "UI bean"} & set(blockers)}
