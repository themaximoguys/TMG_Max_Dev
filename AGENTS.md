# TMG_Max_Dev — shared coding-agent instructions

This guide applies to every coding agent working in this repository. Read
`skills/maximo-dev/SKILL.md` first. Paths in this guide are relative to the repository
root; skill-local references are relative to that skill's directory.

## Repository and runtime

- Maximo/MAS 9 configuration and code live in `src/`, one file per record.
- All Maximo access goes through `python3 -m maxdev` or the `tmg-maximo-dev`
  MCP server. The CLI is the complete fallback when MCP or skill discovery is unavailable.
- `maxdev/` runs on local Python 3.10+. Deployed scripts use Maximo Jython 2.7;
  do not apply Python 3 syntax or tooling assumptions to `src/` or `catalog/` scripts.
- Install local dependencies with `python3 -m pip install -e .` in a virtual environment.
  Run commands from the repository root. No tenant is needed for offline checks.
- `maxdev/registry.yaml` defines artifact types and folders; `catalog/templates/`
  supplies script templates. Do not invent parallel registries or deployment clients.

## Skills and standards

Canonical skills live in `skills/`; `.agents/skills` and `.claude/skills` expose
that same content for discovery. Read only the skill and references relevant to the task.

| Task | Skill |
|---|---|
| Extract, edit, diff, deploy, bootstrap, diagnose Maximo | `skills/maximo-dev/SKILL.md` |
| Create or extend automation scripts | `skills/create-automation-script/SKILL.md` |
| Convert Java customizations | `skills/convert-java-to-script/SKILL.md` |
| Convert TRM rules | `skills/convert-trm-to-script/SKILL.md` |
| Generate workflows and their dependencies | `skills/maximo-workflow/SKILL.md` |

`docs/standards/TMG_AUTOSCRIPT_STANDARDS.md` is authoritative for scripts.
Build from catalog templates with `python3 -m maxdev build`; Java conversion starts
with `python3 -m maxdev java analyze`. Workflows belong in `src/13-workflows/`.
Reference material is TMG-only: do not introduce client names or third-party assessments.

## Safety and scope

- Edit local files, lint/diff, and show a dry run before requesting approval for
  live writes. Apply only after user approval for the concrete target and changes.
- Pass `--env NAME` (MCP: `env`) explicitly for tenant operations. If the target is
  unknown, prepare local work and ask before contacting a tenant.
- Never edit `environments/.env.*` yourself or expose credentials in output, code,
  MCP configs, or Git. The user manages environment files and protection flags.
- Protected environments refuse writes. Do not bypass this through curl, another
  client, direct IBM MCP registration, or an automation script.
- Script handlers can write even over GET; they require dry run and approval.
  Admin Mode can log users out; obtain explicit approval for it.
- No demo/seed data loads unless requested. Filter extracts by name, `--like`,
  `--where`, or `--limit`; avoid unrestricted tenant dumps.
- Preserve unrelated changes and untracked extracts. Do not overwrite an existing
  script when another already owns the MBO/event. Review before staging files.
- App Designer uses additive merge by default; `--force-replace` requires explicit
  authorization. Report FAILED and not-attempted receipt rows accurately.
- Local edits and offline tests do not need tenant-write approval. Do not deploy
  merely to validate a documentation or tooling change.

## Validation and handoff

- Engine/CLI/MCP changes: `python3 -m unittest discover -s tests`.
- Scripts: `python3 -m maxdev lint` (or pass changed script paths); no lint errors.
- Agent setup: `python3 tools/check_agent_setup.py`.
- Components: `python3 tools/check_components.py` (registry folders, predeployment, standards).
- Git hooks in `.githooks/` run these checks on commit/push once enabled with
  `git config core.hooksPath .githooks`; Claude Code hooks are in `.claude/settings.json`.
- Review `git diff --check` and the diff; report checks run, failures, and any
  unverified live behavior. Do not claim a tenant test from an offline test.
- Keep vendor entry files as small pointers to this guide. Setup and MCP examples:
  `docs/AGENT_SETUP.md`. No CI/CD or automatic deployment is configured here.
