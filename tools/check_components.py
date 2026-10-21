"""Validate that the repo's developed components are present and wired, offline."""
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Scripts maxdev calls by name on the tenant; each must ship in the predeployment.
CALLED_SCRIPTS = {"TMG_EXPORT_PRES": "maxdev/engine.py", "TMG.CONFIGDB.APPLY": "maxdev/admin.py"}


def check(root=ROOT):
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)

    src = root / "src"
    predeploy = src / "00_predeployment"
    structures = predeploy / "15-integration" / "object-structures"
    library = predeploy / "09-automation-scripts" / "library"

    try:
        registry = yaml.safe_load((root / "maxdev/registry.yaml").read_text(encoding="utf-8"))
        types = registry["types"]
    except (OSError, yaml.YAMLError, KeyError, TypeError) as exc:
        return [f"maxdev/registry.yaml unreadable: {exc}"]

    ids = [t.get("id") for t in types]
    require(len(ids) == len(set(ids)), "registry.yaml: duplicate type ids")
    folders = {}
    for t in types:
        folder = t.get("folder")
        require(bool(folder), f"registry type {t.get('id')}: missing folder")
        if not folder:
            continue
        require(folder not in folders, f"registry types {folders.get(folder)} and {t['id']} share folder {folder}")
        folders[folder] = t["id"]
        require((src / folder).is_dir(), f"src/{folder} missing (registry type {t['id']})")
        require((src / folder / ".gitkeep").is_file() or any((src / folder).glob("*")),
                f"src/{folder}: add a .gitkeep so the folder survives a fresh clone")

    from maxdev.bootstrap_gen import PLAN
    for name in sorted(PLAN):
        require((structures / f"{name}.json").is_file(),
                f"predeployment structure {name} missing; run `maxdev bootstrap generate`")
    for path in sorted(structures.glob("*.json")):
        require(path.stem in PLAN, f"{path.relative_to(root)} is not in bootstrap_gen.PLAN")

    for t in types:
        os_names = t.get("os") or []
        os_names = [os_names] if isinstance(os_names, str) else os_names
        for name in os_names:
            if name.startswith("TMG") and t.get("status", "ok") != "verify":
                require(name in PLAN, f"registry type {t['id']} uses {name}, which bootstrap does not create")

    readme = (predeploy / "README.md")
    text = readme.read_text(encoding="utf-8") if readme.is_file() else ""
    require(bool(text), "src/00_predeployment/README.md missing")
    for name in sorted(PLAN):
        require(name in text, f"src/00_predeployment/README.md does not document {name}")

    for script, caller in CALLED_SCRIPTS.items():
        require((library / f"{script}.py").is_file(),
                f"{caller} calls {script}, but {library.relative_to(root)}/{script}.py is missing")

    errors += _check_engine(root, {t["id"] for t in types})

    for rel in ("catalog/templates", "docs/standards/TMG_AUTOSCRIPT_STANDARDS.md", "manifests/EXAMPLE.yaml",
                ".mcp.json", ".githooks/pre-commit", ".githooks/pre-push"):
        require((root / rel).exists(), f"{rel} missing")
    return errors


def _check_engine(root, type_ids):
    """Design subagents in .claude/agents/ <-> the dispatch table in the maximo-dev-engine skill."""
    import re
    errors = []
    skill = root / "skills/maximo-dev-engine/SKILL.md"
    if not (skill / "../TICKET_TEMPLATE.md").resolve().is_file():
        errors.append("skills/maximo-dev-engine/TICKET_TEMPLATE.md missing")
    named = set(re.findall(r"\|\s*`([a-z][a-z-]+)`\s*\|\s*$", skill.read_text(encoding="utf-8"), re.M)) if skill.is_file() else set()
    files = {p.stem: p for p in (root / ".claude/agents").glob("*.md")}
    for name in sorted(named - set(files)):
        errors.append(f"maximo-dev-engine names subagent {name}, but .claude/agents/{name}.md is missing")
    for name in sorted(set(files) - named):
        errors.append(f".claude/agents/{name}.md is not in the maximo-dev-engine dispatch table")
    for name, path in sorted(files.items()):
        parts = path.read_text(encoding="utf-8").split("---", 2)
        try:
            meta = yaml.safe_load(parts[1]) if len(parts) == 3 and not parts[0].strip() else None
        except yaml.YAMLError as exc:
            errors.append(f".claude/agents/{name}.md: invalid frontmatter YAML: {str(exc).splitlines()[0]}")
            continue
        if not isinstance(meta, dict) or meta.get("name") != name or not meta.get("description"):
            errors.append(f".claude/agents/{name}.md: frontmatter needs name: {name} and a description")
    return errors


if __name__ == "__main__":
    problems = check()
    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)
    if not problems:
        print("Components OK: registry folders, predeployment, design subagents, ticket template, standards, hooks")
    sys.exit(bool(problems))
