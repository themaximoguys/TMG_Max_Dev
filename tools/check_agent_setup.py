"""Validate shared agent wiring offline, including copied Windows discovery trees."""
from pathlib import Path
import json
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)

    expected = {"maximo-dev", "create-automation-script", "convert-java-to-script",
                "convert-trm-to-script", "maximo-workflow", "maximo-dev-engine"}
    skills = root / "skills"
    require({p.relative_to(skills).as_posix() for p in skills.rglob("SKILL.md")} ==
            {f"{name}/SKILL.md" for name in expected},
            "Skill catalog is incomplete or contains nested/duplicate skills; keep evaluation workspaces outside skills/")
    for name in sorted(expected):
        entry = skills / name / "SKILL.md"
        if not entry.is_file():
            errors.append(f"Missing {entry.relative_to(root)}")
            continue
        text = entry.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        try:
            meta = yaml.safe_load(parts[1]) if len(parts) == 3 and not parts[0].strip() else {}
            require(isinstance(meta, dict) and meta.get("name") == name, f"{name}: invalid skill name")
            require(isinstance(meta, dict) and isinstance(meta.get("description"), str)
                    and bool(meta["description"].strip()), f"{name}: missing description")
        except yaml.YAMLError as exc:
            errors.append(f"{name}: invalid YAML: {exc}")
        for ref in re.findall(r"`([^`\n]+\.md)`", text):
            require((root / ref).is_file() or (entry.parent / ref).is_file(),
                    f"{name}: missing Markdown reference {ref}")
        ui = entry.parent / "agents/openai.yaml"
        try:
            interface = yaml.safe_load(ui.read_text(encoding="utf-8"))["interface"]
            require(f"${name}" in interface["default_prompt"], f"{name}: incorrect Codex prompt")
        except (OSError, yaml.YAMLError, KeyError, TypeError) as exc:
            errors.append(f"{name}: invalid Codex metadata: {exc}")

    for rel in (".agents/skills", ".claude/skills"):
        discovery = root / rel
        require(discovery.is_dir(), f"Missing discovery directory: {rel}")
        if not discovery.is_dir():
            continue
        canonical = {p.relative_to(skills): p.read_bytes() for p in skills.rglob("*") if p.is_file()}
        exposed = {p.relative_to(discovery): p.read_bytes() for p in discovery.rglob("*") if p.is_file()}
        require(canonical == exposed, f"{rel}: discovery content differs from skills/")

    for rel in ("CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md", ".cursor/rules/maximo.mdc"):
        path = root / rel
        require(path.is_file() and "AGENTS.md" in path.read_text(encoding="utf-8"),
                f"{rel}: missing shared-guide pointer")
    try:
        config = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
        servers = config["mcpServers"]
        require(set(servers) == {"tmg-maximo-dev"}, "Default MCP registration must use the guarded local server")
        local = servers["tmg-maximo-dev"]
        require(local == {"command": "python3", "args": ["-m", "maxdev.mcp_server"]},
                "Unexpected shared MCP defaults; keep credentials and tenant choices local")
    except (OSError, ValueError, KeyError) as exc:
        errors.append(f"Invalid MCP config: {exc}")
    config = root / ".codex/config.toml"
    template = root / "config/agents/codex.toml"
    require(config.is_file() and config.read_bytes() == template.read_bytes(),
            "Codex project config missing or differs from portable template")
    return errors


if __name__ == "__main__":
    problems = check()
    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)
    if not problems:
        print("Agent setup OK: 6 shared skills, discovery trees, client entry points, and MCP defaults")
    sys.exit(bool(problems))
